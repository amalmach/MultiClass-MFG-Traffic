<div align="center">

# Multi-Class Traffic Flow Modeling with Mean-Field Games

**Micro–Macro Dynamics | Nash Mean-Field Games | Scientific Computing | Traffic Simulation**

<br>

[![Research Paper](https://img.shields.io/badge/Research_Paper-Elsevier-0B7285?style=for-the-badge)](https://doi.org/10.1016/j.trb.2025.103196)
[![arXiv](https://img.shields.io/badge/Preprint-arXiv-B31B1B?style=for-the-badge)](https://arxiv.org/abs/2306.13543)
[![PhD Thesis](https://img.shields.io/badge/PhD_Thesis-HAL-6F42C1?style=for-the-badge)](https://theses.hal.science/tel-05806256/document)

<br>

</div>

---

<details open>
<summary><h2>🔬 Project Overview</h2></summary>

<br>

This repository accompanies research on **multi-class traffic flow modeling using Nash Mean-Field Games (NMFGs)**. The project extends a single-class, single-lane game-theoretic traffic framework to heterogeneous vehicle populations, with numerical investigations focusing on **cars and trucks**.

It establishes connections between:

- **Microscopic models:** Finite-player differential games describing individual vehicle dynamics.
- **Macroscopic models:** Nash Mean-Field Games describing interactions between vehicle populations.
- **Numerical methods:** Algorithms for solving coupled nonlinear PDE systems.
- **High-performance computing:** Parallel implementations for large-scale numerical experiments.

The research also investigates the ability of **mean-field equilibrium controls to provide approximate Nash strategies** for finite-player traffic games.

> **Model scope:** The published model considers a single-lane traffic setting and does not explicitly impose microscopic collision-avoidance constraints. Multi-lane traffic and collision avoidance are possible future extensions.

### 🚀 Interactive Demonstrations

Explore the numerical methods directly in your browser using 
[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/amalmach/MultiClass-MFG-Traffic/main?labpath=notebooks%2Fone_class_LWR.ipynb)

</details>

---

<details>
<summary><h2>📐 MModels</h2></summary>

<br>

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

</details>

---

<details>
<summary><h2>⚙️ Numerical Methods & High-Performance Computing</h2></summary>

<br>

The coupled Nash Mean-Field Game formulation leads to a large nonlinear algebraic system after space–time discretization.

The numerical methodology combines discretization schemes, iterative nonlinear solvers, regularization, and high-performance computing.

<details>
<summary><strong>📏 1. Space–Time Finite Difference Discretization</strong></summary>

<br>

The spatial and temporal domains are discretized using uniform grids.

The numerical formulation includes:

- Lax–Friedrichs discretization of the continuity equation.
- Upwind finite differences for the HJB equation.
- Discretization of optimal feedback laws.
- Periodic boundary conditions.
- Courant–Friedrichs–Lewy (CFL) stability restrictions.

The resulting discretization produces a coupled nonlinear system involving the unknown density, velocity, and value-function variables.

**References:**
[Research paper, §3.1](https://doi.org/10.1016/j.trb.2025.103196) ·
[PhD thesis, Chapter II, §II.6.1](https://theses.hal.science/tel-05806256/document)

</details>

<br>

<details>
<summary><strong>🔢 2. Newton–Krylov and LGMRES Solvers</strong></summary>

<br>

The nonlinear algebraic system is treated using Newton-type iterative methods.

The computational approach includes:

- Newton iterations.
- Krylov subspace methods.
- LGMRES iterative linear solvers.
- Numerical treatment of ill-conditioned Jacobians.
- Regularization-continuation techniques.
- Preconditioning and initialization strategies.

These methodologies are investigated to improve numerical robustness and enable larger computational experiments.

**References:**
[Research paper, §3.2](https://doi.org/10.1016/j.trb.2025.103196) ·
[PhD thesis, Chapter II, §II.6.2-II.6.9](https://theses.hal.science/tel-05806256/document)

</details>

<br>

<details>
<summary><strong>⚡ 3. High-Performance Computing</strong></summary>

<br>

The project investigates parallel numerical implementations for large-scale traffic simulations.

The computational tools include:

| Technology | Role |
|:---|:---|
| Python | Scientific programming |
| NumPy / SciPy | Numerical computing |
| PETSc / petsc4py | Scalable numerical solvers |
| MPI / mpi4py | Parallel computing |
| Pyccel | Performance-oriented numerical computing |
| LGMRES | Iterative linear system solution |

The associated research reports experiments involving nonlinear systems of up to approximately **88 million unknowns**.

**References:**
[Research paper, §3](https://doi.org/10.1016/j.trb.2025.103196) ·
[PhD thesis, Chapter II, §II.6](https://theses.hal.science/tel-05806256/document)

</details>

<br>

<details>
<summary><strong>🧮 4. Numerical Conditioning, Regularization and Computational Challenges</strong></summary>

<br>

The research investigates several numerical challenges associated with coupled forward–backward PDE systems:

- Ill-conditioned Jacobian matrices.
- Nonlinear solver convergence.
- Numerical regularity.
- Shock formation.
- Initialization strategies.
- Regularization–continuation.
- Computational scalability.

These issues motivate the investigation of advanced numerical methods and scalable computational approaches.

**References:**
[Research paper, §3](https://doi.org/10.1016/j.trb.2025.103196) ·
[PhD thesis, Chapter II, §§II.6 and II.10](https://theses.hal.science/tel-05806256/document)

</details>

</details>

---

<details>
<summary><h2>📊 Numerical Results & Scientific Visualizations</h2></summary>

<br>

The numerical investigations explore **single-class and multi-class traffic dynamics** through macroscopic mean-field models and microscopic finite-player games.

The experiments cover different traffic configurations and cost functionals (**LWR, GLWR, GS, and GNS**), together with the numerical assessment of **mean-field approximations, ε-Nash equilibria, and low-rank structures**.

A complete gallery of the numerical results, including **12 scientific figures**, detailed descriptions, and references to the corresponding publications, is available below.

<div align="center">

### 📈 [Explore the Scientific Figures & Numerical Results Gallery](results/figures/README.md)

<sub>Traffic Configurations · Macroscopic Dynamics · Microscopic Simulations · Nash Equilibrium Accuracy · Low-Rank Analysis</sub>

</div>

</details>

---

<details>
<summary><h2>💻 Source Code & Computational Workspace</h2></summary>

<br>

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

</details>

---

<details>
<summary><h2>📚 Publications & Scientific References</h2></summary>

<br>

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

### Original Research Code

The original implementation has been preserved through the GitHub release:

[![Original Release](https://img.shields.io/badge/Original_Research_Code-v1.0.0--original-2F855A)](https://github.com/amalmach/MultiClass-MFG-Traffic/releases/tag/v1.0.0-original)

This release preserves a reference snapshot of the repository before subsequent restructuring and software extensions.

</details>

---

<details>
<summary><h2>👩‍💻 Development & Contributions</h2></summary>

<br>

### Lead Developer & Repository Maintainer

**[Amal Machtalay](https://github.com/amalmach)**

This repository originated from collaborative research associated with the scientific publication cited above.

The existing software license and applicable contributor notices remain in force.

For reuse conditions, consult the repository's [LICENSE](LICENSE).

</details>

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
