"""
ORBIT - Long-Term Orbital Diagnostics

Studies the long-term stability of numerical integrators
using energy, angular momentum and Keplerian orbital elements.

AI assistance: OpenAI ChatGPT assisted with implementation.
"""

import csv
import numpy as np
import matplotlib.pyplot as plt

from orbit import (
    create_solar_system,
    INTEGRATORS,
    total_energy,
    angular_momentum
)


DURATION = 50.0
DT = 0.001
SAMPLE_EVERY = 10

METHODS = ["euler", "verlet", "rk4"]


def orbital_elements(r, v, system):
    """Calculate osculating Keplerian elements for Earth relative to Sun."""

    relative_r = r[1] - r[0]
    relative_v = v[1] - v[0]

    distance = np.linalg.norm(relative_r)
    mu = system.G * (system.masses[0] + system.masses[1])

    if distance < 1e-12:
        return np.nan, np.nan

    specific_energy = (
        0.5 * np.dot(relative_v, relative_v)
        - mu / distance
    )

    if specific_energy >= 0:
        return np.nan, np.nan

    semi_major_axis = -mu / (2 * specific_energy)

    h = (
        relative_r[0] * relative_v[1]
        - relative_r[1] * relative_v[0]
    )

    eccentricity_vector = np.array([
        relative_v[1] * h / mu,
        -relative_v[0] * h / mu
    ]) - relative_r / distance

    eccentricity = np.linalg.norm(eccentricity_vector)

    return semi_major_axis, eccentricity


def run_diagnostics(system, method_name):
    """Run a long simulation and record physical diagnostics."""

    steps = int(round(DURATION / DT))
    dt = DURATION / steps

    r = system.positions.copy()
    v = system.velocities.copy()

    integrator = INTEGRATORS[method_name]

    initial_energy = total_energy(
        r, v, system.masses, system.G
    )

    initial_angular = angular_momentum(
        r, v, system.masses
    )

    records = []

    for step in range(steps + 1):

        if step % SAMPLE_EVERY == 0 or step == steps:
            time = step * dt

            energy = total_energy(
                r, v, system.masses, system.G
            )

            angular = angular_momentum(
                r, v, system.masses
            )

            energy_error = abs(
                (energy - initial_energy)
                / max(abs(initial_energy), 1e-30)
            )

            angular_error = abs(
                (angular - initial_angular)
                / max(abs(initial_angular), 1e-30)
            )

            semi_major_axis, eccentricity = orbital_elements(
                r, v, system
            )

            records.append({
                "method": method_name,
                "time_years": time,
                "energy_error": energy_error,
                "angular_error": angular_error,
                "semi_major_axis_AU": semi_major_axis,
                "eccentricity": eccentricity
            })

        if step < steps:
            r, v = integrator(
                r, v, system.masses, system.G, dt
            )

            if not np.all(np.isfinite(r)) or not np.all(np.isfinite(v)):
                raise FloatingPointError(
                    f"{method_name}: numerical instability at step {step}"
                )

    return records


def main():
    system = create_solar_system()

    print("\nORBIT - LONG-TERM ORBITAL DIAGNOSTICS")
    print("=" * 65)
    print(f"Duration: {DURATION} years")
    print(f"Timestep: {DT} years")
    print(f"Integrator methods: {', '.join(METHODS)}")
    print("\nStarting simulations...")

    all_records = []

    for method in METHODS:
        print(f"\nRunning {method.upper()}...")

        records = run_diagnostics(system, method)
        all_records.extend(records)

        max_energy = max(
            item["energy_error"] for item in records
        )

        max_angular = max(
            item["angular_error"] for item in records
        )

        valid_a = [
            item["semi_major_axis_AU"]
            for item in records
            if np.isfinite(item["semi_major_axis_AU"])
        ]

        valid_e = [
            item["eccentricity"]
            for item in records
            if np.isfinite(item["eccentricity"])
        ]

        print(f"Maximum energy error:   {max_energy:.6e}")
        print(f"Maximum angular error:  {max_angular:.6e}")

        if valid_a and valid_e:
            print(
                f"Semi-major axis range:  "
                f"{min(valid_a):.8f} - {max(valid_a):.8f} AU"
            )
            print(
                f"Eccentricity range:     "
                f"{min(valid_e):.8e} - {max(valid_e):.8e}"
            )

    # Export all measurements.
    with open(
        "diagnostics_results.csv",
        "w",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "method",
                "time_years",
                "energy_error",
                "angular_error",
                "semi_major_axis_AU",
                "eccentricity"
            ]
        )

        writer.writeheader()
        writer.writerows(all_records)

    # Plot long-term stability.
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    for method in METHODS:
        selected = [
            item for item in all_records
            if item["method"] == method
        ]

        times = np.array([
            item["time_years"] for item in selected
        ])

        energy = np.array([
            item["energy_error"] for item in selected
        ])

        angular = np.array([
            item["angular_error"] for item in selected
        ])

        semi_major = np.array([
            item["semi_major_axis_AU"] for item in selected
        ])

        eccentricity = np.array([
            item["eccentricity"] for item in selected
        ])

        axes[0, 0].semilogy(
            times,
            np.maximum(energy, 1e-18),
            label=method.upper()
        )

        axes[0, 1].semilogy(
            times,
            np.maximum(angular, 1e-18),
            label=method.upper()
        )

        axes[1, 0].plot(
            times,
            semi_major,
            label=method.upper()
        )

        axes[1, 1].plot(
            times,
            eccentricity,
            label=method.upper()
        )

    axes[0, 0].set_title("Relative energy error")
    axes[0, 1].set_title("Relative angular momentum error")
    axes[1, 0].set_title("Semi-major axis")
    axes[1, 1].set_title("Orbital eccentricity")

    axes[0, 0].set_ylabel("|ΔE / E₀|")
    axes[0, 1].set_ylabel("|ΔL / L₀|")
    axes[1, 0].set_ylabel("Semi-major axis (AU)")
    axes[1, 1].set_ylabel("Eccentricity")

    for ax in axes.flat:
        ax.set_xlabel("Time (years)")
        ax.grid(True)
        ax.legend()

    fig.suptitle(
        "ORBIT - Long-Term Numerical Stability",
        fontsize=15
    )

    plt.tight_layout()
    plt.savefig(
        "orbital_diagnostics.png",
        dpi=200
    )
    plt.close(fig)

    print("\nFiles generated:")
    print("- diagnostics_results.csv")
    print("- orbital_diagnostics.png")


if __name__ == "__main__":
    main()
