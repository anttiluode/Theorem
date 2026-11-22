"""Gate 006 — stress the causal boundary of private-action IV.

This is a *new, synthetic test* of the Gate 005 estimator, not a claim
of new system-identification mathematics.

The learned object is the input-command -> observed-next-field response.
If the physical actuator has transfer G and the world has transfer H,
the immediate IV moment identifies H*G, not necessarily H.

Fresh independently signed commands remain orthogonal to autonomous and
sensor disturbances even when those disturbances are temporally colored,
provided the new sign is conditionally independent. Temporal correlation
can still degrade finite-sample variance and confidence calibration.

Unknown delayed actuation can make the ZERO-LAG instrument miss the law;
re-pairing the same data with the correct lag restores the direct moment.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

from active_iv_gate import (
    N, M, make_kernel, motion, white, kernel_from_spectrum, decide,
)

PASSIVE = 16
ACTIONS = 48
BUDGET = .45
PAIR_LAGS = (0, 1)
CASES = (
    "iid",
    "temporal_ar085",
    "spatial_colored",
    "temporal_spatial_colored",
    "independent_actuator_noise",
    "unknown_gain",
    "shifted_actuator",
    "delayed_actuator",
)
SHIFT = (5, 7)
LOCAL = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1))


def sensor_series(rng, kind, count, sd):
    """Output noise independent of each NEW intervention sign.

    AR(1) parameter refers to sensor TIME correlation per pixel.
    The spatial case correlates neighboring detector pixels. All cases
    have approximately the same stationary marginal per-pixel SD.
    """
    rho = .85 if kind in ("temporal_ar085", "temporal_spatial_colored") else 0.
    spatial = kind in ("spatial_colored", "temporal_spatial_colored")
    state = rng.normal(0., sd, size=(N, N))
    out = []
    for _ in range(count):
        if rho:
            state = rho * state + np.sqrt(1. - rho * rho) * rng.normal(
                0., sd, size=(N, N))
        else:
            state = rng.normal(0., sd, size=(N, N))
        x = state
        if spatial:
            # A simple correlated detector with unit expected variance
            # for stationary independent spatial innovations.
            x = (state + .8 * np.roll(state, 1, axis=1)) / np.sqrt(1. + .8**2)
        out.append(x.copy())
    return out


def actual_actuation(command, previous, case, rng):
    """How the *physical* action differs from the commanded action."""
    if case == "independent_actuator_noise":
        return command + .65 * BUDGET * white(rng)
    if case == "unknown_gain":
        return .55 * command
    if case == "shifted_actuator":
        return np.roll(command, SHIFT, axis=(0, 1))
    if case == "delayed_actuator":
        return previous
    return command


def estimate_action_transfer(commands, outputs, lag=0):
    """Only paired command-output records; no h, R, truth or actuator.

    lag=0 uses U_t with Y_(t+1); lag=1 uses U_(t-1) with Y_(t+1).
    No oracle lag selection is made by the estimator: both analyses are
    explicitly defined arms, and their different assumptions are reported.
    """
    if lag not in PAIR_LAGS:
        raise ValueError("Only preregistered action lags 0 or 1 supported")
    if len(commands) != len(outputs) or len(commands) < 8:
        raise ValueError("Need matched command and next-observation arrays")
    if lag:
        us, ys = commands[:-lag], outputs[lag:]
    else:
        us, ys = commands, outputs
    mid = len(us) // 2

    def fit(one_u, one_y):
        num = np.zeros((N, N), dtype=complex)
        den = np.zeros((N, N), dtype=float)
        for u, y in zip(one_u, one_y):
            U = np.fft.fft2(u)
            num += np.conj(U) * np.fft.fft2(y)
            den += abs(U)**2
        return kernel_from_spectrum(num, den)[0]

    left = fit(us[:mid], ys[:mid])
    right = fit(us[mid:], ys[mid:])
    chosen, evidence = decide(left, right)  # identical frozen Gate005 rule
    hhat = .5 * (left + right)
    return {
        "chosen": chosen,
        "evidence": evidence,
        "local_mae_vs_given_h": None,  # scoring only, not part of estimator
        "estimate": hhat,
        "first": left,
        "second": right,
        "n_pairs": len(us),
    }


def run_case(seed, case="iid", remote=True, lag=0):
    if case not in CASES:
        raise ValueError(case)
    rw = np.random.default_rng(seed + 50000)
    ra = np.random.default_rng(seed + 100000)
    rn = np.random.default_rng(seed + 150000)
    rs = np.random.default_rng(seed + 170000)
    h, true_remote = make_kernel(rw, remote, remote_range=(.045, .075))
    H = np.fft.fft2(h)
    sd = float(rw.uniform(.012, .022))
    YY, XX = np.indices((N, N))
    x = .25 * np.cos(2*np.pi*(YY + 2*XX)/N + rw.uniform(-np.pi, np.pi))
    noise = sensor_series(rs, case, PASSIVE + ACTIONS + 1, sd)
    commands, observations = [], []
    previous_command = np.zeros((N, N))
    u_rms = []
    for t in range(PASSIVE + ACTIONS):
        if t < PASSIVE:
            cmd = np.zeros((N, N))
        else:
            # Fresh private randomized action, independent of previous state
            # and all sensor errors; white energy is exactly BUDGET.
            cmd = BUDGET * white(ra) * ra.choice([-1, 1])
        physical = actual_actuation(cmd, previous_command, case, rn)
        # Never treat actuator error as observed action; exact physical
        # actuation is known only inside the simulator.
        x = motion(x + physical, H) + .0005 * rn.normal(size=(N, N))
        y = x + noise[t + 1]
        if t >= PASSIVE:
            commands.append(cmd)
            observations.append(y)
            u_rms.append(float(np.linalg.norm(physical)))
        previous_command = cmd

    fitted = estimate_action_transfer(commands, observations, lag=lag)
    choice = fitted["chosen"]
    coeffs = fitted["estimate"]
    effective_h = h
    if case == "shifted_actuator":
        effective_h = np.roll(h, SHIFT, axis=(0, 1))
    if case == "unknown_gain":
        effective_h = .55 * h
    if case == "delayed_actuator" and lag == 0:
        # No instantaneous action gain. The observed cross moment may
        # nevertheless have finite-sample contamination.
        effective_h = np.zeros_like(h)
    local_mae = float(np.mean([abs(coeffs[d] - h[d]) for d in LOCAL]))
    effective_mae = float(np.mean([abs(coeffs[d] - effective_h[d])
                                    for d in LOCAL]))
    effective_kernel_mae = float(np.mean(abs(coeffs-effective_h)))
    return {
        "seed": int(seed),
        "case": case,
        "world": "remote" if remote else "null",
        "truth": list(true_remote) if true_remote else None,
        "reported": list(choice) if choice else None,
        "correct_world": bool(choice == true_remote) if remote else choice is None,
        "false_world_link": bool(not remote and choice is not None),
        "action_lag_used": lag,
        "n_action_pairs": fitted["n_pairs"],
        "mean_actual_action_norm": float(np.mean(u_rms)),
        "original_kernel_local_mae": local_mae,
        "effective_kernel_local_mae": effective_mae,
        "effective_kernel_all_mae": effective_kernel_mae,
        "declared_sensor_sd_hidden_from_estimator": sd,
        "reported_weight": fitted["evidence"]["holdout_weight"],
        "reported_uncertainty_proxy": fitted["evidence"]["holdout_noise_proxy"],
        "action_shift": list(SHIFT) if case == "shifted_actuator" else None,
    }


def group(rows):
    return {
        "correct": sum(x["correct_world"] for x in rows),
        "n": len(rows),
        "false_remote": sum(x["false_world_link"] for x in rows),
        "mean_local_mae_true": float(np.mean([
            x["original_kernel_local_mae"] for x in rows])),
        "mean_local_mae_effective": float(np.mean([
            x["effective_kernel_local_mae"] for x in rows])),
        "mean_all_mae_effective": float(np.mean([
            x["effective_kernel_all_mae"] for x in rows])),
    }


def evaluate(remote_seeds=range(4501, 4541),
             null_seeds=range(5501, 5541)):
    rows = []
    for case in CASES:
        for remote, seeds in ((True, remote_seeds), (False, null_seeds)):
            for seed in seeds:
                # Same simulator seeds and action sequence for two timing
                # estimators; the delayed case is analyzed with both.
                rows.append(run_case(seed, case, remote, lag=0))
                if case == "delayed_actuator":
                    rows.append(run_case(seed, case, remote, lag=1))
    groups = []
    for case in CASES:
        for lag in ((0, 1) if case == "delayed_actuator" else (0,)):
            for remote in (True, False):
                selected = [r for r in rows if r["case"] == case
                            and (r["world"] == "remote") == remote
                            and r["action_lag_used"] == lag]
                groups.append({
                    "case": case, "lag": lag,
                    "world": "remote" if remote else "null",
                    **group(selected)})
    return {
        "title": "Gate 006 — Private-action IV under noise and actuator distortion",
        "fixed_design": {
            "remote_seeds": list(remote_seeds),
            "null_seeds": list(null_seeds),
            "steps_passive": PASSIVE,
            "steps_active": ACTIONS,
            "command_l2_norm": BUDGET,
            "sensor_sd_world_range": [.012,.022],
            "unknown_local_kernel_coefficients": True,
            "unknown_remote_strength_sign_and_address": True,
            "unknown_sensor_noise_to_estimator": True,
            "frozen_robust_MAD_threshold": 3.4,
            "spatial_sensor_noise_nearest_neighbor_coefficient": .8,
            "sensor_temporal_ar": .85,
            "actuator_independent_noise_fraction": .65,
            "actuator_unknown_gain": .55,
            "actuator_hidden_spatial_shift": list(SHIFT),
            "actuator_hidden_delay_frames": 1,
            "lag_one_is_oracle_provided_analysis_arm": True,
        },
        "results": groups, "rows": rows,
        "limits": [
            "The learnable physical system is still a shift-invariant linear sparse convolution.",
            "The measured moment identifies the composite H*G if the actuator G is unknown.",
            "Lag=1 analysis is an explicitly calibrated comparison, NOT blind lag estimation.",
            "The null detection rule remains heuristic and uncalibrated for familywise error.",
            "Temporal AR sensor noise independent of private signs may change variance but not the population IV moment.",
            "Observing a wrong or correct address does not by itself prove physical source.",
        ],
    }


def markdown(data):
    lines = [
        "# Gate 006 — When does a private kick stop revealing the physical law?",
        "",
        "| Condition | Alignment | Real remote: exact | No remote: refused | Remote local MAE | Null false links |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for case in CASES:
        lags=(0,1) if case=="delayed_actuator" else (0,)
        for lag in lags:
            a=next(r for r in data["results"] if r["case"]==case and r["lag"]==lag and r["world"]=="remote")
            b=next(r for r in data["results"] if r["case"]==case and r["lag"]==lag and r["world"]=="null")
            lines.append(
                f"| {case} | {lag} | {a['correct']}/{a['n']} | {b['correct']}/{b['n']} | "
                f"{a['mean_local_mae_true']:.4f} | {b['false_remote']}/{b['n']} |")
    lines += [
        "",
        "An independent private sign remains a valid instrument under temporal sensor noise",
        "that is independent of that sign. Colored noise can still alter variance and break",
        "an uncalibrated significance threshold. No widening of the instrument lag is",
        "universally needed to restore the population moment.",
        "",
        "With unknown actuator gain, the action/output moment identifies scaled H.",
        "With a hidden spatial actuator shift, it identifies a shifted H; a no-link",
        "world may appear to contain a physically remote connection. An uncalibrated",
        "actuator lag can erase the immediate moment; supplying the correct known",
        "lag gives an alternative pairing of the same data.",
        "",
        "All conclusions are limited to this sparse linear convolution simulator.",
        "The spatial-MAD refusal criterion is heuristic, not a calibrated test.",
        "",
    ]
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="results")
    p.add_argument("--quick",action="store_true")
    args=p.parse_args()
    if args.quick:
        data=evaluate(range(701,705),range(801,805))
    else:
        data=evaluate()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    (out/"gate006.json").write_text(json.dumps(data,indent=2)+"\n")
    m=markdown(data)
    (out/"gate006.md").write_text(m)
    print(m,flush=True)


if __name__=="__main__":
    main()
