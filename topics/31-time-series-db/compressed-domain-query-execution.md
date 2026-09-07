---
id: 31-time-series-db/compressed-domain-query-execution
title: "Compression-aware query execution"
topic: 31-time-series-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Compression-aware query execution

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/compressed-domain-query-execution` · **Status:** partially-solved

## 1. Problem Statement

Given time-series data stored in compressed blocks (RLE, dictionary, FOR, bit-packing, delta, Gorilla/XOR), evaluate queries — selection/filters, aggregates (SUM, COUNT, MIN/MAX, AVG, quantiles), and joins — **directly over the compressed representation**, decoding as little as possible (ideally nothing for whole-block-resolvable predicates).

Variants:
- **Filter pushdown:** decide per block whether it can be skipped (zone maps / min-max), fully accepted, or must be partially scanned.
- **Aggregate-in-compressed-domain:** compute aggregates from codec metadata (e.g. SUM over RLE = $\sum v_k \cdot \text{run}_k$) without materializing points.
- **Join/group-by over encoded keys:** operate on dictionary codes rather than decoded values.

Goal: minimize decoded bytes and CPU, ideally achieving cost proportional to **output / surviving data**, not input size.

## 2. Mathematical Foundations

A codec defines a decode map $D: \text{compressed} \to \text{values}$. A query operator $\mathcal{O}$ is **compression-aware** if there exists $\mathcal{O}'$ with $\mathcal{O}(D(c)) = \mathcal{O}'(c)$ (exact) computable more cheaply than $\mathcal{O}\circ D$. This is a **homomorphism** condition: the codec's algebraic structure must commute with the operator.

- **RLE & dictionary** are homomorphic for COUNT/SUM/GROUP-BY: aggregation distributes over runs/codes. Formally, SUM is a semiring homomorphism over the run-length monoid.
- **FOR / delta** preserve order partially: MIN/MAX and range predicates reduce to comparisons on (reference + offset), exact without full decode.
- **Order-preserving dictionary encoding** lets range predicates run on codes.
- **XOR/Gorilla** is *not* homomorphic for value predicates (XOR destroys magnitude order) — only sequential decode helps; this marks a fundamental limit.

The general design question is which (codec, operator) pairs admit an exact or $\varepsilon$-approximate $\mathcal{O}'$, and the speedup is bounded by the **compression ratio** for fully homomorphic pairs. SIMD vectorization (operate on packed lanes) is the systems realization.

## 3. State of the Art (SOTA)

- **Foundational:** **C-Store / Vertica** (Stonebraker et al., VLDB 2005) and **Abadi et al., "Integrating Compression and Execution in Column-Oriented Database Systems"** (SIGMOD 2006) — the seminal statement that operators should run on compressed data; classifies codecs by whether operators can act directly.
- **Systems-SOTA:** **MonetDB/X100–Vectorwise** vectorized execution; **DuckDB** compressed-vector execution; **ClickHouse** skip indexes + codec pipelines; TSDBs **Apache IoTDB**, **InfluxDB IOx (Arrow/Parquet)**, **TimescaleDB** compressed chunks with batch decompression and predicate pushdown; **FastLanes** (CWI) decode-friendly layouts enabling SIMD predicate evaluation.
- **Partially-solved:** homomorphic operators for RLE/dictionary/FOR are well understood and deployed; XOR-class and lossy codecs largely still require decode.

## 4. Upper Bound

For homomorphic (codec, aggregate) pairs, query cost is $O(\text{compressed size})$ — a speedup equal to the compression ratio, with exact results. Zone-map/min-max pruning yields cost proportional to surviving blocks plus metadata, i.e. **output-sensitive** for selective filters. SIMD bit-unpacking gives constant-factor wins even when decode is needed. These are the best-known and are essentially tight for the pairs that admit homomorphism.

## 5. Lower Bound

- **Codec-imposed:** for non-homomorphic codecs (XOR/Gorilla, arbitrary entropy coding), any exact value-predicate or magnitude aggregate provably requires decoding the affected block — $\Omega(\text{block size})$ work; XOR's destruction of order is the obstruction.
- **Information-theoretic / cell-probe:** answering range/aggregate queries over compressed arrays touches lower bounds from **succinct data structures** — e.g., rank/select and range-sum on compressed sequences face cell-probe time–space tradeoffs (Pătraşcu-style $\Omega(\log n / \log(t \cdot w))$). Achieving both near-entropy space *and* sublinear query is constrained.
- No general method makes an arbitrary codec homomorphic for an arbitrary operator without auxiliary indexing.

## 6. The Gap

Closed for the "nice" pairs (RLE/dictionary/FOR with SUM/COUNT/MIN/MAX/range). Genuinely open/partial: (1) compressed-domain execution for **XOR/Gorilla and lossy** codecs (currently decode-bound); (2) **joins and complex aggregates** (quantiles, distinct) over compressed keys with output-sensitive guarantees; (3) co-designing codecs *for* queryability (succinct-structure-backed) that hit near-entropy space with sublinear query — the cell-probe tradeoff frontier.

## 7. Current Research (as of June 2026)

- Query-aware / decode-light codec layouts (FastLanes, ALP) enabling SIMD predicate evaluation without scalar decode *(frontier — verify)*.
- Succinct/wavelet-tree-backed time-series stores for compressed-domain range aggregates.
- Lossy compressed-domain execution with error propagation (ties to lossy-with-guarantees problem).
- Groups: CWI (Boncz), TUM (Neumann), DuckDB Labs, Apache IoTDB/Arrow communities.

## 8. Future Work

- Operator algebra characterizing exactly which (codec, query) pairs are homomorphic or $\varepsilon$-homomorphic.
- Compressed-domain joins and quantiles with provable bounds.
- Codecs co-designed with succinct indexes for near-entropy space and sublinear queries.

## 9. Key References

- **[Foundational]** D. Abadi, S. Madden, M. Ferreira. *Integrating Compression and Execution in Column-Oriented Database Systems.* SIGMOD, 2006. — [DOI](https://doi.org/10.1145/1142473.1142548)
- **[Foundational]** M. Stonebraker et al. *C-Store: A Column-oriented DBMS.* VLDB, 2005. — [DBLP](https://dblp.org/rec/conf/vldb/StonebrakerABCCFLLMOORTZ05.html)
- **[SOTA]** P. Boncz, M. Zukowski, N. Nes. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR, 2005. — [DBLP](https://dblp.org/rec/conf/cidr/BonczZN05.html)
- **[SOTA]** A. Afroozeh, P. Boncz. *The FastLanes Compression Layout.* VLDB, 2023. — [DOI](https://doi.org/10.14778/3598581.3598587)
- **[Foundational]** G. Navarro. *Compact Data Structures: A Practical Approach.* Cambridge University Press, 2016. — [ACM](https://dl.acm.org/doi/book/10.5555/3092586)

## 10. Worked Example

A 12-row column stored **RLE** as $(value,\ run)$ pairs:

$$(7,4),\ (7,3),\ (12,5)\quad\text{i.e. }7,7,7,7,\ 7,7,7,\ 12,12,12,12,12.$$

Query: `SELECT SUM(x), COUNT(*)`. RLE is homomorphic for SUM/COUNT, so compute directly from the 3 metadata pairs without materializing 12 values:

$$\text{SUM}=\sum_k v_k\cdot \text{run}_k = 7\cdot4 + 7\cdot3 + 12\cdot5 = 28+21+60 = 109,\qquad \text{COUNT}=\sum_k \text{run}_k = 4+3+5 = 12.$$

Cost is $O(\text{compressed size})=3$ operations versus $12$ for full decode — a $4\times$ speedup equal to the compression ratio.

Now contrast a **filter** `WHERE x > 10` on the same column. RLE/FOR keep value magnitude, so the predicate runs on the 3 runs: only $(12,5)$ survives, returning 5 rows, output-sensitive. But if the column were instead **XOR/Gorilla**-encoded, the stored stream is $7\oplus7\oplus12\dots$, where the XOR deltas destroy magnitude order — the operator $\mathcal{O}'$ satisfying $\mathcal{O}(D(c))=\mathcal{O}'(c)$ does not exist, so the predicate forces a full $\Omega(\text{block size})$ sequential decode. This is exactly the homomorphic / non-homomorphic boundary the problem turns on.

---
*Part of the [DBMS Research catalog](../../README.md).*
