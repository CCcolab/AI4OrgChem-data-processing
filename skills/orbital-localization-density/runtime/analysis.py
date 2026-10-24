"""Review an explicitly supplied orbital rotation; does not run a localizer."""
import numpy as np
from .support import array, check, keys, metric, require_rows, scope_result, tolerance


def analyze(parameters, data):
    keys(parameters, ['atol', 'density_semantics'])
    keys(data, ['overlap', 'coefficients', 'occupations', 'rotation'], ['hcore', 'veff', 'nuclear_hartree'])
    atol = tolerance(parameters['atol'])
    if parameters['density_semantics'] != 'SPIN_SUMMED_REAL_AO_RHF':
        raise ValueError('Only declared real spin-summed RHF AO density is implemented.')
    s, _, _ = metric(data['overlap'], atol)
    c = array(data['coefficients'], 2)
    require_rows(c, len(s), 'coefficients')
    occ, u = array(data['occupations'], 1), array(data['rotation'], 2)
    if c.shape[1] != len(occ) or u.shape != (len(occ), len(occ)) or len(occ) > len(s):
        raise ValueError('C, occupation and rotation dimensions differ.')
    if np.max(np.minimum(abs(occ), abs(occ - 2))) > atol:
        raise ValueError('Only occupations 0/2 to the declared tolerance are admitted; no rounding is applied.')
    rotated = c @ u
    d = (c * occ) @ c.T
    d2 = (rotated * occ) @ rotated.T
    checks = [check('C_metric_orthonormality', np.linalg.norm(c.T @ s @ c - np.eye(len(occ))), atol),
              check('rotation_orthogonality', np.linalg.norm(u.T @ u - np.eye(len(occ))), atol),
              check('occupation_commutation', np.linalg.norm(u @ np.diag(occ) @ u.T - np.diag(occ)), atol),
              check('density_relative_difference', np.linalg.norm(d2 - d) / max(np.linalg.norm(d), 1e-15), atol),
              check('electron_number_preservation', abs(np.trace(d2 @ s) - np.trace(d @ s)), atol)]
    energies = None
    if set(data).intersection({'hcore', 'veff', 'nuclear_hartree'}):
        if not {'hcore', 'veff', 'nuclear_hartree'}.issubset(data):
            raise ValueError('Energy comparison requires hcore, veff and nuclear_hartree together.')
        h, v = array(data['hcore'], 2), array(data['veff'], 2)
        if h.shape != s.shape or v.shape != s.shape or type(data['nuclear_hartree']) not in {int, float} or not np.isfinite(data['nuclear_hartree']):
            raise ValueError('Invalid energy evidence.')
        if np.max(abs(h - h.T)) > atol or np.max(abs(v - v.T)) > atol:
            raise ValueError('Energy matrices are not symmetric.')
        before = float(np.trace(d @ h) + .5 * np.trace(d @ v) + data['nuclear_hartree'])
        after = float(np.trace(d2 @ h) + .5 * np.trace(d2 @ v) + data['nuclear_hartree'])
        energies = {'before_hartree': before, 'after_hartree': after, 'fixed_veff_comparison': True}
        checks.append(check('fixed_density_energy_preservation_hartree', abs(after - before), atol))
    return scope_result('SUPPLIED_ORBITAL_ROTATION_AND_DENSITY_REVIEW_NOT_LOCALIZATION_OR_NEW_SCF', checks,
                        rotated_coefficients=rotated.tolist(), density_before=d.tolist(), density_after=d2.tolist(),
                        electron_number=float(np.trace(d @ s)), energy_comparison=energies,
                        energy_check='EXECUTED_FIXED_MATRICES' if energies else 'NOT_EXECUTED_MISSING_OPTIONAL_MATRICES',
                        limits=['No Boys/Pipek-Mezey objective optimization or localized-orbital chemical classification.',
                                'Only equal-occupation rotations preserve this density; occupied/virtual mixing is not invariant.',
                                'Fixed hcore/veff energy comparison is not a new self-consistent endpoint or stability test.'])
