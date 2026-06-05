# RPQ containment and equivalence decidability

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/rpq-containment` · **Status:** partially-solved

## 1. Problem Statement

Given two queries $Q_1, Q_2$ in a navigational graph-query language, **containment** $Q_1 \sqsubseteq Q_2$ asks whether $Q_1(G) \subseteq Q_2(G)$ for *every* graph $G$; **equivalence** $Q_1 \equiv Q_2$ is two-way containment. Containment is the engine of query optimization: rewriting, view-based answering, redundancy elimination, and minimization all reduce to it.

We consider the hierarchy:
- **RPQ** (regular expressions over labels),
- **2RPQ** (with inverse labels),
- **CRPQ / C2RPQ** (conjunctions),
- **UC2RPQ** (unions of C2RPQs, with inverses).

The problem: give **tight complexity** and **practical decision procedures** for containment/equivalence across this hierarchy (and their unions with inverses), distinguishing the cleanly-decidable cases from those bordering undecidability (e.g. when *data values*, *path variables*, or *counting* are added).

## 2. Mathematical Foundations

Single RPQ containment $r_1 \sqsubseteq r_2$ is exactly **regular-language containment** $L(r_1)\subseteq L(r_2)$, decided by NFA complementation + emptiness — **PSPACE-complete**. For CRPQs the relevant tool is the **canonical database / frozen** technique (à la Chandra–Merlin for CQs) lifted to regular languages: $Q_1 \sqsubseteq Q_2$ iff $Q_2$ has a "homomorphism" (a *query expansion* mapping) into every *canonical expansion* of $Q_1$. Because RPQ atoms expand to *infinitely many* relational CQs (one per word length), one reasons over **automata on the space of expansions**, giving an **EXPSPACE** procedure (Calvanese–De Giacomo–Lenzerini–Vardi). The proofs use *two-way automata*, *tree automata*, and for tight lower bounds, *tiling / Turing-machine encodings*. Adding inverses (2-way) preserves decidability via two-way automata closure.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Calvanese, De Giacomo, Lenzerini, Vardi established containment of **(U)C2RPQs is EXPSPACE-complete** (PODS 2000 / ICDT lineage). Florescu–Levy–Suciu (PODS 1998) gave the first results for CQs with regular path expressions. Refinements: *bounded-treewidth* and *acyclic* CRPQ containment drop to lower levels (PSPACE / coNP regions); Barceló, Figueira, Romero, and Reutter map the fine structure, including **C2RPQs with path/variable comparisons** (often undecidable) and approximation/minimization.
- **Systems-SOTA:** Practical SPARQL property-path containment is largely unimplemented at full generality; engines use *sound-but-incomplete* rewrite rules. The W3C SPARQL property-path semantics and the **GQL** standard renew interest in decidable optimization fragments.

## 4. Upper Bound

- **RPQ / 2RPQ containment:** **PSPACE** (regular containment via complementation + emptiness; two-way automata for inverses).
- **(U)C2RPQ containment:** **EXPSPACE** via the automata-on-expansions construction (Calvanese et al.) — a single exponential blowup over CQ containment's NP.
- **Restricted fragments:** acyclic / bounded-treewidth CRPQ containment is in **PSPACE** or lower; containment of an RPQ in a CRPQ and minimization results have matching tractable cases. These bounds are in the standard alternating-Turing-machine / automata model.

## 5. Lower Bound

- **RPQ containment is PSPACE-hard** (from NFA universality / regular-expression inequivalence — Meyer–Stockmeyer).
- **(U)C2RPQ containment is EXPSPACE-hard** (Calvanese–De Giacomo–Lenzerini–Vardi, PODS 2000), matching the upper bound — the hardness comes from forcing exponentially long canonical expansions, encoded via tiling/Turing-machine simulation.
- **Undecidability frontier:** extending CRPQs with **path/data-value comparisons**, **register/data-path** features, or **counting** (e.g. CRPQs with arithmetic on path lengths) makes containment **undecidable** (reductions from PCP / Turing-machine halting). Thus the decidable core sits right below several natural extensions.

## 6. The Gap

**Partially solved.** The *worst-case complexity* is **tight** for the central fragments: RPQ/2RPQ containment is PSPACE-complete and (U)C2RPQ containment is EXPSPACE-complete — upper and lower bounds **match**. The remaining gaps are *practical and structural*: (1) EXPSPACE is hopeless in practice, so the open problem is **efficient decision procedures / heuristics** that are complete on the fragments arising in real workloads; (2) the exact decidability boundary for *expressive extensions* (data values, path comparisons, regular-relation atoms, counting) is only partially mapped; (3) tight bounds for *approximate* containment and for containment **under integrity constraints / schema** (e.g. PG-Schema, shapes). Closing it is less about complexity classes than about *useful, implementable* algorithms.

## 7. Current Research (as of June 2026)

- *(frontier — verify)* Decidability/complexity of containment for **GQL/SQL-PGQ** path patterns under restricted path modes (TRAIL/ACYCLIC/SHORTEST), where semantics differ from classical arbitrary-path RPQs (groups: Edinburgh, Oxford, IMFD Chile, Warsaw).
- Containment for **C2RPQs with comparisons / data paths** — pinpointing decidable islands (Figueira, Barceló, Romero).
- *(frontier — verify)* practical *incomplete-but-useful* containment checkers integrated into graph optimizers and view-based rewriting for property paths.

## 8. Future Work

- Implementable containment/minimization for the CRPQ fragments used in SPARQL/Cypher/GQL.
- Decidability map for navigational queries with data, counting, and aggregation.
- Containment under schemas/constraints (PG-Schema, shape constraints, key/inclusion dependencies).
- Approximate and parameterized (FPT) containment to sidestep EXPSPACE in practice.

## 9. Key References

- **[Foundational]** Florescu, Levy, Suciu. *Query Containment for Conjunctive Queries with Regular Expressions.* PODS 1998. — [DOI](https://doi.org/10.1145/275487.275503)
- **[Foundational]** Calvanese, De Giacomo, Lenzerini, Vardi. *Containment of Conjunctive Regular Path Queries with Inverse.* KR 2000 / *Reasoning on Regular Path Queries.* SIGMOD Record 2003. — [KR 2000](https://www.inf.unibz.it/~calvanese/papers-html/KR-2000.html)
- **[Foundational]** Chandra, Merlin. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC 1977 (containment via homomorphism). — [DOI](https://doi.org/10.1145/800105.803397)
- **[SOTA]** Barceló, Romero, Vardi. *Semantic Acyclicity on Graph Databases / Does Query Evaluation Tractability Help?* SIGMOD/PODS 2013–2016. — [DOI](https://doi.org/10.1145/2463664.2463671)
- **[SOTA]** Figueira. *Containment of UC2RPQs: The Hard and Easy Cases.* ICDT 2020. — [DOI](https://doi.org/10.4230/LIPIcs.ICDT.2020.9)
- **[Survey]** Barceló. *Querying Graph Databases.* PODS 2013 (tutorial); Angles et al. *Foundations of Modern Query Languages for Graph Databases.* ACM Computing Surveys 2017. — [DOI](https://doi.org/10.1145/3104031) — [arXiv](https://arxiv.org/abs/1610.06264)

## 10. Worked Example

**Single-RPQ containment as language containment.** Let $r_1 = a\,(b\,a)^{*}$ and $r_2 = (a\,b)^{*}\,a$ over $\Sigma=\{a,b\}$. Both define exactly the words $a, aba, ababa, \dots$ — i.e. $L(r_1)=L(r_2)=a(ba)^{*}$. To decide $r_1 \sqsubseteq r_2$ we build NFAs $A_1,A_2$, complement $A_2$ (subset construction → DFA → swap accepting states), and test $L(A_1)\cap \overline{L(A_2)}=\emptyset$. The product is empty, so $r_1\sqsubseteq r_2$; symmetrically $r_2\sqsubseteq r_1$, hence $r_1\equiv r_2$. The complementation step is the source of the **PSPACE** upper bound: $\overline{L(A_2)}$ can need $2^{|A_2|}$ states, but emptiness is checked on-the-fly in polynomial space.

**Why CRPQs jump to EXPSPACE.** Consider $Q_1(x,y) \leftarrow x \xrightarrow{a^{*}} y$ contained in $Q_2(x,y)\leftarrow x\xrightarrow{a}z_1\xrightarrow{a}\dots\xrightarrow{a}y$. Checking containment requires reasoning over *canonical expansions* of $Q_1$ of every length $a^k$; a single CRPQ atom unfolds into infinitely many CQs, and certifying that $Q_2$ maps into all of them forces an automaton over expansions whose size is single-exponential — matching the EXPSPACE-completeness of (U)C2RPQ containment.

---
*Part of the [DBMS Research catalog](../../README.md).*
