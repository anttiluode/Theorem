"""Theorem Gate 004 — temporal closed-loop identification of an unknown offset.

World: a Luotain2-inspired 64x64 time-evolving linear field with an unknown
single remote spatial link, including a no-link case.

KNOWN MODEL PRIOR TO LEARNER:
    A0(x) = 0.6*x + 0.1*sum(cardinal_neighbor(x))
    A_candidate(x) = A0(x) + 0.1*(shift(x,dy,dx)-x)
    dy,dx can be ANY of the 4096 periodic offsets; (0,0) means no link.
KNOWN: local baseline, positive link strength 0.1, periodic convolution
structure, i.i.d. measurement variance R.
HIDDEN: true remote offset, whether there is a remote link, latent state.

At each step the learner observes y_t = x_t + eps_t, chooses u_t, and sees
y_{t+1} = A_true(x_t+u_t) + eta_t + eps_{t+1}. State is NOT reset. Passive
initial dynamics excite only one Fourier mode. All input actions have equal
L2 energy. No policy receives the true offset.

The cumulative score is the candidate-specific *known-R-corrected* negative
half squared error. This prevents the "smoother law looks better" trap due
to noise in y_t. This is NOT Luotain2's blind-IV candidate search, and
does not estimate R, coefficients or the local stencil.
"""
from __future__ import annotations
import json
from functools import lru_cache
from pathlib import Path
import numpy as np

N=64
SENSOR_STD=.01
PROCESS_STD=0.0
ACTION_NORM=.45
PASSIVE_STEPS=24
ACTIVE_STEPS=16
CHECKPOINTS=(0,2,4,8,16)
CARD=((1,0),(-1,0),(0,1),(0,-1))
FREQUENCIES=tuple((ky,kx) for ky in range(10)
                  for kx in range(10) if ky or kx)
POLICIES=("passive","targeted","random_fourier","white","fixed_fourier")


@lru_cache(None)
def grid():
    return np.indices((N,N))


@lru_cache(None)
def candidate_phases():
    Y,X=grid()
    yy,xx=Y.ravel(),X.ravel()
    return np.exp(-2j*np.pi*np.asarray(
        [ky*yy+kx*xx for ky,kx in FREQUENCIES])/N)


@lru_cache(None)
def candidate_noise_norms():
    # Squared convolution-kernel norm for every candidate.
    # Null model A0 = .6 self + .1*4 cardinal => .40.
    # Remote model = .5 self + .1*4 cardinal + .1 shift => .30.
    # A candidate overlapping a cardinal neighbor merges with it => .32.
    kernel=np.full((N,N),.30,dtype=float)
    kernel[0,0]=.40
    for dy,dx in CARD:kernel[dy%N,dx%N]=.32
    return kernel


def local_base(v):
    return .6*v+.1*sum(np.roll(v,(dy,dx),(0,1)) for dy,dx in CARD)


def simulator_step(v,remote):
    """Never called by the learning strategy; only by the simulator."""
    return local_base(v)+.1*(np.roll(v,remote,(0,1))-v)


def update_scores(previous,observed_input,observed_next,
                  assumed_sensor_std=SENSOR_STD):
    """All 4096 candidate offsets evaluated in one FFT correlation.

    Negative half-squared error difference (candidate minus no-link):
        .1 * (cross_c - cross_0) - .01 * (auto_0 - auto_c).
    To correct known input measurement noise add
        +(R/2)*N²*(||A_candidate||²-||A0||²).
    This is the exact expected risk correction for i.i.d. errors
    independent across measurement instants; not an IV claim.
    """
    x=np.asarray(observed_input,float)
    y=np.asarray(observed_next,float)
    if x.shape!=(N,N) or y.shape!=(N,N):
        raise ValueError("Observed input/output must be N by N")
    if assumed_sensor_std<0 or not np.isfinite(assumed_sensor_std):
        raise ValueError("Noise calibration must be finite nonnegative")
    r=y-local_base(x)
    F=np.fft.fft2(x)
    cross=np.fft.ifft2(np.fft.fft2(r)*np.conj(F)).real
    auto=np.fft.ifft2(abs(F)**2).real
    increment=.1*(cross-cross[0,0])-.01*(auto[0,0]-auto)
    corrected=.5*assumed_sensor_std**2*N*N*(candidate_noise_norms()-.40)
    score=np.asarray(previous,float)+increment+corrected
    score[0,0]=0.  # no-link hypothesis has zero relative discrepancy
    return score


def choose_frequency(scores):
    """Inspect best 24 scored candidates and maximize phase disagreement.

    Candidate positions come ONLY from previous observed data. The ground
    truth and any unobserved physical state are not passed to this function.
    We use a 99-mode feasible probe library, not a hidden oracle frequency.
    """
    flattened=np.asarray(scores,float).ravel()
    top=np.argpartition(flattened,-24)[-24:]
    top=top[np.argsort(flattened[top])]
    p=candidate_phases()[:,top]
    disagreement=1-abs(np.mean(p,axis=1))**2
    return FREQUENCIES[int(np.argmax(disagreement))]


def choose_action(policy,scores,rng):
    if policy=="passive":
        return np.zeros((N,N)),None
    if policy=="targeted":
        ky,kx=choose_frequency(scores)
    elif policy=="random_fourier":
        ky,kx=FREQUENCIES[int(rng.integers(len(FREQUENCIES)))]
    elif policy=="fixed_fourier":
        ky,kx=(1,2)
    elif policy=="white":
        v=rng.normal(size=(N,N))
        return ACTION_NORM*v/np.linalg.norm(v),None
    else:
        raise ValueError(policy)
    Y,X=grid()
    v=np.cos(2*np.pi*(ky*Y+kx*X)/N+rng.uniform(-np.pi,np.pi))
    return ACTION_NORM*v/np.linalg.norm(v),(int(ky),int(kx))


def hidden_offset(seed):
    """Truth is created in the world, separate from learner/decision code."""
    rng=np.random.default_rng(seed+19874)
    excluded={(0,0)}|{(dy%N,dx%N) for dy,dx in CARD}
    while True:
        offset=(int(rng.integers(N)),int(rng.integers(N)))
        if offset not in excluded:
            return offset


def run_case(seed,policy,remote=None,correct_R=True,process_std=PROCESS_STD):
    if remote is None:
        remote=hidden_offset(seed)
    if policy not in POLICIES:
        raise ValueError(policy)
    if process_std<0:
        raise ValueError("process_std must be nonnegative")
    truth=(int(remote[0])%N,int(remote[1])%N)
    environment=np.random.default_rng(100000+seed)
    policy_rng=np.random.default_rng(200000+seed)
    Y,X=grid()
    phase=environment.uniform(-np.pi,np.pi)
    state=np.cos(2*np.pi*(Y+2*X)/N+phase)
    state=.25*state/state.std()

    # Sensor/process innovations are generated independently of and shared
    # between policies. Once actions start, latent states may diverge.
    measured_noise=environment.normal(
        size=(PASSIVE_STEPS+ACTIVE_STEPS+1,N,N))*SENSOR_STD
    innovations=environment.normal(
        size=(PASSIVE_STEPS+ACTIVE_STEPS,N,N))*process_std
    measurement=state+measured_noise[0]
    scores=np.zeros((N,N))
    checkpoints={}
    action_modes=[]
    worst_action_norm_error=0.
    for t in range(PASSIVE_STEPS+ACTIVE_STEPS):
        active=t>=PASSIVE_STEPS
        policy_now=policy if active else "passive"
        u,mode=choose_action(policy_now,scores,policy_rng)
        if active and policy!="passive":
            worst_action_norm_error=max(
                worst_action_norm_error,abs(np.linalg.norm(u)-ACTION_NORM))
        if mode is not None:action_modes.append(list(mode))
        next_state=simulator_step(state+u,truth)+innovations[t]
        next_measurement=next_state+measured_noise[t+1]
        scores=update_scores(
            scores,measurement+u,next_measurement,
            SENSOR_STD if correct_R else 0.)
        state=next_state
        measurement=next_measurement
        count=max(0,t+1-PASSIVE_STEPS)
        if t+1==PASSIVE_STEPS or (active and count in CHECKPOINTS):
            chosen=np.unravel_index(np.argmax(scores),scores.shape)
            checkpoints[str(count)]={
                "chosen_offset":[int(chosen[0]),int(chosen[1])],
                "correct":bool(chosen==truth),
                "true_rank":int(np.sum(scores>scores[truth]))+1,
                "best_advantage_over_null":float(np.max(scores)),
                "truth_advantage_over_null":float(scores[truth]),
            }
    return {
        "seed":int(seed),
        "policy":policy,
        "true_offset":[int(x) for x in truth],
        "null":truth==(0,0),
        "known_R_corrected":bool(correct_R),
        "process_std":float(process_std),
        "sensor_std":SENSOR_STD,
        "action_l2_norm":ACTION_NORM,
        "max_action_norm_error":float(worst_action_norm_error),
        "passive_steps":PASSIVE_STEPS,
        "active_steps":ACTIVE_STEPS,
        "checkpoints":checkpoints,
        "chosen_probe_modes":action_modes,
        "correct_final":checkpoints[str(ACTIVE_STEPS)]["correct"]
    }


def aggregate(rows):
    output={}
    keys=(str(x) for x in CHECKPOINTS)
    for k in keys:
        output[k]={
          "correct":sum(r["checkpoints"][k]["correct"] for r in rows),
          "total":len(rows),
          "median_true_rank":float(np.median([
              r["checkpoints"][k]["true_rank"] for r in rows]))
        }
    return output


def frozen_suite(remote_seeds=range(901,941),
                 null_seeds=range(1901,1941),
                 process_seeds=range(1101,1121)):
    records=[]
    for seed in remote_seeds:
        for kind in POLICIES:
            records.append(run_case(seed,kind))
    for seed in null_seeds:
        for kind in POLICIES:
            records.append(run_case(seed,kind,remote=(0,0)))
        for kind in ("targeted","white"):
            records.append(run_case(
                seed,kind,remote=(0,0),correct_R=False))
    process_records=[]
    for std in (0.,.0002,.001,.003):
        for seed in process_seeds:
            for kind in ("passive","targeted","white"):
                process_records.append(
                    run_case(seed,kind,process_std=std))
    results={}
    for group in ("remote","null"):
        for kind in POLICIES:
            rs=[r for r in records if
                ("null" if r["null"] else "remote")==group and
                r["policy"]==kind and r["known_R_corrected"]]
            results[f"{group}:{kind}"]=aggregate(rs)
    for kind in ("targeted","white"):
        rs=[r for r in records if r["null"] and
            r["policy"]==kind and not r["known_R_corrected"]]
        results[f"null:{kind}:uncorrected_R"]=aggregate(rs)
    process={}
    for std in (0.,.0002,.001,.003):
        for kind in ("passive","targeted","white"):
            rs=[r for r in process_records
                if r["process_std"]==std and r["policy"]==kind]
            process[f"{std:g}:{kind}"]=aggregate(rs)

    return {
        "name":"Theorem Gate 004: feedback-selected excitation in one continuous noisy world",
        "status":"simulated evaluation; all structural limits apply",
        "fixed_design":{
          "N":N,"passive_steps":PASSIVE_STEPS,
          "active_steps":ACTIVE_STEPS,"max_active_probe_l2":ACTION_NORM,
          "sensor_std":SENSOR_STD,
          "local_baseline_known":True,
          "remote_positive_coefficient_known":0.1,
          "candidate_spatial_offsets":N*N,
          "null_is_offset_0_0":True,
          "frequency_candidates":len(FREQUENCIES),
          "top_scored_offsets_used_for_adaptive_frequency":24,
          "policy_receives_hidden_truth":False,
          "same_measurement_reused_as_next_step_input":True,
          "same_exogenous_noise_across_policies":True,
          "no_state_resets_within_trajectories":True,
          "main_remote_seeds":list(remote_seeds),
          "main_null_seeds":list(null_seeds),
          "process_sweep_seeds":list(process_seeds),
          "process_noise_std":(0.,.0002,.001,.003)
        },
        "aggregate":results,
        "process_sweep":process,
        "remote_and_null_rows":records,
        "process_rows":process_records,
        "limits":[
          "Local stencil and coefficient 0.1 are provided to learner; only offset and null-vs-link are unknown.",
          "This is a 64x64 one-lag spatial convolution model, not Luotain2's full open candidate grammar.",
          "The agent can inject externally controlled patterns before state transition, although it cannot reset the state.",
          "The initial passive field is deliberately a single Fourier mode; exact aliases are expected.",
          "Sensor errors are i.i.d. Gaussian with exactly known variance; no correlated noise or R estimation.",
          "Comparing 4096 candidates without a formal multiple-testing confidence interval: top1 is not a calibrated p-value.",
          "Active targeted Fourier probes are restricted to 99 low-to-mid modes and select among 24 highest-scored offsets.",
          "White-noise probing is a strong baseline and may be at least as good as targeted probing.",
          "Synthetic remote offsets and process levels are simulator-defined, not physical ground truth about the brain."
        ]
    }


def markdown(result):
    a=[
        "# Gate 004 — Can the learner wake up a dark, ongoing world?",
        "",
        "An initial sinusoidal state evolves continuously; the agent cannot",
        "reset it. All candidate spatial offsets and the null model compete",
        "using known-R-corrected prediction risk. The learner is given the",
        "local stencil and remote coefficient +0.1, NOT the remote address.",
        "",
        "| Test | Policy | Passive exact | After 2 actions | After 4 | After 8 | After 16 |",
        "|---|---|---:|---:|---:|---:|---:|"
    ]
    for group in ("remote","null"):
        for kind in POLICIES:
            vals=result["aggregate"][f"{group}:{kind}"]
            def score(k):
                v=vals[str(k)]
                return f"{v['correct']}/{v['total']}"
            a.append(f"| {group} | {kind} | {score(0)} | {score(2)} | {score(4)} | {score(8)} | {score(16)} |")
    for kind in ("targeted","white"):
        vals=result["aggregate"][f"null:{kind}:uncorrected_R"]
        def score(k):return f"{vals[str(k)]['correct']}/{vals[str(k)]['total']}"
        a.append(f"| null, incorrectly set R=0 | {kind} | {score(0)} | {score(2)} | {score(4)} | {score(8)} | {score(16)} |")
    a += ["","## Disturbance sweep (new independent seeds)", "",
          "| Process noise SD | Policy | Passive exact | After 4 | After 8 |",
          "|---:|---|---:|---:|---:|"]
    for std in (0.,.0002,.001,.003):
        for kind in ("passive","targeted","white"):
            r=result["process_sweep"][f"{std:g}:{kind}"]
            a.append(f"| {std:g} | {kind} | {r['0']['correct']}/{r['0']['total']} | {r['4']['correct']}/{r['4']['total']} | {r['8']['correct']}/{r['8']['total']} |")
    a += ["",
          "## Mechanism and limitations",
          "",
          "Observational ambiguity is exact on the single passive Fourier mode:",
          "64 periodic shifts yield the same complex transfer on that mode.",
          "The corrected score removes expected candidate-specific sensor",
          "noise penalties. Without this correction, the null model is",
          "systematically beaten by fake smoothing links under active probing.",
          "",
          "Targeted probes are derived from the top 24 *learned* offset scores;",
          "they do not see the true shift. Compare against broadband white",
          "noise without dismissing a tie or white-noise victory.",
          "",
          "This is narrow classical convolutional experiment design with known",
          "local stencil and known coupling strength. It is NOT an unknown",
          "multi-lag nonlinear operator, an IV/WAIVES theorem, a natural sensor",
          "result, or evidence for a new law of neural or language processing.",
          ""]
    return "\n".join(a)


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="results")
    p.add_argument("--quick",action="store_true")
    opts=p.parse_args()
    out=(frozen_suite(range(801,805),range(1801,1805),range(701,705))
         if opts.quick else frozen_suite())
    folder=Path(opts.out);folder.mkdir(exist_ok=True,parents=True)
    (folder/"gate004.json").write_text(json.dumps(out,indent=2)+"\n")
    report=markdown(out)
    (folder/"gate004.md").write_text(report)
    print(report,flush=True)


if __name__=="__main__":
    main()
