#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sparse Preconditioner for the General J-Class Traffic MFG
==========================================================

Based on:
    PhD thesis, Appendix D.1, Listing D.8

The preconditioner is constructed from the analytical
or approximate Jacobian matrix.

Supported factorization methods:
    - splu: sparse LU factorization (thesis default)
    - spilu: incomplete sparse LU factorization

The resulting preconditioner is represented as a
scipy.sparse.linalg.LinearOperator and can be passed
directly to scipy.sparse.linalg.gmres().
"""

import numpy as np

from scipy.sparse import csc_matrix
from scipy.sparse.linalg import (
    LinearOperator,
    splu,
    spilu,
)


# ============================================================
# 1. Construct the sparse preconditioner
# ============================================================

def get_preconditioner(
    w,
    Nt,
    Nx,
    J,
    dt,
    dx,
    eps,
    jacobian,
    u_max_vec,
    rho_jam_vec,
    model,
    exact=0,
    method="splu",
    drop_tol=1e-4,
    fill_factor=10.0,
):
    """
    Construct a sparse LU/ILU preconditioner.

    Parameters
    ----------
    w : ndarray
        Current global solution vector.

    Nt, Nx, J : int
        Temporal steps, spatial cells, vehicle classes.

    dt, dx : float
        Temporal and spatial step sizes.

    eps : float
        Dimensionless artificial viscosity.

    jacobian : callable
        Jacobian assembly function from jacobian_exact.py.

    u_max_vec : array_like
        Class-dependent maximum velocities.

    rho_jam_vec : array_like
        Class-dependent jam densities.

    model : dict
        Selected GLWR, GS, or GNS cost model.

    exact : int, optional
        0: approximate Jacobian (default).
        1: exact Jacobian.

    method : str, optional
        "splu": sparse LU (default).
        "spilu": incomplete sparse LU.

    drop_tol : float, optional
        Drop tolerance for spilu.

    fill_factor : float, optional
        Fill factor for spilu.

    Returns
    -------
    scipy.sparse.linalg.LinearOperator
        Preconditioner representing the action of
        the inverse factorization.
    """

    # --------------------------------------------------------
    # Validate inputs
    # --------------------------------------------------------

    if method not in ("splu", "spilu"):
        raise ValueError(
            "method must be 'splu' or 'spilu'."
        )

    if exact not in (0, 1):
        raise ValueError(
            "exact must be 0 or 1."
        )

    if drop_tol < 0:
        raise ValueError(
            "drop_tol must be nonnegative."
        )

    if fill_factor < 1:
        raise ValueError(
            "fill_factor must be at least 1."
        )

    w = np.asarray(w, dtype=float)

    N = (3 * Nt + 2) * J * Nx

    if w.shape != (N,):
        raise ValueError(
            f"Expected solution shape ({N},), "
            f"received {w.shape}."
        )

    # --------------------------------------------------------
    # Assemble the Jacobian
    # --------------------------------------------------------

    A = jacobian(
        w,
        Nt,
        Nx,
        J,
        dt,
        dx,
        eps,
        u_max_vec,
        rho_jam_vec,
        model,
        exact=exact,
    )

    A = csc_matrix(A)

    if A.shape != (N, N):
        raise ValueError(
            f"Unexpected Jacobian shape: {A.shape}. "
            f"Expected ({N}, {N})."
        )

    # --------------------------------------------------------
    # Sparse factorization
    # --------------------------------------------------------

    if method == "splu":

        # Sparse LU: active method in thesis Listing D.8.
        factorization = splu(A)

    else:

        # Optional incomplete LU factorization.
        factorization = spilu(
            A,
            drop_tol=drop_tol,
            fill_factor=fill_factor,
        )

    # --------------------------------------------------------
    # Preconditioning operator
    # --------------------------------------------------------

    def apply_preconditioner(r):
        """
        Apply the inverse factorization to a vector.
        """
        return factorization.solve(r)

    M = LinearOperator(
        shape=(N, N),
        matvec=apply_preconditioner,
        dtype=np.float64,
    )

    return M
