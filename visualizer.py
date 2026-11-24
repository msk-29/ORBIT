"""
ORBIT - Interactive Orbital Visualizer

Animated visualization of Newtonian gravitational systems.

Controls:
    SPACE: Pause / resume
    Q: Close simulation

AI assistance: OpenAI ChatGPT assisted with implementation.
"""

import argparse
import numpy as np
import matplotlib

# Use an interactive backend for the orbital animation.
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from orbit import (
    create_solar_system,
    create_three_body,
    simulate
)


def main():
    parser = argparse.ArgumentParser(
        description="ORBIT - Interactive Orbital Visualizer"
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

    parser.add_argument("--dt", type=float, default=0.002)
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

    print("ORBIT - INTERACTIVE VISUALIZER")
    print(f"Scenario: {args.scenario}")
    print(f"Integrator: {args.integrator}")
    print(f"Duration: {duration}")
    print(f"Timestep: {args.dt}")
    print("\nCalculating trajectories...")

    times, history, energies, angular = simulate(
        system,
        args.integrator,
        args.dt,
        duration
    )

    print("Simulation ready.")
    print("SPACE: pause/resume | Q: close")

    # Limit displayed frames while retaining the complete simulation.
    max_frames = 1500
    stride = max(1, len(times) // max_frames)
    frame_indices = list(range(0, len(times), stride))

    if frame_indices[-1] != len(times) - 1:
        frame_indices.append(len(times) - 1)

    # Determine plot boundaries.
    all_positions = history.reshape(-1, 2)

    minimum = np.min(all_positions, axis=0)
    maximum = np.max(all_positions, axis=0)

    center = (minimum + maximum) / 2
    span = max(np.max(maximum - minimum), 0.1)
    margin = span * 0.15

    fig, ax = plt.subplots(figsize=(9, 9))
    fig.subplots_adjust(bottom=0.13)

    ax.set_xlim(
        center[0] - span / 2 - margin,
        center[0] + span / 2 + margin
    )

    ax.set_ylim(
        center[1] - span / 2 - margin,
        center[1] + span / 2 + margin
    )

    ax.set_aspect("equal")
    ax.set_xlabel(f"X ({system.unit})")
    ax.set_ylabel(f"Y ({system.unit})")
    ax.set_title(
        f"ORBIT | {args.scenario.upper()} | "
        f"{args.integrator.upper()}"
    )
    ax.grid(True, alpha=0.3)

    lines = []
    bodies = []

    for i, name in enumerate(system.names):
        line, = ax.plot(
            [], [],
            linewidth=1.2,
            label=name
        )

        body, = ax.plot(
            [], [],
            marker="o",
            linestyle="None",
            markersize=8,
            label=f"{name} position"
        )

        lines.append(line)
        bodies.append(body)

    time_label = ax.text(
        0.02, 0.96,
        "",
        transform=ax.transAxes,
        verticalalignment="top"
    )

    ax.legend(loc="upper right")

    paused = False

    def update(frame):
        index = frame_indices[frame]
        current = history[index]

        for i in range(len(system.names)):
            trail = history[:index + 1, i]

            lines[i].set_data(
                trail[:, 0],
                trail[:, 1]
            )

            bodies[i].set_data(
                [current[i, 0]],
                [current[i, 1]]
            )

        time_label.set_text(
            f"Time: {times[index]:.4f} / {duration:.4f}"
        )

        return [*lines, *bodies, time_label]

    def on_key(event):
        nonlocal paused

        if event.key == " ":
            if paused:
                animation.event_source.start()
                paused = False
            else:
                animation.event_source.stop()
                paused = True

        elif event.key == "q":
            plt.close(fig)

    fig.canvas.mpl_connect("key_press_event", on_key)

    animation = FuncAnimation(
        fig,
        update,
        frames=len(frame_indices),
        interval=20,
        blit=True,
        repeat=True
    )

    plt.show()


if __name__ == "__main__":
    main()
