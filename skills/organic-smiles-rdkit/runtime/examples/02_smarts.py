"""Case 2: match carboxylic acid OH, distinguishing acetate and phenol."""
from pathlib import Path
import argparse
from skill_loader import SKILL_DIR, run_skill


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    parameters = dict(radius=2, fp_size=2048, include_chirality=True,
                      query_smarts='[CX3](=O)[OX2H1]', reference_id='A01')
    receipt = run_skill(
        skill_file=SKILL_DIR / 'SKILL.md',
        input_csv=SKILL_DIR / 'runtime/examples/02-smarts/molecules.csv',
        parameters=parameters,
        task='比较羧酸、乙酸根和酚的SMARTS匹配数量，解释查询的范围。',
        output_dir=args.output,
        mode='tools', case_name='smarts',
    )
    print(receipt['status'], receipt['report'])


if __name__ == '__main__':
    main()
