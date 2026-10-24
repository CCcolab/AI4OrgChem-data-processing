"""Authored synthetic regression example; no chemical prediction claim."""
from pathlib import Path
import argparse
import sys
PAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAGE / 'runtime'))
from fit_csv import run_skill

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(run_skill(input_csv=PAGE / 'runtime/examples/02-linear.csv', output_dir=args.output,
                    x_unit='arbitrary_x_unit', y_unit='arbitrary_y_unit', degree=1))
