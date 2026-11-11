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

**Reference:** Research paper, Section 2.1.

</details>

<br>

<details>
<summary><strong>🌐 2. Macroscopic Traffic Model — Nash Mean-Field Games</strong></summary>

<br>

At the macroscopic level, traffic is represented through class-dependent density and velocity fields.

For each vehicle class $j=1,\ldots,J$, the model couples:

1. A forward continuity equation.
2. A backward Hamilton–Jacobi–Bellman equation.
3. An optimal velocity feedback law.

The resulting system is:

$$
\begin{aligned}
\partial_t \rho_j + \partial_x(\rho_j u_j) &= 0,\\
\partial_t V_j + H_j(\partial_x V_j,\boldsymbol{\rho}) &= 0,\\
u_j &= \partial_{p_j}H_j(\partial_x V_j,\boldsymbol{\rho}).
\end{aligned}
$$

where:

| Symbol | Description |
|:---|:---|
| $\rho_j$ | Traffic density of vehicle class $j$ |
| $u_j$ | Optimal velocity field of class $j$ |
| $V_j$ | Optimal value function of class $j$ |
| $H_j$ | Hamiltonian associated with class $j$ |
| $\rho$ | Vector of class-dependent traffic densities |
| $J$ | Number of vehicle classes |

The Hamiltonian associated with class $j$ is defined by:

$$
H_j(p_j,\boldsymbol{\rho})
=
\min_{0\leq\alpha\leq u_{\max}^j}
\left\{
f_j(\alpha,\boldsymbol{\rho})+\alpha p_j
\right\}.
$$

The published numerical experiments consider periodic boundary conditions on a ring road.

**Reference:** Research paper, Section 2.1.

</details>

<br>

<details>
<summary><strong>🔄 3. Micro–Macro Connection and ε-Nash Approximation</strong></summary>

<br>

The research investigates the relationship between:

- Microscopic finite-player differential games.
- Macroscopic Nash Mean-Field Game equilibria.
- Vehicle-level controls reconstructed from the mean-field solution.

Starting from an optimal macroscopic velocity field, microscopic controls are constructed through:

$$
\widehat{v}_i^j(t)
=
u_j^*\left(t,x_i^j(t)\right).
$$

The resulting strategies are compared with microscopic best-response controls.

The objective is to assess whether the mean-field-constructed controls provide an **approximate Nash equilibrium** for the finite-player traffic game.

The approximation quality is studied through differences between individual cost functionals.

These comparisons provide numerical evidence supporting the ε-Nash approximation.

**References:**

- Research paper, Section 2.2.
- PhD Thesis, Chapter II, Section II.8.

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

**Reference:** Research paper, Section 3.1.

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
- Regularization techniques.
- Preconditioning and initialization strategies.

These methodologies are investigated to improve numerical robustness and enable larger computational experiments.

**Reference:** PhD Thesis, Chapter II, Section II.6.

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

**Reference:** PhD Thesis, Chapter II, Section II.6.

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

- PhD Thesis, Chapter II, Section II.6.
- PhD Thesis, Chapter II, Section II.10.

</details>

</details>

---

<details>
<summary><h2>📊 Numerical Results & Scientific Visualizations</h2></summary>

<br>

The numerical investigations examine different traffic configurations, objective functionals, and computational methodologies.

<details>
<summary><strong>🚦 1. Traffic Scenarios</strong></summary>

<br>

Three initial configurations of cars and trucks are investigated.

| Scenario | Configuration |
|:---|:---|
| **TC** | Segregated traffic configuration with trucks in front |
| **CT** | Segregated traffic configuration with cars in front |
| **TCT** | Interlaced configuration with alternating trucks and cars |

The scenarios are combined with different traffic cost functionals to investigate interactions between vehicle populations.

**Reference:** Research paper, Section 4.

</details>

<br>

<details>
<summary><strong>🌊 2. Macroscopic Traffic Simulations</strong></summary>

<br>

The macroscopic numerical investigations analyze:

- Traffic density evolution.
- Class-dependent velocity fields.
- Optimal value functions.
- Congestion dynamics.
- Interactions between vehicle populations.
- Numerical regularity and shock formation.

**Reference:** PhD Thesis, Chapter II, Section II.7.

### Scientific Figures

Figures illustrating these results will be progressively added to the repository.

The objective is to provide high-quality, reproducible visualizations rather than screenshots alone.

</details>

<br>

<details>
<summary><strong>🚗 3. Microscopic Dynamics and ε-Nash Investigations</strong></summary>

<br>

The microscopic experiments investigate:

- Mean-field-constructed controls.
- Microscopic best-response strategies.
- Differences between individual cost functionals.
- ε-Nash accuracy measures.
- Effects of finite population size.

These numerical experiments evaluate the consistency between microscopic and macroscopic traffic descriptions.

**Reference:** PhD Thesis, Chapter II, Section II.8.

</details>

<br>

<details>
<summary><strong>📈 4. Numerical Solver Performance</strong></summary>

<br>

The computational investigations examine:

- Nonlinear solver convergence.
- Numerical conditioning.
- Regularization effects.
- Computational efficiency.
- Large-scale numerical performance.
- Parallel computing strategies.

**References:**

- PhD Thesis, Chapter II, Section II.6.
- PhD Thesis, Chapter II, Section II.10.

</details>

<br>

<details>
<summary><strong>🖼️ 5. Scientific Results Gallery — Planned Organization</strong></summary>

<br>

The numerical results will be organized into the following categories:

| Gallery | Scientific Objective |
|:---|:---|
| Traffic Density Fields | Visualize class-dependent density evolution |
| Optimal Velocity Fields | Analyze vehicle strategies |
| Space–Time Diagrams | Investigate congestion and traffic propagation |
| Micro–Macro Comparisons | Compare finite-player and mean-field controls |
| ε-Nash Accuracy | Study the approximation of Nash equilibria |
| Numerical Convergence | Evaluate solver behavior |
| HPC Performance | Investigate computational scalability |

Representative figures from the paper and PhD thesis will be integrated as source image files or regenerated from numerical outputs.

</details>

</details>

---

<details>
<summary><h2>💻 Source Code & Computational Workspace</h2></summary>

<br>

The repository contains numerical implementations associated with Mean-Field Game-based traffic modeling.

### Existing Research Code

| Directory | Description |
|:---|:---|
| `Traffic/newton_krylov/` | Newton–Krylov numerical implementations |
| `Traffic/petsc4py/` | PETSc-based parallel implementations |

### Working with the Code Locally

Researchers, engineers, and students can clone the repository and work independently.

```bash
git clone https://github.com/amalmach/MultiClass-MFG-Traffic.git

cd MultiClass-MFG-Traffic

git switch -c experiments/my-traffic-study
```

This creates a local working branch where users can modify code and conduct experiments without affecting the original repository.

Users who want their own GitHub-hosted copy can also **fork the repository**.

### Planned Software Improvements

The repository will be progressively organized to support:

- Reusable numerical solvers.
- Configurable traffic models.
- Independent computational experiments.
- Reproducible numerical results.
- Scientific visualization.
- Automated numerical tests.
- Educational tutorials.

Detailed installation and execution instructions will be added after verification of the existing and extended implementations.

</details>

---

<details>
<summary><h2>🎓 Tutorials & Learning Resources</h2></summary>

<br>

The project is intended for different audiences.

<details>
<summary><strong>📚 For Students</strong></summary>

<br>

Suggested learning pathway:

1. Introduction to Mean-Field Games.
2. Microscopic traffic modeling.
3. Macroscopic traffic models.
4. Hamilton–Jacobi–Bellman equations.
5. Continuity equations.
6. Numerical discretization.
7. Traffic simulation.
8. Interpretation of numerical results.

**Recommended starting point:**

Research paper, Sections 1–2.

</details>

<br>

<details>
<summary><strong>🔬 For Researchers</strong></summary>

<br>

Research-oriented topics include:

- Multi-population Mean-Field Games.
- Finite-player differential games.
- Nash equilibria and ε-Nash approximation.
- Coupled forward–backward PDE systems.
- Numerical linear algebra.
- Newton–Krylov methods.
- Preconditioning and regularization.
- Large-scale computational methods.

**Recommended reading:**

PhD Thesis, Chapter II.

</details>

<br>

<details>
<summary><strong>⚙️ For Engineers</strong></summary>

<br>

Engineering-oriented topics include:

- Multi-class traffic modeling.
- Interactions between vehicle populations.
- Traffic congestion analysis.
- Optimal velocity strategies.
- Numerical simulations.
- Computational performance.
- High-performance computing.

The numerical framework provides a research-oriented tool for investigating traffic dynamics under different mathematical modeling assumptions.

</details>

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

The original commits and historical contributors remain acknowledged through the repository's Git history.

Ongoing development focuses on:

- Multi-class traffic modeling.
- Numerical solver improvements.
- High-performance computing.
- Reproducible numerical experiments.
- Scientific documentation.
- Tutorials and educational resources.

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
