# Long-Running Read-Only Transaction Isolation

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/long-read-only-isolation` · **Status:** empirically-open

## 1. Problem Statement

A long-running, read-only (analytical) transaction $Q$ must observe a **single transaction-consistent snapshot** of the database while a high-throughput OLTP write workload concurrently mutates the same data ("hot store"). The challenge is to serve $Q$'s consistent read **without (a) blocking writers, (b) forcing $Q$ to abort/restart, or (c) unbounded version retention** ("version bloat") that bloats memory and degrades MVCC scan and garbage-collection performance.

Variants:
- **Isolation guarantee:** provide $Q$ serializable / snapshot-isolation-consistent reads versus weaker bounded-staleness consistency.
- **Optimization:** minimize peak version-store size (or GC stall) subject to keeping all snapshots needed by in-flight long readers.
- **HTAP scheduling:** decide which versions to retain, when to migrate cold versions to columnar/secondary store, and how to route $Q$ to minimize interference with OLTP.

Marked **empirically-open**: the consistency mechanism (MVCC snapshots) is well understood, but the *resource/performance tradeoff* of doing so under adversarial long readers has no provably optimal solution.

## 2. Mathematical Foundations

Under **MVCC**, each item $x$ holds a version chain $x_{t_1} \ll x_{t_2} \ll \dots$ tagged with commit timestamps. A reader with snapshot timestamp $\tau$ sees, for each $x$, the version with the largest $t_i \le \tau$ that is committed and not in $\tau$'s in-flight set. A version $x_{t_i}$ is **garbage-collectable** iff no active snapshot $\tau$ in the system has $t_i \le \tau < t_{i+1}$; formally the *low-watermark* $\tau^\star = \min_{Q \in \text{active}} \tau_Q$ pins all versions with timestamp $> $ the second-newest below $\tau^\star$. A single long reader holding $\tau_Q$ forces retention of **every** version overwritten after $\tau_Q$, so version-store size grows as
$$
\Theta\!\big( W \cdot (t_{\text{now}} - \tau_Q) \big),
$$
where $W$ is the write rate to items $Q$ may touch — linear in reader duration. This is the **version-bloat / GC-watermark tension**: correctness (serializability via a fixed snapshot) directly conflicts with space. Serializability of read-only transactions can be obtained "for free" in SI when the read set's snapshot is consistent, but write-skew/anomaly avoidance for *mixed* workloads requires SSI-style certification (Fekete et al.).

## 3. State of the Art (SOTA)

**Systems-SOTA.** Production MVCC engines pin a snapshot for long readers: **PostgreSQL** (XID-horizon + autovacuum), **HyPer/Umbra** (Neumann, Mühlbauer, Kemper, SIGMOD 2015 — fast serializable MVCC with precision locking and efficient GC), **SAP HANA** and **Hekaton** all confront version bloat. **HTAP** designs isolate analytics from OLTP via fresh consistent snapshots on a columnar replica: **HyPer's fork-based snapshotting** (Kemper, Neumann, ICDE 2011) uses OS copy-on-write; **TiDB/TiFlash**, **SingleStore**, and **Oracle In-Memory** route long scans to a separate consistent column store. **Scalable MVCC GC** (Böttcher, Leis, Neumann, Kemper, VLDB 2019) introduces interval-based and steam GC to bound retained versions even with long readers.

**Theory-SOTA.** Serializable SI (Cahill, Röhm, Fekete, SIGMOD 2008) gives the consistency-side theory; no tight theory bounds the space–staleness frontier.

## 4. Upper Bound

With a fixed snapshot, $Q$ reads consistently in $O(\text{read-set} + \text{chain-walk})$ time, and version-store space is $O(W \cdot \Delta)$ for reader duration $\Delta$ — an *upper* bound matched in the worst case (every touched item rewritten). GC strategies reduce the *constant* and reclaim eagerly down to the watermark; interval-based GC (VLDB 2019) achieves retained-version count proportional to the genuinely-needed versions across active snapshots, near information-theoretic optimal for a given set of active readers. Bounded-staleness variants cap space at $O(W \cdot S)$ for staleness budget $S$ by refreshing $Q$'s snapshot, trading consistency for space. These hold in the **in-memory multicore MVCC** model.

## 5. Lower Bound

**Information-theoretic / space lower bound:** to serve a serializable snapshot as of $\tau_Q$ while writers continue, the system *must* retain at least one distinct version for each item overwritten in $(\tau_Q, t_{\text{now}}]$ that $Q$ could read; an adversarial writer touching $W$ distinct items forces $\Omega(W \cdot \Delta)$ retained state. Thus **no mechanism preserving exact snapshot consistency can avoid space linear in reader duration $\times$ overwrite breadth** — version bloat is unavoidable in the worst case. Avoiding it *requires* relaxing to bounded staleness or recomputation. There is also a **CAP-style** tension in replicated HTAP: a fresh consistent analytical snapshot on a replica cannot be both maximally fresh and available under partition.

## 6. The Gap

The consistency mechanism is *solved* (MVCC snapshots + SSI). What is **open** is the *resource-optimal* policy: given a distribution over reader durations and write hotspots, which versions to retain, when to spill cold versions to secondary/columnar storage, and how to schedule GC so that worst-case bloat is bounded while OLTP latency stays flat. No algorithm provably minimizes peak version-store space subject to serving all live readers under online (unknown-duration) arrivals, and no competitive-ratio result exists for online version retention. Closing the gap means an online retention/spilling policy with proven competitive guarantees, or a hardness result.

## 7. Current Research (as of June 2026)

Directions: (i) **HTAP version-store offloading** — migrating overwritten versions to columnar/secondary stores so long readers don't pin the hot store *(frontier — verify)*; (ii) GC scheduling that is hot-path-aware (Umbra, Neumann/Leis at TU Munich); (iii) **disaggregated and tiered MVCC** keeping old versions in cheaper memory/SSD; (iv) bounded-staleness analytical engines with formal freshness SLAs. Leading groups: TU Munich (Neumann, Leis, Kemper), CMU-DB (Pavlo — version-storage study, Wu et al. VLDB 2017), MIT (Madden), and HTAP vendors (TiDB/PingCAP, SingleStore). Cloud-native separation of compute/storage (Aurora, Socrates) reshapes the bloat tradeoff by externalizing version history to the log store.

## 8. Future Work

- Online version-retention policies with provable competitive ratios against the clairvoyant optimum for unknown reader durations.
- Cost models and schedulers for tiered version stores (DRAM → NVMe → object store) under mixed HTAP load.
- Formal characterization of the space–staleness–consistency tradeoff (a "CAP-like" theorem for long analytical reads).
- Workload-adaptive GC that provably bounds OLTP tail-latency impact while serving long scans.

## 9. Key References

- **[SOTA]** T. Neumann, T. Mühlbauer, A. Kemper. *Fast Serializable Multi-Version Concurrency Control for Main-Memory Database Systems.* SIGMOD, 2015.
- **[SOTA]** J. Böttcher, V. Leis, T. Neumann, A. Kemper. *Scalable Garbage Collection for In-Memory MVCC Systems.* VLDB, 2019.
- **[SOTA]** A. Kemper, T. Neumann. *HyPer: A Hybrid OLTP&OLAP Main Memory Database System Based on Virtual Memory Snapshots.* ICDE, 2011.
- **[SOTA]** M. J. Cahill, U. Röhm, A. D. Fekete. *Serializable Isolation for Snapshot Databases.* SIGMOD, 2008.
- **[Survey]** Y. Wu, J. Arulraj, J. Lin, R. Xian, A. Pavlo. *An Empirical Evaluation of In-Memory Multi-Version Concurrency Control.* VLDB, 2017.
- **[Foundational]** H. Berenson, P. Bernstein, J. Gray, J. Melton, E. O'Neil, P. O'Neil. *A Critique of ANSI SQL Isolation Levels.* SIGMOD, 1995.

---
*Part of the [DBMS Research catalog](../../README.md).*
