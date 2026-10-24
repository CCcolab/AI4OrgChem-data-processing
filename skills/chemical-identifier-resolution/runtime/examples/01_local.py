"""Case 1: locally parse two ethanol spellings and specified lactic acid."""
from pathlib import Path
import argparse
import sys

PAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAGE / 'runtime'))
from resolve_identifiers import run_skill

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(run_skill(input_csv=PAGE / 'runtime/examples/01-local.csv', output_dir=args.output))
