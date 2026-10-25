"""Build an explicit bounded CSV request; retain preflight failures without model calls."""
from pathlib import Path
import argparse
import csv
import importlib.util
import io
import json
import math
import sys
import tempfile

PAGE = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--template',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--id-column',default='id')
    parser.add_argument('--features',nargs='+',required=True)
    parser.add_argument('--feature-units',nargs='+',required=True)
    parser.add_argument('--target')
    parser.add_argument('--target-unit')
    parser.add_argument('--groups')
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('csv_skill_entry',PAGE/'runtime/run_skill.py')
    api=importlib.util.module_from_spec(spec);spec.loader.exec_module(api)
    api.verify_resources()
    evidence=api.evidence_api()
    output=evidence.checked_output(PAGE,args.output)
    snapshots={}
    try:
        snapshots['input.csv']=evidence.read_bounded(args.input,128000)
        snapshots['template.json']=evidence.read_bounded(args.template,128000)
        settings={k:v for k,v in vars(args).items() if k not in {'template','input','output'}}
        snapshots['conversion.json']=json.dumps(settings,ensure_ascii=False,allow_nan=False).encode('utf-8')
        if len(args.features)!=len(args.feature_units) or len(set(args.features))!=len(args.features):
            raise ValueError('Declare one unit per unique feature column.')
        if any(not unit.strip() for unit in args.feature_units):
            raise ValueError('Feature units must not be empty or whitespace; declare dimensionless explicitly.')
        if bool(args.target)!=bool(args.target_unit) or (args.target_unit is not None and not args.target_unit.strip()):
            raise ValueError('Provide target and explicit nonblank target unit together.')
        if any(name in args.features for name in [args.id_column,args.target,args.groups] if name is not None):
            raise ValueError('ID, target and group columns cannot also be feature columns.')
        template=api.strict_json(snapshots['template.json'])
        text=snapshots['input.csv'].decode('utf-8-sig')
        reader=csv.DictReader(io.StringIO(text));rows=list(reader)
        required={args.id_column,*args.features}|({args.target} if args.target else set())|({args.groups} if args.groups else set())
        if (not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames))
                or not required.issubset(reader.fieldnames) or not 5<=len(rows)<=200
                or any(None in row or None in row.values() for row in rows)):
            raise ValueError('Declare unique existing headers and 5–200 complete rows.')
        ids=[row[args.id_column] for row in rows]
        if len(set(ids))!=len(ids) or any(not value for value in ids):
            raise ValueError('IDs must be unique and nonempty.')
        def number(value):
            value=float(value)
            if not math.isfinite(value):
                raise ValueError('CSV numeric values must be finite; no row deletion or imputation.')
            return value
        data={'ids':ids,'features':[[number(row[name]) for name in args.features] for row in rows],
              'feature_names':args.features,'feature_units':args.feature_units,'source_csv_text':text}
        if args.target:
            data.update(target=[number(row[args.target]) for row in rows],target_unit=args.target_unit)
        if args.groups:
            data['groups']=[row[args.groups] for row in rows]
            if any(not value for value in data['groups']):raise ValueError('Groups must be nonempty.')
        request={'parameters':template['parameters'],'data':data,
                 'provenance':{'kind':'USER_PROVIDED_CSV','description':'Explicit columns and units; original CSV retained, not authenticated experimental data.'}}
        output.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='skill-csv-',dir=output.parent) as work:
            path=Path(work)/'request.json'
            path.write_text(json.dumps(request,ensure_ascii=False,allow_nan=False),encoding='utf-8')
            result=api.run_skill(request_file=path,output_dir=output,snapshots=snapshots)
        print(result['status'],result['scope'])
        return int(result['status']!='COMPLETE_DEFINED_SCOPE')
    except (ValueError,OSError,RuntimeError,ArithmeticError,ImportError,KeyError,TypeError) as error:
        if not output.exists():
            owned=evidence.begin_output(PAGE,output,snapshots)
            evidence.record_failure(owned,error,stage='CSV_PREPROCESSING')
        print(str(error),file=sys.stderr)
        return 2


if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,RuntimeError,ImportError) as error:
        print(str(error),file=sys.stderr);raise SystemExit(2)
