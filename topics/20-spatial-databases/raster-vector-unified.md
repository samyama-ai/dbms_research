# In-database raster-vector unification

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/raster-vector-unified` · **Status:** open

## 1. Problem Statement
Define a single **query model and physical design** that treats *raster* data (regular-grid arrays: imagery, elevation, climate fields) and *vector* data (points, lines, polygons) as first-class citizens of one **optimizable algebra**, so that cross-paradigm queries — e.g. "average NDVI inside each administrative polygon," "rasterize these parcels then zonal-stat against a DEM," "vectorize flood extent from a raster then join to road segments" — are expressed declaratively and optimized end-to-end (operator reordering, pushdown, cost-based choice of raster-vs-vector representation).

Variants:
- **Algebra design (expressiveness/closure):** find operators closed over a unified type so plans compose.
- **Optimization:** given a query, choose representation conversions and operator order minimizing cost (a *physical-design + plan* search problem).
- **Decision flavor:** is a given cross-paradigm query expressible/optimizable within the algebra at all?

The crux is that raster (dense, array, implicit geometry, value-per-cell) and vector (sparse, object, explicit geometry, attributes) have fundamentally different algebras (linear/array algebra vs. relational + geometric), and naive bridging via materialized conversion (rasterize-everything or vectorize-everything) destroys both performance and accuracy.

## 2. Mathematical Foundations
Vector data fits **relational algebra** extended with geometric predicates/functions (the ROSE/realm and "spatial algebra" tradition: $\sigma, \pi, \bowtie$ plus `intersects`, `overlaps`, `buffer`). Raster data fits **array algebra** — an algebra over functions $f:\mathbb{Z}^d \supseteq D \to V$ with operators `apply` (map), `aggregate` (reduce over a subdomain), `regrid`/`reshape`, and a structural `join` (SciDB/Map Algebra; Tomlin's local/focal/zonal/global classes). Unification seeks a common type $T$ (e.g. a *partial function over $\mathbb{R}^d$* / measurable field) with a closed operator set, so that rasterization $\rho$ and vectorization $\nu$ are explicit, cost-bearing morphisms rather than ad-hoc casts. Desiderata mirror relational theory: **closure**, **equivalence rules** (rewrite laws enabling reordering, e.g. push `aggregate` through `mask`), and a **cost model** over both array (cells, tiles, $(M,B)$ I/O) and geometric (object count, MBR overlap) cardinalities. Soundness of rewrites can be argued via denotational equivalence on the field semantics; completeness/optimality of the rewrite system is the open theoretical target.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** PostGIS Raster + geometry (loosely coupled), Oracle GeoRaster, RasdaMan / SciDB (array-DB side), Google Earth Engine (functional raster+vector but proprietary, no relational optimizer), Apache Sedona / GeoTrellis (raster + vector on Spark), and OGC's *Coverages* + *Discrete Global Grid Systems (DGGS)* standards as a common-substrate attempt. None offer a single cost-based optimizer that jointly reorders raster and vector operators.
- **Theory-SOTA:** the *spatial algebra* line (Güting; ROSE) and *array algebra* line (Baumann; Marathe–Salem) remain largely separate; recent "spatial data cube" and DGGS work unifies *representation* but not *optimization*.

## 4. Upper Bound
No single result; the practical ceiling is **operator-at-a-time** execution with hand-tuned conversion points. Zonal statistics (the canonical cross-paradigm op) runs in $O(\text{cells} + \text{vector boundary})$ with tiled raster scan + polygon rasterization; cross-products of raster tiles and vector partitions are handled by SFC/tile co-partitioning. End-to-end *optimality* across representations is not bounded — it is unestablished because no agreed optimizable algebra exists.

## 5. Lower Bound
There is no clean complexity-theoretic lower bound here; the problem is one of *modeling and optimization completeness* rather than asymptotic hardness. Indirect barriers: cost-based join/operator ordering is NP-hard in general (so the unified optimizer inherits plan-search hardness), and exact raster↔vector conversion is *lossy/ill-posed* in both directions (rasterization loses topology; vectorization is an inverse problem), so a "free" canonical form provably cannot exist without accuracy loss.

## 6. The Gap
The gap is conceptual, not numeric: we have two mature but disjoint algebras and many point integrations, but **no closed, optimizable, cost-modeled unification** with proven rewrite soundness/completeness. Closing it requires (1) a field-based type and operator set provably closed and expressive enough for standard GIS workloads, (2) a sound, ideally complete rewrite system, and (3) a cost model spanning array and geometric cardinalities so the optimizer can choose representations.

## 7. Current Research (as of June 2026)
Active directions: DGGS-based common substrates (H3, S2, rHEALPix) as the discretization layer enabling uniform raster+vector ops *(frontier — verify)*; "spatial/EO data cubes" (openEO, Pangeo, STAC + datacube) pushing functional raster+vector pipelines with emerging optimizers *(frontier — verify)*; and ML-pipeline integration where raster (imagery) and vector (labels) must be jointly queried. Groups: Freire/Doraiswamy (geometric data model + algebra), Baumann (array/coverages), the openEO/Pangeo communities, and Sedona/GeoTrellis maintainers.

## 8. Future Work
- A provably-closed unified algebra with a sound and (partially) complete rewrite calculus.
- Cost models and cardinality estimation spanning cells and objects.
- Automatic, cost-based selection of raster-vs-vector representation per sub-query.
- Accuracy/uncertainty propagation across $\rho$/$\nu$ conversions in the optimizer.

## 9. Key References
- **[Foundational]** Güting. *An Introduction to Spatial Database Systems.* VLDB Journal, 1994.
- **[Foundational]** Tomlin. *Geographic Information Systems and Cartographic Modeling (Map Algebra).* Prentice Hall, 1990.
- **[Foundational]** Baumann. *A Database Array Algebra for Spatio-Temporal Data and Beyond.* NGITS, 1999 (rasdaman).
- **[SOTA]** Stonebraker et al. *The Architecture of SciDB.* SSDBM, 2011.
- **[SOTA]** Doraiswamy, Freire. *A GPU-Friendly Geometric Data Model and Algebra for Spatial Queries.* SIGMOD, 2020.
- **[Survey]** OGC. *Topic 6: Coverages / Abstract Specification & DGGS.* Open Geospatial Consortium, 2017–2024.

---
*Part of the [DBMS Research catalog](../../README.md).*
