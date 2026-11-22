# Theorem Gate 005 — Private randomized intervention as IV, with unknown R

**Status: protocol and code committed, 2026-11-22.** This gate follows the temporal Gate 004 and is a new explicitly restricted synthetic experiment. It tests the core proposal from Neon, but refuses two unjustified shortcuts: an adaptively chosen control is NOT automatically exogenous, and a variogram does NOT universally reveal sensor noise without assumptions on the latent motion.

## What is hidden and what is assumed

World: a 64×64 periodic **linear, spatially shift-invariant convolutional** dynamical field.

    x[t+1] = H * (x[t] + u[t]) + process_noise[t]
    y[t]   = x[t] + sensor_noise[t]

The learner is not given the true kernel H, its local coefficients, the remote link offset or sign or coupling magnitude, or the sensor noise variance R. The simulator draws each of these independently in each world. There are also null worlds without a remote link.

However, the learner IS given: the linear shift-invariant operator family, the perfectly known additive input port, the exact action u[t], that the kernel is sparse, and that remote-link selection is outside a spatial radius of three grid positions. Sensor and process noises are independent of fresh intervention randomization. These are strong causal and structural assumptions, not open-world physics discovery.

The first 16 transitions are passive, followed by up to 48 actions on one continuously evolving latent field, with **no resets**.

## Why the random sign matters

At time t the agent chooses an action pattern v[t] using prior measurements and estimates. It then draws a fresh private independent random sign z[t] ∈ {-1,+1} and applies u[t] = action_budget × z[t] × v[t]. By construction E[u[t] | prior observations and state]=0 if the sign is genuinely independent of the latent system and noise.

The next output is y[t+1]=H*x[t] + H*u[t] + new_noise. Thus for each sufficiently excited Fourier coordinate k,

    E[conj(U[t,k]) * Y[t+1,k] | pre-kick history]
       = E[|U[t,k]|² | pre-kick history] * H[k].

Accumulate paired action/response cross-spectra and invert the Fourier transfer. This identifies a kernel from an **independent randomized input**, without regressing the noisy EEG-like current state on its noisy next state and without using R as a correction factor.

If instead one deterministically sets u[t] = -a*y[t]/||y[t]||, the chosen action is correlated with x[t] and sensor error[t]; the IV condition need not hold. Merely knowing the control numbers does not repair this endogeneity.

**Prior art:** externally randomized reference inputs and closed-loop IV are established system-identification techniques. This is an engineering demonstration, not a newly discovered theorem.

## How a remote link is selected without knowing R

The first half of the 48 independently randomized action/response pairs estimates the entire spatial impulse kernel. The largest estimated coefficient **outside the declared local neighborhood** is proposed as the remote link. A coefficient is accepted only if it exceeds a robust spatial median-absolute-deviation noise proxy by a fixed factor 3.4 in that first half and if the **second, separate half** independently confirms its sign and exceeds the same threshold.

This is **not a family-wise calibrated significance test**. Coefficient errors can be correlated in space and across time, and the sparse-kernel assumption is necessary for the spatial MAD proxy to behave like a noise estimate. No formal p-value or false-link guarantee is claimed.

The learner does **not estimate R**. It avoids needing it for the IV moment under explicitly independent action and future noise. WAIVES-style variogram extrapolation can conflate true microscale/process variation and measurement error; this gate deliberately does not equate an observed lag-variogram intercept with R.

## Controls and frozen evaluation

**Action policies**, equal L2 energy within each regime:

- White: broadband random full-field action, multiplied by private sign.
- Two-phase: first eight white actions; then a hybrid of 75% broadband action and 25% a Fourier mode selected from the two strongest estimated remote candidates. Renormalized to the same energy and multiplied by an independent sign chosen after selecting the shape.
- Fourier-only: a fresh random low-mid spatial Fourier wave per action, revealing the cost of incomplete spectral support.
- Feedback: deterministic noisy-state feedback without a private sign, showing that even a policy which sometimes classifies correctly may estimate biased coefficients.
- Placebo: the world receives a real white intervention, but the estimator is supplied an unrelated, never-injected randomized input of identical energy.
- Passive: receives no actions and therefore cannot construct the active-IV moment.

**Development seeds** 701–708 were used for design checks. The easy diagnostic regime includes previously inspected remote seeds 2101–2120 and no-link seeds 3101–3120; do not count it as a fresh holdout.

The **new, harder holdout** was fixed separately: remote seeds 2201–2240, null seeds 3201–3240. It has lower coupling magnitudes (0.045–0.075 vs 0.065–0.11), larger unknown per-world sensor SD (0.012–0.022 vs 0.006–0.014), and a smaller action budget (0.45 vs 0.70). These ranges describe how the simulator samples observations but are NOT supplied to the estimator.

All policies are scored at **12, 16, 24, 32, and 48 active steps**, including failed/abstaining cases. The claimed win condition is exact matching of the remote address, or correct refusal when no remote link exists. No oracle access during estimator updates or action choices.

This is not a fair cross-domain comparison to the particular 0.01 sensor SD in Gate 004; it is a new task that drops model-coefficient/noise knowledge and retains a strong active intervention port.

## Kill criteria and limitations

The central positive result must beat the placebo and Fourier-only controls, not merely solve easy simulations. The white-noise baseline is strong and **may beat two-phase**. If it does, report the failure of the adaptive advantage, even if both recover a link.

A successful result does NOT imply:
- valid IV for arbitrary feedback laws or nonrandomized kicks;
- known-R corrections are universally unnecessary;
- all noise colors and temporal correlations are harmless;
- blind recovery of nonlinear or multi-lag Luotain2 equations;
- a statistically corrected universal family-wise no-link test;
- real EEG tissue/source localization or LLM model-collapse measurement.

For related prior art, see [instrumental-variable methods for closed-loop system identification](https://www.sciencedirect.com/science/article/pii/S0005109804002845), [minimum external excitation](https://www.sciencedirect.com/science/article/pii/S0959152415000207), and [variogram nugget/measurement ambiguity](https://support.sas.com/documentation/cdl/en/statug/66859/HTML/default/statug_variogram_details02.htm).

## Reproduce

    python -m pip install numpy pytest
    python -m pytest -q
    python -m active_iv_gate --quick
    python -m active_iv_gate --out results

The CI workflow stores exact per-seed observations, selected addresses, local coefficient errors, active action histories and the split-sample evidence. No EEG or other private data is used.
