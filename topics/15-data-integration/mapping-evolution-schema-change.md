---
id: 15-data-integration/mapping-evolution-schema-change
title: "Mapping Evolution Under Schema Change"
topic: 15-data-integration
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Mapping Evolution Under Schema Change

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/mapping-evolution-schema-change` · **Status:** partially-solved

## 1. Problem Statement

A schema mapping $\mathcal{M}: \mathbf{S} \to \mathbf{T}$ (a finite set of GLAV/TGD constraints) is deployed in an integration pipeline. The source schema then evolves $\mathbf{S} \xrightarrow{\mathcal{F}} \mathbf{S}'$ or the target evolves $\mathbf{T} \xrightarrow{\mathcal{G}} \mathbf{T}'$, where $\mathcal{F}, \mathcal{G}$ are themselves mappings describing the schema change (add/drop/rename attribute, split/merge relation, normalize/denormalize, change keys). The problem is to **automatically derive an adapted mapping** $\mathcal{M}'$ that re-establishes the integration over the evolved schemas, ideally as a **composition** $\mathcal{M}' = \mathcal{F}^{-1} \circ \mathcal{M}$ or $\mathcal{M} \circ \mathcal{G}$, with a **minimal-change** guarantee: $\mathcal{M}'$ should differ from $\mathcal{M}$ no more than necessary and preserve the semantics of unchanged parts.

Variants: **decision** (does a mapping $\mathcal{M}'$ expressing the adaptation exist within a given mapping language?); **synthesis/optimization** (compute a minimal or "least-surprise" $\mathcal{M}'$); **incremental** (update $\mathcal{M}$ given a small edit $\delta$ to a schema rather than recomputing from scratch).

## 2. Mathematical Foundations

The semantic backbone is the **algebra of schema mappings**: **composition** $\mathcal{M}_{12} \circ \mathcal{M}_{23}$ and **inverse** operators (Fagin–Kolaitis–Popa–Tan). A mapping is a binary relation on instances $[\![\mathcal{M}]\!] \subseteq \mathrm{Inst}(\mathbf{S}) \times \mathrm{Inst}(\mathbf{T})$; composition is relational composition $[\![\mathcal{M}_1]\!] \circ [\![\mathcal{M}_2]\!]$. The fundamental result: **st-TGDs are not closed under composition** — composition may require **second-order TGDs (SO-tgds)**, which *are* closed and form the right semantic universe (FKPT, ACM TODS 2005).

Inverses are subtle: exact inverses rarely exist, so weaker notions — **quasi-inverse**, **maximum recovery** (Arenas–Pérez–Riveros) and **chase-inverse** — formalize "best partial undo." Schema evolution $\mathcal{F}$ is modeled as a mapping; adaptation is $\mathcal{M}' = \mathcal{F}^{-1} \circ \mathcal{M}$ using *maximum recovery* when $\mathcal{F}$ is non-invertible. Minimality is captured via **information-preservation** orders and homomorphism-based equivalence ($\equiv$, logical equivalence; $\equiv_{CQ}$, data-exchange equivalence; $\equiv_{DE}$).

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Fagin–Kolaitis–Popa–Tan's composition (SO-tgds) and the **maximum recovery** theory (Arenas, Pérez, Riveros, PODS 2008; TODS 2009) are the formal core. Bernstein–Melnik's **model management** ("Mapping operators and the rondo/Moda framework") gives the operator algebra (Match, Compose, Merge, Diff, Invert).
- **Systems-SOTA.** **PRISM/PRISM++** (Curino, Moon, Zaniolo, VLDB 2008/2013) automate relational schema evolution with SMO/ICMO operators and rewrite queries across versions. **Clio**/**++Spicy** regenerate mappings from updated correspondences; **MeMo** and **DB-MAIN** address conceptual-schema evolution.

## 4. Upper Bound

Composition of two SO-tgd mappings is computable and yields an SO-tgd whose size can be **exponential** in the inputs; evaluating certain answers under SO-tgds is in **PTime data complexity** (chase the source through the SO-tgd). Maximum recovery of an st-TGD mapping exists iff the mapping satisfies the "subset/unique-solutions" condition and is computable; deciding existence is in **coNP/PTime** depending on the language. PRISM-style rewriting of a CQ across a chain of SMO operators is polynomial in the number of operators for invertible operators. Model: data complexity in PTime; combined complexity up to ExpTime for SO-tgd manipulation.

## 5. Lower Bound

Deciding whether the composition of two st-TGD mappings is **expressible by st-TGDs** (i.e., avoids genuine second-order quantification) is **undecidable** (FKPT). Deciding **logical equivalence** of two SO-tgd mappings is **undecidable**; even for st-TGDs, equivalence is **coNEXPTIME**-hard / undecidable in general, and CQ-equivalence is decidable but **$\Pi_2^p$**-class. Existence of an **exact inverse** is undecidable for general mappings; existence of a quasi-inverse/maximum recovery is decidable but with high combined complexity. Model: many-one reductions, recursion-theoretic undecidability.

## 6. The Gap

The **operator algebra is semantically complete** (SO-tgds + maximum recovery cover composition and best-effort inversion), so the foundational layer is *partially solved*. The open gap is **minimal-change synthesis**: there is no agreed objective function nor algorithm that, given $\mathcal{M}$ and a concrete schema edit, returns a provably *minimal* and *human-intelligible* $\mathcal{M}'$ — minimality competes with intelligibility, and the relevant equivalence ($\equiv$ vs $\equiv_{CQ}$ vs $\equiv_{DE}$) is itself a design choice. Closing it needs (a) a robust minimality metric with tractable optimization, and (b) incremental algorithms whose cost scales with the edit size $|\delta|$, not $|\mathcal{M}|$.

## 7. Current Research (as of June 2026)

Active directions: **incremental/differential mapping maintenance** scaling with edit distance; learning schema-change operators from version histories. *(frontier — verify)* **LLM-assisted mapping adaptation** that proposes $\mathcal{M}'$ from natural-language change descriptions, validated against composition/maximum-recovery semantics as an oracle. *(frontier — verify)* Evolution of mappings over **knowledge graphs and lakehouse catalogs** (Iceberg/Delta schema evolution) with provenance-tracked column lineage. Groups: Kolaitis (UCSC), Arenas (PUC Chile), Pichler/Sallinger (TU Wien/Oxford), Bernstein (Microsoft Research legacy), Zaniolo/Curino lineage.

## 8. Future Work

- A canonical, tractable **minimality metric** for adapted mappings with synthesis algorithms.
- Truly **incremental** adaptation with $O(\mathrm{poly}(|\delta|))$ cost.
- Round-trip guarantees: adapt-then-revert recovers the original up to maximum recovery.
- Integrating evolution with **EGDs/keys** changes (key restructuring) without losing decidability.

## 9. Key References

- **[Foundational]** R. Fagin, P. Kolaitis, L. Popa, W.-C. Tan. *Composing schema mappings: Second-order dependencies to the rescue.* ACM TODS, 2005. — [DOI](https://doi.org/10.1145/1114244.1114249)
- **[Foundational]** M. Arenas, J. Pérez, C. Riveros. *The recovery of a schema mapping: Bringing exchanged data back.* ACM TODS, 2009. — [DOI](https://doi.org/10.1145/1620585.1620589)
- **[SOTA]** C. Curino, H. J. Moon, C. Zaniolo. *Graceful database schema evolution: The PRISM workbench.* VLDB, 2008. — [DOI](https://doi.org/10.14778/1453856.1453939)
- **[SOTA]** C. Curino, H. J. Moon, A. Deutsch, C. Zaniolo. *Automating the database schema evolution process (PRISM++).* VLDB Journal, 2013. — [DOI](https://doi.org/10.1007/s00778-012-0302-x)
- **[Foundational]** P. Bernstein, S. Melnik. *Model management 2.0: Manipulating richer mappings.* SIGMOD, 2007. — [DOI](https://doi.org/10.1145/1247480.1247482)
- **[Survey]** B. ten Cate, P. Kolaitis, W.-C. Tan. *Schema mappings and data examples.* (Tutorial), EDBT/ICDT, 2013. — [DOI](https://doi.org/10.1145/2452376.2452479)

## 10. Worked Example

A deployed mapping $\mathcal{M}: \mathsf{Emp}(\text{id}, \text{name}, \text{dept}) \rightarrow \mathsf{T}(\text{id}, \text{name}, \text{dept})$. The source is then **normalized** (split): $\mathsf{Emp}$ is replaced by $\mathsf{Person}(\text{id}, \text{name})$ and $\mathsf{Works}(\text{id}, \text{dept})$. The schema change $\mathcal{F}$ is itself a mapping:
$$\mathsf{Emp}(i,n,d) \;\leftrightarrow\; \mathsf{Person}(i,n) \wedge \mathsf{Works}(i,d).$$
To re-establish the integration we want $\mathcal{M}' = \mathcal{F}^{-1} \circ \mathcal{M}$. Composing the inverse of the split (a join) with $\mathcal{M}$ yields the adapted st-tgd
$$\mathsf{Person}(i,n) \wedge \mathsf{Works}(i,d) \rightarrow \mathsf{T}(i,n,d).$$

Trace on data: $\mathsf{Person}(7, \text{Bo})$, $\mathsf{Works}(7, \text{HR})$ chase to $\mathsf{T}(7, \text{Bo}, \text{HR})$ — identical to what old $\mathcal{M}$ produced from $\mathsf{Emp}(7, \text{Bo}, \text{HR})$, so semantics on unchanged data is preserved. Note: if $\mathsf{Works}$ allowed an employee with no dept row, the join drops that person — $\mathcal{F}$ is only a *maximum recovery*, not an exact inverse, exactly the subtlety section 2 flags. Here the composition stays a plain st-tgd, but in general it would require an SO-tgd.

---
*Part of the [DBMS Research catalog](../../README.md).*
