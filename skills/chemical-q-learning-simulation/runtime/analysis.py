"""Actual tabular Q-learning in an explicit finite teaching MDP, no chemistry engine."""
from pathlib import Path
import numpy as np
from .support import keys,integer,real,array,check

def update(q,state,action,reward,next_state,terminated,alpha,gamma):
    target=reward if terminated else reward+gamma*float(np.max(q[next_state]))
    q[state,action]+=alpha*(target-q[state,action])
    return target

def analyze(parameters,data,output_dir):
    keys(parameters,['seed','episodes','max_steps','alpha','gamma','epsilon','evaluation_episodes'])
    seed=integer(parameters['seed'],0,2**31-1,'seed');episodes=integer(parameters['episodes'],1,200,'episodes')
    max_steps=integer(parameters['max_steps'],1,20,'max_steps');evaluation=integer(parameters['evaluation_episodes'],1,20,'evaluation_episodes')
    alpha=real(parameters['alpha'],.001,1,'alpha');gamma=real(parameters['gamma'],0,.999,'gamma');epsilon=real(parameters['epsilon'],0,1,'epsilon')
    keys(data,['states','actions','initial_state','terminal_states','transition_probability','transition_reward','reward_unit'])
    states,actions=data['states'],data['actions']
    for names,lo,hi in [(states,2,20),(actions,1,4)]:
        if not isinstance(names,list) or not lo<=len(names)<=hi or len(set(names))!=len(names) or any(not isinstance(n,str) or not n for n in names):raise ValueError('Unique bounded names required.')
    n,a=len(states),len(actions)
    terminals=data['terminal_states']
    if not isinstance(terminals,list) or not terminals or len(set(terminals))!=len(terminals) or not set(terminals)<=set(states) or data['initial_state'] not in states or data['initial_state'] in terminals:raise ValueError('Explicit initial nonterminal and terminal states required.')
    if not isinstance(data['reward_unit'],str) or not data['reward_unit']:raise ValueError('Explicit reward unit required.')
    p=array(data['transition_probability'],3);r=array(data['transition_reward'],3)
    if p.shape!=(n,a,n) or r.shape!=p.shape or np.any(p<0) or not np.allclose(p.sum(axis=2),1,atol=1e-12,rtol=0) or np.max(abs(r))>1e6:raise ValueError('Finite bounded transition reward/probability arrays; stochastic rows must sum1.')
    terminal_indices={states.index(t) for t in terminals};initial=states.index(data['initial_state'])
    for t in terminal_indices:
        if np.any(p[t,:,t]!=1) or np.any(r[t]!=0):raise ValueError('Declared terminal rows must be absorbing with zero subsequent reward.')
    rng=np.random.default_rng(seed);q=np.zeros((n,a));training=[]
    def episode(learn):
        state=initial;total=0.;terminated=False;steps=[]
        for step in range(max_steps):
            action=int(rng.integers(a)) if learn and rng.random()<epsilon else int(np.argmax(q[state]))
            nxt=int(rng.choice(n,p=p[state,action]));reward=float(r[state,action,nxt]);terminated=nxt in terminal_indices
            target=update(q,state,action,reward,nxt,terminated,alpha,gamma) if learn else None
            steps.append({'state':states[state],'action':actions[action],'next_state':states[nxt],'reward':reward,'terminated':terminated,'target':target})
            total+=reward;state=nxt
            if terminated:break
        return {'undiscounted_return':total,'terminated':terminated,'truncated':not terminated,'steps':steps}
    for _ in range(episodes):training.append(episode(True))
    frozen=q.copy();evaluation_rows=[episode(False) for _ in range(evaluation)]
    artifact=Path(output_dir)/'q-values.npy';np.save(artifact,q,allow_pickle=False);restored=np.load(artifact,allow_pickle=False)
    return {'scope':'ACTUAL_TABULAR_Q_LEARNING_EXPLICIT_TOY_MDP_NOT_REACTION_KINETICS_OR_LAB_CONTROL',
        'environment':{'numpy':np.__version__},'q_values':q.tolist(),'policy':{s:actions[int(np.argmax(q[i]))] for i,s in enumerate(states) if i not in terminal_indices},
        'training_episodes':training,'frozen_greedy_evaluation':evaluation_rows,
        'termination_rule':'Bootstrap zero only for explicit terminal state; external step-cap truncation still bootstraps.',
        'local_training_runs':1,'training_updates':sum(len(row['steps']) for row in training),
        'optimization_status':'FIXED_BUDGET_NOT_CONVERGENCE_OR_OPTIMALITY_CERTIFIED',
        'checks':[check('evaluation_does_not_modify_q',np.array_equal(q,frozen)),check('q_save_restore',np.array_equal(q,restored))],
        'limits':['All transition probabilities and rewards are authored or user-supplied; no new chemical rates, energetics or experiments.',
                  'Finite horizon inherent to a physical task requires remaining time in state; current cap is an external truncation.',
                  'Fixed epsilon/alpha and finite budget do not establish asymptotic convergence or an optimal policy.']}
