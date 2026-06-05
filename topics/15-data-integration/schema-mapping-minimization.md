# Schema Mapping Optimization and Minimality

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/schema-mapping-minimization` · **Status:** partially-solved

## 1. Problem Statement

A schema mapping is generated, learned, or composed — and is often **redundant**: it contains dependencies that are implied, mergeable, or unnecessarily large. The **mapping optimization / minimization problem** asks: given a GLAV mapping $M$, decide whether another mapping $M'$ is **equivalent** to it, and compute an **equivalent mapping of minimal size**, where size = number of dependencies, total atoms, or number of existential variables.

Crucially, *equivalence* is not unique — it depends on the **semantics of interest**:

- **Logical equivalence** ($M \equiv M'$): same set of solutions for every source instance.
- **Data-exchange equivalence** ($M \equiv_{\mathrm{DE}} M'$): same *universal solutions* (same materialized target up to homomorphic equivalence).
- **CQ-equivalence** ($M \equiv_{\mathrm{CQ}} M'$): same **certain answers** to all conjunctive queries.

Variants: **decision** (equivalence under semantics $X$), **optimization** (smallest equivalent $M'$), and **normalization** (canonical form). Logical $\Rightarrow$ DE $\Rightarrow$ CQ equivalence, and the implications are strict — so the *easier* the semantics, the *more* simplifications become legal and the smaller $M'$ can be.

## 2. Mathematical Foundations

GLAV mappings are sets of s-t TGDs. The semantic anchors:

- **CQ-equivalence collapses to query/dependency containment** via the chase: $M \equiv_{\mathrm{CQ}} M'$ iff each fires the same certain answers, checkable by **chasing one mapping's dependencies with the other** (a TGD-implication test).
- **Data-exchange equivalence** uses **universal solutions** (Fagin–Kolaitis–Miller–Popa) and the **core** of a universal solution (Fagin–Kolaitis–Popa, *Data Exchange: Getting to the Core*, TODS 2005) as the canonical target.
- Minimization of a single TGD's right-hand side is **CQ core computation**; minimization across TGDs is **redundant-TGD elimination** under implication.

Fagin–Kolaitis–Nash–Popa, *Towards a Theory of Schema-Mapping Optimization* (PODS 2008), is the defining framework: it formalizes the three equivalence notions, proves their separation, and gives **normalization** procedures (split, fold, reduce). The hardness of TGD implication (the engine of equivalence) drives the complexity.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** **Fagin, Kolaitis, Nash, Popa** (PODS 2008) — the foundational optimization/equivalence theory: decidability and complexity of the three equivalences and minimal-size results. **Pichler–Sallinger–Savenkov** and **Gottlob–Pichler–Savenkov** refined the complexity of TGD/EGD equivalence and core-based minimization. **Arenas–Pérez–Reutter–Riveros** studied mapping composition/inverse, whose outputs are exactly what needs minimizing.
- **Systems-SOTA.** **++Spicy/?Spicy** (Mecca–Papotti) computes *core* solutions and rewrites mappings to generate them efficiently — a practical minimization for data exchange. **Clio** rewrites/normalizes nested mappings. **Llunatic** uses core computation in cleaning.

## 4. Upper Bound

- **CQ-equivalence and DE-equivalence of s-t GLAV mappings are decidable**; the decision problems sit in **NP / $\Pi_2^p$ / coNEXPTIME** ranges depending on the precise notion and whether nesting/EGDs are allowed (Fagin–Kolaitis–Nash–Popa; Pichler et al.). Single-TGD core minimization (RHS) is in **NP** (guess the smaller core, verify by homomorphism). Computing the **core** universal solution is in **PTime in data** for fixed weakly-acyclic mappings (Gottlob–Nash; Fagin–Kolaitis–Popa), so DE-optimal target generation is tractable in data complexity. Models: RAM / standard combined-complexity.

## 5. Lower Bound

- **TGD implication is undecidable in general** (folklore from Beeri–Vardi), so **logical equivalence of unrestricted (target-TGD) mappings is undecidable**. For **s-t** (source-to-target only) GLAV the equivalences become decidable but **NP-hard / $\Pi_2^p$-hard** (CQ-containment / core hardness, Chandra–Merlin reductions).
- **Core computation hardness:** finding the core of an instance is **DP-hard / NP-hard in combined complexity** (Fagin–Kolaitis–Popa); minimizing a mapping to one generating cores inherits this.
- Stated in **NP/$\Pi_2^p$/DP**-completeness (s-t case) and **$\Sigma^0_1$ undecidability** (with target TGDs) models.

## 6. The Gap

**Partially solved.** For **source-to-target GLAV** mappings the picture is largely complete: the three equivalences are decidable with known (NP/$\Pi_2^p$-range) complexity, and minimal-size results exist. The **open** parts: (i) once **target TGDs/EGDs** are admitted, logical equivalence is **undecidable** and only fragment-restricted islands are mapped; (ii) for **SO-tgds** (closure under composition) the minimization theory is **incomplete** — even deciding equivalence is delicate (Feinerer–Pichler–Sallinger–Savenkov showed SO-tgd equivalence is undecidable in general); (iii) tight bounds for **nested / relational** mappings and for *minimum number of existentials* are open. Closing it means charting the decidable fragments with target constraints and completing the SO-tgd story.

## 7. Current Research (as of June 2026)

Active: equivalence and minimization for **SO-tgds and plain SO-tgds** (Pichler, Sallinger, Savenkov), and **core-generating mapping rewriting** at scale. *(frontier — verify)* 2024–2025 work connects mapping minimization to **GLAV fitting/learning** — produce the *smallest* mapping consistent with examples (ten Cate, Funk, Jung, Lutz on fitting and *separability*), an Occam-style objective. *(frontier — verify)* There is renewed interest in **minimal mappings for KG/ontology** integration and in **provenance-preserving** minimization (does the smaller mapping keep why-provenance?). Groups: Kolaitis, ten Cate, Pichler/Sallinger, Mecca/Papotti.

## 8. Future Work

- Complete the decidability/complexity map for mappings **with target constraints**.
- Finish the **SO-tgd** minimization theory (identify decidable, optimizable fragments).
- Minimize under additional invariants: **provenance**, **incremental maintenance** cost, **privacy**.
- Practical, certified minimizers that integrate with composition/inversion pipelines.

## 9. Key References

- **[Foundational]** R. Fagin, P. Kolaitis, L. Popa. *Data Exchange: Getting to the Core.* ACM TODS, 2005.
- **[Foundational]** R. Fagin, P. Kolaitis, A. Nash, L. Popa. *Towards a Theory of Schema-Mapping Optimization.* PODS, 2008.
- **[SOTA]** G. Gottlob, R. Pichler, V. Savenkov. *Normalization and Optimization of Schema Mappings.* PVLDB / VLDB Journal, 2009–2011.
- **[SOTA]** I. Feinerer, R. Pichler, E. Sallinger, V. Savenkov. *On the Undecidability of the Equivalence of Second-Order Tuple Generating Dependencies.* AMW / Information Systems, 2015.
- **[SOTA]** G. Mecca, P. Papotti, S. Raunich. *Core Schema Mappings.* SIGMOD, 2009.
- **[Survey]** M. Arenas, P. Barceló, L. Libkin, F. Murlak. *Foundations of Data Exchange.* Cambridge University Press, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
