# Log compression and reclamation bounds

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/log-compression-reclamation` · **Status:** open

## 1. Problem Statement
A recovery log grows monotonically as transactions commit; for the system to run forever in bounded space it must be **compressed** (encode records compactly) and **reclaimed/truncated** (discard records no longer needed for recovery). The problem: **establish bounds on how compactly a recoverable log can be encoded, and how aggressively it can be truncated**, while still guaranteeing correct recovery to any required point.

Variants:
- **Counting / information-theoretic:** minimum number of bits a log must retain to recover all committed state to the latest durable point (or to any point, for point-in-time recovery / PITR).
- **Optimization:** minimize steady-state log size (and reclamation I/O) subject to recovery correctness and a retention window.
- **Decision:** given a truncation point and a checkpoint, is recovery still correct (no record needed for redo/undo of an unflushed change is discarded)?

## 2. Mathematical Foundations
**Truncation correctness** is governed by the recovery dependency frontier. A redo record for page $p$ at LSN $L$ may be discarded only once $p$ is durably persisted past $L$ (the **redo-LSN / dirty-page-table minimum LSN** in ARIES) and no active transaction needs it for undo. Formally, the safe truncation point is
$$\text{minLSN} = \min\big(\text{recLSN over dirty pages},\ \text{firstLSN over active transactions}\big),$$
so reclamation is bounded *below* by the oldest in-flight dependency, not by the checkpoint alone. This couples reclamation tightly to [checkpoint scheduling](./checkpoint-scheduling-optimization.md): faster flushing ⇒ more aggressive truncation.

**Compression bounds** are information-theoretic. The minimum encoded size of the retained log is its **entropy given the recovery context**: a record need only carry the information not already derivable from the prior database state and earlier records — a **conditional-entropy / Kolmogorov-complexity** floor. Logical records approach this floor (carry the operation, not the page delta); physical records sit above it (redundant byte images). Standard tools — Lempel–Ziv on byte logs, delta-encoding against before-images, dictionary/columnar encoding of structured log fields, and **arithmetic coding** toward the entropy rate — provide the achievability side. For PITR you cannot truncate below the retention horizon, so the bound is the **integral of new information over the retention window**.

For log-structured / LSM systems the "log" and the "data" coincide; reclamation becomes **compaction**, and the relevant bound is **write-amplification** — the cut-set between space (compactness) and rewrite cost is captured by the **RUM conjecture** (Read–Update–Memory trade-off, Athanassoulis et al.) and by LSM compaction theory (Dostoevsky, Monkey).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Every engine truncates via checkpoint + active-transaction frontier (ARIES log truncation; PostgreSQL WAL recycling bounded by `min_wal_size`/replication slots/archive needs; InnoDB redo as a fixed ring overwritten once checkpointed). Compression: **log compression** ships in DB2, SQL Server (backup/log compression), and replication streams; **Aurora/Socrates** ship compact *redo* as the unit of replication, exploiting logical compactness. LSM compaction (RocksDB leveled/tiered; **Dostoevsky** and **Monkey**, Dayan et al., SIGMOD 2017/2018) is the SOTA for jointly tuning space vs. write amplification.
- **Theory-SOTA:** The RUM conjecture and LSM compaction analyses give the cleanest *trade-off* characterizations; there is **no accepted tight bound** on minimum recoverable-log size for general transactional logs — hence **open**.

## 4. Upper Bound
Achievable compactness: encoding the retained log near its conditional entropy via delta + entropy coding gives size $\approx H(\text{committed updates}\mid\text{base state})$ over the retention window; logical logging plus LZ/arithmetic coding approaches this in practice. Truncation: the log can be safely reduced to records at or after $\text{minLSN}$, so steady-state size is $O(\text{redo since oldest unflushed dependency} + \text{active-undo})$ — independent of total history, bounded by checkpoint frequency. For LSM, leveled compaction bounds space amplification to $\approx 1{+}1/(T{-}1)$ at write-amplification $O(T\log_T(N))$ for size ratio $T$.

## 5. Lower Bound
- **Information-theoretic:** the retained log cannot be smaller than the **conditional entropy** of the committed updates given recoverable base state plus the retention horizon's information content — you cannot recover information you did not store (a counting/source-coding lower bound).
- **Truncation:** you cannot truncate below $\text{minLSN}$ without violating redo/undo correctness — a hard correctness lower bound on how aggressive reclamation can be; aggressiveness is therefore capped by the slowest flush / longest-running transaction.
- **LSM space-vs-rewrite:** RUM-style trade-offs lower-bound the product of space saving and rewrite cost; you cannot get minimal space and minimal write-amplification simultaneously.

## 6. The Gap
The correctness lower bound on truncation ($\text{minLSN}$) is exact and matched in practice. The **compression** side is open: the information-theoretic floor ($H(\cdot\mid\text{state})$) is clear in principle but there is **no tight, workload-general characterization** of how close practical recoverable encodings can get while preserving fast, possibly *random-access* (point-in-time, single-page) recovery — entropy coding fights against the need to redo/restore individual pages cheaply. The genuine open question is the trade-off surface between **compactness, recovery random-access cost, and reclamation I/O**, and whether a scheme can simultaneously approach the entropy floor and support single-page/instant recovery.

## 7. Current Research (as of June 2026)
- Compact redo for **disaggregated logs** (Aurora/Socrates/Neon), where log bytes are the replication and storage cost, making compression directly load-bearing *(frontier — verify)*.
- Learned / semantic log compression exploiting workload regularities and schema structure beyond generic LZ *(frontier — verify)*.
- Joint compaction-and-recovery design for LSM so that reclamation (compaction) and recoverability share work.
- Bounded-retention PITR with provable minimal storage under a retention SLO.

## 8. Future Work
- A tight, workload-parameterized bound on minimal recoverable-log size that *also* supports random-access (single-page / PITR) recovery.
- Formal trade-off surface: compactness vs. recovery random-access cost vs. reclamation I/O.
- Unifying log compression with erasure-coded durability and with instant recovery.
- Reclamation policies that minimize write-amplification while honoring replication-slot and archive retention constraints.

## 9. Key References
- **[Foundational]** Mohan, C. et al. *ARIES (log truncation, dirty-page table, minLSN).* ACM TODS, 1992.
- **[Foundational]** O'Neil, P., Cheng, E., Gawlick, D. & O'Neil, E. *The Log-Structured Merge-Tree.* Acta Informatica, 1996.
- **[SOTA]** Athanassoulis, M. et al. *Designing Access Methods: The RUM Conjecture.* EDBT, 2016.
- **[SOTA]** Dayan, N. & Idreos, S. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores via Adaptive Removal of Superfluous Merging.* SIGMOD, 2018.
- **[Foundational]** Cover, T. & Thomas, J. *Elements of Information Theory.* Wiley, 2006. (Source-coding / conditional-entropy bounds.)
- **[SOTA]** Verbitski, A. et al. *Amazon Aurora: Design Considerations for High-Throughput Cloud-Native Relational Databases.* SIGMOD, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
