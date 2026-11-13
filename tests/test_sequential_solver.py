"""Integration tests for the sequential multi-class Newton-GMRES solver."""

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / "src" / "newton_krylov" / "multi_class"
SOLVER = MODULE_DIR / "main.py"

sys.path.insert(0, str(MODULE_DIR))

from cost_functions import get_model
from inputs import get_inputs
from newton_func import newton_func


@pytest.mark.parametrize("model_name", ("GLWR", "GS", "GNS"))
def test_sequential_solution(model_name, tmp_path):
    """Verify solution arrays, flux identity and nonlinear residual."""

    output = tmp_path / f"{model_name}.npz"

    command = [
        sys.executable,
        str(SOLVER),
        "--J", "3",
        "--model", model_name,
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
    )

    assert result.returncode == 0, (
        f"Solver failed for {model_name}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    assert output.is_file()

    with np.load(output, allow_pickle=False) as data:
        w = data["solution"]
        rho = data["rho"]
        u = data["u"]
        V = data["V"]
        Q = data["Q"]
        x = data["x"]
        t = data["t"]

        J = int(data["J"])
        Nx = int(data["Nx"])
        Nt = int(data["Nt"])
        dt = float(data["dt"])
        dx = float(data["dx"])
        eps = float(data["eps"])

        u_max = data["u_max_vec"]
        rho_jam = data["rho_jam_vec"]

        reported_l2 = float(data["residual_l2"])
        reported_inf = float(data["residual_inf"])

        assert J == 3
        assert Nx == 5
        assert Nt == 8

        N = (3 * Nt + 2) * J * Nx

        assert w.shape == (N,)
        assert rho.shape == (J, Nx, Nt + 1)
        assert u.shape == (J, Nx, Nt)
        assert V.shape == (J, Nx, Nt + 1)
        assert Q.shape == (J, Nx, Nt)
        assert x.shape == (Nx + 1,)
        assert t.shape == (Nt + 1,)

        for array in (w, rho, u, V, Q, x, t):
            assert np.isfinite(array).all()

        np.testing.assert_allclose(
            Q,
            rho[:, :, :-1] * u,
            rtol=0,
            atol=1e-14,
        )

        # Recompute the nonlinear residual independently
        # from the solution saved by the solver.

        params = get_inputs(J=J, model=model_name)
        model = get_model(model_name)

        residual = np.asarray(
            newton_func(
                w,
                model["f_starp"],
                model["f_star"],
                params["rho_int_list"],
                Nt,
                Nx,
                J,
                dt,
                dx,
                eps,
                x,
                params["VT"],
                u_max,
                rho_jam,
            )
        )

        computed_l2 = np.linalg.norm(residual)
        computed_inf = np.max(np.abs(residual))

        assert computed_l2 < 1e-8

        np.testing.assert_allclose(
            reported_l2,
            computed_l2,
            rtol=1e-4,
            atol=1e-12,
        )

        np.testing.assert_allclose(
            reported_inf,
            computed_inf,
            rtol=1e-4,
            atol=1e-12,
        )

        # GS and GNS have explicitly bounded controls.
        if model_name in ("GS", "GNS"):
            assert np.min(u) >= -1e-10
            assert np.all(
                u <= u_max[:, None, None] + 1e-10
            )

        print(
            f"\n{model_name}: N={N}, "
            f"residual L2={computed_l2:.12e}, "
            f"residual inf={computed_inf:.12e}"
        )
