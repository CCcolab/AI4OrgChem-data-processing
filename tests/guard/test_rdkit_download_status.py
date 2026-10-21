"""Program evidence wins over model wording; failures never become PASS."""
from pathlib import Path
import hashlib, json, tempfile, types, unittest, zipfile
from rdkit_notebook_resources import resource_bytes

ROOT=Path(__file__).resolve().parents[2]
module=types.ModuleType('rdkit_file_presentation')
exec(compile(resource_bytes()['result_presentation.py'],'<Notebook:result_presentation.py>','exec'),module.__dict__)

class DownloadEvidenceTests(unittest.TestCase):
    def setUp(self):
        tmp=ROOT/'.guard-test-tmp';tmp.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=tmp)
        self.root=Path(self.temp.name)
        self.raw='本页未生成可下载文件；请本地运行（未执行）。<script>example</script>'
        for n in module.REQUIRED:(self.root/n).write_text('fixture\n',encoding='utf-8')
        (self.root/'SKILL.md').write_text('test-only Skill\n',encoding='utf-8')
        (self.root/'agent-explanation.md').write_text(self.raw,encoding='utf-8')
        self.params={'radius':2}
        self.write('numerical-result.json',{'status':'PASS_BOUNDED_RDKIT_ANALYSIS','checks':{'fixture_check':True},'parameters':self.params})
        self.receipt={'status':'PASS_REAL_MODEL_AND_TOOL_CALL','tool_calls':1,'parameters':self.params,'execution_location':'TEST_FIXTURE','skill_sha256':hashlib.sha256((self.root/'SKILL.md').read_bytes()).hexdigest()}
        self.write('run-receipt.json',self.receipt)
        self.pack()
    def tearDown(self):self.temp.cleanup()
    def write(self,n,v):(self.root/n).write_text(json.dumps(v),encoding='utf-8')
    def pack(self):
        names=list(module.REQUIRED)+['SKILL.md','agent-explanation.md','run-receipt.json']
        self.write('export-manifest.json',[{'file':n,'sha256':hashlib.sha256((self.root/n).read_bytes()).hexdigest()} for n in names])
        with zipfile.ZipFile(self.root/'organic-smiles-rdkit-results.zip','w') as z:
            for n in names+['export-manifest.json']:z.write(self.root/n,n)
    def test_denial_cannot_override_actual_files(self):
        view=module.display_bundle(self.root)
        self.assertEqual(view['status']['status'],'PASS_VERIFIED_DOWNLOAD')
        self.assertEqual(view['model_file_claim'],'CONTRADICTED')
        self.assertIn('本次文件已生成且ZIP校验通过',view['markdown'])
        self.assertNotIn('本页未生成可下载文件',view['markdown'])
        self.assertIn('<details>',view['raw_model_html'])
        self.assertNotIn('<script>',view['raw_model_html'])
        self.assertEqual((self.root/'agent-explanation.md').read_text('utf-8'),self.raw)
    def test_unflagged_model_text_is_not_certified(self):
        (self.root/'agent-explanation.md').write_text('请使用课末程序下载按钮。',encoding='utf-8');self.pack()
        self.assertEqual(module.display_bundle(self.root)['model_file_claim'],'NOT_FLAGGED_NOT_CERTIFIED')
    def test_tool_evidence_does_not_claim_zip_already_exists(self):
        (self.root/'organic-smiles-rdkit-results.zip').unlink()
        evidence=module.tool_file_evidence(self.root)
        self.assertEqual(evidence['status'],'FILES_WRITTEN_BY_PROGRAM')
        self.assertEqual(len(evidence['files']),8)
        self.assertIn('AFTER_FINAL_MODEL_REPLY',evidence['zip_status'])
        with self.assertRaises(ValueError):module.verify_download(self.root)
    def test_missing_actual_file_rejected(self):
        (self.root/'analysis.csv').unlink()
        with self.assertRaises(ValueError):module.display_bundle(self.root)
    def test_tampered_actual_file_rejected(self):
        (self.root/'analysis.csv').write_text('changed',encoding='utf-8')
        with self.assertRaises(ValueError):module.verify_download(self.root)
    def test_corrupt_archive_rejected(self):
        (self.root/'organic-smiles-rdkit-results.zip').write_bytes(b'broken zip')
        with self.assertRaises(zipfile.BadZipFile):module.verify_download(self.root)
    def test_wrong_receipt_parameters_rejected(self):
        self.receipt['parameters']={'radius':3};self.write('run-receipt.json',self.receipt);self.pack()
        with self.assertRaises(ValueError):module.verify_download(self.root)
    def test_failed_program_not_overridden_by_model(self):
        self.write('numerical-result.json',{'status':'FAIL','checks':{'fixture_check':False},'parameters':self.params});self.pack()
        with self.assertRaises(ValueError):module.display_bundle(self.root)
    def test_bad_skill_identity_rejected(self):
        self.receipt['skill_sha256']='0'*64;self.write('run-receipt.json',self.receipt);self.pack()
        with self.assertRaises(ValueError):module.verify_download(self.root)
    def test_duplicate_manifest_rejected(self):
        p=self.root/'export-manifest.json';m=json.loads(p.read_text('utf-8'));m.append(m[0]);self.write(p.name,m)
        with self.assertRaises(ValueError):module.verify_download(self.root)
    def test_nested_manifest_path_rejected(self):
        p=self.root/'export-manifest.json';m=json.loads(p.read_text('utf-8'));m.append({'file':'../outside','sha256':'0'*64});self.write(p.name,m)
        with self.assertRaises(ValueError):module.verify_download(self.root)
    def test_zip_member_set_mismatch_rejected(self):
        with zipfile.ZipFile(self.root/'organic-smiles-rdkit-results.zip','a') as z:z.writestr('extra.txt','not in manifest')
        with self.assertRaises(ValueError):module.verify_download(self.root)

if __name__=='__main__':unittest.main()
