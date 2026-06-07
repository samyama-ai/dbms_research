---
id: 02-query-optimization/plan-explainability
title: "Explainability and debuggability of plan choices"
topic: 02-query-optimization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Explainability and debuggability of plan choices

> **Topic:** Query Optimization · **ID:** `02-query-optimization/plan-explainability` · **Status:** open

## 1. Problem Statement

A cost-based optimizer maps a query $Q$ to a physical plan $P^\* = \arg\min_{P \in \mathcal{P}(Q)} \widehat{C}(P)$,
where $\widehat{C}$ is an estimated cost built from cardinality estimates, cost-model constants, and
statistics. **Explainability** asks for a faithful, human- or machine-actionable answer to *why $P^\*$
was chosen over its alternatives*, and *which inputs, if changed, would change the choice*. Distinct
variants:

- **Descriptive (decision):** Given $Q, P^\*$, and the optimizer state, produce an explanation $E$ that
  is **faithful** — every causal claim in $E$ holds in the actual optimizer — and **sufficient** —
  $E$ entails the ranking $P^\* \prec P'$ for the rival plans that matter.
- **Counterfactual / debugging (optimization):** Find the **minimum-weight perturbation** $\delta$ to
  inputs (a selectivity, a stat, a cost constant, a knob) such that the optimizer's choice flips to a
  target plan $P_t$ (or to *any* plan $\neq P^\*$). This is the "why did it pick the bad plan?" query.
- **Robustness/sensitivity (counting/measure):** Characterize the region of estimate-space
  $\{\hat\rho : \arg\min \widehat{C} = P^\*\}$ — the **plan diagram** cell — and its volume/boundaries.

The hard part is that the optimizer is a search procedure with pruning, transformation rules, and
heuristics; a faithful explanation must reflect *that procedure*, not a post-hoc rationalization.

## 2. Mathematical Foundations

Let parameters $\theta \in \mathbb{R}^m$ collect selectivities, base/intermediate cardinalities, and
cost constants. The cost of each candidate plan is (approximately) **piecewise-multilinear** in $\theta$,
so the optimizer induces a partition of parameter space into **optimality regions**
$\mathcal{R}_P = \{\theta : \widehat{C}_P(\theta) \le \widehat{C}_{P'}(\theta)\ \forall P'\}$. Each
$\mathcal{R}_P$ is an intersection of sign conditions on cost differences; the collection is the
**plan diagram** of Reddy–Haritsa. The minimum-perturbation problem is a distance-to-boundary query:
$\delta^\* = \arg\min_{\theta'} \lVert \theta' - \theta \rVert$ s.t. $\theta' \notin \mathcal{R}_{P^\*}$,
generally non-convex because $\mathcal{P}(Q)$ is exponential.

Two formal notions of explanation can be borrowed: **sufficient reasons / prime implicants**
(minimal subsets of estimates that pin the decision) and **Shapley/Banzhaf attribution** over the
input estimates, $\phi_i = \sum_{S} w_{|S|}\,[\,v(S\cup i) - v(S)\,]$ with $v$ a decision-indicator
value function — both are #P-hard to compute exactly in general. Faithfulness is the constraint that
the surrogate model used for attribution agree with the optimizer on the realized search path.

## 3. State of the Art (SOTA)

- **Systems-SOTA (descriptive):** `EXPLAIN`/`EXPLAIN ANALYZE` (PostgreSQL), SQL Server *Showplan* and
  Query Store, Oracle `DBMS_XPLAN` + SQL Plan Management, and DB2 `db2exfmt` expose chosen-plan trees,
  estimated vs. actual rows, and (in some) *missing-index*/regression hints. These show *what* was
  chosen, weakly *why*.
- **Systems-SOTA (counterfactual/robustness):** Picasso (Haritsa, VLDB demo 2005-2010) renders plan
  and cost diagrams; **Plan Bouquets** and parametric/anorexic optimization give worst-case plan-cost
  guarantees under estimate error. Microsoft `CardinalityEstimation` XEvents + Query Store enable
  regression root-causing in practice.
- **Theory-SOTA:** parametric query optimization (PQO) characterizes $\mathcal{R}_P$ and bounds the
  number of cells; explanation-as-attribution borrows from ML interpretability (LIME/SHAP, prime
  implicants), but a database-native, faithfulness-guaranteed framework is not standardized.

## 4. Upper Bound

- **Descriptive explanation** by replaying the optimizer's memo/search and emitting the winning
  rule sequence: linear in optimizer work, i.e. $O(|\text{memo}|)$ extra bookkeeping (RAM model);
  faithful by construction since it logs the actual path.
- **Single-parameter counterfactual:** sweeping one selectivity to find the flip point is a 1-D
  scan over plan-cost crossovers, computable in $O(|\mathcal{P}'|\log)$ via the lower envelope of the
  relevant cost lines, where $\mathcal{P}'$ is the (often small) set of plans competitive near $\theta$.
- **Plan-diagram approximation:** Picasso-style grid sampling computes an $\epsilon$-approximate
  diagram with $O(\epsilon^{-d})$ optimizer calls in $d$ varied dimensions (anytime/RAM).

## 5. Lower Bound

- **Exact minimum counterfactual** over the full plan space is **NP-hard**: it embeds optimal join
  ordering (cyclic/cross-product variants, Cluet–Moerkotte 1995) as the inner $\arg\min$, so deciding
  the cheapest flip is at least as hard as the optimization it explains.
- **Exact attribution** (Shapley/Banzhaf, prime-implicant enumeration) over $m$ estimates is
  **#P-hard** in general, matching results for Shapley values over Boolean/decision functions
  (information-theoretic counting model).
- **Faithfulness vs. compactness tension:** there is no sub-exponential *general* certificate that a
  short surrogate explanation agrees with the optimizer on all of parameter space — boundary
  description has worst-case exponentially many cells in the number of plans (parametric-LP arrangement
  bound). No tight SETH-conditional bound is yet established for the counterfactual variant —
  *(frontier — verify)*.

## 6. The Gap

We can faithfully *log* the chosen path cheaply, and we can *approximate* robustness diagrams, but
**minimal, faithful, counterfactual** explanations sit between an NP-hard/#P-hard exact target and
fast-but-unguaranteed heuristics (sampling, local sensitivity, ML surrogates). The open question is
whether a *fixed-parameter* or *output-sensitive* algorithm exists when only $k$ plans are
near-optimal near $\theta$ (often true in practice), giving guaranteed-faithful explanations in time
polynomial in $k$ rather than $|\mathcal{P}(Q)|$. Closing it needs either such an algorithm or a
fine-grained hardness result tying explanation to enumeration.

## 7. Current Research (as of June 2026)

- **Learned-optimizer explainability:** as Bao/Balsa/LEON/Neo-style value models enter systems, the
  community is adapting ML attribution (SHAP, integrated gradients, counterfactuals) to plan choice —
  with active debate on whether these surrogates are *faithful* to the optimizer they explain
  *(frontier — verify)*.
- **Robustness-first optimization:** Haritsa's group (IISc) continues plan-bouquet / robust-plan work;
  TUM (Neumann) and CWI (DuckDB) expose richer `EXPLAIN` provenance and per-operator estimate vs.
  actual diagnostics.
- **Regression root-causing & SQL plan management** in cloud engines (Snowflake, BigQuery, Redshift,
  Azure SQL) — automated detection of "plan flipped, cardinality model to blame" *(frontier — verify)*.
- Links to **query provenance/lineage** (topic 22) and **cardinality estimation** (topic 26): an
  explanation is only as faithful as the attributable estimate that drove it.

## 8. Future Work

- A formal, optimizer-native definition of **faithful explanation** with complexity-theoretic
  guarantees, and output-sensitive algorithms parameterized by the number of competitive plans.
- **Causally-correct counterfactuals** that respect statistical dependence among selectivities rather
  than perturbing them independently.
- Standardized, machine-checkable explanation formats (beyond ad-hoc `EXPLAIN` text) usable by
  autonomous/self-tuning systems (topic 35) for closed-loop repair.
- Explainability for **learned** and **hybrid** optimizers with end-to-end faithfulness certificates.

## 9. Key References

- **[Foundational]** Selinger, Astrahan, Chamberlin, Lorie, Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Graefe. *The Cascades Framework for Query Optimization.* IEEE Data Eng. Bull., 1995. — [DBLP](https://dblp.org/rec/journals/debu/Graefe95a.html)
- **[SOTA]** Reddy, Haritsa. *Analyzing Plan Diagrams of Database Query Optimizers.* VLDB, 2005. — [DBLP](https://dblp.org/rec/conf/vldb/ReddyH05.html)
- **[SOTA]** Dutt, Haritsa. *Plan Bouquets: Query Processing without Selectivity Estimation.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2588566)
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[Survey]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really?* VLDB, 2015. — [DOI](https://doi.org/10.14778/2850583.2850594)
- **[Foundational]** Cluet, Moerkotte. *On the Complexity of Generating Optimal Left-Deep Processing Trees with Cross Products.* ICDT, 1995. — [DOI](https://doi.org/10.1007/3-540-58907-4_6)

## 10. Worked Example

**A single-parameter counterfactual.** A two-table join `A ⋈ B` has two competitive plans whose estimated cost is linear in the estimated selectivity $\hat s$ of a filter on $A$:

- $P_{\text{NL}}$ (index nested-loop): $\widehat{C}=100 + 900\,\hat s$
- $P_{\text{HJ}}$ (hash join): $\widehat{C}=400$ (build/probe dominate, nearly flat in $\hat s$).

At the optimizer's estimate $\hat s = 0.1$: $\widehat{C}_{\text{NL}}=190 < 400$, so it picks $P_{\text{NL}}$. The user asks "why not the hash join, and what would flip it?"

**Flip point:** solve $100 + 900\,s = 400 \Rightarrow s^\* = 1/3 \approx 0.333$. So the *minimum counterfactual perturbation* is $\delta = s^\* - 0.1 = 0.233$: if the true selectivity were $\ge 0.333$, $P_{\text{HJ}}$ wins.

This is computed by the lower envelope of the two cost lines in $O(|\mathcal P'|\log|\mathcal P'|)$ over the small competitive set $\mathcal P'=\{P_{\text{NL}},P_{\text{HJ}}\}$ (Section 4) — cheap and faithful in 1-D. The hardness (Section 5) appears only when the inner $\arg\min$ ranges over the full exponential plan space and many parameters move at once.

---
*Part of the [DBMS Research catalog](../../README.md).*
