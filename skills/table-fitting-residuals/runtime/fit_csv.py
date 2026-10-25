"""Bounded CSV least squares with explicit units, residuals and weights.

The complete Skill is read and saved; no model, automatic model selection or
executable formula is used. Existing HPLC reproduction remains a separate entry.
"""
from pathlib import Path
import argparse
import importlib.util
import csv
import hashlib
import io
import json
import sys
import zipfile

PAGE = Path(__file__).resolve().parents[1]


def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def evidence_api():
    path = PAGE / 'runtime/output_evidence.py'
    spec = importlib.util.spec_from_file_location('_output_evidence', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_skill(*, input_csv, output_dir, x_unit, y_unit, degree=1, sigma_column=None):
    evidence = evidence_api()
    evidence.checked_output(PAGE, output_dir)
    raw = evidence.read_bounded(input_csv, 128000)
    output = evidence.begin_output(PAGE, output_dir, {'input.csv': raw})
    skill = (output / 'SKILL.used.md').read_bytes()
    try:
        settings = {'degree': degree, 'fit_intercept': True, 'x_unit': x_unit, 'y_unit': y_unit,
                    'sigma_column': sigma_column, 'weight_definition': '1/sigma_y^2' if sigma_column else 'UNWEIGHTED',
                    'residual_definition': 'observed_y - fitted_y', 'rcond': 1e-12,
                    'scaled_design_condition_limit': 1e10, 'inference': 'NOT_PERFORMED'}
        dump(output / 'parameters.json', settings)
        import numpy as np
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        if type(degree) is not int or degree not in {1, 2}:
            raise ValueError('degree must be integer 1 or 2; intercept is always fitted.')
        if not all(isinstance(unit, str) and 0 < len(unit) <= 80 and unit.strip() for unit in [x_unit, y_unit]):
            raise ValueError('Declare x_unit and y_unit; use explicit arbitrary units for synthetic data.')
        reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
        rows = list(reader)
        if (not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames))
                or not {'id', 'x', 'y'}.issubset(reader.fieldnames) or any(None in row or None in row.values() for row in rows)
                or not degree + 2 <= len(rows) <= 1000):
            raise ValueError('Require unique headers id,x,y, complete records and p<n<=1000.')
        if sigma_column is not None and (sigma_column not in reader.fieldnames or sigma_column in {'id', 'x', 'y'}):
            raise ValueError('Choose a distinct existing sigma column containing response standard deviations.')
        if any(not row['id'] for row in rows) or len({row['id'] for row in rows}) != len(rows):
            raise ValueError('IDs must be nonempty and unique; keep repeated observations under distinct IDs.')
        x = np.array([float(row['x']) for row in rows])
        y = np.array([float(row['y']) for row in rows])
        sigma = np.array([float(row[sigma_column]) for row in rows]) if sigma_column else np.ones(len(rows))
        if not all(np.isfinite(a).all() for a in [x, y, sigma]) or np.any(sigma <= 0):
            raise ValueError('All x,y,sigma must be finite; sigma must be strictly positive. No row deletion.')
        center = float(np.mean(x))
        scale = float(np.std(x))
        if not np.isfinite(center) or not np.isfinite(scale) or scale <= 0:
            raise ValueError('Constant x or numerical overflow; no identifiable slope.')
        z = (x - center) / scale
        design = np.vander(z, degree + 1, increasing=True)
        weighted_design = design / sigma[:, None]
        target = y / sigma
        if not np.isfinite(weighted_design).all() or not np.isfinite(target).all():
            raise ValueError('Weight scaling overflow; finite weighted design and response required.')
        coefficients, _, rank, singular = np.linalg.lstsq(weighted_design, target, rcond=1e-12)
        condition = float(singular[0] / singular[-1]) if singular[-1] > 0 else float('inf')
        if rank != degree + 1 or not np.isfinite(condition) or condition > 1e10:
            raise ValueError('Rank-deficient or ill-conditioned scaled design; no usable fit.')
        fitted = design @ coefficients
        residual = y - fitted
        # Convert scaled polynomial coefficients to the supplied x units.
        polynomial = np.polynomial.Polynomial(coefficients)
        original_polynomial = polynomial(np.polynomial.Polynomial([-center / scale, 1 / scale]))
        beta = original_polynomial.coef
        if not all(np.isfinite(a).all() for a in [fitted, residual, beta]):
            raise ValueError('Nonfinite numerical result.')
        # A well-conditioned scaled fit can have an unstable original-x export.
        # Persist the representation actually used for predictions, then diagnose
        # the legacy coefficients on observed x separately from fit quality.
        with np.errstate(over='ignore', invalid='ignore'):
            legacy_replay = np.polynomial.polynomial.polyval(x, beta)
            replay_error = np.abs(legacy_replay - fitted)
        # Normalize by the actual fitted response scale, never by max(1,scale)
        # or a fixed dimensional atol. A change of y units must not hide loss.
        response_scale = float(np.max(np.abs(fitted)))
        replay_rtol = 1e-10
        replay_finite = bool(np.isfinite(replay_error).all())
        with np.errstate(over='ignore', invalid='ignore'):
            relative_replay_error = float(replay_error.max() / response_scale) if response_scale else (
                0.0 if replay_finite and not np.any(replay_error) else float('inf'))
        replay_passed = replay_finite and relative_replay_error <= replay_rtol
        original_basis_diagnostic = {
            'status': 'REPLAY_WITHIN_TOLERANCE_ON_OBSERVED_X' if replay_passed else 'REPLAY_UNSTABLE',
            'domain': 'OBSERVED_X_ONLY_NOT_EXTRAPOLATION',
            'max_absolute_error_y': float(replay_error.max()) if replay_finite else None,
            'finite_replay': replay_finite, 'response_scale_y': response_scale,
            'max_error_relative_to_response_scale': relative_replay_error if np.isfinite(relative_replay_error) else None,
            'relative_tolerance': replay_rtol, 'atol_y': 0.0,
            'criterion': 'max(abs(original_x_replay - scaled_fit))/max(abs(scaled_fit)) <= relative_tolerance',
            'zero_response_policy': 'Exact zero replay required when fitted response scale is zero.',
            'tolerance_role': 'ENGINEERING_REPLAY_DIAGNOSTIC_NOT_MEASUREMENT_UNCERTAINTY',
        }
        warnings = [] if replay_passed else ['ORIGINAL_BASIS_REPLAY_UNSTABLE']
        rss = float(residual @ residual)
        weighted_rss = float((residual / sigma) @ (residual / sigma))
        tss = float((y - y.mean()) @ (y - y.mean()))
        r2 = None if np.all(y == y[0]) else float(1 - rss / tss)
        if not all(np.isfinite(v) for v in [rss, weighted_rss]) or (r2 is not None and not np.isfinite(r2)):
            raise ValueError('Metric overflow.')
        result = {'status': 'COMPLETE_BOUNDED_LEAST_SQUARES', 'records': len(rows), 'rank': int(rank),
                  'coefficient_order': 'INCREASING_POWERS_OF_ORIGINAL_X', 'coefficients': beta.tolist(),
                  'coefficient_units': [y_unit] + [y_unit + '/(' + x_unit + ')^' + str(i) for i in range(1, degree + 1)],
                  'prediction_representation': 'SCALED_X_POLYNOMIAL',
                  'scaled_coefficients': coefficients.tolist(),
                  'scaled_coefficient_order': 'INCREASING_POWERS_OF_Z',
                  'scaled_coefficient_units': [y_unit] * (degree + 1),
                  'prediction_formula': 'z=(x-scaled_x_center)/scaled_x_scale; yhat=sum(scaled_coefficients[k]*z**k)',
                  'original_basis_diagnostic': original_basis_diagnostic, 'warnings': warnings,
                  'rss': rss, 'rss_unit': '(' + y_unit + ')^2', 'weighted_rss': weighted_rss,
                  'weighted_rss_unit': 'dimensionless' if sigma_column else '(' + y_unit + ')^2',
                  'rmse': float(np.sqrt(rss / len(rows))), 'rmse_unit': y_unit,
                  'r2_unweighted_with_intercept': r2, 'degrees_of_freedom': len(rows) - int(rank),
                  'scaled_design_condition': condition, 'scaled_x_center': center, 'scaled_x_scale': scale,
                  'scaled_x_center_unit': x_unit, 'scaled_x_scale_unit': x_unit,
                  'parameters': settings, 'environment': {'python': sys.version.split()[0], 'numpy': np.__version__,
                                                         'matplotlib': matplotlib.__version__},
                  'input_sha256': sha(raw), 'skill_sha256': sha(skill), 'model_calls': 0, 'network_calls': 0,
                  'skill_use': 'READ_AND_SNAPSHOTTED_NO_MODEL_INTERPRETATION',
                  'limitations': ['Descriptive fit only; no causal or predictive validation.',
                                  'x errors and correlated responses are not modeled.',
                                  'No confidence interval, p-value or automatic degree selection.',
                                  'Use scaled coefficients for prediction; original-x coefficients are a legacy export with a separate replay diagnostic.',
                                  'Condition threshold is an engineering admission rule, not scientific validation.']}
        with (output / 'residuals.csv').open('w', newline='', encoding='utf-8') as stream:
            writer = csv.writer(stream)
            writer.writerow(['id', 'x', 'y', 'fitted_y', 'residual_y_minus_fit', 'sigma_y_or_one'])
            writer.writerows(zip([row['id'] for row in rows], x, y, fitted, residual, sigma))
        dump(output / 'run-receipt.json', result)
        fig, axes = plt.subplots(2, 1, figsize=(7, 6), layout='constrained')
        if sigma_column:
            axes[0].errorbar(x, y, yerr=sigma, fmt='o', label='Supplied response SD')
        else:
            axes[0].scatter(x, y, label='Input observations')
        grid = np.linspace(x.min(), x.max(), 100)
        axes[0].plot(grid, polynomial((grid - center) / scale), label='Degree ' + str(degree))
        axes[0].set_ylabel('Response / ' + y_unit)
        axes[0].legend()
        axes[1].axhline(0, color='gray')
        axes[1].scatter(x, residual)
        axes[1].set_xlabel('x / ' + x_unit)
        axes[1].set_ylabel('(Observed - fitted) / ' + y_unit)
        fig.savefig(output / 'fit-and-residuals.png', dpi=140)
        plt.close(fig)
    except Exception as error:
        evidence.record_failure(output, error)
        raise
    evidence.seal_output(output)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--x-unit', required=True)
    parser.add_argument('--y-unit', required=True)
    parser.add_argument('--degree', type=int, choices=[1, 2], default=1)
    parser.add_argument('--sigma-column')
    args = parser.parse_args()
    try:
        print(json.dumps(run_skill(input_csv=args.input, output_dir=args.output,
                                   x_unit=args.x_unit, y_unit=args.y_unit, degree=args.degree,
                                   sigma_column=args.sigma_column), ensure_ascii=False))
        return 0
    except (ValueError, OSError, RuntimeError, ArithmeticError, ImportError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
