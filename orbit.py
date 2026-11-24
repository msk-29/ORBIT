
"""
ORBIT v1.0
Computational Gravitational Mechanics

Educational scientific simulator using Newtonian gravity.

AI assistance: OpenAI ChatGPT was used during development
for implementation support and code generation.
"""

import argparse
from dataclasses import dataclass

import numpy as np
import matplotlib.pyplot as plt


@dataclass
class System:
    names: list
    masses: np.ndarray
    positions: np.ndarray
    velocities: np.ndarray
    G: float
    unit: str


def create_solar_system():
    # Astronomical units: AU, years, solar masses.
    return System(
        names=["Sun", "Earth"],
        masses=np.array([1.0, 3.003e-6]),
        positions=np.array([
            [0.0, 0.0],
            [1.0, 0.0]
        ]),
        velocities=np.array([
            [0.0, 0.0],
            [0.0, 2 * np.pi]
        ]),
        G=4 * np.pi**2,
        unit="AU / year"
    )


def create_three_body():
    # Figure-eight periodic solution.
    return System(
        names=["Body A", "Body B", "Body C"],
        masses=np.array([1.0, 1.0, 1.0]),
        positions=np.array([
            [-0.97000436, 0.24308753],
            [0.97000436, -0.24308753],
            [0.0, 0.0]
        ]),
        velocities=np.array([
            [0.466203685, 0.43236573],
            [0.466203685, 0.43236573],
            [-0.93240737, -0.86473146]
        ]),
        G=1.0,
        unit="normalized units"
    )


def acceleration(positions, masses, G):
    """Calculate gravitational acceleration of every body."""

    n = len(masses)
    result = np.zeros_like(positions)

    for i in range(n):
        for j in range(n):
            if i == j:
                continue

            displacement = positions[j] - positions[i]
            distance = np.linalg.norm(displacement)

            if distance < 1e-12:
                raise ValueError("Collision or singularity detected.")

            result[i] += (
                G * masses[j] * displacement / distance**3
            )

    return result


def total_energy(positions, velocities, masses, G):
    """Return total mechanical energy."""

    kinetic = 0.5 * np.sum(
        masses[:, None] * velocities**2
    )

    potential = 0.0
    n = len(masses)

    for i in range(n):
        for j in range(i + 1, n):
            distance = np.linalg.norm(
                positions[j] - positions[i]
            )

            if distance < 1e-12:
                raise ValueError("Singularity in energy calculation.")

            potential -= G * masses[i] * masses[j] / distance

    return kinetic + potential


def angular_momentum(positions, velocities, masses):
    """Calculate total angular momentum."""

    momentum = masses[:, None] * velocities

    if positions.shape[1] == 2:
        return np.sum(
            positions[:, 0] * momentum[:, 1]
            - positions[:, 1] * momentum[:, 0]
        )

    return np.sum(np.cross(positions, momentum))


def euler_cromer(r, v, masses, G, dt):
    a = acceleration(r, masses, G)

    new_v = v + a * dt
    new_r = r + new_v * dt

    return new_r, new_v


def velocity_verlet(r, v, masses, G, dt):
    a = acceleration(r, masses, G)

    new_r = r + v * dt + 0.5 * a * dt**2

    new_a = acceleration(new_r, masses, G)

    new_v = v + 0.5 * (a + new_a) * dt

    return new_r, new_v


def rk4(r, v, masses, G, dt):
    """Fourth-order Runge-Kutta integration."""

    def derivative(position, velocity):
        return velocity, acceleration(position, masses, G)

    k1r, k1v = derivative(r, v)

    k2r, k2v = derivative(
        r + 0.5 * dt * k1r,
        v + 0.5 * dt * k1v
    )

    k3r, k3v = derivative(
        r + 0.5 * dt * k2r,
        v + 0.5 * dt * k2v
    )

    k4r, k4v = derivative(
        r + dt * k3r,
        v + dt * k3v
    )

    new_r = r + dt / 6 * (
        k1r + 2*k2r + 2*k3r + k4r
    )

    new_v = v + dt / 6 * (
        k1v + 2*k2v + 2*k3v + k4v
    )

    return new_r, new_v


INTEGRATORS = {
    "euler": euler_cromer,
    "verlet": velocity_verlet,
    "rk4": rk4
}


def simulate(system, integrator, dt, duration):
    """Integrate the system and record physical diagnostics."""

    steps = int(round(duration / dt))

    if steps < 1:
        raise ValueError("Duration must be at least one timestep.")

    dt = duration / steps

    r = system.positions.copy()
    v = system.velocities.copy()

    history = np.zeros((steps + 1, *r.shape))
    energies = np.zeros(steps + 1)
    angular = np.zeros(steps + 1)
    times = np.linspace(0, duration, steps + 1)

    history[0] = r
    energies[0] = total_energy(
        r, v, system.masses, system.G
    )
    angular[0] = angular_momentum(
        r, v, system.masses
    )

    method = INTEGRATORS[integrator]

    for step in range(1, steps + 1):
        r, v = method(
            r, v, system.masses, system.G, dt
        )

        if not np.all(np.isfinite(r)) or not np.all(np.isfinite(v)):
            raise FloatingPointError(
                f"Numerical instability at step {step}"
            )

        history[step] = r
        energies[step] = total_energy(
            r, v, system.masses, system.G
        )
        angular[step] = angular_momentum(
            r, v, system.masses
        )

    return times, history, energies, angular



def analyze(system, times, energies, angular):
    e0 = energies[0]
    l0 = angular[0]

    energy_error = np.abs(
        (energies - e0) / max(abs(e0), 1e-30)
    )

    # Relative error is undefined when initial
    # angular momentum is zero.
    if abs(l0) > 1e-14:
        angular_error = np.abs(
            (angular - l0) / abs(l0)
        )
        angular_label = "Relative angular momentum error"
    else:
        angular_error = np.abs(angular - l0)
        angular_label = "Absolute angular momentum drift"

    print("\n========== ORBIT ANALYSIS ==========")
    print(f"System: {', '.join(system.names)}")
    print(f"Bodies: {len(system.masses)}")
    print(f"Duration: {times[-1]:.6f}")
    print(f"Initial energy: {e0:.12e}")
    print(f"Final energy:   {energies[-1]:.12e}")
    print(f"Maximum relative energy error: "
          f"{np.max(energy_error):.6e}")
    print(f"Initial angular momentum: {l0:.12e}")
    print(f"Final angular momentum:   {angular[-1]:.12e}")
    print(f"{angular_label}: "
          f"{np.max(angular_error):.6e}")
    print("====================================\n")

    return energy_error, angular_error



def plot_results(system, times, history, energies, angular,
                 energy_error, angular_error, integrator):

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))

    # Orbital trajectories.
    ax = axes[0, 0]

    for i, name in enumerate(system.names):
        ax.plot(
            history[:, i, 0],
            history[:, i, 1],
            label=name
        )

        ax.scatter(
            history[0, i, 0],
            history[0, i, 1],
            marker="o",
            s=35
        )

    ax.set_title("Gravitational trajectories")
    ax.set_xlabel(f"X ({system.unit})")
    ax.set_ylabel(f"Y ({system.unit})")
    ax.axis("equal")
    ax.grid(True)
    ax.legend()

    # Energy.
    axes[0, 1].plot(times, energies)
    axes[0, 1].set_title("Total mechanical energy")
    axes[0, 1].set_xlabel("Time")
    axes[0, 1].set_ylabel("Energy")
    axes[0, 1].grid(True)

    # Relative energy error.
    axes[1, 0].semilogy(
        times,
        np.maximum(energy_error, 1e-18)
    )
    axes[1, 0].set_title("Relative energy error")
    axes[1, 0].set_xlabel("Time")
    axes[1, 0].set_ylabel("|ΔE / E₀|")
    axes[1, 0].grid(True)

    # Angular momentum error.
    axes[1, 1].semilogy(
        times,
        np.maximum(angular_error, 1e-18)
    )
    axes[1, 1].set_title("Relative angular momentum error")
    axes[1, 1].set_xlabel("Time")
    axes[1, 1].set_ylabel("Angular momentum error")
    axes[1, 1].grid(True)

    fig.suptitle(
        f"ORBIT | {integrator.upper()} | {len(system.masses)} bodies",
        fontsize=15
    )

    plt.tight_layout()
    plt.savefig("orbit_results.png", dpi=180)
    print("Graph saved: orbit_results.png")

    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="ORBIT - Gravitational Mechanics Simulator"
    )

    parser.add_argument(
        "--scenario",
        choices=["solar", "three-body"],
        default="solar"
    )

    parser.add_argument(
        "--integrator",
        choices=["euler", "verlet", "rk4"],
        default="verlet"
    )

    parser.add_argument("--dt", type=float, default=0.001)
    parser.add_argument("--duration", type=float, default=None)

    args = parser.parse_args()

    if args.dt <= 0:
        parser.error("Timestep must be positive.")

    if args.duration is not None and args.duration <= 0:
        parser.error("Duration must be positive.")

    if args.scenario == "solar":
        system = create_solar_system()
        duration = args.duration or 1.0
    else:
        system = create_three_body()
        duration = args.duration or 6.3259

    print("\nORBIT v1.0")
    print("Computational Gravitational Mechanics")
    print(f"Integrator: {args.integrator}")
    print(f"Scenario: {args.scenario}")
    print(f"Timestep: {args.dt}")

    times, history, energies, angular = simulate(
        system,
        args.integrator,
        args.dt,
        duration
    )

    energy_error, angular_error = analyze(
        system, times, energies, angular
    )

    plot_results(
        system,
        times,
        history,
        energies,
        angular,
        energy_error,
        angular_error,
        args.integrator
    )


if __name__ == "__main__":
    main()
