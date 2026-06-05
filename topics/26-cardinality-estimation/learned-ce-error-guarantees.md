# Worst-Case Error Guarantees for Learned CE

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/learned-ce-error-guarantees` · **Status:** open

## 1. Problem Statement

Machine-learned cardinality estimators (LCEs) routinely beat classical histograms/sketches on average accuracy, but they offer **no certificate** on any individual query. The problem: **equip an LCE with a provable accuracy or robustness guarantee** — a statement of the form "for every query $q$ in stated class $\mathcal{Q}$, the estimate $\hat c(q)$ satisfies a known bound relative to the true $c(q)$," or a valid probabilistic surrogate.

Variants:

- **Deterministic certificate (decision/estimation):** produce a verifiable bound $\hat c(q)/c(q)\in[1/\alpha,\alpha]$ for all $q\in\mathcal Q$, or a one-sided pessimistic guarantee $\hat c(q)\ge c(q)$ (never under-estimate).
- **Distribution-free probabilistic guarantee:** emit an interval $[\ell(q),u(q)]$ with $\Pr[c(q)\in[\ell,u]]\ge 1-\delta$ that holds without assuming the data/query distribution (conformal-style coverage).
- **Robustness certificate:** bound the worst-case error over an adversarial neighborhood of $q$ (perturbed predicates/constants), as in certified ML robustness.

Why it matters: optimizers need a *floor* on how badly a single estimate can mislead plan choice; average q-error says nothing about the tail that produces catastrophic plans.

## 2. Mathematical Foundations

Selectivity $s(q)\in[0,1]$, cardinality $c(q)=s(q)\cdot n$. The plan-relevant error metric is **q-error**, $\mathrm{qerr}(q)=\max(\hat c/c,\, c/\hat c)\ge 1$; Moerkotte et al. (VLDB 2009) show bounded q-error bounds plan suboptimality. A *guarantee* is a function $\alpha(q)$ with $\mathrm{qerr}(q)\le\alpha(q)$ certified before seeing $c(q)$.

Three foundations are in play:

- **Statistical learning under shift:** PAC/Rademacher bounds give in-distribution generalization; **conformal prediction** gives finite-sample, distribution-free coverage *under exchangeability*, extendable to covariate shift via importance weighting (Tibshirani et al., 2019). These yield valid intervals, not deterministic bounds.
- **Pessimistic upper bounds:** the **AGM bound** $|{\bowtie}|\le \prod_e |R_e|^{x_e}$ for any fractional edge cover $x$ (Atserias–Grohe–Marx, 2008) and its refinements (polymatroid / entropic bounds, degree-aware bounds) give *certified never-under-estimate* envelopes independent of any model.
- **Certified robustness:** randomized smoothing / interval-bound propagation give Lipschitz-type guarantees $|\hat f(q)-\hat f(q')|\le L\,\|q-q'\|$, transferring to error bounds only when the true selectivity is itself Lipschitz in the predicate.

## 3. State of the Art (SOTA)

- **Theory-SOTA (envelopes):** AGM and its polymatroid/entropic strengthenings; **degree-based bounds** (DBPLP, MND) and the **"safe" pessimistic CE** of Cai, Balazinska, Suciu (SIGMOD 2019) — certified upper bounds via a sketch-backed bound formula.
- **Systems-SOTA (learned + guardrail):** hybrid estimators that pair a learned point estimate with a classical pessimistic cap, e.g. the pessimistic/upper-bound line and **FactorJoin** (Wu et al., SIGMOD 2023) which combines factor graphs with bound-style worst-case reasoning.
- **Probabilistic wrappers:** conformalized CE that emits calibrated intervals *(frontier — verify)*; uncertainty-aware Naru/DeepDB variants reporting predictive variance.

## 4. Upper Bound

- **Certified one-sided:** AGM/polymatroid bounds give a computable $\hat c\ge c$ with no distributional assumption, in time polynomial in the query (LP over edge covers). The bound can be loose by factors exponential in query size but is *always valid* in the RAM model.
- **Two-sided probabilistic:** weighted conformal prediction yields intervals with $1-\delta$ marginal coverage under bounded covariate shift; coverage is exact under exchangeability, finite-sample, model-agnostic.
- **No known** deterministic two-sided multiplicative guarantee for a *learned* model over an open query class.

## 5. Lower Bound

- **Information-theoretic:** any estimator using a summary of $o(n)$ bits cannot give a non-trivial worst-case multiplicative bound for arbitrary selective predicates — predicates hitting unseen joint mass force unbounded error (no-free-lunch / OOD impossibility).
- **Sampling barrier:** estimators that sample inherit $\Omega(\sqrt{n/r})$ lower bounds for low-selectivity predicates and distinct-value estimation (Charikar et al., PODS 2000; Chaudhuri–Motwani–Narasayya).
- **Robustness hardness:** exact worst-case-over-neighborhood verification of a ReLU network is NP-hard (Katz et al., 2017), so deterministic robustness certificates for deep LCEs are intractable in general; only relaxations (IBP, smoothing) are polynomial.

## 6. The Gap

Wide and **genuinely open**. We have certified *one-sided* envelopes (often very loose) and *probabilistic* two-sided intervals (valid only under exchangeability/bounded shift), but no deterministic, tight, two-sided guarantee for an expressive learned model. Closing it requires either (a) a constructive estimator class with provable q-error over a rich, named query class, or (b) a hardness theorem showing such a guarantee is impossible below $\Omega(n)$ space — pinning down the accuracy/space/robustness trade-off.

## 7. Current Research (as of June 2026)

- Conformal and calibrated-interval wrappers giving distribution-free coverage, with weighting for workload/data shift *(frontier — verify)*.
- "Guardrail" hybrids: learned estimate clamped to a pessimistic AGM/sketch envelope, trading tightness for a hard never-catastrophic floor (Suciu/UW; Wu, Cong et al.).
- Tightening pessimistic bounds via degree sequences and entropic/polymatroid LPs to make the certified envelope usable for planning (TUM Kemper/Neumann; Microsoft Research Chaudhuri/Narasayya).
- Certified-robustness transfer (smoothing/IBP) to CE so adversarially perturbed constants cannot flip estimates *(frontier — verify)*.

## 8. Future Work

- Tight two-sided certificates over a stated query class, or a matching space lower bound.
- Pessimistic bounds tight enough (small constant factor) to replace point estimates in the optimizer.
- Coverage guarantees that remain valid under *unbounded* drift via abstention ("I don't know") signals.
- Optimizer designs that consume intervals/certificates rather than point estimates.

## 9. Key References

- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008.
- **[Foundational]** Moerkotte, Neumann, Steinbrunn. *Preventing Bad Plans by Bounding the Impact of Cardinality Estimation Errors.* VLDB, 2009.
- **[SOTA]** Cai, Balazinska, Suciu. *Pessimistic Cardinality Estimation: Tighter Upper Bounds for Intermediate Join Cardinalities.* SIGMOD, 2019.
- **[SOTA]** Wu, Cong, et al. *FactorJoin: A New Cardinality Estimation Framework for Join Queries.* SIGMOD, 2023.
- **[Foundational]** Tibshirani, Foygel Barber, Candès, Ramdas. *Conformal Prediction Under Covariate Shift.* NeurIPS, 2019.
- **[Foundational]** Katz, Barrett, Dill, Julian, Kochenderfer. *Reluplex: An Efficient SMT Solver for Verifying Deep Neural Networks.* CAV, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
