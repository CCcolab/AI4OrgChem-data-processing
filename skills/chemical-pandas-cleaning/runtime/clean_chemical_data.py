"""Read SKILL.md, audit a bounded chemical CSV and produce descriptive statistics.

No imputation, unit conversion, duplicate removal, inference or model call.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import io
import json
import math
import statistics
import sys
import zipfile

PAGE = Path(__file__).resolve().parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def archive_results(output):
    files = sorted(path for path in output.iterdir() if path.is_file())
    (output / 'SHA256SUMS.txt').write_text(''.join(sha(path.read_bytes()) + '  ' + path.name + '\n'
                                                for path in files), encoding='utf-8')
    with zipfile.ZipFile(output / 'results.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files + [output / 'SHA256SUMS.txt']:
            archive.write(path, path.name)


def descriptive_summary(values):
    """Finite float summaries using Python3.12's integer-ratio accumulators.

    Do not pass a rounded float mean to stdev: its default implementation
    retains the exact sum-of-squares arithmetic before the final square root.
    A defined but unrepresentable SD is a calculation failure, not missing SD.
    """
    values = [float(value) for value in values]
    count = len(values)
    if not count:
        return {'mean': None, 'sample_sd': None, 'minimum': None, 'maximum': None,
                'sample_sd_status': 'UNDEFINED_N_LT_2'}
    try:
        mean = statistics.mean(values)
        sd = statistics.stdev(values) if count > 1 else None
        if not math.isfinite(mean) or (sd is not None and not math.isfinite(sd)):
            raise OverflowError('Nonfinite derived statistic.')
        if mean == 0.0:
            # Only the zero-output branch needs an exact cancellation check.
            # Dividing by n before summing could lose a representable small sum.
            from fractions import Fraction
            exact_sum = sum((Fraction.from_float(value) for value in values if value), Fraction(0))
            if exact_sum:
                raise OverflowError('Nonzero mean underflowed to zero in the float output.')
        if sd == 0.0 and min(values) != max(values):
            raise OverflowError('Nonzero sample SD underflowed to zero in the float output.')
    except (OverflowError, ValueError) as error:
        raise ArithmeticError('DERIVED_STATISTIC_NOT_REPRESENTABLE: ' + str(error)) from error
    return {'mean': mean, 'sample_sd': sd, 'minimum': min(values), 'maximum': max(values),
            'sample_sd_status': 'DEFINED' if count > 1 else 'UNDEFINED_N_LT_2'}


def read_source(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2_000_000:
        raise ValueError('CSV must be a regular file no larger than 2 MB.')
    return path.read_bytes()


def read_csv(path, raw=None):
    import pandas as pd

    raw = read_source(path) if raw is None else raw
    try:
        records = list(csv.reader(io.StringIO(raw.decode('utf-8-sig'), newline=''), strict=True))
    except csv.Error as error:
        raise ValueError('Invalid CSV quoting: ' + str(error)) from None
    header = records[0] if records else []
    if not header or any(not value.strip() for value in header) or len(header) != len(set(header)):
        raise ValueError('CSV headers must be nonempty and unique; no automatic column renaming.')
    rows = records[1:]
    if any(len(row) != len(header) for row in rows):
        raise ValueError('Every CSV record must have exactly the header width; blank/ragged records are rejected.')
    # Construct from checked string fields: no implicit index or NA inference.
    frame = pd.DataFrame(rows, columns=header, dtype=str)
    if not 1 <= len(frame) <= 10000 or any(str(c).startswith('_adp_') for c in frame.columns):
        raise ValueError('Require 1–10000 rows and no reserved _adp_ columns.')
    return raw, frame


def save_input_failure(raw, output_dir, error):
    output = Path(output_dir).resolve()
    if output.is_relative_to(PAGE) or output.exists():
        raise ValueError('Use a NEW result directory outside the Skill source.')
    output.mkdir(parents=True)
    (output / 'input.csv').write_bytes(raw)
    (output / 'SKILL.used.md').write_bytes((PAGE / 'SKILL.md').read_bytes())
    dump(output / 'failure.json', {'status': 'FAILED_INPUT_RETAINED', 'type': type(error).__name__,
                                 'message': str(error), 'model_calls': 0, 'network_calls': 0})
    files = sorted(path for path in output.iterdir() if path.is_file())
    (output / 'SHA256SUMS.txt').write_text(''.join(sha(path.read_bytes()) + '  ' + path.name + '\n'
                                                for path in files), encoding='utf-8')
    with zipfile.ZipFile(output / 'results.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in files + [output / 'SHA256SUMS.txt']:
            archive.write(path, path.name)


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
    raw = read_source(input_csv)
    try:
        _, original = read_csv(input_csv, raw=raw)
        if not {id_column, value_column, group_column}.issubset(original.columns):
            raise ValueError('Missing explicitly selected ID, value or group column.')
        if original[id_column].eq('').any():
            raise ValueError('Empty ID requires correction; repeated nonempty IDs are retained and flagged.')
    except (ValueError, UnicodeError) as error:
        save_input_failure(raw, output_dir, error)
        raise
    output = Path(output_dir).resolve()
    if output.exists() or output.is_relative_to(PAGE):
        raise ValueError('Use a NEW output directory outside the Skill.')
    output.mkdir(parents=True)
    (output / 'input.csv').write_bytes(raw)
    skill = (PAGE / 'SKILL.md').read_bytes()
    (output / 'SKILL.used.md').write_bytes(skill)
    settings = {'id_column': id_column, 'value_column': value_column, 'group_column': group_column,
                'unit': unit, 'minimum': minimum, 'maximum': maximum, 'lookup_key': lookup_key,
                'duplicate_policy': 'FLAG_ALL_RETAIN_ALL', 'statistics': 'DESCRIPTIVE_SAMPLE_SD_DDOF_1',
                'summary_algorithm': 'PYTHON312_STATISTICS_MEAN_STDEV_INTEGER_RATIO_ACCUMULATION',
                'derived_result_policy': 'FINITE_OR_EXPLICIT_FAILURE_UNDEFINED_SD_ONLY_IF_N_LT_2',
                'derived_zero_policy': 'REJECT_UNDERFLOWED_ZERO_PRESERVE_EXACT_ZERO'}
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
            lookup_raw = read_source(lookup_csv)
            (output / 'lookup-input.csv').write_bytes(lookup_raw)
            _, lookup = read_csv(lookup_csv, raw=lookup_raw)
            if lookup_key not in lookup or lookup[lookup_key].eq('').any() or lookup[lookup_key].duplicated().any():
                raise ValueError('Lookup keys must be present, nonempty and unique (many_to_one).')
            if set(frame.columns).intersection(lookup.columns) != {lookup_key}:
                raise ValueError('Lookup columns overlap; rename metadata explicitly before joining.')
            # Empty data keys must not match an empty metadata key.
            frame = frame.merge(lookup, how='left', on=lookup_key, sort=False,
                                validate='many_to_one', indicator='_adp_join_status')
            if len(frame) != len(original) or frame['_adp_record_index'].tolist() != list(range(1, len(original) + 1)):
                raise RuntimeError('Join changed row count or ordering.')
        # Preserve row-level evidence even if a derived statistic is outside the
        # float output range. Do not publish inf/blank as a completed summary.
        frame.to_csv(output / 'audit.csv', index=False)
        frame.loc[~status.eq('VALID')].to_csv(output / 'issues.csv', index=False)
        summaries = []
        for group, rows in frame.groupby(group_column, sort=False, dropna=False):
            valid = rows['_adp_numeric_value'].dropna().tolist()
            try:
                computed = descriptive_summary(valid)
            except ArithmeticError:
                dump(output / 'statistics-failure.json', {
                    'status': 'FAILED_DERIVED_STATISTICS', 'error_code': 'DERIVED_STATISTIC_NOT_REPRESENTABLE',
                    'group': str(group), 'valid_count': len(valid),
                    'sample_sd_status': 'CALCULATION_FAILED_NOT_UNDEFINED_N',
                    'algorithm': settings['summary_algorithm'], 'python': sys.version.split()[0]})
                raise
            summaries.append({group_column: group, 'total_rows': len(rows), 'valid_count': len(valid),
                              **computed, 'excluded_count': len(rows) - len(valid), 'unit': unit})
        summary = pd.DataFrame(summaries).set_index(group_column)
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
        derived_failure = isinstance(error, ArithmeticError)
        dump(output / 'failure.json', {'status': 'FAILED_DERIVED_STATISTICS_INPUT_RETAINED' if derived_failure else 'FAILED_INPUT_RETAINED',
                                      'error_code': 'DERIVED_STATISTIC_NOT_REPRESENTABLE' if derived_failure else None,
                                      'type': type(error).__name__, 'message': str(error), 'model_calls': 0, 'network_calls': 0})
        archive_results(output)
        raise
    archive_results(output)
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
    except (ValueError, OSError, RuntimeError, UnicodeError, ArithmeticError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
