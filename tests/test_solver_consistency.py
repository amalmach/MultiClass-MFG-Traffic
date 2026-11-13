"""Consistency tests between sequential Newton-GMRES and PETSc/MPI."""

import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]

SEQUENTIAL_SOLVER = (
    ROOT / "src" / "newton_krylov" / "multi_class" / "main.py"
)

PETSC_SOLVER = (
    ROOT / "src" / "petsc4py" / "multi_class" / "main.py"
)

MPIEXEC = shutil.which("mpirun") or shutil.which("mpiexec")


def run_solver(command, model):
    """Execute a solver and report its output if it fails."""

    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, (
        f"{model} solver execution failed.\n"
        f"Command: {' '.join(command)}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


@pytest.mark.parametrize("model", ("GLWR", "GS", "GNS"))
def test_sequential_petsc_consistency(model, tmp_path):
    """Compare the complete solutions from both implementations."""

    if MPIEXEC is None:
        pytest.skip("MPI launcher is unavailable")

    pytest.importorskip("petsc4py")
    pytest.importorskip("mpi4py")

    sequential_output = tmp_path / f"sequential_{model}.npz"
    petsc_output = tmp_path / f"petsc_{model}.npz"

    sequential_command = [
        sys.executable,
        str(SEQUENTIAL_SOLVER),
        "--J", "3",
        "--model", model,
        "--nx", "5",
        "--nt", "8",
        "--max-grids", "1",
        "--newton-tol", "1e-10",
        "--gmres-rtol", "1e-10",
        "--max-newton-iter", "50",
        "--output", str(sequential_output),
    ]

    petsc_command = [
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
        "--output", str(petsc_output),
        "-ksp_type", "preonly",
        "-pc_type", "lu",
        "-pc_factor_mat_solver_type", "mumps",
    ]

    run_solver(sequential_command, model)
    run_solver(petsc_command, model)

    assert sequential_output.is_file()
    assert petsc_output.is_file()

    with (
        np.load(sequential_output, allow_pickle=False) as seq,
        np.load(petsc_output, allow_pickle=False) as par,
    ):
        # Confirm that both solvers use the same discretization.
        for key in ("J", "Nx", "Nt"):
            assert int(seq[key]) == int(par[key])

        for key in ("dt", "dx", "eps"):
            np.testing.assert_allclose(
                seq[key],
                par[key],
                rtol=1e-12,
                atol=1e-14,
            )

        for key in ("u_max_vec", "rho_jam_vec"):
            np.testing.assert_allclose(
                seq[key],
                par[key],
                rtol=1e-12,
                atol=1e-14,
            )

        assert str(seq["model"]) == str(par["model"]) == model

        # Compare the complete solution vectors.
        w_seq = np.asarray(seq["solution"])
        w_par = np.asarray(par["solution"])

        assert w_seq.shape == w_par.shape

        difference = w_seq - w_par

        maximum_error = np.max(np.abs(difference))
        l2_error = np.linalg.norm(difference)

        relative_error = (
            l2_error / max(np.linalg.norm(w_seq), 1e-15)
        )

        assert relative_error < 1e-7, (
            f"{model}: relative solution error = "
            f"{relative_error:.12e}"
        )

        np.testing.assert_allclose(
            w_seq,
            w_par,
            rtol=1e-6,
            atol=1e-7,
        )

        # Compare reconstructed physical variables.
        for key in ("rho", "u", "V", "Q"):
            a = np.asarray(seq[key])
            b = np.asarray(par[key])

            assert a.shape == b.shape

            np.testing.assert_allclose(
                a,
                b,
                rtol=1e-6,
                atol=1e-7,
                err_msg=f"{model}: mismatch in {key}",
            )

        sequential_residual = float(seq["residual_l2"])
        petsc_residual = float(par["residual_l2"])

        assert sequential_residual < 1e-8
        assert petsc_residual < 1e-7

        print(f"\nModel: {model}")
        print(f"Solution vector size: {w_seq.size}")
        print(f"Maximum absolute error: {maximum_error:.12e}")
        print(f"L2 difference:          {l2_error:.12e}")
        print(f"Relative L2 difference: {relative_error:.12e}")
        print(f"Sequential residual:    {sequential_residual:.12e}")
        print(f"PETSc residual:         {petsc_residual:.12e}")
