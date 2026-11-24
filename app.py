import tkinter as tk
from tkinter import ttk, messagebox

import numpy as np
import matplotlib
matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from matplotlib.lines import Line2D

import orbit


METHODS = {
    "Euler-Cromer": "euler",
    "Verlet": "verlet",
    "RK4": "rk4"
}

METHOD_COLORS = {
    "Euler-Cromer": "#ff718d",
    "Verlet": "#65d6e8",
    "RK4": "#d7b8ff"
}

BODY_COLORS = ["#d7b8ff", "#65d6e8", "#ffb86b", "#ff718d"]


class OrbitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ORBIT | Gravitational Mechanics Simulator")
        self.root.geometry("1250x850")
        self.root.minsize(950, 680)
        self.root.configure(bg="#15121f")

        self.animation = None
        self.running = False
        self.times = None
        self.history = None
        self.energies = None
        self.frame_indices = None
        self.lines = []
        self.points = []

        self.system_var = tk.StringVar(value="Solar system")
        self.integrator_var = tk.StringVar(value="Verlet")
        self.dt_var = tk.StringVar(value="0.002")
        self.duration_var = tk.StringVar(value="1.0")
        self.status_var = tk.StringVar(value="Ready")
        self.time_var = tk.StringVar(value="Time: —")

        self.build_interface()
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def build_interface(self):
        header = tk.Frame(self.root, bg="#211b30", padx=20, pady=14)
        header.pack(fill="x")

        tk.Label(
            header, text="ORBIT",
            bg="#211b30", fg="#d7b8ff",
            font=("Arial", 24, "bold")
        ).pack(side="left")

        tk.Label(
            header, text="GRAVITATIONAL MECHANICS SIMULATOR",
            bg="#211b30", fg="#aaa0bb",
            font=("Arial", 10)
        ).pack(side="left", padx=16, pady=(8, 0))

        controls = tk.Frame(self.root, bg="#211b30", padx=14, pady=12)
        controls.pack(fill="x")

        self.add_selector(
            controls, "SYSTEM", self.system_var,
            ["Solar system", "Three-body"]
        )
        self.add_selector(
            controls, "INTEGRATOR", self.integrator_var,
            list(METHODS.keys())
        )
        self.add_entry(controls, "TIME STEP", self.dt_var)
        self.add_entry(controls, "DURATION", self.duration_var)

        self.make_button(
            controls, "RUN SIMULATION",
            self.run_simulation, "#8156b3"
        )
        self.make_button(
            controls, "COMPARE INTEGRATORS",
            self.compare_integrators, "#426f91"
        )

        self.pause_button = self.make_button(
            controls, "PAUSE", self.toggle_pause, "#393047"
        )
        self.pause_button.config(state="disabled")

        self.reset_button = self.make_button(
            controls, "RESTART", self.restart_animation, "#393047"
        )
        self.reset_button.config(state="disabled")

        plot_frame = tk.Frame(self.root, bg="#15121f", padx=12, pady=12)
        plot_frame.pack(fill="both", expand=True)

        self.figure = Figure(figsize=(11, 6), dpi=100)
        self.figure.patch.set_facecolor("#15121f")

        self.ax_orbit = self.figure.add_subplot(121)
        self.ax_energy = self.figure.add_subplot(122)

        self.style_axes()
        self.figure.subplots_adjust(
            left=0.07, right=0.97, top=0.90,
            bottom=0.12, wspace=0.28
        )

        self.canvas = FigureCanvasTkAgg(
            self.figure, master=plot_frame
        )
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        footer = tk.Frame(self.root, bg="#211b30", padx=18, pady=10)
        footer.pack(fill="x")

        tk.Label(
            footer, textvariable=self.status_var,
            bg="#211b30", fg="#c8b6df",
            font=("Arial", 10)
        ).pack(side="left")

        tk.Label(
            footer, textvariable=self.time_var,
            bg="#211b30", fg="#c8b6df",
            font=("Arial", 10)
        ).pack(side="right")

    def make_button(self, parent, text, command, color):
        button = tk.Button(
            parent, text=text, command=command,
            bg=color, fg="white",
            activebackground="#a477d4",
            activeforeground="white",
            relief="flat", padx=11, pady=9,
            font=("Arial", 8, "bold")
        )
        button.pack(side="left", padx=4)
        return button

    def add_selector(self, parent, label, variable, options):
        frame = tk.Frame(parent, bg="#211b30")
        frame.pack(side="left", padx=6)

        tk.Label(
            frame, text=label,
            bg="#211b30", fg="#a99bbd",
            font=("Arial", 8, "bold")
        ).pack(anchor="w")

        ttk.Combobox(
            frame, textvariable=variable,
            values=options, state="readonly", width=13
        ).pack(pady=(5, 0))

    def add_entry(self, parent, label, variable):
        frame = tk.Frame(parent, bg="#211b30")
        frame.pack(side="left", padx=6)

        tk.Label(
            frame, text=label,
            bg="#211b30", fg="#a99bbd",
            font=("Arial", 8, "bold")
        ).pack(anchor="w")

        tk.Entry(
            frame, textvariable=variable,
            width=8, bg="#30283e", fg="white",
            insertbackground="white", relief="flat"
        ).pack(ipady=5, pady=(5, 0))

    def style_axes(self):
        for ax in (self.ax_orbit, self.ax_energy):
            ax.clear()
            ax.set_facecolor("#1d1929")
            ax.tick_params(colors="#aaa0bb")
            ax.grid(True, color="#494052", alpha=0.35)

            for spine in ax.spines.values():
                spine.set_color("#51465e")

        self.ax_orbit.set_title(
            "ORBITAL TRAJECTORIES",
            color="#e4d8f2", fontsize=12, pad=12
        )
        self.ax_orbit.set_xlabel("X position", color="#b8adc7")
        self.ax_orbit.set_ylabel("Y position", color="#b8adc7")

        self.ax_energy.set_title(
            "RELATIVE ENERGY ERROR",
            color="#e4d8f2", fontsize=12, pad=12
        )
        self.ax_energy.set_xlabel("Simulation time", color="#b8adc7")
        self.ax_energy.set_ylabel("|E - E₀| / |E₀|", color="#b8adc7")
        self.ax_energy.set_yscale("log")

    def get_configuration(self):
        dt = float(self.dt_var.get())
        duration = float(self.duration_var.get())

        if not np.isfinite(dt) or not np.isfinite(duration):
            raise ValueError("Values must be finite.")

        if dt <= 0 or duration <= 0:
            raise ValueError("Time step and duration must be positive.")

        steps = int(round(duration / dt))

        if steps < 1:
            raise ValueError("The selected time step is too large.")

        if steps > 500_000:
            raise ValueError("Maximum allowed: 500,000 steps.")

        scenario = self.system_var.get()

        system = (
            orbit.create_solar_system()
            if scenario == "Solar system"
            else orbit.create_three_body()
        )

        return system, dt, duration

    def energy_error(self, energies):
        initial = abs(float(energies[0]))

        if initial < 1e-14:
            scale = max(float(np.max(np.abs(energies))), 1e-14)
            return np.abs(energies - energies[0]) / scale

        return np.abs(energies - energies[0]) / initial

    def run_simulation(self):
        try:
            system, dt, duration = self.get_configuration()
            method_name = self.integrator_var.get()
            method = METHODS[method_name]

            self.stop_animation()
            self.status_var.set("Calculating simulation...")
            self.root.update_idletasks()

            times, history, energies, angular = orbit.simulate(
                system, method, dt, duration
            )

            self.times = times
            self.history = history
            self.energies = energies

            frame_count = min(len(times), 1600)
            self.frame_indices = np.linspace(
                0, len(times) - 1, frame_count, dtype=int
            )

            self.prepare_single_plot(system, method_name)
            self.draw_frame(0)

            self.pause_button.config(state="normal", text="PAUSE")
            self.reset_button.config(state="normal")

            self.status_var.set(
                f"Simulation | {system.names} | {method_name}"
            )
            self.start_animation()

        except Exception as error:
            self.status_var.set("Simulation error")
            messagebox.showerror("ORBIT", str(error))

    def prepare_single_plot(self, system, method_name):
        self.style_axes()

        self.ax_orbit.set_title(
            f"ORBITAL TRAJECTORIES — {method_name}",
            color="#e4d8f2", fontsize=11
        )

        max_radius = max(float(np.max(np.abs(self.history))), 1.0)
        limit = max_radius * 1.25

        self.ax_orbit.set_xlim(-limit, limit)
        self.ax_orbit.set_ylim(-limit, limit)
        self.ax_orbit.set_aspect("equal", adjustable="box")

        self.lines = []
        self.points = []

        for i, name in enumerate(system.names):
            color = BODY_COLORS[i % len(BODY_COLORS)]

            line, = self.ax_orbit.plot(
                [], [], color=color, linewidth=1.3, alpha=0.7
            )
            point, = self.ax_orbit.plot(
                [], [], marker="o", linestyle="None",
                color=color, markersize=7
            )

            self.lines.append(line)
            self.points.append(point)

        self.ax_orbit.legend(
            handles=[
                Line2D([0], [0], color=BODY_COLORS[i % len(BODY_COLORS)],
                       marker="o", label=name)
                for i, name in enumerate(system.names)
            ],
            facecolor="#292235", edgecolor="#51465e",
            labelcolor="#e4d8f2"
        )

        error = self.energy_error(self.energies)
        positive = np.maximum(error, 1e-16)

        self.ax_energy.plot(
            self.times, positive,
            color=METHOD_COLORS[method_name],
            linewidth=1.4, label=method_name
        )
        self.ax_energy.legend(
            facecolor="#292235", edgecolor="#51465e",
            labelcolor="#e4d8f2"
        )

        self.canvas.draw_idle()

    def draw_frame(self, animation_frame):
        if self.history is None:
            return

        index = self.frame_indices[animation_frame]
        positions = self.history[index]
        trail_start = max(0, index - 500)

        for i, (line, point) in enumerate(zip(self.lines, self.points)):
            trail = self.history[trail_start:index + 1, i, :]
            line.set_data(trail[:, 0], trail[:, 1])
            point.set_data([positions[i, 0]], [positions[i, 1]])

        self.time_var.set(f"Time: {self.times[index]:.4f}")
        self.canvas.draw_idle()

    def start_animation(self):
        if self.frame_indices is None or len(self.frame_indices) < 2:
            return

        self.running = True
        self.animation = FuncAnimation(
            self.figure,
            self.animate,
            frames=len(self.frame_indices),
            interval=25,
            repeat=True,
            blit=False,
            cache_frame_data=False
        )
        self.canvas.draw_idle()

    def animate(self, frame):
        if self.running:
            self.draw_frame(frame)

    def toggle_pause(self):
        if self.animation is None:
            return

        if self.running:
            self.running = False
            self.animation.event_source.stop()
            self.pause_button.config(text="RESUME")
            self.status_var.set("Paused")
        else:
            self.running = True
            self.animation.event_source.start()
            self.pause_button.config(text="PAUSE")
            self.status_var.set("Running")

    def restart_animation(self):
        if self.animation is None:
            return

        self.animation.event_source.stop()
        self.running = True
        self.draw_frame(0)
        self.animation.frame_seq = self.animation.new_frame_seq()
        self.animation.event_source.start()
        self.pause_button.config(text="PAUSE")
        self.status_var.set("Running")

    def compare_integrators(self):
        try:
            system, dt, duration = self.get_configuration()

            self.stop_animation()
            self.status_var.set("Comparing numerical integrators...")
            self.root.update_idletasks()

            results = {}

            for name, method in METHODS.items():
                times, history, energies, angular = orbit.simulate(
                    system, method, dt, duration
                )

                results[name] = {
                    "times": times,
                    "history": history,
                    "energies": energies
                }

            self.draw_comparison(system, results)

            self.pause_button.config(state="disabled")
            self.reset_button.config(state="disabled")
            self.status_var.set(
                f"Comparison complete | {system.names} | dt={dt:g}"
            )
            self.time_var.set(f"Duration: {duration:g}")

        except Exception as error:
            self.status_var.set("Comparison error")
            messagebox.showerror("ORBIT", str(error))

    def draw_comparison(self, system, results):
        self.style_axes()

        self.ax_orbit.set_title(
            "TRAJECTORY COMPARISON",
            color="#e4d8f2", fontsize=11
        )
        self.ax_orbit.set_aspect("equal", adjustable="datalim")

        max_radius = max(
            float(np.max(np.abs(item["history"])))
            for item in results.values()
        )
        limit = max(max_radius * 1.15, 1.0)
        self.ax_orbit.set_xlim(-limit, limit)
        self.ax_orbit.set_ylim(-limit, limit)

        styles = {
            "Euler-Cromer": "--",
            "Verlet": "-",
            "RK4": ":"
        }

        for body_index, body_name in enumerate(system.names):
            body_color = BODY_COLORS[body_index % len(BODY_COLORS)]

            for method_name, result in results.items():
                trajectory = result["history"][:, body_index, :]

                self.ax_orbit.plot(
                    trajectory[:, 0],
                    trajectory[:, 1],
                    color=body_color,
                    linestyle=styles[method_name],
                    linewidth=1.25,
                    alpha=0.9
                )

        method_handles = [
            Line2D(
                [0], [0],
                color=METHOD_COLORS[name],
                linestyle="-",
                linewidth=2,
                label=name
            )
            for name in METHODS
        ]

        self.ax_orbit.legend(
            handles=method_handles,
            facecolor="#292235", edgecolor="#51465e",
            labelcolor="#e4d8f2"
        )

        self.ax_energy.set_title(
            "ENERGY ERROR BY INTEGRATOR",
            color="#e4d8f2", fontsize=11
        )

        for method_name, result in results.items():
            error = self.energy_error(result["energies"])

            self.ax_energy.plot(
                result["times"],
                np.maximum(error, 1e-16),
                color=METHOD_COLORS[method_name],
                linewidth=1.4,
                label=method_name
            )

        self.ax_energy.legend(
            facecolor="#292235", edgecolor="#51465e",
            labelcolor="#e4d8f2"
        )

        self.canvas.draw_idle()

    def stop_animation(self):
        self.running = False

        if self.animation is not None:
            self.animation.event_source.stop()
            self.animation = None

    def close(self):
        self.stop_animation()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = OrbitApp(root)
    root.mainloop()
