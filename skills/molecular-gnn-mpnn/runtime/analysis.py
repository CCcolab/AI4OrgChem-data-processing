"""Actual tiny reference MPNN training, not a benchmark reproduction."""
from pathlib import Path
import csv
import numpy as np
import torch
from .graph_support import Predictor, check, dataset, environment, gradient_finite, integer, keys, permutation, real, split


def analyze(parameters, data, output_dir):
    keys(parameters,['seed','test_indices','task','hidden_units','depth','epochs','learning_rate'])
    graphs,y=dataset(data)
    train,test=split(parameters,data,graphs)
    hidden=integer(parameters['hidden_units'],4,32,'hidden_units')
    depth=integer(parameters['depth'],1,3,'depth')
    epochs=integer(parameters['epochs'],1,100,'epochs')
    rate=real(parameters['learning_rate'],1e-5,.05,'learning_rate')
    classification=parameters['task']=='binary_classification'
    if parameters['task'] not in {'regression','binary_classification'}:
        raise ValueError('Declare regression or binary_classification.')
    if classification and (not np.isin(y,[0,1]).all() or len(set(y[train]))!=2):
        raise ValueError('Binary labels 0/1 and both training classes required.')
    torch.set_num_threads(1)
    torch.manual_seed(parameters['seed'])
    model=Predictor(hidden,depth)
    optimizer=torch.optim.Adam(model.parameters(),lr=rate)
    mean,scale=(0.,1.) if classification else (float(y[train].mean()),float(y[train].std()) or 1.)
    target=torch.tensor((y[train]-mean)/scale,dtype=torch.float32)
    criterion=torch.nn.BCEWithLogitsLoss() if classification else torch.nn.MSELoss()
    training_graphs=[graphs[i] for i in train]
    losses=[]
    for _ in range(epochs):
        model.train();optimizer.zero_grad()
        loss=criterion(model(training_graphs),target)
        if not torch.isfinite(loss):raise ValueError('Nonfinite training loss.')
        loss.backward()
        if not gradient_finite(model):raise ValueError('Nonfinite or missing gradients.')
        torch.nn.utils.clip_grad_norm_(model.parameters(),10)
        optimizer.step();losses.append(float(loss.detach()))
    model.eval()
    held=[graphs[i] for i in test]
    with torch.no_grad():
        raw=model(held)
        values=torch.sigmoid(raw).numpy() if classification else raw.numpy()*scale+mean
        invariant=torch.allclose(model([graphs[0]]),model([permutation(graphs[0])]),atol=1e-5,rtol=1e-5)
    artifact=Path(output_dir)/'self-produced-weights.pt'
    torch.save(model.state_dict(),artifact)
    restored=Predictor(hidden,depth)
    restored.load_state_dict(torch.load(artifact,weights_only=True,map_location='cpu'));restored.eval()
    with torch.no_grad():replay=torch.allclose(raw,restored(held),atol=1e-6,rtol=1e-6)
    with (Path(output_dir)/'held-out-predictions.csv').open('w',newline='',encoding='utf-8') as stream:
        writer=csv.writer(stream);writer.writerow(['id','raw_smiles','observed','predicted_probability' if classification else 'predicted'])
        writer.writerows((data['ids'][i],data['smiles'][i],float(y[i]),float(p)) for i,p in zip(test,values))
    score=float(np.mean((values>=.5)==y[test])) if classification else float(np.mean(abs(values-y[test])))
    return {'scope':'ACTUAL_BOUNDED_CPU_REFERENCE_MPNN_TRAINING_NOT_CHEMICAL_PREDICTIVE_VALIDATION',
            'environment':environment(),'train_indices':train,'test_indices':test,'training_loss':losses,
            'target_train_mean':mean,'target_train_scale':scale,'target_unit':data['target_unit'],
            'held_out_accuracy' if classification else 'held_out_MAE':score,
            'local_training_runs':1,'optimizer_updates':epochs,'optimization_status':'FIXED_BUDGET_NOT_CONVERGENCE_CERTIFIED',
            'checks':[check('node_order_permutation_invariance',invariant),check('owned_weights_prediction_replay',replay),
                      check('finite_held_out_predictions',np.isfinite(values).all())],
            'unencoded_stereo_or_isotope_ids':[data['ids'][i] for i,g in enumerate(graphs) if g['unencoded_stereo_or_isotope']],
            'limits':['Reference architecture: atom number/degree/charge/aromaticity, directed bond-order messages and sum pooling; not a reproduction of a published benchmark.',
                      'No 3D coordinates, isotope or stereochemical feature encoding; affected records explicitly listed.',
                      'Finite-budget training and synthetic labels do not establish convergence, chemical generalization or predictive uncertainty.',
                      'No pre-trained weights, external model service or arbitrary graph-model checkpoint is imported.']}
