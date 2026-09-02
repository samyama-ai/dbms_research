---
id: 20-spatial-databases/spatial-join-on-compressed
title: "Spatial joins on compressed/encoded data"
topic: 20-spatial-databases
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-09
last_substantive_update: 2026-09
stale_since: ""
provenance: synthesized
---

# Spatial joins on compressed/encoded data

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/spatial-join-on-compressed` · **Status:** empirically-open

## 1. Problem Statement
Given two collections of geometries $R$ and $S$ stored in a **compressed or encoded** form (delta/varint-coded coordinates, topological/TopoJSON encodings, quantized SFC keys, simplified or progressively-encoded polylines/polygons, columnar geometry blocks, or learned codecs), evaluate a spatial join $R \bowtie_\theta S$ for $\theta \in \{\text{intersects}, \text{contains}, \text{within-}\epsilon, \text{overlaps}\}$ **directly over the compressed representation**, decompressing as little as possible.

Variants:
- **Filter step:** decide candidate pairs (MBR/approximate overlap) entirely in the encoded domain.
- **Refinement step:** evaluate exact topological predicates with partial/progressive decompression.
- **Decision vs. counting:** report pairs vs. count/aggregate join size.
- **Optimization:** minimize total bytes decompressed (I/O + CPU) for a correct result, the true objective.

The challenge: exact geometric predicates need coordinates, but full decompression dominates cost; we want predicate evaluation whose decompression budget scales with the *boundary complexity actually probed*, not with object size.

## 2. Mathematical Foundations
A geometry is a sequence of vertices; compression exploits **spatial autocorrelation** (successive vertices are close) and **shared topology** (adjacent polygons share arcs). Coordinate streams are modeled with entropy $H$; delta+entropy coding approaches $H$ bits/coordinate. Order-preserving / monotone encodings (Z-order, Hilbert keys) let MBR and range predicates be tested on *keys* because the curve is locality-preserving (dilation bound). The refinement step is computational geometry: segment-intersection and point-in-polygon, where **progressive / multiresolution** representations (vertex hierarchies, Douglas–Peucker hierarchies, BBox-trees) permit *conservative* tests at coarse resolution that are exact when a separating/containing certificate is found early. Formally, a join predicate over a *simplified* geometry $\tilde g$ with Hausdorff error $\eta$ yields a **two-sided certificate**: if the simplified test clears a margin $>\eta$ it certifies the exact answer; only ambiguous pairs (within band $\eta$ of the boundary) require deeper decode. Output size obeys the **AGM/intersection** bound; the open quantity is the *decompression complexity* — bytes decoded as a function of join selectivity and boundary ambiguity.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** GEOS/PostGIS use MBR + prepared-geometry refinement but on *decompressed* WKB. Apache Sedona/Parquet-WKB and GeoArrow give columnar layouts; FlatGeobuf and Tiny-WKB reduce decode cost. SpatialParquet and learned/columnar geometry encodings (recent SIGMOD/VLDB 2022–2024) push some filtering into encoded blocks. Raster-side and SFC-key joins (cuSpatial, BEVA-style) operate on quantized keys.
- **Theory-SOTA:** the *compressed/succinct computation* program — operating on compressed strings/grids without decompression (e.g. compressed text indexing, grammar-compressed computation) — provides the template, but spatial-join-specific results are sparse.

## 4. Upper Bound
Filter step on monotone keys: $O((|R|+|S|)\log + K_{\text{cand}})$ with no coordinate decode, only key comparisons. Refinement with multiresolution certificates: expected decode $\propto$ ambiguous-band pairs $\times$ depth, often $\ll$ full decode; worst case still $O(\text{total vertices})$ when boundaries densely interleave. Distance-$\epsilon$ joins admit conservative grid/SFC pruning. No bound provably guarantees *sublinear-in-object-size* decode for adversarial geometries.

## 5. Lower Bound
Exact topological predicates can require $\Omega(\text{boundary vertices})$ in the worst case (two polygons whose relationship is decided only by their finest features), so no method beats full decode on adversarial inputs. Set-intersection / OMv-style and $3$SUM-flavored barriers apply to the *pairing* problem; segment-intersection reporting is $\Omega(n\log n + K)$. These are model-dependent (comparison / fine-grained) and worst-case; they do not preclude strong *data-dependent* (compressed-size-sensitive) bounds.

## 6. The Gap
We have strong heuristics (key-domain filtering, progressive refinement) but **no proven decompression-sensitive complexity** characterizing when joins beat decompress-then-join. The problem is empirically open: systems show large wins on real, redundant data, yet lack guarantees and a clear model relating compression ratio, selectivity, and decode work. Closing it needs (a) join algorithms with bounds in the *bits-decoded* model, and (b) codecs designed jointly with the join (predicate-aware compression).

## 7. Current Research (as of June 2026)
Directions: predicate-pushdown into columnar/encoded geometry (GeoArrow/GeoParquet ecosystems) *(frontier — verify)*; learned and grammar-/topology-aware geometry codecs that expose coarse predicates without full decode *(frontier — verify)*; succinct geometry indexes (wavelet-tree / SFC-key joins) for in-memory analytics; and GPU joins directly over Morton-encoded points. Active groups: Sedona/GeoArrow maintainers, columnar-spatial-storage groups (e.g. work around SpatialParquet), and the succinct-data-structures community (Navarro lineage) bridging to geometry.

A reproducible attack on the *true* objective (bytes decoded, not pairs compared): over a Douglas–Peucker level-of-detail ladder, a **progressive certificate join** certified by a two-sided Hausdorff-margin test returns the provably exact intersection join while decoding **3.4–16.8× (median 5.9×) fewer vertices** than decompress-then-refine, and ≈4.9× fewer than the single-approximation multi-step baseline of Brinkhoff et al. (1994), with zero correctness violations across 31 workloads on US Census TIGER water polygons. The characterisation — the **decode-work law** — is that decode work is governed by each pair's signed-clearance margin, i.e. how close the pair sits to the predicate flip, which is the decompression-sensitive complexity §6 asks for, stated empirically rather than proved (Samyama, arXiv:2607.01182) *(frontier — verify)*.

## 8. Future Work
- A formal *decompression-sensitive* complexity model for spatial predicates.
- Predicate-aware (join-aware) lossy/lossless geometry codecs with certificate margins.
- Progressive refinement with provable early-termination guarantees.
- GPU/vectorized evaluation entirely in the encoded domain; error-bounded approximate joins on simplified geometries.

## 9. Key References
- **[Foundational]** Brinkhoff, Kriegel, Seeger. *Efficient Processing of Spatial Joins Using R-trees.* SIGMOD, 1993. — [ACM](https://dl.acm.org/doi/10.1145/170035.170075)
- **[Foundational]** Patel, DeWitt. *Partition Based Spatial-Merge Join.* SIGMOD, 1996. — [ACM](https://dl.acm.org/doi/10.1145/235968.233338) · [DBLP](https://dblp.org/rec/conf/sigmod/PatelD96.html)
- **[SOTA]** Pandey et al. *How Good Are Modern Spatial Analytics Systems? (and SpatialParquet / columnar-spatial line).* VLDB, 2018–2023. — [DOI](https://doi.org/10.14778/3236187.3236213) · [DBLP](https://dblp.org/rec/journals/pvldb/PandeyKNK18.html)
- **[SOTA]** GeoArrow / GeoParquet specifications. *Columnar Encodings for Geometry.* OGC / Apache, 2022–2024. — [GeoArrow](https://geoarrow.org/) · [GeoParquet](https://geoparquet.org/)
- **[Survey]** Navarro. *Compact Data Structures: A Practical Approach.* Cambridge University Press, 2016. — [DOI](https://doi.org/10.1017/CBO9781316588284)

- **[SOTA]** Samyama Research. *The Decode-Work Law: Margin-Governed, Provably-Exact Spatial Joins over Compressed Geometry.* arXiv:2607.01182 (cs.DB), 2026. — [arXiv](https://arxiv.org/abs/2607.01182) · [code](https://github.com/samyama-ai/spatial-join-on-compressed)
## 10. Worked Example

Join two polygons stored progressively (Douglas–Peucker hierarchies), testing **intersects**. Each polygon has $1{,}000$ vertices; full decode = $1{,}000$ coordinate pairs each.

**Case A — clear separation.** $R$ lies in $x\in[0,3]$, $S$ in $x\in[7,10]$. Their coarse simplifications $\tilde R,\tilde S$ at level 0 (4 vertices each, Hausdorff error $\eta = 0.5$). The simplified MBR gap is $7 - 3 = 4 > 2\eta = 1$, so the conservative test clears the margin and **certifies disjoint** after decoding $8$ vertices total — a $1{,}000/8 = 125\times$ saving over full decode.

**Case B — boundary grazing.** $R$ in $x\in[0,5]$, $S$ in $x\in[4.9,10]$; the overlap band $[4.9,5]$ is narrower than $\eta=0.5$. Coarse tests stay *ambiguous*, so refinement must descend the hierarchy in the band region only. If just $30$ vertices of each polygon fall in that $x$-band, decode $\approx 60$ vertices, not $2{,}000$.

**Adversarial worst case.** Two interlocking combs whose teeth alternate every level force descent everywhere: decode $\Theta(\text{total vertices}) = 2{,}000$ — matching the $\Omega(\text{boundary vertices})$ lower bound. Average redundant data is cheap; adversarial data is not.

---
*Part of the [DBMS Research catalog](../../README.md).*
