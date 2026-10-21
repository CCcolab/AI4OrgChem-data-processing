"""Offline checks of the delivered pages, inputs, downloads and navigation."""
import ast
import base64
import csv
import hashlib
import io
import json
import re
import unittest
import zipfile
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / 'skills/organic-smiles-rdkit'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    return json.loads(path.read_text('utf-8'))

class SkillNavigationTests(unittest.TestCase):
    def test_eight_categories_and_unique_assignment(self):
        nav = read_json(ROOT / 'NAVIGATION.json')
        cats = nav['categories']
        self.assertEqual(len(cats), 8)
        self.assertEqual(len({c['id'] for c in cats}), 8)
        self.assertEqual(sum(c['kind'] == 'professional_application' for c in cats), 7)
        self.assertEqual(sum(c['kind'] == 'shared_support' for c in cats), 1)
        self.assertFalse(nav['render_empty_categories'])
        assigned = [s for c in cats for s in c['skills']]
        self.assertCountEqual(assigned, [s['id'] for s in nav['skills']])
        self.assertEqual(len(set(assigned)), len(assigned))

    def test_only_two_available_pages_are_rendered(self):
        nav = read_json(ROOT / 'NAVIGATION.json')
        self.assertEqual(len(nav['skills']), 2)
        for name in ['README.md', 'START_HERE_zh-CN.md']:
            text = (ROOT / name).read_text('utf-8')
            for cat in nav['categories']:
                self.assertEqual('## ' + cat['title'] in text, bool(cat['skills']))
            for skill in nav['skills']:
                for key in ['page', 'notebook_entry', 'run']:
                    self.assertTrue((ROOT / skill[key]).is_file())
                    self.assertIn(skill[key], text)

    def test_canonical_names_and_professional_categories(self):
        nav = read_json(ROOT / 'NAVIGATION.json')
        self.assertEqual([c['title'] for c in nav['categories']], [
            '有机分子结构与身份识别', '有机分析与实验数据处理', '物理有机与能量分析',
            '计算有机化学与电子结构', '分子结构优化与多态比较', '化学信息学与分子设计',
            '化学实验设计与优化', '共用运行支持'])
        skills = {s['id']: s for s in nav['skills']}
        self.assertEqual(skills['organic-smiles-rdkit']['title'], 'SMILES 与 RDKit')
        self.assertEqual(skills['organic-smiles-rdkit']['category'], 'organic-structure')
        self.assertEqual(skills['table-fitting-residuals']['category'], 'organic-analysis')
        self.assertEqual(skills['table-fitting-residuals']['title'], '表格拟合与残差分析')

    def test_teaching_and_running_have_separate_responsibilities(self):
        for skill in read_json(ROOT / 'NAVIGATION.json')['skills']:
            teaching = (ROOT / skill['page']).read_text('utf-8')
            running = (ROOT / skill['run']).read_text('utf-8')
            self.assertTrue(skill['page'].endswith('/TEACHING.md'))
            self.assertTrue(skill['run'].endswith('/RUNNING.md'))
            self.assertIn('sources.json', teaching)
            self.assertIn('data-provenance.json', teaching)
            self.assertIn('## 学习目标', teaching)
            self.assertIn('## 自测', teaching)
            self.assertNotIn('DEEPSEEK_API_KEY', teaching)
            for term in ['DEEPSEEK_API_KEY', '## 3. 参数与调用模板', '## 5. 保存Notebook与下载结果', '文件 → 上传笔记本', 'Download raw file']:
                if term == 'Download raw file':
                    self.assertIn(term, (ROOT / skill['notebook_entry']).read_text('utf-8'))
                else:
                    self.assertIn(term, running)

    def test_notebook_archives_are_exact_native_notebooks(self):
        for skill in read_json(ROOT / 'NAVIGATION.json')['skills']:
            notebook = ROOT / skill['notebook']
            with zipfile.ZipFile(ROOT / skill['notebook_zip']) as archive:
                self.assertEqual(archive.namelist(), [notebook.name])
                self.assertEqual(archive.read(notebook.name), notebook.read_bytes())
            nb = read_json(notebook)
            self.assertEqual(nb['nbformat'], 4)
            self.assertEqual(len({c['id'] for c in nb['cells']}), len(nb['cells']))
            self.assertTrue(all(c['cell_type'] in ('markdown','code','raw') for c in nb['cells']))

    def test_homepage_notebook_links_use_reliable_retrieval_page(self):
        nav = read_json(ROOT / 'NAVIGATION.json')
        for name in ['README.md', 'START_HERE_zh-CN.md']:
            text = (ROOT / name).read_text('utf-8')
            links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', text)
            self.assertFalse(any(link.endswith('.ipynb') for link in links))
        for skill in nav['skills']:
            entry = (ROOT / skill['notebook_entry']).read_text('utf-8')
            self.assertIn('https://github.com/CCcolab/AI4OrgChem-data-processing/raw/refs/heads/main/' + skill['notebook_zip'], entry)
            self.assertIn('https://colab.research.google.com/', entry)
            self.assertNotIn('colab.research.google.com/drive/', entry)

    def test_markdown_local_links_resolve(self):
        for path in ROOT.rglob('*.md'):
            if any(p.startswith('.') for p in path.relative_to(ROOT).parts):
                continue
            # SMARTS such as [CX3](=O) in code spans are chemical syntax, not links.
            prose = re.sub(r'```[\s\S]*?```|`[^`\n]+`', '', path.read_text('utf-8'))
            for target in re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', prose):
                target = target.strip().split(' "')[0].strip('<>')
                if not target or target.startswith(('#', 'http:', 'https:', 'mailto:')):
                    continue
                local = unquote(target.split('#')[0].split('?')[0])
                self.assertTrue((path.parent / local).resolve().is_relative_to(ROOT), (path, target))
                self.assertTrue((path.parent / local).exists(), (path, target))

    def test_notebook_identity_and_default_collapse(self):
        nbfile = PAGE / 'organic-smiles-rdkit.ipynb'
        proof = read_json(PAGE / 'PUBLICATION_CHECK.json')
        self.assertEqual(digest(nbfile.read_bytes()), proof['accepted_notebook_sha256'])
        nb = read_json(nbfile)
        self.assertEqual(len(nb['cells']), 13)
        metadata = nb['cells'][1]['metadata']
        self.assertTrue(metadata['collapsed'])
        self.assertTrue(metadata['jupyter']['source_hidden'])
        self.assertEqual(len([o for c in nb['cells'] for o in c.get('outputs', []) if 'image/png' in o.get('data', {})]), 2)
        self.assertNotIn('colab.research.google.com/drive/', nbfile.read_text('utf-8'))

    def test_embedded_resources_match_delivered_sources(self):
        nb = read_json(PAGE / 'organic-smiles-rdkit.ipynb')
        values = {}
        for node in ast.parse(''.join(nb['cells'][1]['source'])).body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        values[target.id] = node.value.value
        payload = base64.b64decode(values['BUNDLE_B64'])
        self.assertEqual(digest(payload), values['BUNDLE_SHA256'])
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            self.assertIsNone(archive.testzip())
            for name in archive.namelist():
                self.assertEqual(archive.read(name), (PAGE / name).read_bytes(), name)

    def test_teaching_inputs_and_parameters_are_explicit(self):
        provenance = read_json(PAGE / 'data-provenance.json')
        self.assertEqual(digest((PAGE / 'molecules.csv').read_bytes()), provenance['sha256'])
        rows = list(csv.DictReader(io.StringIO((PAGE / 'molecules.csv').read_text('utf-8'))))
        self.assertEqual(len(rows), 14)
        self.assertEqual(len({r['id'] for r in rows}), 14)
        self.assertEqual(rows[10]['smiles'], 'C1CC')
        self.assertEqual(rows[11]['smiles'], '')
        self.assertEqual(provenance['kind'], 'AUTHORED_TEACHING_STRUCTURES_NOT_EXPERIMENTAL_DATA')
        params = read_json(PAGE / 'parameters.json')
        self.assertEqual((params['radius'], params['fp_size'], params['reference_id']), (2, 2048, '005'))
        self.assertTrue(params['include_chirality'])

    def test_material_download_preserves_accepted_sources(self):
        with zipfile.ZipFile(PAGE / 'organic-smiles-rdkit-materials.zip') as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(len(archive.namelist()), 16)
            for name in archive.namelist():
                self.assertEqual(archive.read(name), (PAGE / name).read_bytes(), name)

    def test_example_download_has_two_verified_numeric_runs(self):
        with zipfile.ZipFile(PAGE / 'example-results.zip') as archive:
            self.assertIsNone(archive.testzip())
            manifest = json.loads(archive.read('SHA256_MANIFEST.json'))
            self.assertEqual(len(manifest), 16)
            self.assertEqual(set(archive.namelist()), {r['file'] for r in manifest} | {'SHA256_MANIFEST.json'})
            for item in manifest:
                self.assertEqual(digest(archive.read(item['file'])), item['sha256'])
                self.assertNotRegex(item['file'], r'(?i)trace|receipt|agent|\.env|token|database')
            for run, radius in [('run-1', 2), ('run-2', 3)]:
                result = json.loads(archive.read(run + '/numerical-result.json'))
                self.assertEqual((result['records'], result['valid'], result['rejected']), (14, 12, 2))
                self.assertEqual(result['parameters']['radius'], radius)
                self.assertTrue(all(result['checks'].values()))
                self.assertEqual(result['new_rhf'], 'NOT_ACCEPTED')

    def test_displayed_pngs_are_native_notebook_outputs(self):
        nb = read_json(PAGE / 'organic-smiles-rdkit.ipynb')
        images = [base64.b64decode(''.join(o['data']['image/png'])) for c in nb['cells'] for o in c.get('outputs', []) if 'image/png' in o.get('data', {})]
        for name, data in zip(['example-molecules.png', 'example-similarity.png'], images):
            self.assertTrue(data.startswith(b'\x89PNG\r\n\x1a\n'))
            self.assertEqual((PAGE / name).read_bytes(), data)

    def test_full_file_inventory_and_sha256(self):
        manifest = read_json(ROOT / 'PUBLIC_MANIFEST.json')
        rows = manifest['files']
        expected = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not any(part.startswith('.') and part != '.gitattributes' and part != '.gitignore' and part not in ('.githooks', '.github') for part in p.relative_to(ROOT).parts) and p.relative_to(ROOT).as_posix() not in ('PUBLIC_MANIFEST.json', 'SHA256SUMS.txt') and '__pycache__' not in p.parts}
        self.assertIn('skills/organic-smiles-rdkit/SHA256SUMS.txt', expected)
        self.assertEqual({r['file'] for r in rows}, expected)
        for row in rows:
            self.assertEqual(digest((ROOT / row['file']).read_bytes()), row['sha256'])
        sums = {}
        for line in (ROOT / 'SHA256SUMS.txt').read_text('utf-8').splitlines():
            value, name = line.split('  ', 1)
            sums[name] = value
        self.assertEqual(set(sums), expected | {'PUBLIC_MANIFEST.json'})
        for name, value in sums.items():
            self.assertEqual(digest((ROOT / name).read_bytes()), value)

if __name__ == '__main__':
    unittest.main()
