"""Metric projection and squared residual norms with explicit numerical rank."""
import numpy as np
from .support import array, check, keys, metric, require_rows, scope_result, tolerance


def analyze(parameters, data):
    keys(parameters, ['atol', 'rank_rtol'])
    keys(data, ['overlap', 'basis', 'vectors'])
    atol = tolerance(parameters['atol'])
    rtol = parameters['rank_rtol']
    if type(rtol) not in {int, float} or not 1e-12 <= rtol <= 1e-4:
        raise ValueError('Declare a Gram eigenvalue relative rank threshold in [1e-12,1e-4].')
    s, _, _ = metric(data['overlap'], atol)
    b, v = array(data['basis'], 2), array(data['vectors'], 2)
    require_rows(b, len(s), 'basis')
    require_rows(v, len(s), 'vectors')
    gram = b.T @ s @ b
    eigenvalues, u = np.linalg.eigh(gram)
    if eigenvalues[-1] <= 0 or eigenvalues[0] < -atol * max(1, eigenvalues[-1]):
        raise ValueError('Zero or invalid Gram matrix.')
    keep = eigenvalues > rtol * eigenvalues[-1]
    inverse = (u[:, keep] / eigenvalues[keep]) @ u[:, keep].T
    projector = b @ inverse @ b.T @ s
    projected = projector @ v
    residual = v - projected
    total_norm = np.diag(v.T @ s @ v)
    leaked_norm = np.diag(residual.T @ s @ residual)
    if np.min(total_norm) < -atol or np.min(leaked_norm) < -atol:
        raise ValueError('Invalid negative metric squared norm.')
    total_norm = np.maximum(total_norm, 0)
    leaked_norm = np.maximum(leaked_norm, 0)
    fractions = [float(r / n) if n > atol else None for r, n in zip(leaked_norm, total_norm)]
    checks = [check('projector_idempotency', np.linalg.norm(projector @ projector - projector), atol),
              check('metric_self_adjointness', np.linalg.norm(projector.T @ s - s @ projector), atol)]
    # Truncated dependent directions are discarded; orthogonality is checked
    # against the retained orthonormal range, not rejected tiny directions.
    q = b @ (u[:, keep] / np.sqrt(eigenvalues[keep]))
    checks.append(check('residual_retained_range_orthogonality', np.linalg.norm(q.T @ s @ residual), atol))
    return scope_result('REAL_METRIC_SUBSPACE_PROJECTION_NOT_ENERGY_OR_PROBABILITY_CERTIFICATION', checks,
                        rank=int(keep.sum()), gram_eigenvalues=eigenvalues.tolist(), rank_cutoff=float(rtol * eigenvalues[-1]),
                        projector=projector.tolist(), projected=projected.tolist(), residual=residual.tolist(),
                        vector_squared_norms=total_norm.tolist(), residual_squared_norms=leaked_norm.tolist(),
                        residual_fractions=fractions,
                        limits=['Fractions use squared S norms, not coefficient sums or energy loss.',
                                'A zero/near-zero input norm has undefined relative fraction, reported null.',
                                'Ambient S must remain positive definite; complex and singular-metric cases are outside this implementation.'])
