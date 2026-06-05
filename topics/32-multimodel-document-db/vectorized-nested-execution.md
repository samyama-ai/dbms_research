# Vectorized execution over nested arrays

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/vectorized-nested-execution` · **Status:** empirically-open

## 1. Problem Statement
Modern analytical engines get their speed from **vectorized, columnar** execution: operators process batches of values in tight, branch-light, SIMD-friendly loops over contiguous arrays. Nested data (arrays of structs, arrays of arrays, optional fields) resists this: **unnesting** (`UNNEST`/`FLATTEN`), **lateral joins**, and **array operators** (map/filter/aggregate over arrays, `array_contains`, positional access) introduce variable-length, ragged structure that breaks the fixed-stride assumptions of vectorization.

- **Algorithmic variant:** design unnest/lateral-join/array-operator algorithms that retain columnar batching and SIMD utilization on ragged data.
- **Layout variant:** choose encodings (Dremel repetition/definition levels, offset/length arrays, Arrow nested layout) that make these operators vectorizable.
- **Cost/optimization variant:** plan when to materialize unnested forms vs. operate in nested form.

## 2. Mathematical Foundations
The data model is **nested relational algebra (NRA)** with $\mathsf{unnest}$, $\mathsf{nest}$, and lateral application; ordered arrays add positional semantics. Physical representation: Dremel's **repetition/definition levels** encode tree structure in flat columns; equivalently, **offset arrays** (CSR-like ragged layout) used by Apache Arrow's `List`/`Struct` types. Vectorization theory rests on the **vectorized/Volcano-batch model** (Boncz–Zukowski–Nes, MonetDB/X100) where per-tuple interpretation overhead is amortized across a batch; the analysis is about **instructions-per-tuple** and memory-bandwidth bounds (roofline model), not classical asymptotic complexity. Lateral joins relate to **dependent join** / $\mathsf{apply}$ decorrelation (unnesting subqueries; Neumann–Kemper). SIMD effectiveness is bounded by the **selectivity / branch-divergence** of ragged loops.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **DuckDB** (vectorized, native `LIST`/`STRUCT`, vectorized UNNEST), **Velox** (Meta's vectorized execution library with Arrow-style nested vectors), **Apache Arrow** compute kernels for list/struct, **Photon** (Databricks, vectorized C++ engine handling nested), Snowflake's vectorized VARIANT access, ClickHouse `arrayJoin`/array functions. Dremel/Capacitor and Parquet's nested encoding define the storage SOTA.
- **Theory/technique-SOTA:** the *Unnesting Arbitrary Queries* decorrelation framework (Neumann–Kemper, BTW 2015) makes lateral/dependent joins into ordinary joins amenable to vectorization; MonetDB/X100 (CIDR 2005) established the vectorized model.

## 4. Upper Bound
With offset/length (Arrow) or repetition/definition (Dremel) layouts, **unnest** is a single linear pass that expands $N$ parent rows into $\sum \ell_i$ child rows in $O(N + \sum \ell_i)$ time with sequential memory access — vectorizable at near memory bandwidth. Lateral joins reduce via decorrelation (Neumann–Kemper) to standard hash/merge joins, inheriting their vectorized upper bounds. Array element-wise operators on a flattened values-buffer + offsets achieve full SIMD width when the operation is branch-free. So in the **vectorized RAM/roofline model**, the *bulk* operators are linear-time and bandwidth-bound.

## 5. Lower Bound
There is no asymptotic hardness here — the operators are linear. The real lower bounds are **architectural / fine-grained constants**:
- Ragged arrays force **data-dependent control flow**; gather/scatter and variable-stride access have hard memory-latency floors (cache-miss and TLB bounds), and SIMD efficiency is bounded below by branch divergence proportional to length-variance.
- Deeply/irregularly nested data approaches a **pointer-chasing** lower bound (memory-latency-bound, ~$\Omega(\text{depth} \times \text{miss latency})$), which no vectorization removes.
- Output-sensitive operators (lateral join with explosive fan-out) are bounded below by output size $\Omega(\sum \ell_i)$ trivially, but materialization pressure is the practical wall.

## 6. The Gap
"Empirically-open": asymptotics are settled (linear), so the open problem is achieving **flat-relational vectorization efficiency** on nested data in practice. Today, nested operators run several-fold slower per byte than equivalent flat scans because of branch divergence, irregular gathers, and materialization of intermediate unnested forms. No engine consistently hits roofline on lateral joins over deeply nested, length-skewed arrays, and no cost model reliably decides nested-vs-flattened execution. Closing the gap is an engineering-plus-modeling problem: layouts and kernels (and possibly adaptive shredding) that keep SIMD utilization high on ragged data.

## 7. Current Research (as of June 2026)
Velox and DuckDB teams publish ongoing work on vectorized nested kernels and lazy/just-in-time flattening; research into **morsel-driven** parallelism over nested vectors and SIMD-friendly ragged layouts (e.g., bit-packed validity + offset prefetching) is active. *(frontier — verify: specific claims that Velox/Photon now reach near-flat throughput on deeply nested lateral joins.)* Groups: TUM (Neumann/Leis/Kemper), CWI (DuckDB lineage of MonetDB), Meta (Velox), Databricks (Photon).

## 8. Future Work
- SIMD kernels robust to length-skew (segmented/grouped reductions).
- Cost models for nested-vs-flattened plans (ties to *adaptive-shredding*).
- Hardware-aware (GPU/SIMD-width-agnostic) ragged operators.
- Pushdown of array predicates to avoid full unnest materialization.

## 9. Key References
- **[Foundational]** P. Boncz, M. Zukowski, N. Nes. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR, 2005. — [PDF](https://www.cidrdb.org/cidr2005/papers/P19.pdf) · [DBLP](https://dblp.org/rec/conf/cidr/BonczZN05.html)
- **[Foundational]** S. Melnik et al. *Dremel: Interactive Analysis of Web-Scale Datasets.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920886) · [PDF](https://research.google.com/pubs/archive/36632.pdf)
- **[SOTA]** T. Neumann, A. Kemper. *Unnesting Arbitrary Queries.* BTW, 2015. — [PDF](https://cs.emis.de/LNI/Proceedings/Proceedings241/383.pdf) · [DBLP](https://dblp.org/rec/conf/btw/0001K15.html)
- **[SOTA]** P. Pedreira et al. *Velox: Meta's Unified Execution Engine.* VLDB, 2022. — [DOI](https://doi.org/10.14778/3554821.3554829) · [PDF](https://www.vldb.org/pvldb/vol15/p3372-pedreira.pdf)
- **[SOTA]** M. Raasveldt, H. Mühleisen. *DuckDB: an Embeddable Analytical Database.* SIGMOD (demo), 2019. — [PDF](https://hannes.muehleisen.org/publications/SIGMOD2019-demo-duckdb.pdf) · [DOI](https://doi.org/10.1145/3299869.3320212)
- **[Foundational]** V. Leis, P. Boncz, A. Kemper, T. Neumann. *Morsel-Driven Parallelism.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2610507) · [PDF](https://db.in.tum.de/~leis/papers/morsels.pdf)

## 10. Worked Example

Three parent rows with a nested `tags` array, stored Arrow-style as a flat **values** buffer plus an **offsets** array:

```
values  = [ x, y, z, w, p ]          // 5 child elements
offsets = [ 0, 2, 2, 5 ]             // row i spans values[offsets[i] : offsets[i+1]]
```

Row 0 has `[x,y]` ($\ell_0=2$), row 1 has `[]` ($\ell_1=0$), row 2 has `[z,w,p]` ($\ell_2=3$).

`UNNEST(tags)` is one linear pass: emit each child paired with its parent id, producing $\sum_i \ell_i = 2+0+3 = 5$ output rows in $O(N + \sum\ell_i) = O(3+5)$ time, reading both buffers sequentially — bandwidth-bound, no per-tuple branching.

The lower-bound wrinkle: row 1 is empty, rows 0 and 2 differ in length. A SIMD kernel processing fixed lanes of, say, width 4 cannot align cleanly to these ragged segments — the length variance forces a *gather* with data-dependent strides and a partially filled final lane. So while the asymptotics stay linear, achieved SIMD utilization on this tiny skewed input is well below 100%, illustrating exactly the "flat-relational efficiency on ragged data" gap of Section 6.

---
*Part of the [DBMS Research catalog](../../README.md).*
