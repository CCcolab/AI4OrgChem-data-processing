"""Actual tiny masked-atom/contrastive pretraining and an optional frozen probe."""
from pathlib import Path
import csv
import numpy as np
import torch
import torch.nn.functional as F
from .graph_support import Encoder, check, dataset, environment, gradient_finite, integer, keys, real, split


def analyze(parameters,data,output_dir):
    keys(parameters,['mode','seed','test_indices','hidden_units','depth','epochs','learning_rate','batch_size','temperature'])
    mode=parameters['mode']
    if mode not in {'masked_atom','contrastive','mask_then_probe'}:
        raise ValueError('Choose masked_atom, contrastive or mask_then_probe.')
    if mode!='mask_then_probe' and {'target','target_unit'}.intersection(data):
        raise ValueError('Unsupervised examples must not include property labels; use mask_then_probe explicitly.')
    graphs,y=dataset(data,supervised=mode=='mask_then_probe')
    train,test=split(parameters,data,graphs)
    hidden=integer(parameters['hidden_units'],4,32,'hidden_units');depth=integer(parameters['depth'],1,3,'depth')
    epochs=integer(parameters['epochs'],1,50,'epochs');rate=real(parameters['learning_rate'],1e-5,.02,'learning_rate')
    batch_size=integer(parameters['batch_size'],2,len(train),'batch_size');tau=real(parameters['temperature'],.05,1,'temperature')
    torch.set_num_threads(1);torch.manual_seed(parameters['seed'])
    encoder=Encoder(hidden,depth)
    head=torch.nn.Linear(hidden,119) if mode!='contrastive' else torch.nn.Sequential(torch.nn.Linear(hidden,hidden),torch.nn.ReLU(),torch.nn.Linear(hidden,8))
    optimizer=torch.optim.Adam([*encoder.parameters(),*head.parameters()],lr=rate)
    losses=[];last_pairs=None
    for _ in range(epochs):
        encoder.train();head.train();optimizer.zero_grad()
        if mode=='contrastive':
            indices=torch.randperm(len(train))[:batch_size].tolist()
            views=[]
            for _view in range(2):
                for index in indices:
                    graph=graphs[train[index]]
                    x=graph['x'].clone();x=x*(torch.rand_like(x)>.15)
                    views.append(head(encoder({**graph,'x':x})))
            embeddings=F.normalize(torch.stack(views),dim=1)
            scores=embeddings@embeddings.T/tau
            scores=scores.masked_fill(torch.eye(2*batch_size,dtype=torch.bool),float('-inf'))
            positives=(torch.arange(2*batch_size)+batch_size)%(2*batch_size)
            last_pairs=positives.tolist()
            loss=F.cross_entropy(scores,positives)
        else:
            terms=[]
            for index in train:
                graph=graphs[index];chosen=int(torch.randint(len(graph['x']),(1,)))
                target=torch.tensor([round(float(graph['x'][chosen,0])*100)],dtype=torch.long)
                masked=graph['x'].clone();masked[chosen,0]=0
                logits=head(encoder.nodes({**graph,'x':masked})[chosen:chosen+1])
                terms.append(F.cross_entropy(logits,target))
            loss=torch.stack(terms).mean()
        if not torch.isfinite(loss):raise ValueError('Nonfinite pretraining loss.')
        loss.backward()
        if not gradient_finite(encoder) or not gradient_finite(head):raise ValueError('Missing/nonfinite gradients.')
        torch.nn.utils.clip_grad_norm_([*encoder.parameters(),*head.parameters()],10)
        optimizer.step();losses.append(float(loss.detach()))
    encoder.eval();head.eval()
    with torch.no_grad():all_vectors=torch.stack([encoder(graph) for graph in graphs])
    checks=[check('finite_pretraining_embeddings',torch.isfinite(all_vectors).all())]
    if mode=='contrastive':
        checks.append(check('positive_pairs_exclude_self',all(i!=j for i,j in enumerate(last_pairs))))
    probe_result=None;probe=None
    if mode=='mask_then_probe':
        encoder.requires_grad_(False)
        before={name:p.detach().clone() for name,p in encoder.named_parameters()}
        mean=all_vectors[train].mean(dim=0);scale=all_vectors[train].std(dim=0,unbiased=False).clamp_min(1e-8)
        z=(all_vectors-mean)/scale
        ymean,yscale=float(y[train].mean()),float(y[train].std()) or 1.
        target=torch.tensor((y[train]-ymean)/yscale,dtype=torch.float32)
        probe=torch.nn.Linear(hidden,1);opt=torch.optim.Adam(probe.parameters(),lr=.02)
        for _ in range(50):
            opt.zero_grad();loss=(probe(z[train]).squeeze(-1)-target).square().mean()
            if not torch.isfinite(loss):raise ValueError('Nonfinite frozen-probe loss.')
            loss.backward();opt.step()
        with torch.no_grad():prediction=probe(z[test]).squeeze(-1).numpy()*yscale+ymean
        checks.append(check('encoder_weights_frozen_during_probe',all(torch.equal(before[name],p) for name,p in encoder.named_parameters())))
        probe_result={'held_out_predictions':prediction.tolist(),'held_out_MAE':float(np.mean(abs(prediction-y[test]))),
                      'target_unit':data['target_unit'],'probe_updates':50,'encoder_frozen':True}
    states={'encoder':encoder.state_dict(),'head':head.state_dict()}
    if probe is not None:states['probe']=probe.state_dict()
    artifact=Path(output_dir)/'self-produced-pretraining-weights.pt';torch.save(states,artifact)
    loaded=torch.load(artifact,weights_only=True,map_location='cpu')
    restored=Encoder(hidden,depth);restored.load_state_dict(loaded['encoder']);restored.eval()
    with torch.no_grad():checks.append(check('owned_encoder_replay',torch.allclose(encoder(graphs[0]),restored(graphs[0]),atol=1e-6,rtol=1e-6)))
    with (Path(output_dir)/'learned-embeddings.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.writer(stream);writer.writerow(['id','split']+['embedding_'+str(i) for i in range(hidden)])
        writer.writerows([id_,'train' if i in train else 'held_out',*v.tolist()] for i,(id_,v) in enumerate(zip(data['ids'],all_vectors)))
    return {'scope':'ACTUAL_TINY_SELF_SUPERVISED_GRAPH_TRAINING_NOT_PRETRAINING_BENEFIT_CERTIFICATION',
            'environment':environment(),'mode':mode,'train_indices':train,'test_indices':test,'training_loss':losses,
            'probe':probe_result,'local_training_runs':2 if probe_result else 1,'optimizer_updates':epochs+(50 if probe_result else 0),
            'unencoded_stereo_or_isotope_ids':[data['ids'][i] for i,g in enumerate(graphs) if g['unencoded_stereo_or_isotope']],
            'optimization_status':'FIXED_BUDGET_NOT_CONVERGENCE_CERTIFIED','checks':checks,
            'limits':['Masked atomic-number targets are held separately; no property labels enter pretraining.',
                      'Feature masking is a tensor augmentation, not a chemically validated new molecule or semantic equivalence proof.',
                      'Different molecules used as negatives may be chemically similar; the objective does not certify chemical semantics.',
                      'No downstream improvement claim without a matched from-scratch baseline and independent data.',
                      'The optional frozen probe is a software demonstration on declared labels, not chemical predictive validation.']}
