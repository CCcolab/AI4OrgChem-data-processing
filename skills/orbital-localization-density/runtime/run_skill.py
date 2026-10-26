"""Verified-scope input preparation, supplied result review and JSON file import.

No model, installer, shell command, Runtime registration or container launcher.
This ordinary entry never imports a user-selected Python backend.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import importlib.util
import json
import platform
import sys
import types
import zipfile

PAGE = Path(__file__).resolve().parents[1]
CONTRACT = 'local-skill-review-v1'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def strict_json(raw):
    return json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Nonfinite JSON: ' + value)))


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def validate_request(request):
    if not isinstance(request, dict) or set(request) != {'parameters', 'data', 'provenance'}:
        raise ValueError('Require exactly parameters, data, provenance.')
    if not isinstance(request['parameters'], dict) or not isinstance(request['data'], dict):
        raise ValueError('parameters and data must be objects.')
    source = request['provenance']
    if (not isinstance(source, dict) or set(source) != {'kind', 'description'}
            or not all(isinstance(v, str) and v.strip() for v in source.values())):
        raise ValueError('Declare provenance kind and description; labels are not authenticated evidence.')
    # Also validate Python backend returns: json.dumps rejects NaN/Infinity.
    json.dumps(request, allow_nan=False)


def verify_resources():
    rows = strict_json((PAGE / 'runtime/resource-manifest.json').read_bytes())
    if not isinstance(rows, list) or not rows:
        raise ValueError('Require a nonempty resource manifest.')
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'file', 'sha256'}:
            raise ValueError('Invalid manifest entry.')
        name = row['file']
        if not isinstance(name, str):
            raise ValueError('Invalid resource name.')
        relative = Path(name)
        path = PAGE / relative
        if (relative.is_absolute() or '..' in relative.parts or name in seen
                or path.is_symlink() or not path.resolve().is_relative_to(PAGE)
                or any(parent.is_symlink() for parent in path.parents if parent != PAGE)):
            raise ValueError('Invalid or repeated resource path.')
        if sha(path.read_bytes()) != row['sha256']:
            raise ValueError('Packaged resource changed: ' + name + '; copy editable inputs outside this package.')
        seen.add(name)
    if not {'README.md', 'SKILL.md', 'runtime/run_skill.py', 'runtime/analysis.py',
            'runtime/requirements.txt', 'runtime/result_file.py'}.issubset(seen):
        raise ValueError('Required resource missing.')


def load_module(path, name, package_directory=None):
    if package_directory is not None:
        package = types.ModuleType(name)
        package.__path__ = [str(package_directory)]
        sys.modules[name] = package
        name += '.analysis'
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError('Provide a regular .py backend file.')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def seal_output(output):
    items = sorted(output.rglob('*'))
    if any(p.is_symlink() or not p.resolve().is_relative_to(output) for p in items):
        raise ValueError('Symlink or escaping output artifact rejected; do not archive it.')
    reserved = {'SHA256SUMS.txt', 'results.zip', 'results.zip.sha256'}
    if any((output / name).exists() for name in reserved):
        raise ValueError('Backend must not create reserved output names.')
    files = [p for p in items if p.is_file()]
    sums = output / 'SHA256SUMS.txt'
    sums.write_text(''.join(sha(p.read_bytes()) + '  ' + p.relative_to(output).as_posix() + '\n'
                            for p in files), encoding='utf-8')
    archive_path = output / 'results.zip'
    with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files + [sums]:
            archive.write(path, path.relative_to(output).as_posix())
    (output / 'results.zip.sha256').write_text(sha(archive_path.read_bytes()) + '  results.zip\n', encoding='utf-8')


def run_skill(*, mode, request_file, output_dir, backend_file=None, execute=False):
    if mode not in {'prepare', 'review', 'import'}:
        raise ValueError('Use prepare, review or import; real backend calls are only in development_preview/run_backend.py.')
    if execute or backend_file is not None:
        raise ValueError('The ordinary entry never executes user Python backends; see development_preview/README.md.')
    verify_resources()
    request_file = Path(request_file)
    if request_file.is_symlink() or not request_file.is_file() or request_file.stat().st_size > 2_000_000:
        raise ValueError('Provide a regular JSON file no larger than 2 MB.')
    raw = request_file.read_bytes()
    output = Path(output_dir).resolve()
    if output.exists() or output.is_relative_to(PAGE):
        raise ValueError('Use a NEW output directory outside the Skill package.')
    output.mkdir(parents=True)
    skill = (PAGE / 'SKILL.md').read_bytes()
    (output / 'request.json').write_bytes(raw)
    (output / 'SKILL.used.md').write_bytes(skill)
    receipt = {'contract': CONTRACT, 'skill': PAGE.name, 'mode': mode,
               'skill_sha256': sha(skill), 'input_sha256': sha(raw),
               'skill_use': 'READ_AND_SNAPSHOTTED_NO_MODEL_INTERPRETATION',
               'python': platform.python_version(), 'runner_model_calls': 0,
               'runner_network_calls': 0, 'backend_calls': 0,
               'backend_import_attempts': 0,
               'backend_execution_kind': 'NOT_EXECUTED',
               'result_file_imports': 0,
               'backend_behavior': 'UNAVAILABLE_IN_ORDINARY_ENTRY',
               'scientific_qualification': 'EXPLICIT_INPUTS_AND_CHECKS_ONLY'}
    error = None
    try:
        request = strict_json(raw)
        validate_request(request)
        if mode == 'prepare':
            receipt.update(status='PREPARED_NOT_EXECUTED', scope='INPUT_SNAPSHOT_AND_REVIEW_PLAN_ONLY')
            dump(output / 'input-plan.json', {
                'contract': CONTRACT, 'required_request_root': ['parameters', 'data', 'provenance'],
                'next_step': 'Supply a review request or import existing normalized result JSON',
                'available_modes': ['review', 'import'], 'new_solver_calls': 0,
                'science_input_validation': 'NOT_EXECUTED',
                'real_backend_entry': 'SEPARATE_DEVELOPMENT_PREVIEW_ONLY'})
        else:
            reviewed = copy.deepcopy(request)
            if mode == 'import':
                receipt['result_file_imports'] = 1
                provider = load_module(PAGE / 'runtime/result_file.py', '_result_file_' + sha(str(PAGE).encode())[:16])
                returned = provider.read_result_file(request, output)
                dump(output / 'import-return.json', returned)
                reviewed = returned['review_request']
                validate_request(reviewed)
                receipt['result_file_import'] = returned['execution']
            dump(output / 'review-request.json', reviewed)
            module = load_module(PAGE / 'runtime/analysis.py', '_review_' + sha(str(PAGE).encode())[:16], PAGE / 'runtime')
            result = module.analyze(reviewed['parameters'], reviewed['data'])
            checks = result.get('checks')
            if (not isinstance(checks, list) or not checks
                    or any(not isinstance(row, dict) or set(row) != {'name', 'passed', 'actual', 'threshold'}
                           or type(row['passed']) is not bool for row in checks)):
                raise ValueError('Nonempty explicit mathematical check list required.')
            status = 'COMPLETE_DEFINED_SCOPE' if all(row['passed'] for row in checks) else 'FAILED_NUMERICAL_CHECKS'
            result.update(status=status, provenance=reviewed['provenance'], skill_sha256=sha(skill),
                          skill_use=receipt['skill_use'])
            dump(output / 'result.json', result)
            receipt.update(status=status, scope=result['scope'])
    except Exception as caught:
        error = caught
        receipt.update(status='FAILED_PARTIAL_OUTPUT_RETAINED')
        dump(output / 'failure.json', {'status': receipt['status'], 'type': type(caught).__name__,
                                      'message': str(caught), 'retry': 'NOT_ATTEMPTED'})
    dump(output / 'run-receipt.json', receipt)
    seal_output(output)
    if error is not None:
        raise RuntimeError(str(error)) from error
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['prepare', 'review', 'import'], default='review')
    parser.add_argument('--input', type=Path, default=PAGE / 'runtime/examples/01.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        receipt = run_skill(mode=args.mode, request_file=args.input, output_dir=args.output)
        print(receipt['status'], str(args.output))
        return int(receipt['status'] == 'FAILED_NUMERICAL_CHECKS')
    except Exception as error:
        print(type(error).__name__ + ': ' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
