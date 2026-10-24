"""CSV and explicit column selection: full Skill invocation template."""
from pathlib import Path
import argparse
import sys
PAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAGE / 'runtime'))
from clean_chemical_data import run_skill

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--id-column', default='id')
    parser.add_argument('--value-column', default='yield_pct')
    parser.add_argument('--group-column', default='batch')
    parser.add_argument('--unit', default='%')
    args = parser.parse_args()
    print(run_skill(input_csv=args.input, output_dir=args.output, id_column=args.id_column,
                    value_column=args.value_column, group_column=args.group_column, unit=args.unit))
