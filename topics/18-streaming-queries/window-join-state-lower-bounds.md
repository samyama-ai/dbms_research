---
id: 18-streaming-queries/window-join-state-lower-bounds
title: "Lower bounds for window-join state"
topic: 18-streaming-queries
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Lower bounds for window-join state

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/window-join-state-lower-bounds` · **Status:** partially-solved

## 1. Problem Statement
For a windowed equi-join $R \bowtie_{R.a=S.a} S$ over two streams restricted to a sliding window of $W$ tuples (or a time window of duration $\tau$), determine the minimum *state* (memory) any algorithm must keep to produce correct output as tuples arrive and expire.

Variants:
- **Exact full output:** emit every join result whose operands are simultaneously in-window.
- **Exact existence/count (decision/counting):** report only whether (or how many) matches exist per probe.
- **Approximate:** estimate the windowed join size (or sample its output) within relative error $\varepsilon$.
- **Sliding vs. tumbling vs. session windows;** **single-pass** vs. limited passes; one-sided (probe-only) vs. symmetric.

The question is to pin matching **upper bounds** (algorithms) and **lower bounds** (space/communication) for each variant, separating exact from approximate.

## 2. Mathematical Foundations
**AGM bound** (Atserias–Grohe–Marx): the output of a join is bounded by the fractional-edge-cover number; for a binary equi-join, output size $\le |R|\cdot|S|$ but can be as small as $\Theta(\max(|R|,|S|))$ — the *worst-case-optimal* perspective dictates how much intermediate state is unavoidable when the output itself is large. For a sliding window, the in-window relations have size $\le W$, so worst-case output is $\Theta(W^2)$; any algorithm that materializes a hash table on the join key uses $\Theta(W)$ state, optimal up to the need to retain expiring tuples.

**Communication complexity** gives space lower bounds in the streaming model. Reductions from **INDEX** and **(multi-party) SET-DISJOINTNESS** show that deciding whether two windowed sets intersect requires $\Omega(W)$ bits in one pass; estimating windowed join size relates to $F_2$/inner-product estimation (AMS sketch) with $\Omega(1/\varepsilon^2)$ and $\Omega(\log)$ dependencies. The **smooth-histogram / exponential-histogram** framework (Datar–Gionis–Indyk–Motwani; Braverman–Ostrovsky) characterizes which functions admit $\text{poly}(\log W, 1/\varepsilon)$ sliding-window sketches; join-size is *not* smooth in general, which is the source of stronger lower bounds.

Formally: maintaining the exact join over a window where each key's multiplicity may change forces retaining per-key counts — by an INDEX reduction on the key domain $[U]$, $\Omega(\min(W, U))$ bits.

## 3. State of the Art (SOTA)
- **Symmetric Hash Join / windowed hash join** (Wilschut–Apers; STREAM, TelegraphCQ): $O(W)$ state, the standard exact algorithm — and provably near-optimal for exact output.
- **AMS / $F_2$ sketches for join-size estimation** (Alon, Gibbons, Matias, Szegedy, PODS 1999; "Tracking Join and Self-Join Sizes," PODS 1999): $O(\varepsilon^{-2}\log\delta^{-1})$ space estimators; **sketch sharing** for multiple joins (Dobra, Garofalakis, Gehrke, Rastogi, SIGMOD 2002).
- **Sliding-window sketches:** Datar–Gionis–Indyk–Motwani exponential histograms (SODA/SICOMP 2002); smooth histograms (Braverman–Ostrovsky, FOCS 2007) for windowed aggregates.
- **Random sampling over windows / join sampling:** priority and random-pairing sampling for windowed join output.
- Systems-SOTA: Flink/Spark interval and window joins keep $O(W)$ state with watermark-driven expiry; theory-SOTA is the sketch line for approximate join size.

## 4. Upper Bound
**Exact windowed equi-join:** symmetric hash join with per-key buckets and time-ordered expiry uses $O(W)$ words of state and $O(1)$ amortized update plus $O(\text{matches})$ output — optimal up to output. **Approximate join size:** AMS-style sketches estimate $|R\bowtie S|$ within $(1\pm\varepsilon)$ using $O(\varepsilon^{-2}\log(1/\delta))$ space; over sliding windows, exponential/smooth histograms lift these to $O(\varepsilon^{-1}\,\text{polylog}\,W)$ for smooth functions. These hold in the single-pass insertion (or sliding-window) streaming model.

## 5. Lower Bound
**Exact:** by reduction from **INDEX** / **SET-DISJOINTNESS**, deciding whether a windowed join is non-empty (let alone enumerating it) requires $\Omega(\min(W,U))$ bits in one pass — so $O(W)$ state is tight up to the key-domain factor. **Approximate:** estimating $F_2$/inner-product (and hence join size) within $\varepsilon$ requires $\Omega(\varepsilon^{-2})$ space (Woodruff; via GAP-HAMMING / multi-party disjointness), and any sliding-window relative-error estimator of a non-smooth function inherits an extra $\Omega(\log W)$ or worse. These are communication-complexity / information-theoretic lower bounds in the data-stream model; no NP-hardness is involved (the hardness is space, not time).

## 6. The Gap
For the *core* binary exact windowed equi-join the gap is essentially **closed**: $\Theta(W)$ state (matching upper and lower bounds modulo the key-domain term). The genuinely **open** parts are: (i) tight space for *multi-way* windowed joins under AGM/worst-case-optimal expiry (how much intermediate state is unavoidable across $\ge 3$ streams with different windows); (ii) tight sliding-window space for *approximate* join size of non-smooth functions, where upper and lower bounds differ by polylog/$\varepsilon$ factors; (iii) lower bounds under **out-of-order/late** arrivals, where retraction of expired-then-late tuples may force extra state. Closing these needs new communication reductions (multi-party, with deletions) and matching sketch constructions.

## 7. Current Research (as of June 2026)
- Worst-case-optimal *streaming/window* multi-way joins extending NPRR/Leapfrog Triejoin to sliding windows *(frontier — verify)*.
- Sliding-window join-size and distinct-element sketches with deletions/retractions (turnstile windowed model).
- Fine-grained space–time trade-offs for window joins tied to OMv/3SUM-style conjectures *(frontier — verify)*.
- Sketch sharing across many windowed joins (links to multi-query optimization).

## 8. Future Work
- Tight multi-way windowed-join state bounds via AGM in the streaming model.
- Lower bounds incorporating out-of-order arrival and late-event retraction.
- Two-sided (insert+delete) sliding-window join sketches with optimal $\varepsilon,W$ dependence.
- Bridging communication lower bounds to real system state via realistic skew models.

## 9. Key References
- **[Foundational]** Alon, N., Matias, Y., Szegedy, M. *The Space Complexity of Approximating the Frequency Moments.* STOC, 1996. — [DOI](https://doi.org/10.1145/237814.237823)
- **[Foundational]** Alon, N., Gibbons, P., Matias, Y., Szegedy, M. *Tracking Join and Self-Join Sizes in Limited Storage.* PODS, 1999. — [DOI](https://doi.org/10.1145/303976.303978)
- **[Foundational]** Datar, M., Gionis, A., Indyk, P., Motwani, R. *Maintaining Stream Statistics over Sliding Windows.* SIAM J. Computing, 2002. — [DOI](https://doi.org/10.1137/S0097539701398363)
- **[SOTA]** Braverman, V., Ostrovsky, R. *Smooth Histograms for Sliding Windows.* FOCS, 2007. — [DOI](https://doi.org/10.1109/FOCS.2007.55)
- **[Foundational]** Atserias, A., Grohe, M., Marx, D. *Size Bounds and Query Plans for Relational Joins.* SIAM J. Computing, 2013. — [DOI](https://doi.org/10.1137/110859440)
- **[SOTA]** Dobra, A., Garofalakis, M., Gehrke, J., Rastogi, R. *Processing Complex Aggregate Queries over Data Streams (Sketch Sharing).* SIGMOD, 2002. — [DOI](https://doi.org/10.1145/564691.564699)
- **[Survey]** Woodruff, D. *Sketching as a Tool for Numerical Linear Algebra.* Foundations and Trends in TCS, 2014. — [arXiv](https://arxiv.org/abs/1411.4357)

## 10. Worked Example

Take a count-based window of $W=4$ tuples per stream, joining on key $a$. Streams arrive interleaved (timestamp in parentheses):

$R$: $r_1{=}(a{:}5,\,t{:}1)$, $r_2{=}(a{:}7,\,t{:}3)$, $r_3{=}(a{:}5,\,t{:}5)$
$S$: $s_1{=}(a{:}5,\,t{:}2)$, $s_2{=}(a{:}9,\,t{:}4)$, $s_3{=}(a{:}5,\,t{:}6)$

A **symmetric hash join** keeps two hash tables keyed on $a$, each holding $\le W$ live tuples. When $s_3$ arrives, the in-window $R$ side is $\{r_1,r_2,r_3\}$; probing key $5$ returns $\{r_1,r_3\}$, emitting $(r_1,s_3)$ and $(r_3,s_3)$. State is $|R_{\text{live}}|+|S_{\text{live}}| \le 2W = 8$ tuples, i.e. $\Theta(W)$.

**Why the lower bound bites:** to decide merely whether key $5$ has a match, an adversary can flip any one of the $W$ live $R$-keys. By an INDEX reduction on domain $[U]$, recovering the answer for an arbitrary probed position forces storing $\Omega(\min(W,U))$ bits — here $\min(4, U)$. So no algorithm beats $\Theta(W)$ exact state, matching the symmetric-hash upper bound. For *approximate* join size instead, an AMS sketch of size $O(\varepsilon^{-2})$ would estimate the count $2$ within $(1\pm\varepsilon)$ without storing the tuples themselves.

---
*Part of the [DBMS Research catalog](../../README.md).*
