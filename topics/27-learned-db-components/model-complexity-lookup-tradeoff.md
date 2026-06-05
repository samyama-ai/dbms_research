# Optimal Model Complexity vs. Lookup Cost

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/model-complexity-lookup-tradeoff` · **Status:** partially-solved

## 1. Problem Statement
A learned index splits total lookup cost into two terms: **model evaluation** (traverse/evaluate the model hierarchy) plus **last-mile search** (correct the prediction within error $\pm\varepsilon$). A larger, more segmented model shrinks $\varepsilon$ (cheaper last mile) but costs more to evaluate and store. The problem: **for a given key set and machine cost model, choose model size, number of segments, and hierarchy shape to minimize total expected lookup cost** under a space budget.

- **Optimization variant:** minimize $C(s) = c_{\text{eval}}(s) + c_{\text{search}}(\varepsilon(s))$ over segment count $s$ (and tree fan-out / number of RMI stages), subject to space $\le m$.
- **Decision variant:** is there a configuration achieving cost $\le \tau$ within budget $m$?
- **Construction variant:** compute the optimal piecewise-linear segmentation for target $\varepsilon$ efficiently.

Status is *partially-solved*: the segmentation subproblem is solved optimally; the *joint* hierarchy + hardware-aware optimization is heuristic.

## 2. Mathematical Foundations
For piecewise-linear approximation, the **minimum number of segments** achieving max-error $\varepsilon$ is computed optimally in $O(n)$ by the streaming convex-hull / O'Rourke algorithm — this is exactly what FITing-tree and PGM use. The tradeoff curve is governed by $\varepsilon(s)$, the error of the best $s$-segment PLA, a convex, data-dependent, decreasing function. Total cost (cache-aware) is
$$C(s) = \underbrace{\alpha \log_f s}_{\text{model traversal}} + \underbrace{\beta \log_2 \varepsilon(s)}_{\text{binary last mile}} + \underbrace{\gamma\,\varepsilon(s)}_{\text{cache-line scan}},$$
with constants $\alpha,\beta,\gamma$ from the memory hierarchy. Minimizing $C$ is a 1-D convex-ish search once $\varepsilon(s)$ is known. The PGM-index makes this **recursive**: each level is itself a learned index over the segment boundaries, giving an optimal multi-level structure. RMI fixes the hierarchy (typically 2 stages) and tunes branching empirically.

## 3. State of the Art (SOTA)
- **Theory:** PGM-index (Ferragina–Vinciguerra, VLDB 2020) — provably minimum segments per level via optimal PLA, recursively optimal in the PLA model. FITing-tree (Galakatos et al., SIGMOD 2019) — error-bounded segmentation with an explicit space/time knob.
- **Systems/empirical:** RMI (Kraska et al., 2018) with **CDFShop** (Marcus et al., DEEM 2020) auto-tunes RMI architecture (stage count, model types, branching) by search. SOSD provides the benchmark for measuring the realized tradeoff. Cost-model-driven auto-configuration is the systems frontier.

## 4. Upper Bound
Optimal $s$-segment PLA in $O(n)$ time (streaming convex hull); given $\varepsilon(s)$, the convex objective $C(s)$ is minimized in $O(\log s)$ or $O(s)$ by scan — so the *single-level* optimum is computable exactly and cheaply. PGM achieves the recursive optimum within the PLA class. CDFShop finds strong RMI configs but offers no optimality proof for the joint (architecture + hardware) problem.

## 5. Lower Bound
Any structure still inherits the $\Omega(\log n)$ comparison / $\Omega(\log_w n)$ cell-probe predecessor floor, so total cost cannot beat that asymptotically for adversarial data. The PLA-segmentation lower bound: achieving error $\varepsilon$ *requires* $\Omega(s^*(\varepsilon))$ segments where $s^*$ is the optimal count — so the space/error frontier is tight within the PLA class. The *joint* optimization over arbitrary model families and real memory hierarchies has **no proven hardness**; it is plausibly tractable but not characterized.

## 6. The Gap
Partly closed. The segmentation and single-level tradeoff are solved optimally; PGM is recursively optimal within piecewise-linear models. The remaining gap: (i) optimality when the model class is **not** PLA (splines, neural, radix), (ii) a **hardware-cost-model-exact** joint optimization of hierarchy shape and branching with guarantees, currently done by search (CDFShop). Closing it needs either a provably optimal joint configurator or a hardness result for the general version.

## 7. Current Research (as of June 2026)
- **Cost-model-driven auto-tuning** of learned-index architecture for specific CPU/cache/NVMe profiles *(frontier — verify)*.
- Mixed model families (spline + radix + linear) with optimal per-region selection *(frontier — verify)*.
- Compression-aware tradeoffs (compressed PGM) balancing space, eval, and search.
- Groups: Ferragina–Vinciguerra (Pisa); MIT DSAIL (RMI/CDFShop); TU Darmstadt (RadixSpline).

## 8. Future Work
- Provably optimal joint hierarchy + branching optimization under explicit memory models.
- Extend optimal segmentation guarantees beyond piecewise-linear to spline/neural classes.
- Online re-optimization as data and hardware change.

## 9. Key References
- **[Foundational]** T. Kraska, et al. *The Case for Learned Index Structures.* SIGMOD, 2018. — [arXiv](https://arxiv.org/abs/1712.01208)
- **[SOTA]** P. Ferragina, G. Vinciguerra. *The PGM-Index.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3389133.3389135)
- **[SOTA]** A. Galakatos, M. Markovitch, C. Binnig, R. Fonseca, T. Kraska. *FITing-Tree.* SIGMOD, 2019. — [arXiv](https://arxiv.org/abs/1801.10207)
- **[SOTA]** R. Marcus, E. Zhang, T. Kraska. *CDFShop: Exploring and Optimizing Learned Index Structures.* SIGMOD (demo), 2020. — [DOI](https://doi.org/10.1145/3318464.3384706)
- **[Foundational]** J. O'Rourke. *An On-Line Algorithm for Fitting Straight Lines Between Data Ranges.* CACM, 1981. — [DOI](https://doi.org/10.1145/358746.358758)

## 10. Worked Example

Take $n=10^8$ sorted keys, cache line = 64 B = 8 keys, so a last-mile scan of $\varepsilon$ keys costs $\gamma\varepsilon$ with $\gamma = 1/8$ cache miss per key. Suppose the best piecewise-linear approximation gives error $\varepsilon(s) = n/s$ for $s$ segments (each segment covers $n/s$ keys at error $\sim n/s$). Model traversal of a one-level array of $s$ segments is a single lookup: $\alpha\log_f s$ with $f=s$ (flat), so $\approx \alpha$, a constant. Then

$$C(s) \approx \alpha + \beta\log_2\!\frac{n}{s} + \gamma\frac{n}{s}.$$

Setting $dC/ds = 0$: $\;\dfrac{dC}{ds} = -\dfrac{\beta}{s\ln 2} + \beta\cdot 0 - \gamma\dfrac{n}{s^2}$. The dominant cache term $\gamma n/s$ drives the optimum: it shrinks until last-mile cost $\gamma\varepsilon \approx$ one cache line, i.e. $\varepsilon^\* \approx 8$, giving $s^\* \approx n/8 = 1.25\times10^7$ segments. Pushing $s$ higher buys no scan savings (already one line) but adds space; pushing lower makes the $\gamma n/s$ scan term explode. This is exactly the convex knee FITing-tree/PGM exploit: pick $\varepsilon$ near one cache line, then size the model to hit it.

---
*Part of the [DBMS Research catalog](../../README.md).*
