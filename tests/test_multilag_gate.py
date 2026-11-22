"""Gate 007: mathematical identities, partial rescue, physical attribution kills."""
from __future__ import annotations
import numpy as np
import pytest

from multilag_gate import (
    N, ACTION, BYPASS, CASES, SAMPLES, LOCAL,
    kernel, convolve, experiment, cross_transfer, ratio, detect,
    exact_certificates, sensor_mixing_certificate,
    measure_case, evaluate,
)


def test_exact_multilag_cancellation_and_persistent_bypass_equivalence():
    c=exact_certificates()
    assert c["minimum_abs_world_eigenvalue"]>.30
    assert c["shifted_actuator_ratio_residual"]<1e-12
    assert c["memoryless_bypass_late_ratio_residual"]<1e-12
    assert c["matching_ringing_vs_effective_actuator_residual"]<1e-12


def test_noncommuting_unknown_sensor_basis_preserves_observations_but_scrambles_geometry():
    c=sensor_mixing_certificate()
    assert c["local_world_apparent_nonlocal_edges"]==0
    assert c["mixed_sensor_apparent_nonlocal_edges"]>150
    assert c["eigenvalue_disagreement"]<1e-9
    assert c["all_trajectories_equivalent_in_transformed_coordinates"]<1e-11


def test_true_lagged_cross_transfer_on_explicit_single_command():
    rng=np.random.default_rng(22)
    h,_=kernel(rng,False)
    H=np.fft.fft2(h)
    U=np.zeros((20,N,N),complex)
    Y=np.zeros((20,N,N),complex)
    u=rng.normal(size=(N,N))
    U[0]=np.fft.fft2(u)
    Y[0]=H*U[0]
    Y[1]=H**2*U[0]
    Y[2]=H**3*U[0]
    for lag in (1,2,3):
        # With only one nonzero command, the full cross-moment is exact.
        out=cross_transfer(U,Y,lag,0,20)
        assert np.max(abs(out-H**lag))<1e-11


def test_unknown_shifted_actuator_fools_first_lag_and_is_rescued_by_second():
    r=measure_case(703,"shifted_actuator",False,samples=128)
    assert r["results"]["one_lag"]["selected"]==list(BYPASS)
    assert r["results"]["one_lag"]["false_remote"]
    assert r["results"]["propagate_1_to_2"]["selected"] is None
    assert r["results"]["sham_corrected_1_to_2"]["selected"] is None


def test_memoryless_feedthrough_needs_late_echo_or_real_sham():
    r=measure_case(703,"memoryless_bypass",False,samples=128)
    assert r["results"]["one_lag"]["false_remote"]
    assert r["results"]["propagate_1_to_2"]["false_remote"]
    assert r["results"]["propagate_2_to_3"]["selected"] is None
    assert r["results"]["sham_corrected_1_to_2"]["selected"] is None
    assert r["results"]["fake_sham_corrected"]["false_remote"]


def test_matched_ringing_can_hide_as_alternative_actuator_even_with_late_lags():
    result=measure_case(703,"matched_ringing_bypass",False,samples=128)
    assert result["results"]["one_lag"]["false_remote"]
    assert result["results"]["sham_sensor"]["selected"]==list(BYPASS)
    assert result["results"]["sham_corrected_1_to_2"]["selected"] is None


def test_different_ringing_does_not_automatically_disappear_from_echoes():
    result=measure_case(703,"different_ringing_bypass",False,samples=128)
    assert result["results"]["one_lag"]["false_remote"]
    assert result["results"]["sham_sensor"]["selected"]==list(BYPASS)
    assert result["results"]["sham_corrected_1_to_2"]["selected"] is None


def test_no_observer_gets_truth_or_port_parameters_as_inputs():
    a=experiment(702,"memoryless_bypass",False,128)
    h,truth,(U,Y,SHAM,FAKE)=a
    assert truth is None and h.shape==(N,N)
    assert all(z.shape==(128,N,N) for z in (U,Y,SHAM,FAKE))
    assert BYPASS not in LOCAL
    assert np.all(np.isfinite(Y))
    assert np.all(np.isfinite(SHAM))


def test_fixed_heuristic_refuses_small_transfer_and_ridge_is_finite():
    h=np.zeros((N,N))
    assert detect(h,h) is None
    assert np.all(np.isfinite(ratio(np.zeros((N,N)),np.zeros((N,N)))))
    with pytest.raises(ValueError):
        experiment(1,"unregistered",False,128)
    with pytest.raises(ValueError):
        cross_transfer(np.zeros((8,N,N)),np.zeros((8,N,N)),5,0,8)


def test_quick_development_sweep_preserves_all_condition_denominators():
    s=evaluate(range(701,703),range(801,803),128)
    assert len(s["rows"])==len(CASES)*2*2
    assert len(s["groups"])==len(CASES)*7
    for g in s["groups"]:
        assert g["remote_total"]==2 and g["null_total"]==2
    assert next(g for g in s["groups"] if g["case"]=="shifted_actuator"
                and g["method"]=="one_lag")["false_null"]==2
