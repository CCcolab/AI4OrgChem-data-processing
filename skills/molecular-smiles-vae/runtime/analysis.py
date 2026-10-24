"""Train a tiny GRU VAE on an explicitly restricted C/N/O chain alphabet."""
from pathlib import Path
import json
import numpy as np
import torch
from torch import nn
import torch.nn.functional as F
from rdkit import Chem,rdBase

VOCAB=['<PAD>','<BOS>','<EOS>','C','N','O']


class VAE(nn.Module):
    def __init__(self,latent):
        super().__init__();self.embedding=nn.Embedding(6,8,padding_idx=0)
        self.encoder=nn.GRU(8,16,batch_first=True);self.mu=nn.Linear(16,latent);self.logvar=nn.Linear(16,latent)
        self.decoder=nn.GRU(8+latent,16,batch_first=True);self.output=nn.Linear(16,6)

    def encode(self,tokens,lengths):
        packed=nn.utils.rnn.pack_padded_sequence(self.embedding(tokens),lengths,batch_first=True,enforce_sorted=False)
        _,hidden=self.encoder(packed)
        return self.mu(hidden[0]),self.logvar(hidden[0]).clamp(-8,8)

    def decode_teacher(self,tokens,z):
        vectors=self.embedding(tokens)
        hidden,_=self.decoder(torch.cat([vectors,z[:,None,:].expand(-1,vectors.shape[1],-1)],dim=2))
        return self.output(hidden)


def analyze(parameters,data,output_dir):
    expected={'seed','epochs','learning_rate','latent_dim','beta','samples','max_length'}
    if set(parameters)!=expected or set(data)!={'ids','smiles'}:
        raise ValueError('Declare the exact bounded VAE parameters and ids/smiles.')
    for field,low,high in [('seed',0,2**31-1),('epochs',1,100),('latent_dim',2,8),('samples',1,16),('max_length',1,12)]:
        if type(parameters[field]) is not int or not low<=parameters[field]<=high:raise ValueError(field+' outside integer budget.')
    for field,low,high in [('learning_rate',1e-5,.02),('beta',0,2)]:
        if type(parameters[field]) not in {int,float} or not np.isfinite(parameters[field]) or not low<=parameters[field]<=high:raise ValueError(field+' outside finite budget.')
    strings,ids=data['smiles'],data['ids']
    if (not isinstance(strings,list) or not 5<=len(strings)<=64 or not isinstance(ids,list) or len(ids)!=len(strings)
            or len(set(ids))!=len(ids) or any(not isinstance(id_,str) or not id_ for id_ in ids)):
        raise ValueError('Require 5–64 unique IDs and aligned training strings.')
    lengths=[];canonical_train=set();encoded=[]
    for s in strings:
        if not isinstance(s,str) or not 1<=len(s)<=parameters['max_length'] or any(c not in 'CNO' for c in s):
            raise ValueError('This teaching model only supports unbranched uppercase C/N/O strings; no rings, stereo, charges or general SMILES.')
        mol=Chem.MolFromSmiles(s)
        if mol is None:raise ValueError('Invalid training SMILES.')
        canonical_train.add(Chem.MolToSmiles(mol,isomericSmiles=True));tokens=[1]+[VOCAB.index(c) for c in s]+[2]
        lengths.append(len(tokens));encoded.append(tokens)
    width=max(lengths);tokens=torch.tensor([row+[0]*(width-len(row)) for row in encoded],dtype=torch.long)
    lengths=torch.tensor(lengths,dtype=torch.long)
    torch.set_num_threads(1);torch.manual_seed(parameters['seed'])
    model=VAE(parameters['latent_dim']);optimizer=torch.optim.Adam(model.parameters(),lr=parameters['learning_rate'])
    losses=[]
    for _ in range(parameters['epochs']):
        optimizer.zero_grad();mu,logvar=model.encode(tokens,lengths)
        z=mu+torch.exp(.5*logvar)*torch.randn_like(mu)
        logits=model.decode_teacher(tokens[:,:-1],z)
        ce=F.cross_entropy(logits.reshape(-1,6),tokens[:,1:].reshape(-1),ignore_index=0)
        kl=-.5*(1+logvar-mu.square()-logvar.exp()).sum(dim=1).mean()
        loss=ce+parameters['beta']*kl
        if not torch.isfinite(loss) or kl< -1e-6:raise ValueError('Nonfinite loss or invalid KL.')
        loss.backward()
        if not all(torch.isfinite(p.grad).all() for p in model.parameters() if p.grad is not None):raise ValueError('Nonfinite gradients.')
        torch.nn.utils.clip_grad_norm_(model.parameters(),10);optimizer.step()
        losses.append({'token_mean_CE':float(ce.detach()),'batch_mean_latent_sum_KL':float(kl.detach()),'objective':float(loss.detach())})
    artifact=Path(output_dir)/'self-produced-vae-weights.pt';torch.save(model.state_dict(),artifact)
    restored=VAE(parameters['latent_dim']);restored.load_state_dict(torch.load(artifact,weights_only=True,map_location='cpu'))
    model.eval();restored.eval()
    with torch.no_grad():
        mu,lv=model.encode(tokens,lengths);mu2,lv2=restored.encode(tokens,lengths)
        replay=torch.allclose(mu,mu2,atol=1e-6,rtol=1e-6) and torch.allclose(lv,lv2,atol=1e-6,rtol=1e-6)
        generated=[]
        for i in range(parameters['samples']):
            z=torch.randn(1,parameters['latent_dim']);token=torch.tensor([[1]]);hidden=None;pieces=[];terminated=False
            for _step in range(parameters['max_length']+1):
                vector=torch.cat([model.embedding(token),z[:,None,:]],dim=2)
                state,hidden=model.decoder(vector,hidden);scores=model.output(state)[0,0];scores[[0,1]]=float('-inf')
                value=int(torch.multinomial(torch.softmax(scores,dim=0),1))
                if value==2:terminated=True;break
                pieces.append(VOCAB[value]);token=torch.tensor([[value]])
            raw=''.join(pieces)
            with rdBase.BlockLogs():mol=Chem.MolFromSmiles(raw) if raw else None
            parsed=mol is not None;valid=terminated and parsed and len(raw)<=parameters['max_length']
            canonical=Chem.MolToSmiles(mol,isomericSmiles=True) if parsed else None
            generated.append({'sample':i,'smiles':raw,'terminated':terminated,'parse_valid':parsed,
                'within_length_limit':len(raw)<=parameters['max_length'],'valid_complete':valid,'canonical':canonical,
                'not_in_training_canonical_set':valid and canonical not in canonical_train})
    (Path(output_dir)/'generated-strings.json').write_text(json.dumps(generated,indent=2)+'\n',encoding='utf-8')
    return {'scope':'ACTUAL_TINY_CNO_CHAIN_VAE_TRAINING_AND_DECODE_NOT_GENERAL_MOLECULAR_GENERATION_VALIDATION',
            'environment':{'numpy':np.__version__,'torch':torch.__version__,'rdkit':rdBase.rdkitVersion,'device':'CPU'},
            'vocabulary':VOCAB,'losses':losses,'generated':generated,'valid_complete_count':sum(row['valid_complete'] for row in generated),
            'unique_valid_canonical_count':len({row['canonical'] for row in generated if row['valid_complete']}),
            'local_training_runs':1,'optimizer_updates':parameters['epochs'],'optimization_status':'FIXED_BUDGET_NOT_CONVERGENCE_CERTIFIED',
            'checks':[{'name':'owned_weights_encoder_replay','passed':bool(replay),'actual':bool(replay),'threshold':True}],
            'limits':['Restricted C/N/O linear chains only; not a general SMILES tokenizer or drug-like generator.',
                      'Unterminated, overlength, empty and invalid outputs are retained, not hidden or claimed successful.',
                      'Novelty is only against this tiny training canonical set, not databases, patents or experimental feasibility.',
                      'No held-out generative quality, chemical usefulness, synthesizeability or property optimization is certified.']}
