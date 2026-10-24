"""Complete CSV / Skill invocation template; no model service."""
from pathlib import Path
import argparse
import sys
PAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAGE / 'runtime'))
from plot_experiment import run_skill

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--x-unit',required=True)
    parser.add_argument('--y-unit',required=True)
    parser.add_argument('--mode',choices=['scatter','supplied-error','replicate-sd'],default='scatter')
    parser.add_argument('--error-type',choices=['SD','SEM','CI_HALF_WIDTH'])
    args=parser.parse_args()
    print(run_skill(input_csv=args.input,output_dir=args.output,x_unit=args.x_unit,y_unit=args.y_unit,
                    mode=args.mode,error_type=args.error_type))
