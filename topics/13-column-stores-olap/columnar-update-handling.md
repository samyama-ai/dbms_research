---
id: 13-column-stores-olap/columnar-update-handling
title: "Updates and Deletes in Column Stores"
topic: 13-column-stores-olap
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Updates and Deletes in Column Stores

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/columnar-update-handling` · **Status:** partially-solved

## 1. Problem Statement
Column stores optimize for read-mostly analytics: data is sorted, compressed, and packed densely, which makes **in-place updates and deletes expensive** (re-encoding a block, breaking RLE runs, shifting positions). The problem is to support transactional inserts/updates/deletes with acceptable write throughput **while preserving** (a) scan speed, (b) compression ratio, and (c) snapshot-isolation / MVCC semantics.

Variants:
- **Insert-heavy append** (e.g., event logs): mostly solved by appending new compressed blocks.
- **Point updates/deletes** under MVCC: the hard case — must reconcile a *position* in a read-optimized base with newer versions.
- **Optimization:** minimize amortized write cost + merge cost + read amplification, subject to a target read latency.

Two canonical architectures: **value-based delta** (a small write-optimized store holding new tuples, periodically merged) and **positional delta trees (PDT)** (deltas keyed by *position* in the stable base so the base never moves until merge).

## 2. Mathematical Foundations
Model the table as a stable, read-optimized image $S$ plus a delta $\Delta$; reads compute $S \oplus \Delta$. The core tension is captured by the **RUM conjecture**: any access method trades off **R**ead, **U**pdate, and **M**emory overheads, and one cannot be optimal in all three. **LSM** analysis formalizes this: with size ratio $T$ and $L=\log_T(N/B)$ levels, leveling gives write amplification $O(T\cdot L)$ and point-read $O(L)$ I/Os; tiering gives write amp $O(L)$ but read $O(T\cdot L)$ — the **Dostoevsky / Monkey** Pareto frontier (Dayan et al.) parameterizes this precisely. Positional deltas add a **position-translation** cost: maintaining a mapping $\pi: \text{SID}\to\text{position}$ under interleaved inserts/deletes is an order-maintenance problem; PDTs amortize it to $O(\log |\Delta|)$ per lookup. Merge cost is governed by amortized analysis: merging $\Delta$ of size $d$ into base $N$ costs $O(N+d)$ but is invoked every $\Theta(d)$ writes, amortizing to $O(N/d)$ per write — choosing $d=\Theta(\sqrt{N})$ balances merge vs delta-scan.

## 3. State of the Art (SOTA)
- **C-Store / Vertica** (Stonebraker et al., VLDB 2005): a Writable Store (WOS) buffers writes, the Tuple Mover migrates to the Read-Optimized Store (ROS); ROS containers are merged like an LSM.
- **MonetDB/X100 → Positional Delta Trees** (Héman, Zukowski, Boncz et al., SIGMOD 2010): differential updates indexed by position, preserving scan order and avoiding base rewrites.
- **Apache Kudu** (Lipcon et al., 2015): per-rowset delta files (REDO/UNDO) + compaction; columnar base with MVCC deltas.
- **Snowflake / BigQuery / Redshift:** immutable micro-partitions/blocks; deletes via tombstone bitmaps, updates as delete+insert, background re-clustering.
- **Apache Hudi / Iceberg / Delta Lake:** lakehouse table formats with **copy-on-write** vs **merge-on-read** (positional/equality delete files) — the modern industrial embodiment of delta architectures.
- **SAP HANA:** L1/L2 (row/columnar) delta + main, dictionary-merge on delta promotion.

## 4. Upper Bound
On the LSM Pareto frontier, **Monkey/Dostoevsky/Spooky** (Dayan, Idreos et al., SIGMOD 2017–2020) achieve asymptotically optimal trade-offs: point lookups $O(1)$ expected with optimally tuned Bloom filters, writes $O(L/B)$ amortized I/Os under lazy leveling. PDT lookups/updates are $O(\log|\Delta|)$; scans over $S\oplus\Delta$ are linear with a small merge-on-read overhead proportional to $|\Delta|/|S|$. With $\Delta$ bounded at $\Theta(\sqrt N)$, amortized write cost is $O(\sqrt N / B)$ I/Os while scans stay near base speed.

## 5. Lower Bound
The **RUM conjecture** posits an inherent three-way trade-off; formal lower bounds exist in restricted models. For the **dictionary/predecessor** structure underlying ordered columnar access, cell-probe lower bounds (Pătraşcu–Thorup) give $\Omega(\log\log N)$-type costs. For external-memory sorted maintenance under updates, the **buffer-tree / LSM** lower bounds show write amp $\Omega(\frac{1}{B}\log_{M/B}\frac{N}{B})$ is unavoidable for comparison-based external structures. Maintaining strict sort order under arbitrary inserts forces either re-write (read-optimal) or out-of-order deltas (update-optimal) — you provably cannot have both at zero cost.

## 6. The Gap
This is **partially solved**: LSM/delta/PDT architectures give practical, tunable trade-offs with known asymptotic frontiers, and lakehouse merge-on-read is widely deployed. Open gaps: (a) tight constants and *self-tuning* policies that adapt $T$, merge cadence, and COW-vs-MOR online to drifting workloads; (b) preserving **compression and zone-map quality** across many small deletes (tombstone accumulation degrades scans); (c) clean MVCC + positional deltas at lakehouse scale where files are immutable on object storage.

## 7. Current Research (as of June 2026)
- **Adaptive merge-on-read vs copy-on-write** selection per partition driven by access skew; auto-compaction of delete files in Iceberg/Hudi *(frontier — verify)*.
- **Deletion-vector** standardization (Delta Lake deletion vectors, Iceberg v3 binary deletes) reducing rewrite amplification.
- Groups: Harvard DASlab (Idreos) on self-designing/learned LSM; CWI (Boncz) lineage on positional deltas; Databricks/Snowflake/Apple engineering on lakehouse delete encodings; CMU (Pavlo) on HTAP storage.
- HTAP convergence: unified row+column delta (SAP HANA, TiDB/TiFlash, SingleStore) keeping OLTP deltas readable by OLAP scans.

## 8. Future Work
- Online, workload-aware tuning of the full RUM/LSM frontier with SLO guarantees.
- Compression-preserving delete encodings that keep zone-maps tight.
- Formal MVCC correctness for positional deltas over immutable object-store files.
- Tighter lower bounds matching practical merge-on-read costs.

## 9. Key References
- **[Foundational]** Stonebraker et al. *C-Store: A Column-oriented DBMS.* VLDB, 2005. — [DBLP](https://dblp.uni-trier.de/rec/conf/vldb/StonebrakerABCCFLLMOORTZ05.html)
- **[Foundational]** Héman, Zukowski, Nes, Boncz et al. *Positional Update Handling in Column Stores.* SIGMOD, 2010. — [DOI](https://doi.org/10.1145/1807167.1807227)
- **[SOTA]** Dayan, Athanassoulis, Idreos. *Monkey / Dostoevsky: Optimal Navigable Key-Value Store / LSM Tuning.* SIGMOD, 2017 / 2018. — [DBLP search](https://dblp.org/search?q=Monkey%20Optimal%20Navigable%20Key-Value%20Store)
- **[SOTA]** Lipcon et al. *Kudu: Storage for Fast Analytics on Fast Data.* 2015. — [DBLP search](https://dblp.org/search?q=Kudu%20Storage%20for%20Fast%20Analytics%20on%20Fast%20Data)
- **[Foundational]** Athanassoulis, Idreos et al. *Designing Access Methods: The RUM Conjecture.* EDBT, 2016. — [DBLP](https://dblp.uni-trier.de/rec/conf/edbt/AthanassoulisKM16.html)
- **[Survey]** Abadi, Boncz, Harizopoulos et al. *The Design and Implementation of Modern Column-Oriented Database Systems.* Foundations and Trends in Databases, 2013. — [DOI](https://doi.org/10.1561/1900000024)

## 10. Worked Example

Let base $N = 10^6$ rows. Choose delta bound $d$ and amortize merge cost as in §2: merging $\Delta$ into the base costs $O(N+d)$ and is triggered once every $\Theta(d)$ writes, so per-write merge cost is $\approx N/d$.

- $d = 10^3$: merge runs every 1000 writes, amortized merge $\approx 10^6/10^3 = 1000$ per write, but each scan re-reads only $|\Delta|/|S| = 10^{-3}$ extra — cheap reads, costly writes.
- $d = 10^5$: amortized merge $\approx 10^6/10^5 = 10$ per write — but every scan now merges 10% extra rows.
- Balanced $d = \sqrt N = 10^3$ gives amortized write $O(\sqrt N) = 1000$ and scan overhead $\sqrt N / N = 10^{-3}$, matching the §4 bound $O(\sqrt N/B)$ I/Os.

A *positional* delete of base position 500 000 is recorded as a tombstone in $\Delta$, leaving the compressed base block untouched until the next merge — illustrating the read/update/memory tension of the RUM conjecture (§5).

---
*Part of the [DBMS Research catalog](../../README.md).*
