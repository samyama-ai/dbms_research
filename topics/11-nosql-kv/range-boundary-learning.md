# Range-Partition Boundary Learning

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/range-boundary-learning` · **Status:** empirically-open

## 1. Problem Statement

Range-partitioned KV stores (HBase regions, Bigtable tablets, CockroachDB/TiKV/Spanner ranges) split the key space into contiguous **ranges**, each owned by one node. **Split points** (boundaries) determine load balance: a well-chosen set keeps per-range request rate, data size, and hotspot exposure even; a poor set creates **hot ranges** and skew. The problem: **learn and continuously maintain** split points that adapt to an **evolving key distribution** (changing data sizes *and* access frequencies), minimizing imbalance and the cost of repartitioning (split/merge/move), under the constraint that splits are made online from streaming observations.

Variants:
- **Static / batch:** Given an estimate of the key access-frequency density $f(k)$, choose $p-1$ boundaries forming $p$ ranges minimizing the maximum range load (a partitioning/quantile problem).
- **Online / streaming:** Observe keys/requests as a stream; maintain boundaries with bounded memory and bounded re-split churn as $f$ drifts.
- **Decision:** Does a $p$-partition with max-load $\leq L$ exist for the current distribution?

This sits at the intersection of **load balancing**, **streaming quantile estimation**, and **online learning under distribution shift**.

## 2. Mathematical Foundations

Order keys on the line; let $f(k)$ be the request density. A partition into ranges $R_1,\dots,R_p$ has loads $w_i=\int_{R_i} f$. The **min-max load** objective:
$$\min_{0=b_0<b_1<\dots<b_p=1}\ \max_i \int_{b_{i-1}}^{b_i} f(k)\,dk.$$
The optimal balanced partition places boundaries at the **$i/p$ quantiles** of $f$ — so boundary learning reduces to **online quantile estimation** of a *drifting* distribution. Streaming quantile sketches give the toolkit: **GK** (Greenwald–Khanna) computes $\epsilon$-approximate quantiles in $O(\frac{1}{\epsilon}\log(\epsilon N))$ space; **t-digest** and **DDSketch** (Masson et al.) give mergeable relative-error quantiles ideal for distributed aggregation across range servers.

Hotspots also depend on *temporal* concentration, not just key frequency — connecting to **heavy-hitters / frequent-elements** sketches (Count-Min, Misra–Gries, Space-Saving). Drift handling invokes **online learning / sliding-window** sketches and possibly **competitive analysis** (repartitioning cost vs. imbalance is a metrical-task-system / rebalancing trade-off). Learned-index ideas (RMI, Kraska et al.) model the CDF directly, making quantiles cheap to query but hard to maintain under shift.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** HBase region splitting (size-based, then `SteppingSplitPolicy`), Bigtable tablet splits, **CockroachDB** load-based splitting (splits a range at the key that best balances QPS, using a streaming reservoir of sampled request keys), **TiKV** PD (Placement Driver) hot-region scheduling, **YugabyteDB**/Spanner auto-sharding. CockroachDB's *load-based splitter* is the clearest production instance of online boundary learning by sampled-key balancing.
- **Theory/sketch-SOTA:** Greenwald–Khanna quantile summaries; DDSketch (Masson–Rim–Lee, VLDB 2019) for relative-error mergeable quantiles; Space-Saving (Metwally et al.) for hot keys.
- **Learned indexes:** Kraska et al. *The Case for Learned Index Structures* (SIGMOD 2018) and updatable variants (ALEX, PGM-index) model key CDFs, applicable to choosing boundaries — but largely for static/insert workloads, not request-load-driven splits.

## 4. Upper Bound

For the **static** min-max partition given an $\epsilon$-quantile summary, placing boundaries at estimated $i/p$ quantiles yields a partition whose max load is within an additive $\epsilon$ (a $(1+O(p\epsilon))$ multiplicative balance) of optimal, in $O(\frac1\epsilon\log(\epsilon N))$ space (GK) — a clean approximation bound. DDSketch gives $\alpha$-relative-error boundaries with mergeability across distributed range servers. For the **online** case, sampled-key load splitting (CockroachDB) empirically converges but has **no proven competitive bound** on imbalance-plus-rebalancing-cost.

## 5. Lower Bound

- **Streaming space:** exact quantiles/median over a stream require $\Omega(N)$ space; any $\epsilon$-approximate comparison-based quantile summary needs $\Omega(\frac1\epsilon\log\frac1\epsilon)$ space (Cormode–Veselý lower bound), so boundary precision is space-limited — you cannot maintain arbitrarily precise drifting quantiles cheaply.
- **Drift / online:** under adversarial distribution shift, any online repartitioner faces a load-balancing-vs-migration trade-off lower-bounded by metrical-task-system / $k$-server-style competitive bounds; no constant-competitive guarantee is possible against a fully adaptive adversary that moves the hot key each step.
- The combined **balance + bounded-churn** objective has no known matching algorithmic bound — the hardness is the online/adaptive part, not the static partition (which is poly-time).

## 6. The Gap

**Empirically-open:** production systems (CockroachDB, TiKV, HBase) demonstrably keep ranges balanced via sampled-load splitting, and streaming quantile theory gives tight *static* approximation bounds. But there is **no theory for the online, drifting case**: no competitive-ratio or regret bound for *jointly* minimizing load imbalance and split/merge/move churn as $f$ evolves, and no principled trigger for *when* to split/merge (avoiding thrashing). The gap is between effective heuristics and any guarantee on adaptive boundary maintenance. Closing it needs an online-learning/competitive-analysis treatment of "rebalance vs. tolerate imbalance" with drift, plus sketch lower bounds folded in.

## 7. Current Research (as of June 2026)

- Load-/access-aware splitting beyond size (CockroachDB Labs, PingCAP/TiKV PD) refining sampled-key balancers and anti-thrashing hysteresis *(frontier — verify)*.
- Updatable learned indexes (ALEX, PGM, LIPP) and learned CDF models for partition boundaries under inserts *(frontier — verify)*.
- ML-driven hotspot prediction / autosharding (cloud Spanner, DynamoDB adaptive capacity / "split for heat").
- Drift-aware streaming quantile sketches with bounded reconfiguration.

## 8. Future Work

- Competitive/regret bounds for online boundary maintenance with migration cost.
- Principled split/merge triggers with anti-thrashing guarantees.
- Joint optimization of split points with replica placement and tiering.
- Distribution-shift-robust learned CDF models maintained incrementally.

## 9. Key References

- **[Foundational]** Greenwald, M., Khanna, S. *Space-Efficient Online Computation of Quantile Summaries.* SIGMOD, 2001.
- **[Foundational]** Chang, F., et al. *Bigtable: A Distributed Storage System for Structured Data.* OSDI, 2006.
- **[SOTA]** Masson, C., Rim, J.E., Lee, H.K. *DDSketch: A Fast and Fully-Mergeable Quantile Sketch with Relative-Error Guarantees.* VLDB, 2019.
- **[SOTA]** Kraska, T., Beutel, A., Chi, E., Dean, J., Polyzotis, N. *The Case for Learned Index Structures.* SIGMOD, 2018.
- **[SOTA]** Metwally, A., Agrawal, D., El Abbadi, A. *Efficient Computation of Frequent and Top-k Elements in Data Streams (Space-Saving).* ICDT, 2005.
- **[Survey]** Cormode, G., Veselý, P. *A Tight Lower Bound for Comparison-Based Quantile Summaries.* PODS, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
