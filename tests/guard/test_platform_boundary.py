import base64, importlib.util, io, json, os, subprocess, sys, tarfile, tempfile, unittest, zipfile
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('boundary',ROOT/'tools/check_platform_boundary.py')
boundary=importlib.util.module_from_spec(spec);spec.loader.exec_module(boundary)

def bundle(entries):
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
        for name,data in entries.items():z.writestr(name,data)
    return b.getvalue()

class BoundaryTests(unittest.TestCase):
    def inspect(self,name,data,rule=None,public=False):
        g=boundary.Guard(public=public);g.inspect(name,data.encode() if isinstance(data,str) else data)
        if rule:self.assertIn(rule,[x['rule'] for x in g.findings],g.result())
        else:self.assertFalse(g.findings,g.result())
        return g
    def test_shared_analysis_is_allowed(self):self.inspect('src/ai4orgchem_data_processing/analysis/fitting.py','import numpy as np\ndef fit(x,y): return np.polyfit(x,y,1)\n')
    def test_history_explanation_is_allowed(self):self.inspect('docs/cleanup.md','旧8765服务已移除；这里是历史边界说明。')
    def test_module_path_is_blocked(self):self.inspect('src/ai4orgchem_data_processing/localweb/app.py','x=1','retired_service_module')
    def test_renamed_import_is_blocked(self):self.inspect('renamed.py','from ai4orgchem_data_processing.localweb.app import create_app','retired_service_import')
    def test_relative_import_is_blocked(self):self.inspect('renamed.py','from ..localweb.guard import Job','retired_service_import')
    def test_renamed_launcher_is_blocked(self):self.inspect('run-anything.ps1','python -m ai4orgchem_data_processing.deployment.control start','retired_launcher_command')
    def test_launcher_filename_is_blocked(self):self.inspect('scripts/start-platform.ps1','# disabled\n','retired_launcher')
    def test_old_installer_is_blocked(self):self.inspect('scripts/install-local.ps1','# installer\n','retired_launcher')
    def test_old_frontend_tree_is_blocked(self):self.inspect('web/index.html','<html>legacy</html>','retired_web_tree')
    def test_port_binding_is_blocked(self):self.inspect('service.py','import uvicorn\nuvicorn.run(app,port=8765)','retired_port_binding')
    def test_socket_binding_is_blocked(self):self.inspect('service.py',"sock.bind(('127.0.0.1',8765))",'retired_port_binding')
    def test_port_default_is_blocked(self):self.inspect('service.py',"p.add_argument('--port',default=8765)",'retired_port_binding')
    def test_serve_cli_is_blocked(self):self.inspect('cli.py',"sub.add_parser('serve')",'retired_serve_cli')
    def test_obsolete_bundle_name_is_blocked(self):self.inspect('AI4OrgChem-data-processing-0.1.0-windows-delivery-r19.zip',bundle({'x.txt':'x'}),'retired_deployment_bundle')
    def test_zip_wheel_module_is_blocked(self):self.inspect('delivery.zip',bundle({'core.whl':bundle({'ai4orgchem_data_processing/localweb/app.py':'x=1'})}),'retired_service_module')
    def test_notebook_embedded_wheel_is_blocked(self):
        raw=bundle({'core.whl':bundle({'ai4orgchem_data_processing/deployment/control.py':'x=1'})})
        nb={'cells':[{'cell_type':'code','source':["BUNDLE_B64 = "+repr(base64.b64encode(raw).decode())]}]}
        self.inspect('lesson.ipynb',json.dumps(nb),'retired_service_module')
    def test_notebook_zip_attachment_is_blocked(self):
        raw=bundle({'start-platform.ps1':'echo nope'})
        nb={'cells':[{'cell_type':'markdown','source':['result'],'attachments':{'x':{'application/zip':base64.b64encode(raw).decode()}}}]}
        self.inspect('lesson.ipynb',json.dumps(nb),'retired_launcher')
    def test_clean_notebook_payload_is_allowed(self):
        raw=bundle({'molecules.csv':'id,smiles\n1,CCO'})
        self.inspect('lesson.ipynb',json.dumps({'cells':[{'cell_type':'code','source':["RESOURCE_B64 = "+repr(base64.b64encode(raw).decode())]}]}))
    def test_readable_notebook_resources_are_allowed(self):
        source='RESOURCE_TEXT = '+repr({'molecules.csv':'id,smiles\n1,CCO\n'})
        self.inspect('lesson.ipynb',json.dumps({'cells':[{'cell_type':'code','source':[source]}]}))
    def test_readable_notebook_resource_import_is_checked(self):
        source='RESOURCE_TEXT = '+repr({'renamed.py':'from ai4orgchem_data_processing.localweb.app import create_app\n'})
        self.inspect('lesson.ipynb',json.dumps({'cells':[{'cell_type':'code','source':[source]}]}),'retired_service_import')
    def test_runtime_metadata_cannot_hide_retired_code(self):
        raw=bundle({'renamed.py':'from ai4orgchem_data_processing.localweb.app import create_app\n'})
        n={'cells':[],'metadata':{'adp_runtime_bundle':{'schema':'adp-notebook-runtime-v1','zip_base64':base64.b64encode(raw).decode()}}}
        self.inspect('lesson.ipynb',json.dumps(n),'retired_service_import')
    def test_runtime_metadata_clean_module_allowed(self):
        raw=bundle({'analysis.py':'value=1\n'})
        n={'cells':[],'metadata':{'adp_runtime_bundle':{'schema':'adp-notebook-runtime-v1','zip_base64':base64.b64encode(raw).decode()}}}
        self.inspect('lesson.ipynb',json.dumps(n))
    def test_runtime_metadata_corruption_rejected(self):
        n={'cells':[],'metadata':{'adp_runtime_bundle':{'schema':'adp-notebook-runtime-v1','zip_base64':'not valid'}}}
        self.inspect('lesson.ipynb',json.dumps(n),'invalid_embedded_payload')
    def test_readable_notebook_resource_filename_is_checked(self):
        source='RESOURCE_TEXT = '+repr({'start-platform.ps1':'echo old\n'})
        self.inspect('lesson.ipynb',json.dumps({'cells':[{'cell_type':'code','source':[source]}]}),'retired_launcher')
    def test_readable_notebook_resource_must_be_literal(self):
        self.inspect('lesson.py','RESOURCE_TEXT = build_dynamic_resources()','invalid_inline_resources')
    def test_malformed_payload_is_blocked(self):self.inspect('lesson.py',"BUNDLE_B64 = 'not base64'",'invalid_embedded_payload')
    def test_corrupt_archive_is_blocked(self):self.inspect('x.zip',b'PK\x03\x04broken','unreadable_archive')
    def test_base64_signature_is_not_a_payload(self):self.inspect('signatures.py',"MAGIC = ('UEsDB', 'H4sI')")
    def test_corrupt_gzip_is_blocked(self):self.inspect('x.tar.gz',b'\x1f\x8bbroken','unreadable_archive')
    def test_archive_traversal_is_blocked(self):self.inspect('x.zip',bundle({'../escape.py':'x=1'}),'unsafe_archive_path')
    def test_tar_launcher_is_blocked(self):
        out=io.BytesIO()
        with tarfile.open(fileobj=out,mode='w:gz') as t:
            b=b'echo old';i=tarfile.TarInfo('scripts/start-local.ps1');i.size=len(b);t.addfile(i,io.BytesIO(b))
        self.inspect('x.tar.gz',out.getvalue(),'retired_launcher')
    def test_private_files_are_not_public(self):self.inspect('inputs/.env','example-not-a-key','private_material_in_publication',True)
    def test_private_drive_is_not_public(self):self.inspect('docs/note.md','https://'+'colab.research.google.com/'+'drive/example','private_machine_or_drive_reference',True)
    def test_size_budget_fails_closed(self):
        with patch.object(boundary,'MAX_FILE',2):self.inspect('x.txt','abc','inspection_budget_exceeded')
    def test_no_execution_during_inspection(self):self.inspect('tools/example.py',"raise RuntimeError('must not execute')")
    def test_staged_bytes_cannot_be_hidden_by_worktree(self):
        parent=os.environ.get('ADP_GUARD_TEST_ROOT')
        if parent:Path(parent).mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent) as temp:
            root=Path(temp)
            subprocess.run(['git','init','--quiet',str(root)],check=True,capture_output=True)
            (root/'payload.py').write_text('from ai4orgchem_data_processing.localweb.app import create_app\n',encoding='utf-8')
            subprocess.run(['git','-C',str(root),'add','payload.py'],check=True,capture_output=True)
            (root/'payload.py').write_text('x=1\n',encoding='utf-8')
            p=subprocess.run([sys.executable,'-B',str(ROOT/'tools/check_platform_boundary.py'),'--root',str(root),'--scope','staged','--skip-entry'],capture_output=True,text=True)
            self.assertEqual(p.returncode,1,p.stdout+p.stderr)
            self.assertIn('retired_service_import',p.stdout)

if __name__=='__main__':unittest.main()
