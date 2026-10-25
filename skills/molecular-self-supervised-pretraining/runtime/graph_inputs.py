"""RDKit input admission for the four-feature educational MPNN; no tensor/model calls."""
from rdkit import Chem, rdBase


def parse_molecule(raw):
    if not isinstance(raw,str) or not 1<=len(raw)<=256:
        raise ValueError('SMILES must be 1–256 characters.')
    options = Chem.SmilesParserParams()
    options.parseName = False
    options.allowCXSMILES = False
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(raw,options)
    if (mol is None or mol.GetNumAtoms()>64 or len(Chem.GetMolFrags(mol))!=1
            or any(a.GetAtomicNum() not in {5,6,7,8,9,14,15,16,17,35,53} for a in mol.GetAtoms())):
        raise ValueError('Only parsed single-component small organic graphs <=64 atoms are supported.')
    if any(atom.GetNumRadicalElectrons()!=0 for atom in mol.GetAtoms()):
        raise ValueError('Radical electrons are unsupported by this educational graph representation; reject this input.')
    return mol
