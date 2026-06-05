# Information-Theoretic Normal Forms

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/information-theoretic-normalization` · **Status:** partially-solved

## 1. Problem Statement

Classical normal forms (BCNF, 3NF, 4NF) are defined **syntactically**: a schema is "good" if every dependency that could cause redundancy is implied by a key. The goal here is to ground normalization in a **semantic, information-theoretic** measure of redundancy that (i) explains *why* BCNF/4NF eliminate redundancy, (ii) characterizes good designs for constraint classes where syntactic theory is incomplete (e.g., arbitrary tgds/egds, multivalued + functional mixtures), and (iii) yields a *decidable* criterion: given schema $R$ and constraints $\Sigma$, decide whether $R$ is "information-theoretically redundancy-free."

**Variants.** *Decision*: is $R$ in the information-theoretic normal form $\mathrm{(IT\text{-}NF)}$ w.r.t. $\Sigma$? *Optimization*: among lossless, dependency-preserving decompositions, find one minimizing residual redundancy / maximizing per-cell information content.

## 2. Mathematical Foundations

Fix a schema, a set of constraints $\Sigma$, and a domain of size $n$. Consider the uniform distribution over all instances of size up to $n$ satisfying $\Sigma$. For a *position* $p$ (a cell = tuple + attribute), let $X_p$ be its value and $X_{-p}$ the rest of the instance. Define the **relative information content**

$$\mathrm{RIC}_n(p) = \frac{H(X_p \mid X_{-p})}{\log n},$$

the conditional entropy of a cell given everything else, normalized to $[0,1]$. A position has **no redundancy** when $\mathrm{RIC}_n(p)\to 1$ as $n\to\infty$ (the cell is maximally "free"); redundancy means other cells constrain it, so $H(X_p\mid X_{-p}) < \log n$.

**Theorem (Arenas–Libkin).** A schema with FDs is in **BCNF iff** $\inf_p \lim_{n} \mathrm{RIC}_n(p) = 1$ (well-designed = every cell asymptotically carries full information). For FDs+MVDs the same measure characterizes **4NF**. This connects the measure to entropy inequalities and to the **chase**: redundancy appears exactly where the chase forces equalities or new tuples.

## 3. State of the Art (SOTA)

- **Theory SOTA**: the Arenas–Libkin *information-theoretic* framework (PODS 2003 / TODS 2005) provides the canonical $\mathrm{RIC}$ measure and proves BCNF/4NF justification. Kolaitis, Pichler, Sallinger, Savenkov and others extended redundancy measures to **general constraints** and to *fact-level* redundancy (whether a tuple is logically entailed by the rest under $\Sigma$). The "**well-designed**" criterion generalizes BCNF to arbitrary first-order constraints via the no-redundancy condition.
- **Systems SOTA**: no production DBMS computes $\mathrm{RIC}$; practitioners still use syntactic BCNF/3NF synthesis. ML-based *automatic schema design* tools approximate redundancy empirically.

## 4. Upper Bound

For FDs/MVDs, checking the IT-NF criterion is **equivalent** to syntactic BCNF/4NF testing, hence PTIME in the schema (the measure adds explanatory power, not cost). For **fact-level redundancy** under a constraint set $\Sigma$, deciding whether some fact is always entailed reduces to **chase / logical implication**: decidable and in EXPTIME for weakly-acyclic tgds+egds; for full tgds it is in 2EXPTIME via the terminating chase.

## 5. Lower Bound

The general "is this fact redundant under $\Sigma$?" question inherits **undecidability of logical implication** for unrestricted tgds (a corollary of the undecidability of the implication problem / unbounded chase). For decidable classes the implication problem is **EXPTIME-hard** (e.g., for inclusion + functional dependencies) and **coNP-hard** combined complexity for simple FD redundancy checks on a given instance. Entropy-based lower bounds tie redundancy to violations of the **Shannon (polymatroid) inequalities**; non-Shannon inequalities show the entropy region is genuinely harder than linear.

## 6. The Gap

For FD/MVD the theory is **closed** (matches syntactic NFs). The gap is open for **arbitrary constraints**: there is no decidable, dependency-class-independent IT-NF test, and no algorithm that *optimally decomposes* to minimize residual $\mathrm{RIC}$ — current synthesis is heuristic. The link between the **entropy region** (and non-Shannon inequalities) and achievable normal forms is largely unexplored.

## 7. Current Research (as of June 2026)

Groups: **Libkin (Edinburgh/RelationalAI)**, **Kolaitis (UCSC)**, **Sallinger / Pichler (TU Wien)**, **Suciu / Khamis / Ngo** (entropy + information theory in databases, e.g., information inequalities for query bounds). Active threads: connecting $\mathrm{RIC}$ to the **AGM/entropic bounds** used in worst-case-optimal joins; redundancy under **denial constraints and conditional FDs**; *learned* normalization that optimizes an information objective *(frontier — verify)*; and redundancy semantics for **JSON/nested** and **graph** schemas.

## 8. Future Work

(1) A decidable IT-NF criterion for the largest possible constraint class. (2) Optimization algorithms producing redundancy-minimal, dependency-preserving designs with provable guarantees. (3) Use of **non-Shannon inequalities** to separate achievable designs. (4) Bridging entropic database bounds (join size) with entropic schema quality. (5) Empirical IT-NF on real, dirty data with approximate dependencies.

## 9. Key References

- **[Foundational]** Codd. *Further Normalization of the Data Base Relational Model.* IBM Research, 1971. — [DBLP](https://dblp.org/rec/persons/Codd71a.html)
- **[Foundational]** Arenas, Libkin. *An Information-Theoretic Approach to Normal Forms for Relational and XML Data.* PODS 2003 / JACM 2005. — [PDF](https://marceloarenas.cl/publications/jacm05.pdf)
- **[SOTA]** Kolaitis, Pichler, Sallinger, Savenkov. *Nested Dependencies / Well-Designed Schemas* (redundancy under general constraints), PODS/ICDT, 2010s. — [DOI](https://doi.org/10.1145/2594538.2594544)
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* PODS 2017. — [arXiv](https://arxiv.org/abs/1612.02503)
- **[Survey]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (Ch. on dependency theory). — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)

## 10. Worked Example

Take $R(\text{Course}, \text{Instructor}, \text{Dept})$ with the FD $\text{Instructor} \to \text{Dept}$ (each instructor sits in one department), and instance:

| Course | Instructor | Dept |
|--------|-----------|------|
| CS101  | Lee       | CS   |
| CS305  | Lee       | CS   |
| EE201  | Roy       | EE   |

This is **not** BCNF: $\text{Instructor}$ is not a key, yet it determines $\text{Dept}$. Pick the redundant cell $p$ = (row 2, Dept). Given everything else, the FD forces $\text{Dept}=\text{CS}$ from row 1's Lee, so $H(X_p \mid X_{-p}) = 0$ and $\mathrm{RIC}_n(p) = 0/\log n = 0$ — maximal redundancy.

Decompose into $R_1(\text{Instructor},\text{Dept})$ and $R_2(\text{Course},\text{Instructor})$ (BCNF, lossless via $\bowtie$ on Instructor). Now in $R_1$ each $\text{Dept}$ cell is pinned only by its own key value with no duplicate constraint across rows, so for the analogous free cell $H(X_p\mid X_{-p}) \to \log n$ and $\mathrm{RIC}_n(p)\to 1$. The measure quantitatively confirms the BCNF design removed the redundancy.

---
*Part of the [DBMS Research catalog](../../README.md).*
