"""Actual small BoTorch qLogNEHVI, finite-pool one-point pending proposal."""
from pathlib import Path
import warnings
import numpy as np
import torch
import botorch,gpytorch
from botorch.models import SingleTaskGP
from botorch.models.transforms.outcome import Standardize
from botorch.fit import fit_gpytorch_mll
from botorch.acquisition.multi_objective.logei import qLogNoisyExpectedHypervolumeImprovement
from botorch.sampling.normal import SobolQMCNormalSampler
from botorch.utils.multi_objective.pareto import is_non_dominated
from botorch.utils.multi_objective.hypervolume import Hypervolume
from gpytorch.mlls import ExactMarginalLogLikelihood
from .support import keys,inputs,array,integer,real,check

def analyze(parameters,data,output_dir):
    keys(parameters,['seed','directions','reference_point','noise_sd','maxiter','mc_samples'])
    seed=integer(parameters['seed'],0,2**31-1,'seed');maxiter=integer(parameters['maxiter'],1,30,'maxiter')
    samples=integer(parameters['mc_samples'],8,64,'mc_samples')
    directions=parameters['directions']
    if not isinstance(directions,list) or len(directions)!=2 or any(v not in {'maximize','minimize'} for v in directions):raise ValueError('Two explicit directions required.')
    reference=array(parameters['reference_point'],1);noise=array(parameters['noise_sd'],1)
    if reference.shape!=(2,) or noise.shape!=(2,) or np.any(noise<1e-6) or np.any(noise>1e6):raise ValueError('Two reference coordinates and positive noise SDs required.')
    x,y,candidates,xs,cs,eligible=inputs(data,multi=True)
    signs=np.array([1 if d=='maximize' else -1 for d in directions]);ys=y*signs;ref=reference*signs
    if not np.any(np.all(ys>ref,axis=1)):raise ValueError('Declared reference must be strictly dominated by at least one observed point in transformed maximization coordinates.')
    torch.set_num_threads(1);torch.manual_seed(seed)
    tx=torch.tensor(xs,dtype=torch.double);ty=torch.tensor(ys,dtype=torch.double)
    variance=torch.tensor(np.broadcast_to(noise**2,ys.shape).copy(),dtype=torch.double)
    model=SingleTaskGP(tx,ty,train_Yvar=variance,outcome_transform=Standardize(m=2))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        fit_gpytorch_mll(ExactMarginalLogLikelihood(model.likelihood,model),max_attempts=1,
                        optimizer_kwargs={'options':{'maxiter':maxiter}})
        model.eval()
        sampler=SobolQMCNormalSampler(sample_shape=torch.Size([samples]),seed=seed)
        acq=qLogNoisyExpectedHypervolumeImprovement(model=model,ref_point=ref.tolist(),X_baseline=tx,sampler=sampler,prune_baseline=False)
        points=torch.tensor(cs[eligible],dtype=torch.double)
        with torch.no_grad():values=acq(points.unsqueeze(1));posterior=model.posterior(points);pred=posterior.mean
    if not torch.isfinite(values).all() or not torch.isfinite(pred).all():raise ValueError('Nonfinite acquisition/posterior.')
    index=int(torch.argmax(values));selected=eligible[index]
    artifact=Path(output_dir)/'self-produced-gp-state.pt';torch.save(model.state_dict(),artifact)
    restored=SingleTaskGP(tx,ty,train_Yvar=variance,outcome_transform=Standardize(m=2))
    restored.load_state_dict(torch.load(artifact,weights_only=True,map_location='cpu'));restored.eval()
    with torch.no_grad():replay=torch.allclose(restored.posterior(points).mean,pred,atol=1e-8,rtol=1e-8)
    pareto=is_non_dominated(ty);hv=Hypervolume(torch.tensor(ref,dtype=torch.double)).compute(ty[pareto])
    return {'scope':'ACTUAL_BOTORCH_TWO_OBJECTIVE_GP_QLOGNEHVI_PENDING_PROPOSAL_NOT_EXPERIMENT',
        'environment':{'numpy':np.__version__,'torch':torch.__version__,'botorch':botorch.__version__,'gpytorch':gpytorch.__version__,'device':'CPU_DOUBLE'},
        'directions':directions,'reference_original_units':reference.tolist(),'observed_hypervolume':float(hv),
        'observed_nondominated_ids':[v for v,keep in zip(data['observed_ids'],pareto.tolist()) if keep],
        'proposal':{'id':data['candidate_ids'][selected],'x':candidates[selected].tolist(),'status':'PENDING_NOT_OBSERVED','posterior_mean_original_units':(pred[index].numpy()*signs).tolist()},
        'eligible_candidate_ids':[data['candidate_ids'][i] for i in eligible],'log_acquisition_values':values.tolist(),
        'fit_warnings':[str(w.message) for w in caught],'optimization_status':'BOUNDED_FIT_NOT_CONVERGENCE_CERTIFIED',
        'observation_count_unchanged':len(y),'local_model_fits':1,'checks':[check('owned_gp_state_restore',replay),check('proposal_not_observed',selected in eligible)],
        'limits':['Objectives/reference/noise assumptions are explicit and not physical calibration.',
                  'Hypervolume has the product of objective units and changes with scale/reference; no cross-study comparison without matching conventions.',
                  'No experiment feedback, objective evaluation, global optimum or chemical feasibility certificate.']}
