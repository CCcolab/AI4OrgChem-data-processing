"""Exercise the actual packager and Git hooks, without network or real credentials."""
import json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
URL='https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/START_HERE_zh-CN.md'

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        parent=Path(os.environ.get('ADP_GUARD_TEST_ROOT',ROOT/'.guard-test-tmp'));parent.mkdir(parents=True,exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=parent);self.base=Path(self.temp.name)
        self.env=os.environ.copy();self.env['PATH']=str(Path(sys.executable).parent)+os.pathsep+self.env.get('PATH','')
    def tearDown(self):self.temp.cleanup()
    def entry(self,root):
        root.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/'PLATFORM_ENTRY.json',root/'PLATFORM_ENTRY.json')
        for name in ['README.md','START_HERE_zh-CN.md']:(root/name).write_text('Current entry: '+URL+'\n',encoding='utf-8')
    def git(self,root,*args,check=True):
        result=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,encoding='utf-8',errors='replace',env=self.env)
        if check and result.returncode:self.fail(result.stdout+result.stderr)
        return result
    def repository(self):
        root=self.base/'repo';self.entry(root)
        self.git(root,'init','--quiet','--initial-branch=main')
        for name in ['tools/check_platform_boundary.py','.githooks/pre-commit','.githooks/pre-push']:
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,p)
            if name.startswith('.githooks/'):p.chmod(0o755)
        self.git(root,'config','core.hooksPath','.githooks');self.git(root,'add','.')
        self.commit(root,'clean baseline')
        return root
    def commit(self,root,message,check=True,extra=()):
        return self.git(root,'-c','user.name=Guard Test','-c','user.email=guard@example.invalid','-c','commit.gpgsign=false',*extra,'commit','--quiet','-m',message,check=check)
    def test_packager_exports_only_passing_candidate(self):
        root=self.base/'candidate';self.entry(root);(root/'analysis.py').write_text('x=1\n',encoding='utf-8');out=self.base/'good.zip'
        p=subprocess.run([sys.executable,'-B',str(ROOT/'tools/package_checked_skill.py'),'--input',str(root),'--output',str(out)],capture_output=True,text=True,env=self.env)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr);self.assertTrue(out.exists());self.assertTrue(Path(str(out)+'.sha256').exists())
    def test_packager_blocks_before_export(self):
        root=self.base/'candidate';self.entry(root);bad=root/'scripts/start-platform.ps1';bad.parent.mkdir();bad.write_text('echo old\n');out=self.base/'bad.zip'
        p=subprocess.run([sys.executable,'-B',str(ROOT/'tools/package_checked_skill.py'),'--input',str(root),'--output',str(out)],capture_output=True,text=True,env=self.env)
        self.assertNotEqual(p.returncode,0);self.assertFalse(out.exists());self.assertFalse(Path(str(out)+'.sha256').exists())
    def test_real_precommit_rejects_old_launcher(self):
        root=self.repository();before=self.git(root,'rev-parse','HEAD').stdout
        bad=root/'scripts/start-platform.ps1';bad.parent.mkdir();bad.write_text('echo old\n');self.git(root,'add','scripts/start-platform.ps1')
        p=self.commit(root,'must be blocked',check=False)
        self.assertNotEqual(p.returncode,0,p.stdout+p.stderr);self.assertIn('retired_launcher',p.stdout+p.stderr)
        self.assertEqual(before,self.git(root,'rev-parse','HEAD').stdout)
    def test_real_prepush_reads_head_not_worktree(self):
        root=self.repository();bare=self.base/'remote.git'
        subprocess.run(['git','init','--quiet','--bare','--initial-branch=main',str(bare)],check=True,capture_output=True,env=self.env)
        self.git(root,'remote','add','origin',str(bare));self.git(root,'push','--quiet','origin','main')
        before=self.git(bare,'rev-parse','main').stdout
        bad=root/'payload.py';bad.write_text('from ai4orgchem_data_processing.localweb.app import create_app\n');self.git(root,'add','payload.py')
        self.commit(root,'simulate bypassed precommit',extra=('-c','core.hooksPath='+str(self.base/'no-hooks')))
        bad.write_text('x=1\n')
        p=self.git(root,'push','origin','main',check=False)
        self.assertNotEqual(p.returncode,0,p.stdout+p.stderr);self.assertIn('retired_service_import',p.stdout+p.stderr)
        self.assertEqual(before,self.git(bare,'rev-parse','main').stdout)

if __name__=='__main__':unittest.main()
