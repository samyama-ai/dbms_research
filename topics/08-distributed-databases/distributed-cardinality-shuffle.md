---
id: 08-distributed-databases/distributed-cardinality-shuffle
title: "Distributed Cardinality for Repartitioning"
topic: 08-distributed-databases
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Distributed Cardinality for Repartitioning

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/distributed-cardinality-shuffle` · **Status:** empirically-open

## 1. Problem Statement
To plan a distributed join, the optimizer must decide whether to **broadcast** the small side or **repartition (shuffle)** both sides, and how to size shuffle partitions. These choices hinge on **intermediate cardinalities** — the sizes of sub-results produced at each operator — which must be estimated *cheaply* and *across nodes* without materializing the intermediates. The problem: design distributed estimators that produce accurate (with error guarantees) intermediate-size estimates at sublinear communication/space cost, good enough to drive shuffle vs. broadcast and partition-count decisions.

Variants:
- **Estimation:** approximate $|R \bowtie S|$, distinct counts, and per-partition sizes within $(1\pm\epsilon)$ with confidence $1-\delta$.
- **Decision-driving:** given estimates with bounded error, choose the plan minimizing expected communication — and bound the *regret* from estimation error (intersection with broadcast-vs-shuffle).
- **Adaptive:** refine estimates mid-execution (runtime re-optimization).

## 2. Mathematical Foundations
Classic single-node estimation: histograms, distinct-value counts, and the textbook join-size formula $|R\bowtie_A S| \approx \frac{|R|\,|S|}{\max(d_A(R), d_A(S))}$ under uniformity/independence. Distributed sketches give rigorous guarantees:
- **HyperLogLog** estimates distinct count in $O(\epsilon^{-2})$ bits, *mergeable* across nodes (union of registers), error $\approx 1.04/\sqrt{m}$.
- **AGM / fractional-cover bound** $|Q| \le \prod_e |R_e|^{x_e}$ gives a provable worst-case ceiling for join output without data peeking.
- **AMS / second-moment sketches** estimate self-join size $F_2 = \sum_k f_k^2$ (hence join size via $\sum_k r_k s_k$ through sketch inner products) in $O(\epsilon^{-2}\log(1/\delta))$ space, linear and mergeable.
- **Count-Min / CountSketch** support per-key and inner-product (join-size) estimation distributively.

Mergeability (sketches compose under set union with bounded error) is the key property enabling cross-node estimation in one aggregation round. Error propagation through a multi-join plan is multiplicative, making deep-plan estimates fragile.

## 3. State of the Art (SOTA)
- **Theory:** AGM bound (Atserias–Grohe–Marx, FOCS 2008) for worst-case output; sketch-based join-size estimation (Alon–Gibbons–Matias–Szegedy; Rusu–Dobra). Distinct counting via HyperLogLog (Flajolet et al., 2007) and its mergeable variants used in BigQuery/Spark.
- **Learned estimators:** *learned cardinality estimation* — MSCN (Kipf et al., CIDR 2019), deep-autoregressive *NeuroCard / Naru* (Yang et al., VLDB 2019/2020), and Bayesian/sum-product networks (DeepDB, Hilprecht et al., VLDB 2020).
- **Systems:** Spark *Adaptive Query Execution* (re-optimizes shuffle/partition sizes at runtime using exact shuffle statistics), Snowflake/BigQuery sketch-based stats, Presto/Trino cost-based optimizer, *Microsoft SCOPE* mid-query re-optimization. Runtime feedback (LEO, Db2) corrects estimates with observed cardinalities.

## 4. Upper Bound
Mergeable sketches give provable bounds achievable distributively in **one aggregation round**: distinct counts within $(1\pm\epsilon)$ in $O(\epsilon^{-2})$ space per node (HLL); join/self-join size within $(1\pm\epsilon)$ with probability $1-\delta$ in $O(\epsilon^{-2}\log(1/\delta))$ space (AMS), composing across $p$ nodes with total communication $O(p\cdot \text{sketch size})$. The AGM bound is computable from per-relation sizes with negligible communication and gives a guaranteed upper envelope. Spark AQE achieves *exact* per-partition sizes for already-materialized shuffle stages, sidestepping estimation for the next stage at the cost of a materialization barrier.

## 5. Lower Bound
- **Single-pass distinct count:** any algorithm estimating distinct elements within $(1\pm\epsilon)$ needs $\Omega(\epsilon^{-2} + \log n)$ space (Indyk–Woodruff; Kane–Nelson–Woodruff) — sketch sizes are essentially optimal.
- **Join-size / $F_2$:** $\Omega(\epsilon^{-2})$ space lower bound for $(1\pm\epsilon)$ second-moment estimation; multiplicative join-size estimation over multiple joins has no sublinear-error guarantee in general (error compounds).
- **Worst case:** without data-dependent statistics, the only *provable* bound is AGM, which can be loose by orders of magnitude on real (correlated) data — a fundamental accuracy ceiling for statistics-free estimation.
- **Communication:** estimating $|R\bowtie S|$ to constant factor can require $\Omega(p)$ communication when skew is adversarial.

## 6. The Gap
Worst-case-tight sketches exist for *single* operators, but **end-to-end multi-join intermediate estimation on real, correlated data has no tight accuracy guarantee** — the status is *empirically-open*: learned estimators win on benchmarks but lack worst-case bounds and can fail catastrophically out of distribution, while provable sketches are accurate only per-operator and degrade through deep plans. No estimator simultaneously offers (a) sublinear distributed cost, (b) provable end-to-end error, and (c) robustness to correlation/skew. Closing the gap likely requires hybrid estimators with conditional guarantees, or theory characterizing achievable error vs. communication for multi-join plans.

## 7. Current Research (as of June 2026)
- Learned + sketch hybrids with error bounds and out-of-distribution safeguards *(frontier — verify)*.
- Runtime/adaptive re-optimization (Spark AQE successors, Velox, Photon) treating estimation as a control problem.
- Robust/pessimistic cardinality estimation using degree sequences and *bound sketches* (e.g., refinements of the AGM/"pessimistic" estimators of Cai–Balazinska–Suciu).
- Distributed estimators co-designed with skew detection and broadcast/shuffle decisions.
- Groups: Suciu/Balazinska (UW, pessimistic estimators), Kemper/Neumann/Leis (TUM), Kraska/MIT (learned components), Databricks/Snowflake query teams, Cormode (sketching).

## 8. Future Work
- Provable end-to-end error bounds for multi-join plans under realistic correlation models.
- Communication-vs-accuracy lower bounds specific to distributed intermediate estimation.
- Estimation-aware plan robustness: planning to minimize regret under estimate uncertainty.
- Unifying pessimistic (AGM-style) and learned estimators with calibrated confidence.

## 9. Key References
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008. (AGM bound.) — [arXiv](https://arxiv.org/abs/1711.03860)
- **[Foundational]** N. Alon, P. Gibbons, Y. Matias, M. Szegedy. *Tracking Join and Self-Join Sizes in Limited Storage.* PODS, 1999. — [DOI](https://doi.org/10.1145/303976.303978)
- **[Foundational]** P. Flajolet, É. Fusy, O. Gandouet, F. Meunier. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA, 2007. — [DMTCS](https://dmtcs.episciences.org/3545)
- **[SOTA]** A. Kipf, T. Kipf, B. Radke, V. Leis, P. Boncz, A. Kemper. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning.* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677)
- **[SOTA]** W. Cai, M. Balazinska, D. Suciu. *Pessimistic Cardinality Estimation: Tighter Upper Bounds for Intermediate Join Cardinalities.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3319894)
- **[Survey]** V. Leis et al. *How Good Are Query Optimizers, Really?* VLDB, 2015. (Estimation error empirics.) — [DOI](https://doi.org/10.14778/2850583.2850594)

## 10. Worked Example

Plan a join of $R(A,B)$ and $S(A,C)$ across $p = 4$ nodes. Suppose $|R| = 10^6$, $|S| = 2\times10^4$, and the optimizer must choose **broadcast $S$** vs **repartition both on $A$**.

First estimate the join size. Distinct values of $A$: merge each node's HyperLogLog ($m = 1024$ registers, error $\approx 1.04/\sqrt{1024} \approx 3.3\%$) by register-wise max, yielding $\hat d_A \approx 5\times10^3$. The textbook formula gives
$$|R\bowtie_A S| \approx \frac{|R|\,|S|}{\max(d_A(R), d_A(S))} = \frac{10^6 \cdot 2\times10^4}{5\times10^3} = 4\times10^6.$$

**Decision:** broadcasting $S$ ships $|S|\cdot(p-1) = 2\times10^4 \cdot 3 = 6\times10^4$ tuples and avoids reshuffling $R$'s $10^6$ tuples — far cheaper than repartitioning both ($\approx 1.02\times10^6$ tuples moved). Since $|S| \ll |R|$ and the estimated output is moderate, broadcast wins. The AGM ceiling $|R|\cdot|S| = 2\times10^{10}$ is here $5000\times$ looser than the estimate — illustrating why statistics-free bounds alone misguide the planner.

---
*Part of the [DBMS Research catalog](../../README.md).*
