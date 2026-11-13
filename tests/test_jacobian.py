"""Finite-difference verification of the analytical sparse Jacobian."""

import sys
from pathlib import Path

import numpy as np
import pytest

MODULE_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "newton_krylov"
    / "multi_class"
)

sys.path.insert(0, str(MODULE_DIR))

from inputs import get_inputs
from cost_functions import get_model
from newton_func import newton_func
from jacobian_exact import jacobian


MODELS = ("GLWR", "GS", "GNS")


@pytest.mark.parametrize("model_name", MODELS)
@pytest.mark.parametrize("J", (1, 2, 3))
def test_exact_jacobian_finite_difference(model_name, J):
    """Compare the analytical Jacobian with a directional derivative."""

    parameters = get_inputs(J=J, model=model_name)
    model = get_model(model_name)

    Nx = 3
    Nt = 4

    dx = parameters["L"] / Nx
    dt = parameters["T"] / Nt

    eps = 0.0 if model_name == "GLWR" else 0.01

    x = np.linspace(0.0, parameters["L"], Nx + 1)

    N = (3 * Nt + 2) * J * Nx

    rng = np.random.default_rng(2026 + J)

    # A reproducible state away from control-switching boundaries.
    w = rng.uniform(-0.02, 0.02, size=N)

    # Normalized perturbation direction.
    direction = rng.normal(size=N)
    direction /= np.linalg.norm(direction)

    def residual(state):
        return newton_func(
            state,
            model["f_starp"],
            model["f_star"],
            parameters["rho_int_list"],
            Nt,
            Nx,
            J,
            dt,
            dx,
            eps,
            x,
            parameters["VT"],
            parameters["u_max_vec"],
            parameters["rho_jam_vec"],
        )

    analytical = jacobian(
        w,
        Nt,
        Nx,
        J,
        dt,
        dx,
        eps,
        parameters["u_max_vec"],
        parameters["rho_jam_vec"],
        model,
        exact=1,
    )

    assert analytical.shape == (N, N)

    h = 1e-6

    numerical_product = (
        residual(w + h * direction)
        - residual(w - h * direction)
    ) / (2.0 * h)

    analytical_product = analytical @ direction

    np.testing.assert_allclose(
        analytical_product,
        numerical_product,
        rtol=1e-6,
        atol=1e-8,
        err_msg=(
            f"Jacobian mismatch for {model_name}, J={J}"
        ),
    )


@pytest.mark.parametrize("model_name", MODELS)
def test_jacobian_is_sparse(model_name):
    """The analytical Jacobian must use a sparse representation."""

    from scipy.sparse import issparse

    J = 3
    Nx = 3
    Nt = 4

    parameters = get_inputs(J=J, model=model_name)
    model = get_model(model_name)

    N = (3 * Nt + 2) * J * Nx

    w = np.zeros(N)

    matrix = jacobian(
        w,
        Nt,
        Nx,
        J,
        parameters["T"] / Nt,
        parameters["L"] / Nx,
        0.0 if model_name == "GLWR" else 0.01,
        parameters["u_max_vec"],
        parameters["rho_jam_vec"],
        model,
        exact=1,
    )

    assert issparse(matrix)
    assert matrix.shape == (N, N)
    assert matrix.nnz > 0
    assert np.isfinite(matrix.data).all()
