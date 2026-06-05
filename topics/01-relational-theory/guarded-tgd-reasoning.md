# Separability and Decidable Guarded TGDs

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/guarded-tgd-reasoning` · **Status:** partially-solved

## 1. Problem Statement

**Tuple-generating dependencies** (tgds, a.k.a. existential rules / Datalog$^\pm$) of the form $\forall \bar x\,\bar y\,\big(\phi(\bar x,\bar y)\to\exists \bar z\,\psi(\bar x,\bar z)\big)$ underpin ontology-mediated query answering and data integration. Unrestricted tgds make **certain-answer / CQ-entailment** (does $\mathcal{D},\Sigma\models Q$?) **undecidable** because the chase may not terminate. The central problem is to **delineate the decidability frontier** and **pin combined/data complexity** for syntactic restrictions — chiefly **guarded** tgds (a body atom containing all body variables) and **frontier-guarded** tgds (an atom containing all *frontier* variables $\bar x$ shared with the head). A connected question is **separability**: when does a set of tgds *not interfere* with egds/keys, so the two can be reasoned about independently.

**Variants.** *Decision*: CQ entailment / BCQ answering. *Boundedness & FO-rewritability*: is the rule set FO/UCQ-rewritable (first-order rewritability, key to ontology-based data access)? *Combined vs. data complexity*.

## 2. Mathematical Foundations

The semantics is given by the (possibly infinite) **chase**: certain answers $=$ answers true in *every* model $=$ answers over the chase (a universal model). Decidability is recovered when the chase, though infinite, has **bounded treewidth** or is **finitely controllable**.

- **Guarded tgds** generate chases of **bounded treewidth**; BCQ answering reduces to satisfiability in the **guarded fragment** of first-order logic, which is decidable (2EXPTIME-complete).
- **Frontier-guarded tgds (FGTGD)** strictly extend guarded and weakly-guarded rules while preserving bounded-treewidth chases; they capture many description-logic ontologies and remain decidable.
- **Separability (Calì–Gottlob–Pieris):** $\Sigma_T$ (tgds) and $\Sigma_E$ (egds/keys) are *separable* if egds never cause new chase failures or new entailments beyond the tgd-chase; then one reasons over tgds alone. **Non-conflicting keys** are a sufficient syntactic condition.

The relevant abstract notion is **bounded-treewidth model property** (BTW): query answering over BTW model classes is decidable by Courcelle/automata techniques.

## 3. State of the Art (SOTA)

- **Theory SOTA**: the **Datalog$^\pm$** family (Calì, Gottlob, Lukasiewicz, Pieris) maps the decidability landscape: **(weakly-)guarded**, **frontier-guarded**, **sticky**, **(weakly-)acyclic**, and **bounded** tgds, each with known complexity. Guarded: 2EXPTIME-complete combined, PTIME data; FGTGD: 2EXPTIME combined, PTIME data. **Sticky** and **linear** tgds add **FO-rewritability** (AC$^0$ data). Baget–Leclère–Mugnier–Thomazo unify these via *(greedy) bounded-treewidth sets*.
- **Systems SOTA**: reasoners/engines such as **VADALOG** (Oxford/Banca d'Italia), **Graal**, **Llunatic**, **RDFox** (for the OWL 2 RL / Datalog fragment), and **PDQ** implement chase-based or rewriting-based query answering for decidable fragments at scale.

## 4. Upper Bound

- **Guarded tgds:** BCQ entailment **2EXPTIME-complete** (combined), **PTIME-complete** in data complexity; **EXPTIME** combined for bounded arity / fixed predicates.
- **Frontier-guarded tgds:** **2EXPTIME** combined, **PTIME** data (Baget–Mugnier–Thomazo; via bounded-treewidth automata).
- **Linear / sticky tgds:** **PSPACE/EXPTIME** combined and **FO-rewritable** ⇒ **AC$^0$** data complexity, enabling SQL rewriting.
- With **separable** egds/keys, these bounds carry over unchanged (egds add no cost).

## 5. Lower Bound

- General tgds: **undecidable** (unbounded chase ⇒ reduction from Turing-machine halting / Datalog boundedness arguments).
- **Guarded** BCQ answering is **2EXPTIME-hard** (combined) — matching the upper bound — and **PTIME-hard** in data complexity (inherited from Datalog).
- **Frontier-guarded** is **2EXPTIME-hard** combined.
- For egds: without separability, adding keys to even simple tgds (e.g., inclusion + functional dependencies) makes implication/entailment **undecidable**, which is why separability conditions are essential.

## 6. The Gap

For the named fragments the bounds are **tight** (matching upper/lower) — these are *closed*. The genuinely **open** frontier is: (i) maximal *decidable* superclasses unifying guarded, sticky, and acyclic without losing PTIME data; (ii) precise **FO-/Datalog-rewritability** boundaries (which decidable fragments are also rewritable, crucial for OBDA); (iii) decidable, *broad* separability criteria for egds beyond non-conflicting keys; (iv) tight bounds for *combinations* (e.g., frontier-guarded + transitivity / counting).

## 7. Current Research (as of June 2026)

Groups: **Gottlob / Pieris / Sallinger (Oxford, Edinburgh, TU Wien — VADALOG)**, **Mugnier / Thomazo / Bourhis (Montpellier/Lille)**, **Benedikt / Bourhis / Vanden Boom (Oxford)**, **Calautti / Console**. Threads: **warded** and **protected** Datalog$^\pm$ (VADALOG's tractable-data fragment) for enterprise reasoning; rewritability and **bounded-derivation-depth** characterizations; **separability** generalizations and chase optimization; and integrating existential-rule reasoning with **probabilistic / neuro-symbolic** pipelines *(frontier — verify)*. Renewed work links guarded fragments to **knowledge-graph** query answering at scale.

## 8. Future Work

(1) A unifying decidable class strictly above frontier-guarded + sticky with PTIME data. (2) Complete the FO/Datalog-rewritability map for OBDA. (3) Broader, automatically-checkable separability for egds/keys. (4) Practical chase termination / acceleration (MFA/MSA refinements) and incremental reasoning. (5) Combined complexity of guarded rules with arithmetic, aggregation, or transitive closure.

## 9. Key References

- **[Foundational]** Beeri, Vardi. *The Implication Problem for Data Dependencies* (undecidability of tgd implication). ICALP 1981. — [DOI](https://doi.org/10.1007/3-540-10843-2_7)
- **[Foundational]** Calì, Gottlob, Lukasiewicz. *A General Datalog-Based Framework for Tractable Query Answering over Ontologies (Datalog$^\pm$).* PODS 2009 / JWS. — [DOI](https://doi.org/10.1145/1559795.1559809)
- **[SOTA]** Calì, Gottlob, Pieris. *Towards More Expressive Ontology Languages: The Query Answering Problem* (separability, non-conflicting keys). Artificial Intelligence, 2012. — [DOI](https://doi.org/10.1016/j.artint.2012.08.002)
- **[SOTA]** Baget, Leclère, Mugnier, Salvat. *On Rules with Existential Variables: Walking the Decidability Line.* Artificial Intelligence, 2011. — [DOI](https://doi.org/10.1016/j.artint.2011.03.002)
- **[SOTA]** Bárány, Gottlob, Otto. *Querying the Guarded Fragment.* LICS 2010 / LMCS. — [arXiv](https://arxiv.org/abs/1309.5822)
- **[SOTA]** Bellomarini, Gottlob, Sallinger. *The Vadalog System: Datalog-based Reasoning for Knowledge Graphs.* VLDB 2018. — [DOI](https://doi.org/10.14778/3213880.3213888)
- **[Survey]** Mugnier, Thomazo. *An Introduction to Ontology-Based Query Answering with Existential Rules.* Reasoning Web, 2014. — [DOI](https://doi.org/10.1007/978-3-319-10587-1_6)

## 10. Worked Example

A guarded TGD whose chase is infinite yet has bounded treewidth. Take the single rule

$$\rho:\quad \text{Person}(x) \;\to\; \exists y\ \big(\text{Person}(y) \wedge \text{parent}(y, x)\big),$$

with database $\mathcal{D} = \{\text{Person}(a)\}$. The body atom $\text{Person}(x)$ is a guard (it contains every body variable), so $\rho$ is guarded. Chasing: $\text{Person}(a)$ fires $\rho$, inventing null $n_1$ with $\text{parent}(n_1,a)$; then $\text{Person}(n_1)$ fires again, inventing $n_2$, and so on — an *infinite* ancestor chain $a \leftarrow n_1 \leftarrow n_2 \leftarrow \cdots$.

The chase never terminates, yet the result is a tree (a path), so its treewidth is $1$. By the bounded-treewidth model property, BCQ answering is decidable: the BCQ $Q :\!-\, \text{parent}(u,v),\text{parent}(w,u)$ ("someone has a grandparent") is *entailed*, since $\text{parent}(n_2,n_1),\text{parent}(n_1,a)$ appears after two steps. Contrast: replace the body with an unguarded conjunction over independent variables and the chase can build a grid (unbounded treewidth), which is exactly where decidability is lost. The guard is what keeps complexity at 2EXPTIME-complete combined, PTIME in data.

---
*Part of the [DBMS Research catalog](../../README.md).*
