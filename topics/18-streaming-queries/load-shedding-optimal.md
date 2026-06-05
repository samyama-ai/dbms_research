# Optimal load shedding under quality objectives

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/load-shedding-optimal` · **Status:** partially-solved

## 1. Problem Statement

When input rates exceed processing capacity, a streaming system must **shed load** — drop or approximate some tuples — to keep latency bounded. The problem: **decide what to drop, when, and how much, so as to maximize a query-quality objective $Q$ under a throughput/latency constraint.** Knobs include **random drop** (sample), **semantic drop** (drop low-value tuples by predicate), **window/operator-level drop**, and **approximate operators** (sketches). Variants:

- **Optimization:** maximize $Q$ (e.g., minimize aggregate relative error, maximize subset-result accuracy, maximize utility) subject to per-operator capacity $\mu_i$ and end-to-end latency $\le L_0$.
- **Decision:** does a shedding plan meeting latency $L_0$ with quality loss $\le q$ exist?
- **Placement:** *where* in the operator network to insert drop operators (drop early to save the most work, but predicting downstream effect is hard).
- **Online/adaptive:** rates and value distributions drift; choose drop rates with regret guarantees.

## 2. Mathematical Foundations

Model the query as a DAG of operators with selectivities $\sigma_i$, per-tuple costs $c_i$, and capacities $\mu_i$; input rate $\lambda$. A **drop operator** with retention probability $p$ inserted on an edge scales downstream load by $p$ and the contributed result by (in expectation) $p$. The **load equation** requires $\lambda \prod (\text{retentions}\cdot\sigma\cdot c) \le \mu$ along each path. The objective $Q$ is typically a **utility/error functional**: e.g., for `SUM`/`AVG`, random sampling at rate $p$ gives unbiased estimates with variance $\propto (1-p)/p$; for set/Top-k queries, quality is subset/Jaccard accuracy.

Two structural facts make near-optimal shedding tractable: (i) for many aggregate-quality objectives the **utility is concave in retained fraction**, and (ii) the placement/selection problem is often **submodular** — marginal quality gain from retaining a tuple/class decreases — so the **greedy algorithm gives a $(1-1/e)$** approximation under a knapsack/capacity (matroid) constraint (Nemhauser–Wolsey–Fisher). Semantic shedding (value-based) maps to a **fractional knapsack** ("drop the lowest-utility-per-cost tuples first") which is exactly solvable when utilities are known. Aurora's **QoS utility functions** (utility vs latency, vs drop, vs value) formalize $Q$. Approximate-operator shedding ties into sketch space–accuracy bounds (AMS: $\Omega(1/\epsilon^2)$ space).

## 3. State of the Art (SOTA)

- **Aurora / load shedding via QoS** — Tatbul, Çetintemel, Zdonik, Cherniack, Stonebraker (VLDB 2003): drop-operator insertion driven by per-output **QoS utility curves**; the canonical framework. **Semantic load shedding** (drop by value) follows.
- **STREAM** load shedding (Babcock, Datar, Motwani 2004): random shedding to bound aggregate-query **relative error**, with an analytic error model.
- **Window-aware / window-based shedding** (Tatbul, Zdonik VLDB 2006): shedding that respects window semantics to avoid disproportionate error.
- **Systems-SOTA:** modern engines (Flink/Heron back-pressure, Spark) primarily *back-pressure* rather than shed; explicit quality-objective shedding is mostly in research/AQP and in approximate-streaming systems. Learning-based shedding (e.g., neural drop policies) is recent *(frontier — verify)*.

## 4. Upper Bound

For **aggregate queries** (SUM/COUNT/AVG) with random shedding, STREAM gives an **analytic, provably error-optimal** allocation of drop rates across operators minimizing variance subject to capacity — an exact convex program. For **semantic** shedding with known per-class utilities, the fractional-knapsack solution is **optimal**; for combinatorial selection under matroid/knapsack capacity, **greedy achieves $1-1/e$** (NWF, optimal for monotone submodular under value-oracle, by Feige's hardness). These are the best-known guarantees and they hold under their respective utility models.

## 5. Lower Bound

- **Submodular maximization** under a cardinality constraint cannot be approximated better than $1-1/e$ in the value-oracle model (Nemhauser–Wolsey; Feige's $1-1/e$ inapproximability for Max-Coverage) — so for objectives in that class, greedy is **optimal** and no polynomial algorithm does better unless P=NP.
- **Online/adaptive** shedding under unknown drifting rates inherits **competitive lower bounds** from online knapsack/ski-rental-style analysis (no $o(\log)$-competitive deterministic policy in general).
- **Approximate-operator** shedding inherits AMS **$\Omega(1/\epsilon^2)$ space** lower bounds for $\epsilon$-accurate frequency moments — bounding how cheap accurate-under-shed operators can be.
- For *arbitrary* (non-submodular, non-concave) quality objectives, optimal shedding is **NP-hard** (reduction from knapsack/coverage).

## 6. The Gap

For tractable objective classes (aggregate-error, monotone-submodular utility) the problem is **essentially closed**: greedy/convex solutions match the $1-1/e$ or analytic-optimal lower bounds. The genuinely open part is **(a) general, non-submodular quality objectives** (e.g., complex joins, pattern/CEP queries) where neither good algorithms nor matching hardness are tight; **(b) the online/drifting regime** with provable regret/competitive ratios; and **(c) network-wide placement** where downstream effects of an upstream drop are hard to predict. Hence **partially-solved**: solved in clean models, open for rich queries and adaptivity.

## 7. Current Research (as of June 2026)

Directions: (i) **learned load shedding** — RL/contextual-bandit drop policies that adapt drop rates and predicates to drift, with empirical gains but few guarantees *(frontier — verify)*; (ii) **CEP / pattern-query shedding** (dropping partial matches by predicted contribution — Slo, Bhowmik, Rothermel lineage) where utility is non-additive; (iii) **shedding integrated with approximate operators and AQP error budgets**; (iv) **fairness/SLA-aware** shedding across multi-tenant queries. The submodular/knapsack core is settled; the frontier is non-additive objectives and provable online guarantees.

## 8. Future Work

- Approximation algorithms + matching hardness for non-submodular (join/CEP) quality objectives.
- Online shedding with regret/competitive guarantees under rate and value-distribution drift.
- Network-wide drop placement with predictive downstream-effect models.
- Unifying shedding with the latency–completeness–cost frontier (companion problem) as one control problem.

## 9. Key References

- **[Foundational]** Nesime Tatbul, Uğur Çetintemel, Stan Zdonik, Mitch Cherniack, Michael Stonebraker. *Load Shedding in a Data Stream Manager.* VLDB, 2003. — [DBLP](https://dblp.org/rec/conf/vldb/TatbulCZCS03.html)
- **[Foundational]** Brian Babcock, Mayur Datar, Rajeev Motwani. *Load Shedding for Aggregation Queries over Data Streams.* ICDE, 2004. — [DOI](https://doi.org/10.1109/ICDE.2004.1320010)
- **[SOTA]** Nesime Tatbul, Stan Zdonik. *Window-Aware Load Shedding for Aggregation Queries over Data Streams.* VLDB, 2006. — [PDF](https://people.csail.mit.edu/tatbul/publications/vldb06.pdf)
- **[Foundational]** George L. Nemhauser, Laurence A. Wolsey, Marshall L. Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)
- **[SOTA]** Ahmad Slo, Sukanya Bhowmik, Kurt Rothermel. *eSPICE: Probabilistic Load Shedding for Complex Event Processing.* Middleware, 2019. — [arXiv](https://arxiv.org/abs/2002.05896)

## 10. Worked Example

A query computes `SUM(value)` over two groups in a window. Group $A$ has $n_A = 100$ tuples with values near $10$; group $B$ has $n_B = 100$ tuples with values near $1$. Input rate $\lambda = 200$ tuples/s but capacity $\mu = 120$/s, so we must keep only a fraction $p = 120/200 = 0.6$.

**Random (uniform) shedding** keeps each tuple with $p = 0.6$ and rescales by $1/p$ (Horvitz–Thompson). For a group of $n$ unit-variance values, $\mathrm{Var}(\hat A) = \sum v^2 (1-p)/p$. With $p=0.6$, $(1-p)/p = 0.667$. For group $B$ ($v \approx 1$): $\mathrm{Var} \approx 100 \cdot 0.667 = 66.7$, sd $\approx 8.2$ against a true sum of $100$ — about $8\%$ relative error.

**Variance-optimal (semantic) allocation** instead spends the same budget unequally: keep more of the high-value group $A$ (each dropped $A$-tuple injects $\approx 100\times$ the variance of a $B$-tuple, since variance scales with $v^2 = 100$). Solving $\min \sum_g v_g^2(1-p_g)/p_g$ s.t. $\sum p_g n_g = 120$ pushes $p_A \to 1$, $p_B \to 0.2$. This slashes the dominant $A$-error while accepting larger relative error on the small-magnitude group $B$ — illustrating why utility-weighted (submodular/knapsack) shedding beats uniform sampling at equal load.

---
*Part of the [DBMS Research catalog](../../README.md).*
