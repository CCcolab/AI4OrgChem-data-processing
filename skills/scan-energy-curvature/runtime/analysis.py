"""Local three-point derivatives on a declared continuous energy scan."""
import math
import numpy as np


def analyze(parameters, data):
    if set(parameters) != {'coordinate_unit', 'energy_unit', 'center_index', 'state_id', 'method_id', 'geometry_definition'} or set(data) != {'points'}:
        raise ValueError('Declare units, center, state, method, coordinate definition and points.')
    if parameters['coordinate_unit'] not in {'angstrom', 'bohr', 'degree', 'radian'} or parameters['energy_unit'] != 'hartree':
        raise ValueError('Use explicit angstrom/bohr/degree/radian and Hartree; no silent conversion.')
    if not all(isinstance(parameters[k], str) and parameters[k].strip() for k in ['state_id', 'method_id', 'geometry_definition']):
        raise ValueError('State/method/coordinate definition are required.')
    points = data['points']
    if not isinstance(points, list) or not 3 <= len(points) <= 1000:
        raise ValueError('Provide 3–1000 scan points in ascending coordinate order.')
    x, energy = [], []
    for row in points:
        if set(row) != {'coordinate', 'energy_hartree', 'state_id', 'method_id', 'converged', 'source_id'}:
            raise ValueError('Every point needs energy, state, method, convergence and source.')
        if row['converged'] is not True or row['state_id'] != parameters['state_id'] or row['method_id'] != parameters['method_id']:
            raise ValueError('Unconverged or discontinuous state/method; derivative is refused.')
        if not isinstance(row['source_id'], str) or not row['source_id']:
            raise ValueError('Every point requires a source.')
        if any(type(row[k]) not in {int, float} for k in ['coordinate', 'energy_hartree']):
            raise ValueError('Finite numeric coordinates and energies are required.')
        x.append(row['coordinate'])
        energy.append(row['energy_hartree'])
    x, energy = np.asarray(x, dtype=float), np.asarray(energy, dtype=float)
    if not np.isfinite(x).all() or not np.isfinite(energy).all() or np.any(np.diff(x) <= 0):
        raise ValueError('Finite points with strictly increasing coordinates required.')
    index = parameters['center_index']
    if type(index) is not int or not 1 <= index < len(points) - 1:
        raise ValueError('center_index must be an interior zero-based integer index.')

    def stencil(indices):
        offsets = x[indices] - x[index]
        scale = float(np.max(np.abs(offsets)))
        z = offsets / scale
        design = np.vstack([np.ones(3), z, z ** 2])
        if np.linalg.cond(design) > 1e8:
            raise ValueError('Ill-conditioned local stencil.')
        values = energy[indices] - energy[index]
        derivatives = []
        for order in [1, 2]:
            rhs = np.zeros(3)
            rhs[order] = math.factorial(order)
            weights = np.linalg.solve(design, rhs) / scale ** order
            derivatives.append(float(weights @ values))
        return {'indices': list(indices), 'offsets': offsets.tolist(), 'first': derivatives[0], 'second': derivatives[1]}

    fine = stencil([index - 1, index, index + 1])
    coarse = stencil([index - 2, index, index + 2]) if 2 <= index < len(points) - 2 else None
    numbers = [fine['first'], fine['second']] + ([coarse['first'], coarse['second']] if coarse else [])
    if not np.isfinite(numbers).all():
        raise ValueError('Derivative overflow.')
    return {'scope': 'LOCAL_FINITE_DIFFERENCES_OF_SUPPLIED_SCAN_NOT_NEW_QUANTUM_ENERGIES',
            'fine': fine, 'coarse': coarse, 'coarse_check': 'EXECUTED' if coarse else 'NOT_EXECUTED_INSUFFICIENT_NEIGHBORS',
            'coarse_minus_fine': [coarse['first'] - fine['first'], coarse['second'] - fine['second']] if coarse else None,
            'derivative_units': ['hartree/' + parameters['coordinate_unit'], 'hartree/(' + parameters['coordinate_unit'] + ')^2'],
            'environment': {'numpy': np.__version__}, 'checks': [],
            'limits': ['Matching state/method labels do not by themselves prove electronic-state continuity.',
                       'Three-point local quadratic interpolation, including nonuniform spacing; no spline or global fit.',
                       'Step-size comparison is diagnostic, not an error bound or convergence certificate.',
                       'Curvature on a scan is not a full vibrational Hessian or unconstrained minimum qualification.']}
