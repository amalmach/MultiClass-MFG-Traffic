#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Parallel numerical helpers for the general J-class traffic MFG.

Reference:
    PhD thesis, Appendix D.2, Listing D.15.

This module provides:
    initialguess      - Coarse-to-fine initialization.
    compute_FF        - Locally owned nonlinear residual rows.
    compute_jacobian  - Locally owned sparse Jacobian rows.

The mathematical model is reused from:
    src/newton_krylov/multi_class/

Important:
    This is a reference MPI assembly strategy.

    The full solution vector is assumed to be available
    on each process. The sequential residual/Jacobian
    routines assemble the complete system, after which
    locally owned rows are selected.

    The next development stage will connect these helpers
    to PETSc SNES and distributed MPI vectors.

    Fully distributed, scalable row assembly is a
    separate optimization step.

No direct PETSc or mpi4py imports are required here.
"""

from pathlib import Path
import sys

import numpy as np


# ============================================================
# 1. Import shared mathematical functions
# ============================================================

THIS_DIR = Path(__file__).resolve().parent

SRC_DIR = THIS_DIR.parents[1]

SHARED_DIR = SRC_DIR / "newton_krylov" / "multi_class"

if not SHARED_DIR.is_dir():
    raise FileNotFoundError(
        "Shared Newton-Krylov multi_class directory not found: "
        f"{SHARED_DIR}"
    )

if str(SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_DIR))


from multi_grid import multigrid
from newton_func import newton_func
from jacobian_exact import jacobian


# ============================================================
# 2. Vector and row-ownership validation
# ============================================================

def system_size(Nt, Nx, J):
    """
    Number of unknowns in the discretized J-class MFG system.

    N = (3*Nt + 2)*J*Nx
    """

    if Nt < 1 or Nx < 3 or J < 1:
        raise ValueError(
            "Require Nt >= 1, Nx >= 3, J >= 1."
        )

    return (3 * Nt + 2) * J * Nx


def check_ownership(start, end, N):
    """
    Validate the range of globally indexed rows
    owned by an MPI process.

    PETSc ownership intervals use:
        [start, end)
    """

    if not (
        0 <= start <= end <= N
    ):
        raise ValueError(
            f"Invalid ownership range [{start}, {end}) "
            f"for system size {N}."
        )


def check_global_vector(w, N):
    """
    Validate a replicated global solution vector.
    """

    w = np.asarray(w, dtype=np.float64)

    if w.shape != (N,):
        raise ValueError(
            f"Expected global vector shape ({N},), "
            f"received {w.shape}."
        )

    return w


# ============================================================
# 3. Coarse-to-fine initial guess
# ============================================================

def initialguess(Nt, Nx, J, multip, filename):
    """
    Load a previously saved coarse-grid solution and
    interpolate it onto a refined grid.

    Parameters
    ----------
    Nt : int
        Target number of temporal steps.

    Nx : int
        Target number of spatial cells.

    J : int
        Number of vehicle classes.

    multip : int
        Spatial refinement factor.

    filename : str or Path
        NumPy archive containing:
            solution
            Nt
            Nx

    Returns
    -------
    ndarray
        Refined global initial-guess vector.

    Notes
    -----
    The spatial grid is refined by ``multip``.

    The temporal interpolation uses the target Nt.
    """

    if multip < 2:
        raise ValueError(
            "multip must be at least 2."
        )

    if Nt % multip != 0:
        raise ValueError(
            "Target Nt must be divisible by multip."
        )

    filename = Path(filename)

    if not filename.is_file():
        raise FileNotFoundError(
            f"Coarse-grid solution not found: {filename}"
        )

    with np.load(
        filename,
        allow_pickle=False,
    ) as data:

        required = {"solution", "Nt", "Nx"}

        missing = required.difference(data.files)

        if missing:
            raise ValueError(
                "Missing required archive fields: "
                f"{sorted(missing)}"
            )

        old_solution = np.asarray(
            data["solution"],
            dtype=np.float64,
        ).copy()

        old_Nt = int(data["Nt"])
        old_Nx = int(data["Nx"])

        if "J" in data.files:
            old_J = int(data["J"])

            if old_J != J:
                raise ValueError(
                    "The saved number of classes "
                    "does not match J."
                )

    if Nx != multip * old_Nx:
        raise ValueError(
            f"Expected target Nx={multip * old_Nx}, "
            f"received Nx={Nx}."
        )

    expected_old_size = system_size(
        old_Nt,
        old_Nx,
        J,
    )

    if old_solution.shape != (expected_old_size,):
        raise ValueError(
            "Saved coarse-grid solution has "
            "an inconsistent length."
        )

    new_solution = multigrid(
        new_Nt=Nt // multip,
        old_Nt=old_Nt,
        Nx=old_Nx,
        J=J,
        w=old_solution,
        multip=multip,
    )

    expected_new_size = system_size(
        Nt,
        Nx,
        J,
    )

    if new_solution.shape != (expected_new_size,):
        raise RuntimeError(
            "Multigrid returned an incorrect "
            "solution dimension."
        )

    return new_solution


# ============================================================
# 4. Locally owned nonlinear residual
# ============================================================

def compute_FF(
    w,
    row_start,
    row_end,
    f_starp,
    f_star,
    rho_int_list,
    Nt,
    Nx,
    J,
    dt,
    dx,
    eps,
    x,
    VT,
    u_max_vec,
    rho_jam_vec,
):
    """
    Compute locally owned rows of the nonlinear residual.

    Parameters
    ----------
    w : ndarray
        Complete global solution vector.

    row_start, row_end : int
        PETSc global ownership interval [start, end).

    Other parameters
    ----------------
    Correspond to newton_func.py.

    Returns
    -------
    ndarray
        Residual entries owned by this process,
        with shape (row_end - row_start,).

    Note
    ----
    The complete residual is currently evaluated
    before selecting local rows.
    """

    N = system_size(Nt, Nx, J)

    check_ownership(
        row_start,
        row_end,
        N,
    )

    w = check_global_vector(w, N)

    FF_global = newton_func(
        w=w,
        f_starp=f_starp,
        f_star=f_star,
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

    return np.asarray(
        FF_global[row_start:row_end],
        dtype=np.float64,
    ).copy()


# ============================================================
# 5. Locally owned sparse Jacobian rows
# ============================================================

def compute_jacobian(
    w,
    row_start,
    row_end,
    Nt,
    Nx,
    J,
    dt,
    dx,
    eps,
    u_max_vec,
    rho_jam_vec,
    model,
    exact=1,
):
    """
    Assemble locally owned Jacobian rows.

    Parameters
    ----------
    w : ndarray
        Complete global solution vector.

    row_start, row_end : int
        PETSc global ownership interval [start, end).

    model : dict
        Model returned by cost_functions.get_model().

    exact : int
        1: exact Jacobian.
        0: approximate Jacobian.

    Returns
    -------
    scipy.sparse.csr_matrix
        Sparse matrix of shape:

            (row_end - row_start, N)

    Note
    ----
    The complete Jacobian is currently assembled
    before extracting locally owned rows.
    """

    N = system_size(Nt, Nx, J)

    check_ownership(
        row_start,
        row_end,
        N,
    )

    w = check_global_vector(w, N)

    A_global = jacobian(
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
        exact=exact,
    )

    A_local = A_global.tocsr()[
        row_start:row_end,
        :
    ]

    return A_local.copy()
