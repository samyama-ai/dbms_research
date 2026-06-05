# Optimal latency for distributed strict serializability

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/latency-lower-bound-strict-serializability` · **Status:** open

## 1. Problem Statement
Consider a transactional key-value store replicated across $n$ data centers (regions) with one-way message delays drawn from a known matrix $d_{ij}$, supporting strict serializability (linearizable transactions: the serialization order respects real-time happens-before across non-overlapping transactions). The question is the **tight lower bound on commit latency**: for a transaction touching keys whose replicas span a set $S$ of regions, what is the minimum wall-clock time, as a function of the round-trip topology and the failure model $f$ (number of crash faults tolerated), before the system may safely acknowledge commit?

Variants:
- **Decision:** Given a latency budget $L$, does a strictly serializable protocol exist meeting $L$ for every transaction under $f$ faults?
- **Optimization:** Minimize worst-case (or expected) commit latency over schedules and replica placements.
- **Lower-bound (the open core):** Prove a *topology-and-fault-parameterized* tight bound, matching it with a protocol. Read-only and read-write transactions, and local vs. cross-region transactions, are distinguished.

The problem is open because existing bounds (one or two wide-area round trips) are not known to be simultaneously tight across all combinations of consistency level, fault tolerance, and read/write mix.

## 2. Mathematical Foundations
Model: asynchronous (or partially synchronous) message-passing with $n$ nodes, up to $f$ crash faults, quorum systems with intersection property $|Q_1|+|Q_2|>n$. Consistency is formalized via histories and the strict-serializability correctness condition (Papadimitriou 1979; Herlihy–Wing linearizability 1990).

Latency is measured in **message delays** along a path; a write quorum of size $\lceil (n+1)/2\rceil$ requires at least one round trip to its furthest member, $\max_{j\in Q} 2 d_{ij}$. Lower bounds combine:
- **Quorum intersection** forcing communication to a majority,
- **Indistinguishability/partition arguments** (à la FLP, Fischer–Lynch–Paterson 1985) showing a single round cannot both linearize and tolerate $f$ faults for read-write transactions,
- **Real-time constraints**: for transactions $T_1 \prec T_2$ (real-time before), the serialization must agree, forcing a "store-then-confirm" or clock-based ordering step.

A useful formalism: define $\text{WPR}(S)$ (wide-path round trips) as the minimum number of cross-region message round trips on the critical path. Conjectured form: $L^* = \Theta(\text{WPR}\cdot \min_{i}\max_{j\in Q} d_{ij})$, with $\text{WPR}=1$ for some read-only optimizations and $\text{WPR}=2$ for general read-write commit under $f\ge1$.

## 3. State of the Art (SOTA)
- **Systems:** Spanner (Corbett et al., OSDI 2012) commits with Paxos + 2PC, roughly two wide-area round trips. CockroachDB and YugabyteDB inherit this. Calvin (Thomson et al., SIGMOD 2012) front-loads ordering. Spanner read-only transactions use TrueTime to avoid a round trip.
- **Latency-optimal theory:** Tango/MDCC/EPaxos (Moraru et al., SOSP 2013) achieve one round trip in the conflict-free case. CURP (Lee et al., NSDI 2019) commits in one RTT by exploiting witnesses. Tempo/Accord (Cassandra) and Detock target one-RTT geo-commit.
- **Lower-bound theory:** Lower bounds on the cost of linearizable/strictly-serializable operations derive from shared-memory and consensus lower bounds (Attiya–Welch 1994 on linearizable register latency; consensus needs $f+1$ rounds in the worst case).

## 4. Upper Bound
Best-known: **two wide-area round trips** for general strictly serializable read-write transactions (Paxos commit + 2PC, or one-round-trip variants like CURP/EPaxos in the contention-free case yielding **one RTT**). For read-only transactions with synchronized clocks (TrueTime), Spanner achieves **zero extra coordination round trips** (a local read at the leader after a bounded wait). Model: partially synchronous, crash faults, majority quorums; competitive vs. the conjectured optimum within a factor of 2.

## 5. Lower Bound
Attiya–Welch (1994) prove a delay-based lower bound: linearizable reads or writes on a shared register incur latency $\ge u/4$ (where $u$ is uncertainty in message delay) — establishing that one cannot make both reads and writes fast under linearizability. Consensus/atomic-commit lower bounds (FLP impossibility; Lamport's lower bounds for Byzantine and crash consensus) force $\ge 2$ message delays for fault-tolerant commit when $f\ge1$. CAP (Gilbert–Lynch 2002) rules out availability under partition for strict consistency. These are *condition-specific* and do not yet form a single tight topology-parameterized bound.

## 6. The Gap
Upper bound is one-to-two wide-area RTTs; lower bounds prove $\ge1$ RTT generically and $\ge2$ in some adversarial schedules — but no proof shows two RTTs are *necessary* for all read-write commits under realistic fault models, nor that one RTT suffices universally. The gap is whether the "second round trip" of 2PC/Paxos-commit is fundamental or an artifact. Closing it requires either a one-RTT strictly-serializable read-write protocol tolerating $f\ge1$ (would collapse the gap downward) or an indistinguishability proof that two RTTs are unavoidable in geo-distributed settings (closing it upward).

## 7. Current Research (as of June 2026)
- One-RTT geo-replicated transaction commit via witness/fast-path quorums: Detock, Janus successors, and *(frontier — verify)* refinements of Accord (Apache Cassandra) targeting single-RTT strict serializability.
- Latency-optimal SMR lower bounds (work building on EPaxos/Tempo, e.g., from groups at MPI-SWS, MIT, CMU).
- Clock-assisted commit (closely tied to the TrueTime-free problem) to remove the ordering round trip.
- *(frontier — verify)* formal lower-bound frameworks parameterizing latency by topology and fault budget, an active direction in the distributed-computing theory community (PODC/DISC).

## 8. Future Work
- A topology- and fault-parameterized tight bound $L^*(d_{ij}, f, \text{read/write mix})$ with matching protocol.
- Separating read-only vs. read-write optimal latency rigorously.
- Incorporating Byzantine faults and reconfiguration into the latency calculus.
- Energy/latency trade-offs and tail-latency (not just worst-case) lower bounds.

## 9. Key References
- **[Foundational]** M. Fischer, N. Lynch, M. Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985.
- **[Foundational]** H. Attiya, J. Welch. *Sequential Consistency versus Linearizability.* ACM TOCS, 1994.
- **[Foundational]** S. Gilbert, N. Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* ACM SIGACT News, 2002.
- **[SOTA]** J. Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012.
- **[SOTA]** I. Moraru, D. Andersen, M. Kaminsky. *There Is More Consensus in Egalitarian Parliaments (EPaxos).* SOSP, 2013.
- **[SOTA]** S. Lee et al. *Exploiting Commutativity For Practical Fast Replication (CURP).* NSDI, 2019.
- **[Foundational]** C. Papadimitriou. *The Serializability of Concurrent Database Updates.* JACM, 1979.

---
*Part of the [DBMS Research catalog](../../README.md).*
