# Load Balancing for Skewed Multi-way Joins

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/skew-optimal-mpc-load` · **Status:** partially-solved

## 1. Problem Statement
Evaluate a multi-way join $Q$ in a **single round** of the MPC model on $p$ machines such that the maximum per-machine load is provably minimized **even when join-attribute values are arbitrarily skewed** (a few "heavy" values appear in a constant fraction of tuples). The skew-free HyperCube guarantee degrades catastrophically under heavy hitters, so the goal is a partitioning that adapts share exponents per value.

Variants:
- **Worst-case load minimization:** minimize $\max_i \text{load}_i$ over all inputs of size $N$ with given degree statistics.
- **Instance-optimal:** match, up to polylog, the best possible load for *this* input given its skew profile.
- **Statistics-budgeted:** achieve the above when only approximate heavy-hitter statistics are available before the round.

## 2. Mathematical Foundations
Let the query hypergraph be $\mathcal{H}=(V,E)$ with fractional edge cover $u^*$ and value $\tau^*$. The skew-free one-round load is $L = O(N/p^{1/\tau^*})$. Skew is captured by **degrees**: $d_v(a)$ = number of tuples with value $a$ on attribute $v$. A value is *heavy* if $d_v(a) > N/p^{1/\tau^*}$.

The **SkewHC / residual-query** technique splits the input: light values use HyperCube with shares $p_v$ chosen by the LP $\sum_v \log_p p_v$ subject to cover constraints; heavy-value combinations form **residual queries** with fewer free attributes (lower $\tau^*$), recursively partitioned. The AGM bound $|Q|\le \prod_e |R_e|^{u_e^*}$ still bounds output and thus a load floor of $\Omega(|Q|^{1/?}/p)$. Information-theoretic lower bounds use the **isoperimetric / friendship-graph** argument adapted to skewed degree sequences.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Beame–Koutris–Suciu (JACM 2017) gave skew-aware one-round algorithms with load $\tilde O(N/p^{1/\tau^*})$ for *known* skew, matching lower bounds for several query classes (e.g., triangles, paths). Koutris–Suciu and later Hu refined residual-query handling. The general arbitrary-query, arbitrary-skew matching bound is **not fully closed**.
- **Systems-SOTA:** Spark's salted/skew-join hints, Flink adaptive shuffles, and **PRPD (Partial Redistribution & Partial Duplication)** in commercial MPP engines (Teradata-style) handle heavy hitters heuristically without optimality guarantees.

## 4. Upper Bound
For **triangle and other specific cyclic queries**, one-round load $\tilde O(N/p^{2/3})$ under arbitrary skew, matching the lower bound (BKS). For general $Q$ with known degree statistics, $\tilde O(N/p^{1/\tau^*})$ via SkewHC with residual decomposition (Koutris–Suciu, ICDT 2016). Output-sensitive refinements give $\tilde O(N/p^{1/\tau^*} + |Q|/p)$.

## 5. Lower Bound
Information-theoretic: $\Omega(N/p^{1/\tau^*})$ for one round, and stronger per-query bounds (e.g., $\Omega(N/p^{2/3})$ for triangles) hold even with full degree knowledge (BKS, JACM 2017). The model is **tuple-based one-round MPC**; bounds are unconditional within it. No matching upper bound is known for *arbitrary* cyclic queries under *arbitrary* skew without extra rounds.

## 6. The Gap
Closed for an important catalog (triangles, paths, stars, and many low-width queries). **Open** in general: there remain queries where the best known skew-aware one-round upper bound exceeds the lower bound by polynomial factors in $p$, and where required statistics may be expensive to gather. Hence the **partially-solved** status. Closing it needs a uniform residual-query LP whose value provably meets the per-instance lower bound for all queries.

## 7. Current Research (as of June 2026)
Hu and Yi (HKUST) push instance-optimal skewed joins; Suciu/Koutris continue the LP-share theory. **Learned / sketch-based heavy-hitter estimation** to pick share exponents online is an active systems-theory bridge *(frontier — verify)*. There is emerging work coupling worst-case-optimal join semantics with MPC skew handling for cyclic workloads *(frontier — verify)*.

## 8. Future Work
- A single algorithm achieving instance-optimal one-round load for *all* conjunctive queries under arbitrary skew.
- Tight bounds when only sublinear-space sketches of the degree distribution are available pre-round.
- Extending guarantees to bag semantics and aggregate (GROUP BY) skew.

## 9. Key References
- **[Foundational]** Beame, Koutris, Suciu. *Communication Steps for Parallel Query Processing.* JACM, 2017.
- **[SOTA]** Koutris, Beame, Suciu. *Worst-Case Optimal Algorithms for Parallel Query Processing.* ICDT, 2016.
- **[SOTA]** Hu, Yi. *Instance and Output Optimal Parallel Algorithms for Acyclic Joins.* PODS, 2019.
- **[Foundational]** Xu, Kostamaa, Gao. *Integrating Hash Joins... Skew Handling (PRPD).* SIGMOD, 2008.
- **[Survey]** Koutris, Suciu. *A Guide to Formal Analysis of Join Processing in MPP Systems.* SIGMOD Record, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
