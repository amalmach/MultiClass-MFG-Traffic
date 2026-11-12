#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sequential Newton–GMRES Solver
==============================

General J-class traffic Mean-Field Game framework.

Based on:
    PhD thesis, Appendix D.1, Listing D.13

Algorithm:
    1. Evaluate the nonlinear residual F(w).
    2. Assemble the analytical Jacobian J_F(w).
    3. Solve J_F(w) * delta_w = -F(w) using GMRES.
    4. Update w = w + delta_w.
    5. Repeat until convergence.

The solver supports an optional sparse preconditioner.

Compatible with SciPy 1.15.
"""

import numpy as np

from scipy.sparse.linalg import gmres


# ============================================================
# 1. GMRES linear solver
# ============================================================

def GMRES_solver(
    A,
    b,
    x0=None,
    M=None,
    rtol=1e-8,
    atol=1e-8,
    restart=None,
    maxiter=None,
):
    """
    Solve A*x = b using preconditioned GMRES.

    Parameters
    ----------
    A : sparse matrix or LinearOperator
        Linear system matrix.

    b : ndarray
        Right-hand side.

    x0 : ndarray, optional
        Initial approximation.

    M : LinearOperator, optional
        Left preconditioner approximating A^(-1).

    rtol, atol : float
        GMRES convergence tolerances.

    restart : int, optional
        Maximum Krylov subspace size.

    maxiter : int, optional
        Maximum number of restart cycles.

    Returns
    -------
    ndarray
        Computed solution.

    Raises
    ------
    RuntimeError
        If GMRES does not converge.
    """

    b = np.asarray(b, dtype=float)

    solution, info = gmres(
        A,
        b,
        x0=x0,
        M=M,
        rtol=rtol,
        atol=atol,
        restart=restart,
        maxiter=maxiter,
    )

    if info != 0:

        if info > 0:
            raise RuntimeError(
                "GMRES did not converge. "
                f"Number of restart cycles: {info}"
            )

        raise RuntimeError(
            f"GMRES failed with info={info}."
        )

    return solution


# ============================================================
# 2. Sequential Newton–GMRES nonlinear solver
# ============================================================

def newton_gmres(
    F,
    w0,
    Jmat,
    Nt,
    Nx,
    J,
    dt,
    dx,
    eps,
    u_max_vec,
    rho_jam_vec,
    M=None,
    rtol=1e-8,
    atol=1e-8,
    max_iter=500,
    gmres_restart=None,
    gmres_maxiter=None,
):
    """
    Solve the nonlinear J-class MFG system using Newton–GMRES.

    Parameters
    ----------
    F : callable
        Nonlinear residual function F(w).

    w0 : ndarray
        Initial guess.

    Jmat : callable
        Function returning the sparse Jacobian J_F(w).

    Nt, Nx, J : int
        Temporal steps, spatial cells, and vehicle classes.

    dt, dx : float
        Temporal and spatial step sizes.

    eps : float
        Dimensionless artificial viscosity.

    u_max_vec : array_like
        Maximum velocities for each class.

    rho_jam_vec : array_like
        Jam densities for each class.

    M : LinearOperator, optional
        Preconditioner for GMRES.

    rtol : float
        Relative tolerance for GMRES.

    atol : float
        Absolute tolerance for GMRES and Newton's
        residual stopping criterion.

    max_iter : int
        Maximum number of Newton iterations.

    gmres_restart : int, optional
        GMRES restart parameter.

    gmres_maxiter : int, optional
        Maximum number of GMRES restart cycles.

    Returns
    -------
    ndarray
        Converged global solution vector.

    Raises
    ------
    RuntimeError
        If Newton or GMRES fails to converge.
    """

    # --------------------------------------------------------
    # Validate numerical configuration
    # --------------------------------------------------------

    if J < 1 or Nx < 1 or Nt < 1:
        raise ValueError(
            "J, Nx, and Nt must be positive."
        )

    if dt <= 0 or dx <= 0:
        raise ValueError(
            "dt and dx must be positive."
        )

    if rtol < 0 or atol < 0:
        raise ValueError(
            "Solver tolerances must be nonnegative."
        )

    if max_iter < 1:
        raise ValueError(
            "max_iter must be at least 1."
        )

    if len(u_max_vec) != J:
        raise ValueError(
            "u_max_vec must have length J."
        )

    if len(rho_jam_vec) != J:
        raise ValueError(
            "rho_jam_vec must have length J."
        )

    # --------------------------------------------------------
    # Initialize the global solution vector
    # --------------------------------------------------------

    w = np.asarray(
        w0,
        dtype=float,
    ).copy()

    expected_size = (
        3 * Nt * (J * Nx)
        + 2 * (J * Nx)
    )

    if w.shape != (expected_size,):
        raise ValueError(
            f"Initial guess must have shape "
            f"({expected_size},). "
            f"Received {w.shape}."
        )

    # ========================================================
    # Newton iterations
    # ========================================================

    print("=" * 65)
    print("Sequential Newton–GMRES Solver")
    print("=" * 65)

    print(f"Number of classes: {J}")
    print(f"Spatial cells:     {Nx}")
    print(f"Temporal steps:    {Nt}")
    print(f"Unknowns:          {expected_size}")
    print(f"Newton tolerance:  {atol:.2e}")
    print(f"GMRES tolerance:   {rtol:.2e}")

    for k in range(max_iter):

        # ----------------------------------------------------
        # Step 1: Evaluate nonlinear residual
        # ----------------------------------------------------

        Fw = np.asarray(F(w), dtype=float)

        if Fw.shape != w.shape:
            raise ValueError(
                "Residual has an unexpected shape."
            )

        if not np.all(np.isfinite(Fw)):
            raise RuntimeError(
                "Nonlinear residual contains NaN or infinity."
            )

        residual_norm = np.linalg.norm(Fw)

        print(
            f"Newton iteration {k:3d} | "
            f"Residual = {residual_norm:.8e}"
        )

        # ----------------------------------------------------
        # Step 2: Check nonlinear convergence
        # ----------------------------------------------------

        if residual_norm < atol:

            print("\nNewton–GMRES converged.")
            print(
                f"Final residual: {residual_norm:.8e}"
            )

            return w

        # ----------------------------------------------------
        # Step 3: Assemble exact Jacobian
        # ----------------------------------------------------

        A = Jmat(w)

        if A.shape != (
            expected_size,
            expected_size,
        ):
            raise ValueError(
                "Jacobian has an unexpected shape."
            )

        # ----------------------------------------------------
        # Step 4: Solve Newton linear system with GMRES
        # ----------------------------------------------------

        delta_w = GMRES_solver(
            A,
            -Fw,
            x0=None,
            M=M,
            rtol=rtol,
            atol=atol,
            restart=gmres_restart,
            maxiter=gmres_maxiter,
        )

        if not np.all(np.isfinite(delta_w)):
            raise RuntimeError(
                "GMRES correction contains NaN or infinity."
            )

        # ----------------------------------------------------
        # Step 5: Full Newton update
        # ----------------------------------------------------

        w = w + delta_w

    # --------------------------------------------------------
    # Final convergence check
    # --------------------------------------------------------

    final_residual = np.linalg.norm(F(w))

    if final_residual < atol:

        print("\nNewton–GMRES converged.")
        print(
            f"Final residual: {final_residual:.8e}"
        )

        return w

    raise RuntimeError(
        "Newton–GMRES did not converge within "
        f"{max_iter} iterations. "
        f"Final residual: {final_residual:.8e}"
    )
