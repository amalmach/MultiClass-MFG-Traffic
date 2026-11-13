#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multi-Class Traffic Mean-Field Game — Numerical Demonstration
=============================================================

Sequential Newton–GMRES simulation of general J-class traffic
Mean-Field Games.

Supported models:
    GLWR — Generalized Lighthill–Whitham–Richards
    GS   — Generalized Separable
    GNS  — Generalized Non-Separable

The demonstration uses the numerical implementation in:

    src/newton_krylov/multi_class/
"""

import argparse
import sys

from argparse import Namespace
from pathlib import Path


# ============================================================
# 1. Project directories
# ============================================================

DEMO_DIR = Path(__file__).resolve().parent

ROOT_DIR = DEMO_DIR.parents[1]

SOLVER_DIR = (
    ROOT_DIR
    / "src"
    / "newton_krylov"
    / "multi_class"
)

sys.path.insert(0, str(SOLVER_DIR))


# ============================================================
# 2. Import the numerical implementation
# ============================================================

from inputs import get_inputs
from main import run_solver
from initial_conditions import get_initial_configuration

# ============================================================
# 3. Command-line interface
# ============================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Numerical demonstration of general J-class "
            "traffic Mean-Field Games."
        )
    )

    parser.add_argument(
        "--J",
        type=int,
        default=3,
        help="Number of vehicle classes (default: 3).",
    )

    parser.add_argument(
        "--model",
        type=str.upper,
        choices=("GLWR", "GS", "GNS"),
        default="GLWR",
        help="Traffic model (default: GLWR).",
    )

    parser.add_argument(
        "--configuration",
        type=str.upper,
        choices=("CT", "TC", "TCT"),
        default=None,
        help=(
            "Initial traffic configuration for J=2: "
            "CT, TC, or TCT. "
            "Default: original solver configuration."
        ),
    )

    parser.add_argument(
        "--sigma",
        type=float,
        default=0.15,
        help=(
            "Gaussian width for CT, TC, and TCT "
            "(default: 0.15)."
        ),
    )

    parser.add_argument(
        "--T",
        type=float,
        default=1.0,
        help="Simulation time horizon (default: 1.0).",
    )

    parser.add_argument(
        "--nx",
        type=int,
        default=5,
        help="Initial number of spatial cells (default: 5).",
    )

    parser.add_argument(
        "--nt",
        type=int,
        default=8,
        help="Minimum initial time steps (default: 8).",
    )

    parser.add_argument(
        "--max-grids",
        type=int,
        default=1,
        help="Number of grid-refinement levels (default: 1).",
    )

    parser.add_argument(
        "--newton-tol",
        type=float,
        default=1e-8,
        help="Newton residual tolerance (default: 1e-8).",
    )

    parser.add_argument(
        "--gmres-rtol",
        type=float,
        default=1e-8,
        help="GMRES relative tolerance (default: 1e-8).",
    )

    parser.add_argument(
        "--max-newton-iter",
        type=int,
        default=50,
        help="Maximum Newton iterations (default: 50).",
    )

    parser.add_argument(
        "--no-precond",
        action="store_true",
        help="Disable sparse LU preconditioning.",
    )

    parser.add_argument(
        "--no-multigrid",
        action="store_true",
        help="Disable interpolation between refined grids.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output .npz filename.",
    )

    return parser.parse_args()


# ============================================================
# 4. Validate numerical parameters
# ============================================================

def validate_arguments(args):

    if args.J < 1:
        raise ValueError(
            "The number of vehicle classes must be positive."
        )

    if args.T <= 0:
        raise ValueError(
            "The simulation time horizon must be positive."
        )

    if args.nx < 2:
        raise ValueError(
            "At least two spatial cells are required."
        )

    if args.nt < 2:
        raise ValueError(
            "At least two temporal steps are required."
        )

    if args.max_grids < 1:
        raise ValueError(
            "At least one grid level is required."
        )

    if args.newton_tol <= 0:
        raise ValueError(
            "Newton tolerance must be positive."
        )

    if args.gmres_rtol <= 0:
        raise ValueError(
            "GMRES tolerance must be positive."
        )

    if args.max_newton_iter < 1:
        raise ValueError(
            "Maximum Newton iterations must be positive."
        )

    if args.configuration is not None and args.J != 2:
        raise ValueError(
            "CT, TC, and TCT configurations require J=2."
        )

    if args.sigma <= 0:
        raise ValueError(
            "Gaussian width must be positive."
        )


# ============================================================
# 5. Prepare the numerical experiment
# ============================================================

def prepare_experiment(args):

    # Load the original physical configuration.
    parameters = get_inputs(
        J=args.J,
        model=args.model,
    )

    # Apply the selected time horizon.
    parameters["T"] = args.T

    # Select the two-class initial traffic configuration.
    if args.configuration is not None:

        configuration = get_initial_configuration(
            configuration=args.configuration,
            sigma=args.sigma,
        )

        parameters["L"] = configuration["L"]

        parameters["rho_int_list"] = (
            configuration["rho_int_list"]
        )

    # Select the output file.
    if args.output is None:

        filename = f"{args.model.lower()}_J{args.J}"

        if args.configuration is not None:
            filename += f"_{args.configuration.lower()}"

        output = DEMO_DIR / f"{filename}.npz"

    else:

        output = args.output.resolve()

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Construct the numerical solver options.
    solver_args = Namespace(
        J=args.J,
        model=args.model,
        nx=args.nx,
        nt=args.nt,
        max_grids=args.max_grids,
        no_precond=args.no_precond,
        no_multigrid=args.no_multigrid,
        newton_tol=args.newton_tol,
        gmres_rtol=args.gmres_rtol,
        max_newton_iter=args.max_newton_iter,
        output=output,
    )

    return parameters, solver_args


# ============================================================
# 6. Execute the demonstration
# ============================================================

def main():

    args = parse_arguments()

    validate_arguments(args)

    parameters, solver_args = prepare_experiment(args)

    print("\n" + "=" * 65)
    print("MULTI-CLASS TRAFFIC MFG — NUMERICAL DEMONSTRATION")
    print("=" * 65)

    print(f"Model:             {args.model}")
    print(f"Vehicle classes:   {args.J}")
    print(f"Time horizon:      {args.T}")
    print(f"Spatial cells:     {args.nx}")
    print(f"Minimum time steps:{args.nt:>8}")
    print(f"Grid levels:       {args.max_grids}")

    print("=" * 65)

    # Execute the original Newton–GMRES implementation.
    results = run_solver(
        solver_args,
        parameters=parameters,
    )

    print("\n" + "=" * 65)
    print("NUMERICAL DEMONSTRATION COMPLETED")
    print("=" * 65)

    print(
        f"Density shape:     {results['rho'].shape}"
    )

    print(
        f"Velocity shape:    {results['u'].shape}"
    )

    print(
        f"Value shape:       {results['V'].shape}"
    )

    print(
        f"Final residual:    {results['residual_l2']:.6e}"
    )

    print(
        f"Results saved to:  {solver_args.output}"
    )

    print("=" * 65)


# ============================================================
# 7. Entry point
# ============================================================

if __name__ == "__main__":
    main()
