# Provenance-Aware View Update

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/provenance-aware-view-update` · **Status:** partially-solved

## 1. Problem Statement
Given a view $V = Q(D)$ defined by a query $Q$ over base relations $D = \{R_1,\dots,R_n\}$, and a requested update $u$ to $V$ (insert, delete, or modify a tuple), find a *translation* $T$ — a set of updates to $D$ — such that re-evaluating $Q$ on the updated database yields exactly the updated view: $Q(T(D)) = u(V)$. The classical **view update problem** asks for translations that are *correct* (no view side effects: only the requested change appears, nothing else moves) and *minimal* (no unnecessary base changes). The provenance-aware variant asks: can fine-grained provenance (which base tuples/cells *witness* each view tuple) make the translation **unambiguous** and **side-effect-free**, and when no such translation exists, certify the obstruction?

Variants: **(decision)** does a side-effect-free translation exist? **(search)** produce one. **(counting/enumeration)** enumerate all minimal translations. **(optimization)** find the translation minimizing a cost (number of base updates, weighted by trust/cost annotations).

## 2. Mathematical Foundations
The semantic gold standard is the **constant-complement** framework (Bancilhon–Spyratos): a view is updatable without side effects on the part of the database fixed by a *complement* view $C$; the pair $(V, C)$ must determine $D$ via a bijection, and the chosen complement fixes a unique update policy. Formally, a translator is well-behaved iff it keeps some complement constant.

Provenance refines this. For positive relational algebra, **why-provenance**, **lineage**, and the **provenance semiring** $\mathbb{N}[X]$ (Green–Karvounarakis–Tannen) annotate each output tuple with a polynomial over base-tuple variables; selection/projection/join/union map to $+$ and $\times$ in a commutative semiring $(K, +, \times, 0, 1)$. A deletion of view tuple $t$ with provenance polynomial $p_t$ must falsify $p_t$, i.e. make the monomial-set evaluate to $0$; the *minimal* deletions correspond to a **minimal hitting set** over the monomials (one base tuple per monomial). Insertions require finding a valuation extending the active domain that produces the new monomial without spuriously satisfying other polynomials (the side-effect condition). Where-provenance (cell origin) governs *modify* translations.

$$ \text{del}(t)\ \text{side-effect-free} \iff \exists\, S \subseteq \text{supp}(p_t):\ \big(\forall m \in \text{mon}(p_t)\ S \cap m \neq \emptyset\big)\ \wedge\ \big(\forall t' \neq t:\ S \cap \text{supp}(p_{t'}) = \emptyset\big). $$

## 3. State of the Art (SOTA)
- **Theory:** Bancilhon–Spyratos constant complements (1981) remain the semantic reference. Cosmadakis–Papadimitriou characterized updatability complexity for select-project-join views. Keller's five conditions enumerate side-effect-free translation strategies for SPJ views.
- **Systems / languages:** *relational lenses* (Bohannon–Pierce–Vaughan, PODS 2006; and Horn–Cheney's verified lenses) give a compositional, provably round-tripping account of updatable views. **Putback-based bidirectional transformation** (Hu, Ko) treats the update direction as primary. Provenance engines **ProvSQL** (Senellart et al., VLDB 2018) and **Perm/GProM** (Glavic, Arab et al.) compute the semiring annotations that drive translation. SQL Server / PostgreSQL support `INSTEAD OF` triggers as a manual escape hatch, conceding the automatic-translation problem.

## 4. Upper Bound
For **SPJU** views over $\mathbb{N}[X]$, checking and producing a side-effect-free deletion reduces to minimal hitting set over the provenance monomials: NP-hard in general but **polynomial when each view tuple's provenance is a single monomial** (e.g. SPJ without union/self-join, or key-preserving joins), giving an $O(|p_t|)$ translation. Lens languages guarantee **PTIME, total, well-behaved** round-tripping by construction (type system rejects non-updatable compositions). Enumeration of all minimal deletions is solvable with polynomial delay via hitting-set enumeration when provenance width is bounded.

## 5. Lower Bound
The general side-effect-free deletion problem is **NP-hard**: minimum-witness deletion encodes **minimum hitting set / vertex cover** over provenance monomials. Cosmadakis–Papadimitriou show deciding existence of a complement-based translation is intractable for unrestricted SPJ views. For insertions, the side-effect-avoidance constraint (no other view tuple may appear) makes existence **coNP-hard** to certify in the presence of joins, because one must verify a universally-quantified non-emergence condition over the (exponential) space of candidate base insertions. No translation policy can be simultaneously total, side-effect-free, and minimal for all SPJU views — an impossibility inherited from the ambiguity of inverting many-to-one $\pi/\bowtie$.

## 6. The Gap
Closed for restricted classes (lenses, single-monomial SPJ): tight PTIME up/down. Genuinely **open** in the middle: for views with bounded provenance width $w$, is side-effect-free deletion FPT in $w$, or W[1]-hard? The boundary between "provenance makes the translation unique" and "irreducibly ambiguous" is not sharply characterized for aggregation and recursive (Datalog) views, where the semiring is $\mathbb{N}[[X]]$ (formal power series) and minimality is undefined.

## 7. Current Research (as of June 2026)
- Extending verified bidirectional lenses to **aggregation and grouping** with provenance-justified update policies (Cheney, Hu groups).
- **GProM**-style reenactment to *simulate* a proposed translation and detect side effects before committing (Glavic). *(frontier — verify)* Work coupling provenance polynomials with SMT to synthesize minimal side-effect-free translations.
- Provenance for **differential / incremental view maintenance** repurposed to *invert* the maintenance delta, treating view update as "run IVM backwards" *(frontier — verify)*.

## 8. Future Work
Characterize updatability via a provenance-width parameter; FPT/W[1] dichotomy. Trust- and cost-weighted minimal translations (which base source to edit when several witness a tuple). Update translation under integrity constraints via the chase. Interactive translation that surfaces the ambiguity to a human when no unique side-effect-free choice exists.

## 9. Key References
- **[Foundational]** François Bancilhon, Nicolas Spyratos. *Update Semantics of Relational Views.* ACM TODS, 1981. — [DOI](https://doi.org/10.1145/319628.319634)
- **[Foundational]** Stavros Cosmadakis, Christos Papadimitriou. *Updates of Relational Views.* JACM, 1984. — [DOI](https://doi.org/10.1145/1634.1887)
- **[Foundational]** Todd Green, Grigoris Karvounarakis, Val Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[SOTA]** Aaron Bohannon, Benjamin C. Pierce, Jeffrey A. Vaughan. *Relational Lenses: A Language for Updatable Views.* PODS, 2006. — [DOI](https://doi.org/10.1145/1142351.1142399)
- **[SOTA]** Pierre Senellart, et al. *ProvSQL: Provenance and Probability Management in PostgreSQL.* PVLDB, 2018. — [DOI](https://doi.org/10.14778/3229863.3236253) · [DBLP](https://dblp.org/rec/journals/pvldb/SenellartJMR18.html)
- **[Survey]** James Cheney, Laura Chiticariu, Wang-Chiew Tan. *Provenance in Databases: Why, How, and Where.* Foundations and Trends in Databases, 2009. — [DOI](https://doi.org/10.1561/1900000006)

## 10. Worked Example

Let $R(A,B)$ have base tuples $r_1=(1,x),\,r_2=(1,y),\,r_3=(2,x)$ and $S(B,C)$ have $s_1=(x,9),\,s_2=(y,8)$. The view $V = \pi_{A,C}(R \bowtie S)$ produces:

| A | C | provenance $p_t$ |
|---|---|------------------|
| 1 | 9 | $r_1 s_1$ |
| 1 | 8 | $r_2 s_2$ |
| 2 | 9 | $r_3 s_1$ |

Request: **delete** view tuple $t=(1,9)$. Its provenance is the single monomial $r_1 s_1$, so any side-effect-free deletion must falsify it: a minimal hitting set picks one of $\{r_1, s_1\}$.

Deleting $r_1$ touches no other monomial — safe. But deleting $s_1$ also kills $r_3 s_1$, so tuple $(2,9)$ vanishes — a **side effect**. The side-effect condition $\forall t'\neq t:\ S\cap\text{supp}(p_{t'})=\varnothing$ rules $s_1$ out (it appears in $(2,9)$'s provenance) and selects $S=\{r_1\}$ as the unique side-effect-free translation.

Because every view tuple here has a single monomial, the hitting set is trivial and translation is PTIME. Introduce a union or self-join so some $p_t$ has several monomials, and the choice becomes a genuine minimum-hitting-set / vertex-cover instance — the NP-hard regime.

---
*Part of the [DBMS Research catalog](../../README.md).*
