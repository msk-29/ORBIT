"""
ORBIT - Numerical Convergence Analysis

Measures the convergence order of Euler-Cromer, Verlet and RK4
using a full-trajectory comparison against a finer RK4 reference.
"""

import csv

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import orbit


DURATION = 0.73
TIME_STEPS = [0.02, 0.01, 0.005, 0.0025, 0.001, 0.0005]
REFERENCE_FACTOR = 20

METHODS = {
    "Euler-Cromer": "euler",
    "Verlet": "verlet",
    "RK4": "rk4",
}


def trajectory_error(history, reference):
    difference = history - reference

    pointwise = np.linalg.norm(difference, axis=2)
    scale = np.sqrt(np.mean(np.sum(reference**2, axis=2)))
    scale = max(float(scale), 1e-14)

    return float(np.sqrt(np.mean(pointwise**2)) / scale)


def estimate_order(step_sizes, errors):
    step_sizes = np.asarray(step_sizes)
    errors = np.asarray(errors)

    valid = (
        np.isfinite(step_sizes)
        & np.isfinite(errors)
        & (step_sizes > 0)
        & (errors > 0)
    )

    slope, _ = np.polyfit(
        np.log(step_sizes[valid]),
        np.log(errors[valid]),
        1
    )

    return float(slope)


def main():
    system_factory = orbit.create_solar_system

    results = {
        name: {"dt": [], "error": []}
        for name in METHODS
    }

    print("\nORBIT - NUMERICAL CONVERGENCE ANALYSIS")
    print("=" * 62)
    print(f"Duration: {DURATION} years")
    print(f"Reference factor: {REFERENCE_FACTOR}x")
    print("Comparison: full trajectory against fine-step RK4")
    print("\nCalculating...\n")

    for requested_dt in TIME_STEPS:
        steps = round(DURATION / requested_dt)
        actual_dt = DURATION / steps

        reference_steps = steps * REFERENCE_FACTOR
        reference_dt = DURATION / reference_steps

        reference_system = system_factory()
        _, reference_history, _, _ = orbit.simulate(
            reference_system,
            "rk4",
            reference_dt,
            DURATION
        )

        reference = reference_history[::REFERENCE_FACTOR]

        for name, method in METHODS.items():
            system = system_factory()

            _, history, _, _ = orbit.simulate(
                system,
                method,
                actual_dt,
                DURATION
            )

            if history.shape != reference.shape:
                raise RuntimeError(
                    f"Trajectory shape mismatch for {name}: "
                    f"{history.shape} vs {reference.shape}"
                )

            error = trajectory_error(history, reference)

            results[name]["dt"].append(actual_dt)
            results[name]["error"].append(error)

            print(
                f"{name:13s} | dt={actual_dt:.6f} "
                f"| trajectory error={error:.6e}"
            )

        print("-" * 62)

    print("\nEXPERIMENTAL CONVERGENCE ORDERS")
    print("=" * 45)

    expected_orders = {
        "Euler-Cromer": 1,
        "Verlet": 2,
        "RK4": 4,
    }

    for name, data in results.items():
        order = estimate_order(data["dt"], data["error"])

        print(
            f"{name:13s} | measured={order:.4f} "
            f"| expected≈{expected_orders[name]}"
        )

        data["measured_order"] = order
        data["expected_order"] = expected_orders[name]

    with open(
        "convergence_results.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "integrator",
            "dt",
            "trajectory_error",
            "measured_order",
            "expected_order"
        ])

        for name, data in results.items():
            for dt, error in zip(data["dt"], data["error"]):
                writer.writerow([
                    name,
                    dt,
                    error,
                    data["measured_order"],
                    data["expected_order"]
                ])

    fig, ax = plt.subplots(figsize=(9, 6))

    for name, data in results.items():
        ax.loglog(
            data["dt"],
            data["error"],
            marker="o",
            linewidth=2,
            label=f"{name} (p={data['measured_order']:.2f})"
        )

    ax.set_xlabel("Time step (dt)")
    ax.set_ylabel("Normalized RMS trajectory error")
    ax.set_title("ORBIT - Numerical Convergence")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    ax.invert_xaxis()

    fig.tight_layout()
    fig.savefig(
        "convergence_analysis.png",
        dpi=180,
        bbox_inches="tight"
    )
    plt.close(fig)

    print("\nGenerated:")
    print("  convergence_results.csv")
    print("  convergence_analysis.png")


if __name__ == "__main__":
    main()
