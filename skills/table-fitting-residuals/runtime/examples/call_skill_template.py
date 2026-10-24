"""Complete CSV and SKILL.md invocation template; explicit units required."""
from pathlib import Path
import argparse
import sys
PAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAGE / 'runtime'))
from fit_csv import run_skill

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--x-unit', required=True)
    parser.add_argument('--y-unit', required=True)
    parser.add_argument('--degree', type=int, choices=[1,2], default=1)
    parser.add_argument('--sigma-column')
    args=parser.parse_args()
    print(run_skill(input_csv=args.input, output_dir=args.output, x_unit=args.x_unit,
                    y_unit=args.y_unit, degree=args.degree, sigma_column=args.sigma_column))
