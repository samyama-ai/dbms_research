# Memory-bandwidth-bound scan optimization

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/bandwidth-bound-scan` · **Status:** empirically-open

## 1. Problem Statement

A columnar scan with predicate evaluation, decompression, and aggregation *should* be limited only by how fast the machine can stream bytes from DRAM — the **memory-bandwidth roofline**. In practice many scan kernels are instead **compute-bound** (too many instructions per byte: branchy predicates, scalar decompression) or **latency-bound** (cache/TLB misses, dependent loads, branch mispredicts), leaving DRAM bandwidth underutilized. The problem: **design scan kernels and data layouts that saturate memory bandwidth** — i.e., reach the roofline where time $\approx \text{BytesRead}/\beta$ — while still doing decompression, predicate filtering, and aggregation, across selectivities and data distributions.

Variants: (i) **kernel design** — vectorized, branch-free predicate + decode reaching $\le$ a few instructions/byte so compute never dominates; (ii) **layout** — block/encoding choices (run-length, bit-packing, dictionary) that keep decode SIMD-friendly; (iii) **selectivity-adaptive** — selective predicates should read *less* (skip via zone maps), turning a bandwidth problem into an I/O-avoidance one; (iv) **multi-core scaling** — many cores sharing one memory controller hit an *aggregate* bandwidth wall.

## 2. Mathematical Foundations

The governing model is the **roofline** (Williams–Waterman–Patterson): for a kernel with operational intensity $I$ (flops or useful ops per byte), attainable performance is $\min(\pi,\ \beta I)$. A scan is bandwidth-bound iff $I < \pi/\beta$ (the ridge point). The design goal is to push $I$ *below* the ridge by *reducing instructions per byte* (vectorization, branch elimination) so that $\beta$ binds, while not increasing bytes read. Bytes read is governed by the **compression ratio** $\kappa$: a column of $N$ logical values at $b$ bits compresses to $\approx \kappa^{-1} N b /8$ bytes, so scan time $\ge \kappa^{-1} N b /(8\beta)$ — *better compression directly lowers the roofline floor*, the key lever. Latency-bound behavior is captured by **Little's Law**: sustaining $\beta$ needs $\approx \beta L/(\text{line size})$ outstanding misses (memory-level parallelism), so sequential, prefetchable access patterns are required. Branch misprediction cost is modeled by predicate selectivity $\sigma$: branch-free predicate evaluation removes the $\sigma(1-\sigma)$ misprediction penalty, trading branches for always-executed SIMD masks.

## 3. State of the Art (SOTA)

- **Systems:** **MonetDB/X100 (Vectorwise)** (Boncz, Zukowski, Manegold — CIDR 2005) established vectorized, cache-conscious bandwidth-aware scans. **DuckDB**, **Velox** (Meta), **Apache Arrow** compute, **ClickHouse**, and **HyPer/Umbra** (TUM) implement SIMD scan kernels. **BtrBlocks** (TUM, SIGMOD 2023) and **FastLanes** (Afroozeh & Boncz, 2023) target SIMD-decodable encodings at bandwidth.
- **Techniques:** branch-free predicate evaluation with SIMD masks (Lang et al.), late-materialization, SIMD bit-unpacking, zone maps / min-max skipping, and NUMA-aware partitioning. AVX-512 / SVE / NEON vectorization is standard. The empirical gap is that *combined* decode+filter+aggregate still falls short of roofline on many real columns.

## 4. Upper Bound

The roofline gives the **upper bound on performance** (lower bound on time): $T \ge \kappa^{-1} N b /(8\beta)$ for reading the compressed column, and no scan can beat single-DRAM-channel $\beta$ (or aggregate $\beta$ across channels). Best kernels (FastLanes-style unpacking, branch-free predicates) reportedly hit a large fraction of per-core and aggregate bandwidth on integer/dictionary columns *(frontier — verify utilization figures)*. With heavy skipping (zone maps, bloom/range filters), selective scans read $\ll N$ bytes and beat the full-scan roofline by avoiding I/O entirely — an orthogonal, data-dependent win.

## 5. Lower Bound

There is **no nontrivial unconditional complexity lower bound**; the binding lower bound is **information-theoretic / roofline**: to evaluate a predicate over a column you must read enough bytes to determine each qualifying row, $\ge$ the compressed size minus what skipping provably elides, so time $\ge \text{BytesActuallyNeeded}/\beta$. Compression is itself bounded by **source entropy** (Shannon): a column with empirical entropy $H$ bits/value cannot be stored below $\approx NH/8$ bytes losslessly, lower-bounding bytes read and hence scan time. On the kernel side, an adversarial data distribution (e.g., predicate selectivity $\sigma=1/2$ with random layout) forces either branch mispredictions or always-on mask compute, so *some* instruction overhead per byte is unavoidable — but this does not push the kernel above the bandwidth roofline for well-vectorized code. The "open" status is empirical: the gap between achieved and roofline throughput on real workloads.

## 6. The Gap

The gap is between **achieved scan throughput and the roofline**, and it is **closed for simple integer/dictionary columns with light predicates** (state-of-the-art kernels saturate bandwidth) but **open for the combined decode + complex-predicate + aggregate pipeline** on string/nested/heavily-encoded data, where instruction overhead or latency-bound decode keeps kernels below roofline. Closing it requires SIMD-decodable encodings for strings/nested types, branch-free fused decode-filter-aggregate kernels, and layouts maximizing memory-level parallelism — plus an aggregate-bandwidth model for many-core contention.

## 7. Current Research (as of June 2026)

- FastLanes / BtrBlocks-style fully SIMD-decodable cascaded encodings extended to strings and floats *(frontier — verify)*.
- Fused decode–filter–aggregate kernels generated by query compilers (Umbra, Velox codegen).
- Aggregate-bandwidth-aware scheduling for many-core scans hitting the shared memory-controller wall.
- GPU and CXL-memory scan kernels where bandwidth modeling is first-order.
- Groups: TUM (Neumann, Boncz/CWI collaborations), CWI (Boncz/Afroozeh), Meta Velox, DuckDB Labs.

## 8. Future Work

- SIMD-decodable encodings for strings/nested/floating types retaining strong ratios.
- A predictive model mapping encoding + predicate + hardware to achieved bandwidth fraction.
- Branch-free fused pipelines that stay bandwidth-bound across all selectivities.
- Many-core / NUMA / CXL aggregate-bandwidth saturation strategies.

## 9. Key References

- **[Foundational]** Boncz, P., Zukowski, M., Nes, N. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR, 2005. — [DBLP](https://dblp.org/rec/conf/cidr/BonczZN05.html) · [PDF](https://www.cidrdb.org/cidr2005/papers/P19.pdf)
- **[Foundational]** Williams, S., Waterman, A., Patterson, D. *Roofline: An Insightful Visual Performance Model.* CACM, 2009. — [DOI](https://doi.org/10.1145/1498765.1498785)
- **[SOTA]** Lang, H., Mühlbauer, T., Funke, F., Boncz, P., Neumann, T., Kemper, A. *Data Blocks: Hybrid OLTP and OLAP on Compressed Storage.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2882925)
- **[SOTA]** Kuschewski, M., Sauerwein, D., Alhomssi, A., Leis, V. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3589263)
- **[SOTA]** Afroozeh, A., Boncz, P. *The FastLanes Compression Layout: Decoding >100 Billion Integers per Second with Scalar Code.* VLDB, 2023. — [DOI](https://doi.org/10.14778/3598581.3598587)

## 10. Worked Example

Scan a column of $N = 10^9$ 32-bit integers, dictionary-encoded to $b = 10$ bits/value (1024 distinct keys), evaluating predicate `x = 42`. Compressed size: $\kappa^{-1} N b / 8 = 10^9 \cdot 10 / 8 = 1.25$ GB. On a core with single-channel $\beta = 20$ GB/s, the roofline floor is

$$T \ge \frac{1.25\text{ GB}}{20\text{ GB/s}} = 62.5\text{ ms}.$$

To stay bandwidth-bound the kernel must do few instructions per byte. The ridge point of the roofline sits at operational intensity $I^\star = \pi/\beta$; with scalar peak $\pi = 4$ Gops/s, $I^\star = 4/20 = 0.2$ ops/byte. A *branchy* predicate doing $\sim 3$ ops/value over $10/8 = 1.25$ bytes/value gives $I = 3/1.25 = 2.4$ ops/byte $\gg I^\star$ — compute-bound, so the scan runs at $\pi$-limited $10^9 \cdot 3 / 4\text{e9} = 750$ ms, $12\times$ slower than the floor.

Switching to a **branch-free SIMD mask** (one compare + one mask-store, auto-vectorized 8-wide) drops effective ops/byte below $I^\star$, so $\beta$ binds and we approach 62.5 ms. Finally, with a **zone map** marking that 90% of blocks never contain key 42, we skip them and read only $0.125$ GB $\Rightarrow$ $\approx 6.25$ ms — beating the full-scan roofline entirely by avoiding I/O.

---
*Part of the [DBMS Research catalog](../../README.md).*
