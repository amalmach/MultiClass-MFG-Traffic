#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nonlinear residual for the general J-class traffic MFG model.

Based on:
    PhD thesis, Appendix D.1, Listing D.6

The global unknown vector contains:
    rho : (J, Nx, Nt+1)
    u   : (J, Nx, Nt)
    V   : (J, Nx, Nt+1)

The nonlinear residual contains:
    F_rho  : continuity equations
    F_u    : optimal-control equations
    F_V    : Hamilton-Jacobi equations
    F_rint : initial-density conditions
    F_Vter : terminal value-function conditions

Spatial boundary conditions are periodic within each class.

The cost functions use zero-based class indices.
The index-mapping functions use one-based combined spatial indices.
"""

import numpy as np
from scipy.integrate import quad

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
# 1. Initial density integration
# ============================================================

def integral(a, b, rho_int):
    """
    Integrate an initial-density function over a spatial cell.

    Parameters
    ----------
    a, b : float
        Cell boundaries.

    rho_int : callable
        Initial-density function rho_int(x).

    Returns
    -------
    float
        Integral of the initial density over [a, b].
    """

    result, _ = quad(
        rho_int,
        a,
        b,
    )

    return result


# ============================================================
# 2. General J-class nonlinear residual
# ============================================================

def newton_func(
    w,
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
    Assemble the discretized J-class traffic MFG system.

    Parameters
    ----------
    w : ndarray
        Global solution vector.

    f_starp : callable
        Optimal-control function from cost_functions.py.

    f_star : callable
        Hamiltonian from cost_functions.py.

    rho_int_list : sequence of callables
        Initial-density functions, one for each class.

    Nt : int
        Number of temporal steps.

    Nx : int
        Number of spatial cells.

    J : int
        Number of vehicle classes.

    dt : float
        Temporal step size.

    dx : float
        Spatial step size.

    eps : float
        Dimensionless artificial viscosity coefficient.

    x : ndarray
        Spatial cell boundaries, length Nx+1.

    VT : callable
        Terminal value-function condition VT(x).
        The same terminal condition is used for all classes.

    u_max_vec : ndarray
        Maximum velocities for all classes.

    rho_jam_vec : ndarray
        Jam densities for all classes.

    Returns
    -------
    FF : ndarray
        Nonlinear residual with the same length as w.
    """

    # --------------------------------------------------------
    # Validate input dimensions
    # --------------------------------------------------------

    w = np.asarray(w, dtype=float)

    x = np.asarray(x, dtype=float)

    u_max_vec = np.asarray(
        u_max_vec,
        dtype=float,
    )

    rho_jam_vec = np.asarray(
        rho_jam_vec,
        dtype=float,
    )

    if J < 1 or Nx < 2 or Nt < 1:
        raise ValueError(
            "Require J >= 1, Nx >= 2, and Nt >= 1."
        )

    if dt <= 0 or dx <= 0:
        raise ValueError(
            "dt and dx must be positive."
        )

    if len(rho_int_list) != J:
        raise ValueError(
            "rho_int_list must contain one function "
            "for each vehicle class."
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

    if len(x) != Nx + 1:
        raise ValueError(
            "The spatial grid must contain Nx+1 points."
        )

    if not np.allclose(np.diff(x), dx):
        raise ValueError(
            "The spatial grid spacing must equal dx."
        )

    Nspace = J * Nx

    N = 3 * Nt * Nspace + 2 * Nspace

    if w.ndim != 1 or len(w) != N:
        raise ValueError(
            f"Invalid solution vector shape {w.shape}. "
            f"Expected ({N},)."
        )

    # --------------------------------------------------------
    # Allocate nonlinear residual
    # --------------------------------------------------------

    FF = np.zeros(N, dtype=float)

    # ========================================================
    # Loop over global class-spatial indices
    # ========================================================

    for kj in range(1, Nspace + 1):

        # ----------------------------------------------------
        # Identify vehicle class and spatial cell
        # ----------------------------------------------------

        # Zero-based class index for the cost functions.
        j = (kj - 1) // Nx

        # One-based local spatial index.
        k = kj - j * Nx

        # ----------------------------------------------------
        # Periodic spatial neighbors within the same class
        # ----------------------------------------------------

        if k > 1:
            left = kj - 1
        else:
            left = j * Nx + Nx

        if k < Nx:
            right = kj + 1
        else:
            right = j * Nx + 1

        # ----------------------------------------------------
        # Initial-density condition
        # ----------------------------------------------------

        rho_int = rho_int_list[j]

        initial_density = (
            integral(
                x[k - 1],
                x[k],
                rho_int,
            )
            / dx
        )

        FF[
            Frint_idx(kj, Nt, Nx, J)
        ] = (
            w[r_idx(kj, 0, Nt)]
            - initial_density
        )

        # ----------------------------------------------------
        # Terminal value-function condition
        # ----------------------------------------------------

        FF[
            FVter_idx(kj, Nt, Nx, J)
        ] = (
            w[V_idx(kj, Nt, Nt, Nx, J)]
            - VT(x[k])
        )

        # ====================================================
        # Time loop
        # ====================================================

        for n in range(Nt):

            # ------------------------------------------------
            # 1. Continuity equation F_rho
            # ------------------------------------------------

            rho_next = w[
                r_idx(kj, n + 1, Nt)
            ]

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

            FF[
                Fr_idx(kj, n, Nt)
            ] = (
                rho_next
                - 0.5 * (rho_left + rho_right)
                + 0.5 * dt / dx
                * (
                    rho_right * u_right
                    - rho_left * u_left
                )
            )

            # ------------------------------------------------
            # 2. Spatial gradient of the value function
            # ------------------------------------------------

            V_right_next = w[
                V_idx(right, n + 1, Nt, Nx, J)
            ]

            V_current_next = w[
                V_idx(kj, n + 1, Nt, Nx, J)
            ]

            p = (
                V_right_next - V_current_next
            ) / dx

            # ------------------------------------------------
            # 3. Build the density vector of all classes
            # ------------------------------------------------

            rho_vec = np.zeros(J, dtype=float)

            for m in range(J):

                # Same spatial cell k, class m.
                km = m * Nx + k

                rho_vec[m] = w[
                    r_idx(km, n, Nt)
                ]

            # ------------------------------------------------
            # 4. Optimal-control equation F_u
            # ------------------------------------------------

            u_current = w[
                u_idx(kj, n, Nt, Nx, J)
            ]

            optimal_u = f_starp(
                j,
                p,
                rho_vec,
                u_max_vec,
                rho_jam_vec,
            )

            FF[
                Fu_idx(kj, n, Nt, Nx, J)
            ] = (
                u_current - optimal_u
            )

            # ------------------------------------------------
            # 5. Hamilton-Jacobi equation F_V
            # ------------------------------------------------

            V_current = w[
                V_idx(kj, n, Nt, Nx, J)
            ]

            V_left_next = w[
                V_idx(left, n + 1, Nt, Nx, J)
            ]

            # All models use a common Hamiltonian interface:
            # f_star(j, p, rho_vec, u_max_vec, rho_jam_vec, u)
            #
            # GLWR does not depend explicitly on u.
            # GS and GNS evaluate the Hamiltonian using u.

            H = f_star(
                j,
                p,
                rho_vec,
                u_max_vec,
                rho_jam_vec,
                u_current,
            )

            diffusion = eps * (
                V_right_next
                - 2.0 * V_current_next
                + V_left_next
            )

            FF[
                FV_idx(kj, n, Nt, Nx, J)
            ] = (
                V_current_next
                - V_current
                + dt * H
                + diffusion
            )

    return FF
