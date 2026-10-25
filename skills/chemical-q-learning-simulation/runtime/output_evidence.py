"""Local bounded snapshots and result sealing; no external service or environment capture."""
from pathlib import Path
import hashlib
import json
import zipfile


def checked_output(page, output_dir):
    original = Path(output_dir)
    output = original.resolve()
    if original.is_symlink() or output.exists() or output.is_relative_to(Path(page).resolve()):
        raise ValueError('Use a NEW output directory outside the Skill source; never overwrite results.')
    return output


def read_bounded(path, limit):
    source = Path(path)
    if source.is_symlink() or not source.is_file() or source.stat().st_size > limit:
        raise ValueError('Provide a regular bounded input file <= '+str(limit)+' bytes.')
    with source.open('rb') as stream:
        raw = stream.read(limit+1)
    if len(raw) > limit:
        raise ValueError('Input grew beyond its declared byte limit.')
    return raw


def begin_output(page, output_dir, snapshots):
    output = checked_output(page,output_dir)
    allowed = {'request.json','input.csv','original-input.csv','template.json','conversion.json'}
    if not isinstance(snapshots,dict) or set(snapshots)-allowed:
        raise ValueError('Unexpected input snapshot name.')
    for name, raw in snapshots.items():
        limit = 2_000_000 if name=='request.json' else 128000
        if not isinstance(raw,bytes) or len(raw)>limit:
            raise ValueError('Only safely read, bounded byte snapshots may be retained.')
    skill = (Path(page)/'SKILL.md').read_bytes()
    output.mkdir(parents=True,exist_ok=False)
    (output/'SKILL.used.md').write_bytes(skill)
    for name, raw in snapshots.items():
        (output/name).write_bytes(raw)
    return output


def seal_output(output):
    output = Path(output)
    items = list(output.rglob('*'))
    if any(p.is_symlink() or not p.resolve().is_relative_to(output.resolve()) for p in items):
        raise ValueError('Result artifacts must remain regular files inside the owned output.')
    reserved = {output/'SHA256SUMS.txt',output/'results.zip'}
    files = sorted(p for p in items if p.is_file() and p not in reserved)
    sums = output/'SHA256SUMS.txt'
    sums.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(output).as_posix()+'\n'
                            for p in files),encoding='utf-8')
    with zipfile.ZipFile(output/'results.zip','w',zipfile.ZIP_DEFLATED) as archive:
        for path in files+[sums]:
            archive.write(path,path.relative_to(output).as_posix())


def record_failure(output, error, stage='VALIDATION_OR_ANALYSIS'):
    # Call only for an output directory just created by this invocation.
    record = {'status':'FAILED_INPUT_RETAINED','stage':stage,'type':type(error).__name__,
              'message':str(error),'model_service_calls':0,'network_calls':0}
    (Path(output)/'failure.json').write_text(json.dumps(record,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    seal_output(output)
