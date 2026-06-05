# Compression of heterogeneous JSON columns

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/json-columnar-compression` · **Status:** empirically-open

## 1. Problem Statement

Given a collection of JSON documents whose structure is **sparse** (most paths absent from most documents), **deeply nested**, and **type-heterogeneous** (the same path holds strings in some documents, ints/objects/null in others), encode it into a **columnar** layout that simultaneously achieves: (i) high compression ratio, (ii) fast vectorized **scan/filter** on individual paths, and (iii) cheap **reconstruction** of whole/partial documents. The tension is that classical columnar shredding (one column per leaf path, à la Dremel/Parquet) explodes the schema, wastes space on definition/repetition metadata for sparse paths, and cannot place type-heterogeneous values in one typed column.

Variants:
- **Encoding (optimization):** choose a shredding + per-column encoding minimizing bytes subject to a scan-latency budget (or minimize a weighted bytes+latency objective).
- **Decision:** does an encoding meeting (ratio $\ge r$, scan $\le \tau$) exist within budget $B$?
- **Layout selection:** assign each path to a physical representation (shredded column, nested type-tagged column, packed "rest" blob) — a combinatorial design problem under a query workload.

## 2. Mathematical Foundations

- **Record shredding / striping:** Dremel's **repetition and definition levels** (Melnik et al., VLDB 2010) losslessly encode nesting and presence; reconstruction is a finite-state machine over levels. The metadata cost per value is $\lceil \log(\text{max-rep}) \rceil + \lceil \log(\text{max-def}) \rceil$ bits — dominant for sparse paths.
- **Information theory:** the achievable ratio is bounded below by the **empirical entropy** of the (path, type, value) distribution; sparse-path presence is a Bernoulli($p$) source compressible to $H(p)$ bits/doc, so dedicated bitmaps beat per-value def-levels when $p$ is small.
- **Type heterogeneity:** a path's values form a *tagged union*; optimal encoding splits by type (a "shredded variant"), each branch a homogeneous column, plus a type-tag column of entropy $H(\text{type-mix})$.
- **Encodings:** dictionary, RLE, FOR/bit-packing, delta, and FSST (string) — each a transform with known ratio/scan tradeoffs; choosing the best per column is the *compression-scheme selection* problem (NP-hard in general as a constrained assignment).
- **Layout = optimization over a path lattice:** the path-presence lattice plus a query workload defines a cost function; selecting a layout is a (submodular-ish) set/partition optimization, related to vertical partitioning (NP-hard).

## 3. State of the Art (SOTA)

- **Systems-SOTA (formats):** Apache **Parquet** (Dremel-derived) and **ORC** for shredded nested data; **Apache Arrow** in-memory; **Spark/BigQuery** shredding. Newer: **Apache (Vortex / Lance / Nimble (Meta Alpha))** and **FastLanes** (Afroozeh–Boncz, VLDB 2023) push vectorized lightweight encodings. **JSONB**/**BSON** are row-major baselines.
- **Heterogeneous-JSON-SOTA:** Snowflake's **VARIANT** with automatic sub-columnarization (Cerebro/“schema-on-read to columnar”) and **Parquet variant / shredded-variant** (the open VARIANT spec, 2024–2025) that materializes frequent typed sub-paths into columns and keeps the rest as a binary blob *(frontier — verify)*. DuckDB JSON, ClickHouse `JSON`/Dynamic type with on-the-fly sub-column extraction, and **SPADE/SQL-Server sparse columns** are systems addressing exactly the sparse/heterogeneous case.
- **Research:** JSON Tiles (Durner–Leis–Neumann, SIGMOD 2021) — automatically infers frequent structure and tiles it into typed columns, leaving rare paths in a fallback — a leading principled result.

## 4. Upper Bound

For *regular, homogeneously-typed* nested data, Dremel-style shredding + lightweight encodings (dictionary/RLE/FOR, FastLanes) approaches empirical entropy with vectorized scans at multi-GB/s — effectively optimal up to encoding overheads. For sparse/heterogeneous data, **JSON Tiles** and **shredded VARIANT** materialize the frequent (path, type) substructure into typed columns (entropy-near, scannable) and pack the long-tail residue into a row blob, achieving compression and scan competitive with hand-tuned schemas while staying schemaless. No encoding is *proven* optimal: layout selection under a workload is the hard part, and the chosen heuristics carry no worst-case ratio guarantee.

## 5. Lower Bound

- **Entropy bound (Shannon):** no lossless encoding beats the empirical entropy $H$ of the (structure, type, value) source — a hard floor; def/rep-level schemes pay a provable overhead above $H$ for sparse paths unless replaced by presence bitmaps.
- **Layout selection is NP-hard:** optimal vertical/columnar partitioning is NP-hard (reduction from partitioning/clustering); choosing the cost-minimal assignment of paths to representations under a workload inherits this — so optimal layout is intractable, only heuristics/approximations are feasible.
- **Compression-scheme selection:** selecting per-column encodings to jointly minimize size and decode cost is a constrained combinatorial optimization with no PTAS known in the general weighted case.
- **Scan vs. ratio tension:** there is an inherent tradeoff — better compression (e.g., entropy coding) raises decode cost; this is an empirical Pareto frontier rather than a single optimum, which is why the problem is **empirically-open**.

## 6. The Gap

The gap is **empirical, not a clean theory gap**. Entropy gives a tight lower bound on size; NP-hardness rules out provably-optimal layout. What's open is *practical*: no method is known to be Pareto-dominant across compression ratio, scan speed, and reconstruction cost for arbitrary sparse/heterogeneous JSON, and there is **no standard benchmark** to even compare them. Closing it means (a) layout-selection algorithms with approximation guarantees under a workload, (b) encodings that beat def/rep-level overhead on extreme sparsity with proven bounds, and (c) a shared benchmark establishing the empirical frontier.

## 7. Current Research (as of June 2026)

- Open **shredded VARIANT** / Parquet-variant standardization and engine support (Spark, DuckDB, Snowflake, Databricks) *(frontier — verify)*.
- Meta **Nimble (Alpha)** and **Vortex/Lance** next-gen formats with adaptive per-stripe encodings and learned layout *(frontier — verify)*.
- Learned/adaptive layout selection that infers tiles from the workload online (Neumann/Leis lineage).
- Groups: TUM (Neumann, Leis, Durner), CWI (Boncz, Afroozeh — FastLanes), Databricks/Snowflake engineering, Meta Velox/Nimble.

## 8. Future Work

- Approximation algorithms (with ratios) for workload-aware JSON layout selection.
- Presence/type-tag encodings provably beating rep/def levels on heavy-tailed sparsity.
- Co-designing the columnar layout with cardinality stats (links to document cardinality estimation).
- A public sparse/heterogeneous-JSON columnar benchmark.

## 9. Key References

- **[Foundational]** Melnik et al. *Dremel: Interactive Analysis of Web-Scale Datasets.* VLDB, 2010.
- **[Foundational]** Abadi, Boncz, Harizopoulos. *The Design and Implementation of Modern Column-Oriented Database Systems.* FnT Databases, 2013.
- **[SOTA]** Durner, Leis, Neumann. *JSON Tiles: Fast Analytics on Semi-Structured Data.* SIGMOD, 2021.
- **[SOTA]** Afroozeh, Boncz. *The FastLanes Compression Layout: Decoding >100 Billion Integers per Second with Scalar Code.* VLDB, 2023.
- **[SOTA]** Zukowski, Heman, Nes, Boncz. *Super-Scalar RAM-CPU Cache Compression.* ICDE, 2006.
- **[Survey]** Boncz, Neumann, Leis. *Compression and analytics over semi-structured/columnar data.* (modern columnar systems overview), 2020–2023.

---
*Part of the [DBMS Research catalog](../../README.md).*
