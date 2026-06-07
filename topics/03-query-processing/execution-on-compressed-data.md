---
id: 03-query-processing/execution-on-compressed-data
title: "Query execution over compressed data"
topic: 03-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Query execution over compressed data

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/execution-on-compressed-data` · **Status:** partially-solved

## 1. Problem Statement

Execute relational operators — filters, joins, grouped aggregation, and sorting —
**directly on encoded or compressed columns**, decompressing as little as possible (ideally
never fully). The goal is to turn compression from a pure storage/IO win into a *compute*
win: less data touched per operator, more values per SIMD register, and predicates resolved
on codes rather than materialized values.

Formally: given a column stored under an encoding scheme $E$ (dictionary, run-length,
bit-packing/FOR, delta, FSST string codes, or a general byte-oriented compressor), and an
operator $\theta$, produce an operator $\theta_E$ that computes $\theta$ on the encoded
representation with output either encoded or materialized, such that
$\text{cost}(\theta_E) < \text{cost}(\text{decode} \to \theta)$.

- **Pushdown variant:** rewrite a predicate $p$ as a predicate $p'$ on codes (e.g.
  dictionary-encoded equality becomes code equality) — exact and lossless.
- **Operate-on-encoded variant:** perform joins/aggregation where keys never leave their
  compressed domain (e.g. RLE runs aggregated by run length).
- **Optimization variant:** choose, per column/operator, the encoding that minimizes total
  query cost across a workload (encoding selection).

It is **partially solved**: lightweight encodings (dictionary, RLE, FOR, bit-packing)
admit well-understood direct execution; general entropy-coded/heavyweight compression and
joins across *mismatched* dictionaries remain open.

## 2. Mathematical Foundations

Let a column $C$ of $n$ values be encoded as $E(C)$ of size $|E(C)| = H \le n\log|\Sigma|$
bits, where $H$ relates to the empirical entropy of the value distribution. An operator is
**encoding-transparent** if there is a homomorphism

$$\theta_E\big(E(C)\big) \;=\; E\big(\theta(C)\big)\quad\text{or}\quad \theta(C) = D\big(\theta_E(E(C))\big),$$

with $D$ the decoder. Order-preserving dictionary encodings give a monotone map
$\phi:\Sigma\to\mathbb{Z}$, so range predicates and sort commute with $\phi$ — enabling
sort/merge-join on codes. RLE turns aggregation into a **weighted reduction**: $\sum$ over a
run of value $v$ with length $\ell$ is $\ell\cdot v$, collapsing $\ell$ tuples to $O(1)$
work, so RLE aggregation cost is $O(\\#\text{runs})$ not $O(n)$ — a provable sublinear win
when runs are long. The information-theoretic frame: any operator that produces $k$ bits of
output must read $\Omega(k)$ bits, but compression lets the *input* side shrink toward $H$,
so encoded execution can approach $\Theta(H + \text{output})$ work — the **compressed-input
lower bound**. Joins across two columns with *different* dictionaries require a code
translation map; with order-preserving dictionaries this is monotone and cheap, otherwise
it costs $O(|\Sigma|)$ to build a remap.

## 3. State of the Art (SOTA)

- **Foundational:** **Abadi, Madden, Ferreira**, *Integrating Compression and Execution in
  Column-Oriented Database Systems* (SIGMOD 2006) is the seminal result: operating on
  compressed C-Store data (RLE, bit-vector, dictionary) yields large speedups, and many
  operators run without decompression.
- **Systems SOTA:** **DuckDB**, **Velox**, **Apache Arrow/Parquet**, and **Vertica**
  push dictionary/RLE/FOR predicates down to encoded data; **SAP HANA** and **Vectorwise**
  operate on dictionary codes throughout. **FSST** (Boncz, Neumann, Leis, VLDB 2020) gives
  random-access string compression that supports comparison on codes.
- **BtrBlocks** (Kuschewski et al., SIGMOD 2023) and **Lightweight compression** surveys
  (Damme et al., 2017/2019) characterize the encoding-vs-execution design space and SIMD
  decoding throughput. **Tile-based / vectorized** engines decode lazily per chunk.

## 4. Upper Bound

For lightweight encodings the upper bounds are strong and tight to within constants:
- **Dictionary predicate pushdown:** $O(|\Sigma|)$ to translate a predicate to a code set,
  then equality/range filtering at $O(n)$ over $\lceil \log|\Sigma|\rceil$-bit codes — more
  values per SIMD lane, a constant-factor speedup proportional to the packing ratio.
- **RLE aggregation:** $O(r)$ for $r$ runs, i.e. $O(n)$ worst case but $O(H)$-flavored when
  $r \ll n$.
- **Sort/merge-join under order-preserving dictionary:** asymptotically identical to plain
  sort/merge ($O(n\log n)$) but on narrower codes.

The aspirational upper bound — execution in $\Theta(H + |\text{output}|)$ for *general*
compressors — is achieved only for specific schemes; no general operator library attains it.

## 5. Lower Bound

- **Compressed-input floor:** any operator must read enough to determine its output; for
  selective filters this is $\Omega(\text{output} + \text{index probes})$, and encoded
  execution cannot beat the entropy $H$ of the relevant columns — an information-theoretic
  bound.
- **Heavyweight-compression obstruction:** for entropy coders (Huffman/ANS/LZ), random
  access to the $i$-th value is not $O(1)$ without auxiliary structure; computing a general
  predicate may require $\Omega(H)$ sequential decode, so "operate without decompression" is
  *provably impossible in general* for adaptive/streaming codes — a structural lower bound
  in the **pointer-machine / bit-probe** sense.
- Joins across non-order-preserving dictionaries inherit set-intersection lower bounds:
  reconciling two code spaces is $\Omega(|\Sigma|)$ work in the comparison model.

## 6. The Gap

For lightweight encodings, upper and lower bounds essentially coincide — the problem is
*solved* there and the remaining work is engineering (SIMD kernels, vectorized decode). The
genuine gap is for **heavyweight/general compression**: we cannot operate on entropy-coded
data without $\Omega(H)$ decode, so there is a real impossibility separating cheap encodings
from strong ones. Bridging it requires either (a) new *computation-friendly* compressed
formats that retain random access and operator homomorphisms near the entropy bound, or (b)
cost models that pick, per column/operator, the encoding on the right point of the
compression-vs-computability frontier. Cross-dictionary joins are the other open frontier.

## 7. Current Research (as of June 2026)

- **CWI/TU Munich (Boncz, Neumann, Leis, Kuschewski)** — BtrBlocks, FSST, and successors
  targeting compute-friendly, randomly-accessible compressed formats *(frontier — verify)*.
- **Damme / TU Dresden** lightweight-compression and *MorphStore* — operating on compressed
  intermediates and recompressing between operators.
- **Learned / cascade encodings** that compose schemes per column with a cost-based selector
  are an active 2025–2026 direction *(frontier — verify)*.
- **Compressed execution on accelerators** (GPU/FPGA decode fused into operators) and
  format unification across Arrow/Parquet/Lance *(frontier — verify)*.

## 8. Future Work

- A general theory of *encoding-transparent operators* characterizing which operators admit
  homomorphic execution under which encodings.
- Computation-friendly near-entropy formats with $O(1)$ random access and predicate support.
- Workload-aware encoding selection with provable cost guarantees.
- Joins/aggregation across heterogeneous dictionaries without full re-dictionarization.

## 9. Key References

- **[Foundational]** D. Abadi, S. Madden, M. Ferreira. *Integrating Compression and Execution in Column-Oriented Database Systems.* SIGMOD, 2006. — [DOI](https://doi.org/10.1145/1142473.1142548)
- **[Foundational]** D. Abadi, S. Madden, N. Hachem. *Column-Stores vs. Row-Stores: How Different Are They Really?* SIGMOD, 2008. — [DOI](https://doi.org/10.1145/1376616.1376712)
- **[SOTA]** P. Boncz, T. Neumann, V. Leis. *FSST: Fast Random Access String Compression.* PVLDB 13(11), 2020. — [DBLP](https://dblp.org/rec/journals/pvldb/Boncz0L20.html)
- **[SOTA]** M. Kuschewski, D. Sauerwein, A. Alhomssi, V. Leis. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3589263)
- **[Survey]** P. Damme, A. Ungethüm, J. Hildebrandt, D. Habich, W. Lehner. *From a Comprehensive Experimental Survey to a Cost-based Selection Strategy for Lightweight Integer Compression Algorithms.* ACM TODS, 2019. — [DOI](https://doi.org/10.1145/3323991)
- **[Foundational]** M. Zukowski, S. Héman, N. Nes, P. Boncz. *Super-Scalar RAM-CPU Cache Compression.* ICDE, 2006. — [DOI](https://doi.org/10.1109/ICDE.2006.150)

## 10. Worked Example

Take a column of $n = 12$ status values, RLE-encoded as (value, run-length) pairs:

$$[(\text{`A'},5),\ (\text{`B'},3),\ (\text{`A'},4)] .$$

**Query:** `SELECT status, COUNT(*) GROUP BY status`.

Naive plan: decode to 12 tuples, then count — $O(n) = 12$ units of work.

Encoded plan: aggregate run lengths directly. `A` $\to 5 + 4 = 9$, `B` $\to 3$. This touches
only $r = 3$ runs, so cost is $O(r) = 3$ — a $4\times$ reduction here, and arbitrarily large
when runs are long ($O(r)$ vs. $O(n)$, with $r \ll n$).

Now a **predicate** `WHERE status = 'B'` under a dictionary `{A:0, B:1}`: it rewrites to the
code predicate `code = 1` (cost $O(|\Sigma|)=2$ to translate), then scans narrow 1-bit codes
instead of full strings — more values per SIMD lane and no string materialization. Both
illustrate the "homomorphism" $\theta_E(E(C)) = E(\theta(C))$: the operator runs in the
compressed domain and never fully decodes.

---
*Part of the [DBMS Research catalog](../../README.md).*
