"""Gate 001 — specified competing mechanisms, support ambiguity, active probe.

This is known linear algebra and an executable cross-domain analogy.
Neither mechanism is learned here. A and B are given to the experiment.
"""
from dataclasses import dataclass
from math import erf, sqrt
from pathlib import Path
import json
import numpy as np


@dataclass(frozen=True)
class Case:
    name: str
    A: np.ndarray
    B: np.ndarray
    Q: np.ndarray  # orthonormal columns span all passive observations
    budget: float
    sigma: float


def orthonormal(x):
    return np.linalg.qr(np.asarray(x, float))[0]


def shadow(n=8, j=3):
    a=np.zeros((1,n)); a[0,j]=1
    b=-np.ones((1,n)); b[0,j]=0
    q=orthonormal(np.eye(n)[:,:n-1]-np.eye(n)[:,[-1]])
    return Case("Zero-sum complement read",a,b,q,.12,.16)


def field(n=16):
    a=.50*np.eye(n)+.20*np.roll(np.eye(n),1,axis=0)+.20*np.roll(np.eye(n),-1,axis=0)
    v=(-1.)**np.arange(n)/sqrt(n)
    b=a+.70*np.outer(v,v)
    theta=np.arange(n)*2*np.pi/n
    q=orthonormal(np.stack((np.ones(n),np.sin(theta),np.cos(theta)),axis=1))
    return Case("Unexcited checkerboard field",a,b,q,.45,.07)


def certificate(case):
    delta=case.A-case.B
    u,s,vh=np.linalg.svd(delta,full_matrices=False)
    best=vh[0]
    return {"ambient_dimensions":case.A.shape[1],
            "passive_dimensions":case.Q.shape[1],
            "passive_disagreement":float(np.linalg.norm(delta@case.Q)),
            "top_singular_value":float(s[0]),
            "max_output_separation":float(case.budget*s[0]),
            "optimal_probe":best,
            "singular_residual":float(abs(np.linalg.norm(delta@best)-s[0]))}


def probe(case,kind,seed):
    rng=np.random.default_rng(seed)
    q=case.Q
    if kind=="optimal": return certificate(case)["optimal_probe"]
    if kind=="random": v=rng.standard_normal(case.A.shape[1])
    elif kind=="tangent": v=q@rng.standard_normal(q.shape[1])
    elif kind=="dark_random":
        v=rng.standard_normal(case.A.shape[1])
        v=v-q@(q.T@v)
    else: raise ValueError(kind)
    norm=np.linalg.norm(v)
    if norm<1e-12: raise ValueError("Degenerate probe")
    return v/norm


def cdf(z):
    return .5*(1+erf(z/sqrt(2)))


def accuracy(case,v):
    separation=float(case.budget*np.linalg.norm((case.A-case.B)@v))
    return cdf(separation/(2*case.sigma))


def simulate(case,v,rng,n):
    gap=float(case.budget*np.linalg.norm((case.A-case.B)@v))
    if gap<1e-12:
        return float(np.mean(rng.random(n)<.5))
    # For independent isotropic Gaussian observation noise and known
    # A,B, the likelihood-ratio sufficient statistic is one Gaussian.
    return float(np.mean(rng.standard_normal(n)>-gap/(2*case.sigma)))


def excitation_spectrum(case,eps,seed=71,n=12000):
    # Fixed total expected input energy = 1 at all epsilon.
    rng=np.random.default_rng(seed)
    q=case.Q
    r=q.shape[1]
    base=q@rng.standard_normal((r,n))/sqrt(r)
    best=certificate(case)["optimal_probe"]
    x=sqrt(1-eps**2)*base+eps*best[:,None]*rng.standard_normal((1,n))
    vals=np.linalg.eigvalsh(x@x.T/n)
    return {"epsilon":eps,"minimum_eigenvalue":float(vals[0]),
            "rank_at_1e_7":int(np.sum(vals>1e-7)),
            "mean_input_power":float(np.mean(np.sum(x*x,axis=0))),
            "specific_probe_variance":float(np.var(best@x))}


def run_experiment(seeds=range(501,531),trials=3000):
    rows={}
    for case in (shadow(),field()):
        cert=certificate(case)
        if cert["passive_disagreement"]>1e-10:
            raise AssertionError("Passive operators are not equivalent")
        groups={}
        per_seed=[]
        for seed in seeds:
            rng=np.random.default_rng(81000+seed)
            for kind in ("tangent","random","dark_random","optimal"):
                v=probe(case,kind,seed)
                sep2=float((case.budget*np.linalg.norm((case.A-case.B)@v))**2)
                per_seed.append({"seed":seed,"probe":kind,"squared_separation":sep2,
                                 "theory_accuracy":accuracy(case,v),
                                 "actual_accuracy":simulate(case,v,rng,trials)})
        for kind in ("tangent","random","dark_random","optimal"):
            rs=[r for r in per_seed if r["probe"]==kind]
            groups[kind]={
                "mean_squared_separation":float(np.mean([r["squared_separation"] for r in rs])),
                "mean_theory_accuracy":float(np.mean([r["theory_accuracy"] for r in rs])),
                "mean_empirical_accuracy":float(np.mean([r["actual_accuracy"] for r in rs])),
                "seed_accuracy_sd":float(np.std([r["actual_accuracy"] for r in rs]))
            }
        projection=case.Q@case.Q.T
        projected=float(np.linalg.norm((case.A-case.B)@projection@cert["optimal_probe"]))
        rows[case.name]={
            "budget":case.budget,"sensor_sd":case.sigma,
            "certificate":{k:(v.tolist() if isinstance(v,np.ndarray) else v)
                           for k,v in cert.items()},
            "groups":groups,
            "post_projection_disagreement":projected,
            "excitation_spectrum":[excitation_spectrum(case,x) for x in (0,.01,.03,.10,.30)],
            "per_seed":per_seed}
    return {
      "experiment":"Gate 001: which perturbation distinguishes two laws?",
      "assumptions":["Both operators supplied to experiment: not blind discovery",
                     "Finite linear operators; all passive inputs in known subspace",
                     "Known i.i.d. Gaussian output measurement noise",
                     "Equal Euclidean energy for every probe",
                     "Input intervention directions physically available",
                     "Equal-prior optimal binary discriminator given both operators"],
      "seeds":list(seeds),"trials_per_seed":trials,"cases":rows}


def report(data):
    a=[
        "# Gate 001 — The missing dimension",
        "",
        "This is a computational demonstration of established nullspace and optimal design mathematics, not a claim to a newly proved theorem.",
        "",
        "| Case | Equal-energy probe | Mean squared output difference | Predicted decision accuracy | Empirical decision accuracy |",
        "|---|---|---:|---:|---:|"
    ]
    for name,c in data["cases"].items():
        for kind,metric in c["groups"].items():
            a.append(f"| {name} | {kind} | {metric['mean_squared_separation']:.6f} | {metric['mean_theory_accuracy']:.3f} | {metric['mean_empirical_accuracy']:.3f} |")
    a += [
        "",
        "Shadow case: direct reads slot j, complement negates the sum of the seven other slots.",
        "They agree whenever all eight details sum to zero. The informative probe",
        "changes their common mode; a sum-preserving probe cannot distinguish them.",
        "",
        "Field case: two constructed spatial operators differ in a checkerboard mode",
        "not contained in the three low-frequency observed modes. This is an",
        "illustration, NOT recovery of the actual Luotain2 wormhole law.",
        "",
        "An input projection onto the original observed subspace annihilates",
        "the identifying probe in both constructed cases. This projection is",
        "not the same physical operation as EEG common-average referencing.",
        "",
        "If D = A-B and every passive input is in span(Q), D Q = 0 implies",
        "equal outputs for all those inputs. At fixed probe budget E,",
        "the largest distinguishable response is E times the top singular",
        "value of D. For two known alternatives and Gaussian sensor SD sigma,",
        "one-measurement Bayes accuracy is Phi(||D probe||/(2 sigma)).",
        "",
        "Limits: known alternative operators, constructed linear tasks, known",
        "input support, uncorrelated output noise; no WAIVES/IV theorem, no",
        "raw EEG source attribution, no human-vs-model-text detector.",
        "",
        "Run: python -m theorem_gate --out results",
        ""
    ]
    return "\n".join(a)


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="results")
    p.add_argument("--seeds",type=int,default=30)
    p.add_argument("--trials",type=int,default=3000)
    opts=p.parse_args()
    data=run_experiment(range(501,501+opts.seeds),opts.trials)
    dest=Path(opts.out);dest.mkdir(parents=True,exist_ok=True)
    (dest/"gate001.json").write_text(json.dumps(data,indent=2,allow_nan=False)+"\n")
    m=report(data)
    (dest/"gate001.md").write_text(m)
    print(m)


if __name__=="__main__":
    main()
