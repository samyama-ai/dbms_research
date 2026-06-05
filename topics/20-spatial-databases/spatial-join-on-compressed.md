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

## 8. Future Work
- A formal *decompression-sensitive* complexity model for spatial predicates.
- Predicate-aware (join-aware) lossy/lossless geometry codecs with certificate margins.
- Progressive refinement with provable early-termination guarantees.
- GPU/vectorized evaluation entirely in the encoded domain; error-bounded approximate joins on simplified geometries.

## 9. Key References
- **[Foundational]** Brinkhoff, Kriegel, Seeger. *Efficient Processing of Spatial Joins Using R-trees.* SIGMOD, 1993.
- **[Foundational]** Patel, DeWitt. *Partition Based Spatial-Merge Join.* SIGMOD, 1996.
- **[SOTA]** Pandey et al. *How Good Are Modern Spatial Analytics Systems? (and SpatialParquet / columnar-spatial line).* VLDB, 2018–2023.
- **[SOTA]** GeoArrow / GeoParquet specifications. *Columnar Encodings for Geometry.* OGC / Apache, 2022–2024.
- **[Survey]** Navarro. *Compact Data Structures: A Practical Approach.* Cambridge University Press, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
