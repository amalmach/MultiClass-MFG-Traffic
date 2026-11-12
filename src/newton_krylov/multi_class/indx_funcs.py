#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Index mappings for the general J-class traffic MFG model.

Based on:
    Appendix D.1, Listings D.1 and D.2

Global unknown vector:
    w = [rho, u, V]

For each class:
    rho: (Nx, Nt+1)
    u:   (Nx, Nt)
    V:   (Nx, Nt+1)

Class and spatial indices are one-based in the mapping
functions, following the thesis convention.

Time indices are zero-based.
"""

import numpy as np


# ============================================================
# 1. Combined class-spatial index
# ============================================================

def kj(j, k, Nx):
    """
    Convert class and spatial indices into a global
    spatial index.

    j = 1, ..., J
    k = 1, ..., Nx

    Returns:
        kj = 1, ..., J*Nx
    """

    return (j - 1) * Nx + k


# ============================================================
# 2. Unknown-vector indices
# ============================================================

def r_idx(kj_val, n, Nt):
    """
    Density rho index.
    """

    return (kj_val - 1) * (Nt + 1) + n


def u_idx(kj_val, n, Nt, Nx, J):
    """
    Optimal velocity u index.
    """

    return (
        (Nt + 1) * (J * Nx)
        + (kj_val - 1) * Nt
        + n
    )


def V_idx(kj_val, n, Nt, Nx, J):
    """
    Value function V index.
    """

    return (
        (2 * Nt + 1) * (J * Nx)
        + (kj_val - 1) * (Nt + 1)
        + n
    )


# ============================================================
# 3. Nonlinear residual indices
# ============================================================

def Fr_idx(kj_val, n, Nt):
    """
    Density equation index.
    """

    return (kj_val - 1) * Nt + n


def Fu_idx(kj_val, n, Nt, Nx, J):
    """
    Optimal-control equation index.
    """

    return (
        Nt * (J * Nx)
        + (kj_val - 1) * Nt
        + n
    )


def FV_idx(kj_val, n, Nt, Nx, J):
    """
    Hamilton-Jacobi equation index.
    """

    return (
        2 * Nt * (J * Nx)
        + (kj_val - 1) * Nt
        + n
    )


def Frint_idx(kj_val, Nt, Nx, J):
    """
    Initial density equation index.
    """

    return (
        3 * Nt * (J * Nx)
        + (kj_val - 1)
    )


def FVter_idx(kj_val, Nt, Nx, J):
    """
    Terminal value-function equation index.
    """

    return (
        (3 * Nt + 1) * (J * Nx)
        + (kj_val - 1)
    )


# ============================================================
# 4. Convert global solution vector into class arrays
# ============================================================

def solutions(sol, Nt, Nx, J):
    """
    Convert the global solution vector into
    class-dependent numerical arrays.

    Parameters
    ----------
    sol : ndarray
        Global numerical solution.

    Nt : int
        Number of temporal steps.

    Nx : int
        Number of spatial cells.

    J : int
        Number of traffic classes.

    Returns
    -------
    rho : ndarray
        Traffic densities, shape (J, Nx, Nt+1).

    u : ndarray
        Optimal velocities, shape (J, Nx, Nt).

    V : ndarray
        Value functions, shape (J, Nx, Nt+1).

    Q : ndarray
        Traffic fluxes, shape (J, Nx, Nt).
    """

    # Allocate numerical arrays

    rho = np.zeros((J, Nx, Nt + 1))
    u = np.zeros((J, Nx, Nt))
    V = np.zeros((J, Nx, Nt + 1))
    Q = np.zeros((J, Nx, Nt))

    # Check global solution dimension

    expected_size = 3 * Nt * (J * Nx) + 2 * (J * Nx)

    if len(sol) != expected_size:
        raise ValueError(
            f"Invalid solution size: {len(sol)}. "
            f"Expected {expected_size}."
        )

    # Loop over all traffic classes

    for j in range(1, J + 1):

        # Loop over spatial cells

        for k in range(1, Nx + 1):

            kj_val = kj(j, k, Nx)

            # Density and value function:
            # n = 0, ..., Nt

            for n in range(Nt + 1):

                rho[j - 1, k - 1, n] = sol[
                    r_idx(kj_val, n, Nt)
                ]

                V[j - 1, k - 1, n] = sol[
                    V_idx(kj_val, n, Nt, Nx, J)
                ]

                # Velocity and flux:
                # n = 0, ..., Nt-1

                if n < Nt:

                    u[j - 1, k - 1, n] = sol[
                        u_idx(kj_val, n, Nt, Nx, J)
                    ]

                    Q[j - 1, k - 1, n] = (
                        rho[j - 1, k - 1, n]
                        * u[j - 1, k - 1, n]
                    )

    return rho, u, V, Q
