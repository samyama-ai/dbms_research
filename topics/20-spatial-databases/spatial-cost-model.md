---
id: 20-spatial-databases/spatial-cost-model
title: "Spatial query optimization cost models"
topic: 20-spatial-databases
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Spatial query optimization cost models

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/spatial-cost-model` · **Status:** empirically-open

## 1. Problem Statement
Build the **cost and selectivity models** a query optimizer needs to plan spatial workloads: for spatial **range/window**, **kNN**, and **spatial-join** (intersection / distance / kNN-join) operators over data drawn from skewed, correlated distributions in $\mathbb{R}^d$ ($d=2,3$, often plus time), predict (a) **selectivity** — the number of qualifying tuples or join pairs — and (b) **operator cost** — page accesses, CPU comparisons, and (for joins) the number of candidate pairs, accurately enough to pick the right plan.

Sub-problems:
- **Range/window selectivity:** estimate $|\{o : o \cap W \ne \emptyset\}|$ for query window $W$.
- **Join cardinality:** estimate $|R \bowtie_{\text{intersect}} S|$ and distance-join sizes.
- **kNN cost:** predict pages/distance-computations for a $k$NN under a given index.
- **Robustness:** all of the above must hold across data skew, varying object extents, and index choice (R-tree, grid, space-filling-curve, learned index).

"Empirically-open": estimators that win on benchmarks (sampling, histograms, learned models) lack worst-case guarantees, and the optimizer's plan choice is acutely sensitive to estimation error exactly in the selective, skewed regime.

## 2. Mathematical Foundations
For point data with density $\mu$, range selectivity is $\mu(W)$; classic models assume per-bucket **uniformity and independence** (the UIA), which fails under correlation and along arbitrary polygon boundaries. Object extents are handled by the **Minkowski-sum / transformation** model: a window query over rectangles of average side $s$ behaves like a point query enlarged by $s$, so expected R-tree node accesses $\approx \sum_{\text{nodes}} \prod_{j}(W_j + e_{i,j})$, where $e_{i,j}$ are node MBR extents — the foundation of analytical R-tree cost models (Theodoridis–Sellis; Pagel–Six–Toben–Widmayer) parameterized by **data density** and the **fractal dimension** of the dataset.

Selectivity quality is bounded by the **VC dimension** of the query class: axis-aligned boxes $\mathrm{VC}=2d$, halfspaces $d+1$, $k$-gons growing with $k$. An **$\varepsilon$-approximation** sample of size $O(\mathrm{VC}/\varepsilon^2)$ gives additive guarantees, but **relative** error for selective queries costs $\Omega(1/(\varepsilon^2\sigma))$ samples. For **join size**, worst-case output is governed by AGM-style bounds; the spatial intersection join's cardinality depends on the joint density and the box-extent distribution, with no clean closed form under skew.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** PostGIS / Oracle Spatial / SQL Server use 2-D equi-depth or histogram-based selectivity (Min-Skew, GENHIST, Euler histograms for extents) plus R-tree analytical cost formulas; SpatialHadoop / GeoSpark (Apache Sedona) estimate partition/join cost from sampled grids. Learned spatial cardinality estimators (deep autoregressive / SPN / set-based models adapted to coordinates and MBRs) lower average error but give no provable bound.
- **Theory-SOTA:** geometric **$\varepsilon$-approximations and coresets** for range counting (Matoušek discrepancy; Phillips); fractal-dimension-based density models (Faloutsos–Kamel) for R-tree page-access prediction; sketch-based join-size estimation.

## 4. Upper Bound
Range-count selectivity: a coreset / sample of size $O(\varepsilon^{-2d/(d+1)})$ (deterministic, discrepancy) or $\tilde O(\varepsilon^{-2})$ (randomized, VC) gives additive $\varepsilon$ error in the **real-RAM model**. Analytical R-tree cost models predict expected node accesses with provable accuracy **under uniformity/fractal assumptions**, and the Faloutsos–Kamel fractal model captures self-similar skew. For join size, sketches give $(1\pm\varepsilon)$ estimates with bounded space. No estimator gives sublinear-in-$1/\sigma$ **relative** error for highly selective skewed polygon/join predicates.

## 5. Lower Bound
Additive $\varepsilon$ selectivity needs $\Omega(\mathrm{VC}(\mathcal{Q})/\varepsilon^2)$ samples (**information-theoretic**), and relative error of a query with true selectivity $\sigma$ needs $\Omega(1/(\varepsilon^2\sigma))$ — the regime the optimizer cares about most. Spatial **join-size** estimation inherits **set-intersection communication** and AGM worst-case-output lower bounds: no small summary preserves accuracy on adversarial inputs. These are unconditional (info-theoretic / communication), not SETH-conditional. Crucially, *cost* estimation error compounds: small selectivity errors can cause arbitrarily bad plan choices (no Lipschitz guarantee from estimate-error to plan-cost).

## 6. The Gap
For **additive** range-count error the sample-complexity bounds essentially match. The genuine, open gaps: (a) **relative**-error guarantees for selective skewed predicates ($1/\sigma$ blowup); (b) **no worst-case envelope** for the learned estimators that win empirically; (c) **join and kNN cost** models under correlation, where analytical formulas rest on independence/fractal assumptions that real data violate; and (d) **robustness** — translating estimation error into bounded plan-regret. Closing it needs instance-/intrinsic-dimension-adaptive estimators, certified learned models, and a plan-stability theory.

## 7. Current Research (as of June 2026)
Active threads: instance-adaptive coresets exploiting **intrinsic/fractal** rather than ambient dimension of real spatial data; conformal-prediction / calibration wrappers giving post-hoc coverage on learned spatial estimators *(frontier — verify)*; workload-driven (query-aware) summaries with PAC-style bounds; learned spatial-join and kNN cost models in Sedona/Spark-style engines; and robustness-aware optimization that bounds plan regret under estimation uncertainty *(frontier — verify)*. Groups: Suciu / Re (probabilistic & learned CE), Phillips (geometric coresets), Faloutsos lineage (fractal cost models), Mokbel / Aref / Sacharidis / Eldawy (spatial systems and SpatialHadoop/Sedona).

## 8. Future Work
- Relative-error selectivity whose cost depends on intrinsic, not ambient, dimension.
- Certified learned cost/selectivity models (monotone/Lipschitz, provable envelopes).
- Correlation-aware join and kNN cost models beyond uniformity/fractal assumptions.
- Plan-robust optimization: bounding plan regret as a function of estimation error.

## 9. Key References
- **[Foundational]** Selinger, Astrahan, Chamberlin, Lorie, Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [ACM](https://dl.acm.org/doi/10.1145/582095.582099) · [DBLP](https://dblp.org/rec/conf/sigmod/SelingerACLP79.html)
- **[Foundational]** Theodoridis, Sellis. *A Model for the Prediction of R-tree Performance.* PODS, 1996. — [ACM](https://dl.acm.org/doi/10.1145/237661.237705)
- **[Foundational]** Faloutsos, Kamel. *Beyond Uniformity and Independence: Analysis of R-trees Using the Concept of Fractal Dimension.* PODS, 1994. — [ACM](https://dl.acm.org/doi/10.1145/182591.182593)
- **[Foundational]** Acharya, Poosala, Ramaswamy. *Selectivity Estimation in Spatial Databases.* SIGMOD, 1999. — [ACM](https://dl.acm.org/doi/10.1145/304182.304184)
- **[SOTA]** Phillips. *Coresets and Sketches.* In *Handbook of Discrete and Computational Geometry*, 3rd ed., 2017. — [arXiv](https://arxiv.org/abs/1601.00617)
- **[SOTA]** Yang et al. *Deep Unsupervised Cardinality Estimation (Naru).* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1905.04278) · [DOI](https://doi.org/10.14778/3368289.3368294)
- **[Survey]** Eldawy, Mokbel. *Spatial Join Techniques: A Tutorial / The Era of Big Spatial Data.* (Spatial query processing surveys), PVLDB, 2017. — [DOI](https://doi.org/10.14778/3137765.3137828)

## 10. Worked Example

Consider $N = 10{,}000$ points uniformly distributed in the unit square $[0,1]^2$, indexed by an R-tree with node capacity $b = 50$, so leaves cover $\approx b/N = 0.005$ area each. A square window query $W$ of side $w = 0.1$ (area $0.01$) is issued.

**Selectivity (UIA model):** expected qualifying points $= N \cdot \mu(W) = 10{,}000 \times 0.01 = 100$.

**Node accesses (Minkowski-sum model):** a leaf MBR has side $s \approx \sqrt{0.005} \approx 0.0707$. The query "touches" a leaf when their centers lie within $w + s = 0.171$, so expected leaf accesses $\approx (N/b)\,(w+s)^2 = 200 \times 0.171^2 \approx 5.8$.

**Where it breaks:** if the points instead lie on a fractal line of dimension $D = 1.4$ rather than filling $D = 2$, the Faloutsos–Kamel formula replaces the exponent: accessed leaves scale as $w^{D}$ not $w^{2}$. With $w = 0.1$, $0.1^{1.4} \approx 0.040$ vs. $0.1^{2} = 0.010$ — a $4\times$ underestimate by the uniform model, illustrating why fractal dimension matters under skew.

---
*Part of the [DBMS Research catalog](../../README.md).*
