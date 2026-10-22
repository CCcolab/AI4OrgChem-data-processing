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
from rdkit_notebook_resources import resource_bytes

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
        self.assertTrue(nav['render_empty_categories'])
        assigned = [s for c in cats for s in c['skills']]
        self.assertCountEqual(assigned, [s['id'] for s in nav['skills']])
        self.assertEqual(len(set(assigned)), len(assigned))

    def test_only_two_available_pages_are_rendered(self):
        nav = read_json(ROOT / 'NAVIGATION.json')
        self.assertEqual(len(nav['skills']), 2)
        for name in ['README.md', 'START_HERE_zh-CN.md']:
            text = (ROOT / name).read_text('utf-8')
            for cat in nav['categories']:
                self.assertIn('## ' + cat['title'],text)
            for skill in nav['skills']:
                for key in ['run']:
                    self.assertTrue((ROOT / skill[key]).is_file())
                    self.assertIn(skill[key], text)

    def test_training_list_contains_all_33_unique_skills_and_only_real_links(self):
        nav=read_json(ROOT/'NAVIGATION.json')
        items=nav['training_catalog']
        self.assertEqual(len(items),33)
        self.assertEqual(len({s['id'] for s in items}),33)
        self.assertCountEqual([x for c in nav['categories'] for x in c['catalog_skills']],[s['id'] for s in items])
        self.assertEqual([len(c['catalog_skills']) for c in nav['categories']],[2,3,4,7,2,10,4,1])
        for filename in ['README.md','START_HERE_zh-CN.md']:
            text=(ROOT/filename).read_text('utf-8')
            self.assertEqual(len(re.findall(r'^- ',text,re.M)),33)
            self.assertNotIn('| ---',text)
            for skill in items:
                if skill['has_learning_page']:
                    self.assertIn('- ['+skill['title']+']('+skill['page']+')',text)
                    self.assertTrue((ROOT/skill['page']).is_file())
                else:
                    self.assertIn('- '+skill['title']+'\n',text)
                    self.assertNotIn('page',skill)

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
            if skill.get('layout') == 'five-part-colab-modules-v1':
                nb=read_json(ROOT/skill['notebook'])
                code=[''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code']
                self.assertEqual(len(code),5)
                self.assertTrue(all(len(c.splitlines())<=20 for c in code))
                self.assertIn('skill_file.read_text',code[2])
                self.assertIn('lab.call_skill(skill_text=skill_text, parameters=parameters)',code[2])
                self.assertNotIn('RESOURCE_TEXT',''.join(code))
                self.assertTrue(resource_bytes())
                continue
            if skill.get('layout') == 'single-readme-three-files-v1':
                text=(ROOT / skill['run']).read_text('utf-8')
                blocks=re.findall(r'(?ms)^~~~~python\n(.*?)^~~~~[ \t]*$',text)
                notebook=read_json(ROOT / skill['notebook'])
                self.assertEqual(blocks,[''.join(c['source']) for c in notebook['cells'] if c['cell_type']=='code'])
                prose=re.sub(r'(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$','',text)
                self.assertEqual(len(re.findall(r'^## ',prose,re.M)),3)
                self.assertIn('SKILL.md',text)
                self.assertIn('sources.json',prose)
                self.assertIn('data-provenance.json',prose)
                self.assertIn('radius=3',prose)
                continue
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
            if skill['id']=='organic-smiles-rdkit':continue
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
            self.assertFalse(any(link.endswith('.ipynb') and not link.startswith('https://colab.research.google.com/github/') for link in links))
            self.assertEqual(len(links),len(nav['skills']))
            self.assertNotIn('教学与来源',text)
        for skill in nav['skills']:
            entry = (ROOT / skill['notebook_entry']).read_text('utf-8')
            for target in skill.get('downloads',{'notebook':skill.get('notebook_zip')}).values():
                self.assertIn('https://github.com/CCcolab/AI4OrgChem-data-processing/raw/'+skill.get('download_source_ref','refs/heads/main')+'/'+target,entry)
            if skill['id']!='organic-smiles-rdkit':self.assertIn('https://colab.research.google.com/', entry)
            self.assertNotIn('colab.research.google.com/drive/', entry)

    def test_direct_colab_routes_are_pinned_and_match_delivered_notebooks(self):
        from urllib.parse import urlparse
        for skill in read_json(ROOT / 'NAVIGATION.json')['skills']:
            url=urlparse(skill['colab_url'])
            self.assertEqual(url.scheme,'https')
            self.assertEqual(url.netloc,'colab.research.google.com')
            self.assertFalse(url.query)
            self.assertFalse(url.fragment)
            ref=skill.get('colab_source_commit',skill.get('colab_source_ref'))
            self.assertRegex(ref,r'^(?:[a-f0-9]{40}|main)$')
            self.assertEqual(url.path,'/github/CCcolab/AI4OrgChem-data-processing/blob/'+ref+'/'+skill['notebook'])
            self.assertEqual(digest((ROOT/skill['notebook']).read_bytes()),skill['colab_notebook_sha256'])
            running=(ROOT/skill['run']).read_text('utf-8')
            if skill['id']=='organic-smiles-rdkit':
                intro=''.join(read_json(ROOT/skill['notebook'])['cells'][0]['source'])
                self.assertNotIn('[▶ 在 Colab 运行]',running)
                self.assertNotIn('包括私有代码库',running)
                self.assertIn('[打开运行Notebook](organic-smiles-rdkit.ipynb)',running)
                self.assertIn('[▶ 在 Colab 运行](https://colab.research.google.com/github/CCcolab/AI4OrgChem-data-processing/blob/main/',intro)
                for term in ['首次运行：账号授权、保存副本与操作步骤','包括私有代码库','保存副本','repo','gist','DEEPSEEK_API_KEY','ENV_FILE','文件 → 下载 → 下载.ipynb']:
                    self.assertIn(term,intro)
            else:
                self.assertIn('[▶ 在 Colab 运行]('+skill['colab_url']+')',running)
                self.assertIn('包括私有代码库',running)
                self.assertIn('保存副本',running)
                self.assertIn('repo',running)
            self.assertNotRegex(skill['colab_url'],r'(?i)token|access_token|github_pat|ghp_')

    def test_markdown_local_links_resolve(self):
        for path in ROOT.rglob('*.md'):
            if any(p.startswith('.') for p in path.relative_to(ROOT).parts):
                continue
            # SMARTS such as [CX3](=O) in code spans are chemical syntax, not links.
            prose = re.sub(r'(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$', '', path.read_text('utf-8'))
            prose = re.sub(r'`[^`\n]+`', '', prose)
            for target in re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', prose):
                target = target.strip().split(' "')[0].strip('<>')
                if not target or target.startswith(('#', 'http:', 'https:', 'mailto:')):
                    continue
                local = unquote(target.split('#')[0].split('?')[0])
                self.assertTrue((path.parent / local).resolve().is_relative_to(ROOT), (path, target))
                self.assertTrue((path.parent / local).exists(), (path, target))

    def test_notebook_identity_and_default_collapse(self):
        nbfile=PAGE/'organic-smiles-rdkit.ipynb'
        nb=read_json(nbfile)
        attachment=nb['metadata']['adp_runtime_bundle']
        self.assertEqual(attachment['sha256'],digest((PAGE/'runtime/rdkit-runtime.zip').read_bytes()))
        self.assertEqual(len(nb['cells']),10)
        self.assertEqual(nb['cells'][1]['metadata']['cellView'],'form')
        self.assertTrue(all(c['execution_count'] is None and not c['outputs'] for c in nb['cells'] if c['cell_type']=='code'))
        self.assertNotIn('colab.research.google.com/drive/',nbfile.read_text('utf-8'))

    def test_embedded_resources_match_delivered_sources(self):
        resources=resource_bytes()
        self.assertEqual(len(resources),15)
        self.assertEqual(resources['SKILL.md'],(PAGE/'SKILL.md').read_bytes())
        for name in ['molecule_tool.py','skill_agent.py','credential_config.py','result_presentation.py']:
            compile(resources[name],name,'exec')
        self.assertNotIn('BUNDLE_B64',''.join(read_json(PAGE/'organic-smiles-rdkit.ipynb')['cells'][1]['source']))

    def test_teaching_inputs_and_parameters_are_explicit(self):
        resources=resource_bytes()
        provenance=json.loads(resources['data-provenance.json'])
        self.assertEqual(digest(resources['molecules.csv']),provenance['sha256'])
        rows=list(csv.DictReader(io.StringIO(resources['molecules.csv'].decode())))
        self.assertEqual(len(rows),14)
        self.assertEqual(len({r['id'] for r in rows}),14)
        self.assertEqual(rows[10]['smiles'],'C1CC')
        self.assertEqual(rows[11]['smiles'],'')
        self.assertEqual(provenance['kind'],'AUTHORED_TEACHING_STRUCTURES_NOT_EXPERIMENTAL_DATA')
        params=json.loads(resources['parameters.json'])
        self.assertEqual((params['radius'],params['fp_size'],params['reference_id']),(2,2048,'005'))
        self.assertTrue(params['include_chirality'])

    def test_minimal_skill_directory_has_only_learning_files(self):
        self.assertEqual({p.name for p in PAGE.iterdir()},{'README.md','SKILL.md','organic-smiles-rdkit.ipynb','assets','runtime'})
        self.assertEqual({p.name for p in (PAGE/'assets').iterdir()},{'example-molecules.png','example-similarity.png'})
        self.assertFalse(any(p.is_symlink() for p in PAGE.rglob('*')))
        self.assertEqual(resource_bytes()['SKILL.md'],(PAGE/'SKILL.md').read_bytes())
        self.assertFalse((ROOT/'docs/RDKIT_PAGE_CHECK.md').exists())

    def test_readme_merges_learning_configuration_sources_and_downloads(self):
        text=(PAGE/'README.md').read_text('utf-8')
        prose=re.sub(r'(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$','',text)
        for term in ['学习目标','必要知识与参考资料','数据从哪里来','调用模板与参数含义','radius=3','实际参数调用案例与输出结果','分别下载Notebook和SKILL.md']:
            self.assertIn(term,prose)
        for name in ['RUNNING.md','TEACHING.md','NOTEBOOK.md','DOWNLOADS.md','PUBLICATION_CHECK.json','SOURCE_REVIEW.json','materials.zip','notebook.zip']:
            self.assertNotIn(']('+name,prose)
        for source in json.loads(resource_bytes()['sources.json']):
            if source['id']!='tanimoto':self.assertIn(source['url'].split('#')[0],prose)
        self.assertIn('www.rdkit.org',prose)
        self.assertIn('www.daylight.com',prose)

    def test_displayed_pngs_are_native_notebook_outputs(self):
        nb = read_json(PAGE / 'organic-smiles-rdkit.ipynb')
        images = [base64.b64decode(''.join(o['data']['image/png'])) for c in nb['cells'] for o in c.get('outputs', []) if 'image/png' in o.get('data', {})]
        for name, data in zip(['example-molecules.png', 'example-similarity.png'], images):
            self.assertTrue(data.startswith(b'\x89PNG\r\n\x1a\n'))
            self.assertEqual((PAGE / 'assets' / name).read_bytes(), data)

    def test_full_file_inventory_and_sha256(self):
        manifest = read_json(ROOT / 'PUBLIC_MANIFEST.json')
        rows = manifest['files']
        expected = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not any(part.startswith('.') and part != '.gitattributes' and part != '.gitignore' and part not in ('.githooks', '.github') for part in p.relative_to(ROOT).parts) and p.relative_to(ROOT).as_posix() not in ('PUBLIC_MANIFEST.json', 'SHA256SUMS.txt') and '__pycache__' not in p.parts}
        self.assertNotIn('skills/organic-smiles-rdkit/SHA256SUMS.txt', expected)
        self.assertIn('skills/organic-smiles-rdkit/README.md',expected)
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
