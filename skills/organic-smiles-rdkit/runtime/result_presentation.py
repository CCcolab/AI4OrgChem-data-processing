"""Determine file availability from program evidence; preserve raw model text."""
from pathlib import Path
import hashlib
import html
import json
import re
import zipfile

REQUIRED = ('analysis.csv', 'errors.csv', 'duplicates.csv', 'similarity.csv',
            'molecules.png', 'similarity.png', 'parameters.json', 'numerical-result.json')

def _sha(data):
    return hashlib.sha256(data).hexdigest()

def _file(root, name):
    if Path(name).name != name or name in ('', '.', '..') or '\\' in name:
        raise ValueError('文件清单包含非法路径。')
    path = root / name
    if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
        raise ValueError('结果文件缺失、为空或为链接：' + name)
    return path

def tool_file_evidence(output):
    """Only existing numeric files are reported; the ZIP is created later."""
    root = Path(output)
    numeric = json.loads(_file(root, 'numerical-result.json').read_text('utf-8'))
    if numeric.get('status') != 'PASS_BOUNDED_RDKIT_ANALYSIS' or not numeric.get('checks') or not all(v is True for v in numeric['checks'].values()):
        raise ValueError('数值程序没有通过，不能宣称已有合格结果。')
    return {'status': 'FILES_WRITTEN_BY_PROGRAM', 'files': [
        {'file': n, 'bytes': _file(root, n).stat().st_size,
         'sha256': _sha(_file(root, n).read_bytes())} for n in REQUIRED],
        'zip_status': 'CREATED_BY_PROGRAM_AFTER_FINAL_MODEL_REPLY',
        'download_instructions': '使用Notebook课末下载单元；文件状态以程序回执、文件清单和实际ZIP为准。'}

def model_denies_files(text):
    return bool(re.search(r'(?:未|没有|并未|尚未)生成(?:任何|可供|可)?下载文件|未生成可下载文件|no downloadable files (?:were |have been )?(?:generated|created)', text, re.I))

def verify_download(output):
    """Reject missing files, bad receipts, tampering and invalid archives."""
    root = Path(output)
    tool_file_evidence(root)
    receipt = json.loads(_file(root, 'run-receipt.json').read_text('utf-8'))
    numeric = json.loads((root/'numerical-result.json').read_text('utf-8'))
    if receipt.get('status') != 'PASS_REAL_MODEL_AND_TOOL_CALL' or receipt.get('tool_calls') != 1:
        raise ValueError('没有合格的真实程序回执。')
    if receipt.get('parameters') != numeric.get('parameters'):
        raise ValueError('程序回执与数值参数不一致。')
    if receipt.get('skill_sha256') != _sha(_file(root, 'SKILL.md').read_bytes()):
        raise ValueError('Skill身份与实际文件不一致。')
    manifest = json.loads(_file(root, 'export-manifest.json').read_text('utf-8'))
    names = [entry['file'] for entry in manifest]
    if len(set(names)) != len(names) or not set(REQUIRED).union({'run-receipt.json', 'SKILL.md', 'agent-explanation.md'}).issubset(names):
        raise ValueError('结果清单不完整或包含重复项。')
    for entry in manifest:
        if _sha(_file(root, entry['file']).read_bytes()) != entry['sha256']:
            raise ValueError('实际结果文件哈希不一致：' + entry['file'])
    archive = _file(root, 'organic-smiles-rdkit-results.zip')
    with zipfile.ZipFile(archive) as z:
        if len(z.namelist()) != len(set(z.namelist())) or set(z.namelist()) != set(names).union({'export-manifest.json'}):
            raise ValueError('下载ZIP与清单文件集合不一致。')
        if sum(x.file_size for x in z.infolist()) > 20_000_000 or z.testzip() is not None:
            raise ValueError('下载ZIP损坏或超出本页大小范围。')
        if z.read('export-manifest.json') != (root/'export-manifest.json').read_bytes():
            raise ValueError('下载ZIP内清单不一致。')
        for entry in manifest:
            if _sha(z.read(entry['file'])) != entry['sha256']:
                raise ValueError('下载ZIP文件哈希不一致。')
    return {'status': 'PASS_VERIFIED_DOWNLOAD', 'files_generated': True,
            'archive': archive.name, 'archive_sha256': _sha(archive.read_bytes()),
            'archive_bytes': archive.stat().st_size, 'manifest_files': len(names),
            'execution_location': receipt['execution_location'], 'parameters': receipt['parameters'],
            'basis': 'Actual program receipt, file manifest, disk files and ZIP bytes'}

def display_bundle(output):
    status = verify_download(output)
    raw = (Path(output)/'agent-explanation.md').read_text('utf-8')
    warning = model_denies_files(raw)
    message = ('### 程序执行与下载（已核验）\n\n'
               '已完成真实Skill与RDKit调用，已生成并校验结果文件。\n\n'
               f"- 本轮ZIP：`{status['archive']}`（{status['archive_bytes']}字节）\n"
               f"- SHA-256：`{status['archive_sha256']}`\n"
               f"- 清单文件：{status['manifest_files']}项；实际运行位置：{status['execution_location']}\n\n"
               '**请使用课末下载单元保存结果；文件状态以本区程序回执、文件清单及实际下载文件为准。**\n\n')
    if warning:
        message += '**模型文件状态声明有误：原文与实际程序证据不一致。本次文件已生成且ZIP校验通过。**\n\n'
    message += '模型文字仅供结果解释参考，不决定执行或文件下载状态。原文保留在结果包中，也可在下方展开核对。'
    raw_html = ('<details><summary>查看原始模型解释（文件状态以程序核验为准）</summary><pre style="white-space:pre-wrap">'
                + html.escape(raw) + '</pre></details>')
    return {'status': status, 'markdown': message, 'raw_model_html': raw_html,
            'model_file_claim': 'CONTRADICTED' if warning else 'NOT_FLAGGED_NOT_CERTIFIED'}
