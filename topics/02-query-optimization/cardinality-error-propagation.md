# Cardinality estimation error propagation through plans

> **Topic:** Query Optimization · **ID:** `02-query-optimization/cardinality-error-propagation` · **Status:** open

## 1. Problem Statement

A query plan is a pipeline of operators, each producing intermediate results whose **cardinality** is
estimated, not known. Errors in early estimates feed into later ones: a join cardinality is computed
from its (already estimated) inputs and an (estimated) selectivity. The problem: **bound how
per-operator estimation error amplifies into end-to-end error in the estimated cardinality of the
plan root, and into error in the plan's cost** $C(T)$, as a function of plan depth, shape, and the
error model of each operator.

Variants:

- **Worst-case propagation:** given per-operator multiplicative error in $[1/\epsilon, \epsilon]$,
  bound the root error.
- **Average/distributional:** given a noise distribution per operator, characterize the root
  error distribution (bias, variance, tail).
- **Cost error:** translate cardinality error into plan-cost error and into *plan-choice* error
  (did the optimizer still pick the right plan?).

## 2. Mathematical Foundations

The classic measure is **q-error**: for true $t$ and estimate $e$, $\mathrm{qerror}=\max(e/t,\,t/e)$.
Moerkotte, Neumann, Steidl (2009) proved that **bounded q-error on inputs gives bounded cost error**:
if every base/selectivity estimate has q-error $\le \theta$, then a plan's cost q-error is bounded by
a polynomial in $\theta$ and the number of joins — the foundational propagation result. The bound is
multiplicative: errors compound roughly as $\theta^{k}$ over $k$ joins in the worst case.

For multiplicative noise $X_i = t_i \cdot e^{\xi_i}$ with $\xi_i$ random, log-cardinality errors add:
$\log \hat n_{\text{root}} = \sum_i \xi_i + \log n_{\text{root}}$, so variance grows additively in
plan depth and the root error is log-normal-like by CLT — but join correlations and the **max** in
selectivity composition break independence, which is the hard part. The **AGM bound** provides a
*hard upper envelope* on any intermediate cardinality, capping worst-case amplification.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Moerkotte–Neumann–Steidl (VLDB 2009) — theory of q-error and its propagation to
  cost, with the result that minimizing maximum q-error minimizes worst-case cost deviation.
  Ioannidis–Christodoulakis (1991) — classic result that **errors propagate exponentially** with the
  number of joins for left-deep plans under independence-based estimation.
- **Systems-SOTA:** The Leis et al. "How Good Are Query Optimizers, Really?" (VLDB 2015) JOB study
  empirically quantified multi-order-of-magnitude error growth and its effect on plan quality;
  pessimistic cardinality estimation (Cai et al., Hertzschuch et al.) uses AGM-style upper bounds to
  cap propagation.

## 4. Upper Bound

- **Bounded-q-error propagation (Moerkotte et al.):** input q-error $\le \theta$ $\Rightarrow$ cost
  q-error $\le \theta^{\,2 \cdot \text{(number of joins)}}$ style bound (model: $C_{out}$-class cost,
  RAM). Tighter for ASI cost.
- **Pessimistic / bound-based estimators:** using AGM or degree bounds, intermediate estimates are
  provable upper bounds, so propagated error is **one-sided** and capped by the worst-case output
  size — eliminating unbounded underestimation, at the price of overestimation.

## 5. Lower Bound

- Ioannidis–Christodoulakis (1991): under independence/uniformity assumptions, expected error grows
  **exponentially in the number of joins** — an information-limited lower bound showing that
  point-estimate propagation cannot be both unbiased and bounded without correlation information.
- Information-theoretic: with only marginal (single-table) statistics, **no estimator** can bound the
  error of a multi-join correlated query — there exist instances with the same marginals but
  cardinalities differing by factors exponential in the number of relations (a counting/adversarial
  argument).

## 6. The Gap

We have a worst-case multiplicative bound (q-error theory) and an empirical exponential-growth
picture, but **no tight, distribution-aware characterization** of propagation that (a) accounts for
join correlation, (b) predicts the *probability* of a plan-choice flip, and (c) yields actionable
per-operator error budgets. Closing it needs propagation bounds parameterized by available statistics
and a translation from cardinality-error distributions to plan-ranking-error probabilities.

## 7. Current Research (as of June 2026)

- Pessimistic/bound-based estimators (DuckDB, Umbra) trading tightness for guaranteed one-sided error.
  *(frontier — verify)*
- Learned estimators with **calibrated uncertainty** whose error distributions can be propagated
  analytically (MIT, TUM, CMU). *(frontier — verify)*
- Error-aware plan selection that integrates propagation bounds into robust optimization.

## 8. Future Work

- Tight propagation bounds incorporating correlation / conditional-independence structure.
- A theory linking input-error distributions to the probability of suboptimal plan choice.
- Per-operator error budgeting to meet an end-to-end cost-error target.

## 9. Key References

- **[Foundational]** Ioannidis, Christodoulakis. *On the Propagation of Errors in the Size of Join Results.* SIGMOD, 1991.
- **[Foundational]** Moerkotte, Neumann, Steidl. *Preventing Bad Plans by Bounding the Impact of Cardinality Estimation Errors (q-error).* VLDB, 2009.
- **[SOTA]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really?* VLDB, 2015.
- **[SOTA]** Cai, Balazinska, Suciu. *Pessimistic Cardinality Estimation: Tighter Upper Bounds for Intermediate Join Cardinalities.* SIGMOD, 2019.
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* FOCS, 2008.

---
*Part of the [DBMS Research catalog](../../README.md).*
