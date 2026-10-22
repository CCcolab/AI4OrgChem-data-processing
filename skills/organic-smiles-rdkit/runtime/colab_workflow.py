"""Companion module for the five short Colab cells. No credentials in this file."""
from pathlib import Path
import base64,hashlib,html,importlib.util,io,json,os,subprocess,sys,tempfile,uuid,zipfile

def _module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def _ready():
    if 'google.colab' not in sys.modules:return
    from google.colab import output
    for attempt in range(3):
        try:
            state=output.eval_js('document.readyState',timeout_sec=18)
            if state in ('interactive','complete'):return
        except Exception:pass
    raise RuntimeError('Colab输出框架未就绪。未重新调用模型；请只重试当前显示步骤。')

class Lab:
    @classmethod
    def prepare(cls,bundle,notebook=None,base=None):
        bundle=Path(bundle);digest=hashlib.sha256(bundle.read_bytes()).hexdigest()
        root=Path(base) if base else (Path('/content') if 'google.colab' in sys.modules else Path.cwd())
        workspace=root/('organic-rdkit-'+digest[:16]);workspace.mkdir(exist_ok=True)
        with zipfile.ZipFile(bundle) as z:
            names=z.namelist()
            if len(names)!=len(set(names)) or any(Path(n).name!=n or '\\' in n or ':' in n for n in names):
                raise ValueError('配套模块含无效路径或重复文件。')
            if sum(i.file_size for i in z.infolist())>4_000_000:raise ValueError('配套包过大。')
            resources={n:z.read(n) for n in names}
            rows=json.loads(resources['resource-manifest.json'])
            for row in rows:
                if hashlib.sha256(resources[row['file']]).hexdigest()!=row['sha256']:raise ValueError('配套资源哈希错误。')
            for name,data in resources.items():
                p=workspace/name
                if p.exists() and p.read_bytes()!=data:raise ValueError('运行模块被修改；拒绝复用。')
                if not p.exists():p.write_bytes(data)
        python=workspace/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        marker=workspace/'environment-ready.json'
        reused=False
        if marker.exists() and python.exists():
            old=json.loads(marker.read_text('utf-8'))
            reused=(old.get('bundle_sha256')==digest and old.get('host_python')==sys.version)
        if not reused:
            subprocess.run([sys.executable,'-m','venv','--without-pip',str(workspace/'.venv')],check=True,capture_output=True,timeout=90)
            p=subprocess.run([sys.executable,'-m','pip','--python',str(python),'install','--only-binary=:all:','--retries','0','--timeout','20',
                              '--report',str(workspace/'pip-report.json'),'--disable-pip-version-check','-r',str(workspace/'requirements-colab.txt')],
                             capture_output=True,text=True,timeout=180)
            (workspace/'pip-install.log').write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
            if p.returncode:raise RuntimeError('依赖安装失败；停止。日志保存在运行目录。')
        check=subprocess.run([sys.executable,'-m','pip','--python',str(python),'check'],capture_output=True,text=True,timeout=30)
        (workspace/'pip-check.log').write_text(check.stdout+'\n'+check.stderr,encoding='utf-8')
        if check.returncode:raise RuntimeError('独立环境依赖冲突，停止。')
        probe=subprocess.run([str(python),'-c','import os;os.environ["MPLBACKEND"]="Agg";import json,platform,rdkit,numpy,matplotlib;print(json.dumps(dict(python=platform.python_version(),rdkit=rdkit.__version__,numpy=numpy.__version__,matplotlib=matplotlib.__version__)))'],capture_output=True,text=True,check=True,timeout=30)
        versions=json.loads(probe.stdout)
        if any(versions[k]!=v for k,v in {'rdkit':'2026.03.6','numpy':'2.4.6','matplotlib':'3.11.2'}.items()):raise RuntimeError('环境版本与合同不一致。')
        marker.write_text(json.dumps({'bundle_sha256':digest,'host_python':sys.version,'versions':versions}),encoding='utf-8')
        self=cls();self.workspace=workspace;self.python=python;self.bundle=bundle;self.notebook=notebook
        # Reinitialization preserves prior successful calls without reusing a failed task.
        self.history=[]
        for p in sorted(workspace.glob('run-*')):
            if (p/'run-receipt.json').is_file() and json.loads((p/'run-receipt.json').read_text('utf-8')).get('status')=='PASS_REAL_MODEL_AND_TOOL_CALL':self.history.append(p)
        print(('PASS：复用并复核已有独立环境。' if reused else 'PASS：首次独立环境安装完成。'),json.dumps(versions))
        return self

    def call_skill(self,*,skill_text,parameters,env_file=''):
        skill=self.workspace/'SKILL.md'
        if skill_text!=skill.read_text('utf-8'):raise ValueError('传入的Skill与已核验SKILL.md不同。')
        # Original agent also checks the full manifest and parameter schema before API work.
        cred=_module(self.workspace/'credential_config.py','organic_credentials')
        key=cred.load_credential(env_file)
        output=self.workspace/('run-'+uuid.uuid4().hex)
        params=self.workspace/('params-'+uuid.uuid4().hex+'.json')
        params.write_text(json.dumps(parameters,ensure_ascii=False,allow_nan=False),encoding='utf-8')
        runner=self.workspace/'runner.py'
        runner.write_text("from pathlib import Path\nimport json,os,sys\nfrom skill_agent import run\nrun(Path(__file__).parent,json.loads(Path(sys.argv[1]).read_text('utf-8')),Path(sys.argv[2]),os.environ['DEEPSEEK_API_KEY'],sys.argv[3])\n",encoding='utf-8')
        env=dict(os.environ);env['DEEPSEEK_API_KEY']=key;env['MPLBACKEND']='Agg'
        try:
            proc=subprocess.Popen([str(self.python),'-B',str(runner),str(params),str(output),'COLAB' if 'google.colab' in sys.modules else 'LOCAL'],
                                  env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            try:stdout,stderr=proc.communicate(timeout=230)
            except subprocess.TimeoutExpired:
                proc.terminate()
                try:proc.communicate(timeout=10)
                except subprocess.TimeoutExpired:proc.kill();proc.communicate(timeout=5)
                raise RuntimeError('执行超时，已终止子进程；本轮未验收。') from None
        finally:env.pop('DEEPSEEK_API_KEY',None);key=None
        if proc.returncode:
            failure=json.loads((output/'failure.json').read_text('utf-8')) if (output/'failure.json').exists() else {'message':'调用初始化失败'}
            raise RuntimeError('真实调用失败：'+failure['message'])
        receipt=json.loads((output/'run-receipt.json').read_text('utf-8'))
        if receipt['status']!='PASS_REAL_MODEL_AND_TOOL_CALL':raise RuntimeError('没有真实模型与工具调用回执。')
        self.history.append(output)
        print('PASS：真实Skill调用完成；下一步查看结果。')
        return output

    def _presentation(self):return _module(self.workspace/'result_presentation.py','organic_result_presentation')

    def show_results(self,output):
        from IPython.display import HTML,display
        output=Path(output);b=self._presentation().display_bundle(output);s=b['status']
        _ready()
        parts=['<section><h3>程序回执（文件已核验）</h3><p>本轮ZIP：'+html.escape(s['archive'])+' · '+str(s['archive_bytes'])+'字节；清单'+str(s['manifest_files'])+'项</p>',
               '<p>SHA-256：<code>'+s['archive_sha256']+'</code></p>',
               '<p>文件状态以程序回执、清单和实际下载文件为准。</p>']
        if b['model_file_claim']=='CONTRADICTED':parts.append('<p>模型的文件状态声明与程序证据不一致；实际结果文件已核验。</p>')
        for name,title in [('molecules.png','分子结构图'),('similarity.png','Morgan指纹相似度图')]:
            parts.append('<h3>'+title+'</h3><img alt="'+title+'" style="max-width:100%;height:auto" src="data:image/png;base64,'+base64.b64encode((output/name).read_bytes()).decode()+'">')
        parts.append('<h3>模型解释</h3>'+b['raw_model_html']+'</section>')
        display(HTML(''.join(parts)))

    def show_downloads(self,output):
        from IPython.display import HTML,display
        self._presentation().verify_download(output)
        combined=self.workspace/'organic-smiles-rdkit-all-runs.zip'
        with zipfile.ZipFile(combined,'w',zipfile.ZIP_DEFLATED) as z:
            for i,p in enumerate(self.history):
                self._presentation().verify_download(p)
                for f in sorted(p.iterdir()):
                    if f.is_file():z.write(f,f'run-{i+1}/'+f.name)
            z.writestr('run-index.json',json.dumps([json.loads((p/'run-receipt.json').read_text('utf-8')) for p in self.history],ensure_ascii=False,indent=2))
        _ready()
        items=[(Path(output)/'organic-smiles-rdkit-results.zip','下载本轮结果ZIP'),(combined,'下载全部运行结果ZIP'),
               (self.workspace/'SKILL.md','下载SKILL.md'),(self.bundle,'下载完整配套模块ZIP')]
        if self.notebook:
            nb=self.workspace/'organic-smiles-rdkit.ipynb'
            nb.write_text(json.dumps(self.notebook,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
            items.insert(3,(nb,'下载运行Notebook源码'))
        parts=['<h3>保存与下载</h3><p>下面下载已有文件，不会重新调用模型。含本次输出的Notebook另用“文件→保存/下载”。</p>']
        for path,label in items:
            raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
            parts.append('<p><a role="button" download="'+html.escape(path.name,quote=True)+'" href="data:application/octet-stream;base64,'+base64.b64encode(raw).decode()+'" style="display:inline-block;padding:10px;background:#17675f;color:white">'+label+'</a><br>'+str(len(raw))+'字节 · SHA-256：<code>'+digest+'</code></p>')
        display(HTML(''.join(parts)))
