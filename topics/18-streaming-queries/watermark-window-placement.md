---
id: 18-streaming-queries/watermark-window-placement
title: "Cost-based watermark/window placement in plans"
topic: 18-streaming-queries
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Cost-based watermark/window placement in plans

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/watermark-window-placement` · **Status:** open

## 1. Problem Statement

In a distributed dataflow plan, *where* should watermark generation, windowing, and aggregation operators be placed? Pushing windowed pre-aggregation early (near sources) reduces data volume but can be incorrect under late/out-of-order data; placing it late preserves correctness but inflates network and state cost. Watermark strategy (how aggressive, where re-stamped, how propagated through joins/unions) trades **latency** against **completeness/accuracy** (how much late data is dropped).

The problem: given a logical streaming query, a distributed topology with per-link costs and per-operator state budgets, and a target completeness/latency SLA, choose (a) the physical placement of watermark, window, and (partial/final) aggregation operators, and (b) watermark-emission policy, to minimize cost.

Variants: **decision** (does a placement meet SLA $L$ at cost $\le B$?), **optimization** (min cost s.t. SLA), and **counting/robust** variants under uncertain input rates and skew.

## 2. Mathematical Foundations

Model the plan as a DAG $G=(V,E)$ with operator candidates and a set of *placements* $\pi$. Event time $\tau$, watermark $W(t)=\max$ assertable lower bound on remaining timestamps. **Out-of-orderness** is captured by a delay distribution; completeness at watermark heuristic $h$ is $\Pr[\text{event later than } W]$.

Placement is a **constrained combinatorial optimization**: assign operators to nodes minimizing $\sum_{e} c_e \cdot \text{vol}_e(\pi) + \sum_v s_v(\pi)$ subject to memory and SLA constraints. This generalizes **operator placement / task assignment**, which is NP-hard (reduction from graph partitioning / quadratic assignment). The pre-aggregation legality is governed by **algebraic decomposability**: a window aggregate $g$ admits early partial aggregation iff it factors through a commutative monoid lift $\langle f_{\text{lift}}, \oplus, f_{\text{lower}}\rangle$ (the General Incremental Sliding-window framework, Tangwongsan et al. 2015) — i.e., it must be associative for safe placement before the shuffle.

Cost-based search inherits the **Selinger** dynamic-programming paradigm (System R, 1979) but over a richer space (placement × watermark policy × parallelism), and selectivity/rate estimates needed for the cost model are themselves the subject of the cardinality-estimation problem.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** The **Dataflow Model** (Akidau et al. 2015) formalizes windowing/triggers/watermarks but leaves placement to the engine. Flink and Spark do *rule-based* operator chaining and combiner pushdown; watermark placement is largely manual/heuristic. **Calcite** provides a streaming-aware cost-based optimizer skeleton but limited watermark reasoning. **Timely Dataflow** propagates progress (frontiers) compositionally, giving a principled substrate but not automatic placement.
- **Theory-SOTA:** No general optimal placement algorithm; results are restricted classes (tree topologies, linear chains) where DP or LP-relaxation gives approximations. Decomposable-aggregation pushdown (sliding-window GIA) is well understood as a *legality* rule, not a cost-optimal placement.

## 4. Upper Bound

For restricted topologies (in-trees / linear pipelines) with decomposable aggregates, **polynomial-time DP** yields optimal placement; LP-rounding gives constant-factor approximations for capacitated assignment variants. General-graph placement admits no known better-than-trivial poly-time algorithm; practical engines use greedy/ILP solvers with no global guarantee. Watermark-policy optimization under a fixed delay distribution reduces to a single-parameter latency/completeness frontier solvable to $\epsilon$ by line search.

## 5. Lower Bound

General operator/window placement is **NP-hard** (reduction from Quadratic Assignment / graph partitioning) and **inapproximable** within constant factors under standard assumptions for the most general capacitated form. Jointly optimizing watermark completeness under adversarial out-of-orderness inherits a **CAP/latency-vs-completeness impossibility**: you cannot simultaneously guarantee minimal latency and zero late-data loss when network delay is unbounded (an FLP-flavored argument — no finite watermark heuristic is both complete and bounded-latency on an asynchronous network).

## 6. The Gap

This is **genuinely open**. There is no accepted cost model that *jointly* captures placement, watermark aggressiveness, and the accuracy cost of dropped late data, and no optimizer that searches that joint space with guarantees. The gap is qualitative: between rule-based heuristics in production systems and the absence of any approximation algorithm for the general joint problem. Closing it requires (a) a validated cost model linking watermark heuristic to completeness, and (b) tractable search (DP/ILP relaxations) with provable competitive ratios under stochastic delay models.

## 7. Current Research (as of June 2026)

- **Learned / cost-based streaming optimizers** extending Calcite and Flink with ML rate/selectivity models to drive placement *(frontier — verify)*.
- Work on **adaptive watermarks** (data-driven, quantile-based watermark heuristics) — e.g., percentile watermark estimators that bound late-data loss probabilistically.
- **Auto-parallelization and operator-reconfiguration** systems (DS2 — Kalavri et al. OSDI 2018, and successors) that decide degree-of-parallelism; placement is an adjacent open layer.
- Decomposable-aggregation theory (Tangwongsan/Hirzel/Schneider lineage) being lifted into cost-based pushdown decisions.

## 8. Future Work

- A unified objective coupling latency, network cost, state budget, and accuracy-loss from late data.
- Approximation algorithms / competitive online placement under unknown input rates.
- Robust placement under rate skew and bursts (relate to cardinality estimation).
- Verified correctness of pre-aggregation pushdown under arbitrary trigger/retraction semantics.

## 9. Key References

- **[Foundational]** P. G. Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** T. Akidau, R. Bradshaw, C. Chambers, S. Chernyak, R. Fernández-Moctezuma, R. Lax, S. McVeety, D. Mills, F. Perry, E. Schmidt, S. Whittle. *The Dataflow Model.* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2824032.2824076)
- **[Foundational]** D. G. Murray, F. McSherry, R. Isaacs, M. Isard, P. Barham, M. Abadi. *Naiad: A Timely Dataflow System.* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522738)
- **[SOTA]** K. Tangwongsan, M. Hirzel, S. Schneider, K.-L. Wu. *General Incremental Sliding-Window Aggregation.* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2752939.2752940)
- **[SOTA]** V. Kalavri, J. Liagouris, M. Hoffmann, D. Dimitrova, M. Forshaw, T. Roscoe. *Three Steps is All You Need: Fast, Accurate, Automatic Scaling Decisions for Distributed Streaming Dataflows (DS2).* OSDI, 2018. — [USENIX](https://www.usenix.org/conference/osdi18/presentation/kalavri)
- **[Survey]** M. Hirzel, R. Soulé, S. Schneider, B. Gedik, R. Grimm. *A Catalog of Stream Processing Optimizations.* ACM Computing Surveys, 2014. — [DOI](https://doi.org/10.1145/2528412)

## 10. Worked Example

Query: per-key `SUM` over a window, with 4 source partitions each emitting $10^6$ tuples/s over $10^4$ keys, feeding one shuffle then a final aggregator. Compare two placements.

**Late placement** (aggregate only after the shuffle): every source tuple crosses the network. Cross-link volume $= 4 \times 10^6$ tuples/s.

**Early placement** (partial `SUM` pushed before the shuffle): `SUM` is decomposable — it factors as $\langle f_{\text{lift}}{=}\text{id},\ \oplus{=}{+},\ f_{\text{lower}}{=}\text{id}\rangle$ over a commutative monoid — so each source pre-aggregates its $10^6$ tuples into at most $10^4$ partial sums (one per key). Cross-link volume $= 4 \times 10^4$ tuples/s, a $100\times$ reduction.

Cost model: with per-link cost $c_e$, objective $\sum_e c_e\cdot\text{vol}_e(\pi)$ drops by that $100\times$ factor for early placement — but only because `SUM` is associative. Had the aggregate been `MEDIAN` (not decomposable into a small commutative-monoid lift), early partial aggregation would be illegal and the planner must keep the late placement. This is exactly the legality-vs-cost coupling the open problem asks an optimizer to search jointly, and general placement is NP-hard (reduction from quadratic assignment).

---
*Part of the [DBMS Research catalog](../../README.md).*
