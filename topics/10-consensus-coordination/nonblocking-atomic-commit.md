---
id: 10-consensus-coordination/nonblocking-atomic-commit
title: "Non-Blocking Atomic Commit at Scale"
topic: 10-consensus-coordination
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Non-Blocking Atomic Commit at Scale

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/nonblocking-atomic-commit` · **Status:** open

## 1. Problem Statement
Classical **Two-Phase Commit (2PC)** is *blocking*: if the coordinator crashes after participants vote `yes` but before learning the outcome, participants hold locks indefinitely. **Three-Phase Commit (3PC)** removes blocking under synchrony by adding a `pre-commit` round, but pays an extra message delay, assumes bounded message delivery, and is fragile under network partitions. The problem: design a commit protocol that is **non-blocking under realistic deployment failures** (coordinator crash, partition, slow links) while matching 2PC's latency and message cost in the common (failure-free) case — and to characterize whether the extra round/assumptions of 3PC are *fundamentally necessary* or an artifact.

Variants: decision (does a protocol with cost profile $X$ exist?), optimization (minimize common-case round-trips and tail-latency under a given fault model), and the practical question of *which assumptions* (clock sync, FD power, replication factor) buy non-blocking cheapest.

## 2. Mathematical Foundations
Setting: $p$ participants (shards) + a logical coordinator, asynchronous-with-failure-detectors or partially-synchronous network, crash (optionally crash-recovery) faults. Atomic commit must satisfy NBAC's four properties (Agreement, Validity, Abort-Validity, Termination). The cost vector is $\langle r, m, d\rangle$ = (message rounds, total messages, durable log writes) per commit.

Foundational fact: non-blocking commit in asynchrony requires consensus-equivalent power (see *Weakest Failure Detector for Commit*). The dominant modern construction replaces the fragile coordinator with a **replicated coordinator**: the decision is itself an entry agreed by Paxos/Raft over $2f+1$ replicas, so coordinator failure is masked rather than detected. Latency lower bound in the common case is then $$\text{commit latency} \;\ge\; 2\,\delta \;+\; \text{consensus}(\text{decision}),$$ where $\delta$ is one-way participant delay; the open question is shaving the additive consensus term toward zero.

## 3. State of the Art (SOTA)
Systems-SOTA: **Spanner** (OSDI 2012) and **CockroachDB** run 2PC where each participant *and* the transaction record are Paxos/Raft groups — non-blocking by replication, at the price of one consensus round on the commit path. **Parallel Commits** (CockroachDB) and **FoundationDB**'s resolver pipeline collapse the prepare and commit-decision durability into overlapping rounds, achieving (in the common case) commit at the latency of a single consensus + one participant RTT. **TAPIR** (SOSP 2015) and **Janus** (OSDI 2016) co-design consistency and commit to merge the consensus and 2PC rounds into a single round trip when there are no conflicts. Theory-SOTA: the $\{\Omega, ?P\}$ characterization bounds what is achievable; "Commit unanimity vs. coordinator masking" framings (Gray–Lamport, *Consensus on Transaction Commit*) unify 2PC+Paxos.

## 4. Upper Bound
With a Paxos-replicated coordinator, NBAC is achieved in the common case in **2 message delays** for prepare + the consensus latency for the decision (1–2 delays for fast/multi-Paxos), total ~3–4 one-way delays, $O(p \cdot f)$ messages. TAPIR/Janus achieve **one round trip** (single delay to a super-quorum) for non-conflicting transactions by folding ordering, consensus, and commit. Model: partial synchrony, crash faults, $f$-fault-tolerant replication per group.

## 5. Lower Bound
Any non-blocking commit must, on the decision, perform work equivalent to one consensus instance, inheriting consensus's lower bounds: $\ge 2$ message delays to a quorum for the decision in the worst case (Lamport), and $\ge f+1$ rounds under crash for full agreement in synchronous models. FLP forbids a non-blocking, deterministic, assumption-free solution. Partition impossibility (CAP) forces a choice: a partitioned minority cannot both make progress and stay safe. Model: asynchronous/partially-synchronous crash.

## 6. The Gap
The qualitative answer (replicate the coordinator) is known and deployed, so 3PC's *extra synchrony assumption* is provably avoidable. The **open** part is the *cost*: can commit be non-blocking at **2PC's exact common-case latency** (no additive consensus round) without conflict-freedom assumptions, across many shards and wide-area links? TAPIR/Janus get there only for conflict-free workloads; under contention they fall back to extra rounds. No protocol simultaneously achieves: 1-RTT common case, contention-robust, partition-graceful, and minimal durable writes. Whether that combination is impossible or merely undiscovered is genuinely open.

## 7. Current Research (as of June 2026)
Directions: (a) **deterministic databases** (Calvin/Aria lineage, Abadi & collaborators) that pre-order transactions to avoid the commit vote entirely; (b) leaderless/EPaxos-style commit merging ordering and atomicity; (c) RDMA- and CXL-accelerated commit paths cutting the durable-write term; (d) **detock**/deterministic geo-commit reducing cross-region rounds. Groups: Abadi (UMD), Aguilera/Microsoft Research, Zhang/Ports lineage (UW), CockroachDB/FoundationDB engineering teams. A 2025–2026 frontier explores commit on **disaggregated memory** where the durable-write semantics change entirely *(frontier — verify)*.

## 8. Future Work
- A tight lower bound separating contention-robust 1-RTT commit from conflict-free 1-RTT commit.
- Commit protocols that degrade gracefully across partitions while bounding minority staleness.
- Cost models in dollars/energy on cloud pricing, not just rounds.
- Formal machine-checked proofs of parallel-commit-style optimizations in production code.

## 9. Key References
- **[Foundational]** Gray, J., Lamport, L. *Consensus on Transaction Commit.* ACM TODS, 2006. — [DOI](https://doi.org/10.1145/1132863.1132867)
- **[Foundational]** Skeen, D. *Nonblocking Commit Protocols.* SIGMOD, 1981. — [DOI](https://doi.org/10.1145/582318.582339)
- **[SOTA]** Corbett, J., et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[SOTA]** Zhang, I., et al. *Building Consistent Transactions with Inconsistent Replication (TAPIR).* SOSP, 2015. — [DOI](https://doi.org/10.1145/2815400.2815404)
- **[SOTA]** Mu, S., Nelson, L., Lloyd, W., Li, J. *Consolidating Concurrency Control and Consensus for Commits under Conflicts (Janus).* OSDI, 2016. — [USENIX](https://www.usenix.org/conference/osdi16/technical-sessions/presentation/mu)
- **[Survey]** Bernstein, P., Hadzilacos, V., Goodman, N. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987. — [DBLP](https://dblp.org/rec/books/aw/BernsteinHG87.html)

## 10. Worked Example

A transaction $T$ touches two shards $S_1, S_2$; each shard is a Paxos group of $2f+1=3$ replicas, and the transaction record is a third Paxos group. Compare the blocking failure 2PC suffers with the replicated-coordinator fix.

**Classic 2PC trace:** coordinator $C$ sends `PREPARE` → both shards vote `YES` and durably log it → $C$ logs `COMMIT` and crashes *before* sending the decision. Now $S_1, S_2$ hold locks on their rows and cannot unilaterally decide (committing risks violating atomicity if the other aborted). They block until $C$ recovers — possibly forever.

**Paxos-replicated coordinator (Gray–Lamport):** the `COMMIT`/`ABORT` decision is itself a Paxos instance over $2f+1=3$ coordinator replicas. With $f=1$, the decision survives one coordinator crash: a surviving replica learns the committed log entry and informs the shards, so locks release. Common-case cost: $2\delta$ for prepare $+$ one consensus round for the decision $\approx 3\text{–}4$ one-way delays. Parallel Commits collapses these by treating the transaction record's durable write *as* the commit point, so in the failure-free case $T$ commits at the latency of a single consensus instance plus one participant RTT — matching 2PC while staying non-blocking.

---
*Part of the [DBMS Research catalog](../../README.md).*
