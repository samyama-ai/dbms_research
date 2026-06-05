# Selection Pushdown into Encoded Scans

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/encoded-predicate-pushdown` · **Status:** partially-solved

## 1. Problem Statement

In a column store, base data lives **encoded**: bit-packed integers, run-length encoding (RLE), frame-of-reference (FOR / FOR-delta), dictionary codes, and bit-/byte-aligned variants. The problem of **selection (predicate) pushdown into encoded scans** is to evaluate predicates — equality, range, IN-lists, conjunctions/disjunctions, even some string predicates — **directly on the compressed representation**, producing a selection vector or bitmap, *without first decoding to plain values*, and to do so with **provable speedups** over decode-then-filter.

Variants:

- **Operate-on-encoded variant:** transform a value predicate $P$ on values into an equivalent predicate $P'$ on codes (possible exactly when the encoding is order-/equality-preserving), so the scan never materializes values.
- **Vectorized/SIMD variant:** evaluate $P'$ on packed words using bit-parallel and SIMD tricks, maximizing values-processed-per-instruction.
- **Skipping-on-encoded variant:** exploit RLE runs and FOR block min/max to skip whole runs/blocks.

The decision question — *which* predicates can be pushed into *which* encodings exactly — is largely understood; the optimization question — the fastest such evaluation per (encoding, predicate, hardware) and the optimal encoding *choice given a predicate* — is partially open.

## 2. Mathematical Foundations

Let an encoding be a (possibly lossy-free) map $E:\mathcal{V}\to\{0,1\}^*$ with decoder $E^{-1}$. Predicate pushdown is exact iff there is $P'$ with $P'(E(v)) = P(v)$ for all $v$. Two structural properties enable this:

- **Order preservation** ($E$ monotone) $\Rightarrow$ range predicates push: $a\le v\le b \iff E(a)\le E(v)\le E(b)$. FOR ($v \mapsto v - \text{base}$) and order-preserving dictionaries are monotone; range pushes directly.
- **Equality preservation** (injectivity) $\Rightarrow$ equality/IN push: $v=c \iff E(v)=E(c)$. All lossless dictionary codes qualify.

**Bit-parallel** evaluation: comparing many sub-word lanes in a $w$-bit word with no cross-lane carry uses Lamport/Knuth "broadword" tricks (SWAR), giving $\Theta(w/b)$ values per instruction for $b$-bit fields. **BitWeaving** (Li & Patel, SIGMOD 2013) formalizes two layouts — *horizontal* (HBP) and *vertical* (VBP, bit-sliced) — and proves comparisons cost $O(b)$ word-ops per group of packed codes producing a result bitmap, i.e. $O(n\cdot b / w)$ total for an $n$-row column with $b$-bit codes — sub-linear in the uncompressed size. RLE turns a predicate over a run of length $\ell$ into $O(1)$ work, an $\ell\times$ speedup. The theoretical frame is the **RAM/word-RAM** model with word size $w$ (e.g., 64) or SIMD width (256/512).

## 3. State of the Art (SOTA)

- **Systems-SOTA:** **BitWeaving/H** and **BitWeaving/V** (Li & Patel, SIGMOD 2013) — predicate evaluation on bit-packed codes producing result bitmaps with early pruning. **ByteSlice** (Feng et al., SIGMOD 2015) — byte-aligned bit-slicing balancing scan speed and lookup. **SIMD-Scan / vectorized predicate evaluation** (Willhalm et al., VLDB 2009) on bit-packed data. Production: **DuckDB**, **Velox**, **Apache Arrow** compute kernels, **ClickHouse**, **Snowflake**, **Photon (Databricks)** push filters into encoded/vectorized scans; **Parquet/ORC** push min/max + dictionary + Bloom predicates.
- **Theory-SOTA:** Broadword/SWAR comparison results and bit-sliced index arithmetic (O'Neil & Quass, SIGMOD 1997, bit-sliced indices) underpin the per-bit cost model.

## 4. Upper Bound

BitWeaving/V evaluates a comparison predicate on $n$ $b$-bit codes in $O(n b / w)$ word operations, with **early stopping** that often examines only the high-order bit-planes — best case $O(n/w)$ when the most-significant plane decides. ByteSlice achieves comparable scan speed with faster random lookups via byte alignment. RLE: predicate over the column costs $O(r)$ where $r$ = number of runs ($r \le n$), an unbounded speedup as runs grow. FOR + block min/max gives $O(1)$ block skip. These are *provable* speedups over the $\Theta(n)$ decode-then-compare baseline in the word-RAM model.

## 5. Lower Bound

Any scan that must report which of $n$ rows satisfy a predicate with non-trivial selectivity must, in the worst case, read $\Omega(n b / w)$ words just to touch every code (a code with no run structure or skip metadata is incompressible w.r.t. the predicate) — so BitWeaving/V is **word-RAM optimal up to the early-stopping constant** for arbitrary data. Predicates that are **not** order/equality-preservable under the encoding (e.g., arbitrary substring `LIKE '%x%'` over whole-value dictionary codes, or arithmetic over RLE that breaks runs) **provably cannot** be pushed exactly and must decode — an information-theoretic obstruction, not a complexity-class one. Conjunction selectivity ordering is essentially a *fine-grained* scheduling problem; adversarial correlations defeat fixed orderings.

## 6. The Gap

**Partially solved.** For the canonical encodings (bit-pack, RLE, FOR, dictionary) and canonical predicates (=, range, IN), pushdown is well-understood and near-optimal in the word-RAM/SIMD model. Open gaps: (1) **cross-encoding cost models** — given a predicate workload, *which* encoding minimizes evaluation cost (ties to the encoding-selection problem); (2) **complex predicate** pushdown (string functions, regex, UDFs, multi-column expressions) over compressed data; (3) hardware-portable optimality across SIMD widths, GPUs, and FPGAs.

## 7. Current Research (as of June 2026)

- **AVX-512 / SVE and GPU** kernels for predicate-on-encoded evaluation in Velox/Photon/DuckDB, and FPGA pushdown in smart storage *(frontier — verify)*.
- Pushing predicates through **FSST**-compressed strings and learned encodings without full decode *(frontier — verify)*.
- Cost-based **encoding-aware predicate planning** that picks evaluation strategy per block based on observed run structure and selectivity.

## 8. Future Work

- A unified cost model selecting (encoding, evaluation strategy, hardware) per predicate with provable competitive ratio.
- Exact or bounded-approx pushdown for richer string/expression predicates over compressed data.
- Adaptive conjunction ordering with guarantees under correlated selectivities.

## 9. Key References

- **[Foundational]** P. O'Neil, D. Quass. *Improved Query Performance with Variant Indexes (bit-sliced indexes).* SIGMOD, 1997.
- **[SOTA]** Y. Li, J. M. Patel. *BitWeaving: Fast Scans for Main Memory Data Processing.* SIGMOD, 2013.
- **[SOTA]** Z. Feng, E. Lo, B. Kao, W. Xu. *ByteSlice: Pushing the Envelope of Main Memory Data Processing with a New Storage Layout.* SIGMOD, 2015.
- **[SOTA]** T. Willhalm et al. *SIMD-Scan: Ultra Fast In-Memory Table Scan Using On-Chip Vector Processing Units.* VLDB, 2009.
- **[Foundational]** D. Abadi, S. Madden, M. Ferreira. *Integrating Compression and Execution in Column-Oriented Database Systems.* SIGMOD, 2006.

---
*Part of the [DBMS Research catalog](../../README.md).*
