# Hybrid OLTP/OLAP Snapshot Consistency

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/htap-snapshot-consistency` · **Status:** empirically-open

## 1. Problem Statement

Hybrid Transactional/Analytical Processing (HTAP) systems run long, read-heavy analytical queries (OLAP) against the *same* logical state that short, write-heavy transactions (OLTP) are mutating in real time. The problem is to give each analytical query a **transaction-consistent snapshot** that is simultaneously (a) **fresh** — reflecting recently committed writes, (b) **consistent** — corresponding to some serial prefix of the commit order, and (c) **cheap** — not throttling OLTP commit throughput nor forcing analytics onto stale row-store layouts. The tension is that analytics want a columnar, scan-optimized, immutable snapshot while transactions want a row-store, write-optimized, mutable state.

Variants: the **decision** form (does a proposed snapshot mechanism preserve a target isolation level, e.g., snapshot isolation or strict serializability?), the **optimization** form (minimize the *staleness–throughput–memory* objective), and the **placement** form (which delta/version data should be materialized in column format and when).

## 2. Mathematical Foundations

Model the database as a sequence of committed transactions $T_1, T_2, \dots$ inducing a totally ordered commit log with monotone commit timestamps $c(T_i)$. A snapshot at timestamp $s$ is the multiversion read state $V(s) = \{\, \text{latest version of } x \text{ with } c(\mathrm{write}) \le s \,\}$. Consistency requires that $V(s)$ equal the state after applying exactly $\{T_i : c(T_i) \le s\}$ — i.e., snapshots are **prefix-consistent** in the commit order.

Define **staleness** $\Delta = c_{\text{now}} - s$ and **visibility lag** as the delay before a committed write enters the columnar replica. The core trade-off is captured by a three-way objective

$$\min \; \alpha \, \mathbb{E}[\Delta] + \beta \, (\text{OLTP latency overhead}) + \gamma \, (\text{memory for retained versions}),$$

subject to the constraint that the analytical side observe a prefix-consistent cut. MVCC garbage-collection theory bounds the retained-version set by the oldest active snapshot timestamp $s_{\min}$: versions older than the minimum live reader are reclaimable (the *watermark* / low-water-mark argument).

## 3. State of the Art (SOTA)

**Systems-SOTA:** SAP HANA (delta/main column store with merge), HyPer (Neumann/Kemper, ICDE 2011) using hardware **fork()**-based virtual-memory snapshots for OLAP on the transactional state, and its successor work on MVCC for main-memory HTAP (Neumann, Mühlbauer, Kemper, SIGMOD 2015). SingleStore, TiDB/TiFlash (Raft-learner columnar replica), Oracle Database In-Memory (dual-format), and Microsoft SQL Server with in-memory column store indexes are the production exemplars. Research systems: BatchDB, L-Store (Sadoghi et al.), Proteus, and Caldera/relaxed-freshness designs. The dual-format and delta-main-merge architectures dominate.

## 4. Upper Bound

With MVCC and a fork-style or epoch-based snapshot, an analytical query obtains a consistent snapshot in $O(1)$ coordination with the writer path (no global lock), and visibility lag can be bounded by the delta-merge interval. HyPer's VM-snapshot gives copy-on-write cost proportional only to pages *actually* dirtied during a scan, not to database size. Epoch-based reclamation bounds retained memory by $O(\text{writes within the longest live snapshot window})$. These are *systems* upper bounds (RAM / shared-memory model with COW page faults); no nontrivial worst-case asymptotic separations are claimed.

## 5. Lower Bound

There is no clean complexity-class lower bound; the obstruction is an empirical/architectural impossibility-style trade-off. Any mechanism guaranteeing zero visibility lag (strictly fresh consistent snapshots) must either block commits during snapshot acquisition or replicate every write synchronously into the scan-optimized format — both impose throughput cost. This mirrors **PACELC**: absent partitions, one still trades **latency vs. consistency/freshness**. Retaining arbitrarily fresh *and* arbitrarily old snapshots simultaneously forces $\Omega(\text{version count})$ memory, a straightforward information-theoretic argument on the number of distinct reconstructable states.

## 6. The Gap

The gap is genuinely **empirically open**: we lack a predictive cost model that, given a workload mix, *provably* dominates on the staleness–throughput–memory frontier, and we lack agreement on the right isolation target (SI vs. serializable vs. bounded-staleness reads) for analytics. No theory says where the Pareto frontier lies for a given hardware/storage hierarchy, so design remains benchmark-driven (e.g., CH-benCHmark / HTAPBench).

## 7. Current Research (as of June 2026)

Active directions: disaggregated-memory and CXL-based HTAP where the columnar replica lives in a shared far-memory tier *(frontier — verify)*; learned/adaptive delta-merge scheduling; GPU-accelerated analytical snapshots over transactional MVCC. Groups: TUM (Neumann, Kemper), Purdue/exploratory data systems (Sadoghi), CMU (Pavlo, on self-driving HTAP knobs), and vendor research at SAP, Oracle, and PingCAP/TiDB. Bounded-freshness contracts as an explicit SLA knob are gaining traction.

## 8. Future Work

- A unified analytical cost model for the staleness/throughput/memory frontier with provable guarantees.
- Standardizing isolation semantics for HTAP analytics (when is bounded-staleness acceptable, and how to expose it).
- Snapshot mechanisms for disaggregated/CXL memory and cloud-native separated storage.
- Workload-adaptive format transition (row↔column) with online guarantees rather than static heuristics.

## 9. Key References

- **[Foundational]** Kemper, A.; Neumann, T. *HyPer: A Hybrid OLTP&OLAP Main Memory Database System Based on Virtual Memory Snapshots.* ICDE, 2011.
- **[SOTA]** Neumann, T.; Mühlbauer, T.; Kemper, A. *Fast Serializable Multi-Version Concurrency Control for Main-Memory Database Systems.* SIGMOD, 2015.
- **[SOTA]** Lang, H.; Mühlbauer, T.; Funke, F.; Boncz, P.; Neumann, T.; Kemper, A. *Data Blocks: Hybrid OLTP and OLAP on Compressed Storage.* SIGMOD, 2016.
- **[SOTA]** Huang, D. et al. *TiDB: A Raft-based HTAP Database.* PVLDB, 2020.
- **[Survey]** Özcan, F.; Tian, Y.; Tözün, P. *Hybrid Transactional/Analytical Processing: A Survey.* SIGMOD (tutorial/survey), 2017.
- **[Foundational]** Abadi, D. *Consistency Tradeoffs in Modern Distributed Database System Design (PACELC).* IEEE Computer, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
