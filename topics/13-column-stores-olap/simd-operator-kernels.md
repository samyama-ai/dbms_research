---
id: 13-column-stores-olap/simd-operator-kernels
title: "Optimal SIMD Operator Kernels"
topic: 13-column-stores-olap
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Optimal SIMD Operator Kernels

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/simd-operator-kernels` · **Status:** empirically-open

## 1. Problem Statement
Design implementations of the core analytical operators — **selection/filter, hashing, hash-table probe/build, partitioning, and aggregation/group-by** — that fully exploit wide-SIMD ISAs (AVX2, AVX-512, ARM SVE/NEON) so that throughput approaches the hardware's vector-lane peak.

The difficulty: these operators are **data-dependent and control-flow heavy** (branch on predicate outcome, follow hash chains, scatter to group buckets), whereas SIMD rewards **branch-free, regular, gather/scatter-light** code. The problem:

- **Construction:** for each operator, build a kernel that is *provably data-parallel* (no per-element serial dependence in the inner loop) and **saturates** vector units — i.e., reaches the roofline ceiling.
- **Decision/lower bound:** is there an inherent serial bottleneck (e.g., conflict in scatter, hash collisions) that prevents full lane utilization for a given operator?
- **Portability:** a kernel that is optimal across vector widths and conflict-detection capabilities.

It is **empirically-open**: excellent kernels exist for many operators, but no general theory says which operators *can* saturate wide SIMD and how to derive the optimal kernel.

## 2. Mathematical Foundations
SIMD execution is the **PRAM/data-parallel** model restricted to a fixed lane width $w$ with synchronous lanes. Key primitives and their cost:
- **Selective store / compaction:** turning a predicate bitmask into a packed output. AVX-512 `VCOMPRESS` does this in hardware; pre-AVX-512 requires permutation-table lookups. Cost is $O(n/w)$ vector ops if compaction is free per lane.
- **Gather/scatter:** random access at $w$ lanes per instruction, but throughput degrades with cache misses and **bank/address conflicts**. AVX-512 `VPCONFLICTD` detects colliding scatter indices — central to conflict-serializing aggregation.
- **Hashing:** multiplicative / Murmur-style hashes are branch-free and vectorize directly; the bottleneck is the **probe** (gathers into the table and chain following), whose parallelism is limited by collision structure.
- **Aggregation conflict:** when multiple lanes update the same group, naive scatter loses updates. The number of *distinct conflict classes* per vector determines achievable parallelism — formally a **graph-coloring / load-balancing** bound on lane utilization.

The performance ceiling is the **roofline**: $\text{throughput} \le \min(w \cdot f,\ \text{BW}/\text{bytes-per-tuple})$. A kernel is "optimal" if it reaches it; the open theory is characterizing for *which inputs* the data-dependent serialization (conflicts, branch divergence) keeps it below the ceiling.

## 3. State of the Art (SOTA)
- **Selection:** Polychroniou, Raghavan, Ross (SIGMOD 2015) — *"Rethinking SIMD Vectorization for In-Memory Databases"* — vectorized selection, hash tables, partitioning, sorting with selective stores/gathers.
- **Hashing/joins:** Balkesen, Teubner, Alonso, Özsu (ICDE 2013; VLDBJ) — main-memory hash join, hardware-conscious; Schuh, Chen, Dittrich (SIGMOD 2016) experimental join study; vectorized **partitioned** and **non-partitioned** hash joins.
- **Aggregation:** vectorized group-by with `VPCONFLICTD`-based conflict serialization (Polychroniou & Ross); morsel-driven parallel aggregation (Leis et al.).
- **Systems-SOTA:** ClickHouse, DuckDB, Velox, Photon ship hand-tuned AVX2/AVX-512 kernels; Apache Arrow compute kernels; libraries auto-dispatch by ISA. **xsimd / Google Highway** provide portable SIMD; **Crystal** (GPU) is the SIMT analog.

## 4. Upper Bound
For **branch-free** operators (hashing, arithmetic filters producing a bitmask), kernels achieve the roofline: $O(n/w)$ vector instructions and **near-perfect lane utilization**, demonstrably saturating AVX-512 (Polychroniou et al.). Selective compaction with `VCOMPRESS` is $O(n/w)$. For **hash-table probe**, throughput is upper-bounded by gather throughput and is within a small constant of peak for low load factors. For **aggregation with conflicts**, the achievable upper bound is $O(n/w \cdot \bar{k})$ where $\bar{k}$ is the average per-vector conflict-resolution cost (1 when groups are distinct across lanes).

## 5. Lower Bound
Lower bounds are **microarchitectural / combinatorial**, not complexity-class:
- **Scatter conflict:** if $g$ lanes in a vector target the same group, at least $g$ serialized updates are forced — an $\Omega(\text{max per-vector duplication})$ lower bound on aggregation, so adversarial all-same-key inputs collapse to scalar speed.
- **Gather divergence:** worst-case random gather across DRAM is bandwidth/latency-bound, giving $\Omega(\text{cache-miss latency})$ per lane regardless of $w$.
- **Branch divergence / selectivity:** at ~50% selectivity, mask-based selection still does full-width work, so speedup is bounded below the ideal $w\times$.
These are **instance-dependent** lower bounds; no operator has a clean unconditional sub-roofline lower bound for *all* inputs, which is why the field is empirical.

## 6. The Gap
The gap is between **per-operator, per-ISA hand-tuned optimality** (achieved empirically) and a **general theory** that, given an operator and input distribution, derives the optimal kernel and certifies whether it saturates the vector unit. For branch-free kernels the gap is essentially closed (roofline reached). For **conflict- and divergence-heavy** kernels (aggregation with skew, chained-hash probe), the achievable fraction of peak is governed by data, and no kernel provably dominates across all inputs — adaptivity (skew detection, fallback) is required but lacks guarantees.

## 7. Current Research (as of June 2026)
Directions: **AVX-512 conflict-detection-driven** aggregation and dedup; **SVE/RVV (RISC-V Vector) length-agnostic** kernels portable across widths; auto-vectorization via MLIR vector dialect and ISPC; learned/adaptive dispatch picking a kernel by observed skew and selectivity; GPU SIMT counterparts (Crystal, Proteus). Groups: Columbia (Ross), ETH/TUM (Teubner, Leis, Neumann), CWI/DuckDB, Meta Velox. Frontier: **portable length-agnostic kernels (SVE/RVV) matching hand-tuned AVX-512** *(frontier — verify)*, and FPGA/CXL near-data kernels *(frontier — verify)*.

## 8. Future Work
- A cost-model/theory predicting per-operator saturable fraction of peak as a function of data skew and ISA.
- Provably conflict-optimal vectorized aggregation under arbitrary key distributions.
- Length-agnostic kernels (SVE/RVV) with portability + optimality guarantees.
- Co-design of compression encodings so kernels operate directly on encoded data without decompression.

## 9. Key References
- **[Foundational]** Zhou, Ross. *Implementing Database Operations Using SIMD Instructions.* SIGMOD 2002. — [DOI](https://doi.org/10.1145/564691.564709)
- **[SOTA]** Polychroniou, Raghavan, Ross. *Rethinking SIMD Vectorization for In-Memory Databases.* SIGMOD 2015. — [DOI](https://doi.org/10.1145/2723372.2747645)
- **[SOTA]** Balkesen, Teubner, Alonso, Özsu. *Main-Memory Hash Joins on Multi-Core CPUs: Tuning to the Underlying Hardware.* ICDE 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544839)
- **[SOTA]** Schuh, Chen, Dittrich. *An Experimental Comparison of Thirteen Relational Equi-Joins in Main Memory.* SIGMOD 2016. — [DOI](https://doi.org/10.1145/2882903.2882917)
- **[Survey]** Leis, Boncz, Kemper, Neumann. *Morsel-Driven Parallelism.* SIGMOD 2014. — [DOI](https://doi.org/10.1145/2588555.2610507)

## 10. Worked Example

Consider a SIMD group-by SUM with lane width $w=8$ over keys, accumulating into per-group buckets via scatter.

**Distinct case.** A vector of 8 keys all map to different groups: `[g0,g1,g2,g3,g4,g5,g6,g7]`. The scatter writes 8 buckets in one instruction — no conflict. Throughput $=O(n/w)$, i.e. $\bar k=1$, full $8\times$ lane utilization.

**Conflict case.** A skewed vector `[g0,g0,g0,g0,g1,g1,g2,g3]`: four lanes target $g0$. A naive scatter would lose 3 of the 4 updates (last-writer-wins). `VPCONFLICTD` detects the colliding indices, and the four $g0$ updates must be **serialized** into a prefix-sum within the conflict class. Per-vector cost rises to $\bar k = \max$ duplication $=4$.

**Adversarial case.** All $n$ keys equal $g0$: every update serializes, collapsing the kernel to scalar speed — the $\Omega(\text{max per-vector duplication})$ lower bound of §5. Speedup degrades from $8\times$ (distinct) toward $1\times$, showing why aggregation saturation is *data-dependent* and motivates skew-adaptive fallback.

---
*Part of the [DBMS Research catalog](../../README.md).*
