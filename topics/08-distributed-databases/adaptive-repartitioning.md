# Adaptive Repartitioning Mid-Query

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/adaptive-repartitioning` · **Status:** empirically-open

## 1. Problem Statement

A distributed query engine partitions relations across $p$ workers using a partitioning function (hash, range, or co-location). The chosen partitioning is fixed at planning time from (possibly stale) statistics. **Adaptive repartitioning** asks: given that during execution we observe the actual data distribution and discover the initial partitioning is suboptimal (e.g., causes skew, redundant shuffles, or breaks locality for a downstream operator), can we detect this and *re-shuffle mid-flight* with **provable amortized cost**?

- **Decision variant:** Given a partial execution trace and a cost model, decide whether repartitioning will reduce total cost below the no-action baseline.
- **Optimization variant:** Choose a new partitioning function $\pi'$ and a migration plan minimizing total work, including the migration's own shuffle cost, amortized over remaining operators.
- **Online variant:** The distribution is revealed incrementally; minimize *competitive ratio* against an offline optimum that knew the distribution up front.

The crux is that repartitioning is itself an expensive all-to-all operation, so a wrong decision can cost more than it saves.

## 2. Mathematical Foundations

Model the query as a DAG of operators $O_1,\dots,O_k$. Each operator runs under a partitioning $\pi_i: \text{dom}(R) \to [p]$. Tuple movement between $\pi_i$ and $\pi_{i+1}$ incurs a shuffle whose volume is the number of tuples whose worker assignment changes. Let $w_j(\pi)$ be the load on worker $j$; the stage cost is dominated by $\max_j w_j(\pi)$ (the straggler term) plus communication $\sum_j |\{\text{tuples crossing into } j\}|$.

Repartitioning is naturally an **online/competitive** problem akin to *metrical task systems* and *ski-rental*: pay a fixed reconfiguration cost $C$ now to lower the per-unit cost from $a$ to $b<a$ on the remaining $m$ tuples. The break-even is $C \le (a-b)\,m$, but $m$ is unknown — yielding the classic $2$-competitive deterministic / $\frac{e}{e-1}$-competitive randomized rent-or-buy structure.

Skew detection rests on estimating the partition load histogram with sublinear sketches; frequency-moment estimation ($F_2$, $F_\infty$) via AMS/Count-Sketch gives $(\varepsilon,\delta)$ guarantees in $O(\varepsilon^{-2}\log\delta^{-1})$ space.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Spark AQE (Adaptive Query Execution, Databricks, 2020) coalesces shuffle partitions and dynamically switches join strategies post-shuffle; Microsoft SCOPE / Peregrine and Snowflake perform runtime partition coalescing. Flink and Presto/Trino do limited adaptive skew-join splitting. These are heuristic, threshold-driven, with no amortized guarantee.
- **Theory-SOTA:** Eddies (Avnur–Hellerstein, SIGMOD 2000) pioneered per-tuple adaptive routing but without distributed-shuffle cost accounting. Recent work on *re-optimization* (Markl et al.) and progressive parametric optimization gives mid-query re-planning frameworks but treats repartitioning cost as a black box.

There is no algorithm with a proven competitive ratio for the full repartition-or-not online problem under realistic shuffle cost.

## 4. Upper Bound

For the simplified rent-or-buy abstraction (single decision, known $C,a,b$, unknown horizon $m$), the deterministic break-even rule is **$2$-competitive** and the randomized rule is **$\frac{e}{e-1}\approx 1.58$-competitive**. For multi-stage settings cast as a metrical task system over the discrete space of partitioning functions, generic MTS algorithms give $O(\log N)$-competitive bounds where $N$ is the number of candidate partitionings — but $N$ is exponential, so this is not directly useful. Practical systems achieve large empirical speedups (2–8×) on skewed workloads but offer only the trivial $O(1)$-factor-of-baseline guarantee in the worst case.

## 5. Lower Bound

Any deterministic online repartitioning algorithm is at least **$2$-competitive** (rent-or-buy lower bound), and randomized at least $\frac{e}{e-1}$, by reduction from ski-rental. Detecting the *need* to repartition with one-pass sublinear space inherits communication-complexity lower bounds: distinguishing skewed from uniform load to multiplicative precision requires $\Omega(\varepsilon^{-2})$ space for $F_2$ estimation (Indyk–Woodruff). No NP-hardness is needed — the difficulty is informational/online, not combinatorial, in the single-decision case; the *optimization* variant of choosing $\pi'$ to minimize migration + downstream cost is NP-hard by reduction from balanced graph partitioning.

## 6. The Gap

The single-decision online gap is **closed** (matching $2$ / $1.58$ bounds). The genuinely **open** gap is the *realistic multi-stage* problem: no algorithm couples (a) sublinear skew detection, (b) shuffle-cost-aware migration planning, and (c) a competitive guarantee against the full downstream DAG. Closing it requires a cost model where the reconfiguration cost itself depends on the chosen $\pi'$ and current placement — breaking the clean rent-or-buy separation. Whether an $O(1)$-competitive algorithm exists for the DAG-wide problem is open.

## 7. Current Research (as of June 2026)

- Databricks and Snowflake continue refining AQE with learned cardinality feedback loops *(frontier — verify)*.
- Academic interest in *learned* repartitioning triggers (reinforcement-learning controllers that decide reshuffle timing) is active in the ML-for-systems community (MIT DSAIL, CMU, TUM) *(frontier — verify)*.
- Theory groups are revisiting online algorithms with ML predictions ("algorithms with predictions") to beat worst-case competitive ratios for reconfiguration decisions — a natural fit since cardinality estimators give noisy predictions.

## 8. Future Work

- A competitive analysis for the DAG-wide repartitioning problem with migration-cost-dependent reconfiguration.
- Combining algorithms-with-predictions with consistency/robustness tradeoffs so a bad estimator never does worse than $2$-competitive.
- Sublinear, continuous skew monitors cheap enough to run on every shuffle exchange.
- Integration with co-partitioning so that repartitioning one relation accounts for join-locality of others.

## 9. Key References

- **[Foundational]** Ron Avnur, Joseph M. Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD, 2000.
- **[SOTA]** Maryann Xue et al. (Databricks). *Adaptive Query Execution in Apache Spark 3.0.* Databricks Engineering Blog / Spark Summit, 2020.
- **[Foundational]** Anna R. Karlin, Mark S. Manasse, Lyle A. McGeoch, Susan Owicki. *Competitive Randomized Algorithms for Nonuniform Problems (ski-rental / rent-or-buy).* Algorithmica, 1994.
- **[Foundational]** Allan Borodin, Nathan Linial, Michael Saks. *An Optimal On-Line Algorithm for Metrical Task Systems.* JACM, 1992.
- **[Survey]** Amol Deshpande, Zachary Ives, Vijayshankar Raman. *Adaptive Query Processing.* Foundations and Trends in Databases, 2007.
- **[SOTA]** Thodoris Lykouris, Sergei Vassilvitskii. *Competitive Caching with Machine Learned Advice.* JACM, 2021 (algorithms-with-predictions framework).

---
*Part of the [DBMS Research catalog](../../README.md).*
