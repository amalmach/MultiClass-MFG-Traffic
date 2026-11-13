<div align="center">

# Multi-Class Traffic Flow Modeling with Mean-Field Games

This repository accompanies research on **multi-class traffic flow modeling using Nash Mean-Field Games (NMFGs)**. The project extends a single-class, single-lane game-theoretic traffic framework to heterogeneous vehicle populations, with numerical investigations focusing on **cars and trucks**. The research also investigates the ability of **mean-field equilibrium controls to provide approximate Nash strategies** for finite-player traffic games.

> **Model scope:** The published model considers a single-lane traffic setting and does not explicitly impose microscopic collision-avoidance constraints. Multi-lane traffic and collision avoidance are possible future extensions.

<br>

[![Research Paper](https://img.shields.io/badge/Research_Paper-Elsevier-0B7285?style=for-the-badge)](https://doi.org/10.1016/j.trb.2025.103196)
[![arXiv](https://img.shields.io/badge/Preprint-arXiv-B31B1B?style=for-the-badge)](https://arxiv.org/abs/2306.13543)
[![PhD Thesis](https://img.shields.io/badge/PhD_Thesis-HAL-6F42C1?style=for-the-badge)](https://theses.hal.science/tel-05806256/document)

<br>

</div>

---
## Models

The multi-class implementations support three traffic cost formulations:

| Model | Description |
| --- | --- |
| GLWR | Generalized Lighthill–Whitham–Richards |
| GS | Generalized Separable |
| GNS | Generalized Non-Separable |

The multi-class implementations support  three distinct initial spatial configurations of cars and trucks:

| Configuration | Description |
|:---:|:---|
| **CT — Cars–Trucks** | Fully segregated configuration with cars initially positioned in front of trucks. |
| **TC — Trucks–Cars** | Fully segregated configuration with trucks initially positioned in front of cars. |
| **TCT — Trucks–Cars–Trucks** | Interlaced configuration with alternating groups of trucks and cars. |

The macroscopic formulation couples a continuity equation, a Hamilton–Jacobi–Bellman equation, and an optimal velocity condition for each vehicle class. The associated research also examines finite-player traffic games and micro–macro comparisons.

The simulations analyze density evolution, class-dependent velocities, interactions between vehicle populations, and numerical regularity.

The investigations provide computational evidence supporting the effectiveness of the ε-Nash approximation.

---

## Quick start

Run the commands below from the repository root.

### Single-class example

Requires Python, NumPy, and SciPy.

```bash
python3 examples/one_class_demo/run_demo.py --help
python3 examples/one_class_demo/run_demo.py
```

The [interactive notebook](notebooks/one_class_LWR.ipynb) can also be opened through [Binder](https://mybinder.org/v2/gh/amalmach/MultiClass-MFG-Traffic/main?labpath=notebooks%2Fone_class_LWR.ipynb).

### Sequential multi-class solver

Requires Python, NumPy, and SciPy.

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 --model GLWR --nx 5 --nt 8 --max-grids 1 \
    --output sequential_J3_GLWR.npz
```

Replace `GLWR` with `GS` or `GNS` to select another cost model. See the [Newton–Krylov documentation](src/newton_krylov/README.md) for numerical parameters and refinement options.

### Parallel multi-class solver

Requires a compatible installation of PETSc, MPI, `petsc4py`, and `mpi4py`, with MUMPS support for the command below.

```bash
mpirun -np 2 python3 src/petsc4py/multi_class/main.py \
    --J 3 --model GLWR --nx 5 --nt 8 \
    --output petsc_J3_GLWR_MPI2.npz \
    -ksp_type preonly \
    -pc_type lu \
    -pc_factor_mat_solver_type mumps
```

See the [PETSc/MPI documentation](src/petsc4py/README.md) for installation and solver options. 

## Numerical verification

For a three-class test with $N_x=5$ spatial cells, $N_t=8$ time steps, and 390 unknowns, the GLWR, GS, and GNS implementations were evaluated using 1, 2, and 4 MPI processes. The tested solutions agreed across process counts within numerical tolerance and conserved class-wise discrete mass.

Comparisons with the sequential Newton–GMRES implementation gave the following relative $L^2$ differences:

| Model | Relative $L^2$ difference (sequential vs. PETSc) |
| --- | ---: |
| GLWR | $1.11\times10^{-12}$ |
| GS | $9.65\times10^{-12}$ |
| GNS | $9.10\times10^{-9}$ |

These are small-grid numerical consistency checks, not parallel performance benchmarks. Additional numerical figures are available in the [results gallery](results/figures/README.md).

---
## Numerical Results & Scientific Visualizations

The numerical investigations explore **single-class and multi-class traffic dynamics** through macroscopic mean-field models and microscopic finite-player games.

The experiments cover different traffic configurations and cost functionals (**LWR, GLWR, GS, and GNS**), together with the numerical assessment of **mean-field approximations, ε-Nash equilibria, and low-rank structures**.

A complete gallery of the numerical results, including **12 scientific figures**, detailed descriptions, and references to the corresponding publications, is available below.

<div align="center">

### 📈 [Explore the Scientific Figures & Numerical Results Gallery](results/figures/README.md)

</div>

---

## Source Code & Computational Workspace

The repository provides numerical implementations for solving
**single-class and multi-class Nash Mean-Field Game traffic models**.

The computational framework includes **Newton–Krylov algorithms,
finite-difference methods, and PETSc-based parallel implementations**.

Detailed information about the code organization, numerical methods,
and execution procedures is provided in the dedicated source-code documentation.

<div align="center">

### 💻 [Explore the Source Code & Numerical Implementations](src/README.md)

<sub>Newton–Krylov Methods · PETSc · Parallel Computing · Numerical Experiments</sub>

</div>

---
## References<

### Journal Publication — 2025

**A. Machtalay, A. Habbal, A. Ratnani, I. Kissami**

*Computational investigations of a multi-class traffic flow model: Mean-field and microscopic dynamics.*

**Transportation Research Part B: Methodological**, Volume 195, 103196 (2025).

[![DOI](https://img.shields.io/badge/DOI-10.1016%2Fj.trb.2025.103196-blue)](https://doi.org/10.1016/j.trb.2025.103196)

[![arXiv](https://img.shields.io/badge/arXiv-2306.13543-B31B1B)](https://arxiv.org/abs/2306.13543)

### PhD Thesis — 2026

**Amal Machtalay**

*Micro–macro modeling and scalable numerical methods for high-dimensional mean-field and control systems: structure-exploiting solvers and low-rank techniques.*

**Université Côte d’Azur & Mohammed VI Polytechnic University**, 2026.

**Relevant material:** Chapter II — Multi-class traffic modeling and computational investigations.

[![Thesis](https://img.shields.io/badge/Read_PhD_Thesis-HAL-6F42C1)](https://theses.hal.science/tel-05806256/document)


---

<div align="center">

### Mathematical Modeling · Scientific Computing · Computational Engineering

*From game-theoretic traffic models to large-scale computation and reproducible numerical experiments.*

<br>

[![GitHub](https://img.shields.io/badge/Explore_Source_Code-GitHub-181717?style=for-the-badge&logo=github)](https://github.com/amalmach/MultiClass-MFG-Traffic)

<br>

[Research Paper](https://doi.org/10.1016/j.trb.2025.103196)
&nbsp;·&nbsp;
[PhD Thesis](https://theses.hal.science/tel-05806256/document)
&nbsp;·&nbsp;
[Original Release](https://github.com/amalmach/MultiClass-MFG-Traffic/releases/tag/v1.0.0-original)

</div>
