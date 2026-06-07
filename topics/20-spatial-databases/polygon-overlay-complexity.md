---
id: 20-spatial-databases/polygon-overlay-complexity
title: "Polygon containment and overlay complexity"
topic: 20-spatial-databases
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Polygon containment and overlay complexity

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/polygon-overlay-complexity` · **Status:** partially-solved

## 1. Problem Statement
Given two planar subdivisions (sets of polygons) $A$ and $B$ with $n$ total edges, compute their **map overlay** — the arrangement formed by superimposing $A$ and $B$, with each output face labeled by the pair of input faces containing it. Special cases: **point-in-polygon containment**, **polygon clipping/intersection** ($A\cap B$), and Boolean operations (union, difference). The hard, deployment-relevant constraints are:

1. **Robustness under floating-point:** naive intersection tests on IEEE-754 coordinates produce inconsistent topology (an edge "crosses" by one test but not its neighbor), causing crashes, gaps, or sliver polygons.
2. **Degeneracy:** collinear edges, coincident vertices, vertices on edges, and overlapping boundaries — the cases real GIS data is full of.
3. **Output sensitivity:** runtime should depend on the actual number $k$ of intersections produced, not the worst-case $\Theta(n^2)$.

Variants: *decision* (do $A,B$ intersect?), *construction* (build the overlay), *counting* (number of intersection points / output faces).

## 2. Mathematical Foundations
The overlay is the **arrangement** $\mathcal{A}(A\cup B)$ of the input segments; its combinatorial complexity is $O(n+k)$ where $k$ is the number of pairwise edge intersections, $k=O(n^2)$ in the worst case. Computing all segment intersections is the classic **Bentley–Ottmann** sweep, $O((n+k)\log n)$; **Chazelle–Edelsbrunner** achieves the optimal $O(n\log n + k)$. Overlay of two *connected* subdivisions can be done in $O(n+k)$ via topological sweep / the DCEL (doubly-connected edge list) merge.

Robustness is governed by **geometric predicates** — the $\mathrm{sign}$ of the **orientation** determinant $\begin{vmatrix} b_x-a_x & b_y-a_y\\ c_x-a_x & c_y-a_y\end{vmatrix}$ and the **in-circle** test. Correct topology requires these signs to be *exact*; floating-point can flip them. The standard remedies are **exact geometric computation (EGC)** with adaptive-precision arithmetic (Shewchuk's predicates), **arithmetic filters**, or the **Simulation of Simplicity** perturbation scheme for degeneracies. The **snap-rounding** framework rounds intersection points to a grid while bounding topological distortion.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Optimal $O(n\log n + k)$ segment intersection (Chazelle–Edelsbrunner, J. ACM 1992); $O(n+k)$ overlay of subdivisions (Guibas–Seidel / Finke–Hinrichs).
- **Robustness-SOTA:** **CGAL** Arrangement_2 and 2D Boolean operations with **exact** number types (and arithmetic filtering) — the gold standard for correctness; **Shewchuk's** adaptive predicates as the kernel.
- **Systems-SOTA:** **GEOS/JTS** (the engine behind PostGIS, Shapely, QGIS) uses a fixed/floating model with noding + the **OverlayNG** robust overlay rewrite; **boost.geometry**, Clipper2 (Vatti-based) for integer/clipping pipelines; GPU/parallel overlay in spatial-analytics engines.

## 4. Upper Bound
- **Intersection reporting / overlay:** $O(n\log n + k)$ time, $O(n)$ space (RAM model, real-RAM with exact predicates), optimal in the comparison/algebraic-decision-tree sense.
- **Point-in-polygon:** $O(\log n)$ query after $O(n\log n)$ preprocessing (point-location via trapezoidal decomposition / Kirkpatrick).
- **Robust overlay:** EGC delivers a *topologically exact* result at the cost of a number-type-dependent multiplicative overhead (filtered exact arithmetic keeps it near floating speed on non-degenerate inputs).

## 5. Lower Bound
- $\Omega(n\log n + k)$ for intersection reporting in the **algebraic decision tree** model (element-distinctness / sorting reduction).
- **Element distinctness** also lower-bounds segment-intersection *detection* at $\Omega(n\log n)$.
- The *robustness* difficulty is not a complexity lower bound but an **impossibility under finite precision**: with fixed-width floating-point, no consistent global topology is guaranteed (the predicates cannot all be evaluated exactly), which is what forces EGC or snap-rounding.

## 6. The Gap
The **complexity** question is essentially **closed**: $\Theta(n\log n + k)$ is optimal and achieved. What remains *partially-solved* is the **robust + degenerate + fast** triple: exact-arithmetic overlay is correct but pays a number-type overhead and is hard to parallelize; floating-point engines are fast but historically buggy (the long tail of GEOS "TopologyException"s, largely tamed by OverlayNG). No single approach simultaneously guarantees exactness, handles all degeneracies, runs at floating-point speed, and parallelizes well — that engineering-theoretic gap is the open part.

## 7. Current Research (as of June 2026)
- **OverlayNG**-style robust noding with snap-rounding as the de-facto production answer; ongoing hardening and performance work in GEOS/JTS *(frontier — verify)*.
- GPU/SIMD-parallel exact-or-filtered overlay for planetary-scale GIS; vectorized point-in-polygon.
- Verified/formally-proven geometric kernels and certified predicates. Groups/people: the CGAL arrangements community (Efi Fogel, Dan Halperin), Jonathan Shewchuk (robust predicates), Martin Davis (JTS/GEOS OverlayNG).

## 8. Future Work
Provably robust *parallel* overlay at floating-point speed; a unified degeneracy-and-precision theory tying snap-rounding distortion to EGC guarantees; formally verified production overlay kernels; output-sensitive overlay on compressed/streamed polygon data.

## 9. Key References
- **[Foundational]** Bentley, Ottmann. *Algorithms for Reporting and Counting Geometric Intersections.* IEEE Trans. Computers, 1979. — [DOI](https://doi.org/10.1109/TC.1979.1675432)
- **[Foundational]** Chazelle, Edelsbrunner. *An Optimal Algorithm for Intersecting Line Segments in the Plane.* J. ACM, 1992. — [DOI](https://doi.org/10.1145/147508.147511)
- **[Foundational]** Shewchuk. *Adaptive Precision Floating-Point Arithmetic and Fast Robust Geometric Predicates.* Discrete & Computational Geometry, 1997. — [DOI](https://doi.org/10.1007/PL00009321)
- **[SOTA]** Fogel, Halperin, Wein. *CGAL Arrangements and Their Applications.* Springer, 2012. — [DOI](https://doi.org/10.1007/978-3-642-17283-0)
- **[SOTA]** Hobby. *Practical Segment Intersection with Finite Precision Output (Snap Rounding).* Computational Geometry: Theory and Applications, 1999. — [DOI](https://doi.org/10.1016/S0925-7721(99)00021-8)

## 10. Worked Example

**A robustness failure in one orientation test.** Overlay two triangles whose edges nearly graze. Subdivision $A$ has edge $e$ from $a=(0,0)$ to $b=(10,10)$; subdivision $B$ has vertex $c=(5.0,5.0000000001)$. To label the face containing $c$ we evaluate the orientation determinant

$$\mathrm{sign}\begin{vmatrix} b_x-a_x & b_y-a_y\\ c_x-a_x & c_y-a_y\end{vmatrix} = \mathrm{sign}\begin{vmatrix} 10 & 10\\ 5 & 5.0000000001\end{vmatrix} = \mathrm{sign}(10\cdot 5.0000000001 - 10\cdot 5) = \mathrm{sign}(10^{-9}) > 0,$$

so $c$ lies just **left** of $e$. The exact value $+10^{-9}$ is far below IEEE-754 double cancellation error: $10\times 5.0000000001 = 50.000000001$ rounds against $50.0$, and the subtraction can yield $0$ or even a negative result. A neighboring vertex tested on the *other* incident edge might be judged **right**, producing a topologically impossible "edge crossing itself" — a sliver polygon or a thrown `TopologyException`.

**Cost side:** with $n=6$ total edges and $k=2$ true crossings, Bentley–Ottmann runs in $O((n+k)\log n)=O(8\log 6)\approx 21$ steps; Shewchuk's adaptive predicate returns the exact $\mathrm{sign}=+1$ here, restoring correct topology at near-float speed because the filter only escalates to exact arithmetic on this near-degenerate test.

---
*Part of the [DBMS Research catalog](../../README.md).*
