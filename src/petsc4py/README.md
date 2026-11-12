# Parallel Traffic Mean-Field Game Solvers — PETSc / MPI

This directory contains PETSc-based implementations of traffic **Mean-Field Game (MFG)** models. It preserves the original **single-class HPC implementation** and adds a **general $J$-class PETSc/MPI reference solver** based on the parallel method described in Appendix D.2 of the PhD thesis.


## Contents

The `one_class/` model-specific sources are documented under:

- `one_class/modules/modules_lwr/modules.py` — LWR model.
- `one_class/modules/modules_separable/modules.py` — separable model.
- `one_class/modules/modules_nonseparable/modules.py` — non-separable model.

These paths are retained from the original documentation; verify the modules present in a particular checkout before attempting to compile or run the legacy driver.

## 1. General $J$-class PETSc/MPI solver (`multi_class/`)

### 1.1 Models

The general implementation supports the same three cost models as the sequential solver:

| Model | Name | Main property |
| --- | --- | --- |
| `GLWR` | Generalized Lighthill–Whitham–Richards | Density-dependent desired velocity |
| `GS` | Generalized Separable | Separable density-dependent running cost |
| `GNS` | Generalized Non-Separable | Density-dependent optimal velocity |

For classes $j=1,\ldots,J$, the coupled numerical system contains conservation, optimality, and Hamilton–Jacobi equations with their initial and terminal conditions. With $N_x$ spatial cells and $N_t$ time steps, the total number of unknowns is $N=(3N_t+2)JN_x.$

For the GS model, the bounded optimal control is $u_j^*=\mathrm{clip}\left(u_{\max,j}(1-u_{\max,j}p_j),\,0,\,u_{\max,j}\right).$

For the GNS model, it is $u_j^*=\mathrm{clip}\left(u_{\max,j}\bigl(1-S(\boldsymbol{\rho})-u_{\max,j}p_j\bigr),\,0,\,u_{\max,j}\right),$

where $S(\boldsymbol{\rho})$ is the model's normalized aggregate-density term. The precise discrete formulas, Jacobian entries, and indexing conventions are shared with the sequential implementation.

### 1.2 Shared numerical code

The parallel driver imports the mathematical implementation from [`../newton_krylov/multi_class/`](../newton_krylov/multi_class/), including:

| Shared module | Role |
| --- | --- |
| `inputs.py` | Physical parameters, initial conditions, viscosity levels |
| `cost_functions.py` | GLWR, GS, and GNS costs and derivatives |
| `indx_funcs.py` | Global unknown indexing and solution reconstruction |
| `newton_func.py` | Nonlinear MFG residual |
| `jacobian_exact.py` | Sparse analytical Jacobian |
| `multi_grid.py` | Grid-to-grid interpolation (used by the helper layer) |

**Do not run `multi_class/main.py` outside this repository structure without adapting the shared-module import paths.** The present parallel driver solves one space–time grid; the sequential driver additionally supports multilevel grid refinement.

### 1.3 PETSc/MPI architecture

- **PETSc SNES** manages nonlinear Newton iterations and line search.
- **PETSc KSP / PC** manages the Newton linear systems.
- **MPI / mpi4py** distributes PETSc solution vectors and sparse matrix rows.
- `parallel_functions.py` selects the residual and analytical Jacobian rows owned by each MPI rank.
- **MUMPS** provides sparse direct LU factorization in the locally verified runs.

**Current implementation limit:** Each rank first reconstructs the full global solution, evaluates the complete SciPy residual/Jacobian, and then extracts its owned rows for PETSc. Thus, PETSc's vector, matrix, and factorization operations are distributed, but nonlinear-system evaluation is *replicated*. This is a **correctness-oriented parallel reference implementation**, not a demonstrated scalable distributed-assembly algorithm. No speedup claims should be inferred from the small-grid timings below.

### 1.4 Correspondence with PhD thesis Appendix D.2

| Thesis listing | Subject | Repository implementation |
| --- | --- | --- |
| **D.15** | Input and numerical wrappers | `multi_class/parallel_functions.py` |
| **D.16** | PETSc and MPI imports/initialization | `multi_class/main.py` |
| **D.17** | PETSc/MPI nonlinear solver | `multi_class/main.py` |

The files **adapt**, rather than reproduce verbatim, the appendix listings. In particular, they use PETSc ownership ranges and the shared general $J$-class numerical kernels; the initial version is single-grid and uses replicated residual/Jacobian evaluation. The thesis additionally describes the original parallel workflow and cluster-specific solver choices.

## 2. Install and test locally (Ubuntu / Conda)

A consistent PETSc/MPI installation is essential. From the repository root:

```bash
conda create -n traffic-petsc -c conda-forge --override-channels \
    python=3.11 numpy scipy mpi4py openmpi petsc petsc4py -y
conda activate traffic-petsc
```

Check your active Python and MPI executables:

```bash
which python3
which mpirun
python3 -c "from mpi4py import MPI; from petsc4py import PETSc; print('PETSc:', PETSc.Sys.getVersion()); print('MPI size:', MPI.COMM_WORLD.Get_size())"
mpirun -np 2 python3 src/petsc4py/multi_class/check_environment.py
```

### 2.1 Run the multi-class solver

Run the commands below **from the repository root**, in the `traffic-petsc` environment. To test GLWR using two MPI processes:

```bash
mpirun -np 2 python3 src/petsc4py/multi_class/main.py \
    --J 3 --model GLWR --nx 5 --nt 8 \
    --tol 1e-8 --max-it 50 \
    --output petsc_J3_GLWR_MPI2.npz \
    -ksp_type preonly -pc_type lu \
    -pc_factor_mat_solver_type mumps \
    -ksp_converged_reason -snes_converged_reason
```

To run GS, change `--model GLWR` to `--model GS` and use a distinct output filename. For GNS with four ranks, the local test needed additional MUMPS workspace:

```bash
mpirun -np 4 python3 src/petsc4py/multi_class/main.py \
    --J 3 --model GNS --nx 5 --nt 8 \
    --tol 1e-8 --max-it 50 \
    --output petsc_J3_GNS_MPI4.npz \
    -ksp_type preonly -pc_type lu \
    -pc_factor_mat_solver_type mumps \
    -mat_mumps_icntl_14 200 \
    -ksp_converged_reason -snes_converged_reason
```

### 2.2 Output format

When `--output` is set, the driver writes a compressed `.npz` file containing the global solution and reconstructed fields (`rho`, `u`, `V`, `Q`), grid coordinates, model parameters, and nonlinear residual norms. Reconstructed density storage is

```text
rho[class, space, time]  # shape (J, Nx, Nt+1)
```

For each class, discrete mass at time step $n$ is $M_j^n=\Delta x\sum_{k=1}^{N_x}\rho_{j,k}^n.$

For the periodic conservation discretization, validation checks whether $M_j^n$ stays constant to numerical precision.

The repository's `.gitignore` excludes `*.npz` simulation outputs so that generated results do not accidentally enter version control.


## 3. Original single-class implementation (`one_class/`)

The original PETSc/Pyccel code is preserved under [`one_class/`](one_class/). It includes:

| File | Purpose |
| --- | --- |
| [`mfg_parallel_main.py`](one_class/mfg_parallel_main.py) | Original parallel driver |
| [`tools.py`](one_class/tools.py) | Original numerical utilities |
| [`batch.slurm`](one_class/batch.slurm) | Original SLURM job configuration |
| [`ReadMe.md`](one_class/ReadMe.md) | Original single-class notes |
| `modules/.../modules.py` | Model-specific residual/Jacobian kernels described in original documentation |

The original documented numerical kernels used **Pyccel**, with a compilation command such as:

```bash
pyccel modules.py
```

The main legacy driver expects an importable model-specific `modules` implementation (`compute_FF`, `compute_jacobian`). **Selection, compilation, and import behavior have not been revalidated for a clean local install.** Consult [`one_class/ReadMe.md`](one_class/ReadMe.md) and the corresponding model sources for that workflow.

### 3.1 Historical SLURM/HPC workflow

The original `batch.slurm` configuration is documented as requesting one exclusive high-memory node, 56 MPI tasks, and a 30-hour time limit, with partition `himem` and QoS `himem-cpu`. Those settings were specific to the original cluster environment and must not be assumed valid elsewhere.

The documented launch command was:

```bash
mpirun python mfg_parallel_main.py -snes_linesearch_type l2
```

The batch script is intended for a compatible SLURM allocation, not a laptop shell. Its software environment includes cluster-specific compiler, Python, MPI, and solver modules. The original documentation also mentioned the historical script name `mfg_parallel_petsc_pyccel.py`; the source entry point in the present file listing is `mfg_parallel_main.py`.

### 3.2 Historical PETSc source-build configuration

The existing README documented a PETSc source build, including:

```bash
git clone -b release https://gitlab.com/petsc/petsc.git petsc
cd petsc
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

Historical build command:

```bash
make PETSC_DIR=/path/to/petsc PETSC_ARCH=arch-linux-c-opt all
```

These commands are retained for provenance. They are **not** the verified installation route for the new multi-class solver. PETSc configuration options and `PETSC_ARCH` depend on the selected release and system. For local reproduction of the new code, use the Conda instructions in Section 2.

### 3.3 Useful PETSc runtime options

| Option | Purpose |
| --- | --- |
| `-snes_monitor` | Show nonlinear convergence |
| `-snes_converged_reason` | Show nonlinear stopping reason |
| `-snes_linesearch_type l2` | Use PETSc's L2 nonlinear line search |
| `-ksp_monitor` | Show linear solver convergence |
| `-ksp_converged_reason` | Show linear stopping reason |
| `-ksp_error_if_not_converged` | Raise an error when KSP fails |
| `-ksp_type preonly -pc_type lu` | Direct LU preconditioner/solve configuration |
| `-pc_factor_mat_solver_type mumps` | Select MUMPS when supported by PETSc |
| `-pc_factor_mat_solver_type superlu_dist` | Select SuperLU_DIST when supported by PETSc |

## 5. References

1. **A. Machtalay, A. Habbal, A. Ratnani, and I. Kissami (2025).** “Computational investigations of a multi-class traffic flow model: mean-field and microscopic dynamics.” *Transportation Research Part B: Methodological*, **195**, 103196. [DOI](https://doi.org/10.1016/j.trb.2025.103196).
2. **A. Machtalay (2026).** *Micro–macro modeling and scalable numerical methods for high-dimensional mean-field and control systems: structure-exploiting solvers and low-rank techniques.* PhD thesis. See **Appendix D.1** (sequential Newton–GMRES) and **Appendix D.2** (parallel PETSc/MPI, Listings D.15–D.17). [Thesis PDF](https://theses.hal.science/tel-05806256/document).

---

[← Back to source-code documentation](../README.md)
