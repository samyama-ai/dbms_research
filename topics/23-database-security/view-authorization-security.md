---
id: 23-database-security/view-authorization-security
title: "Provably Secure View-Based Authorization"
topic: 23-database-security
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Provably Secure View-Based Authorization

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/view-authorization-security` · **Status:** partially-solved

## 1. Problem Statement

View-based authorization grants a user access to a set of views $\mathcal{V}$ rather than base tables; the intent is that the user learns *only* what the views reveal. The classical, syntactic notion is weak: a view restriction may *look* restrictive yet still allow the user to reconstruct hidden information via determinacy (the views functionally fix a secret), or it may *appear* to hide a value while leaking it through join keys, constraints, or the absence of tuples.

The problem: **decide when a set of authorized views is *information-theoretically* (security-wise) safe with respect to a confidentiality policy**, i.e., the views reveal *no more* than the policy's declared "public" information — as opposed to merely being a syntactic projection/selection that happens to drop columns.

Decision variant: *Given views $\mathcal{V}$, a secret query $Q_s$, and constraints $\Sigma$, do $\mathcal{V}$ leak nothing about $Q_s$ beyond what an explicitly allowed view $\mathcal{P}$ already reveals?* Formalized via **view determinacy** and its **non-leakage** complement (instance-independent security).

This is **partially solved**: secure for well-characterized fragments (e.g., certain projection/selection views, "secure XML/relational views" with conditional rewriting), open in general because the underlying determinacy is undecidable.

## 2. Mathematical Foundations

Let $\mathcal{W}(\mathcal{V}, v) = \{D' \models \Sigma : \mathcal{V}(D') = v\}$ be the possible-worlds set induced by observed view answers $v$. Two security notions:

- **Determinacy-based leakage.** $\mathcal{V}$ *leaks* $Q_s$ if $Q_s$ takes a constant value across $\mathcal{W}$ when it should not — i.e., $\mathcal{V} \twoheadrightarrow Q_s$ (Nash–Segoufin–Vianu determinacy).
- **Instance-independent / perfect security.** $\mathcal{V}$ is *secure* for secret $S$ if for every base instance, the user's posterior over $S$ equals their prior given only allowed information $\mathcal{P}$:
$$\Pr[S \mid \mathcal{V}(D), \mathcal{P}] = \Pr[S \mid \mathcal{P}] \quad \text{(no information gain)}.$$

The **secure-views** framework (Miklau–Suciu) defines *perfect secrecy* of a query view $\mathcal{V}$ with respect to a secret query $S$: $\mathcal{V}$ leaks nothing about $S$ iff their "critical tuples" are disjoint, characterized via a probabilistic, instance-independent criterion. Decidability there is tied to query containment/equivalence (**$\Pi_2^p$ / NP** for CQs) and to determinacy (undecidable in general).

## 3. State of the Art (SOTA)

- **Secure relational views (Miklau–Suciu, 2004/2007):** the foundational *information-theoretic* definition of query-answering security; perfect secrecy is **decidable for conjunctive queries** and characterized via critical tuples, but becomes undecidable / intractable for richer languages.
- **Authorization views & query rewriting (Rizvi–Mendelzon–Sudarshan–Roy, 2004):** the "Truman vs. Non-Truman" model — validity of a query against authorization views, with rewriting that is sound but not always complete.
- **Secure XML publishing (Fan–Chan–Garofalakis; Miklau–Suciu):** provably secure view specifications for tree data via access-control annotations and query rewriting.
- Systems-SOTA: PostgreSQL/Oracle **VPD** and **row-level security** implement *syntactic* view security; they do not certify information-theoretic non-leakage.

## 4. Upper Bound

- Perfect secrecy of CQ views w.r.t. a CQ secret: **decidable**, reducible to CQ containment/equivalence; complexity **NP / $\Pi_2^p$** in query size (combined), polynomial-checkable for fixed bounded views.
- Non-Truman validity (Rizvi et al.): equivalent-rewriting test decidable for CQ/UCQ via query equivalence under views.
- Bounded fragments admit polynomial-time security certificates.

## 5. Lower Bound

- **View determinacy for UCQ/CQ-with-inequality is undecidable** (Nash–Segoufin–Vianu) — so general "does $\mathcal{V}$ leak the secret?" is undecidable.
- CQ containment is **NP-complete**, lower-bounding the security test for the CQ fragment.
- Determinacy and rewritability **diverge**: a secret can be *determined* (hence leaked) yet *not first-order rewritable*, so rewriting-based auditors are *incomplete* — a structural lower bound on syntactic methods.

## 6. The Gap

For **conjunctive queries the problem is essentially solved**: there is a clean information-theoretic definition (Miklau–Suciu) and decidable tests. The gap is the jump to **practical SQL**: aggregation, negation, recursion, and integrity constraints push security into the *undecidable* determinacy regime. Between the solved CQ core and undecidable full SQL lies a large, only partly charted band where we lack tight decidability/complexity results and lack complete (not merely sound) security certifiers. Closing it requires either new decidable fragments above CQ or principled sound-and-relatively-complete approximations with quantified leakage bounds.

## 7. Current Research (as of June 2026)

- Reconciling information-theoretic view security with **differential privacy** to give *quantified* (not just Boolean) leakage guarantees for analytic views *(frontier — verify)*.
- Security analysis of **row-/column-level security policies as views** in cloud warehouses (Snowflake, BigQuery), seeking certified non-leakage under joins and masking *(frontier — verify)*.
- Determinacy results for **graph/RPQ views** to extend the secure-views theory beyond relational CQs.
- Lineage of Miklau, Suciu, Sudarshan, Segoufin/Vianu remains central.

## 8. Future Work

- Decidable security tests for SQL fragments with aggregation and constraints.
- Unifying perfect secrecy, controlled query evaluation, and DP under one quantitative leakage measure.
- Compiler-style tools that emit a machine-checkable *proof of non-leakage* for a deployed view set.
- Security under *updates*: certifying that view security is preserved as base data and policies change.

## 9. Key References

- **[Foundational]** Gerome Miklau, Dan Suciu. *A Formal Analysis of Information Disclosure in Data Exchange.* Journal of Computer and System Sciences, 2007 (and SIGMOD 2004). — [DOI](https://doi.org/10.1016/j.jcss.2006.10.004)
- **[Foundational]** Shariq Rizvi, Alberto Mendelzon, S. Sudarshan, Prasan Roy. *Extending Query Rewriting Techniques for Fine-Grained Access Control.* SIGMOD, 2004. — [DOI](https://doi.org/10.1145/1007568.1007631)
- **[SOTA]** Alan Nash, Luc Segoufin, Victor Vianu. *Views and Queries: Determinacy and Rewriting.* ACM Transactions on Database Systems, 2010. — [DOI](https://doi.org/10.1145/1806907.1806913)
- **[Foundational]** Wenfei Fan, Chee-Yong Chan, Minos Garofalakis. *Secure XML Querying with Security Views.* SIGMOD, 2004. — [DOI](https://doi.org/10.1145/1007568.1007634)
- **[Survey]** Surajit Chaudhuri, Tanmoy Dutta, S. Sudarshan. *Fine Grained Authorization Through Predicated Grants.* ICDE, 2007. — [DOI](https://doi.org/10.1109/ICDE.2007.368976)

## 10. Worked Example

**Leakage through a join key.** Base table $\texttt{Emp}(\underline{\text{eid}}, \text{name}, \text{dept}, \text{salary})$. The secret is each employee's salary. We grant two "harmless-looking" views that each drop salary:

- $\mathcal{V}_1 = \pi_{\text{eid},\text{salary}}\,\texttt{Emp}$ but with names *removed* — i.e. $(\text{eid},\text{salary})$ pairs.
- $\mathcal{V}_2 = \pi_{\text{eid},\text{name}}\,\texttt{Emp}$ — the directory $(\text{eid},\text{name})$.

Individually neither view links a *name* to a *salary*. But $\text{eid}$ is a key shared by both, so the user computes
$$\mathcal{V}_1 \bowtie_{\text{eid}} \mathcal{V}_2 = \pi_{\text{name},\text{salary}}\,\texttt{Emp},$$
fully reconstructing the secret $Q_s = \pi_{\text{name},\text{salary}}\texttt{Emp}$. Formally $\{\mathcal{V}_1,\mathcal{V}_2\} \twoheadrightarrow Q_s$ (determinacy), so perfect secrecy *fails*: the posterior $\Pr[S\mid \mathcal{V}_1,\mathcal{V}_2]$ collapses to a point.

The Miklau–Suciu critical-tuple test catches this: the two views' critical tuples overlap on the $\text{eid}$-join, so they are *not* disjoint — exactly the condition under which a CQ view leaks a CQ secret. A purely syntactic "salary column is hidden in every view" check would miss the leak.

---
*Part of the [DBMS Research catalog](../../README.md).*
