# ⚡ Parallel Mean-Field Game Solver — PETSc

This directory contains a parallel numerical implementation for
single-class traffic flow models formulated through Mean-Field Games.

The computational framework combines:

- **PETSc / petsc4py** for nonlinear and linear algebra.
- **MPI / mpi4py** for distributed-memory parallel computing.
- **Pyccel** for compiling performance-critical numerical functions.
- **SLURM** for submitting simulations to HPC clusters.

---

## 📁 Code Organization

```text
petsc4py/
├── README.md
├── options.txt
│
└── one_class/
    ├── mfg_parallel_main.py
    ├── tools.py
    ├── batch.slurm
    ├── ReadMe.md
    │
    └── modules/
        ├── modules_lwr/
        │   └── modules.py
        ├── modules_separable/
        │   └── modules.py
        └── modules_nonseparable/
            └── modules.py
```

---

## 📐 Mathematical Models

Three single-class traffic formulations are implemented:

| Model | Source |
|:---|:---|
| LWR | [`modules/modules_lwr/modules.py`](one_class/modules/modules_lwr/modules.py) |
| Separable | [`modules/modules_separable/modules.py`](one_class/modules/modules_separable/modules.py) |
| Non-Separable | [`modules/modules_nonseparable/modules.py`](one_class/modules/modules_nonseparable/modules.py) |

Each module includes numerical routines for evaluating the nonlinear
system and constructing Jacobian entries.

The principal computational functions are:

- `compute_FF` — Nonlinear system residual.
- `compute_jacobian` — Jacobian assembly data.

---

## ⚙️ Main Components

| File | Purpose |
|:---|:---|
| [`mfg_parallel_main.py`](one_class/mfg_parallel_main.py) | Main parallel simulation script |
| [`tools.py`](one_class/tools.py) | Supporting numerical utilities |
| [`batch.slurm`](one_class/batch.slurm) | SLURM job submission script |
| `modules.py` | Model-specific numerical kernels compiled using Pyccel |

---

## 🖥️ Original HPC Configuration

The original experiments used a SLURM-managed computing environment.

The included `batch.slurm` requests:

- One compute node.
- 56 MPI tasks.
- A high-memory partition.
- A 30-hour time limit.

The original job launches the simulation using:

```bash
mpirun python mfg_parallel_main.py -snes_linesearch_type l2
```

This command is provided as a reference to the original HPC workflow.
It requires a compatible software environment and an importable,
model-specific `modules` implementation.

---

## 🔧 Pyccel Compilation

The numerical kernels are provided for three mathematical models:

- LWR.
- Separable.
- Non-Separable.

The original documentation indicates that Pyccel was used to compile
the selected `modules.py` implementation.

**Note:** The complete model-selection and compilation procedure
has not yet been verified for a clean environment.

Compilation and execution instructions will be updated after the
model-loading procedure and software dependencies have been tested.

---

# 🚀 Installation & Execution

This section documents the PETSc installation procedure, execution commands,
and solver configuration options associated with the original numerical
implementation.

The commands reflect the original research workflow and may require
adaptation to the operating system, PETSc version, and available
computational resources.

<details>
<summary><strong>📦 1. Download PETSc</strong></summary>

<br>

The original installation procedure obtains PETSc from its Git repository.

```bash
git clone -b release https://gitlab.com/petsc/petsc.git petsc
```

Enter the PETSc source directory:

```bash
cd petsc
```

**Note:** The original `release` branch reference is preserved here.
For reproducible installations, a specific compatible PETSc release
should be selected and documented.

</details>

<br>

<details>
<summary><strong>⚙️ 2. Configure & Install PETSc</strong></summary>

<br>

The original configuration enables optimized compilation and several
external numerical libraries.

### PETSc Configuration

```bash
./configure \
    --with-debugging=0 \
    --download-p4est=1 \
    --with-zlib=1 \
    --with-fortran-bindings=0 \
    --download-parmetis=1 \
    --download-metis=1 \
    --download-hdf5=1 \
    --download-hypre=1 \
    --download-scalapack \
    --download-superlu \
    --download-superlu_dist \
    --download-mumps \
    --with-petsc4py
```

The configuration includes support for numerical libraries such as:

| Library | Role |
|:---|:---|
| PETSc | Parallel numerical computing |
| MUMPS | Sparse direct linear solvers |
| METIS / ParMETIS | Graph partitioning |
| HYPRE | Parallel preconditioning |
| SuperLU / SuperLU_DIST | Sparse linear system solvers |
| ScaLAPACK | Distributed linear algebra |
| HDF5 | Scientific data storage |
| p4est | Parallel mesh management |

### Build PETSc

The original build command is:

```bash
make PETSC_DIR=/path/to/petsc PETSC_ARCH=arch-linux-c-opt all
```

Replace `/path/to/petsc` with the actual PETSc installation directory.

The value of `PETSC_ARCH` must correspond to the architecture
configured during installation.

### Python Bindings

The original instructions also include:

```bash
python3 -m pip install --user -e .
```

**Important:** This command was part of the historical installation
procedure. Its correct execution directory and compatibility with the
selected PETSc/petsc4py version must be verified before use.

</details>

<br>

<details>
<summary><strong>🔧 3. Compile Numerical Modules with Pyccel</strong></summary>

<br>

The implementation provides three model-specific numerical modules:

| Mathematical Model | Source Directory |
|:---|:---|
| LWR | `one_class/modules/modules_lwr/` |
| Separable | `one_class/modules/modules_separable/` |
| Non-Separable | `one_class/modules/modules_nonseparable/` |

Each directory contains a `modules.py` file implementing
model-specific numerical functions.

The original compilation command is:

```bash
pyccel modules.py
```

Pyccel is used to compile performance-critical numerical routines.

The main script requires an importable `modules` implementation:

```python
from modules import compute_jacobian, compute_FF
```

**Note:** The exact procedure for selecting, compiling, and exposing
a particular model-specific module to the main script remains to be
verified for a clean installation.

</details>

<br>

<details>
<summary><strong>▶️ 4. Run the Parallel Simulation</strong></summary>

<br>

### Original Documented Command

The historical README specified:

```bash
mpirun -n 2 python mfg_parallel_petsc_pyccel.py -pc_factor_mat_solver_type mumps
```

This command is preserved for reference.

However, the current repository contains the main script:

```text
one_class/mfg_parallel_main.py
```

The filename used in the original documentation differs from the
current source file.

### Current Source Entry Point

The included SLURM script launches:

```bash
mpirun python mfg_parallel_main.py -snes_linesearch_type l2
```

This is the execution command used in the repository's
`one_class/batch.slurm` file.

The program requires:

- An appropriate PETSc and petsc4py installation.
- MPI and mpi4py.
- A compatible model-specific numerical module.
- Access to the required numerical libraries.

The execution procedure must be tested in a compatible environment
before being treated as a verified reproduction command.

</details>

<br>

<details>
<summary><strong>🖥️ 5. HPC Execution with SLURM</strong></summary>

<br>

The repository includes a SLURM submission script:

[`one_class/batch.slurm`](one_class/batch.slurm)

The original configuration uses:

| Parameter | Configuration |
|:---|:---|
| Partition | `himem` |
| Quality of service | `himem-cpu` |
| Nodes | 1 |
| MPI tasks | 56 |
| Memory | All available memory on the allocated node |
| Time limit | 30 hours |
| Resource allocation | Exclusive node |

The original submission command is:

```bash
sbatch batch.slurm
```

This command must be executed from a suitable directory on
a SLURM-managed HPC system.

The script loads environment-specific modules, including
MUMPS, Python, OpenMPI, and compiler tools.

**Note:** Partition names, available libraries, and resource limits
are cluster-dependent. The provided configuration reflects
the original computing environment.

</details>

<br>

<details>
<summary><strong>🛠️ 6. Optional PETSc Solver Options</strong></summary>

<br>

PETSc provides runtime options for controlling nonlinear solvers,
linear solvers, convergence monitoring, and error handling.

The following options were documented in the original implementation.

| Option | Description |
|:---|:---|
| `-snes_linesearch_type l2` | Use an L2-norm-based nonlinear line search |
| `-snes_lag_jacobian -2` | Reuse the Jacobian according to PETSc's lagging configuration |
| `-ksp_rmonitor` | Residual monitoring option from the original documentation |
| `-snes_monitor` | Display nonlinear solver convergence |
| `-snes_converged_reason` | Display the SNES convergence or divergence reason |
| `-ksp_converged_reason` | Display the KSP convergence or divergence reason |
| `-ksp_error_if_not_converged` | Raise an error when the linear solver does not converge |

### Example: Monitor Nonlinear Convergence

```bash
mpirun -n 2 python mfg_parallel_main.py \
    -snes_monitor \
    -snes_converged_reason
```

### Example: Monitor Linear Convergence

```bash
mpirun -n 2 python mfg_parallel_main.py \
    -ksp_monitor \
    -ksp_converged_reason
```

### Example: MUMPS Direct Solver

```bash
mpirun -n 2 python mfg_parallel_main.py \
    -pc_factor_mat_solver_type mumps
```

These examples demonstrate PETSc option syntax and assume that
the execution environment and model-specific module are correctly
configured.

Some options depend on PETSc version and solver configuration.
For example, the historical `-ksp_rmonitor` option should be checked
against the selected PETSc release.

</details>

---

## 📚 Scientific References

**Research paper:**  
[Computational investigations of a multi-class traffic flow model:
mean-field and microscopic dynamics](https://doi.org/10.1016/j.trb.2025.103196)

**PhD thesis:**  
[Chapter II — Numerical methods and computational investigations](https://theses.hal.science/tel-05806256/document)

---

[⬅ Back to Source Code Documentation](../README.md)
