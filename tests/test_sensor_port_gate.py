"""Gate 006: distinguish colored sensor errors from actuator confounding."""
import numpy as np
import pytest

from active_iv_gate import make_kernel, motion, white
from sensor_port_gate import (
    N, M, SHIFT, BUDGET, sensor_series, actual_actuation,
    estimate_action_transfer, run_case, evaluate,
)


def test_temporal_sensor_autocorrelation_does_not_by_itself_break_private_iv():
    r=np.random.default_rng(87)
    n=12000
    signs=np.random.default_rng(97).choice([-1,1], size=n)
    noise=np.empty(n)
    e=0.
    for i,z in enumerate(r.normal(size=n)):
        e=.85*e+np.sqrt(1.-.85**2)*z
        noise[i]=e
    assert np.corrcoef(noise[:-1],noise[1:])[0,1]>.83
    assert abs(np.mean(signs*noise))<.03
    assert abs(np.corrcoef(signs,noise)[0,1])<.03


def test_spatial_sensor_noise_is_correlated_and_temporal_noise_has_same_scale():
    rng=np.random.default_rng(17)
    x=sensor_series(rng,"temporal_spatial_colored",32,.02)
    assert len(x)==32 and all(v.shape==(N,N) for v in x)
    assert .015 < np.std(np.stack(x)) < .025
    a=np.stack(x)
    assert np.corrcoef(a[:-1].ravel(),a[1:].ravel())[0,1]>.75
    assert np.corrcoef(a[:,:,:-1].ravel(),a[:,:,1:].ravel())[0,1]>.35


def test_unknown_spatial_actuator_shift_is_indistinguishable_from_shifted_operator_for_direct_kicks():
    rng=np.random.default_rng(19)
    h,_=make_kernel(rng,False)
    H=np.fft.fft2(h)
    u=BUDGET*white(rng)
    y1=motion(np.roll(u, SHIFT, axis=(0,1)),H)
    shifted_h=np.roll(h, SHIFT, axis=(0,1))
    y2=motion(u,np.fft.fft2(shifted_h))
    assert np.max(abs(y1-y2))<1e-13
    assert shifted_h[SHIFT]>.35
    # Thus an actually local world looks remote through an unknown port.
    assert abs(h[SHIFT])<1e-12


def test_actuator_noise_is_extra_variance_not_population_IV_bias():
    rng=np.random.default_rng(20)
    u=BUDGET*white(rng)
    x=[]
    for _ in range(200):
        x.append(actual_actuation(u,None,"independent_actuator_noise",rng))
    assert np.max(abs(np.mean(x,axis=0)-u))<.012
    assert np.array_equal(
        actual_actuation(np.zeros((N,N)),None,"independent_actuator_noise",rng),
        np.zeros((N,N)))


def test_incorrect_time_alignment_and_fixed_corrected_arm_are_distinct():
    a=run_case(705,"delayed_actuator",remote=True,lag=0)
    b=run_case(705,"delayed_actuator",remote=True,lag=1)
    assert a["truth"]==b["truth"]
    assert a["n_action_pairs"]==48 and b["n_action_pairs"]==47
    assert b["correct_world"]
    assert b["original_kernel_local_mae"]<a["original_kernel_local_mae"]


def test_actuator_shift_can_invent_a_remote_link_in_a_true_null():
    r=run_case(708,"shifted_actuator",remote=False,lag=0)
    assert r["truth"] is None
    assert r["reported"] is not None
    assert r["false_world_link"]
    assert r["effective_kernel_local_mae"]<r["original_kernel_local_mae"]


def test_colored_noise_can_preserve_the_moment_but_not_guarantee_a_calibrated_threshold():
    a=run_case(706,"iid",remote=True,lag=0)
    b=run_case(706,"temporal_ar085",remote=True,lag=0)
    assert a["correct_world"] and b["correct_world"]
    assert np.isfinite(a["original_kernel_local_mae"])
    assert np.isfinite(b["original_kernel_local_mae"])
    assert b["n_action_pairs"]==48


def test_unknown_gain_hides_physical_coefficient_scale():
    r=run_case(706,"unknown_gain",remote=True)
    assert r["effective_kernel_local_mae"]<r["original_kernel_local_mae"]
    assert r["truth"] is not None


def test_frozen_metadata_schema_and_matched_count():
    o=evaluate(range(701,703),range(801,803))
    assert len(o["results"])==18
    assert len(o["rows"])==36
    for g in o["results"]:
        assert g["n"]==2
    assert all(r["action_lag_used"] in (0,1) for r in o["rows"])
    with pytest.raises(ValueError):
        run_case(1,"bad-case")
    with pytest.raises(ValueError):
        estimate_action_transfer([],[])
    with pytest.raises(ValueError):
        estimate_action_transfer([np.zeros((N,N))]*10,
                                 [np.zeros((N,N))]*10,lag=2)
