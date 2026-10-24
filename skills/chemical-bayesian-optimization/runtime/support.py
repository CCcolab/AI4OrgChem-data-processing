"""Finite-pool optimization inputs: supplied observations are never fabricated."""
import numpy as np

def keys(value,required,optional=()):
    if not isinstance(value,dict) or not set(required)<=set(value) or set(value)-set(required)-set(optional):
        raise ValueError('Required fields: '+','.join(required))

def integer(value,low,high,name):
    if type(value) is not int or not low<=value<=high:raise ValueError(name+' out of integer budget.')
    return value

def real(value,low,high,name):
    if type(value) not in {int,float} or not np.isfinite(value) or not low<=value<=high:raise ValueError(name+' outside finite budget.')
    return float(value)

def array(value,ndim):
    a=np.asarray(value)
    if a.dtype.kind not in 'if' or a.ndim!=ndim or not a.size or not np.isfinite(a).all():raise ValueError('Finite real arrays required.')
    return a.astype(float)

def inputs(data,multi=False):
    keys(data,['bounds','feature_names','feature_units','observed_ids','observed_x','observed_y','source_ids','candidate_ids','candidate_x','objective_units'])
    bounds=array(data['bounds'],2);x=array(data['observed_x'],2);candidates=array(data['candidate_x'],2)
    y=array(data['observed_y'],2 if multi else 1)
    if (not 1<=len(bounds)<=3 or bounds.shape[1]!=2 or not np.all(bounds[:,1]>bounds[:,0])
            or not 3<=len(x)<=32 or not 1<=len(candidates)<=64 or x.shape[1]!=len(bounds) or candidates.shape[1]!=len(bounds)
            or len(y)!=len(x) or multi and y.shape[1]!=2):raise ValueError('1–3 dimensions,3–32 observations,1–64 candidates,2 objectives for MO.')
    for key,length in [('feature_names',len(bounds)),('feature_units',len(bounds)),('observed_ids',len(x)),('source_ids',len(x)),('candidate_ids',len(candidates)),('objective_units',2 if multi else 1)]:
        values=data[key]
        if not isinstance(values,list) or len(values)!=length or any(not isinstance(v,str) or not v for v in values):raise ValueError('Explicit aligned '+key+' required.')
    if len(set(data['observed_ids']+data['candidate_ids']))!=len(x)+len(candidates) or len(set(data['feature_names']))!=len(bounds):raise ValueError('Unique observation/candidate IDs and feature names required.')
    span=bounds[:,1]-bounds[:,0]
    xs=(x-bounds[:,0])/span;cs=(candidates-bounds[:,0])/span
    if np.any(xs<0) or np.any(xs>1) or np.any(cs<0) or np.any(cs>1):raise ValueError('Points outside declared bounds.')
    if not np.isfinite(xs).all() or not np.isfinite(cs).all():raise ValueError('Unrepresentable scaled inputs.')
    if any(np.allclose(xs[i],xs[j],atol=1e-12,rtol=0) for i in range(len(x)) for j in range(i)):
        raise ValueError('Duplicate observation coordinates require explicit replicate/noise treatment, not this interface.')
    if any(np.allclose(cs[i],cs[j],atol=1e-12,rtol=0) for i in range(len(cs)) for j in range(i)):
        raise ValueError('Duplicate candidate coordinates.')
    eligible=[i for i,c in enumerate(cs) if not np.any(np.all(np.isclose(xs,c,atol=1e-12,rtol=0),axis=1))]
    if not eligible:raise ValueError('No unobserved candidate remains.')
    return x,y,candidates,xs,cs,eligible

def check(name,passed):return {'name':name,'passed':bool(passed),'actual':bool(passed),'threshold':True}
