# Single-Class PETSc/MPI Traffic Solver

This directory contains the original parallel implementation of single-class traffic Mean-Field Game models.

The solver uses PETSc for nonlinear and linear algebra, MPI for distributed-memory execution, and Pyccel for compiling model-specific numerical routines.

## Source Files

| File | Description |
|:---|:---|
| `mfg_parallel_main.py` | PETSc/MPI simulation driver |
| `tools.py` | Numerical utilities and grid interpolation |
| `batch.slurm` | SLURM job submission script |
| `modules/modules_lwr/modules.py` | LWR numerical model |
| `modules/modules_separable/modules.py` | Separable traffic model |
| `modules/modules_nonseparable/modules.py` | Non-Separable traffic model |

## Requirements

The implementation requires:

- Python, NumPy, and SciPy;
- PETSc and petsc4py;
- MPI and mpi4py;
- Pyccel and its compilation dependencies;
- A compatible PETSc sparse direct solver.

SLURM is required for execution using the supplied batch script.

## Model Selection and Compilation

The numerical driver imports the model-specific functions using:

```python
from modules import compute_jacobian, compute_FF
```

The model implementation must therefore be compiled and made importable as `modules` before executing the simulation.

The three available model sources are located in:

```text
modules/modules_lwr/modules.py
modules/modules_separable/modules.py
modules/modules_nonseparable/modules.py
```

Compile the selected model using Pyccel:

```bash
pyccel modules.py
```

Run this command from the directory containing the selected source file.

The generated module must be accessible to `mfg_parallel_main.py`. The exact compilation and module-loading procedure depends on the Pyccel version and Python environment.

## Running the Solver

The main simulation driver is:

```text
mfg_parallel_main.py
```

Once the selected numerical module is available on the Python import path, the solver can be launched using MPI:

```bash
mpirun -np 2 python3 mfg_parallel_main.py \
    -snes_linesearch_type l2
```

This command is intended to be executed from the `one_class/` directory.

The numerical parameters and grid-refinement settings are defined in `mfg_parallel_main.py`.

The solver saves the results of successive grid levels as NumPy archives:

```text
data_solutions_grid1.npz
data_solutions_grid2.npz
...
```

Each archive contains the grid parameters and the computed numerical solution.

## SLURM Execution

The supplied `batch.slurm` script defines the original HPC configuration.

| Parameter | Value |
|:---|:---|
| Partition | `himem` |
| Quality of service | `himem-cpu` |
| Nodes | 1 |
| MPI tasks | 56 |
| Memory | All memory available on the allocated node |
| Time limit | 30 hours |
| Node allocation | Exclusive |

The script loads the required software modules and launches:

```bash
mpirun python mfg_parallel_main.py -snes_linesearch_type l2
```

Submit the job from the `one_class/` directory:

```bash
sbatch batch.slurm
```

The module names, partition, resource allocation, and library versions must be adapted to the target HPC environment.

## References

1. A. Machtalay, A. Habbal, A. Ratnani, and I. Kissami, “Computational investigations of a multi-class traffic flow model: Mean-field and microscopic dynamics,” *Transportation Research Part B: Methodological*, **195**, 103196 (2025). [DOI](https://doi.org/10.1016/j.trb.2025.103196).

2. A. Machtalay, *Micro–macro modeling and scalable numerical methods for high-dimensional mean-field and control systems: Structure-exploiting solvers and low-rank techniques*, PhD thesis (2026). [Full text](https://theses.hal.science/tel-05806256/document).

---

[Back to PETSc/MPI documentation](../README.md)
