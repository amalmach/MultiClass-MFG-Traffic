<div align="center">

# Multi-Class Traffic Flow Modeling with Mean-Field Games

### Mathematical Modeling · Numerical Methods · High-Performance Computing

**Micro–Macro Dynamics | Nash Mean-Field Games | Scientific Computing | Traffic Simulation**

<br>

[![Research Paper](https://img.shields.io/badge/Research_Paper-Elsevier-0B7285?style=for-the-badge)](https://doi.org/10.1016/j.trb.2025.103196)
[![arXiv](https://img.shields.io/badge/Preprint-arXiv-B31B1B?style=for-the-badge)](https://arxiv.org/abs/2306.13543)
[![PhD Thesis](https://img.shields.io/badge/PhD_Thesis-HAL-6F42C1?style=for-the-badge)](https://theses.hal.science/tel-05806256/document)

<br>

*Research software for mathematical modeling and large-scale numerical investigation of heterogeneous traffic flow.*

</div>

---

<details open>
<summary><h2>🔬 Project Overview</h2></summary>

<br>

### Research Motivation

How can the collective behavior of heterogeneous traffic populations be modeled through individual strategic interactions? How accurately can macroscopic Mean-Field Game equilibria approximate the behavior of finite populations of vehicles? And how can the resulting nonlinear systems be solved efficiently at large computational scales?

This repository accompanies research on **multi-class traffic flow modeling using Nash Mean-Field Games (NMFGs)**. The project extends a single-class, single-lane game-theoretic traffic framework to heterogeneous vehicle populations, with numerical investigations focusing on **cars and trucks**.

It establishes connections between:

- **Microscopic models:** Finite-player differential games describing individual vehicle dynamics.
- **Macroscopic models:** Nash Mean-Field Games describing interactions between vehicle populations.
- **Numerical methods:** Algorithms for solving coupled nonlinear PDE systems.
- **High-performance computing:** Parallel implementations for large-scale numerical experiments.

The research also investigates the ability of **mean-field equilibrium controls to provide approximate Nash strategies** for finite-player traffic games.

### Project at a Glance

| Mathematical Modeling | Numerical Computing | Traffic Applications |
|:---|:---|:---|
| Multi-class Nash Mean-Field Games | Finite difference methods | Cars and trucks |
| Finite-player differential games | Newton–Krylov methods | Traffic density evolution |
| Coupled HJB–continuity equations | LGMRES iterative solvers | Optimal velocity strategies |
| Class-dependent cost functionals | Regularization and preconditioning | Traffic congestion dynamics |
| Approximate Nash equilibria | MPI and PETSc | Micro–macro comparisons |

> **Model scope:** The published model considers a single-lane traffic setting and does not explicitly impose microscopic collision-avoidance constraints. Multi-lane traffic and collision avoidance are possible future extensions.

### 🚀 Interactive Demonstrations

Explore the numerical methods directly in your browser using Binder.
[![Launch Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/amalmach/MultiClass-MFG-Traffic/main?labpath=notebooks%2Fone_class_LWR.ipynb)

</details>

---

<details>
<summary><h2>🎯 Main Scientific Contributions</h2></summary>

<br>

The research combines mathematical modeling, numerical analysis, scientific computing, and traffic engineering.

### 1. Multi-Class Traffic Modeling

Extension of a single-class traffic framework to heterogeneous vehicle populations.

The mathematical formulation connects microscopic finite-player differential games with macroscopic Nash Mean-Field Games.

### 2. Class-Dependent Traffic Objectives

Investigation of three families of cost functionals:

- **GLWR:** Generalized Lighthill–Whitham–Richards.
- **GS:** Generalized Separable.
- **GNS:** Generalized Non-Separable.

These models allow the investigation of different traffic behaviors and interactions between vehicle populations.

### 3. Large-Scale Numerical Algorithms

Development and investigation of computational methodologies combining:

- Space–time finite difference discretization.
- Newton-type nonlinear iterations.
- Newton–Krylov methods.
- LGMRES iterative solvers.
- Regularization-continuation techniques.
- Preconditioning and initialization strategies.
- Parallel computing.

### 4. Investigation of Different Initial Traffic Configurations

Systematic numerical investigation of three distinct initial spatial configurations of cars and trucks to analyze the influence of vehicle-class distributions on multi-class traffic dynamics.

The three configurations considered are:

| Configuration | Description |
|:---:|:---|
| **CT — Cars–Trucks** | Fully segregated configuration with cars initially positioned in front of trucks. |
| **TC — Trucks–Cars** | Fully segregated configuration with trucks initially positioned in front of cars. |
| **TCT — Trucks–Cars–Trucks** | Interlaced configuration with alternating groups of trucks and cars. |

These configurations are investigated under different traffic cost functionals (**GLWR, GS, and GNS**).

### 5. Multi-Class Numerical Simulations

Extensive numerical investigations involving different configurations of cars and trucks.

The simulations analyze density evolution, class-dependent velocities, interactions between vehicle populations, and numerical regularity.

### 6. Micro–Macro Consistency

Numerical comparison of macroscopic mean-field controls and microscopic best-response strategies.

The investigations provide computational evidence supporting the effectiveness of the ε-Nash approximation.

### 7. High-Performance Computing

The associated publication reports numerical investigations of nonlinear systems involving up to approximately **88 million unknowns**.

The computational methodology includes PETSc-based parallel implementations and MPI.

**Scientific references:**
- [Research Paper](https://doi.org/10.1016/j.trb.2025.103196)
- [PhD Thesis — Chapter II](https://theses.hal.science/tel-05806256/document)

</details>

---

<details>
<summary><h2>📐 Mathematical Modeling</h2></summary>

<br>

The mathematical framework connects individual vehicle dynamics with collective traffic behavior through Mean-Field Game theory.

<details>
<summary><strong>🚗 1. Microscopic Traffic Model — Finite-Player Differential Games</strong></summary>

<br>

At the microscopic level, vehicles are modeled as individual agents belonging to different classes.

For vehicle $i$ of class $j$, its position evolves according to: $d x_i^j(t)=v_i^j(t) dt,$

where:

- $x_i^j(t)$ is the vehicle position.
- $v_i^j(t)$ is its velocity control.
- $j$ denotes the vehicle class.

Each vehicle seeks to minimize an individual cost functional depending on its control, its trajectory, and interactions with other vehicles.

The resulting system is formulated as a **finite-player differential game**.

The objective is to investigate the strategic behavior of interacting vehicle populations and relate it to the corresponding macroscopic description.

**References:**
[Research paper, §2.1](https://doi.org/10.1016/j.trb.2025.103196) ·
[PhD thesis, Chapter II, §§II.4.1–II.4.2](https://theses.hal.science/tel-05806256/document)

</details>

<br>

<details>
<summary><strong>🌐 2. Macroscopic Traffic Model — Nash Mean-Field Games</strong></summary>

<br>

At the macroscopic level, traffic is represented through class-dependent density and velocity fields.

For each vehicle class $j=1,\ldots,J$, the model couples:

**1. A forward continuity equation**: $\displaystyle \partial_t \rho^j + \partial_x(\rho^j u^j) = 0$

**2. A backward Hamilton–Jacobi–Bellman equation**: $\displaystyle \partial_t V^j + H_j(\partial_x V^j,\boldsymbol{\rho}) = 0$

**3. An optimal velocity feedback law**: $\displaystyle u^j = \partial_{p_j}H_j(\partial_x V^j,\boldsymbol{\rho})$

where:

| Symbol | Description |
|:---|:---|
| $\rho^j$ | Traffic density of vehicle class $j$ |
| $u^j$ | Optimal velocity field of class $j$ |
| $V^j$ | Optimal value function of class $j$ |
| $H_j$ | Hamiltonian associated with class $j$ |
| $p_j$ | Gradient of $V^j$ ($p_j=\partial_x V^j$) |
| $\boldsymbol{\rho}$ | Vector of class-dependent traffic densities |
| $J$ | Number of vehicle classes |

The Hamiltonian associated with class $j$ is defined by:

<p align="center">
$H_j(p_j,\boldsymbol{\rho})
=
\min_{0\leq\alpha\leq u_{\max}^j}
\left\{
f_j(\alpha,\boldsymbol{\rho})+\alpha p_j
\right\}.$
</p>

The published numerical experiments consider periodic boundary conditions on a ring road.

**References:**
[Research paper, §2.1](https://doi.org/10.1016/j.trb.2025.103196) ·
[PhD thesis, Chapter II, §§II.4.3–II.4.7](https://theses.hal.science/tel-05806256/document)

</details>

<br>

<details>
<summary><strong>🔄 3. Micro–Macro Connection and ε-Nash Approximation</strong></summary>

<br>

The research investigates the relationship between:

- Microscopic finite-player differential games.
- Macroscopic Nash Mean-Field Game equilibria.
- Vehicle-level controls reconstructed from the mean-field solution.

Starting from an optimal macroscopic velocity field, microscopic controls are constructed through: $\widehat{v}_i^j(t) = u^{j,*}\left(t,x_i^j(t)\right).$

The resulting strategies are compared with microscopic best-response controls.

The objective is to assess whether the mean-field-constructed controls provide an **approximate Nash equilibrium** for the finite-player traffic game.

The approximation quality is studied through differences between individual cost functionals.

These comparisons provide numerical evidence supporting the ε-Nash approximation.

**References:**
[Research paper, §2.2](https://doi.org/10.1016/j.trb.2025.103196) ·
[PhD thesis, Chapter II, §II.4.8](https://theses.hal.science/tel-05806256/document)

</details>

<br>

<details>
<summary><strong>📖 4. Mathematical Analysis and Theoretical Foundations</strong></summary>

<br>

The mathematical foundations include:

- Mean-Field Game formulations.
- Finite-player differential games.
- Hamilton–Jacobi–Bellman equations.
- Continuity equations.
- Nash equilibrium conditions.
- Approximate Nash equilibria.
- Connections between microscopic and macroscopic dynamics.

Detailed assumptions, derivations, theoretical discussions, and supporting mathematical results are presented in the PhD thesis.

**Further reading:**
[PhD Thesis — Chapter II](https://theses.hal.science/tel-05806256/document)

</details>

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
