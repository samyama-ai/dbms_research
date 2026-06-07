---
id: 29-hardware-conscious-db/simd-compression-codecs
title: "SIMD-friendly compression codecs"
topic: 29-hardware-conscious-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# SIMD-friendly compression codecs

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/simd-compression-codecs` · **Status:** partially-solved

## 1. Problem Statement

Columnar engines want compression that is **decodable at memory bandwidth using vector (SIMD) instructions** while keeping the **compression ratio** high. These goals trade off: entropy coders (arithmetic, ANS, Huffman) compress best but decode with serial, data-dependent control flow that resists vectorization; lightweight schemes (bit-packing, frame-of-reference, RLE, dictionary, delta) vectorize beautifully but compress worse. The problem: design codecs (and codec *cascades*) that sit on the **Pareto frontier** of (decode throughput in bytes/sec under SIMD) versus (compression ratio), ideally decoding at $\ge$ DRAM bandwidth so scans stay bandwidth-bound (see *bandwidth-bound-scan*).

Variants: (i) **decode-throughput-bounded** — maximize ratio s.t. SIMD decode $\ge \beta$; (ii) **ratio-bounded** — maximize decode throughput s.t. ratio $\ge r$; (iii) **random-access** — support decoding an arbitrary value/range without full-block scan (selection pushdown); (iv) **type-specific** — integers vs strings vs floats vs nested.

## 2. Mathematical Foundations

Lossless compression is bounded by **Shannon source entropy**: a column with empirical per-value entropy $H$ bits cannot be coded below $\approx NH$ bits, so ratio $\le b/H$ for $b$-bit raw values; codecs trade closeness-to-$H$ against decode cost. The **SIMD decode model** counts vector instructions per output element: a codec is "bandwidth-decodable" if it emits $W$ values per few vector ops with no data-dependent branches, giving throughput $\Theta(W \cdot f / \text{ops})$ that can exceed $\beta$. **Frame-of-reference + bit-packing** decodes via vector shifts/masks (branch-free, $O(1)$ vector ops per word). **ANS** (Duda) approaches entropy with table lookups but has a serial state dependency that limits SIMD parallelism unless *interleaved* into $k$ independent streams (raising lanes at a small ratio cost). The **cascade** view (FastLanes, BtrBlocks) composes reversible transforms $T_k\circ\cdots\circ T_1$ each individually vectorizable; choosing the cascade per column is a combinatorial search over a transform DAG. Random access uses **vectorized bit-unpacking** with per-block headers; supporting $O(1)$ value access lower-bounds metadata overhead.

## 3. State of the Art (SOTA)

- **Lightweight SIMD integer codecs:** **SIMD-BP128 / FastPFor / StreamVByte** (Lemire, Boytsov — SPE 2015) decode billions of integers/sec via AVX. **FastLanes** (Afroozeh & Boncz, VLDB 2023) achieves >100B integers/sec with a transposed layout decodable by scalar *and* SIMD code.
- **Cascaded columnar:** **BtrBlocks** (TUM, SIGMOD 2023) auto-selects encoding cascades per column for data-lake formats; **BtrBlocks/Parquet/ORC** dictionary+RLE+delta stacks are standard.
- **Entropy at speed:** **ANS / FSE** (Duda; Collet's zstd/FSE) and interleaved-rANS give near-entropy ratios with SIMD-friendly multi-stream decode. Why *partially-solved*: integers are essentially solved (bandwidth decode at strong ratios); strings, floats, and near-entropy-at-bandwidth remain open.

## 4. Upper Bound

The **ratio upper bound** is entropy: $\le b/H$, approached by ANS/arithmetic to within a fraction of a bit/symbol. The **throughput upper bound** is set by SIMD width and the roofline; FastLanes-style bit-unpacking decodes well above DRAM bandwidth for fixed-width integers (so the scan, not the decoder, becomes the bottleneck) *(frontier — verify exact rates)*. Multi-stream interleaved rANS decodes near entropy at multiple GB/s. Thus for integers the Pareto frontier is largely characterized; the achievable frontier for strings/floats is the open quantity.

## 5. Lower Bound

The **information-theoretic lower bound** (Shannon/Kraft) caps ratio at entropy $H$; no codec decodes losslessly below $NH$ bits, and approaching $H$ to within $\epsilon$ bits/symbol forces either large tables or serial state that costs SIMD parallelism — a *concrete tension*, though not a proven asymptotic separation. For **random access**, supporting $O(1)$-time value retrieval requires $\Omega$(succinct-index) redundancy: **succinct data structure** lower bounds (e.g., for rank/select, Pătraşcu; Golynski) imply that strong compression *plus* fast random access pays an unavoidable lower-order space overhead. There is no NP-hardness; the binding limits are information-theoretic and cell-probe (for the indexed/random-access variant). The decode-throughput vs ratio frontier itself has no proven closed form for general sources.

## 6. The Gap

For **fixed-width and lightly-skewed integers**, the gap is essentially **closed**: SIMD codecs decode above bandwidth at near-best lightweight ratios — hence *partially-solved*. The genuinely open parts: (i) **near-entropy ratios at memory bandwidth** for skewed data (interleaved ANS narrows but does not eliminate the ratio cost of parallel decode); (ii) **strings, floats, and nested types**, which lack a clean SIMD-decodable near-entropy codec; (iii) **random-access** codecs that hit the succinct-index lower bound while staying SIMD-decodable. Closing these needs new transform cascades and parallel entropy coders proven to approach both Shannon and roofline simultaneously.

## 7. Current Research (as of June 2026)

- SIMD-decodable string/float cascades extending FastLanes/BtrBlocks *(frontier — verify)*.
- Interleaved/SIMD rANS variants narrowing the parallel-entropy ratio penalty *(frontier — verify)*.
- Learned/auto-tuned cascade selection per column under a decode-throughput constraint.
- GPU and hardware (FPGA/ASIC) decoders changing the throughput frontier.
- Groups: CWI (Boncz, Afroozeh), TUM (Leis, Kuschewski), Lemire (lightweight SIMD codecs), zstd/FSE community (Collet, Duda).

## 8. Future Work

- A near-entropy, SIMD-decodable codec at DRAM bandwidth for skewed integer/string data.
- Provable characterization of the decode-throughput vs ratio Pareto frontier.
- Random-access codecs meeting succinct lower bounds with vectorized rank/select.
- Co-design of codec with scan kernel and pushdown (predicate evaluation on compressed data).

## 9. Key References

- **[Foundational]** Shannon, C. E. *A Mathematical Theory of Communication.* Bell System Technical Journal, 1948. — [DOI](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x)
- **[Foundational]** Duda, J. *Asymmetric Numeral Systems (ANS).* arXiv:1311.2540, 2013. — [arXiv](https://arxiv.org/abs/1311.2540)
- **[SOTA]** Lemire, D., Boytsov, L. *Decoding Billions of Integers per Second through Vectorization (SIMD-BP128/FastPFor).* Software: Practice and Experience, 2015. — [DOI](https://doi.org/10.1002/spe.2203)
- **[SOTA]** Afroozeh, A., Boncz, P. *The FastLanes Compression Layout.* VLDB, 2023. — [DOI](https://doi.org/10.14778/3598581.3598587)
- **[SOTA]** Kuschewski, M., Sauerwein, D., Alhomssi, A., Leis, V. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3589263)
- **[Foundational]** Abadi, D., Madden, S., Ferreira, M. *Integrating Compression and Execution in Column-Oriented Database Systems.* SIGMOD, 2006. — [DOI](https://doi.org/10.1145/1142473.1142548)

## 10. Worked Example

Column of 32-bit integers, all in $[1000, 1063]$ — e.g. timestamps offset from an epoch. Raw size $b = 32$ bits/value.

*Frame-of-reference + bit-packing.* Subtract the frame $1000$; residuals lie in $[0,63]$, needing $\lceil\log_2 64\rceil = 6$ bits each. Compression ratio $= 32/6 \approx 5.3\times$. Decode is branch-free: load a 192-bit word holding $32$ packed 6-bit values, then a fixed sequence of SIMD shift + mask + add(frame) ops emits a full vector — no data-dependent control flow. On AVX-512 (16 lanes) this sustains well above DRAM bandwidth, so a scan stays bandwidth-bound (the decoder is not the bottleneck).

*Entropy comparison.* Suppose the residuals are skewed with empirical entropy $H = 3.0$ bits/value. Shannon caps ratio at $b/H = 32/3 \approx 10.7\times$ — about $2\times$ better than the $5.3\times$ of bit-packing. An entropy coder (rANS) approaches it but its single serial state dependency stalls SIMD lanes. The fix: interleave $k=8$ independent rANS streams so 8 lanes advance in parallel, recovering most throughput at a small ratio cost (per-stream flush overhead).

This is the Pareto tension of Section 6: bit-packing gives $5.3\times$ at $>$bandwidth decode; near-entropy $10.7\times$ costs parallelism unless interleaved — and for skewed/non-integer data no codec yet hits *both* Shannon and roofline simultaneously.

---
*Part of the [DBMS Research catalog](../../README.md).*
