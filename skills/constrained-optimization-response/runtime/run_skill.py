"""Complete bounded Skill call: instructions -> explicit JSON -> tool -> evidence.

This module is copied into each self-contained Skill package. It never invokes
a model, executes supplied expressions, installs dependencies or opens a network.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import platform
import sys
import types
import zipfile

PAGE = Path(__file__).resolve().parents[1]


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


def verify_resources():
    manifest = strict_json((PAGE / 'runtime/resource-manifest.json').read_bytes())
    seen = set()
    for row in manifest:
        name = row['file']
        file = PAGE / name
        if name in seen or file.is_symlink() or not file.resolve().is_relative_to(PAGE):
            raise ValueError('Invalid or repeated resource path.')
        if sha(file.read_bytes()) != row['sha256']:
            raise ValueError('Packaged resource changed: ' + name)
        seen.add(name)
    if not {'SKILL.md', 'runtime/run_skill.py', 'runtime/analysis.py', 'runtime/requirements.txt'}.issubset(seen):
        raise ValueError('Required resource is missing.')


def run_skill(*, request_file, output_dir):
    verify_resources()
    request_file = Path(request_file)
    if request_file.is_symlink() or not request_file.is_file() or request_file.stat().st_size > 2_000_000:
        raise ValueError('Provide a regular JSON request no larger than 2 MB.')
    raw = request_file.read_bytes()
    request = strict_json(raw)
    if not isinstance(request, dict) or set(request) != {'parameters', 'data', 'provenance'}:
        raise ValueError('Require exactly parameters,data,provenance.')
    if not isinstance(request['parameters'], dict) or not isinstance(request['data'], dict):
        raise ValueError('parameters and data must be objects.')
    provenance = request['provenance']
    if (not isinstance(provenance, dict) or set(provenance) != {'kind', 'description'}
            or not all(isinstance(value, str) and value.strip() for value in provenance.values())):
        raise ValueError('Declare provenance kind and description; it is not independently authenticated.')
    output = Path(output_dir).resolve()
    if output.exists() or output.is_relative_to(PAGE):
        raise ValueError('Choose a NEW output directory outside the Skill source.')
    output.mkdir(parents=True)
    skill = (PAGE / 'SKILL.md').read_bytes()
    (output / 'request.json').write_bytes(raw)
    (output / 'SKILL.used.md').write_bytes(skill)
    try:
        path = PAGE / 'runtime/analysis.py'
        package_name = '_skill_' + sha(str(path.parent).encode())[:16]
        if package_name not in sys.modules:
            package = types.ModuleType(package_name)
            package.__path__ = [str(path.parent)]
            sys.modules[package_name] = package
        spec = importlib.util.spec_from_file_location(package_name + '.analysis', path)
        backend = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(backend)
        result = backend.analyze(request['parameters'], request['data'])
        # Backends report all requested gates; a failed gate is not success.
        checks = result.get('checks', [])
        if not isinstance(checks, list) or any(set(row) != {'name', 'passed', 'actual', 'threshold'}
                or type(row['passed']) is not bool for row in checks):
            raise ValueError('Invalid backend check receipt.')
        status = 'COMPLETE_DEFINED_SCOPE' if all(row['passed'] for row in checks) else 'FAILED_NUMERICAL_CHECKS'
        result.update(status=status, provenance=provenance, model_calls=0, network_calls=0,
                      skill_use='READ_AND_SNAPSHOTTED_NO_MODEL_INTERPRETATION',
                      skill_sha256=sha(skill), input_sha256=sha(raw),
                      python=platform.python_version())
        dump(output / 'result.json', result)
        dump(output / 'run-receipt.json', {'status': status, 'skill': PAGE.name,
             'scope': result['scope'], 'input_sha256': sha(raw), 'skill_sha256': sha(skill),
             'model_calls': 0, 'network_calls': 0,
             'scientific_qualification': 'ONLY_EXPLICIT_CHECKS_AND_INPUTS_NOT_GENERAL_METHOD_VALIDATION'})
    except Exception as error:
        dump(output / 'failure.json', {'status': 'FAILED_INPUT_RETAINED', 'type': type(error).__name__,
                                     'message': str(error), 'model_calls': 0, 'network_calls': 0})
        raise
    files = sorted(p for p in output.iterdir() if p.is_file())
    (output / 'SHA256SUMS.txt').write_text(''.join(sha(p.read_bytes()) + '  ' + p.name + '\n' for p in files), encoding='utf-8')
    with zipfile.ZipFile(output / 'results.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files + [output / 'SHA256SUMS.txt']:
            archive.write(path, path.name)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=PAGE / 'runtime/examples/01.json')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = run_skill(request_file=args.input, output_dir=args.output)
        print(result['status'], result['scope'], str(args.output))
        return int(result['status'] != 'COMPLETE_DEFINED_SCOPE')
    except (ValueError, OSError, RuntimeError, ArithmeticError, ImportError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
