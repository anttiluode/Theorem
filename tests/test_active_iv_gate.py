"""Scientific kill tests for Gate 005: private dither as an instrument."""
import numpy as np
import pytest
from active_iv_gate import (
    N,ACTION,make_kernel,motion,white,iv_estimate,noise_floor,decide,
    run_case,pick_frequency,evaluate
)


def test_randomized_exogenous_iv_identifies_unannounced_local_coefficients():
    rng=np.random.default_rng(22)
    h,remote=make_kernel(rng,True)
    assert remote is not None
    H=np.fft.fft2(h)
    kicks=[];outputs=[];x=np.zeros((N,N))
    for t in range(36):
        u=ACTION*white(rng)*rng.choice((-1,1))
        x=motion(x+u,H)
        y=x+.01*rng.standard_normal((N,N))
        kicks.append(u);outputs.append(y)
    fitted,support_fraction=iv_estimate(kicks,outputs)
    assert support_fraction==1.
    for dy,dx in ((0,0),(1,0),(-1,0),(0,1),(0,-1)):
        assert abs(fitted[dy,dx]-h[dy,dx])<.035
    assert abs(fitted[remote]-h[remote])<.035


def test_true_weights_and_noise_scale_not_inputs_to_estimator():
    rng=np.random.default_rng(3)
    h,truth=make_kernel(rng,True)
    assert truth is not None
    u=[ACTION*white(rng)*rng.choice((-1,1)) for _ in range(32)]
    outputs=[motion(v,np.fft.fft2(h))+
             .01*rng.standard_normal((N,N)) for v in u]
    first,_=iv_estimate(u[:16],outputs[:16])
    second,_=iv_estimate(u[16:],outputs[16:])
    picked,metric=decide(first,second)
    assert picked==truth
    assert metric["accepted"]
    assert noise_floor(first)>0


def test_passive_world_has_no_instrument_and_not_identified():
    run=run_case(11,"passive",has_remote=True)
    assert run["chosen"] is None and run["instrument_count"]==0
    assert not run["correct"]


def test_wrongly_paired_placebo_cannot_identify_hidden_remote():
    for seed in range(701,709):
        r=run_case(seed,"placebo",has_remote=True)
        assert r["chosen"] is None


def test_adaptive_probe_reads_only_previous_estimate():
    h=np.zeros((N,N));h[12,9]=.08;h[27,33]=.07
    k=pick_frequency(h)
    assert isinstance(k,tuple) and all(1<=v<=11 for v in k)
    assert k==pick_frequency(h.copy())


def test_equal_energy_and_sample_counts():
    for kind in ("white","two_phase","fourier_only","feedback","placebo"):
        r=run_case(801,kind)
        assert r["instrument_count"]==48
        assert abs(r["action_l2"]-.70)<1e-12
        assert set(r["checkpoints"])=={"12","16","24","32","48"}
    r=run_case(801,"two_phase",stress=True)
    assert r["instrument_count"]==48 and r["action_l2"]==.45


def test_no_link_refusal_when_R_hidden_in_development_seeds():
    for policy in ("white","two_phase"):
        for seed in range(701,709):
            r=run_case(seed,policy,has_remote=False,stress=True)
            assert r["chosen"] is None


def test_feedback_action_not_an_instrument_by_default():
    # If u=-k*y and y=x+eta, u is correlated with BOTH latent x and eta.
    rng=np.random.default_rng(999)
    x=rng.normal(size=100000)
    eta=rng.normal(size=len(x))
    u=-.5*(x+eta)
    assert abs(np.corrcoef(u,eta)[0,1])>.6
    assert abs(np.corrcoef(u,x)[0,1])>.6
    z=rng.normal(size=len(x))
    assert abs(np.corrcoef(z,eta)[0,1])<.02
    assert abs(np.corrcoef(z,x)[0,1])<.02


def test_two_phase_not_assumed_better_than_white():
    r=evaluate(range(701,705),range(801,805),stress=True)
    groups={(g["world"],g["policy"]):g for g in r["aggregate"]}
    assert groups["remote","white"]["n"]==4
    assert groups["remote","two_phase"]["n"]==4
    assert groups["null","white"]["false_link"]==0
    assert groups["null","two_phase"]["false_link"]==0
    assert groups["remote","placebo"]["success"]==0


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError):iv_estimate([],[])
    with pytest.raises(ValueError):
        iv_estimate([np.zeros((N,N))],[np.zeros((N,N))]*3)
    with pytest.raises(ValueError):run_case(1,"magic")
