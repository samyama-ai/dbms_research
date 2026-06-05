# Cache coherence over disaggregated storage

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/disaggregated-cache-coherence` · **Status:** empirically-open

## 1. Problem Statement

A disaggregated cloud database runs many (often stateless or ephemeral) compute nodes that each cache pages from a shared, remote, log-structured storage tier. When one node writes (appends to the log / produces a new page version), other nodes holding the old page in their buffer cache must observe a consistent view. The **disaggregated cache-coherence problem**: maintain a coherent (or chosen-consistency) buffer cache across $N$ readers/writers over shared remote storage, minimizing coherence traffic, invalidation latency, and staleness, while preserving the database's isolation level.

Variants: (a) **strong coherence** — every read reflects the latest committed write (linearizable pages); (b) **snapshot/MVCC** — each transaction reads a consistent snapshot (LSN-based), tolerating bounded staleness for read replicas; (c) **invalidation vs. update** protocol design; (d) **lease/lock granularity** — page vs. range vs. table.

## 2. Mathematical Foundations

Coherence here is the classical **multi-reader/multi-writer cache-coherence** problem lifted from CPU caches to a distributed setting over a log. With a totally-ordered log (each write gets a monotonically increasing LSN), a snapshot read at LSN $\ell$ is well-defined; coherence reduces to ensuring caches do not serve pages with version $>\ell$ to a snapshot at $\ell$, and serve the latest for strong reads. This connects to **distributed shared memory** consistency models (linearizability, sequential, causal, snapshot isolation) and to **CAP/PACELC**: under partition you trade consistency vs. availability, and even absent partition you trade latency vs. consistency (the *EL* of PACELC). Invalidation protocols are **directory-based coherence** (a home/owner tracks sharers) vs. **lease-based** (time-bounded read permissions, à la leases of Gray–Cheriton). Lower-bound reasoning uses **communication complexity** of keeping $N$ caches consistent and the **FLP** impossibility for the agreement substrate.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Aurora uses a single-writer/many-reader design with redo-log shipping; replicas apply the log and use LSN-based read views (avoiding general write-write coherence). Socrates separates log, page, and compute. PolarDB Serverless (VLDB 2021) implements remote-memory buffer pools with a coherence protocol across compute nodes. Neon keeps compute stateless over a multi-tenant pageserver with LSN-addressed page versions. NAM-DB and FaRM-style RDMA designs explore shared remote memory coherence; Microsoft's and Alibaba's disaggregated-memory DBs are active.
- **Theory-SOTA:** leases (Gray & Cheriton, 1989), directory coherence, and the consistency-model hierarchy (Herlihy–Wing linearizability) are the rigorous foundations; no DB-specific optimal coherence protocol over log-structured storage is established.

## 4. Upper Bound

LSN/snapshot-based read views give **wait-free consistent snapshot reads** with no invalidation traffic for read replicas (each reader simply chooses a watermark LSN) — effectively $O(1)$ coherence cost for snapshot isolation, at the price of bounded staleness. For strong (linearizable) page reads, **lease-based** protocols bound stale-read latency by the lease term and avoid an RTT on the common (lease-valid) path; directory-based invalidation achieves coherence with $O(\text{sharers})$ invalidation messages per write. RDMA one-sided reads of remote buffer pools (PolarDB Serverless) cut coherence latency to microseconds.

## 5. Lower Bound

**CAP / PACELC:** under a network partition you cannot have both linearizable page reads and availability; absent partition, PACELC forces a latency–consistency trade-off — strong coherence costs at least one cross-node round trip in the worst case. **FLP impossibility** bounds the agreement substrate: no deterministic protocol guarantees coherence agreement with even one crash failure in a fully asynchronous network without extra assumptions (timeouts/leases/leadership). Communication-complexity: keeping $N$ writer-visible caches strongly coherent under an adversarial write stream requires $\Omega(N)$ invalidation messages per conflicting write in the worst case.

## 6. The Gap

For **snapshot/MVCC read replicas** the problem is essentially *solved* in practice (LSN watermarks, cheap and scalable). The status is **empirically-open** for **multi-writer** strong coherence over disaggregated log storage at scale: protocols exist (directory/lease, RDMA buffer pools) but there is no clean theory pinning the optimal trade-off among coherence traffic, staleness, invalidation latency, and write throughput, and production systems mostly *avoid* multi-writer by funnelling writes through one node. Closing the gap means either a provably traffic-optimal multi-writer coherence protocol or a sharp impossibility characterizing what disaggregation forbids.

## 7. Current Research (as of June 2026)

Active: RDMA/CXL disaggregated-memory buffer pools, multi-writer cloud databases (Aurora Limitless, PolarDB multi-master), and learned/adaptive coherence granularity. Groups: TUM (Leis/Kemper lineage on cloud buffer management), MIT, CMU, Microsoft Research, Alibaba, and AWS. *(frontier — verify)* 2025–2026 work leverages **CXL 3.0 memory pooling** to share a coherent far-memory buffer pool across compute nodes with hardware-assisted coherence, potentially sidestepping software invalidation; maturity and consistency guarantees are unverified.

## 8. Future Work

- Provably traffic-optimal multi-writer coherence over log-structured remote storage.
- Hardware-software co-design with CXL coherence for shared buffer pools.
- Adaptive granularity (page/range/table) coherence driven by contention.
- Formal staleness–latency–throughput Pareto characterization per isolation level.

## 9. Key References

- **[Foundational]** Gray, Cheriton. *Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency.* SOSP, 1989.
- **[Foundational]** Herlihy, Wing. *Linearizability: A Correctness Condition for Concurrent Objects.* TOPLAS, 1990.
- **[Foundational]** Gilbert, Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services (CAP).* SIGACT News, 2002.
- **[SOTA]** Cao, Liu, et al. *PolarDB Serverless: A Cloud Native Database for Disaggregated Data Centers.* SIGMOD, 2021.
- **[SOTA]** Verbitski, Gupta, et al. *Amazon Aurora: On Avoiding Distributed Consensus for I/Os, Commits, and Membership Changes.* SIGMOD, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
