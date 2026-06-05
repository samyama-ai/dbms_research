# Recovery under partial/torn writes

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/torn-write-recovery` · **Status:** partially-solved

## 1. Problem Statement

Durability protocols often assume some unit of write is *atomic*: a page, a sector, or a cache line either fully lands on stable storage or not at all. Real devices violate this. A **torn write** (a.k.a. partial write) occurs when a crash interrupts a multi-sector page write, leaving on disk a page that is part-old, part-new — and on persistent memory, when a store spanning multiple persistence granules is partially persisted. The problem: **guarantee recoverability when the assumed atomic unit can tear.**

Concretely, given a logging/recovery protocol that relies on atomic writes of granularity $g$ (e.g., ARIES assumes atomic page writes), design detection and recovery so that after a crash:

- every torn unit is *detected*, and
- the database is restored to a transactionally consistent state (committed prefix preserved, uncommitted effects rolled back),

while minimizing the *write amplification* and latency the protection imposes.

Variants: (a) *detection* — decide whether a persisted unit is torn; (b) *recovery* — reconstruct a clean version of every torn unit; (c) *optimization* — minimize extra I/O / space to tolerate tearing.

## 2. Mathematical Foundations

Model a page write as an attempt to atomically transition stable state $P[u]$ from value $a$ to $b$ for unit $u$ of size $g$, composed of $k = g/s$ device-atomic sub-units of size $s$. A crash yields $P[u] \in \{(x_1,\dots,x_k) : x_i \in \{a_i, b_i\}\}$ — any of $2^k$ mixtures. Recoverability requires a recovery map $R$ such that for all $2^k$ outcomes, $R$ produces either a fully-old or fully-new $u$ consistent with the log.

**Detection** is an error-detecting-code argument: append a checksum/version such that a torn page is distinguishable from any intact page with high probability. With a $c$-bit checksum, undetected-tear probability is $\le 2^{-c}$ under standard assumptions. **Torn-page detection via LSN bracketing** (Microsoft SQL Server) writes a bit per sector and toggles it, so a torn page shows a mismatched sector; this is a deterministic detector using $k$ bits.

**Recovery** rests on **write-ahead logging**: if the log holds a physical (or physiological + before-image) redo/undo record for $u$, then $R$ replays/rolls back to a clean version — provided the *log itself* is written in device-atomic units (e.g., log records padded and checksummed so a torn log tail is truncated at the first bad record). The reduction is: torn-write tolerance ⇐ atomic-log-append + per-page detection + idempotent redo.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** **ARIES** assumes atomic page writes; production systems add tear protection underneath. **PostgreSQL full-page writes** log the entire page image on first modification after a checkpoint, so any torn page is reconstructable from the WAL. **MySQL/InnoDB doublewrite buffer** writes each page twice (to a sequential doublewrite area, then in place); a torn in-place page is recovered from the doublewrite copy. **SQL Server torn-page detection / page checksums** detect tearing. On PM, **logging structures use 8-byte atomic writes** as the trusted granule and build larger atomic updates via redo logs or PMwCAS.
- **Device-SOTA:** **NVMe atomic write** (`AWUN`/`AWUPF`) and **MySQL 8 atomic doublewrite on supported hardware** push atomicity into the device, eliding software doubling when the device guarantees the granule.

## 4. Upper Bound

With WAL + full-page-image logging, torn writes are tolerated at the cost of **one extra full page write per page per checkpoint epoch** (PostgreSQL) — amortized to near-zero for hot pages touched many times per epoch. Doublewrite gives **2× write amplification on the protected pages** but sequential, so throughput cost is sub-2×. Device-atomic writes give **zero software overhead** when the requested granule $\le$ the device's `AWUPF`. Detection costs **$O(1)$ bits per sector** (toggle bits) or a fixed checksum per page.

## 5. Lower Bound

- **Information-theoretic detection:** with a $c$-bit checksum, no detector can drive undetected-tear probability below $2^{-c}$ for adversarial bit patterns; deterministic detection of *every* tear requires per-sub-unit redundancy ($\Omega(k)$ bits for $k$ sub-units, as with toggle bits).
- **Recovery I/O floor:** to recover a torn unit to a clean value, that value's information must exist somewhere durable that was *not* torn by the same crash — forcing either a redundant copy (≥ 1 extra write) or a logged image. You cannot tolerate tearing of granule $g$ using only in-place single copies of granule $g$ (a pigeonhole / adversary argument: the crash can corrupt the sole copy).
- This is not NP-hard; the hardness is an unavoidable redundancy/round-trip cost, akin to the "no premature ack" durability floor.

## 6. The Gap

Largely solved in practice but with an *efficiency* gap: full-page logging and doublewrite both pay redundancy that device-atomic writes can avoid — yet device guarantees are heterogeneous, narrow (small granules), and not portable. The open part is a protocol that *adapts* to the device's true atomic granule, paying redundancy only for the gap between required and device-provided atomicity, with a matching lower bound on that residual cost. PM tearing across cache-line / persistency-granule boundaries under weak persistency models is less settled *(frontier — verify)*.

## 7. Current Research (as of June 2026)

Active threads: exploiting NVMe atomic-write and CXL semantics to remove doublewrite (MySQL/InnoDB, MariaDB engineering); formal verification of crash-consistency under torn writes (the Chidambaram group's CrashMonkey/ B³ bug-finding, and verified file systems like DFSCQ); PM tearing under Px86 persistency and "failure-atomic" `msync`/transactions *(frontier — verify)*. Cloud/disaggregated storage reframes tearing as partial-object visibility, intersecting with the disaggregated-logging problem.

## 8. Future Work

- Device-adaptive tear protection that provably pays only the residual redundancy above hardware atomicity.
- Verified end-to-end recovery proofs spanning device atomicity assumptions and the WAL protocol.
- Torn-write semantics for byte-addressable PM and CXL memory under realistic persistency models.
- Tear tolerance integrated with checksummed, self-describing log formats that auto-truncate torn tails.

## 9. Key References

- **[Foundational]** C. Mohan, Don Haderle, Bruce Lindsay, Hamid Pirahesh, Peter Schwarz. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS, 1992.
- **[Foundational]** Jim Gray, Andreas Reuter. *Transaction Processing: Concepts and Techniques.* Morgan Kaufmann, 1993.
- **[SOTA]** Ashvin Goel, Bhavish Aggarwal, et al. / InnoDB engineering. *The InnoDB Doublewrite Buffer.* (MySQL/InnoDB reference manual and design notes).
- **[SOTA]** Jayashree Mohan, Ashlie Martinez, Soujanya Ponnapalli, Pandian Raju, Vijay Chidambaram. *Finding Crash-Consistency Bugs with Bounded Black-Box Crash Testing (B³ / CrashMonkey).* OSDI, 2018.
- **[Survey]** Vijay Chidambaram. *Orderless and Eventually Durable File Systems / crash consistency.* (PhD thesis and surveys on crash consistency), 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
