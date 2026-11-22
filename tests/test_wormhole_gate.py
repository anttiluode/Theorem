"""Independent numeric checks for actual Luotain2 wormhole shift signature."""
import numpy as np
from wormhole_gate import (
    true_wormhole,missing_link_alternative,difference,gain,
    candidate_fourier_mode,direction,mode_spectrum,experiment,
    response_separation, BUDGET
)


def test_wormhole_equation_matches_remote_vs_local_swap():
    rng=np.random.default_rng(77)
    x=rng.standard_normal((64,64))
    remote=np.roll(x,(17,-9),axis=(0,1))
    assert np.max(abs(difference(x)-.1*(remote-x)))<1e-12
    assert not np.allclose(true_wormhole(x),missing_link_alternative(x))


def test_fourier_shift_formula_on_multiple_distinct_modes():
    for ky,kx in [(0,32),(9,17),(1,2),(3,7),(0,5),(4,9),(31,1)]:
        v=candidate_fourier_mode(ky,kx)
        assert abs(np.linalg.norm(difference(v))-gain(ky,kx))<1e-11, (ky,kx)
    assert abs(gain(0,32)-.2)<1e-12
    assert gain(9,17)<1e-12


def test_even_high_frequency_can_be_exactly_dark():
    v=direction("exact_dark",701)
    bright=direction("bright",701)
    near=direction("near_dark",701)
    assert np.linalg.norm(difference(v))<1e-12
    assert np.linalg.norm(difference(bright))>.199999
    assert np.linalg.norm(difference(near))<.010
    assert np.linalg.norm(difference(near))>.009


def test_spectrum_has_nontrivial_dark_lattice_not_just_low_pass():
    s=mode_spectrum()
    assert s["exact_dark_modes"]==64
    assert s["maximal_bright_modes"]==64
    assert s["n_fourier_modes"]==4096
    assert s["example_near_dark_gain"]<.01


def test_equal_energy_kicks_and_noise_rejection():
    result=experiment(range(701,711),2000)
    g=result["groups"]
    for label in g:
        assert g[label]["max_input_energy_mismatch"]<1e-11
    assert abs(g["exact_dark"]["empirical_accuracy"]-.5)<.04
    assert g["bright"]["empirical_accuracy"]>.9
    assert g["bright"]["empirical_accuracy"]>g["white"]["empirical_accuracy"]+.04
    assert g["bright"]["mean_squared_output_separation"]>(
        g["near_dark"]["mean_squared_output_separation"]*300)
    for label in g:
        assert abs(g[label]["predicted_accuracy"]-g[label]["empirical_accuracy"])<.025
