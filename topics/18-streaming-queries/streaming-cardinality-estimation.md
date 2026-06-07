---
id: 18-streaming-queries/streaming-cardinality-estimation
title: "Streaming cardinality and rate estimation for optimization"
topic: 18-streaming-queries
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Streaming cardinality and rate estimation for optimization

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/streaming-cardinality-estimation` · **Status:** empirically-open

## 1. Problem Statement

A continuous-query optimizer needs live statistics to (re-)choose join orders, parallelism, and placement: per-stream **arrival rates**, **selectivities** of predicates and joins, **distinct cardinalities**, and **skew** of key distributions. Unlike one-shot relational optimization, these quantities drift over time (bursts, diurnal cycles, concept drift), so estimates must be maintained online from a single pass with bounded state and must be *good enough* to keep a long-running plan near-optimal.

The problem: continuously estimate selectivities $\hat{s}$, rates $\hat{\lambda}$, distinct counts $\hat{n}_d$, and skew descriptors over the live window, with error bounds, *and* trigger re-optimization only when the estimate change implies a plan change worth its migration cost.

Variants: **counting** (distinct/cardinality), **estimation** (selectivity/rate as statistics), and **decision** (does the current optimum differ from the running plan?). Marked *empirically-open*: individual sketches have tight theory, but the *end-to-end* "estimate well enough to drive correct re-optimization under drift" question is judged empirically with no accepted guarantee.

## 2. Mathematical Foundations

- **Distinct counting (F0):** **HyperLogLog** (Flajolet et al. 2007) estimates $n_d$ with relative std-error $\approx 1.04/\sqrt{m}$ using $m$ registers ($O(\log\log n_d)$ bits each), mergeable across partitions. **Theta sketches** (DataSketches) support set operations needed for join-cardinality estimation.
- **Join cardinality:** the worst-case output is bounded by the **AGM bound** (Atserias–Grohe–Marx 2013): $|Q| \le \prod_e |R_e|^{x_e}$ for a fractional edge cover $\mathbf x$; streaming optimizers want *expected* output, estimable from per-key sketches and degree distributions.
- **Frequency moments / skew:** $F_2$ via **AMS sketch** (Alon–Matias–Szegedy 1999) in $O(\log m)$ space gives self-join size and a skew proxy; heavy-key detection feeds partitioning.
- **Rates:** decayed counters / exponentially-weighted estimators over sliding windows (DGIM-style) give $\hat\lambda$ with $\epsilon$-bounds.
- **Drift detection:** sequential change-point tests (CUSUM, ADWIN — Bifet–Gavaldà 2007) bound false-alarm vs. detection-delay, gating re-optimization.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Production engines (Flink, Spark, Snowflake, ClickHouse) ship HLL/Theta/Count-Min for `APPROX_COUNT_DISTINCT` and use coarse runtime rate metrics; *adaptive* re-optimization is mostly heuristic (Eddies, CACQ lineage; Avnur–Hellerstein 2000) or absent in production CQ engines.
- **Theory-SOTA:** HLL (optimal $O(\epsilon^{-2} + \log n)$-style distinct counting; near-optimal per Kane–Nelson–Woodruff 2010), AMS for moments, AGM/degree-based join estimation. **Learned cardinality estimators** (MSCN — Kipf et al. 2019; deep models) dominate *static* benchmarks but lack worst-case guarantees and adaptation under drift.

## 4. Upper Bound

- **Distinct (F0):** $O(\epsilon^{-2}\log\log n + \log n)$ bits, optimal (Kane–Nelson–Woodruff 2010), randomized, turnstile-friendly variants exist.
- **$F_2$ / skew:** $O(\epsilon^{-2}\log m \log\tfrac1\delta)$ bits (AMS), mergeable.
- **Rates over windows:** $O(\tfrac1\epsilon\log^2 N)$ bits (exponential histogram).
- **Drift gating:** ADWIN maintains a window with $O(\log N)$ memory and rigorous error/detection-delay bounds.

These give per-quantity guarantees in the (turnstile/sliding-window) streaming model. The *composite* selectivity used by the optimizer has no clean closed-form bound.

## 5. Lower Bound

- **Distinct counting:** $\Omega(\epsilon^{-2} + \log n)$ bits (Indyk–Woodruff; Kane–Nelson–Woodruff) via communication complexity (Gap-Hamming / set-disjointness).
- **Join-size estimation from samples/sketches:** estimating join cardinality to constant factor can require $\Omega(\sqrt{N})$ space for skewed inputs (information-theoretic; correlated-sampling lower bounds), and *uniform sampling* provably fails on skewed joins.
- **General multi-join selectivity:** propagating single-table estimates is known to be arbitrarily wrong; no sublinear sketch gives bounded multiplicative error for general acyclic joins (relates to AGM tightness gaps).

## 6. The Gap

Per-statistic estimation is **largely closed** (HLL, AMS match lower bounds). The open gap is **compositional and dynamic**: there is no method that turns bounded per-quantity errors into a *bounded plan-regret* guarantee for a continuously re-optimized query under drift. Empirically, learned estimators reduce error but can be catastrophically wrong out-of-distribution, and we lack theory connecting estimation error to optimizer decision quality. Hence *empirically-open*: progress is measured by benchmark plan-quality/regret, not closed bounds.

## 7. Current Research (as of June 2026)

- **Learned + sketch hybrids** with error bounds (robust/learning-augmented cardinality estimation; Hsu–Indyk–Katabi–Vakilian lineage) extended to streaming and drift *(frontier — verify)*.
- **Robust query optimization** minimizing *regret* over uncertainty regions rather than point estimates (lines from the MaxNorm / parametric-query-optimization community).
- **Continuous re-optimization with migration cost** — deciding when an estimate change justifies plan change (relates to watermark/window placement and adaptive parallelism, DS2).
- Drift-aware estimators combining ADWIN with mergeable sketches for distributed CQ *(frontier — verify)*.

## 8. Future Work

- A theory linking sketch error to *plan regret* for continuous queries.
- Worst-case-robust learned estimators with certified bounds and online updating.
- Joint estimation of correlated selectivities (avoiding the independence assumption) in sublinear state.
- Standard benchmarks for *streaming* (drifting) cardinality estimation, analogous to JOB for static.

## 9. Key References

- **[Foundational]** P. Flajolet, É. Fusy, O. Gandouet, F. Meunier. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA, 2007. — [HAL](https://hal.science/hal-00406166)
- **[Foundational]** N. Alon, Y. Matias, M. Szegedy. *The Space Complexity of Approximating the Frequency Moments.* JCSS, 1999. — [DOI](https://doi.org/10.1006/jcss.1997.1545)
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* SIAM J. Computing, 2013. — [DOI](https://doi.org/10.1137/110859440)
- **[SOTA]** D. M. Kane, J. Nelson, D. P. Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS, 2010. — [DOI](https://doi.org/10.1145/1807085.1807094)
- **[SOTA]** A. Kipf, T. Kipf, B. Radke, V. Leis, P. Boncz, A. Kemper. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677)
- **[SOTA]** A. Bifet, R. Gavaldà. *Learning from Time-Changing Data with Adaptive Windowing (ADWIN).* SDM, 2007. — [DOI](https://doi.org/10.1137/1.9781611972771.42)
- **[Foundational]** R. Avnur, J. M. Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD, 2000. — [DOI](https://doi.org/10.1145/342009.335420)

## 10. Worked Example

**HyperLogLog in miniature, and why composition is the hard part.** Use $m=4$ registers ($p=2$ prefix bits selecting the register; the rest count leading zeros). Each key is hashed to a bitstring; the register update keeps the max "position of the first 1" $\rho$ over the remaining bits.

Stream of distinct keys with hashes (register-bits | rest):
- $h_1=\texttt{01|}\underline{001}\dots\Rightarrow$ reg 1, $\rho=3$
- $h_2=\texttt{11|}\underline{1}\dots\Rightarrow$ reg 3, $\rho=1$
- $h_3=\texttt{01|}\underline{1}\dots\Rightarrow$ reg 1, $\rho=1$ (keeps max $3$)
- $h_4=\texttt{00|}\underline{01}\dots\Rightarrow$ reg 0, $\rho=2$

Registers $M=[2,\,3,\,0,\,1]$ (reg 2 unseen $\to 0$). The estimate is $\hat{n}_d=\alpha_m m^2 / \sum_j 2^{-M_j}$ with $\alpha_4\approx 0.673$:
$$\sum_j 2^{-M_j}=2^{-2}+2^{-3}+2^{0}+2^{-1}=0.25+0.125+1+0.5=1.875,$$
$$\hat{n}_d=\frac{0.673\cdot 16}{1.875}\approx 5.7.$$
True distinct $=4$; with only $m=4$ registers the relative error $\sim 1.04/\sqrt{m}=52\%$ is large, shrinking as $m$ grows. **Mergeability:** two HLLs combine by register-wise max — this is what lets a join optimizer estimate $|A\cup B|$.

The Section-6 gap is precisely that this clean per-sketch guarantee does **not** compose into a bounded *plan-regret* guarantee once such estimates feed join-order choices under drift.

---
*Part of the [DBMS Research catalog](../../README.md).*
