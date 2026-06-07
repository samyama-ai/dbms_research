---
id: 20-spatial-databases/spatial-selectivity-estimation
title: "Spatial selectivity estimation under skew"
topic: 20-spatial-databases
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Spatial selectivity estimation under skew

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/spatial-selectivity-estimation` · **Status:** open

## 1. Problem Statement
Given a relation $R$ of $n$ spatial objects (points, polygons, or trajectories) drawn from a highly skewed and correlated distribution over $\mathbb{R}^d$ (typically $d=2$ or $d=3$ plus time), and a query predicate $q$ (range / window, $k$NN radius, distance join, or arbitrary polygon containment/intersection), estimate the **selectivity** $\sigma(q) = |\{r \in R : r \models q\}| / n$ — and for join predicates, the join cardinality — within a *provable* relative or absolute error using a summary of size $s \ll n$.

Variants:
- **Counting (estimation):** return $\hat\sigma$ with guarantee $\Pr[|\hat\sigma - \sigma| > \varepsilon] < \delta$.
- **Optimization:** for a fixed budget $s$, minimize worst-case error over a query class $\mathcal{Q}$.
- **Decision/threshold:** distinguish $\sigma \ge \tau$ from $\sigma \le \tau/2$ (the form the optimizer actually needs for plan choice).

The hard core is *arbitrary polygon and trajectory predicates under skew*: the boundary of $q$ can cut through arbitrarily dense regions, so axis-aligned per-bucket uniformity assumptions break.

## 2. Mathematical Foundations
Let objects induce a measure $\mu$ on $\mathbb{R}^d$. A range-counting query is $\sigma(q)=\mu(q)$ for a query region $q$ in a range space $(\mathbb{R}^d, \mathcal{Q})$. Worst-case summary quality is governed by the **VC dimension** of $\mathcal{Q}$: for axis-aligned boxes $\mathrm{VC}=2d$; for halfspaces $\mathrm{VC}=d+1$; for $k$-gons it grows with $k$; for general semialgebraic predicates it is bounded via the number of sign conditions.

An **$\varepsilon$-approximation** $S$ satisfies $\sup_{q\in\mathcal{Q}}|\,|S\cap q|/|S| - \mu(q)\,| \le \varepsilon$; classical results give $|S|=O((\mathrm{VC}/\varepsilon^2)\log(1/\delta))$ by sampling, and deterministic $\varepsilon$-approximations of size $O((1/\varepsilon)^{2d/(d+1)})$ for boxes via discrepancy theory. **Relative** ($\varepsilon$-relative approximations) need sensitivity-weighted samples of size $\tilde O(\mathrm{VC}/(\varepsilon^2\sigma))$, which blows up exactly for the selective (small-$\sigma$) queries optimizers care about.

For trajectories, the predicate is over curves; the relevant range space is segments/stabbing, with VC dimension tied to the geometric complexity of the trajectory and the query corridor. Information-theoretic lower bounds follow from $\Omega(\mathrm{VC}/\varepsilon^2)$ sample complexity and from communication-complexity reductions for join-size estimation (AGM-style worst case for spatial joins).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** PostGIS/Oracle/SQL Server use 2-D equi-depth or self-tuning histograms (Min-Skew, GENHIST, ST-histograms). DBMS-X learned estimators (multidimensional models, e.g. deep autoregressive / Naru-style and DeepDB-style SPNs adapted to coordinates) lower average error but give no provable bound.
- **Theory-SOTA:** coresets and $\varepsilon$-approximations for range counting (Phillips; Matoušek discrepancy bounds), and sketch-based join-size estimation. Spatial-specific learned cardinality estimators for polygon/range predicates appeared at SIGMOD/VLDB 2021–2024 but evaluate empirically.

## 4. Upper Bound
For axis-aligned range counting, a sample / coreset of size $O(\varepsilon^{-2d/(d+1)})$ (deterministic, discrepancy) or $\tilde O(\varepsilon^{-2})$ (randomized, VC) yields additive $\varepsilon$ error in the **comparison/real-RAM model**. For arbitrary convex-polygon predicates with $\le k$ edges, additive-error summaries of size $\mathrm{poly}(k,1/\varepsilon)$ exist via VC bounds. No known summary of size sublinear in $1/\sigma$ achieves *relative* error for skewed selective polygon/trajectory predicates.

## 5. Lower Bound
Sample complexity $\Omega(\mathrm{VC}(\mathcal{Q})/\varepsilon^2)$ is information-theoretically necessary for additive $\varepsilon$ on the worst distribution; relative-error estimation of a query of true selectivity $\sigma$ needs $\Omega(1/(\varepsilon^2\sigma))$ samples. Spatial **join-size** estimation inherits set-intersection / index-evaluation communication lower bounds, and AGM gives worst-case output sizes that no summary can compress below without losing accuracy on adversarial inputs. These are unconditional (info-theoretic / communication), not SETH-conditional.

## 6. The Gap
For additive error the bounds essentially match. The genuine gap is **(a)** relative-error guarantees for highly selective predicates — the $1/\sigma$ blowup makes provable estimators impractical exactly where the optimizer is most sensitive; and **(b)** the absence of any worst-case guarantee for the *learned* estimators that win empirically. Closing it requires either instance-optimal (distribution-adaptive) bounds that beat worst-case VC on real skew, or a learned estimator with a certified error envelope.

## 7. Current Research (as of June 2026)
Active threads: instance-/distribution-adaptive coresets that exploit fractal/intrinsic dimension of real spatial data; calibration and conformal-prediction wrappers giving *post-hoc* coverage guarantees on learned spatial estimators *(frontier — verify)*; query-driven (workload-aware) summaries with PAC-style bounds; and trajectory-specific sketches over corridor predicates. Groups around Suciu/Re (probabilistic/learned CE), Phillips (geometric coresets), and spatial-DB groups (Mokbel, Sacharidis, Aref) are relevant; several 2024–2025 SIGMOD/VLDB learned-spatial-CE papers report large average-error wins but no tail guarantees *(frontier — verify)*.

## 8. Future Work
- Relative-error summaries whose size depends on *intrinsic* rather than ambient dimension.
- Certified learned estimators (monotone/Lipschitz architectures with provable envelopes).
- Selectivity estimation for trajectory and spatiotemporal predicates with motion/uncertainty models.
- Estimator robustness under data drift and adversarial query workloads.

## 9. Key References
- **[Foundational]** Selinger et al. *Access Path Selection in a Relational DBMS.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Acharya, Poosala, Ramaswamy. *Selectivity Estimation in Spatial Databases.* SIGMOD, 1999. — [DOI](https://doi.org/10.1145/304182.304184)
- **[Foundational]** Matoušek. *Geometric Discrepancy.* Springer, 1999 (deterministic $\varepsilon$-approximations). — [DOI](https://doi.org/10.1007/978-3-642-03942-3)
- **[SOTA]** Phillips. *Coresets and Sketches.* In *Handbook of Discrete and Computational Geometry*, 3rd ed., 2017. — [arXiv](https://arxiv.org/abs/1601.00617)
- **[SOTA]** Yang et al. *Deep Unsupervised Cardinality Estimation (Naru).* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1905.04278)
- **[Survey]** Har-Peled. *Geometric Approximation Algorithms.* AMS, 2011. — [AMS](https://bookstore.ams.org/surv-173)

## 10. Worked Example

Suppose $R$ has $n=1000$ points, with $990$ packed inside a tiny dense city block $B=[0,1]^2$ and $10$ scattered over the rest of a $[0,100]^2$ map. Query $q$ is the range $[0.4,0.6]^2$ — a small window deep inside the dense block.

**Uniform-per-bucket assumption.** A coarse $10\times10$ equi-width grid puts all $990$ city points in one $10\times10$ cell of area $100$. Assuming uniformity inside that cell, the optimizer estimates $\hat\sigma = 990 \cdot \frac{0.04}{100} \cdot \frac{1}{1000}\approx 0.0004$, i.e. $\approx 0.4$ rows. The true answer might be $300$ rows. The skew inside the bucket destroys the estimate.

**Sample-complexity view.** True selectivity here is $\sigma = 300/1000 = 0.3$. For *additive* error $\varepsilon=0.05$ on axis-boxes ($\mathrm{VC}=2d=4$), a uniform sample of $O(\mathrm{VC}/\varepsilon^2)\approx 4/0.0025 = 1600$ points suffices. But for a *relative* $\varepsilon=0.1$ guarantee on a highly selective query with $\sigma=0.001$, the bound $\tilde O(1/(\varepsilon^2\sigma)) = 1/(0.01\cdot0.001)=10^5$ samples already exceeds $n$ — the $1/\sigma$ blowup of Section 5 in action.

---
*Part of the [DBMS Research catalog](../../README.md).*
