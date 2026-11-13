"""MPI process-count consistency tests for the multi-class PETSc solver."""

import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]

PETSC_SOLVER = (
    ROOT / "src" / "petsc4py" / "multi_class" / "main.py"
)

MPIEXEC = shutil.which("mpirun") or shutil.which("mpiexec")

PROCESS_COUNTS = (1, 2, 4)
MODELS = ("GLWR", "GS", "GNS")


def run_petsc(model, processes, output):
    """Run the PETSc solver with the specified number of MPI processes."""

    command = [
        MPIEXEC,
        "-np",
        str(processes),
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

    # Additional MUMPS workspace was required in the
    # previously validated four-process GNS configuration.
    if model == "GNS" and processes == 4:
        command.extend(["-mat_mumps_icntl_14", "200"])

    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )

    assert result.returncode == 0, (
        f"{model} failed with {processes} MPI processes.\n"
        f"Command: {' '.join(command)}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    assert output.is_file(), (
        f"Missing output for {model}, MPI processes={processes}"
    )


def load_solution(filename):
    """Load the numerical arrays needed for consistency checks."""

    with np.load(filename, allow_pickle=False) as data:
        return {
            key: np.array(data[key], copy=True)
            for key in (
                "solution",
                "rho",
                "u",
                "V",
                "Q",
                "J",
                "Nx",
                "Nt",
                "dt",
                "dx",
                "eps",
                "u_max_vec",
                "rho_jam_vec",
                "residual_l2",
                "residual_inf",
            )
        }


@pytest.mark.parametrize("model", MODELS)
def test_mpi_process_count_consistency(model, tmp_path):
    """Compare solutions obtained with 1, 2, and 4 MPI processes."""

    if MPIEXEC is None:
        pytest.skip("MPI launcher is unavailable")

    pytest.importorskip("petsc4py")
    pytest.importorskip("mpi4py")

    results = {}

    for processes in PROCESS_COUNTS:
        output = tmp_path / f"{model}_MPI{processes}.npz"

        run_petsc(model, processes, output)
        results[processes] = load_solution(output)

    reference = results[1]

    J = int(reference["J"])
    Nx = int(reference["Nx"])
    Nt = int(reference["Nt"])

    N = (3 * Nt + 2) * J * Nx

    assert J == 3
    assert Nx == 5
    assert Nt == 8
    assert reference["solution"].shape == (N,)

    print(f"\nModel: {model}")
    print(f"Unknowns: {N}")

    for processes in PROCESS_COUNTS:
        result = results[processes]

        # Verify matching discretization.
        for key in ("J", "Nx", "Nt"):
            assert int(result[key]) == int(reference[key])

        for key in ("dt", "dx", "eps"):
            np.testing.assert_allclose(
                result[key],
                reference[key],
                rtol=1e-12,
                atol=1e-14,
            )

        for key in ("u_max_vec", "rho_jam_vec"):
            np.testing.assert_allclose(
                result[key],
                reference[key],
                rtol=1e-12,
                atol=1e-14,
            )

        # Check finite numerical values.
        for key in ("solution", "rho", "u", "V", "Q"):
            assert np.isfinite(result[key]).all()

        # Check nonlinear residual.
        residual = float(result["residual_l2"])
        assert np.isfinite(residual)
        assert residual < 1e-7

        # Check flux identity.
        np.testing.assert_allclose(
            result["Q"],
            result["rho"][:, :, :-1] * result["u"],
            rtol=0,
            atol=1e-12,
        )

        # Check conservation of each class's mass.
        dx = float(result["dx"])

        mass = dx * np.sum(result["rho"], axis=1)
        mass_error = np.max(
            np.abs(mass - mass[:, [0]]),
            axis=1,
        )

        assert np.all(mass_error < 1e-8)

        # Check explicit velocity constraints for GS/GNS.
        if model in ("GS", "GNS"):
            u_max = result["u_max_vec"]

            assert np.min(result["u"]) >= -1e-10
            assert np.all(
                result["u"] <= u_max[:, None, None] + 1e-10
            )

        print(
            f"MPI processes={processes}: "
            f"residual={residual:.12e}, "
            f"max mass error={np.max(mass_error):.12e}"
        )

    # Compare the 2-rank and 4-rank results with the 1-rank solution.
    w_reference = reference["solution"]

    for processes in (2, 4):
        current = results[processes]

        difference = current["solution"] - w_reference

        maximum_error = np.max(np.abs(difference))
        relative_error = (
            np.linalg.norm(difference)
            / max(np.linalg.norm(w_reference), 1e-15)
        )

        np.testing.assert_allclose(
            current["solution"],
            w_reference,
            rtol=1e-8,
            atol=1e-10,
        )

        assert relative_error < 1e-8

        for key in ("rho", "u", "V", "Q"):
            np.testing.assert_allclose(
                current[key],
                reference[key],
                rtol=1e-8,
                atol=1e-10,
                err_msg=(
                    f"{model}: mismatch in {key} "
                    f"between 1 and {processes} MPI processes"
                ),
            )

        print(
            f"MPI 1 vs {processes}: "
            f"maximum solution difference={maximum_error:.12e}, "
            f"relative L2 difference={relative_error:.12e}"
        )
