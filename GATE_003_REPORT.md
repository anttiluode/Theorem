# Real mathematical gate 003 — Recover an unknown remote spatial address

**Experimental status:** 2026-11-22, successful. [GitHub Actions workflow](https://github.com/anttiluode/Theorem/actions/runs/45039881706) passed **21/21 tests** and completed a fresh **20-seed** evaluation. [Full per-seed numerical artifact](https://github.com/anttiluode/Theorem/actions/runs/45039881706/artifacts/14760799250).

This is a **synthetic, active, restricted, linear** inverse problem. It is not a theorem of biological EEG, language, WAIVES stochastic calculus, or unrestricted Luotain2 law discovery.

## What was and was not told to the estimator

The simulator implements the original Luotain2 wormhole one-step law on a periodic 64×64 field:

    next = 0.5 * current
           + 0.1 * [shift(+1,0) + shift(-1,0)
                    + shift(0,+1) + shift(0,-1)]
           + 0.1 * shift(+17,-9)

The implementation is copied from and checked against [Luotain2 worlds.py](https://github.com/anttiluode/Luotain2/blob/main/luotain2/worlds.py). The six true shift locations and coefficients are known only to the simulator, hidden from the estimator until scoring.

The **estimator** is given: an array of chosen input images x, a corresponding array of noisy output images y, the size of the periodic field, the assumption that the operator is linear and translationally invariant, and a calibrated independent Gaussian sensor standard deviation R½ = **0.08**. It is **not** given the true offset, the six-term support size, the real kernel coefficients, a candidate model set, or a local-neighbor stencil prior.

Thus, this is a blind *spatial support/address* search inside a tightly declared model family, **not** fully open-grammar dynamics discovery, multi-step state-space inference, or WAIVES instrumental variables.

## No secret tuning on the benchmark seeds

Three equal-Euclidean-energy source/probe patterns:

1. **Smooth:** Gaussian-smoothed random spatial texture, whose FFT suppresses high-frequency support.
2. **White:** unit-norm Gaussian random image.
3. **Flat spectrum:** random real input converted to its complex Fourier spectrum, every frequency amplitude replaced with 1 while preserving conjugate symmetry, inverse transformed and unit-norm normalized. This produces real, spatially distributed input with exactly equal Fourier power in each bin.

Each experimental x has **unit L2 norm**, so energy is matched. All outputs are generated with the same absolute independent sensor noise standard deviation 0.08. We tested **8, 24 and 48 separate probes** per run.

Reconstruction uses the classical complex cross-spectrum transfer:

    Hhat(k) = sum_t(conj(X_t(k)) * Y_t(k))
              / sum_t(abs(X_t(k))²).

Frequency bins below a fixed minimum input power (0.15 times number of probes) are left unestimated rather than filled with invented values. The inverse FFT of Hhat yields the candidate spatial kernel. A Gaussian noise calculation estimates every spatial coefficient's measurement uncertainty:

    variance_each_kernel_coefficient =
        (R / M) * sum_over_observed_frequencies(1 / source_power(k)),
        M=4096, R=(0.08)².

The method labels coefficients as present only when their absolute value exceeds the conservative family-wise union-bound cutoff

    threshold = std_kernel * sqrt(2*log(2*M/0.05)).

**This decision rule does not receive the true number of terms.** The threshold depends on a known-noise and Gaussian/independence assumption; it is not an inference of unknown R.

The 20 independent evaluation seeds **801–820** were committed before the CI run. There is a separate 3-seed development smoke test using seeds 701–703. No hyperparameters were changed after examining the fresh 20-seed results. We also ran a **null physical system** using the same actual input patterns and Gaussian sensor noise but *no* input-to-output operator.

## Frozen results

| Number of equally powered probes | Smooth input exact support | White input exact support | Flat-spectrum input exact support |
|---:|---:|---:|---:|
| **8** | 0/20 | 0/20 | 0/20 |
| **24** | 0/20 | 10/20 | **11/20** |
| **48** | 0/20 | 19/20 | **20/20** |

The remote (+17,−9) link itself was recovered:

| Number of probes | Smooth | White | Flat spectrum |
|---:|---:|---:|---:|
| 8 | 0/20 | 1/20 | 2/20 |
| 24 | 0/20 | 18/20 | 18/20 |
| 48 | 0/20 | 20/20 | 20/20 |

The smooth probes excited only **3.4–3.5%** of the spatial spectral bins above the declared information threshold. The white and flat-spectrum ensembles excited effectively **100%** under the same threshold. This is a simple observable excitation diagnostic: the smooth measurements never contained the high-frequency information required for localized inverse FFT support recovery.

**Null world:** zero false-positive trials among **60** independent cases (20 seeds × three probe counts). The family-wise Gaussian cutoff was fixed before running them; the observed zero is not a universal guarantee of zero false positives.

### What is interesting

The source signal's **geometric support**, rather than its total amplitude or smooth visual appearance, controlled what could be recovered. With the same injected energy and the same sensor static, 48 flat-spectrum probes recovered the unknown remote address and the complete spatial stencil in 20/20 cases. Smooth probes failed in all 20 cases.

This is *not new mathematical physics*: it is what full-band spectral identification predicts. The value is that this new executable, truth-withheld gate replicates the intuition behind SighImageInverse, BlackBoxSpotlight and Luotain2 on an actual Luotain2 synthetic law.

### The remaining limitation that matters most

The difficult part of Luotain2 is **not** that the remote link can never be seen. If you can actively inject rich spatial patterns and the system is linear and shift invariant, a standard inverse FFT can uncover the kernel. The hard problem is **passive, noisy, time-delayed, potentially nonlinear dynamics**, where you do not control the latent input and a naive Fourier transfer is not justified.

The right follow-up is therefore to test *learner-designed feasible excitation* against ordinary white probing under the *original multi-frame wormhole simulator*, with the input-to-operator feedback genuinely hidden from the design algorithm. The first successful static kernel inversion should **not** be treated as a full solution.

## Reproduction

    python -m pip install numpy pytest
    python -m pytest -q
    python -m blind_kernel_gate --out results --seeds 20

[Source](blind_kernel_gate.py) · [tests](tests/test_blind_kernel_gate.py) · [workflow](.github/workflows/gate003.yml) · [compact persistent results](results/gate003_summary.json) · [complete CI artifact](https://github.com/anttiluode/Theorem/actions/runs/45039881706/artifacts/14760799250).

**Conclusion:** a noisy hidden spatial link can be recovered through externally designed, spectral-support-complete observations. That is an instrumental capability, not yet a scientific novelty or general law of learning.
