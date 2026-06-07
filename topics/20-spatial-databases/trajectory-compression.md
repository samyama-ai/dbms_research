---
id: 20-spatial-databases/trajectory-compression
title: "Trajectory compression with query guarantees"
topic: 20-spatial-databases
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Trajectory compression with query guarantees

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/trajectory-compression` · **Status:** partially-solved

## 1. Problem Statement
Given a trajectory $T = \langle p_1,\dots,p_m\rangle$ (points in $\mathbb{R}^2$ or $\mathbb{R}^2\times\mathbb{R}_{\ge 0}$, possibly with speed/heading), produce a **compressed** representation $\tilde T$ — typically a subsequence (line simplification) or a model-coded stream — that is small yet **answers downstream queries with bounded error**.

Variants:
- **Min-size under error bound (optimization):** minimize $|\tilde T|$ s.t. $\mathrm{err}(T,\tilde T)\le\varepsilon$ for a chosen error measure (Hausdorff, Fréchet, synchronous Euclidean distance / SED, or position-at-time error).
- **Min-error under size budget (dual):** minimize error s.t. $|\tilde T|\le b$.
- **Query-faithful compression:** guarantee that **range**, **kNN**, **distance-join**, or **similarity** queries evaluated on $\tilde T$ return answers within a stated tolerance of those on $T$ (e.g. no false dismissals, bounded ranking error).

The distinction that makes this "partially-solved": geometric simplification with a bounded *positional* error is well understood, but propagating that bound into **query-result** guarantees (kNN ordering, similarity-join membership) is largely open.

## 2. Mathematical Foundations
**Line simplification** picks $\tilde T \subseteq T$ keeping endpoints, minimizing vertices subject to each dropped point lying within $\varepsilon$ of the retained segment under measure $\delta$. For the **Hausdorff/Fréchet** error the optimal min-# (Imai–Iri) is solvable in polynomial time by building a shortcut graph and shortest-pathing it; Agarwal–Har-Peled–Mustafa–Wang give near-linear $(c\varepsilon)$-approximations under Fréchet. **Douglas–Peucker** is the classic $O(m\log m)$ heuristic (no optimality guarantee, can violate Fréchet).

Key relations:
- **Triangle-inequality lifting:** if $\delta_F(T,\tilde T)\le\varepsilon$ then for any query curve $Q$, $|d(T,Q)-d(\tilde T,Q)|\le\varepsilon$ when $d$ obeys the triangle inequality (Fréchet, ERP) — giving directly a $\pm\varepsilon$ guarantee on similarity queries, and (via radius inflation $r\pm\varepsilon$) a *no-false-dismissal* filter for range/kNN. For non-metric $d$ (DTW/EDR) this lifting fails.
- **SED / time-aware error** bounds position-at-time, needed for spatiotemporal range and "where was the object at $t$" queries.

Information-theoretic limits: rate–distortion bounds the achievable size for a target expected error; the min-vertices objective is an instance of geometric set-cover-like covering.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** optimal Imai–Iri min-# under $L_\infty$/Hausdorff; near-linear approximate Fréchet simplification (Agarwal et al., 2005); $(1+\varepsilon)$-coresets for directional/segment queries.
- **Systems-SOTA:** online bounded-error simplifiers — **SQUISH / SQUISH-E** (priority-queue, SED-bounded), **Dead Reckoning**, **STTrace**, **BQS/OPERB** (one-pass error-bounded), and learned/semantic compressors. Distributed stream compressors in trajectory platforms (TrajStore, UlTraMan, JUST). Most bound *positional* error; query-guarantee-aware compressors (e.g. error-bounded for range/kNN) appear in REST/CISED-style work but remain narrow.

## 4. Upper Bound
Min-# simplification under Hausdorff/Fréchet: polynomial (Imai–Iri $O(m^3)$ exact via shortcut graph; near-linear $O(m\log m)$ for constant-factor Fréchet approximations) in the **real-RAM model**. One-pass online simplification achieves SED $\le\varepsilon$ in $O(1)$ amortized per point with $O(b)$ memory. Via the triangle-inequality lifting, a Fréchet-$\varepsilon$ simplification yields **range/kNN with no false dismissals** at radius inflation $\varepsilon$, and **$\pm\varepsilon$** on metric similarity queries.

## 5. Lower Bound
Exact min-# under the **Fréchet** measure with the standard model is conjectured hard to optimize in strongly subquadratic time, and approximation is tied to Fréchet-decision hardness (SETH-conditional, via the single-pair barrier; Bringmann 2014). Rate–distortion gives an **information-theoretic** floor on size for target expected distortion. For **query-faithful** compression under non-metric distances no positional bound can guarantee bounded kNN-ranking error in the worst case — an adversarial input can flip rankings under DTW with arbitrarily small positional perturbation, an unconditional impossibility for that combination.

## 6. The Gap
Positional/Fréchet simplification is essentially solved (optimal poly-time, near-linear approximations, practical one-pass streamers). The **open** part: (a) compressors with provable guarantees for **non-metric** (DTW/EDR/LCSS) downstream queries; (b) joint optimization of size against a *query workload* rather than a generic distance; (c) compression with bounded **kNN-ordering** error rather than just bounded value error. These are genuinely open — the metric-lifting trick does not extend, and no matching lower bound or algorithm yet exists.

## 7. Current Research (as of June 2026)
Active threads: error-bounded online simplification with workload-aware budgets; learned/semantic trajectory compression (RL- and autoencoder-based codecs) that empirically preserve query accuracy but lack guarantees *(frontier — verify)*; coreset constructions for trajectory range/kNN with provable $(1\pm\varepsilon)$ query preservation; and integration of compression into storage engines (column-encoded trajectory stores). Groups: Agarwal, Har-Peled (geometric simplification); Jensen, Zheng, Cheng, Sacharidis, Pelekis–Theodoridis (trajectory data management). Coreset-backed query-faithful compressors are an active frontier *(frontier — verify)*.

## 8. Future Work
- Query-faithful coresets covering DTW/EDR/LCSS, not just Fréchet.
- Compression jointly optimized against a query workload with end-to-end accuracy bounds.
- Bounded kNN-ranking-error (not just value-error) compression.
- Hardware/storage-aware error-bounded codecs integrated with spatial indexes.

## 9. Key References
- **[Foundational]** Douglas, Peucker. *Algorithms for the Reduction of the Number of Points Required to Represent a Digitized Line or Its Caricature.* Cartographica, 1973. — [DOI](https://doi.org/10.3138/FM57-6770-U75U-7727)
- **[Foundational]** Imai, Iri. *Polygonal Approximations of a Curve — Formulations and Algorithms.* In *Computational Morphology*, 1988. — [DOI](https://doi.org/10.1016/B978-0-444-70467-2.50011-4)
- **[Foundational]** Agarwal, Har-Peled, Mustafa, Wang. *Near-Linear Time Approximation Algorithms for Curve Simplification.* Algorithmica, 2005. — [DOI](https://doi.org/10.1007/s00453-005-1165-y)
- **[SOTA]** Muckell et al. *SQUISH-E: An Online Approach for Compressing Trajectories.* GeoInformatica, 2014. — [DOI](https://doi.org/10.1007/s10707-013-0184-0)
- **[SOTA]** Lin, Ma, Zhang, Wo, Huai. *One-Pass Error-Bounded Trajectory Simplification (OPERB).* VLDB, 2017. — [arXiv](https://arxiv.org/abs/1702.05597)
- **[Survey]** Zheng. *Trajectory Data Mining: An Overview.* ACM TIST, 2015. — [DOI](https://doi.org/10.1145/2743025)

## 10. Worked Example

Take a 5-point trajectory $T=\langle p_1,\dots,p_5\rangle$ with $p_1=(0,0)$, $p_2=(1,0.3)$, $p_3=(2,0.1)$, $p_4=(3,0.4)$, $p_5=(4,0)$, and Douglas–Peucker tolerance $\varepsilon=0.5$.

**DP trace.** Keep endpoints $p_1,p_5$; the baseline is the segment $y=0$. Perpendicular distances of interior points: $p_2{:}0.3$, $p_3{:}0.1$, $p_4{:}0.4$ — the max is $p_4$ at $0.4<\varepsilon$. So *every* interior point is dropped: $\tilde T=\langle p_1,p_5\rangle$, compressing $5\to2$ vertices ($60\%$ reduction).

**Query-faithfulness via Fréchet lifting.** Here the Fréchet error $\delta_F(T,\tilde T)\le 0.4\le\varepsilon$. For a range query "all points within radius $r=1.0$ of $q=(2,1.2)$": evaluated on $T$, $p_4$ is at distance $\sqrt{1+0.64}\approx1.28>1$, so $T$ does *not* qualify. Evaluating on $\tilde T$ at *inflated* radius $r+\varepsilon=1.4$ guarantees **no false dismissal** — the lifted bound $|d(T,q)-d(\tilde T,q)|\le\varepsilon$ (Section 2) certifies the filter. Under non-metric DTW this guarantee would not hold (Section 5).

---
*Part of the [DBMS Research catalog](../../README.md).*
