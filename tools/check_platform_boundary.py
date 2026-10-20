"""Offline guard for current sources, Git index/HEAD and publication artifacts.

Only stdlib; inspect bytes without executing or extracting payloads. Historical
reports may mention the retired port. Executable modules/bindings are rejected.
"""
from __future__ import annotations
import argparse, ast, base64, gzip, hashlib, io, json, os, re, stat, subprocess, sys, tarfile, zipfile
from pathlib import Path, PurePosixPath

CANONICAL = 'https://github.com/CCcolab/AI4OrgChem-data-processing/blob/main/START_HERE_zh-CN.md'
BLOCKED_SCRIPTS = {'start-platform.ps1','stop-platform.ps1','status-platform.ps1',
                   'start-local.ps1','stop-local.ps1','status-local.ps1','configure-backend.ps1'}
EXCLUDED = {'.git','__pycache__','.pytest_cache','node_modules','build','dist','local-config',
            'publication','validation','deliveries','repro','environment'}
MAX_FILE = 64 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_MEMBERS = 25000
MAX_DEPTH = 9

class Guard:
    def __init__(self, public=False):
        self.public=public;self.findings=[];self.total=0;self.members=0;self.files=0;self.archives=0;self.embedded=0
    def fail(self, path, rule):
        item={'path':path,'rule':rule}
        if item not in self.findings and len(self.findings)<100:self.findings.append(item)
    def path(self, name, nested=False):
        value=name.replace('\\','/');p=PurePosixPath(value);parts=p.parts;lower=[x.lower() for x in parts]
        if nested and (value.startswith('/') or '..' in parts or any(':' in x for x in parts)):
            self.fail(name,'unsafe_archive_path')
        if any(x=='ai4orgchem_data_processing' and i+1<len(lower) and lower[i+1] in {'localweb','deployment'} for i,x in enumerate(lower)):
            self.fail(name,'retired_service_module')
        if p.name.lower() in BLOCKED_SCRIPTS:self.fail(name,'retired_launcher')
        if re.search(r'(?i)AI4OrgChem-data-processing.*(?:windows.*delivery|delivery-r1[5-9]|r1[5-9].*delivery)',p.name):
            self.fail(name,'retired_deployment_bundle')
        if self.public and (any(x in {'validation','local-config','internal-evidence','migration-backup'} for x in lower)
                            or p.name.lower() in {'.env','session-token.txt'} or p.suffix.lower() in {'.db','.sqlite','.sqlite3'}):
            self.fail(name,'private_material_in_publication')
    def decode_payload(self, value, label, depth, required=False):
        try:
            raw=base64.b64decode(value,validate=True)
        except (ValueError,TypeError):
            if required:self.fail(label,'invalid_embedded_payload')
            return
        if raw.startswith((b'PK',b'\x1f\x8b')):
            self.embedded+=1;self.inspect(label+('!payload.zip' if raw.startswith(b'PK') else '!payload.tar.gz'),raw,depth+1)
        elif required:self.fail(label,'unsupported_embedded_payload')
    def python(self, name, text, depth):
        try:tree=ast.parse(text)
        except (SyntaxError,ValueError):self.fail(name,'invalid_python');return
        for node in ast.walk(tree):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                modules=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or '']
                if any(re.search(r'(?:^|\.)(?:localweb|deployment\.control|deployment\.windows_broker)(?:\.|$)',m) for m in modules):
                    self.fail(name,'retired_service_import')
            if isinstance(node,ast.Assign):
                names=[t.id.upper() for t in node.targets if isinstance(t,ast.Name)]
                if isinstance(node.value,ast.Constant) and node.value.value==8765 and any(n in {'PORT','HTTP_PORT','SERVICE_PORT','LISTEN_PORT'} for n in names):
                    self.fail(name,'retired_port_configuration')
                if isinstance(node.value,ast.Constant) and isinstance(node.value.value,str) and any(n.endswith(('_B64','_BASE64')) and any(k in n for k in ('BUNDLE','RESOURCE','ARCHIVE','WHEEL','PACKAGE')) for n in names):
                    self.decode_payload(node.value.value,name,depth,required=True)
            if isinstance(node,ast.Call):
                func=node.func.attr if isinstance(node.func,ast.Attribute) else node.func.id if isinstance(node.func,ast.Name) else ''
                if func=='add_parser' and node.args and isinstance(node.args[0],ast.Constant) and node.args[0].value=='serve':
                    self.fail(name,'retired_serve_cli')
                if any(k.arg=='port' and isinstance(k.value,ast.Constant) and k.value.value==8765 for k in node.keywords):
                    self.fail(name,'retired_port_binding')
                if func in {'bind','listen','serve','run','start_server','create_server'} and any(isinstance(v,ast.Constant) and v.value==8765 for a in node.args for v in ast.walk(a)):
                    self.fail(name,'retired_port_binding')
                if func=='add_argument' and any(isinstance(a,ast.Constant) and a.value=='--port' for a in node.args) and any(k.arg=='default' and isinstance(k.value,ast.Constant) and k.value.value==8765 for k in node.keywords):
                    self.fail(name,'retired_port_binding')
                if func in {'run','Popen','call','check_call','check_output','system','exec','eval'}:
                    constants=[n.value for a in node.args for n in ast.walk(a) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
                    if any('ai4orgchem_data_processing.deployment.control' in s or 'ai4orgchem_data_processing.localweb' in s for s in constants):
                        self.fail(name,'retired_launcher_command')
                    if func=='exec' and node.args and isinstance(node.args[0],ast.Constant) and isinstance(node.args[0].value,str):
                        if depth>=MAX_DEPTH:self.fail(name,'payload_depth_limit')
                        else:self.python(name+'!exec',node.args[0].value,depth+1)
            if isinstance(node,ast.Constant) and isinstance(node.value,str) and len(node.value)>32 and node.value.startswith(('UEsDB','H4sI')):
                self.decode_payload(node.value,name,depth)
    def json_payloads(self, obj, name, depth):
        if depth>64:self.fail(name,'json_depth_limit');return
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in {'application/zip','application/octet-stream'} and isinstance(v,str):self.decode_payload(v,name,depth,required=True)
                elif k=='application/zip' and isinstance(v,list):self.decode_payload(''.join(v),name,depth,required=True)
                elif isinstance(v,(dict,list)):self.json_payloads(v,name,depth+1)
        elif isinstance(obj,list):
            for v in obj:
                if isinstance(v,(dict,list)):self.json_payloads(v,name,depth+1)
    def inspect(self, name, data, depth=0):
        self.files+=1;self.path(name,nested=depth>0)
        self.total+=len(data)
        if depth>MAX_DEPTH or len(data)>MAX_FILE or self.total>MAX_TOTAL:
            self.fail(name,'inspection_budget_exceeded');return
        if data.startswith(b'PK\x03\x04') or name.lower().endswith(('.zip','.whl','.npz')):
            self.archives+=1
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    seen=set()
                    for member in z.infolist():
                        self.members+=1
                        if self.members>MAX_MEMBERS:self.fail(name,'archive_member_limit');break
                        key=member.filename.replace('\\','/').casefold()
                        if key in seen:self.fail(name,'duplicate_archive_member')
                        seen.add(key);label=name+'!'+member.filename
                        self.path(member.filename,nested=True)
                        if member.flag_bits&1:self.fail(label,'encrypted_archive');continue
                        if stat.S_ISLNK(member.external_attr>>16):self.fail(label,'archive_link');continue
                        if member.is_dir():continue
                        if member.file_size>MAX_FILE or self.total+member.file_size>MAX_TOTAL:self.fail(label,'inspection_budget_exceeded');continue
                        self.inspect(label,z.read(member),depth+1)
            except (OSError,ValueError,zipfile.BadZipFile,RuntimeError,EOFError):self.fail(name,'unreadable_archive')
            return
        if name.lower().endswith(('.tar','.tar.gz','.tgz','.tar.bz2','.tar.xz')):
            self.archives+=1
            try:
                with tarfile.open(fileobj=io.BytesIO(data),mode='r:*') as t:
                    for member in t:
                        self.members+=1;self.path(member.name,nested=True)
                        if self.members>MAX_MEMBERS:self.fail(name,'archive_member_limit');break
                        if member.issym() or member.islnk():self.fail(name+'!'+member.name,'archive_link');continue
                        if member.isfile():
                            if member.size>MAX_FILE or self.total+member.size>MAX_TOTAL:self.fail(name,'inspection_budget_exceeded');continue
                            self.inspect(name+'!'+member.name,t.extractfile(member).read(),depth+1)
            except (OSError,ValueError,tarfile.TarError,EOFError):self.fail(name,'unreadable_archive')
            return
        suffix=PurePosixPath(name).suffix.lower()
        if suffix not in {'.py','.ipynb','.json','.ps1','.cmd','.bat','.sh','.yml','.yaml','.toml','.md','.txt','.html','.js'}:return
        try:text=data.decode('utf-8-sig')
        except UnicodeError:self.fail(name,'unreadable_text');return
        if self.public and re.search(r'(?:[A-Za-z]:[\\/]+AI4Science|https://colab\.research\.google\.com/drive/)',text,re.I):self.fail(name,'private_machine_or_drive_reference')
        if suffix=='.py':self.python(name,text,depth)
        if suffix in {'.json','.ipynb'}:
            try:obj=json.loads(text)
            except ValueError:self.fail(name,'invalid_json');return
            if suffix=='.ipynb':
                if not isinstance(obj,dict) or not isinstance(obj.get('cells'),list):self.fail(name,'invalid_notebook');return
                for i,c in enumerate(obj['cells']):
                    if c.get('cell_type')=='code':self.python(name+f'!cell-{i}.py',''.join(c.get('source',[])),depth)
            self.json_payloads(obj,name,0)
        if suffix in {'.ps1','.cmd','.bat','.sh','.yml','.yaml'}:
            for line in text.splitlines():
                if line.lstrip().startswith(('#','REM ','rem ')):continue
                if re.search(r'ai4orgchem_data_processing\.(?:deployment\.control|localweb)',line) or re.search(r'(?:--port|-Port)\s+8765\b',line,re.I):self.fail(name,'retired_launcher_command')
        if name.endswith('entry_points.txt') and re.search(r'ai4orgchem_data_processing\.(?:localweb|deployment)',text):self.fail(name,'retired_launcher_command')
    def result(self):
        return {'status':'PASS' if not self.findings else 'BLOCKED','files_inspected':self.files,'archives_inspected':self.archives,
                'embedded_payloads':self.embedded,'findings':self.findings,'scope':'Current bytes only; not a GitHub cache eraser'}

def git(root,args,data=None):
    p=subprocess.run(['git','-C',str(root),*args],capture_output=True,input=data)
    if p.returncode:raise RuntimeError('Git inventory unavailable')
    return p.stdout

def git_snapshot(root, mode, guard):
    args=['ls-files','--stage','-z'] if mode=='staged' else ['ls-tree','-r','-z','HEAD']
    entries=[]
    for row in git(root,args).split(b'\0'):
        if not row:continue
        head,name=row.split(b'\t',1);fields=head.decode().split();name=name.decode()
        if mode=='staged':filemode,oid,stage=fields
        else:filemode,kind,oid=fields;stage='0'
        if stage!='0':guard.fail(name,'unmerged_index');continue
        if filemode=='120000':guard.fail(name,'git_symlink');continue
        entries.append((name,oid))
    oids=list(dict.fromkeys(oid for _,oid in entries));request=('\n'.join(oids)+'\n').encode()
    sizes={}
    for line in git(root,['cat-file','--batch-check=%(objectname) %(objecttype) %(objectsize)'],request).decode().splitlines():
        oid,kind,size=line.split();sizes[oid]=int(size)
        if kind!='blob':raise RuntimeError('Unexpected Git object')
    accepted=[];total=0
    for oid in oids:
        if sizes[oid]>MAX_FILE or total+sizes[oid]>MAX_TOTAL:guard.fail('<git-object>','git_inventory_budget_exceeded');continue
        accepted.append(oid);total+=sizes[oid]
    if not accepted:return {}
    data=git(root,['cat-file','--batch'],('\n'.join(accepted)+'\n').encode());pos=0;contents={}
    for oid in accepted:
        end=data.index(b'\n',pos);header=data[pos:end].decode().split();size=int(header[2]);pos=end+1
        if header[0]!=oid or header[1]!='blob':raise RuntimeError('Unexpected Git batch order')
        contents[oid]=data[pos:pos+size];pos+=size+1
    return {name:contents[oid] for name,oid in entries if oid in contents}

def candidates(root):
    # Explicit current source roots plus any existing tracked file. Historical
    # output directories are not blindly walked; forced tracked additions count.
    found={}
    for base,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=[n for n in dirs if n not in EXCLUDED and not n.startswith('.venv') and not (Path(base)/n).is_symlink()]
        for n in names:
            p=Path(base)/n
            if p.is_symlink():continue
            found[p.relative_to(root).as_posix()]=p
    if (root/'.git').exists():
        for name in git(root,['ls-files','-z']).decode().split('\0'):
            p=root/name
            if name and p.is_file() and not p.is_symlink():found[name]=p
    return found

def check_entry(root, guard, lookup=None):
    def read(name):return lookup[name] if lookup is not None else (root/name).read_bytes()
    try:
        entry=json.loads(read('PLATFORM_ENTRY.json'))
        if entry.get('canonical_url')!=CANONICAL or entry.get('entry_file')!='START_HERE_zh-CN.md' or entry.get('legacy_web_enabled') is not False:
            guard.fail('PLATFORM_ENTRY.json','entry_policy_mismatch')
        for name in ['README.md','START_HERE_zh-CN.md']:
            if CANONICAL not in read(name).decode('utf-8'):guard.fail(name,'canonical_entry_missing')
        text=read('START_HERE_zh-CN.md').decode('utf-8')
        if re.search(r'http://(?:127\.0\.0\.1|localhost):\d+',text):guard.fail('START_HERE_zh-CN.md','local_web_entry')
    except (OSError,KeyError,ValueError,UnicodeError):guard.fail('PLATFORM_ENTRY.json','entry_files_missing_or_invalid')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=Path.cwd())
    p.add_argument('--scope',choices=['source','staged','commit','release','delivery','artifact'],default='source')
    p.add_argument('--artifact',type=Path);p.add_argument('--report',type=Path);p.add_argument('--skip-entry',action='store_true')
    a=p.parse_args(argv);root=a.root.resolve();g=Guard(public=a.scope=='release')
    try:
        if a.scope in {'staged','commit'}:
            lookup=git_snapshot(root,a.scope,g)
            for n,b in lookup.items():g.inspect(n,b)
            if not a.skip_entry:check_entry(root,g,lookup)
        elif a.scope=='artifact':
            if a.artifact is None:p.error('--artifact required')
            file=a.artifact.resolve()
            if not file.is_file() or file.stat().st_size>MAX_FILE:g.fail(file.name,'artifact_missing_or_too_large')
            else:g.inspect(file.name,file.read_bytes())
        else:
            paths=candidates(root) if a.scope=='source' else {x.relative_to(root).as_posix():x for x in root.rglob('*') if x.is_file() and '.git' not in x.relative_to(root).parts}
            for n,file in sorted(paths.items()):
                if file.stat().st_size>MAX_FILE:g.fail(n,'file_too_large');continue
                if a.scope=='release' and (n.split('/')[0] in EXCLUDED or n.startswith(('src/','local-config/'))):g.fail(n,'not_publication_material')
                if file.is_symlink():g.fail(n,'publication_symlink');continue
                g.inspect(n,file.read_bytes())
            if not a.skip_entry and a.scope!='delivery':check_entry(root,g)
    except (OSError,RuntimeError,ValueError,RecursionError,MemoryError):g.fail('<inventory>','inspection_failed_closed')
    result=g.result();result['mode']=a.scope
    if a.report:
        a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False));return 0 if result['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
