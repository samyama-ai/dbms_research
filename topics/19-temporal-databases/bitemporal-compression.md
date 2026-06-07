---
id: 19-temporal-databases/bitemporal-compression
title: "Compression of Bitemporal Histories"
topic: 19-temporal-databases
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Compression of Bitemporal Histories

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/bitemporal-compression` · **Status:** empirically-open
> **Verification note:** The Bliujute–Jensen–Saltenis–Slivinskas R-tree bitemporal indexing paper appeared at *VLDB 1998*, not ICDE 1998.

## 1. Problem Statement
A bitemporal table records every fact with both a **valid-time** period (when the fact is true in the modeled world) and a **transaction-time** period (when the fact was current in the database). The full history is therefore a set of *rectangles* in the 2-D (valid, transaction) plane, and it grows monotonically: corrections, retroactive updates, and as-of snapshots all add rectangles. The problem is to **encode this bitemporal history compactly while preserving efficient random version access** — given any $(\text{as-of transaction time } \tau,\ \text{valid-time } v)$ point or range, reconstruct the relevant tuples without decompressing the whole history.

Variants:
- **Optimization:** minimize bytes subject to a query-latency budget (the rate–access trade-off).
- **Decision:** does an encoding of size $\le B$ supporting $\le L$-latency point queries exist?
- **Dynamic:** maintain near-optimal encoding under append-only growth.

The tension is structural: temporal locality (most rows change rarely; long unchanged runs) invites delta/run-length encoding, but delta chains destroy $O(1)$ random version access. We want both.

## 2. Mathematical Foundations
Model the history as a function $H : \mathcal{T}_{tt} \times \mathcal{T}_{vt} \to \text{Tuples}$, piecewise-constant over a partition of the plane into axis-aligned rectangles. Compression seeks a minimal description length (MDL) encoding of this piecewise-constant 2-D step function. Two classical lenses:

1. **Persistent data structures** (Driscoll–Sarnak–Sleator–Tarjan, 1989): a *fully persistent* / *confluently persistent* structure stores all versions in space $O(\text{total updates})$ with $O(\log n)$ access — the partial-persistence bound is the gold standard for transaction-time-only histories. The **multiversion B-tree (MVBT)** (Becker et al., VLDBJ 1996) achieves asymptotically optimal $O(\log_b n)$ access with linear space in the number of updates.
2. **Information theory / MDL:** the incompressible core is the *entropy* of the update stream; achievable rate is bounded below by $H(\text{updates})$. Temporal locality manifests as low conditional entropy $H(\text{state}_t \mid \text{state}_{t-1})$, which delta-coding exploits. Random access under compression connects to **succinct data structures** and the **rank/select** lower bounds (cell-probe model): supporting access in $t$ probes constrains redundancy $r$ via Pătrașcu-style $r \cdot t = \Omega(n)$-type trade-offs.

The bitemporal case is the 2-D generalization: it is essentially compressed **stabbing/point-location** over a planar subdivision with version semantics, where the 2-D structure (vs. 1-D transaction-time persistence) is what makes optimality unsettled.

## 3. State of the Art (SOTA)
**Theory-SOTA:** For *transaction-time only*, partial persistence (DSST 1989) and the MVBT give space-optimal, log-time historical access; the **Snapshot Index** and **TSB-tree** (Lomet–Salzberg) are space/access-optimal for append-only transaction time. For full **bitemporal** indexing, the 4R-tree, **bitemporal R-trees**, and the work of Bliujute–Jensen–Saltenis–Slivinskas (VLDB 1998) handle the 2-D rectangles but without compression-optimality guarantees.

**Systems-SOTA:** Columnar/LSM engines apply delta + dictionary + RLE + bit-packing (Parquet/ORC, Apache Arrow), and lakehouse time-travel (Iceberg/Delta) stores per-snapshot manifests with file-level reuse. SQL:2011 system-versioned tables (MariaDB, Db2, SQL Server) keep history tables compressed by the engine's generic page compression — *not* temporally aware. Research prototypes (e.g. Immortal DB, SAP HANA history) and chunk/zonemap-pruned columnar stores give the best deployed random-access-under-compression today.

## 4. Upper Bound
For **transaction-time** histories: space $O(m)$ in the number of updates $m$ with $O(\log_b m)$ block-access per as-of query (MVBT / partial persistence) — optimal in the external-memory / pointer-machine model. With generic columnar coding, empirical compression of 5–20× is typical at the cost of block-granular decompression. For **bitemporal**: best provable bound is roughly $O(m)$ space and $O(\log m)$ access via 2-D persistent / multiversion structures, but **no encoding is known to simultaneously hit the information-theoretic (entropy) lower bound *and* $O(1)$/$O(\log)$ random version access** in the bitemporal plane — that is precisely the empirically-open part.

## 5. Lower Bound
Information-theoretic: any encoding uses at least $H(\text{update stream})$ bits; temporal locality lowers but does not eliminate this. **Cell-probe** lower bounds for supporting fast access on compressed/succinct representations (Pătrașcu–Thorup; Pătrașcu, *Succincter*) give redundancy–query-time trade-offs: you cannot have both near-entropy space and $O(1)$ probes for general predecessor/point-location, implying an unavoidable tension between maximal compression and constant-time version access. Planar **point location** under updates carries $\Omega(\log n / \log\log n)$ cell-probe lower bounds, lower-bounding bitemporal as-of point queries on any small-redundancy encoding.

## 6. The Gap
The asymptotic *access* side is closed for transaction-time-only (persistence is optimal). What is **empirically open** is the joint optimum for the **bitemporal** case: the gap between (a) generic columnar compression that achieves great ratios but block-granular access, and (b) persistent/multiversion indexes that give log-time access but near-zero compression of value redundancy. No construction provably matches entropy *and* the cell-probe access lower bound in 2-D, and on real workloads the best ratio-vs-latency frontier is determined experimentally, not by a tight theorem. Closing it needs an encoding unifying succinct rank/select with multiversion 2-D point location.

## 7. Current Research (as of June 2026)
Active: (i) **learned / model-based compression** of versioned columns (learned indexes, learned bit-packing) pushing the rate–access frontier; (ii) lakehouse time-travel optimization — manifest pruning, file-level dedup, and "compaction without losing time travel" in Iceberg/Delta/Hudi; (iii) succinct multiversion structures combining wavelet trees / FM-index ideas with persistence. *(frontier — verify)* Recent prototypes report bitemporal histories compressed near columnar ratios while keeping sub-millisecond as-of point access by layering a learned model over delta-of-delta encodings and zonemaps. Groups: Lomet (persistence/Immortal DB lineage), Jensen/Saltenis (Aalborg, bitemporal indexing), Kraska/learned-systems (MIT), columnar-engine teams (DuckDB, ClickHouse, Velox).

## 8. Future Work
- An encoding provably matching the **entropy bound and the cell-probe access lower bound** in the bitemporal plane.
- Workload-adaptive (learned) rate–latency frontiers with guarantees, not just benchmarks.
- Compaction that preserves *complete* time-travel while reclaiming redundancy.
- Hardware-aware (SIMD/GPU) random-access decompression of temporal deltas.

## 9. Key References
- **[Foundational]** Driscoll, J., Sarnak, N., Sleator, D., Tarjan, R. *Making Data Structures Persistent.* JCSS, 1989. — [DOI](https://doi.org/10.1016/0022-0000(89)90034-2)
- **[Foundational]** Becker, B., Gschwind, S., Ohler, T., Seeger, B., Widmayer, P. *An Asymptotically Optimal Multiversion B-Tree.* VLDB Journal, 1996. — [DOI](https://doi.org/10.1007/s007780050028)
- **[Foundational]** Lomet, D., Salzberg, B. *The Performance of a Multiversion Access Method (TSB-tree).* SIGMOD, 1990. — [DOI](https://doi.org/10.1145/93605.98744)
- **[SOTA]** Salzberg, B., Tsotras, V. *Comparison of Access Methods for Time-Evolving Data.* ACM Computing Surveys, 1999. — [DOI](https://doi.org/10.1145/319806.319816)
- **[Foundational]** Pătrașcu, M. *Succincter.* FOCS, 2008. (succinct redundancy / cell-probe trade-offs) — [DOI](https://doi.org/10.1109/FOCS.2008.83)
- **[SOTA]** Kraska, T., Beutel, A., Chi, E., Dean, J., Polyzotis, N. *The Case for Learned Index Structures.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196909) · [arXiv](https://arxiv.org/abs/1712.01208)

## 10. Worked Example

Take a transaction-time history of one attribute over 8 versions:
$\langle 7,7,7,7,9,9,9,12\rangle$. Naive per-version storage costs $8$ values. Delta-of-delta /
run-length encoding stores only the *change points*: $(v_0{=}7),(v_4{:}+2),(v_7{:}+3)$ — three
records. Compression ratio $8/3\approx 2.7\times$, and the empirical entropy is low because
$H(\text{state}_t\mid\text{state}_{t-1})$ is near zero on the long constant runs.

But now answer "value as-of version $\tau=6$?" A pure delta chain must replay from $v_0$:
$7\xrightarrow{}7\xrightarrow{}9$ — up to $O(m)$ steps for $m$ changes. The succinct fix stores the
change *positions* in a rank/select bitvector $B=10001001$ (a 1 at each change point). Then
$\text{rank}_1(6)=2$ gives "2 changes occurred at or before 6", indexing directly into the value
array $[7,9,12]$ to return $9$ in $O(1)$ probes — matching the Pătrașcu redundancy/probe trade-off:
near-entropy space *with* fast access. The bitemporal case repeats this per valid-time stripe,
turning the 1-D rank/select into 2-D point location.

---
*Part of the [DBMS Research catalog](../../README.md).*
