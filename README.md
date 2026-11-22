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

## Reproduce all three gates

Requirements: **Python 3.10+**, NumPy and pytest. CPU only; no torch or GPU. On Windows you can use Python 3.13.

~~~powershell
py -3.13 -m pip install numpy pytest
py -3.13 -m pytest -q
py -3.13 -m theorem_gate --out results
py -3.13 -m wormhole_gate --out results
py -3.13 -m blind_kernel_gate --out results
~~~

Or use plain python on Linux/macOS. The three GitHub Actions workflows run all tests and archive complete seed-level JSON receipts:

- [Gate 001 CI results](https://github.com/anttiluode/Theorem/actions/runs/45038711769)
- [Gate 002 CI results](https://github.com/anttiluode/Theorem/actions/runs/45039130421)
- [Gate 003 CI results](https://github.com/anttiluode/Theorem/actions/runs/45039881706)

## Scientific boundaries

**Established math, tested simulation:** for specified linear mechanisms A and B, their outputs agree wherever (A−B)x=0. At fixed input-energy budget E, the probe maximizing their output discrepancy is a top right singular vector of A−B. Under independent isotropic Gaussian measurement noise with known variance, it also maximizes binary discriminability. With physically constrained probes or correlated/unknown noise the optimal design changes. See [formal statement](THEOREM_T1.md).

**Not yet discovered:** a new general theorem, a universal LLM model-collapse law, a learned diagnostic that works without candidate laws, a hidden complement circuit inside real GPT/Qwen, or a skull-versus-cable classification from public EEG.

The ShadowValley 180-run causal follow-up explicitly found **no covert complement reads when attention pointed at the answer**; the observed noise penalty for solved complement reads was **6.8–8.5× variance**, close to the ideal **7×**, *not* the earlier 36–58× claim. [Read Claude's controls](https://github.com/anttiluode/shadowvalley#follow-up-are-standard-blocks-hiding-silent-complement-reads-complementpy).

HeadAsResonator3's reference subtraction is a sensor-space operation and is **not** mathematically identical to the input-space zero-sum projection in Gate 001. It does not uniquely locate a sound pathway. These analogies guide experiments but are not proofs of shared physical or learning mechanisms.

## Next actual research gate

**Candidate-blind active temporal wormhole audit.** Gate 003 already recovers the remote address when source probing is controlled and the operator is known to be shift-invariant convolution. Now take two different multi-frame law candidates **proposed by the noisy Luotain2 learner**, never from the hidden generator. Compute a feasible phase-targeted probe *only from their disagreement*. Apply that probe to the synthetic world, or measure existing independent holdout trajectories that excite the predicted modes. Compare its ability to discriminate against equal-energy white noise, smooth noise, passive observation, and an intentionally wrong probe. Then evaluate whether the selected correct law generalizes to new seeds and **new random wormhole offsets**.

That is where an original method might emerge. Until then, Theorem is an honest working instrument built on prior mathematics.

## Prior art

Persistent excitation and model-informativity conditions are established in system identification; [Van den Hof et al., On the informativity of direct identification experiments in dynamical networks](https://www.sciencedirect.com/science/article/pii/S0005109822006082) explicitly examines experiment design for identifying dynamics. [Parameter estimation under lack of persistency of excitation](https://www.sciencedirect.com/science/article/pii/S0167691121002103) discusses rank defects; [nullspace projection in linear imaging](https://pmc.ncbi.nlm.nih.gov/articles/PMC10560448/) provides the inverse-problem counterpart. This project claims no priority over them.

Built to falsify ideas, not to decorate them.
