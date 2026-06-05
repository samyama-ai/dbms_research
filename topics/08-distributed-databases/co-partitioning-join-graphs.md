# Co-Partitioning for Join Graphs

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/co-partitioning-join-graphs` · **Status:** open

## 1. Problem Statement
Given a schema and a workload of join queries, decide whether the database can be **co-partitioned** so that **every** query in the workload joins **locally** (no cross-node data movement) — i.e., all tuples that must meet to produce an answer reside on the same node — and, if not perfectly possible, how close one can get.

Variants:
- **Decision (perfect co-partitioning):** Does there exist an assignment of partitioning keys to tables such that all workload joins are co-located?
- **Counting / maximization:** Maximize the (weighted) number of queries made local, or minimize residual shuffle traffic.
- **Bounded-replication:** Allow $r$-fold replication of some tables; decide feasibility / minimize replication to achieve full locality.

## 2. Mathematical Foundations
Build the **join graph** $G$: vertices = (table, attribute) partitioning candidates; an edge connects attributes equated by a join predicate in the workload. A perfect co-partitioning corresponds to choosing **one partitioning key per table** so that for every query, all its join edges are "satisfied" — equivalently, a consistent labeling on the **equivalence classes of join attributes** induced by the union of query join graphs. This is closely related to **constraint satisfaction / 2-coloring-style** consistency and to **functional-dependency closure** (the chase): two attributes must co-partition if a query equi-joins them, and consistency must propagate transitively. Conflicts arise when one table must be partitioned by two incompatible keys for different queries — a structure analogous to **graph/hypergraph coloring conflicts** and **(hyper)graph cut** when partial. Replication relaxes the single-key constraint, turning feasibility into a covering problem with submodular structure.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** The perfect-locality decision reduces to consistency of an attribute-equivalence labeling; when each table has a single key it is checkable in near-linear time via union-find over join-attribute classes, but with **choice** of keys per table (or aggregation/group-by keys) it becomes a constraint problem that is NP-hard in general. Maximization (most-queries-local) is an NP-hard **max-constraint / graph-cut** variant.
- **Systems-SOTA:** Reference-partitioning and **co-located joins** in Oracle, Google **Spanner** interleaved tables, **Citus** (distributed Postgres) co-location groups, **Vertica/Greenplum** distribution keys, and **CockroachDB** locality hints. These let DBAs declare co-location but do not automatically *solve* the optimal co-partitioning for a workload.

## 4. Upper Bound
Single-key-per-table perfect-locality check: $O((N_{\text{attrs}} + N_{\text{joins}})\,\alpha)$ via union-find (near-linear). With per-table key choice or partial locality, best-known are heuristic / ILP-based solvers and **constant-factor approximations only for restricted join-graph classes** (e.g., when the global join graph is acyclic/tree-structured, a greedy propagation gives full locality if and only if no class conflict exists). Bounded-replication feasibility admits greedy submodular approximations $(1-1/e)$ for coverage objectives.

## 5. Lower Bound
The general feasibility/maximization problem is **NP-hard** (reduction from graph coloring / constraint satisfaction over the join-attribute conflict structure). Maximizing the number of locally-joinable queries is **APX-hard**, inheriting inapproximability from **max-cut / label-cover** style reductions. No polynomial algorithm decides optimal bounded-replication co-partitioning in general unless P = NP.

## 6. The Gap
The **perfect, single-key** case is tractable and well understood. The **gap** lies between (a) this easy case and (b) the realistic case with key choice, group-by/aggregation keys, partial locality, and bounded replication, which is NP/APX-hard with only heuristics deployed. **Open**: principled approximation algorithms and a sharp dichotomy characterizing which workload join-graph structures admit (near-)perfect co-partitioning. Closing it needs both a structural theorem (which join graphs are co-partitionable) and matching approximation/hardness.

## 7. Current Research (as of June 2026)
Active in distributed-SQL systems (Citus, CockroachDB, Spanner) on automatic co-location advisors *(frontier — verify)*. Theory groups revisit the problem via **CSP dichotomy** and **graph-structure** lenses, and via learned advisors that predict good distribution keys *(frontier — verify)*. Connections to **referential-integrity-aware** partitioning (interleaving) are being formalized.

## 8. Future Work
- A dichotomy theorem: exactly which workload join graphs admit full local-join co-partitioning.
- Approximation algorithms for max-local-queries and min-replication-for-locality with guarantees.
- Joint optimization of co-partitioning with replication, materialized views, and drifting workloads.

## 9. Key References
- **[Foundational]** Zilio, Rao, Lightstone, Lohman et al. *DB2 Design Advisor: Integrated Automatic Physical Database Design.* VLDB, 2004.
- **[SOTA]** Curino, Jones, Zhang, Madden. *Schism: A Workload-Driven Approach to Replication and Partitioning.* VLDB, 2010.
- **[Foundational]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (acyclicity, chase, dependencies).
- **[SOTA]** Corbett et al. *Spanner: Google's Globally-Distributed Database* (interleaved tables / co-location). OSDI, 2012.
- **[Survey]** Özsu, Valduriez. *Principles of Distributed Database Systems* (4th ed.). Springer, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
