#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
General J-Class Traffic Mean-Field Game
=======================================

Sequential Newton-GMRES solver.

Based on:
    PhD thesis, Appendix D.1, Listings D.13-D.14.

Supported models:
    GLWR - Generalized LWR
    GS   - Generalized Separable
    GNS  - Generalized Non-Separable

Numerical components:
    - Nonlinear residual
    - Exact analytical Jacobian
    - Sparse LU preconditioner
    - GMRES linear solver
    - Newton nonlinear solver
    - Multigrid interpolation

Run from the repository root:

    python3 src/newton_krylov/multi_class/main.py

Example:

    python3 src/newton_krylov/multi_class/main.py \
        --J 3 --model GLWR --nx 5 --nt 8 --max-grids 1
"""

import argparse
import time
from pathlib import Path

import numpy as np

from inputs import get_inputs, print_inputs
from cost_functions import get_model
from newton_func import newton_func
from jacobian_exact import jacobian
from precond import get_preconditioner
from multi_grid import multigrid
from gmres_solver import newton_gmres
from indx_funcs import solutions


# ============================================================
# 1. Command-line arguments
# ============================================================

def parse_arguments():
    """Read numerical parameters from the command line."""

    parser = argparse.ArgumentParser(
        description=(
            "Sequential Newton-GMRES solver for "
            "general J-class traffic Mean-Field Games."
        )
    )

    parser.add_argument(
        "--J",
        "--classes",
        dest="J",
        type=int,
        default=2,
        help="Number of vehicle classes (default: 2).",
    )

    parser.add_argument(
        "--model",
        type=str.upper,
        choices=("GLWR", "GS", "GNS"),
        default="GLWR",
        help="Traffic model (default: GLWR).",
    )

    parser.add_argument(
        "--nx",
        type=int,
        default=None,
        help="Initial spatial cells (default: thesis Nx0).",
    )

    parser.add_argument(
        "--nt",
        type=int,
        default=None,
        help="Minimum initial time steps (default: thesis Nt0).",
    )

    parser.add_argument(
        "--max-grids",
        type=int,
        default=1,
        help=(
            "Number of grid levels to solve. "
            "Default: 1 for initial testing."
        ),
    )

    parser.add_argument(
        "--no-precond",
        action="store_true",
        help="Disable sparse LU preconditioning.",
    )

    parser.add_argument(
        "--no-multigrid",
        action="store_true",
        help="Use a zero initial guess on refined grids.",
    )

    parser.add_argument(
        "--newton-tol",
        type=float,
        default=1e-8,
        help="Newton residual tolerance.",
    )

    parser.add_argument(
        "--gmres-rtol",
        type=float,
        default=1e-8,
        help="Relative tolerance for GMRES.",
    )

    parser.add_argument(
        "--max-newton-iter",
        type=int,
        default=50,
        help="Maximum Newton iterations.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional .npz output file.",
    )

    return parser.parse_args()


# ============================================================
# 2. Compute stable space-time grid
# ============================================================

def compute_grid(T, L, Nx, Nt_requested, u_max, mu, CFL, EPS,
                 multip):
    """
    Construct a uniform grid satisfying the CFL condition.

    For positive viscosity, also impose the diffusion bound.

    Nt is rounded up to a multiple of the refinement factor.
    The final time step is dt = T/Nt.
    """

    if T <= 0 or L <= 0:
        raise ValueError("T and L must be positive.")

    if Nx < 3 or Nt_requested < 4:
        raise ValueError(
            "Require Nx >= 3 and Nt_requested >= 4."
        )

    if multip < 2:
        raise ValueError(
            "Refinement factor must be at least 2."
        )

    if not 0 < CFL < 1:
        raise ValueError("Require 0 < CFL < 1.")

    if not 0 < EPS < 0.5:
        raise ValueError("Require 0 < EPS < 0.5.")

    if mu < 0:
        raise ValueError("Viscosity must be nonnegative.")

    dx = L / Nx

    dt_limit = CFL * dx / np.max(u_max)

    if mu > 0:
        dt_limit = min(
            dt_limit,
            EPS * dx**2 / mu,
        )

    # At least the requested number of steps and enough
    # additional steps to satisfy the stability restriction.
    Nt_min = max(
        Nt_requested,
        int(np.ceil(T / dt_limit)),
    )

    # Keep the time-step count compatible with multigrid.
    Nt = multip * int(
        np.ceil(Nt_min / multip)
    )

    dt = T / Nt

    eps = mu * dt / dx**2

    x = np.linspace(0.0, L, Nx + 1)
    t = np.linspace(0.0, T, Nt + 1)

    return Nt, dt, dx, eps, x, t


# ============================================================
# 3. Solve the J-class traffic MFG system
# ============================================================

def run_solver(args):
    """Execute the sequential Newton-GMRES grid loop."""

    # --------------------------------------------------------
    # Load physical and numerical inputs
    # --------------------------------------------------------

    parameters = get_inputs(
        J=args.J,
        model=args.model,
    )

    print_inputs(parameters)

    model = get_model(args.model)

    J = parameters["J"]
    T = parameters["T"]
    L = parameters["L"]

    u_max_vec = parameters["u_max_vec"]
    rho_jam_vec = parameters["rho_jam_vec"]

    rho_int_list = parameters["rho_int_list"]
    VT = parameters["VT"]

    CFL = parameters["CFL"]
    EPS = parameters["EPS"]

    mu_list = parameters["mu"]

    multip = parameters["multip"]

    Nx0 = (
        parameters["Nx0"]
        if args.nx is None
        else args.nx
    )

    Nt0 = (
        parameters["Nt0"]
        if args.nt is None
        else args.nt
    )

    if args.max_grids < 1:
        raise ValueError(
            "--max-grids must be at least 1."
        )

    if args.max_grids > parameters["nb_grid"]:
        raise ValueError(
            "--max-grids exceeds the number of "
            "configured viscosity/grid levels."
        )

    if args.newton_tol <= 0 or args.gmres_rtol <= 0:
        raise ValueError(
            "Solver tolerances must be positive."
        )

    use_precond = (
        parameters["use_precond"]
        and not args.no_precond
    )

    use_multigrid = (
        parameters["use_multigrid"]
        and not args.no_multigrid
    )

    print("\nSelected solver options:")
    print(f"Preconditioning: {use_precond}")
    print(f"Multigrid:       {use_multigrid}")
    print(f"Grid levels:     {args.max_grids}")

    # --------------------------------------------------------
    # Initial grid sizes
    # --------------------------------------------------------

    Nx = Nx0
    Nt_requested = Nt0

    previous_solution = None
    previous_Nx = None
    previous_Nt = None

    start_total = time.perf_counter()

    # ========================================================
    # Grid refinement loop
    # ========================================================

    for grid_level in range(args.max_grids):

        print("\n" + "=" * 70)
        print(
            f"GRID LEVEL {grid_level + 1} "
            f"OF {args.max_grids}"
        )
        print("=" * 70)

        # ----------------------------------------------------
        # Refine spatial and requested temporal resolution
        # ----------------------------------------------------

        if grid_level > 0:
            Nx = previous_Nx * multip
            Nt_requested = previous_Nt * multip

        # ----------------------------------------------------
        # Viscosity parameter for this level
        # ----------------------------------------------------

        mu = mu_list[grid_level]

        # ----------------------------------------------------
        # Calculate stable grid
        # ----------------------------------------------------

        Nt, dt, dx, eps, x, t = compute_grid(
            T=T,
            L=L,
            Nx=Nx,
            Nt_requested=Nt_requested,
            u_max=u_max_vec,
            mu=mu,
            CFL=CFL,
            EPS=EPS,
            multip=multip,
        )

        Nspace = J * Nx
        N = (3 * Nt + 2) * Nspace

        print(f"Classes:           {J}")
        print(f"Spatial cells:     {Nx}")
        print(f"Temporal steps:    {Nt}")
        print(f"Unknowns:          {N}")
        print(f"dx:                {dx:.8e}")
        print(f"dt:                {dt:.8e}")
        print(f"Viscosity mu:      {mu:.8e}")
        print(f"Numerical eps:     {eps:.8e}")
        print(f"Final time:        {t[-1]:.8f}")

        # ----------------------------------------------------
        # Construct initial guess
        # ----------------------------------------------------

        if (
            grid_level > 0
            and use_multigrid
        ):

            print("\nInterpolating previous solution...")

            guess = multigrid(
                new_Nt=Nt // multip,
                old_Nt=previous_Nt,
                Nx=previous_Nx,
                J=J,
                w=previous_solution,
                multip=multip,
            )

        else:

            print("\nUsing zero initial guess.")

            guess = np.zeros(
                N,
                dtype=float,
            )

        if guess.shape != (N,):
            raise RuntimeError(
                "Incorrect multigrid initial-guess size."
            )

        # ----------------------------------------------------
        # Define the nonlinear residual
        # ----------------------------------------------------

        def F(w):
            return newton_func(
                w=w,
                f_starp=model["f_starp"],
                f_star=model["f_star"],
                rho_int_list=rho_int_list,
                Nt=Nt,
                Nx=Nx,
                J=J,
                dt=dt,
                dx=dx,
                eps=eps,
                x=x,
                VT=VT,
                u_max_vec=u_max_vec,
                rho_jam_vec=rho_jam_vec,
            )

        # ----------------------------------------------------
        # Define the exact Newton Jacobian
        # ----------------------------------------------------

        def Jmat(w):
            return jacobian(
                w=w,
                Nt=Nt,
                Nx=Nx,
                J=J,
                dt=dt,
                dx=dx,
                eps=eps,
                u_max_vec=u_max_vec,
                rho_jam_vec=rho_jam_vec,
                model=model,
                exact=1,
            )

        # ----------------------------------------------------
        # Construct the approximate-Jacobian preconditioner
        # ----------------------------------------------------

        M = None

        if use_precond:

            print("\nBuilding sparse LU preconditioner...")

            start_precond = time.perf_counter()

            M = get_preconditioner(
                w=guess,
                Nt=Nt,
                Nx=Nx,
                J=J,
                dt=dt,
                dx=dx,
                eps=eps,
                jacobian=jacobian,
                u_max_vec=u_max_vec,
                rho_jam_vec=rho_jam_vec,
                model=model,
                exact=0,
                method="splu",
            )

            elapsed_precond = (
                time.perf_counter() - start_precond
            )

            print(
                "Preconditioner time: "
                f"{elapsed_precond:.3f} s"
            )

        # ----------------------------------------------------
        # Sequential Newton-GMRES
        # ----------------------------------------------------

        print("\nStarting Newton-GMRES...\n")

        start_solve = time.perf_counter()

        solution = newton_gmres(
            F=F,
            w0=guess,
            Jmat=Jmat,
            Nt=Nt,
            Nx=Nx,
            J=J,
            dt=dt,
            dx=dx,
            eps=eps,
            u_max_vec=u_max_vec,
            rho_jam_vec=rho_jam_vec,
            M=M,
            rtol=args.gmres_rtol,
            atol=args.newton_tol,
            max_iter=args.max_newton_iter,
        )

        elapsed_solve = (
            time.perf_counter() - start_solve
        )

        # ----------------------------------------------------
        # Verify nonlinear residual
        # ----------------------------------------------------

        residual = F(solution)

        residual_l2 = np.linalg.norm(residual)
        residual_inf = np.linalg.norm(
            residual,
            ord=np.inf,
        )

        print("\nFinal nonlinear residual:")
        print(f"L2 norm:       {residual_l2:.8e}")
        print(f"Infinity norm: {residual_inf:.8e}")

        if not np.all(np.isfinite(solution)):
            raise RuntimeError(
                "Solution contains NaN or infinity."
            )

        if residual_l2 >= args.newton_tol:
            raise RuntimeError(
                "The final nonlinear residual "
                "exceeds the requested tolerance."
            )

        print(f"\nSolver time: {elapsed_solve:.3f} s")

        # ----------------------------------------------------
        # Reconstruct physical variables
        # ----------------------------------------------------

        rho, u, V, Q = solutions(
            solution,
            Nt,
            Nx,
            J,
        )

        print("\nSolution statistics:")

        for j in range(J):

            print(f"\nClass {j + 1}:")
            print(
                "  Density range: "
                f"[{rho[j].min():.6e}, "
                f"{rho[j].max():.6e}]"
            )
            print(
                "  Velocity range: "
                f"[{u[j].min():.6e}, "
                f"{u[j].max():.6e}]"
            )
            print(
                "  Value range: "
                f"[{V[j].min():.6e}, "
                f"{V[j].max():.6e}]"
            )

        # ----------------------------------------------------
        # Optional output: final grid only
        # ----------------------------------------------------

        if (
            args.output is not None
            and grid_level == args.max_grids - 1
        ):

            output_path = args.output

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            np.savez_compressed(
                output_path,
                solution=solution,
                rho=rho,
                u=u,
                V=V,
                Q=Q,
                x=x,
                t=t,
                J=J,
                Nx=Nx,
                Nt=Nt,
                T=T,
                L=L,
                dt=dt,
                dx=dx,
                eps=eps,
                mu=mu,
                model=args.model,
                u_max_vec=u_max_vec,
                rho_jam_vec=rho_jam_vec,
                residual_l2=residual_l2,
                residual_inf=residual_inf,
            )

            print(
                "\nSaved numerical results to:"
            )
            print(output_path)

        # ----------------------------------------------------
        # Store solution for the next refinement level
        # ----------------------------------------------------

        previous_solution = solution.copy()
        previous_Nx = Nx
        previous_Nt = Nt

    # ========================================================
    # Final summary
    # ========================================================

    elapsed_total = (
        time.perf_counter() - start_total
    )

    print("\n" + "=" * 70)
    print("SEQUENTIAL NEWTON-GMRES COMPLETED")
    print("=" * 70)

    print(f"Model:           {args.model}")
    print(f"Classes:         {J}")
    print(f"Final grid:      Nx={Nx}, Nt={Nt}")
    print(f"Unknowns:        {N}")
    print(f"Residual L2:     {residual_l2:.8e}")
    print(f"Total time:      {elapsed_total:.3f} s")

    return {
        "solution": solution,
        "rho": rho,
        "u": u,
        "V": V,
        "Q": Q,
        "x": x,
        "t": t,
        "residual_l2": residual_l2,
        "residual_inf": residual_inf,
    }


# ============================================================
# 4. Main execution
# ============================================================

if __name__ == "__main__":

    arguments = parse_arguments()

    run_solver(arguments)
