"""Case 1: descriptors, duplicate ethanol spellings and invalid rows."""
from pathlib import Path
import argparse
from skill_loader import SKILL_DIR, run_skill


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    parameters = dict(radius=2, fp_size=2048, include_chirality=True,
                      query_smarts='[#6]', reference_id='E01')
    receipt = run_skill(
        skill_file=SKILL_DIR / 'SKILL.md',
        input_csv=SKILL_DIR / 'runtime/examples/01-descriptors/molecules.csv',
        parameters=parameters,
        task='计算描述符，保留E01/E02重复映射及X01/X02错误记录。',
        output_dir=args.output,
        mode='tools', case_name='descriptors',
    )
    print(receipt['status'], receipt['report'])


if __name__ == '__main__':
    main()
