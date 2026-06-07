---
id: 20-spatial-databases/moving-object-index
title: "Indexing moving objects with predictive queries"
topic: 20-spatial-databases
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Indexing moving objects with predictive queries

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/moving-object-index` · **Status:** partially-solved

## 1. Problem Statement
Index a set of $n$ **continuously moving points**, each described by a position function (typically linear motion $p_i(t)=p_i(t_0)+v_i\,(t-t_0)$), to answer:
- **time-parameterized range / k-NN queries** at the **present** time, and
- **predictive (future-time)** queries: "which objects will lie in region $Q$ at time $t_q>t_{\text{now}}$?" or window queries over a future interval,

while keeping the **per-update cost bounded** as objects change their motion parameters (velocity updates) at high rate. The structure must avoid re-indexing on every timestep — positions change continuously, so the index stores *motion functions*, not snapshots.

Variants: **present-time** vs. **future-time** queries; **point** vs. **interval** (window) time predicates; exact vs. approximate; the **decision** core is range containment under motion, the **optimization** is amortized update cost vs. query accuracy over the prediction horizon $H$.

## 2. Mathematical Foundations
Two dual representations:
1. **Primal (TPR-tree):** store each object as a point + velocity; a bounding rectangle becomes a **time-parameterized bounding rectangle (TPBR)** whose extent grows linearly: $\text{MBR}(t)=\text{MBR}(t_0)+ [v^-,v^+](t-t_0)$. Query at future $t_q$ tests the swept rectangle. The key cost driver is **bounding-box dilation**: conservative velocity bounds make TPBRs grow without limit, degrading queries far in the future — formalized by an **integrated overlap/area** objective $\int_{t_0}^{t_0+H} \text{area}(\text{TPBR}(t))\,dt$ that insertion heuristics minimize (TPR\*-tree).
2. **Dual / parametric space:** map a linearly-moving point $(x_0,v)$ to a point in **dual space**; a future range query becomes a **simplex / wedge** query in dual space (Kollios–Gunopulos–Tsotras). This enables **partition-tree / range-searching** machinery: simplex range searching in dimension $d'$ has the classical tradeoff $O(n/B \cdot (\text{query})) $ with query $\tilde O((n/B)^{1-1/d'})$ — the foundation for worst-case bounds (Agarwal–Arge–Erickson **kinetic/parametric** structures).

**Kinetic Data Structures (KDS)** (Basch–Guibas–Hershberger) provide the other formal lens: maintain a **certificate** set whose validity is checked by an **event queue**; quality is measured by **responsiveness, locality, compactness, efficiency** (ratio of internal events to external/output changes). Update cost relates to certificate failures per motion change.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **TPR-tree** (Šaltenis, Jensen, Leutenegger, Lopez SIGMOD 2000) and **TPR\*-tree** (Tao, Papadias, Sun VLDB 2003) are the workhorses — R-trees over time-parameterized rectangles, supporting present and near-future queries with practical update cost. **B^x-tree** and **B^dual-tree** (Jensen, Lin, Ooi) map moving points onto a B+-tree via space-filling curve + reference-time, giving good update throughput. **STRIPES** (dual-transform quadtree). For trajectories/history, **MVR-tree / SETI / TB-tree**.
- **Theory-SOTA:** **Kinetic / parametric range search** structures (Agarwal, Arge, Erickson SODA/PODS 2000) give **worst-case** bounds for time-parameterized range queries via partition trees and kinetic range trees; KDS theory (Basch–Guibas–Hershberger 1997) bounds maintenance via certificate events.

## 4. Upper Bound
- **Theory:** Parametric/kinetic external structures answer a future-time range query in $\tilde O((n/B)^{1/2}+k/B)$ I/Os (2-D linear motion, dual-simplex view) with near-linear space, and support velocity updates in $O(\log^2 n)$-type amortized cost (Agarwal–Arge–Erickson). KDS gives **efficient** structures where internal events are near-linear in external events for many motion models.
- **Practical:** TPR\*-tree achieves logarithmic-height update and query with strong empirical performance over a bounded horizon $H$; cost grows with $H$ due to TPBR dilation, so updates are needed before boxes balloon.

## 5. Lower Bound
- Future-time queries inherit **simplex range searching** lower bounds: with $\tilde O(n)$ space, query time is $\Omega((n/B)^{1-1/d'})$ in the **partition-tree / semigroup arithmetic** model (Chazelle), so sublinear-but-not-logarithmic queries are unavoidable for unbounded-horizon predictive search — fundamentally harder than static point range search.
- **Unbounded horizon:** as $H\to\infty$, any conservative bounding structure must either lose accuracy (box dilation) or pay $\Omega(n)$ rescans; there is no free lunch for far-future prediction under arbitrary velocity updates.

## 6. The Gap
**Partially solved:** present-time and **near-future** (bounded horizon $H$) queries are handled well in practice (TPR\*-tree) and have matching kinetic/parametric **worst-case** theory. The **open** gap is (a) reconciling the *practical* TPR-family (good amortized updates, no clean worst-case query bound, horizon-limited) with the *theoretical* parametric structures (clean bounds, but heavier constants and rarely deployed), and (b) **unbounded-horizon / nonlinear motion** prediction with bounded update — where box dilation and simplex-search lower bounds bite. Closing it means a single structure that is simultaneously deployable, worst-case-bounded for queries, and update-cheap under high-rate velocity changes.

## 7. Current Research (as of June 2026)
- **Learned / model-based motion prediction** indexes (RNN/transformer trajectory models feeding the index) for better non-linear future-time accuracy *(frontier — verify worst-case guarantees, which learned predictors generally lack)*.
- **GPU/streaming** continuous-query engines for moving objects (overlap with distributed spatial joins on streams).
- **Kinetic + concurrent** structures: applying KDS under high-throughput concurrent velocity updates.
- **Trajectory data management** at scale (UC Riverside Eldawy; Aalborg Jensen group; Hong Kong / Singapore mobility-data groups).

## 8. Future Work
- A deployable predictive index with provable worst-case query bounds and $O(\text{polylog})$ amortized velocity-update cost.
- Robust handling of **nonlinear / uncertain** motion (acceleration, road-network-constrained movement).
- Tight characterization of the **horizon $H$ vs. accuracy vs. update-rate** tradeoff.
- Integration with concurrency and high-churn maintenance for real fleet/IoT telemetry.

## 9. Key References
- **[Foundational]** S. Šaltenis, C. S. Jensen, S. T. Leutenegger, M. A. Lopez. *Indexing the positions of continuously moving objects (TPR-tree).* SIGMOD, 2000. — [DOI](https://doi.org/10.1145/342009.335427), [DBLP](https://dblp.org/rec/conf/sigmod/SaltenisJLL00.html)
- **[Foundational]** G. Kollios, D. Gunopulos, V. J. Tsotras. *On indexing mobile objects.* PODS, 1999. — [DOI](https://doi.org/10.1145/303976.304002)
- **[Foundational]** P. K. Agarwal, L. Arge, J. Erickson. *Indexing moving points.* PODS, 2000 (JCSS, 2003). — [DOI](https://doi.org/10.1145/335168.335220)
- **[Foundational]** J. Basch, L. J. Guibas, J. Hershberger. *Data structures for mobile data (kinetic data structures).* SODA, 1997 / J. Algorithms, 1999. — [DOI](https://doi.org/10.1006/jagm.1998.0988)
- **[SOTA]** Y. Tao, D. Papadias, J. Sun. *The TPR\*-tree: an optimized spatio-temporal access method for predictive queries.* VLDB, 2003. — [DBLP](https://dblp.org/rec/conf/vldb/TaoPS03.html)
- **[SOTA]** C. S. Jensen, D. Lin, B. C. Ooi. *Query and update efficient B+-tree based indexing of moving objects (B^x-tree).* VLDB, 2004. — [DBLP](https://dblp.org/rec/conf/vldb/JensenLO04.html)
- **[Survey]** L. H. U, et al. / M. F. Mokbel, T. M. Ghanem, W. G. Aref. *Spatio-temporal access methods.* IEEE Data Eng. Bull., 2003. — [DBLP](https://dblp.org/rec/journals/debu/MokbelGA03.html)

## 10. Worked Example

Three objects on a 1-D line at reference time $t_0=0$, each with position $x_i(t)=x_i(0)+v_i t$:

| obj | $x_i(0)$ | $v_i$ |
|-----|----------|-------|
| A | 0 | $+2$ |
| B | 4 | $-1$ |
| C | 6 | $+1$ |

A **TPR-tree** groups them in one node with a time-parameterized bounding interval. The lower bound moves with $v^-=\min v_i=-1$ (B), the upper with $v^+=\max v_i=+2$ (A); the box at $t_0$ is $[0,6]$. So $\text{TPBR}(t)=[\,0 + (-1)t,\; 6 + 2t\,]=[-t,\,6+2t]$, with width $w(t)=6+3t$ — it **dilates** linearly even though the objects stay within $[\,0,\,6+2t\,]$ tightly.

A predictive query "who is in $[10,12]$ at $t_q=4$?" first tests the TPBR: $\text{TPBR}(4)=[-4,14]$, which overlaps $[10,12]$, so the node is opened. Actual positions at $t{=}4$: $A=8$, $B=0$, $C=10$. Only $C$ qualifies — but the conservative box forced us to examine all three. The integrated-area cost $\int_0^4 w(t)\,dt=\int_0^4(6+3t)\,dt=24+24=48$ is exactly the TPR\*-tree insertion objective (Section 2): far-future queries pay because the swept area grows, which is why velocity updates must arrive before boxes "balloon."

---
*Part of the [DBMS Research catalog](../../README.md).*
