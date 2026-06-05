# Negative and Self-Join Sketch Estimation

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/self-join-sketch-estimation` · **Status:** open

## 1. Problem Statement
Linear sketches estimate the size of a single relation or a foreign-key join well, but break down on three structurally harder query classes: (i) **self-joins** $R\bowtie_{A=B} R$ and higher self-join powers (which compute the second frequency moment $F_2=\sum_x f(x)^2$ and beyond), (ii) **set difference / antijoin** $R\setminus S$ and `NOT EXISTS`/`NOT IN` (negation), and (iii) general queries mixing positive and negative subexpressions. The problem: design synopses that, from compact summaries of base relations (ideally built once, in one streaming pass), return $(1\pm\varepsilon)$-relative-error estimates of the *result size* (and aggregates over the result) for these query classes, with provable error and graceful behavior as the answer shrinks toward zero.

The **estimation** variant wants a tight CI on the result size; the **decision** variant asks whether the antijoin/difference is empty or exceeds a threshold; the **counting** variant is the join-size / $F_2$ computation itself. The hard kernel is that negation and self-correlation make the answer a *difference of large quantities*, where additive sketch error overwhelms a small true result.

## 2. Mathematical Foundations
Represent $R$ over join key as frequency vector $f$ and $S$ as $g$. Equi-join size is the inner product $|R\bowtie S|=\langle f,g\rangle=\sum_x f(x)g(x)$; self-join size is $\|f\|_2^2=F_2$. **AGM bound** caps worst-case join output at $\prod$ of fractional-cover degree products and frames why self-joins are expensive. Set difference size is $\sum_x \max(0,f(x)-g(x))$ — a *non-linear* functional that linear sketches do not directly expose; antijoin count is $|\{x: f(x)>0, g(x)=0\}|$, an existence/support functional.

The classic tool is **AMS sketching** (Alon–Matias–Szegedy, STOC 1996): random $\pm1$ projections $X=\langle f,r\rangle$ give $\mathbb{E}[X^2]=F_2$ with variance $\le 2F_2^2$, so $O(\varepsilon^{-2}\log\tfrac1\delta)$ projections yield $(1\pm\varepsilon)F_2$. Inner-product (join size) is estimated by sharing the *same* random seed across $f$ and $g$: $\langle Xf, Xg\rangle$ is unbiased for $\langle f,g\rangle$ with variance $\propto \|f\|_2^2\|g\|_2^2$ — fine when the join is dense, catastrophic when $\langle f,g\rangle \ll \|f\|_2\|g\|_2$. For difference/negation, $L_1$-sketches and the $L_p$-sampling primitive estimate $\sum_x|f(x)-g(x)|$ and sample support, but unbiased estimation of $\max(0,f-g)$ has no known sketch with relative-error guarantees.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** AMS and Count-Sketch give $\Theta(\varepsilon^{-2})$ space for $F_2$ and join size *relative to the $L_2$ norms*; $L_p$-sampling (Monemizadeh–Woodruff; Jowhari–Sağlam–Tardos, PODS 2011) supports support-set and difference estimation. Tug-of-war and fast Count-Sketch variants reduce update time to $O(1)$.
- **Systems-SOTA:** Practical engines lean on **sampling over joins** instead of sketches for self-joins — `Wander Join` (SIGMOD 2016, ripple/random-walk sampling) and `Join-Synopses` (Acharya et al., SIGMOD 1999) handle self-joins with sample-based CIs; antijoins/`NOT EXISTS` are typically *not* approximated in production AQP and fall back to exact execution.

## 4. Upper Bound
$F_2$/self-join size: $(1\pm\varepsilon)$ in $O(\varepsilon^{-2}\log\tfrac1\delta)$ words, one pass, **streaming/sketch model** (AMS). Join size $\langle f,g\rangle$: same space but error scales with $\|f\|_2\|g\|_2/\langle f,g\rangle$ — so *relative* error needs space inflating by that ratio. $L_p$-difference $\|f-g\|_p$: $\tilde O(\varepsilon^{-2})$ for $p\in(0,2]$. Wander Join self-join: $O(1)$-per-sample with CIs whose width $\propto 1/\sqrt{\text{\\#samples}}$, no worst-case space bound but data-adaptive.

## 5. Lower Bound
Negation and small-result joins are information-theoretically hard. Estimating set **disjointness** / antijoin emptiness needs $\Omega(n)$ bits of communication (Razborov), so no sublinear sketch certifies emptiness of $R\setminus S$ in the worst case. For *relative*-error inner-product (join size), an $\Omega(\|f\|_2\|g\|_2/\langle f,g\rangle)$ blow-up is unavoidable — when the true join is a tiny fraction of the norm product, any linear sketch's variance dominates (lower bounds via Gap-Hamming and indexing reductions). These are unconditional communication-complexity barriers, not conjecture-based.

## 6. The Gap
For *self-joins as $F_2$* the gap is closed ($\Theta(\varepsilon^{-2})$). The genuinely **open** part is (a) relative-error join/self-join size when the result is small relative to norms, and (b) any sketch with provable relative error for `max(0,f-g)` set-difference cardinality and antijoin counting. The disjointness lower bound shows no general worst-case solution exists, so the open question is *which structural restrictions* (bounded degree, foreign-key constraints, bounded "negative mass") make negation sketchable — a parameterized characterization no one has nailed down.

## 7. Current Research (as of June 2026)
Directions: degree-aware and *colorful* sampling that adapts to skew for self-joins; differential/learned components that predict the small-result correction; combining sampling (Wander Join lineage) with sketches to bound the bias of difference estimators. *(frontier — verify)* Recent 2025 work explores sketches for `NOT EXISTS` under bounded-negative-mass assumptions and instance-specific guarantees, but no peer-reviewed result gives worst-case-free relative error for general antijoins.

## 8. Future Work
- A parameterized dichotomy for when negation/antijoins admit provable sublinear estimation.
- Relative-error self-join estimators robust to extreme skew, beating the $L_2$-norm penalty under realistic constraints.
- Composable error algebra spanning positive *and* negative subexpressions of a query plan.

## 9. Key References
- **[Foundational]** Alon, N., Matias, Y., Szegedy, M. *The Space Complexity of Approximating the Frequency Moments.* STOC, 1996. — [DOI](https://doi.org/10.1145/237814.237823)
- **[Foundational]** Razborov, A. *On the Distributional Complexity of Disjointness.* Theoretical Computer Science, 1992. — [DOI](https://doi.org/10.1016/0304-3975(92)90260-M)
- **[SOTA]** Li, F., Wu, B., Yi, K., Zhao, Z. *Wander Join: Online Aggregation via Random Walks.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2915235)
- **[Foundational]** Acharya, S., Gibbons, P., Poosala, V., Ramaswamy, S. *Join Synopses for Approximate Query Answering.* SIGMOD, 1999. — [DOI](https://doi.org/10.1145/304182.304207)
- **[SOTA]** Jowhari, H., Sağlam, M., Tardos, G. *Tight Bounds for $L_p$ Samplers, Finding Duplicates in Streams, and Related Problems.* PODS, 2011. — [arXiv](https://arxiv.org/abs/1012.4889)
- **[Foundational]** Atserias, A., Grohe, M., Marx, D. *Size Bounds and Query Plans for Relational Joins (AGM bound).* FOCS, 2008. — [DOI](https://doi.org/10.1109/FOCS.2008.43)

## 10. Worked Example

**Why a small inner-product join is hard to sketch.** Take join key domain $\{1,2,3\}$. Relation $R$ has frequencies $f=(100,100,0)$ and $S$ has $g=(0,0,100)$, plus one accidental shared tuple making $g=(1,0,100)$. The true join size is $\langle f,g\rangle = 100\cdot1 + 100\cdot0 + 0\cdot100 = 100$.

Self-join $F_2$ of $R$ is $\|f\|_2^2 = 100^2+100^2 = 20000$, so $\|f\|_2 \approx 141$; similarly $\|g\|_2 \approx 100$. An AMS inner-product estimator is unbiased for $\langle f,g\rangle=100$ but its standard deviation scales like $\|f\|_2\|g\|_2/\sqrt{m} \approx 14100/\sqrt{m}$ for $m$ projections.

To get relative error $\varepsilon=0.1$ on the answer 100, we need std $\le 10$, i.e. $\sqrt{m}\ge 1410$, so $m \ge 2\times10^6$ projections — the blow-up factor $\|f\|_2\|g\|_2/\langle f,g\rangle = 14100/100 = 141$ squared. This is exactly the $\Omega(\|f\|_2\|g\|_2/\langle f,g\rangle)$ penalty of Section 5: when the true join is a tiny sliver of the norm product, linear-sketch variance swamps it, and an antijoin ($R\setminus S$, here keys $\{1,2\}$) is even harder — disjointness forces $\Omega(n)$.

---
*Part of the [DBMS Research catalog](../../README.md).*
