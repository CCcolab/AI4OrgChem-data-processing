"""CSV adaptation and result delivery; no model or network import is needed."""
from pathlib import Path
from contextlib import contextmanager
import csv
import hashlib
import html
import importlib.metadata
import io
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import zipfile


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def json_text(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('JSON含重复字段：' + key)
            result[key] = value
        return result
    def nonfinite(value):
        raise ValueError('JSON不得包含NaN或Infinity。')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=nonfinite)


def read_json(path):
    if path.stat().st_size > 128_000:
        raise ValueError('JSON超过128000字节。')
    return json_text(path.read_text('utf-8-sig'))


def check_environment(page):
    if platform.python_version_tuple()[:2] not in [('3', '12'), ('3', '13')]:
        raise RuntimeError('本版要求Python 3.12或3.13。')
    installed = {}
    for line in (page / 'runtime/requirements.txt').read_text('utf-8').splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        name, version = line.split('==')
        try:
            actual = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            raise RuntimeError('缺少依赖；请在独立环境安装runtime/requirements.txt。') from None
        if tuple(map(int, actual.split('.'))) != tuple(map(int, version.split('.'))):
            raise RuntimeError('依赖版本不符：' + name + '；请安装runtime/requirements.txt。')
        installed[name] = actual
    return {'python': platform.python_version(), 'packages': installed}


def output_path(requested, page):
    raw = requested or Path.cwd() / ('rdkit-results-' + uuid.uuid4().hex[:10])
    if raw.exists() or raw.is_symlink():
        raise FileExistsError('结果目录已存在；请使用新目录，不覆盖旧结果。')
    output = raw.resolve()
    if output.is_relative_to(page):
        raise ValueError('结果目录必须在Skill源码目录外。')
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def run_tool(root, parameters, output):
    """Run only this packaged deterministic tool, with a 120-second deadline."""
    environment = dict(os.environ)
    for key in ['DEEPSEEK_API_KEY', 'OPENAI_API_KEY']:
        environment.pop(key, None)
    environment['MPLBACKEND'] = 'Agg'
    try:
        result = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--tool',
                                 str(root), json.dumps(parameters, allow_nan=False), str(output)],
                                capture_output=True, timeout=120, env=environment)
    except subprocess.TimeoutExpired:
        raise RuntimeError('数值工具超过120秒，已终止；本轮没有成功回执。') from None
    if result.returncode:
        raise RuntimeError('数值工具执行失败：' + result.stderr.decode('utf-8', errors='replace')[-1000:])
    return read_json(output / 'numerical-result.json')


@contextmanager
def input_workspace(page, source, skill_text, parent, kind):
    """Keep caller bytes unchanged; adapt only an ephemeral five-column copy."""
    if source.is_symlink() or source.stat().st_size > 128_000:
        raise ValueError('CSV须为普通文件，且不超过128000字节。')
    with source.open('rb') as stream:
        raw = stream.read(128_001)
    if len(raw) > 128_000:
        raise ValueError('CSV超过128000字节。')
    try:
        text = raw.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(text, newline=''), strict=True)
        fields = reader.fieldnames
        if fields is None or len(fields) != len(set(fields)) or not {'id', 'smiles'}.issubset(fields) or set(fields) - {'id', 'smiles', 'label'}:
            raise ValueError('CSV必需id、smiles列，可选label列；不接受其他列或重复列名。')
        rows = list(reader)
    except (UnicodeError, csv.Error) as error:
        raise ValueError('CSV须为UTF-8，且引号/分隔符合法。') from error
    if not 1 <= len(rows) <= 50:
        raise ValueError('CSV必须包含1至50条记录。')
    normalized = []
    for row in rows:
        if set(row) != set(fields) or any(not isinstance(v, str) for v in row.values()):
            raise ValueError('CSV数据行缺列或多列。')
        normalized.append({'id': row['id'], 'label': row.get('label', row['id']),
                           'smiles': row['smiles'], 'source_id': 'user' if kind == 'USER_PROVIDED_CSV' else 'project',
                           'role': 'input'})
    with tempfile.TemporaryDirectory(prefix='.rdkit-input-', dir=parent) as directory:
        root = Path(directory)
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, fieldnames=['id', 'label', 'smiles', 'source_id', 'role'])
        writer.writeheader()
        writer.writerows(normalized)
        normalized_bytes = stream.getvalue().encode('utf-8')
        (root / 'molecules.csv').write_bytes(normalized_bytes)
        (root / 'SKILL.md').write_text(skill_text, encoding='utf-8', newline='')
        shutil.copy2(page / 'runtime/sources.json', root / 'sources.json')
        provenance = {'kind': kind, 'file': 'molecules.csv', 'sha256': digest(normalized_bytes),
                      'original_file': 'input.csv', 'original_sha256': digest(raw), 'rows': len(rows),
                      'processing': 'Only column adaptation; IDs, record order and raw SMILES retained',
                      'source_statement': 'Caller-supplied provenance is not independent experimental authentication' if kind == 'USER_PROVIDED_CSV' else 'Project-authored teaching structures, not experimental data'}
        write_json(root / 'data-provenance.json', provenance)
        yield {'root': root, 'raw_input': raw, 'input_sha256': digest(raw),
               'csv_text': text, 'provenance': provenance}


def save_results(calculated, output, context, task, receipt, explanation, trace):
    for p in calculated.iterdir():
        if p.is_file():
            shutil.copy2(p, output / p.name)
    (output / 'input.csv').write_bytes(context['raw_input'])
    (output / 'task.txt').write_text(task + '\n', encoding='utf-8')
    if digest((output / 'SKILL.md').read_bytes()) != receipt['skill_sha256']:
        raise ValueError('运行Skill快照与调用身份不一致。')
    write_json(output / 'run-receipt.json', receipt)
    if explanation is not None:
        (output / 'agent-explanation.md').write_text(explanation, encoding='utf-8')
    if trace is not None:
        write_json(output / 'agent-trace.json', trace)
    with (output / 'analysis.csv').open(encoding='utf-8', newline='') as stream:
        records = list(csv.DictReader(stream))
    def table(rows, columns):
        result = '<div style="overflow-x:auto"><table><tr>' + ''.join('<th>' + html.escape(k) + '</th>' for k in columns) + '</tr>'
        for row in rows:
            result += '<tr>' + ''.join('<td>' + html.escape(row.get(k, '')) + '</td>' for k in columns) + '</tr>'
        return result + '</table></div>'
    identity_columns = ['id', 'label', 'smiles', 'parse_status', 'canonical_isomeric_smiles',
                        'formula', 'isotope_formula', 'formal_charge', 'charged_atom_count',
                        'components', 'radical_electrons', 'metal_elements', 'stereo_status',
                        'chiral_centers', 'descriptor_applicability', 'warning_messages', 'error', 'error_hint']
    descriptor_columns = ['id', 'mol_wt_g_mol', 'mol_logp_model', 'hbd', 'hba', 'tpsa_A2',
                          'tpsa_with_S_P_A2', 'query_match_count', 'query_atom_indices', 'scaffold_status']
    with (output / 'duplicates.csv').open(encoding='utf-8', newline='') as stream:
        duplicates = list(csv.DictReader(stream))
    summary = read_json(output / 'numerical-result.json')
    conventions = read_json(output / 'descriptor-conventions.json')
    body = ['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>SMILES与RDKit结果</title>',
            '<style>body{font:16px/1.6 sans-serif;max-width:1100px;margin:2em auto;padding:1em}pre{white-space:pre-wrap}img{max-width:100%}td,th{border:1px solid #ccc;padding:.4em}table{border-collapse:collapse}</style>',
            '<h1>SMILES与RDKit结果</h1><h2>程序回执</h2><pre>' + html.escape(json.dumps(receipt, ensure_ascii=False, indent=2)) + '</pre>',
            '<p>VALID仅表示本版解析与清理成功，不等于描述符适用或化学身份认证。'
            '保留原始输入并报告解析后有效的立体信息；未指定构型不等于无手性或外消旋混合物。</p>',
            '<h2>结构、适用范围与警告</h2>' + table(records, identity_columns),
            '<h2>描述符与查询</h2><p>MolWt：g/mol；MolLogP：无量纲模型值；HBD/HBA：规则计数；'
            'TPSA：Å²。主TPSA不计硫/磷，另列计入S/P的对照值。对应输入质子化状态，不预测pH分布。'
            '盐、离子、自由基、金属及多组分需按警告复核，不能将组合数值当实测分配系数或混合物物性。'
            '匹配数只针对本次SMARTS；羧酸片段模式也会在碳酸匹配两次。</p>' + table(records, descriptor_columns),
            '<h2>重复映射</h2>' + table(duplicates, ['id', 'first_id', 'rule']),
            '<details><summary>具体描述符约定与检查范围</summary><pre>' +
            html.escape(json.dumps(conventions, ensure_ascii=False, indent=2)) + '</pre><p>' +
            html.escape(summary['engineering_check_scope']) + '</p></details>']
    import base64
    body.append('<h2>SMARTS原子编号与匹配高亮</h2><p>查询：' + html.escape(receipt['parameters']['query_smarts']) +
                '；零起始编号对应解析图。高亮为所有匹配原子的并集；逐次匹配见query_atom_indices。</p>')
    for name in ['query-highlight.png', 'molecules.png', 'similarity.png']:
        body.append('<h2>' + name + '</h2><img alt="' + name + '" src="data:image/png;base64,' + base64.b64encode((output / name).read_bytes()).decode() + '">')
    if receipt['mode'] == 'agent' and explanation is None:
        body.append('<h2>模型解释状态</h2><p>数值结果已经保存并可下载；模型解释' +
                    ('失败' if receipt['interpretation_status'] == 'FAILED' else '尚未完成') +
                    '。这不是模型与工具全流程成功；不要为重试文字解释重复计算。</p>')
    elif explanation is None:
        body.append('<p>本次直接运行本地工具，模型调用为0；SKILL.md作为运行快照记录，没有交给模型解释。</p>')
    else:
        body.append('<h2>模型解释</h2><p>文件状态以程序回执及实际文件为准。</p><pre>' + html.escape(explanation) + '</pre>')
    body.append('<h2>保存结果</h2><a href="results.zip" download>结果ZIP</a> · <a href="SHA256SUMS.txt">SHA-256清单</a></html>')
    (output / 'report.html').write_text(''.join(body), encoding='utf-8')
    generated = {'SHA256SUMS.txt', 'results.zip', 'results.zip.sha256', '.results.zip.tmp'}
    files = sorted(p for p in output.iterdir() if p.is_file() and p.name not in generated)
    (output / 'SHA256SUMS.txt').write_text(''.join(digest(p.read_bytes()) + '  ' + p.name + '\n' for p in files), encoding='utf-8')
    # Only a directory freshly claimed by this run is updated; existing user outputs
    # are rejected by output_path(). Replace the checkpoint ZIP atomically.
    staging = output / '.results.zip.tmp'
    try:
        with zipfile.ZipFile(staging, 'w', zipfile.ZIP_DEFLATED) as z:
            for p in files + [output / 'SHA256SUMS.txt']:
                z.write(p, p.name)
        os.replace(staging, output / 'results.zip')
    finally:
        if staging.exists():
            staging.unlink()
    (output / 'results.zip.sha256').write_text(digest((output / 'results.zip').read_bytes()) + '  results.zip\n', encoding='utf-8')
    verify_results(output)


def verify_results(output):
    if output.is_symlink():
        raise ValueError('结果目录不能是符号链接。')
    rows = {}
    lines = (output / 'SHA256SUMS.txt').read_text('utf-8').splitlines()
    if not 1 <= len(lines) <= 100:
        raise ValueError('结果清单必须包含1至100项。')
    for line in lines:
        value, name = line.split('  ', 1)
        if not re.fullmatch('[0-9a-f]{64}', value) or Path(name).name != name or any(c in name for c in '/\\:') or name in rows:
            raise ValueError('结果清单无效。')
        p = output / name
        if p.is_symlink() or digest(p.read_bytes()) != value:
            raise ValueError('结果哈希不符：' + name)
        rows[name] = value
    if {p.name for p in output.iterdir()} != rows.keys() | {'SHA256SUMS.txt', 'results.zip', 'results.zip.sha256'}:
        raise ValueError('结果目录含缺失或额外文件。')
    archive = output / 'results.zip'
    if archive.stat().st_size > 25_000_000:
        raise ValueError('结果ZIP过大。')
    if (output / 'results.zip.sha256').read_text('utf-8').strip() != digest(archive.read_bytes()) + '  results.zip':
        raise ValueError('结果ZIP哈希不符。')
    with zipfile.ZipFile(archive) as z:
        if len(z.infolist()) > 100 or sum(i.file_size for i in z.infolist()) > 25_000_000 or len(z.namelist()) != len(set(z.namelist())) or set(z.namelist()) != rows.keys() | {'SHA256SUMS.txt'} or z.testzip() is not None:
            raise ValueError('结果ZIP清单或CRC不符。')
        for name, value in rows.items():
            if digest(z.read(name)) != value:
                raise ValueError('ZIP内部哈希不符。')
        if z.read('SHA256SUMS.txt') != (output / 'SHA256SUMS.txt').read_bytes():
            raise ValueError('ZIP内部清单不符。')


if __name__ == '__main__':
    if len(sys.argv) != 5 or sys.argv[1] != '--tool':
        raise SystemExit('配套工具仅由主程序调用。')
    from molecule_tool import analyze
    analyze(Path(sys.argv[2]), json_text(sys.argv[3]), Path(sys.argv[4]))
