"""Gate 002: exact Fourier blind/bright modes of Luotain2's spatial wormhole.

Source law: anttiluode/Luotain2/luotain2/worlds.py, make_world("wormhole")
  y = 0.5*x + 0.1*(4 cardinal neighbors) + 0.1*shift(x,+17,-9)
Alternative H0 (declared, not a recovered fitted hypothesis):
  y = 0.6*x + 0.1*(4 cardinal neighbors).
The difference D = 0.1*(shift(+17,-9)-identity).

For Fourier mode (ky,kx), D's gain magnitude is exactly
  0.2 * |sin(pi*(17*ky - 9*kx)/64)|.
Therefore phase-aligned Fourier modes are completely blind to the
remote link even with arbitrarily strong amplitude, and opposite-phase
modes are optimal at equal Euclidean energy. This is the standard
Fourier-shift identity, not a newly discovered theorem.

The experiment is a supplied-alternative A-versus-B discrimination task
with Gaussian sensor noise. It is NOT blind support discovery or WAIVES.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from math import erf,sqrt


N=64
DY,DX=17,-9
COEF=.1
BUDGET=.60
SENSOR_SD=.04


def shift(x,dy,dx):
    return np.roll(x,(dy,dx),axis=(0,1))


def true_wormhole(x):
    card=sum(shift(x,dy,dx) for dy,dx in
             ((1,0),(-1,0),(0,1),(0,-1)))
    return .5*x+.1*card+.1*shift(x,DY,DX)


def missing_link_alternative(x):
    card=sum(shift(x,dy,dx) for dy,dx in
             ((1,0),(-1,0),(0,1),(0,-1)))
    return .6*x+.1*card


def difference(x):
    return true_wormhole(x)-missing_link_alternative(x)


def gain(ky,kx,n=N):
    return 2*COEF*abs(np.sin(np.pi*(DY*ky+DX*kx)/n))


def candidate_fourier_mode(ky,kx,n=N):
    y,x=np.indices((n,n))
    f=np.cos(2*np.pi*(ky*y+kx*x)/n)
    return f/np.linalg.norm(f)


def special_modes(n=N):
    # Predefine a smooth nonconstant near-null mode (ky=1,kx=2):
    # 17*1-9*2=-1, so a long-range shift barely changes it.
    near=(1,2)
    # Nonconstant exactly dark mode (ky=9,kx=17): dot(offset,k)=0.
    exact=(9,17)
    # Opposite-phase mode: dot(offset,k) = -288 = 32 mod 64.
    bright=(0,32)
    assert gain(*exact,n)<1e-14
    assert abs(gain(*bright,n)-.2)<1e-12
    return {"near_dark":near,"exact_dark":exact,"bright":bright}


def direction(which,seed):
    modes=special_modes()
    if which in modes:return candidate_fourier_mode(*modes[which])
    if which=="white":
        v=np.random.default_rng(seed).standard_normal((N,N))
        return v/np.linalg.norm(v)
    if which=="smooth":
        # Low-pass random image constructed without inspecting signal.
        rng=np.random.default_rng(seed)
        a=np.fft.fftfreq(N)*N
        KY,KX=np.meshgrid(a,a,indexing="ij")
        spectrum=np.exp(-(KY*KY+KX*KX)/(2*3**2))
        x=np.fft.ifft2(spectrum*np.fft.fft2(rng.standard_normal((N,N)))).real
        return x/np.linalg.norm(x)
    raise KeyError(which)


def response_separation(v):
    return float(BUDGET*np.linalg.norm(difference(v)))


def theoretical_accuracy(separation):
    return .5*(1+erf(separation/(2*SENSOR_SD*sqrt(2))))


def simulate_one(separation,rng,n_trials):
    if separation<1e-13:
        return float(np.mean(rng.random(n_trials)<.5))
    return float(np.mean(rng.standard_normal(n_trials)>
                         -separation/(2*SENSOR_SD)))


def mode_spectrum(n=N):
    ky,kx=np.indices((n,n))
    g=2*COEF*np.abs(np.sin(np.pi*(DY*ky+DX*kx)/n))
    # Tolerance must reflect exactly equal integer phase indices.
    phase_mod=(DY*ky+DX*kx)%n
    return {
       "n_fourier_modes":n*n,
       "exact_dark_modes":int(np.sum(phase_mod==0)),
       "maximal_bright_modes":int(np.sum(phase_mod==n//2)),
       "maximum_gain":float(g.max()),
       "example_near_dark_gain":gain(1,2,n),
       "example_exact_dark_gain":gain(9,17,n),
       "example_bright_gain":gain(0,32,n),
    }


def experiment(seeds=range(701,731),trials=3000):
    catalog=("exact_dark","near_dark","smooth","white","bright")
    results={}
    for seed in seeds:
        rng=np.random.default_rng(seed+30000)
        for k in catalog:
            v=direction(k,seed)
            sep=response_separation(v)
            results.setdefault(k,[]).append({
               "seed":int(seed),
               "separation":sep,
               "power":float(np.sum(v*v)),
               "predicted_accuracy":theoretical_accuracy(sep),
               "measured_accuracy":simulate_one(sep,rng,trials)})
    groups={}
    for k,rows in results.items():
        groups[k]={
         "mean_output_separation":float(np.mean([r["separation"] for r in rows])),
         "mean_squared_output_separation":float(np.mean([r["separation"]**2 for r in rows])),
         "predicted_accuracy":float(np.mean([r["predicted_accuracy"] for r in rows])),
         "empirical_accuracy":float(np.mean([r["measured_accuracy"] for r in rows])),
         "max_input_energy_mismatch":float(max(abs(r["power"]-1) for r in rows))}
    return {
      "title":"Gate 002 — The actual (+17,-9) wormhole link has Fourier blind ridges",
      "status":"known Fourier shift identity, simulated noisy two-hypothesis discrimination",
      "source_law":"anttiluode/Luotain2/luotain2/worlds.py wormhole",
      "hypotheses":{
        "A":"true wormhole: .5 self + .1 four-neighbor + .1 shift(+17,-9)",
        "B":"constructed local substitute: .6 self + .1 four-neighbor",
        "important":"B is NOT claimed to be Luotain2's previously recovered delayed-AR false law"},
      "noise_sd_absolute":SENSOR_SD,"input_perturbation_norm":BUDGET,
      "frozen_seeds":list(seeds),"trials_per_seed":trials,
      "spectrum":mode_spectrum(),
      "groups":groups,"per_seed":results,
      "limits":[
         "Both candidate laws supplied to the discriminator; no blind law recovery",
         "Single-step field response, not multi-step dynamical system identification",
         "Gaussian output sensor noise with known scale, no corrupted input regressors",
         "The simple competitor is local, not the previously fitted time-delayed shortcut",
         "All probes are synthetic field perturbations that cannot necessarily be physically applied",
         "Fourier-shift phase nulls are established mathematics"]
    }


def report(data):
    o=[
      "# Gate 002 — The wormhole has dark Fourier ridges",
      "",
      "The actual Luotain2 wormhole shift (+17,-9) is contrasted against",
      "an explicitly specified local-only replacement, not an estimated",
      "false AR law. Every probe has equal energy and independent noise.",
      "",
      "| Field probe | Mean signal separation | Predicted mechanism-choice accuracy | Measured accuracy |",
      "|---|---:|---:|---:|"]
    for k,g in data["groups"].items():
        o.append(f"| {k} | {g['mean_output_separation']:.5f} | {g['predicted_accuracy']:.3f} | {g['empirical_accuracy']:.3f} |")
    s=data["spectrum"]
    o+=["",
       f"Of {s['n_fourier_modes']} Fourier coordinates, {s['exact_dark_modes']}",
       f"are exactly dark to this link-vs-local contrast and {s['maximal_bright_modes']}",
       "are maximally bright. A highly structured field can be dark;",
       "large amplitude alone does not distinguish the two candidates.",
       "",
       "For spatial Fourier index (ky,kx), the transfer difference is",
       "0.1*(exp(-i*2*pi*(17*ky-9*kx)/64)-1). Its magnitude",
       "is 0.2*abs(sin(pi*(17*ky-9*kx)/64)).",
       "",
       "Known Fourier-shift identity; NO new theorem; NO blinded",
       "discovery of the true (+17,-9) term; NO passive EEG localization.",
       ""]
    return "\n".join(o)


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="results")
    p.add_argument("--seeds",type=int,default=30)
    p.add_argument("--trials",type=int,default=3000)
    a=p.parse_args()
    result=experiment(range(701,701+a.seeds),a.trials)
    dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True)
    (dest/"gate002.json").write_text(json.dumps(result,indent=2)+"\n")
    text=report(result)
    (dest/"gate002.md").write_text(text)
    print(text)


if __name__=="__main__":
    main()
