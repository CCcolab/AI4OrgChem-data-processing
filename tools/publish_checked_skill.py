"""Only push a clean, tested, private Skill publication checkout; never force."""
from pathlib import Path
import argparse,json,subprocess,sys

REPO='CCcolab/AI4OrgChem-data-processing'
URL='https://github.com/'+REPO+'.git'
def run(args,root,**kw):return subprocess.run(args,cwd=root,check=True,**kw)
def main():
    p=argparse.ArgumentParser();p.add_argument('--repo-root',type=Path,required=True);p.add_argument('--push',action='store_true');p.add_argument('--expected-remote',required=True);a=p.parse_args()
    root=a.repo_root.resolve();script=root/'tools/check_platform_boundary.py'
    run([sys.executable,'-B',str(script),'--root',str(root),'--scope','release'],root)
    run([sys.executable,'-B',str(script),'--root',str(root),'--scope','commit'],root)
    run([sys.executable,'-B','-m','unittest','discover','-s','tests/guard','-p','test_*.py'],root)
    dirty=run(['git','status','--porcelain'],root,capture_output=True,text=True).stdout
    if dirty:raise RuntimeError('Publication checkout has uncommitted or untracked files')
    remote=run(['git','remote','get-url','origin'],root,capture_output=True,text=True).stdout.strip()
    if remote!=URL:raise RuntimeError('Wrong publication remote')
    repo=json.loads(run(['gh','repo','view',REPO,'--json','nameWithOwner,visibility'],root,capture_output=True,text=True).stdout)
    if repo['visibility']!='PRIVATE' or repo['nameWithOwner']!=REPO:raise RuntimeError('Publication requires the intended PRIVATE repository')
    actual=run(['gh','api','repos/'+REPO+'/git/ref/heads/main','--jq','.object.sha'],root,capture_output=True,text=True).stdout.strip()
    if actual!=a.expected_remote:raise RuntimeError('Remote changed; review before publishing')
    if a.push:run(['git','-c','credential.helper=','-c','credential.helper=!gh auth git-credential','-c','http.version=HTTP/1.1','push','origin','HEAD:main'],root)
    print(json.dumps({'status':'PASS_CHECKED_PUBLICATION','private':True,'pushed':a.push,'force':False}))

if __name__=='__main__':main()
