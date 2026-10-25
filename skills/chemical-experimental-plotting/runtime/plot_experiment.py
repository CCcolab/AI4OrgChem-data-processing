"""Read SKILL.md, validate CSV and draw declared observations/uncertainty.

No fit, interpolation, imputation, model call or automatic outlier removal.
"""
from pathlib import Path
import argparse
import importlib.util
import csv
import hashlib
import io
import json
import sys
import statistics
import math
import zipfile

PAGE = Path(__file__).resolve().parents[1]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def replicate_summary(values):
    # CPython statistics uses exact integer-ratio accumulation for float inputs.
    # Returning a float mean still rounds to a representable observation unit.
    center = float(statistics.mean(values))
    deviation = float(statistics.stdev(values)) if len(values) > 1 else None
    if not math.isfinite(center) or (deviation is not None and not math.isfinite(deviation)):
        raise ValueError('Replicate summary is outside the finite float range.')
    if deviation == 0 and any(value != values[0] for value in values):
        raise ValueError('Nonzero replicate spread underflowed to zero; rescale declared units before retrying.')
    return center, deviation


def evidence_api():
    path = PAGE / 'runtime/output_evidence.py'
    spec = importlib.util.spec_from_file_location('_output_evidence', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_skill(*, input_csv, output_dir, x_unit, y_unit, mode='scatter', error_type=None):
    evidence = evidence_api()
    evidence.checked_output(PAGE, output_dir)
    raw = evidence.read_bounded(input_csv, 128000)
    output = evidence.begin_output(PAGE, output_dir, {'input.csv': raw})
    skill = (output / 'SKILL.used.md').read_bytes()
    try:
        settings = {'mode': mode, 'error_type': error_type, 'x_unit': x_unit, 'y_unit': y_unit,
                    'replicate_SD_ddof': 1, 'replicate_SD_algorithm': 'statistics.stdev_exact_ratio_accumulation',
                    'nonzero_SD_underflow_policy': 'REJECT_NOT_ZERO', 'confidence_level': 'NOT_INFERRED', 'outlier_policy': 'KEEP_ALL'}
        dump(output / 'parameters.json', settings)
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        if mode not in {'scatter', 'supplied-error', 'replicate-sd'}:
            raise ValueError('Select scatter, supplied-error or replicate-sd.')
        if (mode == 'supplied-error' and error_type not in {'SD', 'SEM', 'CI_HALF_WIDTH'}) or (mode != 'supplied-error' and error_type is not None):
            raise ValueError('Declare the supplied uncertainty meaning; no implicit conversion or confidence level.')
        if not all(isinstance(unit, str) and 0 < len(unit) <= 80 and unit.strip() for unit in [x_unit, y_unit]):
            raise ValueError('Explicit x and y units are required.')
        reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
        rows = list(reader)
        needed = {'id', 'x', 'y', 'group'} | ({'yerr'} if mode == 'supplied-error' else set())
        if (not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames)
                or not needed.issubset(reader.fieldnames) or not 1 <= len(rows) <= 1000
                or any(None in row or None in row.values() for row in rows)):
            raise ValueError('Require unique headers, complete rows, id,x,y,group and optional yerr.')
        if len({row['id'] for row in rows}) != len(rows) or any(not row['id'] or not row['group'] for row in rows):
            raise ValueError('IDs must be unique/nonempty; group must be declared.')
        points = []
        for row in rows:
            point = {'id': row['id'], 'group': row['group'], 'x': float(row['x']), 'y': float(row['y']),
                     'n': 1, 'yerr': float(row['yerr']) if mode == 'supplied-error' else None}
            if not np.isfinite([point['x'], point['y']]).all() or (
                    point['yerr'] is not None and (not np.isfinite(point['yerr']) or point['yerr'] < 0)):
                raise ValueError('Coordinates must be finite and supplied symmetric yerr nonnegative; no dropped rows.')
            points.append(point)
        plotted = points
        if mode == 'replicate-sd':
            bins = {}
            for point in points:
                bins.setdefault((point['group'], point['x']), []).append(point)
            plotted = []
            for (group, x), observations in bins.items():
                values = [p['y'] for p in observations]
                center, deviation = replicate_summary(values)
                plotted.append({'id': '|'.join(p['id'] for p in observations), 'group': group, 'x': x,
                                'y': center, 'n': len(values), 'yerr': deviation})
        if not all(np.isfinite(p['y']) and (p['yerr'] is None or np.isfinite(p['yerr'])) for p in plotted):
            raise ValueError('Summary overflow.')
        fig, ax = plt.subplots(figsize=(7, 5), layout='constrained')
        for group in dict.fromkeys(p['group'] for p in plotted):
            selected = [p for p in plotted if p['group'] == group]
            collection = ax.scatter([p['x'] for p in selected], [p['y'] for p in selected], label=group)
            error_points = [p for p in selected if p['yerr'] is not None]
            if error_points:
                ax.errorbar([p['x'] for p in error_points], [p['y'] for p in error_points],
                            yerr=[p['yerr'] for p in error_points], fmt='none', capsize=3,
                            color=collection.get_facecolor()[0])
        ax.set_xlabel('x / ' + x_unit)
        ax.set_ylabel('Response / ' + y_unit)
        meaning = 'Sample SD (ddof=1)' if mode == 'replicate-sd' else error_type or 'No uncertainty supplied'
        ax.set_title(mode + ' | ' + meaning)
        ax.legend(title='Declared group')
        for suffix in ['png', 'svg']:
            fig.savefig(output / ('observations.' + suffix), dpi=150)
        plt.close(fig)
        with (output / 'plotted-values.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.DictWriter(stream, fieldnames=['id', 'group', 'x', 'y', 'n', 'yerr'])
            writer.writeheader()
            writer.writerows(plotted)
        result = {'status': 'COMPLETE_DECLARED_DATA_PLOT', 'records': len(rows), 'plotted_points': len(plotted),
                  'points_without_defined_SD': sum(p['yerr'] is None for p in plotted) if mode == 'replicate-sd' else None,
                  'input_sha256': sha(raw), 'skill_sha256': sha(skill), 'parameters': settings,
                  'environment': {'python': sys.version.split()[0], 'numpy': np.__version__, 'matplotlib': matplotlib.__version__},
                  'model_calls': 0, 'network_calls': 0, 'skill_use': 'READ_AND_SNAPSHOTTED_NO_MODEL_INTERPRETATION',
                  'limits': ['No fit, significance, causality or prediction claim.',
                             'Replicate meaning and independence require experimental design information.',
                             'CI_HALF_WIDTH copies user-supplied half-width; confidence level and computation are not certified.',
                             'n=1 sample SD remains undefined, plotted without a zero-error claim.']}
        dump(output / 'run-receipt.json', result)
    except Exception as error:
        evidence.record_failure(output, error)
        raise
    evidence.seal_output(output)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=PAGE / 'runtime/examples/01-scatter.csv')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--x-unit', required=True)
    parser.add_argument('--y-unit', required=True)
    parser.add_argument('--mode', choices=['scatter', 'supplied-error', 'replicate-sd'], default='scatter')
    parser.add_argument('--error-type', choices=['SD', 'SEM', 'CI_HALF_WIDTH'])
    args = parser.parse_args()
    try:
        print(json.dumps(run_skill(input_csv=args.input, output_dir=args.output, x_unit=args.x_unit,
                                   y_unit=args.y_unit, mode=args.mode, error_type=args.error_type), ensure_ascii=False))
        return 0
    except (ValueError, OSError, RuntimeError, ArithmeticError, ImportError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
