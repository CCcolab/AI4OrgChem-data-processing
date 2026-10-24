"""Actual Chemprop D-MPNN regression on explicit held-out molecular inputs."""
from pathlib import Path
import numpy as np
import torch
from .graph_support import check, dataset, environment, integer, keys, real, split


def analyze(parameters, input_data, output_dir):
    from chemprop import data,featurizers,nn,models
    import chemprop
    keys(parameters,['seed','test_indices','hidden_units','depth','epochs','learning_rate'])
    graphs,y=dataset(input_data)
    train,test=split(parameters,input_data,graphs)
    hidden=integer(parameters['hidden_units'],8,32,'hidden_units')
    depth=integer(parameters['depth'],2,3,'depth')
    epochs=integer(parameters['epochs'],1,100,'epochs')
    rate=real(parameters['learning_rate'],1e-5,.02,'learning_rate')
    torch.set_num_threads(1);torch.manual_seed(parameters['seed'])
    mean,scale=float(y[train].mean()),float(y[train].std()) or 1.
    featurizer=featurizers.SimpleMoleculeMolGraphFeaturizer()

    def batch(indices):
        points=[data.MoleculeDatapoint.from_smi(input_data['smiles'][i],[(float(y[i])-mean)/scale]) for i in indices]
        dataset_=data.MoleculeDataset(points,featurizer=featurizer)
        return next(iter(data.build_dataloader(dataset_,batch_size=len(points),num_workers=0,shuffle=False)))

    training,held=batch(train),batch(test)

    def build():
        return models.MPNN(nn.BondMessagePassing(d_h=hidden,depth=depth),nn.MeanAggregation(),
                           nn.RegressionFFN(input_dim=hidden,hidden_dim=hidden),batch_norm=False)

    model=build();optimizer=torch.optim.Adam(model.parameters(),lr=rate);losses=[]
    for _ in range(epochs):
        model.train();optimizer.zero_grad()
        prediction=model(training.bmg,training.V_d,training.X_d)
        loss=(prediction-training.Y).square().mean()
        if not torch.isfinite(loss):raise ValueError('Nonfinite Chemprop loss.')
        loss.backward()
        gradients=[p.grad for p in model.parameters() if p.grad is not None]
        if not gradients or not all(torch.isfinite(g).all() for g in gradients):raise ValueError('Nonfinite/missing gradients.')
        torch.nn.utils.clip_grad_norm_(model.parameters(),10);optimizer.step();losses.append(float(loss.detach()))
    model.eval()
    with torch.no_grad():raw=model(held.bmg,held.V_d,held.X_d)
    artifact=Path(output_dir)/'self-produced-chemprop-weights.pt';torch.save(model.state_dict(),artifact)
    restored=build();restored.load_state_dict(torch.load(artifact,weights_only=True,map_location='cpu'));restored.eval()
    with torch.no_grad():replay=restored(held.bmg,held.V_d,held.X_d)
    values=raw[:,0].numpy()*scale+mean
    return {'scope':'ACTUAL_BOUNDED_CHEMPROP_DMPNN_REGRESSION_TRAINING_NOT_PRETRAINED_OR_CHEMICAL_VALIDATION',
            'environment':{**environment(),'chemprop':chemprop.__version__},'train_indices':train,'test_indices':test,
            'training_loss':losses,'target_train_mean':mean,'target_train_scale':scale,'target_unit':input_data['target_unit'],
            'held_out_predictions':values.tolist(),'held_out_observed':y[test].tolist(),'held_out_MAE':float(np.mean(abs(values-y[test]))),
            'local_training_runs':1,'optimizer_updates':epochs,'optimization_status':'FIXED_BUDGET_NOT_CONVERGENCE_CERTIFIED',
            'checks':[check('held_out_shape_and_finite',raw.shape==(len(test),1) and np.isfinite(values).all()),
                      check('owned_Chemprop_weights_replay',torch.allclose(raw,replay,atol=1e-6,rtol=1e-6))],
            'limits':['Explicit Chemprop 2.x molecular regression only; no reaction/atom-site model, classification or pretrained model import.',
                      'Target scaling uses training rows only; whole-molecule featurization does not authenticate chemical identity or applicability.',
                      'Finite-budget synthetic-label training is not chemical predictive validation, uncertainty calibration or production convergence.']}
