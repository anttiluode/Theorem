# Gate 007 — Frozen protocol: multi-lag physical attribution and sham sensor

**Declared before inspecting fresh held-out seeds, November 22, 2026.**

This gate responds to Neon's correction to Gate 006: a hidden actuator spatial shift can be canceled from **successive impulse-response lags** if the world state dynamics are homogeneous, the sensor measures the world in known coordinates, the relevant response is invertible, and no sensor bypass contaminates those lags.

## 1. Precise world and measurement geometry

On a periodic 64×64 field, simulate one continuously evolving linear system, with independently randomized command u[t]:

    x[t+1] = H * (x[t] + G*u[t]) + w[t]
    z[t+1] = K*z[t] + D*u[t]
    y[t+1] = x[t+1] + z[t+1] + eps[t+1]
    sham[t+1] = z[t+1] + eps_sham[t+1]

Here H is the hidden world kernel, G an actuator, and z a potential parallel *sensor-only* bypass. The sham is a **second instrumented measurement** that receives detector bypass z but **not** the latent world x, with independent additional observation noise. A *fake sham* contains unrelated noise and is required to fail.

**Assumptions given to the estimator:** recorded independently randomized command waveforms/timing, 64×64 periodic spatial convolution class, ability to observe up to the third causal echo, and the sham port when that analysis arm is enabled. No true H, G, D, K, coefficient weights, remote link address/sign, or sensor-noise variance is provided to the estimator.

All simulator worlds have independently sampled local coefficients, optional one remote link of unknown sign/address, and a **strictly stable, invertible H** by construction (minimum transfer magnitude >0.30). This is deliberately favorable for spectral division and MUST remain in the limitations. The remote link belongs outside a fixed local radius.

## 2. Exact identifiability boundary

For causal action→measurement transfer at lag l (counting first next-frame effect as l=1),

    R_l = H^l G + K^(l-1) D.

The simulator model permits three claims:

- **No bypass D=0:** R2/R1 = H if R1 has no zero frequency modes. An unknown invertible spatial actuator shift is canceled; R1 alone would mistakenly show a distant displaced kernel.
- **Memoryless bypass K=0:** R1 = HG+D but R2=H²G and R3=H³G, so R3/R2 = H when R2 invertible. The bypass is absent from the later causal echoes.
- **Matching ringing K=H:** all Rl are consistent with **an alternative effective actuator** G'=G+H^-1 D, because Rl=H^l G' for all l. Multi-lag data can identify H while remaining **unable to allocate the initial transfer between actuator and sensor bypass**. The proposed sham can expose D directly. This ambiguity is exact, not merely poor estimator performance.

For ringing K≠H, neither ratio necessarily equals H, and a sham can recover the world-only transfer under its own calibration assumptions.

**A separate finite 8×8 matrix certificate** permutes sensor coordinates by an unknown invertible C: the observed transition becomes C H C^-1, preserving trajectories and eigenvalues but changing the apparent locality of physical links. This is a known state-space similarity ambiguity, **not a blind numerical recovery test**. A sham alone need not reveal C.

## 3. Frozen measurement and analysis

- **Five declared cases:** ideal channel; unknown actuator shift (+5,+7); memoryless direct sensor bypass at (+5,+7); sensor-only ringing with K=H; and sensor-only ringing with K=0.55 I.
- **World parameters:** local self coefficient drawn 0.60–0.65 and four cardinal coefficients 0.035–0.050, optional remote strength |c|=0.075–0.095 at a random distant position. The sum of absolute kernel weights is <0.95 and the minimum transfer magnitude >0.30.
- **Actions:** 256 independent white spatial perturbations with Euclidean norm exactly 0.85, independent private random sign. No reset between actions; process innovation SD 0.00025; primary sensor SD 0.006; sham SD 0.004.
- **First three lags:** complex cross-spectrum average of current u[t] with observed y[t+lag] (using code's first-next-frame = lag 1 convention), dividing by average commanded input spectral power. Source action signs are exogenous. Two nonoverlapping time segments: first 128 vs last 128, without pretending the latent trajectories are statistically independent.
- **Ratios:** direct inverse FFT of R1 (the deliberately naive control); ridge-stabilized R2/R1; ridge-stabilized R3/R2. Ridge fixed at 0.005 times median |denominator|² of **observed** response. No H, G or D is given to this numerical estimator.
- **Correctly wired sham:** subtract its observed waveform from the primary measurement, estimate the first two/three lags again. Includes sham measurement noise. Separate sham-only response should identify direct bypass.
- **Mismatched fake sham:** subtract a separate independent noise-only channel as a negative control. It must not produce the same benefit as a real sham.
- **Remote detection:** Gate 005's same spatial 3.4 × robust-MAD threshold, first-half selected remote term confirmed with same sign and threshold in the second segment. **Not a familywise-calibrated p-value.**

## 4. Unseen holdout and registered tests

- Development seeds 701–703 and 801–803 were used to check script behavior at 128 actions.
- **Unseen remote worlds:** seeds 7101–7120, 20 per physical case.
- **Unseen no-link worlds:** seeds 8101–8120, 20 per physical case.
- 5 cases × 40 worlds = **200 independent simulated world-condition trajectories**. Seven estimator arms analyze the **same** trajectories. Thus the result count is not 1,400 independent worlds.
- Additional exact operator identities and sensor-basis matrices are numerical proof certificates, not new stochastic world trials.

**Outcomes:** exact remote address recovery when physical H contains a remote link, correct refusal when H is local-only, false physical remote link attribution, mean absolute local coefficient error, whether the sham independently sees the bypass, and all failures. The judge sees truth only for scoring.

**Predictions to falsify, not promised results:** With actuator shift and D=0, R2/R1 should recover H and reject false links, unlike R1. With memoryless sensor bypass, R3/R2 should recover H; the sham should help earlier. A ringing bypass K=H remains physically unidentifiable as a distinct bypass from only the main channel, despite recoverability of H under exact ratios. The sham should expose the bypass, but can itself fail under sensor-noise or calibration assumptions. Nonmatching ringing can confound the ratio; subtraction should remove its separate channel if sham is correctly wired.

## 5. Prior art and epistemic boundary

This is classical **Markov-parameter and impulse-response system identification**, including direct feedthrough and state-space similarity transformations. See [MIT Underactuated Robotics, System Identification](https://underactuated.csail.mit.edu/sysid.html), [standard state-space impulse-response representations](https://www.mathworks.com/help/ident/ref/era.html), and [state-space realization similarity invariance](https://www.mdpi.com/2624-599X/3/3/37).

**Not claimed:** newly discovered theorem, unique detection of a ringing detector path from one output, world-operator recovery under arbitrary sensor mixing, reliable ratio inversion if frequencies are dark, real-world anatomical localization or diagnosis, formal FWER control, automatic blind timing calibration, or physical equipment experiments.

**Original research question:** Can a practical instrument track *which physical distinction additional echoes genuinely resolve*, refuse to assign an internal link when the ambiguity persists, and specify the second measurement required to break it?

## Reproduction

    python -m pip install numpy pytest
    python -m pytest -q
    python -m multilag_gate --quick
    python -m multilag_gate --out results

The GitHub Actions workflow archives complete per-run JSON receipts and derived summaries only. No EEG or user-private recordings are used.
