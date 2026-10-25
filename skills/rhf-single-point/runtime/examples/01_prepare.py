"""Prepare inputs only; no solver, NumPy or model is called."""
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

receipt = bridge.run_skill(mode='prepare', request_file=request, output_dir=args.output)
print(receipt['status'])
raise SystemExit(int(receipt['status'] == 'FAILED_NUMERICAL_CHECKS'))
