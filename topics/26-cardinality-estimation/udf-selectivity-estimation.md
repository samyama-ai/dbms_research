# User-Defined Function Selectivity

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/udf-selectivity-estimation` · **Status:** open

## 1. Problem Statement
Given a predicate `WHERE f(t)` where `f` is a **user-defined function** (UDF) or otherwise **opaque, black-box** boolean over a tuple `t` (an ML model call, a regex/UDF, a remote service, a stored procedure), estimate its **selectivity** $s(f) = \Pr_{t\sim R}[f(t)=\text{true}]$ — the fraction of rows that pass — and the resulting output cardinality $s(f)\cdot|R|$.

Variants:
- **Estimation variant:** approximate $s(f)$ for cost-based optimization, ideally with a confidence interval.
- **Online/adaptive variant:** the predicate is expensive (per-call cost $c$), so the optimizer must also choose *predicate ordering* and *pushdown* — selectivity and cost jointly determine the optimal plan (the "expensive-predicate" problem).
- **Decision variant:** is $s(f)$ above/below a threshold (e.g. should the UDF be evaluated first)?

The defining constraint: `f` exposes **no histogram, no monotonicity, no algebraic structure** the optimizer can introspect. Classical attribute statistics are useless; the optimizer typically falls back to a fixed magic constant (e.g. Postgres uses 1/3 for unknown boolean predicates).

## 2. Mathematical Foundations
Selectivity estimation of a black box is **Monte-Carlo mean estimation**: draw a sample $S$ of size $n$ from $R$, evaluate $f$, and estimate $\hat s = \frac{1}{n}\sum_{t\in S} \mathbf 1[f(t)]$. By Hoeffding, $\Pr[|\hat s - s| > \varepsilon] \le 2e^{-2n\varepsilon^2}$, so $n = O(\varepsilon^{-2}\log\frac1\delta)$ samples suffice for additive error $\varepsilon$ w.p. $1-\delta$ — independent of $|R|$. For *small* $s$ (rare predicates) relative error needs $n=O(\frac{1}{s\varepsilon^2}\log\frac1\delta)$, motivating **importance/stratified sampling**.

When `f` is expensive, this is a **budgeted estimation / sampling-under-cost** problem: minimize estimation variance subject to total cost $\sum c \le B$. The **expensive-predicate ordering** problem (Hellerstein–Stonebraker) reduces to ranking predicates by *rank* $= (1-s)/c$ (selectivity per unit cost) — provably optimal for independent conjuncts, NP-hard with correlation.

The opacity itself is the hardness core: with no oracle structure, no estimator can do better than sampling — there is no analog of a histogram lookup. This connects to **query learning / property testing**: estimating a property of a black-box boolean function is governed by query complexity lower bounds.

## 3. State of the Art (SOTA)
**Systems-SOTA:** (i) **catalog-stored UDF selectivity hints** — Postgres `ROWS`/`support functions`, Oracle extensible optimizer "selectivity" interfaces let developers register an estimator; (ii) **sampling at optimization/runtime** — sample-then-evaluate, used in adaptive query processing; (iii) **learned cost/selectivity models** that featurize the UDF inputs (not the UDF body) and regress selectivity from execution feedback.

**Theory/feedback-SOTA:** **self-tuning / feedback (LEO-style)** approaches (Stillger et al., DB2 LEO, VLDB 2001; Markl et al. on consistent estimation) treat observed cardinalities from prior executions as ground truth and correct future estimates — the dominant practical mechanism for opaque predicates. **Mid-query re-optimization** and **eddies** (Avnur–Hellerstein, SIGMOD 2000) adapt ordering at runtime when selectivity is unknown a priori.

## 4. Upper Bound
Additive-$\varepsilon$ selectivity estimation: $O(\varepsilon^{-2}\log\frac1\delta)$ black-box evaluations via uniform sampling + Hoeffding (model: oracle access to `f`, uniform sampling of $R$). For expensive conjunctive predicates with independence, optimal ordering computable in $O(m\log m)$ for $m$ predicates by sorting on rank $(1-s_i)/c_i$ (Hellerstein–Stonebraker). Adaptive (online) regret for predicate ordering: sublinear regret achievable via bandit/eddy formulations.

## 5. Lower Bound
- **Information-theoretic:** estimating $s$ to additive $\varepsilon$ requires $\Omega(\varepsilon^{-2})$ evaluations (matching Hoeffding; from estimating a Bernoulli mean). For relative error on rare events, $\Omega(1/(s\varepsilon^2))$.
- **No-structure floor:** for a truly opaque `f`, no algorithm can predict $s$ without evaluating `f`; any estimate from fewer than the sampling bound has worst-case error $\Theta(1)$ (adversary hides the satisfying set).
- **Optimal ordering with correlation:** ordering expensive predicates to minimize expected cost is **NP-hard** once selectivities are correlated (reduction from pipelined-set-cover / sequential testing), and hard to approximate beyond known constant factors.

## 6. The Gap
For a *single* opaque predicate, the gap is **closed in the worst case**: sampling is both necessary and sufficient (matching $\Theta(\varepsilon^{-2})$). The **open** frontier is structural: (a) exploiting *partial* structure (monotonicity, smoothness, learned surrogates of the UDF) to beat the worst-case sampling cost; (b) joint selectivity + cost optimization under correlation, where ordering is NP-hard and the approximation landscape is incomplete; (c) reusing feedback across queries with provable convergence rather than heuristics.

## 7. Current Research (as of June 2026)
- **LLM/ML-UDF-aware optimization:** as predicates become model inferences (semantic filters, embeddings, "LLM-as-filter"), estimating their selectivity and *cost* jointly is an active area; "semantic operators" and proxy-model cascades aim to predict pass-rates cheaply *(frontier — verify)*.
- **Surrogate/proxy models:** train a cheap classifier approximating the expensive UDF to pre-filter and to estimate selectivity, with statistical guarantees on the proxy gap.
- **Feedback-driven robust optimization:** principled use of execution telemetry (LEO descendants) with concentration bounds and drift handling.
- **Bandit predicate ordering** with formal regret bounds for adaptive evaluation.

## 8. Future Work
- Tight characterization of which structural assumptions on `f` provably reduce sampling cost.
- Approximation algorithms / hardness dichotomy for correlated expensive-predicate ordering.
- Confidence-interval-carrying selectivity estimates that flow into robust plan selection and runtime re-optimization.
- Cost models for UDFs whose cost itself is data-dependent (e.g. early-exit models).

## 9. Key References
- **[Foundational]** J. M. Hellerstein, M. Stonebraker. *Predicate Migration: Optimizing Queries with Expensive Predicates.* SIGMOD, 1993.
- **[Foundational]** R. Avnur, J. M. Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD, 2000.
- **[SOTA]** M. Stillger, G. Lohman, V. Markl, M. Kandil. *LEO – DB2's LEarning Optimizer.* VLDB, 2001.
- **[SOTA]** S. Chaudhuri, V. Narasayya, R. Ramamurthy. *Estimating Progress of Long Running SQL Queries.* SIGMOD, 2004. *(feedback/runtime estimation context)*
- **[SOTA]** C. Patel et al. *Semantic Operators / LLM-as-filter selectivity.* (recent CIDR/SIGMOD-track work) *(frontier — verify)*
- **[Survey]** S. Chaudhuri. *An Overview of Query Optimization in Relational Systems.* PODS, 1998.

---
*Part of the [DBMS Research catalog](../../README.md).*
