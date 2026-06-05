# Sliding-window distinct counting space bounds

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/sliding-window-distinct-count` · **Status:** partially-solved

## 1. Problem Statement

Given a stream of elements from a universe $[m]$, maintain an estimate of the number of **distinct** elements among those that fall within the most recent window — either the last $N$ arrivals (**sequence-based**) or those with timestamp in $[\text{now}-w, \text{now}]$ (**time-based**). The estimate must be available at any query time and updated incrementally, using as little memory as possible.

This is the **sliding-window $F_0$ / distinct-count** problem. Exact counting requires storing the window, so the interesting regime is **approximate**: report $\hat{D}$ with $(1\pm\epsilon)$ relative error and failure probability $\le \delta$.

Variants:
- **Counting:** estimate $|\{\text{distinct in window}\}|$.
- **Decision:** is the window's distinct count above a threshold?
- **Sequence- vs. time-based** windows (the latter has a variable number of elements).
- **Insertion-only** within the window vs. with explicit deletions (turnstile) — the latter overlaps with the "sketches under deletions" problem.

The central question is the **tight space complexity** $\Theta(?)$ as a function of $\epsilon$, $\delta$, window size $N$ (or universe $m$), and word size.

## 2. Mathematical Foundations

In the unbounded (non-windowed) model, distinct counting ($F_0$) is solved in $O(\epsilon^{-2}\log m + \log m)$ bits by the optimal **Kane–Nelson–Woodruff** sketch (2010), matching the $\Omega(\epsilon^{-2} + \log m)$ lower bound. HyperLogLog (Flajolet et al. 2007) gives the practical $O(\epsilon^{-2}\log\log m)$-bit estimator.

Sliding windows are harder because old elements **expire**, and an element re-occurring inside the window must not be double-counted. The key technique is the **smooth histogram / exponential histogram** framework (Datar–Gionis–Indyk–Motwani 2002; Braverman–Ostrovsky 2007): maintain $O(\frac{1}{\epsilon}\log N)$ "buckets" / sub-window sketches at geometric scales so any window suffix's statistic is approximable. A function is *smooth* if when a suffix's value is $(1-\beta)$-close to the whole, it stays close as elements expire — $F_0$ is smooth, enabling the framework.

For distinct counting specifically, **distinct sampling / $\ell_0$-sampling** with timestamp-aware retention (keep, for each sampled hash level, the most recent occurrence) yields windowed estimators; Gibbons–Tirthapura "distinct counting over sliding windows" (2002) gives the classic construction. Information-theoretically, the window must distinguish many possible distinct-sets, forcing $\Omega(\epsilon^{-2})$ counter bits plus $\Omega(\log N)$ for expiry bookkeeping.

## 3. State of the Art (SOTA)

- **Gibbons, Tirthapura.** *Distributed Streams Algorithms for Sliding Windows.* (SPAA 2002): first distinct-count-over-sliding-window with provable bounds.
- **Datar, Gionis, Indyk, Motwani** (SODA/SICOMP 2002): **exponential histograms** — $(1\pm\epsilon)$ sum/count and basic statistics over sliding windows in $O(\frac{1}{\epsilon}\log^2 N)$ bits; foundational for windowed $F_0$.
- **Braverman, Ostrovsky** (FOCS 2007): **smooth histograms** — generalize EH to a broad class including $F_p$ and distinct counts, with $O(\frac{1}{\epsilon}\log N)$ sub-sketches.
- **Kane, Nelson, Woodruff** (PODS 2010): optimal $F_0$ in the unbounded model — the per-window sub-sketch SOTA.
- **Systems SOTA:** **Sliding HyperLogLog** (Chabchoub, Hébrail 2010) and time-windowed HLL variants; widely used in practice for approximate windowed distinct counts.

## 4. Upper Bound

Combining smooth histograms with optimal $F_0$ sub-sketches gives windowed distinct counting in
$$O\!\left(\frac{1}{\epsilon}\log N \cdot \left(\frac{1}{\epsilon^2} + \log m\right)\right) \text{ bits (roughly } \tilde{O}(\epsilon^{-3}\log N)\text{)},$$
for $(1\pm\epsilon)$ relative error with constant success probability (boost to $1-\delta$ by $O(\log\frac{1}{\delta})$ repetition), in the **insertion-only sliding-window model**. Distinct-sampling/timestamp-retention constructions (Gibbons–Tirthapura) achieve comparable $\tilde{O}(\epsilon^{-2}\log N \log m)$ bounds. Practical Sliding-HLL uses $O(\epsilon^{-2}\log\log m)$-style registers with timestamped maxima, far smaller in constants though without the cleanest worst-case guarantee.

## 5. Lower Bound

- **$\Omega(\epsilon^{-2} + \log m)$** bits is inherited from the unbounded $F_0$ lower bound (Kane–Nelson–Woodruff; Indyk–Woodruff; Alon–Matias–Szegedy gap-Hamming reductions): even a single window query needs this.
- **Sliding-window penalty:** windowed problems generally require an extra $\Omega(\frac{1}{\epsilon}\log N)$ factor over the unbounded version (DGIM-style lower bounds), because the algorithm must be able to answer for *every* window boundary; this is shown via reductions from indexing/augmented-indexing in **communication complexity**.
- For the smooth-histogram class the $\Omega(\frac{1}{\epsilon}\log N)$ number of necessary checkpoints is essentially tight, so the leading $\frac{1}{\epsilon}\log N$ factor is not removable in general.

## 6. The Gap

**Partially solved.** The window dependence ($\log N$) and the base $F_0$ dependence ($\epsilon^{-2}$, $\log m$) each match known lower bounds, but their **product** in the best upper bound is not known to be necessary. Specifically, whether windowed distinct counting truly needs $\tilde{\Theta}(\epsilon^{-3}\log N)$ or can be done in $\tilde{O}(\epsilon^{-2}\log N)$ (matching the sum of the two lower bounds rather than their product) is **open**. The gap is the extra $1/\epsilon$ factor from running an $\epsilon$-accurate sub-sketch at each of $O(\frac{1}{\epsilon}\log N)$ smooth-histogram checkpoints. A tight bound would either improve the sub-sketch sharing across checkpoints or prove a matching $\Omega(\epsilon^{-3})$-style lower bound.

## 7. Current Research (as of June 2026)

- **Sub-sketch sharing across checkpoints:** reducing the $\frac{1}{\epsilon}\times\frac{1}{\epsilon^2}$ product by maintaining a single mergeable distinct sketch with timestamp annotations rather than independent per-bucket sketches *(frontier — verify)*.
- **Adversarially robust** windowed distinct counting (where future input depends on past estimates) — extending Ben-Eliezer–Jayaram–Woodruff–Yogev robust-sketching to sliding windows *(frontier — verify)*.
- **Practical bias-corrected Sliding-HLL** and time-decayed cardinality estimators with tighter empirical error.
- Distinct counting under both **expiry and deletions** (links to the sketches-under-deletions problem).
- Active researchers: Woodruff, Nelson, Braverman (theory); Cormode, Ting (practical sketches); Tirthapura/Gibbons lineage.

## 8. Future Work

- Close the $\epsilon^{-2}$-vs-$\epsilon^{-3}$ gap with either a better algorithm or a matching lower bound.
- Mergeable, distributed windowed distinct sketches with optimal communication.
- Unified estimator handling time-based windows with variable element counts at tight space.
- Robustness against adaptive adversaries with provable error.
- Tight bounds in the turnstile (deletion-allowing) sliding-window model.

## 9. Key References

- **[Foundational]** Datar, Gionis, Indyk, Motwani. *Maintaining Stream Statistics over Sliding Windows.* SIAM J. Comput., 2002.
- **[Foundational]** Gibbons, Tirthapura. *Distributed Streams Algorithms for Sliding Windows.* SPAA, 2002.
- **[SOTA]** Braverman, Ostrovsky. *Smooth Histograms for Sliding Windows.* FOCS, 2007.
- **[SOTA]** Kane, Nelson, Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS, 2010.
- **[Foundational]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA, 2007.
- **[SOTA]** Chabchoub, Hébrail. *Sliding HyperLogLog: Estimating Cardinality in a Data Stream over a Sliding Window.* ICDM Workshops, 2010.

---
*Part of the [DBMS Research catalog](../../README.md).*
