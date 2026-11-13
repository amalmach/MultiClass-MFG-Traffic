<div align="center">
    
# Newton–Krylov Solvers for Traffic Mean-Field Games

This directory contains Python implementations of Newton–Krylov methods
for solving traffic flow models formulated within the framework of
**Mean-Field Games (MFGs)**.


| Directory | Vehicle Classes | Description |
|---|---|---|
| [`one_class/`](one_class/) | $J=1$ | Single-class traffic MFG implementation |
| [`two_class/`](two_class/) | $J=2$ | Two-class traffic MFG implementation |
| [`multi_class/`](multi_class/) | $J\geq1$ | General $J$-class Newton–GMRES solver |

The `multi_class/` directory provides an explicitly organized
implementation of the general $J$-class algorithm described in
Appendix D.1 of the PhD thesis.

</div>

---

## Mathematical Models

Consider $J$ vehicle classes, indexed by $j=1,\ldots,J$.

Each class is described by:

- $\rho_j(t,x)$: traffic density;
- $u_j(t,x)$: optimal velocity;
- $V_j(t,x)$: value function;
- $Q_j(t,x)=\rho_j(t,x)u_j(t,x)$: traffic flux.

The governing system couples continuity equations, Hamilton–Jacobi–Bellman equations, and optimal velocity conditions.

The general multi-class implementation supports three cost formulations:

| Model | Abbreviation | Description |
|---|---|---|
| Generalized LWR | **GLWR** | Density-dependent desired velocity |
| Generalized Separable | **GS** | Separable velocity and density costs |
| Generalized Non-Separable | **GNS** | Coupled velocity-density cost |

### Generalized Lighthill–Whitham–Richards (GLWR)

For vehicle class $j$, the desired velocity is 

<p align="center">
$U_j(\boldsymbol{\rho}) = u_{\max,j} \left( 1- \sum_{m=1}^{J} \frac{\rho_m}{\rho_{\mathrm{jam},m}} \right),$
</p>

where:

- $u_{\max,j}$ is the free-flow velocity of class $j$.
- $\rho_{\mathrm{jam},m}$ is the jam density of class $m$.
- $\rho_m$ is the density of class $m$.

The running cost is 

<p align="center">
$f_j(u_j,\boldsymbol{\rho}) = \frac{1}{2} \left( U_j(\boldsymbol{\rho})-u_j \right)^2.$
</p>

The optimal velocity is $u_j^* = U_j(\boldsymbol{\rho})-p_j,$

where $p_j$ denotes the spatial derivative of the value function.

The physical admissibility of the desired velocity depends on the
combined normalized occupancy 

<p align="center">
$\sum_{m=1}^{J} \frac{\rho_m}{\rho_{\mathrm{jam},m}} \leq 1.$
</p>

Unlike GS and GNS, the implemented GLWR optimal control is not
explicitly clipped to the interval $[0,u_{\max,j}]$.

### Generalized Separable (GS)

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

### Generalized Non-Separable (GNS)

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
\mathrm{clip}
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

## Numerical Method

The discretized traffic MFG equations form a nonlinear algebraic system $F(w)=0,$

where $w$ contains the discrete densities, velocities, and value functions for all vehicle classes.

For $J$ classes, $N_x$ spatial cells, and $N_t$ time steps, the general multi-class implementation uses $N=(3N_t+2)JN_x $ unknowns.

At each Newton iteration, the linearized system is $ J_F(w^{(k)})\delta w^{(k)} = -F(w^{(k)}),$

followed by the update $ w^{(k+1)} = w^{(k)}+\delta w^{(k)}.$

The general multi-class solver uses:

- Analytical sparse Jacobian assembly;
- GMRES for the Newton linear systems;
- Sparse LU preconditioning;
- Optional incomplete LU preconditioning;
- Coarse-to-fine interpolation for initializing refined-grid solutions.

The grid-refinement procedure interpolates a converged solution onto a finer grid before starting the next nonlinear solve.

---

## General Multi-Class Implementation

**Directory:** [`multi_class/`](multi_class/)

### Source Files

| File | Description |
|:---|:---|
| `main.py` | Simulation driver and command-line interface |
| `inputs.py` | Model parameters and initial conditions |
| `cost_functions.py` | GLWR, GS, and GNS cost functions |
| `indx_funcs.py` | Index mappings and solution reconstruction |
| `newton_func.py` | Nonlinear residual assembly |
| `jacobian_exact.py` | Analytical sparse Jacobian assembly |
| `gmres_solver.py` | Newton–GMRES iterations |
| `precond.py` | Sparse LU and incomplete LU preconditioning |
| `multi_grid.py` | Coarse-to-fine interpolation |

### Requirements

The general multi-class solver requires:

- Python 3;
- NumPy;
- SciPy.

Install the Python dependencies with:

```bash
python3 -m pip install numpy scipy
```

### Running the Solver

Execute the following commands from the repository root.

**GLWR:**

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 \
    --model GLWR \
    --nx 5 \
    --nt 8 \
    --max-grids 1 \
    --output sequential_J3_GLWR.npz
```

**GS:**

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 \
    --model GS \
    --nx 5 \
    --nt 8 \
    --max-grids 1 \
    --output sequential_J3_GS.npz
```

**GNS:**

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 \
    --model GNS \
    --nx 5 \
    --nt 8 \
    --max-grids 1 \
    --output sequential_J3_GNS.npz
```

The `--J` argument specifies the number of vehicle classes.

For $J>2$, the default parameters and initial-density profiles are illustrative class-dependent configurations. The original two-class parameterization is retained separately.

### Command-Line Options

| Option | Description | Default |
|:---|:---|:---|
| `--J` | Number of vehicle classes | `2` |
| `--model` | Traffic model: `GLWR`, `GS`, or `GNS` | `GLWR` |
| `--nx` | Initial number of spatial cells | Model configuration |
| `--nt` | Minimum initial number of time steps | Model configuration |
| `--max-grids` | Number of grid levels | `1` |
| `--newton-tol` | Nonlinear residual tolerance | `1e-8` |
| `--gmres-rtol` | GMRES relative tolerance | `1e-8` |
| `--max-newton-iter` | Maximum Newton iterations | `50` |
| `--no-precond` | Disable sparse LU preconditioning | Disabled |
| `--no-multigrid` | Disable interpolation-based initialization on refined grids | Disabled |
| `--output` | Output filename in NumPy `.npz` format | No file |

The available options can be displayed with:

```bash
python3 src/newton_krylov/multi_class/main.py --help
```

### Grid Refinement

Multiple grid levels can be requested using `--max-grids`.

For example:

```bash
python3 src/newton_krylov/multi_class/main.py \
    --J 3 \
    --model GLWR \
    --nx 5 \
    --nt 8 \
    --max-grids 2 \
    --output sequential_J3_GLWR_refined.npz
```

The solver initializes the refined-grid solution by interpolating the preceding grid solution.

The permitted number of grid levels depends on the model configuration.

### Output Format

When `--output` is specified, numerical results are saved as a compressed NumPy archive.

The principal output arrays are:

| Variable | Shape | Description |
|:---|:---|:---|
| `solution` | `(N,)` | Complete discrete solution vector |
| `rho` | `(J, Nx, Nt+1)` | Traffic densities |
| `u` | `(J, Nx, Nt)` | Optimal velocities |
| `V` | `(J, Nx, Nt+1)` | Value functions |
| `Q` | `(J, Nx, Nt)` | Traffic fluxes |
| `x` | `(Nx,)` | Spatial grid |
| `t` | `(Nt+1,)` | Temporal grid |

The archive also contains the discretization parameters, model information, and nonlinear residual norms.

An output file can be loaded using:

```python
import numpy as np

with np.load("sequential_J3_GLWR.npz") as data:
    rho = data["rho"]
    u = data["u"]
    V = data["V"]
    Q = data["Q"]

print("Density shape:", rho.shape)
print("Velocity shape:", u.shape)
```

---

## Single-Class Implementation

**Directory:** [`one_class/`](one_class/)

The single-class directory contains the original Newton–Krylov research implementation for a homogeneous vehicle population.

It includes the nonlinear traffic MFG system, Jacobian-related operations, Krylov solvers, preconditioning, and grid-refinement utilities.

A standalone LWR example is available in the repository:

```bash
python3 examples/one_class_demo/run_demo.py
```

The corresponding figures can be generated with:

```bash
python3 examples/one_class_demo/plot_results.py
```

An interactive demonstration is available in the [single-class LWR notebook](../../notebooks/one_class_LWR.ipynb).

The notebook can also be launched using [Binder](https://mybinder.org/v2/gh/amalmach/MultiClass-MFG-Traffic/main?labpath=notebooks%2Fone_class_LWR.ipynb).

---

## Two-Class Implementation

**Directory:** [`two_class/`](two_class/)

This directory contains the original numerical implementation for two interacting vehicle populations.

The model accounts for class-dependent traffic characteristics, including free-flow velocities, jam densities, and density-dependent interactions.

The implementation is retained separately from the general $J$-class solver.

---

## References

1. A. Machtalay, A. Habbal, A. Ratnani, and I. Kissami, “Computational investigations of a multi-class traffic flow model: Mean-field and microscopic dynamics,” *Transportation Research Part B: Methodological*, **195**, 103196 (2025). [DOI](https://doi.org/10.1016/j.trb.2025.103196).

2. A. Machtalay, *Micro–macro modeling and scalable numerical methods for high-dimensional mean-field and control systems: Structure-exploiting solvers and low-rank techniques*, PhD thesis (2026). [Full text](https://theses.hal.science/tel-05806256/document).

The general multi-class sequential solver follows the numerical methodology described in Appendix D.1 of the thesis.

---

**Repository:** [MultiClass-MFG-Traffic](https://github.com/amalmach/MultiClass-MFG-Traffic)
