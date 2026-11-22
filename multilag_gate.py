"""Gate 007: distinguish internal dynamics from actuator/sensor bypass by causal lags.

Periodic linear world:
  x[t+1] = H*(x[t]+G*u[t])+process_error
  z[t+1] = K*z[t]+D*u[t]                 (optional detector bypass)
  y[t+1] = x[t+1]+z[t+1]+sensor_error
  sham[t+1] = z[t+1]+independent_sham_error.

For independent private white interventions, lag-l cross spectrum gives
R_l=H^l G + K^(l-1) D. Memoryless bypass K=0 affects R1 but not R2.
If D=0 and R1 invertible, H=R2/R1. With memoryless bypass H=R3/R2.
When K=H, the entire measured series is also consistent with a different
effective actuator, so detector bypass itself remains unidentifiable from
the main channel. A calibrated sham can provide extra evidence.

All are classical impulse-response/Markov-parameter identities, not new
physics or new mathematical theorems. The numerical ratio is ridge-stabilized.
"""
from __future__ import annotations
import numpy as np
from pathlib import Path
import json, argparse

N=64
SAMPLES=256
ACTION=.85
LAGS=(1,2,3)
LOCAL=((0,0),(1,0),(-1,0),(0,1),(0,-1))
BYPASS=(5,7)
CASES=("ideal","shifted_actuator","memoryless_bypass",
       "matched_ringing_bypass","different_ringing_bypass")
METHODS=("one_lag","propagate_1_to_2","propagate_2_to_3",
         "sham_corrected_1_to_2","sham_corrected_2_to_3","sham_sensor")


def kernel(rng,remote):
    h=np.zeros((N,N))
    h[0,0]=rng.uniform(.60,.65)
    for d in LOCAL[1:]:
        h[d]=rng.uniform(.035,.050)
    truth=None
    if remote:
        while True:
            d=tuple(int(x) for x in rng.integers(N,size=2))
            if min(d[0],N-d[0])>=9 and min(d[1],N-d[1])>=9:
                break
        truth=d
        h[d]=rng.choice([-1,1])*rng.uniform(.075,.095)
    # Explicit favorable identifiability assumption: stable, invertible H.
    assert h[0,0]-sum(abs(h[d]) for d in LOCAL[1:])-(abs(h[truth]) if truth else 0)>.30
    assert np.sum(abs(h))<.95
    return h,truth


def convolve(x,fft_kernel):
    return np.fft.ifft2(np.fft.fft2(x)*fft_kernel).real


def experiment(seed,case,remote=False,samples=SAMPLES):
    if case not in CASES:
        raise ValueError(case)
    world=np.random.default_rng(seed+65000)
    actions=np.random.default_rng(seed+75000)
    measure=np.random.default_rng(seed+85000)
    h,truth=kernel(world,remote)
    H=np.fft.fft2(h)
    b=np.zeros((N,N))
    b[BYPASS]=.58
    D=np.fft.fft2(b)
    x=.1*world.normal(size=(N,N))
    z=np.zeros((N,N))
    us=[];ys=[];shams=[];fake=[]
    for t in range(samples):
        u=actions.normal(size=(N,N))
        u=ACTION*u/np.linalg.norm(u)
        u*=actions.choice((-1,1))
        physical=np.roll(u,BYPASS,axis=(0,1)) if case=="shifted_actuator" else u
        x=convolve(x+physical,H)+.00025*world.normal(size=(N,N))
        if case=="memoryless_bypass":
            z=convolve(u,D)
        elif case=="matched_ringing_bypass":
            z=convolve(z,H)+convolve(u,D)
        elif case=="different_ringing_bypass":
            z=.55*z+convolve(u,D)
        else:
            z=np.zeros((N,N))
        y=x+z+.006*measure.normal(size=(N,N))
        sham=z+.004*measure.normal(size=(N,N))
        fake_sham=.004*measure.normal(size=(N,N))
        us.append(np.fft.fft2(u));ys.append(np.fft.fft2(y))
        shams.append(np.fft.fft2(sham));fake.append(np.fft.fft2(fake_sham))
    return h,truth,(np.stack(us),np.stack(ys),np.stack(shams),np.stack(fake))


def cross_transfer(U,Y,lag,start,end):
    if lag not in LAGS:
        raise ValueError("Only predeclared lags 1, 2, 3")
    if end-start<lag+12:
        raise ValueError("Insufficient actions")
    u=U[start:end-lag+1]
    v=Y[start+lag-1:end]
    return (np.conj(u)*v).sum(axis=0)/np.maximum((abs(u)**2).sum(axis=0),1e-12)


def ratio(numerator,denominator,ridge=.005):
    # Missing/zero-excitation bands must not produce NaN or fake certainty.
    # Keep the numerical floor even if median input-response power is zero.
    reg=max(1e-14,ridge*float(np.median(abs(denominator)**2)))
    return np.fft.ifft2(numerator*np.conj(denominator)/(
        abs(denominator)**2+reg)).real


def detect(first,second,multiplier=3.4):
    """Gate005 sign-confirmed spatial-MAD threshold; NOT FWER calibrated."""
    allowed=np.ones((N,N),bool)
    for dy in range(-3,4):
        for dx in range(-3,4):
            allowed[dy%N,dx%N]=False
    def sd(h):
        x=h[allowed]
        return max(1e-12,1.4826*np.median(abs(x-np.median(x))))
    scores=abs(first).copy();scores[~allowed]=0.
    pos=tuple(int(x) for x in np.unravel_index(np.argmax(scores),scores.shape))
    if (abs(first[pos])>multiplier*sd(first) and
        abs(second[pos])>multiplier*sd(second) and
        first[pos]*second[pos]>0):
        return pos
    return None


def measure_case(seed,case,remote=False,samples=SAMPLES):
    h,truth,(U,Y,SHAM,FAKE)=experiment(seed,case,remote,samples)
    results={}
    for method in METHODS+("fake_sham_corrected",):
        estimates=[]
        for start,end in ((0,samples//2),(samples//2,samples)):
            arr=(Y-SHAM if method.startswith("sham_corrected") else
                 SHAM if method=="sham_sensor" else
                 Y-FAKE if method=="fake_sham_corrected" else Y)
            R1=cross_transfer(U,arr,1,start,end)
            if method in ("one_lag","sham_sensor"):
                estimate=np.fft.ifft2(R1).real
            else:
                R2=cross_transfer(U,arr,2,start,end)
                if method in ("propagate_1_to_2","sham_corrected_1_to_2",
                              "fake_sham_corrected"):
                    estimate=ratio(R2,R1)
                else:
                    R3=cross_transfer(U,arr,3,start,end)
                    estimate=ratio(R3,R2)
            estimates.append(estimate)
        selected=detect(*estimates)
        is_correct=selected==truth if truth is not None else selected is None
        local_mae=float(np.mean([
            np.mean([abs(v[d]-h[d]) for d in LOCAL]) for v in estimates]))
        results[method]={
            "selected":list(selected) if selected is not None else None,
            "correct":bool(is_correct),
            "false_remote":bool(truth is None and selected is not None),
            "local_mae_physical":local_mae,
            "bypass_detected":bool(method=="sham_sensor" and selected==BYPASS),
        }
    return {"seed":int(seed),"case":case,
            "world":"remote" if remote else "null",
            "truth":list(truth) if truth is not None else None,
            "sensor_sd":.006,"sham_sd":.004,
            "n_interventions":samples,"action_l2":ACTION,"results":results}


def exact_certificates():
    rng=np.random.default_rng(159)
    h,_=kernel(rng,True)
    H=np.fft.fft2(h)
    g=np.zeros((N,N));g[BYPASS]=1;G=np.fft.fft2(g)
    d=np.zeros((N,N));d[BYPASS]=.58;D=np.fft.fft2(d)
    # Shifted actuator, ideal sensor: successive response ratio is H.
    R1=H*G;R2=H**2*G
    assert np.max(abs(R2/R1-H))<1e-12
    # Memoryless detector bypass: it enters only the first lag.
    R1b=H+D;R2b=H**2;R3b=H**3
    assert np.max(abs(R3b/R2b-H))<1e-12
    # Matching detector ringing K=H: H is recoverable,
    # but the entire impulse-response series admits different actuator G'.
    R1c=H+D;R2c=H**2+H*D;R3c=H**3+H**2*D
    Gprime=1+D/H
    assert np.max(abs(R2c/R1c-H))<1e-12
    assert np.max(abs(R3c/R2c-H))<1e-12
    assert np.max(abs(R3c-H**3*Gprime))<1e-12
    return {
        "minimum_abs_world_eigenvalue":float(np.min(abs(H))),
        "shifted_actuator_ratio_residual":float(np.max(abs(R2/R1-H))),
        "memoryless_bypass_late_ratio_residual":float(np.max(abs(R3b/R2b-H))),
        "matching_ringing_vs_effective_actuator_residual":float(
            np.max(abs(R3c-H**3*Gprime))),
        "conclusion":"R_l can identify H but need not identify the physical distribution of actuation and detector bypass."
    }


def sensor_mixing_certificate(n=8):
    """Finite-matrix proof of sensor basis ambiguity C H C^-1."""
    size=n*n
    H=np.zeros((size,size))
    for y in range(n):
        for x in range(n):
            a=y*n+x;H[a,a]=.55
            for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
                b=((y+dy)%n)*n+(x+dx)%n
                H[a,b]+=.08
    rng=np.random.default_rng(171)
    perm=rng.permutation(size)
    observed=H[np.ix_(perm,perm)]
    before=np.argwhere(abs(H-np.diag(np.diag(H)))>1e-12)
    after=np.argwhere(abs(observed-np.diag(np.diag(observed)))>1e-12)
    def far(edges):
        return int(sum(
            min(abs(a//n-b//n),n-abs(a//n-b//n))+
            min(abs(a%n-b%n),n-abs(a%n-b%n))>1 for a,b in edges))
    eig=float(np.max(abs(np.sort_complex(np.linalg.eigvals(H))-
                             np.sort_complex(np.linalg.eigvals(observed)))))
    x=rng.normal(size=size)
    response=float(np.max(abs((H@x)[perm]-observed@x[perm])))
    assert eig<1e-9 and response<1e-11
    return {
        "local_world_apparent_nonlocal_edges":far(before),
        "mixed_sensor_apparent_nonlocal_edges":far(after),
        "eigenvalue_disagreement":eig,
        "all_trajectories_equivalent_in_transformed_coordinates":response,
        "limit":"Unknown invertible sensor mixing C yields C H C^-1; a sham channel alone cannot identify C."
    }


def evaluate(remote_seeds=range(7101,7121),
             null_seeds=range(8101,8121),samples=SAMPLES):
    rows=[]
    for case in CASES:
        for remote,seeds in ((True,remote_seeds),(False,null_seeds)):
            for seed in seeds:
                rows.append(measure_case(seed,case,remote,samples))
    groups=[]
    for case in CASES:
        for method in METHODS+("fake_sham_corrected",):
            a=[r["results"][method] for r in rows
               if r["case"]==case and r["world"]=="remote"]
            b=[r["results"][method] for r in rows
               if r["case"]==case and r["world"]=="null"]
            groups.append({
                "case":case,"method":method,
                "exact_remote":sum(x["correct"] for x in a),
                "remote_total":len(a),
                "correct_null":sum(x["correct"] for x in b),
                "null_total":len(b),
                "false_null":sum(x["false_remote"] for x in b),
                "mean_local_mae_remote":float(np.mean(
                    [x["local_mae_physical"] for x in a])),
                "sham_detected_remote":sum(x["bypass_detected"] for x in a),
                "sham_detected_null":sum(x["bypass_detected"] for x in b),
            })
    return {
        "title":"Gate 007 — multi-lag causal response and sham channel",
        "design":{
            "grid":[N,N],"world_family":"stable invertible sparse periodic linear convolution",
            "one_world_per_run_without_reset":True,
            "actions_per_world":samples,
            "action_l2":ACTION,
            "per_pixel_sensor_sd":.006,
            "per_pixel_sham_sd":.004,
            "independent_private_actions":True,
            "known_to_estimator":"command times, full-field sensor readings, optional sham readout",
            "hidden_from_estimator":"world H, actuator G, feedthrough D and ringing K, link address and sign, sensor R",
            "methods":"one-lag, R2/R1, R3/R2, correctly wired sham subtraction and fake sham control",
            "ridge_fraction_of_denominator_median_power":.005,
            "selection":"3.4 spatial MAD + same-sign in two non-overlapping windows; not FWER calibrated",
            "remote_seeds":list(remote_seeds),"null_seeds":list(null_seeds)
        },
        "exact_proofs":exact_certificates(),
        "mixed_sensor_basis":sensor_mixing_certificate(),
        "groups":groups,"rows":rows,
        "limitations":[
            "Ideal full-field periodic linear dynamics; stable invertible operator selected to permit ratios",
            "Finite noisy impulse ratios can be ill-conditioned even where exact ratios are identifiable",
            "Sham exactly measures bypass with additive independent measurement noise; real calibration could fail",
            "The two time windows share an evolving state; their errors need not be independent",
            "Remote link detector uses heuristic spatial MAD threshold and is not a corrected p-value",
            "Spatial mixing certificate is exact finite linear algebra, not learned blind",
            "No physical EEG source or universal identifiability theorem claimed"
        ]
    }


def markdown(data):
    names={"one_lag":"first echo",
           "propagate_1_to_2":"R2/R1",
           "propagate_2_to_3":"R3/R2",
           "sham_corrected_1_to_2":"sham-subtracted R2/R1",
           "sham_corrected_2_to_3":"sham-subtracted R3/R2",
           "sham_sensor":"sham channel alone",
           "fake_sham_corrected":"fake-sham R2/R1"}
    lines=[
        "# Gate 007 — Can later echoes reveal which part of the instrument lied?",
        "",
        "| World/port condition | Method | Exact remote | No-link refused | False remote in null |",
        "|---|---|---:|---:|---:|"]
    for r in data["groups"]:
        lines.append(
            f"| {r['case']} | {names[r['method']]} | "
            f"{r['exact_remote']}/{r['remote_total']} | "
            f"{r['correct_null']}/{r['null_total']} | "
            f"{r['false_null']}/{r['null_total']} |")
    lines += [
        "",
        "A calibrated sham measures detector bypass z without latent world x.",
        "A fake independent sham is the negative control, NOT a correction.",
        "All counts are finite-sample synthetic results using favorable stable H.",
        "Ringing bypass may mimic an alternative actuator at every lag.",
        "Uncalibrated noncommuting sensor mixing yields C H C^-1 even with exact lags.",
        "No new theorem or actual head/cable/neural anatomical source classification.",
        ""]
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="results")
    p.add_argument("--quick",action="store_true")
    a=p.parse_args()
    out=(evaluate(range(701,704),range(801,804),128) if a.quick else evaluate())
    path=Path(a.out);path.mkdir(parents=True,exist_ok=True)
    (path/"gate007.json").write_text(json.dumps(out,indent=2)+"\n")
    m=markdown(out)
    (path/"gate007.md").write_text(m)
    print(m,flush=True)


if __name__=="__main__":
    main()
