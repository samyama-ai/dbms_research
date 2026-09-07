---
id: 17-approximate-query-processing/approximate-topk-heavy-hitters
title: "Approximate Top-K and Heavy Hitters"
topic: 17-approximate-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Approximate Top-K and Heavy Hitters

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/approximate-topk-heavy-hitters` · **Status:** partially-solved

## 1. Problem Statement

Given a stream (or large relation) of items with frequencies/weights, identify in **one pass** the heavy hitters — items whose frequency exceeds a threshold $\phi N$ — and/or the **top-$k$** most frequent items, with explicit guarantees on (a) false positives / false negatives, (b) frequency-estimation error, and (c) rank error, while using space sublinear in the universe size $n$ and ideally in the stream length $N$.

Variants:
- **$(\phi,\varepsilon)$-heavy-hitters (decision/reporting):** report every item with $f_i > \phi N$, none with $f_i < (\phi-\varepsilon)N$.
- **Top-$k$ (optimization):** return $k$ items minimizing rank/frequency error vs. the true top-$k$.
- **$\ell_1$ vs. $\ell_2$ guarantee:** error bounded by $\varepsilon\|f\|_1$ (Misra–Gries / CountMin) vs. the stronger $\varepsilon\|f\|_2$ (CountSketch), which is far better for skewed data.
- **Turnstile (insert/delete)** vs. **cash-register (insert-only)**.

## 2. Mathematical Foundations

Let $f \in \mathbb{Z}_{\ge 0}^n$ be the frequency vector, $N=\|f\|_1$. An **$\varepsilon$-approximate frequency oracle** returns $\hat f_i$ with $|\hat f_i - f_i| \le \varepsilon\|f\|_p$.

- **Misra–Gries (1982):** deterministic, $O(1/\varepsilon)$ counters, gives $f_i - \varepsilon N \le \hat f_i \le f_i$ — an $\ell_1$ guarantee, insert-only.
- **Count-Min Sketch** (Cormode–Muthukrishnan, 2005): $d\times w$ table, $w=\lceil e/\varepsilon\rceil$, $d=\lceil\ln(1/\delta)\rceil$; $\hat f_i \le f_i + \varepsilon\|f\|_1$ w.p. $1-\delta$; supports turnstile.
- **Count-Sketch** (Charikar–Chen–Farach-Colton, 2002): signed estimator with $\ell_2$ guarantee $|\hat f_i - f_i| \le \varepsilon\|f\|_2$ — strictly stronger on heavy-tailed data, where $\|f\|_2 \ll \|f\|_1$.

The **$\ell_2$ heavy-hitter** problem (find $i$ with $f_i \ge \varepsilon\|f\|_2$) is the gold standard; the **ExpanderSketch / BPTree** (Larsen–Nelson–Nguyen–Thorup; Braverman et al., 2017) achieve it in near-optimal space and time. Rank error connects to **$\varepsilon$-approximate quantiles** (GK, KLL), since top-$k$ by frequency is a selection on the frequency distribution.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** **BPTree** (Braverman, Chestnut, Ivkin, Nelson, Wang, Woodruff, COLT 2017) solves $\ell_2$ heavy hitters in $O(\varepsilon^{-2}\log n)$ words with fast per-update time; **ExpanderSketch** (Larsen, Nelson, Nguyen, Thorup, FOCS 2016) gives optimal space with fast decode in turnstile. For quantiles/rank, **KLL** (Karnin–Lang–Liberty, FOCS 2016) is optimal: $O(\varepsilon^{-1}\log\log(1/\delta))$ space.
- **Systems-SOTA:** **Count-Min** and **Misra–Gries / SpaceSaving** (Metwally–Agrawal–El Abbadi, 2005) are the deployed workhorses (Apache DataSketches, Redis, network telemetry). **SpaceSaving** gives the tightest deterministic top-$k$ in practice; recent cache-aware/SIMD variants (e.g. Augmented Sketch, Cold Filter, ElasticSketch — Yang et al., SIGCOMM 2018) optimize accuracy-per-byte for skewed traffic.

## 4. Upper Bound

- $\ell_1$ heavy hitters: $\Theta(1/\varepsilon)$ counters (Misra–Gries / SpaceSaving), deterministic, optimal.
- $\ell_2$ heavy hitters, turnstile: $O(\varepsilon^{-2}\log n)$ words (ExpanderSketch/BPTree), with $\mathrm{poly}(\log n)$ update/report time.
- Quantile/rank for top-$k$ ordering: KLL achieves $O(\varepsilon^{-1}\log\log(1/\delta))$ words for additive rank error $\varepsilon N$.

## 5. Lower Bound

- Any algorithm reporting $\varepsilon$-$\ell_1$ heavy hitters needs $\Omega(1/\varepsilon)$ counters (pigeonhole / communication).
- $\ell_2$ heavy hitters in turnstile require $\Omega(\varepsilon^{-2}\log n)$ bits — matching BPTree — via a reduction from **Augmented Indexing** / one-way communication complexity (and INDEX/DISJOINTNESS arguments).
- Comparison-based / **multi-pass** lower bounds: exact top-$k$ or exact heavy hitters is impossible in $o(n)$ space (must store the universe), an information-theoretic Ω-bound; hence approximation is mandatory.
- For quantiles, $\Omega(\varepsilon^{-1}\log(1/\delta))$ comparisons-style and space lower bounds nearly match KLL.

## 6. The Gap

For the canonical $\ell_1$ and $\ell_2$ heavy-hitter problems the gap is **closed** up to constants/log factors (matching upper and lower bounds). The *partially-solved* status reflects the remaining frontier: (i) **simultaneous** tight bounds on false-positive/negative **and** rank error in a single one-pass structure (most methods bound frequency error, then *infer* rank, losing tightness); (ii) **distributed / sliding-window / duplicate-resilient** settings where constants and log factors are not pinned down; (iii) heavy hitters under **adversarial robustness** (an adaptive querier), where recent work shows extra cost is sometimes necessary.

## 7. Current Research (as of June 2026)

Active: **adversarially robust** streaming HH and the price of robustness (Ben-Eliezer, Jayaram, Woodruff, Yogev and successors); **learning-augmented** sketches that use a predictor of which items are heavy to cut error/space (Hsu–Indyk–Katabi–Vakilian, ICLR 2019, and 2024-25 refinements) *(frontier — verify)*; differentially private heavy hitters at scale (Apple/Google deployments, local-DP). Systems side: SmartNIC/programmable-switch sketches for line-rate telemetry (ElasticSketch lineage) and GPU sketch kernels. Groups: Woodruff (CMU), Nelson (Berkeley), Cormode (Warwick/Meta), Yang's sketch group (Peking U), Indyk (MIT).

## 8. Future Work

- A single one-pass synopsis with *jointly* tight FP/FN and rank-error guarantees.
- Tight constants for sliding-window and fully-distributed heavy hitters.
- Robust + private heavy hitters with provably minimal overhead.
- Principled learning-augmented sketches whose guarantees degrade gracefully when the predictor is wrong.

## 9. Key References

- **[Foundational]** J. Misra, D. Gries. *Finding Repeated Elements.* Science of Computer Programming, 1982. — [DOI](https://doi.org/10.1016/0167-6423(82)90012-0)
- **[Foundational]** G. Cormode, S. Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch and its Applications.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Foundational]** M. Charikar, K. Chen, M. Farach-Colton. *Finding Frequent Items in Data Streams (CountSketch).* ICALP, 2002. — [DBLP](https://dblp.org/rec/conf/icalp/CharikarCF02.html)
- **[SOTA]** V. Braverman, S. R. Chestnut, N. Ivkin, J. Nelson, Z. Wang, D. P. Woodruff. *BPTree: An $\ell_2$ Heavy Hitters Algorithm Using Constant Memory.* COLT/PODS, 2017. — [arXiv](https://arxiv.org/abs/1603.00759)
- **[SOTA]** Z. Karnin, K. Lang, E. Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** T. Yang et al. *Elastic Sketch: Adaptive and Fast Network-wide Measurements.* SIGCOMM, 2018. — [DOI](https://doi.org/10.1145/3230543.3230544)
- **[Survey]** G. Cormode, M. Hadjieleftheriou. *Finding Frequent Items in Data Streams.* VLDB, 2008. — [DOI](https://doi.org/10.14778/1454159.1454225)

## 10. Worked Example

Run **Misra–Gries** with $k-1=2$ counters (so $1/\varepsilon=k=3$, i.e. $\varepsilon=1/3$) on the stream
$$a,\,b,\,a,\,c,\,a,\,b,\,d,\,a.$$
Processing each item: increment its counter if tracked; else if a free slot exists, start it at 1; else decrement **all** counters and drop any hitting 0.

| item | state after |
|------|-------------|
| a | a:1 |
| b | a:1, b:1 |
| a | a:2, b:1 |
| c | (no slot) decrement all → a:1; new c… a:1, c:1 |
| a | a:2, c:1 |
| b | (no slot) decrement all → a:1 (c dropped); new b… a:1, b:1 |
| d | (no slot) decrement all → all 0, dropped |
| a | a:1 |

Final counters: $a:1$. Guarantee: $\hat f_i \ge f_i - \varepsilon N$ with $N=8$, $\varepsilon N \approx 2.67$. True $f_a=4$; reported lower bound $f_a \ge 4-2.67=1.33$, consistent with $\hat f_a=1$ understating but never over. Any true heavy hitter with $f_i > \varepsilon N = 2.67$ — here only $a$ — is guaranteed to survive in the table, illustrating the $O(1/\varepsilon)$-counter $\ell_1$ guarantee.

---
*Part of the [DBMS Research catalog](../../README.md).*
