---
id: 06-recovery-logging/instant-recovery-indexes
title: "Instant recovery for indexes"
topic: 06-recovery-logging
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Instant recovery for indexes

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/instant-recovery-indexes` · **Status:** partially-solved

## 1. Problem Statement
After a crash (or media failure), classical recovery must finish redo/undo before the database accepts new transactions, giving downtime proportional to log/restore volume. **Instant recovery** instead makes the system transactionally available almost immediately and recovers state **on demand, query-driven**: a page (or key range) is restored only when a transaction first touches it. The problem here narrows to **indexes** — B-trees and LSM trees — which have rich invariants (sortedness, balance, sibling links, level structure) that on-demand recovery must preserve while serving reads/writes during recovery.

Variants:
- **Optimization:** minimize time-to-first-transaction and total recovery work while bounding per-access latency tax during recovery.
- **Decision/correctness:** does an on-demand restore schedule preserve index invariants and transactional consistency (no torn structure, no lost/duplicated keys) for every interleaving?
- **Scheduling:** order background restoration to minimize expected stalls given a query access distribution.

## 2. Mathematical Foundations
The enabling abstraction is the **per-page log partition** plus **page-LSN test-and-set** idempotency from ARIES, restricted so that restoring one page needs only that page's log records (a *log archive indexed by page id*) — "single-page recovery." Restoring page $p$ to LSN $L$ requires applying exactly the records in $p$'s log chain with `record.LSN > backup.LSN`, an **idempotent fold** $\text{restore}(p) = \text{fold}(\oplus, \text{backup}(p), \text{log}_p)$.

For B-trees, correctness rests on the **link/Blink-tree** discipline (Lehman & Yao): high-keys + right-sibling links make structure modifications (splits/merges) recoverable and traversable even when a node is provisionally inconsistent, so a reader can be redirected rather than blocked. On-demand recovery composes single-page restoration with the Blink invariant so that touching a node triggers its restore and any pending structural action.

For LSM trees the model differs: durability comes from the WAL + immutable sorted runs (SSTables) plus a manifest. Recovery is **replay WAL into the memtable** + **re-open the run set**; "instant" availability means serving reads from already-durable runs while the memtable is rebuilt and compactions resume. The relevant quantities are **read-amplification during recovery** and the **manifest consistency** (which runs are live), an atomic-commit problem over the level structure.

Scheduling restoration under a query distribution is an **online paging / competitive caching** problem: order page restores to minimize expected on-access stalls — related to weighted caching and to **prefetching with known access hints**.

## 3. State of the Art (SOTA)
- **Systems/Theory-SOTA:** The **Instant Recovery** program of **Goetz Graefe, Caetano Sauer, Wey Guy, Theo Härder** is the canonical body: *"Instant Recovery with Write-Ahead Logging"* (Synthesis Lectures, 2014/2016) and Sauer's work on **single-page repair, on-demand redo/undo, instant restore from log archives, and instant failover** (Sauer, Graefe, Härder, "Instant Restore After a Media Failure," ADBIS 2017; SIGMOD/VLDB-adjacent venues). This makes B-tree-style on-demand recovery genuinely **partially-solved** for disk-based engines.
- **Main-memory:** Parallel/instant recovery in **Hekaton**, **SiloR** (OSDI 2014), and **H-Store** reconstruct indexes by parallel re-population; main-memory indexes are typically rebuilt, not page-restored.
- **LSM:** Production engines (RocksDB, LevelDB) already open immediately from durable SSTables + WAL replay; the "instant" story is largely solved in practice though under-formalized.

## 4. Upper Bound
Single-page recovery restores a page in $O(|\text{log}_p|)$ log records, independent of total log size, given a page-indexed log archive. Instant restore achieves **time-to-first-transaction $\approx$ constant** (bounded by metadata/backup-catalog load), with total restore work $O(\text{database size})$ amortized in the background and per-access overhead $O(\text{on-demand fragment size})$. For LSM, recovery is $O(|\text{WAL}|)$ replay plus $O(1)$ manifest re-open, with reads available immediately at elevated read-amplification.

## 5. Lower Bound
- **Information / I/O:** you cannot make a page consistent without reading its backup image and its log records; total restore work is lower-bounded by the changed-data volume since the last full backup (you must transfer/replay at least the modified bytes).
- **Online scheduling:** restoration ordering under unknown future accesses is an online paging problem; deterministic competitive ratio is $\Omega(k)$ (cache size $k$), so no online restore schedule can match the optimal offline schedule by more than that factor — adversarial access patterns force stalls.
- No availability *impossibility* applies once durability is satisfied, so the lower bounds are I/O-volume and online-competitive, not hardness.

## 6. The Gap
For single-node B-trees, upper and lower bounds nearly meet — restore work is within constants of the changed-data floor — which is why this is *partially*, not fully, solved. Open gaps: (1) **LSM instant recovery lacks the clean formal single-page guarantees** B-trees enjoy, especially around compaction-state and manifest recovery; (2) **distributed/disaggregated** instant recovery (page server + log service, e.g., Aurora/Socrates) is not characterized; (3) optimal **restore scheduling** vs. a competitive lower bound is open under realistic access skew; (4) interaction with **secondary indexes / multi-index consistency** during partial recovery.

## 7. Current Research (as of June 2026)
- Extending instant recovery to **disaggregated cloud OLTP** (page servers, log-as-a-service), where on-demand page restore from a remote log is a natural fit *(frontier — verify)*.
- Formalizing **instant recovery for LSM** compaction and manifest state, and for learned indexes *(frontier — verify)*.
- Access-hint / learned prefetching to schedule background restoration and minimize the recovery latency tax.
- Instant failover combined with single-copy/erasure-coded durability.

## 8. Future Work
- A unified correctness + competitiveness theory covering B-tree *and* LSM on-demand recovery.
- Provably near-optimal restore scheduling under measured access distributions.
- Multi-index and distributed-consistency guarantees during partial recovery.
- Energy/SLO-bounded recovery (bounded p99 latency tax during restore).

## 9. Key References
- **[SOTA / Survey]** Graefe, G., Guy, W. & Sauer, C. *Instant Recovery with Write-Ahead Logging: Page Repair, System Restart, Media Restore, and System Failover.* Synthesis Lectures on Data Management, Morgan & Claypool, 2nd ed., 2016. — [DOI](https://doi.org/10.1007/978-3-031-01857-2)
- **[SOTA]** Sauer, C., Graefe, G. & Härder, T. *Instant Restore After a Media Failure.* ADBIS, 2017. — [DOI](https://doi.org/10.1007/978-3-319-66917-5_21)
- **[Foundational]** Lehman, P. & Yao, S. B. *Efficient Locking for Concurrent Operations on B-Trees (Blink-trees).* ACM TODS, 1981. — [DOI](https://doi.org/10.1145/319628.319663)
- **[Foundational]** Mohan, C. et al. *ARIES.* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[Foundational]** O'Neil, P., Cheng, E., Gawlick, D. & O'Neil, E. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996. — [DOI](https://doi.org/10.1007/s002360050048)

## 10. Worked Example

A B-tree leaf page $p$ has backup image at LSN 100. Since the backup, four updates touched $p$, logged as records with LSNs 140, 175, 175 (a duplicate replay), 220, plus an unrelated record at LSN 160 on another page. Crash strikes; a transaction now reads a key in $p$, triggering **single-page restore**.

**Restore fold.** Load $\text{backup}(p)$ at LSN 100, then apply only $p$'s chain with $\text{LSN} > 100$: records 140, 175, 220 (record 160 belongs to a different page and is skipped). Idempotency: the page-LSN test-and-set means re-applying the duplicate 175 is a no-op once page-LSN $\ge 175$, so $\text{restore}(p) = \text{fold}(\oplus, \text{backup}(p), \{140,175,220\})$ yields page-LSN $= 220$. Cost is $O(|\text{log}_p|) = 3$ records, **independent of total log size**.

**Availability.** Time-to-first-transaction is $\approx$ constant (load backup catalog), not $O(\text{whole log})$. Other pages restore lazily on first touch; total background work is $O(\text{changed bytes since backup})$ — the I/O lower bound.

**Online-scheduling tax.** With cache size $k$, the deterministic competitive ratio for ordering background restores against adversarial access is $\Omega(k)$, so some on-access stalls are unavoidable under skewed, unknown future accesses.

---
*Part of the [DBMS Research catalog](../../README.md).*
