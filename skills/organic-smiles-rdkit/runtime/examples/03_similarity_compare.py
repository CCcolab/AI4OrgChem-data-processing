"""Case 3: compare radius 2 and 3 on the same CSV in separate outputs."""
from pathlib import Path
import argparse
from skill_loader import SKILL_DIR, run_skill


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='全新的比较结果根目录')
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(SKILL_DIR):
        raise ValueError('比较结果目录必须位于Skill源码目录之外。')
    args.output.mkdir(parents=True, exist_ok=False)
    for radius in [2, 3]:
        parameters = dict(radius=radius, fp_size=2048, include_chirality=True,
                          query_smarts='[CX3](=O)[OX2H1]', reference_id='B01')
        receipt = run_skill(
            skill_file=SKILL_DIR / 'SKILL.md',
            input_csv=SKILL_DIR / 'runtime/examples/03-similarity/molecules.csv',
            parameters=parameters,
            task='比较相对于B01苯的Morgan相似度，记录当前半径结果。',
            output_dir=args.output / f'radius-{radius}',
            mode='tools', case_name='similarity',
        )
        print(radius, receipt['status'], receipt['result_zip'])


if __name__ == '__main__':
    main()
