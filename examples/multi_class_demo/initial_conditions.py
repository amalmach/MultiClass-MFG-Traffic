#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Initial Traffic Density Configurations
======================================

Two-class traffic configurations:

    CT  — Cars–Trucks
    TC  — Trucks–Cars
    TCT — Trucks–Cars–Trucks

Vehicle classes:
    Class 1: Cars
    Class 2: Trucks

The Gaussian density profiles follow the initial configurations
used in the two-class traffic experiments.

Reference:
    Machtalay, PhD thesis (2026), Chapter II.
"""

import numpy as np


# ============================================================
# 1. Gaussian density profile
# ============================================================

def gaussian(x, center, sigma, amplitude):
    """Return a Gaussian density profile."""

    if sigma <= 0:
        raise ValueError("Gaussian width must be positive.")

    return amplitude * np.exp(
        -0.5 * ((np.asarray(x) - center) / sigma) ** 2
    )


# ============================================================
# 2. Two-class initial configurations
# ============================================================

def get_initial_configuration(
    configuration="TC",
    sigma=0.15,
):
    """
    Construct two-class initial traffic densities.

    Parameters
    ----------
    configuration : str
        CT, TC, or TCT.

    sigma : float
        Gaussian width.

    Returns
    -------
    dict
        Road length, configuration name, and initial
        density functions for cars and trucks.
    """

    configuration = configuration.upper()

    if configuration not in ("CT", "TC", "TCT"):
        raise ValueError(
            "Choose CT, TC, or TCT."
        )

    if sigma <= 0:
        raise ValueError(
            "Gaussian width must be positive."
        )

    # Jam densities from the two-class traffic model.
    rho_car_max = 1.0
    rho_truck_max = 0.5

    # --------------------------------------------------------
    # TC — Trucks–Cars
    # --------------------------------------------------------

    if configuration == "TC":

        L = 2.0

        def rho_cars(x):
            return gaussian(
                x,
                center=3.0 * L / 4.0,
                sigma=sigma,
                amplitude=rho_car_max,
            )

        def rho_trucks(x):
            return gaussian(
                x,
                center=L / 4.0,
                sigma=sigma,
                amplitude=rho_truck_max,
            )

    # --------------------------------------------------------
    # CT — Cars–Trucks
    # --------------------------------------------------------

    elif configuration == "CT":

        L = 2.0

        def rho_cars(x):
            return gaussian(
                x,
                center=L / 4.0,
                sigma=sigma,
                amplitude=rho_car_max,
            )

        def rho_trucks(x):
            return gaussian(
                x,
                center=3.0 * L / 4.0,
                sigma=sigma,
                amplitude=rho_truck_max,
            )

    # --------------------------------------------------------
    # TCT — Trucks–Cars–Trucks
    # --------------------------------------------------------

    else:

        # Original six-peak configuration.
        #
        # Road layout:
        #
        # Trucks  Cars  Trucks  Cars  Trucks  Cars
        #   0.5    1.5    2.5    3.5    4.5    5.5
        #
        # Road length: L = 6

        L = 6.0

        car_centers = (
            1.5,
            3.5,
            5.5,
        )

        truck_centers = (
            0.5,
            2.5,
            4.5,
        )

        def rho_cars(x):
            """Initial car density with three Gaussian peaks."""

            return sum(
                gaussian(
                    x,
                    center=center,
                    sigma=sigma,
                    amplitude=rho_car_max,
                )
                for center in car_centers
            )

        def rho_trucks(x):
            """Initial truck density with three Gaussian peaks."""

            return sum(
                gaussian(
                    x,
                    center=center,
                    sigma=sigma,
                    amplitude=rho_truck_max,
                )
                for center in truck_centers
            )

    # --------------------------------------------------------
    # Return the selected initial configuration
    # --------------------------------------------------------

    return {
        "configuration": configuration,
        "L": L,
        "sigma": sigma,
        "rho_int_list": [
            rho_cars,
            rho_trucks,
        ],
        "class_names": [
            "Cars",
            "Trucks",
        ],
    }

# ============================================================
# 3. Validate initial density profiles
# ============================================================

def validate_initial_configuration(
    parameters,
    n_points=1000,
):
    """
    Check the initial density profiles on a spatial grid.

    The normalized total density is:

        rho_cars / rho_jam_cars
        +
        rho_trucks / rho_jam_trucks

    Returns the maximum normalized density.
    """

    L = parameters["L"]

    rho_int_list = parameters["rho_int_list"]

    x = np.linspace(
        0.0,
        L,
        n_points,
    )

    rho_cars = rho_int_list[0](x)
    rho_trucks = rho_int_list[1](x)

    if not (
        np.all(np.isfinite(rho_cars))
        and np.all(np.isfinite(rho_trucks))
    ):
        raise ValueError(
            "Initial density contains non-finite values."
        )

    if np.any(rho_cars < 0) or np.any(rho_trucks < 0):
        raise ValueError(
            "Initial densities must be nonnegative."
        )

    normalized_density = (
        rho_cars / 1.0
        +
        rho_trucks / 0.5
    )

    max_density = float(
        np.max(normalized_density)
    )

    return max_density
