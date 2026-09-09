---
id: 12-newsql-distributed-sql/live-resharding-transactional
title: "Dynamic resharding of live transactional data"
topic: 12-newsql-distributed-sql
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Dynamic resharding of live transactional data

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/live-resharding-transactional` · **Status:** partially-solved

## 1. Problem Statement

A distributed SQL system partitions a keyspace $K$ across shards. As load and data skew
change, the partitioning must be revised — splitting hot ranges, merging cold ones,
migrating ranges between nodes, or changing the partition function entirely. The problem:
perform this **online repartitioning with zero downtime**, **no lost or duplicated data**,
and **preserved isolation** (in-flight and new transactions still observe the system's
claimed consistency level — e.g., strict serializability — across the cutover).

Variants: (i) **Mechanism (decision/safety)** — design a protocol that moves ownership of a
key range from a source to a target while concurrent transactions read/write that range,
guaranteeing atomic, isolation-preserving handover. (ii) **Optimization** — choose *which*
ranges to move and *when* to minimize migration cost, latency disruption, and time-to-
balance, subject to capacity. (iii) **Continuous/online** — track a drifting workload with
bounded reconfiguration churn (stability vs. responsiveness).

## 2. Mathematical Foundations

Model the keyspace as ranges owned by replication groups (e.g., Raft/Paxos groups). A
**split** partitions a range $r = [a,c)$ into $[a,b)$ and $[b,c)$; a **merge** is the
inverse; a **transfer/rebalance** moves a replica/leaseholder to a new node. Correctness is
stated against the **multi-version serialization graph**: the reconfiguration must be a
**linearizable reconfiguration** — there is a single logical instant (a *split/move
timestamp* $t_s$) such that transactions with commit timestamp $< t_s$ see the old
ownership and those $\ge t_s$ see the new, with no transaction straddling inconsistently.
This connects to **atomic configuration change** in consensus (joint consensus / single-
server reconfiguration, Ongaro–Ousterhout) and to **two-phase / handover** protocols for
the data plane.

The placement-selection layer is a **load-balancing / bin-packing with migration cost**
problem: minimize $\sum$(imbalance) + $\beta \cdot$(bytes moved), an online problem analyzed
via **metrical task systems** and competitive analysis; choosing split points to equalize
load is a one-dimensional partitioning / quantile-estimation problem over a key-access
distribution.

## 3. State of the Art (SOTA)

**Systems SOTA.** Google **Spanner** performs directory-level movement and dynamic
resplitting of Paxos groups; **CockroachDB** continuously splits/merges ranges and rebalances
leaseholders via a Raft-based snapshot+log catch-up handover; **YugabyteDB** and **TiDB/PD**
(Placement Driver) implement automatic region/tablet splitting and rebalancing with a
control loop. **Vitess** (YouTube/PlanetScale) does online resharding of MySQL with
**VReplication**: copy + tail binlog + cutover, with filtered replication and a write-
switch. Slicer (Adya et al., OSDI 2016) is Google's general sharding service that moves
shards based on load while preserving assignment consistency.

**Theory SOTA.** Atomic reconfiguration of replicated state machines (Raft joint consensus;
Vertical Paxos, Lamport–Malkhi–Zhou) gives the consensus-level safety substrate; consistent
hashing with bounded loads (Mirrokni et al.) and online rebalancing competitive analysis
inform which moves to make.

## 4. Upper Bound

The **mechanism** has efficient upper bounds: a range split/merge or leaseholder transfer
costs $O(\text{range size})$ data movement plus $O(1)$ consensus rounds for the atomic
ownership flip, with a brief (sub-millisecond to low-millisecond) leaseholder-handover
window rather than full downtime; CockroachDB/Spanner achieve this in production. Vitess-
style copy+tail+cutover bounds cutover disruption to a short write-stall. For **placement**,
online rebalancing admits competitive algorithms for migration-cost-aware load balancing
(constant-competitive in restricted models), and consistent-hashing-with-bounded-loads
caps per-move imbalance with $O(1)$ overhead. These are the operational upper bounds.

## 5. Lower Bound

Lower bounds are partly impossibility/consensus-theoretic: any atomic ownership change that
must remain consistent under failures inherits **FLP** (no non-blocking consensus in pure
asynchrony) and requires at least a consensus round, so a truly **zero-stall, zero-extra-
round** cutover is unattainable under adversarial asynchrony — some handover latency is
fundamental. The **placement-optimization** variant is **NP-hard** (it generalizes
bin-packing / balanced partitioning with migration cost), and online versions have
nontrivial competitive lower bounds (any algorithm pays $\Omega(1)$-competitive migration
cost against an offline optimum in metrical-task-system models). Tail-latency-preserving
guarantees during migration intersect the speed-of-light/quorum bounds of consistent reads.

## 6. The Gap

Marked **partially-solved**: robust, production-grade *mechanisms* exist and largely meet
the zero-downtime + isolation-preservation goals for range-based systems. The open gaps:
(1) **provably isolation-preserving** resharding under *arbitrary* repartitioning (changing
the partition *function*, not just splitting ranges), with a machine-checked proof that no
straddling transaction breaks strict serializability; (2) the **optimization** layer —
near-optimal, low-churn online repartitioning with competitive guarantees that also bound
*tail-latency* disruption, not just average cost; (3) resharding that preserves
**cross-shard secondary indexes** and foreign-key constraints atomically with the data
move; (4) handling **hot single keys** that cannot be split. These are genuinely open.

## 7. Current Research (as of June 2026)

Active directions: formal verification of reconfiguration/handover protocols (TLA+/Ivy
proofs for Raft-based split-merge) *(frontier — verify)*; learned/adaptive split-point and
rebalancing controllers reacting to predicted hotspots *(frontier — verify)*; and
resharding that co-moves global secondary indexes consistently. Industrial work continues at
CockroachLabs, Yugabyte, PingCAP (TiDB/PD), PlanetScale (Vitess), and Google (Spanner/
Slicer lineage). Disaggregated-storage architectures (e.g., Aurora/Neon-style separation)
change the cost model by making "resharding" partly a metadata operation
*(frontier — verify)*.

## 8. Future Work

- Machine-checked isolation-preservation proofs for general (function-changing) resharding.
- Competitive online repartitioning that bounds tail-latency disruption, not just bytes
  moved.
- Atomic co-resharding of data plus global secondary indexes and referential constraints.
- Strategies for unsplittable hot keys (e.g., replication/escrow) integrated with the
  resharding control loop.

## 9. Key References

- **[Foundational]** Ongaro, Ousterhout. *In Search of an Understandable Consensus Algorithm (Raft).* USENIX ATC, 2014. — [USENIX](https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro)
- **[Foundational]** Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[SOTA]** Adya, Myers, Howell, Elson, Meek, Khemani, Fulger, Gu, Bhuvanagiri, Hunter, Peon, Kai, Shraer, Merchant, Lev-Ari. *Slicer: Auto-Sharding for Datacenter Applications.* OSDI, 2016. — [USENIX](https://www.usenix.org/conference/osdi16/technical-sessions/presentation/adya)
- **[Docs]** The Vitess Project. *VReplication and Online Resharding.* (PlanetScale/CNCF documentation), 2019–. — [Vitess docs](https://vitess.io/docs/user-guides/configuration-advanced/resharding/)
- **[Foundational]** Mirrokni, Thorup, Zadimoghaddam. *Consistent Hashing with Bounded Loads.* SODA, 2018. — [arXiv](https://arxiv.org/abs/1608.01350)
- **[Foundational]** Lamport, Malkhi, Zhou. *Vertical Paxos and Primary-Backup Replication.* PODC, 2009. — [DOI](https://doi.org/10.1145/1582716.1582783)

## 10. Worked Example

A range $r=[1,100)$ owned by a Raft group on node $A$ holds keys with a hot subrange. The
control loop decides to **split** at $b=40$, sending $[40,100)$ to node $B$. Pick a split
timestamp $t_s = 1000$ (a logical/HLC instant).

Trace of a concurrent txn $T$ that reads key $55$:
1. $T$ gets commit timestamp $\tau$.
2. If $\tau < t_s = 1000$: $T$ is routed to the **old** owner $A$ (still authoritative).
3. If $\tau \ge 1000$: $T$ is routed to the **new** owner $B$.

The atomic flip costs $O(1)$ consensus rounds plus $O(|[40,100)|)$ bytes of snapshot
transfer; the leaseholder-handover stall is sub-millisecond, not full downtime (Section 4).

**Why straddling breaks SS.** Suppose $T_1$ (ts $=999$) writes key $55$ on $A$ and $T_2$
(ts $=1001$) reads key $55$ on $B$. If the split copied $A$'s state at the instant
$t_s' = 998 \neq t_s$, $B$ misses $T_1$'s write and $T_2$ reads a stale value — a real-time
ordering violation. Correctness demands a **single** logical instant $t_s$ for copy-cutoff and
ownership flip; the open gap (Section 6) is a machine-checked proof that *function-changing*
repartitions preserve this invariant.

---
*Part of the [DBMS Research catalog](../../README.md).*
