# Schema-Mapping Inversion Semantics

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/schema-mapping-inversion` · **Status:** partially-solved

## 1. Problem Statement

Given a schema mapping $M$ from source $\mathbf{S}$ to target $\mathbf{T}$ (a GLAV / s-t TGD specification), an **inverse** $M^{-1}$ from $\mathbf{T}$ back to $\mathbf{S}$ should "undo" $M$, recovering the source data from the materialized target. Because mappings lose information (project columns, introduce nulls, merge tuples), an *exact* inverse rarely exists, so the central problem is: **define a unified, computable notion of inverse that always exists, is expressible in a manageable language, and comes with provable information-recovery (loss) guarantees.**

Decision variants: (i) does an inverse of a given flavor **exist**? (ii) is a candidate $M'$ a valid inverse? Optimization variant: find the **most informative** recoverable inverse (minimize information loss). The difficulty is that several competing definitions exist — *exact inverse*, *quasi-inverse*, *maximum recovery* — and reconciling them into one coherent, computable theory is the open part.

## 2. Mathematical Foundations

Fagin (PODS 2006) defined the first rigorous notion: $M^{-1}$ is an **exact inverse** if $M \circ M^{-1} = \mathsf{Id}_{\mathbf{S}}$ (identity mapping on source instances), where $\mathsf{Id}$ relates each $I$ to itself. Exact inverses are rare, so:

- **Quasi-inverse** (Fagin–Kolaitis–Popa–Tan, 2007): relaxes equality up to *data-exchange equivalence*, identifying instances that map to the same target solutions.
- **Maximum recovery** (Arenas–Pérez–Riveros, PODS 2008): a mapping $M'$ from $\mathbf{T}$ to $\mathbf{S}$ that recovers **as much sound information as possible**; defined via *recovery* — $M'$ is a recovery if $(I,I) \in M \circ M'$ for every $I$ — and *maximum* if it is the most informative such. A maximum recovery **always exists** for GLAV mappings, giving the most "unified" notion.

Information-loss is quantified via the **space of solutions**: for target $J$, the recoverable source content is $\bigcap\{$source instances consistent with $J$ under $M\}$ — connecting to *certain answers* and the **homomorphism lattice** of solutions.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Fagin (exact inverse, 2006); FKPT (quasi-inverse, TODS 2008); Arenas–Pérez–Riveros (**maximum recovery**, the most general — PODS 2008, TODS 2009). Arenas–Pérez–Reutter unified these under a **language for inverse mappings** using disjunctive TGDs with inequalities/constants. Computing maximum recoveries is the practical SOTA target.
- **Systems-SOTA.** Mapping-design tools (**Clio**, **++Spicy**) and model-management prototypes incorporate (quasi-)inverse computation for round-tripping and schema-evolution support; production ELT lineage tools approximate inversion via column-level lineage rather than formal inverses.

## 4. Upper Bound

For GLAV mappings, a **maximum recovery always exists and is computable**; it is expressible in an extension of GLAV with **disjunction, equalities, and constants** (CQ$^{=}$ / disjunctive TGDs). Checking whether $M'$ is a recovery, and computing a maximum recovery, are **decidable**, with the recovery itself of size polynomial-to-exponential in $M$. Query answering through the inverse reduces to **certain-answer** computation, hence **PTime data complexity** for the resulting recovered queries.

## 5. Lower Bound

**Existence is restrictive for stronger notions:** deciding whether a GLAV mapping has an **exact inverse** is **coNP-hard / undecidable** depending on the language; many natural mappings (with projections or existentials) provably have **no exact and no quasi-inverse**, only a maximum recovery — an *information-theoretic* impossibility (lost columns cannot be reconstructed). Verifying that a candidate is a **maximum** recovery and minimizing the inverse's size are computationally hard (at least coNP-hard); the target language strictly **exceeds GLAV**, a syntactic lower bound mirroring the SO-tgd result for composition.

## 6. The Gap

**Partially solved.** Maximum recovery resolves *existence* (it always exists) and gives the unifying notion. The remaining gaps: (1) **canonical, minimal** representations — maximum recoveries are not unique and current constructions can be large/unwieldy; (2) a clean, **quantitative information-loss measure** (how much was recovered, in bits or via an entropy/lattice metric) that practitioners can act on; (3) inversion under **target constraints and SO tgds**, where theory thins out. Bridging the formal recovery theory and **lineage-based** approximations used in systems is open.

## 7. Current Research (as of June 2026)

Active directions: **inverses for richer mappings** (existential rules, nested/RDF, SO tgds) and **quantitative information-loss semantics**. *(frontier — verify)* Recent work connects inversion to **provenance semirings** and to **bidirectional transformations / lenses** (the PL community's *well-behaved lens* laws are a cousin of mapping invertibility). *(frontier — verify)* The Chile group (Arenas, Barceló, Reutter) and collaborators continue structural work; interest is rising in **invertibility for data-versioning and reproducibility** in ML pipelines.

## 8. Future Work

- Minimal/canonical maximum-recovery normal forms and tight size bounds.
- A practical **information-loss metric** linking recovery to certain answers and entropy.
- Inversion theory under target EGDs/TGDs and under SO tgds.
- Unifying database mapping inversion with PL **bidirectional transformations (lenses)**.

## 9. Key References

- **[Foundational]** R. Fagin. *Inverting Schema Mappings.* PODS 2006 / TODS, 2007. — [DOI](https://doi.org/10.1145/1292609.1292615)
- **[Foundational]** R. Fagin, P. Kolaitis, L. Popa, W.-C. Tan. *Quasi-Inverses of Schema Mappings.* PODS 2007 / TODS, 2008. — [DBLP](https://dblp.org/rec/journals/tods/FaginKPT08.html)
- **[SOTA]** M. Arenas, J. Pérez, C. Riveros. *The Recovery of a Schema Mapping: Bringing Exchanged Data Back.* PODS 2008 / TODS, 2009. (Maximum recovery.) — [PDF](https://www.cs.ox.ac.uk/people/cristian.riveros/papers/tods09.pdf)
- **[SOTA]** M. Arenas, J. Pérez, J. Reutter. *Inverting Schema Mappings: Bridging the Gap between Theory and Practice.* VLDB, 2009. — [PDF](http://marceloarenas.cl/publications/vldb09.pdf)
- **[Survey]** P. Barceló. *Logical Foundations of Relational Data Exchange.* SIGMOD Record, 2009. — [DBLP](https://dblp.uni-trier.de/db/journals/sigmod/sigmod38.html)
- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data exchange: semantics and query answering.* TCS, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)

## 10. Worked Example

Source $\mathrm{Emp}(\mathit{name}, \mathit{dept})$; mapping $M$ projects away the department:
$$\mathrm{Emp}(n,d) \to \mathrm{Person}(n).$$
On $I = \{\mathrm{Emp}(\text{Ann},\text{HR}),\ \mathrm{Emp}(\text{Bob},\text{IT})\}$ the target is $J = \{\mathrm{Person}(\text{Ann}),\ \mathrm{Person}(\text{Bob})\}$.

**No exact inverse exists:** $J$ alone cannot tell whether Ann was in HR or IT — the column $d$ is information-theoretically lost, so $M \circ M^{-1} \neq \mathsf{Id}_{\mathbf{S}}$ for any $M^{-1}$.

**Maximum recovery** $M'$ recovers all *sound* facts — exactly that each person was an employee in *some* department:
$$\mathrm{Person}(n) \to \exists d\, \mathrm{Emp}(n,d).$$
Check the recovery condition $(I,I)\in M\circ M'$: chasing $I$ through $M$ then $M'$ yields $\{\mathrm{Emp}(\text{Ann}, N_1), \mathrm{Emp}(\text{Bob}, N_2)\}$, which homomorphically maps back into $I$ (nulls $N_i \mapsto$ real depts). It is *maximum* because no GLAV inverse can pin down $d$ — recovering the existential is the most informative sound conclusion.

---
*Part of the [DBMS Research catalog](../../README.md).*
