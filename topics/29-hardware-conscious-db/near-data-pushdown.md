---
id: 29-hardware-conscious-db/near-data-pushdown
title: "Near-data processing operator pushdown"
topic: 29-hardware-conscious-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Near-data processing operator pushdown

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/near-data-pushdown` · **Status:** empirically-open

## 1. Problem Statement

Computational storage devices (CSDs) — SSDs/NICs/DIMMs with embedded compute (ARM cores, FPGA, or fixed-function ASICs) — let a DBMS **push operators down to where data lives**, cutting data movement across the storage interface. But in-storage compute is weak (low clocks, little memory, no SIMD/vector richness of the host) and the win comes only from **bandwidth amplification**: a pushed filter/aggregate that reduces the result by selectivity $\sigma$ saves host-bound traffic proportional to $1-\sigma$, while paying in-device compute cost. The problem: **decide which operators (and which sub-plan fragments) to push into the device** so that total query latency/energy is minimized, given the device's limited compute throughput and the bandwidth gain from early reduction.

Variants: (i) **decision** — for a fixed plan, choose a subset of pushable operators meeting a latency budget; (ii) **optimization** — co-optimize the *plan shape* and the *push/no-push assignment*; (iii) **pipeline-aware** — pushdown alters the host plan's input cardinalities, so the decision is coupled to cardinality estimation; (iv) **multi-device/scheduling** — many CSDs in parallel, balancing device compute against host.

## 2. Mathematical Foundations

Model the system as two compute tiers with throughputs $\pi_h$ (host) and $\pi_d \ll \pi_h$ (device), connected by an interface of bandwidth $\beta_{io}$. An operator $o$ reads $N$ bytes, costs $c_o(N)$ cycles, and emits $\sigma_o N$ bytes. Pushing $o$ to the device is beneficial roughly when

$$\frac{N}{\beta_{io}} + \frac{c_o(N)}{\pi_h} \;>\; \frac{c_o(N)}{\pi_d} + \frac{\sigma_o N}{\beta_{io}},$$

i.e., the saved interface traffic $(1-\sigma_o)N/\beta_{io}$ must exceed the device's compute slowdown $c_o(N)(1/\pi_d - 1/\pi_h)$. This is a **roofline/Amdahl** condition: pushdown helps only for **selective, compute-light, bandwidth-heavy** operators. Choosing a pushable subset along a pipeline where each operator's output is the next's input makes selectivities **multiplicative** and the objective non-linear; the assignment problem over a plan DAG is a **constrained partition / knapsack-on-a-DAG** that is NP-hard in general. Submodularity sometimes holds (diminishing returns of pushing more), enabling greedy $1-1/e$ guarantees when the saving function is monotone submodular under a device-capacity (knapsack/matroid) constraint.

## 3. State of the Art (SOTA)

- **Systems:** **Amazon S3 Select / Redshift Spectrum** and **PolarDB** push selection/projection into storage. **YourSQL** and **Biscuit** (Samsung, ISCA 2016) and **Summarizer** (MICRO 2017) pioneered in-SSD filtering. **Newport / Eideticom NoLoad** and SNIA's Computational Storage standard (NVMe TP4091 / CS) define a programmable substrate. **PushdownDB** (Yu et al., VLDB 2020) systematically studies which operators to push to S3.
- **Research engines:** **Polaris / Caribou** (ETH), **INSIDER** (UCSD, ATC 2019), and **Solros**-style splits. Cost-based pushdown advisors exist but rely on coarse heuristics; the *which-operators* decision under tight device limits is the empirically open core.

## 4. Upper Bound

No tight asymptotic bound; the practical optimum is the roofline-feasible assignment. For a **single operator**, the decision is $O(1)$ given accurate $\sigma_o$, $c_o$. For a **pipeline/DAG** under a device-capacity constraint with monotone submodular savings, greedy achieves a $(1-1/e)$-approximation (Nemhauser–Wolsey–Fisher), and continuous-greedy/LP rounding can match it under matroid constraints. Exact optima come from ILP/DP over the plan DAG for small operator counts. PushdownDB-style measurements show end-to-end speedups of $1.5$–$30\times$ on selective S3 workloads *(frontier — verify magnitudes per workload)*.

## 5. Lower Bound

The general assignment is **NP-hard** by reduction from knapsack / partition (pack pushed operators under device compute budget to maximize traffic saved). When savings are *not* submodular (e.g., joins whose pushdown changes downstream cardinalities non-monotonically), no constant-factor guarantee is known and the problem can encode set-cover-like hardness, giving an $\Omega(\ln n)$ inapproximability flavor. There is no nontrivial *unconditional* lower bound isolating the achievable bandwidth-saving fraction — the gap between heuristic advisors and optimal pushdown is **empirical**, which is what keeps the problem empirically open rather than theoretically closed. The information-theoretic floor is the unavoidable traffic $\sigma_{\text{final}}\,N/\beta_{io}$ of the final result.

## 6. The Gap

For submodular savings under a capacity constraint, the gap is essentially **closed** ($(1-1/e)$ achievable, set-cover-hard to beat). The genuinely open part is (i) joins and stateful operators where pushdown reshapes cardinalities and submodularity fails, and (ii) the **dependence on accurate $\sigma_o$ and $c_o$** — estimation error can flip a push decision, so the practical gap is between an oracle-cost optimizer and a real one with imperfect cardinality estimates. Closing it needs robust pushdown under uncertain selectivity plus a model for stateful-operator savings.

## 7. Current Research (as of June 2026)

- SNIA/NVMe Computational Storage (CS) programmable namespaces maturing into a portable pushdown ISA *(frontier — verify standard status)*.
- Robust/learning-based pushdown advisors that hedge against selectivity misestimation.
- Pushdown for decompression + filter fused in-device (avoiding host decompress).
- Disaggregated/CXL near-memory pushdown blurring storage vs memory tiers.
- Groups: UCSD (Zhao/Swanson, INSIDER), ETH Zürich (Alonso), MIT (PushdownDB lineage), Samsung/SK Hynix CSD teams.

## 8. Future Work

- A cost model for stateful-operator (join/group) pushdown with provable savings bounds.
- Selectivity-robust assignment with bounded regret under estimation error.
- Co-optimizing plan shape and pushdown jointly inside the query optimizer.
- Multi-device scheduling balancing aggregate device compute vs host roofline.

## 9. Key References

- **[Foundational]** Nemhauser, G. L., Wolsey, L. A., Fisher, M. L. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)
- **[SOTA]** Yu, X., Lu, Y., Yao, N., Zhang, J., Stonebraker, M., et al. *PushdownDB: Accelerating a DBMS Using S3 Computation.* ICDE, 2020. — [arXiv](https://arxiv.org/abs/2002.05837) · [DOI](https://doi.org/10.1109/ICDE48307.2020.00174)
- **[SOTA]** Ruan, Z., He, T., Cong, J. *INSIDER: Designing In-Storage Computing System for Emerging High-Performance Drive.* USENIX ATC, 2019. — [USENIX](https://www.usenix.org/conference/atc19/presentation/ruan)
- **[Foundational]** Do, J., Kee, Y.-S., Patel, J. M., et al. *Query Processing on Smart SSDs: Opportunities and Challenges.* SIGMOD, 2013. — [DOI](https://doi.org/10.1145/2463676.2465295)
- **[SOTA]** Koo, G., et al. *Summarizer: Trading Communication with Computing Near Storage.* MICRO, 2017. — [DOI](https://doi.org/10.1145/3123939.3124553)
- **[Survey]** Barbalace, A., Do, J. *Computational Storage: Where Are We Today?* CIDR, 2021. — [PDF](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper29.pdf)

## 10. Worked Example

A `SELECT ... WHERE price > 100` filter scans $N = 10$ GB from a computational SSD. Interface bandwidth $\beta_{io} = 2$ GB/s. Host throughput $\pi_h = 10$ GB/s; weak device cores $\pi_d = 1$ GB/s. The filter's selectivity is $\sigma = 0.1$ (10% of rows pass), and its compute cost is $c(N) = N$ "byte-cycles."

**No pushdown:** transfer all 10 GB to host, then filter on host.
$$\frac{N}{\beta_{io}} + \frac{c(N)}{\pi_h} = \frac{10}{2} + \frac{10}{10} = 5 + 1 = 6\text{ s}.$$

**Pushdown:** filter in-device, transfer only $\sigma N = 1$ GB.
$$\frac{c(N)}{\pi_d} + \frac{\sigma N}{\beta_{io}} = \frac{10}{1} + \frac{1}{2} = 10 + 0.5 = 10.5\text{ s}.$$

Here pushdown *loses* — the wimpy device core ($\pi_d = 1$) dominates. The break-even from §2 requires the saved traffic $(1-\sigma)N/\beta_{io} = 9/2 = 4.5$ s to exceed the device slowdown $c(N)(1/\pi_d - 1/\pi_h) = 10(1 - 0.1) = 9$ s — it does not. But raise device speed to $\pi_d = 5$ GB/s and the slowdown term falls to $10(0.2-0.1)=1$ s $< 4.5$ s, flipping the decision to push. This is exactly the **selective, compute-light, bandwidth-heavy** condition.

---
*Part of the [DBMS Research catalog](../../README.md).*
