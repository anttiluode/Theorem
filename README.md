# THEOREM

### Find the missing dimension before claiming the missing law.

This repo is a research lab connecting three independently developed investigations:

- [ShadowValley](https://github.com/anttiluode/shadowvalley): the zero-sum complement reader, which can solve the ordinary task without attending to the answer token and is fragile when the zero-sum constraint breaks;
- [Luotain2](https://github.com/anttiluode/Luotain2): blind spatial-law discovery fails when the available dynamics do not excite the operators' distinguishing modes, even if the wrong law predicts the observed frames;
- [HeadAsResonator3](https://github.com/anttiluode/HeadAsResonator3): audio-to-electrode prediction can be strong yet largely removed by changing the measurement reference, which exposes a shared recorded component **without identifying its physical source**.

The central idea worth testing is **difference-aware identifiability**:

> Observations distinguish candidate mechanisms only in directions where (1) the candidate mechanisms respond differently, (2) the source actually excites those directions, and (3) the measurement retains those differences above its noise floor.

This is not a newly invented universal theorem. The linear version follows from established nullspace geometry, singular value decomposition, persistent excitation, and optimal experiment design. The interesting work is whether we can turn it into a reliable *algorithm* that finds the right probe from noisy measurements **without being told the answer**.

## Live geometry: see the wormhole become visible

**[Open the single-file microscope](index.html)** — download and double-click index.html in any modern browser; no web service, library, server or GPU is needed.

Three canvases show a spatial pattern, the same pattern shifted by Luotain2's remote (+17,−9) wormhole, and the difference between a remote link and a local-only substitute. Select **Exact dark**, **Nearly dark** or **Maximum reveal**.

The surprising geometry: even an intricate high-frequency pattern can be **completely dark** to a particular remote link. What matters is whether the shift changes the pattern's phase. There are **64 precisely blind** and **64 maximally bright** Fourier coordinates among the 4,096 on a 64×64 periodic field for this particular link-vs-local contrast. The number follows from modular arithmetic and the Fourier shift property; it is not claimed as a new law of physics.

## Gate 001 — Two laws, identical predictions, one useful probe

[Code](theorem_gate.py) · [Proof and exact assumptions](THEOREM_T1.md) · [Successful CI run](https://github.com/anttiluode/Theorem/actions/runs/45038711769).

We give the experiment two distinct linear operators. Each pair agrees **exactly** on every input in a restricted passive data subspace. We compare equal-energy tangent, random, dark-subspace-random, and top-singular-vector (optimal) probes.

Frozen synthetic experiment: 30 seeds (501–530), 3,000 independent sensor-noise draws per seed and probe; no tuning after evaluation.

| Known-law discrimination, equal probe energy | Tangent (uninformative) | Random | Targeted optimal |
|---|---:|---:|---:|
| ShadowValley-style zero-sum complement read | 50.3% | 61.6% | **85.5%** |
| Constructed 16D checkerboard field | 50.3% | 68.5% | **98.8%** |

These are **two-known-hypothesis decisions**, not blind source discovery or trained LLM tests. The predictions of the exact Gaussian likelihood formula agree with the simulations.

**The most useful distinction:** the 16D field still has twelve unexcited modes after adding the optimal probe (rank grows **3 → 4**). Its *global* smallest input-covariance eigenvalue remains **zero**. But the added single mode is enough to distinguish the **two specified candidate laws**. Full rank is necessary to identify every unrestricted direction, not to discriminate a particular pair. This is elementary but a powerful warning against treating one global excitation score as an answer to every question.

## Gate 002 — Use the actual Luotain2 wormhole offset

[Code](wormhole_gate.py) · [Successful CI run](https://github.com/anttiluode/Theorem/actions/runs/45039130421) · [Original law](https://github.com/anttiluode/Luotain2/blob/main/luotain2/worlds.py).

Use Luotain2's **actual** (+17,−9) remote neighbor coefficient +0.1 from its wormhole law. Compare the correct one-step operator against a **specified simplified local-only hypothesis** that substitutes +0.1 of the center value for the remote signal. Do not confuse this competitor with Luotain2's previously recovered incorrect autoregressive law, and do not claim a blind-IV recovery.

The distinguishing gain at Fourier index (ky,kx) is:

    0.2 * abs( sin(pi * (17*ky − 9*kx)/64) )

The remote shift is exactly invisible when 17*ky−9*kx is divisible by 64, and maximally exposed when it equals 32 modulo 64. Some nonconstant patterns are completely dark regardless of amplitude.

30 seeds (701–730), 3000 fresh Gaussian noise draws per seed and equal-energy synthetic probe:

| Probe | Predicted correct candidate | Measured correct candidate |
|---|---:|---:|
| Exactly dark Fourier pattern | 50.0% | **49.9%** |
| Nearly dark nonconstant low-frequency pattern | 52.9% | **53.2%** |
| Smoothed random field | 85.2% | **85.4%** |
| White-noise random field | 85.6% | **85.6%** |
| Targeted bright Fourier pattern | 93.3% | **93.3%** |

The stronger candidate-aware probe is obtained from the operator difference, not from a general preference for high frequencies. The weak/strong Fourier modes follow from standard mathematics.

## Gate 003 — Blindly recover the remote address, without an oracle support list

[**Full method, results and limitations**](GATE_003_REPORT.md) · [Successful 21-test CI](https://github.com/anttiluode/Theorem/actions/runs/45039881706) · [Persistent numerical summary](results/gate003_summary.json) · [Full per-seed data](https://github.com/anttiluode/Theorem/actions/runs/45039881706/artifacts/14760799250).

This gate closes the first two gates' obvious loophole: **we no longer tell the estimator where the wormhole is**. It receives a set of controlled input spatial fields, their noisy output fields, and the assumed Gaussian sensor-noise standard deviation. It knows only that the unknown operator is *linear and translation-invariant* on a periodic 64×64 field—not its number of spatial links, offsets or coefficients. Complex Fourier cross-spectrum inversion reconstructs the impulse response and a fixed noise-calibrated threshold selects its significant spatial offsets.

At matched input energy and fixed absolute sensor noise, on **20 new seeds**:

| Number of input/output probe pairs | Smoothed random | White random | Exact flat-spectrum random |
|---:|---:|---:|---:|
| 8 | 0/20 | 0/20 | 0/20 |
| 24 | 0/20 | 10/20 | **11/20** |
| **48** | **0/20** | 19/20 | **20/20** |

The full **six-term spatial support** was recovered, including the **hidden (+17,−9) link**. A no-law null yielded **0 false-positive trials in 60** runs. Smooth probes illuminated only ~3.5% of observable frequency bins; white and flat-spectrum probes covered essentially all of them.

**What has actually advanced:** active phase-preserving measurements can recover an unknown distant spatial coupling using an explicitly calibrated, physically interpretable estimator. This is an empirical success on the **actual Luotain2 synthetic wormhole law**, not simply pairwise discrimination with given alternatives.

**What remains old/limited:** this is classical linear convolution identification, not a new theorem, not passive/unknown-input Luotain2, not nonlinear or multi-frame discovery, and not a medical EEG finding. The estimator has unusually favorable assumptions: exact input-output pairs, known shift invariance, and calibrated independent Gaussian measurement noise.

## Gate 004 — Unknown remote address in a continuous, noisy world

[**Full Gate 004 report**](GATE_004_REPORT.md) · [successful 30-test workflow](https://github.com/anttiluode/Theorem/actions/runs/45041594315) · [row-level experimental artifact](https://github.com/anttiluode/Theorem/actions/runs/45041594315/artifacts/14762031846) · [permanent compact summary](results/gate004_summary.json).

This gate eliminates the static input/output reset of Gate 003. The world is a **continuously evolving 64×64 dynamical field** observed with independent sensor noise. The initial passive state has only one Fourier mode, so **64 different offset hypotheses are exactly equivalent** without further excitation. The agent sees only noisy state observations and chooses small action patterns; it **does not know which of 4096 offsets is true or whether any remote link exists**. It does know the local four-neighbor stencil, positive remote coupling strength 0.1, and the sensor-noise variance; those are strong family priors.

With 24 passive steps followed by 16 equally powered interventions, on **40 fresh random hidden addresses**:

| Policy | Passive correct | After 4 interventions | After 8 | After 16 |
|---|---:|---:|---:|---:|
| Passive / no disturbance | 3/40 | 1/40 | 1/40 | **1/40** |
| Candidate-directed Fourier probe | 3/40 | 22/40 | 39/40 | **40/40** |
| Random Fourier probe | 3/40 | 19/40 | 37/40 | **40/40** |
| **Broadband white noise** | 3/40 | **32/40** | **40/40** | **40/40** |
| Fixed familiar Fourier mode | 3/40 | 1/40 | 1/40 | 1/40 |

**Important negative:** candidate-directed probing **did not beat white noise**. Broadband random excitation was more sample-efficient under the chosen budget. The result supports breaking a specific passive ambiguity, not a superiority claim for the adaptive frequency selector.

**Noise correction was essential for false-link refusal.** On **40 separate no-link worlds**, the known-R-corrected learner reported no remote connection in **40/40** with either targeted or white probes after 16 actions. Under the **same observations**, falsely setting R=0 yielded **0/40 correct nulls**: the learner invented smoothing links. This mirrors Luotain2's earlier noise-induced wrong-law selection.

An independent 20-seed process-disturbance sweep also shows that ongoing random environmental kicks can supply excitation without externally designed actions. Process SD 0.003 produced **18/20** passive exact addresses after 24 steps, versus **0/20** for SD 0, 0.0002 or 0.001. This sweep does not keep latent global power fixed, so its numerical transition is not comparable to the Fixed-R Gate IV-003 threshold or a universal law.

All results are from a **synthetic known-family linear model** with one lag, known local dynamics and known remote coupling coefficient. This is not a solution to unknown-coefficient/multiple-lag/nonlinear blind law search, a general causal identifiability theorem, or real EEG.

## Gate 005 — Unknown coefficients and R: private interventions as instruments

[**Gate 005 full real protocol and report**](GATE_005_REPORT.md) · [source](active_iv_gate.py) · [frozen protocol](GATE_005_PROTOCOL.md) · [passing 40-test CI](https://github.com/anttiluode/Theorem/actions/runs/45043279743) · [permanent numerical summary](results/gate005_summary.json) · [complete seed-level results](https://github.com/anttiluode/Theorem/actions/runs/45043279743/artifacts/14762816341).

This gate removes Gate 004's *known local coefficients, known remote-link strength and known sensor-noise variance*. Each continuous 64×64 simulator world has a randomly sampled local kernel, an optional remote link with unknown positive/negative weight and address, and a random sensor-noise SD. The estimator still assumes a **linear sparse translation-invariant spatial operator and a known additive actuation port**, so it is not model-free causal discovery.

The critical experimental detail: **a known action is not automatically a valid instrument**. An action selected from the current noisy observation inherits dependence on that measurement. We use a fresh independent **private ± sign** *after* determining each action's spatial shape. This supplies an exogenous instrument under the simulator's explicit noise/feedback assumptions. Cross-spectrum inversion of the actual action against the next measured frame estimates the **unknown full spatial kernel without supplying R**; candidate remote support must replicate on a non-overlapping block of freshly signed interventions; the adaptive blocks are not unconditionally independent observations.

On the **harder, frozen 40-remote/40-no-link seed sets**, with weaker remote links and higher unannounced sensor noise:

| Policy (equal action energy) | Exact remote recovered | No-link correctly rejected |
|---|---:|---:|
| **White broadband private kicks** | **40/40** | **40/40** |
| White → targeted hybrid private kicks | 36/40 | 40/40 |
| Random single Fourier frequency | 0/40 | 40/40 |
| Deterministic feedback, not a valid IV by default | 33/40 | 40/40 |
| Mispaired never-applied placebo instrument | 0/40 | 40/40 |

Broadband **white noise still won** at final recovery. The hybrid was slightly ahead at 12 and 16 actions, but finished worse (36/40 versus 40/40). No two-phase optimality theorem is established.

The local coefficient estimation error makes the exogeneity concern tangible: weak-regime five-weight MAE was **0.0062** under private white probes, but **0.0310** with deterministic noisy feedback, despite the latter often guessing the right remote address. The null refusal is a result of these simulated worlds and an exploratory **spatial MAD threshold**, **not** a calibrated family-wise false-discovery rate.

The WAIVES variogram idea was *not* used to manufacture an unknown-R estimate: without additional assumptions, temporal increments mix sensor noise and real process change. This experiment avoids needing R by using independent intervention inputs, rather than claiming R can always be read off a noise-floor plot.

**Boundary:** still assumes controllable random excitation, a known spatially shift-invariant linear model class and local support region, independent sensor errors and an exact action-to-state port. Colored noise, nonlinear/multi-lag dynamics and nonideal actuation are untested.

## Gate 006 — The false connection was in the actuator

[**Gate 006 complete report**](GATE_006_REPORT.md) · [frozen protocol](GATE_006_PROTOCOL.md) · [source](sensor_port_gate.py) · [successful 49-test CI and 40-seed sweep](https://github.com/anttiluode/Theorem/actions/runs/45044598034) · [all per-seed receipts](https://github.com/anttiluode/Theorem/actions/runs/45044598034/artifacts/14762208996) · [permanent numerical summary](results/gate006_summary.json).

**The critical new finding is a carefully controlled *negative* physical attribution test.** When the real world contained **no distant spatial connection**, but its *actuator* secretly shifted every commanded intervention by (+5,+7), the active-IV estimator reported a false remote link in **all 40 of 40 no-link worlds**. The estimator was recovering the **composite command-to-observation transfer**, not necessarily the internal physical-world operator.

In a spatial convolution model, a world kernel H and uncalibrated actuator kernel G yield intervention response **H·G** in Fourier coordinates. A pure actuator shift can make a world with only local coupling look like it has a long-range internal shortcut. No amount of private-sign independence alone resolves the physical factorization. This is established system identification mathematics, not a newly proved theorem.

Same fixed energy, same 40 new remote and 40 new no-link seeds per condition, the same unknown kernel coefficients and sensor R as Gate 005:

| Stress condition | True remote recovered | No-link correctly refused |
|---|---:|---:|
| Independent sensor noise, ideal actuator | **40/40** | **40/40** |
| Temporal AR sensor noise, rho 0.85 | 39/40 | 40/40 |
| Spatially correlated sensor noise | 40/40 | 40/40 |
| Both temporal + spatial sensor correlations | 39/40 | 40/40 |
| Independent unmeasured actuator noise | 40/40 | 40/40 |
| Unknown actuator gain 0.55× | **15/40** | 40/40 |
| **Unknown actuator spatial shift (+5,+7)** | **0/40** | **0/40 (40 false links)** |
| Unknown one-frame actuation delay, wrong lag | 0/40 | 40/40 |
| **Same delayed recording, correct lag supplied** | **40/40** | **40/40** |

This is an explicit correction to the suggestion that **temporally correlated sensor noise automatically invalidates private-action IV**. It does not: a new private sign can remain conditionally orthogonal to future correlated sensor noise, although finite-sample confidence and variance can suffer. **Physical port calibration** was the much more dangerous obstacle here.

Unknown gain biased the internal weight estimates (mean local MAE 0.0672 instead of 0.0046). A wrong one-frame lag erased all 40 remote detections; externally supplying the correct lag to the *same recordings* restored 40/40. **The lag was not learned blindly.**

**Limits:** these are synthetic worlds with a full-field sensor, one optional remote link, sparse linear spatial convolution and an exploratory non-FWER-corrected remote coefficient threshold. The 40/40 successes and failures are sample counts, not universal guarantees; they cannot locate brain, skull or cable sources from EEG.

## Reproduce all six gates

Requirements: **Python 3.10+**, NumPy and pytest. CPU only; no torch or GPU. On Windows you can use Python 3.13.

~~~powershell
py -3.13 -m pip install numpy pytest
py -3.13 -m pytest -q
py -3.13 -m theorem_gate --out results
py -3.13 -m wormhole_gate --out results
py -3.13 -m blind_kernel_gate --out results
py -3.13 -m temporal_gate --out results
py -3.13 -m active_iv_gate --out results
py -3.13 -m sensor_port_gate --out results
~~~

Or use plain python on Linux/macOS. The six GitHub Actions workflows run all tests and archive complete seed-level JSON receipts:

- [Gate 001 CI results](https://github.com/anttiluode/Theorem/actions/runs/45038711769)
- [Gate 002 CI results](https://github.com/anttiluode/Theorem/actions/runs/45039130421)
- [Gate 003 CI results](https://github.com/anttiluode/Theorem/actions/runs/45039881706)
- [Gate 004 CI results](https://github.com/anttiluode/Theorem/actions/runs/45041594315)
- [Gate 005 CI results](https://github.com/anttiluode/Theorem/actions/runs/45043279743)
- [Gate 006 CI results](https://github.com/anttiluode/Theorem/actions/runs/45044598034)

## Scientific boundaries

**Established math, tested simulation:** for specified linear mechanisms A and B, their outputs agree wherever (A−B)x=0. At fixed input-energy budget E, the probe maximizing their output discrepancy is a top right singular vector of A−B. Under independent isotropic Gaussian measurement noise with known variance, it also maximizes binary discriminability. With physically constrained probes or correlated/unknown noise the optimal design changes. See [formal statement](THEOREM_T1.md).

**Not yet discovered:** a new general theorem, a universal LLM model-collapse law, a learned diagnostic that works without candidate laws, a hidden complement circuit inside real GPT/Qwen, or a skull-versus-cable classification from public EEG.

The ShadowValley 180-run causal follow-up explicitly found **no covert complement reads when attention pointed at the answer**; the observed noise penalty for solved complement reads was **6.8–8.5× variance**, close to the ideal **7×**, *not* the earlier 36–58× claim. [Read Claude's controls](https://github.com/anttiluode/shadowvalley#follow-up-are-standard-blocks-hiding-silent-complement-reads-complementpy).

HeadAsResonator3's reference subtraction is a sensor-space operation and is **not** mathematically identical to the input-space zero-sum projection in Gate 001. It does not uniquely locate a sound pathway. These analogies guide experiments but are not proofs of shared physical or learning mechanisms.

## Next actual research gate

**Direct actuator-to-sensor feedthrough** is the next clear kill test. Even when the actuator enters the state accurately and the private sign is exogenous, a direct measurement path from action to sensor can produce

    measured_next = H*(latent + G*command) + C*command + sensor_noise

so the causal input-to-measurement response is **H·G + C**, not H alone. A remote-looking sensor artifact C can create the appearance of a remote internal coupling while the intervention is genuinely randomized and the output is perfectly predicted.

A scientifically useful Gate 007 would compare the single-sensor result against an **independently calibrated actuator sensor**, a **sham/blank sensor that receives feedthrough but no world response**, or two separately varied input geometries. Require the falsely inferred remote link to disappear when the physically distinct path is constrained. This is particularly relevant to HeadAsResonator's uncertainty about skull, cable and reference pickup: it is the instrument's *causal geometry*, not its coherence alone, that must be identified.

A separate branch with Claude's Luotain2 nonlinear blind search remains open: its Hermite-corrected score works with known independent Gaussian R, while Theorem 005–006 avoids needing R only under linear convolution and a valid private intervention. Neither result automatically solves the other's assumptions. Do not conflate these estimators.

Until a real new method survives those physically grounded calibrations and a prior-art check, Theorem is a rigorously tested instrument, **not a claim to a universal new theorem**.

## Prior art

Persistent excitation and model-informativity conditions are established in system identification; [Van den Hof et al., On the informativity of direct identification experiments in dynamical networks](https://www.sciencedirect.com/science/article/pii/S0005109822006082) explicitly examines experiment design for identifying dynamics. [Parameter estimation under lack of persistency of excitation](https://www.sciencedirect.com/science/article/pii/S0167691121002103) discusses rank defects; [nullspace projection in linear imaging](https://pmc.ncbi.nlm.nih.gov/articles/PMC10560448/) provides the inverse-problem counterpart. This project claims no priority over them.

Built to falsify ideas, not to decorate them.
