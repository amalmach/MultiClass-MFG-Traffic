#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Single-Class LWR Mean-Field Game
================================

Configurable demonstration based on the original
Newton–Krylov research implementation.

Source:
    src/newton_krylov/one_class/

Supports:
    - Physical parameters
    - Initial-density parameters
    - Spatial and temporal discretization
    - Artificial viscosity
    - Preconditioning
    - Multigrid refinement
"""

from pathlib import Path
import argparse
import sys
import time

import numpy as np
from scipy.optimize import newton_krylov


# ============================================================
# 1. Locate the original implementation
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

SOURCE = ROOT / "src" / "newton_krylov" / "one_class"

sys.path.insert(0, str(SOURCE))

import inputs as original_inputs


# ============================================================
# 2. LWR mathematical functions
# ============================================================

def U(rho):
    """Greenshields desired velocity."""

    return original_inputs.u_max * (
        1.0 - rho / original_inputs.rho_jam
    )


def f_mfg(u, rho):
    """LWR running cost."""

    return 0.5 * (U(rho) - u)**2


def f_starp(p, rho):
    """Optimal velocity feedback."""

    return U(rho) - p


def f_star(p, rho, u):
    """LWR Hamiltonian."""

    return -0.5 * p**2 + U(rho) * p


# ============================================================
# 3. Analytical derivatives
# ============================================================

def f_starp_p(p, rho):
    return -1.0


def f_starp_r(p, rho):
    return (
        -original_inputs.u_max
        / original_inputs.rho_jam
    )


def f_star_p(p, rho, u):
    return -p + U(rho)


def f_star_r(p, rho, u):
    return (
        -original_inputs.u_max
        / original_inputs.rho_jam
    ) * p


def f_star_u(p, rho, u):
    return 0.0


# ============================================================
# 4. Select the LWR model
# ============================================================

original_inputs.f_mfg = f_mfg
original_inputs.f_starp = f_starp
original_inputs.f_star = f_star

original_inputs.f_starp_p = f_starp_p
original_inputs.f_starp_r = f_starp_r

original_inputs.f_star_p = f_star_p
original_inputs.f_star_r = f_star_r
original_inputs.f_star_u = f_star_u


# Import original solver modules after selecting LWR.

from indx_funcs import solutions
from newton_func import newton_func
from jacobian_exact import jacobian
from multi_grid import multigrid
from precond import get_preconditioner


# ============================================================
# 5. Parameter configuration
# ============================================================

def configure_parameters(args):

    (
        T,
        L,
        u_max,
        rho_jam,
        rho_a,
        rho_b,
        gama,
        CFL,
        EPS,
        nb_grid,
        mu,
        Nx0,
        Nt0,
        multip,
        use_precond,
        use_multigrid,
    ) = original_inputs.inputs()

    # ----------------------------------------------
    # Physical parameters
    # ----------------------------------------------

    T = args.T if args.T is not None else T
    L = args.L if args.L is not None else L

    u_max = (
        args.u_max
        if args.u_max is not None
        else u_max
    )

    rho_jam = (
        args.rho_jam
        if args.rho_jam is not None
        else rho_jam
    )

    # ----------------------------------------------
    # Initial-density parameters
    # ----------------------------------------------

    rho_a = (
        args.rho_a
        if args.rho_a is not None
        else rho_a
    )

    rho_b = (
        args.rho_b
        if args.rho_b is not None
        else rho_b
    )

    gama = (
        args.gama
        if args.gama is not None
        else gama
    )

    # ----------------------------------------------
    # Numerical parameters
    # ----------------------------------------------

    CFL = (
        args.CFL
        if args.CFL is not None
        else CFL
    )

    EPS = (
        args.EPS
        if args.EPS is not None
        else EPS
    )

    Nx0 = (
        args.nx
        if args.nx is not None
        else Nx0
    )

    Nt0 = (
        args.nt
        if args.nt is not None
        else Nt0
    )

    # ----------------------------------------------
    # Solver configuration
    # ----------------------------------------------

    if args.preconditioner == "on":
        use_precond = True

    elif args.preconditioner == "off":
        use_precond = False

    # ----------------------------------------------
    # Artificial viscosity
    # ----------------------------------------------

    mu = list(mu)

    if args.mu is not None:

        mu = [args.mu] * nb_grid

    # ----------------------------------------------
    # Validate parameters
    # ----------------------------------------------

    if T <= 0 or L <= 0:
        raise ValueError("T and L must be positive.")

    if u_max <= 0 or rho_jam <= 0:
        raise ValueError(
            "u_max and rho_jam must be positive."
        )

    if not (0 <= rho_a <= rho_jam):
        raise ValueError(
            "rho_a must lie between 0 and rho_jam."
        )

    if not (0 <= rho_b <= rho_jam):
        raise ValueError(
            "rho_b must lie between 0 and rho_jam."
        )

    if gama <= 0:
        raise ValueError("gama must be positive.")

    if CFL <= 0 or EPS <= 0:
        raise ValueError(
            "CFL and EPS must be positive."
        )

    if Nx0 < 4 or Nt0 < 4:
        raise ValueError(
            "Nx and Nt must be at least 4."
        )

    if Nt0 % multip != 0:
        raise ValueError(
            f"Nt must be divisible by {multip}."
        )

    if any(value < 0 for value in mu):
        raise ValueError(
            "Artificial viscosity must be nonnegative."
        )

    if not 1 <= args.max_grids <= nb_grid:
        raise ValueError(
            f"max_grids must be between 1 and {nb_grid}."
        )

    # ----------------------------------------------
    # Update the original input module in memory
    # ----------------------------------------------

    # Functions from inputs.py that read these global
    # values at runtime will now see the new settings.
    # This does not change the source file on disk.

    original_inputs.T = T
    original_inputs.L = L
    original_inputs.u_max = u_max
    original_inputs.rho_jam = rho_jam

    original_inputs.rho_a = rho_a
    original_inputs.rho_b = rho_b
    original_inputs.gama = gama

    original_inputs.CFL = CFL
    original_inputs.EPS = EPS

    original_inputs.Nx0 = Nx0
    original_inputs.Nt0 = Nt0

    original_inputs.mu = mu

    # Return the configured values.

    return {
        "T": T,
        "L": L,
        "u_max": u_max,
        "rho_jam": rho_jam,
        "rho_a": rho_a,
        "rho_b": rho_b,
        "gama": gama,
        "CFL": CFL,
        "EPS": EPS,
        "Nx0": Nx0,
        "Nt0": Nt0,
        "mu": mu,
        "nb_grid": nb_grid,
        "multip": multip,
        "use_precond": use_precond,
        "use_multigrid": use_multigrid,
    }


# ============================================================
# 6. Numerical simulation
# ============================================================

def run_demo(args):

    parameters = configure_parameters(args)

    T = parameters["T"]
    L = parameters["L"]
    u_max = parameters["u_max"]
    rho_jam = parameters["rho_jam"]

    CFL = parameters["CFL"]
    EPS = parameters["EPS"]

    Nx = parameters["Nx0"]
    Nt = parameters["Nt0"]

    mu = parameters["mu"]
    multip = parameters["multip"]

    use_precond = parameters["use_precond"]
    use_multigrid = parameters["use_multigrid"]

    max_grids = args.max_grids

    if max_grids > 1 and not use_multigrid:
        raise ValueError(
            "Multiple grids require multigrid interpolation."
        )

    output_dir = Path(__file__).resolve().parent

    print("=" * 65)
    print("Single-Class LWR Mean-Field Game")
    print("Configurable Newton–Krylov Demonstration")
    print("=" * 65)

    print("\nPhysical parameters:")

    for key in [
        "T",
        "L",
        "u_max",
        "rho_jam",
        "rho_a",
        "rho_b",
        "gama",
    ]:
        print(f"{key:20s} = {parameters[key]}")

    print("\nNumerical parameters:")

    print(f"Nx                  = {Nx}")
    print(f"Nt                  = {Nt}")
    print(f"CFL                 = {CFL}")
    print(f"EPS                 = {EPS}")
    print(f"mu                  = {mu}")
    print(f"Preconditioning     = {use_precond}")
    print(f"Number of grids     = {max_grids}")

    previous_solution = None
    previous_Nx = None
    previous_Nt = None

    # ========================================================
    # Grid refinement loop
    # ========================================================

    for i in range(max_grids):

        print("\n" + "=" * 65)
        print(f"GRID LEVEL {i}")
        print("=" * 65)

        if i > 0:

            Nx = previous_Nx * multip
            Nt = previous_Nt * multip

        # ----------------------------------------------------
        # Discretization
        # ----------------------------------------------------

        dx = L / Nx

        if mu[i] == 0.0:

            dt = min(
                T / Nt,
                CFL * dx / u_max,
            )

            eps = 0.0

        else:

            dt = min(
                T / Nt,
                CFL * dx / abs(u_max),
                EPS * dx**2 / mu[i],
            )

            eps = mu[i] * dt / dx**2

        x = np.linspace(
            0.0,
            L,
            Nx + 1,
        )

        t = np.arange(
            0.0,
            T + dt,
            dt,
        )

        Nt = multip * int(
            (len(t) - 1) / multip
        )

        if Nt < 2:
            raise ValueError(
                "The effective temporal grid is too small."
            )

        n_unknowns = 3 * Nt * Nx + 2 * Nx

        print(f"Nx          = {Nx}")
        print(f"Nt          = {Nt}")
        print(f"dx          = {dx:.8f}")
        print(f"dt          = {dt:.8f}")
        print(f"eps         = {eps:.8f}")
        print(f"Unknowns    = {n_unknowns}")

        # ----------------------------------------------------
        # Initial guess
        # ----------------------------------------------------

        if i == 0:

            guess = np.zeros(n_unknowns)

        else:

            guess = multigrid(
                int(Nt / multip),
                previous_Nt,
                previous_Nx,
                previous_solution,
                multip,
            )

        # ----------------------------------------------------
        # Preconditioner
        # ----------------------------------------------------

        prec = None

        if use_precond:

            print("\nConstructing preconditioner...")

            start = time.perf_counter()

            prec = get_preconditioner(
                guess,
                Nt,
                Nx,
                dt,
                dx,
                eps,
                jacobian,
            )

            elapsed = time.perf_counter() - start

            print(
                f"Preconditioner time: {elapsed:.3f} s"
            )

        # ----------------------------------------------------
        # Nonlinear residual
        # ----------------------------------------------------

        def residual(w):

            return newton_func(
                w,
                original_inputs.f_starp,
                original_inputs.f_star,
                original_inputs.rho_int,
                Nt,
                Nx,
                dt,
                dx,
                eps,
                x,
                original_inputs.VT,
            )

        # ----------------------------------------------------
        # Newton–Krylov solver
        # ----------------------------------------------------

        print("\nStarting Newton–Krylov iterations...\n")

        start = time.perf_counter()

        solution = newton_krylov(
            residual,
            guess,
            method="lgmres",
            verbose=1,
            inner_M=prec,
        )

        solver_time = time.perf_counter() - start

        # ----------------------------------------------------
        # Extract solution
        # ----------------------------------------------------

        density, velocity, value, flux = solutions(
            solution,
            Nt,
            Nx,
        )

        residual_norm = np.linalg.norm(
            residual(solution),
            ord=np.inf,
        )

        print("\nSolver completed.")
        print(f"Solver time: {solver_time:.3f} s")
        print(f"Residual:    {residual_norm:.6e}")

        print("\nDensity:")
        print(f"  Min = {density.min():.6f}")
        print(f"  Max = {density.max():.6f}")

        print("\nVelocity:")
        print(f"  Min = {velocity.min():.6f}")
        print(f"  Max = {velocity.max():.6f}")

        # ----------------------------------------------------
        # Save results
        # ----------------------------------------------------

        output_file = (
            output_dir / f"lwr_solution_grid{i}.npz"
        )

        np.savez(
            output_file,
            model="LWR",
            Nx=Nx,
            Nt=Nt,
            T=T,
            L=L,
            u_max=u_max,
            rho_jam=rho_jam,
            rho_a=parameters["rho_a"],
            rho_b=parameters["rho_b"],
            gama=parameters["gama"],
            CFL=CFL,
            EPS=EPS,
            mu=mu[i],
            dx=dx,
            dt=dt,
            eps=eps,
            x=x,
            t=t,
            density=density,
            velocity=velocity,
            value=value,
            flux=flux,
            solution=solution,
            residual_norm=residual_norm,
        )

        print(f"\nResults saved: {output_file}")

        previous_solution = solution
        previous_Nx = Nx
        previous_Nt = Nt

    print("\n" + "=" * 65)
    print("LWR demonstration completed.")
    print("=" * 65)


# ============================================================
# 7. Command-line interface
# ============================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Configurable single-class LWR "
            "Mean-Field Game demonstration"
        )
    )

    # Physical parameters

    parser.add_argument("--T", type=float)
    parser.add_argument("--L", type=float)
    parser.add_argument("--u-max", type=float)
    parser.add_argument("--rho-jam", type=float)

    # Initial density

    parser.add_argument("--rho-a", type=float)
    parser.add_argument("--rho-b", type=float)
    parser.add_argument("--gama", type=float)

    # Numerical parameters

    parser.add_argument("--nx", type=int)
    parser.add_argument("--nt", type=int)
    parser.add_argument("--CFL", type=float)
    parser.add_argument("--EPS", type=float)
    parser.add_argument("--mu", type=float)

    # Solver configuration

    parser.add_argument(
        "--preconditioner",
        choices=["on", "off"],
        default="on",
    )

    parser.add_argument(
        "--max-grids",
        type=int,
        default=1,
    )

    args = parser.parse_args()

    run_demo(args)


if __name__ == "__main__":
    main()
