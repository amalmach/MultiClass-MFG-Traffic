<div align="center">

# Parallel Traffic Mean-Field Game Solvers — PETSc / MPI

This directory contains parallel numerical implementations of traffic Mean-Field Game (MFG) models using PETSc and MPI.

The implementations cover single-class traffic models and general multi-class systems with $J$ interacting vehicle populations.

The numerical framework combines finite-difference discretization, Newton-type nonlinear solvers, sparse Jacobian assembly, and parallel linear algebra.

| Directory | Description |
|:---|:---|
| [`one_class/`](one_class/) | Single-class PETSc/MPI implementation |
| [`multi_class/`](multi_class/) | General $J$-class PETSc/MPI solver |

</div>


## General Multi-Class Solver

**Directory:** [`multi_class/`](multi_class/)

### Numerical Method

The parallel solver uses:

- **PETSc SNES** for nonlinear Newton iterations.
- **PETSc KSP** for linear system solution.
- **PETSc PC** for preconditioning and sparse factorization.
- **MPI/mpi4py** for distributed vectors and matrices.
- **Analytical sparse Jacobians** for the nonlinear system.
- **MUMPS** for sparse direct factorization in the documented execution examples.

The general multi-class implementation shares its mathematical functions with the sequential Newton–Krylov solver located in [`../newton_krylov/multi_class/`](../newton_krylov/multi_class/).

The current implementation distributes PETSc vectors and matrices across MPI processes. Residual and Jacobian evaluations are performed on the complete system before extracting locally owned rows. Consequently, this implementation provides distributed linear algebra but does not yet use fully distributed nonlinear assembly.

## Source Files

| File | Description |
|:---|:---|
| [`main.py`](multi_class/main.py) | PETSc/MPI simulation driver |
| [`parallel_functions.py`](multi_class/parallel_functions.py) | Residual and Jacobian evaluation interfaces |
| [`check_environment.py`](multi_class/check_environment.py) | PETSc/MPI environment verification |
| [`requirements-hpc.txt`](multi_class/requirements-hpc.txt) | Software dependency notes |

The shared numerical routines provide the model parameters, initial conditions, cost functions, index mappings, nonlinear residual, and analytical Jacobian.

---

## Installation

### Requirements

The general multi-class solver requires:

- Python 3;
- NumPy;
- SciPy;
- MPI;
- mpi4py;
- PETSc;
- petsc4py.

MUMPS support is required for the sparse direct solver configuration used in the examples below.

### Conda Installation

On Linux, the required packages can be installed from conda-forge:

```bash
conda create -n traffic-petsc \
    -c conda-forge --override-channels \
    python=3.11 \
    numpy scipy \
    mpi4py openmpi \
    petsc petsc4py \
    -y
```

Activate the environment:

```bash
conda activate traffic-petsc
```

The PETSc installation must include the sparse solver packages required by the selected linear solver configuration.

### Verify the Environment

From the repository root, execute:

```bash
python3 src/petsc4py/multi_class/check_environment.py
```

To verify MPI execution with two processes:

```bash
mpirun -np 2 python3 src/petsc4py/multi_class/check_environment.py
```

The script reports the Python, MPI, and PETSc versions and verifies that the required PETSc interfaces are available.

This check does not verify MUMPS availability; that is established by running a solver with the MUMPS configuration.

---

## Running the Multi-Class Solver

All commands below should be executed from the repository root.

### GLWR Model

```bash
mpirun -np 2 python3 src/petsc4py/multi_class/main.py \
    --J 3 \
    --model GLWR \
    --nx 5 \
    --nt 8 \
    --output petsc_J3_GLWR.npz \
    -ksp_type preonly \
    -pc_type lu \
    -pc_factor_mat_solver_type mumps
```

### GS Model

```bash
mpirun -np 2 python3 src/petsc4py/multi_class/main.py \
    --J 3 \
    --model GS \
    --nx 5 \
    --nt 8 \
    --output petsc_J3_GS.npz \
    -ksp_type preonly \
    -pc_type lu \
    -pc_factor_mat_solver_type mumps
```

### GNS Model

```bash
mpirun -np 2 python3 src/petsc4py/multi_class/main.py \
    --J 3 \
    --model GNS \
    --nx 5 \
    --nt 8 \
    --output petsc_J3_GNS.npz \
    -ksp_type preonly \
    -pc_type lu \
    -pc_factor_mat_solver_type mumps
```

The number of MPI processes is specified using `-np`.

For example, to run GLWR with four processes, replace `-np 2` with `-np 4`.

Depending on the model, grid size, and number of processes, additional MUMPS workspace may be required. For example:

```bash
-mat_mumps_icntl_14 200
```

This option increases the MUMPS workspace allocation parameter.

### Command-Line Options

| Option | Description | Default |
|:---|:---|:---|
| `--J` | Number of vehicle classes | `2` |
| `--model` | Traffic model: `GLWR`, `GS`, or `GNS` | `GLWR` |
| `--nx` | Number of spatial cells | `5` |
| `--nt` | Minimum number of time steps | `8` |
| `--tol` | Nonlinear solver tolerance | `1e-8` |
| `--max-it` | Maximum nonlinear iterations | `50` |
| `--output` | Output filename in `.npz` format | None |

Available options can be displayed with:

```bash
python3 src/petsc4py/multi_class/main.py --help
```

Additional PETSc options can be supplied directly on the command line.

### PETSc Solver Options

The following options are useful for controlling and monitoring the numerical solver.

| Option | Description |
|:---|:---|
| `-snes_monitor` | Display nonlinear residuals |
| `-snes_converged_reason` | Display nonlinear convergence status |
| `-snes_atol` | Absolute nonlinear tolerance |
| `-snes_rtol` | Relative nonlinear tolerance |
| `-snes_max_it` | Maximum nonlinear iterations |
| `-ksp_monitor` | Display linear solver residuals |
| `-ksp_converged_reason` | Display linear solver convergence status |
| `-ksp_type preonly` | Apply the preconditioner as the linear solve |
| `-pc_type lu` | Use LU factorization |
| `-pc_factor_mat_solver_type mumps` | Select MUMPS for sparse LU factorization |

PETSc options supplied on the command line override the corresponding default solver settings.

For additional options, consult the [PETSc documentation](https://petsc.org/release/).

---

## Output Format

When `--output` is specified, the solver saves the numerical solution as a compressed NumPy archive.

The main output variables are:

| Variable | Description |
|:---|:---|
| `solution` | Complete numerical solution vector |
| `rho` | Traffic density for each class |
| `u` | Optimal velocity for each class |
| `V` | Value function for each class |
| `Q` | Traffic flux for each class |
| `x` | Spatial coordinates |
| `t` | Temporal coordinates |
| `J` | Number of vehicle classes |
| `Nx`, `Nt` | Spatial and temporal discretization sizes |
| `dt`, `dx` | Time and space steps |
| `eps` | Numerical regularization parameter |
| `model` | Selected traffic model |
| `u_max_vec` | Class-dependent maximum velocities |
| `rho_jam_vec` | Class-dependent jam densities |
| `residual_l2` | Final nonlinear residual L2 norm |
| `residual_inf` | Final nonlinear residual infinity norm |

The density array has shape

$$
(J,N_x,N_t+1).
$$

The numerical results can be loaded with:

```python
import numpy as np

with np.load("petsc_J3_GLWR.npz") as data:
    rho = data["rho"]
    u = data["u"]
    V = data["V"]
    Q = data["Q"]

print("Density shape:", rho.shape)
print("Velocity shape:", u.shape)
```

---

## Original Single-Class Implementation

**Directory:** [`one_class/`](one_class/)

The single-class implementation provides PETSc/MPI solvers for homogeneous traffic Mean-Field Game models.

It includes three model-specific numerical modules:

| Model | Source |
|:---|:---|
| LWR | [`modules/modules_lwr/modules.py`](one_class/modules/modules_lwr/modules.py) |
| Separable | [`modules/modules_separable/modules.py`](one_class/modules/modules_separable/modules.py) |
| Non-Separable | [`modules/modules_nonseparable/modules.py`](one_class/modules/modules_nonseparable/modules.py) |

### Source Files

| File | Description |
|:---|:---|
| [`mfg_parallel_main.py`](one_class/mfg_parallel_main.py) | Parallel simulation driver |
| [`tools.py`](one_class/tools.py) | Numerical utilities |
| [`batch.slurm`](one_class/batch.slurm) | SLURM submission script |
| [`ReadMe.md`](one_class/ReadMe.md) | Original installation and execution notes |

The numerical modules use Pyccel for compiling selected computational routines.

The original documentation specifies the following compilation command, executed in the directory containing the selected `modules.py`:

```bash
pyccel modules.py
```

The corresponding compiled module must be available on the Python import path used by the simulation driver.

Consult the [single-class documentation](one_class/ReadMe.md) for the original workflow.

### SLURM Execution

The repository includes a SLURM submission script for the single-class implementation.

The supplied configuration requests:

| Parameter | Value |
|:---|:---|
| Nodes | 1 |
| MPI processes | 56 |
| Partition | `himem` |
| Quality of service | `himem-cpu` |
| Time limit | 30 hours |
| Node allocation | Exclusive |

The script launches the simulation using:

```bash
mpirun python mfg_parallel_main.py -snes_linesearch_type l2
```

Submit the job from the directory containing `batch.slurm`:

```bash
sbatch batch.slurm
```

The partition, module names, and resource settings depend on the HPC system and may need to be adapted.

---

## References

1. A. Machtalay, A. Habbal, A. Ratnani, and I. Kissami, “Computational investigations of a multi-class traffic flow model: Mean-field and microscopic dynamics,” *Transportation Research Part B: Methodological*, **195**, 103196 (2025). [DOI](https://doi.org/10.1016/j.trb.2025.103196).

2. A. Machtalay, *Micro–macro modeling and scalable numerical methods for high-dimensional mean-field and control systems: Structure-exploiting solvers and low-rank techniques*, PhD thesis (2026). [Full text](https://theses.hal.science/tel-05806256/document).

The sequential and PETSc/MPI numerical methods are described in Appendix D of the thesis.

---

[← Back to source-code documentation](../README.md)
