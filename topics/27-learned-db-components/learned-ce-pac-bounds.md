# PAC Bounds for Learned Cardinality Estimation

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/learned-ce-pac-bounds` · **Status:** open

## 1. Problem Statement

A learned cardinality estimator is a function $\hat{c}_\theta$, fit from a training
sample, that maps a query $q$ (a conjunction of range/equality predicates, possibly
with joins) to an estimate $\hat{c}_\theta(q)$ of its true result size
$c(q) = |q(D)|$ on database instance $D$. The **PAC problem** asks: how many training
queries (and/or how much sampled data) are required so that, with probability at
least $1-\delta$, the learned estimator achieves error at most $\varepsilon$ on
**unseen** predicates and joins drawn from a query distribution $\mathcal{Q}$?

- **Decision variant:** does there exist $\theta$ in hypothesis class $\mathcal{H}$
  achieving expected q-error $\le 1+\varepsilon$? (agnostic/realizable distinction)
- **Optimization (learning) variant:** output $\hat\theta$ minimizing expected error.
- **Sample-complexity variant:** bound $m(\varepsilon,\delta)$, the number of labeled
  queries sufficient to guarantee generalization — the core open question here.

"Solving" means a distribution-free or distribution-dependent generalization bound
that is **tight** in the structural complexity of the predicate/join space.

## 2. Mathematical Foundations

Frame estimation as learning real-valued functions under a bounded loss, e.g.
the symmetric q-error $\ell(q) = \log\max\!\big(\hat c(q)/c(q),\, c(q)/\hat c(q)\big)$.
Standard PAC machinery applies to the induced threshold/loss class:

$$\Pr_{S\sim\mathcal{Q}^m}\!\Big[\sup_{h\in\mathcal{H}}\big|\hat L_S(h)-L(h)\big| > \varepsilon\Big] \le \delta,$$

with $m = O\!\big(\varepsilon^{-2}(\,\mathrm{Comp}(\mathcal{H}) + \log\frac1\delta)\big)$,
where $\mathrm{Comp}$ is VC dimension (binary thresholds), **pseudo-dimension** /
fat-shattering dimension $\mathrm{fat}_\gamma(\mathcal H)$ (real-valued outputs), or
Rademacher complexity $\mathfrak{R}_m(\mathcal H)$. Key dependencies:

- Range-predicate selectivity classes relate to VC dimension of axis-parallel boxes
  in $d$ attributes, $O(d)$ — but **joins** compose predicate classes, and result
  size is governed by the **AGM bound** $c(q)\le \prod_e |R_e|^{x_e}$ over a fractional
  edge cover, making the target a high-degree multilinear object.
- Conditional independence assumptions reduce effective dimension; their *failure*
  (correlation) inflates the fat-shattering dimension and thus $m$.

## 3. State of the Art (SOTA)

- **Theory SOTA:** No tight, join-aware PAC bound exists. Closest results are classical
  uniform-convergence bounds for real-valued regression (Anthony–Bartlett) and
  agnostic-learning bounds via Rademacher complexity, applied informally. Recent work
  on learning-augmented algorithms (Mitzenmacher–Vassilvitskii) frames estimators as
  predictions with consistency/robustness, but without selectivity-specific complexity.
- **Systems SOTA:** Empirically strong learned estimators — Naru/NeuroCard
  (deep autoregressive, VLDB 2020/2021), MSCN (multi-set CNN, CIDR 2019), DeepDB
  (SPN-based, VLDB 2020), FactorJoin (SIGMOD 2023) — report low median q-error but
  give **no** generalization guarantee; tail error on out-of-distribution joins is
  the dominant failure mode (see the CE benchmark of Wang et al., VLDB 2021).

## 4. Upper Bound

For a fixed single-table predicate family of VC/pseudo-dimension $D$, uniform
convergence gives $m = O(\varepsilon^{-2}(D + \log\frac1\delta))$ queries to bound
expected loss within $\varepsilon$ — a clean **RAM/statistical-learning** result, but
only under the assumption that test queries are i.i.d. from the same $\mathcal{Q}$.
With a margin-based (fat-shattering) analysis the dependence becomes
$\tilde O(\varepsilon^{-2}\mathrm{fat}_{\varepsilon}(\mathcal H))$. No nontrivial
upper bound is known that controls error on join queries whose schema/topology was
unseen at training time.

## 5. Lower Bound

Information-theoretically, no sample of queries can guarantee bounded q-error on
arbitrary unseen predicates: an adversary can plant a heavy hitter in an
unqueried region (an Ω lower bound by a packing/coupon-collector argument over
selectivity cells). For correlated multi-attribute data, distinguishing two
instances with identical training-query answers but differing target selectivity
requires $\Omega(N)$ samples of the underlying data in the worst case
(reduction from learning a hidden subset). These are **information-theoretic**
limits; no SETH/fine-grained separation specific to learned CE is established.

## 6. The Gap

The gap is fundamental, not merely quantitative: meaningful PAC guarantees demand a
**realizable or bounded-complexity assumption** on $\mathcal{Q}$ and on the
data's correlation structure, and no agreed-upon such assumption yet yields tight,
join-composable bounds. Closing it requires (a) a complexity measure for the join
predicate space that composes under the AGM bound, and (b) distribution
assumptions weak enough to be realistic yet strong enough to defeat the planted-
heavy-hitter lower bound.

## 7. Current Research (as of June 2026)

- Distribution-shift and OOD generalization for learned estimators, connecting CE to
  domain-adaptation theory *(frontier — verify)*.
- Learning-augmented (algorithms-with-predictions) analyses giving consistency +
  robustness trade-offs for estimators feeding the optimizer (Mitzenmacher, Lykouris,
  Vassilvitskii lineage).
- Conformal-prediction wrappers producing distribution-free coverage intervals around
  $\hat c$ — a practical route to PAC-style guarantees on *intervals* rather than
  point estimates *(frontier — verify)*.

## 8. Future Work

- A join-aware pseudo-dimension and matching uniform-convergence bound.
- Active-learning query selection minimizing $m(\varepsilon,\delta)$.
- Bounds that interpolate between realizable (independence holds) and agnostic
  (heavy correlation) regimes, parameterized by a measurable correlation quantity.

## 9. Key References

- **[Foundational]** M. Anthony, P. Bartlett. *Neural Network Learning: Theoretical Foundations.* Cambridge Univ. Press, 1999.
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* FOCS 2008 / SICOMP 2013.
- **[SOTA]** Z. Yang et al. *NeuroCard: One Cardinality Estimator for All Tables.* VLDB 2021.
- **[SOTA]** M. Mitzenmacher, S. Vassilvitskii. *Algorithms with Predictions.* CACM 2022.
- **[Survey]** X. Wang et al. *Are We Ready for Learned Cardinality Estimation?* VLDB 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
