"""Case 3: query the public NCI CIR resolver without equating it to identity certification."""
from pathlib import Path
import argparse
import sys

PAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAGE / 'runtime'))
from resolve_identifiers import run_skill

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--allow-network', action='store_true', required=True)
    args = parser.parse_args()
    receipt = run_skill(input_csv=PAGE / 'runtime/examples/03-cir.csv', output_dir=args.output,
                        service='cir', allow_network=args.allow_network)
    print(receipt)
    raise SystemExit(int(receipt['failed_service_rows'] > 0))
