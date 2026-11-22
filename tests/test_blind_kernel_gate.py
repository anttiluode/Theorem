"""Gate 003: truth-hidden estimation, Gaussian calibration and nulls."""
import numpy as np
import pytest
from blind_kernel_gate import (
    N,M,probe,response,estimate,hidden_kernel,simulate,run,
    SENSOR_SD,ALPHA,
)


def test_unknown_kernel_inversion_recovers_location_without_term_count():
    rng=np.random.default_rng(4)
    h=hidden_kernel()
    xs=[];ys=[]
    for _ in range(64):
        x=probe(rng,"flat_spectrum")
        xs.append(x);ys.append(response(x,h)+.05*rng.standard_normal(x.shape))
    fit=estimate(xs,ys,sensor_sd=.05)
    truth={tuple(i) for i in np.argwhere(h!=0)}
    assert fit["support"]==truth, (fit["support"],truth)
    assert (17,55) in fit["coefficients"]
    assert abs(fit["coefficients"][(17,55)]-.10)<.04


def test_flat_spectrum_has_full_input_power_and_bounded_spatial_amplitude():
    for seed in range(10):
        rng=np.random.default_rng(seed)
        f=probe(rng,"flat_spectrum")
        assert abs(np.linalg.norm(f)-1)<1e-12
        S=abs(np.fft.fft2(f))
        assert np.max(abs(S-1))<1e-10
        assert np.max(abs(f))<.10
        assert abs(np.linalg.norm(probe(rng,"white"))-1)<1e-12
        assert abs(np.linalg.norm(probe(rng,"smooth"))-1)<1e-12


def test_smooth_input_refuses_dark_frequencies():
    rng=np.random.default_rng(9)
    h=hidden_kernel()
    xs=[probe(rng,"smooth") for _ in range(12)]
    ys=[response(x,h)+SENSOR_SD*rng.standard_normal(x.shape) for x in xs]
    fit=estimate(xs,ys)
    assert fit["spectral_support_fraction"]<.15
    # No arbitrary cap on selected coefficients: a band-limited inverse
    # can spread one real spike over many nearby pixels, and those must
    # remain visible as failures rather than being assumed away.
    assert np.isfinite(fit["h_est"]).all()


def test_null_world_does_not_claim_wormhole():
    r=simulate(seed=9001,n_probes=48,kind="flat_spectrum",null=True)
    assert r["exact"]
    assert r["n_found"]==0
    assert not r["remote_offset_recovered"]


def test_empty_invalid_or_mismatched_files_refused():
    with pytest.raises(ValueError):
        estimate([],[])
    with pytest.raises(ValueError):
        estimate([np.zeros((N,N))],[])
    with pytest.raises(ValueError):
        estimate([np.zeros((N,2))],[np.zeros((N,2))])
    with pytest.raises(ValueError):
        estimate([np.zeros((N,N))],[np.zeros((N,N))],sensor_sd=0)


def test_frozen_small_development_sweep_is_consistent():
    r=run(range(701,704))
    assert len(r["rows"])==3*3*4
    assert all(x["n_found"]==0 for x in r["rows"] if x["null"] and x["exact"])
    for group in r["groups"]:
        assert group["total"]==3
    assert all(0<=g["mean_spectral_fraction"]<=1 for g in r["groups"])
    assert next(g for g in r["groups"]
                if g["kind"]=="flat_spectrum" and g["n_probes"]==48
                )["mean_spectral_fraction"]==1
