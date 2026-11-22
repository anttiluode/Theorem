"""Falsification tests for the narrow linear identifiability certificate."""
import numpy as np
from theorem_gate import (
    shadow,field,certificate,probe,predict_accuracy,simulate,
    excitation_spectrum,run_experiment,
)


def test_same_predictions_on_all_passive_inputs_but_different_elsewhere():
    for case in [shadow(),field()]:
        rng=np.random.default_rng(22)
        xs=case.Q@rng.standard_normal((case.Q.shape[1],5000))
        assert np.max(abs(case.A@xs-case.B@xs))<1e-12
        u=probe(case,"optimal",22)
        diff=np.linalg.norm((case.A-case.B)@u)
        assert diff>.69
        assert certificate(case)["passive_disagreement"]<1e-12


def test_optimal_input_has_right_singular_vector_certificate():
    for case in [shadow(),field()]:
        cert=certificate(case)
        assert cert["singular_residual"]<1e-12
        assert cert["max_probe_separation"]>0
        optimum=cert["optimal_probe"]
        rng=np.random.default_rng(100)
        AminusB=case.A-case.B
        for _ in range(1000):
            v=rng.standard_normal(case.A.shape[1])
            v/=np.linalg.norm(v)
            assert np.linalg.norm(AminusB@v)<=np.linalg.norm(AminusB@optimum)+1e-11


def test_zero_sum_violation_is_exactly_the_missing_common_mode():
    c=shadow()
    d=c.A-c.B
    assert np.allclose(d,np.ones((1,8)))
    assert np.linalg.norm(d@c.Q)<1e-12
    assert np.linalg.norm(d@probe(c,"tangent",100))<1e-12
    assert abs(np.linalg.norm(d@probe(c,"optimal",100))-np.sqrt(8))<1e-12
    # An input projection restoring zero-sum destroys even optimal probes.
    P=c.Q@c.Q.T
    assert np.linalg.norm(d@P@probe(c,"optimal",100))<1e-12


def test_checkerboard_stays_dark_under_smooth_fields():
    c=field()
    a=c.A-c.B
    P=c.Q@c.Q.T
    assert np.linalg.norm(a@P)<1e-12
    assert np.linalg.norm(a@probe(c,"optimal",200))>.69
    assert np.linalg.norm(a@probe(c,"tangent",200))<1e-12


def test_one_informative_direction_can_be_identified_without_global_full_rank():
    # This is the critical distinction: a pairwise mechanism is identifiable
    # even while many completely unrelated input modes remain unobservable.
    x0=excitation_spectrum(field(),0)
    x1=excitation_spectrum(field(),.10)
    assert x0["rank_at_1e_7"]==3
    assert x1["rank_at_1e_7"]==4
    assert abs(x1["minimum_eigenvalue"])<1e-10
    assert x1["specific_probe_variance"]>.009
    assert abs(x0["mean_input_power"]-x1["mean_input_power"])<.06
    c=shadow()
    assert excitation_spectrum(c,0)["rank_at_1e_7"]==7
    assert excitation_spectrum(c,.10)["rank_at_1e_7"]==8


def test_equal_energy_tangent_and_optimal_were_not_conflated():
    for c in [shadow(),field()]:
        for k in ("tangent","random","dark_random","optimal"):
            v=probe(c,k,555)
            assert abs(np.linalg.norm(v)-1)<1e-12
        assert predict_accuracy(c,probe(c,"tangent",555))==.5
        assert predict_accuracy(c,probe(c,"optimal",555))>.70


def test_gaussian_likelihood_calibration_independent_of_training():
    r=np.random.default_rng(991)
    for c in (shadow(),field()):
        for kind in ("optimal","random","tangent"):
            direction=probe(c,kind,130)
            empirical=simulate(c,direction,r,50000)
            expected=predict_accuracy(c,direction)
            assert abs(empirical-expected)<.014,(c.name,kind,empirical,expected)


def test_frozen_monte_carlo_seeds_probe_advantage_without_retuning():
    data=run_experiment(range(501,511),1000)
    assert len(data["cases"])==2
    for c in data["cases"].values():
        g=c["groups"]
        assert g["optimal"]["mean_squared_separation"] > (
            g["random"]["mean_squared_separation"]*2)
        assert g["optimal"]["mean_empirical_accuracy"] > (
            g["random"]["mean_empirical_accuracy"]+.07)
        assert abs(g["tangent"]["mean_empirical_accuracy"]-.5)<.04
