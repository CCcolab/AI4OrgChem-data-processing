"""Reusable CSV-to-Skill program: replace task, input and parameters."""
from pathlib import Path
import argparse
import importlib.util


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-dir', type=Path, default=Path(__file__).resolve().parents[2],
                        help='完整代码包的Skill文件夹；模板复制到别处时显式指定')
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--params', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--task', default='分析本次CSV，解释描述符、查询匹配与相似度。')
    parser.add_argument('--mode', choices=['tools', 'agent'], default='tools')
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    skill_dir = args.skill_dir.resolve()
    spec = importlib.util.spec_from_file_location('rdkit_skill', skill_dir / 'runtime/organic-smiles-rdkit.py')
    skill_api = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(skill_api)
    receipt = skill_api.run_skill(
        skill_file=skill_dir / 'SKILL.md',
        input_csv=args.input,
        parameters=args.params,
        task=args.task,
        output_dir=args.output,
        mode=args.mode,
        env_file=args.env_file,
    )
    print(receipt['status'])
    print(receipt['result_zip'])


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, ImportError) as error:
        raise SystemExit('执行失败：' + str(error))
