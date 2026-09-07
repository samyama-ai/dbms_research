---
id: 18-streaming-queries/continuous-multiquery-optimization
title: "Multi-query optimization for continuous queries"
topic: 18-streaming-queries
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Multi-query optimization for continuous queries

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/continuous-multiquery-optimization` · **Status:** partially-solved

## 1. Problem Statement
Given a workload of $N$ standing continuous queries over one or more data streams, compute a single shared execution plan (a DAG of operators with shared windows, predicates, and intermediate state) that minimizes resource cost — CPU per tuple, total state/memory, and/or network/latency — subject to per-query correctness and latency SLAs.

Variants:
- **Decision:** does a shared plan of cost $\le B$ exist?
- **Optimization:** find the minimum-cost shared plan (the practical target).
- **Online/adaptive:** queries arrive and leave, and stream statistics drift, so the shared plan must be re-optimized incrementally without violating SLAs during reconfiguration.

The continuous setting differs from classical (one-shot) multi-query optimization (MQO) because sharing must hold across *time*: shared sub-results are windows/state that must be maintained, not materialized once. Sharing scopes include identical sub-expressions, *subsuming* windows/predicates (a coarser computation feeds finer ones), and *fragment* sharing (partial operator state).

## 2. Mathematical Foundations
Model each query as a query plan; a shared plan is a DAG $G=(V,E)$ where nodes are operators with reuse. Classical MQO is the problem of selecting, for each query, one of several alternative plans so as to maximize sharing of common subexpressions — equivalent to a weighted set-cover / Steiner-tree-style selection and is **NP-hard** (Sellis 1988). Picking shared windows is closely tied to **interval/segment covering**.

Cost is often **submodular** in the set of shared materializations: marginal benefit of adding a shared view diminishes as more views are shared, so greedy yields a $(1-1/e)$ guarantee for the coverage relaxation when benefits are submodular and monotone. Sharing windows of different sizes uses **slicing/paning**: a window of range $r$ and slide $s$ is decomposed into panes (size $\gcd$ of involved ranges/slides), and aggregates compose via algebraic/commutative-monoid structure so a sub-aggregate is computed once and reused. For **distributive/algebraic** aggregates (SUM, COUNT, AVG), pane sharing gives exact reuse; for **holistic** aggregates (MEDIAN, COUNT DISTINCT) reuse requires mergeable sketches.

Formally a shared aggregation over many windows reduces to building a **Reactive Aggregator / FlatFAT** tree giving $O(\log W)$ amortized update for a window of $W$ tuples while answering arbitrary sub-window queries.

## 3. State of the Art (SOTA)
- **NiagaraCQ** (Chen, DeWitt, Tian, Wang, SIGMOD 2000): group-based sharing of selection/predicate constants — foundational systems result for scaling to large numbers of CQs.
- **TelegraphCQ** (Chandrasekaran et al., CIDR 2003) and **STREAM/CQL** (Arasu, Babu, Widom, VLDBJ 2006): shared operators, synopses, and the standard window semantics.
- **Pane/slice sharing:** Li et al. "No Pane, No Gain" (SIGMOD Record 2005); Krishnamurthy et al. on shared aggregation.
- **Cutty / Scotty** (Carbone et al.; Traub et al., ICDE 2018 / TKDE 2021): general aggregate sharing across out-of-order, arbitrary (session, sliding, tumbling) windows.
- **SharedDB / BatchDB** and **AStream / SharedJoin** (Karimov et al., SIGMOD 2019): sharing windowed joins across many concurrent queries in Flink.
- Systems-SOTA: Apache Flink, Spark Structured Streaming, Timely/Differential Dataflow, and Materialize provide operator/state sharing; specialized sharing remains workload-specific.

## 4. Upper Bound
For shared sliding-window aggregation, **FlatFAT / Reactive Aggregator** (Tangwongsan, Hirzel, Schneider, Wu, VLDB 2015) gives $O(\log n)$ amortized per update and $O(1)$ window query, $O(n)$ space, for a window of $n$ tuples — and Scotty (Traub et al.) extends this to general, overlapping windows shared across queries at amortized $O(\log)$ cost. For plan selection, greedy submodular-coverage gives a $(1-1/e)$-approximation to the sharing benefit; heuristic AND/OR-DAG search (Roy et al., SIGMOD 2000) is the practical optimizer. These are the best general guarantees; full MQO plan choice has no constant-factor approximation known in general.

## 5. Lower Bound
Classical MQO — choosing per-query plans to maximize common-subexpression sharing — is **NP-hard** and inapproximable in the worst case via reduction from weighted set cover (hence $\Omega(\ln n)$-hard to approximate unless P=NP) (Sellis 1988; Roy et al. 2000). Optimal shared-window selection embeds **set cover / Steiner tree**, inheriting their hardness. In the streaming model, any operator that must answer a holistic aggregate (e.g., exact COUNT DISTINCT) over each of $N$ windows has $\Omega(N)$ space lower bounds from communication complexity (INDEX/DISJOINTNESS), so unbounded exact sharing is impossible — bounding requires approximation or mergeable sketches.

## 6. The Gap
The *online/adaptive* optimization problem — continuously re-deriving a near-optimal shared plan under churn (arriving/leaving queries, drifting statistics) with bounded reconfiguration cost and no SLA violation — has no tight competitive-ratio characterization. Static sharing is well-understood (good heuristics, submodular guarantees for aggregation); dynamic, cost-model-driven, multi-resource (CPU vs. state vs. latency) joint optimization is open. There is no algorithm with proven competitive ratio for online shared-plan maintenance, and no matching lower bound beyond the NP-hardness of the static core.

## 7. Current Research (as of June 2026)
- Generalized window slicing and stream-slice sharing continue (Traub, Rabl, Markl group at TU Berlin / HPI) extending Scotty to multi-dimensional and user-defined windows.
- Learned/cost-based adaptive sharing and reinforcement-learning operator placement for shared CQ DAGs *(frontier — verify)*.
- Sharing under exactly-once and watermarking semantics in Flink/Materialize; differential-dataflow sharing of arrangements (McSherry, Materialize).
- Multi-query sharing on streaming hardware accelerators (FPGA/GPU) and serverless/elastic stream processing *(frontier — verify)*.

## 8. Future Work
- A unified online competitive analysis of shared-plan maintenance under query and statistics churn.
- Multi-resource Pareto-optimal sharing (CPU, memory, network, latency) rather than single-cost.
- Provable sharing for holistic aggregates via mergeable sketches with error budgets.
- Co-optimizing sharing with load shedding and elasticity/auto-scaling.

## 9. Key References
- **[Foundational]** Sellis, T. *Multiple-Query Optimization.* ACM TODS, 1988. — [DOI](https://doi.org/10.1145/42201.42203)
- **[Foundational]** Chen, J., DeWitt, D., Tian, F., Wang, Y. *NiagaraCQ: A Scalable Continuous Query System for Internet Databases.* SIGMOD, 2000. — [DOI](https://doi.org/10.1145/342009.335432)
- **[Foundational]** Roy, P., Seshadri, S., Sudarshan, S., Bhobe, S. *Efficient and Extensible Algorithms for Multi Query Optimization.* SIGMOD, 2000. — [DOI](https://doi.org/10.1145/342009.335419) · [arXiv](https://arxiv.org/abs/cs/9910021)
- **[SOTA]** Tangwongsan, K., Hirzel, M., Schneider, S., Wu, K.-L. *General Incremental Sliding-Window Aggregation.* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2752939.2752940)
- **[SOTA]** Traub, J., Grulich, P., Cuéllar, A.R., Breß, S., Katsifodimos, A., Rabl, T., Markl, V. *Scotty: Efficient Window Aggregation for Out-of-Order Stream Processing.* ICDE 2018 / TKDE, 2021. — [DOI](https://doi.org/10.1109/ICDE.2018.00135)
- **[SOTA]** Karimov, J., Rabl, T., Markl, V. *AStream / AJoin: Shared Window/Join Processing.* SIGMOD, 2019. — [DBLP](https://dblp.org/rec/conf/sigmod/KarimovRM19.html) · [PDF](https://hpi.de/fileadmin/user_upload/fachgebiete/rabl/publications/2019/AStreamSIGMOD2019.pdf)
- **[Survey]** Arasu, A., Babu, S., Widom, J. *The CQL Continuous Query Language: Semantic Foundations and Query Execution.* VLDB Journal, 2006. — [DOI](https://doi.org/10.1007/s00778-004-0147-z)

## 10. Worked Example

Two standing queries over a stream of trades, both `SUM(volume)` over sliding windows on the same source:

- $Q_1$: range $6$ s, slide $2$ s.
- $Q_2$: range $4$ s, slide $2$ s.

**Without sharing:** each query maintains its own window. Per slide, $Q_1$ re-aggregates up to $6$ s of tuples and $Q_2$ up to $4$ s — overlapping work recomputed independently, and both rescan the shared recent tuples every $2$ s.

**With pane/slice sharing:** decompose into panes of size $\gcd(\text{ranges, slides}) = \gcd(6,4,2) = 2$ s. The stream becomes a sequence of pane partials $p_1, p_2, p_3, \dots$, each a single $\texttt{SUM}$ over one $2$-s slice, computed **once**:

$$Q_1\text{ at time }t = p_{t-2}+p_{t-1}+p_t \quad(3\text{ panes}), \qquad Q_2\text{ at time }t = p_{t-1}+p_t \quad(2\text{ panes}).$$

Suppose pane partials are $p_1{=}5,\ p_2{=}3,\ p_3{=}8,\ p_4{=}2$. At the slide ending after $p_4$: $Q_1 = p_2+p_3+p_4 = 13$, $Q_2 = p_3+p_4 = 10$ — and $p_3,p_4$ were each summed exactly once, then reused. Because `SUM` is a distributive (commutative-monoid) aggregate, pane reuse is exact. A FlatFAT/Reactive-Aggregator tree over the panes then answers any sub-window in $O(\log W)$ amortized time. (Holistic aggregates like `COUNT DISTINCT` would instead need mergeable sketches to share.)

---
*Part of the [DBMS Research catalog](../../README.md).*
