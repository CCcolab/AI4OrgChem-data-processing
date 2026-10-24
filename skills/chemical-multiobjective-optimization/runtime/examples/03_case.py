"""Case 3: 改变参考点. Expected process exit code: 0."""
from pathlib import Path
import argparse
import importlib.util
PAGE=Path(__file__).resolve().parents[2]

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=PAGE / 'runtime/examples/03.json')
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('skill_entry', PAGE / 'runtime/run_skill.py')
    api=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    try:
        result=api.run_skill(request_file=args.input, output_dir=args.output)
        print(result['status'], result['scope'])
        raise SystemExit(int(result['status'] != 'COMPLETE_DEFINED_SCOPE'))
    except (ValueError, OSError, RuntimeError, ArithmeticError) as error:
        print('INPUT/EXECUTION FAILED:', error)
        raise SystemExit(2)
