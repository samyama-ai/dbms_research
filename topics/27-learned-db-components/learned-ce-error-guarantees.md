# Worst-Case Error Guarantees for Learned CE

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/learned-ce-error-guarantees` · **Status:** open

## 1. Problem Statement

Most learned cardinality estimators optimize **average** accuracy and exhibit large
**tail** errors that mislead the query optimizer into catastrophic plans. The problem:
design a learned estimator $\hat c$ that provides a **worst-case** guarantee on the
multiplicative q-error,

$$\mathrm{qerr}(q) = \max\!\Big(\tfrac{\hat c(q)}{c(q)},\, \tfrac{c(q)}{\hat c(q)}\Big) \le \rho \quad \text{for all } q \in \mathcal Q,$$

for an instance $D$, with a **provably bounded** $\rho$ — while retaining the
compactness and query speed that make learned models attractive.

- **Decision variant:** given budget $B$ (space/time), does an estimator with
  worst-case q-error $\le\rho$ exist for $(D,\mathcal Q)$?
- **Optimization variant:** minimize $\rho$ subject to space $\le B$ (or minimize
  space subject to $\rho$).
- **Construction variant:** output such an estimator and a *certificate* of its bound.

"Solving" means estimators carrying a per-query or per-class certified bound, not
merely good empirical percentiles.

## 2. Mathematical Foundations

Worst-case CE is intimately tied to **sketching and synopsis lower bounds**. For a
single range-count, a data structure answering all rectangle queries with relative
error $\rho$ has space governed by discrepancy / range-counting theory. For joins,
the achievable error connects to the **AGM/polymatroid** bound and to *worst-case
optimal join* analysis: any selectivity within $[\,1,\ \prod_e|R_e|^{x_e}]$ may
occur, so a guarantee must either pessimistically use the upper envelope or read
enough data. Relevant tools:

- **Sketches with guarantees:** Count-Min / AMS give $(\varepsilon,\delta)$
  additive/relative bounds; these are *learned-free* baselines that DO carry worst-case
  (probabilistic) guarantees.
- **Monotonicity & consistency constraints:** a sound estimator should satisfy
  $c(q_1)\le c(q_2)$ when $q_1\Rightarrow q_2$; enforcing such lattice constraints can
  bound error propagation through plan enumeration.
- **Robust optimization:** treat the learned $\hat c$ as a nominal value inside an
  uncertainty set and bound regret of the chosen plan (links to "instance-optimal
  query plans").

## 3. State of the Art (SOTA)

- **Theory SOTA:** Classical synopses with provable bounds — Count-Min (Cormode–
  Muthukrishnan 2005), AMS sketches (1996), and multidimensional histograms with
  bounded error — but these are not "learned." No learned model is known to carry a
  nontrivial certified worst-case q-error on joins.
- **Systems SOTA:** Hybrid/safe estimators that fall back to pessimistic
  bounds: **Pessimistic Cardinality Estimation** (Cai et al., SIGMOD 2019) gives a
  provable *upper* bound on join size via the AGM/entropic bound; **SafeBound**
  (Deeds et al., SIGMOD 2023) produces guaranteed upper bounds usable for robust
  planning. These bound only one side (over-estimation) and are not learned in the
  deep-model sense, but are the closest to a guarantee.

## 4. Upper Bound

Pessimistic estimators give a *one-sided* worst-case guarantee:
$\hat c(q) \ge c(q)$ always, with $\hat c(q) \le \prod_e |R_e|^{x_e}$ (AGM) or the
tighter entropic/degree-bounded envelope, computable in time polynomial in the query
and synopsis size. For two-sided $\rho$ on single-table range queries, a synopsis of
size $\tilde O(\varepsilon^{-1})$ per dimension achieves relative error $1+\varepsilon$
in the **RAM/streaming** model. No learned estimator improves on these guarantees
while matching their bound.

## 5. Lower Bound

Two-sided multiplicative error on multi-table joins is **information-theoretically
hard** under bounded space: a synopsis of size $o(N)$ cannot certify q-error $<\rho$
for all join queries on correlated data (reduction from set-disjointness /
index in **communication complexity**, where the synopsis is the message). For range
queries, **cell-probe** lower bounds for approximate range counting force
$\Omega(\log/\log\log)$-type trade-offs between space and query time. These imply any
learned model, viewed as a synopsis, inherits the same space–error frontier.

## 6. The Gap

The gap is one-sided vs. two-sided and learned vs. classical. We have provable
*upper-bound* (pessimistic) estimators and provable classical *two-sided* synopses,
but no learned model that is both compact and certifiably bounded on both sides for
joins. Closing it requires either a learned model whose hypothesis class is
constrained to a certifiable family (e.g., monotone, AGM-consistent) or a tight
characterization of when two-sided guarantees are impossible below linear space.

## 7. Current Research (as of June 2026)

- Combining learned point estimates with pessimistic envelopes to get *bounded
  optimism* (learned interpolation between true and AGM bound) *(frontier — verify)*.
- Conformal prediction for certified per-query intervals over learned estimates
  *(frontier — verify)*.
- Entropic/degree-aware tighter upper bounds (Khamis, Ngo, Suciu lineage) feeding
  robust plan selection.

## 8. Future Work

- Two-sided certified learned estimators for acyclic joins.
- Space–error–time lower bounds *specific* to learned (compressible) data.
- Optimizer integration that consumes a $[\,\underline c,\overline c\,]$ interval
  rather than a point estimate and bounds resulting plan regret.

## 9. Key References

- **[Foundational]** G. Cormode, S. Muthukrishnan. *An Improved Data Stream Summary: the Count-Min Sketch.* J. Algorithms, 2005.
- **[Foundational]** M. Abo Khamis, H. Ngo, D. Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* PODS 2017.
- **[SOTA]** W. Cai, M. Balazinska, D. Suciu. *Pessimistic Cardinality Estimation.* SIGMOD 2019.
- **[SOTA]** K. Deeds, B. Sagi, D. Suciu, et al. *SafeBound: A Practical System for Generating Cardinality Bounds.* SIGMOD 2023.
- **[Survey]** X. Wang et al. *Are We Ready for Learned Cardinality Estimation?* VLDB 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
