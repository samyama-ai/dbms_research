# End-to-end exactly-once with external side effects

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/exactly-once-side-effects` · **Status:** open

## 1. Problem Statement

Stream processors advertise "exactly-once" semantics, but the guarantee is really *exactly-once-effective state*: internal operator state is checkpointed and replayed so that the *observable result state* is as if each record were processed once. The hard, open case is when an operator performs a **non-idempotent external side effect** — a payment charge, an email, an inventory decrement, a third-party API call — outside the engine's transactional boundary. On failure-and-replay, such effects can be duplicated or lost.

The problem: guarantee that each logical input contributes its external side effect **exactly once**, end-to-end, across operator failures, checkpoint rollbacks, and partitioned/asynchronous external systems — or characterize precisely when this is impossible and what the best achievable semantics is.

Variants: **decision** (can a given sink + protocol guarantee exactly-once?), **construction** (build a protocol given sink capabilities), and **optimization** (minimize latency/throughput cost of the guarantee). Status *open*: in full generality it is provably unachievable; the open work is mapping the boundary and the best practical relaxations.

## 2. Mathematical Foundations

Model: dataflow with input log $I$, checkpoints giving snapshots $C_0, C_1, \dots$ (asynchronous barrier snapshotting, Carbone et al. 2015), and a sink with an external effect function $e: \Sigma \to \text{World}$. "Exactly once" means the multiset of effects equals $\{e(x) : x \in I\}$ exactly.

- **Idempotence** makes the problem trivial: if $e$ is idempotent (or carries a dedup key), at-least-once delivery suffices — this is the **idempotent-producer / dedup-key** reduction.
- **Transactional sinks** allow *atomic commit* coupling engine checkpoint with the external write via **two-phase commit (2PC)** (Gray 1978; Mohan et al. Presumed-Commit/Abort, 1986) — the **TwoPhaseCommitSinkFunction** pattern. Correctness rests on the **atomic commitment** problem.
- **Impossibility substrate:** atomic commitment among asynchronous processes with crash faults is subject to **FLP impossibility** (Fischer–Lynch–Paterson 1985) and the **two-generals / coordinated-attack impossibility** — no protocol guarantees agreement on commit over an unreliable channel. **CAP** (Gilbert–Lynch 2002 formalization of Brewer) forces a choice when the external store partitions.
- Without 2PC or idempotence, exactly-once degenerates to a *consensus on a shared commit token*, which an arbitrary external API does not provide.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Flink's **exactly-once sinks** via 2PC (`TwoPhaseCommitSinkFunction`) work for transactional targets (Kafka transactions, JDBC-XA, file commits). Kafka's **idempotent producer + transactions** give exactly-once *within Kafka*. Spark Structured Streaming relies on **idempotent sinks + offset-committed batches**. These cover idempotent or transactional sinks only.
- For *arbitrary* non-idempotent external calls, production guidance is: make them idempotent (dedup keys), or accept at-least-once + downstream dedup. No system provides true exactly-once for a generic non-transactional, non-idempotent API.
- **Theory-SOTA:** the reduction to atomic commitment is well understood; **Calvin/deterministic** databases sidestep nondeterministic replay but still cannot make a third-party charge atomic with the checkpoint.

## 4. Upper Bound

- **Idempotent sink:** exactly-once-effective achievable with at-least-once delivery + dedup key; $O(1)$ extra state per pending key, no extra round trips beyond the write.
- **Transactional/XA sink:** exactly-once via 2PC, costing one extra coordination round trip and a *blocking window* on coordinator failure; correctness holds in the **partially-synchronous** model with a recoverable coordinator (Paxos/Raft-backed coordinator removes the single-point blocking).
- These are the best achievable and both *require a capability from the sink* (dedup or transactions).

## 5. Lower Bound

- **Impossibility (general case):** for a sink that is neither idempotent nor transactional and is reached over an asynchronous, possibly-partitioned channel, **exactly-once is impossible** — directly from the **two-generals problem** and **FLP**: the engine and the external world cannot reach reliable agreement on whether the effect committed, so it must risk duplication or loss. **CAP** rules out availability + consistency under partition.
- **2PC blocking:** the atomic-commitment lower bound shows 2PC blocks on coordinator failure; non-blocking commitment (3PC) needs synchrony assumptions and still fails under partitions.

## 6. The Gap

The theoretical boundary is **closed in the negative**: with idempotence or transactions, exactly-once is attainable; without either, it is provably impossible. The **open** engineering/research gap is everything between: (i) systematically *characterizing* which real external systems can be retrofitted with dedup/transaction tokens; (ii) designing **standardized side-effect protocols** (effect-ledger, idempotency-key conventions) so generic APIs become exactly-once-capable; and (iii) defining and optimizing principled *relaxations* (effectively-once with bounded duplication probability, sagas/compensation). No accepted general framework or cost-optimal protocol family exists.

## 7. Current Research (as of June 2026)

- **Effect-ledger / idempotency-key standardization** (e.g., HTTP `Idempotency-Key` conventions, transactional outbox pattern) being generalized into engine-level abstractions *(frontier — verify)*.
- **Saga / compensation-based** exactly-once-effect for long-running workflows; integration of workflow engines (Temporal, Cadence) with streaming sinks for durable, dedup'd side effects.
- **Deterministic execution kernels** (Calvin/Aria lineage) combined with transactional outboxes to shrink the nondeterministic boundary (links to the deterministic-replay problem).
- Formal-methods work (TLA+/Stateright) verifying end-to-end exactly-once protocols and pinning down their synchrony assumptions *(frontier — verify)*.

## 8. Future Work

- A taxonomy + protocol library mapping sink capabilities to achievable semantics.
- Standard idempotency-token interface for external services to make generic exactly-once tractable.
- Quantified "effectively-once" guarantees (bounded duplication/loss probability) with cost models.
- Non-blocking, partition-tolerant commitment tailored to streaming checkpoints under partial synchrony.

## 9. Key References

- **[Foundational]** J. Gray. *Notes on Database Operating Systems.* In Operating Systems: An Advanced Course, Springer, 1978 (two-phase commit).
- **[Foundational]** M. Fischer, N. Lynch, M. Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985.
- **[Foundational]** S. Gilbert, N. Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (CAP).* ACM SIGACT News, 2002.
- **[SOTA]** P. Carbone, G. Fóra, S. Ewen, S. Haridi, K. Tzoumas. *Lightweight Asynchronous Snapshots for Distributed Dataflows (ABS).* arXiv:1506.08603, 2015.
- **[SOTA]** P. Carbone, A. Katsifodimos, S. Ewen, V. Markl, S. Haridi, K. Tzoumas. *Apache Flink: Stream and Batch Processing in a Single Engine.* IEEE Data Eng. Bulletin, 2015.
- **[Foundational]** C. Mohan, B. Lindsay, R. Obermarck. *Transaction Management in the R* Distributed Database Management System.* ACM TODS, 1986.

---
*Part of the [DBMS Research catalog](../../README.md).*
