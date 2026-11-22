# Theorem candidate T1 — Difference-aware identifiability

**Status: a proved, elementary linear-algebra statement, not a new theorem or claimed discovery.** This repository is an executable test bench for identifying where *specific rival explanations* disagree. The user-selected name Theorem is the project name, not a priority claim.

## 1. Exact statement and proof

Take **two specified** real matrices A and B, each mapping an input vector x to an output vector. Let the observed input distribution be contained in the column space of orthonormal Q. Let D = A − B.

**Passive equivalence.** If D Q = 0, then A x = B x for every observed x = Qz, regardless of how many passive examples are collected. Even with unlimited noise-free data from that subspace, a passive learner cannot distinguish A and B using their outputs. In stochastic data with the same observation-noise distribution under both hypotheses, their full output distributions agree.

**Probe certificate.** Suppose we can inject u with ||u||₂ ≤ E into a known baseline x, and both operators act linearly. Then the difference between their post-probe predictions is D u. A singular-value decomposition of D gives

    max_{||u||<=E} ||D u||₂ = E * sigma_max(D).

The maximizing probe is E times the leading right singular vector of D. Any probe constrained to a feasible subspace span(W) has best difference E sigma_max(D W); if D W = 0, no feasible input distinguishes the pair.

**Known-hypothesis Gaussian discrimination.** Suppose output noise is independent N(0, sigma² I), both operators are known alternatives, the baseline input is known, and the hypotheses have equal priors. Their possible measured outputs have equal covariance and mean separation ||D u||. The optimal likelihood-ratio rule is the perpendicular bisector of those means. Its probability of choosing correctly is

    P(correct) = Phi( ||D u|| / (2 sigma) ),

where Phi is the standard normal cumulative distribution function. Thus the singular-vector probe is also optimal for this *specific* binary Gaussian test. This is **not** blind recovery of A or B and says nothing about unseen alternatives, nonlinear systems, colored noise, or physical constraints on intervention.

These observations are standard subspace geometry and optimal-experiment-design facts. Their joint presentation is intended to make a practical diagnostic, not to claim priority.

## 2. The important distinction: identify a choice, not the entire operator

A matrix of observations may have low rank with many permanently unexcited directions. The global smallest singular value of the input covariance can remain **zero** even while there is enough excitation to distinguish *two nominated hypotheses*.

Proof by construction. Let the observations span r dimensions in an n-dimensional input, with n−r > 1. Let D = c vvᵀ for some unit vector v orthogonal to the observed subspace. All passive observations are identical under A and B. Now inject inputs with independent nonzero variation along v alone. The covariance rank rises from r to r+1 but is still less than n, hence its smallest eigenvalue is zero. Yet Dv ≠ 0, so the two nominated alternatives now make different predictions and can be discriminated arbitrarily well by enough independent noisy replicates.

**This is the candidate-specific identifiability distinction.** A global lack-of-rank alarm is correct about *full operator recovery*, but can be overly restrictive for asking whether A differs from B in one named direction.

This is the point to test in Luotain2's wormhole selection: which *specific combination of spatiotemporal modes* makes a real wormhole law disagree with the wrong autoregressive shortcut? A global first-stage F or full-rank check does not answer that narrower question by itself.

## 3. Constructed ShadowValley bridge

There are eight detail tokens whose values sum to zero. The cue chooses token j.

- Direct reader A returns d_j.
- Complement reader B returns the negative sum of the other seven details.

For every zero-sum input they return **exactly the same value**. The difference A − B reads the **sum of all eight components**. Thus any perturbation keeping that sum unchanged gives zero distinguishing information. The optimal perturbation, at equal input energy, changes the **uniform common-mode direction**.

This is a reduced *specified-linear-reader analogue* of the task in [ShadowValley](https://github.com/anttiluode/shadowvalley), NOT a retraining or causal patching of its learned networks. Claude's later 180-run intervention study matters: it found several genuine complement solutions and *no attention-map-hiding complement reader* when attention pointed at the target. The measured noise-variance penalty for those learned complements was about 6.8–8.5x, close to the ideal seven, not the earlier 36–58x claim. Theorem must not repeat the pre-control overclaim.

There is a counterintuitive caveat: if the **input itself** is projected back onto the zero-sum space before being processed, even the optimal uniform perturbation vanishes, and A and B become identical again. That mathematical input projection is NOT the same physical operation as common-average re-referencing of EEG sensor outputs in HeadAsResonator3. It illustrates how a preprocessing step can erase a potentially identifying direction; it does **not** establish a physical audio route.

## 4. Constructed Luotain2 bridge

A is a stable circular smoothing operator on 16 positions. B is A plus a rank-one alteration of its checkerboard spatial mode. Ordinary training examples contain only the constant and first sine/cosine spatial modes. Since those do not overlap the checkerboard, both candidate mechanisms make identical predictions.

The optimal targeted probe excites the checkerboard. A random equal-energy perturbation injects much of its energy into irrelevant modes. A tangent probe staying in the smooth space can never distinguish the models.

After injecting one checkerboard mode, the 16D input covariance increases in rank from 3 to **4**, so its **smallest eigenvalue remains zero**. Nevertheless the difference between A and B is observable. That is the distinction behind candidate-aware excitation as opposed to insisting on full-rank identification of every operator coefficient.

This constructed example is NOT the actual 64×64 Luotain2 wormhole with spatial offset (+17,−9), and is not an IV or WAIVES benchmark. The proper next experiment is to compare the actual recovered candidate laws and design a diagnostic to test their disagreement.

## 5. Gate 001 evidence and falsification

The exact equal-output identities, rank diagnostics and top-singular-vector optimum are tested numerically. Thirty independent seeds (501–530) each perform 3000 fresh Gaussian measurement draws under *each* of four equal-energy probes: tangent, isotropic random, random only in the unseen subspace, and optimum based on the supplied two mechanisms.

The test must fail if: A and B differ on the passive subspace, the returned probe is suboptimal, probes differ in total Euclidean energy, tangent data can distinguish the alternatives, the Gaussian formula fails, or the reconstructed covariance gains a fake full rank from a single targeted field kick.

Evidence is synthetic and the candidate difference is handed to the experiment. It does not prove practical identifiability when the candidates, noise covariance or measurement channel are unknown.

## 6. Relation to existing research (not an originality claim)

The underlying ideas are longstanding: persistent excitation and rank conditions for system identification; nullspaces and regularized inverse problems; and active/optimal experiment design.

- [On the informativity of direct identification experiments in dynamical networks](https://www.sciencedirect.com/science/article/pii/S0005109822006082) develops informative excitation and optimal experiment design for dynamics.
- [On exponentially convergent parameter estimation with lack of persistency of excitation](https://www.sciencedirect.com/science/article/pii/S0167691121002103) discusses rank-deficient regressor information and partial identifiability.
- [Computing a Projection Operator onto the Null Space of a Linear Imaging Operator](https://pmc.ncbi.nlm.nih.gov/articles/PMC10560448/) reviews invisible nullspace components in imaging.
- [ShadowValley](https://github.com/anttiluode/shadowvalley) and its complement intervention controls; [Luotain2 Fixed-R Gate](https://github.com/anttiluode/Luotain2/blob/main/FIXED_R_GATE.md); [HeadAsResonator3](https://github.com/anttiluode/HeadAsResonator3).
- The continuous-time WAIVES result is **not** assumed to apply to the present static linear Gaussian experiment.

## 7. What would count as original work here?

The classical identity is only a tool. For a scientific advance, we need to learn or infer rival **unknown** operators from genuine observations, calculate which physically feasible probe would distinguish them *without being handed truth*, use that probe on an unseen system, and show a calibrated intervention-response gain over matched random, passive, and deliberately misleading probes. That is a larger and still untested claim.

A meaningful paper should also benchmark proposal failure, null false positives, correlated measurement noise, invalid/too-costly interventions, and discrepancies between model-relative and global excitation diagnostics.

**Boundary:** no proof that model collapse is literally an Ornstein–Uhlenbeck SDE, that all LLM attention reads are false, or that EEG/audio sensor covariance uniquely locates skull, brain, or cable pathways.
