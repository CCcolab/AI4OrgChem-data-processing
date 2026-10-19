"""Generate links locally after the GitHub target and rights are approved; no network/Git writes."""
from pathlib import Path
import argparse,json,re
from urllib.parse import quote
r=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--owner',required=True);p.add_argument('--repo',required=True);p.add_argument('--ref',required=True);a=p.parse_args()
assert re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}',a.owner)
assert re.fullmatch(r'[A-Za-z0-9_.-]+',a.repo) and a.repo not in ['.','..']
assert re.fullmatch(r'[A-Za-z0-9_./-]+',a.ref) and '..' not in a.ref and not a.ref.startswith('/')
rows=[]
for id_ in ['A01','A02','B03','F01','F02']:
 path='colab/'+id_+'-colab.ipynb';assert (r/path).is_file()
 rows.append({'lesson':id_,'path':path,'github_read':'https://github.com/'+a.owner+'/'+a.repo+'/blob/'+quote(a.ref,safe='')+'/lessons/'+id_+'.ipynb','colab':'https://colab.research.google.com/github/'+a.owner+'/'+a.repo+'/blob/'+quote(a.ref,safe='')+'/'+path,'remote_validation':'NOT_EXECUTED'})
(r/'publication-target.json').write_text(json.dumps({'owner':a.owner,'repo':a.repo,'ref':a.ref,'remote_validation':'NOT_EXECUTED'},indent=2)+'\n',encoding='utf-8')
(r/'github-entrypoints.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
(r/'COLAB_LINKS.md').write_text('# Colab入口（尚待真实远程验收）\n\n'+''.join('- ['+x['lesson']+']('+x['colab']+')\n' for x in rows),encoding='utf-8')
print('Generated local links only. No repository created, no push, no remote PASS.')
