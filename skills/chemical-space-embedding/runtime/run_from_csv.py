"""Convert explicit CSV columns to a Skill request and call the complete runner.

No guessing column names, filling targets or importing arbitrary model files.
The original CSV text and declared units are preserved in request.json.
"""
from pathlib import Path
import argparse
import csv
import importlib.util
import io
import json
import tempfile

PAGE = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template', type=Path, required=True)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--id-column', default='id')
    parser.add_argument('--features', nargs='+', required=True)
    parser.add_argument('--feature-units', nargs='+', required=True)
    parser.add_argument('--target')
    parser.add_argument('--target-unit')
    parser.add_argument('--groups')
    args = parser.parse_args()
    if len(args.features) != len(args.feature_units) or len(set(args.features)) != len(args.features):
        parser.error('Declare one unit per unique feature column.')
    if bool(args.target) != bool(args.target_unit):
        parser.error('--target and --target-unit must be provided together.')
    if any(name in args.features for name in [args.id_column, args.target, args.groups] if name is not None):
        parser.error('ID, target and group columns cannot also be selected as numeric features.')
    for path in [args.input, args.template]:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 128000:
            parser.error('Use regular bounded UTF-8 input/template files <=128000 bytes.')
    spec = importlib.util.spec_from_file_location('skill_entry', PAGE / 'runtime/run_skill.py')
    api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    api.verify_resources()
    template = api.strict_json(args.template.read_bytes())
    text = args.input.read_bytes().decode('utf-8-sig')
    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    required = {args.id_column, *args.features} | ({args.target} if args.target else set()) | ({args.groups} if args.groups else set())
    if (not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)) or not required.issubset(reader.fieldnames)
            or not 5 <= len(rows) <= 200 or any(None in row or None in row.values() for row in rows)):
        parser.error('Declare existing unique headers and 5–200 complete rows.')
    data = {'ids': [row[args.id_column] for row in rows], 'features': [[float(row[name]) for name in args.features] for row in rows],
            'feature_names': args.features, 'feature_units': args.feature_units, 'source_csv_text': text}
    if args.target:
        data.update(target=[float(row[args.target]) for row in rows], target_unit=args.target_unit)
    if args.groups:
        data['groups'] = [row[args.groups] for row in rows]
    request = {'parameters': template['parameters'], 'data': data,
               'provenance': {'kind': 'USER_PROVIDED_CSV', 'description': 'Explicit selected columns and units; original CSV text retained, not authenticated experimental data.'}}
    args.output.resolve().parent.mkdir(parents=True, exist_ok=True)
    # The transient request is outside the Skill and is removed after its exact
    # contents are snapshotted into the final new result directory.
    with tempfile.TemporaryDirectory(prefix='skill-csv-', dir=args.output.resolve().parent) as work:
        path = Path(work) / 'request.json'
        path.write_text(json.dumps(request, ensure_ascii=False, allow_nan=False), encoding='utf-8')
        result = api.run_skill(request_file=path, output_dir=args.output)
    print(result['status'], result['scope'])
    return int(result['status'] != 'COMPLETE_DEFINED_SCOPE')


if __name__ == '__main__':
    raise SystemExit(main())
