---
id: 09-replication-consistency/crdt-space-optimal-gc
title: "Space-optimal CRDTs with garbage collection"
topic: 09-replication-consistency
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Space-optimal CRDTs with garbage collection

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/crdt-space-optimal-gc` · **Status:** open

## 1. Problem Statement

Conflict-free Replicated Data Types (CRDTs) achieve strong eventual consistency without coordination, but most designs accumulate **metadata that never shrinks**: tombstones for deleted elements, version vectors per element, or causal histories. A removed element in an OR-Set, or a deleted character in a sequence CRDT (RGA, Logoot, Treedoc), leaves a tombstone so concurrent re-adds/inserts resolve deterministically. Over a long-lived workload this metadata can dwarf the live state.

The problem: **Design CRDTs whose per-element and per-replica metadata overhead is provably bounded, and whose tombstones/causal metadata can be safely garbage-collected (reclaimed) without coordination — or characterize exactly when coordination-free GC is impossible.**

- **Optimization variant:** minimize worst-case metadata bits as a function of live size $n$, operations $m$, and replicas $N$.
- **Decision variant:** given a CRDT spec and a candidate GC rule, decide whether GC ever causes divergence (a "resurrection" or ordering anomaly).
- **Impossibility variant:** prove that for a class of CRDTs, bounded metadata + coordination-free GC + strong eventual consistency cannot hold simultaneously.

## 2. Mathematical Foundations

State-based CRDTs form a **join-semilattice** $(S, \sqcup)$: states are partially ordered, merge is the least upper bound, and convergence follows from monotone, inflationary updates. GC corresponds to an *abstraction/quotient* map $\phi: S \to S'$ that must commute with merge: $\phi(x \sqcup y) = \phi(x) \sqcup \phi(y)$ to preserve convergence. The danger: removing a tombstone lowers the state in the lattice, breaking monotonicity, so a delayed concurrent operation can resurrect deleted data.

Safe GC requires **causal stability**: an event $e$ is stable once every replica has observed all events concurrent with $e$, after which metadata distinguishing $e$ from successors is redundant. Detecting stability needs a **stability frontier** (a stable vector timestamp), costing $\Theta(N)$ metadata to track exactly. Information-theoretically, an OR-Set under arbitrary concurrent add/remove must encode which of $2^{m}$ operation subsets are live, giving lower bounds tied to the active causal frontier rather than $n$ alone.

## 3. State of the Art (SOTA)

- **Theory SOTA:** Shapiro et al.'s lattice framework (INRIA RR-7506, 2011) establishes the semilattice convergence theorem; *δ-CRDTs* (Almeida, Baquero, Shapiro, 2018) ship join-irreducible deltas to cut shipping cost but not resident metadata. Causal-stability GC formalized in the *Pure Operation-Based CRDTs* line (Baquero, Almeida, Shoker).
- **Systems SOTA:** Riak DT, Automerge, and Yjs use tombstones with periodic compaction; Yjs/Y-CRDT achieves near-optimal sequence representation via run-length integration and conservative GC after document load. Redis Active-Active bounds tombstone lifetime via observed-remove with epoch-based reclamation.

## 4. Upper Bound

For counters and registers, metadata is $O(N)$ (one entry per replica), reclaimable to $O(1)$ live value once stable. For OR-Sets, the optimized OR-Set (Bieniusa et al.) reduces per-element version data to a single dot, giving $O(n + N)$ resident metadata with tombstone-free removal. Sequence CRDTs achieve $O(n \log n)$ identifier bits for $n$ live elements with logarithmic densification; Yjs-style block coalescing is $O(\text{\\#blocks})$. With a stability detector ($O(N)$), tombstones become reclaimable in amortized $O(1)$ per stabilized op.

## 5. Lower Bound

Information-theoretic: any add-wins set must, in the worst case, retain metadata proportional to the number of *concurrently contended* elements — concurrency cannot be compressed below the size of the unstable frontier. Coordination-free GC is provably impossible while events remain causally unstable (a removed-then-re-added element is indistinguishable from a never-removed one without retained metadata). No-coordination + bounded metadata + full concurrency support cannot all hold — a CAP-style tension applied to GC.

## 6. The Gap

Practical CRDTs are bounded *in the stable region* but unbounded during sustained concurrency on the same keys. There is no tight characterization of minimum metadata as a function of contention/concurrency degree, nor a clean dividing line between types admitting coordination-free bounded GC (counters, LWW) and those that do not (general OR-Set under adversarial concurrency). Closing the gap requires matching information-theoretic lower bounds to GC-enabled constructions parameterized by concurrency, not live size.

## 7. Current Research (as of June 2026)

Active work on *pure op-based* and *δ-state* CRDTs with explicit causal-stability GC (Baquero, Almeida, Shapiro), and on formally verified compaction in Automerge/Yjs *(frontier — verify)*. Mechanized GC correctness (no resurrection) via Isabelle/Coq proofs of the semilattice + stability argument is maturing *(frontier — verify)*. Interest in succinct sequence CRDTs with provable identifier-length bounds (Fugue; Collabs from CMU) is growing.

## 8. Future Work

- A tight metadata lower bound parameterized by concurrency/contention degree, not live size.
- Mechanically verified coordination-free GC rules with no resurrection, for arbitrary user CRDTs.
- Hybrid designs that escalate to bounded coordination only on contended keys to enable aggressive GC.

## 9. Key References

- **[Foundational]** M. Shapiro, N. Preguiça, C. Baquero, M. Zawirski. *Conflict-free Replicated Data Types.* SSS, 2011 (INRIA RR-7506/RR-7687). — [DOI](https://doi.org/10.1007/978-3-642-24550-3_29)
- **[Foundational]** A. Bieniusa, M. Zawirski, N. Preguiça, M. Shapiro, C. Baquero, et al. *An optimized conflict-free replicated set.* INRIA RR-8083, 2012. — [arXiv](https://arxiv.org/abs/1210.3368)
- **[SOTA]** P. Almeida, A. Shoker, C. Baquero. *Delta state replicated data types.* J. Parallel Distrib. Comput., 2018. — [DOI](https://doi.org/10.1016/j.jpdc.2017.08.003)
- **[SOTA]** C. Baquero, P. Almeida, A. Shoker. *Pure operation-based replicated data types.* arXiv:1710.04469, 2017. — [arXiv](https://arxiv.org/abs/1710.04469)
- **[Survey]** N. Preguiça. *Conflict-free Replicated Data Types: An Overview.* arXiv:1806.10254, 2018. — [arXiv](https://arxiv.org/abs/1806.10254)

## 10. Worked Example

Take an OR-Set replicated on $N=3$ replicas. Replica A adds element $x$ with unique dot $(A,1)$; the set is $\{x \mapsto \{(A,1)\}\}$. Later A removes $x$ by recording that $(A,1)$ is observed-removed. The naive design keeps the dot $(A,1)$ as a **tombstone** so a concurrent re-add at B (dot $(B,1)$) is not erased on merge.

Causal-stability GC: track each replica's version vector. Once **every** replica's vector dominates $(A,1)$ — say all reach $A:1$ — the event is *stable*: no future concurrent operation referencing $(A,1)$ can arrive. Only then is the tombstone safe to drop. If we GC'd earlier and a delayed add carrying $(A,1)$ arrived, $x$ would be **resurrected**.

Cost accounting: tracking the stability frontier costs $\Theta(N)=3$ entries. During quiescence (no concurrency) metadata collapses to the $O(n)$ live elements. The lower bound bites only under *sustained concurrency on the same key*: $k$ concurrently contended dots force $\Omega(k)$ retained metadata — concurrency, not live size $n$, is the floor.

---
*Part of the [DBMS Research catalog](../../README.md).*
