# Subset/Superset Consistency of Estimates

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/estimate-consistency-monotonicity` · **Status:** open

## 1. Problem Statement

A cardinality estimator $\hat{c}(\cdot)$ should respect **logical relationships** among related (sub)queries even when each individual estimate is approximate. Two core consistency laws:

- **Monotonicity:** if $Q_1 \models Q_2$ (every result of $Q_1$ is a result of $Q_2$, e.g. adding a conjunct, or $\sigma_{p\wedge q} \subseteq \sigma_p$), then $\hat{c}(Q_1) \le \hat{c}(Q_2)$.
- **Additivity / inclusion–exclusion:** for disjoint or complementary predicates, $\hat{c}(\sigma_p) + \hat{c}(\sigma_{\neg p}) = \hat{c}(R)$, and more generally estimates satisfy inclusion–exclusion.

The problem: design estimators / reconcile a *set* of estimates so they are mutually **consistent**, because inconsistency causes optimizers to make logically impossible cost comparisons (a more selective subplan estimated as larger than its superplan), leading to bad, non-deterministic, or unstable plans.

Variants: **certify** that a given estimator is consistent (decision); **repair** an inconsistent set of estimates with minimal change (optimization); **construct** an inherently consistent estimator.

## 2. Mathematical Foundations

The clean framework is **measure-theoretic / probabilistic**: a consistent estimator corresponds to a single underlying (sub-)probability measure $\mu$ on tuples, with $\hat{c}(Q) = |R|\cdot \mu(\sigma_Q)$. Monotonicity and inclusion–exclusion are then automatic because $\mu$ is monotone and additive. Inconsistency arises precisely when estimates are **not realizable** by any single measure — e.g. independent-assumption products combined with feedback constraints.

The reconciliation problem is the **maximum-entropy** program: among all distributions consistent with known marginals/constraints, choose the one of minimum relative entropy (KL) to a prior — guaranteeing a *single* measure, hence consistency (Markl et al.). Monotone selectivity over a Boolean lattice of predicates relates to **lattice / poset** structure; enforcing monotonicity is an **isotonic regression** problem (projection onto the monotone cone), solvable by PAV-type algorithms. AGM/polymatroid bounds provide consistent *upper* envelopes for joins.

## 3. State of the Art (SOTA)

**Theory/Systems-SOTA:**
- **Max-entropy consistent selectivity** (Markl, Megiddo, Kutsch, Tran, Haas, Srivastava, VLDB 2005): the principal method for combining multiple selectivity constraints into one consistent model — guarantees inclusion–exclusion and avoids inconsistency by construction.
- **ISOMER** (Srivastava et al., ICDE 2006): max-entropy histogram maintenance preserving consistency under feedback.
- **Bound-based estimators** (AGM/SafeBound, Cai–Suciu 2019; Deeds 2023): provide monotone *upper bounds* — a superplan bound dominates its subplan, giving partial consistency for join planning.
- Empirical critiques (Leis et al., "How Good Are Query Optimizers, Really?", VLDB 2015) document how inconsistency and error propagation wreck plans.

Most production optimizers do **not** guarantee global monotonicity — a recognized, largely unaddressed weakness.

## 4. Upper Bound

Max-entropy reconciliation over $k$ linear (marginal) constraints is a convex program, solvable to $\varepsilon$ in $\text{poly}(k)$ time, yielding a single measure (hence fully consistent estimates). Enforcing monotonicity on a chain/lattice of $n$ estimates via isotonic regression costs $O(n)$ (chain, PAV) or $O(n^2)$–$O(n\log n)$ (general DAG via min-cut formulations). Pessimistic AGM/polymatroid bounds are computable per-query by LP and are monotone-by-construction along the subset lattice of joins.

## 5. Lower Bound

Deciding realizability of a set of arbitrary marginal/selectivity constraints by a single distribution is, in general, hard — the **consistency of marginals** problem is NP-hard for general overlapping marginals (related to the marginal problem / membership in the marginal polytope, and to #P-hard partition functions in graphical models). Thus globally consistent reconciliation of arbitrary estimate sets is intractable in the worst case; max-entropy is tractable only because it restricts to a specific constraint form. Enforcing monotonicity over a general partial order while staying close to given values is a constrained projection whose hardness scales with the order's structure.

## 6. The Gap

**Open.** We have consistency *by construction* for restricted methods (max-entropy over compatible marginals; monotone upper bounds), but **no scalable estimator** guarantees full subset/superset monotonicity and additivity across the *entire* plan space *and* high per-query accuracy — especially for learned estimators, which are notoriously non-monotone (adding a predicate can increase the estimate). The gap: worst-case intractability of general marginal consistency vs. the practical need for it. Closing it requires either tractable structural restrictions that real workloads satisfy, or estimator architectures (e.g. measure-realizable learned models) that are monotone by design with quantified accuracy loss.

## 7. Current Research (as of June 2026)

- **Monotonicity-constrained learned estimators**: architectures (monotone networks, measure-parameterized models) enforcing $Q_1 \models Q_2 \Rightarrow \hat{c}_1 \le \hat{c}_2$ *(frontier — verify)*.
- **Consistency as a regularizer/penalty** during training of learned CE models (lattice/inclusion-exclusion losses).
- **Bound-and-estimate hybrids** that wrap learned estimates inside monotone AGM/SafeBound envelopes.
- Optimizer-side **plan-stability** work tying estimate inconsistency to non-robust plans.

## 8. Future Work

- Provably measure-realizable learned estimators (single latent distribution).
- Tractable characterizations of consistency over realistic predicate lattices.
- Repair algorithms that minimally adjust an inconsistent estimate set with accuracy guarantees.
- Quantifying the accuracy cost of imposing consistency.

## 9. Key References

- **[Foundational]** Markl, Megiddo, Kutsch, Tran, Haas, Srivastava. *Consistently Estimating the Selectivity of Conjuncts of Predicates (max-entropy).* VLDB, 2005. — [VLDB Journal version (DOI)](https://doi.org/10.1007/s00778-006-0030-1)
- **[SOTA]** Srivastava, Haas, Markl, Kutsch, Tran. *ISOMER: Consistent Histogram Construction Using Query Feedback.* ICDE, 2006. — [DBLP](https://dblp.org/rec/conf/icde/SrivastavaHMKT06.html)
- **[SOTA]** Cai, Balazinska, Suciu. *Pessimistic Cardinality Estimation.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3319894)
- **[Survey]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really?* VLDB, 2015. — [DBLP](https://dblp.org/rec/journals/pvldb/LeisGMBK015.html)
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008. — [DBLP](https://dblp.org/rec/conf/focs/AtseriasGM08.html) · [arXiv](https://arxiv.org/abs/1711.03860)

## 10. Worked Example

Take $|R| = 1000$ with two predicates $p$ (`color = red`) and $q$ (`size = L`). An optimizer holds three feedback selectivities: $s_p = 0.30$, $s_q = 0.20$, and the *conjunct* $s_{p\wedge q} = 0.18$.

Check monotonicity: $Q_1 = \sigma_{p\wedge q}$ logically implies $Q_2 = \sigma_p$, so we need $\hat c(p\wedge q) \le \hat c(p)$, i.e. $180 \le 300$. Holds. But the independence guess would predict $s_p\cdot s_q = 0.30\times 0.20 = 0.06$ (60 rows), far below the observed 180 — the attributes are positively correlated.

Now inclusion–exclusion must close: from the four cells $\{pq, p\bar q, \bar p q, \bar p\bar q\}$,
$$s_{pq}=0.18,\quad s_{p\bar q}=s_p-s_{pq}=0.12,\quad s_{\bar p q}=s_q-s_{pq}=0.02,$$
and the remainder $s_{\bar p\bar q}=1-0.18-0.12-0.02=0.68$. All four are $\ge 0$ and sum to $1$, so a single measure $\mu$ realizes them — the estimates are consistent. Had feedback instead claimed $s_{p\wedge q}=0.35 > s_p=0.30$, monotonicity would break ($350 > 300$) and the cell $s_{p\bar q}=-0.05<0$ would prove no distribution realizes the set; max-entropy reconciliation would project back to a feasible, consistent point.

---
*Part of the [DBMS Research catalog](../../README.md).*
