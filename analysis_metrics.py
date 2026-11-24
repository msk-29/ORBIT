"""
ORBIT - Numerical Accuracy Analysis

Compares Euler-Cromer, Velocity Verlet and RK4 against
a finer-step RK4 reference solution.

Metrics:
- Normalized RMS position error
- Maximum normalized position error
- Maximum relative energy drift
- Maximum relative angular momentum drift
"""

import csv
import numpy as np
import matplotlib.pyplot as plt

from orbit import create_solar_system, simulate


DURATION = 1.0
DT = 0.002
REFERENCE_FACTOR = 20

METHODS = {
    "Euler-Cromer": "euler",
    "Verlet": "verlet",
    "RK4": "rk4"
}


def calculate_metrics(system, method, dt, reference):
    _, positions, energies, angular = simulate(
        system, method, dt, DURATION
    )

    reference_positions = reference[::REFERENCE_FACTOR]

    if positions.shape != reference_positions.shape:
        raise ValueError("Reference and simulation lengths do not match.")

    differences = positions - reference_positions

    scale = np.max(np.linalg.norm(reference_positions, axis=2))
    scale = max(scale, 1e-30)

    position_errors = np.linalg.norm(differences, axis=2) / scale

    rms_error = np.sqrt(np.mean(position_errors**2))
    max_error = np.max(position_errors)

    energy_drift = np.max(
        np.abs((energies - energies[0]) / max(abs(energies[0]), 1e-30))
    )

    angular_drift = np.max(
        np.abs((angular - angular[0]) / max(abs(angular[0]), 1e-30))
    )

    return {
        "integrator": next(
            name for name, key in METHODS.items() if key == method
        ),
        "dt": DT,
        "rms_position_error": rms_error,
        "max_position_error": max_error,
        "max_relative_energy_drift": energy_drift,
        "max_relative_angular_momentum_drift": angular_drift
    }


def main():
    system = create_solar_system()

    _, reference_positions, _, _ = simulate(
        system,
        "rk4",
        DT / REFERENCE_FACTOR,
        DURATION
    )

    results = []

    for name, method in METHODS.items():
        metrics = calculate_metrics(
            system, method, DT, reference_positions
        )
        results.append(metrics)

        print(f"\n{name}")
        print(f"  RMS position error:       {metrics['rms_position_error']:.6e}")
        print(f"  Maximum position error:   {metrics['max_position_error']:.6e}")
        print(f"  Energy drift:              {metrics['max_relative_energy_drift']:.6e}")
        print(f"  Angular momentum drift:    {metrics['max_relative_angular_momentum_drift']:.6e}")

    with open("accuracy_results.csv", "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    labels = [result["integrator"] for result in results]

    metrics_to_plot = [
        ("rms_position_error", "RMS position error"),
        ("max_position_error", "Maximum position error"),
        ("max_relative_energy_drift", "Relative energy drift"),
        ("max_relative_angular_momentum_drift", "Relative angular momentum drift")
    ]

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    for axis, (key, title) in zip(axes.flat, metrics_to_plot):
        values = [result[key] for result in results]
        axis.bar(labels, values)
        axis.set_title(title)
        axis.set_yscale("log")
        axis.set_ylabel("Error")
        axis.grid(axis="y", alpha=0.25)

    fig.suptitle("ORBIT - Numerical Accuracy Comparison")
    fig.tight_layout()
    fig.savefig("accuracy_comparison.png", dpi=180)
    plt.show()


if __name__ == "__main__":
    main()
