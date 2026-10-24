"""Assemble declared fragment-supported AO columns in one global metric."""
import numpy as np
from .support import array, check, keys, metric, require_rows, scope_result, tolerance


def analyze(parameters, data):
    keys(parameters, ['atol', 'rank_rtol'])
    keys(data, ['overlap', 'fragments', 'target_vectors'], ['operator'])
    atol = tolerance(parameters['atol'])
    rtol = parameters['rank_rtol']
    if type(rtol) not in {int, float} or not 1e-12 <= rtol <= 1e-4:
        raise ValueError('Declare rank_rtol in [1e-12,1e-4].')
    s, _, _ = metric(data['overlap'], atol)
    fragments = data['fragments']
    if not isinstance(fragments, list) or not 1 <= len(fragments) <= 16:
        raise ValueError('Provide 1–16 explicit fragments.')
    columns, names = [], set()
    for fragment in fragments:
        keys(fragment, ['id', 'ao_indices', 'coefficients'])
        if not isinstance(fragment['id'], str) or not fragment['id'] or fragment['id'] in names:
            raise ValueError('Unique fragment IDs required.')
        names.add(fragment['id'])
        indices = fragment['ao_indices']
        if not isinstance(indices, list) or not indices or len(set(indices)) != len(indices) or any(type(i) is not int or not 0 <= i < len(s) for i in indices):
            raise ValueError('Explicit unique zero-based fragment AO indices required.')
        b = array(fragment['coefficients'], 2)
        require_rows(b, len(s), 'fragment coefficients')
        outside = sorted(set(range(len(s))) - set(indices))
        if outside and np.max(abs(b[outside])) > atol:
            raise ValueError('Fragment coefficient has support outside its declared AO set.')
        columns.append(b)
    b = np.concatenate(columns, axis=1)
    if b.shape[1] > 128:
        raise ValueError('More than 128 candidate columns.')
    gram = b.T @ s @ b
    eigenvalues, u = np.linalg.eigh(gram)
    if eigenvalues[-1] <= 0:
        raise ValueError('No nonzero working space.')
    keep = eigenvalues > rtol * eigenvalues[-1]
    q = b @ (u[:, keep] / np.sqrt(eigenvalues[keep]))
    target = array(data['target_vectors'], 2)
    require_rows(target, len(s), 'target vectors')
    residual = target - q @ (q.T @ s @ target)
    checks = [check('working_basis_orthonormality', np.linalg.norm(q.T @ s @ q - np.eye(q.shape[1])), atol),
              check('target_coverage_S_norm', np.sqrt(max(0, float(np.trace(residual.T @ s @ residual)))), atol)]
    transformed = None
    if 'operator' in data:
        operator = array(data['operator'], 2)
        if operator.shape != s.shape or np.max(abs(operator - operator.T)) > atol:
            raise ValueError('Optional AO operator must be compatible real symmetric.')
        transformed = (q.T @ operator @ q).tolist()
    return scope_result('DECLARED_FRAGMENT_SUPPORT_WORKING_BASIS_AND_ONE_ELECTRON_TRANSFORM_ONLY', checks,
                        rank=int(keep.sum()), candidate_columns=b.shape[1], gram_eigenvalues=eigenvalues.tolist(),
                        working_coefficients=q.tolist(), transformed_operator=transformed,
                        target_residual=residual.tolist(),
                        limits=['All fragments use the same supplied global AO order and overlap; labels do not authenticate that identity.',
                                'Global orthogonalization can mix fragments; final columns need not retain individual fragment support.',
                                'No fragment energy decomposition, two-electron tensor transformation, self-consistency or new electronic structure.'])
