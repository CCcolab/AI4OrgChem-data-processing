"""Complete reusable Skill invocation: explicit request and new result directory."""
from pathlib import Path
import argparse
import importlib.util

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-dir',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('skill_entry',args.skill_dir/'runtime/run_skill.py')
    api=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(api)
    result=api.run_skill(request_file=args.input,output_dir=args.output)
    print(result['status'],result['scope'])
    raise SystemExit(int(result['status']!='COMPLETE_DEFINED_SCOPE'))
