"""Convert explicitly named CSV columns to a graph-training request; no inferred labels."""
from pathlib import Path
import argparse
import csv
import io
import json
import importlib.util
import sys
import tempfile

PAGE = Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--id-column',default='id')
    parser.add_argument('--smiles-column',default='smiles')
    parser.add_argument('--target')
    parser.add_argument('--target-unit')
    parser.add_argument('--groups')
    args=parser.parse_args()
    if args.input.stat().st_size>128000:raise ValueError('CSV limit128KB.')
    raw=args.input.read_text('utf-8-sig'); reader=csv.DictReader(io.StringIO(raw))
    headers=reader.fieldnames
    if not headers or len(headers)!=len(set(headers)):raise ValueError('Unique CSV headers required.')
    columns=[args.id_column,args.smiles_column]+[v for v in [args.target,args.groups] if v]
    if len(columns)!=len(set(columns)) or not set(columns)<=set(headers):raise ValueError('Select distinct existing columns.')
    rows=list(reader)
    if not 5<=len(rows)<=64 or any(None in row or any(v is None for v in row.values()) for row in rows):raise ValueError('5–64 regular rows required.')
    spec=importlib.util.spec_from_file_location('entry',PAGE/'runtime/run_skill.py')
    entry=importlib.util.module_from_spec(spec);spec.loader.exec_module(entry)
    req=entry.strict_json(args.template.read_bytes())
    data={'ids':[row[args.id_column] for row in rows], 'smiles':[row[args.smiles_column] for row in rows]}
    if args.target:
        if not args.target_unit:raise ValueError('Explicit target unit required.')
        data.update(target=[float(row[args.target]) for row in rows],target_unit=args.target_unit)
    elif args.target_unit:raise ValueError('Target unit without target.')
    if args.groups:data['groups']=[row[args.groups] for row in rows]
    req['data']=data
    req['provenance']={'kind':'USER_CSV_DECLARED_NOT_AUTHENTICATED','description':'Columns selected explicitly; original CSV copied beside request. No example labels retained.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',suffix='.json',dir=args.output.parent,encoding='utf-8',delete=False) as stream:
        json.dump(req,stream,ensure_ascii=False,allow_nan=False);temporary=Path(stream.name)
    try:
        result=entry.run_skill(request_file=temporary,output_dir=args.output)
        # Add original CSV and refresh evidence; do not leave it outside the result ZIP.
        (args.output/'original-input.csv').write_bytes(args.input.read_bytes())
        import hashlib,zipfile
        files=sorted(p for p in args.output.rglob('*') if p.is_file() and p.name not in {'SHA256SUMS.txt','results.zip'})
        (args.output/'SHA256SUMS.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(args.output).as_posix()+'\n' for p in files),encoding='utf-8')
        with zipfile.ZipFile(args.output/'results.zip','w',zipfile.ZIP_DEFLATED) as z:
            for p in files+[args.output/'SHA256SUMS.txt']:z.write(p,p.relative_to(args.output).as_posix())
        return int(result['status']!='COMPLETE_DEFINED_SCOPE')
    finally:temporary.unlink(missing_ok=True)

if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,RuntimeError,ImportError) as error:
        print(error,file=sys.stderr);raise SystemExit(2)
