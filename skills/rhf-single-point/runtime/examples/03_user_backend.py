"""Call the complete result-file adapter once; no new scientific backend."""
from pathlib import Path
import argparse
import importlib.util
import json

PAGE = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
spec = importlib.util.spec_from_file_location('portable_bridge', PAGE / 'runtime/run_skill.py')
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
request = PAGE / 'runtime/examples/01.json'
# User-owned result files may be exported by any existing software/environment.
input_file = args.output.parent / (args.output.name + '-file-request.json')
if input_file.exists():
    raise ValueError('Choose a fresh output/request name.')
input_file.parent.mkdir(parents=True, exist_ok=True)
input_file.write_text(json.dumps({'parameters': {'backend_result_file': str(request)}, 'data': {},
    'provenance': {'kind': 'EXISTING_RESULT_FILE', 'description': 'File adapter demonstration; no new solver.'}}, indent=2), encoding='utf-8')
request = input_file
receipt = bridge.run_skill(mode='backend', request_file=request, output_dir=args.output, backend_file=PAGE / 'runtime/backends/file_backend.py', execute=True)
print(receipt['status'])
raise SystemExit(int(receipt['status'] == 'FAILED_NUMERICAL_CHECKS'))
