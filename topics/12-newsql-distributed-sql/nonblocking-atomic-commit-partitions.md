# Atomic commit without blocking under partitions

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/nonblocking-atomic-commit-partitions` · **Status:** partially-solved

## 1. Problem Statement
A distributed transaction spanning multiple shards must reach **atomic commit**: all participants commit or all abort, with agreement preserved despite crashes and network partitions. Classic two-phase commit (2PC) is *blocking*: if the coordinator fails after the prepare phase, participants holding locks cannot unilaterally decide and stall indefinitely. The problem: design an **atomic commit protocol that is non-blocking** — every correct participant eventually decides — while tolerating network partitions and coordinator failure, ideally without a heavyweight extra phase.

Variants:
- **Decision:** Given fault model $f$ and a partition pattern, does a protocol exist that lets every non-faulty participant decide within bounded message delays once the network heals?
- **Liveness/optimization:** Minimize the latency and message overhead of non-blocking commit vs. blocking 2PC.
- **Safety constraint:** Never violate atomicity even under arbitrary partition timing.

It is "partially solved": three-phase commit (3PC) and Paxos/Raft-replicated coordinators remove the single-coordinator stall, but each carries cost (extra round trips, or quorum availability requirements) — and under true partitions the CAP tension forces a choice between availability and consistency.

## 2. Mathematical Foundations
Atomic commit is formalized by the **Atomic Commitment Problem (ACP)** specification (Bernstein, Hadzilacos, Goodman 1987): agreement, validity (commit only if all vote yes), non-triviality, and termination. Non-blocking ACP requires that a *failure detector* of class $\Diamond S$ (eventually strong; Chandra–Toueg 1996) or equivalently a consensus oracle be available, since **Non-Blocking Atomic Commit is reducible to and from consensus** (Guerraoui 1995; Charron-Bost–Schiper). Hence FLP impossibility applies: in a purely asynchronous model with even one crash, *no deterministic non-blocking commit protocol exists*. Partitions are modeled as periods where quorum intersection $|Q_1|+|Q_2|>n$ may fail to hold for a minority side.

Key relationship: $\text{NBAC} \equiv \text{Consensus}$ under crash faults given a perfect-ish failure detector; under partitions, CAP (Gilbert–Lynch 2002) forces a CP system to sacrifice availability for the minority partition.

## 3. State of the Art (SOTA)
- **Theory:** Skeen's three-phase commit (1981) is non-blocking under crash faults with a synchronous network but is *not* partition-tolerant. The reduction NBAC↔consensus (Guerraoui) is the canonical theoretical result.
- **Systems:** Modern NewSQL systems replicate the **transaction coordinator state via Paxos/Raft** so coordinator failure no longer blocks: Spanner (2PC over Paxos groups, OSDI 2012), CockroachDB (parallel commits + Raft), YugabyteDB. **Parallel Commits** (CockroachDB) makes the common path one round trip by recording a "transaction record" whose committed state is implied by the presence of all writes. Calvin (SIGMOD 2012) sidesteps 2PC by deterministic ordering, eliminating commit-time agreement entirely.

## 4. Upper Bound
Best-known: **non-blocking commit at the cost of replicating the coordinator** — 2PC where each role (coordinator and participants) is a Raft/Paxos group, giving termination as long as a majority within each group is reachable. Latency is one or two wide-area round trips (Parallel Commits achieves ~one RTT in the common case). Model: partially synchronous, crash faults, majority quorums. This is optimal up to constants for CP systems but inherently *unavailable to minority partitions*.

## 5. Lower Bound
- **FLP (1985):** no deterministic non-blocking commit in fully asynchronous systems with one crash — randomization or partial synchrony / failure detectors are necessary.
- **Consensus equivalence (Guerraoui 1995):** NBAC is at least as hard as consensus; the weakest failure detector for NBAC is known to be related to $\Diamond S$ plus an anti-$\Omega$ component.
- **CAP (Gilbert–Lynch 2002):** under a partition, a protocol cannot be both consistent and available; the minority side *must* block or abort. This is the fundamental obstacle to "non-blocking under partitions."

## 6. The Gap
The gap is conceptual rather than a numeric ratio: under crash faults with eventual synchrony, the problem is essentially **solved** (replicate the coordinator). Under genuine partitions, CAP proves you *cannot* have both safety and unconditional liveness, so "non-blocking under partition" is impossible in the strict sense — the residual research question is minimizing the blocking window (time-to-decision after partition heals), reducing the latency tax of replicated coordinators toward a single round trip, and characterizing which transactions can safely commit on the majority side without global agreement.

## 7. Current Research (as of June 2026)
- Reducing commit latency: Parallel Commits, *(frontier — verify)* one-RTT atomic commit via witness quorums extending CURP-style ideas to multi-shard transactions.
- Deterministic databases (Calvin/Aria/Detock lineage from Yale, Daniel Abadi's group) that avoid agreement at commit time, trading off interactivity.
- Leaderless/EPaxos-style commit to remove coordinator hotspots.
- *(frontier — verify)* formal weakest-failure-detector characterizations for partition-tolerant commit under partial synchrony.

## 8. Future Work
- Tightening the blocking-window bound after partition recovery.
- Hybrid protocols that maximize majority-side availability while bounding minority-side staleness.
- Byzantine-fault-tolerant non-blocking commit with practical latency.
- Formal verification of replicated-coordinator commit (TLA+/Ivy proofs at scale).

## 9. Key References
- **[Foundational]** P. Bernstein, V. Hadzilacos, N. Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987.
- **[Foundational]** D. Skeen. *Nonblocking Commit Protocols.* SIGMOD, 1981.
- **[Foundational]** R. Guerraoui. *Revisiting the Relationship Between Non-Blocking Atomic Commitment and Consensus.* WDAG/DISC, 1995.
- **[Foundational]** T. Chandra, S. Toueg. *Unreliable Failure Detectors for Reliable Distributed Systems.* JACM, 1996.
- **[Foundational]** S. Gilbert, N. Lynch. *Brewer's Conjecture and the Feasibility of CAP Services.* SIGACT News, 2002.
- **[SOTA]** A. Thomson et al. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012.
- **[SOTA]** J. Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
