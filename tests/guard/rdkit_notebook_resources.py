"""Read the exact runtime sources shipped inside the standalone Notebook."""
import ast,json,hashlib
from pathlib import Path
PAGE=Path(__file__).resolve().parents[2]/'skills/organic-smiles-rdkit'
def resource_bytes():
    notebook=json.loads((PAGE/'organic-smiles-rdkit.ipynb').read_text('utf-8'))
    values={}
    for node in ast.parse(''.join(notebook['cells'][1]['source'])).body:
        if isinstance(node,ast.Assign):
            for target in node.targets:
                if isinstance(target,ast.Name) and target.id in {'RESOURCE_TEXT','RESOURCE_CRLF'}:
                    values[target.id]=ast.literal_eval(node.value)
    resources={name:(text.replace('\n','\r\n') if name in values['RESOURCE_CRLF'] else text).encode('utf-8') for name,text in values['RESOURCE_TEXT'].items()}
    for name in resources:
        if Path(name).name!=name:raise ValueError('Unsafe embedded resource name')
    for item in json.loads(resources['resource-manifest.json']):
        if hashlib.sha256(resources[item['file']]).hexdigest()!=item['sha256']:raise ValueError('Embedded resource hash mismatch')
    return resources
