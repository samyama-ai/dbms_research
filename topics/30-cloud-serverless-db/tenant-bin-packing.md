---
id: 30-cloud-serverless-db/tenant-bin-packing
title: "Bin-packing tenants to minimize machines"
topic: 30-cloud-serverless-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Bin-packing tenants to minimize machines

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/tenant-bin-packing` · **Status:** open

## 1. Problem Statement
A DBaaS provider hosts many tenants, each a database with a resource footprint (CPU, memory, IOPS, connections, storage) that **varies over time**. **Tenant consolidation** packs tenants onto the fewest physical nodes (bins) such that, on every node, aggregate demand stays within capacity *with high probability* (to meet SLOs), tenants are sufficiently **isolated** (security/noisy-neighbor), and **resource correlations** (tenants that spike together) don't co-locate dangerously.

Variants:
- **Decision:** can $n$ tenants fit on $m$ machines respecting all constraints?
- **Optimization:** minimize machines (or \$/carbon) used.
- **Online/dynamic:** tenants arrive/leave and resize; minimize machines *and* live-migration churn.
- **Stochastic/robust:** demands are random; pack so per-node overflow probability $\le \epsilon$.

Unlike classic bin packing, items are **multidimensional**, **stochastic & correlated**, **time-varying**, and subject to **conflict (anti-affinity)** constraints — making it a hard, genuinely **open** optimization in its realistic form.

## 2. Mathematical Foundations
Classic **bin packing**: items of size $s_i\in(0,1]$ into unit bins, minimize bins — strongly NP-hard, with an asymptotic PTAS / AFPTAS (Karmarkar–Karp). The tenant problem layers on:

- **Vector bin packing** ($d$ resources): items $\vec{s}_i\in[0,1]^d$, bins have capacity $\vec{1}$; pack so $\sum_{i\in B}\vec{s}_i \le \vec{1}$. Approximable to $O(\ln d)$ but **hard to approximate within $d^{1-\epsilon}$** for large $d$.
- **Stochastic/robust packing:** demand $X_i$ random; feasibility requires $\Pr[\sum_{i\in B} X_i > C]\le \epsilon$. Using concentration (Hoeffding/Bernstein/Chernoff), an item's *effective size* is $\mu_i + z_\epsilon \sigma_i^{\text{eff}}$; for **correlated** demands the effective bin load depends on the covariance $\Sigma$, so packing must respect $\mu^\top x + z_\epsilon\sqrt{x^\top \Sigma x}\le C$ — a **second-order-cone (chance) constraint**, not linear. Negatively correlated tenants can be co-located cheaply; positively correlated cannot.
- **Conflict constraints:** anti-affinity is **bin packing with conflicts** = packing on a conflict graph $G$; bins are independent sets, so it generalizes **graph coloring** (hard even to approximate).
- **Online** dynamic packing connects to **competitive ratio**; minimizing migrations adds a metric/MPC (online with switching cost) flavor.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Microsoft **SQL DB / Azure** elastic-pool consolidation and the **P-Store / SQLVM / "Sharing Buffer Pool"** line; Snowflake/Salesforce multi-tenant pod packing; Google **Autopilot** (resource right-sizing) and **Borg** bin packing; **DBSeer**-style workload modeling for consolidation; Microsoft Research's *robust tenant placement under resource correlation* (Das, Narasayya et al.). VMware/cloud VM packing (e.g., **Protean** at Azure) is the closest production analog.
- **Theory-SOTA:** Karmarkar–Karp AFPTAS for 1-D; vector-packing approximations (Chekuri–Khanna, Bansal–Eliáš–Khan); **stochastic bin packing** with chance constraints (Goel–Indyk; Kleinberg–Rabani–Tardos for bursty/correlated); bin packing with conflicts (Jansen).

## 4. Upper Bound
- **1-D:** AFPTAS — $(1+\epsilon)\text{OPT}+O(1/\epsilon^2)$ bins (Karmarkar–Karp).
- **$d$-D vector packing:** poly-time $O(\ln d)$-approximation; first-fit-type heuristics give $d+\epsilon$.
- **Stochastic (independent, bounded):** $(1+\epsilon)$-type guarantees via effective-size + concentration (Kleinberg–Rabani–Tardos give bicriteria bounds for bursty demands).
- **With conflicts:** approximation tracks the conflict graph's colorability — constant-factor on perfect/interval graphs, $O(\log n)$-type otherwise.
- Practical robust placement (MSR) hits machine counts within a few percent of LP lower bounds on real workloads.

## 5. Lower Bound
- **1-D bin packing is strongly NP-hard**; no algorithm uses $\le (3/2-\epsilon)\text{OPT}$ bins in the worst case unless P=NP (absolute ratio), via PARTITION.
- **Vector bin packing** is **NP-hard to approximate within $d^{1-\epsilon}$** for $d$ growing (Chekuri–Khanna / later strengthenings) — the curse of dimensionality is provable.
- **With conflicts**, the problem contains **graph coloring**, hence NP-hard to approximate within $n^{1-\epsilon}$.
- **Online** bin packing has competitive-ratio lower bound $\ge 1.54$ (Balogh et al.), and online with correlated stochastic demands inherits these.

## 6. The Gap
For the **realistic** tenant problem — multidimensional + correlated-stochastic + conflict + online with migration cost — there is **no algorithm with proven guarantees on the full constraint set**, and strong inapproximability (vector + coloring) suggests none with constant factor exists. The gap is not a missing constant in 1-D (that is essentially closed); it is the absence of a tractable model/algorithm that *jointly* handles correlation-aware chance constraints, isolation conflicts, and online resizing with provable bounds. This is genuinely **open**; even the *right robust objective* (which percentile, which correlation estimator) is unsettled.

## 7. Current Research (as of June 2026)
- **Correlation-aware robust packing** with learned demand distributions and covariance estimation; chance-constrained / SOCP placement at scale *(frontier — verify)*.
- **Learning-augmented online packing** minimizing both machines and live-migration churn (switching-cost-aware).
- **Serverless scale-to-zero** packing: tenants that idle to zero change the packing calculus (pack many idle tenants, burst a few).
- Joint **packing + carbon/cost** objectives (links to carbon-aware scheduling).
- Microsoft Research, Google, and Azure systems teams on right-sizing + consolidation co-design.

## 8. Future Work
- A unified robust-online model with provable bicriteria (machines, SLO-violation) bounds.
- Tractable correlation-aware effective-size theory with statistical guarantees.
- Migration-cost-aware repacking with competitive bounds.
- Truthful packing when tenants misreport footprints (mechanism design).

## 9. Key References
- **[Foundational]** Narendra Karmarkar, Richard M. Karp. *An Efficient Approximation Scheme for the One-Dimensional Bin-Packing Problem.* FOCS, 1982. — [DOI](https://doi.org/10.1109/SFCS.1982.61)
- **[Foundational]** Chandra Chekuri, Sanjeev Khanna. *On Multidimensional Packing Problems.* SIAM J. Computing, 2004. — [DOI](https://doi.org/10.1137/S0097539799356265)
- **[Foundational]** Jon Kleinberg, Yuval Rabani, Éva Tardos. *Allocating Bandwidth for Bursty Connections.* SIAM J. Computing, 2000 (stochastic/bursty packing). — [DOI](https://doi.org/10.1137/S0097539797329142)
- **[SOTA]** Sudipto Das, Vivek Narasayya, Feng Li, Manoj Syamala. *CPU Sharing Techniques for Performance Isolation in Multi-tenant Relational Database-as-a-Service.* VLDB, 2013 (and the MSR multi-tenant placement line). — [DOI](https://doi.org/10.14778/2732219.2732223)
- **[SOTA]** Ori Hadary, et al. *Protean: VM Allocation Service at Scale.* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/hadary)
- **[Survey]** Henrik I. Christensen, Arindam Khan, Sebastian Pokutta, Prasad Tetali. *Approximation and Online Algorithms for Multidimensional Bin Packing: A Survey.* Computer Science Review, 2017. — [DOI](https://doi.org/10.1016/j.cosrev.2016.12.001)

## 10. Worked Example

Three tenants with stochastic CPU demand (capacity per node $C=1.0$), means and standard deviations:

| Tenant | $\mu_i$ | $\sigma_i$ |
|---|---|---|
| A | 0.40 | 0.10 |
| B | 0.35 | 0.10 |
| C | 0.30 | 0.15 |

**Mean-only packing** sums to $0.40+0.35+0.30 = 1.05 > 1.0$, so all three never fit on one node by means alone.

**Chance constraint** ($\epsilon = 2.3\%$, so $z_\epsilon = 2$). Try co-locating A+B, assuming independence ($\Sigma$ diagonal): effective load
$$ \mu_A+\mu_B + z_\epsilon\sqrt{\sigma_A^2+\sigma_B^2} = 0.75 + 2\sqrt{0.01+0.01} = 0.75 + 0.283 = 1.033 > 1.0. $$
Infeasible — A+B overflow with probability $>2.3\%$. But if A and B are **negatively correlated** ($\rho=-0.6$), the variance term becomes $x^\top\Sigma x = 0.01+0.01+2(-0.6)(0.1)(0.1)=0.008$, giving $0.75+2\sqrt{0.008}=0.929 \le 1.0$ — now feasible on one node. This shows why correlation, not just mean size, drives the packing: identical means but $\rho=-0.6$ vs $\rho=0$ flips A+B from 3 nodes to 2.

---
*Part of the [DBMS Research catalog](../../README.md).*
