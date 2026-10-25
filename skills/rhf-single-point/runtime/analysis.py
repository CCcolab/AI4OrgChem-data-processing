"""Small real-AO closed-shell RHF result review, independent of the solver."""
import numpy as np
from .support import array, check, keys, metric, scope_result, tolerance


def analyze(parameters, data):
    keys(parameters, ['method', 'basis', 'geometry_id', 'ao_order', 'electron_count',
                      'density_semantics', 'matrix_atol', 'energy_atol_hartree'])
    keys(data, ['overlap', 'coefficients', 'occupations', 'density', 'hcore', 'veff',
                'fock', 'nuclear_hartree', 'reported_total_hartree', 'scf_converged'])
    if parameters['method'] != 'RHF' or parameters['density_semantics'] != 'SPIN_SUMMED_REAL_AO_RHF':
        raise ValueError('Only real spin-summed closed-shell RHF is implemented.')
    if any(not isinstance(parameters[k], str) or not parameters[k].strip()
           for k in ['basis', 'geometry_id', 'ao_order']):
        raise ValueError('Explicit basis, geometry and AO-order identity required.')
    electrons = parameters['electron_count']
    if type(electrons) is not int or electrons <= 0 or electrons % 2:
        raise ValueError('Positive even RHF electron count required.')
    atol, etol = tolerance(parameters['matrix_atol']), tolerance(parameters['energy_atol_hartree'])
    if type(data['scf_converged']) is not bool:
        raise ValueError('SCF convergence must be an explicit Boolean, not inferred from energy.')
    s, _, _ = metric(data['overlap'], atol)
    c, occ = array(data['coefficients'], 2), array(data['occupations'], 1)
    d, h, v, f = [array(data[k], 2) for k in ['density', 'hcore', 'veff', 'fock']]
    if (any(m.shape != s.shape for m in [d, h, v, f]) or c.shape[0] != len(s)
            or c.shape[1] != len(occ) or len(occ) > len(s)):
        raise ValueError('Incompatible real AO dimensions; maximum 128 per dimension.')
    if np.max(np.minimum(abs(occ), abs(occ - 2))) > atol:
        raise ValueError('Only occupations 0/2 are accepted; no silent rounding.')
    if any(type(data[k]) not in {int, float} or not np.isfinite(data[k])
           for k in ['nuclear_hartree', 'reported_total_hartree']):
        raise ValueError('Finite energies in Hartree required.')
    rebuilt = (c * occ) @ c.T
    energy = float(np.trace(d @ h) + .5 * np.trace(d @ v) + data['nuclear_hartree'])
    checks = [check('symmetric_AO_matrices', max(float(np.max(abs(m - m.T))) for m in [d, h, v, f]), atol),
              check('C_metric_orthonormality', np.linalg.norm(c.T @ s @ c - np.eye(len(occ))), atol),
              check('electron_number_Tr_DS', abs(float(np.trace(d @ s)) - electrons), atol),
              check('density_reconstruction', np.linalg.norm(d - rebuilt) / max(np.linalg.norm(d), 1e-15), atol),
              check('closed_shell_idempotency', np.linalg.norm(d @ s @ d - 2 * d) / max(np.linalg.norm(d), 1e-15), atol),
              check('F_equals_hcore_plus_veff', np.linalg.norm(f - h - v), atol),
              check('SCF_commutator_residual', np.linalg.norm(f @ d @ s - s @ d @ f), atol),
              check('energy_ledger_hartree', abs(energy - data['reported_total_hartree']), etol),
              {'name': 'declared_scf_convergence', 'passed': data['scf_converged'],
               'actual': data['scf_converged'], 'threshold': True}]
    return scope_result('SUPPLIED_REAL_AO_RHF_ARRAY_REVIEW_NOT_NEW_SCF_OR_STABILITY', checks,
                        electron_number=float(np.trace(d @ s)), rebuilt_energy_hartree=energy,
                        limits=['Numerical consistency does not prove the physical ground state or RHF stability.',
                                'Method, geometry, AO order and convergence provenance still require source evidence.',
                                'No UHF, DFT, complex orbitals, fractional occupations, periodic cells or ECP convention inference.'])
