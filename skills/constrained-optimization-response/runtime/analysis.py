"""Review one supplied endpoint with explicit linear coordinate constraints."""
import numpy as np
from .support import array, check, keys, scope_result, tolerance


def analyze(parameters, data):
    keys(parameters, ['coordinate_unit', 'position_atol', 'gradient_atol', 'hessian_atol', 'curvature_min', 'rank_rtol'])
    keys(data, ['coordinates', 'gradient', 'hessian', 'constraint_matrix', 'constraint_target', 'converged', 'source_definition'])
    if parameters['coordinate_unit'] not in {'angstrom', 'bohr'}:
        raise ValueError('One common length unit required; mixed angle/length coordinates are not implemented.')
    pos, grad, htol = [tolerance(parameters[k]) for k in ['position_atol', 'gradient_atol', 'hessian_atol']]
    curvature = parameters['curvature_min']
    rtol = parameters['rank_rtol']
    if type(curvature) not in {int, float} or not np.isfinite(curvature) or curvature < 0:
        raise ValueError('Declare a nonnegative finite curvature threshold in Hartree/coordinate_unit^2.')
    if type(rtol) not in {int, float} or not 1e-12 <= rtol <= 1e-4:
        raise ValueError('Declare rank_rtol in [1e-12,1e-4].')
    if type(data['converged']) is not bool or not isinstance(data['source_definition'], str) or not data['source_definition'].strip():
        raise ValueError('Declare actual source and convergence; labels do not prove them.')
    x, g, h = array(data['coordinates'], 1, 60), array(data['gradient'], 1, 60), array(data['hessian'], 2, 60)
    a, b = array(data['constraint_matrix'], 2, 60), array(data['constraint_target'], 1, 60)
    if g.shape != x.shape or h.shape != (len(x), len(x)) or a.shape[1] != len(x) or a.shape[0] != len(b) or not 1 <= len(b) < len(x):
        raise ValueError('Require compatible arrays and at least one free coordinate.')
    if np.max(abs(h - h.T)) > htol:
        raise ValueError('Hessian is not symmetric to the declared absolute threshold.')
    _, singular, vh = np.linalg.svd(a, full_matrices=True)
    if singular[-1] <= rtol * singular[0]:
        raise ValueError('Linearly dependent constraints; no silent deletion.')
    tangent = vh[len(b):].T
    projected_gradient = tangent.T @ g
    restricted_hessian = tangent.T @ h @ tangent
    eigenvalues = np.linalg.eigvalsh(restricted_hessian)
    checks = [check('linear_constraint_residual', np.linalg.norm(a @ x - b), pos),
              check('tangent_gradient_norm', np.linalg.norm(projected_gradient), grad),
              {'name': 'declared_backend_convergence', 'passed': data['converged'], 'actual': data['converged'], 'threshold': True},
              {'name': 'positive_tangent_curvature', 'passed': bool(eigenvalues[0] > curvature),
               'actual': float(eigenvalues[0]), 'threshold': {'strictly_greater_than': curvature}}]
    return scope_result('SUPPLIED_LINEAR_CONSTRAINT_ENDPOINT_REVIEW_NOT_GEOMETRY_OPTIMIZATION', checks,
                        full_gradient_norm=float(np.linalg.norm(g)), projected_gradient=projected_gradient.tolist(),
                        tangent_hessian_eigenvalues=eigenvalues.tolist(), tangent_basis=tangent.tolist(),
                        endpoint_label='CANDIDATE_MINIMUM_WITHIN_DECLARED_LINEAR_CONSTRAINTS' if all(c['passed'] for c in checks) else 'NOT_QUALIFIED',
                        derivative_units=['hartree/' + parameters['coordinate_unit'], 'hartree/(' + parameters['coordinate_unit'] + ')^2'],
                        source_definition=data['source_definition'], new_optimization='NOT_EXECUTED',
                        limits=['No optimizer or new energy/gradient backend is called.',
                                'Only linear constraints are supported; nonlinear constraint curvature and Lagrangian terms require a different protocol.',
                                'Full gradient need not vanish at a constrained endpoint.',
                                'Tangent positive curvature does not establish an unconstrained/global minimum or electronic-state continuity.'])
