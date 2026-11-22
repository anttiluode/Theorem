# Research notebook — 2026-11-22

## The candidate unifying statement

**Identifiability is relative to the questions asked.**

A weakly excited system may be unable to identify its *full* operator and still have ample information to distinguish two particular possible operators. Conversely, a complex and strongly changing signal can be exactly uninformative about a particular hidden connection if its variations lie in the nullspace of the **difference** between the candidate mechanisms.

This is a precise *linear* statement. It should not be promoted to a theorem about every LLM, nervous system, image inverse problem, or nonlinear stochastic process.

## Evidence audited

### ShadowValley: zero-sum observational equivalence

Claude's 600-run sweep verified the look-away trap in an attention-only controlled architecture. The follow-up 180-run causal probe [complement.py](https://github.com/anttiluode/shadowvalley/blob/main/complement.py) corrected an earlier overclaim: solved complement readers do exist, but attention maps in the tested standard blocks do not hide a complement circuit when attention points to the answer. Measured noise penalty 6.8–8.5× **variance**; ideal seven. Theorem's supplied direct/complement operators are an exactly solvable mathematical version, not a replication of trained transformers.

### Luotain2: fixed-R IV versus OLS

[FIXED_R_GATE](https://github.com/anttiluode/Luotain2/blob/main/FIXED_R_GATE.md) reports exact structural support recovery of **6/6 IV versus 0/6 OLS** at the chosen 1% process excitation level, with global latent amplitude and absolute sensor variance fixed. This was six synthetic runs across two special field worlds, three seeds each. At 2% both methods won 6/6; at 0% both lost 0/6. This is a useful method-specific phase transition, not a general theorem about the meaning of 1% noise.

### HeadAsResonator3: referencing reveals confounding but not material

[Real Gate 003B](https://github.com/anttiluode/HeadAsResonator3/blob/main/REAL_RESULT_003B.md) found strong audio-linked EEG voltage in five of nine recordings across two of three participants. Common-average reference suppressed >80% of the mean predictive R² in all five strong recordings. The recording reference is a **sensor-space transformation** and can remove genuine spatially shared neural activity along with artifacts. Nothing in these observations identifies skull versus cable versus microphone-electrode-interface origin.

### New executable bridges in this repository

- **Gate 001:** two intentionally provided operators are exactly identical on a passive subspace; an optimal singular-vector probe separates them under fixed Gaussian noise. 30 seeds, eight numerical tests originally; [successful CI](https://github.com/anttiluode/Theorem/actions/runs/45038711769). A target pair can become distinguishable while the **global** input covariance still has 12 zero eigenvalues.
- **Gate 002:** the actual (+17,−9) spatial offset in Luotain2 has 64 exact dark Fourier coordinates and 64 maximal ones under the declared remote-vs-local contrast on a 64×64 torus. [Successful CI](https://github.com/anttiluode/Theorem/actions/runs/45039130421). A textured (9,17) Fourier input remains exactly uninformative; an optimal (0,32) checkerboard is maximally discriminating. This Fourier geometry is textbook, not newly derived physics.

### Gate 003: address recovery when the true stencil is actually hidden

[Full Gate 003 report](GATE_003_REPORT.md) · [verified CI](https://github.com/anttiluode/Theorem/actions/runs/45039881706).

This went beyond supplied-model discrimination. On the actual 64×64 Luotain2 wormhole one-step law, the estimator received known input/output probe pairs under Gaussian sensor noise SD 0.08, **but neither the true spatial offsets nor the number of terms**. It assumed a periodic linear convolution and known noise level. Complex cross-spectrum estimation plus a predeclared Gaussian false-positive threshold recovered exact six-term support in **20/20** new-seed trials with 48 equal-energy flat-spectrum probes, **19/20** with 48 white probes, and **0/20** with 48 smooth probes. All 60 no-law null runs had zero selected false connections. Code, full per-seed receipts, tests and limitations are committed.

This is **established Fourier linear system identification**, not a new theorem and not the original Luotain2 passive noisy time-delay problem. It does, however, give a concrete instrument for determining whether a supposedly invisible remote link can be made measurable by a feasible input change.

### Gate 004: a dark world responds to a chosen kick, but white noise is better than our chooser

[Detailed independent benchmark](GATE_004_REPORT.md) · [successful complete CI](https://github.com/anttiluode/Theorem/actions/runs/45041594315) · [permanent numeric receipt](results/gate004_summary.json).

We made the spatial link **unknown among all 4,096 periodic offsets**, including the no-link hypothesis. The field runs continuously with **no reset inside a trajectory** and its passive state is restricted to a single spatial Fourier mode. Exactly **64 candidate offsets** are phase aliases and therefore passively identical on that initial mode. The agent receives noisy sensor readings and can inject equal-energy disturbances before the next update. It knows the local stencil, positive remote-link strength 0.1, and i.i.d. sensor variance—a deliberately narrow strong prior.

Fresh seeds: 40 unknown remote addresses, 40 no-link worlds, and another 20 seeds across a process-disturbance sweep. After 24 passive frames followed by 16 chosen interventions, candidate-directed Fourier recovered **40/40** remote addresses versus **1/40** for passive observation. But crucially, **broadband white noise also recovered 40/40 and was faster** at four interventions (32/40 compared with targeted 22/40). The adaptive method is not yet superior to a sensible nonadaptive baseline.

A separate **null failure boundary** emerged: after 16 actions, correcting the model comparison for independently calibrated input measurement noise chose no-link in **40/40** cases. Falsely setting measurement noise R to zero with otherwise matched observations yielded **0/40** correct nulls. Without correcting the operator-dependent input-noise penalty, the selector consistently invented smoothing connections. This is an empirical direct connection to Luotain2's previous noise-induced wrong-law selection, not a novel theory of inference.

With independent ongoing process innovations of per-pixel SD 0.003, passive identification recovered 18/20 addresses after 24 steps; at 0, 0.0002 and 0.001 it recovered 0/20. The numerical transition depends on the simulator and does not preserve global latent power. Avoid treating it as a physical threshold or as equivalent to Luotain2's fixed-R/latent-power matched study.

Gate 004 is stronger than Gate 003 because the simulator state evolves and the learner doesn't know the remote address. It is **still not open structural discovery**: local stencil, coefficient magnitude and one-lag form are supplied. It requires controlled action and known white sensor noise, neither of which exists automatically for real EEG or passive LLM text.

### Gate 005: corrected IV exogeneity and the weaker two-phase claim

[Full report](GATE_005_REPORT.md) · [passing GitHub Actions](https://github.com/anttiluode/Theorem/actions/runs/45043279743) · [persisted JSON summary](results/gate005_summary.json).

Neon's proposed connection to active instrumental variables had a crucial **causal timing qualification**: knowing the intervention's precise waveform does not make it exogenous when it is selected deterministically from a noisy state. The model uses fresh private Rademacher randomization **after** choosing a spatial action shape. Conditional on the previous measurements/latent state, the signed action has expectation zero and the next output receives a causal operator response to that action. Its cross-spectral moment therefore identifies the linear convolution kernel under independent future noise without needing sensor-noise variance R.

The simulator still gives the learner the shift-invariant linear family, a perfectly known additive actuation port, and a sparse/locality prior; it withholds **all actual stencil weights, the remote location/strength/sign and realized R**. The estimator fits the entire spatial kernel from action-next-measurement moments, using a spatial-MAD coefficient threshold and non-overlapping first/second action blocks to filter discoveries. These blocks are *not unconditionally independent* in an adaptive closed-loop run; future actions and states depend on earlier data. Fresh private random signs support the conditional moment, not a claim of formally independent trials or calibrated p-values.

On the separate hard 40 remote / 40 no-link holdout, broadband private white kicks recovered **40/40** remote addresses and correctly refused **40/40** no-link worlds. The two-phase broadband→targeted controller recovered **36/40**, worse than white; it was slightly ahead only at 12/16 actions and that exploratory comparison is not statistically decisive. Narrowband and mispaired placebo action records recovered **0/40** links. Deterministic noisy feedback recovered **33/40** addresses but had substantially worse local coefficient MAE (**~0.031 vs ~0.006** for white), showing that classification success can coexist with biased mechanism estimation.

The cleanest result is therefore **unknown-R, unknown-weight system identification using independent private excitation in a restricted linear convolutional model**. That is established IV/active system identification deployed as a reproducible new engineering gate, **not a mathematical discovery**. The proposed targeted information-efficiency advantage still has not survived a strong broadband baseline.

A short-lag WAIVES-style variogram estimate of R was **not** smuggled in: process motion and measurement noise can both contribute to near-zero-lag variation, so R cannot universally be inferred without model and smoothness assumptions. Further gate tests should deliberately violate independent sensor noise, spatial shift invariance, single remote link and exact actuator access.

### Gate 006: an estimator can be causally right and physically wrong

[Full experiment and assumptions](GATE_006_REPORT.md) · [passing 49-test CI](https://github.com/anttiluode/Theorem/actions/runs/45044598034) · [permanent JSON receipt](results/gate006_summary.json).

Theorem Gate 006 broke Gate 005's assumed ideal sensor and actuator separately. **Fresh private-sign randomized inputs stayed effective under AR(1) temporal sensor noise (rho=.85) and spatially correlated detector noise** in 40 new remote and 40 new null worlds per condition: 39–40/40 true remote addresses recovered, and 40/40 nulls refused in each sensor-noise arm. Autocorrelation is not the same thing as correlation with a *new random instrument*. This is a limited-sample success under exogenous noise, not guaranteed calibration of the spatial MAD threshold.

Actuator-path changes were dramatically worse. An unknown physical spatial shift (+5,+7) of the commanded action made the **all-local, no-remote world look remotely connected in every one of 40 null trials**. The learned command-response operator has transfer H*G, and without actuator G calibration it is not necessarily the actual world H. In a shift-invariant field the equality H*shift(u)=shift(H)*u is exact for all input waveforms. This is a classic identifiability/factorization ambiguity: a causal IV is not a proof of the *material path* of the response.

Other frozen results: unknown command gain .55 recovered only 15/40 weak remote addresses, with true local-weight MAE .0672 (versus .0046 baseline); additive independent actuator noise recovered 40/40; and an unknown one-frame actuator delay gave 0/40 with naive time alignment but **40/40** on the *same recordings* when the correct lag was supplied. The lag calibration was not discovered blindly. All stress rows, including failures, remain in the artifact.

This exposes a direct methodological bridge to HeadAsResonator: a signal can have a real, reproducible, causally driven sensor relationship while its *physical route* remains unidentified. It does not establish that the EEG pickup followed an actuator, skull, cable, electrical-reference or neuronal route.

**Next boundary:** a direct action-to-detector artifact C yields measured transfer H*G + C; even actuator calibration alone may be insufficient without a sensor sham/reference or multiple independently varied intervention channels. This is more scientifically urgent than increasing model complexity in a simulator with unvalidated ports.

## A genuinely interesting research question

Can a learner obtain a reliable **candidate-specific excitation certificate without knowing which candidate is true**?

The experiments above use operators A and B supplied by us. That is their chief limitation. A promising workflow would:

1. Fit an ensemble of plausible laws to the *same* noisy passive data, keeping supports and uncertainty honest.
2. Discard explanations that fail independent held-out behavior; retain genuine near-ties.
3. Compute where surviving candidates disagree in feasible input or mode space. For nonlinear models use local Jacobians or a robust finite-difference approximation rather than pretending a global linear matrix exists.
4. Under a strict intervention-energy and safety budget, choose probes expected to separate candidates, against equal-energy random, broadband, smooth, and intentionally null probes.
5. Hide the true simulator during proposal, probe choice and model selection, reveal it only for final scoring on unseen generators and random remote offsets.
6. Report failures: no adequate rival proposals, no feasible input direction, incorrect confidence, wrong law despite good predictive fit, and sensor-noise confounding.

If a method succeeds across *novel model families and natural data*, and rigorous prior-art search confirms a meaningful methodological difference, it may become a research contribution. If it does not, the outcome is still information: the geometric analogy has reached its limit.

## Open scientific cautions

- High temperature text sampling is NOT automatically independent measurement noise: generated tokens are fed into the future context and can create dependent effects.
- Rare human turns of phrase are not automatically the process noise of an identifiable SDE; applying WAIVES to surprisal streams requires validating a dynamical model and instrument exogeneity.
- A trained attention head can read through an equality constraint without learning the true independent causal input. That failure is distribution-specific, not universal to ordinary pre-LN transformers.
- Nonlinear dynamics can have multiple operators that agree locally; Jacobian-based probe designs may leave the local regime under large interventions.
- A strong observation-level Fourier mode is not necessarily a feasible or safe control input to a real physical system.
- An identifiability score is question-specific. Report both **pairwise separability** and **global unidentifiability** rather than replacing one with the other.

**Scientific status:** no novel universal theorem has been discovered here. We now have a formal, executable shared question—and a demanding next experiment that might uncover something beyond the known math.
