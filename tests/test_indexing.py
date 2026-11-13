"""Tests for the general J-class indexing functions."""

import sys
from pathlib import Path

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = ROOT / "src" / "newton_krylov" / "multi_class"

sys.path.insert(0, str(MODULE_DIR))

from indx_funcs import (
    kj,
    r_idx,
    u_idx,
    V_idx,
    Fr_idx,
    Fu_idx,
    FV_idx,
    Frint_idx,
    FVter_idx,
    solutions,
)


@pytest.mark.parametrize("J,Nx,Nt", [
    (1, 3, 4),
    (2, 4, 6),
    (3, 5, 8),
    (4, 3, 5),
])
def test_solution_indices(J, Nx, Nt):
    """Every unknown must have exactly one valid global index."""

    N = (3 * Nt + 2) * J * Nx

    indices = []

    for j in range(1, J + 1):
        for k in range(1, Nx + 1):

            jk = kj(j, k, Nx)

            for n in range(Nt + 1):
                indices.append(r_idx(jk, n, Nt))
                indices.append(V_idx(jk, n, Nt, Nx, J))

            for n in range(Nt):
                indices.append(u_idx(jk, n, Nt, Nx, J))

    assert len(indices) == N
    assert len(set(indices)) == N
    assert set(indices) == set(range(N))


@pytest.mark.parametrize("J,Nx,Nt", [
    (1, 3, 4),
    (2, 4, 6),
    (3, 5, 8),
    (4, 3, 5),
])
def test_residual_indices(J, Nx, Nt):
    """Every nonlinear equation must have a unique index."""

    N = (3 * Nt + 2) * J * Nx

    indices = []

    for j in range(1, J + 1):
        for k in range(1, Nx + 1):

            jk = kj(j, k, Nx)

            for n in range(Nt):
                indices.append(Fr_idx(jk, n, Nt))
                indices.append(Fu_idx(jk, n, Nt, Nx, J))
                indices.append(FV_idx(jk, n, Nt, Nx, J))

            indices.append(Frint_idx(jk, Nt, Nx, J))
            indices.append(FVter_idx(jk, Nt, Nx, J))

    assert len(indices) == N
    assert len(set(indices)) == N
    assert set(indices) == set(range(N))


@pytest.mark.parametrize("J,Nx,Nt", [
    (1, 3, 4),
    (2, 4, 6),
    (3, 5, 8),
    (4, 3, 5),
])
def test_solution_reconstruction(J, Nx, Nt):
    """Reconstructed arrays must match the global solution vector."""

    N = (3 * Nt + 2) * J * Nx

    rng = np.random.default_rng(12345)
    w = rng.random(N)

    rho, u, V, Q = solutions(w, Nt, Nx, J)

    assert rho.shape == (J, Nx, Nt + 1)
    assert u.shape == (J, Nx, Nt)
    assert V.shape == (J, Nx, Nt + 1)
    assert Q.shape == (J, Nx, Nt)

    for j in range(1, J + 1):
        for k in range(1, Nx + 1):

            jk = kj(j, k, Nx)

            for n in range(Nt + 1):
                assert rho[j - 1, k - 1, n] == w[
                    r_idx(jk, n, Nt)
                ]

                assert V[j - 1, k - 1, n] == w[
                    V_idx(jk, n, Nt, Nx, J)
                ]

            for n in range(Nt):
                assert u[j - 1, k - 1, n] == w[
                    u_idx(jk, n, Nt, Nx, J)
                ]

    np.testing.assert_allclose(
        Q,
        rho[:, :, :-1] * u,
        rtol=0,
        atol=0,
    )


def test_invalid_solution_size():
    """An incorrectly sized solution vector must be rejected."""

    J = 3
    Nx = 5
    Nt = 8

    N = (3 * Nt + 2) * J * Nx

    invalid_solution = np.zeros(N - 1)

    with pytest.raises(ValueError, match="Invalid solution size"):
        solutions(invalid_solution, Nt, Nx, J)
