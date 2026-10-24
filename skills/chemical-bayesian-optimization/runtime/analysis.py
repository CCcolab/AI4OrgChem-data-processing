"""Fixed-kernel Gaussian process and one unobserved finite-pool EI proposal."""
from pathlib import Path
import csv
import numpy as np
import scipy
from scipy.stats import norm
import sklearn
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import ConstantKernel,RBF
import joblib
from .support import keys,inputs,integer,real,check

def analyze(parameters,data,output_dir):
    keys(parameters,['seed','direction','noise_sd','length_scale','xi'])
    seed=integer(parameters['seed'],0,2**31-1,'seed')
    direction=parameters['direction']
    if direction not in {'maximize','minimize'}:raise ValueError('Explicit maximize/minimize required.')
    noise=real(parameters['noise_sd'],1e-6,1e6,'noise_sd')
    length=real(parameters['length_scale'],.01,10,'length_scale')
    xi=real(parameters['xi'],0,1e6,'xi')
    x,y,candidates,xs,cs,eligible=inputs(data)
    center=float(y.mean());scale=float(y.std()) or 1.
    if not np.isfinite(center) or not np.isfinite(scale):raise ValueError('Target scale overflow.')
    gp=GaussianProcessRegressor(kernel=ConstantKernel(1.,constant_value_bounds='fixed')*RBF(length,length_scale_bounds='fixed'),
        alpha=(noise/scale)**2,optimizer=None,normalize_y=False,random_state=seed)
    gp.fit(xs,(y-center)/scale)
    mean,sd=gp.predict(cs,return_std=True);mean=mean*scale+center;sd=sd*scale
    sign=1 if direction=='maximize' else -1
    best=float(max(sign*y));improvement=sign*mean-best-xi
    z=np.divide(improvement,sd,out=np.zeros_like(sd),where=sd>0)
    ei=np.where(sd>0,improvement*norm.cdf(z)+sd*norm.pdf(z),np.maximum(improvement,0))
    if not np.isfinite(mean).all() or not np.isfinite(sd).all() or not np.isfinite(ei).all():raise ValueError('Nonfinite posterior/acquisition.')
    selected=max(eligible,key=lambda i:float(ei[i]))
    artifact=Path(output_dir)/'self-produced-gp.joblib';joblib.dump(gp,artifact)
    restored=joblib.load(artifact)
    replay=np.allclose(restored.predict(cs),gp.predict(cs),atol=1e-12,rtol=1e-12)
    with (Path(output_dir)/'candidate-predictions.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['id','eligible_unobserved','posterior_mean','latent_sd','expected_improvement'])
        w.writerows([id_,i in eligible,float(m),float(s),float(e)] for i,(id_,m,s,e) in enumerate(zip(data['candidate_ids'],mean,sd,ei)))
    return {'scope':'ACTUAL_FIXED_KERNEL_GP_AND_FINITE_POOL_EI_PENDING_PROPOSAL_NOT_EXPERIMENT',
        'environment':{'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__},
        'direction':direction,'target_center_train_only':center,'target_scale_train_only':scale,
        'posterior_sd_definition':'LATENT_FUNCTION_CONDITIONAL_ON_FIXED_KERNEL_AND_DECLARED_OBSERVATION_NOISE_NOT_CALIBRATED_PHYSICAL_UNCERTAINTY',
        'proposal':{'id':data['candidate_ids'][selected],'x':candidates[selected].tolist(),'status':'PENDING_NOT_OBSERVED','predicted_mean':float(mean[selected]),'expected_improvement':float(ei[selected])},
        'observation_count_unchanged':len(y),'local_model_fits':1,'checks':[check('owned_gp_save_restore',replay),check('proposal_not_observed',selected in eligible)],
        'limits':['No objective evaluation, measured feedback, automatic observation insertion or convergence claim.',
                  'Fixed length scale/amplitude and assumed noise are explicit choices, not optimized or calibrated from this small dataset.',
                  'A proposal is restricted to the declared finite pool; it is not a global or chemically feasible optimum.']}
