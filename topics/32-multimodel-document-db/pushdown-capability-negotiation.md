# Pushdown capability negotiation in federation

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/pushdown-capability-negotiation` · **Status:** partially-solved

## 1. Problem Statement
A federated/multi-model query engine sits over heterogeneous sources (a relational DB, a document store, a key-value or graph backend, a REST/SaaS endpoint) that each expose a *limited and asymmetric* set of operations they can execute locally. The engine must decide, for a logical plan, **which sub-expressions to push down** to each source and which to evaluate in the federation layer, so as to minimize cost while respecting each source's *capability profile*.

Variants:
- **Feasibility (decision):** does there exist *any* executable plan, i.e., can every required operation be either pushed to a willing source or evaluated centrally given the data movement allowed? (Classic "capability-based rewriting": some sources cannot answer a query at all without a required binding pattern.)
- **Optimization:** among feasible plans, find the minimum-cost one (the relevant practical problem).
- **Negotiation/online:** capabilities are discovered incrementally (e.g., probing a SaaS API), so the optimizer must reason under partial knowledge of what each source supports.

The genuinely open part is *partial, asymmetric predicate and operator pushdown*: a source may support `=` but not `>`, may push `LIKE 'x%'` but not `LIKE '%x'`, may support a join only with a binding pattern, may push aggregation only when grouped on an indexed column, and may differ in supported types/collations.

## 2. Mathematical Foundations
The foundational model is **answering queries using capabilities/views with limited access patterns**:
- A source capability is formalized as a set of *access templates* (binding patterns $\mathit{adornment} \in \{b,f\}^k$) plus a *capability grammar* describing which relational-algebra fragments it can evaluate. This generalizes Rajaraman–Sagiv–Ullman's *answering queries using views with binding patterns* and Florescu–Levy–Manolescu–Suciu's capability-based query rewriting.
- **Recursive feasibility:** with binding-pattern restrictions, deciding whether a conjunctive query is answerable is tied to the *connection/reachability* of a datalog-like program; minimal executable plans correspond to a least fixpoint over which variables become "bound and retrievable."
- **Cost optimization** layers a System-R style join/operator DAG search (Selinger) on top, but the search space is constrained by the capability lattice. Predicate pushdown forms a *partial order*: capability sets are closed under intersection but not arbitrary union, giving a meet-semilattice $(\mathcal{C}, \sqcap)$ that the optimizer must traverse.

Key theorem it rests on: query answerability under access-pattern limitations is decidable but can require *non-trivial* (sometimes exponential-size) executable plans (Rajaraman–Sagiv–Ullman, PODS 1995; Li–Chang on answering queries with binding patterns).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** capability-based rewriting (Florescu et al., 1999), source descriptions in GAV/LAV mediation, and minimal-plan synthesis under binding patterns are well understood for conjunctive queries; Deutsch–Ludäscher–Nash and Benedikt et al.'s *PDQ / cost-based plan synthesis with constraints* give complete plan-search procedures that respect access methods and integrity constraints.
- **Systems-SOTA:** Apache Calcite's adapter/`RelOptRule` pushdown framework, Trino/Presto connector pushdown (predicate, aggregate, TopN, join), Spark's `SupportsPushDownFilters`/`SupportsPushDownAggregates` Data Source V2, DuckDB's filter/projection pushdown into Parquet/Arrow, and PostgreSQL FDW (`postgres_fdw`) remote-condition pushdown. These encode capabilities as ad-hoc per-connector predicates rather than a uniform negotiated profile.

## 4. Upper Bound
For **conjunctive queries** under binding-pattern access limitations, deciding answerability and producing a minimal executable plan is achievable; plan synthesis with constraints (Benedikt et al.'s PDQ) is **complete and decidable** but worst-case **exponential** in query size (the proof system explores chase-derived candidate plans). Cost-optimal pushdown selection is solved in practice by branch-and-bound over the capability-restricted plan DAG; no better-than-exponential guarantee is known for the general cost-optimization variant. In the model of *RAM with a cost oracle*, greedy/heuristic pushdown is linear in plan size but not optimal.

## 5. Lower Bound
- Cost-optimal join ordering is already **NP-hard** (Ibaraki–Kameda) for general query graphs; adding capability constraints only restricts the feasible set, so the optimization variant is **NP-hard** as well.
- Answerability under access patterns is **complete for** classes between PTIME and PSPACE depending on the query language (conjunctive vs. with negation/recursion); with integrity constraints, deciding existence of a plan can be undecidable in the full setting (it reduces to constraint implication / the chase termination problem).
- No unconditional super-polynomial *evaluation* lower bound beyond these; the hardness is in *plan choice*, not execution.

## 6. The Gap
The conjunctive, static-capability case is essentially **closed** (complete synthesis procedures exist; hardness matches). The open gap is twofold: (1) a *uniform formal calculus* for **partial, asymmetric predicate pushdown** (per-operator, per-type, per-collation, partial predicates with residuals computed centrally) — current systems hard-code this; and (2) **online capability negotiation** with provable competitive bounds, where the optimizer learns capabilities by probing. Closing it means a capability algebra that composes across models (document filter pushdown vs. relational predicate pushdown vs. graph traversal pushdown) with a cost model and a matching optimality guarantee.

## 7. Current Research (as of June 2026)
- Connector-pushdown formalization and *residual predicate* accounting in Trino, Calcite, and Velox-based engines is active engineering, increasingly described declaratively *(frontier — verify the extent of cross-engine standardization)*.
- Substrait as a portable plan IR aims to carry capability/pushdown negotiation between engines and accelerators; capability advertisement is an open design point.
- Learned/adaptive federation cost models (extending Benedikt et al.'s PDQ and learned cardinality estimation) to drive pushdown decisions under uncertainty are an emerging PODS/SIGMOD direction.

## 8. Future Work
- A compositional **capability algebra** spanning relational, document, and graph operators with sound residual-evaluation semantics.
- Competitive-ratio analysis for *online* capability discovery/negotiation.
- Pushdown that is provenance- and semantics-preserving across model boundaries (e.g., NULL/missing-field and collation mismatches between SQL and JSON sources).
- Integration with privacy/cost SLAs: pushdown that respects data-egress and policy constraints, not only execution cost.

## 9. Key References
- **[Foundational]** A. Rajaraman, Y. Sagiv, J. D. Ullman. *Answering Queries Using Templates with Binding Patterns.* PODS, 1995. — [DBLP search](https://dblp.org/search?q=Answering+Queries+Using+Templates+with+Binding+Patterns)
- **[Foundational]** D. Florescu, A. Levy, I. Manolescu, D. Suciu. *Query Optimization in the Presence of Limited Access Patterns.* SIGMOD, 1999. — [DOI](https://doi.org/10.1145/304181.304210)
- **[Foundational]** P. G. Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[SOTA]** M. Benedikt, J. Leblay, B. ten Cate, E. Tsamoura. *Generating Plans from Proofs: The Interpolation-based Approach to Query Reformulation (PDQ).* Morgan & Claypool / ICDT line, 2016. — [DOI](https://doi.org/10.1007/978-3-031-01856-5)
- **[SOTA]** E. Begoli, J. Camacho-Rodríguez, J. Hyde, M. Mior, D. Lemire. *Apache Calcite: A Foundational Framework for Optimized Query Processing Over Heterogeneous Data Sources.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3190662), [arXiv](https://arxiv.org/abs/1802.10233)

## 10. Worked Example

Query: `SELECT name FROM Orders WHERE region='EU' AND amount > 500 AND descr LIKE '%urgent%'`, where `Orders` lives in a SaaS source.

Capability profile of the source: equality predicates pushable; range `>` pushable; prefix `LIKE 'x%'` pushable; **infix** `LIKE '%x%'` *not* pushable. So the optimizer splits the WHERE conjunction:

- Pushed down: `region='EU' AND amount > 500` → source returns the filtered rows.
- Residual (evaluated in federation layer): `descr LIKE '%urgent%'`.

Cost trace with $|Orders| = 10^6$ rows, selectivity $\sigma_{\text{region}} = 0.2$, $\sigma_{\text{amount}} = 0.05$:

- Pushdown reduces transferred rows to $10^6 \times 0.2 \times 0.05 = 10^4$.
- The federation then applies the infix filter on $10^4$ rows instead of $10^6$ — a $100\times$ reduction in both data movement and residual-filter work.

If instead `region` lacked an index and the source refused the equality push (asymmetric capability), the optimizer would push only `amount > 500` ($5\times10^4$ rows) and evaluate the rest centrally. The capability profile, not the logical plan alone, dictates the split.

---
*Part of the [DBMS Research catalog](../../README.md).*
