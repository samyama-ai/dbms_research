---
id: 13-column-stores-olap/open-columnar-format-design
title: "Cloud-Native Open Columnar Formats"
topic: 13-column-stores-olap
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Cloud-Native Open Columnar Formats

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/open-columnar-format-design` · **Status:** open

## 1. Problem Statement
Design an open, on-disk/object-store columnar file format — a successor to Parquet/ORC/Arrow — co-designed for (a) **object storage** (high-latency, range-GET-billed, throughput-oriented blob stores like S3), (b) **wide and nested schemas** (thousands of columns, deeply nested/semi-structured fields), and (c) **predicate and projection pushdown** (skip data without decoding). Variants:

- **Layout/optimization:** given a workload distribution, choose row-group size, column chunking, encoding, and metadata placement to minimize bytes scanned and GET requests.
- **Decision (skipping):** given a predicate, decide which pages/row-groups to read using zone maps / statistics / indexes embedded in the file — minimizing false positives.
- **Encoding selection:** per-column encoding+compression that maximizes decode throughput per byte (see also `optimal-encoding-selection`).

The problem is open because no single format yet jointly optimizes object-store I/O patterns, wide-schema metadata cost, fast random access, and lightweight encodings amenable to SIMD/vectorized decode.

## 2. Mathematical Foundations
Cost on object storage is dominated by **request count and latency**, not just bytes: reading $r$ ranges costs $\approx r\cdot(\ell + s/B_{\text{net}})$ where $\ell$ is per-GET latency, $s$ the bytes, $B_{\text{net}}$ throughput. Good formats minimize $r$ (coalesce ranges) and maximize **data skipping**: with per-block statistics (min/max, null counts, sketches), the expected fraction read under predicate $P$ is the probability a block's value range intersects $P$ — minimized by **clustering/sorting** that reduces value-range overlap (a min-skew / small-spread objective). 

Wide-schema metadata is itself a scaling problem: a footer listing statistics for $C$ columns × $G$ row-groups is $\Theta(CG)$; for $C=10^4$ this footer can dominate small files, motivating **lazy/columnar metadata**. Encodings exploit source entropy: dictionary, run-length, FOR/delta, bit-packing approach the per-column empirical entropy $H$ while keeping decode **branch-free and vectorizable**. Nested data uses Dremel **repetition/definition levels** to shred trees into flat columns losslessly.

## 3. State of the Art (SOTA)
- **Format-SOTA:** Apache Parquet and ORC (row-groups + footer stats + page-level encodings); Apache Arrow (in-memory + Arrow IPC/Feather). These are the incumbents but predate object storage at scale.
- **Next-gen (2023–2026):** **Lance** (columnar for ML/random access), **Nimble** (Meta, formerly Alpha — wide-schema, modular encodings), **Vortex** (Spiral — cascading lightweight encodings + late materialization), **BtrBlocks** (Kuschewski et al., SIGMOD 2023 — automatic cascade of lightweight encodings tuned for decompression speed), and **FastLanes** (Afroozeh & Boncz, VLDB 2023 — SIMD-friendly bit-packing/encoding layout). The "format wars" paper (Zeng, Pavlo, Zhang et al., VLDB 2023) benchmarks Parquet/ORC and exposes their object-store and wide-schema weaknesses.

## 4. Upper Bound
With ideal clustering and per-block statistics, data read approaches the **information-theoretic minimum**: only blocks overlapping the predicate, i.e. $O(\text{selectivity}\cdot n)$ bytes plus metadata. Lightweight cascaded encodings (BtrBlocks, FastLanes) reach within a small factor of general-purpose compressors (zstd) on size while decoding at multiple GB/s/core — near memory bandwidth — by staying branch-free and SIMD-parallel. Request count can be driven to $O(\\#\text{relevant column-chunks})$ via range coalescing. These are practical, model-as-roofline upper bounds, not proven optima.

## 5. Lower Bound
Data skipping cannot beat the data: $\Omega(\text{selectivity}\cdot n)$ bytes must be read for an exact scan (information-theoretic). For a *single* physical clustering, predicates on non-sort columns provably suffer overlap — no clustering simultaneously minimizes spread on all columns (a multi-objective impossibility tied to the **min-skew partitioning** hardness; optimal multi-dimensional clustering is NP-hard). Object-store latency $\ell$ imposes an irreducible per-request floor, so formats trade footer size against request count. Compression below per-column entropy $H$ is impossible (Shannon).

## 6. The Gap
This is genuinely **open**: incumbents (Parquet/ORC) were designed for HDFS row-groups, not S3 latency, $10^4$-column schemas, or SIMD decode; the 2023–2026 contenders each optimize a subset (random access, encoding speed, wide schemas) but no standardized format jointly wins, and ecosystem inertia is large. Closing the gap requires a format that is simultaneously (i) object-store-native (few, coalesced GETs; lazy metadata), (ii) wide/nested-schema scalable, (iii) SIMD-decode-fast, (iv) richly skippable — and adopted as an open standard.

## 7. Current Research (as of June 2026)
Active: BtrBlocks/FastLanes encoding cascades (Boncz/CWI, Neumann/TUM lineage); **Vortex** and **Nimble** as modular, extensible encoding frameworks; Parquet v3 / "Parquet++" discussions on bloom filters, page indexes, and variant/semi-structured types; integration with **lakehouse table formats** (Iceberg, Delta) that layer file-skipping metadata above the format. Open questions on adaptive per-column encoding selection (learned), and on a metadata layer that scales to very wide schemas without footer blowup *(frontier — verify)*. Groups: CWI (Boncz, Afroozeh), TUM, MIT DSAIL (Madden, Zeng), Meta/Spiral/LanceDB engineering.

## 8. Future Work
- A standardized, object-store-native open format with lazy columnar metadata for wide schemas.
- Learned/adaptive encoding selection per column and per workload with decode-speed guarantees.
- First-class semi-structured/variant and vector/embedding columns.
- Co-design with table-format skipping indexes (Iceberg/Delta) to avoid redundant statistics.

## 9. Key References
- **[Foundational]** Melnik, Gubarev, Long, Romer, et al. *Dremel: Interactive Analysis of Web-Scale Datasets.* VLDB 2010. — [DOI](https://doi.org/10.14778/1920841.1920886)
- **[SOTA]** Kuschewski, Sauerwein, Alhomssi, Leis. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD 2023. — [DOI](https://doi.org/10.1145/3589263)
- **[SOTA]** Afroozeh, Boncz. *The FastLanes Compression Layout: Decoding >100 Billion Integers per Second with Scalar Code.* VLDB 2023. — [DOI](https://doi.org/10.14778/3598581.3598587)
- **[SOTA]** Zeng, Hui, Shen, Pavlo, McKinney, Zhang. *An Empirical Evaluation of Columnar Storage Formats.* VLDB 2023. — [arXiv](https://arxiv.org/abs/2304.05028)
- **[Foundational]** Abadi, Boncz, Harizopoulos, et al. *The Design and Implementation of Modern Column-Oriented Database Systems.* Foundations and Trends in Databases, 2013. — [DOI](https://doi.org/10.1561/1900000024)

## 10. Worked Example

A file on S3 stores column `temp` in $G=4$ row-groups of $1000$ rows each, with min/max zone maps:

| Row-group | min | max |
|-----------|-----|-----|
| RG0 | 10 | 25 |
| RG1 | 22 | 40 |
| RG2 | 5 | 60 |
| RG3 | 70 | 90 |

Query: `WHERE temp BETWEEN 30 AND 35`. Skipping logic keeps only row-groups whose $[\min,\max]$ intersects $[30,35]$: RG1 ($[22,40]$ ✓) and RG2 ($[5,60]$ ✓); RG0 and RG3 are pruned. So $2/4$ row-groups are read.

Cost on object storage: each surviving group is one coalesced range-GET. With per-GET latency $\ell=20$ ms and bytes negligible, naive read $=4\ell=80$ ms; skipped read $=2\ell=40$ ms.

Notice RG2's wide spread $[5,60]$ forces a read even though few of its rows likely match — this is the **overlap penalty** of poor clustering. Sorting `temp` globally would shrink per-group spread and prune more, but no single sort order helps every column at once (the min-skew multi-dimensional impossibility from §5).

---
*Part of the [DBMS Research catalog](../../README.md).*
