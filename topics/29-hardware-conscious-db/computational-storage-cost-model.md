---
id: 29-hardware-conscious-db/computational-storage-cost-model
title: "Computational-storage cost model and bounds"
topic: 29-hardware-conscious-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Computational-storage cost model and bounds

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/computational-storage-cost-model` · **Status:** open

## 1. Problem Statement

Whether in-storage filtering/aggregation beats host execution depends on a tangle of parameters: device compute throughput, device-internal bandwidth (often **far higher** than the host interface — the whole point), interface bandwidth, host compute, result selectivity, and energy. Practitioners need a **predictive cost model** that, given an operator and these device/host parameters, says *when pushdown wins and by how much*, plus **provable bounds** on the maximum achievable speedup. The problem: derive a cost model that is (a) **accurate** enough to drive optimizer decisions and (b) **analyzable** enough to yield closed-form crossover thresholds and an upper bound on attainable benefit under interface limits.

Variants: (i) **decision** — predict the sign of (host cost − pushdown cost); (ii) **quantitative** — predict the ratio/speedup; (iii) **bounding** — prove the maximum speedup any pushdown can yield given the internal-vs-interface bandwidth ratio; (iv) **energy** model variant minimizing joules rather than latency.

## 2. Mathematical Foundations

Let internal device bandwidth be $\beta_{\text{int}}$, host interface bandwidth $\beta_{io}$ with $\rho = \beta_{\text{int}}/\beta_{io} \ge 1$ the **bandwidth amplification**, host compute $\pi_h$, device compute $\pi_d$, and operator selectivity $\sigma$ on $N$ bytes. Two **roofline** times:

$$T_{\text{host}} = \max\!\Big(\tfrac{N}{\beta_{io}},\, \tfrac{c(N)}{\pi_h}\Big), \qquad T_{\text{dev}} = \max\!\Big(\tfrac{N}{\beta_{\text{int}}},\, \tfrac{c(N)}{\pi_d}\Big) + \tfrac{\sigma N}{\beta_{io}}.$$

Pushdown's **ideal speedup** is bounded by $\rho$ when the operator is bandwidth-bound and selective ($\sigma\to 0$): $T_{\text{host}}/T_{\text{dev}} \le \rho$, an **Amdahl-type ceiling**. When the device is compute-bound ($c(N)/\pi_d$ dominates), speedup is capped at $\pi_d/\pi_h < 1$ — i.e., pushdown *hurts*. The crossover is the $\sigma^\star$ solving $T_{\text{host}} = T_{\text{dev}}$. The model rests on the **roofline model** (Williams–Waterman–Patterson), the **I/O / external-memory model** (Aggarwal–Vitter) for counting block transfers across the interface, and **Amdahl/Gustafson** scaling laws for the speedup ceiling. Energy variants use $E = P_{\text{static}}T + \sum_i e_i \cdot \text{ops}_i$ and compare host vs device energy-delay product.

## 3. State of the Art (SOTA)

- **Models:** roofline-based pushdown advisors in **PushdownDB** (MIT, VLDB 2020) and **Smart-SSD** cost models (Do et al., SIGMOD 2013). **Summarizer** and **Biscuit** include analytic models for communication-vs-compute trade. SNIA's Computational Storage architecture frames device-internal vs interface bandwidth as the key lever.
- **Calibration:** measured $\rho$ ranges from $\sim 2\times$ (SATA/SAS) to $\sim 4$–$8\times$ for multi-channel NVMe internal bandwidth vs PCIe lanes; CXL/near-memory pushes $\rho$ higher. Most systems use *measured* crossovers per device rather than a portable model — the portable, provably-bounded model is the open gap.

## 4. Upper Bound

The **provable upper bound on speedup is $\rho = \beta_{\text{int}}/\beta_{io}$** for a single bandwidth-bound, perfectly selective operator in the roofline model — no in-storage execution can beat the ratio of internal to interface bandwidth, since the host must still receive at least the (possibly empty) result and the device cannot read faster than $\beta_{\text{int}}$. For aggregation ($\sigma N \to$ tiny scalar), the bound tightens to $\approx \rho$ on the read-dominated portion. Algorithmically, given accurate parameters the decision and ratio are computable in $O(1)$ per operator; the modeling challenge is *parameter accuracy*, not computational complexity.

## 5. Lower Bound

Two lower-bound flavors apply. (1) **Information-theoretic / I/O:** any execution must transfer the operator's input across *some* level; in the external-memory model the host-visible traffic is $\ge \sigma N / \beta_{io}$ (final result must arrive), so speedup is bounded above by $\rho$ — equivalently a *lower bound on $T_{\text{dev}}$*. (2) **Modeling impossibility:** because $c(N)$, $\sigma$, and effective $\beta_{\text{int}}$ are data- and access-pattern-dependent, no fixed-parameter model is exact across workloads; a worst-case adversary choosing data layouts can make any static crossover prediction err by a constant factor — an empirical robustness lower bound, not a complexity one. There is no NP-hardness here; the difficulty is predictive accuracy and tightness of the $\rho$ ceiling under real interference.

## 6. The Gap

The ceiling ($\rho$) is **known and tight in theory**, but real systems achieve a *fraction* of $\rho$ because of device contention, firmware overhead, partial selectivity, and queuing. The open problem is a **portable, calibrated model** that predicts the achieved fraction within tight error and exposes closed-form crossovers — and a matching argument for how close to $\rho$ a well-designed device can get under concurrent load. This is **genuinely open**: closing it needs both better device-internal performance modeling (queuing/contention) and validation that the $\rho$ bound is approached, not just asymptotically possible.

## 7. Current Research (as of June 2026)

- Queuing-theoretic extensions of the roofline for concurrent in-device operators *(frontier — verify)*.
- CXL-attached near-memory accelerators where $\rho$ and latency must be re-modeled *(frontier — verify)*.
- Energy-delay-product models for pushdown, motivated by datacenter power limits.
- Auto-calibrating cost models that learn device parameters from microbenchmarks at load time.
- Groups: MIT (PushdownDB lineage), ETH Zürich (Alonso), UCSD (Swanson), SNIA CS working group.

## 8. Future Work

- A validated model predicting achieved-vs-$\rho$ fraction under contention with bounded error.
- Closed-form crossover selectivities for joins/groups, not just scans/filters.
- Energy-aware pushdown bounds and Pareto frontiers.
- Standardized microbenchmarks to calibrate the model portably across CSD vendors.

## 9. Key References

- **[Foundational]** Williams, S., Waterman, A., Patterson, D. *Roofline: An Insightful Visual Performance Model for Multicore Architectures.* CACM, 2009. — [DOI](https://doi.org/10.1145/1498765.1498785)
- **[Foundational]** Aggarwal, A., Vitter, J. S. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[SOTA]** Do, J., Kee, Y.-S., Patel, J. M., Park, C., Kim, K., DeWitt, D. J. *Query Processing on Smart SSDs.* SIGMOD, 2013. — [DOI](https://doi.org/10.1145/2463676.2465295)
- **[SOTA]** Yu, X., Lu, Y., Stonebraker, M., et al. *PushdownDB: Accelerating a DBMS Using S3 Computation.* ICDE, 2020. — [DOI](https://doi.org/10.1109/ICDE48307.2020.00174) · [arXiv](https://arxiv.org/abs/2002.05837)
- **[Survey]** Barbalace, A., Do, J. *Computational Storage: Where Are We Today?* CIDR, 2021. — [DBLP](https://dblp.org/rec/conf/cidr/BarbalaceD21.html) · [PDF](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper29.pdf)

## 10. Worked Example

A computational SSD holds a 100 GB table; we run `SELECT COUNT(*) WHERE region = 'EU'`, a bandwidth-bound aggregation. Device-internal bandwidth $\beta_{\text{int}} = 8$ GB/s (8 NAND channels), host interface $\beta_{io} = 2$ GB/s (saturated PCIe lane share), so amplification $\rho = 8/2 = 4$. Selectivity $\sigma$ varies; the aggregate result is a single scalar, so $\sigma N \to 0$ bytes returned.

**Host execution** must drag all 100 GB across the interface: $T_{\text{host}} = N/\beta_{io} = 100/2 = 50$ s.

**Pushdown** reads internally and returns ~nothing: $T_{\text{dev}} = N/\beta_{\text{int}} + \sigma N/\beta_{io} \approx 100/8 = 12.5$ s. Speedup $= 50/12.5 = 4 = \rho$ — hitting the Amdahl-type ceiling exactly (Section 4).

Now a **filter** returning $\sigma = 0.5$ of the rows. $T_{\text{dev}} = 100/8 + (0.5\cdot 100)/2 = 12.5 + 25 = 37.5$ s vs host 50 s — speedup only $1.33$. Solving the crossover $T_{\text{host}} = T_{\text{dev}}$:

$$\frac{N}{\beta_{io}} = \frac{N}{\beta_{\text{int}}} + \frac{\sigma^\star N}{\beta_{io}} \;\Rightarrow\; \sigma^\star = 1 - \frac{\beta_{io}}{\beta_{\text{int}}} = 1 - \tfrac14 = 0.75.$$

So pushdown wins only when selectivity $\sigma < 0.75$; above that, shipping raw is no worse. This closed-form $\sigma^\star$ is precisely the optimizer-driving crossover the problem seeks.

---
*Part of the [DBMS Research catalog](../../README.md).*
