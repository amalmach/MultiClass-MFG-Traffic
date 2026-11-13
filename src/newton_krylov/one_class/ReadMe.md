# Single-Class Newton–Krylov Solver

This directory contains the original sequential numerical implementation of single-class traffic Mean-Field Game models.

The implementation uses finite-difference discretization, Newton iterations, Krylov subspace methods, and sparse preconditioning.

## Numerical Components

| File | Description |
|:---|:---|
| `indx_funcs.py` | Index mappings and solution reconstruction |
| `jacobian_exact.py` | Jacobian assembly |
| `multi_grid.py` | Grid refinement and interpolation |
| `newton_func.py` | Nonlinear residual evaluation |
| `precond.py` | Preconditioning routines |
| `inputs.py` | Numerical parameters and initial conditions |
| `gmres_solver.py` | Newton–GMRES solver |

The modules provide the numerical components of the single-class implementation.

For a standalone example, see the [single-class LWR demonstration](../../../examples/one_class_demo/).

## References

The mathematical formulation and numerical methods are described in the [research article](https://doi.org/10.1016/j.trb.2025.103196) and [PhD thesis](https://theses.hal.science/tel-05806256/document).

[Back to Newton–Krylov documentation](../README.md)
