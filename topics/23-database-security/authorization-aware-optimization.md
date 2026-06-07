---
id: 23-database-security/authorization-aware-optimization
title: "Authorization-Aware Query Optimization"
topic: 23-database-security
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Authorization-Aware Query Optimization

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/authorization-aware-optimization` · **Status:** open

## 1. Problem Statement

Fine-grained access control (row-level security, label-based policies, cell-level masking, predicated views) constrains which tuples a user may see. A query optimizer normally pushes selections down and reorders joins for speed. When *security predicates* are pushed down or evaluated lazily, two confidentiality hazards arise:

1. **Inference via partial results / errors:** a security predicate evaluated *after* a cheaper user predicate may cause user-visible side effects — divide-by-zero, type errors, UDF side effects, or returned-then-filtered rows — that reveal the existence or values of tuples the user is not authorized to see (a classic "leaky predicate ordering" channel).
2. **Inference via timing:** the *plan chosen* and its runtime depend on data the user cannot read; an adversary who measures latency learns about hidden tuples (e.g. whether an index seek on a forbidden value found a match).

The problem: produce a plan that is **secure** — its observable behavior (results, errors, timing, resource use) is a function only of authorized data — while remaining as fast as possible. Variants: *decision* (is a candidate plan non-interfering for a given policy?), *optimization* (cheapest secure plan), and a *counting/quantitative* variant (minimize bits of leakage under a budget, à la quantitative information flow).

## 2. Mathematical Foundations

Model a query as a relational-algebra plan $P$ over relations $R_1,\dots,R_k$; a policy assigns each user $u$ an authorized view $V_u(R_i) = \sigma_{\phi_{u,i}}(R_i)$. Correctness (Truman/Non-Truman models, Rizvi et al. SIGMOD 2004) requires the answer equal the query over authorized views. Security is a **non-interference** property: let $D \sim_u D'$ denote databases agreeing on $u$'s authorized data; the plan is *secure* if its observable trace $\mathsf{Obs}(P, D) = \mathsf{Obs}(P, D')$ whenever $D \sim_u D'$, where $\mathsf{Obs}$ includes results, raised exceptions, and (for timing security) the cost/latency profile.

Predicate ordering safety is captured by a partial order: a "tainted" predicate $p$ (one whose evaluation can side-effect or leak) must not be evaluated on tuples not yet filtered by the security predicate $\phi$ — formally, in every root-to-leaf path the guard $\phi$ dominates $p$. This is a constrained plan-search where the optimizer's reordering lattice is intersected with a *security dominance lattice*. Quantitative leakage uses min-entropy/channel-capacity $\mathcal{L}(P) = \log_2 \sum_o \max_s p(o\mid s)$ over secret states $s$ and observations $o$.

## 3. State of the Art (SOTA)

**Systems-SOTA.** Oracle VPD/Label Security, PostgreSQL **Row-Level Security**, and SQL Server RLS implement view-based fine-grained AC; commercial optimizers mark certain predicates **non-pushdown-safe** ("leakproof" functions in PostgreSQL — only `LEAKPROOF`-tagged functions may be evaluated before RLS predicates). Rizvi et al. (SIGMOD 2004) formalized Truman/Non-Truman models; Wang et al. and Chaudhuri et al. (ICDE 2007) studied fine-grained AC semantics and optimization correctness.

**Theory-SOTA.** Language-based information-flow (Sabelfeld–Myers) and *secure query* type systems (e.g. SeLINQ, Jacqueline/policy-agnostic programming, Yang et al. POPL 2012/2016) give non-interference guarantees but largely ignore the *cost* dimension. Timing-channel-aware planning remains mostly unaddressed by mainstream optimizers.

## 4. Upper Bound

For *result/exception* security, PostgreSQL-style `LEAKPROOF` gating gives a sound, low-overhead solution: the optimizer freely reorders leakproof predicates and forces security predicates above non-leakproof ones — overhead is only the lost pushdown opportunities for tainted predicates. Constructing the cheapest secure plan is, like classic join ordering, solvable by dynamic programming over the secure sub-lattice in $O(3^n)$ for $n$ relations (Selinger DP intersected with dominance constraints). Quantitative-leakage-bounded optimization can be expressed as constrained search but no efficient exact algorithm is known.

## 5. Lower Bound

Choosing an optimal plan is already NP-hard (join ordering / bushy-tree optimization is NP-hard; Ibaraki–Kameda). Adding security-dominance constraints does not reduce hardness. **Timing non-interference** is, in the general (Turing-complete UDF / cost-model) setting, *undecidable* — it reduces to program-equivalence of observable cost. Even restricted, full timing-channel elimination tends to force worst-case (data-independent) execution, recovering the **ORAM/obliviousness $\Omega(\log n)$** penalties. Quantitative information-flow bounding is #P-hard in general (counting models satisfying an observation).

## 6. The Gap

The field has *sound-but-conservative* result-leakage defenses (leakproof gating) yet **no principled, cost-aware, timing-secure optimizer**. The gap is genuinely open: (i) we lack a tractable characterization of when a *fast* plan is also non-interfering w.r.t. timing; (ii) the trade-off curve between performance loss and quantitative leakage is uncharacterized; (iii) verification that a real optimizer's chosen plan is secure (not just that a safe plan exists) is largely unautomated. Closing it needs decidable sub-models plus optimizer-integrated leakage budgets.

## 7. Current Research (as of June 2026)

Active threads: **policy-agnostic / faceted execution** brought into databases (Jacqueline-style) for provable result non-interference *(frontier — verify)*; constant-time / data-oblivious operator selection to kill timing channels in encrypted DBs; **quantitative information-flow for SQL** measuring per-plan leakage; and verification of RLS-rewrites in formal frameworks (e.g. Cosette-style equivalence checking) *(frontier — verify)*. Groups: Stephen Chong (Harvard) and faceted-execution lineage, Berkeley/Wisconsin DB-security groups, the PostgreSQL security team (leakproof analysis), and information-flow researchers (Sabelfeld at Chalmers, Myers at Cornell).

## 8. Future Work

- A timing-secure cost model: optimize over *padded* costs so latency is data-independent yet not worst-case.
- Decidable fragments where "secure cheapest plan" is polynomial.
- Optimizer-integrated leakage budgets (spend $\varepsilon$ bits of timing leakage for $k\times$ speedup).
- Automated certification that a deployed plan satisfies non-interference for its policy.
- Extending leakproof analysis to UDFs, ML inference operators, and external functions.

## 9. Key References

- **[Foundational]** Rizvi, S., Mendelzon, A., Sudarshan, S., Roy, P. *Extending Query Rewriting Techniques for Fine-Grained Access Control.* SIGMOD, 2004. — [DOI](https://doi.org/10.1145/1007568.1007631)
- **[Foundational]** Selinger, P.G., Astrahan, M., Chamberlin, D., Lorie, R., Price, T. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[SOTA]** Wang, Q., Yu, T., Li, N., Lobo, J., Bertino, E., Irwin, K., Byun, J.-W. *On the Correctness Criteria of Fine-Grained Access Control in Relational Databases.* VLDB, 2007. — [PDF](https://www.vldb.org/conf/2007/papers/research/p555-wang.pdf)
- **[SOTA]** Yang, J., Yessenov, K., Solar-Lezama, A. *A Language for Automatically Enforcing Privacy Policies.* POPL, 2012. — [DOI](https://doi.org/10.1145/2103656.2103669)
- **[Survey]** Smith, G. *On the Foundations of Quantitative Information Flow.* FoSSaCS, 2009. — [DOI](https://doi.org/10.1007/978-3-642-00596-1_21)
- **[Foundational]** Sabelfeld, A., Myers, A.C. *Language-Based Information-Flow Security.* IEEE JSAC, 2003. — [DOI](https://doi.org/10.1109/JSAC.2002.806121)

## 10. Worked Example

**A leaky predicate ordering.** Table $\textsf{Accounts}(id, owner, balance, region)$. User $u$'s row-level policy restricts visibility to the security predicate $\phi \equiv (region = \texttt{'EU'})$. The user issues:

```sql
SELECT id FROM Accounts WHERE 1000000 / balance > 5;
```

The user predicate $p \equiv (10^6 / balance > 5)$ contains a division. If the optimizer pushes $p$ below the security predicate $\phi$ for speed, then a non-EU row with $balance = 0$ is evaluated, raising **division-by-zero** — a visible error. The very *occurrence* of that error tells $u$ "there exists a non-EU account with zero balance," leaking the existence of a tuple $u$ may not see. This is a confidentiality violation even though no forbidden row is returned.

**Secure ordering.** Mark $p$ as non-leakproof. The dominance constraint forces $\phi$ above $p$ on every path, so $p$ runs only on already-authorized (EU) rows:
$$\sigma_{p}\big(\sigma_{\phi}(\textsf{Accounts})\big),\quad\text{never}\quad \sigma_{\phi}\big(\sigma_{p}(\textsf{Accounts})\big).$$
PostgreSQL implements exactly this: only `LEAKPROOF`-tagged functions may be evaluated before an RLS predicate. The cost is the lost pushdown of $p$.

---
*Part of the [DBMS Research catalog](../../README.md).*
