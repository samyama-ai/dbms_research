---
id: 17-approximate-query-processing/distinct-count-sketch-frontier
title: "Distinct-Count Sketches Beyond HLL"
topic: 17-approximate-query-processing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Distinct-Count Sketches Beyond HLL

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/distinct-count-sketch-frontier` · **Status:** empirically-open
> **Verification note:** Błasiok's optimal-$F_0$ result appeared at SODA 2018 (Best Student Paper), not FOCS 2018 as stated in sections 3–5.

## 1. Problem Statement
Cardinality estimation — counting distinct elements ($F_0$) in a multiset using sublinear space — is dominated in practice by **HyperLogLog (HLL)**, which achieves relative standard error $\approx 1.04/\sqrt{m}$ using $m$ registers of $\approx 6$ bits. The frontier problem: design distinct-count sketches that **strictly improve HLL's accuracy/space frontier** (better error per byte) while simultaneously supporting:
1. **set operations** (union, intersection, difference) with controlled error,
2. **predicate/filtered cardinality** (distinct count of rows satisfying a selection), and
3. **mergeability** for distributed aggregation.

This is "empirically open": no sketch dominates HLL on *all* axes, and the few that beat its bits-per-accuracy frontier (e.g., compressed variants) often sacrifice mergeability simplicity, update speed, or set-operation support. The decision variant: given a byte budget $b$ and relative-error target $\varepsilon$, does a sketch exist meeting both with the required operations?

## 2. Mathematical Foundations
The information-theoretic optimum for $F_0$ with relative error $\varepsilon$ is $\Theta(\tfrac1{\varepsilon^2}+\log n)$ bits (Kane–Nelson–Woodruff, PODS 2010). HLL stores $m$ "max leading-zero" registers, giving standard error $\sigma\approx 1.04/\sqrt m$ and using $\approx m\log_2\log_2 n$ bits — a $\log\log n$ factor above optimal. The estimator is $\hat n = \alpha_m m^2 / \sum_j 2^{-M_j}$ with harmonic-mean bias correction.

Key alternatives:
- **MinCount/KMV/AKMV:** keep $k$ smallest hashes; $\hat n=(k-1)/u_{(k)}$, error $\approx 1/\sqrt k$, but supports inclusion–exclusion set ops natively.
- **Theta sketch:** generalizes KMV with adaptive threshold $\theta$; unbiased set operations.
- **CPC (Compressed Probabilistic Counting):** entropy-codes the register distribution, getting **closer to the $\tfrac1{\varepsilon^2}$ bound** than HLL at the same accuracy — roughly 30–40% smaller for equal error (DataSketches).
- **HLL++ / Martingale (HLL-TailCut, "UltraLogLog", "ExaLogLog"):** improve constants and small-range bias.

The set-operation requirement is the crux: HLL has no unbiased intersection; KMV/Theta do, trading some space.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Kane–Nelson–Woodruff optimal $F_0$; Błasiok's optimal streaming $F_0$ with optimal space *and* update time (SODA 2018).
- **Systems-SOTA:** **HLL++** (Heule–Nunkesser–Hall, EDBT 2013, Google) with sparse/dense modes and bias correction; **Apache DataSketches CPC and Theta**; and recent **UltraLogLog / ExaLogLog** (Ertl, 2023–2024) improving HLL's memory-efficiency frontier by storing more state per register more compactly. *(frontier — verify exact constants of ExaLogLog vs. CPC.)*

## 4. Upper Bound
Optimal $F_0$: $O(\tfrac1{\varepsilon^2}+\log n)$ bits with $O(1)$ update (Błasiok, SODA 2018) — the theory ceiling. Practical mergeable sketches: HLL at $1.04/\sqrt m$ error in $\approx 6m$ bits; CPC and UltraLogLog reach the same error in measurably fewer bits (closer to the entropy bound). Theta/KMV add unbiased set operations at $\approx 1/\sqrt k$ error.

## 5. Lower Bound
$\Omega(\tfrac1{\varepsilon^2}+\log n)$ bits for $F_0$ to relative error $\varepsilon$ (Kane–Nelson–Woodruff; Gap-Hamming communication lower bound of Indyk–Woodruff / Chakrabarti–Regev). For **intersection** cardinality from independent sketches, error grows unboundedly as overlap $\to 0$ (set-disjointness $\Omega(n)$ bits for exact answers), so predicate/intersection support is fundamentally harder than plain cardinality.

## 6. The Gap
Plain distinct counting is theoretically *closed* ($\Theta(\tfrac1{\varepsilon^2})$), and CPC/UltraLogLog have nearly closed the *practical* constant-factor gap to the entropy bound. The genuinely open part is the **joint frontier**: a single sketch that is simultaneously (a) within small constant of the entropy bound, (b) fast to update, (c) mergeable, and (d) supports unbiased filtered/intersection cardinality. No construction dominates on all four; this is the "empirically open" core.

## 7. Current Research (as of June 2026)
Otmar Ertl's UltraLogLog and ExaLogLog push HLL's bits-per-accuracy down with maximum-likelihood estimators. *(frontier — verify)* Learned/neural cardinality estimators and GPU-resident sketches are explored for predicate-conditioned counts. DataSketches continues to refine CPC and Tuple sketches for filtered distinct counts. Open questions on adversarially robust cardinality (robust against adaptive inputs) are active (Ben-Eliezer, Woodruff et al.).

## 8. Future Work
- A practical sketch matching the $\tfrac1{\varepsilon^2}$ bound with full set-operation support.
- Predicate-pushdown distinct counts (distinct-under-selection) with provable error.
- Adversarially-robust and differentially-private distinct-count sketches at the optimal frontier.

## 9. Key References
- **[Foundational]** Flajolet, P., Fusy, É., Gandouet, O., Meunier, F. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AOFA 2007. — [HAL](https://hal.science/hal-00406166v2)
- **[Foundational]** Kane, D., Nelson, J., Woodruff, D. *An Optimal Algorithm for the Distinct Elements Problem.* PODS 2010. — [ACM](https://dl.acm.org/doi/10.1145/1807085.1807094)
- **[SOTA]** Heule, S., Nunkesser, M., Hall, A. *HyperLogLog in Practice (HLL++).* EDBT 2013. — [ACM](https://dl.acm.org/doi/10.1145/2452376.2452456)
- **[SOTA]** Ertl, O. *UltraLogLog: A Practical and More Space-Efficient Alternative to HyperLogLog.* 2023 (arXiv:2308.16862). — [arXiv](https://arxiv.org/abs/2308.16862)
- **[SOTA]** Błasiok, J. *Optimal Streaming and Tracking Distinct Elements with High Probability.* SODA 2018. — [arXiv](https://arxiv.org/abs/1804.01642)

## 10. Worked Example

**KMV vs. HLL on a tiny stream.** Stream the multiset $\{a,b,a,c,b,a,d\}$, true $F_0=4$ (distinct: $a,b,c,d$). Hash each element uniformly into $[0,1]$; suppose the *distinct* values hash to $h(a)=0.12,\;h(b)=0.47,\;h(c)=0.31,\;h(d)=0.08$.

**KMV with $k=2$:** keep the 2 smallest hashes $\{0.08,0.12\}$, so $u_{(2)}=0.12$. Estimate
$$\hat n=\frac{k-1}{u_{(k)}}=\frac{1}{0.12}\approx 8.3.$$
With only $k=2$ the relative error $\approx1/\sqrt k\approx 0.71$ is huge — but raising $k$ shrinks it as $1/\sqrt k$, and KMV supports **set union** for free: merging two KMV sketches just keeps the global $k$ smallest hashes.

**HLL register intuition:** HLL instead tracks the max leading-zero count $\rho$ per bucket; seeing $h(d)=0.08$ ($\approx 0.000101_2$, 3 leading zeros after the point) suggests $n\gtrsim 2^{3}$. HLL needs $m\approx 1.04^2/\varepsilon^2$ registers for relative error $\varepsilon$; e.g. $\varepsilon=0.02$ needs $m\approx 2700$ registers ($\approx 2$ KB), versus the entropy floor that CPC/UltraLogLog approach more tightly.

---
*Part of the [DBMS Research catalog](../../README.md).*
