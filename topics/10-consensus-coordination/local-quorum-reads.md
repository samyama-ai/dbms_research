# Quorum Reads Without Round Trips

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/local-quorum-reads` · **Status:** partially-solved

## 1. Problem Statement
In a replicated state machine, a **linearizable read** normally costs a quorum round: the reader must confirm with $\lceil (n+1)/2\rceil$ replicas that it is not stale and that no newer write has committed. This adds a network round-trip to every read, dominating latency in read-heavy, geo-distributed workloads. The problem: serve **linearizable reads from a single replica** (ideally a local one) **without** a quorum round *and* without relying on **unbounded or unsafe clock/lease assumptions**. The tension is that the two known shortcuts — **leader leases** (read locally if you hold a time-bounded lease) and **read-index** (skip the data round but still ping a quorum once) — each reintroduce either a clock assumption or a round trip. The goal is reads that are local, linearizable, and safe under realistic (bounded but adversarially testable) timing.

Variants: decision ("is a local read linearizable given state $S$?"), optimization ("minimize read latency / quorum traffic for a target staleness=0 guarantee"), and the bounded-staleness relaxation ("serve within $\Delta$-staleness locally").

## 2. Mathematical Foundations
Linearizability requires every read to return a value at least as new as the latest *completed* write, consistent with a single total order. For a follower to read locally and safely it must know it has *all* committed writes up to the read point. Two mechanisms:

- **Leader lease**: leader holds a lease valid until clock-time $t_{\text{exp}}$ guaranteeing no other leader is elected before then; it may answer reads locally within $t_{\text{exp}} - \epsilon$ (margin $\epsilon \ge 2\rho L + \delta$ for drift $\rho$; see *Lease Safety Under Clock Drift*). Safety hinges on the clock bound.
- **Read-index** (Raft): leader records its current commit index $i^*$, confirms leadership via **one heartbeat round to a quorum**, then waits until its state machine has applied $i^*$ and answers — *no data round, but one coordination round, no clock assumption*.
- **Follower/local reads** need a *freshness certificate*: either a lease delegated from the leader, or a **closed timestamp / watermark** $\tau$ such that the follower has applied all writes with timestamp $\le \tau$, letting it answer reads as of $\tau$ (bounded-staleness, or linearizable if $\tau$ tracks real time within the clock bound).

Formally, a local linearizable read is safe iff $$\text{applied}_i \supseteq \text{committed}(\le \text{read-point}) \;\wedge\; \text{no-newer-leader}(\text{read-point}),$$ and the design choice is *how* to certify the second conjunct: a clock (lease) or a message (round).

## 3. State of the Art (SOTA)
Systems-SOTA: **Raft read-index / lease-read** (Ongaro–Ousterhout, ATC 2014) — lease-read is local but clock-dependent; read-index is one round, clock-free. **Spanner** (OSDI 2012) serves **snapshot reads** at a TrueTime-bounded timestamp from any replica with no quorum round, paying a small **safe-time** wait; **CockroachDB** uses **closed timestamps** + follower reads for the same effect with HLC. **PQR / Paxos Quorum Reads** (Charapko, Ailijiang, Demirbas, 2019) show that reading a *quorum* of followers' latest accepted values — without contacting the leader at all — can be linearizable, trading the leader round for a follower quorum round. Theory-SOTA: characterizations of which read protocols are linearizable under which timing/quorum assumptions are well developed; the precise frontier of *single-replica* linearizable reads without clocks remains the soft spot.

## 4. Upper Bound
Best achievable: **zero coordination rounds** for a local read under a *valid bounded-drift lease* (latency = local read + margin wait $\le \epsilon$); **one round** (read-index) with *no* clock assumption; **bounded-staleness** local reads with zero rounds via closed timestamps (linearizable only up to the watermark's real-time lag). PQR achieves leaderless linearizable reads in **one follower-quorum round**, off-loading the leader. Model: partially-synchronous crash, $f<n/2$, bounded-drift clocks where leases are used.

## 5. Lower Bound
Without *any* timing assumption, a linearizable read **cannot** be served from a single replica with zero coordination: the reader cannot rule out a concurrent newer write/leader without hearing from a quorum — an indistinguishability argument (a partitioned-but-running stale replica is locally indistinguishable from a fresh one). Hence **clock-free ⇒ at least one quorum-confirming round**; **zero-round ⇒ a clock/lease assumption**. This is a hard dichotomy, not an artifact. With clocks, the residual cost is the lease margin / safe-time wait, lower-bounded by clock uncertainty $\varepsilon$. Model: asynchronous (for the clock-free bound), bounded-drift (for the lease bound).

## 6. The Gap
The dichotomy is essentially proven, so in that sense the problem is **partially solved**: you can have *clock-free at one round* or *zero-round with a clock assumption*, and bounded-staleness in between. What stays open: (a) **shrinking the clock assumption's cost** — sub-microsecond time sync could make lease-reads safe with negligible margin, effectively giving "free" linearizable local reads, but the *adversarial* drift case (see lease problem) is unresolved; (b) whether a **probabilistically** local read (local most of the time, quorum-fallback on detected risk) can give a tight expected-latency optimum with a worst-case linearizability guarantee; (c) leaderless local reads that beat PQR's follower-quorum round. No protocol yet gives single-replica, clock-assumption-free, worst-case-linearizable reads — and the lower bound says that exact combination is impossible, so the real research is on the best *relaxation*.

## 7. Current Research (as of June 2026)
Active: **closed-timestamp / follower-read** improvements in CockroachDB and YugabyteDB shrinking staleness; **clock-uncertainty reduction** (cloud time appliances, PTP) making lease-reads near-free; PQR-style **leaderless read** refinements and quorum-read optimizations; bounded-staleness coordination primitives (links to *Bounded Staleness Coordination*). Groups: Demirbas (Buffalo/AWS), Spanner/Google time team, CockroachDB and Yugabyte engineering, Ports/Zhang lineage (UW). A 2025–2026 frontier explores **verifiable freshness tokens** letting an edge replica prove linearizability of a local read without a round, leveraging sub-µs sync *(frontier — verify)*.

## 8. Future Work
- Local linearizable reads with provably negligible margin under hardware time sync, including adversarial-drift safety.
- Probabilistic local-read protocols with worst-case linearizability and optimal expected latency.
- Tight lower bounds on leaderless local-read cost beating PQR.
- Unified cost model across lease, read-index, and closed-timestamp reads.

## 9. Key References
- **[Foundational]** Herlihy, M., Wing, J. *Linearizability: A Correctness Condition for Concurrent Objects.* ACM TOPLAS, 1990.
- **[Foundational]** Ongaro, D., Ousterhout, J. *In Search of an Understandable Consensus Algorithm (Raft).* USENIX ATC, 2014.
- **[SOTA]** Corbett, J., et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012.
- **[SOTA]** Charapko, A., Ailijiang, A., Demirbas, M. *Linearizable Quorum Reads in Paxos (PQR).* HotStorage, 2019.
- **[Foundational]** Attiya, H., Bar-Noy, A., Dolev, D. *Sharing Memory Robustly in Message-Passing Systems (ABD).* JACM, 1995.

---
*Part of the [DBMS Research catalog](../../README.md).*
