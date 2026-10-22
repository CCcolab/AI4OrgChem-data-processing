"""Read and verify the same companion package carried by the notebook."""
import base64,hashlib,io,json,zipfile
from pathlib import Path
PAGE=Path(__file__).resolve().parents[2]/'skills/organic-smiles-rdkit'
def resource_bytes():
    n=json.loads((PAGE/'organic-smiles-rdkit.ipynb').read_text('utf-8'))
    a=n['metadata']['adp_runtime_bundle'];raw=base64.b64decode(a['zip_base64'],validate=True)
    if hashlib.sha256(raw).hexdigest()!=a['sha256']:raise ValueError('Runtime bundle mismatch')
    if raw!=(PAGE/'runtime/rdkit-runtime.zip').read_bytes():raise ValueError('Companion differs from attachment')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:resources={p:z.read(p) for p in z.namelist()}
    for p,b in resources.items():
        if Path(p).name!=p or (PAGE/'runtime'/p).read_bytes()!=b:raise ValueError('Companion source mismatch')
    for row in json.loads(resources['resource-manifest.json']):
        if hashlib.sha256(resources[row['file']]).hexdigest()!=row['sha256']:raise ValueError('Resource mismatch')
    return resources
