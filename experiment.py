
import csv
import numpy as np
import matplotlib.pyplot as plt

from orbit import (
    create_solar_system,
    simulate
)

METHODS = ["euler", "verlet", "rk4"]

TIMESTEPS = [
    0.02,
    0.01,
    0.005,
    0.0025,
    0.001,
    0.0005
]

DURATION = 1.0

results = []

print("\nORBIT - NUMERICAL EXPERIMENTS")
print("=" * 55)

for method in METHODS:
    for dt in TIMESTEPS:

        system = create_solar_system()

        times, history, energies, angular = simulate(
            system,
            method,
            dt,
            DURATION
        )

        energy_error = np.max(
            np.abs(
                (energies - energies[0])
                / abs(energies[0])
            )
        )

        angular_error = np.max(
            np.abs(
                (angular - angular[0])
                / abs(angular[0])
            )
        )

        results.append({
            "method": method,
            "dt": dt,
            "energy_error": energy_error,
            "angular_error": angular_error
        })

        print(
            f"{method:8} | dt={dt:.5f} | "
            f"Energy error={energy_error:.6e} | "
            f"Angular error={angular_error:.6e}"
        )


# Export results to CSV.
with open("experiment_results.csv", "w", newline="") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "method",
            "dt",
            "energy_error",
            "angular_error"
        ]
    )

    writer.writeheader()
    writer.writerows(results)


# Plot numerical convergence.
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

for method in METHODS:
    selected = [
        item for item in results
        if item["method"] == method
    ]

    axes[0].loglog(
        [x["dt"] for x in selected],
        [x["energy_error"] for x in selected],
        marker="o",
        label=method.upper()
    )

    axes[1].loglog(
        [x["dt"] for x in selected],
        [x["angular_error"] for x in selected],
        marker="o",
        label=method.upper()
    )

axes[0].set_title("Energy error convergence")
axes[0].set_xlabel("Time step (h)")
axes[0].set_ylabel("Maximum relative energy error")

axes[1].set_title("Angular momentum error")
axes[1].set_xlabel("Time step (h)")
axes[1].set_ylabel("Maximum relative angular momentum error")

for ax in axes:
    ax.grid(True, which="both")
    ax.legend()

plt.tight_layout()
plt.savefig("numerical_comparison.png", dpi=180)
plt.close(fig)

print("\nResults saved:")
print("- experiment_results.csv")
print("- numerical_comparison.png")
