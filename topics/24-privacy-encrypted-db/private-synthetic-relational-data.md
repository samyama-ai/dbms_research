# Private Synthetic Relational Data with Utility Guarantees

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/private-synthetic-relational-data` · **Status:** partially-solved

## 1. Problem Statement

Differentially private **synthetic data** generates a fake dataset $\tilde D$ from real data $D$ such that $\tilde D$ is $(\varepsilon,\delta)$-DP and yet answers a target class of queries about $D$ accurately. For a *single table*, marginal-based methods are mature. The hard, **multi-table relational** case is the open frontier: synthetic data must preserve **join keys and foreign-key structure**, so that **join queries and aggregates over joins** (the workloads analysts actually run) remain accurate — not just per-table marginals. The problem: generate DP synthetic *relational* (multi-table) data with **provable utility guarantees** for a class of join/aggregate queries, controlling how error compounds across joins.

Variants:
- **Single-table marginal-preserving (largely solved):** answer a workload of $k$-way marginals/counts within bounded error.
- **Multi-table with FK constraints (open):** preserve join cardinalities and post-join aggregates.
- **Decision:** given a target accuracy and $\varepsilon$, decide feasibility for a given schema/workload.

## 2. Mathematical Foundations

For a linear query workload $W$ (a matrix mapping the data histogram $x\in\mathbb{N}^{|\mathrm{dom}|}$ to answers $Wx$), DP synthetic-data error is governed by the **matrix mechanism / projection mechanism** and by **discrepancy** lower bounds. The marginal approach models a distribution $P_\theta$ over the domain (often a **graphical model** / Markov random field selected from DP-noised low-order marginals — the PGM approach), then samples $\tilde D \sim P_\theta$. Utility for a marginal query is $\|W\hat x - Wx\|$ where $\hat x$ is the model's implied histogram. For **joins**, sensitivity is the killer: a single row can participate in many join tuples, so the relevant sensitivity is **multiplicity-bounded** and the AGM bound $|R_1\bowtie\cdots\bowtie R_m|\le \prod \rho_e$ (Atserias–Grohe–Marx) governs worst-case blowup; error on a join aggregate compounds multiplicatively across the join tree. The domain size $|\mathrm{dom}|$ is exponential in attributes, so the genuinely hard sub-problem is *selecting which low-order statistics to measure* (marginals / FK-co-occurrences) under a budget — a combinatorial model-selection problem.

## 3. State of the Art (SOTA)

- **Theory-SOTA (single table):** The **MWEM** mechanism (Hardt, Ligett, McSherry, NeurIPS 2012) — multiplicative-weights + exponential mechanism — answers an arbitrary linear-query workload with error scaling polylogarithmically in the number of queries; foundational for the "answer a workload" formulation. **Private PGM** (McKenna, Sheldon, Miklau, ICML 2019) estimates a graphical model from noisy marginals and is the engine behind multiple competition-winning methods. **AIM** (McKenna et al., VLDB 2022) adaptively selects marginals and won NIST-style benchmarks.
- **Systems-SOTA:** NIST DP synthetic-data challenge winners (PGM-based), **DPGAN/PATE-GAN** style deep generators (weaker formal utility), and **MST** (Maximum Spanning Tree marginals). For **relational/multi-table**, work is nascent: relational extensions select FK-aware marginals and chain per-table models along the schema's join graph.

## 4. Upper Bound

For a workload of $k$ linear queries on a single table, MWEM/projection mechanisms achieve expected error $\tilde O\!\big(n^{2/3}(\log k)^{1/3}/\varepsilon^{1/3}\big)$ (and better for structured workloads), with the projection mechanism near-optimal for $\ell_2$ workloads. Private PGM/AIM give strong empirical utility on all-low-order marginals with budget split across measured marginals via convex optimization. For **multi-table**, the best provable guarantees apply when the join is **acyclic / bounded-treewidth**: error on join-aggregate queries is bounded in terms of the per-table marginal error times a join-tree-width-dependent factor, but **tight bounds for cyclic joins are not known** — this is why the status is *partially-solved*.

## 5. Lower Bound

DP linear-query release has a **discrepancy / hereditary-discrepancy lower bound** (Muthukrishnan–Nikolov; Nikolov–Talwar–Zhang, STOC 2013): error is $\Theta(\mathrm{herdisc}(W)/\varepsilon)$ up to polylog, tightly characterizing $\ell_2$ workload error. Releasing all $k$-way marginals accurately is information-theoretically hard for large $k$ (exponential domain). For joins, sensitivity is **unbounded** without row-multiplicity caps, and the AGM/worst-case join-size bound forces either truncation (bias) or large noise. Reconstruction lower bounds (Dinur–Nissim) cap how much accurate linear information any DP synthetic dataset can carry.

## 6. The Gap

The gap is **partially closed for single tables, open for relational data**. Single-table marginal workloads have matching discrepancy-tight bounds and excellent practical methods (PGM/AIM). For **multi-table**: there is no general algorithm with provable utility for join-aggregate workloads over arbitrary (esp. cyclic / many-to-many) schemas, and the right *sensitivity model* (how to bound a row's join multiplicity DP-soundly without crippling bias) is unsettled. Closing it needs a join-aware sensitivity/utility theory connecting AGM-style join bounds to DP error, plus model-selection over FK-co-occurrence statistics with guarantees.

## 7. Current Research (as of June 2026)

- FK-aware / schema-following synthetic generators that chain Private-PGM models along the join graph with budget allocated per relationship *(frontier — verify)*.
- DP synthetic data with **downstream-query-aware** objectives (optimize for a declared join/aggregate workload rather than generic marginals) *(frontier — verify)*.
- Bridging **worst-case optimal join** sensitivity (Ngo–Re–Rudra lineage) with DP noise calibration for relational release.
- Groups: Miklau/McKenna/Sheldon (PGM/AIM), Machanavajjhala/He (relational DP), NIST PSCR benchmark community.

## 8. Future Work

- Provable utility for join-aggregate workloads over cyclic and many-to-many schemas.
- Tight sensitivity bounds via row-multiplicity / truncation with bias–variance control.
- Unified discrepancy-style lower bounds for *relational* workloads.
- Scaling graphical-model synthesis to large, high-arity schemas.

## 9. Key References

- **[Foundational]** Hardt, Ligett, McSherry. *A Simple and Practical Algorithm for Differentially Private Data Release (MWEM).* NeurIPS, 2012. — [arXiv](https://arxiv.org/abs/1012.4763)
- **[Foundational]** Nikolov, Talwar, Zhang. *The Geometry of Differential Privacy: The Sparse and Approximate Cases (discrepancy bounds).* STOC, 2013. — [DOI](https://doi.org/10.1145/2488608.2488652) — [arXiv](https://arxiv.org/abs/1212.0297)
- **[SOTA]** McKenna, Sheldon, Miklau. *Graphical-model based Estimation and Inference for Differential Privacy (Private-PGM).* ICML, 2019. — [arXiv](https://arxiv.org/abs/1901.09136)
- **[SOTA]** McKenna, Miklau, Sheldon, et al. *AIM: An Adaptive and Iterative Mechanism for Differentially Private Synthetic Data.* VLDB, 2022. — [arXiv](https://arxiv.org/abs/2201.12677) — [DOI](https://doi.org/10.14778/3551793.3551817)
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* SIAM J. Computing / FOCS, 2008. — [DOI](https://doi.org/10.1137/110859440) — [arXiv](https://arxiv.org/abs/1711.03860)
- **[Survey]** Bowen, Liu. *Comparative Study of Differentially Private Data Synthesis Methods.* Statistical Science, 2020. — [DOI](https://doi.org/10.1214/19-STS742) — [arXiv](https://arxiv.org/abs/1602.01063)

## 10. Worked Example

Schema: `Customer(cid, region)` and `Order(oid, cid, amount)`, FK `Order.cid → Customer.cid`. Real data: 100 customers, region $\in\{N,S\}$ split $60/40$; each customer has $0$–$5$ orders. Target workload: `SELECT region, COUNT(*) FROM Order JOIN Customer USING(cid) GROUP BY region`.

Single-table marginals are easy: a DP histogram of `region` gives $\hat n_N = 60 \pm \mathrm{Lap}(1/\varepsilon)$. The trouble is the **join**. One customer with $5$ orders contributes $5$ join tuples, so the sensitivity of the per-region order count is the **max join multiplicity** $\Delta=5$, not $1$. Naively adding $\mathrm{Lap}(\Delta/\varepsilon)$ inflates noise $5\times$; truncating each customer to $\le 2$ orders caps $\Delta=2$ but biases the count downward.

Suppose true join counts are $(N\!:\!180,\ S\!:\!120)$. With multiplicity cap $\tau=2$ we keep at most $2$ orders/customer, true capped counts become $(N\!:\!110,\ S\!:\!75)$ — a large bias — then add $\mathrm{Lap}(2/\varepsilon)$. The bias–variance tension here is exactly the open problem: there is no general rule choosing $\tau$ that bounds *join-aggregate* error with provable utility on many-to-many schemas.

---
*Part of the [DBMS Research catalog](../../README.md).*
