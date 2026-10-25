"""Small CPU molecular graph inputs and a real trainable reference MPNN."""
import numpy as np
import torch
from torch import nn
from rdkit import Chem, rdBase


def keys(value, required, optional=()):
    if not isinstance(value, dict) or not set(required).issubset(value) or set(value) - set(required) - set(optional):
        raise ValueError('Required fields: ' + ','.join(required))


def integer(value, low, high, name):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(name + ' is outside its integer budget.')
    return value


def real(value, low, high, name):
    if type(value) not in {int, float} or not np.isfinite(value) or not low <= value <= high:
        raise ValueError(name + ' is outside its finite declared budget.')
    return float(value)


def graph(raw):
    if not isinstance(raw, str) or not 1 <= len(raw) <= 256:
        raise ValueError('SMILES must be 1–256 characters.')
    options = Chem.SmilesParserParams()
    options.parseName = False
    options.allowCXSMILES = False
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(raw, options)
    if mol is None or mol.GetNumAtoms() > 64 or len(Chem.GetMolFrags(mol)) != 1 or any(a.GetAtomicNum() not in {5,6,7,8,9,14,15,16,17,35,53} for a in mol.GetAtoms()):
        raise ValueError('Only parsed single-component small organic graphs <=64 atoms are supported.')
    x = torch.tensor([[a.GetAtomicNum()/100, a.GetDegree()/4, a.GetFormalCharge()/2, float(a.GetIsAromatic())]
                      for a in mol.GetAtoms()], dtype=torch.float32)
    edges, bonds = [], []
    for bond in mol.GetBonds():
        i, j = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
        edges.extend([(i,j),(j,i)])
        bonds.extend([[bond.GetBondTypeAsDouble()/3], [bond.GetBondTypeAsDouble()/3]])
    edge_index = torch.tensor(edges, dtype=torch.long).reshape(-1,2).T
    edge_features = torch.tensor(bonds, dtype=torch.float32).reshape(-1,1)
    comparison = Chem.Mol(mol)
    for atom in comparison.GetAtoms():
        atom.SetAtomMapNum(0)
    feature_key = Chem.MolToSmiles(comparison, isomericSmiles=False)
    return {'x': x, 'edges': edge_index, 'bonds': edge_features, 'feature_key': feature_key,
            'raw_smiles': raw, 'parsed_isomeric_smiles': Chem.MolToSmiles(mol, isomericSmiles=True),
            'unencoded_stereo_or_isotope': any(a.GetIsotope() or a.GetChiralTag() != Chem.ChiralType.CHI_UNSPECIFIED for a in mol.GetAtoms())
                or any(b.GetStereo() != Chem.BondStereo.STEREONONE for b in mol.GetBonds())}


def require_real_leaves(value):
    """Validate raw numeric leaves before NumPy can promote mixed Booleans."""
    pending = [value]
    visited = 0
    while pending:
        item = pending.pop()
        visited += 1
        if visited > 100000:
            raise ValueError('Numeric input exceeds the bounded traversal budget.')
        if isinstance(item, (list, tuple)):
            pending.extend(item)
        elif isinstance(item, np.ndarray):
            if item.dtype.kind not in 'if':
                raise ValueError('Require real numeric leaves; Boolean/string/null/complex input is not admitted.')
        elif isinstance(item, (bool, np.bool_)) or not isinstance(item, (int, float, np.integer, np.floating)):
            raise ValueError('Require real numeric leaves; Boolean/string/null/complex input is not admitted.')


def dataset(data, supervised=True):
    required = ['ids','smiles'] + (['target','target_unit'] if supervised else [])
    optional = ['groups','source_csv_text'] + ([] if supervised else ['target','target_unit'])
    keys(data, required, optional)
    ids, strings = data['ids'], data['smiles']
    if (not isinstance(strings,list) or not 5 <= len(strings) <= 64 or not isinstance(ids,list)
            or len(ids) != len(strings) or len(set(ids)) != len(ids) or any(not isinstance(id_,str) or not id_ for id_ in ids)):
        raise ValueError('Require 5–64 aligned unique nonempty IDs and SMILES.')
    graphs = [graph(raw) for raw in strings]
    y = None
    if supervised or 'target' in data:
        require_real_leaves(data['target'])
        y = np.asarray(data['target'])
        if y.dtype.kind not in 'if' or y.shape != (len(graphs),) or not np.isfinite(y).all() or not isinstance(data.get('target_unit'),str) or not data['target_unit'].strip():
            raise ValueError('Explicit finite aligned target and units are required.')
        y = y.astype(float)
    if 'groups' in data and (not isinstance(data['groups'],list) or len(data['groups']) != len(graphs)
                            or any(not isinstance(g,str) or not g for g in data['groups'])):
        raise ValueError('Groups must be explicit aligned nonempty strings.')
    return graphs, y


def split(parameters, data, graphs):
    integer(parameters['seed'],0,2**31-1,'seed')
    test = parameters['test_indices']
    if not isinstance(test,list) or not 1 <= len(test) <= len(graphs)-3 or len(set(test)) != len(test) or any(type(i) is not int or not 0 <= i < len(graphs) for i in test):
        raise ValueError('Declare disjoint zero-based test indices leaving at least three training molecules.')
    train = [i for i in range(len(graphs)) if i not in set(test)]
    if {graphs[i]['feature_key'] for i in train}.intersection(graphs[i]['feature_key'] for i in test):
        raise ValueError('Same graph under the reference feature policy crosses train/test; refuse leakage.')
    if 'groups' in data and {data['groups'][i] for i in train}.intersection(data['groups'][i] for i in test):
        raise ValueError('Declared groups cross train/test.')
    return train, test


class Encoder(nn.Module):
    def __init__(self, hidden, depth):
        super().__init__()
        self.input = nn.Linear(4,hidden)
        self.layers = nn.ModuleList(nn.Linear(hidden,hidden) for _ in range(depth))

    def nodes(self, graph):
        h = torch.relu(self.input(graph['x']))
        for layer in self.layers:
            messages = torch.zeros_like(h)
            if graph['edges'].shape[1]:
                src,dst = graph['edges']
                messages.index_add_(0,dst,layer(h[src])*graph['bonds'])
            h = torch.relu(h+messages)
        return h

    def forward(self, graph):
        return self.nodes(graph).sum(dim=0)


class Predictor(nn.Module):
    def __init__(self, hidden, depth):
        super().__init__()
        self.encoder=Encoder(hidden,depth)
        self.head=nn.Linear(hidden,1)

    def forward(self, graphs):
        return self.head(torch.stack([self.encoder(graph) for graph in graphs])).squeeze(-1)


def check(name, condition):
    return {'name':name,'passed':bool(condition),'actual':bool(condition),'threshold':True}


def gradient_finite(model):
    gradients=[p.grad for p in model.parameters() if p.requires_grad and p.grad is not None]
    return bool(gradients) and all(torch.isfinite(g).all().item() for g in gradients)


def permutation(graph):
    order=torch.arange(len(graph['x'])-1,-1,-1)
    inverse=torch.argsort(order)
    return {**graph,'x':graph['x'][order],'edges':inverse[graph['edges']]}


def environment():
    return {'numpy':np.__version__,'torch':torch.__version__,'rdkit':rdBase.rdkitVersion,'device':'CPU','threads':torch.get_num_threads()}
