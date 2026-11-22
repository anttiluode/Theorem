# Gate 007 — The echo sometimes reveals the world. Sometimes it reveals only the instrument.

**22 November 2026. Completed, not a new theorem.** [Successful GitHub Actions run](https://github.com/anttiluode/Theorem/actions/runs/45047960483): **59 automated tests passed**, and the full frozen study completed. [Every per-seed record](https://github.com/anttiluode/Theorem/actions/runs/45047960483/artifacts/14764790289) · [Committed numerical summary](results/gate007_summary.json) · [Protocol](GATE_007_PROTOCOL.md) · [Source](multilag_gate.py).

## The question

Gate 006 showed a serious physical attribution failure: when a hidden actuator spatially shifted its intervention, a world with **no internal remote connection** appeared to possess a remote shortcut in **40/40 no-link cases**.

Neon caught an important qualification: **the first response is not the whole observable experiment**. An actuator applies a perturbation to a continuing world; the world applies its own dynamics at every subsequent time step. Comparing *successive causal echoes* can cancel an unknown actuator and recover the internal propagation law.

The answer from Gate 007 is conditional:

- **Yes** for a hidden spatial actuator shift, when later responses are sufficiently excited and invertible.
- **Yes** for a **memoryless** direct sensor bypass, but only by starting from the uncontaminated later responses.
- **Not reliably** for a separate sensor circuit with its own ongoing ringing. Some cases are **exactly ambiguous** even with noiseless multi-lag impulse responses.
- Under the simulated assumptions, an **independently calibrated sham sensor** that measures the bypass but not the world restores physical-link decisions, while an unrelated fake sham does not.

## The exact mechanism

Let the hidden spatial world be a linear periodic convolution H, the unknown actuator G, the direct sensor bypass D, and its own ringing filter K:

    x[t+1] = H * (x[t] + G*u[t]) + process_error
    z[t+1] = K*z[t] + D*u[t]
    y[t+1] = x[t+1] + z[t+1] + sensor_error
    sham[t+1] = z[t+1] + independent_sham_error

Here * denotes spatial convolution. The sham's direct access to the bypass z, together with the absence of the world x from that channel, is a **special instrument-construction assumption**. A real sham electrode or wire may not match the measurement coupling or phase, so its physical validity would need calibration.

With independently randomized private commands, the ideal causal action-to-primary-sensor transfer at lag l is

    R_l = H^l G + K^(l-1) D

counting the first *next-frame* response as l=1. This is a sequence of classical **Markov parameters / impulse-response operators**.

**Unknown actuator, no sensor bypass:** R1=HG, R2=H²G. If R1 is invertible, R2/R1=H. The actuator cancels. No sham is needed to identify H in this ideal case.

**Memoryless sensor bypass:** K=0. The first echo R1 contains D; R2=H²G and R3=H³G do not. If R2 is invertible, R3/R2=H. This distinguishes a transient sensor pickup from a world pathway.

**Detector rings with the same dynamics as H:** K=H. Then

    R_l = H^l G + H^(l-1) D
        = H^l (G + H^-1 D).

Every one of those responses is **exactly identical to a different model with no sensor bypass and effective actuator G' = G+H^-1D**. Even perfect, noiseless measurements of all impulse lags identify H but do **not** uniquely assign the initial response to the actuator versus the detector. Here the extra sham measurement genuinely adds information about the physical pathway. It is *one possible* additional calibration; it is not the only mathematically conceivable way.

**Detector has a different ringing law K:** In general R2/R1 and R3/R2 need not equal H. Correctly subtracting independently measured z restores an H-only echo sequence; subtracting unrelated noise does not.

These are established linear-system facts. No claim of new mathematical priority is made.

## Frozen study design

The method and test seeds were documented in [GATE_007_PROTOCOL.md](GATE_007_PROTOCOL.md) before inspecting held-out outcomes.

- 64×64 periodic, **linear** spatial world, evolving continuously without resetting between actions.
- Randomized unknown local weights, one optional distant link of unknown sign/strength/location.
- Deliberately **stable and invertible** world operator: minimum Fourier response magnitude >0.30 and total impulse-kernel absolute weight <0.95. This favorable assumption is crucial to testing the ratios, and is not guaranteed for natural fields.
- 256 independent, privately randomized white interventions per world, each Euclidean norm 0.85.
- Primary sensor noise SD 0.006 per pixel, sham noise SD 0.004, independent process innovation SD 0.00025.
- Causal cross-spectral transfer estimates for lags 1, 2 and 3. Fixed numerical ridge = 0.005 × median observed denominator spectral power, with a nonzero numerical floor on unexcited data.
- Compare naive first echo, R2/R1, R3/R2, sham-subtracted ratios, independent sham detection and a **fake noise-only sham**.
- Candidate remote support must exceed the existing Gate 005 **3.4× spatial median-absolute-deviation** heuristic and agree in sign across two nonoverlapping time blocks. This is **not** a family-wise significance test; the two blocks share one dynamic trajectory.
- 20 new remote seeds **7101–7120** and 20 no-link seeds **8101–8120** for **each** of five conditions, for 200 condition-specific simulation trajectories. Seed numbers are reused across conditions for *paired comparison*, and the seven analysis arms use the same underlying trajectories. These are **not 1,400 independent worlds**.

The physical stress conditions are: ideal sensor/actuator; spatially shifted actuator (+5,+7); memoryless detector bypass at (+5,+7); detector ringing with K=H; and detector ringing with K=0.55 I.

## Held-out results

Each pair of counts below is **exact true remote address recovered / 20 real-link worlds** and **correct no-link refusal / 20 true no-link worlds**. An incorrect no-link decision means the estimator invented a physical distant connection.

| Hidden physical condition | First echo alone | Successive R2/R1 | Later R3/R2 | Correctly wired sham + R2/R1 |
|---|---|---|---|---|
| Ideal | **20/20 · 20/20** | **20/20 · 20/20** | **20/20 · 20/20** | **20/20 · 20/20** |
| **Secretly shifted actuator** | 0/20 · 0/20 | **20/20 · 20/20** | **20/20 · 20/20** | **20/20 · 20/20** |
| **Memoryless sensor bypass** | 0/20 · 0/20 | 0/20 · 0/20 | **20/20 · 20/20** | **20/20 · 20/20** |
| **Ringing bypass, K=H** | 0/20 · 0/20 | 20/20 · **0/20** | 20/20 · **1/20** | **20/20 · 20/20** |
| **Ringing bypass, K=0.55 I** | 0/20 · 0/20 | 20/20 · **0/20** | 20/20 · **0/20** | **20/20 · 20/20** |

The second ratio after correctly wired sham subtraction (R3/R2) also recovered **20/20 real links and rejected 20/20 nulls in every physical condition**. The unrelated fake-sham did not repair the memoryless or ringing bypass: it retained **20/20 false connections** in those null conditions using the early ratio.

The sham-alone trace showed a distant bypass response in every bypass condition and none in ideal/shifted-actuator conditions in these held-out cases. **That response belongs to the sham sensor channel.** Treating it as a physical world connection would itself be a category error.

### Why the exact matched-ringing ratio still produced false links in finite samples

There is no contradiction between the exact identity R2/R1=H when K=H and the **20/20 false no-link detections** produced by this particular *estimated* ratio.

The identity uses the exact transfer operators and assumes nonzero denominator at every relevant mode. Here the estimator estimates two complex impulse responses with **finite, noisy data**, and then divides them. Sensor ringing can create partial spectral cancellation in the observed composite response, making some frequency bins ill-conditioned. Numerical stabilization and a spatial threshold do not magically supply the missing information. In the null worlds this produced apparent distant coefficients that passed the exploratory two-window threshold.

A properly calibrated sham subtracts the bypass response *before* taking the ratio, improving the conditioning and removing the false physical support in this chosen simulator. The ratio estimator cannot currently calibrate its own error bars or abstain reliably when the measured denominator is near zero. That is an important limitation for a future scientific instrument.

## A second exact identifiability certificate: unknown spatial sensor coordinates

An unknown invertible sensor transformation C changes the measured world transition to **C H C^-1**, not H. A compact 8×8-grid finite-matrix test used a hidden permutation C:

- Physical world: only local nearest-neighbor connections, **0 nonlocal edges**.
- Observed, permuted sensor coordinate graph: **242 apparent nonlocal edges**.
- Exact transformed trajectories and eigenvalues agree numerically (to floating-point tolerance).

Thus even observing the entire infinite-time impulse sequence does **not** recover *physical spatial addresses* unless the sensor coordinate map is calibrated or independently constrained. This certificate uses exact matrices, not blind/noisy fitting, and the permuted operator is not necessarily shift invariant in sensor coordinates. A sham bypass electrode by itself does not necessarily identify C.

## What it means for HeadAsResonator3

A strong audio→electrode transfer, phase-coherent peak or correct inverse fit describes a recorded relationship. It does not uniquely distinguish mechanical/acoustic vibration, electronic reference coupling, facial muscle activity and actual neural participation.

Gate 007 now states which **additional evidence** might help in a suitable physical experiment:

- A response that persists according to the internal dynamical law over multiple impulse-response lags can support a real dynamical pathway rather than a memoryless sensor bypass.
- A dummy sensor or independently calibrated detector path can expose sensor-only feedthrough even when that path rings and resembles the world.
- A separately calibrated spatial sensor map and actuator geometry are needed to assign a remote link to actual *anatomical* coordinates.
- Independent intervention is valuable, but cannot on its own factor a composite measurement into unique physical sources.

The existing public speech-EEG dataset is passive overt speech, not a controlled randomized actuator experiment. The Gate 007 results **do not** label the HeadAsResonator3 residual pickup as skull, jaw, electrode or amplifier.

## Prior art and current boundary

Impulse-response/Markov-parameter methods, direct-feedthrough terms, and similarity ambiguity are standard system identification; [MIT Underactuated Robotics, system identification](https://underactuated.csail.mit.edu/sysid.html) explicitly presents the state-space model with A, B, C, D and the Ho–Kalman realization problem. [Eigensystem Realization Algorithm documentation](https://www.mathworks.com/help/ident/ref/era.html) covers state-space fitting from impulse responses.

**Established here:** exact linear identifiability examples and a reproducible synthetic intervention benchmark showing when later echoes suffice and when a second sensor helps.

**Not established:** a novel general theorem, robust ratios with dark/zero bands, fully blind model family selection, calibration of an unknown sham gain/lag, a corrected no-link p-value, nonlinear or nonstationary systems, or anatomical/clinical conclusions.

## Next decisive stress test

Have the sham *fail subtly*: unknown gain, latency or frequency response; multiple physical bypass filters; an actuator that itself rings; or direct action-dependent sensor contamination. Develop a **joint multichannel calibration and refusal rule** that estimates whether the extra sensor truly identifies D, instead of assuming it does.

In particular, a detector signal that is itself driven by the commanded action can be statistically **causal** and still entirely separate from the internal world. The instrument needs to explicitly report *what is observed*, *what remains equivalent*, and *which independent calibration would resolve the ambiguity*.

## Reproduce

    python -m pip install numpy pytest
    python -m pytest -q
    python -m multilag_gate --out results

[Full source](multilag_gate.py) · [Tests](tests/test_multilag_gate.py) · [Frozen protocol](GATE_007_PROTOCOL.md) · [Complete CI artifact](https://github.com/anttiluode/Theorem/actions/runs/45047960483/artifacts/14764790289) · [Persistent compact summary](results/gate007_summary.json).
