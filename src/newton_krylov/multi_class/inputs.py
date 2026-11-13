#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Traffic Inputs for the General J-Class Mean-Field Game
=======================================================

Based on:
    PhD thesis, Appendix D.1
    Listing D.10 — J-class traffic inputs
    Listing D.11 — Initial density configuration
    Listing D.12 — Two-class initial densities

Supported models:
    GLWR — Generalized LWR
    GS   — Generalized Separable
    GNS  — Generalized Non-Separable

The two-class defaults follow the thesis configuration.

For J > 2, additional class parameters and initial density
profiles are generated for numerical experimentation.
These additional defaults are illustrative, not thesis data.
"""

import numpy as np


# ============================================================
# 1. Terminal cost
# ============================================================

def VT(x):
    """
    Terminal value function.

    V(T, x) = 0
    """
    return 0.0


# ============================================================
# 2. Initial-density function
# ============================================================

def gaussian_density(rho_a, rho_b, center, sigma):
    """
    Construct a Gaussian initial-density profile.

    rho(x) = rho_a + (rho_b - rho_a)
             * exp(-0.5 * ((x-center)/sigma)**2)
    """

    if sigma <= 0:
        raise ValueError("sigma must be positive.")

    def rho_int(x):
        return (
            rho_a
            + (rho_b - rho_a)
            * np.exp(
                -0.5 * ((x - center) / sigma)**2
            )
        )

    return rho_int


# ============================================================
# 3. General J-class input configuration
# ============================================================

def get_inputs(J=2, model="GLWR"):
    """
    Return the parameters for a J-class traffic MFG problem.

    Parameters
    ----------
    J : int
        Number of vehicle classes.

    model : str
        GLWR, GS, or GNS.

    Returns
    -------
    dict
        Physical parameters, numerical parameters,
        initial density functions, and solver settings.
    """

    # --------------------------------------------------------
    # Validate the model
    # --------------------------------------------------------

    if not isinstance(J, (int, np.integer)) or J < 1:
        raise ValueError(
            "J must be a positive integer."
        )

    model = model.upper()

    if model not in ("GLWR", "GS", "GNS"):
        raise ValueError(
            "Choose GLWR, GS, or GNS."
        )

    # --------------------------------------------------------
    # Time horizon
    # --------------------------------------------------------

    T = 1.0

    # --------------------------------------------------------
    # Vehicle-class parameters
    # --------------------------------------------------------

    if J == 1:

        # Illustrative single-class configuration
        N_list = np.array([1.0])
        L_list = np.array([1.0])
        l_list = np.array([1.0])

        rho_jam_vec = np.array([1.0])
        u_max_vec = np.array([1.0])

    elif J == 2:

        # Original two-class parameters from Listing D.10
        N_list = np.array([1.0, 1.0])
        L_list = np.array([1.0, 1.0])
        l_list = np.array([1.0, 2.0])

        rho_jam_vec = np.array([1.0, 0.5])
        u_max_vec = np.array([1.0, 0.5])

    else:

        # Illustrative extension to arbitrary J classes
        N_list = np.ones(J)
        L_list = np.ones(J)

        l_list = np.linspace(1.0, 2.0, J)

        rho_jam_vec = 1.0 / l_list

        u_max_vec = np.linspace(1.0, 0.5, J)

    # --------------------------------------------------------
    # Aggregate parameters
    # --------------------------------------------------------

    N_total = float(np.sum(N_list))
    L_total = float(np.sum(L_list))
    l_total = float(np.sum(l_list))

    # Common spatial domain for the numerical problem.
    # Here we use L_total as the road length.

    L = L_total

    # --------------------------------------------------------
    # Stability parameters
    # --------------------------------------------------------

    CFL = 0.75
    EPS = 0.45

    # --------------------------------------------------------
    # Multigrid parameters
    # --------------------------------------------------------

    nb_grid = 5
    multip = 2

    use_multigrid = True
    use_precond = True

    # Coarse spatial-temporal grid
    Nx0 = 15
    Nt0 = 60

    # --------------------------------------------------------
    # Artificial viscosity
    # --------------------------------------------------------

    if model == "GLWR":

        mu = [0.0] * nb_grid

    elif model == "GS":

        # First five values from the GS example in D.10
        mu = [
            0.05,
            0.045,
            0.04,
            0.035,
            0.03,
        ]

    else:

        # GNS example from D.10
        mu = [
            0.04,
            0.03,
            0.02,
            0.01,
            0.0,
        ]

    # --------------------------------------------------------
    # Class-dependent initial densities
    # --------------------------------------------------------

    rho_int_list = []

    if J == 1:

        # Gaussian configuration
        rho_int_list.append(
            gaussian_density(
                rho_a=0.2,
                rho_b=0.8,
                center=L / 2.0,
                sigma=0.15 * L,
            )
        )

    elif J == 2:

        # Fully segregated TC configuration,
        # following Listing D.12.
        #
        # Class 1: density concentrated near 3L/4
        # Class 2: density concentrated near L/4

        sigma = 0.15

        rho_int_list.append(
            gaussian_density(
                rho_a=0.0,
                rho_b=1.0,
                center=3.0 * L / 4.0,
                sigma=sigma,
            )
        )

        rho_int_list.append(
            gaussian_density(
                rho_a=0.0,
                rho_b=0.5,
                center=L / 4.0,
                sigma=sigma,
            )
        )

    else:

        # Illustrative J-class configuration.
        #
        # Distribute the initial density concentrations
        # across different positions of the road.

        centers = np.linspace(
            L / (J + 1),
            J * L / (J + 1),
            J,
        )

        sigma = 0.15 * L

        for j in range(J):

            rho_int_list.append(
                gaussian_density(
                    rho_a=0.0,
                    rho_b=(0.8 / J) * rho_jam_vec[j],
                    center=centers[j],
                    sigma=sigma,
                )
            )

    # --------------------------------------------------------
    # Validate the configuration
    # --------------------------------------------------------

    if len(rho_int_list) != J:
        raise ValueError(
            "Expected one initial-density function "
            "for each vehicle class."
        )

    if len(mu) != nb_grid:
        raise ValueError(
            "Viscosity list must contain nb_grid entries."
        )

    if not (
        len(u_max_vec)
        == len(rho_jam_vec)
        == len(N_list)
        == J
    ):
        raise ValueError(
            "Inconsistent class-dependent arrays."
        )

    # --------------------------------------------------------
    # Return the parameters
    # --------------------------------------------------------

    return {
        "model": model,
        "T": T,
        "J": J,
        "L": L,
        "N_list": N_list,
        "N_total": N_total,
        "L_list": L_list,
        "L_total": L_total,
        "l_list": l_list,
        "l_total": l_total,
        "rho_jam_vec": rho_jam_vec,
        "u_max_vec": u_max_vec,
        "CFL": CFL,
        "EPS": EPS,
        "mu": mu,
        "nb_grid": nb_grid,
        "multip": multip,
        "use_multigrid": use_multigrid,
        "use_precond": use_precond,
        "Nx0": Nx0,
        "Nt0": Nt0,
        "rho_int_list": rho_int_list,
        "VT": VT,
    }


# ============================================================
# 4. Display the configuration
# ============================================================

def print_inputs(parameters):
    """
    Print the selected traffic configuration.
    """

    print("=" * 60)
    print("General J-Class Traffic Mean-Field Game")
    print("=" * 60)

    print(f"Model:                  {parameters['model']}")
    print(f"Number of classes:      {parameters['J']}")

    print("\nPhysical parameters:")

    print(f"T:                      {parameters['T']}")
    print(f"L:                      {parameters['L']}")
    print(f"Maximum velocities:     {parameters['u_max_vec']}")
    print(f"Jam densities:          {parameters['rho_jam_vec']}")

    print("\nNumerical parameters:")

    print(f"Nx0:                    {parameters['Nx0']}")
    print(f"Nt0:                    {parameters['Nt0']}")
    print(f"CFL:                    {parameters['CFL']}")
    print(f"EPS:                    {parameters['EPS']}")
    print(f"Viscosity coefficients: {parameters['mu']}")

    print("\nSolver settings:")

    print(f"Grid levels:            {parameters['nb_grid']}")
    print(f"Refinement factor:      {parameters['multip']}")
    print(f"Preconditioning:        {parameters['use_precond']}")
    print(f"Multigrid:              {parameters['use_multigrid']}")
