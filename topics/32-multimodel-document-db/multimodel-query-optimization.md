# Multi-model query optimization across models

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/multimodel-query-optimization` · **Status:** open

## 1. Problem Statement
A single engine supports multiple data models — relational tables, JSON documents, and property graphs — within one query (e.g., a SQL/PGQ + SQL/JSON statement joining a table to a document field and traversing a graph). The problem: perform **joint, cost-based plan enumeration and selection over operators from all three algebras simultaneously**, rather than optimizing each model's subquery in isolation and gluing results. Outputs: a single physical plan minimizing estimated cost. Sub-problems:
- a **unified logical algebra** into which relational joins, document unnest/navigation, and graph pattern-matching/path operators all translate, so that cross-model rewrites (e.g., pushing a relational filter through a graph traversal, or turning a document-join into a graph reachability) are expressible;
- **plan enumeration** over the enlarged search space (model-crossing join orders, where to "materialize" between models);
- **cost comparability** — costing a graph traversal against a hash join against a document scan on one scale.
Decision/optimization variants: optimal join order is already the relational hard core; multi-model strictly enlarges it.

## 2. Mathematical Foundations
- **Relational core:** join-order optimization is the canonical hard subproblem; even for chain/star queries, choosing optimal bushy order is NP-hard (Ibaraki–Kameda; Cluet–Moerkotte). Dynamic programming (System R / `DPccp`) explores the join lattice.
- **Worst-case-optimal joins & the AGM bound** (Atserias–Grohe–Marx; Ngo–Ré–Rudra) give tight output-size bounds and algorithms (Leapfrog Triejoin, generic-join) that matter because **graph pattern matching is multiway join** — unifying graph and relational costing.
- **Algebra unification:** document navigation = nested relational algebra with unnest ($\mu$) and nest ($\nu$); graph matching = conjunctive regular path queries (CRPQs), themselves conjunctive queries with transitive closure. A common algebra is thus *nested relational algebra + transitive closure*, whose equivalences define the rewrite space.
- **Optimization as search:** plan space is a graph; transformation-based optimization (Volcano/Cascades) explores it via cost-guided rules; the multi-model rule set is the open object.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** "multi-model" engines — ArangoDB, OrientDB, Microsoft Cosmos DB, Oracle (relational + JSON + graph), SQL Server, and PostgreSQL (relational + `jsonb` + recursive-CTE graph) — largely optimize per-model and connect via generic joins; true cross-model cost-based rewriting is limited. Apache AGE, TigerGraph, Neo4j, DuckDB (relational+JSON), and Umbra/HyPer (compiling unified algebras) push toward unified optimization. The SQL:2023 standard (SQL/PGQ) finally gives a common surface language.
- **Theory-SOTA:** the worst-case-optimal-join line and factorized/FAQ frameworks (Abo Khamis–Ngo–Rudra, *FAQ*) provide a genuinely model-agnostic optimization theory for conjunctive workloads spanning relations and graphs; document features (order, nesting) are less integrated.

## 4. Upper Bound
- Optimal join order by DP (`DPccp`) costs time exponential in the number of relations but polynomial in the number of *connected subgraphs*; practical for tens of relations.
- **Worst-case-optimal** multiway-join algorithms run in $O(\mathrm{AGM}(Q))$ time, matching the worst-case output bound — applicable uniformly to relational joins and graph patterns, and (via unnest) to document joins.
- For the unified conjunctive fragment, the **FAQ/InsideOut** algorithm gives bounds parameterized by fractional hypertree width $\mathrm{fhw}$: time $\tilde{O}(N^{\mathrm{fhw}} + \text{out})$.

## 5. Lower Bound
- **Join-order optimization is NP-hard** for general (cross/bushy) query graphs (Ibaraki–Kameda 1984; Cluet–Moerkotte for the general case) — the multi-model space contains this as a special case, so optimal planning is NP-hard.
- **Conjunctive-query / CRPQ evaluation** is NP-hard in combined complexity; adding graph regular-path operators retains hardness.
- Fine-grained: triangle/clique subqueries (ubiquitous in graph patterns) are subject to **3SUM/APSP-conditional** lower bounds, bounding how fast even single multi-model joins can run.

## 6. The Gap
**Open.** Each model's optimization is individually mature, but there is no accepted **unified cost model and search algorithm** that provably trades off across models, nor a characterization of *when cross-model rewrites help*. The gap is (i) the absence of a single comparable cost metric (graph traversal vs. document parse vs. hash join), (ii) the explosion of the plan space with model-crossing operators and no good pruning theory, and (iii) cardinality estimation that spans models (see schemaless-cost-model). Closing it needs a common algebra with a complete, sound rewrite/equivalence theory, a unified cost calibration, and enumeration with provable optimality/quality on the cross-model lattice.

## 7. Current Research (as of June 2026)
- Compiling **SQL/PGQ + SQL/JSON** into a single relational-style plan in systems like DuckDB, Umbra, and Cosmos DB *(frontier — verify how much true cross-model cost-based rewriting ships vs. per-model)*.
- **Factorized databases / FAQ** and worst-case-optimal joins as the unifying optimization substrate (Olteanu, Ngo, Abo Khamis groups).
- Learned/RL-based join ordering (Bao, Balsa, Neo lineage) extended to heterogeneous operators.

## 8. Future Work
- A provably complete equivalence/rewrite system for nested-relational + transitive-closure algebra.
- Unified, calibrated cost model and cross-model statistics.
- Quality-guaranteed enumeration (anytime / bounded-suboptimality) over the multi-model plan lattice.

## 9. Key References
- **[Foundational]** P. Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** H. Ngo, C. Ré, A. Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013. — [DOI](https://doi.org/10.1145/2590989.2590991)
- **[SOTA]** M. Abo Khamis, H. Ngo, A. Rudra. *FAQ: Questions Asked Frequently.* PODS, 2016. — [DOI](https://doi.org/10.1145/2902251.2902280)
- **[Foundational]** G. Moerkotte, T. Neumann. *Analysis of Two Existing and One New Dynamic Programming Algorithm for the Generation of Optimal Bushy Join Trees (DPccp).* VLDB, 2006. — [DBLP](https://dblp.org/rec/conf/vldb/MoerkotteN06.html)
- **[Survey]** J. Lu, I. Holubová. *Multi-model Databases: A New Journey to Handle the Variety of Data.* ACM Computing Surveys, 2019. — [DOI](https://doi.org/10.1145/3323214)
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins.* SIAM J. Computing, 2013. — [DOI](https://doi.org/10.1137/110859440)

## 10. Worked Example

A cross-model triangle query: relational `Follows(a,b)`, document field path `mentions(b,c)` (unnested from JSON arrays), and graph edge `knows(c,a)`. Logically this is the three-way join
$$Q = \text{Follows}(a,b)\bowtie \text{mentions}(b,c)\bowtie \text{knows}(c,a),$$
the classic triangle — identical whether the relations come from a table, a shredded document, or a graph.

**AGM bound.** With each relation of size $N$, the fractional edge cover number is $\rho^* = 3/2$ (assign weight $\tfrac12$ to all three edges; every vertex is covered: $\tfrac12+\tfrac12 = 1$). So the output is at most $N^{3/2}$, and a worst-case-optimal join (Leapfrog Triejoin) computes $Q$ in $\tilde{O}(N^{3/2})$.

**Why binary joins lose.** Any pairwise plan first materializes a two-relation join, e.g. $\text{Follows}\bowtie\text{mentions}$, which can have $\Theta(N^2)$ tuples even though the final triangle has only $\le N^{3/2}$. On a star-of-paths instance this $N^2$ intermediate is realized — so a System-R/`DPccp` pairwise enumerator is asymptotically worse than the multiway algorithm.

The point for multi-model optimization: once `mentions` (document) and `knows` (graph) are costed on the *same* AGM scale as the relational `Follows`, the optimizer can pick the worst-case-optimal multiway plan across all three models — the unification Section 6 calls for.

---
*Part of the [DBMS Research catalog](../../README.md).*
