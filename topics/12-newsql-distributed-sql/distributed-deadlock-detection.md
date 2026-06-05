# Distributed deadlock detection at scale

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/distributed-deadlock-detection` · **Status:** partially-solved

## 1. Problem Statement

A lock-based distributed SQL engine with thousands of shards must detect deadlocks: cycles in the global **wait-for graph (WFG)** whose vertices are transactions and whose edges $T_i \to T_j$ mean $T_i$ waits on a lock held by $T_j$. Each shard sees only a local fragment; a deadlock cycle may span many shards. The challenge is detection that is (i) **low-overhead** (sub-linear messaging, not a global graph collection per check), (ii) **false-positive-free** (never aborts a transaction for a phantom deadlock caused by stale edges), and (iii) **scalable** to thousands of shards and high transaction churn.

**Decision variant:** does the global WFG currently contain a cycle? **Detection-and-resolution variant:** find a cycle and choose a victim minimizing aborted work. **Counting/optimization variant:** detect all cycles while minimizing message complexity and victim cost. A key subtlety: the WFG is a *moving target* — edges appear and vanish, so an algorithm must distinguish a *true* persistent cycle from a *transient* one (avoiding phantom deadlocks).

## 2. Mathematical Foundations

The WFG is a directed graph $G=(V,E)$ distributed across $p$ sites; site $s$ holds edges incident to transactions it coordinates. A deadlock is a cycle in the **stable** WFG — the snapshot consistent with a single global instant. The central difficulty is that no site has a consistent global snapshot, so detection must work on a possibly inconsistent union of local views. Chandy–Misra–Haas formalize edge-chasing via **probe messages** $(i, j, k)$ that propagate along wait-for edges; a deadlock exists iff a probe returns to its initiator. Phantom deadlocks arise precisely when the union of local snapshots is not a *consistent cut* (Chandy–Lamport). Correctness conditions: an algorithm is **safe** (no phantoms) iff every reported cycle exists in some consistent global state; **live** iff every persistent cycle is eventually reported. Lower bounds connect to distributed cycle detection and to the communication complexity of set-intersection across the cut.

## 3. State of the Art (SOTA)

- **Chandy–Misra–Haas edge-chasing** (TODS 1983): the canonical probe-based AND-model detector; $O(\text{edges in cycle})$ messages, phantom-free for the AND model.
- **Path-pushing & global-graph construction**: Obermarck's algorithm (used in System R*) — periodic transmission of WFG paths; simple but heavier.
- **Practical NewSQL stance:** most modern systems (CockroachDB, Spanner, TiDB, YugabyteDB) **avoid global detection** via *deadlock prevention* — Wound-Wait / Wait-Die timestamp ordering, or timeout-based abort — trading some unnecessary aborts for $O(1)$ local decisions.
- **Deterministic systems (Calvin/SLOG)** sidestep deadlock entirely by pre-declaring lock order, eliminating the WFG.

## 4. Upper Bound

Edge-chasing (Chandy–Misra–Haas) detects an AND-model deadlock with message complexity $O(m)$ where $m$ is the number of edges in the deadlock cycle, and detection latency $O(\ell)$ for cycle length $\ell$ — independent of total shard count, which is what makes it scale to thousands of shards. Timeout-based prevention gives $O(1)$ per-transaction overhead. Wound-Wait/Wait-Die guarantee no deadlock with zero detection messages, at the cost of some spurious aborts (no false negatives, but "false positives" in the sense of unnecessary restarts).

## 5. Lower Bound

Detecting a cycle that spans the cut between two sites requires communication: deciding whether the union graph has a cycle reduces to a set-disjointness-style problem across the partition, giving an $\Omega(\cdot)$ communication lower bound in the number of cross-shard edges that must be exchanged in the worst case. Phantom-freedom imposes a fundamental tension with latency: by an indistinguishability argument, a detector that never collects a consistent cut can report a cycle that has already dissolved, so guaranteed phantom-freedom requires either snapshot synchronization (Chandy–Lamport-style, extra rounds) or stable-edge confirmation, which costs latency proportional to cycle diameter.

## 6. The Gap

Prevention (Wound-Wait/timeouts) is *cheap but lossy* — it aborts transactions that were not actually deadlocked; true detection is *precise but communication-bound*. The open part (hence *partially-solved*) is whether one can get **both** near-zero false aborts **and** sub-cycle-diameter latency at thousand-shard scale. Edge-chasing is optimal in messages for a *known stable* WFG, but real systems pay extra to establish stability, and no algorithm tightly matches the communication lower bound while remaining phantom-free under high churn. Closing the gap needs detectors with provable abort-rate/latency tradeoffs.

## 7. Current Research (as of June 2026)

Directions: hybrid prevention+detection (timeout as a fast path, edge-chasing as confirmation to suppress phantom aborts); contention-aware scheduling to keep WFGs shallow; and deterministic execution (Abadi's Calvin/SLOG, Aria) to remove the problem. There is renewed work on **lock-free / optimistic** distributed concurrency (e.g. Sundial's logical leases) measuring real-world deadlock-cycle distributions to argue detection is rarely needed *(frontier — verify)*. Cockroach Labs and PingCAP report production deadlock-handling telemetry *(frontier — verify)*.

## 8. Future Work

- A detector matching the cross-cut communication lower bound while phantom-free under churn.
- Provable bounds on unnecessary aborts for Wound-Wait under skewed contention.
- ML-driven victim selection minimizing aborted work / cascading restarts.
- Unified theory linking deterministic-DB lock pre-ordering to detection cost.

## 9. Key References

- **[Foundational]** Chandy, Misra, Haas. *Distributed Deadlock Detection.* ACM TODS, 1983.
- **[Foundational]** Chandy, Lamport. *Distributed Snapshots: Determining Global States.* ACM TOCS, 1985.
- **[Foundational]** Obermarck. *Distributed Deadlock Detection Algorithm.* ACM TODS, 1982.
- **[SOTA]** Thomson, Abadi, et al. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012.
- **[SOTA]** Yu, Xia, et al. *Sundial: Harmonizing Concurrency Control and Caching.* VLDB, 2018.
- **[Survey]** Knapp. *Deadlock Detection in Distributed Databases.* ACM Computing Surveys, 1987.

---
*Part of the [DBMS Research catalog](../../README.md).*
