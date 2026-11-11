#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Single-Class LWR Mean-Field Game — Numerical Demonstration

Reuses the numerical implementation from:
    src/newton_krylov/one_class/

The demonstration uses:
    - Original simulation parameters
    - Original initial density and terminal cost
    - Original finite-difference residual
    - Original exact Jacobian
    - Original Newton–Krylov/LGMRES solver
    - Original preconditioner
    - Original multigrid interpolation

The LWR model functions are activated in memory.
The original inputs.py file is not modified.

By default, only the first grid level is solved.
Use --max-grids 5 to attempt all five configured grid levels.

Scientific references:
    Machtalay et al., Transportation Research Part B (2025)
    PhD thesis, Chapter II (2026)
"""

from pathlib import Path
import argparse
import sys
import time

import numpy as np
from scipy.optimize import newton_krylov


# ============================================================
# 1. Locate original numerical implementation
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

SOURCE = ROOT / "src" / "newton_krylov" / "one_class"

sys.path.insert(0, str(SOURCE))

import inputs as original_inputs


# ============================================================
# 2. Activate original LWR functions in memory
# ============================================================

# These expressions reproduce the LWR definitions
# commented out in the original inputs.py.

def U(rho):
    return original_inputs.u_max * (
        1.0 - rho / original_inputs.rho_jam
    )


def f_mfg(u, rho):
    return 0.5 * (U(rho) - u) ** 2


def f_starp(p, rho):
    return U(rho) - p


def f_star(p, rho, u):
    return -0.5 * p**2 + U(rho) * p


# Derivatives used by the analytical Jacobian.

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


# Update the imported module in memory.
# This does not change inputs.py on disk.

original_inputs.f_mfg = f_mfg
original_inputs.f_starp = f_starp
original_inputs.f_star = f_star

original_inputs.f_starp_p = f_starp_p
original_inputs.f_starp_r = f_starp_r
original_inputs.f_star_p = f_star_p
original_inputs.f_star_r = f_star_r
original_inputs.f_star_u = f_star_u


# Import numerical modules AFTER selecting LWR.
# This allows their imports from inputs.py to obtain
# the LWR functions and derivatives.

from indx_funcs import solutions
from newton_func import newton_func
from jacobian_exact import jacobian
from multi_grid import multigrid
from precond import get_preconditioner


# ============================================================
# 3. Simulation
# ============================================================

def run_demo(max_grids=1):

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

    if not 1 <= max_grids <= nb_grid:
        raise ValueError(
            f"max_grids must be between 1 and {nb_grid}"
        )

    if max_grids > 1 and not use_multigrid:
        raise ValueError(
            "Grid refinement requires an initial guess "
            "from the original multigrid routine."
        )

    output_dir = Path(__file__).resolve().parent

    print("=" * 65)
    print("Single-Class LWR Mean-Field Game")
    print("Original Newton–Krylov Implementation")
    print("=" * 65)

    print("\nOriginal model parameters:")
    print(f"T                  = {T}")
    print(f"L                  = {L}")
    print(f"u_max              = {u_max}")
    print(f"rho_jam            = {rho_jam}")
    print(f"rho_a              = {rho_a}")
    print(f"rho_b              = {rho_b}")
    print(f"gama               = {gama}")
    print(f"CFL                = {CFL}")
    print(f"EPS                = {EPS}")

    print("\nSolver configuration:")
    print(f"Initial Nx         = {Nx0}")
    print(f"Initial Nt         = {Nt0}")
    print(f"Available grids    = {nb_grid}")
    print(f"Selected grids     = {max_grids}")
    print(f"Refinement factor  = {multip}")
    print(f"Preconditioning    = {use_precond}")
    print(f"Multigrid          = {use_multigrid}")

    Nx = Nx0
    Nt = Nt0

    previous_solution = None
    previous_Nx = None
    previous_Nt = None

    for i in range(max_grids):

        print("\n" + "=" * 65)
        print(f"GRID LEVEL {i}")
        print("=" * 65)

        # ----------------------------------------------------
        # Grid construction: same formulas as original solver
        # ----------------------------------------------------

        if i > 0:
            Nx = previous_Nx * multip
            Nt = previous_Nt * multip

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

        x = np.linspace(0, L, Nx + 1)
        t = np.arange(0, T + dt, dt)

        Nt = multip * int((len(t) - 1) / multip)

        n_unknowns = 3 * Nt * Nx + 2 * Nx

        print(f"Nx          = {Nx}")
        print(f"Nt          = {Nt}")
        print(f"dx          = {dx:.8f}")
        print(f"dt          = {dt:.8f}")
        print(f"eps         = {eps:.8f}")
        print(f"Unknowns    = {n_unknowns}")

        # ----------------------------------------------------
        # Initial guess: original workflow
        # ----------------------------------------------------

        if i == 0:

            guess = np.zeros(n_unknowns)

        else:

            print("\nInterpolating previous solution...")

            guess = multigrid(
                int(Nt / multip),
                previous_Nt,
                previous_Nx,
                previous_solution,
                multip,
            )

        # ----------------------------------------------------
        # Original analytical preconditioner
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

            precond_time = time.perf_counter() - start

            print(
                f"Preconditioner time: {precond_time:.3f} s"
            )

        # ----------------------------------------------------
        # Original nonlinear residual
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
        # Newton–Krylov with LGMRES
        # ----------------------------------------------------

        print("\nStarting Newton–Krylov solver...\n")

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
        # Extract results
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

        print(f"Solver time   = {solver_time:.3f} s")
        print(f"Residual norm = {residual_norm:.6e}")

        print("\nDensity:")
        print(f"  min = {np.min(density):.6f}")
        print(f"  max = {np.max(density):.6f}")

        print("\nVelocity:")
        print(f"  min = {np.min(velocity):.6f}")
        print(f"  max = {np.max(velocity):.6f}")

        # ----------------------------------------------------
        # Save numerical results
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
            dx=dx,
            dt=dt,
            eps=eps,
            x=x,
            t=t,
            solution=solution,
            density=density,
            velocity=velocity,
            value=value,
            flux=flux,
            residual_norm=residual_norm,
        )

        print(f"\nSaved: {output_file}")

        previous_solution = solution
        previous_Nx = Nx
        previous_Nt = Nt

    print("\n" + "=" * 65)
    print("LWR demonstration finished.")
    print("=" * 65)


# ============================================================
# 4. Command-line interface
# ============================================================

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Single-class LWR MFG demonstration"
    )

    parser.add_argument(
        "--max-grids",
        type=int,
        default=1,
        help="Number of grid levels to solve (default: 1)",
    )

    args = parser.parse_args()

    run_demo(max_grids=args.max_grids)
