#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Exact/Approximate Jacobian for the J-class traffic MFG model.

Based on:
    PhD thesis, Appendix D.1, Listing D.7.

Supported models:
    GLWR, GS, GNS

The Jacobian corresponds to the nonlinear residual defined in:
    newton_func.py

Options
-------
exact=1:
    Assemble the complete analytical Jacobian.

exact=0:
    Assemble an approximate Jacobian by omitting
    derivatives of the cost/optimal-control functions.

Returns
-------
scipy.sparse.csc_matrix
    Sparse Jacobian of shape (N, N), where

    N = (3*Nt + 2)*J*Nx.
"""

import numpy as np
from scipy.sparse import coo_matrix

from indx_funcs import (
    r_idx,
    u_idx,
    V_idx,
    Fr_idx,
    Fu_idx,
    FV_idx,
    Frint_idx,
    FVter_idx,
)


# ============================================================
# 1. Assemble the analytical Jacobian
# ============================================================

def jacobian(
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
    exact=1,
):
    """
    Assemble the Jacobian matrix of the J-class MFG system.

    Parameters
    ----------
    w : ndarray
        Global solution vector.

    Nt, Nx, J : int
        Temporal steps, spatial cells, and vehicle classes.

    dt, dx : float
        Temporal and spatial step sizes.

    eps : float
        Dimensionless artificial viscosity.

    u_max_vec : array_like
        Maximum velocities for each class.

    rho_jam_vec : array_like
        Jam densities for each class.

    model : dict
        Cost functions and their derivatives,
        returned by cost_functions.get_model().

    exact : int
        1 for the exact Jacobian.
        0 for the approximate Jacobian.

    Returns
    -------
    scipy.sparse.csc_matrix
        Sparse Jacobian matrix.
    """

    # --------------------------------------------------------
    # Validate inputs
    # --------------------------------------------------------

    w = np.asarray(w, dtype=float)

    u_max_vec = np.asarray(
        u_max_vec,
        dtype=float,
    )

    rho_jam_vec = np.asarray(
        rho_jam_vec,
        dtype=float,
    )

    if J < 1 or Nx < 3 or Nt < 1:
        raise ValueError(
            "Require J >= 1, Nx >= 3, Nt >= 1."
        )

    if dt <= 0 or dx <= 0:
        raise ValueError(
            "dt and dx must be positive."
        )

    if exact not in (0, 1):
        raise ValueError(
            "exact must be 0 or 1."
        )

    if len(u_max_vec) != J:
        raise ValueError(
            "u_max_vec must have length J."
        )

    if len(rho_jam_vec) != J:
        raise ValueError(
            "rho_jam_vec must have length J."
        )

    if np.any(u_max_vec <= 0):
        raise ValueError(
            "Maximum velocities must be positive."
        )

    if np.any(rho_jam_vec <= 0):
        raise ValueError(
            "Jam densities must be positive."
        )

    Nspace = J * Nx
    N = (3 * Nt + 2) * Nspace

    if w.shape != (N,):
        raise ValueError(
            f"Expected w.shape == ({N},), "
            f"received {w.shape}."
        )

    required_functions = (
        "f_starp_p",
        "f_starp_r",
        "f_star_p",
        "f_star_r",
        "f_star_u",
    )

    for name in required_functions:
        if name not in model:
            raise KeyError(
                f"Missing model derivative: {name}"
            )

    # --------------------------------------------------------
    # Sparse matrix storage
    # --------------------------------------------------------

    rows = []
    cols = []
    values = []

    def add(row, col, value):
        """Append a nonzero Jacobian entry."""

        if value != 0.0:
            rows.append(row)
            cols.append(col)
            values.append(value)

    # ========================================================
    # Loop over all classes and spatial cells
    # ========================================================

    for j in range(J):

        for k in range(1, Nx + 1):

            # Combined one-based spatial index.
            kj = j * Nx + k

            # -----------------------------------------------
            # Periodic neighbors within the same class
            # -----------------------------------------------

            if k > 1:
                left = kj - 1
            else:
                left = j * Nx + Nx

            if k < Nx:
                right = kj + 1
            else:
                right = j * Nx + 1

            # ===============================================
            # Initial-density equation
            # ===============================================

            add(
                Frint_idx(kj, Nt, Nx, J),
                r_idx(kj, 0, Nt),
                1.0,
            )

            # ===============================================
            # Terminal value-function equation
            # ===============================================

            add(
                FVter_idx(kj, Nt, Nx, J),
                V_idx(kj, Nt, Nt, Nx, J),
                1.0,
            )

            # ===============================================
            # Time loop
            # ===============================================

            for n in range(Nt):

                # -------------------------------------------
                # Equation indices
                # -------------------------------------------

                row_rho = Fr_idx(kj, n, Nt)

                row_u = Fu_idx(
                    kj, n, Nt, Nx, J
                )

                row_V = FV_idx(
                    kj, n, Nt, Nx, J
                )

                # ===========================================
                # 1. CONTINUITY EQUATION
                # ===========================================

                rho_left = w[
                    r_idx(left, n, Nt)
                ]

                rho_right = w[
                    r_idx(right, n, Nt)
                ]

                u_left = w[
                    u_idx(left, n, Nt, Nx, J)
                ]

                u_right = w[
                    u_idx(right, n, Nt, Nx, J)
                ]

                # -------------------------------------------
                # F_rho / rho
                # -------------------------------------------

                add(
                    row_rho,
                    r_idx(kj, n + 1, Nt),
                    1.0,
                )

                add(
                    row_rho,
                    r_idx(left, n, Nt),
                    -0.5
                    - 0.5 * dt / dx * u_left,
                )

                add(
                    row_rho,
                    r_idx(right, n, Nt),
                    -0.5
                    + 0.5 * dt / dx * u_right,
                )

                # -------------------------------------------
                # F_rho / u
                # -------------------------------------------

                add(
                    row_rho,
                    u_idx(left, n, Nt, Nx, J),
                    -0.5 * dt / dx * rho_left,
                )

                add(
                    row_rho,
                    u_idx(right, n, Nt, Nx, J),
                    0.5 * dt / dx * rho_right,
                )

                # ===========================================
                # 2. VALUE-FUNCTION GRADIENT
                # ===========================================

                V_right_next = w[
                    V_idx(
                        right, n + 1, Nt, Nx, J
                    )
                ]

                V_current_next = w[
                    V_idx(
                        kj, n + 1, Nt, Nx, J
                    )
                ]

                p = (
                    V_right_next - V_current_next
                ) / dx

                # -------------------------------------------
                # Density vector for all classes
                # -------------------------------------------

                rho_vec = np.zeros(
                    J,
                    dtype=float,
                )

                for m in range(J):

                    km = m * Nx + k

                    rho_vec[m] = w[
                        r_idx(km, n, Nt)
                    ]

                u_current = w[
                    u_idx(kj, n, Nt, Nx, J)
                ]

                # ===========================================
                # 3. OPTIMAL-CONTROL EQUATION
                # ===========================================

                # -------------------------------------------
                # F_u / rho^m
                # -------------------------------------------

                for m in range(J):

                    km = m * Nx + k

                    derivative = model[
                        "f_starp_r"
                    ](
                        j,
                        m,
                        p,
                        rho_vec,
                        u_max_vec,
                        rho_jam_vec,
                    )

                    add(
                        row_u,
                        r_idx(km, n, Nt),
                        -exact * derivative,
                    )

                # -------------------------------------------
                # F_u / u
                # -------------------------------------------

                add(
                    row_u,
                    u_idx(kj, n, Nt, Nx, J),
                    1.0,
                )

                # -------------------------------------------
                # F_u / V
                # -------------------------------------------

                derivative_p = model[
                    "f_starp_p"
                ](
                    j,
                    p,
                    rho_vec,
                    u_max_vec,
                    rho_jam_vec,
                )

                dHp = exact * derivative_p / dx

                add(
                    row_u,
                    V_idx(
                        right, n + 1, Nt, Nx, J
                    ),
                    -dHp,
                )

                add(
                    row_u,
                    V_idx(
                        kj, n + 1, Nt, Nx, J
                    ),
                    dHp,
                )

                # ===========================================
                # 4. HAMILTON-JACOBI EQUATION
                # ===========================================

                # -------------------------------------------
                # F_V / rho^m
                # -------------------------------------------

                for m in range(J):

                    km = m * Nx + k

                    derivative = model[
                        "f_star_r"
                    ](
                        j,
                        m,
                        p,
                        rho_vec,
                        u_max_vec,
                        rho_jam_vec,
                        u_current,
                    )

                    add(
                        row_V,
                        r_idx(km, n, Nt),
                        exact * dt * derivative,
                    )

                # -------------------------------------------
                # F_V / u
                # -------------------------------------------

                derivative_u = model[
                    "f_star_u"
                ](
                    j,
                    p,
                    rho_vec,
                    u_max_vec,
                    rho_jam_vec,
                    u_current,
                )

                add(
                    row_V,
                    u_idx(kj, n, Nt, Nx, J),
                    exact * dt * derivative_u,
                )

                # -------------------------------------------
                # F_V / V
                # -------------------------------------------

                derivative_p = model[
                    "f_star_p"
                ](
                    j,
                    p,
                    rho_vec,
                    u_max_vec,
                    rho_jam_vec,
                    u_current,
                )

                dHp = exact * derivative_p / dx

                # Current time
                add(
                    row_V,
                    V_idx(kj, n, Nt, Nx, J),
                    -1.0,
                )

                # Next time: left neighbor
                add(
                    row_V,
                    V_idx(
                        left, n + 1, Nt, Nx, J
                    ),
                    eps,
                )

                # Next time: current cell
                add(
                    row_V,
                    V_idx(
                        kj, n + 1, Nt, Nx, J
                    ),
                    1.0 - dt * dHp - 2.0 * eps,
                )

                # Next time: right neighbor
                add(
                    row_V,
                    V_idx(
                        right, n + 1, Nt, Nx, J
                    ),
                    dt * dHp + eps,
                )

    # ========================================================
    # Construct the sparse matrix
    # ========================================================

    matrix = coo_matrix(
        (values, (rows, cols)),
        shape=(N, N),
        dtype=float,
    )

    # CSC format is efficient for sparse factorization.
    # Duplicate entries are summed automatically.
    matrix = matrix.tocsc()

    return matrix
