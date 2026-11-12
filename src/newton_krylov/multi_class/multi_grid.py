#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Multigrid Interpolation for the General J-Class Traffic MFG
============================================================

Based on:
    PhD thesis, Appendix D.1, Listing D.9

Purpose:
    Transfer a numerical solution from a coarse space-time
    grid to a refined grid.

Numerical method:
    - Cubic interpolation in space
    - Cubic interpolation in time

Solution variables:
    rho : (J, Nx, Nt+1)
    u   : (J, Nx, Nt)
    V   : (J, Nx, Nt+1)

The implementation preserves the original solution-vector
ordering defined in indx_funcs.py.
"""

import numpy as np
from scipy.interpolate import interp1d

from indx_funcs import (
    r_idx,
    u_idx,
    V_idx,
)


# ============================================================
# 1. Convert global vector into 3D arrays
# ============================================================

def from_1d_to_3d(Nt, Nx, J, sol, rho, u, V):
    """
    Convert the global solution vector into 3D arrays.

    Parameters
    ----------
    Nt : int
        Number of temporal steps.

    Nx : int
        Number of spatial cells.

    J : int
        Number of traffic classes.

    sol : ndarray
        Global solution vector.

    rho : ndarray
        Density array with shape (J, Nx, Nt+1).

    u : ndarray
        Velocity array with shape (J, Nx, Nt).

    V : ndarray
        Value-function array with shape (J, Nx, Nt+1).
    """

    expected_size = (3 * Nt + 2) * J * Nx

    if np.asarray(sol).shape != (expected_size,):
        raise ValueError(
            f"Expected solution vector of length "
            f"{expected_size}."
        )

    if rho.shape != (J, Nx, Nt + 1):
        raise ValueError("Invalid density array shape.")

    if u.shape != (J, Nx, Nt):
        raise ValueError("Invalid velocity array shape.")

    if V.shape != (J, Nx, Nt + 1):
        raise ValueError("Invalid value-function array shape.")

    for j in range(1, J + 1):

        for k in range(1, Nx + 1):

            kj = (j - 1) * Nx + k

            for n in range(Nt):

                rho[j - 1, k - 1, n] = sol[
                    r_idx(kj, n, Nt)
                ]

                u[j - 1, k - 1, n] = sol[
                    u_idx(kj, n, Nt, Nx, J)
                ]

                V[j - 1, k - 1, n] = sol[
                    V_idx(kj, n, Nt, Nx, J)
                ]

            # Terminal-time values

            rho[j - 1, k - 1, Nt] = sol[
                r_idx(kj, Nt, Nt)
            ]

            V[j - 1, k - 1, Nt] = sol[
                V_idx(kj, Nt, Nt, Nx, J)
            ]

    return rho, u, V


# ============================================================
# 2. Convert 3D arrays into global vector
# ============================================================

def from_3d_to_1d(Nt, Nx, J, sol, rho, u, V):
    """
    Convert class-dependent 3D arrays into the
    global solution vector.
    """

    expected_size = (3 * Nt + 2) * J * Nx

    if np.asarray(sol).shape != (expected_size,):
        raise ValueError(
            f"Expected output vector of length "
            f"{expected_size}."
        )

    if rho.shape != (J, Nx, Nt + 1):
        raise ValueError("Invalid density array shape.")

    if u.shape != (J, Nx, Nt):
        raise ValueError("Invalid velocity array shape.")

    if V.shape != (J, Nx, Nt + 1):
        raise ValueError("Invalid value-function array shape.")

    for j in range(1, J + 1):

        for k in range(1, Nx + 1):

            kj = (j - 1) * Nx + k

            for n in range(Nt):

                sol[
                    r_idx(kj, n, Nt)
                ] = rho[j - 1, k - 1, n]

                sol[
                    u_idx(kj, n, Nt, Nx, J)
                ] = u[j - 1, k - 1, n]

                sol[
                    V_idx(kj, n, Nt, Nx, J)
                ] = V[j - 1, k - 1, n]

            # Terminal-time values

            sol[
                r_idx(kj, Nt, Nt)
            ] = rho[j - 1, k - 1, Nt]

            sol[
                V_idx(kj, Nt, Nt, Nx, J)
            ] = V[j - 1, k - 1, Nt]

    return sol


# ============================================================
# 3. One-dimensional cubic interpolation
# ============================================================

def interpol(n, new_n, data):
    """
    Interpolate a one-dimensional array using cubic splines.

    This follows the normalized-coordinate interpolation
    approach in Listing D.9.

    Parameters
    ----------
    n : int
        Original number of data points.

    new_n : int
        Number of interpolated data points.

    data : ndarray
        One-dimensional input array.

    Returns
    -------
    ndarray
        Interpolated data with length new_n.
    """

    data = np.asarray(data, dtype=float)

    if data.ndim != 1:
        raise ValueError(
            "Interpolation input must be one-dimensional."
        )

    if len(data) != n:
        raise ValueError(
            f"Expected {n} input values, "
            f"received {len(data)}."
        )

    if n < 4:
        raise ValueError(
            "Cubic interpolation requires at least "
            "four input points."
        )

    if new_n < 4:
        raise ValueError(
            "The refined grid requires at least four points."
        )

    # Normalized original and refined coordinates.

    old_grid = np.linspace(
        0.0,
        1.0,
        n,
    )

    new_grid = np.linspace(
        0.0,
        1.0,
        new_n,
    )

    interpolation_function = interp1d(
        old_grid,
        data,
        kind="cubic",
        assume_sorted=True,
    )

    new_data = interpolation_function(
        new_grid
    )

    return np.asarray(new_data, dtype=float)


# ============================================================
# 4. General J-class multigrid interpolation
# ============================================================

def multigrid(new_Nt, old_Nt, Nx, J, w, multip):
    """
    Interpolate a coarse-grid solution onto a finer grid.

    Parameters
    ----------
    new_Nt : int
        Target temporal steps divided by multip.

        The actual refined number of temporal steps is:
            new_Nt2 = multip * new_Nt

    old_Nt : int
        Number of coarse-grid temporal steps.

    Nx : int
        Number of coarse-grid spatial cells.

    J : int
        Number of traffic classes.

    w : ndarray
        Coarse-grid global solution vector.

    multip : int
        Spatial refinement factor.

    Returns
    -------
    new_w : ndarray
        Interpolated global solution vector.
    """

    # --------------------------------------------------------
    # Validate grid parameters
    # --------------------------------------------------------

    if J < 1:
        raise ValueError(
            "J must be at least 1."
        )

    if Nx < 4:
        raise ValueError(
            "Nx must be at least 4 for cubic interpolation."
        )

    if old_Nt < 4:
        raise ValueError(
            "old_Nt must be at least 4."
        )

    if new_Nt < 1:
        raise ValueError(
            "new_Nt must be positive."
        )

    if multip < 2:
        raise ValueError(
            "multip must be at least 2."
        )

    # --------------------------------------------------------
    # Allocate original class-dependent arrays
    # --------------------------------------------------------

    rho = np.zeros(
        (J, Nx, old_Nt + 1)
    )

    u = np.zeros(
        (J, Nx, old_Nt)
    )

    V = np.zeros(
        (J, Nx, old_Nt + 1)
    )

    # --------------------------------------------------------
    # Convert coarse solution vector into 3D arrays
    # --------------------------------------------------------

    from_1d_to_3d(
        old_Nt,
        Nx,
        J,
        w,
        rho,
        u,
        V,
    )

    # --------------------------------------------------------
    # Refined grid dimensions
    # --------------------------------------------------------

    new_Nx = multip * Nx

    new_Nt2 = multip * new_Nt

    if new_Nt2 < 4:
        raise ValueError(
            "Refined temporal grid is too small."
        )

    # ========================================================
    # 5. Spatial interpolation
    # ========================================================

    rho_space = np.zeros(
        (J, new_Nx, old_Nt + 1)
    )

    u_space = np.zeros(
        (J, new_Nx, old_Nt)
    )

    V_space = np.zeros(
        (J, new_Nx, old_Nt + 1)
    )

    for j in range(J):

        for n in range(old_Nt):

            rho_space[j, :, n] = interpol(
                Nx,
                new_Nx,
                rho[j, :, n],
            )

            u_space[j, :, n] = interpol(
                Nx,
                new_Nx,
                u[j, :, n],
            )

            V_space[j, :, n] = interpol(
                Nx,
                new_Nx,
                V[j, :, n],
            )

        # Final temporal level of density and value function

        rho_space[j, :, old_Nt] = interpol(
            Nx,
            new_Nx,
            rho[j, :, old_Nt],
        )

        V_space[j, :, old_Nt] = interpol(
            Nx,
            new_Nx,
            V[j, :, old_Nt],
        )

    # ========================================================
    # 6. Temporal interpolation
    # ========================================================

    rho_new = np.zeros(
        (J, new_Nx, new_Nt2 + 1)
    )

    u_new = np.zeros(
        (J, new_Nx, new_Nt2)
    )

    V_new = np.zeros(
        (J, new_Nx, new_Nt2 + 1)
    )

    for j in range(J):

        for k in range(new_Nx):

            rho_new[j, k, :] = interpol(
                old_Nt + 1,
                new_Nt2 + 1,
                rho_space[j, k, :],
            )

            u_new[j, k, :] = interpol(
                old_Nt,
                new_Nt2,
                u_space[j, k, :],
            )

            V_new[j, k, :] = interpol(
                old_Nt + 1,
                new_Nt2 + 1,
                V_space[j, k, :],
            )

    # ========================================================
    # 7. Convert refined arrays into global vector
    # ========================================================

    new_Nspace = J * new_Nx

    new_size = (
        3 * new_Nt2 * new_Nspace
        + 2 * new_Nspace
    )

    new_w = np.zeros(
        new_size,
        dtype=float,
    )

    from_3d_to_1d(
        new_Nt2,
        new_Nx,
        J,
        new_w,
        rho_new,
        u_new,
        V_new,
    )

    return new_w
