"""Gate 004: temporal world, exact alias, no oracle and sensor-noise controls."""
import numpy as np
import pytest
from temporal_gate import (
    N,SENSOR_STD,ACTION_NORM,CARD,
    grid,local_base,simulator_step,update_scores,
    choose_frequency,choose_action,hidden_offset,run_case,
    PASSIVE_STEPS,CHECKPOINTS,aggregate
)


def test_exact_64_fold_passive_alias_is_not_resolved_by_more_time():
    y,x=grid()
    signal=np.cos(2*np.pi*(y+2*x)/N+.63)
    a=(17,55)
    b=(19,54)
    assert a!=b
    assert ((a[0]+2*a[1])-(b[0]+2*b[1]))%N==0
    assert np.max(abs(simulator_step(signal,a)-
                      simulator_step(signal,b)))<1e-12
    left=signal.copy();right=signal.copy()
    for _ in range(18):
        left=simulator_step(left,a)
        right=simulator_step(right,b)
        assert np.max(abs(left-right))<1e-11
    assert sum((dy+2*dx)%N==(a[0]+2*a[1])%N
               for dy in range(N) for dx in range(N))==64


def test_fft_score_matches_pixelwise_corrected_model_risk():
    rng=np.random.default_rng(93)
    x=rng.normal(size=(N,N))
    y=rng.normal(size=(N,N))
    base=local_base(x)
    score=update_scores(np.zeros((N,N)),x,y,assumed_sensor_std=.01)
    norm_base=.40
    for dy,dx,norm in [(17,55,.30),(1,0,.32),(0,0,.40)]:
        predicted=simulator_step(x,(dy,dx))
        raw=-.5*(np.sum((y-predicted)**2)-np.sum((y-base)**2))
        expected=raw+.5*SENSOR_STD**2*N*N*(norm-norm_base)
        assert abs(score[dy,dx]-expected)<1e-10


def test_actions_equal_energy_and_target_frequency_only_sees_learned_scores():
    rng=np.random.default_rng(7)
    scores=np.random.default_rng(8).normal(size=(N,N))
    k=choose_frequency(scores)
    assert 0<=k[0]<10 and 0<=k[1]<10
    for kind in ("targeted","random_fourier","white","fixed_fourier"):
        u,_=choose_action(kind,scores,rng)
        assert abs(np.linalg.norm(u)-ACTION_NORM)<1e-12
    u,_=choose_action("passive",scores,rng)
    assert np.count_nonzero(u)==0
    with pytest.raises(ValueError):
        choose_action("oracle",scores,rng)


def test_random_truth_is_full_domain_and_excludes_local_stencils():
    local={(0,0)}|{(dy%N,dx%N) for dy,dx in CARD}
    offsets={hidden_offset(seed) for seed in range(301,451)}
    assert len(offsets)>=130
    assert not offsets & local


def test_paired_environment_passive_observations_identical_across_policies():
    seed=777
    baseline=run_case(seed,"passive")
    for kind in ("targeted","random_fourier","white","fixed_fourier"):
        alt=run_case(seed,kind)
        assert baseline["checkpoints"]["0"]==alt["checkpoints"]["0"]
        assert baseline["true_offset"]==alt["true_offset"]
        assert alt["max_action_norm_error"]<1e-11


def test_passive_bottleneck_and_active_recovery_on_development_seeds():
    cases={k:[run_case(seed,k) for seed in range(801,809)]
           for k in ("passive","targeted","random_fourier","white","fixed_fourier")}
    assert sum(r["checkpoints"]["0"]["correct"] for r in cases["passive"])<=2
    assert sum(r["checkpoints"]["16"]["correct"] for r in cases["targeted"])>=7
    assert sum(r["checkpoints"]["16"]["correct"] for r in cases["white"])>=7
    assert sum(r["checkpoints"]["16"]["correct"] for r in cases["passive"])<=2
    assert all(r["true_offset"]!=[17,55] for r in cases["passive"])


def test_known_sensor_variance_removes_false_null_remote_links():
    # Crucial kill test: changing only the sensor-noise correction changes
    # the false-link decision even with identical latent path and action.
    for kind in ("targeted","white"):
        good=[run_case(seed,kind,remote=(0,0),correct_R=True)
              for seed in range(801,813)]
        bad=[run_case(seed,kind,remote=(0,0),correct_R=False)
             for seed in range(801,813)]
        assert sum(r["correct_final"] for r in good)>=11
        assert sum(r["correct_final"] for r in bad)==0
        assert all(r["null"] for r in good)


def test_process_innovation_is_separate_from_sensor_noise():
    a=run_case(991,"passive",process_std=0.)
    b=run_case(991,"passive",process_std=.003)
    assert a["true_offset"]==b["true_offset"]
    assert a["process_std"]==0 and b["process_std"]==.003
    assert a["checkpoints"]["16"]!=b["checkpoints"]["16"]


def test_summary_does_not_mix_null_and_remote_denominators():
    cases=[run_case(seed,"white") for seed in range(810,813)]
    grouped=aggregate(cases)
    assert grouped["0"]["total"]==3
    assert grouped["16"]["total"]==3
    assert 0<=grouped["16"]["correct"]<=3
