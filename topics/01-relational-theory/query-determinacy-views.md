---
id: 01-relational-theory/query-determinacy-views
title: "Query Determinacy and Rewriting Using Views"
topic: 01-relational-theory
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Query Determinacy and Rewriting Using Views

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/query-determinacy-views` · **Status:** open
> **Verification note:** Gogacz–Marcinkowski (LICS 2015, arXiv:1501.01817) proved *unrestricted* CQ-to-CQ determinacy undecidable (and the finite-instance variant in arXiv:1512.01681), so the "CQ determinacy is open/in a narrow band" framing in sections 3 and 6 overstates how open the unrestricted case is.

## 1. Problem Statement

Given a set of views $\mathcal{V} = \{V_1,\dots,V_n\}$ (each defined by a query) and a query $Q$, we ask two coupled questions:

- **(Determinacy / Decision)** Does $\mathcal{V}$ **determine** $Q$? That is, for any two databases $D_1, D_2$, if $V_i(D_1) = V_i(D_2)$ for all $i$, does $Q(D_1) = Q(D_2)$? Written $\mathcal{V} \twoheadrightarrow Q$. Equivalently, is the answer to $Q$ a *function* of the view extents alone?
- **(Rewriting / Synthesis)** If $\mathcal{V}$ determines $Q$, is there a **rewriting** $R$ such that $Q = R \circ \mathcal{V}$, and in what language (first-order? the language of the views? monotone?)?

The central open problem: **decidability of determinacy for conjunctive queries and views**, and whether determinacy implies the existence of a *first-order* (or CQ) rewriting — i.e., the **completeness of a language for rewritings**.

## 2. Mathematical Foundations

Determinacy is an *information-theoretic* notion: $\mathcal{V} \twoheadrightarrow Q$ iff the map $D \mapsto \mathcal{V}(D)$ has enough information to recover $Q(D)$. Rewriting is the *constructive* counterpart. Key relationships:

$$
\text{(CQ rewriting exists)} \implies \mathcal{V}\twoheadrightarrow Q \implies \text{(some rewriting exists in principle)} .
$$

A language $\mathcal{L}$ is **complete for $\mathcal{L}'$-to-$\mathcal{L}''$ rewritings** if whenever views/queries in those classes have determinacy, a rewriting exists in $\mathcal{L}$. Segoufin & Vianu (*PODS* 2005) formalized this and showed determinacy does **not** in general imply first-order (or even CQ) rewriting — the gap between "determined" and "rewritable" is real. Nash, Segoufin & Vianu (*TODS* 2010) proved that for CQ views and a CQ query, determinacy does **not** imply CQ-rewritability, and connected losslessness to the chase.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Segoufin & Vianu (2005) and Nash, Segoufin & Vianu (2010) established the foundational picture: determinacy is undecidable / open across natural classes, and rewriting languages are incomplete. Afrati studied **monotone determinacy**. **Gogacz & Marcinkowski** (*LICS* 2015, *JACM*) proved **undecidability of determinacy for unions of conjunctive queries (UCQs)** and made deep progress isolating the CQ case — showing determinacy for CQs lies very close to undecidable and is not finitely controllable.
- **Systems-SOTA.** Practical **answering-queries-using-views (AQUV)**: the **MiniCon** algorithm (Pottinger & Halevy, *VLDBJ* 2001), the **bucket** and **inverse-rules** algorithms; used in data integration (Information Manifold, Tukwila) and in materialized-view selection in commercial optimizers (Microsoft SQL Server, Oracle).

## 4. Upper Bound

For restricted classes determinacy is decidable: e.g., **path queries / chain CQs** (Afrati), and cases reducible to query containment (decidable, NP-complete for CQs). When a CQ rewriting exists it can be found by enumerating candidate rewritings bounded by the views (MiniCon), giving an **NP**/$\Sigma_2^p$-style search. The "**equivalent rewriting using views**" problem for CQs is **NP-complete** (Levy, Mendelzon, Sagiv, Srivastava 1995). Model: set semantics, finite databases; determinacy under both finite and unrestricted instances has been studied (they can differ).

## 5. Lower Bound

- **Determinacy is undecidable for UCQs** (Gogacz & Marcinkowski, LICS 2015) and undecidable for several richer classes; for **CQs with inequalities / FO views** undecidability also holds.
- Even when decidable, **finding a rewriting is NP-hard** (equivalence of CQ rewriting; LMSS 1995).
- **Incompleteness lower bound**: there exist $\mathcal{V}, Q$ (CQs) with $\mathcal{V} \twoheadrightarrow Q$ but *no* first-order rewriting (Nash–Segoufin–Vianu) — an expressiveness impossibility, proved via the chase and infinite-model arguments.

## 6. The Gap

The **decidability of CQ-to-CQ determinacy is the headline open problem.** UCQ determinacy is known undecidable; pure CQ determinacy is *neither proven decidable nor proven undecidable* — it sits in a narrow open band, with strong evidence (Gogacz–Marcinkowski) that it is hard and that natural rewriting languages are incomplete. Separately, the gap between **determinacy and rewritability** is genuinely open in expressive power: we lack a characterization of exactly which determined queries are FO- (or Datalog-) rewritable. Closing it needs either a decision procedure for CQ determinacy or an undecidability reduction reaching the CQ case.

## 7. Current Research (as of June 2026)

- Pinning the **exact decidability boundary** of determinacy between CQs and UCQs (Gogacz, Marcinkowski, and collaborators). *(frontier — verify)* Partial decidability results for "**packed**" / bounded-treewidth CQ classes are an active target.
- **Determinacy under integrity constraints / the chase** (Benedikt, ten Cate, Pieris) — using constraints to make rewriting decidable and to certify losslessness.
- **Datalog and recursive rewritings** as a more complete target language than FO (ten Cate, Dalmau).
- *(frontier — verify)* Renewed systems interest from **semantic caching and learned/ materialized-view recommendation** for cloud warehouses, where determinacy underpins correctness of view-based query acceleration.

## 8. Future Work

- Settle decidability of CQ-to-CQ determinacy.
- Characterize the class of determined queries admitting FO / Datalog rewritings.
- Determinacy and rewriting under bag (multiset) semantics, which behaves differently.
- Practical determinacy-aware view selection and semantic caching in cloud query engines.

## 9. Key References

- **[Foundational]** A. Y. Levy, A. O. Mendelzon, Y. Sagiv, D. Srivastava. *Answering queries using views.* PODS, 1995. — [DOI](https://doi.org/10.1145/212433.220198)
- **[Foundational]** L. Segoufin, V. Vianu. *Views and queries: determinacy and rewriting.* PODS, 2005. — [PDF](https://www.di.ens.fr/~segoufin/Papers/Mypapers/views.pdf)
- **[SOTA]** A. Nash, L. Segoufin, V. Vianu. *Views and queries: determinacy and rewriting.* ACM TODS, 2010. — [DOI](https://doi.org/10.1145/1806907.1806913)
- **[SOTA]** T. Gogacz, J. Marcinkowski. *The hunt for a red spider: conjunctive query determinacy is undecidable.* LICS, 2015. — [arXiv](https://arxiv.org/abs/1501.01817)
- **[SOTA]** R. Pottinger, A. Y. Halevy. *MiniCon: a scalable algorithm for answering queries using views.* VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100048)
- **[Survey]** A. Y. Halevy. *Answering queries using views: a survey.* VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100054)

## 10. Worked Example

Let the base relation be $E(x,y)$ (a directed graph). Define one view and one query:
$$V(x,z) \,\text{:-}\, E(x,y), E(y,z) \quad(\text{2-paths}), \qquad Q(x,w) \,\text{:-}\, E(x,y),E(y,z),E(z,w) \;(\text{3-paths}).$$

Does $V$ determine $Q$? Consider two databases:
- $D_1 = \{E(1,2),E(2,3),E(3,4)\}$ gives $V = \{(1,3),(2,4)\}$ and $Q=\{(1,4)\}$.
- $D_2 = \{E(1,2),E(2,3),E(3,4),E(2,4)\}$ — but this changes $V$ (adds $(2,?)$ only if there is an outgoing edge from the $z$), so it is not a valid counterexample here.

The known result (Afrati; Nash–Segoufin–Vianu) is that for such *path views/queries* $V \twoheadrightarrow Q$ can hold yet admit **no CQ rewriting**: $Q$ = "3-path" cannot be written as a CQ over the single view "2-path" because composing two 2-paths yields a 4-path, and one 2-path yields only length 2. There is no way to assemble length 3 from copies of length-2 atoms in a CQ. This concretely exhibits the section-5 gap: *determined but not CQ-rewritable*, the heart of why rewriting languages are incomplete.

---
*Part of the [DBMS Research catalog](../../README.md).*
