---
id: 02-query-optimization/view-selection-rewriting
title: "Optimizing under materialized views and rewriting"
topic: 02-query-optimization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimizing under materialized views and rewriting

> **Topic:** Query Optimization · **ID:** `02-query-optimization/view-selection-rewriting` · **Status:** open

## 1. Problem Statement
Given a workload of queries $Q = \{q_1,\dots,q_m\}$ (with frequencies/weights), a storage and maintenance budget, and a set of base relations, **jointly**:
1. **View selection:** choose a set $V$ of materialized views (and indexes) to precompute, and
2. **Rewriting:** for each query, find the cheapest plan that may *use* views in $V$ (answering the query partly or wholly from materialized results),

so as to minimize total expected query cost plus view maintenance cost, subject to the budget. The two are coupled: a view is only worth materializing if rewriting can exploit it, and the optimal rewrite depends on which views exist.

Variants:
- **Decision:** is there a $V$ within budget $B$ achieving total cost $\le C$? (NP-complete.)
- **Optimization:** minimize cost (the practical target).
- **Rewriting-only:** given fixed $V$, **answer queries using views** — does an equivalent (or maximally-contained) rewrite exist, and is it minimal?
- **Online/adaptive:** select views as the workload drifts.

## 2. Mathematical Foundations
**Answering queries using views (AQUV).** For conjunctive queries (CQs), deciding whether a rewriting using views computes exactly $q$ is tied to **query containment**, which is **NP-complete** for CQs (Chandra–Merlin) and decided by **homomorphisms** between query bodies. Maximally-contained rewritings for CQs are produced by the **bucket**, **inverse-rules**, and **MiniCon** algorithms. With **integrity constraints / FDs / inclusion dependencies**, equivalence under constraints is decided via the **chase** (which may not terminate in general; terminates under weak acyclicity).

**View selection as optimization.** Model candidate views as nodes in an **AND/OR DAG** (the "data cube lattice" for OLAP, after Harinarayan–Rajaraman–Ullman). Benefit of materializing view $v$ given already-chosen set $S$ is the cost reduction it provides; this benefit function is **monotone submodular** in many OLAP formulations:
$$ f(S\cup\{v\}) - f(S) \ \ge\ f(T\cup\{v\}) - f(T), \quad S\subseteq T. $$
Hence the classic **greedy algorithm achieves a $(1-1/e)$ approximation** under a cardinality/budget constraint (Nemhauser–Wolsey–Fisher), and HRU prove this bound for cube view selection. General SPJ + maintenance-cost variants are *not* submodular and lose the guarantee.

## 3. State of the Art (SOTA)
- **Theory/rewriting:** MiniCon (Pottinger–Halevy, VLDBJ 2001) remains the practical algorithm for CQ rewriting using views; chase-based rewriting handles constraints.
- **OLAP view selection:** Harinarayan, Rajaraman, Ullman (SIGMOD 1996) greedy lattice selection with the $(1-1/e)$ guarantee; Gupta–Mumick added maintenance cost.
- **Systems:** Microsoft SQL Server's **AutoAdmin / Database Tuning Advisor** (Agrawal, Chaudhuri, Narasayya) does integrated index+view+partition selection via what-if optimizer calls; Oracle materialized-view query rewrite; Calcite's materialization-based rewrite; **learned/ML advisors** in cloud warehouses (Snowflake, Redshift, BigQuery materialized views) and DBA-bandit / Microsoft research tuners.

## 4. Upper Bound
For **monotone submodular** view-selection objectives under a cardinality constraint, greedy gives a **$1 - 1/e \approx 0.632$ approximation** in polynomial time (oracle = optimizer cost calls); under a knapsack (storage) budget, cost-benefit greedy + partial enumeration gives **$\tfrac12(1-1/e)$**, improvable to $1-1/e$ with Sviridenko's algorithm. For **CQ rewriting**, a maximally-contained rewriting can be computed in time exponential in query size but the rewriting *exists and is finite* for CQs/CQs-with-views; MiniCon avoids enumerating spurious combinations.

## 5. Lower Bound
- **View selection is NP-hard** (reduces from set cover / weighted set cover); under cost-benefit constraints it inherits set-cover **inapproximability: no $(1-o(1))\ln n$ approximation** unless P = NP (Feige), matching greedy up to constants in the budgeted submodular case.
- **CQ containment / equivalence is NP-complete** (Chandra–Merlin), so even checking that a proposed rewrite is correct is NP-hard.
- With **arbitrary (non-weakly-acyclic) constraints**, the chase may not terminate and equivalence/rewriting becomes **undecidable** in general; for CQ-equivalence under unrestricted TGDs it is undecidable.

## 6. The Gap
For the **OLAP submodular slice** the gap is essentially closed: greedy is optimal up to the set-cover barrier. For the **general SPJ + maintenance + joint-with-rewriting** problem the gap is wide open: the objective is non-submodular, the optimizer-cost oracle is itself estimate-laden, and no algorithm with workload-level approximation guarantees is known. Closing it requires either structural restrictions that restore submodularity or fundamentally new techniques.

## 7. Current Research (as of June 2026)
- **Learned/RL workload advisors** that recommend views/indexes jointly and adapt online (Microsoft, cloud-warehouse teams). *(frontier — verify)*
- **Semantic/learned rewriting** using LLMs or learned equivalence to discover non-obvious view uses, with verification to guarantee soundness. *(frontier — verify)*
- Robust selection under **uncertain cardinalities** and drifting workloads; budget-aware online submodular maximization.
- Groups: Chaudhuri/Narasayya (Microsoft), Calcite community, cloud-warehouse optimizer teams, theory groups on AQUV and the chase (Benedikt, Gottlob, Kolaitis).

## 8. Future Work
- Provable approximation for joint view-selection + rewriting beyond the submodular regime.
- Incremental view maintenance cost folded into selection with worst-case guarantees.
- Verified semantic rewriting (machine-checked equivalence) to safely admit learned candidates.

## 9. Key References
- **[Foundational]** Chandra, Merlin. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC, 1977. — [ACM](https://dl.acm.org/doi/10.1145/800105.803397)
- **[Foundational]** Harinarayan, Rajaraman, Ullman. *Implementing Data Cubes Efficiently.* SIGMOD, 1996. — [ACM](https://dl.acm.org/doi/10.1145/235968.233333)
- **[SOTA]** Pottinger, Halevy. *MiniCon: A Scalable Algorithm for Answering Queries Using Views.* VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100048)
- **[Survey]** Halevy. *Answering Queries Using Views: A Survey.* VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100054)
- **[SOTA]** Agrawal, Chaudhuri, Narasayya. *Automated Selection of Materialized Views and Indexes for SQL Databases.* VLDB, 2000. — [PDF](https://www.vldb.org/conf/2000/P496.pdf)

## 10. Worked Example

**Greedy cube view selection (HRU).** A 2-dimensional cube has a lattice of 4 views with these row counts (= query cost to scan): `ALL`=1, `Part`=20, `Supplier`=80, `PartSupplier`(base)=600. Any view answers a query iff it is an ancestor; benefit of materializing $v$ = (rows saved per descendant that now uses $v$ instead of its cheapest materialized ancestor). The base `PartSupplier` is always materialized. Budget: pick **1** extra view.

Compute marginal benefit over the baseline (everything reads the 600-row base):
- `Part` (cost 20): serves `Part` and `ALL`, each saving $600-20=580$, total $\mathbf{1160}$.
- `Supplier` (cost 80): serves `Supplier`+`ALL`, saving $(600-80)\cdot2 = \mathbf{1040}$.

Greedy picks `Part` (1160). Because the benefit function is **monotone submodular**, greedy is within $1-1/e\approx0.63$ of the optimal subset (Nemhauser–Wolsey–Fisher; HRU). Here greedy is in fact optimal for $k=1$. Add per-view *maintenance* cost or SPJ views and submodularity is lost (§6), so the $0.63$ guarantee no longer holds — the open general case.

---
*Part of the [DBMS Research catalog](../../README.md).*
