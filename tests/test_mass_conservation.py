"""Mass-conservation tests for the multi-class traffic MFG solver."""

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]

SOLVER = (
    ROOT
    / "src"
    / "newton_krylov"
    / "multi_class"
    / "main.py"
)


@pytest.mark.parametrize("model", ["GLWR", "GS", "GNS"])
def test_mass_conservation(model, tmp_path):
    """Each vehicle class must conserve its discrete total mass."""

    output = tmp_path / f"sequential_J3_{model}.npz"

    command = [
        sys.executable,
        str(SOLVER),
        "--J", "3",
        "--model", model,
        "--nx", "5",
        "--nt", "8",
        "--max-grids", "1",
        "--newton-tol", "1e-10",
        "--gmres-rtol", "1e-10",
        "--max-newton-iter", "50",
        "--output", str(output),
    ]

    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, (
        f"{model} solver failed.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    assert output.exists(), f"{model} output file was not created."

    with np.load(output, allow_pickle=False) as data:

        rho = np.asarray(data["rho"])

        J = int(data["J"])
        Nx = int(data["Nx"])
        Nt = int(data["Nt"])
        dx = float(data["dx"])

        residual = float(data["residual_l2"])

        assert rho.shape == (J, Nx, Nt + 1)
        assert J == 3

        assert np.isfinite(rho).all()
        assert np.isfinite(residual)

        # Total mass for every class at every time step.
        # Shape: (J, Nt + 1)
        mass = dx * np.sum(rho, axis=1)

        # Initial mass for each class.
        initial_mass = mass[:, [0]]

        mass_error = np.abs(mass - initial_mass)

        max_error = np.max(mass_error)

        print(f"\nModel: {model}")
        print(f"Maximum mass-conservation error: {max_error:.12e}")
        print(f"Final nonlinear residual:        {residual:.12e}")

        for j in range(J):
            class_error = np.max(mass_error[j])

            print(
                f"Class {j + 1}: "
                f"initial mass = {initial_mass[j, 0]:.12e}, "
                f"maximum error = {class_error:.12e}"
            )

            assert class_error < 1e-8, (
                f"{model}: mass conservation failed "
                f"for class {j + 1}"
            )

        assert residual < 1e-8, (
            f"{model}: nonlinear residual is too large"
        )
