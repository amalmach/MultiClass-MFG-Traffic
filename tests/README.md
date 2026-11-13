# Numerical Tests

This directory contains automated tests for the sequential Newton–GMRES and parallel PETSc/MPI implementations of the multi-class traffic Mean-Field Game models.

The tests use `pytest` and cover the GLWR, GS, and GNS formulations.

## Test Organization

| File | Description |
|:---|:---|
| `test_indexing.py` | Index mappings and solution reconstruction |
| `test_cost_functions.py` | Cost functions, analytical derivatives, and velocity constraints |
| `test_jacobian.py` | Analytical sparse Jacobian verification using finite differences |
| `test_mass_conservation.py` | Class-wise discrete mass conservation |
| `test_sequential_solver.py` | Sequential Newton–GMRES solution consistency |
| `test_petsc_solver.py` | PETSc/MPI solver integration tests |
| `test_solver_consistency.py` | Comparison between sequential and PETSc solutions |
| `test_mpi_consistency.py` | Consistency across 1, 2, and 4 MPI processes |

## Requirements

The unit tests require Python, NumPy, SciPy, and pytest.

The PETSc integration tests additionally require PETSc, petsc4py, MPI, mpi4py, and a PETSc installation with MUMPS support.

## Running the Tests

Execute the following commands from the repository root.

### Complete Test Suite

```bash
python3 -m pytest tests/ -v
```

### Mathematical Unit Tests

```bash
python3 -m pytest \
    tests/test_indexing.py \
    tests/test_cost_functions.py \
    tests/test_jacobian.py -v
```

### Sequential Solver Tests

```bash
python3 -m pytest \
    tests/test_mass_conservation.py \
    tests/test_sequential_solver.py -v
```

### PETSc/MPI Tests

```bash
python3 -m pytest \
    tests/test_petsc_solver.py \
    tests/test_solver_consistency.py \
    tests/test_mpi_consistency.py -v
```

The PETSc integration tests launch MPI processes internally. Run pytest normally rather than through `mpirun`.

---

[Back to the main repository](../README.md)
