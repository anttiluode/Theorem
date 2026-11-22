# Gate 005 — Private dither finds a remote link without knowing R or stencil weights

**Status: completed successful synthetic experiment, 22 November 2026.** [Passing GitHub Actions evaluation](https://github.com/anttiluode/Theorem/actions/runs/45043279743), with **40 tests passed**. [Full per-seed receipts](https://github.com/anttiluode/Theorem/actions/runs/45043279743/artifacts/14762816341) · [Frozen protocol](GATE_005_PROTOCOL.md) · [Python implementation](active_iv_gate.py) · [Compact committed summary](results/gate005_summary.json).

## The key correction to Neon

A known action is **not automatically a valid instrumental variable**. Deterministic feedback chosen from a noisy current observation depends on that observation's latent state and sensor error. It can bias the estimated operator.

The intervention here is selected as a known spatial pattern using measurements from the past, but **its sign is chosen independently at the last instant**. This private sign ensures zero conditional mean and isolates the causal effect of the physically injected intervention under the assumed additive linear simulator. The learner exploits this noise-free input channel, not a claim that any feedback signal is exogenous.

The underlying system is still assumed to be linear, sparse, spatially shift invariant, and equipped with an accurately known additive intervention port. This is **established IV/convolution system-identification mathematics**, not a new theorem.

## Experimental design

All 64×64 worlds evolve continuously, with 16 passive transitions followed by 48 equal-power interventions. The generator draws the local self and neighboring coupling strengths, optional **one random nonlocal link of either sign**, hidden remote address, and sensor noise SD. No model coefficient, offset or R is supplied to the estimator.

The learner combines the Fourier cross-power of the *actual independently randomized action* with the following measured frame, estimates a full spatial kernel, then selects a candidate outside a predeclared local radius. Candidate selection uses only the **first half** of the intervention records; the **second non-overlapping block** must reproduce a same-sign effect above its own spatial MAD threshold (3.4×). These blocks are not unconditionally independent: the evolving state and adaptive action shapes depend on earlier data. The fresh private random signs provide conditional exogeneity, not a traditional independent-sample p-value.

The noise proxy is derived from the **spatial spread of estimated kernel coefficients**, using sparsity as an assumption. This is **not** a validated family-wise false-positive control; the claim is solely what happened in these sampled simulations.

Policies: pure broadband white; white followed by a hybrid white-plus-candidate-directed Fourier mode; narrowband random Fourier; deterministic noisy-feedback (invalid exogeneity control); and independently mispaired placebo actions.

### Easy diagnostic (previously inspected, not the holdout)

| World | White | Two phase | Narrowband Fourier | Feedback | Placebo |
|---|---:|---:|---:|---:|---:|
| Remote present: exact address | 20/20 | 20/20 | 0/20 | 20/20 | 0/20 |
| No remote: correct refusal | 20/20 | 20/20 | 18/20 | 20/20 | 20/20 |

Narrowband Fourier produced **two false remote links in 20 no-link diagnostic worlds**. The successful feedback classifications do not validate it as an instrument: its **local coefficient MAE was 0.046** versus 0.0025 for white, a factor of about 18 in this easy regime.

### Stronger independent weak-link holdout

The weak regime was selected using disjoint development seeds (701–708). **Frozen evaluation:** 40 new remote worlds (seeds 2201–2240), 40 separate null worlds (seeds 3201–3240). The remote coefficient magnitude is only 0.045–0.075, sensor SD varies across worlds from 0.012 to 0.022, and every action has L2 norm 0.45. The estimator is **not told** these realized values.

| World | Broadband white | Broadband → targeted | Single random Fourier | Deterministic feedback | Mispaired placebo |
|---|---:|---:|---:|---:|---:|
| **Remote link: exact location** | **40/40** | 36/40 | 0/40 | 33/40 | 0/40 |
| **No remote: correctly refuses** | **40/40** | **40/40** | 40/40 | 40/40 | 40/40 |

White-noise excitation was **better at final recovery than the two-phase controller**, 40/40 versus 36/40. That is a negative result for the proposed adaptive improvement; it must not be described as a win.

### Sample efficiency in the weak-link holdout

| Interventions | Broadband white | Broadband → targeted | Feedback (endogenous) |
|---:|---:|---:|---:|
| 12 | 10/40 | **13/40** | 2/40 |
| 16 | 19/40 | **22/40** | 12/40 |
| 24 | **28/40** | **28/40** | 21/40 |
| 32 | **36/40** | 33/40 | 27/40 |
| 48 | **40/40** | 36/40 | 33/40 |

The two-phase method had a **small exploratory early advantage** at 12 and 16 interventions, but lost it later. These repeated checkpoint comparisons were not powered for statistical claims; no corrected significance testing was done. They do **not** establish an adaptive information boundary, let alone a novel optimal scheduler.

### Did it actually learn local coefficients?

Yes, under the model assumptions. In the weak regime the average absolute error over five true local stencil coefficients was:

| Probe policy | Mean absolute coefficient error |
|---|---:|
| Broadband white | **0.0062** |
| Two-phase | 0.0067 |
| Deterministic feedback (not exogenous) | 0.0310 |
| Narrowband random Fourier | 0.1421 |
| Mispaired placebo | 0.1480 |

This is important because a controller can sometimes report the right remote address for the **wrong reasons**: the feedback policy correctly located 33/40 remote links but was substantially worse at estimating the actual local law. It demonstrates why classification alone is not an adequate test of a mechanism.

## What succeeded, and what did not

**Succeeded:** without any supplied sensor-noise variance, local stencil coefficients, remote link sign or strength, the private-action IV plus split confirmation recovered all 40 hidden weak links and rejected all 40 no-link cases with broadband probing. Matching outputs to never-applied interventions failed to recover any links. Broad spectral support mattered greatly.

**Not demonstrated:** superiority of targeted probing; correctness for arbitrary nonlinear world dynamics, unknown measurement/actuation timing, temporally/spatially colored sensor noise, nonlinear observation maps, missing input channels, multiple interacting remote links, or an operator changing during the experiment. The spatial MAD threshold has no calibrated family-wise guarantee outside these synthetic conditions.

The key physical distinction is between **known input waveform** and **exogenous intervention**. Only the latter gives the IV orthogonality needed by this estimator. The private random sign is a simple sufficient condition in our specific additive simulator.

The variogram idea is deferred: a short-lag variogram combines small-scale physical variation and observation noise unless further assumptions separate them. We did **not** estimate R from the variogram, and there is no need to invent one to explain the 40/40 result. See [variogram nugget documentation](https://support.sas.com/documentation/cdl/en/statug/66859/HTML/default/statug_variogram_details02.htm), and [classical closed-loop IV](https://www.sciencedirect.com/science/article/pii/S0005109804002845).

## Next honest falsification

Destroy the assumption that the measurement is an instantaneous identity sensor of the latent field: use **colored spatial noise, delayed observations, drifting observation gains and an imperfect actuator**, then test whether cross-instrument moments still identify the true kernel. Add two remote links with unknown signs and potentially similar Fourier responses. The no-link refusal test and coefficient-error test should remain mandatory, and white probing should continue as the primary reference baseline.

## Reproduce

    python -m pip install numpy pytest
    python -m pytest -q
    python -m active_iv_gate --out results

All source code, test fixtures, world seeds, full individual outcomes, model declarations and negative controls are available in the repository and CI artifact. No real EEG or private data is involved.
