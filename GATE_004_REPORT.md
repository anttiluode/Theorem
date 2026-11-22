# Theorem Gate 004 — Can a learner wake up a continuously evolving, dark world?

**Status: completed synthetic intervention study, 2026-11-22.** [Passing GitHub Actions workflow](https://github.com/anttiluode/Theorem/actions/runs/45041594315): **30 tests passed**, all fresh-seed intervention and null sweeps completed. [Full per-run JSON and Markdown artifact](https://github.com/anttiluode/Theorem/actions/runs/45041594315/artifacts/14762031846). [Executable code](temporal_gate.py) · [Focused tests](tests/test_temporal_gate.py) · [Persistent summary](results/gate004_summary.json).

This is an intentionally narrow but much more realistic challenge than Gate 003's paired static input/output inverse. It is a continuously evolving world with an unknown spatial link, **one measurement stream**, no resetting during a trajectory, and small chosen disturbances.

## A. What the learner is given

The data generator is the Luotain2-inspired *linear, translation-invariant 64×64 wormhole family*:

    x[t+1] = A_d(x[t] + u[t]) + process_noise[t]
    A_d(v) = 0.6*v + 0.1*sum(4 cardinal neighbor shifts of v)
             + 0.1*(shift(v,dy,dx) - v)
    y[t] = x[t] + sensor_noise[t]

The unknown periodic offset d=(dy,dx) may be **any of 4096 spatial addresses**. The choice (0,0) is the **no-remote-link hypothesis**. All other candidates have the same declared positive coupling 0.1. The world generator chooses a previously unseen offset; only the generator and final scorer see this truth.

The **learner knows** the local reference stencil, the remote-link coefficient 0.1, that there is *at most one* remote link, the 64×64 periodic translation-invariant family, and the calibrated sensor-noise SD 0.01. It does **not** know the offset, the hidden latent state, whether there is a link, or any future measurements. Unlike full Luotain2 blind-IV, it does **not** learn all coefficients, the local law or the model grammar. This is an **address-within-a-known-family** identification problem.

The learner observes one noisy frame y[t], selects a small added spatial control u[t], and then receives one noisy frame y[t+1]. **The state is never reset within a trajectory.** The sensor measurement at t+1 is reused as the current measurement in the next transition. The external process-noise samples and sensor-noise samples are shared across compared policies for each seed, though different interventions subsequently produce different latent states.

All actions have Euclidean norm **0.45** regardless of method. The initial latent state has spatial SD **0.25**, a deliberately uninformative single 2-D Fourier rhythm. The first **24 transitions are passive**. Then the policy gets up to **16 more transitions**, each with no action or one equally powered action.

### Exact passive ambiguity, before fitting

The initial spatial Fourier index is (ky,kx)=(1,2). Under any shift-invariant linear operator, this single mode and its conjugate remain closed under passive evolution when process noise is zero.

For this Fourier mode, the unknown offset appears only through the phase

    exp(-i*2*pi*(dy + 2*dx)/64).

For any one offset there are **64 distinct alternative offsets** satisfying the same dy+2dx modulo 64. All those operators are exactly indistinguishable on the passive state, even without sensor noise and with infinitely many passive frames. More time *cannot* fix that particular identifiability defect without a new independent mode.

This is standard Fourier geometry, not a newly discovered theorem.

## B. What the learner chooses

The learner scores every one of the 4,096 candidate offsets using the complete noisy temporal observations accumulated so far. FFT cross-correlation evaluates all candidates without passing in the generating offset.

The **candidate-directed Fourier strategy** selects the best-scored 24 candidates, examines 99 available frequencies (indices 0–9 in both dimensions, excluding zero/zero), and chooses the frequency at which those candidates' predicted phase responses disagree most. That design is based solely on **learned candidate scores**. It has no access to the true offset.

Matched baselines are passive observation, a random single Fourier mode from the same 99 frequencies, a repeatedly used fixed mode (1,2) already present in the passive state, and broadband white-noise excitation. All nonpassive actions have exactly the same L2 norm. White noise is a **strong** baseline: it probes a broad spectrum at once.

## C. Known sensor noise changes which mechanism wins

A key negative control comes from the prior Luotain2 results: predicting a noisy target using a noisy input can reward a *wrong* low-pass law.

The no-link operator has local squared kernel norm **0.40**. Most one-link competitors have norm **0.30** (or **0.32** when the candidate overlaps an existing cardinal neighbor). With additive independent measurement noise of variance R, ordinary noisy squared-error risk contains a model-dependent term proportional to R times the kernel's squared norm. This systematically rewards some nonexistent smoothing links.

For every candidate the learner corrects the accumulated negative-half-squared-error difference by adding

    + 0.5 * R * N² * (||A_candidate kernel||² − ||A_null kernel||²)

per observed frame transition. This is the exact **expected** correction for the assumed independent, additive, known-variance sensor errors. It is **not** an instrumental-variable method and it is **not** justified if sensor error is correlated over time, colored over space, or of unknown variance.

We deliberately repeat the null experiment with that correction disabled, while keeping the observations and policies otherwise matched. Thus this ablation checks whether the correction matters, rather than giving the learner the correct answer.

## D. Frozen independent results — unknown remote address

Fresh remote offsets: **seeds 901–940**, 40 simulator draws. These were not used in the local development trials. Correct means **the single top-scoring candidate offset is exactly the hidden address**, not merely predictive loss under a tolerance.

| Policy | End of 24 passive steps | After 2 interventions | After 4 | After 8 | After 16 |
|---|---:|---:|---:|---:|---:|
| Passive only | 3/40 | 2/40 | 1/40 | 1/40 | **1/40** |
| Candidate-directed Fourier | 3/40 | 7/40 | 22/40 | 39/40 | **40/40** |
| Random Fourier | 3/40 | 4/40 | 19/40 | 37/40 | **40/40** |
| **White noise** | 3/40 | **10/40** | **32/40** | **40/40** | **40/40** |
| Fixed original Fourier mode | 3/40 | 2/40 | 1/40 | 1/40 | **1/40** |

**Important negative finding:** broad white-noise probing beat the targeted strategy on *sample efficiency*. At four interventions, white had 32/40, targeted 22/40. By eight, they reached 40/40 and 39/40 respectively. Candidate-directed probes do outperform random **single-frequency** probes by eight (39 versus 37), but this 40-case sample does not establish a general advantage, and neither beats broadband white.

The result is not that **adaptive targeting wins**; the result is that **an unseen remote address can become identifiable from small interventions that break an otherwise exact passive alias**.

## E. Null-world kill test — could it invent a connection?

Fresh no-link worlds: **seeds 1901–1940**, 40 distinct measurement-noise trajectories. Correct means the top-scoring candidate is **(0,0), no remote link**.

| Policy | With calibrated sensor-noise correction, after 16 actions | Identical policy but wrongly setting R=0 |
|---|---:|---:|
| Targeted Fourier | **40/40 correct null** | **0/40 correct null** |
| White noise | **40/40 correct null** | **0/40 correct null** |

Without noise calibration, the estimator consistently prefers a false smoother spatial operator over the real no-link law. This is the clearest connection between the temporal experiment and Luotain2's noisy-regression problem. It must **not** be generalized into an automatic no-false-positives guarantee: only 40 synthetic nulls and perfectly known independent sensor noise were used. No calibrated selection confidence or p-value is claimed.

## F. A separate ongoing process-disturbance sweep

Another **20 fresh seeds 1101–1120** test independently driven process noise while the observation sensor SD stays fixed at 0.01. These are absolute per-pixel process standard deviations, **not** Luotain2's relative-noise definitions.

| Process SD | Passive correct after 24 steps | Passive correct after 28 steps | Targeted after 8 actions | White after 8 actions |
|---|---:|---:|---:|---:|
| 0 | 0/20 | 0/20 | 20/20 | 20/20 |
| 0.0002 | 0/20 | 0/20 | 20/20 | 20/20 |
| 0.001 | 0/20 | 0/20 | 20/20 | 20/20 |
| 0.003 | **18/20** | **20/20** | 20/20 | 20/20 |

Independent stochastic process disturbance can supply the missing excitation even without deliberate intervention. The observed transition is **not a universal threshold**, and this sweep does not globally match latent power as Luotain2's fixed-R Gate IV-003 did. It should not be conflated with that experiment.

## G. Falsification and current scientific boundary

The combined gate tests check the exact 64-fold passive alias, FFT score against direct pixelwise squared-error, correct candidate-specific noise terms for nonlocal and local offsets, identical action L2 norms, hidden truth access, paired passive observations, unknown offset draws, independent process-vs-measurement disturbances, and the false-link calibration control. CI successfully completed the full suite.

**Established by this simulated benchmark:** action-induced new spatial modes make a hidden translation-invariant remote link selectable where the undisturbed field remains exactly ambiguous. Correct measurement-noise calibration is critical to rejecting nonexistent remote links in this known-family score. White-noise probing is at least as good as this particular targeted policy.

**Not established:** a novel system-identification theorem, optimal active experiment design, recovery of unknown coupling coefficient or local stencil, true blind nonlinear/multilag Luotain2, a physically feasible intervention in an actual sensor, neural mechanism, or any claim about LLM self-training/model collapse.

### Follow-up that would matter

Remove the learner's oracle-like prior knowledge of the local stencil and remote coefficient. Have it fit rival structures on passive measurements, decide on a probe from those *fitted hypotheses* under input constraints, and test new worlds with variable coefficients, multiple links and time lags. A statistically calibrated **refusal region** is required before treating the top-scoring address as an identified physical fact.

## Reproduction

Windows PowerShell or a POSIX shell, Python 3.10+:

    python -m pip install numpy pytest
    python -m pytest -q
    python -m temporal_gate --out results

The frozen suite uses 40 new remote worlds × five policies, 40 null worlds × five corrected policies plus two uncorrected controls, and a 20-seed × four-process-level × three-policy sweep. Source: [temporal_gate.py](temporal_gate.py) · [tests/test_temporal_gate.py](tests/test_temporal_gate.py) · [workflow](.github/workflows/gate004.yml). The artifact includes full per-case offset decisions, ranks and mode selections, but no EEG or private recordings.
