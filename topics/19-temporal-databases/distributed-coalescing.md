---
id: 19-temporal-databases/distributed-coalescing
title: "Temporal Coalescing in Distributed Engines"
topic: 19-temporal-databases
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Temporal Coalescing in Distributed Engines

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/distributed-coalescing` · **Status:** empirically-open

## 1. Problem Statement

**Coalescing** merges value-equivalent tuples whose valid-time periods are adjacent or overlapping into a single maximal-period tuple — the temporal analogue of duplicate elimination, and a prerequisite for correct temporal aggregation, difference, and snapshot equivalence. In a single node it is a sort/group operation. In a **distributed/shared-nothing engine** (Spark, Flink, Trino, BigQuery, Snowflake, distributed Postgres), the interval data is **partitioned** across workers, and two value-equivalent intervals that must coalesce can live on different partitions.

The problem: coalesce a partitioned set of (key, value, $[ts,te)$) intervals **correctly** (every maximal merge realized) while (i) minimizing **network shuffle**, (ii) keeping **per-partition skew bounded** despite hot keys / hot time-ranges, and (iii) scaling to high cardinality. Variants: *decision* (does any cross-partition merge exist?), *optimization* (minimize bytes shuffled subject to a skew bound $\beta$), *streaming* (coalesce an unbounded interval stream with bounded watermark-delayed state). The tension is fundamental: hash-partitioning by value-key co-locates mergeable tuples but concentrates hot keys; range-partitioning by time balances load but separates mergeable tuples spanning a boundary.

## 2. Mathematical Foundations

Let the input be a multiset of intervals tagged by an equivalence class (value-key) $g$. Coalescing computes, per class $g$, the **union of intervals** $\bigcup_i I_i$ as a set of maximal disjoint intervals. Within one class this is the classic interval-union / merge problem, solvable in $O(m\log m)$ by sorting endpoints and sweeping; the union has the *Helly-on-the-line* structure (intervals overlap pairwise within a maximal run iff they share a common point in a connected component of the interval graph).

Distributed cost is analyzed in the **Massively Parallel Computation (MPC)** model (Beame–Koutris–Suciu): $p$ servers, rounds of computation separated by all-to-all shuffles, with *load* $L$ = max bytes received by any server. Coalescing by value-key is a *group-by* whose MPC cost is governed by the **maximum group size**; the lower bound on load for a single round is $L = \Omega(m/p)$ in the balanced case and $\Omega(\max_g |g|)$ when a class is a hot key, so skew is information-theoretically unavoidable for adversarial inputs. Range-partition correctness requires a **boundary-merge** phase: an interval straddling a range boundary at time $b$ contributes to two partitions, and a final reduce must stitch maximal runs across boundaries — formalizable as a connected-components computation on a boundary-interval graph whose size is bounded by the number of boundary-crossing intervals, the *cut*. Minimizing shuffle subject to skew bound $\beta$ is an optimization over the (value $\times$ time) partition grid; the offline version is related to **balanced graph/hypergraph partitioning**, which is NP-hard.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Single-node optimal coalescing is folklore ($O(m\log m)$ sweep; Böhlen–Snodgrass–Soo, *VLDB 1996*, established the operator and its SQL realizations). MPC group-by lower/upper bounds (Beame–Koutris–Suciu, *PODS 2013/2014*) bound the distributed group cost but do not specifically address interval stitching.
- **Systems-SOTA:** Interval/temporal joins and aggregation in distributed engines use **interval-partitioning** strategies — Overlap Interval Partition Join (Dignös–Böhlen–Gamper, *SIGMOD 2014*) and disjoint/replication-based interval partitioning in Spark (e.g. the *Temporal/Interval* operators studied by Bouros–Mamoulis and the Spark-based temporal extensions). Production engines (Snowflake, BigQuery) coalesce via window functions (`LAG`/gaps-and-islands), which incur a full partition-by-key shuffle and degrade on hot keys. No engine ships a skew-bounded, shuffle-minimal coalescing operator.

## 4. Upper Bound

A two-phase algorithm achieves correctness with controlled cost: **(P1)** range-partition the time axis into $p$ balanced ranges by quantiles of endpoint density (bounding load to $O(m/p)$ for non-degenerate inputs), coalesce within each range, replicating each boundary-crossing interval to both sides; **(P2)** a single additional round stitches boundary runs, with shuffle proportional to the **boundary cut** $c \ll m$. Total: $O((m/p)\log(m/p))$ local work and $O(m/p + c)$ load in $O(1)$ MPC rounds when the cut is small. For value-key hashing, coalescing matches the MPC group-by upper bound $L = O(m/p)$ *only* when the largest class fits, i.e. $\max_g|g| = O(m/p)$. Hybrid (value $\times$ time grid) partitioning interpolates and is the practical upper-bound state.

## 5. Lower Bound

Any single-round MPC algorithm that coalesces by value-key must incur load $L = \Omega(\max_g |g|)$ — a hot value-key forces all its intervals onto one server (a direct *skew* lower bound, since the maximal-interval output for that class depends on all its members). For time-range partitioning, adversarial inputs (a single long-lived interval per class spanning all ranges, plus dense short intervals) force either replication blow-up or a non-constant number of stitching rounds, giving a **shuffle vs. rounds** trade-off lower bound analogous to MPC connectivity lower bounds (computing connected components of the boundary-interval graph needs $\Omega(\log_{L/m} (\text{diameter}))$ rounds under the *one-cycle-vs-two-cycles* conjecture, Roughgarden–Vassilvitskii–Wang). Offline skew-minimal partitioning is NP-hard via reduction from balanced partitioning.

## 6. The Gap

This is **empirically open**: we have a clean single-node optimum, MPC bounds for the group-by skeleton, and good heuristics (interval partitioning, replication of boundary crossings), but *no* algorithm proven to simultaneously achieve minimal shuffle and a worst-case skew bound across the realistic regime (mixed long-lived + short intervals, hot keys, hot time-windows). The constant-round vs. shuffle-volume trade-off for boundary stitching is unquantified in practice, and engines have not converged on a standard operator. Closing it is partly a *systems-measurement* problem (which partitioning wins on which workload) and partly a *theory* problem (a tight skew-vs-shuffle Pareto frontier for interval union).

## 7. Current Research (as of June 2026)

- Skew-aware interval partitioning for distributed temporal joins/aggregation (Bouros, Mamoulis, and the Dignös–Böhlen–Gamper group) being re-cast for coalescing specifically *(frontier — verify)*.
- Watermark-based streaming coalescing in Flink/Arroyo/RisingWave with bounded state and out-of-order tolerance *(frontier — verify)*.
- MPC-model analyses of interval/connectivity operators extending Beame–Koutris–Suciu to interval stitching *(frontier — verify)*.

## 8. Future Work

- A coalescing operator with a provable skew-vs-shuffle Pareto guarantee under mixed interval-length distributions.
- Adaptive long-lived-interval handling (separate "fat" intervals into a broadcast lane) with cost models in the optimizer.
- Standardized streaming coalescing semantics (watermark + retraction) and a shared benchmark for distributed temporal coalescing.

## 9. Key References

- **[Foundational]** M. Böhlen, R. T. Snodgrass, M. D. Soo. *Coalescing in Temporal Databases.* VLDB, 1996. — [PDF](https://www.vldb.org/conf/1996/P180.PDF)
- **[Foundational]** P. Beame, P. Koutris, D. Suciu. *Communication Steps for Parallel Query Processing.* ACM PODS, 2013 (MPC model, skew). — [DBLP](https://dblp.org/rec/conf/pods/BeameKS13.html) · [arXiv](https://arxiv.org/abs/1306.5972)
- **[SOTA]** A. Dignös, M. H. Böhlen, J. Gamper. *Overlap Interval Partition Join.* ACM SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2612175)
- **[SOTA]** P. Bouros, N. Mamoulis. *A Forward Scan based Plane Sweep Algorithm for Parallel Interval Joins.* VLDB, 2017. — [DOI](https://doi.org/10.14778/3137628.3137644)
- **[SOTA]** T. Roughgarden, S. Vassilvitskii, J. R. Wang. *Shuffles and Circuits: On Lower Bounds for Modern Parallel Computation.* Journal of the ACM, 2018 (MPC round lower bounds). — [DOI](https://doi.org/10.1145/3232536)
- **[Survey]** M. H. Böhlen, A. Dignös, J. Gamper, C. S. Jensen. *Temporal Data Management — An Overview.* eBISS, Springer, 2018. — [DOI](https://doi.org/10.1007/978-3-319-96655-7_3)

## 10. Worked Example

Coalesce these (key, $[ts,te)$) intervals, all key $A$, across $p=2$ workers by **time-range**
partition at boundary $b=20$ (worker 0 owns $[0,20)$, worker 1 owns $[20,40)$):

$$A:[2,8),\ [6,14),\ [18,24),\ [30,36)$$

**P1 (local coalesce).** Endpoint sweep per worker. Worker 0 sees $[2,8),[6,14)$ and the left part
of the straddler $[18,24)$ (replicated to both sides): merging the overlapping run gives
$[2,14)$ and $[18,20)$. Worker 1 sees the right part $[20,24)$ and $[30,36)$: gives $[20,24)$ and
$[30,36)$.

**P2 (boundary stitch).** Only intervals touching $b=20$ can still merge. Worker 0's $[18,20)$ and
worker 1's $[20,24)$ meet at 20, so one stitch round merges them into $[18,24)$. Final output:

$$A:[2,14),\ [18,24),\ [30,36)$$

Cost: local work $O((m/p)\log(m/p))$; the shuffle in P2 is just the **boundary cut**
$c$ = number of boundary-crossing intervals = $1$ here, not all $m=4$ — illustrating the
$O(m/p + c)$ load bound. Had every interval been one long-lived $A:[0,40)$ spanning both ranges
(the adversarial case of §5), replication would blow up and the cut $c$ would dominate, forcing the
skew-vs-shuffle trade-off the problem leaves open.

---
*Part of the [DBMS Research catalog](../../README.md).*
