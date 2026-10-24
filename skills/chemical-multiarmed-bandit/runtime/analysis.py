"""Bounded stationary Bernoulli bandit simulation or explicitly supplied history."""
import math
import numpy as np
from .support import keys,integer,real,check

def select(algorithm,counts,rewards,t,rng,exploration):
    missing=np.flatnonzero(counts==0)
    if len(missing):return int(missing[0])
    if algorithm=='ucb':return int(np.argmax(rewards/counts+exploration*np.sqrt(2*math.log(max(t,2))/counts)))
    return int(np.argmax(rng.beta(1+rewards,1+counts-rewards)))

def analyze(parameters,data):
    keys(parameters,['mode','algorithm','seed','budget','exploration'])
    mode=parameters['mode'];algorithm=parameters['algorithm']
    if mode not in {'simulate','replay'} or algorithm not in {'ucb','thompson'}:raise ValueError('Explicit simulate/replay and ucb/thompson required.')
    seed=integer(parameters['seed'],0,2**31-1,'seed');budget=integer(parameters['budget'],1,200,'budget')
    exploration=real(parameters['exploration'],.01,10,'exploration')
    keys(data,['arms','probabilities'] if mode=='simulate' else ['arms','history'])
    arms=data['arms']
    if not isinstance(arms,list) or not 2<=len(arms)<=10 or any(not isinstance(a,str) or not a for a in arms) or len(set(arms))!=len(arms):raise ValueError('2–10 unique named arms required.')
    rng=np.random.default_rng(seed);counts=np.zeros(len(arms),dtype=int);sums=np.zeros(len(arms),dtype=int);history=[]
    probabilities=None
    if mode=='simulate':
        probabilities=np.asarray(data['probabilities'])
        if probabilities.dtype.kind not in 'if' or probabilities.shape!=(len(arms),) or not np.isfinite(probabilities).all() or np.any(probabilities<0) or np.any(probabilities>1):raise ValueError('Declared finite Bernoulli probabilities per arm required.')
        for t in range(budget):
            a=select(algorithm,counts,sums,t+1,rng,exploration);reward=int(rng.random()<probabilities[a])
            counts[a]+=1;sums[a]+=reward;history.append({'step':t+1,'arm':arms[a],'reward':reward,'source_id':'AUTHORED_BERNOULLI_SIMULATION'})
    else:
        if not isinstance(data['history'],list) or not 1<=len(data['history'])<=budget:raise ValueError('1..budget explicitly supplied observations required.')
        sources=set()
        for row in data['history']:
            keys(row,['arm','reward','source_id'])
            if row['arm'] not in arms or type(row['reward']) is not int or row['reward'] not in {0,1} or not isinstance(row['source_id'],str) or not row['source_id'] or row['source_id'] in sources:raise ValueError('Existing arm, integer0/1 reward and unique nonempty source required.')
            sources.add(row['source_id']);a=arms.index(row['arm']);counts[a]+=1;sums[a]+=row['reward'];history.append(dict(row))
    before=counts.copy();proposal=select(algorithm,counts,sums,int(counts.sum())+1,rng,exploration)
    return {'scope':'ACTUAL_STATIONARY_BERNOULLI_BANDIT_SIMULATION_OR_HISTORY_REPLAY_NOT_CHEMICAL_EXPERIMENT',
        'environment':{'numpy':np.__version__},'mode':mode,'algorithm':algorithm,'arm_counts':dict(zip(arms,counts.tolist())),
        'arm_successes':dict(zip(arms,sums.tolist())),'history':history,'simulated_probabilities':probabilities.tolist() if probabilities is not None else None,
        'proposal':{'arm':arms[proposal],'status':'PENDING_NOT_OBSERVED'},'observed_reward_count':int(counts.sum()),
        'checks':[check('recommendation_does_not_create_observation',np.array_equal(counts,before)),check('observations_not_lost',int(counts.sum())==len(history))],
        'limits':['Only stationary Bernoulli0/1 reward; fractional yield, continuous cost and drifting conditions are unsupported.',
                  'Thompson uses independent Beta(1,1) priors; UCB first explores unvisited arms in declared order.',
                  'Simulated probabilities are disclosed teaching inputs; no real experiment was performed and no best-arm/convergence guarantee is claimed.']}
