"""Read SKILL.md, audit a bounded chemical CSV and produce descriptive statistics.

No imputation, unit conversion, duplicate removal, inference or model call.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import io
import json
import sys
import zipfile

PAGE = Path(__file__).resolve().parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def read_csv(path):
    import pandas as pd

    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2_000_000:
        raise ValueError('CSV must be a regular file no larger than 2 MB.')
    raw = path.read_bytes()
    header = next(csv.reader(io.StringIO(raw.decode('utf-8-sig'))), [])
    if not header or len(header) != len(set(header)):
        raise ValueError('CSV headers must be nonempty and unique; no automatic column renaming.')
    # Read all fields as text: 001, NA and empty fields retain their meaning.
    frame = pd.read_csv(io.StringIO(raw.decode('utf-8-sig')), dtype=str,
                        keep_default_na=False, na_filter=False, on_bad_lines='error')
    if not 1 <= len(frame) <= 10000 or any(str(c).startswith('_adp_') for c in frame.columns):
        raise ValueError('Require 1–10000 rows and no reserved _adp_ columns.')
    return raw, frame


def run_skill(*, input_csv, output_dir, id_column='id', value_column='yield_pct',
              group_column='batch', unit='%', minimum=None, maximum=None,
              lookup_csv=None, lookup_key=None):
    import numpy as np
    import pandas as pd

    if any(value is not None and type(value) not in {int, float} for value in [minimum, maximum]):
        raise ValueError('Range bounds must be real numbers, not text or booleans.')
    if minimum is not None and not np.isfinite(minimum):
        raise ValueError('minimum must be finite.')
    if maximum is not None and not np.isfinite(maximum):
        raise ValueError('maximum must be finite.')
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ValueError('minimum must not exceed maximum.')
    if len({id_column, value_column, group_column}) != 3 or not isinstance(unit, str) or len(unit) > 80:
        raise ValueError('Choose three distinct columns and a short unit label.')
    raw, original = read_csv(input_csv)
    if not {id_column, value_column, group_column}.issubset(original.columns):
        raise ValueError('Missing explicitly selected ID, value or group column.')
    if original[id_column].eq('').any():
        raise ValueError('Empty ID requires correction; repeated nonempty IDs are retained and flagged.')
    output = Path(output_dir).resolve()
    if output.exists() or output.is_relative_to(PAGE):
        raise ValueError('Use a NEW output directory outside the Skill.')
    output.mkdir(parents=True)
    (output / 'input.csv').write_bytes(raw)
    skill = (PAGE / 'SKILL.md').read_bytes()
    (output / 'SKILL.used.md').write_bytes(skill)
    settings = {'id_column': id_column, 'value_column': value_column, 'group_column': group_column,
                'unit': unit, 'minimum': minimum, 'maximum': maximum, 'lookup_key': lookup_key,
                'duplicate_policy': 'FLAG_ALL_RETAIN_ALL', 'statistics': 'DESCRIPTIVE_SAMPLE_SD_DDOF_1'}
    dump(output / 'parameters.json', settings)
    try:
        frame = original.copy(deep=True)
        frame.insert(0, '_adp_record_index', range(1, len(frame) + 1))
        frame['_adp_duplicate_row'] = original.duplicated(keep=False)
        frame['_adp_repeated_id'] = original[id_column].duplicated(keep=False)
        text = original[value_column].str.strip()
        values = pd.to_numeric(text, errors='coerce')
        missing = text.eq('')
        # Distinguish a nonfinite literal from a syntactically unparseable value.
        nonfinite_literal = text.str.lower().isin(['nan', '+nan', '-nan', 'inf', '+inf', '-inf',
                                                  'infinity', '+infinity', '-infinity'])
        invalid = values.isna() & ~missing & ~nonfinite_literal
        nonfinite = nonfinite_literal | (~values.isna() & ~np.isfinite(values))
        outside = pd.Series(False, index=frame.index)
        if minimum is not None:
            outside |= values.lt(minimum)
        if maximum is not None:
            outside |= values.gt(maximum)
        status = pd.Series('VALID', index=frame.index)
        status.loc[outside] = 'OUT_OF_DECLARED_RANGE'
        status.loc[nonfinite] = 'NONFINITE'
        status.loc[invalid] = 'INVALID_NUMERIC'
        status.loc[missing] = 'MISSING'
        frame['_adp_numeric_status'] = status
        frame['_adp_numeric_value'] = values.where(status.eq('VALID'))
        if lookup_csv is not None:
            if not lookup_key or lookup_key not in frame.columns:
                raise ValueError('Choose an existing lookup_key before joining.')
            lookup_raw, lookup = read_csv(lookup_csv)
            (output / 'lookup-input.csv').write_bytes(lookup_raw)
            if lookup_key not in lookup or lookup[lookup_key].eq('').any() or lookup[lookup_key].duplicated().any():
                raise ValueError('Lookup keys must be present, nonempty and unique (many_to_one).')
            if set(frame.columns).intersection(lookup.columns) != {lookup_key}:
                raise ValueError('Lookup columns overlap; rename metadata explicitly before joining.')
            # Empty data keys must not match an empty metadata key.
            frame = frame.merge(lookup, how='left', on=lookup_key, sort=False,
                                validate='many_to_one', indicator='_adp_join_status')
            if len(frame) != len(original) or frame['_adp_record_index'].tolist() != list(range(1, len(original) + 1)):
                raise RuntimeError('Join changed row count or ordering.')
        summary = frame.groupby(group_column, sort=False, dropna=False)['_adp_numeric_value'].agg(
            total_rows='size', valid_count='count', mean='mean', sample_sd='std', minimum='min', maximum='max')
        summary['excluded_count'] = summary['total_rows'] - summary['valid_count']
        summary['unit'] = unit
        frame.to_csv(output / 'audit.csv', index=False)
        frame.loc[~status.eq('VALID')].to_csv(output / 'issues.csv', index=False)
        summary.to_csv(output / 'group-summary.csv')
        if not original.equals(frame[list(original.columns)]):
            raise RuntimeError('Original data changed.')
        receipt = {'status': 'COMPLETE_DESCRIPTIVE_AUDIT', 'records': len(original),
                   'valid_numeric': int(status.eq('VALID').sum()), 'excluded_from_statistics': int((status != 'VALID').sum()),
                   'duplicate_rows_flagged': int(frame['_adp_duplicate_row'].sum()),
                   'repeated_ids_flagged': int(frame['_adp_repeated_id'].sum()),
                   'skill_sha256': sha(skill), 'input_sha256': sha(raw), 'parameters': settings,
                   'environment': {'python': sys.version.split()[0], 'pandas': pd.__version__, 'numpy': np.__version__},
                   'model_calls': 0, 'network_calls': 0,
                   'skill_use': 'READ_AND_SNAPSHOTTED_NO_MODEL_INTERPRETATION',
                   'limitations': ['No deduplication, imputation, unit conversion or independence assumption.',
                                   'Descriptive SD requires n>=2; missing SD stays empty, not zero.',
                                   'No p-values, confidence interval, causal inference or chemical identity certification.']}
        dump(output / 'run-receipt.json', receipt)
    except Exception as error:
        dump(output / 'failure.json', {'status': 'FAILED_INPUT_RETAINED', 'type': type(error).__name__,
                                      'message': str(error), 'model_calls': 0})
        raise
    files = sorted(path for path in output.iterdir() if path.is_file())
    (output / 'SHA256SUMS.txt').write_text(''.join(sha(path.read_bytes()) + '  ' + path.name + '\n' for path in files), encoding='utf-8')
    with zipfile.ZipFile(output / 'results.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files + [output / 'SHA256SUMS.txt']:
            archive.write(path, path.name)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=PAGE / 'runtime/examples/01-replicates.csv')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--id-column', default='id')
    parser.add_argument('--value-column', default='yield_pct')
    parser.add_argument('--group-column', default='batch')
    parser.add_argument('--unit', default='%')
    parser.add_argument('--minimum', type=float)
    parser.add_argument('--maximum', type=float)
    parser.add_argument('--lookup', type=Path)
    parser.add_argument('--lookup-key')
    args = parser.parse_args()
    try:
        print(json.dumps(run_skill(input_csv=args.input, output_dir=args.output, id_column=args.id_column,
                                   value_column=args.value_column, group_column=args.group_column, unit=args.unit,
                                   minimum=args.minimum, maximum=args.maximum,
                                   lookup_csv=args.lookup, lookup_key=args.lookup_key), ensure_ascii=False))
        return 0
    except (ValueError, OSError, RuntimeError, UnicodeError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
