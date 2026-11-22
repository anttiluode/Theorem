# Theorem Gate 008 — The pulse reveals curvature. The sensor can lie about it.

**Completed 22 November 2026, frozen independent holdout.** [Passing GitHub Actions run](https://github.com/anttiluode/Theorem/actions/runs/45050940878), **72 automated tests passed**. [Full 1,240-case per-seed JSON artifact](https://github.com/anttiluode/Theorem/actions/runs/45050940878/artifacts/14765286977) · [Preregistered protocol](GATE_008_PROTOCOL.md) · [Source](equilibrium_gate.py) · [Committed numerical receipt](results/gate008_summary.json).

## 1. Why this follows Claude's Luotain2 findings

Claude's [ESTIMATED_R_GATE](https://github.com/anttiluode/Luotain2/blob/main/ESTIMATED_R_GATE.md) discovered a sharp weak-excitation limit: below 2% process excitation, the Allen–Cahn field frequently relaxes toward nearly stationary phase domains, so an identity shortcut predicts its passively observed states while diffusion and cubic reaction become poorly identifiable. Claude independently estimated Gaussian observation variance in its nonlinear polynomial search, recovering 12/12 laws at 4% sensor noise and 10/12 at 8%, versus 11/12 at 8% with true R given. This does not mean it has already solved arbitrary real-sensor calibration or this active experiment.

We deliberately avoided another linear actuator simulation and asked the experimentally different question:

**Can a carefully designed perturbation distinguish reaction from diffusion at a bulk equilibrium, without knowing D, r, or observation-noise variance R?**

Yes, in the restricted experiment below. More importantly, **a nonlinear detector can fake the very reaction signature the optimal pulse is designed to expose.**

## 2. A concrete nonlinear, exact, symmetry-based observable

A 32×32 periodic field has candidate one-step law

    F(v;s) = v + D*Lap(v) + a*(v-s) + r*(v-v³).

The physical Allen–Cahn world has D>0, r>0 and a=0. The phase-dependent linear surrogate a(v-s) is an alternative locally linear response; it is **not** a globally valid Allen–Cahn physical equation. The learner knows this candidate grammar, not the true support or coefficient values.

The equilibrium s is either −1 or +1. All these laws satisfy F(s;s)=s; consequently unlimited noiseless passive observations of the same uniform equilibrium do **not** reveal D, r or a.

For **two separately prepared copies of the identical state**, apply +u to one and −u to the other. The two noise-free output responses obey exact identities:

    E(u) = [F(s+u)+F(s-u)]/2 - s = -3*s*r*u².

    O(u) = [F(s+u)-F(s-u)]/2 - u
         = D*Lap(u) + (a-2*r)*u - r*u³.

This is the key separation. Spatial diffusion and linear restoring response are odd in the perturbation and cancel in the **even** response. The even response can isolate the cubic reaction's curvature; after estimating r, the odd response estimates D and a. Using spatially centered E and u² removes an arbitrary constant offset per pair.

This is an instance of ordinary **symmetric finite-difference response analysis and optimal experiment design**, not a newly discovered theorem. It assumes the two copies truly start in the same hidden state; otherwise systematic preparation mismatch can fake the even response.

## 3. Hidden variables, power fairness, and model selection

Each world has a randomly drawn D in [0.11,0.19] if diffusion exists, r in [0.14,0.26] if cubic reaction exists, and a in approximately [-0.52,-0.28] for the local-linear surrogate. The fitter never receives them. Each world draws Gaussian sensor SD in [0.07,0.09], independently from the physical law. Process innovation SD is 0.003.

Four matched ±pulse pairs are available. The solver uses only each pair's **recorded pulse, measured positive/negative responses, and the equilibrium sign inferred from a noisy baseline**. It estimates its own residual-based standard errors and requires coefficient detection above 3 estimated SE, with consistent sign in **each** two-pair half. The test is a **heuristic support rule**, not a family-wise-adjusted hypothesis test, and it does not identify an arbitrary law outside the supplied grammar.

Every active input has identical L2 energy (pixel RMS 0.055) and must obey exactly the same per-pixel displacement cap (0.16):

- **White:** clipped and renormalized Gaussian random spatial field.
- **Targeted sparse:** a randomly located, amplitude-saturated sparse field. This maximizes the candidate cubic-curvature information proportional to sum((u² - mean(u²))²) given total energy and a pixelwise cap; the optimizer knows *possible* cubic features but not true parameters.
- **Single Fourier:** one spatial cosine; the low-dimensional response can make Lap(u) and u collinear. The fitter must refuse near-singular D/a fits.
- **Passive:** no intervention. No evidence about physical coefficients at constant equilibrium.
- **Mislogged input:** a real white pulse is delivered, but the solver is told a different never-applied pulse, revealing the importance of correct actuator records.

The explicit **physical measurement trap** uses a truly diffusion-only world (r=0) but replaces its primary sensor with a deliberately nonlinear front end:

    measured = physical_output + q*s*(physical_output-s)² + sensor_error,

with q drawn in [-3.8,-3.2]. A separate idealized linear reference sensor measures the same latent transition without this distortion. The reference is **an additional trusted physical measurement** and its correctness is not inferred.

Design/debugging used seeds 10–49, 301–340 and 1001–1040. These are **not** holdout evidence. The protocol was committed before evaluating the entirely new **2001–2040** seeds: 40 seeds per world/policy, five policies over six world types, and one extra trusted-reference arm: **1,240 comparisons**, sharing seeds across conditions for matched analysis, not 1,240 independent laws.

## 4. Frozen holdout results — physical Allen–Cahn

| Probe method | Physical diffusion detected | Physical cubic reaction detected | Full Allen–Cahn support exactly correct |
|---|---:|---:|---:|
| Passive | 0/40 | 0/40 | 0/40 |
| White random pulse | 40/40 | **1/40** | 0/40 |
| **Targeted sparse pulse** | **40/40** | **27/40** | **27/40** |
| Single Fourier mode | 4/40 | 0/40 | 0/40 |
| Mislogged unrelated pulse | 0/40 | 0/40 | 0/40 |

The targeted method outperformed broadband white under equal L2 energy and equal local amplitude cap for **this specific nonlinear curvature measurement**. This is notably different from Theorem's earlier Gates 004–005, where broadband white was better at searching thousands of unknown **linear spatial addresses**.

The difference is *which feature needs excitation*: for an unknown shift in a linear convolution, wide spectral support helps; for cubic reaction around a known equilibrium, the squared perturbation's spatial contrast matters, and concentrated amplitude-limited pulses increase that feature-specific information.

Across the 40 true Allen–Cahn holdout worlds, mean absolute r estimation error was **0.0230** with targeted sparse input versus **0.0632** with white input. Mean D error was 0.0069 versus 0.0086. White identified D but often missed the reaction and even reported a spurious linear term in **8/40** cases; the targeted method reported no spurious linear terms in this true Allen–Cahn set.

The reaction-only world repeats the nonlinear detection contrast: **27/40 targeted** versus **1/40 white**, with diffusion appropriately not detected in either. Two linear-world controls matter:

| True world | Targeted exact support | White exact support | False cubic from targeted |
|---|---:|---:|---:|
| Diffusion-only | **40/40** | 32/40 | 0/40 |
| Linearized phase-conditioned surrogate | **37/40** | 27/40 | 0/40 |
| Identity/no law | **40/40** | 32/40 | 0/40 |

The passive identity world also scored 40/40 as empty support, but this is **default abstention**, not positive identification of its physics: passive data cannot distinguish identity from the other equilibrium laws.

## 5. The physical measurement trap — a detector can manufacture a cubic law

In the **quadratic-detector world**, the *actual physical field is linear diffusion* (D>0, r=0). Only the detector adds a nonlinear response. Under the targeted sparse perturbation, the solver nevertheless inferred a **physical cubic reaction in 21/40 worlds**. White input produced 3/40 such errors; a single Fourier input, which is otherwise a weak way to identify diffusion, produced **34/40 false cubic detections**.

This is especially important: an informative pulse can magnify not only the internal law's curvature but also unmodeled **sensor curvature**. A strictly valid identification rule for the world needs a sensor model or independent calibration—not merely a more energetic or more statistically significant stimulus.

The independent **trusted linear reference sensor** corrected the attribution in all **40/40** of those same-world cases: it made **0/40 false cubic claims** and recovered exact diffusion-only support **40/40**. This is a strong simulated physical-calibration assumption, not a claim that arbitrary real sham sensors or reference wires have trustworthy response.

The **wrongly logged action** was another failure: it never recovered the physical reaction in the true Allen–Cahn worlds (**0/40**), but still reported a **spurious local linear relaxation term in 40/40** of them. Under an incorrectly recorded intervention, apparently decisive regression can tell a coherent but physically wrong story.

This unifies the lesson of Gate 007 with a genuinely nonlinear field. A detector or intervention port can acquire the exact statistical signature of a term in the intended physical grammar, without the term existing inside the world.

## 6. What is demonstrated and what remains unproven

**Demonstrated in this frozen synthetic benchmark:** strong nonlinear equilibrium ambiguity under passive observation; exact even/odd response separation; 27/40 nonlinear support recovery using targeted sparse pulses versus 1/40 nonlinear detections with equal-energy white probes; estimated coefficients without a supplied R; and a successful independent-sensor attribution control on 21/40 false nonlinear primary detections.

**Not demonstrated:** a general closed-loop experiment on an unreset Allen–Cahn phase-domain field; unknown dynamics outside the supplied Lap/linear/cubic grammar; physical repeatability of identical equilibria; robustness to spatially/temporally correlated or state-dependent sensor noise; a calibrated false-discovery probability; a universal superiority of targeted impulses; or recovery of a real-world biological/optical/thermal law.

A new theorem would require a precise claim beyond standard symmetric finite differences and optimal design, together with appropriate proof and prior-art comparison. This gate is a controlled engineering result that narrows the scientifically meaningful uncertainty.

## 7. Next real-world test, not another synthetic victory lap

The hardest assumption now is experimental reality: an actual physical system does not generally supply perfectly cloned latent states with known applied pulses and an idealized reference detector.

A strong next direction is a **public experimental recording with controlled input pulses, independent measurements of the physical input and the detector, and known raw timing**—for example a mechanical resonator, thermal actuator experiment, an optical trapping calibration series, or a documented electronics input/output benchmark. Test whether the even response is reproducible in real hardware, whether the detector reference suppresses a fake nonlinearity, and whether the instrument can abstain when the source path cannot be separated.

Do not equate this synthetic gate with a solution to Luotain2's low-excitation nonlinear *passive* state-space problem or to HeadAsResonator3's passive EEG signal-source attribution.

## Reproduce

Windows PC:

    py -3.13 -m pip install numpy pytest
    py -3.13 -m pytest -q
    py -3.13 -m equilibrium_gate --out results

[Full Python source](equilibrium_gate.py) · [frozen method](GATE_008_PROTOCOL.md) · [verified 72-test workflow](https://github.com/anttiluode/Theorem/actions/runs/45050940878) · [per-seed artifact](https://github.com/anttiluode/Theorem/actions/runs/45050940878/artifacts/14765286977).
