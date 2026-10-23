"""Case 4: analyze a user-owned CSV instead of the teaching input."""
from pathlib import Path
import argparse
from skill_loader import SKILL_DIR, run_skill


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='UTF-8 CSV：id、smiles，可选label')
    parser.add_argument('--reference-id', required=True, help='本次CSV中有效分子的ID')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    parameters = dict(radius=2, fp_size=2048, include_chirality=True,
                      query_smarts='[CX3](=O)[OX2H1]', reference_id=args.reference_id)
    receipt = run_skill(
        skill_file=SKILL_DIR / 'SKILL.md',
        input_csv=args.input,
        parameters=parameters,
        task='分析用户CSV，保留全部ID和原SMILES，报告错误、查询和相似度。',
        output_dir=args.output, mode='tools',
    )
    print(receipt['status'], receipt['report'])


if __name__ == '__main__':
    main()
