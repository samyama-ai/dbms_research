---
id: 20-spatial-databases/spatial-data-lake
title: "Spatial data lakes and serverless query"
topic: 20-spatial-databases
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Spatial data lakes and serverless query

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/spatial-data-lake` · **Status:** empirically-open

## 1. Problem Statement
Spatial datasets (GeoParquet, FlatGeobuf, Zarr, COG rasters, vector tiles) increasingly live as immutable files on **object storage** (S3/GCS/Azure Blob) and are queried by **serverless** engines (AWS Lambda/Athena, DuckDB-WASM, Trino, Spark-on-Lambda). The problem is to support efficient spatial **range, kNN, and join** queries in this setting, where the storage layer is high-latency, immutable, billed per request, and the compute is ephemeral with **cold starts** and no warm shared index.

Concretely: design **indexing and predicate pushdown** for spatial data on object storage such that a query (a) reads as few bytes/objects as possible (data skipping), (b) tolerates and amortizes cold-start latency, and (c) needs no always-on coordinator. Sub-problems: *layout* (how to physically order/partition files for spatial locality), *index residence* (where the spatial index lives when there is no warm node), *pushdown* (what spatial predicates the storage/format can evaluate), and *cost/latency* optimization under a per-request billing model.

## 2. Mathematical Foundations
The core mechanism is **data skipping**: a query with spatial predicate $q$ reads only blocks/files whose **zone map** (min/max bounding box) intersects $q$. Effectiveness depends on **clustering quality** — how well physical layout preserves spatial locality — quantified by **space-filling-curve (SFC)** locality (Hilbert/Z-order): the expected number of contiguous runs a query range maps to, with Hilbert curves giving asymptotically fewer clusters per query box than Z-order. Formally, for an SFC $\phi:\mathbb{R}^2\to[0,1]$, a query box $Q$ induces $C(Q)$ index intervals; minimizing $\mathbb{E}[C(Q)]$ over the workload is the layout objective, bounded below by the curve's intrinsic **clustering number**.

Cost is a **two-level external-memory** problem: with object-store latency $L$ (tens of ms) per GET and bandwidth $B$, query time $\approx (\\#\text{requests})\cdot L + (\text{bytes})/B + \text{cold-start}$. This is the **EM/PDAM** model with an unusually large, request-priced "block" and a fixed cold-start additive term — index designs must minimize *request count*, not just bytes, distinguishing it from classic disk-based R-tree analysis.

## 3. State of the Art (SOTA)
- **Formats:** **GeoParquet** (with per-row-group bbox statistics), FlatGeobuf (embeds a static packed Hilbert R-tree), Cloud-Optimized GeoTIFF and Zarr for rasters; the OGC/Overture ecosystem.
- **Systems-SOTA:** **DuckDB** + `spatial` extension reading remote Parquet with bbox pushdown; **Apache Sedona** on object storage; **Wherobots** (managed Sedona) and **GeoParquet-on-Athena/Trino** deployments; H3/S2 discrete-global-grid keys for partition pruning.
- **Indexing:** static packed Hilbert R-trees serialized alongside data (FlatGeobuf); manifest/metadata-level pruning via table formats (Iceberg/Delta) carrying spatial column statistics; H3/S2 cell-id columns enabling cheap range pruning.

## 4. Upper Bound
- **Range query:** with a static packed Hilbert R-tree of branching $b$ resident in the object, $O(\log_b n + k/b)$ node fetches, each an object-store GET — so request count $\Theta(\log_b n + \text{output blocks})$; byte cost equals overlapping row groups.
- **Pruning effectiveness:** Hilbert-ordered layout yields $\mathbb{E}[C(Q)] = O(\sqrt{|Q|})$ runs for a query of area $|Q|$ on a uniform grid (SFC clustering result), bounding the number of contiguous reads.
- Cold start is an additive $O(1)$ per invocation; batching/coalescing GETs reduces the $L$-multiplied term.

## 5. Lower Bound
- **SFC locality:** no space-filling curve achieves $o(\sqrt{|Q|})$ expected clusters for arbitrary axis-parallel query boxes — a geometric/discrepancy lower bound; **no single linear order preserves 2-D locality perfectly** (a folklore impossibility: any bijection $\mathbb{R}^2\to\mathbb{R}$ distorts some neighborhoods unboundedly).
- **Request/latency floor:** in the external-memory model any range query reporting $k$ items must issue $\Omega(\log_B n + k/B)$ I/Os; with object-store latency this is an $\Omega(L\cdot\log_B n)$ wall-clock floor that **cold-start tolerance cannot remove**, only amortize.
- Communication/cell-probe lower bounds for predecessor/range search transfer to the per-request setting.

## 6. The Gap
The asymptotics (SFC $\Theta(\sqrt{|Q|})$ clustering, $\Theta(\log_B n + k/B)$ I/O) are **understood**, but the regime is *empirically-open*: real performance is dominated by **request latency, cold starts, and billing**, for which there is no accepted cost model or optimizer. Open empirical questions: optimal row-group size vs. request count; whether to embed indexes, store them as side files, or rebuild on the fly per cold invocation; how to push spatial predicates (especially joins and kNN) into stateless serverless workers without a warm coordinator; and how to handle updates on immutable storage (compaction vs. delta files). No system convincingly co-optimizes layout, index residence, pushdown, and cold-start cost.

## 7. Current Research (as of June 2026)
- **Serverless spatial joins/kNN** with index sharing across ephemeral workers; "index-as-a-file" formats and lazy index materialization on cold start *(frontier — verify)*.
- Learned and workload-adaptive layouts (which SFC / partition key) chosen per dataset; H3/S2-keyed pruning combined with bbox zone maps.
- Cost models for per-request-billed object stores feeding query planners. Groups/people: the **DuckDB**/spatial and **Apache Sedona/Wherobots** teams (Jia Yu, Mohamed Sarwat), the GeoParquet/Overture/OGC community, and cloud-DB research on serverless analytics (e.g., Lambada-style query engines).

## 8. Future Work
A principled object-store cost model (latency + request price + cold start) and an optimizer that uses it; update handling on immutable spatial lakes; pushdown of joins/kNN into storage; standardized spatial-data-lake benchmarks across cold/warm regimes.

## 9. Key References
- **[Foundational]** Faloutsos, Roseman. *Fractals for Secondary Key Retrieval (Hilbert/SFC locality).* PODS, 1989. — [ACM](https://dl.acm.org/doi/10.1145/73721.73746)
- **[Foundational]** Aggarwal, Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [ACM](https://dl.acm.org/doi/10.1145/48529.48535)
- **[SOTA]** Yu, Zhang, Sarwat. *Spatial Data Management in Apache Spark: The GeoSpark Perspective.* GeoInformatica, 2019. — [DOI](https://doi.org/10.1007/s10707-018-0330-9)
- **[SOTA]** Müller et al. (OGC). *GeoParquet Specification.* Open Geospatial Consortium / community standard, 2023–2024. — [spec](https://geoparquet.org/) · [GitHub](https://github.com/opengeospatial/geoparquet)
- **[SOTA]** Perron, Castro Fernandez, DeWitt, Madden. *Starling: A Scalable Query Engine on Cloud Functions.* SIGMOD, 2020. — [ACM](https://dl.acm.org/doi/10.1145/3318464.3380609) · [arXiv](https://arxiv.org/abs/1911.11727)

## 10. Worked Example

A GeoParquet file on S3 holds $10^6$ points in $1{,}000$ row groups of $1{,}000$ points each, each carrying a bbox zone map. Object-store latency $L = 30$ ms/GET, bandwidth $B = 100$ MB/s, cold start $= 200$ ms.

**Layout matters.** Query window $Q$ covers $1\%$ of the area.

- *Random order:* the $10{,}000$ matching points are spread across nearly all $1{,}000$ row groups; with bbox pruning few groups can be skipped, so $\approx 900$ GETs. Wall time $\approx 200 + 900\times 30 = 27{,}200$ ms.
- *Hilbert-ordered:* by the SFC clustering bound, the query box maps to $\mathbb{E}[C(Q)] = O(\sqrt{|Q|})$ runs. With area fraction $0.01$, runs $\propto \sqrt{0.01}=0.1$ of the linear extent $\Rightarrow \approx 100$ contiguous row groups, coalesced into, say, $10$ ranged GETs. Wall time $\approx 200 + 10\times 30 = 500$ ms.

The $\approx 50\times$ speedup comes entirely from request count, not bytes read (both touch $\approx 10{,}000$ points $\approx$ same payload) — illustrating why this is a *request-minimizing* external-memory problem, not a byte-minimizing one.

---
*Part of the [DBMS Research catalog](../../README.md).*
