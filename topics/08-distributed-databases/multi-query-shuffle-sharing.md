---
id: 08-distributed-databases/multi-query-shuffle-sharing
title: "Multi-Query Shuffle Sharing"
topic: 08-distributed-databases
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Multi-Query Shuffle Sharing

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/multi-query-shuffle-sharing` · **Status:** open

## 1. Problem Statement

A distributed engine executes a workload $Q = \{q_1, \dots, q_n\}$ of concurrent (or overlapping-in-time) queries, each compiled to a DAG of operators with **exchange/shuffle** boundaries (repartition by a key) that dominate network cost. Many queries repartition the same base or intermediate relations on the same or compatible keys. The problem is to construct a **shared execution schedule** that computes shuffle products once and routes them to all consumers, minimizing aggregate network bytes (and skew/latency) while respecting per-query deadlines.

- **Optimization variant:** given $Q$ and arrival times, choose a set of shared exchange operators and a routing/materialization plan minimizing total bytes shuffled subject to latency/SLA constraints.
- **Decision variant:** does a shared plan with $\le B$ shuffled bytes and all deadlines met exist? (NP-hard.)
- **Online variant:** queries arrive over time; decide sharing without full future knowledge.

This generalizes classic **multi-query optimization (MQO)** from CPU/common-subexpression reuse to the **network/shuffle** resource, where partitioning compatibility (key + hash function + partition count) governs reuse.

## 2. Mathematical Foundations

Represent the workload as a **global plan DAG** $G=(V,E)$ where nodes are candidate (sub)plans, including alternative shuffle keys; sharing is selecting a subgraph covering every query's required outputs at minimum cost. Classic MQO casts this as **Directed Steiner Tree / weighted set cover**, which is NP-hard and admits only $O(\log n)$-type approximations (DST has no $o(\log^2 n)$ approximation under standard assumptions).

Shuffle sharing adds a **partitioning lattice**: a relation partitioned by $(k, h, p)$ can serve a consumer needing $(k, h, p')$ iff $p' \mid p$ or via cheap local re-split; compatibility is a partial order. The objective decomposes as
$$\min \sum_{e \in \text{shuffles}} \text{bytes}(e)\cdot x_e \;\;\text{s.t.}\;\; \text{each } q_i \text{ covered},\ \text{deadlines},\ \text{capacity}.$$
Sharing benefit is **submodular** in the chosen exchange set under certain monotone cost models, enabling greedy $(1-1/e)$ guarantees, but interacts with skew and pipeline-breaking materialization.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** MQO foundations (Sellis, TODS 1988; Roy et al. *Volcano* extensions, SIGMOD 2000) give DST/cover formulations; no tight bounds specific to shuffle sharing.
- **Systems-SOTA:** Work-sharing engines — **SharedDB / MQJoin** (Giannikis et al., VLDB 2012/2016), **CJoin**, and column-store shared scans (Qiao et al., *Cooperative Scans*; **CScan**, **Crescando**) share scans/joins. In big-data engines, **Spark SQL Exchange reuse** (`ReuseExchange`), Trino/Presto common-subplan caching, and **AStream/SharedHashJoin** prototypes reuse shuffle output for identical exchanges. Materialized intermediate caching (Nectar, Tachyon/Alluxio) provides cross-query reuse but not key-compatible partial sharing.

## 4. Upper Bound

- **Approximation:** greedy submodular maximization yields $(1-1/e)$ of optimal sharing benefit under monotone-submodular cost assumptions; DST-based sharing yields $O(n^{\epsilon})$ / $O(\log^2 n)$ approximations for the Steiner-style selection.
- **Practical:** exact-match `ReuseExchange` is "free" (detect identical shuffle subtrees, $O(|G|)$) and already deployed; gains up to integer-factor byte reductions on overlapping workloads.

Model: offline batch with known plans; cost = network bytes.

## 5. Lower Bound

- **Hardness:** optimal multi-query plan selection is **NP-hard** (reduction from weighted set cover / Directed Steiner Tree); DST inapproximability gives $\Omega(\log^{2-\epsilon} n)$ hardness for the sharing-selection core.
- **Online:** with adversarial arrivals, no online algorithm matches the offline optimum within a constant — competitive ratio $\Omega(\log n)$ lower bounds inherited from online Steiner/caching.
- No tight communication-complexity lower bound *specific to partition-compatible shuffle reuse* is known.

## 6. The Gap

This is **genuinely open**. Systems exploit only *exact-match* exchange reuse; **partition-compatible partial sharing** (different but compatible keys/granularities, partial overlap of consumers) has no algorithm with provable guarantees, and no matching lower bound captures the partitioning-lattice structure. Closing it needs (a) a cost model unifying bytes + skew + materialization, (b) an approximation algorithm over the partitioning lattice, and (c) an online/streaming-arrival competitive analysis.

## 7. Current Research (as of June 2026)

- Cloud warehouses exploring cross-query exchange and result reuse at scale (Snowflake, BigQuery, Databricks Photon); largely exact-match today. *(frontier — verify)*
- Learned/ML-driven workload-aware sharing and admission control for shared shuffle. *(frontier — verify)*
- Sharing in disaggregated/shuffle-service architectures (Magnet, Cosco, Uniffle) where a dedicated shuffle tier could materialize once and fan out.

## 8. Future Work

- Provable approximation for partition-compatible multi-consumer shuffle sharing.
- Online and SLA-aware sharing with deadline constraints.
- Co-optimizing sharing with skew handling and elastic resource scaling.

## 9. Key References

- **[Foundational]** Sellis. *Multiple-Query Optimization.* ACM TODS, 1988. — [DOI](https://doi.org/10.1145/42201.42203)
- **[Foundational]** Roy, Seshadri, Sudarshan, Bhobe. *Efficient and Extensible Algorithms for Multi-Query Optimization.* SIGMOD, 2000. — [DOI](https://doi.org/10.1145/342009.335419), [arXiv](https://arxiv.org/abs/cs/9910021)
- **[SOTA]** Giannikis, Alonso, Kossmann. *SharedDB: Killing One Thousand Queries with One Stone.* VLDB, 2012. — [DOI](https://doi.org/10.14778/2168651.2168654), [arXiv](https://arxiv.org/abs/1203.0056)
- **[SOTA]** Makreshanski, Giannikis, Alonso, Kossmann. *MQJoin: Efficient Shared Execution of Main-Memory Joins.* VLDB, 2016. — [PDF](https://www.vldb.org/pvldb/vol9/p480-makreshanski.pdf)
- **[Survey]** Halim, Idreos, Karras, Yap. *Stochastic Database Cracking / shared-work directions* — see also Qiao et al. *Main-Memory Scan Sharing for Multi-Core CPUs.* VLDB, 2008. — [DOI](https://doi.org/10.14778/1453856.1453924)

## 10. Worked Example

Three concurrent queries over `Orders(cust_id, ...)`, each needing it repartitioned by `cust_id`:
- $q_1$: join with `Customers`, needs `Orders` hashed on `cust_id` into 8 partitions.
- $q_2$: same join, also needs hash on `cust_id`, 8 partitions — *identical* exchange.
- $q_3$: group-by `cust_id`, needs hash on `cust_id` into 4 partitions.

Say shuffling `Orders` once costs 800 MB of network bytes. Without sharing: $q_1,q_2,q_3$ each shuffle independently $\Rightarrow 3\times 800 = 2400$ MB.

Exact-match reuse (deployed today, e.g. Spark `ReuseExchange`): $q_1$ and $q_2$ share the 8-way shuffle $\Rightarrow$ one 800 MB shuffle serves both; $q_3$ still shuffles separately $\Rightarrow 800 + 800 = 1600$ MB.

Partition-compatible sharing (the open part): since $4 \mid 8$, $q_3$'s 4 partitions can be obtained by *local* coalescing of the 8-way result — no second network shuffle. Total $= 800$ MB, a $3\times$ reduction. The 4-and-8 compatibility ($p'\mid p$ in the partitioning lattice of section 2) is exactly the reuse opportunity current systems leave on the table.

---
*Part of the [DBMS Research catalog](../../README.md).*
