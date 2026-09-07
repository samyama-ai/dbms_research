---
id: 17-approximate-query-processing/mergeable-summaries-bounds
title: "Mergeable Summaries Lower Bounds"
topic: 17-approximate-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Mergeable Summaries Lower Bounds

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/mergeable-summaries-bounds` · **Status:** partially-solved
> **Verification note:** In the Section 10 Misra–Gries example the 4th element of each stream triggers a decrement-and-evict, so node A reduces to {a:1} and node B to {d:1} (not {a:2,b:1}/{d:2,a:1}); the stated post-processing intermediate counts should be recomputed.

## 1. Problem Statement
A summary (synopsis) is **mergeable** if two summaries of datasets $A$ and $B$ — each built with no knowledge of the other — can be combined into one summary of $A\uplus B$ with the *same size and error guarantee*, and the merge can be applied recursively over an arbitrary tree (distributed/streaming-friendly). Mergeability is strictly stronger than streamability: it forbids any blow-up across merges of equal-sized inputs.

The problem: determine **tight space lower bounds** for fully mergeable summaries answering three canonical queries to error $\varepsilon$ with failure probability $\delta$:
1. **$\varepsilon$-approximate quantiles** (rank error $\le \varepsilon n$),
2. **$\varepsilon$-heavy hitters** (report items with frequency $\ge \varepsilon n$, no false item below $(\varepsilon-\varepsilon')n$),
3. **distinct counts** (relative error $\varepsilon$ on $|{\rm distinct}|$).

We want matching upper/lower bounds on summary size $m(\varepsilon,\delta,n)$ under the mergeable model — distinguishing *deterministic* from *randomized* and *comparison-based* from *general* summaries.

## 2. Mathematical Foundations
The mergeable model (Agarwal–Cormode–Huang–Phillips–Wei–Yi, PODS 2012/TODS 2013) formalizes a class $\mathcal{C}$ of summaries closed under a merge operator $\mathrm{merge}:\mathcal{C}\times\mathcal{C}\to\mathcal{C}$ with $\mathrm{size}(\mathrm{merge}(S_A,S_B))\le f(\varepsilon,\delta)$ independent of merge depth.

For quantiles, the GK summary (Greenwald–Khanna 2001) gives $O(\tfrac{1}{\varepsilon}\log\varepsilon n)$ but is **not** known to be mergeable; the breakthrough mergeable quantile result achieves $O(\tfrac{1}{\varepsilon}\log^{1.5}\tfrac{1}{\varepsilon})$ deterministically and $O(\tfrac{1}{\varepsilon}\log\log\tfrac{1}{\delta})$ randomized via KLL (FOCS 2016). The $\Omega(\tfrac1\varepsilon\log\tfrac1\varepsilon)$ comparison-based lower bound matches up to log factors.

For distinct counts, sketches occupy $\Theta(\tfrac1{\varepsilon^2}+\log n)$ bits (Kane–Nelson–Woodruff, PODS 2010 optimal $F_0$); HLL's $\Theta(\tfrac1{\varepsilon^2}\log\log n)$ is near-optimal and inherently mergeable (max-merge). Heavy hitters rest on the $F_\infty$/frequency-moment communication framework.

## 3. State of the Art (SOTA)
- **Quantiles:** KLL is the SOTA mergeable summary, $O(\tfrac1\varepsilon\log\log\tfrac1\delta)$ randomized, fully mergeable; deterministic GK-mergeable variants and the "ReqSketch" (relative-error quantiles, Cormode–Karnin–Liberty–Thaler–Veselý, PODS 2021) extend to relative error.
- **Heavy hitters:** Misra–Gries and SpaceSaving are mergeable with $O(1/\varepsilon)$ counters; CountSketch/CM give randomized mergeable variants.
- **Distinct counts:** HLL and the **CPC sketch** (Compressed Probabilistic Counting, DataSketches) approach the entropy lower bound.

## 4. Upper Bound
- Quantiles: $O\!\big(\tfrac1\varepsilon\log\log\tfrac1\delta\big)$ words (KLL), fully mergeable; relative-error $O(\tfrac1\varepsilon\log^{1.5}(\varepsilon n))$ (ReqSketch).
- Heavy hitters: $O(1/\varepsilon)$ counters (Misra–Gries), mergeable with bounded error accumulation $\le \varepsilon n$.
- Distinct counts: $O(\tfrac1{\varepsilon^2}\log\log n + \log n)$ bits (HLL/CPC); the $F_0$-optimal $O(\tfrac1{\varepsilon^2}+\log n)$ bits exists but with weaker practical merge structure.

## 5. Lower Bound
- Quantiles: $\Omega(\tfrac1\varepsilon)$ trivially; $\Omega(\tfrac1\varepsilon\log\tfrac1\varepsilon)$ for deterministic comparison-based mergeable summaries — within a $\sqrt{\log(1/\varepsilon)}$ factor of the upper bound.
- Distinct counts: $\Omega(\tfrac1{\varepsilon^2}+\log n)$ bits (Indyk–Woodruff / Kane–Nelson–Woodruff via Gap-Hamming and communication complexity); matches HLL up to the $\log\log n$ factor.
- Heavy hitters: $\Omega(1/\varepsilon)$ space from set-disjointness reductions.

## 6. The Gap
Distinct counts are essentially **closed** ($\Theta(\tfrac1{\varepsilon^2})$). Heavy hitters are closed up to constants. Quantiles remain genuinely open: the deterministic mergeable gap is a $\sqrt{\log(1/\varepsilon)}$ (or $\log^{1.5}$ vs. $\log$) factor, and whether *deterministic* mergeable quantiles can match the randomized $O(\tfrac1\varepsilon)$ is unresolved. Closing it needs either a smaller deterministic merge construction or a stronger comparison-tree lower bound.

## 7. Current Research (as of June 2026)
Relative-error and weighted/streaming variants (ReqSketch, DDSketch) are actively refined. *(frontier — verify)* Recent work tightens deterministic quantile merge constants and studies mergeability under differential privacy and under sliding windows; private mergeable summaries (Smith, Thakurta et al.) are an active frontier. Groups: Phillips/Yi/Cormode/Karnin/Liberty lineage; DataSketches contributors.

## 8. Future Work
- Close the deterministic mergeable quantile gap.
- Mergeable summaries simultaneously optimal for quantiles + heavy hitters + distinct counts (multi-objective synopses).
- Private and adversarially-robust mergeable summaries with matching bounds.

## 9. Key References
- **[Foundational]** Agarwal, P.K., Cormode, G., Huang, Z., Phillips, J., Wei, Z., Yi, K. *Mergeable Summaries.* PODS 2012 / ACM TODS 2013. — [DOI](https://doi.org/10.1145/2500128)
- **[SOTA]** Karnin, Z., Lang, K., Liberty, E. *Optimal Quantile Approximation in Streams (KLL).* FOCS 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** Cormode, G., Karnin, Z., Liberty, E., Thaler, J., Veselý, P. *Relative Error Streaming Quantiles (ReqSketch).* PODS 2021. — [arXiv](https://arxiv.org/abs/2004.01668)
- **[Foundational]** Kane, D., Nelson, J., Woodruff, D. *An Optimal Algorithm for the Distinct Elements Problem.* PODS 2010. — [DOI](https://doi.org/10.1145/1807085.1807094)
- **[Foundational]** Greenwald, M., Khanna, S. *Space-Efficient Online Computation of Quantile Summaries.* SIGMOD 2001. — [DOI](https://doi.org/10.1145/375663.375670)

## 10. Worked Example

**Misra–Gries mergeability for heavy hitters.** Take $\varepsilon=1/3$, so each summary keeps $k-1=2$ counters ($k=\lceil 1/\varepsilon\rceil=3$). Two nodes summarize disjoint streams.

Node $A$, stream $[a,a,b,c]$ (n=4). MG keeps top counters: after processing, $\{a:2, b:1\}$ ($c$ caused a decrement-and-evict). Node $B$, stream $[a,d,d,e]$ (n=4): $\{d:2, a:1\}$.

**Merge:** add counters elementwise → $\{a:3, b:1, d:2, e:0\}$, then keep the $k-1=2$ largest and subtract the $(k)$-th largest value from all (the MG merge rule). The 3rd-largest count is $1$ (b's), so subtract $1$: $\{a:2, d:1\}$, drop non-positive entries.

True frequencies over $A\uplus B$ ($n=8$): $a=3,d=2,b=1,c=1,e=1$. The merged summary reports $a$ (est $2$, true $3$) and $d$ (est $1$, true $2$) — each underestimate is within $\varepsilon n = 8/3 \approx 2.67$, and every item with true frequency $\ge \varepsilon n=2.67$ (only $a$, at $3$) is retained. Size stayed at $2$ counters across the merge — the defining no-blowup property of Section 1, achieved with the $O(1/\varepsilon)$ space of Section 4.

---
*Part of the [DBMS Research catalog](../../README.md).*
