# Hybrid Row/Column (HTAP) Layout

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/htap-hybrid-layout` · **Status:** open

## 1. Problem Statement

Hybrid Transactional/Analytical Processing (HTAP) asks a single system to serve high-throughput, point-access **OLTP** (row-friendly: full-tuple reads/writes, indexed lookups, MVCC) *and* scan-heavy, aggregate **OLAP** (column-friendly: few columns, large ranges, vectorized SIMD) **from one logical dataset**, ideally on **fresh** data, without crippling either workload.

The core problem: choose a *physical organization* (and the machinery around it) that resolves the fundamental tension — row layout is optimal for OLTP locality but pathological for OLAP scan bandwidth, and vice versa.

Variants:

- **Design / decision variant:** does there exist a layout + maintenance scheme meeting target SLAs for both workloads simultaneously (latency for OLTP, scan throughput for OLAP, freshness lag $\le \tau$)?
- **Optimization variant:** minimize total cost (OLTP latency + OLAP scan cost + conversion/maintenance overhead + memory) over a mixed workload, choosing the row/column split, the delta-to-main merge policy, and replication factor.
- **Resource-isolation variant:** guarantee that analytical scans do not degrade transactional tail latency (interference bound).

## 2. Mathematical Foundations

Model a relation as $n$ tuples over attributes $A_1,\dots,A_c$. A layout is a partition/replication function $\pi$ mapping (tuple, attribute) cells to storage segments, each tagged row-major or column-major. Two cost regimes:

- **OLTP cost:** point op touches one tuple; row-major cost $O(1)$ cache lines, column-major cost $O(c)$ scattered accesses. Write amplification under MVCC adds version-chain traversal.
- **OLAP cost:** scan of $k\le c$ columns over $n$ rows; column-major cost $\propto k\cdot n / W$ (bandwidth $W$, SIMD width amortized), row-major cost $\propto c\cdot n / W$ — a factor $c/k$ penalty.

The classic compromise is **PAX** (Ailamaki et al., VLDB 2001): row-grouped pages with per-page column minipages — cache-friendly scans without losing tuple locality on disk. HTAP generalizes PAX with a **two-store delta/main** decomposition: writes land in a write-optimized **delta** (row or uncompressed columnar), periodically **merged** into a read-optimized compressed **main**. Freshness is governed by a merge/queueing model; the merge is an amortized-cost problem akin to **LSM compaction**, with read-amplification vs. write-amplification vs. freshness as a three-way trade-off. Snapshot isolation/MVCC provides the correctness substrate.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** **SAP HANA** (delta/main, dictionary-encoded columnar, Sikka et al. SIGMOD 2012); **Hyper** (Neumann/Kemper, ICDE 2011 — fork/CoW snapshots for analytics over OLTP); **MemSQL/SingleStore** (row in-memory + columnstore on disk, "universal storage"); **Microsoft SQL Server columnstore + in-memory OLTP** (Larson et al.); **Oracle Database In-Memory** (dual-format, Lahiri et al. ICDE 2015); **DuckDB / Umbra** for the analytical side; **TiDB/TiFlash** (Raft-replicated row + columnar learner, VLDB 2020); **Databricks/Snowflake** lean OLAP-only. *(frontier — verify: SingleStore/TiFlash freshness-lag specifics.)*
- **Theory-SOTA:** No closed-form optimal; the design space is characterized qualitatively. Closest formal results are LSM cost models (Dayan et al., **Monkey**, SIGMOD 2017) bounding the read/write/space trade-off that the delta-merge inherits.

## 4. Upper Bound

PAX gives a *provably better* cache-miss profile than NSM for scans while matching NSM tuple locality on disk — an upper bound on the compromise's overhead. Dual-format systems achieve near-pure-OLTP and near-pure-OLAP performance *at the cost of ~2× memory* (data materialized in both formats). For delta/main, **Monkey**-style analysis bounds amortized write cost and read amplification of the merge as a function of merge frequency, giving an upper bound on the freshness/throughput surface. No single-copy layout is known to dominate both workloads.

## 5. Lower Bound

The tension is *information-/architecture-theoretic*, not NP-hardness. With a **single copy** in one major order, any scan of $k$ of $c$ columns under row-major pays $\Omega(c/k)$ bandwidth overhead vs. column-major, and any point read under column-major pays $\Omega(c)$ scattered cache lines vs. row-major — so **no single layout** is simultaneously optimal for both (a Pareto-frontier impossibility). Replication breaks the bound but incurs $\Omega(\text{storage}\times f)$ space and a synchronization/freshness lower bound: keeping a replica fresh within lag $\tau$ requires update propagation work $\Omega(\text{write-rate})$, and resource interference between scans and transactions is bounded below by shared-memory-bandwidth contention. CAP-style: under partitions a distributed HTAP replica must trade freshness (consistency) for analytical availability.

## 6. The Gap

**Genuinely open.** There is no agreed optimal point on the {OLTP latency, OLAP throughput, freshness, memory, isolation} surface, no tight formal model that an optimizer can solve, and no single-copy layout that beats dual-format without sacrificing a dimension. Closing it would require either a provably Pareto-optimal adaptive layout or a tight lower bound proving the dual-format 2×-space penalty is necessary for given SLAs.

## 7. Current Research (as of June 2026)

- **Adaptive / morphing layouts** that transition tuples row↔column based on access (H2O, Casper; modern successors in lakehouse engines) *(frontier — verify)*.
- **Lakehouse HTAP**: serving fresh OLTP into open columnar formats (Iceberg/Delta/Hudi) with low-latency upserts and deletion vectors *(frontier — verify)*.
- Hardware-assisted isolation (CXL/NUMA-aware scan throttling) to bound transactional tail-latency interference.

## 8. Future Work

- A solvable cost model unifying delta-merge, replication, and freshness for an HTAP optimizer.
- Single-copy adaptive layouts with provable competitive ratio vs. the dual-format ideal.
- Formal interference/isolation guarantees between analytical scans and OLTP under shared memory bandwidth.

## 9. Key References

- **[Foundational]** A. Ailamaki, D. DeWitt, M. Hill, M. Skounakis. *Weaving Relations for Cache Performance (PAX).* VLDB, 2001. — [VLDB PDF](https://www.vldb.org/conf/2001/P169.pdf)
- **[SOTA]** A. Kemper, T. Neumann. *HyPer: A Hybrid OLTP&OLAP Main Memory Database System Based on Virtual Memory Snapshots.* ICDE, 2011. — [DBLP](https://dblp.org/rec/conf/icde/KemperN11.html)
- **[SOTA]** V. Sikka et al. *Efficient Transaction Processing in SAP HANA Database.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213946)
- **[SOTA]** D. Huang et al. *TiDB: A Raft-based HTAP Database.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3415478.3415535)
- **[Survey]** F. Özcan, Y. Tian, P. Tözün. *Hybrid Transactional/Analytical Processing: A Survey.* SIGMOD (tutorial), 2017. — [DOI](https://doi.org/10.1145/3035918.3054784)
- **[SOTA]** N. Dayan, M. Athanassoulis, S. Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DiSC lab](https://disc.bu.edu/papers/monkey-optimal-navigable-key-value-store)

## 10. Worked Example

Take a table `orders` with $c=10$ columns, $n=10^6$ rows, cache line $= 64$ B, bandwidth $W$.

**OLAP query:** `SELECT SUM(amount) WHERE region='EU'` touches $k=2$ columns. Column-major scans $2 \times 10^6$ values; row-major must stream all $10$ columns: a $c/k = 5\times$ bandwidth penalty.

**OLTP op:** `SELECT * WHERE order_id=42` reads one full tuple. Row-major: $1$ cache line. Column-major: $10$ scattered fetches, one per column minipage — a $10\times$ access penalty.

No single layout wins both: the Pareto impossibility of section 5.

**Delta/main freshness:** writes land in a row delta at rate $r = 5{,}000$/s; merge into compressed columnar main every $\tau = 2$ s, so the delta holds $\le 10{,}000$ rows. An OLAP scan reads $10^6$ main rows plus $\le 10^4$ delta rows ($1\%$ read amplification). Halving $\tau$ to $1$ s cuts the delta to $5{,}000$ rows but doubles merge work — the read/write/freshness three-way trade-off Monkey-style analysis bounds.

---
*Part of the [DBMS Research catalog](../../README.md).*
