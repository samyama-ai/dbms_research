---
id: 01-relational-theory/cq-containment-under-constraints
title: "Conjunctive Query Containment Under Constraints"
topic: 01-relational-theory
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Conjunctive Query Containment Under Constraints

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/cq-containment-under-constraints` · **Status:** partially-solved

## 1. Problem Statement

Given two conjunctive queries $Q_1, Q_2$ and a set $\Sigma$ of integrity constraints (TGDs and EGDs), **containment under constraints** asks whether
$$Q_1 \subseteq_\Sigma Q_2 \quad\Longleftrightarrow\quad \forall D \models \Sigma:\; Q_1(D) \subseteq Q_2(D).$$

Without constraints, $Q_1 \subseteq Q_2$ iff a containment mapping (homomorphism) from $Q_2$ to $Q_1$ exists (Chandra–Merlin) — NP-complete. With constraints, containment must hold over the restricted universe of models of $\Sigma$, which both *adds* containments (constraints can force them) and entangles the problem with the (often undecidable) implication problem.

Variants:
- **Decision:** does $Q_1 \subseteq_\Sigma Q_2$ hold? (primary)
- **Equivalence under constraints:** $Q_1 \equiv_\Sigma Q_2$.
- **Certain-answer / query-answering** reformulation: $Q_1$ is the (frozen) canonical database; containment reduces to evaluating $Q_2$ over $\mathrm{chase}(Q_1,\Sigma)$.

Status: **partially solved** — undecidable for arbitrary TGDs, with large, well-characterized decidable fragments.

## 2. Mathematical Foundations

A CQ is $Q(\bar{x}) \leftarrow \exists \bar{y}\, \phi(\bar{x},\bar{y})$ with $\phi$ a conjunction of atoms; equivalently a homomorphism question on its **canonical (frozen) database**. The bridge to constraints is the **chase**: by the universal-model property,
$$Q_1 \subseteq_\Sigma Q_2 \iff Q_2 \text{ maps homomorphically into } \mathrm{chase}(\hat{Q_1},\Sigma),$$
where $\hat{Q_1}$ is $Q_1$'s frozen body. Hence **decidability of containment under $\Sigma$ tracks decidability of the chase / certain answering** for $\Sigma$. The relevant fragments are exactly those guaranteeing finite or finitely-controllable universal models: **weakly acyclic** TGDs, and the *guarded* family — **guarded, frontier-guarded, sticky, warded, shy** (Datalog$^\pm$) — which ensure decidable query answering even when the chase is infinite.

## 3. State of the Art (SOTA)

Foundations: **Chandra–Merlin (1977)** for the unconstrained case; **Johnson–Klug (1984)** for containment under FDs and INDs. The modern theory is **Datalog$^\pm$** (Calì–Gottlob–Lukasiewicz–Pieris, 2009–2013), which catalogs decidable TGD classes and their precise complexity for query answering (= containment). **Bárány–ten Cate–Segoufin** established the deep equivalence between guarded TGDs and the **guarded fragment / guarded negation fragment** of first-order logic, giving 2EXPTIME-completeness. **Gottlob–Manna–Pieris** delivered combined-complexity dichotomies across the hierarchy. Systems-SOTA: ontology-based data access (Ontop, VADALOG, Stardog) implement query rewriting (e.g., perfect rewriting for linear/sticky TGDs) so containment-style reasoning runs over real SQL/SPARQL backends.

## 4. Upper Bound

- **No constraints:** NP-complete (Chandra–Merlin).
- **FDs + INDs:** decidable; containment under INDs is in 2EXPTIME via the chase (Johnson–Klug for restricted cases is PSPACE).
- **Weakly acyclic TGDs + EGDs:** decidable; certain answering is **coNP-complete in data complexity**, EXPTIME-/2EXPTIME-complete in combined complexity.
- **Guarded TGDs:** query answering / containment is **2EXPTIME-complete** combined, **PTIME** data (Calì–Gottlob–Kifer; Bárány–ten Cate–Segoufin).
- **Linear / sticky / non-recursive TGDs:** **first-order rewritable** — containment reduces to evaluating a UCQ, in $\mathrm{AC}^0$ data complexity, PSPACE/NP combined.

## 5. Lower Bound

- **Unconstrained:** NP-hard (3-colorability reduction, Chandra–Merlin).
- **General TGDs:** containment under arbitrary TGDs is **undecidable** (it subsumes the embedded-dependency implication problem, Beeri–Vardi).
- **FDs + INDs (general):** **undecidable** (Casanova–Fagin–Papadimitriou / Mitchell).
- Within decidable fragments, the bounds are **tight**: guarded TGDs are 2EXPTIME-hard (combined); weakly acyclic TGD answering is coNP-hard in data complexity; bounded-arity guarded cases are EXPTIME-complete.

## 6. The Gap

For the decidable Datalog$^\pm$ classes, upper and lower bounds **match** — these gaps are closed (PTIME/coNP data; EXPTIME/2EXPTIME combined). The genuinely open territory is at the *boundary*: classifying maximal decidable TGD fragments, the exact complexity of mixed TGD+EGD interaction (EGDs can break guardedness and separability), and tighter **fine-grained** complexity within the polynomial-data-complexity cases (is guarded-CQ answering optimally PTIME, or does it admit conditional lower bounds?). Closing these requires either new decidable-class characterizations or fine-grained reductions.

## 7. Current Research (as of June 2026)

(1) **Existential rules / Datalog$^\pm$** refinement: warded and *bounded-derivation-depth* fragments balancing expressivity and tractability (Gottlob, Pieris, Sallinger; the VADALOG project). (2) **EGD–TGD separability** and "harmless" EGD detection so equality reasoning doesn't destroy decidability. (3) **Counting / bag-aware** containment under constraints *(frontier — verify)*. (4) Containment for **CQs with negation, comparisons, and aggregation** under constraints. (5) Practical OBDA rewriting at scale (Ontop, Stardog teams; Calvanese, Xiao, Kontchakov).

## 8. Future Work

- Complete the decidability map for arbitrary TGD+EGD combinations.
- Fine-grained complexity of guarded/frontier-guarded CQ answering.
- Containment under constraints for richer query languages (UCQ$^\neg$, aggregation, recursion).
- Tight bounds for containment under *probabilistic* / *approximate* constraints.

## 9. Key References

- **[Foundational]** A. K. Chandra, P. M. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Data Bases.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Foundational]** D. S. Johnson, A. Klug. *Testing Containment of Conjunctive Queries Under Functional and Inclusion Dependencies.* JCSS, 1984. — [DOI](https://doi.org/10.1016/0022-0000(84)90081-3)
- **[SOTA]** A. Calì, G. Gottlob, T. Lukasiewicz. *A General Datalog-Based Framework for Tractable Query Answering over Ontologies (Datalog±).* JWS / PODS, 2009–2012. — [DOI](https://doi.org/10.1145/1559795.1559809)
- **[SOTA]** V. Bárány, B. ten Cate, L. Segoufin. *Guarded Negation.* JACM, 2015. — [DOI](https://doi.org/10.1145/2701414)
- **[SOTA]** G. Gottlob, M. Manna, A. Pieris. *Combining Decidability Paradigms for Existential Rules / Complexity of Query Answering.* PODS / TOCL, 2013–2015. — [DOI (TPLP)](https://doi.org/10.1017/S1471068413000550)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)

## 10. Worked Example

Schema: $\text{Emp}(e,d)$, $\text{Dept}(d)$. Constraint $\Sigma$: the inclusion dependency $\text{Emp}[d]\subseteq\text{Dept}[d]$, i.e. the TGD $\text{Emp}(e,d)\to\text{Dept}(d)$. Take
$$Q_1(e)\leftarrow \text{Emp}(e,d),\qquad Q_2(e)\leftarrow \text{Emp}(e,d)\wedge \text{Dept}(d).$$
Without constraints $Q_1\not\subseteq Q_2$: the canonical DB of $Q_1$ is $\{\text{Emp}(e_0,d_0)\}$ (freeze the variables), and $Q_2$ has no homomorphism into it because no $\text{Dept}$ atom exists. Now chase with $\Sigma$: the TGD fires, adding $\text{Dept}(d_0)$, giving $\mathrm{chase}(\hat Q_1,\Sigma)=\{\text{Emp}(e_0,d_0),\text{Dept}(d_0)\}$. Now $Q_2$ maps in via $e\mapsto e_0,\,d\mapsto d_0$. Hence $Q_1\subseteq_\Sigma Q_2$ — the constraint *forced* a containment that was false without it. This single chase step (terminating because the IND is non-recursive here) is exactly the decision procedure; with recursive INDs the chase may grow unboundedly, which is why decidability tracks chase behaviour.

---
*Part of the [DBMS Research catalog](../../README.md).*
