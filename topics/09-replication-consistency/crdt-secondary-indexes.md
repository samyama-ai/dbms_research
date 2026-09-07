---
id: 09-replication-consistency/crdt-secondary-indexes
title: "Convergent secondary indexes over CRDTs"
topic: 09-replication-consistency
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Convergent secondary indexes over CRDTs

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/crdt-secondary-indexes` · **Status:** open

## 1. Problem Statement
Conflict-free Replicated Data Types (CRDTs) give convergent *primary* state: replicas that have absorbed the same set of updates hold equal values. But applications need to **query** that state — "all users in region X", "documents tagged `urgent`", range scans, top-$k$, aggregates. A **secondary index** maps an attribute value to the set of primary keys having it; a **materialized view** is a derived query result. The problem: maintain such indexes/views as *first-class replicated objects that are themselves convergent (CRDTs)*, are kept consistent with the primary CRDT under concurrent updates, and answer queries without coordination.

Variants:
- **Equality index** (value → key-set): the canonical case.
- **Range / ordered index** (B-tree-like, supports range scans).
- **Aggregate / materialized view** (counts, sums, joins, top-$k$) — view maintenance over CRDTs.
- **Decision flavor:** given a primary CRDT type and a query, does a convergent index of bounded metadata exist that is *consistent* (returns exactly the keys whose merged primary state satisfies the predicate)?

## 2. Mathematical Foundations
A state-based CRDT is a join-semilattice $(S, \sqcup)$ with monotone, inflationary updates; convergence = commutativity/associativity/idempotence of $\sqcup$. A secondary index is a derived map $\iota: S \to I$ into another semilattice $(I, \sqcup_I)$. The core requirement is that $\iota$ be a **semilattice homomorphism** so that
$$\iota(s_1 \sqcup s_2) = \iota(s_1) \sqcup_I \iota(s_2),$$
i.e. the index converges *and agrees with the merged primary*. The trouble: indexing requires **removal** — when a key's attribute changes from $a$ to $b$, the index must drop $(a,\text{key})$ and add $(b,\text{key})$. Removal is non-monotone, so naive index-as-set is not a homomorphism. This forces tombstone/causal machinery: an Observed-Remove or **Add-Wins** set (OR-Set) keyed by unique update tags, or a **causal-length / dot-store** ($\delta$-CRDT) representation. The mathematics is that of *map and embedded-set CRDTs* (Almeida, Shoker, Baquero) plus the lattice theory of **bounded join-semilattices** and the algebra of incremental view maintenance (delta queries, the relational ring of Koch's DBToaster).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** $\delta$-state CRDTs and "Composition of state-based CRDTs" (Almeida, Shoker, Baquero, 2018) give the map/set building blocks; **Lasp** (Meiklejohn & Van Roy, PPDP 2015) provides a dataflow algebra (map/filter/product/fold) over CRDTs whose results are themselves CRDTs — the closest thing to declarative convergent views. **Gallifrey / "Mergeable Replicated Data Types"** (Kaki et al., OOPSLA 2019) derive merges from a relational specification, applicable to indexes.
- **Systems-SOTA:** AntidoteDB (causal+ transactional CRDT store, Shapiro/Preguiça/Zawirski lineage) supports limited indexing; Riak's secondary indexes were *not* convergence-safe across concurrent writes. Industrial CRDT stores (Redis Enterprise Active-Active, Azure Cosmos) largely punt on convergent secondary indexes.

## 4. Upper Bound
For **equality indexes** over a primary built from OR-Map/OR-Set, a convergent index exists with metadata $O(u)$ in the number of (causally live) updates $u$ — each indexed entry carries the dots of the update that produced it; $\delta$-mutators bound shipped state to changed dots. Lasp realizes arbitrary monotone relational views convergently with space proportional to the materialized relation plus provenance. Range indexes can be built as convergent ordered-log / LSM-style merge structures with $O(\log n)$ query, $O(u)$ space.

## 5. Lower Bound
Convergent indexing inherits the **metadata lower bounds of causal CRDTs**: Burckhardt, Gotsman, Yang, Zawirski (*Replicated Data Types: Specification, Verification, Optimality*, POPL 2014) prove that any implementation of an add-wins set with the optimal interface still requires per-element metadata $\Omega(\text{causal context})$ — you cannot index with removal support while keeping $O(1)$ amortized metadata in the worst case. Tombstone/dot overhead is provably necessary for non-monotone (delete/update) workloads. For *joins/aggregates*, convergent incremental view maintenance is at least as hard as non-replicated IVM, plus the cross-replica reconciliation, giving no sub-linear-in-updates general bound.

## 6. The Gap
**Genuinely open.** We have building blocks (Lasp, $\delta$-CRDTs, MRDTs) and matching metadata bounds for single OR-Sets, but *no* general theory characterizing which queries admit a convergent index of *bounded* (sub-linear, garbage-collectable) metadata, nor optimal tombstone-GC under causal stability. Range/top-$k$/multi-key-join convergent views lack tight bounds entirely. Closing the gap needs a query-class taxonomy mapped to achievable index metadata.

## 7. Current Research (as of June 2026)
- **Pure-operation-based CRDTs** and causal-stability GC to bound index tombstones (Baquero, Almeida, Shoker).
- Convergent IVM / "incremental Datalog over CRDTs" — extending Lasp's dataflow with negation and aggregation *(frontier — verify)*.
- Verified merge synthesis (Katara, "Synthesizing CRDTs from sequential data types", Laddad et al., OOPSLA 2022) applied to index types.
- Hydroflow/Hydro project work on convergent distributed dataflow at Berkeley (Hellerstein, Milano) *(frontier — verify)*.

## 8. Future Work
- A complete characterization of queries with bounded-metadata convergent indexes.
- Convergent range and top-$k$ structures with worst-case GC guarantees.
- Convergent multi-CRDT joins with formal correctness, and benchmarks vs. coordination-based indexing.

## 9. Key References
- **[Foundational]** Shapiro, Preguiça, Baquero, Zawirski. *Conflict-free Replicated Data Types.* SSS, 2011. — [DOI](https://doi.org/10.1007/978-3-642-24550-3_29)
- **[Foundational]** Burckhardt, Gotsman, Yang, Zawirski. *Replicated Data Types: Specification, Verification, Optimality.* POPL, 2014. — [DOI](https://doi.org/10.1145/2535838.2535848)
- **[SOTA]** Almeida, Shoker, Baquero. *Delta State Replicated Data Types.* JPDC, 2018. — [DOI](https://doi.org/10.1016/j.jpdc.2017.08.003)
- **[SOTA]** Meiklejohn, Van Roy. *Lasp: A Language for Distributed, Coordination-Free Programming.* PPDP, 2015. — [DOI](https://doi.org/10.1145/2790449.2790525)
- **[SOTA]** Kaki, Priya, Sivaramakrishnan, Jagannathan. *Mergeable Replicated Data Types.* OOPSLA, 2019. — [DOI](https://doi.org/10.1145/3360580)
- **[Survey]** Preguiça. *Conflict-free Replicated Data Types: An Overview.* arXiv:1806.10254, 2018. — [arXiv](https://arxiv.org/abs/1806.10254)

## 10. Worked Example

Primary: an OR-Map `user → region`. We want an equality index `region → {users}`. Two replicas start with `alice → EU` (tagged by dot $a_1$); the index holds `EU → {(alice, a_1)}`.

Concurrently:
- Replica 1 updates `alice → US` (new dot $a_2$, observing-remove of $a_1$): index becomes `US → {(alice, a_2)}`.
- Replica 2 updates `alice → APAC` (new dot $a_3$, observing $a_1$): index becomes `APAC → {(alice, a_3)}`.

Merge. The OR-Map's add-wins resolution keeps both live dots $\{a_2, a_3\}$ since neither observed the other; $a_1$ is removed by both. Index join gives `US → {(alice, a_2)}`, `APAC → {(alice, a_3)}` — and crucially **no** stale `EU` entry, because the homomorphism $\iota$ dropped $(EU, a_1)$ exactly when the primary dropped $a_1$. A query "users in EU" correctly returns $\emptyset$. Note the cost: each entry carries its dot ($O(u)$ metadata), illustrating the $\Omega(\text{causal context})$ lower bound — a tombstone-free index cannot resolve this concurrent re-tagging.

---
*Part of the [DBMS Research catalog](../../README.md).*
