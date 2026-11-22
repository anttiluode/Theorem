# Gate 006 — The false wormhole was in the actuator

**22 November 2026. Completed.** [Successful GitHub Actions evaluation](https://github.com/anttiluode/Theorem/actions/runs/45044598034) with **49/49 automated tests passing**. [Complete held-out individual receipts](https://github.com/anttiluode/Theorem/actions/runs/45044598034/artifacts/14762208996) · [Frozen protocol](GATE_006_PROTOCOL.md) · [code](sensor_port_gate.py) · [permanent compact summary](results/gate006_summary.json).

## The scientific finding is a *negative attribution result*

Theorem Gate 005 showed that a fresh private randomized action could identify a hidden remote spatial link without being given R or actual kernel coefficients. Gate 006 now tests how much of that statement survives when the **sensors and actuators** have their own dynamics.

The sharp result: **the same algorithm reported a nonexistent remote connection in all 40 truly no-link worlds** when the actuator secretly shifted every injected pattern by (5,7) pixels. The numerical inverse was recovering a real *command-to-observation response*, but that response was not the internal world operator.

That is a direct, falsifiable analogy to HeadAsResonator's central epistemic distinction: excellent signal transfer does not uniquely establish which material or apparatus carried the signal. It does **not** demonstrate any head/EEG source path.

## Precisely what the estimator learned

Let H be the internal linear spatial convolution of the evolving state and G the actuator's transfer from the **recorded commanded action** u to the **actual applied field**. For private randomized interventions whose signs are independent of latent history and upcoming observation noise,

    x[t+1] = H * (x[t] + G*u[t]) + w[t]
    y[t+1] = x[t+1] + eps[t+1]

the causal cross-spectral moment identifies

    K(k) = E[conj(U[k]) Y_next[k]] / E[|U[k]|^2]
         = H(k) G(k)

under the stated conditional exogeneity and enough excitation.

**K is the composite response, not H.** If G is unknown, factoring K into H and G is in general nonunique. For a hidden spatial shift G(u)=shift(u,+5,+7), convolution commutes with the shift, so

    H * shift(u,+5,+7) == shift(H,+5,+7) * u

for every intervention waveform u. In a true no-link world with a local-only H, the second expression has a remotely shifted *effective* kernel. The estimator, incorrectly assuming G=identity, selects that displaced local response as a remote link.

This is an exact equality of **immediate action-response operators**. It does *not* assert that both factorizations are observationally equivalent under all possible autonomous state trajectories, multiple independent actuators, spatial sensor layouts, or additional calibration evidence.

## Frozen real experiment settings

The study uses the 64x64 **synthetic Luotain2-inspired linear convolution** world from Theorem Gate 005, with newly drawn hidden local kernel coefficients and, when present, one randomly placed remote link of unknown sign and magnitude 0.045–0.075.

All trials have 16 passive steps and 48 independently signed white spatial interventions with commanded Euclidean L2 norm 0.45, on one evolving trajectory without resets. Every world has independent unknown-to-estimator sensor standard deviation in 0.012–0.022. Process innovation SD is 0.0005 per pixel. Kernel estimation is by the same Fourier IV cross-moment and the same first/second-half **heuristic 3.4 spatial-MAD remote-link selection rule** from Gate 005. No threshold was changed after seeing results. **The MAD rule is not a calibrated family-wise false-positive test.**

The registered holdout uses 40 new remote worlds (seeds 4501–4540) and 40 separately seeded no-link worlds (5501–5540) **for each condition**. The delayed-actuator condition is reanalyzed under two timing hypotheses on exactly the same trajectories. There are 640 simulated world-condition trajectories plus 80 alternative lag analyses—not 720 independent worlds.

## Results

| Physical sensing / actuator condition | True remote address recovered | No-link worlds correctly refused | Mean MAE for five true local weights |
|---|---:|---:|---:|
| Independent Gaussian sensor (reference) | **40/40** | **40/40** | 0.0046 |
| Temporal AR(1) sensor noise, rho=0.85 | 39/40 | 40/40 | 0.0046 |
| Spatially correlated detector noise | 40/40 | 40/40 | 0.0046 |
| Both temporal AR and spatial correlation | 39/40 | 40/40 | 0.0047 |
| Independent unmeasured actuator noise, 65% action norm | 40/40 | 40/40 | 0.0046 |
| Actual action gain 0.55× commanded (unknown) | **15/40** | 40/40 | **0.0672** |
| Actual action spatially shifted (+5,+7), unknown | **0/40** | **0/40 — 40 false links** | **0.1490** |
| Actual action delayed one frame, naively paired | 0/40 | 40/40 | 0.1490 |
| **Same delayed world, correct lag supplied to analysis** | **40/40** | **40/40** | **0.0046** |

All results derive from synthetic worlds. Values above are mean absolute coefficient errors against the *internal physical operator*, not only against the combined command-response kernel.

### The colored-sensor correction to Neon's hypothesis

Noise with temporal correlation rho=0.85 **did not systematically bias the private IV moment**. Full correct recovery remained 39/40 for remote worlds and 40/40 for no-link worlds, with local weight error nearly unchanged. Adding nearest-neighbor spatial detector noise also preserved 40/40 full recovery and refusal in this finite evaluation.

The key condition is not "no temporal correlation," but **the new private intervention sign is exogenous to the sensor error at the measured future step**, conditional on the history used to choose its spatial waveform. Autocorrelation can still affect finite-sample variance, effective sample size, and thresholds. Forty trials do not prove a universal guarantee. Merely widening the instrument gap to bypass sensor AR noise is *not* inherently necessary; a wider gap can itself misalign the causal actuator-response moment.

### What additive independent actuator noise did

The actuator applied commanded u plus an independent random spatial perturbation of Euclidean norm 0.65×command budget. Since the added actuator error is independent of the private sign, the command cross-moment remains an unbiased estimate of the desired H in expectation in this simulator, though variance can change.

Empirically 40/40 remote addresses and 40/40 null refusals survived. This is *not* a claim about input errors that depend on the hidden state, command sign, amplifier saturation or electronics-induced sensor pickup.

### Why the unknown-gain result matters

The physical actuator applied **0.55×** the recorded commanded action. The IV then tends to estimate **0.55H**, not H, even when it has found the correct spatial address. That reduces weak-link signal strength and the remote identification rate to **15/40**, while local coefficient error against the true physical H rises to 0.0672.

This is an *identifiability limitation*, not primarily a new bad optimization method: a single observed action channel with unknown gain cannot determine the absolute internal operator scale from that action-response moment alone without additional information. Passive state dynamics, repeated independently calibrated actuation channels or other physical constraints may help.

### The alignment kill test

When the actual actuator applied the **previous frame's commanded action**, incorrectly pairing current u[t] with next observed y[t+1] recovered **0/40** remote links. Reanalyzing **the same measurements** with u[t−1] (the correct lag supplied as an external analysis assumption) recovered **40/40** and restored accurate local coefficients.

This is not blind lag discovery; the correct lag was handed to the second analysis arm. An unresolved sensor/actuator clock delay can defeat a good IV instrument even though the action is independently randomized.

## Connection to Luotain2's nonlinear polynomial gate

Claude's [POLY_GATE.md](https://github.com/anttiluode/Luotain2/blob/main/POLY_GATE.md) addresses a different uncertainty: under known independent Gaussian sensor variance R and 2% process excitation, exact polynomial Hermite risk correction improved blind Allen–Cahn/Burgers structural recovery to **22/24 IV** and **21/24 LS**, with 0/48 false null-law selections. That demonstrates the importance of correct *nonlinear noise scoring*. It does not prove physical actuator calibration, and Gate 006 does not solve unknown-R nonlinear polynomial fitting.

Together these gates clarify three distinct components that cannot simply be collapsed into one "noise correction":
1. **Statistical instrument exogeneity:** is the newly randomized command independent of the unwanted disturbances?
2. **Physical input/observation calibration:** did the logged command enter the intended system at the intended spatial and temporal location?
3. **Model-specific error correction:** does the model-selection objective properly account for the observation-noise distribution and nonlinear regressors?

Success on one does not substitute for the other two.

## Important limits and next kill test

All Gate 006 worlds are linear, periodic, sparse and shift invariant. They have only one optional remote link and full-field measurements. No unidentified real experimental apparatus was used. The agent has a perfect record of what it *commanded*; the model does not estimate actuator dynamics. The lag-corrected arm is an externally supplied calibration hypothesis. No physical source/pathway has been proven.

The most direct next failure mode is **action-dependent measurement feedthrough**:

    y[t+1] = x[t+1] + C*u[t] + eps[t+1].

Even when the private action is perfectly independent of all external noise, its cross-moment then identifies **H*G + C**, which can invent a remote connection in exactly the same way as an unknown actuator filter. This is especially relevant to attempts to interpret audio-linked EEG as if the electrode were an ideal sensor of neuronal activity. To distinguish H from C requires an independently constrained sensor path, blank/dummy sensor, intervention geometry, or some other measurement that breaks the factorization ambiguity.

A second stress test should allow multiple unknown actuator ports or a delayed sensor, then ask whether an independently measured actuator calibration makes a false remote disappear. White broadband excitation should remain the strong baseline.

## Reproduce

    python -m pip install numpy pytest
    python -m pytest -q
    python -m sensor_port_gate --quick
    python -m sensor_port_gate --out results

[Run](https://github.com/anttiluode/Theorem/actions/runs/45044598034) · [full per-seed receipts](https://github.com/anttiluode/Theorem/actions/runs/45044598034/artifacts/14762208996) · [source code](sensor_port_gate.py).

**Conclusion:** an IV can correctly identify an input-output operator while failing to identify the internal physics. Under independently randomized input, unknown actuator shifts and delays can be more damaging to physical attribution than temporally correlated sensor noise.
