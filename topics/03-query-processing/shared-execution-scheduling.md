# Multi-query / shared execution scheduling

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/shared-execution-scheduling` · **Status:** partially-solved

## 1. Problem Statement

When many queries run concurrently they often touch the same tables, compute overlapping
predicates, and build identical or similar intermediates. **Work-sharing** (a.k.a.
multi-query optimization, MQO, and shared execution) exploits this: a shared scan reads each
base table once for all consumers; a shared hash table or join feeds many queries; common
sub-expressions are materialized once. The goal is to **minimize the total work (and
resource use) of a query set or a continuous query stream**, rather than optimizing each
query in isolation.

Formally, given a set/stream of queries $Q = \{q_1,\dots,q_m\}$, find a **shared physical
plan** — a DAG of operators whose nodes may serve multiple queries — that minimizes total
cost $\sum$ over shared operators, subject to per-query latency/SLA constraints.

- **Decision variant:** is there a shared plan with total cost $\le C$ meeting all SLAs?
- **Optimization (MQO) variant:** choose which common subexpressions to materialize/share to
  minimize total cost — classically **NP-hard** (Sellis 1988).
- **Online/streaming variant:** schedule a continuously arriving query stream over shared
  operators (shared scans, group-and-route) to maximize throughput.

It is **partially solved**: shared scans and operator sharing are deployed in production
(SharedDB, CJOIN, BigQuery-style shuffles, Snowflake), and good heuristics exist, but
*optimal* sharing is NP-hard and the online scheduling theory is incomplete.

## 2. Mathematical Foundations

Cast MQO as selecting a subset $S$ of candidate **common subexpressions** (CSEs) to
materialize. Each CSE $e$ has build cost $b(e)$ and, if materialized, reduces the cost of
every query reusing it. With reuse benefits, total cost is

$$\text{cost}(S) \;=\; \sum_{e\in S} b(e) \;+\; \sum_{q\in Q} \min_{\text{plan of }q \text{ using } S} \text{cost}(q\mid S).$$

This is a **plan-selection over an AND/OR DAG** and is NP-hard; the benefit of sharing is
typically **submodular** (diminishing returns), so greedy CSE selection gives a
$(1-1/e)$ approximation under matroid/cardinality constraints. Shared *scans* map to
**interval/coverage scheduling**: $m$ queries each need a (sub)range of a table; one circular
scan serves all with cost $\Theta(|T|)$ instead of $\Theta(m|T|)$ — an $m\times$ saving when
arrival times align. Continuous-query sharing (e.g. predicate indexing, group-by routing)
relates to **set-cover / facility-location** structure. The streaming-scheduling objective
(throughput / mean response time) connects to classic **online scheduling** with competitive
analysis.

## 3. State of the Art (SOTA)

- **Foundational:** **Sellis**, *Multiple-Query Optimization* (ACM TODS 1988) framed MQO and
  its NP-hardness; **Roy, Seshadri, Sudarshan, Bhobe** (SIGMOD 2000) gave practical greedy
  CSE-sharing in a Volcano optimizer.
- **Systems SOTA:** **QPipe** (Harizopoulos, Shkapenyuk, Ailamaki, SIGMOD 2005) shares work
  via per-operator "micro-engines"; **CJOIN** (Candea et al., VLDB 2009) shares a single
  pipelined star-join across many queries; **SharedDB** (Giannikis, Alonso, Kossmann, VLDB
  2012) batches and shares whole query plans; **DataPath** pushes a shared data-flow model.
- **Cloud SOTA:** materialized-view and **common-subexpression reuse** in **BigQuery /
  Snowflake / Databricks / SCOPE** (Microsoft's *CloudViews*, Jindal et al., recurring-job
  CSE reuse) deploys sharing at scale; **work-sharing for streaming** appears in
  **Flink / Trill**. ML/feature-pipeline sharing is a recent extension.

## 4. Upper Bound

- **Shared scan:** serving $m$ concurrent (sub)scans of table $T$ with one cooperative scan
  costs $O(|T| + \sum_j r_j)$ instead of $O(\sum_j |T|)$, an exact $\Theta(m)$ reduction in
  the work-overlap regime — provably optimal for full-table coverage (each byte read once).
- **CSE selection:** since the sharing benefit is submodular, **greedy** materialization
  yields a $(1-1/e)$-approximation to the optimal total cost under a cardinality/budget
  constraint (Nemhauser–Wolsey–Fisher), the best known general guarantee.
- **Pipelined shared joins (CJOIN/SharedDB):** total join work approaches that of a *single*
  join over the union of probes, i.e. amortized $O(1)$ extra per added query under shared
  build — an empirical near-optimal upper bound rather than a closed-form one.

## 5. Lower Bound

- **NP-hardness:** optimal multi-query plan selection (which CSEs to share/materialize) is
  **NP-hard** (Sellis 1988; reductions from set-cover/Steiner-tree-in-DAG), so no
  polynomial-time exact algorithm exists unless P = NP.
- **Inapproximability:** because the structure embeds **weighted set cover**, the cost
  objective is hard to approximate better than a logarithmic factor in the worst case
  (set-cover $\Omega(\ln n)$ hardness), bounding general MViews/CSE selection.
- **Online floor:** for the streaming/online scheduling variant, adversarial arrival orders
  impose competitive-ratio lower bounds (no online scan-sharing scheduler can match the
  offline optimum on adversarial sub-range requests) — competitive-analysis model.

## 6. The Gap

Shared scans and simple operator sharing are essentially solved (tight $\Theta(m)$ wins,
deployed). The remaining gap is in **optimal CSE selection and joint scheduling**: greedy
$(1-1/e)$ / $O(\ln n)$ approximations leave a provable gap to the NP-hard optimum, and we
lack a unified theory that *jointly* picks what to share, when to materialize, and how to
schedule under SLA and memory constraints — especially online, with imperfect cost
estimates. Closing it requires approximation algorithms with tighter, instance-dependent
guarantees and competitive online schedulers for the streaming case.

## 7. Current Research (as of June 2026)

- **Cloud CSE reuse** at scale: Microsoft (Jindal et al., *CloudViews / computation reuse in
  SCOPE*), and analogous recurring-workload reuse in Snowflake/Databricks
  *(frontier — verify)*.
- **EPFL DIAS (Ailamaki)** continuation of QPipe-style adaptive work-sharing on modern
  hardware and heterogeneous accelerators *(frontier — verify)*.
- **Learned / cost-model-driven sharing** that predicts overlap and schedules shared
  operators under uncertainty; sharing for **vector/embedding and feature pipelines** in
  ML serving *(frontier — verify)*.
- **Shared execution for streaming** (sub-expression sharing in Flink/Trill-style engines)
  and multi-tenant resource-aware scheduling.

## 8. Future Work

- Approximation algorithms for joint CSE-selection + scheduling beating greedy in practice
  with provable instance-optimal guarantees.
- Competitive online schedulers for shared scans/joins under adversarial and stochastic
  arrivals.
- SLA-aware sharing that trades total-work minimization against per-query latency.
- Sharing across heterogeneous engines (CPU/GPU) and across ML + relational pipelines.

## 9. Key References

- **[Foundational]** T. K. Sellis. *Multiple-Query Optimization.* ACM TODS 13(1), 1988.
- **[Foundational]** P. Roy, S. Seshadri, S. Sudarshan, S. Bhobe. *Efficient and Extensible Algorithms for Multi Query Optimization.* SIGMOD, 2000.
- **[SOTA]** S. Harizopoulos, V. Shkapenyuk, A. Ailamaki. *QPipe: A Simultaneously Pipelined Relational Query Engine.* SIGMOD, 2005.
- **[SOTA]** G. Candea, N. Polyzotis, R. Vingralek. *A Scalable, Predictable Join Operator for Highly Concurrent Data Warehouses (CJOIN).* PVLDB, 2009.
- **[SOTA]** G. Giannikis, G. Alonso, D. Kossmann. *SharedDB: Killing One Thousand Queries with One Stone.* PVLDB, 2012.
- **[SOTA]** A. Jindal, K. Karanasos, S. Rao, H. Patel. *Selecting Subexpressions to Materialize at Datacenter Scale (CloudViews).* PVLDB, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
