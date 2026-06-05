# Two-Variable and Guarded Logic Query Power

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/guarded-logic-expressiveness` · **Status:** partially-solved

## 1. Problem Statement
Map the expressiveness/complexity tradeoffs of decidable **fragments of first-order logic** used as query and constraint languages: the **two-variable fragment** $\mathrm{FO}^2$ (and $\mathrm{C}^2$ with counting), the **guarded fragment (GF)** and its **guarded negation** (GNFO), **frontier-guarded** rules, and the **unary-negation fragment (UNFO)**. For each fragment $\mathcal{F}$ determine:

- **Expressive power:** what queries/constraints $\mathcal{F}$ can and cannot define (relative to FO, CQ, UCQ, RPQ, MSO).
- **Static analysis:** decidability and complexity of **satisfiability**, **finite satisfiability**, **containment**, and **query answering under constraints** (open-world certain answers).
- **Combined/data complexity** of evaluation.

The aim is a unified picture of *why* these fragments are decidable (the **tree-model / bounded-tree-width** property) and where the practically useful sweet spots lie for description logics, ontology-based access, and graph querying. **Partially-solved**: the major fragments are characterized, but the interaction of guardedness with **counting, transitivity, and CQ answering** has open cells.

## 2. Mathematical Foundations
Decidability of these fragments rests on **tree-like model** properties. **GF** (Andréka–van Benthem–Németi 1998) restricts quantification to $\exists \bar y\,(\alpha(\bar x,\bar y) \wedge \varphi)$ where $\alpha$ is an atom **guarding** all free variables; models can be taken of **bounded tree-width**, enabling **tree-automata** decision procedures. GF generalizes modal/description logics; its **bisimulation-invariance** characterization (Grädel–Hirsch–Otto) states GF = the guarded-bisimulation-invariant fragment of FO.

$\mathrm{FO}^2$ has the **finite-model property** (Mortimer); $\mathrm{C}^2$ (two variables + counting) is decidable (Grädel–Otto–Rosen; Pratt-Hartmann for the complexity), but lacks the finite-model property, requiring separate finite-satisfiability analysis. **GNFO/UNFO** (Bárány–ten Cate–Segoufin) restrict negation rather than quantification, regain CQ-friendliness, and enjoy **Craig interpolation** and decidable containment — making them especially suited to **query answering**. **Frontier-guarded TGDs** (Baget–Leclère–Mugnier–Salvat) give decidable CQ entailment via the **guarded chase** of bounded tree-width.

## 3. State of the Art (SOTA)
- **GF:** satisfiability **2EXPTIME-complete** (EXPTIME for bounded arity) — Grädel 1999.
- **$\mathrm{FO}^2$:** satisfiability **NEXPTIME-complete** (Grädel–Kolaitis–Vardi); **$\mathrm{C}^2$** also **NEXPTIME-complete** (Pratt-Hartmann 2005), finite satisfiability likewise.
- **GNFO / UNFO:** satisfiability **2EXPTIME-complete**, decidable **containment**, and decidable **CQ answering / FO-rewritability** results (Bárány–ten Cate–Segoufin 2015; ten Cate–Segoufin).
- **Frontier-guarded Datalog$^\pm$:** CQ answering decidable, **2EXPTIME** combined / tractable data complexity (Baget et al.; Gottlob–Pieris).
- These underpin **DL-Lite/$\mathcal{EL}$/$\mathcal{ALC}$** reasoning and OBDA engines.

## 4. Upper Bound
- GF / GNFO / UNFO satisfiability and CQ answering: **2EXPTIME** (combined), via bounded-tree-width models and tree automata; EXPTIME for bounded arity.
- **Data complexity** of CQ answering under guarded/frontier-guarded rules: **PTIME-complete**; for many DLs **AC$^0$/FO-rewritable** (DL-Lite) or PTIME.
- $\mathrm{C}^2$ satisfiability: **NEXPTIME**; with binary-coded numbers still NEXPTIME (Pratt-Hartmann).

## 5. Lower Bound
- GF / GNFO satisfiability is **2EXPTIME-hard** (alternating tree automata / tiling reductions); EXPTIME-hard at bounded arity.
- $\mathrm{FO}^2$ and $\mathrm{C}^2$ are **NEXPTIME-hard**.
- Adding **transitivity** or three variables breaks decidability: **$\mathrm{FO}^3$** and **GF + transitive guards (unrestricted)** are **undecidable**; $\mathrm{FO}^2$ with two transitive relations is undecidable.
- Data-complexity **PTIME-hardness** for CQ answering under guarded rules (beyond FO-rewritable DLs).

## 6. The Gap
The "pure" satisfiability/expressiveness cells are largely **closed** with tight bounds. The open frontier is at the **interactions**: guardedness **plus counting** (guarded $\mathrm{C}^2$ / counting in GNFO) for CQ answering; **transitivity / functionality** combined with guards; precise containment/Beth-definability for **frontier-guarded** classes; and the exact boundary of **FO-rewritability** for expressive DLs and existential-rule fragments. Tight combined complexity for CQ answering under several rich fragments, and finite-model reasoning with counting, remain only partially resolved.

## 7. Current Research (as of June 2026)
Active themes: **GNFO/UNFO** as a unifying decidable host for OBDA, interpolation-based **rewriting**, and **separability**; guarded logics with **counting and arithmetic**; **finite-model** and **finite-controllability** results for existential rules; and connections to **graph querying** (guarded fragments capturing navigational cores). *(frontier — verify)* Recent work extends GNFO with **transitive relations** and **counting** while preserving decidability of CQ answering, and refines the **chase-termination / bounded-tree-width** toolbox. People/groups: Otto, Grädel, ten Cate, Segoufin, Bárány, Pratt-Hartmann, Benedikt, Bourhis, Pieris, Mugnier, Lutz, Bienvenu.

## 8. Future Work
- Decidability/complexity of CQ answering for **guarded + counting + transitivity** combinations.
- Sharp **FO-rewritability** boundaries and interpolation-based rewriting for GNFO/UNFO.
- Finite-model reasoning and certain answers under existential rules with counting.
- Practical reasoners exploiting bounded-tree-width models for OBDA and graph-constraint checking.

## 9. Key References
- **[Foundational]** H. Andréka, J. van Benthem, I. Németi. *Modal languages and bounded fragments of predicate logic.* J. Philosophical Logic, 1998.
- **[Foundational]** E. Grädel. *On the restraining power of guards.* J. Symbolic Logic, 1999.
- **[Foundational]** I. Pratt-Hartmann. *Complexity of the two-variable fragment with counting quantifiers.* J. Logic, Language and Information, 2005.
- **[SOTA]** V. Bárány, B. ten Cate, L. Segoufin. *Guarded negation.* JACM, 2015.
- **[SOTA]** J.-F. Baget, M. Leclère, M.-L. Mugnier, E. Salvat. *On rules with existential variables: Walking the decidability line.* Artificial Intelligence, 2011.
- **[Survey]** M. Bienvenu, M. Ortiz. *Ontology-mediated query answering with data-tractable description logics.* Reasoning Web, 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
