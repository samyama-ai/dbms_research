# Tunable consistency with provable SLA guarantees

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/tunable-consistency-sla` · **Status:** open

## 1. Problem Statement

Modern stores expose *consistency knobs* (e.g., Cassandra's ONE/QUORUM/ALL, DynamoDB's eventual/strong reads, Cosmos DB's five levels, session/read-your-writes toggles). The problem: given per-operation knob settings, **derive enforceable, composable Service-Level Agreements (SLAs)** on (a) *staleness* (how old a read may be, in time or versions) and (b) *latency* (a percentile bound), such that:
- each operation carries a guarantee that holds under a specified failure/contention model;
- guarantees **compose** across an operation sequence (a transaction or session), yielding an end-to-end SLA, not just per-op;
- the runtime can *select* knob settings to meet a declared SLA at minimum cost, or report infeasibility.

Variants: **decision** ("is this consistency configuration SLA-satisfiable under failure model $F$?"); **optimization** ("cheapest configuration meeting latency p99 $\le L$ and staleness $\le \Delta$"); **certification** ("emit a machine-checkable proof that the delivered result met its SLA"). Status is **open**: probabilistic staleness *prediction* exists (PBS), but *provable, composable, enforceable* SLAs spanning latency and staleness together do not.

## 2. Mathematical Foundations

Let an operation have a consistency level $c$ drawn from a lattice $\mathcal{C}$ ordered by strength (Viotti–Vukolić consistency hierarchy). A read returns a version $v$ with **staleness** $s = \max(0,\, \text{lat}_{\text{commit}}(v^\star) - \text{visible}(v))$, measured in time ($t$-staleness) or versions ($k$-staleness). The **Probabilistically Bounded Staleness** model (Bailis et al., VLDB 2012) gives, for partial quorums, the distribution
$$\Pr[\text{staleness} \le t] = f(R, W, N, \text{write-propagation delays}),$$
the *$\langle k,t\rangle$-staleness* guarantee. An SLA is a predicate $\Pr[\,s\le\Delta \wedge \text{lat}\le L\,]\ge 1-\delta$.

Composition needs an algebra: staleness under sequential composition is sub-additive only under monotonic-reads/session guarantees (Terry et al. session model); latency percentiles compose via convolution of operation-latency distributions (not simple addition of percentiles). The **CAP** theorem (Gilbert–Lynch 2002) and its quantitative refinement **PACELC** (Abadi 2012) set the feasibility boundary: under partition you trade availability vs. consistency, *else* latency vs. consistency. **Consistency-availability-convergence (CAC)** and the CALM theorem (Hellerstein–Ameloot) bound what is achievable coordination-free.

## 3. State of the Art (SOTA)

- **Systems:** Pileus / Tuba (Terry et al., SOSP 2013) — *consistency-based SLAs*: clients declare ranked (consistency, latency, utility) subSLAs and the system picks the highest-utility achievable one; this is the closest deployed analogue but offers *best-effort selection*, not a proof. Azure Cosmos DB exposes five well-defined levels with documented (but not formally certified) staleness bounds. Cassandra/DynamoDB expose tunable quorums.
- **Prediction:** PBS (Bailis et al.) predicts staleness distributions from quorum config and latency traces.
- **Theory:** consistency hierarchies (Viotti–Vukolić survey 2016), PACELC characterization, bounded-staleness models (TACT / "conits", Yu–Vahdat 2002) quantifying numerical/order/staleness error budgets.

## 4. Upper Bound

Given measured write-propagation and round-trip distributions, PBS computes $\langle k,t\rangle$-staleness probabilities in closed/Monte-Carlo form — an *achievable* per-op probabilistic guarantee. Pileus selects an SLA-maximizing configuration in polynomial time over a fixed menu of subSLAs. TACT enforces *hard* numerical/staleness bounds by blocking when an error budget is exhausted (an availability cost). These are the strongest known *constructive* results; all are per-operation or menu-restricted.

## 5. Lower Bound

CAP/PACELC are the governing impossibilities: no configuration can simultaneously guarantee linearizability, availability, and partition-tolerance (Gilbert–Lynch). Hence any *hard* latency SLA forces bounded staleness (or unavailability) under partition — staleness and latency cannot both be driven to zero. FLP impossibility (Fischer–Lynch–Paterson 1985) precludes guaranteed bounded-time consensus under asynchrony, so *deterministic* latency SLAs for strong ops are impossible without timing assumptions; SLAs must be probabilistic or partially synchronous. These are information-theoretic/impossibility bounds, not complexity bounds.

## 6. The Gap

We can *predict* staleness (PBS) and *select* among offered SLAs (Pileus), but we cannot yet **certify** a composable end-to-end SLA across a session/transaction with a checkable proof, nor optimally choose knobs to meet a declared joint latency+staleness target. The gap is conceptual (no composition algebra with soundness theorems) and practical (no runtime emits SLA-violation evidence). Closing it needs: a sound composition calculus for (consistency, staleness, latency) and a controller with regret/feasibility guarantees against drifting conditions.

## 7. Current Research (as of June 2026)

Threads: formal consistency-model algebras and mechanized soundness proofs (building on Viotti–Vukolić) *(frontier — verify)*; SLA-aware adaptive controllers using online learning with feasibility guarantees *(frontier — verify)*; verified observability that certifies delivered staleness from client-side metadata. Cosmos DB's bounded-staleness formalization and academic work at Berkeley (RISE lineage), MPI-SWS, and MSR are relevant. Differential-privacy-style *budgeted* guarantees (staleness budgets) are an emerging framing.

## 8. Future Work

- A composition algebra proving end-to-end SLAs from per-op knobs.
- Runtime certificates of delivered consistency/latency (auditable, tamper-evident).
- Cost-optimal knob selection under drifting latency with regret bounds.
- Unifying probabilistic staleness (PBS) with hard error-budget enforcement (TACT) in one declarative interface.

## 9. Key References

- **[Foundational]** Gilbert, S., Lynch, N. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* SIGACT News, 2002.
- **[Foundational]** Abadi, D. *Consistency Tradeoffs in Modern Distributed Database System Design (PACELC).* IEEE Computer, 2012.
- **[SOTA]** Bailis, P. et al. *Probabilistically Bounded Staleness for Practical Partial Quorums.* VLDB, 2012.
- **[SOTA]** Terry, D. et al. *Consistency-Based Service Level Agreements for Cloud Storage (Pileus).* SOSP, 2013.
- **[Foundational]** Yu, H., Vahdat, A. *Design and Evaluation of a Conit-Based Continuous Consistency Model (TACT).* ACM TOCS, 2002.
- **[Survey]** Viotti, P., Vukolić, M. *Consistency in Non-Transactional Distributed Storage Systems.* ACM Computing Surveys, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
