"""Prepare/review fixed water, or call an existing registered Runtime once.

No PySCF installation, image building, new registration, settings change, network
or model call. Compute delegates all scientific/lifecycle gates to the preserved
registered molecular-service launcher and never kills it independently.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

PAGE = Path(__file__).resolve().parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def verify_resources():
    rows = json.loads((PAGE / 'runtime/resource-manifest.json').read_bytes())
    seen = set()
    for row in rows:
        path = PAGE / row['file']
        if row['file'] in seen or path.is_symlink() or not path.resolve().is_relative_to(PAGE):
            raise ValueError('Invalid resource path.')
        if sha(path.read_bytes()) != row['sha256']:
            raise ValueError('Resource changed: ' + row['file'])
        seen.add(row['file'])
    if not {'SKILL.md', 'runtime/run_skill.py', 'runtime/fixed-water/request.json',
            'runtime/fixed-water/molecule.xyz', 'runtime/saved-water/arrays.npz'}.issubset(seen):
        raise ValueError('Required resources missing.')


def review_arrays(directory):
    import numpy as np

    directory = Path(directory)
    with np.load(directory / 'arrays.npz', allow_pickle=False) as archive:
        expected = {'overlap', 'density', 'hcore', 'veff', 'fock', 'canonical_coefficients',
                    'occupations', 'orbital_energies_hartree'}
        if set(archive.files) != expected:
            raise ValueError('Fixed water evidence arrays differ.')
        arrays = {key: archive[key] for key in expected}
    matrices = ['overlap', 'density', 'hcore', 'veff', 'fock', 'canonical_coefficients']
    if (any(arrays[key].shape != (18, 18) for key in matrices)
            or any(arrays[key].shape != (18,) for key in ['occupations', 'orbital_energies_hartree'])
            or any(array.dtype.kind != 'f' or not np.isfinite(array).all() for array in arrays.values())):
        raise ValueError('Require finite real 18-AO fixed-water evidence.')
    s, d, c, occupations = [arrays[key] for key in ['overlap', 'density', 'canonical_coefficients', 'occupations']]
    eigenvalues = np.linalg.eigvalsh(s)
    if eigenvalues[0] <= 1e-10 or eigenvalues[-1] / eigenvalues[0] > 1e10:
        raise ValueError('Overlap metric is not admissible.')
    result = json.loads((directory / 'result.json').read_bytes())
    if result.get('basis') != '6-31G(d)' or result.get('density_semantics') != 'SPIN_SUMMED_AO_DENSITY_IN_ORIGINAL_AO_ORDER':
        raise ValueError('Saved result does not match the fixed water convention.')
    energy = result['diagnostics']['energy_ledger']
    rebuilt_energy = float(np.trace(d @ arrays['hcore']) + 0.5 * np.trace(d @ arrays['veff']) + energy['nuclear_repulsion'])
    occupied = c[:, occupations > 0]
    rebuilt_density = (c * occupations) @ c.T
    symmetry = max(float(np.max(abs(arrays[key] - arrays[key].T)))
                   for key in ['overlap', 'density', 'hcore', 'veff', 'fock'])
    values = [
        ('electron_number_Tr_DS', abs(float(np.trace(d @ s)) - 10), 1e-8),
        ('matrix_symmetry', symmetry, 1e-10),
        ('occupied_orthonormality', float(np.linalg.norm(occupied.T @ s @ occupied - np.eye(occupied.shape[1]))), 1e-8),
        ('density_relative_reconstruction', float(np.linalg.norm(d - rebuilt_density) / max(np.linalg.norm(d), 1e-15)), 1e-9),
        ('RHF_energy_ledger', abs(rebuilt_energy - energy['scf_total']), 1e-9),
        ('F_equals_hcore_plus_veff', float(np.max(abs(arrays['fock'] - arrays['hcore'] - arrays['veff']))), 1e-10),
        ('closed_shell_occupations', float(np.max(np.minimum(abs(occupations), abs(occupations - 2)))), 1e-12),
    ]
    checks = [{'name': key, 'actual': value, 'threshold': threshold, 'passed': value <= threshold}
              for key, value, threshold in values]
    return {'scope': 'FIXED_WATER_SAVED_AO_ARRAY_REVIEW_NOT_NEW_SCF', 'checks': checks,
            'electron_number': float(np.trace(d @ s)), 'rebuilt_energy_hartree': rebuilt_energy,
            'environment': {'numpy': np.__version__},
            'limits': ['No new SCF, stability test or physical ground-state certification.',
                       'Full virtual-space orbital qualification not included; no pointwise orbital coefficient comparison.',
                       'Saved metadata/source declarations are not independently authenticated experimental evidence.']}


def registration(runtime_root, record_file, expected_sha256):
    runtime_root, record_file = Path(runtime_root).resolve(), Path(record_file).resolve()
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 or sha(record_file.read_bytes()) != expected_sha256:
        raise ValueError('Installation-record SHA-256 differs; do not re-register automatically.')
    record = json.loads(record_file.read_bytes())
    if (record.get('schema') != 'ai4orgchem-runtime-installation-v1' or record.get('service') != 'molecular-service'
            or record.get('tasks') != ['single-point'] or record.get('modes') != ['live']):
        raise ValueError('This adapter accepts only the existing registered v1 molecular single-point service.')
    for name, digest in record['host_files'].items():
        path = runtime_root / name
        if path.is_symlink() or not path.resolve().is_relative_to(runtime_root) or sha(path.read_bytes()) != digest:
            raise ValueError('Registered host bytes changed: ' + name)
    for name in ['request.json', 'molecule.xyz']:
        if (runtime_root / 'examples/molecular-service/water' / name).read_bytes() != (PAGE / 'runtime/fixed-water' / name).read_bytes():
            raise ValueError('Fixed water request differs from the existing Runtime fixture.')
    return runtime_root, record_file, record


def run_skill(*, mode, output_dir, runtime_root=None, installation_record=None, record_sha256=None, lock_root=None):
    if mode not in {'prepare', 'review', 'compute'}:
        raise ValueError('Choose prepare, review or compute.')
    verify_resources()
    output = Path(output_dir).resolve()
    if output.exists() or output.is_relative_to(PAGE):
        raise ValueError('Use a NEW output directory outside the Skill.')
    if mode != 'compute' and any(value is not None for value in [runtime_root, installation_record, record_sha256, lock_root]):
        raise ValueError('Runtime identity arguments belong only to compute mode.')
    if mode == 'compute' and any(value is None for value in [runtime_root, installation_record, record_sha256, lock_root]):
        raise ValueError('Compute requires explicit existing runtime, record, expected record SHA-256 and shared lock root.')
    output.mkdir(parents=True)
    skill = (PAGE / 'SKILL.md').read_bytes()
    (output / 'SKILL.used.md').write_bytes(skill)
    for name in ['request.json', 'molecule.xyz']:
        shutil.copyfile(PAGE / 'runtime/fixed-water' / name, output / name)
    identity = {'mode': mode, 'model_calls': 0, 'skill_sha256': sha(skill),
                'skill_use': 'READ_AND_SNAPSHOTTED_NO_MODEL_INTERPRETATION',
                'contract': 'skill-rhf-fixed-water-runtime-adapter-v1',
                'science_budget': {'threads': 1, 'memory_bytes': 1073741824, 'soft_seconds': 100,
                                   'hard_seconds': 120, 'max_scf_cycles': 100, 'max_kernel_calls': 1},
                'budget_owner': 'Preserved registered Runtime; startup/cleanup separate, no independent unsafe launcher kill'}
    try:
        if mode == 'prepare':
            receipt = {**identity, 'status': 'PREPARED_NOT_EXECUTED', 'scope': 'FIXED_WATER_INPUT_COPY_ONLY',
                       'new_scf_calls': 0, 'numerical_qualification': 'NOT_EXECUTED'}
        elif mode == 'review':
            reviewed = review_arrays(PAGE / 'runtime/saved-water')
            dump(output / 'saved-array-review.json', reviewed)
            receipt = {**identity, 'status': 'PASS_SAVED_ARRAY_REVIEW' if all(row['passed'] for row in reviewed['checks']) else 'FAIL_SAVED_ARRAY_REVIEW',
                       'scope': reviewed['scope'], 'new_scf_calls': 0}
        else:
            runtime, record_file, record = registration(runtime_root, installation_record, record_sha256)
            docker = shutil.which('docker')
            if docker is None:
                raise RuntimeError('Docker executable unavailable; no installation attempted.')
            probe = subprocess.run([docker, 'info', '--format', '{{json .}}'], capture_output=True, timeout=10)
            (output / 'docker-info.stdout.log').write_bytes(probe.stdout)
            (output / 'docker-info.stderr.log').write_bytes(probe.stderr)
            if probe.returncode != 0:
                raise RuntimeError('Existing Docker Linux engine is unavailable; no SCF was started.')
            info = json.loads(probe.stdout)
            if info.get('OSType') != 'linux':
                raise RuntimeError('Existing engine is not Linux; no configuration change attempted.')
            command = [sys.executable, '-B', str(runtime / 'scripts/run-installed-runtime.py'),
                       '--installation-record', str(record_file), '--task', 'single-point', '--mode', 'live',
                       '--request', str(output / 'request.json'), '--output-root', str(output / 'runtime-run'),
                       '--lock-root', str(Path(lock_root).resolve()), '--docker-executable', docker]
            dump(output / 'compute-command.json', {'argv': command, 'installation_record_sha256': record_sha256,
                                                  'image_id': record['image_id'], 'automatic_retry': False})
            # The original lifecycle supervisor owns all containers and deadlines.
            # Never impose a child kill that could abandon a native worker.
            with (output / 'launcher.stdout.log').open('wb') as stdout, (output / 'launcher.stderr.log').open('wb') as stderr:
                process = subprocess.run(command, stdout=stdout, stderr=stderr)
            if process.returncode != 0:
                raise RuntimeError('Registered Runtime did not pass; preserve its full output and cleanup receipts. Exit ' + str(process.returncode))
            receipt = {**identity, 'status': 'RUNTIME_RETURNED_ZERO_REQUIRES_SCIENTIFIC_RECEIPT_REVIEW',
                       'scope': 'NEW_FIXED_WATER_RUNTIME_EXECUTION', 'runtime_exit_code': process.returncode,
                       'scientific_qualification': 'REVIEW_ORIGINAL_RUNTIME_RECEIPTS_AND_ARRAYS', 'automatic_retry': False}
        dump(output / 'run-receipt.json', receipt)
    except Exception as error:
        dump(output / 'failure.json', {**identity, 'status': 'FAILED_OR_NOT_EXECUTED_INPUT_RETAINED',
                                      'error_type': type(error).__name__, 'message': str(error)})
        raise
    files = sorted(path for path in output.rglob('*') if path.is_file())
    (output / 'SHA256SUMS.txt').write_text(''.join(sha(path.read_bytes()) + '  ' + path.relative_to(output).as_posix() + '\n'
                                                for path in files), encoding='utf-8')
    with zipfile.ZipFile(output / 'results.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files + [output / 'SHA256SUMS.txt']:
            archive.write(path, path.relative_to(output).as_posix())
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['prepare', 'review', 'compute'], default='prepare')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--runtime-root', type=Path)
    parser.add_argument('--installation-record', type=Path)
    parser.add_argument('--record-sha256')
    parser.add_argument('--lock-root', type=Path)
    args = parser.parse_args()
    try:
        receipt = run_skill(mode=args.mode, output_dir=args.output, runtime_root=args.runtime_root,
                            installation_record=args.installation_record, record_sha256=args.record_sha256,
                            lock_root=args.lock_root)
        print(json.dumps(receipt, ensure_ascii=False))
        return int(receipt['status'].startswith('FAIL'))
    except (ValueError, OSError, RuntimeError, ArithmeticError, ImportError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
