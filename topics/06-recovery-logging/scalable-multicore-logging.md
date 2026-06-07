---
id: 06-recovery-logging/scalable-multicore-logging
title: "Scalable multicore log manager"
topic: 06-recovery-logging
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Scalable multicore log manager

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/scalable-multicore-logging` · **Status:** partially-solved

## 1. Problem Statement

A classical write-ahead log manager serializes all transactions through a single in-memory log buffer protected by a latch, and assigns each log record a monotonically increasing Log Sequence Number (LSN) from a single counter. On a handful of cores this is fine; on hundreds of cores it becomes the dominant scalability bottleneck — every committing transaction contends on the buffer latch, the LSN counter cache line, and the log-flush serialization point.

**Problem:** design a log manager whose throughput scales (near-)linearly with core count while preserving full recoverability — i.e., the ability to reconstruct a transaction-consistent state after a crash, including correct WAL ordering (a log record must be durable before the corresponding page is) and a recoverable commit order.

Sub-problems: (a) remove the centralized log buffer (buffer contention); (b) remove the global monotonic LSN (counter contention / false sharing); (c) keep recovery correct and ideally not slower; (d) preserve cross-record ordering needed for WAL and for replication.

## 2. Mathematical Foundations

The serialization point can be modeled with a contention/throughput law. Under USL (Universal Scalability Law), throughput $C(N) = \dfrac{N}{1 + \alpha(N-1) + \beta N(N-1)}$, where the global LSN counter contributes to the *contention* term $\alpha$ and cross-core cache-line ping-pong to the *coherence* term $\beta$. A single global counter forces $\beta>0$, capping and eventually *decreasing* throughput as $N$ grows.

The correctness object is a partial order. WAL requires: for any page $p$ and its update $u$, $\text{persist}(\text{log}(u)) \prec \text{persist}(p)$. Commit recoverability requires a recoverable *serialization order* consistent with the conflict graph. Distributed logging relaxes the *total* order on LSNs to a *partial* order plus a merge rule: per-core logs carry local sequence numbers, and a global order is reconstructed at recovery from vector-clock-like timestamps or from a consistent cut. Correctness reduces to showing the merged replay yields a serializable, prefix-consistent state.

Key invariant for partitioned logs: any inter-log dependency edge must be made *recoverable* — typically by stamping records with a global commit timestamp $ts$ (from a scalable source) so recovery can topologically order across logs.

## 3. State of the Art (SOTA)

- **Aether** (Johnson, Pandis, Stoica, Ailamaki; VLDB 2010) — consolidation-array log buffer, flush pipelining, and decoupled buffer fill/flush; removes much of the buffer-latch and log-flush contention. The reference baseline.
- **Distributed / partitioned logging** — per-core or per-socket logs (Wang & Johnson, *Scalable Logging through Emerging Non-Volatile Memory*, VLDB 2014) using NVM to make many small logs cheap, with a global sequence reconstruction.
- **Silo / SiloR** (Tu, Zheng, Kohler, Liskov, Madden; SOSP 2013) — epoch-based commit removes the global LSN entirely: transactions get a (TID, epoch) and durability is at epoch granularity; recovery replays whole epochs. This is the cleanest "no global counter" answer.
- **Taurus / dependency-tracking logging** (Xia et al.) — per-thread logs with explicit LSN-vector dependency tracking enabling parallel recovery *(frontier — verify exact venue)*.

## 4. Upper Bound

Best achieved: **near-linear commit throughput** to ~100+ cores using epoch-based group commit (Silo) — the global counter is replaced by a coarse global epoch advanced infrequently, so its cache line is read-mostly. Parallel/distributed logging schemes attain **per-core log bandwidth scaling** (aggregate $\Theta(N)$ log throughput) with recovery time reduced via parallel replay (SiloR recovers by replaying epochs across all cores, roughly $O(\text{log}/N)$ wall-clock). NVM-resident per-core logs push per-commit persist latency toward a single cache-line flush.

## 5. Lower Bound

Any protocol that produces a *single totally ordered* durable log has an inherent serialization point; by the coherence term of USL / a simple adversary on a shared counter, sustaining $\Omega(N)$ distinct concurrent committers through one monotonic counter incurs $\Omega(N)$ coherence traffic, bounding scalability. More fundamentally, recovering a serializable order requires persisting *enough ordering information* to reconstruct the conflict-graph topological order — an information-theoretic floor: you cannot use fully independent unordered logs if transactions conflict; some cross-log ordering bits must be persisted. There is no NP-hardness here; the barrier is contention/communication, not computation.

## 6. The Gap

Largely closed *in practice* for OLTP throughput: epoch commit + partitioned logs scale. The residual gaps: (1) recovery-time scalability and parallelism are less studied than commit-time; (2) coarse epoch durability widens the *durability window* (data loss bound), trading latency for throughput — the optimal point is workload-dependent and not characterized; (3) cross-partition / distributed transactions reintroduce ordering bottlenecks; (4) no tight theory of the minimum cross-log ordering information. Hence *partially-solved*.

## 7. Current Research (as of June 2026)

Active: log-as-the-database / log-is-the-truth designs (e.g., Amazon Aurora's "the log is the database," Socrates) push logging into a scalable storage tier; parallel recovery and **instant/constant-time recovery** integration with multicore logging; NVM/CXL-attached memory for cheap per-core durable logs *(frontier — verify)*. Groups: Ailamaki (EPFL DIAS), Madden/Liskov-lineage (MIT), Johnson, and cloud-DB teams (AWS, Microsoft). A 2025–2026 thread reconstructs global order from RDMA/CXL-shared timestamps to scale distributed commit *(frontier — verify)*.

## 8. Future Work

- Tight characterization of the throughput/durability-window/recovery-time trade-off.
- Scalable logging for the *distributed* case without a global timestamp oracle.
- Co-designing log layout with parallel recovery so both commit and recovery scale.
- Exploiting CXL shared memory for a logically-shared but contention-free log.

## 9. Key References

- **[Foundational]** C. Mohan et al. *ARIES.* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[SOTA]** Ryan Johnson, Ippokratis Pandis, Radu Stoica, Anastasia Ailamaki, Babak Falsafi. *Aether: A Scalable Approach to Logging.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920928)
- **[SOTA]** Stephen Tu, Wenting Zheng, Eddie Kohler, Barbara Liskov, Samuel Madden. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522713)
- **[SOTA]** Tianzheng Wang, Ryan Johnson. *Scalable Logging through Emerging Non-Volatile Memory.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2732951.2732960)
- **[SOTA]** Wenting Zheng et al. *Fast Databases with Fast Durability and Recovery through Multicore Parallelism (SiloR).* OSDI, 2014. — [DBLP](https://dblp.org/rec/conf/osdi/ZhengTKL14.html)

## 10. Worked Example

Take $N=64$ committing cores, all serializing through one global LSN counter. Model the counter cache line as a critical section of $L=80$ ns (one coherence round-trip to fetch the line exclusive). A single shared counter can hand out at most $1/L = 12.5$M LSNs/s, so aggregate commit throughput is capped at $\approx 12.5$M txn/s no matter how many cores you add — and USL's coherence term $\beta>0$ actually *bends the curve down* past the peak.

Now switch to Silo-style epoch commit. Replace the per-commit counter bump with one global epoch advanced every $40$ ms by a single thread; each core stamps commits with its read-mostly copy of the epoch. The hot cache line is now read $64\times$ but written once per epoch ($25$/s), removing the write-coherence bottleneck: per-core commit work becomes contention-free, and aggregate throughput scales as $\Theta(N)$.

The trade-off appears in the *durability window*: a crash can lose up to one epoch of committed-but-not-yet-persisted work, i.e. $\le 40$ ms of transactions — exactly the latency-for-throughput exchange section 6 flags as workload-dependent.

---
*Part of the [DBMS Research catalog](../../README.md).*
