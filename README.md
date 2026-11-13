<div align="center">

# Multi-Class Traffic Flow Modeling with Mean-Field Games

This repository accompanies research on **multi-class traffic flow modeling using Nash Mean-Field Games (NMFGs)**. The project extends a single-class, single-lane game-theoretic traffic framework to heterogeneous vehicle populations, with numerical investigations focusing on **cars and trucks**. The research also investigates the ability of **mean-field equilibrium controls to provide approximate Nash strategies** for finite-player traffic games.


<br>

[![Research Paper](https://img.shields.io/badge/Research_Paper-Elsevier-0B7285?style=for-the-badge)](https://doi.org/10.1016/j.trb.2025.103196)
[![arXiv](https://img.shields.io/badge/Preprint-arXiv-B31B1B?style=for-the-badge)](https://arxiv.org/abs/2306.13543)
[![PhD Thesis](https://img.shields.io/badge/PhD_Thesis-HAL-6F42C1?style=for-the-badge)](https://theses.hal.science/tel-05806256/document)

<br>

</div>


### 📈 [Explore the Scientific Figures & Numerical Results Gallery](results/figures/README.md)

### 💻 [Explore the Source Code & Numerical Implementations](src/README.md)


---
## Mathematical Models

The macroscopic formulation describes the interactions of heterogeneous vehicle populations through a coupled system of continuity equations, Hamilton–Jacobi–Bellman equations, and optimal velocity conditions.

The multi-class numerical implementations support three cost formulations:

| Model | Description |
|:---|:---|
| **GLWR** | Generalized Lighthill–Whitham–Richards |
| **GS** | Generalized Separable |
| **GNS** | Generalized Non-Separable |

The framework considers class-dependent traffic densities, velocity constraints, and congestion costs.

### Initial Traffic Configurations

The numerical investigations presented in the associated research consider three spatial arrangements of cars and trucks:

| Configuration | Description |
|:---:|:---|
| **CT — Cars–Trucks** | Cars initially positioned in front of trucks |
| **TC — Trucks–Cars** | Trucks initially positioned in front of cars |
| **TCT — Trucks–Cars–Trucks** | Trucks and cars arranged in successive groups |

The simulations examine density evolution, class-dependent velocities, and interactions between vehicle populations under different initial conditions.

### Mean-Field and Microscopic Dynamics

In addition to the macroscopic PDE system, the associated research investigates finite-player traffic games and compares their dynamics with mean-field solutions.

The numerical investigations provide computational evidence for the approximation of finite-player Nash equilibria using mean-field equilibrium controls.

The published model considers single-lane traffic and does not explicitly impose microscopic collision-avoidance constraints.


---

## Quick start

The following commands should be executed from the repository root.

### Single-class example

Requires Python, NumPy, and SciPy.

```bash
python3 examples/one_class_demo/run_demo.py
```

An interactive version is available in the [single-class LWR notebook](notebooks/one_class_LWR.ipynb).

The notebook can also be opened through [Binder](https://mybinder.org/v2/gh/amalmach/MultiClass-MFG-Traffic/main?labpath=notebooks%2Fone_class_LWR.ipynb).

### Sequential multi-class solver

Requires Python, NumPy, and SciPy.

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 \
    --model GLWR \
    --nx 5 \
    --nt 8 \
    --max-grids 1 \
    --output sequential_J3_GLWR.npz
```

The `--model` argument accepts `GLWR`, `GS`, or `GNS`, and `--J` specifies the number of vehicle classes.

For solver parameters and numerical options, see the [Newton–Krylov documentation](src/newton_krylov/README.md).

### Parallel multi-class solver

Requires a compatible installation of PETSc, MPI, `petsc4py`, and `mpi4py`, with MUMPS support for the command below.

```bash
mpirun -np 2 python3 src/petsc4py/multi_class/main.py \
    --J 3 \
    --model GLWR \
    --nx 5 \
    --nt 8 \
    --output petsc_J3_GLWR_MPI2.npz \
    -ksp_type preonly \
    -pc_type lu \
    -pc_factor_mat_solver_type mumps
```

The parallel implementation uses PETSc SNES for nonlinear solution and supports the GLWR, GS, and GNS formulations.

Installation instructions and additional solver options are provided in the [PETSc/MPI documentation](src/petsc4py/README.md).

---
## References

### Journal Article

**A. Machtalay, A. Habbal, A. Ratnani, I. Kissami**

*Computational investigations of a multi-class traffic flow model: Mean-field and microscopic dynamics.*

**Transportation Research Part B: Methodological**, Volume 195, 103196 (2025).

[![DOI](https://img.shields.io/badge/DOI-10.1016%2Fj.trb.2025.103196-blue)](https://doi.org/10.1016/j.trb.2025.103196)

[![arXiv](https://img.shields.io/badge/arXiv-2306.13543-B31B1B)](https://arxiv.org/abs/2306.13543)

### PhD Thesis — 2026

**Amal Machtalay**

*Micro–macro modeling and scalable numerical methods for high-dimensional mean-field and control systems: structure-exploiting solvers and low-rank techniques.*

**Université Côte d’Azur & Mohammed VI Polytechnic University**, 2026.

**Relevant material:** Chapter II — Multi-class traffic modeling and computational investigations and Appendix D on the numerical implementations.

[![Thesis](https://img.shields.io/badge/Read_PhD_Thesis-HAL-6F42C1)](https://theses.hal.science/tel-05806256/document)

---

## License

This repository is distributed under the [GNU General Public License, version 3](LICENSE).

The [original research-code release](https://github.com/amalmach/MultiClass-MFG-Traffic/releases/tag/v1.0.0-original) is available for reference.
