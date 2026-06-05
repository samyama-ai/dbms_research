# Skew-Resilient Distributed Aggregation

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/skew-resilient-aggregation` · **Status:** partially-solved

## 1. Problem Statement

A distributed `GROUP BY ... AGG(...)` partitions tuples by group key across $p$ reducers. When group sizes are **skewed** — a few "heavy" keys hold a constant fraction of all tuples — the reducer owning a heavy key becomes a *hot reducer*, dominating stage latency while others idle. The problem: **compute group-by aggregates without a single hot reducer**, i.e., spread the work of heavy groups while still producing correct per-group results.

- **Decision variant:** Given group-size distribution and $p$ reducers, can the maximum reducer load be kept $\le L$?
- **Optimization variant:** Minimize the maximum reducer load (makespan) over all valid key-to-reducer assignments and splitting strategies.
- The difficulty depends on whether `AGG` is **decomposable/algebraic** (SUM, COUNT, MIN, MAX, AVG — partial aggregates combine associatively) or **holistic** (median, distinct-count — see the holistic-aggregates page).

## 2. Mathematical Foundations

Let group $g$ have size $|g|$ tuples. The default hash partitioning gives reducer load $= \sum_{g \mapsto j} |g|$; with one group of size $\Theta(N)$ this is $\Theta(N)$ regardless of $p$ — no parallelism. The problem is **makespan minimization on identical machines** (bin-packing / $P||C_{max}$): pack groups (jobs) into $p$ reducers (machines) minimizing the max load. This is NP-hard, with the **LPT** (longest-processing-time) and **multifit** approximations giving $\frac{4}{3}$ and $\frac{11}{9}$ ratios.

The escape hatch unique to aggregation: **decomposable aggregates can be pre-aggregated**. For algebraic aggregates a heavy group's tuples can be partially aggregated on *every* mapper (combiner), so a group of size $|g|$ produces only $O(p)$ partial states to merge — a tree/two-phase aggregation reduces reducer load for that group from $|g|$ to $O(p)$. Formally, an aggregate is *decomposable* if there exist $f_{\text{partial}}, f_{\text{merge}}$ with $\text{AGG}(A \cup B) = f_{\text{merge}}(f_{\text{partial}}(A), f_{\text{partial}}(B))$ (Gray et al.'s data-cube algebra: distributive/algebraic/holistic taxonomy).

Detecting heavy keys uses **heavy-hitters sketches** — Misra–Gries / Space-Saving / Count-Min give the $\phi$-heavy hitters in $O(1/\phi)$ space with $\varepsilon N$ error, identifying which groups need splitting without a full pass.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Two-phase (partial + final) aggregation with map-side combiners is standard in Spark, Flink, Presto/Trino, and classic MapReduce. Spark AQE adds *skew-join* and *skew-aggregate* handling that detects large partitions and splits them. "Salting" heavy keys (append a random suffix, aggregate, then re-aggregate) is the common production trick for decomposable aggregates.
- **Theory-SOTA:** Adaptive/skew-aware partitioning with provable load balance dates to parallel-DB work (DeWitt–Gray, "Parallel Database Systems," CACM 1992) and skew handling in parallel joins (Walton–Dale–Jenevein, VLDB 1991). Two-phase aggregation makes *decomposable* aggregation provably load-balanced to within the heavy-hitter splitting overhead.

## 4. Upper Bound

For **decomposable** aggregates, two-phase aggregation with heavy-key salting achieves max reducer load $O(N/p + p)$: the $N/p$ term is the balanced share, and the $p$ term is the cost of merging $O(p)$ partial states per heavy group — essentially optimal up to the additive $p$. Assigning the (now small) per-group partial states to reducers is $P||C_{max}$, solvable to a $\frac{4}{3}$-approximation by LPT or a PTAS (Hochbaum–Shmoys) since the problem admits a polynomial-time approximation scheme. So for algebraic aggregates the load-balancing problem is **near-closed**.

## 5. Lower Bound

Exact makespan minimization for assigning *indivisible* groups (holistic case, where a group's tuples cannot be pre-aggregated) is **NP-hard** by reduction from PARTITION/bin-packing, and *strongly* NP-hard for the multi-way version (3-PARTITION), ruling out an FPTAS. Information-theoretically, a single group of $m$ distinct-valued tuples whose aggregate is *holistic* (e.g., COUNT DISTINCT, MEDIAN) cannot be reduced below $\Omega(m)$ communication to one reducer in the worst case without approximation — a hard floor that pre-aggregation cannot beat for non-decomposable functions. Thus the lower bound bites precisely where decomposability fails.

## 6. The Gap

**Partially-solved.** For decomposable (distributive/algebraic) aggregates the gap is essentially closed: two-phase aggregation + salting + PTAS assignment is near-optimal. The remaining gap is for **holistic** aggregates and for **online/streaming** skew where the heavy keys shift over time and must be detected and re-balanced mid-query without a clairvoyant size distribution. Bridging these connects to the holistic-aggregates-in-MPC problem and to adaptive repartitioning. A clean characterization of the achievable load for holistic group-by under skew is open.

## 7. Current Research (as of June 2026)

- Learned / adaptive skew detection integrated with AQE (Databricks, TUM HyPer/Umbra lineage) *(frontier — verify)*.
- Skew handling for approximate holistic aggregates via mergeable sketches (KLL quantiles, HyperLogLog, theta-sketches) so even "holistic" aggregates become approximately decomposable.
- GPU and vectorized engines re-examining skew because hot groups break SIMD load balance *(frontier — verify)*.

## 8. Future Work

- Optimal load characterization for *exact* holistic group-by under skew.
- Online skew re-balancing with regret/competitive guarantees against shifting heavy hitters.
- Tight tradeoffs between approximation error and reducer load for sketch-based holistic aggregation.
- Co-design with shuffle scheduling so salting respects heterogeneous link bandwidth.

## 9. Key References

- **[Foundational]** Jim Gray, Surajit Chaudhuri, Adam Bosworth, et al. *Data Cube: A Relational Aggregation Operator (distributive/algebraic/holistic taxonomy).* Data Mining and Knowledge Discovery, 1997. — [arXiv](https://arxiv.org/abs/cs/0701155)
- **[Foundational]** David DeWitt, Jim Gray. *Parallel Database Systems: The Future of High Performance Database Systems.* CACM, 1992. — [DOI](https://doi.org/10.1145/129888.129894)
- **[Foundational]** Christopher B. Walton, Alfred G. Dale, Roy M. Jenevein. *A Taxonomy and Performance Model of Data Skew Effects in Parallel Joins.* VLDB, 1991. — [ACM](https://dl.acm.org/doi/10.5555/645917.672307)
- **[SOTA]** Maryann Xue et al. (Databricks). *Adaptive Query Execution (skew handling) in Apache Spark 3.0.* Spark Summit, 2020. — [Databricks](https://www.databricks.com/blog/2020/05/29/adaptive-query-execution-speeding-up-spark-sql-at-runtime.html)
- **[Foundational]** Dorit S. Hochbaum, David B. Shmoys. *A Polynomial Approximation Scheme for Scheduling on Uniform Processors ($P||C_{max}$ PTAS).* SIAM J. Computing, 1988. — [DOI](https://doi.org/10.1137/0217033)
- **[Survey]** Graham Cormode, Minos Garofalakis, Peter J. Haas, Chris Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2012. — [ACM](https://dl.acm.org/doi/book/10.5555/2222651)

## 10. Worked Example

Take $N = 1{,}000{,}000$ tuples, $p = 4$ reducers, and `SELECT key, SUM(v) GROUP BY key`. One heavy key $H$ holds $700{,}000$ tuples; the remaining $300{,}000$ spread over many light keys.

**Naive hash partitioning:** $H$ maps to one reducer, giving it load $\ge 700{,}000$ while the others share $300{,}000$ — makespan $\approx 700{,}000$, far above the balanced share $N/p = 250{,}000$.

**Two-phase + salting (SUM is algebraic):** Salt $H$ into 4 sub-keys $H{:}0..H{:}3$ by random suffix. Each mapper combiner pre-aggregates locally, so $H$'s $700{,}000$ tuples collapse to one partial $\texttt{SUM}$ per (mapper, salt) pair. With $\le 4$ partials per salt bucket, each reducer sees $\approx 75{,}000$ light-key tuples ($300{,}000/p$) plus $O(p)$ partial states. Phase 2 re-sums the 4 salt partials: $\texttt{SUM}(H) = \sum_{s=0}^{3}\texttt{SUM}(H{:}s)$.

Max load drops from $700{,}000$ to $\approx N/p + O(p) = 250{,}000 + O(4)$ — matching the $O(N/p + p)$ upper bound of Section 4. Had the aggregate been `MEDIAN` (holistic), salting could not collapse $H$, so $\Omega(700{,}000)$ would still flow to one reducer.

---
*Part of the [DBMS Research catalog](../../README.md).*
