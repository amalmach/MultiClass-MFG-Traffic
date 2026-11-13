<div align="center">

# 📊 Scientific Figures & Numerical Results

This gallery presents numerical results from the investigation of single-class and multi-class traffic flow models based on Nash Mean-Field Games (NMFGs).

The figures illustrate macroscopic traffic dynamics, microscopic finite-player games, mean-field equilibrium approximations, and numerical solution properties.

The results are associated with the [research article](https://doi.org/10.1016/j.trb.2025.103196) and [PhD thesis](https://theses.hal.science/tel-05806256/document).

</div>

---

# 🚗 1. Initial Traffic Configurations

<details>
<summary><strong>📌 Figure II.1 — One-Class Initial Density Distribution</strong></summary>

<br>

![Single-class initial density](one_class_initial_density.png)

Initial density distribution for the single-class traffic model.

**Source:** PhD thesis, Figure II.1.

</details>

<br>

<details>
<summary><strong>📌 Figure II.2 — Two-Class Traffic Configurations (TC, CT, TCT)</strong></summary>

<br>

![Two-class initial traffic configurations](two_class_initial_configurations.png)

Initial density distributions for heterogeneous traffic composed of cars and trucks.

Three spatial configurations are considered:

- **TC:** Trucks–Cars.
- **CT:** Cars–Trucks.
- **TCT:** Trucks–Cars–Trucks.

These configurations are used to investigate the influence of the initial spatial arrangement on traffic dynamics.

**Sources:** PhD thesis, Figure II.2; research article, Figure 1.

</details>

---

# 🌊 2. Macroscopic Traffic Simulations

The macroscopic simulations describe the evolution of traffic density, optimal velocity, and value functions under different traffic cost formulations.

<details>
<summary><strong>📌 Figure II.3 — One-Class Macroscopic Traffic Dynamics</strong></summary>

<br>

<div align="center">

<img src="one_class_macroscopic_dynamics.png"
     width="900">

</div>

<br>

Macroscopic numerical results for the single-class LWR, Separable, and Non-Separable models.

The figure compares traffic densities, optimal velocities, value functions, and fundamental diagrams.

**Sources:** PhD thesis, Figure II.3; research article, Figure 8.

</details>

<br>

<details>
<summary><strong>📌 Figure II.4 — GLWR Model: Multi-Class Traffic Dynamics</strong></summary>

<br>

<div align="center">

<img src="glwr_traffic_configurations.png"
     alt="GLWR macroscopic traffic dynamics for TC, CT, and TCT configurations"
     width="900">

</div>

<br>

Macroscopic traffic dynamics for the Generalized Lighthill–Whitham–Richards (GLWR) model.

The simulations examine heterogeneous vehicle populations under the TC, CT, and TCT initial configurations.

**Sources:** PhD thesis, Figure II.4; research article, Figure 2.

</details>

<br>

<details>
<summary><strong>📌 Figure II.5 — Generalized Separable (GS) Model</strong></summary>

<br>

<div align="center">

<img src="gs_macroscopic_dynamics.png"
     alt="Generalized Separable macroscopic traffic dynamics"
     width="900">

<br>

<sub>
<b>Figure II.5.</b> Macroscopic traffic simulations under the
Generalized Separable (GS) cost functional.
</sub>

</div>

<br>

Macroscopic numerical results for the Generalized Separable (GS) traffic model.

The figure presents class-dependent density, velocity, and value-function evolution for different initial traffic configurations.

**Sources:** PhD thesis, Figure II.5; research article, Figure 3.
</details>

<br>

<details>
<summary><strong>📌 Figure II.6 — Generalized Non-Separable (GNS) Model</strong></summary>

<br>

<div align="center">

<img src="gns_macroscopic_dynamics.png"
     alt="Generalized Non-Separable macroscopic traffic dynamics"
     width="900">

<br>

<sub>
<b>Figure II.6.</b> Macroscopic traffic simulations under the
Generalized Non-Separable (GNS) cost functional.
</sub>

</div>

<br>

Macroscopic numerical results for the Generalized Non-Separable (GNS) traffic model.

The simulations illustrate the influence of non-separable congestion-dependent costs on heterogeneous traffic dynamics.

**Sources:** PhD thesis, Figure II.6; research article, Figure 4.
</details>

---

# 🚘 3. Microscopic Traffic Simulations

The microscopic experiments compare strategies derived from mean-field equilibria with best-response strategies in finite-player traffic games.

<details>
<summary><strong>📌 Figure II.7 — One-Class Microscopic Strategy Comparison</strong></summary>

<br>

<div align="center">

<img src="one_class_microscopic_comparison.png"
     alt="Microscopic strategy comparison for the single-class traffic model"
     width="900">

<br>

<sub>
<b>Figure II.7.</b> Comparison between mean-field-derived
strategies and finite-player best responses for one-class traffic.
</sub>

</div>

<br>

Comparison of mean-field-derived controls and finite-player best-response strategies for the single-class traffic model.

The analysis includes the corresponding individual costs.

**Sources:** PhD thesis, Figure II.7; research article, Figure 9.
</details>

<br>

<details>
<summary><strong>📌 Figure II.9 — Two-Class Microscopic Strategy Comparison</strong></summary>

<br>

<div align="center">

<img src="two_class_microscopic_comparison.png"
     alt="Two-class microscopic traffic comparison under GS and GNS models"
     width="900">

<br>

<sub>
<b>Figure II.9.</b> Microscopic traffic comparisons for
heterogeneous two-class systems under GS and GNS cost functionals.
</sub>

</div>

<br>

Microscopic comparisons for heterogeneous populations of cars and trucks.

The experiments consider the Generalized Separable and Generalized Non-Separable models under different initial traffic configurations.

**Sources:** PhD thesis, Figure II.9; research article, Figure 5.

</details>

<br>

<details>
<summary><strong>📌 Figure II.10 — Mean-Field and Microscopic Optimal Controls</strong></summary>

<br>

<div align="center">

<img src="two_class_optimal_controls.png"
     alt="Comparison of mean-field optimal controls and microscopic best responses"
     width="900">

<br>

<sub>
<b>Figure II.10.</b> Comparison of macroscopic mean-field
equilibrium controls and microscopic best-response controls.
</sub>

</div>

<br>

Comparison between optimal controls obtained from the macroscopic mean-field formulation and finite-player best-response controls.

**Sources:** PhD thesis, Figure II.10; research article, Figure 7.

</details>

---

# 🎯 4. Nash Equilibrium Approximation & Convergence

These experiments investigate the accuracy of mean-field equilibrium strategies as approximations of Nash equilibria in finite-player traffic games.

<details>
<summary><strong>📌 Figure II.8 — One-Class Nash Approximation Accuracy</strong></summary>

<br>

<div align="center">

<img src="one_class_nash_accuracy.png"
     alt="Nash equilibrium approximation accuracy for one-class traffic"
     width="900">

<br>

<sub>
<b>Figure II.8.</b> Mean and maximum approximation errors
and log–log convergence analysis for one-class traffic.
</sub>

</div>

<br>

Mean and maximum approximation errors for the single-class traffic game.

The results include log–log representations of the approximation errors as the number of players increases.

**Sources:** PhD thesis, Figure II.8; research article, Figure 10.


</details>

<br>

<details>
<summary><strong>📌 Figure II.11 — Two-Class Nash Approximation Accuracy</strong></summary>

<br>

<div align="center">

<img src="two_class_nash_accuracy.png"
     alt="Nash approximation accuracy and convergence for two-class traffic"
     width="900">

<br>

<sub>
<b>Figure II.11.</b> Mean and maximum approximation errors
and log–log convergence analysis for heterogeneous two-class traffic.
</sub>

</div>

<br>

Mean and maximum approximation errors for heterogeneous finite-player traffic games.

The numerical results examine the accuracy of multi-class mean-field equilibrium controls as approximate Nash strategies.

**Sources:** PhD thesis, Figure II.11; research article, Figure 6.

</details>

---

# 📉 5. Low-Rank Structure & Numerical Analysis

<details>
<summary><strong>📌 Figure II.12 — Singular-Value Decay and Low-Rank Structure</strong></summary>

<br>

<div align="center">

<img src="singular_value_decay.png"
     alt="Singular-value decay of traffic density, velocity, and optimal-cost matrices"
     width="900">

<br>

<sub>
<b>Figure II.12.</b> Normalized singular-value decay for
density, velocity, and optimal-cost matrices.
</sub>

</div>

<br>

Normalized singular-value decay of numerical matrices associated with traffic density, optimal velocity, and value functions.

The analysis considers different discretization resolutions and single-class traffic cost formulations, illustrating the potential of low-rank approximation techniques.

**Source:** PhD thesis, Figure II.12.
</details>

---

# 📚 Scientific References

**Research paper**

1. A. Machtalay, A. Habbal, A. Ratnani, and I. Kissami, "Computational investigations of a multi-class traffic flow model: Mean-field and microscopic dynamics," *Transportation Research Part B: Methodological*, **195**, 103196 (2025). [DOI](https://doi.org/10.1016/j.trb.2025.103196).

2. A. Machtalay, *Micro–macro modeling and scalable numerical methods for high-dimensional mean-field and control systems: Structure-exploiting solvers and low-rank techniques*, PhD thesis (2026). [Full text](https://theses.hal.science/tel-05806256/document).

---

<div align="center">

[⬅ Back to Main Repository](../../README.md)

</div>
