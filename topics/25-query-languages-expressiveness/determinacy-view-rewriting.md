---
id: 25-query-languages-expressiveness/determinacy-view-rewriting
title: "Decidable Query Determinacy and View Rewriting"
topic: 25-query-languages-expressiveness
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Decidable Query Determinacy and View Rewriting

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/determinacy-view-rewriting` · **Status:** open

## 1. Problem Statement
Let $\mathcal{V} = \{V_1, \dots, V_k\}$ be a set of view definitions and $Q$ a query. We say $\mathcal{V}$ **determines** $Q$ (written $\mathcal{V} \twoheadrightarrow Q$) if for all databases $D_1, D_2$, $\mathcal{V}(D_1) = \mathcal{V}(D_2) \Rightarrow Q(D_1) = Q(D_2)$: the view extents carry enough information to compute the answer to $Q$. Two coupled questions:

1. **Determinacy (decision):** Is $\mathcal{V} \twoheadrightarrow Q$ decidable for a given query/view language $\mathcal{L}$?
2. **Rewriting (constructive):** When $\mathcal{V} \twoheadrightarrow Q$, does an **equivalent rewriting** of $Q$ exist in a target language $\mathcal{L}'$ (FO, Datalog, the view language itself)?

The deep issue is the possible **mismatch** between determinacy (information-theoretic) and rewritability (expressibility in a fixed language): determinacy may hold while no rewriting in $\mathcal{L}'$ exists ("losslessness without a query plan").

## 2. Mathematical Foundations
Determinacy is a semantic, second-order condition: $\mathcal{V} \twoheadrightarrow Q$ iff $Q$ is constant on each fiber of the map $D \mapsto \mathcal{V}(D)$. A language $\mathcal{L}'$ is a **sound and complete rewriting language for $(\mathcal{L}_V, \mathcal{L}_Q)$** if determinacy implies the existence of an $\mathcal{L}'$-rewriting.

Key tool: **interpolation**. By Craig/Beth definability, if determinacy is expressible as an FO entailment, an FO rewriting exists (Beth definability theorem). Failure of an effective interpolation analogue at finite models is the crux of negative results. The **chase** and the existence of homomorphisms between canonical instances give algorithmic handles for CQ views. Counterexample constructions exploit infinite "unwindings" where finitely many view tuples constrain $Q$ globally but no finite FO formula captures the constraint.

## 3. State of the Art (SOTA)
- **CQ views, CQ query:** determinacy is **undecidable** (Gogacz–Marcinkowski 2015, resolving a long-standing open problem). Earlier, Nash–Segoufin–Vianu (2010) established that even when determinacy holds, CQs are **not complete** as a rewriting language (determinacy ≠ FO-rewritability).
- **Monadic / path views:** decidable fragments exist for monadic views, "boolean" combinations, and chain queries.
- **RPQ/regular views over graphs:** determinacy is decidable for some path-shaped fragments (Francis–Segoufin–Sirangelo; Fan–Geerts; Calvanese et al.).
- **Exact/lossless XML and tree-pattern views:** several decidable cases isolated.

## 4. Upper Bound
For monadic and certain path/tree-pattern view classes, determinacy is decidable in elementary (often EXPTIME/2EXPTIME) time via automata or chase termination. When an FO rewriting is guaranteed, it can be extracted by **interpolant computation** from a proof of the determinacy entailment, with size potentially non-elementary. For "**unions of conjunctive queries with comparisons**" under bag semantics, special tractable cases are known.

## 5. Lower Bound
- **CQ determinacy is undecidable** (Gogacz–Marcinkowski 2015) — the central negative result.
- **Determinacy does not imply CQ- or even FO-rewritability** for CQs (Nash–Segoufin–Vianu 2010): an explicit family of views determines a CQ with no FO rewriting.
- Deciding existence of an **equivalent rewriting** is at least as hard as containment (NP-hard for CQs, and undecidable for recursive classes).

## 6. The Gap
This is a genuinely **open** problem area. We lack: (i) a clean syntactic characterization of which view/query pairs admit a complete rewriting language; (ii) decidability for natural fragments between monadic and full CQ; (iii) understanding of determinacy under **integrity constraints** (TGDs), where the chase changes determinacy nontrivially; (iv) the relationship to **lossless join** and information theory. Closing the gap likely requires a finite-model interpolation theory tailored to relational fragments.

## 7. Current Research (as of June 2026)
Active directions: determinacy and rewriting for **graph/path queries** (UCRPQ views) driven by GQL; **information-theoretic** characterizations linking determinacy to entropy/lossless decomposition; and **constraint-aware** determinacy under existential rules. Researchers include Vianu, Segoufin, Marcinkowski, Barceló, Figueira, Romero, and Pieris. *(frontier — verify)* Recent papers connect "**semantic determinacy**" to the existence of homomorphism-closed rewritings and study determinacy for **Datalog views** and for queries with limited recursion. Work on **certain-answer rewritings** under OWA bridges this page with maximally-contained rewriting.

## 8. Future Work
- Decidability of determinacy for explicit fragments (e.g., acyclic CQs, two-way path views).
- A finite-model interpolation/Beth-definability theory pinpointing complete rewriting languages.
- Determinacy under bag semantics and under TGD/EGD constraints.
- Quantitative "almost-determinacy" and its use in approximate query answering and privacy (view-based information leakage).

## 9. Key References
- **[Foundational]** A. Nash, L. Segoufin, V. Vianu. *Views and queries: Determinacy and rewriting.* ACM TODS, 2010. — [DOI](https://doi.org/10.1145/1806907.1806913)
- **[SOTA]** T. Gogacz, J. Marcinkowski. *The hunt for a red spider: Conjunctive query determinacy is undecidable.* LICS, 2015. — [arXiv](https://arxiv.org/abs/1501.01817)
- **[Foundational]** A. Halevy. *Answering queries using views: A survey.* VLDB Journal, 2001. — [DOI](https://doi.org/10.1007/s007780100054)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[SOTA]** D. Calvanese, G. De Giacomo, M. Lenzerini, M. Vardi. *View-based query processing: On the relationship between rewriting, answering and losslessness.* ICDT, 2005. — [DOI](https://doi.org/10.1007/978-3-540-30570-5_22)

## 10. Worked Example

**A determinacy that *does* yield a rewriting, and the gap it hints at.** Schema: one binary relation $E(x,y)$. Define two CQ views
$$V_1(x,y) = E(x,y),\qquad V_2(x,z) = \exists y\,\big(E(x,y)\wedge E(y,z)\big),$$
and ask whether $\{V_1,V_2\}$ determines the query $Q(x,z)=\exists y\,(E(x,y)\wedge E(y,z))$ (paths of length 2).

Here determinacy holds **trivially and constructively**: $Q\equiv V_2$, so the rewriting is just $Q(x,z):\!-\,V_2(x,z)$. For any two databases with $\mathcal V(D_1)=\mathcal V(D_2)$ we get $V_2(D_1)=V_2(D_2)$, hence $Q(D_1)=Q(D_2)$ — determinacy as required by the fiber definition of §2.

Now perturb: keep only $V_1(x,y)=E(x,y)$ and ask whether $V_1$ determines **even-length reachability** $Q'(x,z)$ = "there is a path of *even* length from $x$ to $z$." Information-theoretically $V_1$ exposes all of $E$, so it *does* determine $Q'$ — yet $Q'$ is **not first-order definable** (parity/transitive-closure is beyond FO, by an Ehrenfeucht–Fraïssé / locality argument). So determinacy holds while no FO rewriting exists; one must climb to Datalog. This is exactly the Nash–Segoufin–Vianu phenomenon — *losslessness without a query plan in the target language* — and it is why determinacy ($V_1\twoheadrightarrow Q'$) and FO-rewritability come apart, the crux of §6.

---
*Part of the [DBMS Research catalog](../../README.md).*
