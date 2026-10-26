"""Read an existing normalized JSON result and review it; no solver or user-code import."""
from pathlib import Path
import argparse
import importlib.util
import json

PAGE = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
spec = importlib.util.spec_from_file_location('local_review', PAGE / 'runtime/run_skill.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
request = args.output.parent / (args.output.name + '-import-request.json')
if request.exists() or args.output.exists():
    raise ValueError('Choose fresh output/request paths.')
request.parent.mkdir(parents=True, exist_ok=True)
request.write_text(json.dumps({'parameters': {'result_file': str((PAGE / 'runtime/examples/01.json').resolve())},
    'data': {}, 'provenance': {'kind': 'EXISTING_RESULT_FILE', 'description': 'Existing JSON import only; no new solver.'}}, indent=2)+'\n', encoding='utf-8')
receipt = bridge.run_skill(mode='import', request_file=request, output_dir=args.output)
print(receipt['status'])
raise SystemExit(int(receipt['status'] == 'FAILED_NUMERICAL_CHECKS'))
