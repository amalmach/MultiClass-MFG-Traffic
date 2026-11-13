#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
General J-Class Traffic Mean-Field Game
=======================================

Parallel PETSc/MPI nonlinear solver.

Based on:
    PhD thesis, Appendix D.2
    Listings D.15, D.16, and D.17.

Models:
    GLWR - Generalized LWR
    GS   - Generalized Separable
    GNS  - Generalized Non-Separable

Numerical methods:
    - PETSc SNES nonlinear solver
    - PETSc KSP Krylov solver
    - MPI distributed vectors
    - PETSc distributed sparse Jacobian
    - Optional output in NumPy format

This first implementation solves a single space-time grid.

The mathematical equations are imported from:
    src/newton_krylov/multi_class/

The parallel residual and Jacobian callbacks currently
reconstruct the global state on every process.
"""

import argparse
import sys
import time
from pathlib import Path

import numpy as np


# ============================================================
# 1. Command-line arguments
# ============================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Parallel PETSc/MPI solver for general "
            "J-class traffic Mean-Field Games."
        )
    )

    parser.add_argument(
        "--J",
        type=int,
        default=2,
        help="Number of vehicle classes.",
    )

    parser.add_argument(
        "--model",
        type=str.upper,
        choices=("GLWR", "GS", "GNS"),
        default="GLWR",
        help="Traffic cost model.",
    )

    parser.add_argument(
        "--nx",
        type=int,
        default=5,
        help="Number of spatial cells.",
    )

    parser.add_argument(
        "--nt",
        type=int,
        default=8,
        help="Minimum number of temporal steps.",
    )

    parser.add_argument(
        "--tol",
        type=float,
        default=1e-8,
        help="Nonlinear solver tolerance.",
    )

    parser.add_argument(
        "--max-it",
        type=int,
        default=50,
        help="Maximum SNES iterations.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output .npz file.",
    )

    # Unknown arguments are passed to PETSc.
    args, petsc_options = parser.parse_known_args()

    return args, petsc_options


# ============================================================
# 2. Initialize PETSc and MPI
# ============================================================

args, petsc_options = parse_arguments()

import petsc4py

petsc4py.init(
    [sys.argv[0]] + petsc_options
)

from petsc4py import PETSc
from mpi4py import MPI


COMM = MPI.COMM_WORLD

RANK = COMM.Get_rank()
SIZE = COMM.Get_size()


# ============================================================
# 3. Import shared numerical modules
# ============================================================

THIS_DIR = Path(__file__).resolve().parent

SRC_DIR = THIS_DIR.parents[1]

SHARED_DIR = SRC_DIR / "newton_krylov" / "multi_class"

if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))

from inputs import get_inputs
from cost_functions import get_model
from indx_funcs import solutions

from parallel_functions import (
    compute_FF,
    compute_jacobian,
    system_size,
)


# ============================================================
# 4. Construct the space-time grid
# ============================================================

def compute_grid(parameters, Nx, Nt_requested):

    T = parameters["T"]
    L = parameters["L"]

    CFL = parameters["CFL"]
    EPS = parameters["EPS"]

    u_max_vec = parameters["u_max_vec"]

    # Initial single-grid experiment.
    mu = parameters["mu"][0]

    if Nx < 3:
        raise ValueError("Require Nx >= 3.")

    if Nt_requested < 4:
        raise ValueError("Require Nt >= 4.")

    if T <= 0 or L <= 0:
        raise ValueError("T and L must be positive.")

    dx = L / Nx

    u_max_global = np.max(u_max_vec)

    dt_limit = CFL * dx / u_max_global

    if mu > 0:

        dt_limit = min(
            dt_limit,
            EPS * dx**2 / mu,
        )

    Nt = max(
        Nt_requested,
        int(np.ceil(T / dt_limit)),
    )

    # Make the temporal grid compatible with
    # the sequential solver's refinement factor.

    multip = parameters["multip"]

    Nt = multip * int(
        np.ceil(Nt / multip)
    )

    dt = T / Nt

    eps = mu * dt / dx**2

    x = np.linspace(
        0.0,
        L,
        Nx + 1,
    )

    t = np.linspace(
        0.0,
        T,
        Nt + 1,
    )

    return Nt, dt, dx, eps, x, t


# ============================================================
# 5. Gather a distributed PETSc vector
# ============================================================

def gather_global_vector(vec):
    """
    Replicate the complete PETSc vector on every MPI rank.

    This provides a simple correctness-oriented interface
    to the existing sequential mathematical functions.

    It requires O(N) memory per MPI process.
    """

    start, end = vec.getOwnershipRange()

    local_values = np.asarray(
        vec.getArray(readonly=True),
        dtype=np.float64,
    ).copy()

    pieces = COMM.allgather(
        (start, end, local_values)
    )

    N = vec.getSize()

    global_values = np.empty(
        N,
        dtype=np.float64,
    )

    for piece_start, piece_end, values in pieces:

        if len(values) != piece_end - piece_start:
            raise RuntimeError(
                "Inconsistent MPI vector ownership."
            )

        global_values[
            piece_start:piece_end
        ] = values

    return global_values


# ============================================================
# 6. Main PETSc/MPI solver
# ============================================================

def run_solver():

    # --------------------------------------------------------
    # Validate inputs
    # --------------------------------------------------------

    if args.tol <= 0:
        raise ValueError(
            "Solver tolerance must be positive."
        )

    if args.max_it < 1:
        raise ValueError(
            "Maximum iterations must be positive."
        )

    # --------------------------------------------------------
    # Load physical parameters
    # --------------------------------------------------------

    parameters = get_inputs(
        J=args.J,
        model=args.model,
    )

    model = get_model(args.model)

    J = parameters["J"]
    Nx = args.nx

    u_max_vec = parameters["u_max_vec"]
    rho_jam_vec = parameters["rho_jam_vec"]

    rho_int_list = parameters["rho_int_list"]
    VT = parameters["VT"]

    Nt, dt, dx, eps, x, t = compute_grid(
        parameters,
        Nx,
        args.nt,
    )

    N = system_size(Nt, Nx, J)

    # --------------------------------------------------------
    # Print configuration
    # --------------------------------------------------------

    if RANK == 0:

        print("=" * 65)
        print("Parallel J-Class Traffic Mean-Field Game")
        print("=" * 65)

        print(f"Model:            {args.model}")
        print(f"Vehicle classes:  {J}")
        print(f"MPI processes:    {SIZE}")
        print(f"Spatial cells:    {Nx}")
        print(f"Temporal steps:   {Nt}")
        print(f"Global unknowns:  {N}")
        print(f"dx:               {dx:.8e}")
        print(f"dt:               {dt:.8e}")
        print(f"eps:              {eps:.8e}")

    # --------------------------------------------------------
    # Construct distributed PETSc Jacobian
    # --------------------------------------------------------

    # This preliminary preallocation is deliberately
    # generous for the small validation problems.

    estimated_nnz = 20 + 2 * J

    A = PETSc.Mat().createAIJ(
        size=(N, N),
        nnz=estimated_nnz,
        comm=PETSc.COMM_WORLD,
    )

    A.setOption(
        PETSc.Mat.Option.NEW_NONZERO_ALLOCATION_ERR,
        False,
    )

    A.setUp()

    # --------------------------------------------------------
    # Construct distributed vectors
    # --------------------------------------------------------

    w = A.createVecRight()
    F = A.createVecLeft()

    w.set(0.0)

    # --------------------------------------------------------
    # Create PETSc SNES nonlinear solver
    # --------------------------------------------------------

    snes = PETSc.SNES().create(
        comm=PETSc.COMM_WORLD,
    )

    snes.setType("newtonls")

    # ========================================================
    # Nonlinear residual callback
    # ========================================================

    def form_function(snes, X, Fvec):

        global_w = gather_global_vector(X)

        start, end = Fvec.getOwnershipRange()

        local_residual = compute_FF(
            w=global_w,
            row_start=start,
            row_end=end,
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

        local_F = Fvec.getArray()

        local_F[:] = local_residual

    # ========================================================
    # Analytical Jacobian callback
    # ========================================================

    def form_jacobian(snes, X, Jac, Prec):

        global_w = gather_global_vector(X)

        start, end = Jac.getOwnershipRange()

        A_local = compute_jacobian(
            w=global_w,
            row_start=start,
            row_end=end,
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

        Jac.zeroEntries()

        # Insert each locally owned sparse matrix row.

        for local_row in range(end - start):

            row_start = A_local.indptr[local_row]
            row_end = A_local.indptr[local_row + 1]

            columns = A_local.indices[
                row_start:row_end
            ]

            values = A_local.data[
                row_start:row_end
            ]

            if len(columns) == 0:
                continue

            global_row = start + local_row

            Jac.setValues(
                [global_row],
                columns,
                values,
            )

        Jac.assemble()

    # --------------------------------------------------------
    # Register nonlinear callbacks
    # --------------------------------------------------------

    snes.setFunction(
        form_function,
        F,
    )

    snes.setJacobian(
        form_jacobian,
        A,
        A,
    )

    # --------------------------------------------------------
    # Configure the PETSc linear solver
    # --------------------------------------------------------

    ksp = snes.getKSP()

    # Direct solution of the Newton linear systems.
    ksp.setType("preonly")

    pc = ksp.getPC()

    # LU factorization using MUMPS.
    pc.setType("lu")
    pc.setFactorSolverType("mumps")

    # --------------------------------------------------------
    # Configure nonlinear convergence
    # --------------------------------------------------------

    snes.setTolerances(
        atol=args.tol,
        rtol=1e-12,
        max_it=args.max_it,
    )

    # PETSc command-line options can override settings.

    snes.setFromOptions()

    # --------------------------------------------------------
    # Monitor nonlinear iterations
    # --------------------------------------------------------

    def monitor(snes, iteration, residual_norm):

        if RANK == 0:

            print(
                f"SNES iteration {iteration:3d} | "
                f"Residual = {residual_norm:.8e}",
                flush=True,
            )

    snes.setMonitor(monitor)

    # --------------------------------------------------------
    # Solve
    # --------------------------------------------------------

    COMM.Barrier()

    start_time = time.perf_counter()

    snes.solve(None, w)

    COMM.Barrier()

    elapsed = time.perf_counter() - start_time

    # --------------------------------------------------------
    # Check convergence
    # --------------------------------------------------------

    reason = snes.getConvergedReason()

    # Evaluate the residual at the final PETSc solution.
    form_function(snes, w, F)

    residual_l2 = F.norm(
        norm_type=PETSc.NormType.NORM_2
    )

    residual_inf = F.norm(
        norm_type=PETSc.NormType.NORM_INFINITY
    )

    if RANK == 0:

        print("\nFinal nonlinear residual:")
        print(f"L2 norm:       {residual_l2:.8e}")
        print(f"Infinity norm: {residual_inf:.8e}")

        print(f"SNES reason:   {reason}")
        print(f"Execution time: {elapsed:.3f} s")

    if reason <= 0:

        raise RuntimeError(
            f"PETSc SNES failed to converge: "
            f"reason={reason}"
        )

    # --------------------------------------------------------
    # Gather final solution
    # --------------------------------------------------------

    solution = gather_global_vector(w)

    # --------------------------------------------------------
    # Reconstruct numerical variables
    # --------------------------------------------------------

    if RANK == 0:

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
                "  Density: "
                f"[{rho[j].min():.6e}, "
                f"{rho[j].max():.6e}]"
            )

            print(
                "  Velocity: "
                f"[{u[j].min():.6e}, "
                f"{u[j].max():.6e}]"
            )

            print(
                "  Value function: "
                f"[{V[j].min():.6e}, "
                f"{V[j].max():.6e}]"
            )

        # ----------------------------------------------------
        # Optional output
        # ----------------------------------------------------

        if args.output is not None:

            args.output.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            np.savez_compressed(
                args.output,
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
                dt=dt,
                dx=dx,
                eps=eps,
                model=args.model,
                u_max_vec=u_max_vec,
                rho_jam_vec=rho_jam_vec,
                residual_l2=residual_l2,
                residual_inf=residual_inf,
            )

            print(
                "\nSaved numerical results to:",
                args.output,
            )

        print("\n" + "=" * 65)
        print("PARALLEL PETSc/MPI SOLVER COMPLETED")
        print("=" * 65)

    # --------------------------------------------------------
    # Release PETSc objects
    # --------------------------------------------------------

    snes.destroy()
    A.destroy()
    F.destroy()
    w.destroy()


# ============================================================
# 7. Main execution
# ============================================================

if __name__ == "__main__":
    run_solver()
