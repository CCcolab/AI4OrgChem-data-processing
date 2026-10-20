"""The supported checked packager for a curated publication or internal delivery."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,zipfile

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--internal',action='store_true');a=p.parse_args()
    project=Path(__file__).resolve().parents[1];source=a.input.resolve();out=a.output.resolve()
    if not source.is_relative_to(project) or not out.is_relative_to(project) or out.is_relative_to(source):p.error('Input/output must stay in project; output must be outside input')
    if out.exists():p.error('Never overwrite an existing delivery')
    guard=project/'tools/check_platform_boundary.py'
    command=[sys.executable,'-B',str(guard),'--root',str(source),'--scope','delivery' if a.internal else 'release']
    subprocess.run(command,check=True)
    paths=[x for x in source.rglob('*') if x.is_file() and '.git' not in x.relative_to(source).parts]
    if any(x.is_symlink() for x in paths):p.error('Symlinks are not deliverable')
    out.parent.mkdir(parents=True,exist_ok=True)
    pending=Path(str(out)+'.pending')
    if pending.exists():p.error('Pending artifact already exists; inspect it first')
    with zipfile.ZipFile(pending,'x',zipfile.ZIP_DEFLATED) as z:
        for file in sorted(paths):z.write(file,file.relative_to(source).as_posix())
    checked=subprocess.run([sys.executable,'-B',str(guard),'--scope','artifact','--artifact',str(pending)])
    if checked.returncode:
        pending.unlink();raise SystemExit(checked.returncode)
    pending.rename(out)
    digest=hashlib.sha256(out.read_bytes()).hexdigest();Path(str(out)+'.sha256').write_text(digest+'  '+out.name+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS_CHECKED_PACKAGE','sha256':digest,'files':len(paths)}))

if __name__=='__main__':main()
