---
id: 18-streaming-queries/deterministic-replay
title: "Deterministic replay for nondeterministic operators"
topic: 18-streaming-queries
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Deterministic replay for nondeterministic operators

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/deterministic-replay` · **Status:** partially-solved

## 1. Problem Statement

A continuous query is a long-running dataflow whose operators may produce outputs that depend on *more than* their input data: processing-time triggers (`ProcessingTimeTimer`), wall-clock-driven windows, random sampling/load shedding, hashing seeds, and external lookups (RPCs, UDFs that read mutable state). When a worker fails and recovers from a checkpoint or log, we must reproduce a stream of outputs *consistent* with what downstream consumers and external sinks already observed — otherwise exactly-once and even idempotent recovery break.

Formally: let an operator be a function $f$ over an input log $I$ plus a *nondeterminism oracle* $\omega$ (timer firings, RNG draws, RPC responses). Replay must reconstruct $\omega$ (or an equivalent $\omega'$ with $f(I,\omega') = f(I,\omega)$ on observed outputs).

Variants: **(a) Decision** — given a recovery point, does a consistent replay exist? **(b) Construction** — produce the minimal auxiliary log enabling deterministic replay. **(c) Optimization** — minimize logging overhead (bytes, latency) subject to bounded replay divergence $\epsilon$.

## 2. Mathematical Foundations

Model a dataflow as a DAG $G=(V,E)$ of operators over event-time/processing-time. Each operator's local execution is a transition system $(S, \Sigma \times \Omega, \delta)$ where $\Sigma$ is the data alphabet and $\Omega$ the nondeterministic events. **Deterministic replay** requires a recorded trace $\tau \subseteq \Omega^*$ s.t. re-executing $\delta$ on $(I,\tau)$ from checkpointed state $s_0$ yields the committed output prefix.

This is the database analogue of **deterministic replay in distributed systems** and rests on **logical/vector clocks** (Lamport 1978) for causal ordering and on the **rollback-recovery / piecewise-determinism (PWD) assumption** (Elnozahy et al. 2002): execution is a sequence of deterministic intervals delimited by recorded *nondeterministic events*. PWD is the key sufficient condition — if every source of nondeterminism is logged at interval boundaries, replay is exact.

Causal consistency of the replayed cut is captured by **consistent global snapshots** (Chandy–Lamport 1985). Where the oracle includes external reads, replay becomes a *commit-log determinization* problem, related to deterministic transaction execution (Calvin, Thomson et al. 2012): fixing an order a priori removes the oracle.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Apache Flink combines asynchronous barrier snapshotting (ABS, Carbone et al. 2015) with operator state checkpoints; nondeterministic operators are handled by *upstream record replay* plus optional **deterministic timer materialization**. Timely/Differential Dataflow (Murray et al., Naiad, SOSP 2013; McSherry et al.) gets determinism by construction for its progress-tracked operators.
- **Spark Structured Streaming** uses micro-batch lineage + idempotent sinks; nondeterminism is constrained by API (forbidding wall-clock UDFs in exactly-once paths).
- **Theory-SOTA:** PWD-based logging is provably sufficient; *deterministic database* execution (Calvin, Aria, Bohm) shows how to eliminate the oracle for transactional side-effects, at concurrency cost.

## 4. Upper Bound

Under the PWD assumption, **exact replay is achievable with logging proportional to the nondeterministic-event rate**, not the data rate: $O(|\Omega|)$ extra log volume, $O(1)$ amortized per event, with replay time $O(\text{work since last checkpoint})$. With *causal logging* (Alvisi–Marzullo 1998) the dependency metadata is $O(\text{antecedence per message})$, bounded by in-degree. For pure timer/RNG nondeterminism, recording seeds gives $O(1)$ per epoch.

## 5. Lower Bound

If external reads are part of the oracle and the external store is not itself replayable/versioned, **no logging scheme can guarantee exact replay**: an information-theoretic argument shows you must persist every distinct observed response, so log size is $\Omega(\\#\text{external interactions})$ — you cannot do better than recording the answers. More fundamentally, achieving a *consistent* recovered cut across operators that interact with an asynchronous, possibly-faulty external world inherits **FLP impossibility** (Fischer–Lynch–Paterson 1985): no fully asynchronous protocol guarantees agreement on the replay boundary with one faulty participant. CAP/PACELC tensions apply when the external store is partitioned.

## 6. The Gap

For *internal* nondeterminism (timers, RNG, hashing) the problem is essentially **closed**: PWD logging matches the information-theoretic lower bound. The genuinely **open** part is *external* side-effecting nondeterminism — bridging to the exactly-once-side-effects problem. The gap is between "log everything" (correct but heavy) and "log nothing, assume determinism" (cheap but unsound). What would close it: principled cost models that decide *which* nondeterminism to capture vs. tolerate divergence $\epsilon$, and protocols that make external stores replay-aware (versioned reads / read-your-writes tokens).

## 7. Current Research (as of June 2026)

- Flink community work on **deterministic operator timers and changelog state backends** to make replay reproducible without full upstream buffering *(frontier — verify)*.
- Research on **provenance-based selective replay** (replaying only the affected sub-DAG) building on Naiad-style progress tracking and lineage stashing (Apache Spark's RDD lineage heritage).
- Integration of **deterministic transaction kernels** (Calvin/Aria lineage; lines from Yale/Daniel Abadi, and from the Aria/Hyper groups) into streaming engines to determinize external writes.
- Verification-oriented efforts using **TLA+/Stateright** models of streaming recovery to prove replay equivalence *(frontier — verify)*.

## 8. Future Work

- A cost-based logger that minimizes overhead subject to an $\epsilon$-divergence SLA.
- Replay-aware external storage interfaces (standardized versioned-read tokens).
- Formal equivalence notions weaker than bit-identical output (observational / sink-equivalence) and protocols that target them.
- Handling *speculative* and approximate operators (load shedding) where exact replay is undesirable but bounded-deviation replay is.

## 9. Key References

- **[Foundational]** L. Lamport. *Time, Clocks, and the Ordering of Events in a Distributed System.* CACM, 1978. — [DOI](https://doi.org/10.1145/359545.359563)
- **[Foundational]** K. M. Chandy, L. Lamport. *Distributed Snapshots: Determining Global States of Distributed Systems.* ACM TOCS, 1985. — [DOI](https://doi.org/10.1145/214451.214456)
- **[Foundational]** E. N. Elnozahy, L. Alvisi, Y.-M. Wang, D. B. Johnson. *A Survey of Rollback-Recovery Protocols in Message-Passing Systems.* ACM Computing Surveys, 2002. — [DOI](https://doi.org/10.1145/568522.568525)
- **[Foundational]** M. Fischer, N. Lynch, M. Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[SOTA]** P. Carbone, S. Ewen, G. Fóra, S. Haridi, S. Richter, K. Tzoumas. *State Management in Apache Flink: Consistent Stateful Distributed Stream Processing.* PVLDB, 2017 (and ABS, 2015). — [DOI](https://doi.org/10.14778/3137765.3137777)
- **[SOTA]** A. Thomson, T. Diamond, S.-C. Weng, K. Ren, P. Shao, D. Abadi. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213838)

## 10. Worked Example

A single operator samples each input tuple with probability $0.5$ using a seeded RNG, then emits kept tuples to an external sink. Input log $I = [t_1, t_2, t_3, t_4]$. The nondeterminism oracle is the RNG draw sequence $\omega$.

**Original run.** Checkpoint $s_0$ taken before $t_1$, recording RNG seed $\sigma = 42$. Draws: $0.31, 0.88, 0.10, 0.67$. Keep if draw $< 0.5$, so kept $= \{t_1, t_3\}$ → emitted to sink, which now durably holds $\{t_1, t_3\}$.

**Crash** after $t_3$ committed. Recover from $s_0$.

- *No logging (assume determinism):* replay re-seeds from wall-clock, draws e.g. $0.62, 0.05, \dots$ → keeps $\{t_2\}$. Sink already has $t_1$; now we re-emit $t_2$ — a **divergent, duplicated** output. Exactly-once broken.
- *PWD logging:* we logged only the seed $\sigma=42$ (one boundary event), not the data. Replaying $\delta$ on $(I, \sigma{=}42)$ from $s_0$ regenerates draws $0.31, 0.88, 0.10$ → keeps exactly $\{t_1, t_3\}$, matching the committed prefix. Extra log volume $= O(1)$ per epoch, independent of the data rate.

**Cost accounting.** Internal RNG nondeterminism: $O(1)$ log (the seed) suffices — matches the information-theoretic optimum. Contrast an *external lookup* `f(t) = RPC(t)`: the responses are not regenerable, so by the §5 lower bound the log must store $\Omega(\\#\text{RPCs})$ distinct answers — here, one recorded response per tuple, i.e. log size grows with the data rate. This is exactly the open internal-vs-external gap.

---
*Part of the [DBMS Research catalog](../../README.md).*
