---
id: 02-query-optimization/approximate-plan-optimization
title: "Optimizing AQP and bounded-error plans"
topic: 02-query-optimization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Optimizing AQP and bounded-error plans

> **Topic:** Query Optimization · **ID:** `02-query-optimization/approximate-plan-optimization` · **Status:** open

## 1. Problem Statement

In **Approximate Query Processing (AQP)**, the answer may be inexact if it meets a stated **accuracy target** — e.g., a relative error $\varepsilon$ at confidence $1-\delta$, or an absolute error bound. The optimizer's job changes: instead of an exact plan, it must select a plan over **approximate operators** (uniform/stratified samples, online aggregation, sketches such as Count-Min, HyperLogLog, AMS, KMV, and wavelets/histograms) that *provably meets the error target at minimum cost* — or, dually, *minimizes error subject to a cost/latency budget*.

- **Decision variant:** does a plan exist meeting error $\le \varepsilon$ w.p. $\ge 1-\delta$ within budget $B$?
- **Optimization variant (cost-min):** minimize cost subject to the accuracy constraint.
- **Optimization variant (error-min):** minimize expected error subject to a budget — the **online aggregation** stopping problem.

"Solving" means propagating error through a plan and choosing operators/sample sizes accordingly — a capability classical cost-based optimizers lack.

## 2. Mathematical Foundations

The accuracy of a sample-based aggregate follows **concentration inequalities**: for a SUM/AVG over a uniform sample of size $n$, the CLT/Hoeffding bound gives error $\propto \sigma/\sqrt{n}$, so meeting relative error $\varepsilon$ needs $n = \Theta(\sigma^2/(\varepsilon^2 \mu^2))$. **Stratified sampling** (BlinkDB's optimization) minimizes variance subject to a storage budget — a constrained optimization over stratum sample sizes. Sketches give worst-case guarantees: **Count-Min** answers point/range queries with error $\varepsilon\|f\|_1$ using $O(\tfrac{1}{\varepsilon}\log\tfrac1\delta)$ space; **HyperLogLog** estimates distinct counts with relative error $\approx 1.04/\sqrt{m}$ using $m$ registers; **AMS** sketches estimate $F_2$ / join sizes.

The hard part is **error propagation through joins and group-bys**: sample-over-join does not commute (the variance of a join of two samples is governed by the **correlated/stratified estimator** problem; Acharya–Gibbons–Poosala–Ramaswamy showed naive sample-then-join is biased), and error composes non-linearly. Formally the optimizer searches plans $P$ minimizing $\text{cost}(P)$ s.t. an **error functional** $\mathcal{E}(P) \le \varepsilon$, where $\mathcal{E}$ is itself an estimate with its own uncertainty — a *chance-constrained* program.

## 3. State of the Art (SOTA)

- **Systems SOTA:** **AQUA** / **Join Synopses** (Bell Labs) for sample-based AQP over joins; **BlinkDB** (MIT/Berkeley) for error/latency-bounded queries via multi-resolution stratified samples and an offline sample-selection optimizer; **Online Aggregation** (Hellerstein–Haas–Wang) and **DBO/Turbo** for ripple joins with running confidence intervals; **VerdictDB** (UMich) as an engine-agnostic AQP middleware; **DataSketches** (Apache) as the production sketch library. Snowflake/BigQuery ship `APPROX_*` aggregates.
- **Theory SOTA:** tight space bounds for distinct counting (Kane–Nelson–Woodruff optimal $F_0$), frequency moments (Indyk–Woodruff for $F_k$), and quantiles (KLL sketch, Karnin–Lang–Liberty, optimal $O(\tfrac1\varepsilon\log\log\tfrac1\delta)$).

## 4. Upper Bound

Per-operator, sketch space/accuracy bounds are *tight*: distinct count in $O(\varepsilon^{-2} + \log n)$ bits (Kane–Nelson–Woodruff, optimal), quantiles in $O(\varepsilon^{-1}\log\log\delta^{-1})$ (KLL, optimal). For **plan selection**, given a fixed family of synopses and an additive error model, choosing minimum-cost sample sizes per stratum is a convex/knapsack-like program solvable in poly time (BlinkDB's formulation). Online aggregation gives anytime $O(1/\sqrt{n})$-shrinking confidence intervals as $n$ tuples are processed.

## 5. Lower Bound

- **Sketch lower bounds** are information-theoretic / communication-complexity based: $F_0$ requires $\Omega(\varepsilon^{-2} + \log n)$ bits, $F_k$ for $k>2$ requires $\Omega(n^{1-2/k})$ space (Bar-Yossef et al.; Chakrabarti–Khot–Sun), and **sampling cannot estimate the number of distinct values** to within a constant factor without $\Omega(N)$ samples (Charikar–Chaudhuri–Motwani–Narasayya) — a fundamental barrier for COUNT DISTINCT via sampling.
- **Sample-over-join** error is provably unbounded for low-selectivity joins (the join may miss heavy contributors); no sublinear-sample estimator achieves relative-error guarantees for arbitrary join queries.

## 6. The Gap

Per-operator the bounds are essentially *closed* (matching sketch bounds). The genuinely **open** problem is **plan-level error propagation and optimization**: there is no general algorithm that, given a multi-join multi-aggregate query and an error target, selects operators with an end-to-end provable error bound at minimum cost. The interaction of sampling with joins, group-bys, and predicates breaks the per-operator guarantees, and the optimizer's own *uncertain* error estimates make the constraint stochastic. Closing the gap needs a compositional error calculus plus a chance-constrained plan optimizer.

## 7. Current Research (as of June 2026)

- **Learned AQP** and learned synopses (generative/ML models answering aggregates), with the open question of *bounded* error guarantees. *(frontier — verify)*
- Compositional error propagation through join–aggregate plans and *online* re-optimization under running confidence intervals.
- Sketch-aware optimizers that treat sketches as first-class physical operators (DataSketches in Druid/Spark). *(frontier — verify)*
- Differentially-private AQP where the error budget and the privacy budget interact (Dwork-style DP composition).

## 8. Future Work

- A sound, tight *end-to-end* error calculus for arbitrary SPJA plans.
- Chance-constrained plan optimization with provable feasibility.
- Joint optimization of sample/sketch *selection* (which synopsis) and plan.
- Error-bounded AQP over joins beyond join-synopses' assumptions.

## 9. Key References

- **[Foundational]** S. Acharya, P. Gibbons, V. Poosala, S. Ramaswamy. *Join Synopses for Approximate Query Answering.* SIGMOD, 1999. — [ACM](https://dl.acm.org/doi/10.1145/304182.304207)
- **[Foundational]** J. M. Hellerstein, P. J. Haas, H. J. Wang. *Online Aggregation.* SIGMOD, 1997. — [DBLP](https://dblp.org/rec/conf/sigmod/HellersteinHW97.html)
- **[SOTA]** S. Agarwal et al. *BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data.* EuroSys, 2013. — [arXiv](https://arxiv.org/abs/1203.5485)
- **[SOTA]** G. Cormode, S. Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch and its Applications.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[SOTA]** Z. Karnin, K. Lang, E. Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[Survey]** G. Cormode, M. Garofalakis, P. Haas, C. Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

Query: `SELECT AVG(amount) FROM sales` over $N = 10^7$ rows. We want relative error $\varepsilon = 0.01$ at confidence $1-\delta = 0.95$. The data has mean $\mu = 50$ and standard deviation $\sigma = 80$ (so coefficient of variation $\sigma/\mu = 1.6$).

Required sample size via the CLT half-width $z_{0.975}\,\sigma/\sqrt{n} \le \varepsilon\mu$:
$$n \ge \left(\frac{z\,\sigma}{\varepsilon\mu}\right)^2 = \left(\frac{1.96 \times 80}{0.01 \times 50}\right)^2 = \left(\frac{156.8}{0.5}\right)^2 \approx 98{,}400.$$

So scanning $\approx 0.98\%$ of the table meets the target — a $\sim 100\times$ cost reduction versus a full scan.

Now add a join `sales ⋈ region`. A uniform sample of `sales` joined with `region` is fine, but a sample of *both* sides is biased: the probability a matching pair survives is $\propto$ (sample rate)$^2$, so heavy join keys are systematically undercounted. This is exactly why **join synopses** sample the join result (or one side fully), restoring the $\sigma/\sqrt{n}$ guarantee that naive sample-then-join loses.

---
*Part of the [DBMS Research catalog](../../README.md).*
