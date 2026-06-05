# Cross-Shard Secondary Index Joins

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/cross-shard-index-joins` · **Status:** open

## 1. Problem Statement
A query filters on a secondary-indexed attribute (`WHERE color = 'red'`) and then needs the full base rows. In a sharded KV/NoSQL store, the secondary index is partitioned by the indexed attribute (so the matching keys are found at a few index shards), but the base rows for those keys are **scattered across many data shards** (partitioned by primary key). Answering the query is therefore a *distributed index-nested-loop join* (or semijoin) between an index relation and a base relation living on disjoint node sets.

Goal: minimize total cost — network bytes, round-trips, and tail latency — of fetching the $|R|$ matching base rows scattered over up to $m$ shards, possibly with additional join/aggregation, under skew and partial failure.

Variants:
- **Optimization:** minimize communication / rounds to return all matching rows (or a top-$k$ / aggregate over them).
- **Decision:** can the query be answered in $r$ rounds with $\le C$ bytes communicated?
- **Counting/cardinality:** estimate $|R|$ and per-shard fan-out for the planner before issuing fetches.

This is the read-time dual of *Global Secondary Index Consistency* (which is the write-time problem).

## 2. Mathematical Foundations
Model: $m$ shards, the index lookup yields a set $K$ of $|K|=N$ primary keys; each key resolves (via the partition function) to one of $m$ shards, inducing a *fan-out* multiset. The naive plan issues $N$ point gets ($N$ messages, up to $N$ round-trips if serial, $O(m)$ if batched per shard). The communication-optimal plan is a **distributed semijoin**: group $K$ by shard and send one batched request per shard, giving $O(m)$ messages and $\le 2$ rounds. Cost is governed by **massively-parallel / MPC (MapReduce) lower bounds**: for a join on $p$ servers with load $L$ per server, the **AGM bound** $\prod$ controls output-sensitive cost, and the **Koutris–Suciu** MPC model gives load $\tilde{O}(\frac{|IN|}{p^{1/\rho^*}})$ for one round where $\rho^*$ is the fractional edge cover number; for an index→base join (essentially a key-foreign-key / semijoin), $\rho^*=1$ so optimal one-round load is $\Theta(|IN|/p)$. **Yannakakis' algorithm** makes acyclic joins (this join is acyclic) run in $O(|IN|+|OUT|)$ via semijoin reduction — the theoretical ideal. Skew (a hot indexed value, or a hot shard) breaks balanced load and needs the **skew-handling MPC** techniques (heavy-hitter splitting). Cardinality/fan-out estimation uses HyperLogLog / Count-Min sketches kept on the index.

## 3. State of the Art (SOTA)
**Systems-SOTA.** MongoDB sharded secondary indexes do *scatter-gather*: broadcast to all shards unless the query also pins the shard key — i.e., $O(m)$ fan-out even when few shards have matches. Cassandra global secondary indexes likewise scatter to all nodes (a known anti-pattern); SAI improves locality but not cross-shard joins. CockroachDB/YugabyteDB execute index joins as **distributed lookup joins** with batched, locality-aware fetches and TPC-style cost-based planning; **Spanner/F1** do distributed joins with co-partitioning and interleaved tables to make many joins local. **Vitess**, **Citus** (distributed Postgres) implement repartition/broadcast joins. Presto/Trino and Spark SQL provide the broadcast-vs-shuffle (repartition) semijoin choice.
**Theory-SOTA.** MPC join algorithms — **HyperCube/Shares** (Afrati–Ullman; Beame–Koutris–Suciu) for multiway joins, and worst-case-optimal sequential joins (**Ngo–Ré–Rudra**, NPRR/LeapFrog-TrieJoin) underpin output-sensitive cost. Yannakakis remains optimal for the acyclic case here.

## 4. Upper Bound
For the index→base semijoin (acyclic, $\rho^*=1$): the **semijoin-reduce + batched-fetch** plan achieves $O(N + |OUT|)$ communicated bytes and **2 rounds** (one to gather candidate keys per shard, one to fetch), with per-shard load $\Theta(N/m)$ when keys are balanced — matching the MPC one-/two-round optimum. With co-partitioning (base interleaved under the index value), the join becomes local: $O(1)$ rounds, no cross-shard fetch. Cardinality-guided shard pruning reduces broadcast to only the shards that actually hold matches, replacing MongoDB-style $O(m)$ scatter with $O(\#\text{touched shards})$. Tail latency is bounded by the slowest touched shard; hedged/redundant requests reduce it.

## 5. Lower Bound
**Communication lower bound (MPC, Koutris–Suciu):** any one-round algorithm computing this join on $p$ servers has max load $\Omega(|IN|/p)$, and for skewed degrees the load is $\Omega(|IN|/p \cdot \text{skew})$ — heavy hitters force either more rounds or higher load. **Round lower bounds:** computing a join whose output is scattered cannot in general be done in one round with optimal load when there is skew (a single hot value must be replicated, costing $\Omega(p)$). Two-party **communication complexity** (set-disjointness / lopsided set-intersection) gives $\Omega(N)$ bits to verify which of $N$ keys exist, so $O(N+|OUT|)$ is communication-optimal up to logs. The CAP/availability constraints apply: under partition, a fetch touching an unavailable shard cannot return a complete linearizable result.

## 6. The Gap
**Open in the practically relevant regime.** The balanced, no-skew, acyclic case is essentially *closed* (Yannakakis / 2-round MPC optimal). The genuine gaps: (1) **skew** — when an indexed value is hot or a shard is hot, no algorithm matches the balanced optimum; the tradeoff between extra rounds, replication, and load under skew is not tightly characterized for the scattered-fetch setting; (2) **cardinality-driven pruning** to avoid scatter-gather depends on accurate, cheap, distributed fan-out estimation, which is itself open under updates; (3) **multi-shard joins with additional predicates/aggregation** (top-$k$, group-by) layered on the index join lack output-optimal distributed plans; (4) co-partitioning helps but is a *schema* decision that cannot serve all query shapes simultaneously. A unified, skew-robust, round-optimal distributed index-join with matching lower bounds is missing.

## 7. Current Research (as of June 2026)
Active: worst-case-optimal *distributed* join algorithms and their integration into NewSQL planners (CockroachDB/YugabyteDB lookup-join improvements, locality-aware batching); skew-resilient MPC joins (heavy-hitter-aware HyperCube); learned cardinality/fan-out estimation feeding shard pruning; adaptive query execution that switches broadcast↔repartition at runtime (Spark AQE lineage). Groups: Suciu/Koutris/Beame (MPC join theory, UW), Ngo/Ré (worst-case-optimal joins), and NewSQL engineering teams (Cockroach Labs, Yugabyte, Google F1). Frontier: round-optimal scattered semijoins under adversarial skew with matching lower bounds *(frontier — verify)*; pushing top-$k$/aggregation into the distributed index join with output-sensitive guarantees *(frontier — verify)*.

## 8. Future Work
- Skew-robust distributed index joins matching MPC lower bounds across rounds.
- Cheap, update-tolerant distributed fan-out estimation to eliminate scatter-gather.
- Output-optimal distributed plans for index joins with aggregation/top-$k$.
- Adaptive co-partitioning that reorganizes for observed query shapes with bounded cost.

## 9. Key References
- **[Foundational]** M. Yannakakis. *Algorithms for Acyclic Database Schemes.* VLDB, 1981.
- **[Foundational]** H. Q. Ngo, C. Ré, A. Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013.
- **[SOTA]** P. Beame, P. Koutris, D. Suciu. *Communication Steps for Parallel Query Processing (MPC model).* JACM / PODS, 2017.
- **[SOTA]** F. N. Afrati, J. D. Ullman. *Optimizing Joins in a Map-Reduce Environment.* EDBT, 2010.
- **[Foundational]** A. K. Chandra, P. M. Merlin. (AGM-line) — see A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008.
- **[SOTA]** J. C. Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
