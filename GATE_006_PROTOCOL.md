# Gate 006 — Frozen stress test of private-action IV: colored sensors vs unknown actuators

**2026-11-22.** This is a stand-alone synthetic falsification protocol following [Gate 005](GATE_005_REPORT.md). It is NOT a new physical theorem, nor a claim to identify neural sources.

## The mathematical distinction

The Gate 005 conditional moment for independent private randomized commands U and future output Y is:

    E[conj(U_k) Y_next,k] / E[abs(U_k)^2] = H_k

only when the action actually enters the world through the **known ideal port** and the independent sign is exogenous.

A stationary temporally correlated sensor error epsilon may produce high dependence between epsilon_t and epsilon_(t+1), but a newly drawn private action sign conditional on the past remains orthogonal to epsilon_(t+1), provided the sensor noise is not affected by that sign and its conditional law is sign-independent. Thus a claim that any temporal correlation automatically biases active IV is false. Finite-sample covariance and selected-support thresholds may be affected; report those separately.

If the unknown physical actuator has a spatial convolution kernel G, the measured action response instead identifies the **composite** H*G. A hidden actuator spatial shift of (5,7) makes a purely local world kernel H appear shifted by (5,7) when analyzing commanded input. The direct response of (H, shifted actuator) equals that of (shifted H, ideal actuator) for *every input*: this is an exact Fourier convolution factorization ambiguity. It does NOT prove passive recordings of the evolving state could never distinguish the worlds with additional assumptions.

Similarly, if the actuator actually applies command u_(t-1) rather than u_t, a naive current-command -> next-output pairing can fail even with a perfect random instrument. Re-pairing with the known lag uses the same actual observations and restores the causal moment. **The lag-one arm is given the lag by the protocol**, not learned blindly. No claim that a generic "wider gap" repairs any noise issue.

## What is frozen

Every trial uses the Gate 005 world generator on a **64x64 periodic linear spatial field**, with randomized unknown local weights and optional one nonlocal link of unknown positive/negative coefficient. The estimator sees full-field observations and the exact *commanded* random action, not true applied action, local stencil values, link sign/address, sensor variance, or actuator distortion.

- **16 passive** transitions followed by **48 commands**, with input L2 norm exactly 0.45 each.
- New independent private random sign per command. Equal energy, same action waveform for all sensor/actuator cases with matched seed.
- Remote coefficient magnitude range 0.045–0.075, world-specific sensor SD range 0.012–0.022 (not provided to estimator).
- Source hidden offset and coefficients sampled from seeded world generator; remote and null worlds scored separately.
- Split into non-overlapping halves; gate 005's unchanged 3.4-times spatial-MAD selection and sign confirmation rule. This is a **heuristic, uncalibrated support decision**, not a family-wise significance guarantee.
- Model assumptions not removed: sparse linear shift-invariant state transition, additive action entering before transition, and independent process noise. No blind class discovery.

### Eight conditions

| Condition | Physical change | Scientific expectation, not guaranteed outcome |
|---|---|---|
| iid | Ideal actuator, independent Gaussian sensor | Gate005-like reference |
| temporal_ar085 | Temporal AR(1) observation noise rho=0.85 at each pixel | Private IV still mean-unbiased; accuracy/variance can change |
| spatial_colored | Adjacent pixels share observation noise | Moment remains mean-unbiased; spatial-MAD null errors may change |
| temporal_spatial_colored | Both sensor correlations | Same caveat, heightened uncertainty |
| independent_actuator_noise | Actual action = command + independent random 0.65×-energy perturbation | Extra variance, no systematic population IV bias if truly independent |
| unknown_gain | Actual action = 0.55× command | Fitted coefficients represent scaled world law; remote address may remain correct |
| shifted_actuator | Actual action = spatial shift(+5,+7) of command | Composite kernel can produce false distant link even in a no-remote world |
| delayed_actuator | Actual action uses previous command | Zero-lag moment may miss the law; explicitly aligned lag-one arm may recover it |

### Registered independent evaluation

- **Remote worlds:** seeds 4501–4540 (40 fresh hidden offsets).
- **No-link worlds:** seeds 5501–5540 (40 null worlds).
- 8 conditions × 80 unique worlds, plus a second analysis of the same 80 delayed-actuator recordings with the **correct lag supplied**. These are **720 analytic rows**, but only 640 distinct world-condition trajectories.
- Primary outputs: exact remote-address recovery, correct null refusal, falsely reported remote connections, mean absolute error against physical world local coefficients, and mean error against the actual command-to-output composite kernel.
- The null acceptance test must count any alleged nonlocal link as a false positive even if the *composite actuator response* really contains that distant term.
- Development and unit tests use unrelated seeds 701–708 and 801–808.
- Keep all failures. Do not retune threshold or add selective cases after seeing fresh seed results.

## Strong adversarial questions

1. Does private randomization preserve the **population** moment under external temporally colored sensor noise? Test algebraically and by Monte Carlo, not by equating correlation with IV bias.
2. With a shifted actuator, can a no-link world be **mistaken for a remote-link world**? A strong *yes* would prove that observed input/output kernels cannot be attributed to the internal world without actuator calibration.
3. Can unknown actuator gain make fitted coefficients inaccurate even when the address is recovered correctly?
4. Does a one-step actuator lag create a misaligned instrument; does a **given**, corrected lag repair recovery from the same observations?
5. Do stochastic actuator disturbances independent of the commanded input act primarily as extra variance rather than systematic expected kernel bias?
6. Is the existing split-MAD null threshold reliable under spatially or temporally correlated sensor noise? Report false links rather than hiding behind apparently correct fits.

This program does **not** test correlated noise induced *by* the intervention (for example, electrically coupled sensor artifacts driven directly by action); such coupling violates the exclusion restriction more severely and is a future gate.

## Scientific status

Known prior art: random-excitation system identification, instrumental variables with closed-loop dynamics, convolution factorization ambiguities and errors from actuator calibration. A hidden actuator filter destroys unique physical attribution of the inferred command-response operator. We make these claims narrow and testable instead of calling them a new universal theorem.

## Reproduction

    python -m pip install numpy pytest
    python -m pytest -q
    python -m sensor_port_gate --quick
    python -m sensor_port_gate --out results

The GitHub Actions workflow saves every seed's hidden truth, reported offset, local-world vs effective-kernel coefficient error, lag choice, and refusal outcome. No real EEG, private files, or external physical signals are involved.
