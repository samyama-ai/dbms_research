# Automated Horizontal Partitioning and Sharding Design

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/horizontal-partitioning-design` · **Status:** open

## 1. Problem Statement
Given a set of relations, their integrity/foreign-key structure, a target number of nodes/shards $k$, and a workload $W$ of queries and transactions, choose **partitioning keys, partitioning functions (hash/range/list), and boundaries** for each relation so as to (a) balance data and load across shards, (b) **minimize cross-partition joins**, and (c) **minimize distributed (multi-shard) transactions**. Replication of small "reference" tables is allowed within a storage budget.

- **Decision variant:** Is there a sharding with $\le \beta$ cross-partition transactions and imbalance $\le \epsilon$?
- **Optimization variant:** minimize a weighted sum of distributed-transaction cost, cross-shard join cost, and load imbalance.
- The design must remain valid under skew and workload drift, making this both a static design and an online problem.

## 2. Mathematical Foundations
Model the data+workload as a **graph/hypergraph** $G=(V,E)$: vertices are tuples (or tuple groups / partition-key values), and a hyperedge connects tuples co-accessed by a transaction. A balanced $k$-way partition minimizing edge cut corresponds to minimizing distributed transactions while balancing shard sizes — this is the basis of the **Schism** approach (graph partitioning via METIS) and its successors.

Formally, minimize cut $\sum_{e\in E} w_e\,[\,e \text{ spans } \ge 2 \text{ parts}\,]$ subject to $|P_i|\le (1+\epsilon)\frac{|V|}{k}$. For join locality, **co-partitioning** equality keys across related tables (key alignment along FK chains) preserves locality; the relevant theory ties to **distributed query cost** and the **AGM bound** for estimating join output / communication in distributed joins. Range design additionally interacts with **order-preserving** access and hot-range skew (modeled via load distributions, not just cardinalities).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Balanced graph/hypergraph $k$-partitioning is NP-hard; practical optimality relies on multilevel partitioners (METIS/hMETIS, KaHIP). No constant-factor approximation for balanced min-cut under hard balance is known in general.
- **Systems-SOTA:** **Schism** (Curino et al., VLDB 2010) — graph-partitioning-based automatic sharding with decision-tree-explained predicates; **SWORD**, **Clay** (Serafini et al., VLDB 2016) for incremental, skew-aware re-partitioning; **Horticulture / Houdini** for stored-procedure-driven partitioning in H-Store; cloud systems (CockroachDB, Spanner, TiDB, Citus, Vitess) ship range/hash auto-sharding with load-based splitting/rebalancing. Learned and cost-based advisors (e.g., in Azure SQL DW / Redshift DISTKEY advisors) target the same problem commercially.

Despite strong systems, no advisor provably balances load **and** minimizes distributed transactions with guarantees; hence **open**.

## 4. Upper Bound
The best practical upper bound is multilevel balanced partitioning (METIS/KaHIP), running near-linearly in graph size and delivering empirically excellent cuts, but with **no worst-case approximation guarantee** under hard balance. For balanced min-cut, the best known approximations are bicriteria ($O(\sqrt{\log n})$-type cut approximations with relaxed balance, via spectral/SDP methods), but these relax the balance constraint and do not directly model distributed-transaction semantics or range-boundary placement. Hash co-partitioning along FK trees yields exact join locality for tree-structured (acyclic) FK schemas in polynomial time.

## 5. Lower Bound
Balanced $k$-way min-cut (the core of cross-transaction minimization) is **NP-hard** and admits **no constant-factor approximation** under hard balance constraints (inapproximability inherited from balanced graph partitioning / minimum bisection-style hardness). Choosing partitioning that simultaneously bounds imbalance and distributed transactions is therefore NP-hard. In the distributed runtime, **CAP** (Brewer/Gilbert–Lynch) imposes a fundamental availability/consistency trade-off across shards, and any cross-shard transaction protocol is bounded by **FLP** impossibility for asynchronous consensus — limits that constrain what any sharding design can achieve operationally, independent of the combinatorial design cost.

## 6. The Gap
The gap is large and open: between NP-hardness/inapproximability of balanced min-cut and the absence of any guaranteed-quality, distributed-transaction-aware advisor that also handles range boundaries, skew, and online drift. Closing it would require (a) approximation algorithms for the combined transaction+balance objective under realistic structural restrictions, or (b) hardness results showing the combined objective is strictly harder than plain balanced partitioning.

## 7. Current Research (as of June 2026)
- Learned/RL-based sharding advisors that predict cross-shard cost and rebalance online *(frontier — verify)*.
- Skew- and drift-aware incremental re-partitioning at minimal data-movement cost (Clay lineage) integrated into cloud autosharders *(frontier — verify)*.
- Joint key + replication + secondary-index sharding design *(frontier — verify)*.
- Groups: Stonebraker/Madden/Curino lineage (MIT/CSAIL, VoltDB), Pavlo (CMU), cloud-DB teams (Google Spanner, Cockroach Labs, PingCAP).

## 8. Future Work
- Distributed-transaction-aware approximation algorithms with guarantees.
- Online sharding that bounds reorganization/migration data movement.
- Co-design of partition keys with secondary indexes and replicas.
- Robust designs under adversarial / drifting skew with regret bounds.

## 9. Key References
- **[SOTA]** C. Curino, E. Jones, Y. Zhang, S. Madden. *Schism: A Workload-Driven Approach to Database Replication and Partitioning.* VLDB, 2010.
- **[SOTA]** M. Serafini, R. Taft, A. Elmore, A. Pavlo, A. Aboulnaga, M. Stonebraker. *Clay: Fine-Grained Adaptive Partitioning for General Database Schemas.* VLDB, 2016.
- **[Foundational]** S. Ceri, M. Negri, G. Pelagatti. *Horizontal Data Partitioning in Database Design.* SIGMOD, 1982.
- **[Foundational]** S. Gilbert, N. Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (CAP).* SIGACT News, 2002.
- **[Foundational]** M. Fischer, N. Lynch, M. Paterson. *Impossibility of Distributed Consensus with One Faulty Process (FLP).* JACM, 1985.
- **[Survey]** M. T. Özsu, P. Valduriez. *Principles of Distributed Database Systems.* Springer, 4th ed., 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
