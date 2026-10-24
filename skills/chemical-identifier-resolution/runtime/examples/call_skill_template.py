"""Complete local/remote invocation template. No model service is used."""
from pathlib import Path
import argparse
import sys

PAGE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PAGE / 'runtime'))
from resolve_identifiers import run_skill


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--service', choices=['pubchem', 'cir', 'both'], default='pubchem')
    parser.add_argument('--allow-network', action='store_true')
    args = parser.parse_args()
    receipt = run_skill(input_csv=args.input, output_dir=args.output,
                        service=args.service, allow_network=args.allow_network)
    print(receipt)
    return int(receipt['failed_service_rows'] > 0)


if __name__ == '__main__':
    raise SystemExit(main())
