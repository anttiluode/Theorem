"""Gate 008: nonlinear equilibrium breaking with independent matched +/- pulses.

The estimator knows the *candidate* Laplacian, local-linear and cubic
reaction terms, but not their coefficients, term support, or sensor R.
It needs two replicated preparations of the SAME latent uniform +/-1
equilibrium per pulse pair. This strong reset assumption is explicit.
Sensor-only nonlinear response is an adversarial physical counterexample.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

N=32
RMS=.055
PIXEL_CAP=.16
PAIRS=4
Z=3.
POLICIES=('passive','white','targeted_sparse','single_fourier','mislogged_kick')
WORLDS=('allen_cahn','diffusion_only','linear_surrogate',
        'reaction_only','identity','quadratic_sensor')


def lap(v):
    return sum(np.roll(v, sh, axis=ax)
               for ax in (0,1) for sh in (-1,1))-4*v


def probe(rng,kind):
    total=N*N*RMS**2
    if kind in ('white','mislogged_kick'):
        z=rng.normal(size=(N,N))
        lo,hi=0.,1.
        while np.sum(np.minimum(abs(z)*hi,PIXEL_CAP)**2)<total:
            hi*=2
        for _ in range(45):
            mid=(lo+hi)/2
            if np.sum(np.minimum(abs(z)*mid,PIXEL_CAP)**2)>total:
                hi=mid
            else:
                lo=mid
        u=np.sign(z)*np.minimum(abs(z)*(lo+hi)/2,PIXEL_CAP)
    elif kind=='targeted_sparse':
        u=np.zeros(N*N)
        full=int(total/PIXEL_CAP**2)
        ix=rng.permutation(N*N)[:full+1]
        u[ix[:full]]=PIXEL_CAP*rng.choice((-1,1),size=full)
        u[ix[full]]=np.sqrt(total-full*PIXEL_CAP**2)*rng.choice((-1,1))
        u=u.reshape(N,N)
    elif kind=='single_fourier':
        y,x=np.indices((N,N))
        f=int(rng.integers(1,8))
        u=np.cos(2*np.pi*f*x/N+rng.uniform(-np.pi,np.pi))
        u=RMS*u/np.sqrt(np.mean(u*u))
    else:
        raise ValueError(kind)
    assert abs(np.linalg.norm(u)-np.sqrt(total))<1e-8
    assert np.max(abs(u))<=PIXEL_CAP+1e-9
    return u


def curvature_info(u):
    v=u*u
    return float(np.sum((v-v.mean())**2))


def true_parameters(seed,world):
    if world not in WORLDS:
        raise ValueError(world)
    rng=np.random.default_rng(seed+44000)
    D=float(rng.uniform(.11,.19))
    r=float(rng.uniform(.14,.26))
    a=0.
    q=0.
    if world in ('diffusion_only','linear_surrogate','identity',
                 'quadratic_sensor'):
        r=0.
    if world=='linear_surrogate':
        a=float(-2*rng.uniform(.14,.26))
    if world=='reaction_only':
        D=0.
    if world=='identity':
        D=0.
    if world=='quadratic_sensor':
        q=float(rng.uniform(-3.8,-3.2))
    return {'D':D,'r':r,'a':a,'detector_q':q}


def step(v,s,truth):
    return (v+truth['D']*lap(v)+truth['a']*(v-s)
            +truth['r']*(v-v*v*v))


def generate(seed,world,policy,channel='primary',sensor_std=None,pairs=PAIRS):
    """Simulator only. Learner receives observations and logged actions.

    Every +/- pair uses two independently noisy copies of the identical
    s=+/-1 latent equilibrium. Primary detector can add quadratic artifact;
    reference channel sees same latent law with an ideal linear detector.
    """
    if policy not in POLICIES:
        raise ValueError(policy)
    if channel not in ('primary','reference'):
        raise ValueError(channel)
    rng=np.random.default_rng(seed+38000)
    truth=true_parameters(seed,world)
    s=float(rng.choice((-1.,1.)))
    sd=float(rng.uniform(.07,.09)) if sensor_std is None else float(sensor_std)
    rows=[]
    for _ in range(pairs):
        actual=(np.zeros((N,N)) if policy=='passive' else
                probe(rng,'white' if policy=='mislogged_kick' else policy))
        plus=step(s+actual,s,truth)+.003*rng.normal(size=(N,N))
        minus=step(s-actual,s,truth)+.003*rng.normal(size=(N,N))
        if truth['detector_q'] and channel=='primary':
            q=truth['detector_q']
            plus+=q*s*(plus-s)**2
            minus+=q*s*(minus-s)**2
        plus+=sd*rng.normal(size=(N,N))
        minus+=sd*rng.normal(size=(N,N))
        baseline=s+sd*rng.normal(size=(N,N))
        measured_sign=1. if baseline.mean()>=0 else -1.
        logged=(probe(rng,'mislogged_kick') if policy=='mislogged_kick'
                else actual)
        rows.append({'u':logged,'p':plus,'m':minus,'sign':measured_sign})
    return rows,truth,sd


def estimate(rows):
    """First infer reaction from even pulse response, then Lap and linear.

    Uses only observed (pulse, +/- output, observed phase sign).
    Empirical residual-based standard errors: no noise variance R argument.
    """
    es=[]
    fs=[]
    for row in rows:
        u=row['u']
        f=-3*row['sign']*(u*u-(u*u).mean())
        e=(row['p']+row['m'])/2
        fs.append(f.ravel())
        es.append((e-e.mean()).ravel())
    F=np.concatenate(fs)
    e=np.concatenate(es)
    info=float(F@F)
    if info<1e-12:
        return {'r':0.,'r_se':None,'D':0.,'D_se':None,
                'a':0.,'a_se':None,'rank':0,'curvature_information':info}
    r=float((F@e)/info)
    err=e-r*F
    sd=np.sqrt(float(err@err)/max(len(e)-1,1))
    r_se=float(sd/np.sqrt(info))
    xx=[]
    yy=[]
    for row in rows:
        u=row['u']
        odd=(row['p']-row['m'])/2-u
        target=odd+2*r*u+r*u**3
        xx.append(np.stack((lap(u).ravel(),u.ravel()),axis=1))
        yy.append(target.ravel())
    X=np.concatenate(xx)
    y=np.concatenate(yy)
    singular=np.linalg.svd(X,compute_uv=False)
    if singular[-1]/max(singular[0],1e-12)<1e-8:
        return {'r':r,'r_se':r_se,'D':0.,'D_se':None,
                'a':0.,'a_se':None,'rank':1,'curvature_information':info}
    theta=np.linalg.lstsq(X,y,rcond=None)[0]
    residual=y-X@theta
    cov=float(np.mean(residual**2))*np.linalg.inv(X.T@X)
    return {'r':r,'r_se':r_se,'D':float(theta[0]),
            'D_se':float(np.sqrt(cov[0,0])),'a':float(theta[1]),
            'a_se':float(np.sqrt(cov[1,1])),'rank':2,
            'curvature_information':info}


def judge(rows):
    half=len(rows)//2
    left=estimate(rows[:half])
    right=estimate(rows[half:])
    def detected(term):
        return bool(
            all(v[term+'_se'] is not None and
                abs(v[term])>Z*v[term+'_se'] for v in (left,right))
            and left[term]*right[term]>0)
    support={key:detected(key) for key in ('D','r','a')}
    pars={key:float((left[key]+right[key])/2) for key in ('D','r','a')}
    return {'selected_support':support,'estimated':pars,
            'train':left,'holdout':right,'nonlinear':support['r']}


def check(seed,world,policy,channel='primary'):
    rows,truth,sd=generate(seed,world,policy,channel)
    result=judge(rows)
    actual={key:abs(truth[key])>1e-12 for key in ('D','r','a')}
    result.update({
        'seed':int(seed),'world':world,'policy':policy,
        'sensor_channel':channel,'sensor_sd_hidden':float(sd),
        'truth':truth,'true_support':actual,
        'exact_support':all(result['selected_support'][key]==actual[key]
                            for key in actual),
        'false_nonlinear':not actual['r'] and result['nonlinear'],
        'r_error':abs(result['estimated']['r']-truth['r']),
        'D_error':abs(result['estimated']['D']-truth['D'])})
    return result


def aggregate(rows):
    return {'exact':sum(z['exact_support'] for z in rows),
            'nonlinear_detected':sum(z['nonlinear'] for z in rows),
            'false_nonlinear':sum(z['false_nonlinear'] for z in rows),
            'diffusion_detected':sum(z['selected_support']['D'] for z in rows),
            'linear_detected':sum(z['selected_support']['a'] for z in rows),
            'n':len(rows),
            'mean_r_abs_error':float(np.mean([z['r_error'] for z in rows])),
            'mean_D_abs_error':float(np.mean([z['D_error'] for z in rows]))}


def evaluate(seeds=range(2001,2041)):
    records=[]
    for seed in seeds:
        for world in WORLDS:
            for policy in POLICIES:
                records.append(check(seed,world,policy))
            if world=='quadratic_sensor':
                records.append(check(seed,world,'targeted_sparse','reference'))
    groups=[]
    for world in WORLDS:
        for policy in POLICIES:
            rr=[r for r in records if r['world']==world and
                r['policy']==policy and r['sensor_channel']=='primary']
            groups.append({'world':world,'policy':policy,
                           'channel':'primary',**aggregate(rr)})
    rr=[r for r in records if r['world']=='quadratic_sensor' and
        r['sensor_channel']=='reference']
    groups.append({'world':'quadratic_sensor','policy':'targeted_sparse',
                   'channel':'reference',**aggregate(rr)})
    return {'title':'Gate 008: nonlinear equilibrium breaking with +/- pulses',
        'status':'synthetic matched preparation experiment, not open PDE discovery',
        'design':{
            'N':N,'pairs_per_world':PAIRS,'split_pairs_per_half':PAIRS//2,
            'probe_pixel_rms':RMS,'max_pixel_displacement':PIXEL_CAP,
            'sensor_sd_unannounced_range':[.07,.09],
            'process_sd':.003,'z_per_half':Z,
            'frozen_seed_list':list(seeds),
            'candidate_library':'Laplacian, local linear restoration, cubic reaction',
            'identical_matched_equilibrium_preparation':True,
            'noise_variance_supplied_to_estimator':False,
            'true_coefficients_supplied_to_estimator':False},
        'groups':groups,'records':records,
        'limitations':[
            'Uniform +/-1 bulk states, not arbitrary Allen-Cahn domain interfaces',
            'Requires independent matched cloned equilibrium states for +/- pulses',
            'Finite candidate grammar provided, not unrestricted blind discovery',
            'Sparse pulse optimized for the possible cubic response, not true coefficients',
            'Two-half 3-SE criterion is heuristic, not familywise-calibrated',
            'Quadratic detector front end can imitate world nonlinearity',
            'Reference channel is a separately assumed trusted linear measurement',
            'No real physical data']}
    

def report(data):
    s=['# Gate 008 — Nonlinear equilibrium-breaking pulse test','','| World | Policy | Exact law support | Reaction detected | False reaction | Diffusion detected |',
       '|---|---|---:|---:|---:|---:|']
    for g in data['groups']:
        pol=g['policy']+(' (reference)' if g['channel']=='reference' else '')
        s.append(f"| {g['world']} | {pol} | {g['exact']}/{g['n']} | {g['nonlinear_detected']}/{g['n']} | {g['false_nonlinear']}/{g['n']} | {g['diffusion_detected']}/{g['n']} |")
    s+=['','Noise variance and true coefficients are hidden from fitter, but',
        'the candidate library and identical +/- equilibrium preparations',
        'are provided. The sparse pulse optimizes curvature information under',
        'a strict amplitude/energy budget; it does not use the true law.',
        'A nonlinear detector can still fake a nonlinear physical law.',
        'A trusted second sensor is additional experimental calibration.',
        'No novel universal theorem or open-grammar PDE discovery is claimed.','']
    return '\n'.join(s)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',default='results')
    p.add_argument('--quick',action='store_true')
    a=p.parse_args()
    result=evaluate(range(301,305) if a.quick else range(2001,2041))
    folder=Path(a.out)
    folder.mkdir(parents=True,exist_ok=True)
    (folder/'gate008.json').write_text(json.dumps(result,indent=2)+'\n')
    summary=report(result)
    (folder/'gate008.md').write_text(summary)
    print(summary,flush=True)


if __name__=='__main__':
    main()
