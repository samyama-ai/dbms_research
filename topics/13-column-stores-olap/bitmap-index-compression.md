---
id: 13-column-stores-olap/bitmap-index-compression
title: "Bitmap Index Compression Tradeoffs"
topic: 13-column-stores-olap
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Bitmap Index Compression Tradeoffs

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/bitmap-index-compression` · **Status:** partially-solved

## 1. Problem Statement
A bitmap index over a column with $c$ distinct values represents each value as a bitmap of length $n$ (one bit per row). Queries reduce to bitwise Boolean operations (AND/OR/NOT) and `COUNT` (population count) over these bitmaps. The problem: design a **compressed bitmap encoding** that is simultaneously (a) near space-optimal and (b) fast for AND/OR/COUNT *directly on the compressed form*, across the full range of column cardinality and bit density. Variants:

- **Optimization:** minimize $\alpha\cdot(\text{space}) + \beta\cdot(\text{query time})$ for a workload over sparse, dense, and clustered bitmaps.
- **Decision/membership:** test bit $i$, or whether a range is all-zero (skip), in $O(1)$/sublinear time.
- **Counting:** `COUNT`/rank/select on the compressed bitmap.

It is *partially solved* because excellent encodings exist (Roaring, WAH/EWAH), but no single scheme is provably optimal in both axes for all cardinality regimes, and the space/speed Pareto frontier is not fully characterized.

## 2. Mathematical Foundations
A bitmap of $n$ bits with $k$ set bits has information content $\log_2\binom{n}{k}$ bits; for sparse $k\ll n$ this is $\approx k\log_2(n/k)$, the target for **succinct** representations. The relevant tradeoff is between this **entropy bound** and supporting fast `rank`/`select` and Boolean ops. 

Run-length schemes (WAH/EWAH/PLWAH) align runs to machine words ($w=32/64$) so AND/OR is a word-at-a-time merge: cost $O(\text{compressed-words})$, exploiting **clustering** (sorted data → long runs). Roaring partitions the universe into $2^{16}$ chunks, each stored as one of {array, bitmap, run} container depending on density — an instance-adaptive choice giving near-optimal space per chunk and SIMD-friendly ops. `COUNT` uses hardware `popcount`. Boolean algebra over bitmaps is exact (no false positives), distinguishing them from Bloom filters. Optimal row ordering to maximize run length (improving WAH) reduces to a **Gray-code / TSP-like** sequencing problem and is NP-hard.

## 3. State of the Art (SOTA)
- **Encoding-SOTA:** **Roaring Bitmaps** (Chambi, Lemire, Kaser, Godin — SPE 2016; Lemire et al.) is the de-facto standard — used in Lucene, Druid, ClickHouse, Spark, InfluxDB; **EWAH**/WAH (Wu, Otoo, Shoshani — the FastBit lineage, ACM TODS 2006) for run-aligned; **PLWAH**, **CONCISE**, **VAL-WAH** as refinements.
- **Systems-SOTA:** Apache Druid, Pilosa/Molecula, FastBit, and column stores use Roaring for inverted/bitmap indexes; binning, range, and interval encodings (Sinha & Winslett) handle high-cardinality and range predicates.
- **Theory:** succinct rank/select structures (RRR — Raman, Raman, Rao; Pătraşcu) give $nH_0 + o(n)$ space with $O(1)$ rank/select.

## 4. Upper Bound
Roaring stores each $2^{16}$ chunk in $\le 2^{16}$ bits and switches container type, so total space is within a small constant of $\sum_{\text{chunks}}\min(\text{dense},\text{sparse})$ cost; AND/OR/COUNT run in $O(\\#\text{containers} + \text{output})$ with SIMD, often faster than uncompressed for sparse data. RRR-style succinct bitmaps achieve $nH_0(B) + o(n)$ bits with **$O(1)$** rank/select in the word-RAM model — essentially the entropy-optimal space with constant-time access. WAH/EWAH give $O(\text{compressed size})$ Boolean ops, optimal in the word-aligned model.

## 5. Lower Bound
Space is bounded below by $\log_2\binom{n}{k} \approx k\log(n/k)$ bits (information-theoretic); no exact encoding beats this. In the **cell-probe model**, supporting `rank`/`select` with $nH_0 + r$ redundancy forces $\Omega(\log n / \log(r/n))$-type tradeoffs (Pătraşcu–Viola; Pătraşcu–Thorup) — you cannot have both minimal redundancy *and* constant time below a threshold. Optimal **row-reordering** to minimize WAH-compressed size is NP-hard (reduction from Hamiltonian-path/TSP), so the most-compressible layout is intractable to find exactly. Boolean-op time is $\Omega(\text{output size})$.

## 6. The Gap
The space axis is essentially closed (entropy + succinct theory). The **remaining gap is the joint frontier**: (i) no encoding provably dominates Roaring across all cardinality/clustering regimes for *both* space and op-speed; (ii) the cell-probe space/time tradeoff for compressed bitmaps with fast Boolean ops (not just rank/select) is not tight; (iii) optimal row-ordering is NP-hard, so practical compressibility relies on heuristics with no approximation guarantee. Hence "partially solved."

## 7. Current Research (as of June 2026)
Active: SIMD/AVX-512 and GPU Roaring operations; bitmap indexes for high-cardinality and range/multidimensional predicates (sliced/interval encodings); hybrid bitmap + sketch indexes; learned binning to maximize run length; integration with columnar zone maps for two-level skipping. Frontier: a *cardinality-adaptive encoding with proven space-and-time near-optimality across the whole density spectrum* and *approximation algorithms for the row-ordering compaction problem* remain open *(frontier — verify)*. Groups: Lemire (UQAM/Roaring community), the FastBit/LBNL lineage, Druid/ClickHouse/Pilosa engineering, succinct-structures theorists (Navarro, Pătraşcu lineage).

## 8. Future Work
- A provably Pareto-optimal, cardinality-adaptive bitmap encoding for space and Boolean-op speed.
- Approximation algorithms (with ratio guarantees) for compressibility-maximizing row ordering.
- Tight cell-probe bounds for compressed bitmaps under AND/OR/COUNT (not only rank/select).
- Bitmap indexes co-designed with GPU/SIMD and with updates (compressed, mutable bitmaps).

## 9. Key References
- **[SOTA]** Chambi, Lemire, Kaser, Godin. *Better Bitmap Performance with Roaring Bitmaps.* Software: Practice and Experience, 2016. — [DOI](https://doi.org/10.1002/spe.2325)
- **[Foundational]** Wu, Otoo, Shoshani. *Optimizing Bitmap Indices with Efficient Compression.* ACM TODS, 2006 (WAH/FastBit). — [DOI](https://doi.org/10.1145/1132863.1132864)
- **[SOTA]** Lemire, Kaser, Kurz, Deri, et al. *Roaring Bitmaps: Implementation of an Optimized Software Library.* Software: Practice and Experience, 2018. — [arXiv](https://arxiv.org/abs/1709.07821)
- **[Foundational]** Raman, Raman, Rao. *Succinct Indexable Dictionaries with Applications.* ACM TALG, 2007 (RRR). — [DOI](https://doi.org/10.1145/1290672.1290680)
- **[Foundational]** Pătraşcu. *Succincter.* FOCS 2008. — [PDF](https://people.csail.mit.edu/mip/papers/succinct/succinct.pdf)

## 10. Worked Example

Take the bitmap for value `region='US'` over $n=128$ rows where only rows $3$ and $70$ qualify: $k=2$ set bits.

**Entropy bound:** $\log_2\binom{128}{2}=\log_2 8128 \approx 13$ bits — the floor for any exact encoding.

**Uncompressed:** $128$ bits.

**WAH ($w=32$):** the bitmap splits into four 31-bit literal words. Rows $3$ and $70$ fall in different words, so two words are all-zero (run-encoded as one fill word each) and two are literals — roughly $4\times32=128$ bits, *no* gain because the set bits break the runs. WAH wins only on long clustered runs.

**Roaring:** one $2^{16}$ chunk holds all rows; with just $2$ set bits it picks the **array container**, storing two 16-bit values $=32$ bits plus small overhead — far below uncompressed and near the entropy floor.

`COUNT` is then a $\texttt{popcount}$ (or array length $=2$); an AND with another sparse bitmap intersects two short sorted arrays in $O(k)$. This illustrates the central tradeoff: container choice adapts to density, so no single scheme dominates across all $k/n$ regimes.

---
*Part of the [DBMS Research catalog](../../README.md).*
