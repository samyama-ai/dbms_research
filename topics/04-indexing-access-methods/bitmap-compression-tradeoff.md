# Bitmap index compression vs. query speed

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/bitmap-compression-tradeoff` · **Status:** partially-solved

## 1. Problem Statement
A bitmap index represents, for each column value, the set of matching row IDs as a bitvector; queries reduce to fast boolean AND/​OR/​NOT over these bitvectors. Compression shrinks sparse/​clustered bitmaps but can destroy the **word-aligned** property that makes boolean ops run at memory bandwidth. The problem: find compression schemes that are **provably (near-)optimal in space** (close to the bitmap's entropy/​gap-encoding bound) while **preserving word-aligned, SIMD-friendly boolean-operation throughput** — ideally with operation cost proportional to *compressed* size.

Variants: (a) minimize space subject to "operate in compressed form at $\Theta(1)$ words/​op-unit"; (b) maximize query throughput subject to a space budget; (c) the *decision* variant: does a scheme exist matching a given (space, AND-time) point? (d) workload-adaptive layout selection.

## 2. Mathematical Foundations
A bitmap of length $N$ with $n$ set bits has information content $\log_2\binom{N}{n}$ bits; *clustered* bitmaps have lower **gap entropy** $\sum_i \log(\text{gap}_i)$. Run-length / word-aligned schemes (WAH, EWAH, Concise, Roaring) trade a constant redundancy per "fill word" for $O(1)$-per-word boolean ops. The key tension: entropy-optimal codes (arithmetic/​Golomb on gaps) are *bit-aligned* and force decode-before-compute, costing $\Omega(n)$ per op; word-aligned codes keep ops at $O(\text{compressed words})$ but spend extra space on alignment.

Formally, for two compressed bitmaps of sizes $c_1,c_2$ words, the AND can be computed in $O(c_1+c_2)$ word operations for run-aligned schemes, versus $O(N/w)$ for raw and $O(n)$ for fully entropy-coded. Roaring's hybrid (array / bitmap / run containers per $2^{16}$ chunk) is provably near-optimal per-container by choosing the min-space representation, giving an *adaptive* point on the trade-off.

## 3. State of the Art (SOTA)
- **WAH** — Wu, Otoo, Shoshani (ACM TODS 2006): word-aligned hybrid, query in compressed form.
- **EWAH / Concise** — Lemire, Kaser, Aouiche (Software P&E 2010); Colantonio–Di Pietro (Concise).
- **Roaring bitmaps** — Chambi, Lemire, Kaser, Godin (Software P&E 2016) + SIMD Roaring (Lemire et al., 2018): the de-facto systems-SOTA, used in Lucene, Druid, Spark, ClickHouse, InfluxDB, etc.
- **Theory-SOTA:** succinct / entropy-bounded bitvector representations (RRR, gap-compressed) with rank/​select, but these optimize membership, not bulk boolean throughput.

## 4. Upper Bound
Roaring: per $2^{16}$-chunk it picks the smaller of array/​bitmap/​run encoding, so space is within a small constant of the per-chunk optimum; AND/​OR run in time proportional to the *sum of compressed container sizes* with SIMD-accelerated container ops. WAH/​EWAH guarantee boolean ops in $O(\text{compressed size})$ words. Thus near-optimal in the "operate in compressed form" model — but with a constant-factor space overhead vs. true gap entropy.

## 5. Lower Bound
Information-theoretic: any representation needs $\ge\log_2\binom{N}{n}$ bits; gap-entropy bounds are lower for clustered data. Lower bounds on **bitvector rank/​select** redundancy (Golynski; Pătraşcu — "succincter") show you cannot have entropy-minimal space *and* $O(1)$ operations without lower-order redundancy. For the *operation* side, computing AND of two sets whose intersection is reported is $\Omega(\text{output} + \text{compressed input})$ trivially; conditional fine-grained lower bounds (e.g., from set-intersection / OV) bound how much faster than scanning the inputs you can intersect in the worst case.

## 6. The Gap
**Partially solved.** Systems schemes (Roaring) are excellent and *empirically* near-optimal, but there is **no proof** that any single word-aligned scheme is *simultaneously* space-optimal (matching gap entropy up to $1+o(1)$) **and** boolean-time-optimal. The gap is the missing tight theorem connecting the chosen container/​alignment to the entropy bound, and a matching lower bound showing the alignment overhead is unavoidable for word-parallel ops.

## 7. Current Research (as of June 2026)
Directions: SIMD/​AVX-512 and GPU Roaring kernels; learned/​workload-adaptive container selection; combining bitmap compression with vectorized query engines (ClickHouse, Velox); "Roaring with run-aware SIMD intersection"; bit-sliced index (BSI) arithmetic for range/​aggregate. *(Frontier — verify)* recent work claims provable near-entropy space with maintained SIMD AND throughput via hybrid bit-sliced + Roaring layouts. Key people: Lemire (TÉLUQ/​Québec) and the Roaring community; LBNL FastBit lineage (Wu).

## 8. Future Work
- A scheme with a *proven* simultaneous space-and-time optimality (or an impossibility separation).
- Tight fine-grained lower bounds for compressed multi-way boolean ops.
- Hardware-co-designed (GPU/​FPGA/​CXL) bitmap operation kernels with guarantees.
- Adaptive schemes that provably track per-block entropy under updates.

## 9. Key References
- **[Foundational]** Wu, Otoo, Shoshani. *Optimizing Bitmap Indices with Efficient Compression (WAH).* ACM TODS, 2006. — [DOI](https://doi.org/10.1145/1132863.1132864)
- **[SOTA]** Chambi, Lemire, Kaser, Godin. *Better Bitmap Performance with Roaring Bitmaps.* Software: Practice & Experience, 2016. — [DOI](https://doi.org/10.1002/spe.2325)
- **[SOTA]** Lemire, Ssi-Yan-Kai, Kaser. *Consistently Faster and Smaller Compressed Bitmaps with Roaring (SIMD).* Software: Practice & Experience, 2016/​2018. — [DOI](https://doi.org/10.1002/spe.2402)
- **[Foundational]** Lemire, Kaser, Aouiche. *Sorting Improves Word-Aligned Bitmap Indexes (EWAH).* Data & Knowledge Engineering, 2010. — [arXiv](https://arxiv.org/abs/0901.3751)

## 10. Worked Example

Index a column over $N = 2^{20}$ rows where value `red` matches just $n = 3$ rows, at positions 5, 6, 7. 

- **Raw bitmap:** $N/w = 2^{20}/64 = 16{,}384$ words — full scan to AND.
- **Entropy bound:** $\log_2\binom{2^{20}}{3} \approx 56$ bits — about 1 word, but a Golomb/arithmetic code is bit-aligned, so an AND must decode first, costing $\Omega(n)$.
- **Roaring:** the single nonzero $2^{16}$-chunk holds positions $\{5,6,7\}$. With only 3 values it picks an **array container** = three 16-bit shorts (6 bytes) rather than an 8 KB bitmap container — adaptively near the per-chunk optimum.

Now AND `red` with `blue` = $\{6,7,8\}$ (also an array container). Roaring intersects two sorted short-arrays in $O(c_1 + c_2) = O(3+3)$ word-ops, yielding $\{6,7\}$ — no decode, no $16{,}384$-word scan. This is the trade-off in miniature: the array container costs $48$ bits vs. the $56$-bit entropy floor (a small constant overhead) while keeping the AND at $\Theta(\text{compressed size})$, which the bit-aligned entropy code cannot.

---
*Part of the [DBMS Research catalog](../../README.md).*
