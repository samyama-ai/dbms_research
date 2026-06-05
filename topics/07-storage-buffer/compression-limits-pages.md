# Information-Theoretic Limits of Page Compression

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/compression-limits-pages` · **Status:** partially-solved

## 1. Problem Statement

A database page (typically 4-64 KB) must support **random access**: the system reads/updates an arbitrary tuple or value without decompressing the whole page. We ask for the **information-theoretic and cell-probe limits of compressing a page while preserving sub-page random access.** Concretely: encode a sequence of $n$ values (a column chunk, a set of tuples) drawn from a distribution or with empirical entropy $H$, into $\le S$ bits, such that (a) $S$ approaches the entropy lower bound, and (b) any single element can be recovered (rank/select/access) in $O(1)$ or $O(\log)$ probes.

**Variants.** *Decision:* can $n$ elements with entropy-per-element $H_0$ be stored in $nH_0 + r$ bits supporting $O(1)$ access for a given redundancy $r$? *Optimization:* minimize redundancy $r$ for a fixed access-probe budget $t$ — the **redundancy–query tradeoff**. *Counting:* how many distinct page contents share a code length (relevant to dictionary sizing). The non-trivial constraint is the *random-access* one: pure entropy coding (arithmetic/ANS) hits $H$ but destroys $O(1)$ access; the science is how much extra space ("redundancy") random access forces.

## 2. Mathematical Foundations

Let a page hold $n$ symbols with order-$0$ empirical entropy $H_0$ (or order-$k$ entropy $H_k$). The **succinct data structures** framework asks for space $nH_k(S) + o(n)$ bits with constant-time `access/rank/select`. Key results:

- **Entropy floor:** Shannon's source coding theorem gives $\ge nH_0$ bits to represent the data; any structure uses at least this minus negligible terms.
- **Redundancy lower bounds (cell-probe model):** Gál–Miltersen and Pătrașcu–Viola show that supporting `rank`/`select`/membership with $t$ probes forces redundancy $r = \Omega(n / (\lg n)^{O(t)})$ — you *cannot* simultaneously have zero redundancy and $O(1)$ probes. Pătrașcu's *succincter* (FOCS'08) gives the matching upper side via "spillover" encoding.
- **AGM-style is irrelevant here; the relevant machinery is the cell-probe model, Kolmogorov/empirical entropy, and the FID (fully-indexable dictionary) lower bounds (Golynski).**

Formally the frontier is the **space–probe tradeoff curve** $r(t)$, partly characterized but not fully tight for all operation mixes.

## 3. State of the Art (SOTA)

**Theory-SOTA:** *succinct/compressed* structures achieving $nH_k + o(n)$ bits with $O(1)$ access: RRR bitvectors (Raman–Raman–Rao, SODA'02), wavelet trees (Grossi–Gupta–Vitter, SODA'03), and Pătrașcu's *succincter* (FOCS'08) which nails the redundancy for several primitives. **Systems-SOTA:** column stores use lightweight, random-access-friendly schemes — dictionary + bit-packing, RLE, frame-of-reference, FastPFor / **roaring bitmaps** — trading some entropy for SIMD-decodable random access. Modern engines (DuckDB, Velox, Parquet/ORC v2, BtrBlocks VLDB'23) pick per-block schemes; learned compression (e.g., **CorBit / learned FOR**, and **LeCo** SIGMOD'23) push toward entropy while keeping $O(1)$ access. Apple/academic *vortex* and *FSST* (string compression, VLDB'20) give random-access string codes.

## 4. Upper Bound

For order-$k$ compression with constant-time `access/rank/select`, the upper bound is $nH_k + o(n)$ bits (RRR, wavelet trees, succincter). For string dictionaries, **FSST** (VLDB'20) gives near-entropy random-access decode at $\sim$GB/s. The redundancy–probe upper bound is $r = O(n / (\lg n)^{t})$ achievable with $t$ probes (succincter / spillover), matching the lower bound up to constants for membership/rank. In the *systems* model (block-decodable, SIMD), BtrBlocks/LeCo achieve within a small constant of $H_0$ while preserving vectorized random access; these are empirical, not provably optimal.

## 5. Lower Bound

The **cell-probe lower bounds** are the crux and they are real and matching for several operations:

- Pătrașcu–Viola (and Gál–Miltersen, "the cell probe complexity of succinct data structures," ICALP'03) prove that any data structure storing $n$ bits and answering `rank` in $t$ cell probes needs redundancy $r = \Omega(n/(\lg n)^{O(t)})$; hence $O(1)$-probe rank cannot achieve $o(n/\text{polylog})$ redundancy.
- Golynski's lower bounds for `select`/permutation representations show inherent space–time tension.
- Shannon entropy is the hard information floor: no random-access scheme beats $nH_0$ in expectation.

These establish that **zero-redundancy, constant-probe random access is impossible** — the "partially solved" status: the tradeoff is characterized for rank/select/access, but not for richer query mixes (predicate pushdown, range, approximate).

## 6. The Gap

For the canonical `access/rank/select` operations the gap is **essentially closed** (matching cell-probe bounds, hence the *partially-solved* status). What remains open: (1) the tradeoff for **richer operations** actually used in query engines — range predicates, late-materialized filters, approximate membership — where tight lower bounds are unknown; (2) bridging the **theory–systems gap**: succinct structures are $O(1)$-probe but slow constants; systems schemes are fast but lack proven near-entropy optimality with random access; no result says BtrBlocks-style block coding is within a constant of the cell-probe optimum *under SIMD/block constraints*. (3) Compression under **updates** (dynamic succinct structures) widens the gap further.

## 7. Current Research (as of June 2026)

- **Learned and hybrid compression** (LeCo, BtrBlocks lineage; TUM, CWI/DuckDB Labs) optimizing the entropy/random-access frontier on real columns *(frontier — verify)*.
- **Hardware-conscious succinctness:** GPU/SIMD-decodable codes with provable redundancy bounds; closing the theory–systems gap *(frontier — verify)*.
- **Compressed execution:** operating directly on compressed pages (predicate pushdown into the code) to make the random-access constraint pay off, not just storage savings.
- Dynamic/updatable succinct dictionaries for in-memory column stores.

## 8. Future Work

- Tight cell-probe bounds for range and predicate operations on compressed pages.
- Provable near-entropy guarantees for SIMD-block-decodable formats (formalize the systems model).
- Compression that co-optimizes with the buffer cache (compressed-cache capacity vs. decode cost).
- Entropy limits under page-level encryption and integrity (ECC/MAC overhead interacts with redundancy).

## 9. Key References

- **[Foundational]** Claude E. Shannon. *A Mathematical Theory of Communication.* Bell System Technical Journal, 1948.
- **[Foundational]** Rajeev Raman, Venkatesh Raman, S. Srinivasa Rao. *Succinct Indexable Dictionaries with Applications to Encoding k-ary Trees and Multisets.* SODA, 2002.
- **[SOTA]** Mihai Pătrașcu. *Succincter.* FOCS, 2008.
- **[Lower Bound]** Anna Gál, Peter Bro Miltersen. *The Cell Probe Complexity of Succinct Data Structures.* ICALP, 2003.
- **[SOTA]** Peter Boncz, Thomas Neumann, Viktor Leis. *FSST: Fast Random Access String Compression.* VLDB, 2020.
- **[SOTA]** Maximilian Kuschewski, David Sauerwein, Adnan Alhomssi, Viktor Leis. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD, 2023.
- **[Survey]** Gonzalo Navarro. *Compact Data Structures: A Practical Approach.* Cambridge University Press, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*