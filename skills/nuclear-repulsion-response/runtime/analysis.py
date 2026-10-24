"""Finite nonperiodic point nuclei: pair Coulomb energy and Cartesian derivatives."""
import numpy as np

BOHR_ANGSTROM = 0.529177210544  # CODATA 2022; independent new module, not frozen core units.


def analyze(parameters, data):
    if set(parameters) != {'coordinate_unit'} or parameters['coordinate_unit'] not in {'bohr', 'angstrom'} or set(data) != {'nuclei'}:
        raise ValueError('Declare coordinate_unit bohr/angstrom and nuclei.')
    rows = data['nuclei']
    if not isinstance(rows, list) or not 2 <= len(rows) <= 64:
        raise ValueError('Provide 2–64 finite nonperiodic nuclei.')
    ids, charges, coordinates = [], [], []
    for row in rows:
        if set(row) != {'id', 'Z', 'xyz'} or not isinstance(row['id'], str) or not row['id'] or row['id'] in ids:
            raise ValueError('Require unique string IDs and exact fields id,Z,xyz.')
        if type(row['Z']) is not int or not 1 <= row['Z'] <= 86:
            raise ValueError('Z must be the actual integer nuclear charge in [1,86], not a fitted or ECP charge.')
        xyz = row['xyz']
        if not isinstance(xyz, list) or len(xyz) != 3 or any(type(v) not in {int, float} for v in xyz):
            raise ValueError('Three finite numeric Cartesian coordinates required.')
        ids.append(row['id'])
        charges.append(row['Z'])
        coordinates.append(xyz)
    coordinates = np.asarray(coordinates, dtype=float)
    if not np.isfinite(coordinates).all():
        raise ValueError('Nonfinite coordinates.')
    factor = 1 / BOHR_ANGSTROM if parameters['coordinate_unit'] == 'angstrom' else 1.0
    r = coordinates * factor
    gradient = np.zeros_like(r)
    hessian = np.zeros((len(rows) * 3, len(rows) * 3))
    energy, pairs = 0.0, []
    for i in range(len(rows)):
        for j in range(i):
            vector = r[i] - r[j]
            distance = float(np.linalg.norm(vector))
            if not np.isfinite(distance) or distance < 1e-6:
                raise ValueError('Coincident/near-coincident or overflowing nuclear separation; refused.')
            product = charges[i] * charges[j]
            pair_energy = product / distance
            pair_gradient = -product * vector / distance ** 3
            block = product * (3 * np.outer(vector, vector) / distance ** 5 - np.eye(3) / distance ** 3)
            energy += pair_energy
            gradient[i] += pair_gradient
            gradient[j] -= pair_gradient
            for a, b, sign in [(i, i, 1), (j, j, 1), (i, j, -1), (j, i, -1)]:
                hessian[3 * a:3 * a + 3, 3 * b:3 * b + 3] += sign * block
            pairs.append({'i': ids[j], 'j': ids[i], 'distance_bohr': distance, 'energy_hartree': pair_energy})
    gradient *= factor
    hessian *= factor ** 2
    if not np.isfinite(energy) or not np.isfinite(gradient).all() or not np.isfinite(hessian).all():
        raise ValueError('Numerical overflow.')
    unit = parameters['coordinate_unit']
    return {'scope': 'NUCLEAR_COULOMB_TERM_ONLY_NO_ELECTRONIC_OR_TOTAL_MOLECULAR_ENERGY',
            'energy_hartree': energy, 'pairs': pairs, 'gradient': gradient.tolist(), 'force': (-gradient).tolist(),
            'hessian': hessian.tolist(), 'gradient_unit': 'hartree/' + unit,
            'hessian_unit': 'hartree/(' + unit + ')^2', 'force_definition': '-gradient',
            'bohr_angstrom': BOHR_ANGSTROM, 'constant_source': 'NIST CODATA 2022',
            'environment': {'numpy': np.__version__},
            'checks': [{'name': 'zero_net_gradient_translation', 'passed': bool(np.linalg.norm(gradient.sum(axis=0)) < 1e-9),
                        'actual': float(np.linalg.norm(gradient.sum(axis=0))), 'threshold': 1e-9},
                       {'name': 'Hessian_symmetry', 'passed': bool(np.max(abs(hessian - hessian.T)) < 1e-9),
                        'actual': float(np.max(abs(hessian - hessian.T))), 'threshold': 1e-9}],
            'limits': ['Nonperiodic point nuclei only, no electrons, ECP corrections, solvent or external charges.',
                       'The nuclear term and its force do not determine the molecular equilibrium geometry.',
                       'Near-coincident cutoff and residual thresholds are explicit engineering safeguards.']}
