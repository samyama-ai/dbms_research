# GLAV Query Answering Complexity Census

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/glav-query-answering-complexity` · **Status:** partially-solved

## 1. Problem Statement

In data integration, a mapping relates a global/target schema to sources. The fundamental task is computing **certain answers**: given a mapping $M$ and a query $q$ over the target, return $\mathrm{certain}_M(q, I) = \bigcap_{J \in \mathrm{Sol}_M(I)} q(J)$ for source instance $I$. The **complexity census** asks for a **complete classification** of the complexity of certain-answer evaluation across the two-dimensional grid:

- **Mapping language:** GAV (global-as-view), LAV (local-as-view), GLAV (global-and-local-as-view = source-to-target TGDs), plus extensions (target TGDs/EGDs, second-order SO-tgds, nested/relational, existential rules / guarded / linear).
- **Query language:** conjunctive queries (CQ), unions of CQs, CQ with inequalities ($\ne$), negation, recursion (Datalog), full FO, aggregation.

For each cell of mapping × query × (target constraints? yes/no), pin down **data complexity** and **combined complexity**, and the dividing lines between PTime, coNP-complete, undecidable.

## 2. Mathematical Foundations

Certain answering reduces to evaluation over a **universal solution** (canonical instance) produced by the **chase**. For CQs and GLAV without target constraints, $\mathrm{certain}_M(q,I) = q(\mathrm{chase}_M(I))_{\downarrow}$ (answers without nulls) — **PTime in data**. Inequalities and negation break this monotonicity.

Core dichotomy (Abiteboul–Duschka 1998; refined by many): for **CQ** queries, certain answering is **PTime (data)**; adding **inequalities** pushes LAV/GLAV to **coNP-complete (data)**; **target EGDs/TGDs** can push to coNP-complete or **undecidable** depending on chase termination.

Formal toolkit: the **homomorphism / universal-model** theorem, monotone vs. non-monotone query collapse, **OWA vs CWA** (open vs closed world — Libkin's semantics matters: certain answers differ under closed-world assumptions), and reductions from **2-coloring / 3-SAT / tiling** for the hardness cells. For existential-rule mappings the census aligns with **ontology-mediated query answering** (OMQA) complexity (guarded, sticky, linear → FO-rewritable / AC⁰ vs PTime-complete vs ExpTime).

## 3. State of the Art (SOTA)

- **Theory-SOTA.** The classical grid is largely filled: **Abiteboul–Duschka** (PODS 1998) gave the GAV/LAV × (CQ, Datalog, FO) × (with/without integrity constraints) table, including the coNP and undecidability boundaries. **Fagin–Kolaitis–Miller–Popa** (ICDT 2003) settled GLAV data-exchange CQ answering (PTime) and certain-answer semantics. **Calì–Gottlob–Lukasiewicz** and the **Datalog±** program (guarded/sticky/linear TGDs) extended the census to target constraints with sharp PTime/ExpTime/2ExpTime lines.
- **Systems-SOTA.** OBDA systems realize the FO-rewritable cells: **Ontop** (linear/DL-Lite mappings → SQL rewriting), **Mastro**, **Stardog**. **Graal / PURe** handle guarded existential rules. These exploit the *tractable* cells of the census.

## 4. Upper Bound

- **GLAV + CQ, no target constraints:** certain answering is **PTime in data**, NP-complete in combined complexity (canonical-solution evaluation).
- **GLAV + target TGDs (weakly acyclic) + CQ:** still **PTime in data** (polynomial universal solution).
- **Guarded / linear existential-rule mappings + CQ:** data complexity in **PTime / AC⁰ (FO-rewritable for linear/DL-Lite)**; combined up to **2ExpTime** for guarded.
- These hold in the standard **RAM / logspace-uniform circuit** models; FO-rewritability gives **AC⁰** data complexity.

## 5. Lower Bound

- **CQ⁺ inequalities under LAV/GLAV:** certain answering is **coNP-complete in data** (Abiteboul–Duschka; van der Meyden) — hardness by reduction from non-2-colorability / monotone-3SAT complements.
- **Datalog/recursive queries with constraints, or unrestricted target TGDs:** **undecidable** (reduction from unbounded tiling / chase non-termination).
- **Guarded TGDs combined complexity:** **2ExpTime-complete** (Calì–Gottlob–Kifer / Baget et al.); linear TGDs **PSpace-complete** combined.
- Lower bounds are stated in **NP/coNP**, **PSpace/ExpTime/2ExpTime** completeness, and **$\Sigma^0_1$ undecidability** models respectively.

## 6. The Gap

For the **classical grid** (GAV/LAV/GLAV × CQ/UCQ × ±EGD) the census is **closed** — tight completeness results exist for essentially every cell. The **partially-solved** status comes from the *extended* dimensions: (i) precise data-complexity classification (AC⁰ vs PTime-complete, i.e., **FO-rewritability**) for many existential-rule fragments combined with mapping features is incomplete; (ii) queries with **aggregation, counting (#certain-answers), and limited negation** have scattered, non-uniform results; (iii) **SO-tgds** (closure of GLAV under composition) lack a complete census for non-CQ queries. Closing it means finishing the FO-rewritability frontier and the counting/aggregation rows.

## 7. Current Research (as of June 2026)

Active: completing **FO-rewritability dichotomies** for ontology-mediated/mapping query answering (Bienvenu, Lutz, Kikot, Kontchakov, Zakharyaschev), and **counting certain answers** (#-OMQA) complexity (Kostylev, Reutter; Calautti–Pieris). *(frontier — verify)* 2024–2025 PODS/ICDT work pushes **certain answers for queries with aggregation** and **bag semantics** over GLAV, and revisits **CWA/GCWA⋆ semantics** (Libkin, Hernich) for non-monotone queries. *(frontier — verify)* The **PDQ/access-pattern** community connects the census to federated answering. Active groups: Kolaitis, ten Cate, Pieris, Lutz, Bienvenu.

## 8. Future Work

- A *single* unified census table spanning mapping features, target constraints, and the full query lattice (incl. aggregation/counting), with FO-rewritability marked per cell.
- Parameterized / fine-grained complexity inside the PTime and coNP cells.
- Census under bag and under closed-world (GCWA⋆) semantics.
- Practical rewriting algorithms that are optimal in the tractable cells.

## 9. Key References

- **[Foundational]** S. Abiteboul, O. Duschka. *Complexity of Answering Queries Using Materialized Views.* PODS, 1998.
- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data Exchange: Semantics and Query Answering.* ICDT 2003 / TCS, 2005.
- **[Foundational]** M. Lenzerini. *Data Integration: A Theoretical Perspective.* PODS, 2002.
- **[SOTA]** A. Calì, G. Gottlob, T. Lukasiewicz. *A General Datalog-Based Framework for Tractable Query Answering over Ontologies (Datalog±).* JWS / PODS, 2009–2012.
- **[SOTA]** M. Bienvenu, C. Lutz, F. Wolter. *First-Order Rewritability of Atomic Queries in Horn Description Logics.* IJCAI, 2013.
- **[Survey]** R. Kontchakov, M. Zakharyaschev. *An Introduction to Description Logics and Query Rewriting (OBDA).* Reasoning Web, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
