"""Integration tests for the general J-class PETSc/MPI traffic solver."""

import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]

PETSC_SOLVER = (
    ROOT
    / "src"
    / "petsc4py"
    / "multi_class"
    / "main.py"
)

MPIEXEC = shutil.which("mpirun") or shutil.which("mpiexec")

pytestmark = pytest.mark.skipif(
    MPIEXEC is None,
    reason="MPI launcher is not installed",
)


@pytest.mark.parametrize("model", ("GLWR", "GS", "GNS"))
def test_petsc_single_process(model, tmp_path):
    """Verify PETSc convergence and physical properties with one rank."""

    pytest.importorskip("petsc4py")
    pytest.importorskip("mpi4py")

    output = tmp_path / f"petsc_J3_{model}.npz"

    command = [
        MPIEXEC,
        "-np", "1",
        sys.executable,
        str(PETSC_SOLVER),
        "--J", "3",
        "--model", model,
        "--nx", "5",
        "--nt", "8",
        "--tol", "1e-8",
        "--max-it", "50",
        "--output", str(output),
        "-ksp_type", "preonly",
        "-pc_type", "lu",
        "-pc_factor_mat_solver_type", "mumps",
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
        f"PETSc solver failed for {model}.\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    assert output.is_file(), (
        f"PETSc output file was not created for {model}"
    )

    with np.load(output, allow_pickle=False) as data:
        w = np.asarray(data["solution"])
        rho = np.asarray(data["rho"])
        u = np.asarray(data["u"])
        V = np.asarray(data["V"])
        Q = np.asarray(data["Q"])

        J = int(data["J"])
        Nx = int(data["Nx"])
        Nt = int(data["Nt"])
        dx = float(data["dx"])

        residual_l2 = float(data["residual_l2"])
        residual_inf = float(data["residual_inf"])

        assert J == 3
        assert Nx == 5
        assert Nt == 8

        N = (3 * Nt + 2) * J * Nx

        assert w.shape == (N,)
        assert rho.shape == (J, Nx, Nt + 1)
        assert u.shape == (J, Nx, Nt)
        assert V.shape == (J, Nx, Nt + 1)
        assert Q.shape == (J, Nx, Nt)

        for array in (w, rho, u, V, Q):
            assert np.isfinite(array).all()

        assert np.isfinite(residual_l2)
        assert np.isfinite(residual_inf)

        # The tested GNS configuration can satisfy the relative
        # SNES convergence criterion before reaching 1e-8 absolute.
        assert residual_l2 < 1e-7

        # Flux identity.
        np.testing.assert_allclose(
            Q,
            rho[:, :, :-1] * u,
            rtol=0,
            atol=1e-12,
        )

        # Class-wise mass conservation.
        mass = dx * np.sum(rho, axis=1)
        initial_mass = mass[:, [0]]

        mass_error = np.max(
            np.abs(mass - initial_mass),
            axis=1,
        )

        assert np.all(mass_error < 1e-8)

        # Explicit velocity constraints for GS and GNS.
        if model in ("GS", "GNS"):
            u_max = np.asarray(data["u_max_vec"])

            assert np.min(u) >= -1e-10
            assert np.all(
                u <= u_max[:, None, None] + 1e-10
            )

        print(f"\nModel: {model}")
        print(f"Unknowns:              {N}")
        print(f"Residual L2:           {residual_l2:.12e}")
        print(f"Residual infinity:     {residual_inf:.12e}")

        for j, error in enumerate(mass_error, start=1):
            print(
                f"Class {j} mass error:  {error:.12e}"
            )
