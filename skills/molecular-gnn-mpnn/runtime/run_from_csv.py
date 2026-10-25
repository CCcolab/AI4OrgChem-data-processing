"""Convert declared molecular CSV columns; preserve bounded preprocessing failures."""
from pathlib import Path
import argparse
import csv
import importlib.util
import io
import json
import math
import sys
import tempfile

PAGE=Path(__file__).resolve().parents[1]


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
    spec=importlib.util.spec_from_file_location('csv_graph_entry',PAGE/'runtime/run_skill.py')
    api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
    api.verify_resources()
    evidence=api.evidence_api();output=evidence.checked_output(PAGE,args.output)
    snapshots={}
    try:
        snapshots['original-input.csv']=evidence.read_bounded(args.input,128000)
        snapshots['template.json']=evidence.read_bounded(args.template,128000)
        snapshots['conversion.json']=json.dumps({k:v for k,v in vars(args).items() if k not in {'input','output','template'}},
                                                  ensure_ascii=False,allow_nan=False).encode('utf-8')
        if bool(args.target)!=bool(args.target_unit) or (args.target_unit is not None and not args.target_unit.strip()):
            raise ValueError('Provide target and explicit nonblank target unit together.')
        text=snapshots['original-input.csv'].decode('utf-8-sig')
        reader=csv.DictReader(io.StringIO(text));headers=reader.fieldnames;rows=list(reader)
        columns=[args.id_column,args.smiles_column]+[v for v in [args.target,args.groups] if v]
        if (not headers or len(headers)!=len(set(headers)) or len(columns)!=len(set(columns))
                or not set(columns)<=set(headers) or not 5<=len(rows)<=64
                or any(None in row or None in row.values() for row in rows)):
            raise ValueError('Require distinct existing columns and 5–64 complete CSV rows.')
        ids=[row[args.id_column] for row in rows]
        if len(set(ids))!=len(ids) or any(not value for value in ids):
            raise ValueError('IDs must be unique and nonempty.')
        request=api.strict_json(snapshots['template.json'])
        data={'ids':ids,'smiles':[row[args.smiles_column] for row in rows],'source_csv_text':text}
        if args.target:
            target=[float(row[args.target]) for row in rows]
            if not all(math.isfinite(v) for v in target):raise ValueError('CSV target values must be finite.')
            data.update(target=target,target_unit=args.target_unit)
        if args.groups:
            data['groups']=[row[args.groups] for row in rows]
            if any(not value for value in data['groups']):raise ValueError('Groups must be nonempty.')
        request['data']=data
        request['provenance']={'kind':'USER_CSV_DECLARED_NOT_AUTHENTICATED',
                               'description':'Explicit columns; original CSV retained. No example labels retained.'}
        output.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='graph-csv-',dir=output.parent) as work:
            path=Path(work)/'request.json';path.write_text(json.dumps(request,ensure_ascii=False,allow_nan=False),encoding='utf-8')
            result=api.run_skill(request_file=path,output_dir=output,snapshots=snapshots)
        return int(result['status']!='COMPLETE_DEFINED_SCOPE')
    except (ValueError,OSError,RuntimeError,ArithmeticError,ImportError,KeyError,TypeError) as error:
        if not output.exists():
            owned=evidence.begin_output(PAGE,output,snapshots)
            evidence.record_failure(owned,error,stage='CSV_PREPROCESSING')
        print(str(error),file=sys.stderr);return 2


if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,RuntimeError,ImportError) as error:
        print(str(error),file=sys.stderr);raise SystemExit(2)
