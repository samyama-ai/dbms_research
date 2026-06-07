---
id: 12-newsql-distributed-sql/follower-read-staleness
title: "Bounding staleness in follower reads"
topic: 12-newsql-distributed-sql
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Bounding staleness in follower reads

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/follower-read-staleness` · **Status:** partially-solved

## 1. Problem Statement

In a leader-based replicated SQL store (Raft/Paxos per shard), serving reads only from the leader concentrates load and adds WAN latency. **Follower reads** let a non-leader replica answer, trading freshness for latency and throughput. The problem is to serve a read at a replica while giving a **tight, provable bound on staleness** — the gap between the snapshot served and the latest committed state — and to do so in a *workload-aware* way so the bound is as small as the replica's actual lag permits, not a conservative constant.

**Decision variant:** given a desired consistency level (linearizable, bounded-staleness-$\Delta$, or session/causal), decide whether replica $r$ can safely serve read $R$ at timestamp $\tau$ now, or must wait/redirect. **Optimization variant:** maximize the fraction of reads served locally subject to a staleness SLO $\Delta$ and a violation budget $\delta$. **Bounding variant:** compute the tightest $\Delta(r,t)$ such that any read at $r$ reflects all writes with timestamp $\le t-\Delta$.

## 2. Mathematical Foundations

Each shard has a replicated log; replica $r$ has applied a prefix up to **closed timestamp** $\mathit{ct}_r(t)$: a timestamp below which no new writes will be assigned, so reads at $\mathit{ct}_r$ are stable and need no leader round-trip. Safety: serving a read at $\tau \le \mathit{ct}_r(t)$ returns a consistent snapshot; staleness $= \mathit{now} - \mathit{ct}_r$.

Formally, let $L_r(t) = t - \mathit{ct}_r(t)$ be lag. The bounded-staleness guarantee is $L_r(t) \le \Delta$ w.p. $\ge 1-\delta$. Linearizable follower reads additionally require a **read lease** or a confirmation that the leader has not advanced beyond a known point, reducible to the standard result that a quorum-disjointness or lease argument is necessary (you cannot serve linearizable reads from a stale follower without either communication or a time lease — a consequence of the impossibility of detecting leader change locally). Causal/session consistency reduces to vector-clock / read-your-writes token comparison: serve iff $\mathit{ct}_r \ge$ the client's high-water mark. The closed-timestamp mechanism couples to the heterogeneous-clock problem because $\mathit{ct}$ advancement uses physical time plus uncertainty $\varepsilon$.

## 3. State of the Art (SOTA)

- **Spanner bounded-staleness & exact-staleness reads** (OSDI 2012): read at $\mathit{now}-\Delta$ from any replica caught up to that timestamp; the canonical design.
- **CockroachDB follower reads / closed timestamps** and **TiDB Follower/Stale Read**: production closed-timestamp propagation with configurable staleness.
- **Leases for linearizable local reads**: Raft read-leases (Ongaro–Ousterhout) and **PQR/Leader Leases**; **Quorum leases** (Moraru et al.) let a subset serve linearizable reads.
- **YugabyteDB** follower reads with bounded staleness; **Aurora** read replicas with replica-lag exposure.

## 4. Upper Bound

For bounded-staleness reads, the achievable staleness equals the closed-timestamp propagation delay: $\Delta = $ (heartbeat interval) $+$ (one-way replication latency) $+ \varepsilon$. Closed-timestamp protocols achieve $O(1)$ extra messages amortized (piggybacked on existing log/heartbeat traffic) and **zero** leader round-trips per read. For linearizable follower reads, a time-based lease gives $O(1)$ local reads valid for the lease duration, with cost amortized over the lease. Workload-aware tightening (adapting heartbeat rate to write skew) lowers $\Delta$ toward the true lag.

## 5. Lower Bound

Linearizable reads from a non-leader fundamentally require either (a) communication with a quorum/leader at read time, or (b) a real-time lease — there is no purely local, communication-free linearizable follower read, by a partition/indistinguishability argument (a follower cannot locally distinguish "I am current" from "leadership moved and I am stale"). This is a CAP-flavored impossibility. For bounded staleness, the served snapshot cannot be fresher than the last closed timestamp the replica has heard about, so $\Delta \ge$ one-way information-propagation delay — an information-theoretic floor tied to message latency and clock uncertainty $\varepsilon$.

## 6. The Gap

Bounded-staleness follower reads are essentially **solved up to the propagation-delay floor** — upper and lower bounds match within the heartbeat granularity. The open frontier (hence *partially-solved*) is: (1) making linearizable local reads cheap under churn without lease-revocation stalls; (2) *tight workload-aware* bounds that track per-key, not per-shard, lag (hot keys lag differently); and (3) jointly optimizing routing + staleness across many shards under an end-to-end SLO, which is a global optimization not captured by per-shard closed timestamps.

## 7. Current Research (as of June 2026)

Active directions: per-key / per-range closed timestamps and learned lag predictors to push $\Delta$ down adaptively; integration with global-snapshot reads for HTAP. Cockroach Labs, PingCAP (TiDB), and Yugabyte publish engineering reports on closed-timestamp tuning *(frontier — verify)*. Academic interest in **mixed-consistency** query planners that pick the weakest sufficient consistency per query, and in formally verified lease protocols. Quorum-lease revival for read-heavy geo workloads is being revisited *(frontier — verify)*.

## 8. Future Work

- Provably tight per-key staleness estimators under adversarial write skew.
- Lease protocols robust to clock faults (links to heterogeneous-clock commit).
- Global multi-shard read routing as an online optimization with regret bounds.
- Cost models exposing the staleness/latency/throughput Pareto frontier to the optimizer.

## 9. Key References

- **[Foundational]** Corbett, Dean, et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[Foundational]** Ongaro, Ousterhout. *In Search of an Understandable Consensus Algorithm (Raft).* USENIX ATC, 2014. — [USENIX](https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro)
- **[SOTA]** Moraru, Andersen, Kaminsky. *Paxos Quorum Leases: Fast Reads Without Sacrificing Writes.* SoCC, 2014. — [DOI](https://doi.org/10.1145/2670979.2671001)
- **[SOTA]** Taft, et al. *CockroachDB: The Resilient Geo-Distributed SQL Database.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3386134)
- **[SOTA]** Huang, et al. *TiDB: A Raft-based HTAP Database.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3415478.3415535)
- **[Survey]** Bailis, et al. *Probabilistically Bounded Staleness for Practical Partial Quorums.* VLDB, 2012. — [arXiv](https://arxiv.org/abs/1204.6082)

## 10. Worked Example

Consider one shard with leader $\ell$ and follower $r$. The leader publishes a **closed timestamp** every heartbeat interval $h = 3\text{ s}$; one-way replication latency is $d = 50\text{ ms}$ and clock uncertainty $\varepsilon = 5\text{ ms}$. At wall-clock $t = 100.000\text{ s}$, the most recent closed timestamp $r$ has received is $\mathit{ct}_r = 96.945\text{ s}$ (it heard the $t{=}97.000$ heartbeat $d$ late, minus $\varepsilon$).

- **Lag:** $L_r = t - \mathit{ct}_r = 100.000 - 96.945 = 3.055\text{ s} \approx h + d + \varepsilon$.
- **Bounded-staleness read** at $\tau = 96.9\text{ s}$: since $\tau \le \mathit{ct}_r$, $r$ serves locally with **zero leader round-trips**, staleness $\le 3.055\text{ s}$.
- **Read at $\tau = 99.0\text{ s}$:** $\tau > \mathit{ct}_r$, so $r$ must **wait** for the next closed timestamp or **redirect** to $\ell$.

Tightening $h$ to $200\text{ ms}$ drops the bound to $\approx 255\text{ ms}$, approaching the $d+\varepsilon = 55\text{ ms}$ propagation floor (Section 5).

---
*Part of the [DBMS Research catalog](../../README.md).*
