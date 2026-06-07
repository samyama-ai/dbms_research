---
id: 12-newsql-distributed-sql/safe-time-watermark-cost
title: "Watermark/safe-time computation cost"
topic: 12-newsql-distributed-sql
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Watermark/safe-time computation cost

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/safe-time-watermark-cost` · **Status:** partially-solved

## 1. Problem Statement

A distributed SQL system serves **consistent reads at a timestamp** $\tau$ from any replica.
A replica may serve such a read only once it knows it has applied (or will never receive) all
writes with timestamp $\le \tau$ across all relevant shards/partitions. The largest such $\tau$
is the **safe time** (a.k.a. **closed timestamp**, **resolved timestamp**, **safe-timestamp
watermark**). The problem is to **compute and advance this watermark efficiently and with low
lag**, across many shards, replicas, and (in HTAP/CDC) streaming consumers.

- **Optimization variant:** minimize the **safe-time lag** $now - \mathrm{safe}$ (freshness)
  and the **messaging/CPU cost** of maintaining it, jointly.
- **Decision/feasibility variant:** given per-shard progress signals, what is the maximal
  $\tau$ provably resolved (no in-flight or future-orderable write $\le \tau$ remains)?
- **Scalability variant:** keep amortized cost per advance sub-linear in the number of shards
  $S$ and replicas $R$.

The watermark underpins follower reads, change-data-capture (CDC), HTAP scans, and
backup/snapshot consistency.

## 2. Mathematical Foundations

Each shard $i$ exposes a monotone **resolved frontier** $\mathrm{rt}_i$: the largest ts below
which no further writes will be assigned (in a hybrid-logical-clock or TrueTime regime, this is
bounded by the leader's clock minus uncertainty and minus any **open intent**). The **global
safe time** is the **meet (min) over shards**:
$$\mathrm{safe} = \min_{i\in S}\ \mathrm{rt}_i.$$
This is exactly the **distributed-snapshots / low-watermark** computation of streaming systems
(Chandy–Lamport global snapshots; the *frontier* in Naiad/Timely Dataflow). It is a
**monotone aggregation**: as a partition's $\mathrm{rt}_i$ advances, the global min may advance,
but a single **straggler** (slow or idle shard, long-running txn holding an open intent) pins the
whole watermark — the *min-is-a-straggler-magnet* property.

Two costs dominate: (a) **liveness** — idle shards must still emit periodic "I have nothing $\le
\tau$" closed-timestamp heartbeats, else $\mathrm{safe}$ stalls; (b) **aggregation** — computing
the global min over $S$ shards and propagating to $R$ replicas. With TrueTime, $\mathrm{rt}_i$ is
clock-derived (commit-wait $2\varepsilon$); with HLC, it depends on observing a higher timestamp
from each source. The structure is a **monoid aggregation** $(\min)$ amenable to tree/gossip
combination, and the lag is governed by the *slowest* path plus clock uncertainty $\varepsilon$.

## 3. State of the Art (SOTA)

- **Systems SOTA:** **Spanner** uses **TrueTime** commit-wait so a replica's safe time is
  $TT.now().earliest - \varepsilon$ minus pending Paxos/2PC intents (OSDI 2012). **CockroachDB**
  *closed timestamps* publish a per-range resolved ts via leaseholder heartbeats; **YugabyteDB**
  uses an HLC-based safe time per tablet. **TiDB/TiKV** *resolved-ts* drives CDC and follower
  reads. Streaming engines (**Flink** watermarks, **Naiad/Timely** frontiers, Millwheel
  low-watermarks) solve the structurally identical problem for dataflow.
- **Theory SOTA:** the **vector-clock / matrix-clock** and **GVT (global virtual time)**
  literature from parallel discrete-event simulation (Time Warp, Fujimoto) gives the canonical
  algorithms and cost bounds for computing a distributed minimum-timestamp frontier with
  transient-message corrections.

## 4. Upper Bound

Computing the global safe time is a **monoid (min) reduction**: $O(S)$ work per recomputation,
or **$O(\log S)$ depth** with a tree/aggregation overlay, and $O(1)$ amortized per shard-update
using a *min-heap / segment-tree* keyed by $\mathrm{rt}_i$ so each advance triggers only the
necessary global re-min. Propagation to $R$ replicas is $O(R)$ or $O(\log R)$ via gossip.
**Lag** is bounded by the heartbeat interval $h$ plus clock uncertainty $\varepsilon$ plus the
longest open-intent duration: $\mathrm{lag} \le h + \varepsilon + L_{\max\text{-intent}}$. These
bounds are realized in production; the computation itself is *cheap*. The hard part is keeping
$h$, $\varepsilon$, and straggler intents small without flooding the system with heartbeats.

## 5. Lower Bound

There is an inherent **freshness lower bound**: a replica cannot certify safe time beyond what
it has *heard* from every shard, so $\mathrm{lag} \ge \varepsilon$ (clock-uncertainty / commit-wait
floor under TrueTime) and $\ge$ one message delay from the slowest contributing shard under
logical clocks. This is a **communication-complexity / knowledge** bound: to advance the global
min by $\delta$, *every* shard must communicate progress, so maintaining freshness across $S$
shards costs $\Omega(S)$ messages per global advance in the worst case (no shard can be skipped
without risking an unresolved write). Idle shards therefore *cannot* be silent for free — the
**silence vs. freshness** tension is fundamental. A single long-running transaction holding an
open intent imposes an *unbounded* lag with no protocol able to advance past it without aborting
or learning its fate.

## 6. The Gap

The aggregation cost is **solved** ($O(\log S)$, well-understood monoid reduction) and is not the
bottleneck. What remains **partially solved** is **minimizing lag at scale cheaply**: trading
heartbeat frequency (cost) against freshness (lag) across millions of mostly-idle ranges, and
handling **stragglers/open-intents** that pin the min. There is no clean optimal policy for
*adaptive* heartbeat scheduling, nor a tight characterization of the achievable
(cost, lag, $\varepsilon$) frontier under realistic clock skew and skewed shard activity. Closing
the gap means an optimal adaptive watermark-advancement protocol with proven cost/freshness
trade-off, and intent-resolution that bounds straggler-induced lag.

## 7. Current Research (as of June 2026)

- **Adaptive / hierarchical closed-timestamp** propagation that scales heartbeat cost to range
  activity, reducing per-range overhead for idle ranges (CockroachDB, TiKV resolved-ts work)
  *(frontier — verify)*.
- Tighter TrueTime-style **clock-uncertainty** reduction (better time sync, e.g., precise
  hardware clocks / PTP) to shrink the $\varepsilon$ floor *(frontier — verify)*.
- Safe-time for **HTAP** so analytical scans on the columnar replica read a consistent, low-lag
  frontier off the row store.
- Borrowing **Timely Dataflow** frontier progress-tracking for transactional watermark maintenance.
Groups: Cockroach Labs, PingCAP, Google, Microsoft, and the Timely/Materialize lineage (McSherry).

## 8. Future Work

- Provably optimal adaptive heartbeat scheduling on the (messaging-cost, freshness) Pareto frontier.
- Straggler/open-intent isolation so one long txn cannot pin the global watermark.
- Hierarchical safe-time across thousands of partitions with sublinear steady-state cost.
- Formal verification (TLA+) of closed-timestamp safety under clock skew and reconfiguration.

## 9. Key References

- **[Foundational]** Chandy, K.M., Lamport, L. *Distributed Snapshots: Determining Global States of Distributed Systems.* ACM TOCS, 1985. — [DOI](https://doi.org/10.1145/214451.214456)
- **[Foundational]** Jefferson, D. *Virtual Time (Time Warp / GVT).* ACM TOPLAS, 1985. — [DOI](https://doi.org/10.1145/3916.3988)
- **[SOTA]** Corbett, J., Dean, J., et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/corbett)
- **[SOTA]** Murray, D., McSherry, F., et al. *Naiad: A Timely Dataflow System.* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522738)
- **[SOTA]** Taft, R., et al. *CockroachDB: The Resilient Geo-Distributed SQL Database.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3386134)
- **[Foundational]** Akidau, T., et al. *MillWheel: Fault-Tolerant Stream Processing at Internet Scale.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2536222.2536229)

## 10. Worked Example

A table is split across four shards with resolved frontiers (all in ms on a common clock):
$$\mathrm{rt}_1=105,\quad \mathrm{rt}_2=108,\quad \mathrm{rt}_3=101,\quad \mathrm{rt}_4=109.$$
Global safe time $=\min_i \mathrm{rt}_i = 101$, pinned by shard 3. A follower-read at $\tau=100$ is servable from any replica; a read at $\tau=104$ must wait — shard 3 has not yet certified past $101$.

Now shard 3 is **idle** (no writes) but emits a closed-timestamp heartbeat every $h=200$ ms. If $\mathrm{now}=300$ and shard 3 last heartbeat-ed at $101$, then despite shards 1,2,4 advancing to $\sim 300$, the global safe time is **stuck at 101** — the straggler/min-magnet effect. Only at the next heartbeat does shard 3 jump to, say, $295$, lifting $\mathrm{safe}$ to $\min(305,308,295,309)=295$.

Lag bound: with clock uncertainty $\varepsilon=7$ ms and no open intents, $\mathrm{lag}\le h+\varepsilon = 207$ ms — showing why shrinking $h$ for idle ranges (adaptive heartbeats) directly buys freshness.

---
*Part of the [DBMS Research catalog](../../README.md).*
