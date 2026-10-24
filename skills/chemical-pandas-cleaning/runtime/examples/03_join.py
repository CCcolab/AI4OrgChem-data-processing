"""03_join.py: authored synthetic teaching table; no experimental inference."""
from pathlib import Path
import argparse
import sys
PAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAGE / 'runtime'))
from clean_chemical_data import run_skill

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(run_skill(input_csv=PAGE / 'runtime/examples/01-replicates.csv', output_dir=args.output, lookup_csv=PAGE / 'runtime/examples/03-metadata.csv', lookup_key='batch'))
