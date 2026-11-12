# Newton–Krylov Solvers for Traffic Mean-Field Games

### Single-Class, Two-Class, and General Multi-Class Models

This directory contains Python implementations of Newton–Krylov methods
for solving traffic flow models formulated within the framework of
**Mean-Field Games (MFGs)**.

The implementations cover three levels of model complexity:

- **Single-class traffic models:** one homogeneous population of vehicles.
- **Two-class traffic models:** two interacting vehicle populations.
- **General multi-class traffic models:** an arbitrary number of vehicle classes, $J \geq 1$.

The numerical methods are based on the research presented in the associated
journal article and PhD thesis.

**Research article**

A. Machtalay, A. Habbal, A. Ratnani, and I. Kissami (2025).

*Computational investigations of a multi-class traffic flow model:
mean-field and microscopic dynamics.*

**Transportation Research Part B: Methodological**, 195, 103196.

[Research article — DOI](https://doi.org/10.1016/j.trb.2025.103196)

**PhD thesis**

A. Machtalay (2026).

*Micro–macro modeling and scalable numerical methods for high-dimensional
mean-field and control systems: structure-exploiting solvers and
low-rank techniques.*

[PhD Thesis — HAL](https://theses.hal.science/tel-05806256/document)

---

## 1. Overview

Traffic Mean-Field Games describe the evolution of vehicle populations
whose dynamics depend on the interactions between traffic density,
individual velocity choices, and optimal control.

For a system with $J$ vehicle classes, each class
$j=1,\ldots,J$ is characterized by:

- A traffic density $\rho_j(t,x)$.
- An optimal velocity $u_j(t,x)$.
- A value function $V_j(t,x)$.
- A traffic flux $Q_j(t,x)$.

The traffic flux is defined by $Q_j(t,x)=\rho_j(t,x)u_j(t,x).$

The interaction between vehicle populations is represented through
class-dependent cost functions and the density vector $\boldsymbol{\rho} = (\rho_1,\rho_2,\ldots,\rho_J).$

The numerical objective is to solve the coupled discretized equations
governing traffic densities, optimal controls, and value functions.

The three directories provide complementary implementations
of the traffic MFG framework.

| Directory | Vehicle Classes | Description |
|---|---|---|
| [`one_class/`](one_class/) | $J=1$ | Original single-class research implementation |
| [`two_class/`](two_class/) | $J=2$ | Original two-class research implementation |
| [`multi_class/`](multi_class/) | $J\geq1$ | General sequential Newton–GMRES implementation |

The original single-class and two-class source files are retained
separately to preserve their research implementations.

The `multi_class/` directory provides an explicitly organized
implementation of the general $J$-class algorithm described in
Appendix D.1 of the PhD thesis.

---

## 3. Mathematical Models

The research framework considers traffic models with different
cost functionals.

The general multi-class implementation supports three models:

| Model | Abbreviation | Description |
|---|---|---|
| Generalized LWR | **GLWR** | Density-dependent desired velocity |
| Generalized Separable | **GS** | Separable velocity and density costs |
| Generalized Non-Separable | **GNS** | Coupled velocity-density cost |

### 3.1. Generalized Lighthill–Whitham–Richards (GLWR)

For vehicle class $j$, the desired velocity is $U_j(\boldsymbol{\rho}) = u_{\max,j} \left( 1- \sum_{m=1}^{J} \frac{\rho_m}{\rho_{\mathrm{jam},m}} \right),$

where:

- $u_{\max,j}$ is the free-flow velocity of class $j$.
- $\rho_{\mathrm{jam},m}$ is the jam density of class $m$.
- $\rho_m$ is the density of class $m$.

The running cost is $f_j(u_j,\boldsymbol{\rho}) = \frac{1}{2} \left( U_j(\boldsymbol{\rho})-u_j \right)^2.$

The optimal velocity is $u_j^* = U_j(\boldsymbol{\rho})-p_j,$

where $p_j$ denotes the spatial derivative of the value function.

The physical admissibility of the desired velocity depends on the
combined normalized occupancy $\sum_{m=1}^{J} \frac{\rho_m}{\rho_{\mathrm{jam},m}} \leq 1.$

Unlike GS and GNS, the implemented GLWR optimal control is not
explicitly clipped to the interval $[0,u_{\max,j}]$.

### 3.2. Generalized Separable (GS)

The running cost is

<p align="center">
$f_j(u_j,\boldsymbol{\rho})
= \frac{1}{2} \left(\frac{u_j}{u_{\max,j}} \right)^2 - \frac{u_j}{u_{\max,j}} +
\frac{1}{J}
\sum_{m=1}^{J}
\frac{\rho_m}{\rho_{\mathrm{jam},m}}.$
</p>

The optimal control is

<p align="center">
$u_j^*
=
\mathrm{clip}
\left(
u_{\max,j}
(1-u_{\max,j}p_j),
0,
u_{\max,j}
\right).$
</p>

The optimal velocity therefore satisfies

<p align="center">
$0\leq u_j^*\leq u_{\max,j}.$
</p>

### 3.3. Generalized Non-Separable (GNS)

The running cost is

<p align="center">
$f_j(u_j,\boldsymbol{\rho})
=
\frac{1}{2}
\left(
\frac{u_j}{u_{\max,j}}
\right)^2
-
\frac{u_j}{u_{\max,j}}
+
\left(
\frac{1}{J}
\sum_{m=1}^{J}
\frac{\rho_m}{\rho_{\mathrm{jam},m}}
\right)
\frac{u_j}{u_{\max,j}}.$
</p>

The optimal velocity is

<p align="center">
$u_j^*
=
\operatorname{clip}
\left(
u_{\max,j}
\left[
1-
\frac{1}{J}
\sum_{m=1}^{J}
\frac{\rho_m}{\rho_{\mathrm{jam},m}}
-u_{\max,j}p_j
\right],
0,
u_{\max,j}
\right).$
</p>

Unlike the separable model, the density directly influences
the optimal velocity.

---

## 4. Numerical Methodology

### 4.1. Discretized Nonlinear System

After discretization, the traffic MFG equations are assembled into
a nonlinear system $F(w)=0.$

The unknown vector contains the discretized densities,
velocities, and value functions for all vehicle classes.

For the general $J$-class implementation, the number
of unknowns is $N=(3N_t+2)JN_x,$

where:

- $N_x$ is the number of spatial cells.
- $N_t$ is the number of temporal steps.
- $J$ is the number of vehicle classes.

### 4.2. Newton Linearization

At iteration $k$, Newton's method solves

<p align="center">
$J_F(w^{(k)})\delta w^{(k)}
=
-F(w^{(k)}),$
</p>

where $J_F$ denotes the Jacobian matrix.

The solution is updated according to

<p align="center">
$w^{(k+1)}
=
w^{(k)}+\delta w^{(k)}.$
</p>

### 4.3. Krylov Linear Solvers

The Newton linear systems are solved using Krylov-subspace methods.

The repository includes implementations using GMRES-related
numerical methods.

The general $J$-class implementation uses
**sequential Newton–GMRES**.

The original single-class research workflow also includes
Newton–Krylov computations using LGMRES.

### 4.4. Sparse Jacobian and Preconditioning

The general multi-class implementation uses:

- Analytical sparse Jacobian assembly.
- Approximate Jacobians for preconditioning.
- Sparse LU factorization through SciPy.
- Optional incomplete LU factorization.

The preconditioner approximates the inverse action of
the Jacobian and is supplied to GMRES as a linear operator.

### 4.5. Multigrid Interpolation

Coarse-grid numerical solutions can be interpolated onto
finer spatial-temporal grids.

The general $J$-class implementation uses cubic interpolation
in space and time, following Appendix D.1 of the thesis.

The interpolated solution provides the initial guess
for the Newton–GMRES iterations on the refined grid.

---

## 5. Single-Class Implementation

**Directory:** [`one_class/`](one_class/)

This directory contains the original numerical research code
for a homogeneous vehicle population.

The implementation includes the nonlinear MFG system,
index mappings, Jacobian-related operations, Krylov solvers,
and numerical preconditioning and refinement utilities.

### Reproducible Single-Class Demonstration

An interactive LWR demonstration is available in the
repository:

[Single-Class LWR Notebook](../../../notebooks/one_class_LWR.ipynb)

The example can also be executed using:

```bash
python3 examples/one_class_demo/run_demo.py
```

Generate the corresponding figures with:

```bash
python3 examples/one_class_demo/plot_results.py
```

These commands should be executed from the repository root.

### Interactive Notebook

The single-class LWR notebook can be launched
directly in a browser:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/amalmach/MultiClass-MFG-Traffic/main?labpath=notebooks%2Fone_class_LWR.ipynb)

The notebook supports numerical experimentation without
requiring a local installation.

---

## 6. Two-Class Implementation

**Directory:** [`two_class/`](two_class/)

This directory contains the original research implementation
for two interacting vehicle populations.

The two-class setting allows different physical characteristics
for each vehicle population, including class-dependent
velocities and jam densities.

It provides a dedicated implementation of the two-population
traffic MFG problem and preserves the numerical code
associated with the research work.

---

## 7. General Multi-Class Implementation

**Directory:** [`multi_class/`](multi_class/)

This directory contains the implementation of the
**Sequential Newton–GMRES solver** for an arbitrary number
of vehicle classes.

It follows:

**Appendix D.1 — Sequential Newton–GMRES solver**

of the PhD thesis.

### Source Files

| File | Purpose |
|---|---|
| `inputs.py` | Physical parameters, initial densities, and numerical settings |
| `indx_funcs.py` | Index mappings and solution reconstruction |
| `cost_functions.py` | GLWR, GS, and GNS cost functions |
| `newton_func.py` | Nonlinear residual assembly |
| `jacobian_exact.py` | Exact and approximate analytical Jacobians |
| `gmres_solver.py` | Sequential Newton–GMRES algorithm |
| `precond.py` | Sparse LU/ILU preconditioners |
| `multi_grid.py` | Coarse-to-fine cubic interpolation |
| `main.py` | Complete simulation and grid-refinement workflow |

### Running GLWR

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 \
    --model GLWR \
    --nx 5 \
    --nt 8 \
    --max-grids 2
```

### Running GS

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 \
    --model GS \
    --nx 5 \
    --nt 8 \
    --max-grids 2
```

### Running GNS

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 \
    --model GNS \
    --nx 5 \
    --nt 8 \
    --max-grids 2
```

### Changing the Number of Vehicle Classes

The number of classes is controlled by the `--J` argument.

For example, a five-class GLWR experiment can be launched with:

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 5 \
    --model GLWR \
    --nx 5 \
    --nt 8 \
    --max-grids 1
```

**Parameter note:** The original two-class physical parameters
are retained from the thesis. For $J>2$, the implementation
uses illustrative class-dependent parameters and initial-density
profiles. 

### Saving Numerical Results

The general solver supports saving results in NumPy format:

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 \
    --model GLWR \
    --nx 5 \
    --nt 8 \
    --max-grids 2 \
    --output multi_class_J3_GLWR.npz
```

The resulting file contains:

| Variable | Shape | Description |
|---|---|---|
| `rho` | `(J, Nx, Nt+1)` | Traffic density |
| `u` | `(J, Nx, Nt)` | Optimal velocity |
| `V` | `(J, Nx, Nt+1)` | Value function |
| `Q` | `(J, Nx, Nt)` | Traffic flux |

The archive also stores numerical parameters,
the computational grid, and residual norms.

---

## 8. Numerical Verification

The general $J$-class solver has been tested for
three vehicle classes using GLWR, GS, and GNS.
### 8.1. Grid Refinement
### 8.2. Nonlinear Convergence: 

All three models converged below the prescribed tolerance $\|F(w)\|_2<10^{-8}.$

### 8.3. Mass Conservation

For the three-class GLWR simulation, the discrete mass
of each class was computed as $M_j^n = \Delta x \sum_{k=1}^{N_x} \rho_{j,k}^{n}.$

### 8.4. Physical Admissibility

For the validated three-class GLWR, GS, and GNS
experiments:

- Computed traffic densities were nonnegative.
- Computed optimal velocities were nonnegative.
- Computed velocities remained below their
  class-dependent free-flow maximum values.

---

## 9. Requirements

The Newton–Krylov implementations use Python
and scientific computing libraries.

The general multi-class implementation requires:

- Python 3
- NumPy
- SciPy

Install these packages using:

```bash
python3 -m pip install numpy scipy
```

The repository's separate PETSc-based implementations
may require additional packages and system dependencies.

---

## 10. References

### Research Article

**A. Machtalay, A. Habbal, A. Ratnani, and I. Kissami (2025).**

*Computational investigations of a multi-class traffic flow model:
mean-field and microscopic dynamics.*

**Transportation Research Part B: Methodological**, 195, 103196.

DOI: [10.1016/j.trb.2025.103196](https://doi.org/10.1016/j.trb.2025.103196)

### PhD Thesis

**A. Machtalay (2026).**

*Micro–macro modeling and scalable numerical methods for high-dimensional
mean-field and control systems: structure-exploiting solvers and
low-rank techniques.*

Appendix D.1: **Sequential Newton–GMRES solver**.

[PhD Thesis — HAL](https://theses.hal.science/tel-05806256/document)

---

**Repository:** [MultiClass-MFG-Traffic](https://github.com/amalmach/MultiClass-MFG-Traffic)
