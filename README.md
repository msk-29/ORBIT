# ORBIT — Gravitational Mechanics Simulator

ORBIT is a two-dimensional gravitational mechanics simulator developed in
Python. It models interacting celestial bodies using Newton's law of universal
gravitation and compares three numerical integration methods.

## Features

- Interactive graphical interface built with Tkinter and Matplotlib.
- Solar system and three-body simulation scenarios.
- Animated orbital trajectories.
- Comparison of three numerical integrators:
  - Euler-Cromer
  - Velocity Verlet
  - Fourth-order Runge-Kutta (RK4)
- Energy and angular momentum diagnostics.
- Numerical accuracy and convergence analysis.
- CSV exports and scientific plots.

## Physics

The simulator uses Newton's law of universal gravitation:

F = G m1 m2 / r²

The acceleration of each body is calculated from the gravitational influence
of all other bodies in the system.

The numerical methods approximate the equations of motion over discrete
time steps. Their accuracy and conservation properties are evaluated using
mechanical energy, angular momentum, and trajectory comparisons.

## Numerical methods

| Method | Order | Main characteristic |
|---|---:|---|
| Euler-Cromer | 1 | Simple symplectic method |
| Velocity Verlet | 2 | Good long-term energy behavior |
| RK4 | 4 | High local accuracy |

## Installation

Requirements: Python 3, NumPy, and Matplotlib. Tkinter must also be available
in the Python installation.

Clone the repository and enter its directory:

    git clone YOUR_REPOSITORY_URL
    cd YOUR_REPOSITORY_NAME

Create and activate a virtual environment:

    python -m venv .venv
    source .venv/bin/activate

Install dependencies:

    python -m pip install -r requirements.txt

## Run the application

Launch the interactive simulator:

    python app.py

Choose a simulation scenario, select an integration method, and run an
individual simulation or compare all three methods.

## Scientific experiments

The project includes separate scripts for numerical analysis:

    python experiment.py
    python diagnostics.py
    python convergence.py
    python analysis_metrics.py

These experiments evaluate integration error, conservation of physical
quantities, orbital behavior, and numerical convergence.

Results are exported as CSV files and PNG plots.

## Limitations

- The simulations are two-dimensional.
- The gravitational model is Newtonian.
- Bodies are treated as point masses.
- The solar scenario is an idealized Sun-Earth two-body system, not a complete
  model of the Solar System.
- Numerical reference solutions are approximations, not exact analytical
  solutions.

## Technologies

- Python
- NumPy
- Matplotlib
- Tkinter
- CSV
- Git

## AI assistance

OpenAI ChatGPT was used during development for implementation assistance,
debugging, documentation, and analysis. The project code and numerical
results should be reviewed and understood by the author.

## Author

Developed as a CS50 final project.
