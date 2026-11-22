"""Theorem Gate 005: privately randomized active-IV for UNKNOWN spatial stencil.

The estimator is given known 64x64 periodic linear shift invariance and the
additive actuation port x_t+u_t. It is NOT given the kernel, local coefficients,
remote position/strength, or sensor-noise variance. A fresh independent random
sign on every action shape makes u_t mean-zero conditional on past readings.
Cross U_t with Y_(t+1) to estimate A: input-state/sensor errors disappear in
expectation; adaptive deterministic feedback alone is NOT a valid instrument.

Controls: null remote, unknown R, broad vs 2-phase vs fixed smooth, placebo
misaligned intervention channel, split-sample confirmation. No claims of
fully model-free nonlinear WAIVES identification or superiority to white noise.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np

N=64; M=N*N; ACTION=.70; PASSIVE=16; ACTIVE=48
MODES=tuple((i,j) for i in range(1,12) for j in range(1,12))


def make_kernel(rng, with_remote, remote_range=(.065,.11)):
    h=np.zeros((N,N))
    h[0,0]=rng.uniform(.40,.48)
    for d in ((1,0),(-1,0),(0,1),(0,-1)):
        h[d]=rng.uniform(.06,.09)
    truth=None
    if with_remote:
        while True:
            d=tuple(int(v) for v in rng.integers(N,size=2))
            if min(d[0],N-d[0])>=5 or min(d[1],N-d[1])>=5:
                break
        truth=d
        h[d]=rng.uniform(*remote_range)*rng.choice((-1,1))
    # Restrict the simulator to stable impulse response norms.
    if np.sum(np.abs(h))>=.96: h*=.95/np.sum(abs(h))
    return h,truth


def motion(x,H):
    return np.fft.ifft2(np.fft.fft2(x)*H).real


def white(rng):
    v=rng.normal(size=(N,N));return v/np.linalg.norm(v)


def sinusoid(rng,k):
    Y,X=np.indices((N,N))
    v=np.cos(2*np.pi*(k[0]*Y+k[1]*X)/N+rng.uniform(-np.pi,np.pi))
    return v/np.linalg.norm(v)


def pick_frequency(h):
    # Select the first two remote candidate supports suggested by noisy
    # private-kick data, excluding local support. NOT the generator truth.
    a=np.abs(h).copy()
    a[:4,:4]=0;a[-3:,:4]=0;a[:4,-3:]=0;a[-3:,-3:]=0
    flat=np.argpartition(a.ravel(),-2)[-2:]
    d1,d2=(np.unravel_index(int(q),a.shape) for q in flat)
    # A chosen sinusoid is most informative where the two possible shifts
    # have contrasting phase; only modest-frequency feasible library.
    gaps=[abs(np.exp(-2j*np.pi*(k[0]*d1[0]+k[1]*d1[1])/N)-
              np.exp(-2j*np.pi*(k[0]*d2[0]+k[1]*d2[1])/N)) for k in MODES]
    return MODES[int(np.argmax(gaps))]


def iv_estimate(actions, outputs):
    """Noise-scale-free Fourier IV estimate of full kernel.

    Each U_t has independent private sign, even after shape selection.
    E[conj(U_t)Y_{t+1}|history] = |U_t|^2 * H, because U_t is
    orthogonal to latent X_t and future observation/process noise.
    """
    if len(actions)<2 or len(actions)!=len(outputs):
        raise ValueError('Need >=2 matched private kicks and following observations')
    num=np.zeros((N,N),complex);den=np.zeros((N,N))
    for u,y in zip(actions,outputs):
        U=np.fft.fft2(u);Y=np.fft.fft2(y)
        num+=np.conj(U)*Y;den+=abs(U)**2
    return kernel_from_spectrum(num,den)


def kernel_from_spectrum(num,den):
    valid=den>1e-8
    H=np.zeros((N,N),complex)
    H[valid]=num[valid]/den[valid]
    return np.fft.ifft2(H).real,float(valid.mean())


def noise_floor(h):
    # Empirical robust uncertainty. Uses that only a tiny fraction of
    # spatial shifts are true (sparse convolution prior). No R given.
    local=np.ones((N,N),bool)
    for dy in range(-3,4):
        for dx in range(-3,4):local[dy%N,dx%N]=False
    a=h[local];med=np.median(a)
    return max(1e-12,1.4826*float(np.median(abs(a-med))))


def decide(train,holdout, z=3.4):
    """Select on first independent kicks; confirm signed coefficient later.

    Empirical MAD threshold is heuristic: spatial coefficients are dependent.
    Neither Bonferroni FWER nor asymptotic normality is asserted.
    """
    s1=noise_floor(train);s2=noise_floor(holdout)
    c=np.abs(train).copy()
    for dy in range(-3,4):
        for dx in range(-3,4):c[dy%N,dx%N]=0
    pos=np.unravel_index(np.argmax(c),c.shape)
    accepted=(abs(train[pos])>z*s1 and
              abs(holdout[pos])>z*s2 and
              train[pos]*holdout[pos]>0)
    return (int(pos[0]),int(pos[1])) if accepted else None,{
        'train_weight':float(train[pos]), 'holdout_weight':float(holdout[pos]),
        'train_noise_proxy':s1,'holdout_noise_proxy':s2,
        'candidate':[int(x) for x in pos], 'accepted':bool(accepted)}


def run_case(seed,policy,has_remote=True,sensor_std=None,stress=False):
    if policy not in ('white','two_phase','fourier_only','passive','placebo','feedback'):
        raise ValueError(policy)
    rng_world=np.random.default_rng(seed+50000)
    rng_act=np.random.default_rng(seed+100000)
    h,truth=make_kernel(rng_world,has_remote,remote_range=(.045,.075) if stress else (.065,.11))
    H=np.fft.fft2(h)
    sd=float(rng_world.uniform(.012,.022) if stress else rng_world.uniform(.006,.014)) if sensor_std is None else float(sensor_std)
    act=.45 if stress else ACTION
    # Start on one passive spatial mode, just as Gate 004 did.
    YY,XX=np.indices((N,N));p=rng_world.uniform(-np.pi,np.pi)
    x=.25*np.cos(2*np.pi*(YY+2*XX)/N+p)
    sensor=rng_world.normal(0,sd,size=(PASSIVE+ACTIVE+1,N,N))
    process=rng_world.normal(0,.0005,size=(PASSIVE+ACTIVE,N,N))
    y=x+sensor[0]
    # Distinct source of private post-decision signs for intervention IV.
    kicks=[];nexts=[];modes=[];checkpoints={}
    sum_cross=np.zeros((N,N),complex)
    sum_power=np.zeros((N,N))
    prefix_cross=[];prefix_power=[]
    for t in range(PASSIVE+ACTIVE):
        u=np.zeros((N,N))
        if t>=PASSIVE and policy!='passive':
            k=t-PASSIVE
            if policy=='feedback':
                v=-y/max(np.linalg.norm(y),1e-12)
            elif policy in ('white','placebo'):
                v=white(rng_act)
            elif policy=='fourier_only':
                v=sinusoid(rng_act,MODES[int(rng_act.integers(len(MODES)))])
            else:
                if k<8:
                    v=white(rng_act)
                else:
                    # Fix a shortlist using ONLY earlier measured responses;
                    # new private sign is drawn AFTER choosing the shape.
                    previous,_=kernel_from_spectrum(sum_cross,sum_power)
                    freq=pick_frequency(previous)
                    modes.append(list(freq))
                    v=(.75*white(rng_act)+.25*sinusoid(rng_act,freq))
                    v/=np.linalg.norm(v)
            sign=(1 if policy=='feedback' else rng_act.choice([-1,1]))
            u=sign*act*v
        xnext=motion(x+u,H)+process[t]
        ynext=xnext+sensor[t+1]
        if t>=PASSIVE and policy!='passive':
            if policy=='placebo':
                # Negative control: measurement paired with a wholly
                # independent never-applied kick, same amplitude.
                false_u=act*white(rng_act)*rng_act.choice([-1,1])
                kicks.append(false_u)
            else:
                kicks.append(u)
            nexts.append(ynext)
            inst=kicks[-1]
            F=np.fft.fft2(inst)
            sum_cross+=np.conj(F)*np.fft.fft2(ynext)
            sum_power+=abs(F)**2
            prefix_cross.append(sum_cross.copy())
            prefix_power.append(sum_power.copy())
        x=xnext;y=ynext
        if len(kicks) in (12,16,24,32,48) and policy!='passive':
            m=len(kicks)//2
            h1,_=kernel_from_spectrum(prefix_cross[m-1],prefix_power[m-1])
            h2,_=kernel_from_spectrum(sum_cross-prefix_cross[m-1],sum_power-prefix_power[m-1])
            choice,_=decide(h1,h2)
            checkpoints[str(len(kicks))]={
                'chosen':list(choice) if choice else None,
                'correct':choice==truth if truth else choice is None}
    if not kicks:
        return {'seed':seed,'policy':policy,'truth':list(truth) if truth else None,
                'chosen':None,'correct':not has_remote,'sensor_sd_hidden':sd,
                'instrument_count':0}
    m=ACTIVE//2
    first,a=kernel_from_spectrum(prefix_cross[m-1],prefix_power[m-1])
    second,b=kernel_from_spectrum(sum_cross-prefix_cross[m-1],sum_power-prefix_power[m-1])
    chosen,stat=decide(first,second)
    return {'seed':seed,'policy':policy,'truth':list(truth) if truth else None,
            'chosen':list(chosen) if chosen else None,
            'correct':chosen==truth if truth else chosen is None,
            'false_link':truth is None and chosen is not None,
            'sensor_sd_hidden':sd, 'full_support_fitted':True,
            'first_spectral_fraction':a,'second_spectral_fraction':b,
            'evidence':stat, 'selected_frequencies':modes,
            'instrument_count':len(kicks),'checkpoints':checkpoints,'stress':stress,'action_l2':act,
            'local_fit_mae':float(np.mean([abs(first[d]-h[d]) for d in
                ((0,0),(1,0),(-1,0),(0,1),(0,-1))]))}


def evaluate(seeds=range(2101,2121),null_seeds=range(3101,3121),stress=False):
    rows=[]
    for has_remote,ss in ((True,seeds),(False,null_seeds)):
        for seed in ss:
            for policy in ('white','two_phase','fourier_only','feedback','placebo'):
                rows.append(run_case(seed,policy,has_remote,stress=stress))
    aggregate=[]
    for kind in ('remote','null'):
        for policy in ('white','two_phase','fourier_only','feedback','placebo'):
            sub=[r for r in rows if (r['truth'] is not None)==(kind=='remote')
                 and r['policy']==policy]
            aggregate.append({'world':kind,'policy':policy,'success':sum(r['correct'] for r in sub),
                              'n':len(sub),'false_link':sum(r['false_link'] for r in sub),
                              'mean_spectral_fraction':float(np.mean([r['first_spectral_fraction'] for r in sub])),
                              'mean_local_fit_mae':float(np.mean([r['local_fit_mae'] for r in sub])),
                              'correct_by_checkpoint':{k:sum(r['checkpoints'][str(k)]['correct'] for r in sub) for k in (12,16,24,32,48)}})
    return {'title':'Gate 005 randomized active IV, unknown coefficients and noise SD',
            'worlds':{'remote':len(seeds),'null':len(null_seeds)},'stress':stress,
            'design':{'grid':N,'passive':PASSIVE,'active':ACTIVE,'action_l2':(.45 if stress else ACTION),
                      'true_local_stencil_known_to_estimator':False,
                      'true_remote_strength_known_to_estimator':False,
                      'sensor_noise_sd_known_to_estimator':False,
                      'known_shift_invariance':True,
                      'known_local_radius_at_most_three_for_classification':True,
                      'sensor_sd_range_hidden_to_estimator':([.012,.022] if stress else [.006,.014]),
                      'remote_strength_magnitude_range_hidden_to_estimator':([.045,.075] if stress else [.065,.11]),
                      'sensor_noise_iid_in_simulator':True,
                      'private_random_action_sign':True,
                      'threshold':'split-halves, sign agreement and heuristic 3.4 MAD',
                      'feedback_control_is_invalid_instrument':True},
            'aggregate':aggregate,'rows':rows,
            'limits':['Not general nonlinear or multi-lag system identification',
                      'Sparse spatial convolution and exact actuation port are assumed',
                      'MAD threshold is heuristic, not calibrated FWER',
                      'A private random sign is essential for an adaptive probe to be valid as a naive IV under this model',
                      'No R estimated; IV avoids needing it under independence assumptions',
                      'Individual spatial estimates correlated and selected from many hypotheses',
                      'One continuous trajectory per seed, 48 controlled actions, simulated system',
                      'Two-phase superiority to white noise is NOT assumed']}


def report(out):
    lines=['# Gate 005 — Private dither as an instrument, unknown R', '',
           '| World | Policy | Exact chosen remote/no-link | False links |',
           '|---|---|---:|---:|']
    for regime,trial in out.items():
      for r in trial['aggregate']:
        lines.append(f"| {regime} / {r['world']} | {r['policy']} | {r['success']}/{r['n']} | {r['false_link']}/{r['n']} |")
    lines+=['', 'The estimator never receives the local kernel, remote offset or strength, or observation noise variance.',
            'It assumes linear shift-invariant dynamics, an additive action port, a sparse kernel, independent private kick signs, and independent sensor innovations.',
            'Spatial median absolute deviation is a heuristic threshold, not a validated family-wise false-link guarantee.',
            'White-noise and placebo controls are retained even when they outperform the targeted controller.', '']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser();p.add_argument('--quick',action='store_true');p.add_argument('--out',default='results');a=p.parse_args()
    if a.quick:
        out={'easy':evaluate(range(701,705),range(801,805)),
             'weak':evaluate(range(701,705),range(801,805),stress=True)}
    else:
        out={'easy':evaluate(range(2101,2121),range(3101,3121)),
             'weak':evaluate(range(2201,2241),range(3201,3241),stress=True)}
    path=Path(a.out);path.mkdir(parents=True,exist_ok=True)
    (path/'gate005.json').write_text(json.dumps(out,indent=2)+'\n')
    md=report(out);(path/'gate005.md').write_text(md);print(md,flush=True)

if __name__=='__main__':main()
