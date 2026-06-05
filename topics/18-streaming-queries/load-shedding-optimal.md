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

- **[Foundational]** Nesime Tatbul, Uğur Çetintemel, Stan Zdonik, Mitch Cherniack, Michael Stonebraker. *Load Shedding in a Data Stream Manager.* VLDB, 2003.
- **[Foundational]** Brian Babcock, Mayur Datar, Rajeev Motwani. *Load Shedding for Aggregation Queries over Data Streams.* ICDE, 2004.
- **[SOTA]** Nesime Tatbul, Stan Zdonik. *Window-Aware Load Shedding for Aggregation Queries over Data Streams.* VLDB, 2006.
- **[Foundational]** George L. Nemhauser, Laurence A. Wolsey, Marshall L. Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978.
- **[SOTA]** Ahmad Slo, Sukanya Bhowmik, Kurt Rothermel. *eSPICE: Probabilistic Load Shedding for Complex Event Processing.* Middleware, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
