"""Read SKILL.md, load a CSV, run a bounded tool or agent, and save results.

Examples: --case descriptors, --case smarts, --case similarity.
Use --help for user CSV input and explicit model configuration.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

PAGE = Path(__file__).resolve().parents[1]


def check_resources():
    """Check packaged code/data before importing the supporting modules."""
    rows = json.loads((PAGE / 'runtime/resource-manifest.json').read_text('utf-8'))
    seen = set()
    for item in rows:
        name = item['file']
        path = PAGE / name
        if name in seen or path.is_symlink() or not path.resolve().is_relative_to(PAGE):
            raise ValueError('运行资源路径重复或无效。')
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('运行资源校验失败：' + name)
        seen.add(name)
    required = {'SKILL.md', 'runtime/organic-smiles-rdkit.py', 'runtime/requirements.txt',
                'runtime/execution.py', 'runtime/agent.py', 'runtime/molecule_tool.py',
                'runtime/chemistry.py',
                'runtime/credential_config.py', 'runtime/sources.json', 'runtime/examples/cases.json'}
    if not required.issubset(seen):
        raise ValueError('运行资源清单缺少必需文件。')


def run_skill(*, skill_file, input_csv, parameters, task, output_dir=None,
              mode='tools', env_file=None, case_name='user-csv'):
    """Complete reusable template: read Skill, validate CSV, call tool, save.

    tools: no model or .env access. agent: send Skill/task/CSV to DeepSeek.
    Returns the real receipt plus result paths. Requires the full package.
    """
    owned_output = None
    try:
        if mode not in {'tools', 'agent'} or (mode == 'agent') != bool(env_file):
            raise ValueError('agent模式必须指定env_file；tools模式不读取.env。')
        check_resources()
        runtime = str(PAGE / 'runtime')
        if runtime not in sys.path:
            sys.path.insert(0, runtime)
        import execution

        # ① Read the complete, authoritative SKILL.md.
        skill_file = Path(skill_file)
        if skill_file.is_symlink() or skill_file.resolve() != PAGE / 'SKILL.md':
            raise ValueError('请使用本代码包顶层的SKILL.md。')
        # Hash and snapshot the exact UTF-8 bytes, including Windows newlines.
        skill_text = skill_file.read_bytes().decode('utf-8')
        if isinstance(parameters, (str, Path)):
            parameters = execution.read_json(Path(parameters))
        if not isinstance(parameters, dict):
            raise ValueError('参数必须是包含五个字段的字典。')
        parameters = dict(parameters)
        if not isinstance(task, str) or not task.strip() or len(task) > 2000:
            raise ValueError('任务说明必须为1至2000字符。')
        input_csv = Path(input_csv)
        if input_csv.is_symlink():
            raise ValueError('CSV不能是符号链接；请提供普通文件。')
        input_csv = input_csv.resolve()
        cases = execution.read_json(PAGE / 'runtime/examples/cases.json')
        authored = {(PAGE / case['input']).resolve() for case in cases.values()}
        kind = ('AUTHORED_TEACHING_STRUCTURES' if input_csv in authored
                else 'USER_PROVIDED_CSV')

        # ② Validate before any paid request or output claim.
        environment = execution.check_environment(PAGE)
        output = execution.output_path(Path(output_dir) if output_dir else None, PAGE)
        with execution.input_workspace(PAGE, input_csv, skill_text, output.parent, kind) as context:
            import molecule_tool
            molecule_tool.preflight(context['root'], parameters)
            output.mkdir(parents=True, exist_ok=False)
            owned_output = output
            calculated = context['root'] / 'calculated'
            identity = {'skill': 'organic-smiles-rdkit', 'case': case_name,
                        'skill_sha256': hashlib.sha256(skill_text.encode('utf-8')).hexdigest(),
                        'input_sha256': context['input_sha256'], 'parameters': parameters,
                        'environment': environment}
            numerical_complete = False

            # ③ Register one fixed tool; never execute model-generated code.
            def analyze_organic_molecules(tool_parameters):
                nonlocal numerical_complete
                if tool_parameters != parameters:
                    raise ValueError('工具参数与用户参数不一致。')
                result = execution.run_tool(context['root'], tool_parameters, calculated)
                if mode == 'agent':
                    # Persist a verified numerical ZIP before another model request.
                    checkpoint = {**identity, 'status': 'NUMERICAL_COMPLETE_EXPLANATION_PENDING',
                                  'mode': 'agent', 'agent_called': True, 'tool_calls': 1,
                                  'model_calls': None, 'numerical_status': 'COMPLETE',
                                  'interpretation_status': 'PENDING', 'numerical_files_saved': True}
                    execution.save_results(calculated, output, context, task, checkpoint, None, None)
                numerical_complete = True
                return result

            # ④ Pass Skill/task/CSV/tool to the agent, or explicitly run tools.
            if mode == 'agent':
                from agent import AgentFailure, call_skill
                try:
                    receipt, explanation, trace = call_skill(
                        skill_text=skill_text, task=task, csv_text=context['csv_text'],
                        parameters=parameters, tool=analyze_organic_molecules,
                        env_file=Path(env_file).resolve(),
                    )
                except AgentFailure as error:
                    if numerical_complete:
                        receipt = {**identity, **error.receipt,
                                   'status': 'PARTIAL_NUMERICAL_COMPLETE',
                                   'numerical_status': 'COMPLETE', 'numerical_files_saved': True}
                        execution.write_json(output / 'failure.json',
                                             {'stage': 'MODEL_INTERPRETATION', 'status': 'FAILED',
                                              'message': str(error), 'numerical_results_retained': True})
                        execution.save_results(calculated, output, context, task,
                                               receipt, None, error.trace)
                        raise RuntimeError('数值计算完成，模型解释失败；未重复计算。'
                                           f'结果已保存：{output / "results.zip"}；原因：{error}') from None
                    raise
            else:
                analyze_organic_molecules(parameters)
                receipt = {'status': 'PASS_LOCAL_TOOLS', 'mode': 'tools', 'model_calls': 0,
                           'agent_called': False, 'tool_calls': 1,
                           'skill_use': 'RECORDED_NOT_INTERPRETED_BY_MODEL'}
                explanation, trace = None, None

            # ⑤ Save actual input, Skill snapshot, results, report and ZIP.
            receipt.update(**identity, numerical_status='COMPLETE', numerical_files_saved=True,
                           interpretation_status='COMPLETE' if mode == 'agent' else 'NOT_REQUESTED')
            execution.save_results(calculated, output, context, task,
                                   receipt, explanation, trace)
        return {**receipt, 'output_directory': str(output),
                'report': str(output / 'report.html'), 'result_zip': str(output / 'results.zip')}
    except (OSError, ValueError, RuntimeError, ArithmeticError, ImportError) as error:
        if owned_output is not None and not (owned_output / 'failure.json').exists():
            execution.write_json(owned_output / 'failure.json',
                                 {'status': 'FAILED', 'type': type(error).__name__,
                                  'message': str(error)})
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=['descriptors', 'smarts', 'similarity'], default='descriptors')
    parser.add_argument('--input', type=Path, help='用户UTF-8 CSV；必需id、smiles列，可选label列')
    parser.add_argument('--params', type=Path, help='完整的五字段参数JSON；省略时用案例模板')
    parser.add_argument('--reference-id', help='显式覆盖模板中的参照ID，必须是本次输入中的有效ID')
    parser.add_argument('--task', help='本次问题；Agent模式随输入一起发送，最长2000字符')
    parser.add_argument('--mode', choices=['tools', 'agent'], default='tools')
    parser.add_argument('--env-file', type=Path, help='仅agent模式读取本地DEEPSEEK_API_KEY')
    parser.add_argument('--output', type=Path, help='全新结果目录，必须在本Skill源码目录外')
    parser.add_argument('--verify', type=Path, help='只校验已有结果，不计算、不调用模型')
    args = parser.parse_args(argv)
    if args.verify and any([args.input, args.params, args.reference_id, args.task, args.output,
                            args.env_file, args.mode != 'tools', args.case != 'descriptors']):
        parser.error('--verify不能与分析选项混用。')
    try:
        check_resources()
        sys.path.insert(0, str(PAGE / 'runtime'))
        import execution
        if args.verify:
            execution.verify_results(args.verify.resolve())
            print('PASS_SAVED_RESULTS：文件、ZIP和SHA-256一致；未运行计算。')
            return 0
        case = execution.read_json(PAGE / 'runtime/examples/cases.json')[args.case]
        parameters = execution.read_json(args.params or PAGE / case['parameters'])
        if not isinstance(parameters, dict):
            raise ValueError('参数JSON必须是对象，包含完整的五个字段。')
        if args.reference_id is not None:
            parameters['reference_id'] = args.reference_id
        receipt = run_skill(
            skill_file=PAGE / 'SKILL.md', input_csv=args.input or PAGE / case['input'],
            parameters=parameters, task=args.task if args.task is not None else case['task'],
            output_dir=args.output, mode=args.mode, env_file=args.env_file, case_name=args.case,
        )
        print(receipt['status'])
        print('报告：', receipt['report'])
        print('结果：', receipt['result_zip'])
        return 0
    except (OSError, ValueError, RuntimeError, ArithmeticError, ImportError) as error:
        print('执行失败：' + str(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
