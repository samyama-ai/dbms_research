---
id: 31-time-series-db/error-bounded-compression-optimal
title: "Optimal error-bounded streaming compression"
topic: 31-time-series-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimal error-bounded streaming compression

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/error-bounded-compression-optimal` · **Status:** open

## 1. Problem Statement

Given a stream of points $(t_1, v_1), (t_2, v_2), \dots$ arriving in time order and a tolerance $\varepsilon \ge 0$, produce a piecewise representation $\hat{f}$ (piecewise-constant, piecewise-linear, or higher-degree polynomial segments) such that $\|v_i - \hat{f}(t_i)\|_\infty \le \varepsilon$ for every point, while **minimizing the number of segments** $k$. The encoder must operate in **one pass**, with bounded memory and amortized $O(1)$ (or polylog) per-point time, emitting each segment before having seen the full stream.

Variants:
- **Optimization:** minimize $k$ (segment count) — equivalently minimize bits given a fixed per-segment cost.
- **Decision:** given budget $k$, does a valid $\varepsilon$-representation with $\le k$ segments exist?
- **Dual / counting:** for fixed $k$, minimize $\varepsilon$; or count distinct minimum representations (rarely needed).

The contrast is with the **offline** optimal segmentation, computable by dynamic programming, against which any online algorithm is measured.

## 2. Mathematical Foundations

Model each segment as a function class $\mathcal{H}$ (constants $\mathbb{R}$; lines $a + bt$; degree-$d$ polynomials). A maximal $\varepsilon$-feasible run starting at index $s$ is the longest prefix $[s, e]$ for which $\exists h \in \mathcal{H}$ with $\max_{s \le i \le e} |v_i - h(t_i)| \le \varepsilon$.

For piecewise-linear $L_\infty$ fitting, feasibility of a run reduces to maintaining the **convex hull / feasible cone** of admissible slopes: each point $(t_i, v_i)$ imposes the constraint that the line pass within $[v_i - \varepsilon, v_i + \varepsilon]$, an intersection of half-planes in $(a,b)$-space. This yields the classic **greedy "as long as feasible" rule** of Sliding-Window and the convex-hull tester of O'Rourke (1981), giving $O(1)$ amortized per point.

Key fact (offline optimality): the greedy "extend each segment maximally" strategy is **optimal for the segment-count objective** when segments are independent and feasibility is *prefix-monotone* — feasibility of $[s,e]$ implies feasibility of every sub-interval. This is a matroid/interval-greedy argument. Hence for fixed start points the greedy is offline-optimal; the subtlety is **online**, where segment boundaries are committed irrevocably and future points are unknown.

Competitive analysis: an online encoder is $c$-competitive if $k_{\text{online}} \le c \cdot k_{\text{OPT}} + O(1)$ on every stream.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** O'Rourke (1981) optimal-in-segments online PLA via convex hull, $O(1)$ amortized. For $L_\infty$ with maximal-segment greedy, the online output equals offline OPT *because of prefix-monotonicity* — so for a single segment class the segment-count problem is essentially solved.
- **Systems-SOTA:** **SwingFilter / SlideFilter** (Elmeleegy et al., VLDB 2009) for streaming PLA; **PMC** (Lazaridis & Mehrotra, 2003) piecewise-constant; **Sim-Piece** (Kitsios et al., VLDB 2023) merges PLA segments sharing slopes/intercepts to beat per-segment storage; **Mix-Piece** and follow-ups (2023–2024). These optimize **bits**, not just segment count, which is where the problem becomes genuinely hard.

## 4. Upper Bound

For the pure segment-count objective with a single fixed segment class and prefix-monotone feasibility: maximal-greedy is **1-competitive (optimal)**, $O(n)$ time total, $O(1)$ working memory. This is the strongest possible.

For the **bit-minimization** objective (segments not independent — shared parameters can be coded jointly, as in Sim-Piece), the best known online results are heuristic; Sim-Piece reports large empirical gains but **no competitive ratio**. The offline bit-optimal segmentation is solvable by DP in $O(n^2)$ (or $O(n \log n)$ with hull structures) but the online bit-optimal upper bound is open.

## 5. Lower Bound

When the objective shifts from "count" to "bits" with **cross-segment coding** or **multiple selectable segment classes**, prefix-monotonicity breaks and irrevocable online commitment forces loss: there exist adversarial streams on which any deterministic online encoder uses $\Omega(\log n)$ or constant-factor more segments/bits than OPT *(the precise tight constant is unproven)*. Information-theoretically, no codec can beat the entropy of the segment-boundary distribution; for fixed $\varepsilon$ the minimum description length is bounded below by $H$ of the empirical run-length distribution. No matching online lower bound for the bit objective is established.

## 6. The Gap

For a **single segment class, segment-count objective**: the gap is **closed** (greedy is optimal). The genuinely **open** problem is the **online bit-optimal** version with shared-parameter coding and/or adaptive choice among polynomial degrees: here we have strong heuristics (Sim-Piece family) with no proven competitive ratio, and no tight online lower bound. Closing it requires either an online algorithm with provable constant-competitiveness against bit-OPT, or an adversarial lower bound separating online from offline.

## 7. Current Research (as of June 2026)

- Extending Sim-Piece/Mix-Piece with online segment-merging and provable bounds *(frontier — verify)*.
- Learned / model-based predictors choosing segment class adaptively (ties to the adaptive-encoding problem in this catalog).
- GPU/SIMD-parallel error-bounded PLA for high-rate sensor streams.
- Groups: TU Berlin / DIMA (Markl), the Sim-Piece authors, and edge-analytics groups publishing in VLDB/SIGMOD/EDBT.

## 8. Future Work

- A clean competitive theory for bit-objective online PLA with shared parameters.
- Tight online lower bounds via adversary/communication arguments.
- Multi-class (constant/linear/quadratic) adaptive segmentation with guarantees.
- Distribution-aware (instance-optimal) bounds rather than worst-case.

## 9. Key References

- **[Foundational]** J. O'Rourke. *An on-line algorithm for fitting straight lines between data ranges.* Communications of the ACM, 1981. — [DOI](https://doi.org/10.1145/358746.358758)
- **[Foundational]** H. Elmeleegy, A. Elmagarmid, E. Cecchet, W. Aref, W. Zwaenepoel. *Online Piece-wise Linear Approximation of Numerical Streams with Precision Guarantees.* VLDB, 2009. — [VLDB PDF](https://www.cs.purdue.edu/homes/ake/pub/online_vldb09.pdf)
- **[SOTA]** X. Kitsios, P. Liakos, K. Papakonstantinou, M. Terrovitis. *Sim-Piece: Highly Accurate Piecewise Linear Approximation through Similar Segment Merging.* VLDB, 2023. — [DOI](https://doi.org/10.14778/3594512.3594521)
- **[Foundational]** I. Lazaridis, S. Mehrotra. *Capturing Sensor-Generated Time Series with Quality Guarantees.* ICDE, 2003. — [IEEE](https://ieeexplore.ieee.org/document/1260811/)
- **[Survey]** P. Esling, C. Agon. *Time-Series Data Mining.* ACM Computing Surveys, 2012. — [DOI](https://doi.org/10.1145/2379776.2379788)

## 10. Worked Example

Piecewise-constant fit, tolerance $\varepsilon = 1.0$, stream $v = [10,\,10.5,\,11,\,11.8,\,3,\,3.2]$.

A constant segment $[s,e]$ is $\varepsilon$-feasible iff $\max_{[s,e]} v - \min_{[s,e]} v \le 2\varepsilon = 2.0$ (the band $[\,\mu-\varepsilon,\mu+\varepsilon\,]$ must cover every point). Greedy "extend while feasible":

- Start at $v_1=10$. Range over $\{10\}=0$, add $10.5$ → range $0.5$, add $11$ → range $1.0$, add $11.8$ → range $1.8 \le 2.0$ ✓. Try $3$ → range $11{-}3=8.8 > 2.0$ ✗. **Commit segment 1** = indices $1..4$, value $\tfrac{11.8+10}{2}=10.9$.
- New segment at $v_5=3$. Add $3.2$ → range $0.2$ ✓, stream ends. **Commit segment 2**, value $3.1$.

Result: $k=2$ segments. Because feasibility here is **prefix-monotone** (any sub-interval of a feasible run is feasible), maximal-greedy is provably 1-competitive — it equals offline OPT. The hardness only appears under *bit*-minimization: if segments could share a coded value, committing index 4 to segment 1 versus starting a new segment early could change total bits, and no online rule is known to be constant-competitive there.

---
*Part of the [DBMS Research catalog](../../README.md).*
