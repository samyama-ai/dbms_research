# Result-Cache and Semantic Reuse for OLAP

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/olap-result-reuse` · **Status:** open

## 1. Problem Statement
Analytical workloads are highly repetitive and overlapping (dashboards, BI tools, drill-downs). Given a stream of queries and a budget for cached results/materialized intermediates, **detect overlap among queries and rewrite a new query to reuse prior results** — exact result-cache hits, *subsumption* (a cached result is a superset that can be filtered/aggregated down), and **common-subexpression** reuse across concurrent queries. Variants:

- **Decision (containment/subsumption):** does cached query $Q_c$'s result suffice to answer (a subexpression of) $Q$? This is **query containment/answering-using-views**.
- **Optimization (view/cache selection):** which results to cache/materialize to minimize total cost over a workload under a space budget.
- **Multi-query optimization (MQO):** given a batch, find a shared plan minimizing total work by reusing common subexpressions.

It is *open*: containment is undecidable/intractable in general, the cache-selection problem is NP-hard, and no system robustly captures the full space of semantic reuse online at low overhead.

## 2. Mathematical Foundations
Reuse rests on **query containment and equivalence**. For conjunctive queries (CQs), $Q_1\sqsubseteq Q_2$ is decidable via **homomorphism / the chase** but **NP-complete** (Chandra–Merlin). Adding union → still decidable; adding inequalities or arithmetic comparisons makes containment $\Pi_2^p$ or harder; with general SQL (negation, aggregation, recursion) containment becomes **undecidable**. 

**Answering queries using views** (Halevy's survey) formalizes rewriting $Q$ over cached view definitions $V_1,\dots,V_m$: a maximally-contained or equivalent rewrite exists iff a homomorphism into the views' expansions exists. Aggregation reuse needs the algebra of **distributive/algebraic** measures: a finer group-by result can be rolled up to a coarser one ($\oplus$-mergeable monoids), and a cached cuboid subsumes its ancestors in the lattice $2^{[d]}$.

**Cache/view selection** is the weighted set-cover-like problem of choosing materializations to cover a workload's subexpressions at minimum cost — NP-hard, but the benefit function is often **submodular**, yielding $(1-1/e)$ greedy approximation. Subexpression detection across a batch is a **plan DAG / common-subexpression** problem.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Chandra–Merlin containment; Halevy's *Answering Queries Using Views* survey (VLDB Journal 2001); the chase & MiniCon/Bucket rewriting algorithms; Harinarayan–Rajaraman–Ullman greedy cuboid selection with submodular guarantee (SIGMOD 1996).
- **Systems-SOTA:** result caches in Snowflake, BigQuery, Redshift (exact + persisted-result reuse); **automatic materialized-view selection & recommendation** in Snowflake/Redshift/Oracle; Calcite's materialized-view rewriting (lattice + spool); **Sparser/recycling intermediates** and "recycling in MonetDB" (Ivanova et al., SIGMOD 2009); **multi-query optimization** in cloud (e.g., AWS, Microsoft SCOPE's CSE detection, Jindal et al. on cloud-scale CSE reuse, VLDB 2018).

## 4. Upper Bound
For CQ/UCQ workloads, exact rewriting using views is decidable and computable; MiniCon-style algorithms enumerate rewrites in time exponential in query size but polynomial in #views in practice. Cuboid/lattice roll-up reuse is $O(1)$ to detect (lattice ancestry) and linear to apply. Cache/view selection admits a **greedy $(1-1/e)$-approximation** for submodular benefit under a knapsack/cardinality budget (Nemhauser–Wolsey–Fisher). Result-cache hit testing is hashable to $O(1)$ for exact-match. These hold in the relational/RAM model for restricted query classes.

## 5. Lower Bound
Containment is **NP-complete for CQs** (Chandra–Merlin) and **undecidable** for SQL with negation/aggregation/recursion (reduction from CQ-with-inequalities / FO validity) — so *complete* semantic reuse is impossible in general. Optimal view/cache selection is **NP-hard** (set-cover reduction), and not approximable better than $(1-1/e)$ unless P=NP for the submodular-coverage formulation. Multi-query optimization (optimal shared plan) is NP-hard. Online cache replacement faces the **competitive-ratio** lower bounds of paging ($k$-competitive). These bound any reuse engine that seeks completeness or optimality.

## 6. The Gap
Genuinely **open**. Exact result-caching is shipping and easy; the hard, unsolved space is *semantic* reuse: detecting subsumption and partial overlap online, across SQL beyond CQs (with aggregation, window functions, joins), at low planning overhead, then *deciding* what to cache under churn. The gap between decidable-but-restricted theory and the messy full-SQL practical need is wide; closing it needs tractable approximate-containment tests, robust online cache-selection with guarantees, and integration with the optimizer.

## 7. Current Research (as of June 2026)
Active: learned/automatic materialized-view and result-cache recommendation in cloud warehouses (Snowflake, BigQuery, Redshift, Databricks); cloud-scale **common-subexpression reuse** across job graphs (Jindal/Microsoft lineage); semantic caching for BI/dashboard workloads; LLM/embedding-based detection of *semantically* overlapping NL or SQL queries for cache reuse *(frontier — verify)*; reuse-aware query optimizers that cost the option to spill-and-reuse. Open: tractable approximate subsumption for full SQL, and online cache-selection with competitive guarantees under workload drift *(frontier — verify)*. Groups: Halevy lineage (views), Microsoft GSL/Jindal (cloud CSE), warehouse vendors, Calcite community.

## 8. Future Work
- Tractable, sound (if incomplete) subsumption tests for SQL with aggregation/windows.
- Online materialization/cache selection with competitive-ratio or regret guarantees under drift.
- Optimizer-integrated reuse that jointly plans across concurrent queries (MQO at scale).
- Semantic (embedding-assisted) overlap detection with correctness safeguards.

## 9. Key References
- **[Foundational]** Chandra, Merlin. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Survey]** Halevy. *Answering Queries Using Views: A Survey.* The VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100054)
- **[Foundational]** Harinarayan, Rajaraman, Ullman. *Implementing Data Cubes Efficiently.* SIGMOD 1996. — [DOI](https://doi.org/10.1145/235968.233333)
- **[SOTA]** Ivanova, Kersten, Nes, Goncalves. *An Architecture for Recycling Intermediates in a Column-Store.* SIGMOD 2009. — [DOI](https://doi.org/10.1145/1559845.1559879)
- **[SOTA]** Jindal, Qiao, Patel, et al. *Computation Reuse in Analytics Job Service at Microsoft.* SIGMOD 2018. — [DOI](https://doi.org/10.1145/3183713.3190656)
- **[Foundational]** Nemhauser, Wolsey, Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)

## 10. Worked Example

A dashboard first runs $Q_c$: `SELECT region, SUM(sales) FROM orders WHERE year=2025 GROUP BY region`, caching a 4-row result `{North:120, South:90, East:150, West:60}`. A drill-down then issues $Q$: `SELECT SUM(sales) FROM orders WHERE year=2025 AND region IN ('North','South')`.

Subsumption test: $Q$'s predicate (`year=2025`, regions restricted) is *contained* in $Q_c$'s, and `SUM` is a distributive measure, so the optimizer rewrites $Q$ to run **on the cache**: $120+90=210$. No base-table scan.

Now suppose `orders` has $n=10^8$ rows. A fresh scan costs $\sim10^8$ tuple reads; the reuse path touches **2 cached rows** — a $\sim5\times10^7$ reduction.

Why aggregation rollup works: the cuboid `{year, region}` sits below `{year}` in the lattice $2^{[d]}$, so it can be rolled up via $\oplus$-merge. But a query grouping by `product` is *not* an ancestor of the cached cuboid — overlap detection correctly returns "no reuse," forcing a base scan. This is the line between cheap exact/subsumption hits and the open semantic-reuse problem.

---
*Part of the [DBMS Research catalog](../../README.md).*
