#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
General J-Class Traffic Mean-Field Game Cost Functions
======================================================

Based on Appendix D.1 of the PhD thesis:

    Listing D.3 — Generalized LWR (GLWR)
    Listing D.4 — Generalized Separable (GS)
    Listing D.5 — Generalized Non-Separable (GNS)

Supported models:
    GLWR
    GS
    GNS

All functions use zero-based class indices:
    j = 0, ..., J-1

The common function signatures are designed for use
with the general J-class Newton–GMRES solver.

For GS and GNS, the Hamiltonian is evaluated using
the current control variable u.

The derivatives of the clipped optimal controls
are evaluated piecewise, with zero derivatives in
the saturated regions.
"""

import numpy as np


# ============================================================
# 1. Shared functions
# ============================================================

def validate_parameters(j, rho_vec, u_max_vec, rho_jam_vec):
    """Validate class-dependent physical parameters."""

    rho_vec = np.asarray(rho_vec, dtype=float)
    u_max_vec = np.asarray(u_max_vec, dtype=float)
    rho_jam_vec = np.asarray(rho_jam_vec, dtype=float)

    if rho_vec.ndim != 1:
        raise ValueError("rho_vec must be one-dimensional.")

    J = len(rho_vec)

    if J < 1:
        raise ValueError("At least one traffic class is required.")

    if len(u_max_vec) != J or len(rho_jam_vec) != J:
        raise ValueError(
            "rho_vec, u_max_vec and rho_jam_vec "
            "must have the same length."
        )

    if not 0 <= j < J:
        raise IndexError("Invalid traffic class index.")

    if np.any(u_max_vec <= 0):
        raise ValueError("Maximum velocities must be positive.")

    if np.any(rho_jam_vec <= 0):
        raise ValueError("Jam densities must be positive.")

    return rho_vec, u_max_vec, rho_jam_vec


def normalized_total_density(rho_vec, rho_jam_vec):
    """
    Sum of densities normalized by their jam densities.
    """

    return np.sum(rho_vec / rho_jam_vec)


def average_normalized_density(rho_vec, rho_jam_vec):
    """
    Average normalized density over all traffic classes.
    """

    J = len(rho_vec)

    return np.sum(rho_vec / rho_jam_vec) / J


def clip_velocity(u, u_max):
    """
    Enforce 0 <= u <= u_max.
    """

    return np.clip(u, 0.0, u_max)


# ============================================================
# 2. GLWR — Generalized Lighthill–Whitham–Richards
# ============================================================

def glwr_U(j, rho_vec, u_max_vec, rho_jam_vec):
    """
    Generalized Greenshields desired velocity.

    U_j(rho) = u_max_j *
        (1 - sum_m rho_m / rho_jam_m)
    """

    S = normalized_total_density(
        rho_vec,
        rho_jam_vec,
    )

    return u_max_vec[j] * (1.0 - S)


def glwr_f_mfg(j, u, rho_vec, u_max_vec, rho_jam_vec):
    """GLWR running cost."""

    U_j = glwr_U(
        j, rho_vec, u_max_vec, rho_jam_vec
    )

    return 0.5 * (U_j - u)**2


def glwr_f_starp(j, p, rho_vec, u_max_vec, rho_jam_vec):
    """GLWR optimal control."""

    return glwr_U(
        j, rho_vec, u_max_vec, rho_jam_vec
    ) - p


def glwr_f_star(
    j, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """GLWR Hamiltonian."""

    U_j = glwr_U(
        j, rho_vec, u_max_vec, rho_jam_vec
    )

    return -0.5 * p**2 + U_j * p


def glwr_f_starp_p(
    j, p, rho_vec, u_max_vec, rho_jam_vec
):
    """Derivative of the optimal control with respect to p."""

    return -1.0


def glwr_f_starp_r(
    j, m, p, rho_vec, u_max_vec, rho_jam_vec
):
    """Derivative of the optimal control with respect to rho_m."""

    return -u_max_vec[j] / rho_jam_vec[m]


def glwr_f_star_p(
    j, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """Derivative of the Hamiltonian with respect to p."""

    return -p + glwr_U(
        j, rho_vec, u_max_vec, rho_jam_vec
    )


def glwr_f_star_r(
    j, m, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """Derivative of the Hamiltonian with respect to rho_m."""

    return -(u_max_vec[j] / rho_jam_vec[m]) * p


def glwr_f_star_u(
    j, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """Derivative of the Hamiltonian with respect to u."""

    return 0.0


# ============================================================
# 3. GS — Generalized Separable
# ============================================================

def gs_f_mfg(j, u, rho_vec, u_max_vec, rho_jam_vec):
    """
    Generalized separable running cost.
    """

    u_max = u_max_vec[j]

    S = average_normalized_density(
        rho_vec, rho_jam_vec
    )

    return (
        0.5 * (u / u_max)**2
        - u / u_max
        + S
    )


def gs_f_starp(j, p, rho_vec, u_max_vec, rho_jam_vec):
    """
    GS optimal control with velocity constraints.
    """

    u_max = u_max_vec[j]

    u = u_max * (1.0 - u_max * p)

    return clip_velocity(u, u_max)


def gs_f_star(
    j, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """
    GS Hamiltonian evaluated at the supplied control u.
    """

    if u is None:
        u = gs_f_starp(
            j, p, rho_vec, u_max_vec, rho_jam_vec
        )

    return (
        gs_f_mfg(
            j, u, rho_vec, u_max_vec, rho_jam_vec
        )
        + u * p
    )


def gs_f_starp_p(
    j, p, rho_vec, u_max_vec, rho_jam_vec
):
    """
    Derivative of the clipped optimal control.

    On the interior: -u_max**2.
    In saturated regions: 0.
    """

    u_max = u_max_vec[j]

    unconstrained_u = u_max * (1.0 - u_max * p)

    if 0.0 < unconstrained_u < u_max:
        return -u_max**2

    return 0.0


def gs_f_starp_r(
    j, m, p, rho_vec, u_max_vec, rho_jam_vec
):
    """Derivative with respect to rho_m."""

    return 0.0


def gs_f_star_p(
    j, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """Partial derivative with respect to p at fixed u."""

    if u is None:
        u = gs_f_starp(
            j, p, rho_vec, u_max_vec, rho_jam_vec
        )

    return u


def gs_f_star_r(
    j, m, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """Derivative with respect to rho_m."""

    J = len(rho_vec)

    return 1.0 / (J * rho_jam_vec[m])


def gs_f_star_u(
    j, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """Partial derivative with respect to u."""

    if u is None:
        u = gs_f_starp(
            j, p, rho_vec, u_max_vec, rho_jam_vec
        )

    u_max = u_max_vec[j]

    return p + u / u_max**2 - 1.0 / u_max


# ============================================================
# 4. GNS — Generalized Non-Separable
# ============================================================

def gns_f_mfg(j, u, rho_vec, u_max_vec, rho_jam_vec):
    """
    Generalized non-separable running cost.
    """

    J = len(rho_vec)

    S = normalized_total_density(
        rho_vec, rho_jam_vec
    ) / J

    u_max = u_max_vec[j]

    return (
        0.5 * (u / u_max)**2
        - u / u_max
        + S * (u / u_max)
    )


def gns_f_starp(j, p, rho_vec, u_max_vec, rho_jam_vec):
    """
    GNS optimal control with velocity constraints.
    """

    u_max = u_max_vec[j]

    S = average_normalized_density(
        rho_vec, rho_jam_vec
    )

    u = u_max * (1.0 - S - u_max * p)

    return clip_velocity(u, u_max)


def gns_f_star(
    j, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """
    GNS Hamiltonian evaluated at the supplied control u.
    """

    if u is None:
        u = gns_f_starp(
            j, p, rho_vec, u_max_vec, rho_jam_vec
        )

    return (
        gns_f_mfg(
            j, u, rho_vec, u_max_vec, rho_jam_vec
        )
        + u * p
    )


def gns_f_starp_p(
    j, p, rho_vec, u_max_vec, rho_jam_vec
):
    """
    Derivative of the clipped GNS optimal control.

    On the interior: -u_max**2.
    In saturated regions: 0.
    """

    u_max = u_max_vec[j]

    S = average_normalized_density(
        rho_vec, rho_jam_vec
    )

    unconstrained_u = u_max * (
        1.0 - S - u_max * p
    )

    if 0.0 < unconstrained_u < u_max:
        return -u_max**2

    return 0.0


def gns_f_starp_r(
    j, m, p, rho_vec, u_max_vec, rho_jam_vec
):
    """
    Derivative with respect to rho_m.

    Uses the derivative of the clipped control.
    """

    u_max = u_max_vec[j]

    S = average_normalized_density(
        rho_vec, rho_jam_vec
    )

    unconstrained_u = u_max * (
        1.0 - S - u_max * p
    )

    if 0.0 < unconstrained_u < u_max:
        return -u_max / (
            len(rho_vec) * rho_jam_vec[m]
        )

    return 0.0


def gns_f_star_p(
    j, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """Partial derivative with respect to p at fixed u."""

    if u is None:
        u = gns_f_starp(
            j, p, rho_vec, u_max_vec, rho_jam_vec
        )

    return u


def gns_f_star_r(
    j, m, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """Derivative with respect to rho_m."""

    if u is None:
        u = gns_f_starp(
            j, p, rho_vec, u_max_vec, rho_jam_vec
        )

    return (
        u / u_max_vec[j]
    ) / (
        len(rho_vec) * rho_jam_vec[m]
    )


def gns_f_star_u(
    j, p, rho_vec, u_max_vec, rho_jam_vec, u=None
):
    """Partial derivative with respect to u."""

    if u is None:
        u = gns_f_starp(
            j, p, rho_vec, u_max_vec, rho_jam_vec
        )

    u_max = u_max_vec[j]

    S = average_normalized_density(
        rho_vec, rho_jam_vec
    )

    return (
        p
        + u / u_max**2
        - 1.0 / u_max
        + S / u_max
    )


# ============================================================
# 5. Model selector
# ============================================================

def get_model(model_name):
    """
    Select the generalized traffic cost functional.

    Parameters
    ----------
    model_name : str
        "GLWR", "GS", or "GNS".

    Returns
    -------
    dict
        Dictionary containing the running cost,
        optimal control, Hamiltonian, and derivatives.
    """

    models = {

        "GLWR": {
            "f_mfg": glwr_f_mfg,
            "f_starp": glwr_f_starp,
            "f_star": glwr_f_star,
            "f_starp_p": glwr_f_starp_p,
            "f_starp_r": glwr_f_starp_r,
            "f_star_p": glwr_f_star_p,
            "f_star_r": glwr_f_star_r,
            "f_star_u": glwr_f_star_u,
        },

        "GS": {
            "f_mfg": gs_f_mfg,
            "f_starp": gs_f_starp,
            "f_star": gs_f_star,
            "f_starp_p": gs_f_starp_p,
            "f_starp_r": gs_f_starp_r,
            "f_star_p": gs_f_star_p,
            "f_star_r": gs_f_star_r,
            "f_star_u": gs_f_star_u,
        },

        "GNS": {
            "f_mfg": gns_f_mfg,
            "f_starp": gns_f_starp,
            "f_star": gns_f_star,
            "f_starp_p": gns_f_starp_p,
            "f_starp_r": gns_f_starp_r,
            "f_star_p": gns_f_star_p,
            "f_star_r": gns_f_star_r,
            "f_star_u": gns_f_star_u,
        },
    }

    name = model_name.upper()

    if name not in models:
        raise ValueError(
            f"Unknown model '{model_name}'. "
            "Choose GLWR, GS, or GNS."
        )

    return models[name]
