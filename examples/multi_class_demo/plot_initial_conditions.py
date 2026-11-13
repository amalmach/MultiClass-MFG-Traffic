#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Initial Density Configurations — Two-Class Traffic MFG
======================================================

Scientific visualization of the CT, TC, and TCT initial
traffic density configurations.

Reference:
    Machtalay, PhD thesis (2026), Chapter II, Figure II.2.
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from initial_conditions import get_initial_configuration


# ============================================================
# 1. Directories
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PLOTS_DIR = BASE_DIR / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. Plot settings
# ============================================================

CONFIGURATIONS = ("CT", "TC", "TCT")

COLORS = {
    "Cars": "#2166AC",
    "Trucks": "#D6604D",
}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "legend.fontsize": 10,
    "figure.dpi": 120,
    "savefig.dpi": 300,
})


# ============================================================
# 3. Generate comparison figure
# ============================================================

def plot_initial_configurations(sigma=0.15):

    fig, axes = plt.subplots(
        1,
        3,
        figsize=(15, 4.5),
        sharey=True,
    )

    for ax, name in zip(axes, CONFIGURATIONS):

        config = get_initial_configuration(
            configuration=name,
            sigma=sigma,
        )

        L = config["L"]

        x = np.linspace(
            0.0,
            L,
            1000,
        )

        rho_cars = config["rho_int_list"][0](x)
        rho_trucks = config["rho_int_list"][1](x)

        ax.plot(
            x,
            rho_cars,
            color=COLORS["Cars"],
            linewidth=2.5,
            label="Cars",
        )

        ax.plot(
            x,
            rho_trucks,
            color=COLORS["Trucks"],
            linewidth=2.5,
            linestyle="--",
            label="Trucks",
        )

        ax.fill_between(
            x,
            rho_cars,
            color=COLORS["Cars"],
            alpha=0.10,
        )

        ax.fill_between(
            x,
            rho_trucks,
            color=COLORS["Trucks"],
            alpha=0.10,
        )

        ax.set_title(
            f"{name} configuration",
            fontweight="bold",
        )

        ax.set_xlabel("Road position $x$")

        ax.set_xlim(0, L)
        ax.set_ylim(0, 1.05)

        ax.grid(
            alpha=0.2,
            linestyle="--",
        )

        ax.legend(
            loc="upper right",
            frameon=False,
        )

    axes[0].set_ylabel(
        r"Initial density $\rho_j(0,x)$"
    )

    fig.tight_layout()

    output = (
        PLOTS_DIR
        / "two_class_initial_configurations.png"
    )

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight",
    )

    print(f"Saved: {output}")

    plt.show()

    return fig


# ============================================================
# 4. Main execution
# ============================================================

if __name__ == "__main__":

    plot_initial_configurations()
