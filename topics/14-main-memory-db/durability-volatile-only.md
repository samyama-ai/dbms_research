---
id: 14-main-memory-db/durability-volatile-only
title: "Durability for Non-Volatile-Free IMDBs"
topic: 14-main-memory-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Durability for Non-Volatile-Free IMDBs

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/durability-volatile-only` · **Status:** partially-solved

## 1. Problem Statement
Intel Optane (NVDIMM) is discontinued; many in-memory engines must again provide the **D** of ACID using only **volatile DRAM plus the network** — i.e. remote replicas and possibly a slow archival tier — rather than local non-volatile media. The problem: **what is the achievable durability guarantee, and at what latency/throughput cost, when no node can locally persist a write, only replicate it?** Concretely, define a **bounded data-loss window** $W$ (in time, or in committed-but-unacknowledged transactions) and ask for protocols that guarantee: under $f$ crash failures out of $n$ replicas, no committed transaction acknowledged to the client is lost, *or* loss is bounded by $W$ under weaker (asynchronous-replica) modes.

Variants:
- *Decision:* given failure model $(n,f)$, network model, and target $W=0$, does a commit protocol exist meeting a latency bound $L$?
- *Optimization:* minimize commit latency / maximize throughput subject to $W$ and durability level.
- The **synchronous** ($W=0$, strong) vs **bounded-asynchronous** ($W>0$, group-commit) tradeoff is the crux.

## 2. Mathematical Foundations
The setting is **fault-tolerant distributed consensus / replicated state machines**. Durability = the commit is in the *stable* set: persisted by a quorum that survives any $f$ failures. With a majority quorum, $n \ge 2f+1$ guarantees a committed write survives $f$ crashes (Lamport, Paxos); flexible/weighted quorums (Howard et al.) relax read/write quorum intersection to $Q_r + Q_w > n$. The **FLP impossibility** (Fischer–Lynch–Paterson, 1985) forbids deterministic consensus under one crash in a fully asynchronous network, so liveness needs partial synchrony / failure detectors; safety (no committed loss) is preserved regardless.

Define the loss window formally: let $C_t$ = transactions acknowledged by time $t$, $D_t$ = transactions durable (on $\ge f+1$ surviving replicas). Synchronous durability requires $C_t \subseteq D_t$ always ($W=0$). Group-commit/async replication permits $|C_t \setminus D_t| \le W$, trading a single round-trip of replication latency $\approx \text{RTT}$ for a bounded exposure. RDMA reduces RTT toward $\sim 1$–$2\,\mu s$, reshaping where the $W=0$ knee sits. **CAP** (Brewer; Gilbert–Lynch 2002) bounds the partition behavior: under partition, a $W=0$ strongly-durable system must sacrifice availability.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **Silo/SiloR** (Tu et al., SOSP 2013; Zheng et al., OSDI 2014) — epoch-based group commit with parallel logging/recovery, the reference for volatile-DRAM durability via logging. **FaRM** (Dragojević et al., SOSP 2015) uses RDMA + replication + (battery-backed) memory for fast durable transactions. **Hekaton** (Diaconu et al., SIGMOD 2013) logs to durable storage; **RAMCloud** (Ousterhout et al.) recovers DRAM state from disk-backed replicas in $\sim 1$–$2$ s by massively parallel scatter. Consensus engines: **Raft** (Ongaro–Ousterhout, ATC 2014), **CURP** (Park–Ousterhout, NSDI 2019) commit in 1 RTT in the common case.
- **Theory-SOTA:** Paxos/Raft give $n=2f+1$ optimal crash tolerance; **Flexible Paxos** (Howard–Malkhi–Spiegelman, 2016) minimizes quorum sizes.

## 4. Upper Bound
With $n = 2f+1$ replicas and partial synchrony, RSM consensus achieves $W=0$ durability at **one network round-trip** commit latency in the failure-free case (Multi-Paxos/Raft steady state; CURP pushes to 1 RTT even with concurrency via witness replicas). Epoch-based group commit (SiloR) amortizes logging so throughput is near-memory-bound while bounding $W$ to one epoch ($\sim$tens of ms). RAMCloud shows full-DRAM-state recovery in $O(1)$ s by sharding recovery across the cluster — a strong availability upper bound.

## 5. Lower Bound
**FLP** rules out a deterministic always-terminating $W=0$ commit under full asynchrony — liveness is fundamentally limited. **CAP/Gilbert–Lynch** force a strong-durability system to lose availability under partition. Crash tolerance is information-theoretically bounded: tolerating $f$ crashes with strong durability requires $n \ge 2f+1$ (Byzantine: $n\ge 3f+1$). Any $W=0$ commit must incur $\ge 1$ network round-trip to a quorum — a latency floor $\Omega(\text{RTT})$ no protocol can beat, since the acknowledging node cannot otherwise know the write survived its own crash.

## 6. The Gap
The *safety* side is essentially **solved**: quorum bounds and the RTT floor are tight. What remains open and largely empirical is the **practical Pareto frontier**: minimizing tail commit latency and maximizing throughput for a target $W$ on modern RDMA/CXL fabrics, plus recovery-time bounds for terabyte-scale DRAM state. Hence *partially-solved* — theory closed, systems frontier active.

## 7. Current Research (as of June 2026)
RDMA- and CXL-fabric replication that shaves the commit RTT toward sub-microsecond; using **CXL-attached shared/pooled memory** as a fast quasi-durable tier between DRAM and network *(frontier — verify)*; programmable-NIC/SmartNIC offload of the replication path; formal links between epoch-commit windows and externally-visible loss. Groups: MIT (Madden/Liskov lineage), Microsoft Research (FaRM/Hekaton teams), Stanford (Ousterhout/RAMCloud lineage), TUM, UW.

## 8. Future Work
- Tight latency/throughput-vs-$W$ frontier characterization on RDMA/CXL fabrics.
- Provably bounded-staleness async-replication modes with client-visible loss guarantees.
- Sub-second recovery proofs for multi-TB DRAM state with parallel scatter-gather.

## 9. Key References
- **[Foundational]** Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://dl.acm.org/doi/10.1145/3149.214121)
- **[Foundational]** Gilbert, S., Lynch, N. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* SIGACT News, 2002. — [DOI](https://dl.acm.org/doi/10.1145/564585.564601)
- **[SOTA]** Tu, S., Zheng, W., Kohler, E., Liskov, B., Madden, S. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013. — [DOI](https://dl.acm.org/doi/10.1145/2517349.2522713)
- **[SOTA]** Zheng, W., Tu, S., Kohler, E., Liskov, B. *Fast Databases with Fast Durability and Recovery (SiloR).* OSDI, 2014. — [USENIX](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/zheng_wenting)
- **[SOTA]** Dragojević, A., et al. *No Compromises: Distributed Transactions with Consistency, Availability, and Performance (FaRM).* SOSP, 2015. — [DOI](https://dl.acm.org/doi/10.1145/2815400.2815425)
- **[SOTA]** Ongaro, D., Ousterhout, J. *In Search of an Understandable Consensus Algorithm (Raft).* USENIX ATC, 2014. — [USENIX](https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro)

## 10. Worked Example

Cluster of $n=5$ replicas, tolerating $f=2$ crashes since $n = 2f+1 = 5$. A write quorum is any majority, $\lceil (n+1)/2 \rceil = 3$ replicas.

**Synchronous ($W=0$).** Client submits $\text{commit}(x{=}7)$. The leader appends to its log and ships it to followers. Once $3$ of $5$ (itself + $2$) have acknowledged, the write is durable: any later majority of $3$ must intersect this set (since $3+3 = 6 > 5$), so at least one survivor holds $x{=}7$ even after $2$ crashes. Only then is the client acked. Cost: one network round-trip, latency $\Omega(\text{RTT})$ — the section-5 floor, since the acking node cannot know the write survived its own crash without a remote copy.

**Bounded-async ($W>0$).** With epoch group commit and epoch length $10$ ms, the leader acks immediately and replicates in batches. A crash mid-epoch can lose up to one epoch of acked-but-unreplicated transactions, so the loss window is $W \le$ one epoch. Trade: throughput rises (batched RTTs) but durability weakens from $W=0$ to $W>0$, exactly the crux tradeoff of section 1.

---
*Part of the [DBMS Research catalog](../../README.md).*
