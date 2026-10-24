"""Review a supplied real AO reflection and a closed subspace before parity adaptation."""
import numpy as np
from .support import array, check, keys, metric, require_rows, scope_result, tolerance


def analyze(parameters, data):
    keys(parameters, ['atol', 'mirror_definition'])
    keys(data, ['overlap', 'reflection', 'basis'])
    atol = tolerance(parameters['atol'])
    if not isinstance(parameters['mirror_definition'], str) or not parameters['mirror_definition'].strip():
        raise ValueError('Explicit mirror and AO representation definition is required.')
    s, _, _ = metric(data['overlap'], atol)
    r, b = array(data['reflection'], 2), array(data['basis'], 2)
    require_rows(b, len(s), 'basis')
    if r.shape != s.shape or b.shape[1] > len(s):
        raise ValueError('Incompatible reflection or subspace dimensions.')
    restricted = b.T @ s @ r @ b
    residual = r @ b - b @ restricted
    checks = [check('reflection_involution', np.linalg.norm(r @ r - np.eye(len(s))), atol),
              check('reflection_metric_unitarity', np.linalg.norm(r.T @ s @ r - s), atol),
              check('basis_metric_orthonormality', np.linalg.norm(b.T @ s @ b - np.eye(b.shape[1])), atol),
              check('subspace_closure_S_norm', np.sqrt(max(0, float(np.trace(residual.T @ s @ residual)))), atol)]
    adapted, parity = None, None
    if all(row['passed'] for row in checks):
        eigenvalues, rotation = np.linalg.eigh((restricted + restricted.T) / 2)
        checks.append(check('restricted_parity_spectrum', np.max(np.minimum(abs(eigenvalues - 1), abs(eigenvalues + 1))), atol))
        if all(row['passed'] for row in checks):
            adapted = (b @ rotation).tolist()
            parity = eigenvalues.tolist()
    return scope_result('SUPPLIED_AO_REFLECTION_SUBSPACE_PARITY_REVIEW', checks,
                        mirror_definition=parameters['mirror_definition'], restricted_reflection=restricted.tolist(),
                        parity_eigenvalues=parity, adapted_coefficients=adapted,
                        limits=['Algebraic checks do not prove that the supplied AO matrix represents the claimed geometric mirror.',
                                'No parity labels are assigned when the subspace is not closed.',
                                'No automatic density/occupation preservation claim, no orbital chemical classification or new SCF.'])
