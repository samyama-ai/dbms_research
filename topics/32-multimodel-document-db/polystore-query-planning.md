# Polystore query planning over heterogeneous engines

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/polystore-query-planning` · **Status:** partially-solved

## 1. Problem Statement
A **polystore** answers one query over several *autonomous* storage engines (e.g., a relational warehouse, a document store, a graph DB, a key-value store, an array store), each with **incomparable capabilities** (which operators it can push down), **incomparable cost models**, and independent statistics. Planning must:
- **decompose** the query into sub-queries, each expressible in some engine's native dialect/capability;
- decide **where each operator executes** (pushdown vs. execute in a federation/middleware engine), respecting capability limits;
- choose **data-movement and join sites** (which intermediate results to ship where), and an overall plan minimizing a global cost (latency or resource).

This differs from multi-model optimization *within one engine* (see multimodel-query-optimization): here the stores are black boxes with limited, sometimes only-described capabilities. It generalizes classic **distributed/federated query optimization** and **answering queries using views/capabilities**. Variants: capability-feasible decomposition (decision: is the query answerable given pushdown limits?), and cost-optimal decomposition (optimization).

## 2. Mathematical Foundations
- **Capability-based / source-limited query answering:** sources are described by capability records or as views with binding patterns; planning = **answering queries using views** (Levy–Mendelzon–Sagiv; Halevy survey) restricted to feasible access patterns, which is the formal core.
- **Distributed cost model:** total cost = local processing + **data-shipping cost** over the network; optimizing join order *and* site selection is the System R*/distributed-INGRES problem, NP-hard in general.
- **Capability as an algebra:** each store exposes a set of supported algebraic operators; a plan is valid iff every sub-plan assigned to a store lies in that store's operator closure. This is a **covering/assignment** problem layered on join ordering.
- **Cost incomparability:** stores report costs on different scales; reconciling them is a *calibration* problem (often via learned per-store cost functions or micro-benchmarks).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **BigDAWG** (Stonebraker/Intel-MIT, the canonical polystore, with "islands" and CAST/SCOPE operators), **Myria**, **Polypheny-DB**, **Apache Calcite** (adapters + cost-based federation), **Trino/Presto** and **Spark** connectors (predicate/aggregate pushdown), **Estocada/Tatooine** (view-based polystore rewriting, Manolescu et al.), and cloud federations (BigQuery Omni, Snowflake external tables). Calcite's pluggable rules + cost model is the most widely deployed capability-aware planner.
- **Theory-SOTA:** the answering-queries-using-views / capability-based-rewriting framework (Levy, Halevy, Florescu–Levy–Manolescu) gives decidability and rewriting algorithms; this is why the problem is *partially solved* — feasibility and rewriting are well understood for conjunctive queries.

## 4. Upper Bound
- For **conjunctive queries with sources as conjunctive views**, finding a maximally-contained / equivalent rewriting is decidable; the MiniCon and bucket algorithms run in time exponential in query size but practical for real queries (Pottinger–Halevy, *VLDBJ* 2001).
- Capability-restricted plan existence (with binding-pattern limitations) is decidable and the feasible-plan space is finite; cost-optimal selection over it is solvable by DP/branch-and-bound, giving an exponential-time exact algorithm and PTIME heuristics with no global guarantee.
- Pushdown maximization is a **monotone covering** problem amenable to greedy approximation.

## 5. Lower Bound
- **Distributed query optimization with data shipping is NP-hard** (site + order selection generalizes the join-order NP-hardness; Wang–Chen and the distributed-System R* analyses).
- **Answering queries using views** is NP-hard (rewriting existence for CQs is NP-complete; Levy–Mendelzon–Sagiv–Srivastava), and becomes **undecidable** with recursion or under certain integrity-constraint/capability descriptions.
- Cross-store **cost incomparability** imposes an *information-theoretic/empirical* barrier: with black-box stores, no plan-selection algorithm can be provably optimal without an accurate global cost model, which the autonomy of stores precludes obtaining exactly.

## 6. The Gap
**Partially solved.** Capability-aware *feasibility* and *rewriting* for conjunctive queries are solid (this is the "solved" part). The open part is **provably good cost-based planning across autonomous, incomparable engines**: there is no unified, calibrated cost model, no general decomposition optimality guarantee beyond the relational core, and limited theory for non-relational capabilities (graph paths, document unnest, array ops). The gap is the distance between (i) sound rewriting frameworks with no cost optimality and (ii) practical systems with heuristic, uncalibrated costs. Closing it needs cross-store cost calibration (likely learned), capability descriptions rich enough for graph/document operators, and decomposition algorithms with bounded suboptimality.

## 7. Current Research (as of June 2026)
- **Learned and adaptive cost calibration** across heterogeneous engines; runtime re-optimization when black-box cost estimates prove wrong *(frontier — verify maturity; mostly research prototypes)*.
- **View-based polystore rewriting** (Estocada lineage, Manolescu/Bonaque) extended to JSON/graph/array fragments.
- Lakehouse federation (Trino, Spark, DuckDB, Substrait as a portable plan IR) standardizing cross-engine plan exchange, enabling capability negotiation.

## 8. Future Work
- A standard capability-description language covering non-relational operators (Substrait is a step).
- Calibrated, comparable cross-store cost models with confidence intervals; robust/pessimistic planning under cost uncertainty.
- Decomposition with provable bounded-suboptimality and adaptive data-movement.

## 9. Key References
- **[Foundational]** A. Levy, A. Mendelzon, Y. Sagiv, D. Srivastava. *Answering Queries Using Views.* PODS, 1995. — [DOI](https://doi.org/10.1145/212433.220198)
- **[Foundational]** M. Stonebraker et al. *The BigDAWG Polystore System.* SIGMOD Record, 2015. — [DOI](https://doi.org/10.1145/2814710.2814713)
- **[SOTA]** R. Pottinger, A. Halevy. *MiniCon: A Scalable Algorithm for Answering Queries Using Views.* VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100048)
- **[SOTA]** R. Bonaque, B. Cautis, F. Goasdoué, I. Manolescu (Estocada/Tatooine). *Mixed-instance querying / view-based polystore rewriting.* VLDB / EDBT, 2016. — [HAL](https://inria.hal.science/hal-01321201v2)
- **[Survey]** A. Halevy. *Answering Queries Using Views: A Survey.* VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100054)
- **[Foundational]** L. Mackert, G. Lohman. *R* Optimizer Validation and Performance Evaluation for Distributed Queries.* VLDB, 1986. — [DBLP](https://dblp.org/rec/conf/vldb/MackertL86.html)

## 10. Worked Example

Query: "for each `customer` in a relational warehouse $W$, find friends-of-friends in a graph store $G$ who reviewed product $P$ (reviews live in a document store $D$)."

$$\text{ans} = \sigma_{\text{prod}=P}\big( W.\text{cust} \bowtie G.\text{fof} \bowtie D.\text{review} \big)$$

Capability records: $G$ can do the 2-hop `fof` traversal (relational stores cannot express it cheaply); $D$ can push down the `prod = P` filter on JSON reviews; $W$ joins and aggregates. Planning:

1. **Decompose** by capability: push `fof` to $G$ (only it can), push `prod=P` selection into $D$ (shrinks 1M reviews to ~500).
2. **Site selection.** Ship the 500 filtered review-ids and the `fof` edge set (say 2k pairs) up to $W$ for the final join, rather than shipping $W$'s 100k customers down. Estimated shipping $\approx 2.5\text{k}$ rows vs. $100\text{k}$ — a 40$\times$ saving.
3. **Cost incomparability.** $G$ reports cost in "traversed edges", $D$ in "scanned docs", $W$ in "I/O pages". The planner must calibrate these to one scale (learned/micro-benchmarked) before comparing alternative plans.

Capability-feasibility (can every sub-plan run on its assigned store?) is decidable via answering-queries-using-views; cost-optimal site selection over the feasible plans is the NP-hard part (section 5).

---
*Part of the [DBMS Research catalog](../../README.md).*
