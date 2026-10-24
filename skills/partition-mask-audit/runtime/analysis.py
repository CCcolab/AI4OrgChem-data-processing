"""Apply a symmetric declared partition mask; positivity depends on matrix role."""
import numpy as np
from .support import array, check, keys, scope_result, tolerance


def analyze(parameters, data):
    keys(parameters, ['atol', 'matrix_role', 'allowed_pairs'])
    keys(data, ['matrix', 'partitions'])
    atol = tolerance(parameters['atol'])
    role = parameters['matrix_role']
    if role not in {'overlap', 'hamiltonian'}:
        raise ValueError('Declare overlap or hamiltonian role; positivity is not universal.')
    h = array(data['matrix'], 2)
    if h.shape[0] != h.shape[1] or np.max(abs(h - h.T)) > atol:
        raise ValueError('Require a square real symmetric matrix.')
    partitions = data['partitions']
    if not isinstance(partitions, list) or not partitions:
        raise ValueError('Declare a nonempty complete partition.')
    index_map, names = {}, []
    for partition in partitions:
        keys(partition, ['id', 'indices'])
        name, indices = partition['id'], partition['indices']
        if not isinstance(name, str) or not name or name in names or not isinstance(indices, list) or not indices:
            raise ValueError('Unique nonempty partition names and indices required.')
        names.append(name)
        for i in indices:
            if type(i) is not int or not 0 <= i < len(h) or i in index_map:
                raise ValueError('Partitions overlap or have invalid indices.')
            index_map[i] = name
    if set(index_map) != set(range(len(h))):
        raise ValueError('Every matrix index must appear exactly once.')
    pairs = parameters['allowed_pairs']
    if not isinstance(pairs, list):
        raise ValueError('Declare allowed unordered coupling pairs, including diagonals if desired.')
    allowed = set()
    for pair in pairs:
        if not isinstance(pair, list) or len(pair) != 2 or any(name not in names for name in pair):
            raise ValueError('Unknown allowed partition pair.')
        key = tuple(sorted(pair))
        if key in allowed:
            raise ValueError('Repeated unordered coupling pair.')
        allowed.add(key)
    mask = np.array([[tuple(sorted((index_map[i], index_map[j]))) in allowed for j in range(len(h))]
                     for i in range(len(h))], dtype=bool)
    masked = np.where(mask, h, 0.0)
    before, after = np.linalg.eigvalsh(h), np.linalg.eigvalsh(masked)
    checks = [check('masked_matrix_symmetry', np.max(abs(masked - masked.T)), atol)]
    if role == 'overlap':
        checks.extend([check('original_overlap_minimum_eigenvalue', max(0, atol - before[0]), 0),
                       check('masked_overlap_minimum_eigenvalue', max(0, atol - after[0]), 0)])
        # Strictly greater than atol is the actual positive-definiteness rule.
        checks[-2]['passed'] = bool(before[0] > atol)
        checks[-1]['passed'] = bool(after[0] > atol)
    return scope_result('DECLARED_PARTITION_MATRIX_MASK_AUDIT_NOT_NEW_HAMILTONIAN_SCIENCE', checks,
                        matrix_role=role, mask=mask.tolist(), masked_matrix=masked.tolist(),
                        original_eigenvalues=before.tolist(), masked_eigenvalues=after.tolist(),
                        removed_frobenius_norm=float(np.linalg.norm(h - masked)),
                        limits=['Hamiltonians may be indefinite; no positivity gate is applied to that role.',
                                'Masking changes the matrix and potentially the problem; it is not an equivalent AO basis transformation.',
                                'Euclidean eigenvalues of an AO Hamiltonian are not automatically orbital energies; generalized metric problems differ.',
                                'No self-consistency, physical energy interpretation or arbitrary conditional-state compute.'])
