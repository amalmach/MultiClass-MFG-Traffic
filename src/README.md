<div align="center">

# 💻 Source Code & Numerical Implementations

This directory contains numerical implementations for single-class and multi-class traffic flow models formulated as Nash Mean-Field Games (NMFGs).

The computational methods combine finite-difference discretizations, Newton–Krylov algorithms, and PETSc/MPI parallel solvers.

</div>

---

## Code Organization

| Directory | Description |
|:---|:---|
| [`newton_krylov/`](newton_krylov/README.md) | Sequential Newton–Krylov solvers for single-class, two-class, and general multi-class traffic models |
| [`petsc4py/`](petsc4py/README.md) | PETSc/MPI implementations for single-class and general multi-class traffic models |

### Newton–Krylov Implementations

The [`newton_krylov/`](newton_krylov/README.md) directory contains:

| Directory | Description |
|:---|:---|
| [`one_class/`](newton_krylov/one_class/) | Single-class traffic models |
| [`two_class/`](newton_krylov/two_class/) | Two-class traffic models |
| [`multi_class/`](newton_krylov/multi_class/) | General $J$-class traffic models |

The numerical solver combines Newton iterations with Krylov subspace methods and supports coarse-to-fine grid refinement.

### PETSc/MPI Implementations

The [`petsc4py/`](petsc4py/README.md) directory contains:

| Directory | Description |
|:---|:---|
| [`one_class/`](petsc4py/one_class/) | Single-class PETSc/MPI implementation |
| [`multi_class/`](petsc4py/multi_class/) | General $J$-class PETSc/MPI implementation |

The general multi-class solver uses PETSc SNES for nonlinear solution and supports the GLWR, GS, and GNS models.

The single-class implementation includes the original HPC workflow with Pyccel and SLURM support.

---
## Running the Solvers

The following examples should be executed from the repository root.

### Sequential Multi-Class Solver

Requires Python, NumPy, and SciPy.

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 --model GLWR --nx 5 --nt 8 \
    --max-grids 1 \
    --output sequential_J3_GLWR.npz
```

### Parallel Multi-Class Solver

Requires PETSc, MPI, `petsc4py`, and `mpi4py`, with MUMPS support.

```bash
mpirun -np 2 python3 src/petsc4py/multi_class/main.py \
    --J 3 --model GLWR --nx 5 --nt 8 \
    --output petsc_J3_GLWR_MPI2.npz \
    -ksp_type preonly \
    -pc_type lu \
    -pc_factor_mat_solver_type mumps
```

For installation requirements, model parameters, and additional execution options, consult the corresponding solver documentation:

- [Newton–Krylov documentation](newton_krylov/README.md)
- [PETSc/MPI documentation](petsc4py/README.md)


---

## Scientific References

The numerical methods and traffic models are described in:

1. A. Machtalay, A. Habbal, A. Ratnani, and I. Kissami, *Computational investigations of a multi-class traffic flow model: Mean-field and microscopic dynamics*, Transportation Research Part B: Methodological, **195**, 103196 (2025). [DOI](https://doi.org/10.1016/j.trb.2025.103196).

2. A. Machtalay, *Micro–macro modeling and scalable numerical methods for high-dimensional mean-field and control systems: Structure-exploiting solvers and low-rank techniques*, PhD thesis (2026). [Full text](https://theses.hal.science/tel-05806256/document).


---

<div align="center">

[⬅ Back to Main Repository](../README.md)

</div>
