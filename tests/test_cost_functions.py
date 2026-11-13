"""Tests for the general J-class traffic cost functions."""

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

from cost_functions import get_model, validate_parameters


MODELS = ("GLWR", "GS", "GNS")

RHO = np.array([0.08, 0.06, 0.04])
U_MAX = np.array([1.0, 0.75, 0.5])
RHO_JAM = np.array([1.0, 2.0 / 3.0, 0.5])

H = 1e-6


def finite_difference(function, x, h=H):
    """Central finite-difference approximation."""
    return (function(x + h) - function(x - h)) / (2.0 * h)


@pytest.mark.parametrize("model_name", MODELS)
def test_model_interface(model_name):
    """All models expose the required numerical functions."""

    model = get_model(model_name)

    required = {
        "f_mfg",
        "f_starp",
        "f_star",
        "f_starp_p",
        "f_starp_r",
        "f_star_p",
        "f_star_r",
        "f_star_u",
    }

    assert set(model) == required
    assert all(callable(model[key]) for key in required)


def test_invalid_model():
    with pytest.raises(ValueError, match="Unknown model"):
        get_model("INVALID")


def test_invalid_parameters():
    with pytest.raises(ValueError):
        validate_parameters(
            0, RHO, U_MAX[:2], RHO_JAM
        )

    with pytest.raises(ValueError):
        validate_parameters(
            0, RHO, U_MAX, np.array([1.0, 0.0, 0.5])
        )

    with pytest.raises(IndexError):
        validate_parameters(
            3, RHO, U_MAX, RHO_JAM
        )


@pytest.mark.parametrize("model_name", MODELS)
@pytest.mark.parametrize("j", range(3))
def test_optimal_control_derivative_p(model_name, j):
    """Check d(u*)/dp away from clipping boundaries."""

    model = get_model(model_name)
    p = 0.1

    numerical = finite_difference(
        lambda value: model["f_starp"](
            j, value, RHO, U_MAX, RHO_JAM
        ),
        p,
    )

    analytical = model["f_starp_p"](
        j, p, RHO, U_MAX, RHO_JAM
    )

    np.testing.assert_allclose(
        analytical, numerical, rtol=1e-6, atol=1e-8
    )


@pytest.mark.parametrize("model_name", MODELS)
@pytest.mark.parametrize("j", range(3))
@pytest.mark.parametrize("m", range(3))
def test_optimal_control_derivative_density(model_name, j, m):
    """Check d(u*)/d(rho_m) away from clipping boundaries."""

    model = get_model(model_name)
    p = 0.1

    def control_with_density(value):
        rho = RHO.copy()
        rho[m] = value
        return model["f_starp"](
            j, p, rho, U_MAX, RHO_JAM
        )

    numerical = finite_difference(
        control_with_density, RHO[m]
    )

    analytical = model["f_starp_r"](
        j, m, p, RHO, U_MAX, RHO_JAM
    )

    np.testing.assert_allclose(
        analytical, numerical, rtol=1e-6, atol=1e-8
    )


@pytest.mark.parametrize("model_name", MODELS)
@pytest.mark.parametrize("j", range(3))
def test_hamiltonian_derivative_p(model_name, j):
    """Check the Hamiltonian's partial derivative with respect to p."""

    model = get_model(model_name)
    p = 0.1
    u = 0.3 * U_MAX[j]

    numerical = finite_difference(
        lambda value: model["f_star"](
            j, value, RHO, U_MAX, RHO_JAM, u=u
        ),
        p,
    )

    analytical = model["f_star_p"](
        j, p, RHO, U_MAX, RHO_JAM, u=u
    )

    np.testing.assert_allclose(
        analytical, numerical, rtol=1e-6, atol=1e-8
    )


@pytest.mark.parametrize("model_name", MODELS)
@pytest.mark.parametrize("j", range(3))
@pytest.mark.parametrize("m", range(3))
def test_hamiltonian_derivative_density(model_name, j, m):
    """Check the Hamiltonian's partial derivative with respect to rho_m."""

    model = get_model(model_name)
    p = 0.1
    u = 0.3 * U_MAX[j]

    def hamiltonian_with_density(value):
        rho = RHO.copy()
        rho[m] = value
        return model["f_star"](
            j, p, rho, U_MAX, RHO_JAM, u=u
        )

    numerical = finite_difference(
        hamiltonian_with_density, RHO[m]
    )

    analytical = model["f_star_r"](
        j, m, p, RHO, U_MAX, RHO_JAM, u=u
    )

    np.testing.assert_allclose(
        analytical, numerical, rtol=1e-6, atol=1e-8
    )


@pytest.mark.parametrize("model_name", MODELS)
@pytest.mark.parametrize("j", range(3))
def test_hamiltonian_derivative_u(model_name, j):
    """Check the Hamiltonian's partial derivative with respect to u."""

    model = get_model(model_name)
    p = 0.1
    u = 0.3 * U_MAX[j]

    numerical = finite_difference(
        lambda value: model["f_star"](
            j, p, RHO, U_MAX, RHO_JAM, u=value
        ),
        u,
    )

    analytical = model["f_star_u"](
        j, p, RHO, U_MAX, RHO_JAM, u=u
    )

    np.testing.assert_allclose(
        analytical, numerical, rtol=1e-6, atol=1e-8
    )


@pytest.mark.parametrize("model_name", ("GS", "GNS"))
@pytest.mark.parametrize("j", range(3))
def test_velocity_bounds(model_name, j):
    """GS and GNS optimal velocities respect their constraints."""

    model = get_model(model_name)

    for p in (-10.0, -1.0, 0.0, 0.1, 1.0, 10.0):
        velocity = model["f_starp"](
            j, p, RHO, U_MAX, RHO_JAM
        )

        assert 0.0 <= velocity <= U_MAX[j]


@pytest.mark.parametrize("model_name", ("GS", "GNS"))
@pytest.mark.parametrize("j", range(3))
@pytest.mark.parametrize("p", (-10.0, 10.0))
def test_saturated_control_derivatives(model_name, j, p):
    """Derivatives of saturated optimal controls are zero."""

    model = get_model(model_name)

    assert model["f_starp_p"](
        j, p, RHO, U_MAX, RHO_JAM
    ) == 0.0

    for m in range(3):
        assert model["f_starp_r"](
            j, m, p, RHO, U_MAX, RHO_JAM
        ) == 0.0
