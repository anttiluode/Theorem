"""Gate008: nonlinear equilibrium response, support recovery and attribution."""
import numpy as np
import pytest
from equilibrium_gate import (
    N,RMS,PIXEL_CAP,PAIRS,WORLDS,POLICIES,
    lap,probe,curvature_info,true_parameters,step,
    generate,estimate,judge,check,evaluate,
)


def test_all_laws_are_unobservable_from_perfect_bulk_equilibrium():
    for world in WORLDS:
        truth=true_parameters(301,world)
        for sign in (-1.,1.):
            x=np.full((N,N),sign)
            assert np.max(abs(step(x,sign,truth)-x))<1e-13


def test_exact_even_and_odd_nonlinear_identities_for_both_phases():
    rng=np.random.default_rng(19)
    u=probe(rng,'targeted_sparse')
    truth={'D':.17,'r':.23,'a':-.04,'detector_q':0.}
    for s in (-1.,1.):
        yp=step(s+u,s,truth)
        ym=step(s-u,s,truth)
        even=(yp+ym)/2-s
        odd=(yp-ym)/2-u
        assert np.max(abs(even+3*s*truth['r']*u*u))<1e-12
        expected=truth['D']*lap(u)+(truth['a']-2*truth['r'])*u-truth['r']*u**3
        assert np.max(abs(odd-expected))<1e-12


def test_all_active_probes_share_exact_energy_and_amplitude_limit():
    rng=np.random.default_rng(345)
    budget=N*RMS
    for kind in ('white','targeted_sparse','single_fourier'):
        for _ in range(20):
            u=probe(rng,kind)
            assert abs(np.linalg.norm(u)-budget)<1e-8
            assert np.max(abs(u))<=PIXEL_CAP+1e-9


def test_sparse_curvature_probe_is_more_informative_than_white_at_same_energy():
    rng=np.random.default_rng(108)
    for _ in range(30):
        s=probe(rng,'targeted_sparse')
        w=probe(rng,'white')
        assert curvature_info(s)>1.3*curvature_info(w)


def test_noiseless_matched_pulse_fitter_recovers_true_unknown_coefficients():
    rng=np.random.default_rng(98)
    for world in ('allen_cahn','diffusion_only','linear_surrogate',
                  'reaction_only','identity'):
        truth=true_parameters(410,world)
        rows=[]
        for s in (1.,-1.,1.,-1.):
            u=probe(rng,'targeted_sparse')
            rows.append({'u':u,'p':step(s+u,s,truth),
                         'm':step(s-u,s,truth),'sign':s})
        out=estimate(rows)
        assert out['rank']==2
        assert abs(out['D']-truth['D'])<1e-11
        assert abs(out['r']-truth['r'])<1e-11
        assert abs(out['a']-truth['a'])<1e-11


def test_single_fourier_rank_cannot_fake_independent_diffusion_and_linear():
    rng=np.random.default_rng(13)
    truth=true_parameters(301,'allen_cahn')
    rows=[]
    for _ in range(2):
        u=probe(rng,'single_fourier')
        rows.append({'u':u,'p':step(1+u,1,truth),
                     'm':step(1-u,1,truth),'sign':1.})
    out=estimate(rows)
    # Two different random cosine frequencies can create rank; a single
    # identical cosine must be flagged as rank-deficient.
    u=probe(rng,'single_fourier')
    same=[{'u':u,'p':step(1+u,1,truth),
           'm':step(1-u,1,truth),'sign':1.} for _ in range(2)]
    assert estimate(same)['rank']==1
    assert out['rank'] in (1,2)


def test_passive_samples_cannot_identify_cubic_law():
    x=check(303,'allen_cahn','passive')
    assert not x['nonlinear']
    assert not x['selected_support']['D']
    assert not x['exact_support']


def test_sensor_only_quadratic_can_fake_nonlinear_law():
    r=[check(seed,'quadratic_sensor','targeted_sparse')
       for seed in range(301,321)]
    assert sum(x['false_nonlinear'] for x in r)>=5


def test_trusted_reference_sensor_is_distinct_additional_measurement():
    r=[check(seed,'quadratic_sensor','targeted_sparse','reference')
       for seed in range(301,321)]
    assert sum(x['false_nonlinear'] for x in r)==0
    assert sum(x['exact_support'] for x in r)>=16


def test_wrong_action_log_cannot_recover_actual_cubic_reaction():
    r=[check(seed,'allen_cahn','mislogged_kick')
       for seed in range(301,321)]
    assert not any(x['nonlinear'] for x in r)
    assert not any(x['exact_support'] for x in r)


def test_development_pulse_win_is_not_the_frozen_holdout():
    a=[check(seed,'allen_cahn','targeted_sparse') for seed in range(301,313)]
    b=[check(seed,'allen_cahn','white') for seed in range(301,313)]
    assert sum(z['nonlinear'] for z in a)>sum(z['nonlinear'] for z in b)


def test_evaluation_keeps_all_six_worlds_and_reference_arm():
    e=evaluate(range(301,303))
    assert len(e['records'])==2*(6*5+1)
    assert len(e['groups'])==6*5+1
    assert set(g['world'] for g in e['groups'])==set(WORLDS)
    assert set(g['policy'] for g in e['groups'])==set(POLICIES)
    for g in e['groups']:
        assert g['n']==2


def test_invalid_world_policy_and_channel_refused():
    with pytest.raises(ValueError):
        true_parameters(1,'invented')
    with pytest.raises(ValueError):
        probe(np.random.default_rng(1),'oracle')
    with pytest.raises(ValueError):
        generate(1,'allen_cahn','oracle')
    with pytest.raises(ValueError):
        generate(1,'allen_cahn','white',channel='fake calibration')
