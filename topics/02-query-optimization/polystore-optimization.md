---
id: 02-query-optimization/polystore-optimization
title: "Cross-engine and polystore query optimization"
topic: 02-query-optimization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Cross-engine and polystore query optimization

> **Topic:** Query Optimization · **ID:** `02-query-optimization/polystore-optimization` · **Status:** open

## 1. Problem Statement

A **polystore** (or federated / multi-engine) system answers a single query by composing operators across heterogeneous backends — a relational warehouse, a document store, a graph engine, a search index, a key-value store, a Spark cluster — each with its *own* cost model, capabilities, data model, and statistics. Given a query $Q$ and a set of engines $\{E_1,\dots,E_n\}$, decide (i) which subexpressions to *delegate* to which engine (operator placement / pushdown), (ii) the cross-engine *data-movement* plan, and (iii) the residual computation in the mediator — minimizing total cost.

The core difficulty: the per-engine cost models are **incompatible and non-comparable** (different units, calibration, and accuracy), so the global optimizer cannot simply add them.

- **Decision variant:** does a cross-engine plan of cost $\le B$ exist under a common cost calibration?
- **Optimization variant:** find the min-cost delegation + movement plan.
- **Capability-feasibility sub-problem:** does *any* feasible plan exist given each engine's limited operator set (capability negotiation)?

## 2. Mathematical Foundations

Build on the **mediator/wrapper** architecture (Wiederhold; Garcia-Molina et al., TSIMMIS) and **capability-based optimization** (Garlic; Roth–Schwarz). Each engine exports a *capability description* — which operators it can evaluate, with what binding patterns — and a *cost interface* $\hat{c}_{E}(\text{op})$. A plan is a labeled operator DAG with an engine assignment $a: \text{ops} \to \{E_1,\dots,E_n,\textsf{mediator}\}$ subject to capability constraints.

The central formal obstacle is **cost-model heterogeneity**: $\hat{c}_{E_i}$ and $\hat{c}_{E_j}$ are not on a common scale; comparing them requires a **calibration map** $\phi_i:\hat{c}_{E_i}\to \mathbb{R}_{\ge 0}$ learned by *probing* (microbenchmarks), à la the **calibration approach** of Du–Krishnamurthy–Shan for heterogeneous DBMS. Output cardinalities still obey the **AGM bound** across the global query, but per-engine cardinality estimates are *opaque*. Operator placement reduces to a **constrained graph-partitioning / multiway-cut** problem on the operator DAG with capability constraints.

## 3. State of the Art (SOTA)

- **Systems SOTA:** **BigDAWG** (MIT/Intel ISTC) introduced *islands of information* with CAST operators between engines; **Garlic** (IBM) and **DiscoDB/Calcite** establish capability-based federation; **Apache Calcite**, **Presto/Trino connectors**, **Polypheny-DB**, and **Myria** federate heterogeneous sources. **CloudMdsQL** gives a functional SQL-like language for multistore. Estocada/ESTOCADA (Inria) optimizes across views materialized in different stores.
- **Theory SOTA:** there is no clean theory; results are about *capability-aware enumeration* and *view-based rewriting* (answering queries using views, Halevy) when each store is described as a set of views.

## 4. Upper Bound

When stores are modeled as views, plan generation is **answering queries using views** — for conjunctive queries and views, finding maximally-contained/equivalent rewritings is decidable via the **bucket / MiniCon / inverse-rules** algorithms (Levy–Mendelzon–Sagiv; Pottinger–Halevy), exponential in query size in the worst case but practical. Operator placement given a *calibrated* cost model is solved by Cascades-style top-down enumeration with engine as a physical property; complexity is $2^{O(n)}$ in the number of operators, the same regime as single-engine optimization.

## 5. Lower Bound

- **Answering queries using views** for conjunctive queries is **NP-complete** (deciding equivalent rewriting), via query-containment hardness (Chandra–Merlin); for richer query/view classes (recursion, arithmetic) it becomes **undecidable**.
- The placement/partitioning of an operator DAG across engines with capacity constraints is **NP-hard** (multiway cut / graph partitioning).
- **Information-theoretic obstacle:** with incomparable cost models, no algorithm can globally optimize without $\Omega(\cdot)$ probing to calibrate — calibration error lower-bounds achievable plan quality.

## 6. The Gap

This is genuinely **open**. Even granting calibrated costs, there is no global-optimality guarantee because each engine is a black box whose true cost and cardinality are revealed only at runtime. The gap is not a tidy upper-vs-lower complexity gap but a *modeling* gap: we lack (a) a principled common cost currency across engines, and (b) cross-engine cardinality propagation. Closing it would require either a standardized cost/statistics interface (a "cost exchange protocol") or fully *learned* cross-engine cost models with transfer guarantees.

## 7. Current Research (as of June 2026)

- **Learned, transferable cost models** that map heterogeneous engine costs to a common scale via probing + ML (zero-shot cost models, e.g. work from TU Darmstadt/Berlin). *(frontier — verify)*
- Adaptive/runtime re-delegation when an engine underperforms its estimate.
- Lakehouse + polystore convergence: Trino, DuckDB, and Velox-based engines as universal execution substrates over open table formats (Iceberg/Delta). *(frontier — verify)*
- Capability negotiation and cross-engine pushdown for vector/search predicates alongside relational ops.

## 8. Future Work

- A standard *cost and statistics exchange* interface across engines.
- Cross-engine cardinality estimation with error propagation guarantees.
- Provable approximation for capability-constrained operator placement.
- Benchmarks isolating polystore planning quality from per-engine execution.

## 9. Key References

- **[Foundational]** G. Wiederhold. *Mediators in the Architecture of Future Information Systems.* IEEE Computer, 1992. — [DOI](https://doi.org/10.1109/2.121508)
- **[Foundational]** L. Haas et al. *Optimizing Queries Across Diverse Data Sources (Garlic).* VLDB, 1997. — [DBLP](https://dblp.org/rec/conf/vldb/HaasKWY97.html)
- **[Foundational]** A. Y. Halevy. *Answering Queries Using Views: A Survey.* VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100054)
- **[SOTA]** J. Duggan et al. *The BigDAWG Polystore System.* SIGMOD Record, 2015. — [DOI](https://doi.org/10.1145/2814710.2814713)
- **[SOTA]** B. Kolev et al. *CloudMdsQL: Querying Heterogeneous Cloud Data Stores with a Common Language.* Distributed and Parallel Databases, 2016. — [DOI](https://doi.org/10.1007/s10619-015-7185-y)
- **[Survey]** R. Tan, R. Chirkova, V. Gadepally, T. Mattson. *Enabling Query Processing across Heterogeneous Data Models: A Survey.* IEEE Big Data, 2017. — [DOI](https://doi.org/10.1109/BigData.2017.8258302)

## 10. Worked Example

A query joins `Orders` (relational warehouse $E_1$, 1M rows) with `Reviews` (document store $E_2$, 200K docs) on `product_id`, filtering `Reviews.stars = 5` (selectivity $0.1$).

Two plans:

- **Plan A — move-then-join in mediator:** ship all 200K reviews to the mediator, filter, join. Movement cost dominates: $200\text{K} \times c_{\text{net}}$.
- **Plan B — pushdown filter to $E_2$:** $E_2$ applies `stars = 5` first, emitting only $200\text{K}\times 0.1 = 20\text{K}$ docs, then move + join. Movement drops $10\times$.

The catch: $E_1$ reports cost in *page reads*, $E_2$ in *internal credits*. The calibration map $\phi_2$ learned by probing finds $1\text{ credit}\approx 0.3$ page-reads. Only after applying $\phi_2$ can the optimizer compare:
$$\hat{C}(B)=\underbrace{20\text{K}\cdot c_{\text{net}}}_{\text{move}}+\phi_2(\text{filter})+\underbrace{C_{\text{join}}}_{\text{mediator}} \ll \hat{C}(A).$$
Without calibration, the opaque $E_2$ filter cost looks "free" or "infinite," and the optimizer cannot reliably choose B over A — the core heterogeneity obstacle.

---
*Part of the [DBMS Research catalog](../../README.md).*
