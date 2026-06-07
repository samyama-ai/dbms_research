---
id: 09-replication-consistency/consistency-composition-theory
title: "Formal composition of consistency guarantees"
topic: 09-replication-consistency
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Formal composition of consistency guarantees

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/consistency-composition-theory` · **Status:** open

## 1. Problem Statement

Real applications stack many layers, each with its *own* consistency model: a browser/edge cache (read-your-writes), a CDN (eventual), an application-tier cache like Redis (often no guarantee), a primary store (snapshot isolation or causal+), a search index or analytics replica (eventual, async), a message queue (at-least-once, possibly reordered), and client-side local state. Engineers reason about each layer in isolation but the **end-to-end** guarantee a user observes is an emergent product of the whole stack — and it is routinely *weaker* than any single layer, in ways that surprise developers (the classic "I read my write from the DB but the search index hadn't caught up" anomaly).

The problem: **build a compositional theory that, given the consistency model of each component and how they are wired (sequential, parallel/replicated, with caches in front, with async propagation between them), predicts — soundly and as tightly as possible — the strongest end-to-end consistency guarantee the composite provides** (and dually, certifies that a target guarantee is met).

Variants: (a) **verification/decision** — does composite $C_1 \circ C_2 \circ \dots$ satisfy target guarantee $G$? (b) **synthesis** — what minimal per-layer guarantees suffice to achieve $G$ end-to-end at least cost? (c) **counterexample generation** — exhibit a client-observable anomaly when it does not.

## 2. Mathematical Foundations

The dominant formal substrate is the **axiomatic / abstract-execution** framework of Burckhardt (and Cerone–Bernardi–Gotsman): an execution is a structure $(\text{ops}, \mathsf{vis}, \mathsf{ar})$ with a **visibility** relation $\mathsf{vis}$ (which operations a given op observes) and an **arbitration** order $\mathsf{ar}$ (tie-break). A consistency model is a *conjunction of axioms* over $(\mathsf{vis},\mathsf{ar})$: e.g. **causal consistency** = $\mathsf{vis}$ is transitive and contains the session/program order; **read-your-writes**, **monotonic reads**, **PRAM**, **sequential**, **linearizability**, **snapshot isolation**, and **serializability** are each fixed axiom sets (Cerone, Bernardi, Gotsman, CONCUR 2015 lattice of consistency models).

Composition is then a **constraint-merging** operation: the composite's admissible executions are those consistent with each layer's axioms *plus* the wiring constraints (a cache's visibility is a sub-relation of its backing store's; async propagation relaxes $\mathsf{vis}$ to allow delay). The end-to-end guarantee is the **strongest axiom set entailed by the conjunction** — a meet in the lattice of models, but *not* simply the meet of the layers' positions, because wiring (caches in front, fan-out to replicas) can drop guarantees that neither layer drops alone (non-compositionality of, e.g., read-your-writes through a stateless cache). Linearizability is famously **local/compositional** (Herlihy–Wing 1990); weaker models generally are **not**, which is the crux.

## 3. State of the Art (SOTA)

- **Foundations:** Burckhardt, *Principles of Eventual Consistency* (2014) gives the operational+axiomatic specification framework; Cerone, Bernardi, Gotsman (2015) give a *lattice* and a uniform axiomatization that makes "strongest entailed model" precise.
- **Herlihy–Wing (1990):** linearizability *is* compositional (a system of linearizable objects is linearizable) — the one clean positive result; locality is exactly what weaker models lack.
- **Verification-SOTA:** tools like **CISE** (Gotsman et al., POPL 2016) prove application invariants under a given (weak) consistency model, and bounded model checkers / Jepsen-style checkers (Knossos, Elle — Kingsbury & Alvaro, VLDB 2020) detect violations; but these analyze *one* store, not a heterogeneous stack.
- No general, mechanized theory composes *heterogeneous* layers into a predicted end-to-end guarantee — the open core.

## 4. Upper Bound

For *checking* whether a finite observed history satisfies a fixed model, complexity is model-dependent: checking **serializability** of a history is NP-complete (Papadimitriou 1979), **linearizability** checking is NP-hard in general but polynomial for fixed object types; **causal consistency** checking is polynomial for some variants and NP-hard for others (Bouajjani, Enea et al.). Compositionally, given per-layer axioms one can in principle *over-approximate* the composite via constraint conjunction and check entailment with an SMT solver — decidable for the first-order axiom fragments used, but worst-case exponential. These are **logic/constraint-solving model** results; no tight bound for the *synthesis* variant is known.

## 5. Lower Bound

- **Non-locality** is the structural lower bound: Herlihy–Wing show only linearizability composes freely; for sequential consistency and weaker models, composing locally-correct components can violate the global model — so any sound composition theory *must* track cross-layer relations, ruling out purely modular ("multiply the labels") reasoning.
- **NP-completeness** of serializability checking (Papadimitriou, JACM 1979) and NP-hardness of various weak-consistency checking problems (Bouajjani–Enea–Hamza and follow-ups) lower-bound even the verification variant.
- **CAP/PACELC** bound what end-to-end guarantee is *achievable* at all under partitions, independent of composition.

## 6. The Gap

There is a clean positive result (linearizability composes) and clean negative results (almost nothing else does, and checking is NP-hard), but **no general predictive calculus** sits between them: given an arbitrary heterogeneous stack we cannot yet *mechanically derive a tight* end-to-end label, only over-approximate or test. Gaps: (1) an algebra of "consistency × wiring" with proven soundness *and* completeness; (2) handling async/lagging propagation and caches as first-class composition operators; (3) tool support that scales to real microservice graphs. Genuinely open.

## 7. Current Research (as of June 2026)

- Extending the Cerone–Gotsman axiomatic lattice with **composition operators** and mechanized (Coq/Isabelle) soundness proofs *(frontier — verify)* (IMDEA Software / MPI-SWS lineage).
- **Consistency types / session-typed** APIs that track per-call guarantees through a service mesh and reject unsafe compositions at compile time *(frontier — verify)*.
- Observability-driven inference: learning the *effective* composite model of a deployed microservice graph from traces, extending Elle-style anomaly detection across services.
- Application of CISE-style invariant proofs to multi-store stacks rather than single stores.

## 8. Future Work

- A sound-and-complete compositional calculus with caches and async propagation as operators.
- Synthesis: derive minimal per-layer guarantees to meet an end-to-end target at least cost (links to cost-aware PACELC tuning).
- Scalable mechanized checkers for industrial service graphs.
- Bridging the axiomatic theory with operational/transactional models (mixed-consistency transactions across layers).

## 9. Key References

- **[Foundational]** Herlihy, M. P., Wing, J. M. *Linearizability: a correctness condition for concurrent objects.* ACM TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[Foundational]** Burckhardt, S. *Principles of Eventual Consistency.* Foundations and Trends in Programming Languages, 2014. — [DOI](https://doi.org/10.1561/2500000011)
- **[SOTA]** Cerone, A., Bernardi, G., Gotsman, A. *A framework for transactional consistency models with atomic visibility.* CONCUR, 2015. — [DOI](https://doi.org/10.4230/LIPIcs.CONCUR.2015.58)
- **[SOTA]** Gotsman, A., Yang, H., Ferreira, C., Najafzadeh, M., Shapiro, M. *'Cause I'm strong enough: reasoning about consistency choices in distributed systems (CISE).* POPL, 2016. — [DOI](https://doi.org/10.1145/2837614.2837625)
- **[Foundational]** Papadimitriou, C. H. *The serializability of concurrent database updates.* JACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[SOTA]** Kingsbury, K., Alvaro, P. *Elle: inferring isolation anomalies from experimental observations.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3430915.3430918)

## 10. Worked Example

A client writes its profile to the **primary store** (causal+, read-your-writes), then immediately issues a read that is routed through a **stateless edge cache** sitting in front of the store.

Trace:
1. `put(profile, v2)` → primary accepts, session now expects to see $v2$.
2. `get(profile)` → cache has a stale entry $v1$ (populated before the write) and returns it on a HIT.

Although the primary alone guarantees read-your-writes (RYW), the *composite* drops it: the cache's visibility relation $\mathsf{vis}_{cache}$ is a strict subset of the store's and does **not** contain the session's own write. Formally RYW requires $\text{so} \subseteq \mathsf{vis}$ (session order in visibility); the cache violates this because it never observed the `put`.

Per-layer labels: $\{\text{RYW}\} \times \{\text{none}\}$. Naive "meet of labels" reasoning would predict the weaker of the two (none), which happens to be right here — but the point is that the *wiring* (cache in front) is what forces the drop, not the cache's standalone label. Move the cache *behind* the write path (write-through) and RYW is restored: composition is wiring-sensitive, not just label-sensitive.

---
*Part of the [DBMS Research catalog](../../README.md).*
