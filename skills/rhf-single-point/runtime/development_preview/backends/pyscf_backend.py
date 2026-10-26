"""Optional existing-PySCF adapter: one RHF or one occupied-space localizer.

No installation, Runtime registration, Docker, WSL launch or model calls. Import
errors are failures, never replaced with synthetic output. This is an in-process
example with cooperative time checks, NOT hard CPU/memory/time containment.
"""
from pathlib import Path
import json
import math
import platform
import time


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def number(value, minimum, maximum, name, integer=False):
    if (type(value) not in ({int} if integer else {int, float}) or not math.isfinite(value)
            or not minimum <= value <= maximum):
        raise ValueError('Invalid explicit ' + name)
    return value


def validate_native(request):
    p = request['parameters']
    base = {'task', 'atoms', 'unit', 'basis', 'charge', 'spin_2s', 'threads',
            'max_memory_mb', 'max_cycle', 'conv_tol', 'conv_tol_grad', 'soft_seconds', 'review_atol'}
    if p.get('task') == 'localize':
        base |= {'localization', 'population_method'}
    if set(p) != base or p['task'] not in {'rhf', 'localize'}:
        raise ValueError('Explicit native parameter schema required; see native-request.json.')
    if p['unit'] not in {'angstrom', 'bohr'} or not isinstance(p['basis'], str) or not p['basis'].strip():
        raise ValueError('Explicit common coordinate unit and named all-electron basis required.')
    number(p['charge'], -20, 20, 'charge', True)
    if type(p['spin_2s']) is not int or p['spin_2s'] != 0:
        raise ValueError('Only closed-shell spin_2s=0 is supported.')
    for key, lo, hi in [('threads', 1, 16), ('max_memory_mb', 128, 16384), ('max_cycle', 1, 200)]:
        number(p[key], lo, hi, key, True)
    for key, lo, hi in [('conv_tol', 1e-12, 1e-5), ('conv_tol_grad', 1e-10, 1e-3),
                        ('soft_seconds', 1, 3600), ('review_atol', 1e-12, 1e-4)]:
        number(p[key], lo, hi, key)
    atoms = p['atoms']
    if not isinstance(atoms, list) or not 1 <= len(atoms) <= 32:
        raise ValueError('Provide 1..32 atoms as [element, [x,y,z]].')
    for atom in atoms:
        if (not isinstance(atom, list) or len(atom) != 2 or not isinstance(atom[0], str)
                or not atom[0].isalpha() or len(atom[0]) > 2
                or not isinstance(atom[1], list) or len(atom[1]) != 3):
            raise ValueError('Invalid atom record; no expression or XYZ parsing.')
        for coordinate in atom[1]:
            number(coordinate, -1000, 1000, 'coordinate')
    if p['task'] == 'rhf' and request['data']:
        raise ValueError('RHF native task uses atoms in parameters and empty data.')
    if p['task'] == 'localize':
        if p['localization'] not in {'boys', 'pm'} or p['population_method'] != 'meta_lowdin':
            raise ValueError('Choose boys/pm; PM example uses explicit meta_lowdin population.')
        if set(request['data']) != {'overlap', 'occupied_coefficients', 'ao_labels'}:
            raise ValueError('Localizer requires existing occupied coefficients, overlap and exact AO labels.')
    return p


def run_backend(request, output_dir):
    p = validate_native(request)
    dump(output_dir / 'native-settings.json', p)
    # Optional imports happen only in explicitly selected backend mode.
    import numpy as np
    import pyscf
    from pyscf import gto, lib, lo, scf

    started = time.monotonic()
    lib.num_threads(p['threads'])
    if lib.num_threads() != p['threads']:
        raise RuntimeError('Requested thread count was not applied.')
    logfile = output_dir / 'native.log'
    mol = gto.M(atom=p['atoms'], unit=p['unit'], basis=p['basis'], charge=p['charge'],
                spin=p['spin_2s'], cart=False, verbose=4, output=str(logfile),
                max_memory=p['max_memory_mb'])
    try:
        if mol.nao_nr() > 128 or mol.nelectron <= 0 or mol.nelectron % 2 or mol.nelectron > 2 * mol.nao_nr():
            raise ValueError('Require 1..128 real spherical AOs and a representable positive even electron count.')
        # Mole.has_ecp() covers its pseudopotential flag as well; Mole has no
        # separate public has_pseudo() method in the reference API.
        if mol.has_ecp():
            raise ValueError('This template does not define ECP/pseudopotential density/energy conventions.')
        s = mol.intor_symmetric('int1e_ovlp')
        w = np.linalg.eigvalsh(s)
        if w[0] <= 1e-10 or w[-1] / w[0] > 1e10:
            raise ValueError('Ill-conditioned overlap; no rank truncation or basis substitution.')
        history = []

        def time_check():
            if time.monotonic() - started > p['soft_seconds']:
                raise TimeoutError('Cooperative time allowance exceeded; no hard process containment is claimed.')

        if p['task'] == 'rhf':
            solver = scf.RHF(mol)
            solver.max_memory, solver.max_cycle = p['max_memory_mb'], p['max_cycle']
            solver.conv_tol, solver.conv_tol_grad = p['conv_tol'], p['conv_tol_grad']

            def callback(env):
                row = {'cycle': int(env['cycle']), 'energy_hartree': float(env['e_tot'])}
                if 'norm_gorb' in env:
                    row['gradient_norm'] = float(env['norm_gorb'])
                history.append(row)
                dump(output_dir / 'iteration-history.json', history)
                time_check()

            solver.callback = callback
            time_check()
            dump(output_dir / 'native-call-counters.json', {'scf_kernel_entered': 1, 'scf_kernel_returned': 0,
                                                           'localization_kernel_entered': 0})
            total = float(solver.kernel())  # exactly one SCF kernel; no retry/fallback
            dump(output_dir / 'native-call-counters.json', {'scf_kernel_entered': 1, 'scf_kernel_returned': 1,
                                                           'localization_kernel_entered': 0})
            time_check()
            c, occupations = np.asarray(solver.mo_coeff), np.asarray(solver.mo_occ)
            d = solver.make_rdm1()
            h, v = solver.get_hcore(), solver.get_veff(mol, d)
            # Save numerical products BEFORE deciding whether the endpoint is qualified.
            np.savez(output_dir / 'native-arrays.npz', overlap=s, coefficients=c,
                     occupations=occupations, density=d, hcore=h, veff=v, fock=h + v)
            dump(output_dir / 'native-endpoint.json', {'energy_hartree': total,
                 'scf_converged': bool(solver.converged), 'ao_labels': mol.ao_labels(),
                 'stability_test': 'NOT_EXECUTED'})
            data = {k: a.tolist() for k, a in {'overlap': s, 'coefficients': c, 'occupations': occupations,
                    'density': d, 'hcore': h, 'veff': v, 'fock': h + v}.items()}
            data.update(nuclear_hartree=float(mol.energy_nuc()), reported_total_hartree=total,
                        scf_converged=bool(solver.converged))
            parameters = {'method': 'RHF', 'basis': p['basis'], 'geometry_id': 'native-settings.json atoms/unit/charge/spin',
                          'ao_order': 'PySCF spherical AO order; labels in native-endpoint.json',
                          'electron_count': int(mol.nelectron), 'density_semantics': 'SPIN_SUMMED_REAL_AO_RHF',
                          'matrix_atol': p['review_atol'], 'energy_atol_hartree': p['review_atol']}
            calls = {'scf_kernel': 1, 'localization_kernel': 0}
        else:
            # Raw real leaf checks before NumPy promotion; no Boolean/string coercion.
            def real_array(value, ndim):
                pending = [value]
                count = 0
                while pending:
                    item = pending.pop()
                    count += 1
                    if count > 100000:
                        raise ValueError('Array traversal limit.')
                    if isinstance(item, list):
                        pending.extend(item)
                    elif type(item) not in {int, float} or not math.isfinite(item):
                        raise ValueError('Require finite real numeric array leaves.')
                a = np.asarray(value, dtype=float)
                if a.ndim != ndim or not a.size or max(a.shape) > 128:
                    raise ValueError('Invalid bounded real AO array.')
                return a

            supplied_s = real_array(request['data']['overlap'], 2)
            c = real_array(request['data']['occupied_coefficients'], 2)
            if (supplied_s.shape != s.shape or c.shape != (len(s), mol.nelectron // 2)
                    or request['data']['ao_labels'] != mol.ao_labels()
                    or np.max(abs(supplied_s - s)) > p['review_atol']
                    or np.linalg.norm(c.T @ s @ c - np.eye(c.shape[1])) > p['review_atol']):
                raise ValueError('Molecule/basis/AO labels/metric/occupied subspace do not match existing orbitals.')
            if c.shape[1] < 2:
                raise ValueError('Use at least two occupied orbitals for this optimizer demonstration.')
            solver = lo.Boys(mol, c) if p['localization'] == 'boys' else lo.PM(mol, c)
            if p['localization'] == 'pm':
                solver.pop_method = p['population_method']
            solver.max_cycle = p['max_cycle']
            solver.conv_tol, solver.conv_tol_grad = p['conv_tol'], p['conv_tol_grad']

            def callback(env):
                required = {'imacro', 'conv', 'norm_gorb', 'de', 'e', 'stat'}
                if not required <= env.keys():
                    raise RuntimeError('Unsupported PySCF localization callback schema; do not infer convergence.')
                history.append({'macro_cycle': int(env['imacro']) + 1, 'converged': bool(env['conv']),
                                'gradient_norm': float(env['norm_gorb']), 'objective_change': float(env['de']),
                                'objective': float(env['e']), 'hessian_operations': int(env['stat'].tot_hop)})
                dump(output_dir / 'iteration-history.json', history)
                time_check()

            time_check()
            dump(output_dir / 'native-call-counters.json', {'scf_kernel_entered': 0,
                  'localization_kernel_entered': 1, 'localization_kernel_returned': 0})
            localized = solver.kernel(callback=callback)  # one localizer; NO SCF/retry
            dump(output_dir / 'native-call-counters.json', {'scf_kernel_entered': 0,
                  'localization_kernel_entered': 1, 'localization_kernel_returned': 1})
            time_check()
            u = c.T @ s @ localized
            np.savez(output_dir / 'native-arrays.npz', overlap=s, coefficients=c,
                     localized_coefficients=localized, rotation=u)
            # kernel mutates solver.mo_coeff; evaluate at returned orbitals,
            # rather than applying the old rotation a second time.
            endpoint = lo.Boys(mol, localized) if p['localization'] == 'boys' else lo.PM(mol, localized)
            if p['localization'] == 'pm':
                endpoint.pop_method = p['population_method']
            endpoint_gradient = float(np.linalg.norm(endpoint.get_grad()))
            qualified = bool(history and history[-1]['converged']
                             and endpoint_gradient < p['conv_tol_grad']
                             and abs(history[-1]['objective_change']) < p['conv_tol'])
            dump(output_dir / 'native-endpoint.json', {'optimizer_converged': qualified,
                 'endpoint_gradient_norm': endpoint_gradient, 'objective': p['localization'],
                 'population_method': p['population_method'] if p['localization'] == 'pm' else 'NOT_APPLICABLE',
                 'ao_labels': mol.ao_labels(), 'scf_calls': 0})
            if not qualified:
                raise RuntimeError('Localizer endpoint not qualified; partial arrays and optimizer evidence retained.')
            data = {'overlap': s.tolist(), 'coefficients': c.tolist(), 'rotation': u.tolist(),
                    'occupations': [2] * c.shape[1]}
            parameters = {'atol': p['review_atol'], 'density_semantics': 'SPIN_SUMMED_REAL_AO_RHF'}
            calls = {'scf_kernel': 0, 'localization_kernel': 1}
        return {'review_request': {'parameters': parameters, 'data': data,
                'provenance': {'kind': 'USER_EXISTING_PYSCF_BACKEND',
                               'description': 'New native call; see native-settings/log/arrays/endpoint and iteration history.'}},
                'execution': {'kind': 'NATIVE_PYSCF_' + p['task'].upper(), 'software': 'PySCF',
                              'version': pyscf.__version__, 'numpy': np.__version__, 'python': platform.python_version(),
                              'calls': calls, 'model_calls': 0, 'network_calls': 0,
                              'elapsed_seconds': time.monotonic() - started,
                              'resources': {'threads': lib.num_threads(), 'max_memory_mb_advisory': p['max_memory_mb'],
                                            'soft_seconds_cooperative': p['soft_seconds'],
                                            'hard_limits': 'NOT_ENFORCED_BY_THIS_IN_PROCESS_TEMPLATE'}}}
    finally:
        if mol.stdout is not None and not mol.stdout.closed:
            mol.stdout.flush()
            mol.stdout.close()
