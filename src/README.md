<div align="center">

# 💻 Source Code & Numerical Implementations

This directory contains numerical implementations for single-class and multi-class traffic flow models formulated as Nash Mean-Field Games (NMFGs).

The computational methods combine finite-difference discretizations, Newton–Krylov algorithms, and PETSc/MPI parallel solvers.

</div>

---

## 📁 Code Organization

| Directory | Description |
|:---|:---|
| [`newton_krylov/`](newton_krylov/) | Numerical implementations based on Newton–Krylov methods. |
| [`petsc4py/`](petsc4py/) | PETSc-based implementations for parallel scientific computing. |

---

## ⚙️ Numerical Methodology

<details>
<summary><strong>📐 1. Mathematical Models & Discretization</strong></summary>

<br>

The numerical framework addresses coupled systems involving:

- Forward continuity equations describing traffic density evolution.
- Backward Hamilton–Jacobi–Bellman equations.
- Optimal feedback control laws.
- Class-dependent traffic cost functionals.

The computational methodology includes finite-difference
discretizations of the governing equations.

**References:**
[Research paper, §3.1](https://doi.org/10.1016/j.trb.2025.103196) ·
[PhD thesis, Chapter II, §II.6.1](https://theses.hal.science/tel-05806256/document).

</details>

<br>

<details>
<summary><strong>🔢 2. Newton–Krylov Numerical Methods</strong></summary>

<br>

The numerical investigation considers Newton-type iterative
methods for solving the nonlinear systems arising from
the discretized mean-field game equations.

The associated methodology includes:

- Newton iterations.
- Krylov subspace methods.
- LGMRES iterative linear solvers.
- Regularization and continuation techniques.
- Numerical strategies for improving solver robustness.

📂 **[Explore the Newton–Krylov implementations](newton_krylov/)**

**References:**
[Research paper, §3.2](https://doi.org/10.1016/j.trb.2025.103196) ·
[PhD thesis, Chapter II, §§II.6.2–II.6.9](https://theses.hal.science/tel-05806256/document).

</details>

<br>

<details>
<summary><strong>⚡ 3. High-Performance Computing with PETSc</strong></summary>

<br>

The research also investigates parallel numerical approaches
for large-scale nonlinear systems.

The computational methodology involves:

- PETSc-based numerical solvers.
- MPI parallelization.
- Scalable linear and nonlinear algebra.
- Large-scale numerical experiments.

📂 **[Explore the PETSc implementations](petsc4py/)**

**References:**
[Research paper, §3](https://doi.org/10.1016/j.trb.2025.103196) ·
[PhD thesis, Chapter II, §II.6](https://theses.hal.science/tel-05806256/document).

</details>

---

## 🚀 Running the Numerical Experiments

Execution instructions will be documented after the
individual scripts, dependencies, and required input files
have been verified.

The aim is to provide reproducible procedures for running
selected numerical experiments.

---

## 📊 Numerical Results

The numerical experiments investigate different traffic
configurations, mathematical models, and numerical strategies.

The corresponding figures and scientific explanations are
available in the dedicated gallery.

📈 **[Explore the Scientific Figures & Numerical Results Gallery](../results/figures/README.md)**

---

## 📚 Scientific References

**Research paper**

A. Machtalay, A. Habbal, A. Ratnani, and I. Kissami.

*Computational investigations of a multi-class traffic flow model:
mean-field and microscopic dynamics.*

Transportation Research Part B: Methodological, 195 (2025), 103196.

📄 [Journal publication](https://doi.org/10.1016/j.trb.2025.103196)

**PhD thesis**

A. Machtalay.

*Micro–macro modeling and scalable numerical methods for high-dimensional
mean-field and control systems: structure-exploiting solvers and low-rank techniques.*

2026.

📖 [Read the PhD thesis](https://theses.hal.science/tel-05806256/document)

---

<div align="center">

### 💻 Scientific Computing · Numerical Methods · High-Performance Computing

[⬅ Back to Main Repository](../README.md)

</div>
