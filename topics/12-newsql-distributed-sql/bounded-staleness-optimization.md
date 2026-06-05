# Bounded-staleness query optimization

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/bounded-staleness-optimization` · **Status:** partially-solved

## 1. Problem Statement

A geo-distributed SQL database keeps multiple replicas of each datum, each at a possibly
different **apply timestamp**. A read transaction (or a read-only query) is annotated with a
**staleness budget** $\Delta$: the query may observe any consistent snapshot whose timestamp is
within $[\,now-\Delta,\; now\,]$ (bounded staleness), instead of the latest committed state.

The problem is to build a **query planner** that, given $\Delta$, chooses for each
read/access path a **replica and a read timestamp** so as to **minimize query latency** (or
cost) while guaranteeing the chosen reads are mutually consistent (same snapshot or a valid
causal frontier).

- **Optimization variant:** minimize end-to-end latency $\mathcal{L}(P)$ over plans $P$
  (replica assignment + read-ts + join order) subject to staleness $\le \Delta$ and a chosen
  consistency level.
- **Decision variant:** does a plan with latency $\le \ell$ and staleness $\le \Delta$ exist?
- **Feasibility:** given per-replica apply-timestamps, is there a single snapshot ts within
  $\Delta$ readable at the *nearest* replicas for all referenced fragments?

## 2. Mathematical Foundations

Each replica $r$ has a **safe/apply timestamp** $\mathrm{safe}_r(t)$: the largest ts at which
$r$ can serve a consistent read without blocking. A read at timestamp $\tau$ on $r$ is *local
(fast)* iff $\tau \le \mathrm{safe}_r$, else it must **wait** until $r$ catches up — turning a
staleness choice into a latency choice. Choosing $\tau$ smaller (staler, within $\Delta$)
enlarges the set of replicas that can serve it locally; this is the **staleness–latency
trade-off** formalized as: minimize $\sum_{\text{fragments}} d(\text{client}, r)$ subject to
$\tau \le \min_r \mathrm{safe}_r$ over chosen $r$ and $now-\tau\le\Delta$.

Consistency requires a **read frontier**: under snapshot/strict isolation a single global
$\tau$; under **causal** consistency a vector frontier dominating the client's dependencies
(Lamport/HLC vector). The planner therefore augments classical **System R / Cascades** cost-based
optimization (Selinger 1979; Graefe) with two extra plan dimensions (replica, read-ts) and a
**snapshot-feasibility** constraint. Join order and replica choice interact: choosing a stale
local replica for one table may force the join partner to a distant fresh replica.

The choice problem with per-replica latencies and a shared-snapshot constraint is a
**constrained assignment**; with arbitrary fragment-replica latency matrices and joint
snapshot feasibility it generalizes facility-location-style assignment.

## 3. State of the Art (SOTA)

- **Systems SOTA:** **Spanner** exposes *bounded-staleness* and *exact-staleness* reads and
  picks the closest replica whose safe-time covers the chosen ts (OSDI 2012); **CockroachDB**
  *follower reads* and **YugabyteDB** follower/observer reads route stale reads to the nearest
  replica using a closed-timestamp / safe-time mechanism. **Azure Cosmos DB** offers a
  *bounded-staleness* consistency level as a first-class SLA knob.
- **Theory/optimizer SOTA:** the planner-level exploitation of $\Delta$ is mostly *rule-based*
  (route to nearest follower if its closed-timestamp $\ge now-\Delta$) rather than a full
  cost-based co-optimization of join order + replica + ts. Research on **consistency-aware
  query planning** and **latency-SLO routing** formalizes the assignment but stops short of an
  optimal integrated optimizer.

## 4. Upper Bound

For a *single* relation / point or range read, optimal replica selection under $\Delta$ is
**polynomial**: pick the latency-minimizing replica whose $\mathrm{safe}_r \ge now-\Delta$;
$O(R)$ over $R$ replicas. For a fixed shared snapshot $\tau$, per-fragment replica choice
decomposes and is solvable greedily in $O(F\cdot R)$ for $F$ fragments. The systems above
realize this rule-based optimum. Co-optimizing $\tau$, replica assignment, **and** join order
remains within the general cost-based optimizer's exponential search but is handled
heuristically; no separate hardness is invoked because join-order search is already the
dominant complexity.

## 5. Lower Bound

The embedded **join-ordering** subproblem makes general cost-based plan selection **NP-hard**
(Ibaraki–Kameda for cyclic/general queries), so the *integrated* bounded-staleness optimizer
inherits NP-hardness in the worst case. Independently, there is a **consistency lower bound**:
serving a read at ts $\tau$ consistently requires the replica to *know* it has applied all
writes $\le \tau$ — i.e., it must observe the safe-time watermark — so no protocol can serve a
fresh ($\Delta\to 0$) read locally without a coordination/round (a PACELC latency cost; Abadi
2012). Thus zero staleness forfeits the latency win — the trade-off is fundamental, not an
artifact.

## 6. The Gap

The *easy* core — pick nearest sufficiently-fresh replica for a fixed snapshot — is **solved**
and shipping. What is only **partially solved** is the **joint** optimization: choosing the read
timestamp, per-fragment replicas, and join order *together*, under causal (vector-frontier)
consistency and heterogeneous replica freshness, with a real cost model. There is no published
optimal-or-approximation-guaranteed algorithm for the integrated problem; current systems use
greedy/rule heuristics with no quantified optimality gap. Closing it means an approximation
algorithm (or hardness-of-approximation result) for the assignment-plus-join-order formulation.

## 7. Current Research (as of June 2026)

- **Learned routing** of stale reads using predicted replica freshness and network latency to
  beat static rules *(frontier — verify)*.
- Integrating staleness as a first-class **cost-model dimension** in Cascades-style optimizers
  (CockroachDB, planner research) rather than a post-plan routing rule.
- **Causal-consistency-aware** planning with vector read-frontiers for partially-replicated
  edge/geo deployments.
- SLA-driven freshness: per-query $\Delta$ derived from application latency budgets, with
  feedback control on observed safe-time lag.
Groups: CMU, MIT, Berkeley, Microsoft (Cosmos DB), and Cockroach/Yugabyte teams.

## 8. Future Work

- An approximation algorithm with a provable ratio for joint replica/ts/join-order selection.
- Optimizer cost models that price staleness against the *risk* of a wait (replica catch-up).
- Cross-query freshness scheduling: amortize safe-time advancement across concurrent stale reads.
- Benchmarks that vary $\Delta$ and replica lag to expose planner quality.

## 9. Key References

- **[Foundational]** Selinger, P., et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979.
- **[Foundational]** Ibaraki, T., Kameda, T. *On the Optimal Nesting Order for Computing N-Relational Joins.* ACM TODS, 1984.
- **[SOTA]** Corbett, J., Dean, J., et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012.
- **[Survey]** Abadi, D. *Consistency Tradeoffs in Modern Distributed Database System Design (PACELC).* IEEE Computer, 2012.
- **[Foundational]** Terry, D., et al. *Consistency-Based Service Level Agreements for Cloud Storage (Pileus).* SOSP, 2013.
- **[SOTA]** Taft, R., et al. *CockroachDB: The Resilient Geo-Distributed SQL Database.* SIGMOD, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
