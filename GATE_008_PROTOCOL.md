# Gate 008 frozen protocol — Kick a frozen Allen–Cahn equilibrium

**Preregistered on 22 November 2026 before fresh holdout.**

## Scientific question

Claude's [Luotain2 Estimated-R Gate](https://github.com/anttiluode/Luotain2/blob/main/ESTIMATED_R_GATE.md) showed that Allen–Cahn dynamics near phase domains become difficult to identify passively: reaction and diffusion largely disappear or cancel on the observed states. Can a feasible, deliberately structured pulse reveal them under unknown observation noise?

Related methods are established in [equilibrium pulse perturbation](https://pmc.ncbi.nlm.nih.gov/articles/PMC122859/), [optimal biological stimulus design](https://pmc.ncbi.nlm.nih.gov/articles/PMC3516143/) and [PDE experiment design](https://www.tandfonline.com/doi/full/10.1080/00207179.2016.1138143). We claim NO new general theorem.

## Restricted candidate family and equilibrium preparation

On a periodic 32×32 grid the simulator prepares uniform bulk equilibria s=+1 or −1, then applies the *unknown* one-step law

    F(v;s) = v + D*Lap(v) + a*(v-s) + r*(v-v^3).

The true Allen–Cahn world has D>0, r>0, a=0. The alternatives are diffusion-only, reaction-only, identity, and a **phase-conditioned linear surrogate** with a<0 (the local linearization of an Allen–Cahn-like reaction, NOT a global physical law). The learner receives the *candidate feature family* Lap, linear, cubic but not true support, coefficients, world type, actual noise variance or latent states.

Each experiment uses two **separately prepared copies of an identical equilibrium state**; apply +u to one, −u to the other. This exact repeated-state preparation is a very favorable intervention assumption and is NOT an unreset continuing Luotain2 simulation. The phase sign is inferred from a noisy baseline measurement.

The precise noiseless algebra:

    EVEN = (F(s+u)+F(s-u))/2 - s = -3*s*r*u^2
    ODD  = (F(s+u)-F(s-u))/2 - u
         = D*Lap(u) + (a-2*r)*u - r*u^3

The EVEN response isolates the nonlinear reaction from any linear diffusion. Center its spatial mean and the u² spatial mean per pair to remove constant offset bias. Fit r first, then D and a from the ODD response. A sign-consistent 3× empirically estimated SE criterion must pass in **both nonoverlapping halves** (two paired trials each). No R is supplied or externally estimated. This is NOT a familywise-calibrated hypothesis test.

## Frozen matched-energy policies

Every nonzero input has pixel RMS 0.055 and pixel absolute amplitude <=0.16, for equal L2 input energy.

- Passive: u=0. A uniform equilibrium is mathematically uninformative about D, a and r.
- White: clipped Gaussian spatial input scaled to exactly the same energy.
- Targeted sparse: an amplitude-capped pulse with as few active pixels as the fixed energy allows. It maximizes the potential quadratic-curvature information sum((u²-mean(u²))²) under fixed total energy and pixel bound. **Only the possible cubic feature class is known; no true r, D or a.**
- Single Fourier: a single spatial sinusoid that can make Lap(u) and u collinear; numerical rank refusal is required.
- Mislogged kick: the world receives a real white input but the estimator gets a different, never-applied equal-energy waveform. This must not count as valid physical evidence.

Four paired ± trials per world; noise SD drawn independently and not revealed to the estimator from [0.07,0.09], process innovation SD 0.003. Coefficients vary per world: D from [0.11,0.19], r from [0.14,0.26] when present, linear-surrogate a=-2*Uniform[0.14,0.26].

**Adversarial physical detector:** a latent diffusion-only world has r=0, but its PRIMARY sensor adds q*s*(F(v)-s)^2 with q drawn from [-3.8,-3.2], which can imitate nonlinear reaction. A second **trusted linear reference sensor** measures the same latent process without that nonlinear front end. Accurate calibration of this second sensor is granted, not learned. Preserve any false reaction claims from the primary instrument.

## Development and independent holdout

The method and thresholds were developed on seeds **10–49, 301–340, 1001–1040**. Do NOT count those as confirmation.

**Completely new frozen holdout seeds 2001–2040**, 40 seeds each across six simulator worlds and five policies, with an extra reference-sensor arm on the detector-quadratic world: **1,240 world-policy analyses**, with common seeds paired across conditions and four ± trials in each. These are NOT 1,240 independent laws.

Report exact support identification for Lap (D), cubic reaction (r), linear surrogate (a), false reaction detections on physical null worlds, the nonlinear-sensor false positive frequency, and the trusted reference-channel recovery. Preserve failure counts and parameter error.

### Abort/kill criteria

- No passive identification from constant equilibria, otherwise label a leak.
- Targeted pulse must beat white on detecting cubic reaction, or report failure.
- Single-mode rank deficiency must be recognized rather than spuriously fit as independent D and a.
- Wrong action logs may produce spurious nonphysical linear couplings; expose them.
- A nonlinear detector may produce an apparent cubic term even in a linear latent world; a trusted reference adds genuine extra measurement, not magical postprocessing.
- Split 3-SE thresholds are exploratory, **not** calibrated multiple-testing significance.

## Scientific boundary

A candidate reaction–diffusion grammar, precise input waveform, perfectly repeated equilibrium preparations and favorable Gaussian independent measurement noise are assumed. This is not passive nonlinear Luotain2 on an unreset field, not domain-wall dynamics, not open-grammar symbolic law discovery, not real physical sensing and not novel optimal-design mathematics.

Reproduce (Python 3.10+): install numpy and pytest; run python -m pytest -q; python -m equilibrium_gate --out results. The full per-seed results and counterexamples must be archived.
