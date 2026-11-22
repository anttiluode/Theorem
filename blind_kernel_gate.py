"""Gate 003: blind spatial-link recovery by active phase-balanced probing.

SOURCE: the existing 64x64 Luotain2 wormhole law from worlds.py.
The unknown 6 spatial offsets and coefficients are NOT provided to the
estimator or to its threshold. Only independent (x,y) probe/response
pairs and calibrated i.i.d. sensor noise sigma are given.

This is conventional linear convolutional system identification, not
a new theorem, not blind temporal dynamics discovery, and not WAIVES.

Fourier cross-spectrum Hhat = sum(conj(Xk)*Yk) / sum(abs(Xk)^2).
Estimate hhat = ifft2(Hhat). Correct variance of each hhat pixel, for
real i.i.d. Gaussian output noise of variance R and M spatial samples:
  var(hhat_pixel) = R/M * sum_valid 1 / sum_probes |X_k|^2.
A conservative Gaussian union bound threshold over all M pixels is
  sigma_eff * sqrt(2*log(2*M/alpha)).
This is a calibrated family-wise *sufficient* bound, not an optimal
statistical test; meaningful only with the assumed input and noise model.
"""
from __future__ import annotations
import json
from math import sqrt,log
from pathlib import Path
import numpy as np

N=64
M=N*N
SENSOR_SD=.08
ALPHA=.05
K_LEVELS=(8,24,48)
PROBE_KINDS=("smooth","white","flat_spectrum")


def hidden_kernel():
    """Used only by simulator and post-selection scoring."""
    h=np.zeros((N,N),dtype=float)
    h[0,0]=.5
    for dy,dx in ((1,0),(-1,0),(0,1),(0,-1)):
        h[dy%N,dx%N]=.1
    h[17,-9]=.1
    return h


def response(x,h):
    return np.fft.ifft2(np.fft.fft2(x)*np.fft.fft2(h)).real


def probe(rng,kind):
    v=rng.standard_normal((N,N))
    if kind=="smooth":
        f=np.fft.fftfreq(N)*N
        ky,kx=np.meshgrid(f,f,indexing="ij")
        v=np.fft.ifft2(np.fft.fft2(v)*np.exp(
            -(ky*ky+kx*kx)/(2*2.5**2))).real
    elif kind=="white":
        pass
    elif kind=="flat_spectrum":
        # If v is real, FFT(v) is Hermitian symmetric.
        # Replacing its complex magnitudes with 1 preserves that symmetry
        # and yields a real signal with exactly flat Fourier energy.
        F=np.fft.fft2(v)
        v=np.fft.ifft2(F/np.maximum(abs(F),1e-14)).real
    else:
        raise ValueError(kind)
    norm=float(np.linalg.norm(v))
    if norm<1e-12:
        raise ValueError("Degenerate probe")
    return v/norm


def estimate(xs,ys,sensor_sd=SENSOR_SD,alpha=ALPHA,min_spectral_power_fraction=.15):
    """No truth, term support, number of links or coefficients are given."""
    if len(xs)!=len(ys) or not len(xs):
        raise ValueError("Unpaired recordings")
    if not (sensor_sd>0 and 0<alpha<1):
        raise ValueError("Known positive sensor std and alpha in (0,1) required")
    den=np.zeros((N,N),dtype=float)
    cross=np.zeros((N,N),dtype=complex)
    for x,y in zip(xs,ys):
        if x.shape!=(N,N) or y.shape!=(N,N):
            raise ValueError("Unexpected field size")
        X=np.fft.fft2(x)
        Y=np.fft.fft2(y)
        den+=abs(X)**2
        cross+=np.conj(X)*Y
    # A fixed minimum-information threshold for inverting spectral bins.
    # Smooth probes leave many bins dark; refuse to invent H there.
    valid=den >= min_spectral_power_fraction*len(xs)
    H=np.zeros((N,N),dtype=complex)
    H[valid]=cross[valid]/den[valid]
    h=np.fft.ifft2(H).real
    # For real-valued probes and real Gaussian noise, this variance
    # is exact up to floating-point tolerance. Harmonic conjugate
    # frequencies share noise in the way the real FFT requires.
    var=(sensor_sd**2/M)*float(np.sum(1/den[valid]))
    threshold=sqrt(var)*sqrt(2*log(2*M/alpha))
    coords=np.argwhere(np.abs(h)>threshold)
    support={(int(dy),int(dx)) for dy,dx in coords}
    return {
       "support":support,
       "coefficients":{(int(dy),int(dx)):float(h[dy,dx]) for dy,dx in coords},
       "threshold":float(threshold),
       "estimated_sensor_sd_kernel":sqrt(var),
       "spectral_support_fraction":float(valid.mean()),
       "min_valid_input_spectral_power":float(den[valid].min()) if valid.any() else None,
       "h_est":h,
    }


def simulate(seed=0,n_probes=24,kind="flat_spectrum",null=False):
    rng=np.random.default_rng(seed)
    truth=hidden_kernel()   # only used in data generator, not estimator
    xs=[];ys=[];peaks=[]
    for _ in range(n_probes):
        x=probe(rng,kind)
        y=(np.zeros_like(x) if null else response(x,truth))
        y=y+SENSOR_SD*rng.standard_normal(y.shape)
        xs.append(x);ys.append(y);peaks.append(float(np.max(np.abs(x))))
    found=estimate(xs,ys)
    exact_support={tuple(map(int,i)) for i in np.argwhere(truth!=0)}
    correct=(found["support"]==set() if null else found["support"]==exact_support)
    miss=sorted(exact_support-found["support"]) if not null else []
    wrong=sorted(found["support"]-exact_support) if not null else sorted(found["support"])
    return {
        "seed":seed,"kind":kind,"n_probes":n_probes,"null":null,
        "status":"exact" if correct else "miss_or_false_link",
        "exact":bool(correct),
        "n_found":len(found["support"]),
        "n_true":0 if null else len(exact_support),
        "found_offsets":[[dy if dy<=N//2 else dy-N,
                          dx if dx<=N//2 else dx-N]
                         for dy,dx in sorted(found["support"])],
        "missed_offsets":miss,
        "false_offsets":wrong,
        "threshold":found["threshold"],
        "estimated_noise_sd_per_coefficient":found["estimated_sensor_sd_kernel"],
        "spectral_support_fraction":found["spectral_support_fraction"],
        "max_probe_abs_amplitude":max(peaks),
        "mean_probe_abs_amplitude":float(np.mean(peaks)),
        "remote_offset_recovered":(17,(-9)%N) in found["support"] if not null else False,
        "remote_coefficient_if_found":found["coefficients"].get((17,(-9)%N)),
    }


def run(seeds=range(801,821)):
    rows=[]
    for seed in seeds:
        for k in K_LEVELS:
            for kind in PROBE_KINDS:
                rows.append(simulate(seed,k,kind,null=False))
            # The null uses the identical time-domain sensor noise model
            # and a flat-spectrum probe family with no physical link.
            rows.append(simulate(seed,k,"flat_spectrum",null=True))
    groups=[]
    for k in K_LEVELS:
        for kind in PROBE_KINDS:
            xs=[r for r in rows if r["n_probes"]==k and
                r["kind"]==kind and not r["null"]]
            groups.append({
                "n_probes":k,"kind":kind,
                "exact":sum(r["exact"] for r in xs),
                "total":len(xs),
                "remote_recovered":sum(r["remote_offset_recovered"] for r in xs),
                "mean_spectral_fraction":float(np.mean([r["spectral_support_fraction"] for r in xs])),
                "mean_threshold":float(np.mean([r["threshold"] for r in xs])),
                "mean_peak_probe_amplitude":float(np.mean([r["max_probe_abs_amplitude"] for r in xs]))
            })
    null_rows=[r for r in rows if r["null"]]
    return {
        "title":"Gate 003 — No-oracle spatial kernel support discovery",
        "world":"Luotain2 wormhole shifted stencil on periodic 64x64 field",
        "truth_given_to_estimator":False,
        "support_size_given_to_estimator":False,
        "calibrated_output_sensor_noise_sd":SENSOR_SD,
        "familywise_alpha":ALPHA,
        "equal_probe_l2_norm":1,
        "seeds":list(seeds),
        "probe_counts":list(K_LEVELS),
        "groups":groups,
        "null_false_positive_runs":sum(not r["exact"] for r in null_rows),
        "null_total":len(null_rows),
        "rows":rows,
        "scope":[
            "The estimator knows linear shift-invariant convolution and the observation noise scale.",
            "True generating offsets/coefficients hidden from fit and threshold; truth consulted only at final scoring.",
            "Known spectral support and fixed threshold rule predeclared, no simulator feedback until row-level scoring.",
            "Ordinary Fourier cross-spectrum inversion and Gaussian union bound, not a novel blind law discovery theorem.",
            "No temporal dynamics, correlated noise, unknown source signal, or cross-family validation.",
            "One selected world and known periodic boundary, synthetic active input access."]
    }


def report(data):
    a=["# Gate 003 — Recover an unannounced wormhole address",
       "",
       "The estimator knows only paired actively injected input fields,",
       "noisy output fields, and a calibrated sensor noise scale.",
       "The true +17,-9 address, coefficients and number of support terms",
       "are withheld until evaluating the selected spatial kernel.",
       "",
       "| Probes | Excitation | Exact full support | Remote link found | Mean spectral bins observable |",
       "|---:|---|---:|---:|---:|"]
    for row in data["groups"]:
        a.append(f"| {row['n_probes']} | {row['kind']} | {row['exact']}/{row['total']} | {row['remote_recovered']}/{row['total']} | {row['mean_spectral_fraction']:.3f} |")
    a.extend(["",
        f"Null false positive runs: {data['null_false_positive_runs']}/{data['null_total']}.",
        "",
        "This is a standard linear convolution inverse using complex phase.",
        "It does not solve unrestricted Luotain2 blind nonlinear or temporal",
        "law selection. The prior assumes a shift-invariant linear system",
        "with a calibrated noise level and experimentally controlled input.",
        ""])
    return "\n".join(a)


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="results")
    p.add_argument("--seeds",type=int,default=20)
    opts=p.parse_args()
    result=run(range(801,801+opts.seeds))
    folder=Path(opts.out);folder.mkdir(parents=True,exist_ok=True)
    (folder/"gate003.json").write_text(json.dumps(result,indent=2)+"\n")
    markdown=report(result)
    (folder/"gate003.md").write_text(markdown)
    print(markdown)


if __name__=="__main__":
    main()
