---
id: 15-data-integration/schema-mapping-composition-closure
title: "Schema-Mapping Composition Closure"
topic: 15-data-integration
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Schema-Mapping Composition Closure

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/schema-mapping-composition-closure` · **Status:** partially-solved

## 1. Problem Statement

A schema mapping $M_{12}$ from schema $\mathbf{S}_1$ to $\mathbf{S}_2$ and a mapping $M_{23}$ from $\mathbf{S}_2$ to $\mathbf{S}_3$ can be **composed** into a single mapping $M_{13} = M_{12} \circ M_{23}$ whose semantics is the relational composition of the two binary "satisfaction" relations:
$$M_{12} \circ M_{23} = \{ (I, K) \mid \exists J,\; (I,J) \in M_{12} \text{ and } (J,K) \in M_{23} \}.$$
Composition is essential for **metadata management** (reusing/chaining mappings during schema evolution and ETL pipeline maintenance).

The problem: given $M_{12}, M_{23}$ expressed in **GLAV** (global-and-local-as-view, i.e., source-to-target TGDs), (1) is $M_{13}$ **expressible** in a usable mapping language, and in which one? (2) what is the **size blow-up** of the resulting specification? Variants: characterizing the **exact expressive class** needed (decision), and **minimizing** the composed mapping's size (optimization).

## 2. Mathematical Foundations

A **GLAV / s-t TGD** has the form $\phi_{\mathbf{S}}(\bar x) \to \exists \bar y\, \psi_{\mathbf{T}}(\bar x, \bar y)$. The class of GLAV mappings is **not closed under composition**: Fagin, Kolaitis, Popa, Tan (PODS 2004) proved that composing s-t TGDs may require **second-order TGDs (SO tgds)** — dependencies with existentially quantified **function symbols**:
$$\exists f\, \forall \bar x\, \big( \phi(\bar x) \to \psi(\bar x, f(\bar x)) \big).$$
Their central theorem: **SO tgds are exactly the closure of s-t TGDs under composition** — every composition of finitely many GLAV mappings is an SO tgd, and every SO tgd arises this way. SO tgds are also exactly the mappings with a **polynomial-time-computable chase** and admit universal solutions. **Nested GLAV / plain SO tgds** (without nested terms) form an intermediate class capturing some but not all SO-tgd compositions.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Fagin–Kolaitis–Popa–Tan (PODS 2004, TODS 2005) settled the foundational closure question (SO tgds). Nash–Bernstein–Melnik and Bernstein–Green–Melnik–Nash studied composition algorithms in the **model-management** algebra. Arenas–Pérez–Riveros characterized which SO tgds are equivalent to *plain* SO tgds / nested GLAV. Feinerer–Pichler–Sallinger–Savenkov studied **size and complexity** of composition.
- **Systems-SOTA.** Microsoft's **model-management** prototypes (Bernstein et al.) and **Rondo**; **Clio/+** (IBM) mapping tools; **++Spicy/LLunatic** mapping systems support compositional reasoning over s-t TGDs.

## 4. Upper Bound

GLAV $\circ$ GLAV is **always expressible as an SO tgd**, computable in time polynomial in the combined input size *per composition step*. Certain-answer / query answering against the composed SO tgd is in **PTime data complexity** (the SO-tgd chase is PTime in the data). For a chain of $k$ GLAV mappings, an SO tgd of size **polynomial in each step** suffices, but iterated composition can produce **nested function terms** whose depth grows with $k$.

## 5. Lower Bound

Composition is **provably not expressible in (finite unions of) s-t TGDs** nor in first-order logic in general (FKPT lower bound — the canonical $\mathsf{Emp}$/transitive-closure-style examples require function symbols). Deciding whether a given SO tgd is **equivalent to a (first-order) GLAV mapping** is **undecidable** in general. The **size blow-up** can be **super-polynomial / exponential** across a chain when one insists on staying within plain SO tgds or nested GLAV; minimizing SO-tgd size is at least **NP-hard**.

## 6. The Gap

**Partially solved.** The *expressibility* question is fully resolved: SO tgds are the exact closure. What remains open/partial: (1) **tight size bounds** — when does a length-$k$ composition force exponential blow-up, and can clever normal forms avoid it? (2) deciding membership in **usable sub-languages** (plain SO tgd, nested GLAV) is undecidable in general, so we lack a complete syntactic test for "stays simple"; (3) composition interacting with **target constraints (EGDs/TGDs on $\mathbf{T}$)** is far less understood and is the active frontier.

## 7. Current Research (as of June 2026)

Directions: **composition with target dependencies** and with **mappings beyond GLAV** (existential rules, nested/relational-to-nested). *(frontier — verify)* Recent ICDT/PODS 2025 work revisits **succinctness and normal forms for SO tgds** and links composition to **provenance semirings** so that composed mappings carry lineage. *(frontier — verify)* The Oxford/TU Wien (Pichler, Sallinger) and Chile (Arenas, Barceló) groups continue work on **structural characterizations** and on composition in **graph/RDF mappings**. Practical mapping-management in modern ELT (dbt-style) reignites interest in cheap, debuggable composed mappings.

## 8. Future Work

- Sharp upper/lower size bounds for iterated GLAV composition.
- Decidable, practically useful **sufficient conditions** for "composition stays in nested GLAV."
- Composition theory for **mappings with target constraints** and **schema-evolution operators** (merge, diff).
- Provenance- and cost-aware composition for ELT toolchains.

## 9. Key References

- **[Foundational]** R. Fagin, P. Kolaitis, L. Popa, W.-C. Tan. *Composing Schema Mappings: Second-Order Dependencies to the Rescue.* PODS 2004 / TODS, 2005. — [DOI](https://doi.org/10.1145/1114244.1114249)
- **[Foundational]** A. Nash, P. Bernstein, S. Melnik. *Composition of mappings given by embedded dependencies.* PODS 2005 / TODS, 2007. — [DOI](https://doi.org/10.1145/1206049.1206053)
- **[SOTA]** M. Arenas, J. Pérez, J. Reutter, C. Riveros. *Foundations of Schema Mapping Management.* PODS, 2010. — [DBLP](https://dblp.org/rec/conf/pods/ArenasPRR10.html)
- **[SOTA]** I. Feinerer, R. Pichler, E. Sallinger, V. Savenkov. *On the Undecidability of the Equivalence of Second-Order Tuple Generating Dependencies.* Information Systems, 2015. — [DOI](https://doi.org/10.1016/j.is.2014.09.003)
- **[Survey]** P. A. Bernstein, S. Melnik. *Model Management 2.0: Manipulating Richer Mappings.* SIGMOD, 2007. — [DOI](https://doi.org/10.1145/1247480.1247482)
- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data exchange: semantics and query answering.* TCS, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)

## 10. Worked Example

Let $\mathbf{S}_1$ have $\mathrm{Emp}(e)$, $\mathbf{S}_2$ have $\mathrm{Mgr}(e,m)$, $\mathbf{S}_3$ have $\mathrm{Self}(m)$.

- $M_{12}$: $\;\mathrm{Emp}(e) \to \exists m\, \mathrm{Mgr}(e,m)\;$ (every employee gets some manager).
- $M_{23}$: $\;\mathrm{Mgr}(e,m) \to \mathrm{Self}(m)\;$ (managers appear in $\mathrm{Self}$).

Composing, the existential $m$ from step 1 must flow into step 3. No s-t TGD over $\{\mathrm{Emp}\}\to\{\mathrm{Self}\}$ captures this without naming the witness, but an **SO tgd** does:
$$\exists f\, \forall e\, \big( \mathrm{Emp}(e) \to \mathrm{Self}(f(e)) \big).$$
Here $f$ is the Skolem function "manager-of." On instance $I = \{\mathrm{Emp}(a)\}$: chase $M_{12}$ gives $\mathrm{Mgr}(a, N_1)$ (null $N_1$); chase $M_{23}$ gives $\mathrm{Self}(N_1)$. The SO tgd produces $\mathrm{Self}(f(a))$ — same up to renaming $f(a)\mapsto N_1$. This is the canonical witness that GLAV is *not* closed under composition: the function symbol $f$ is irremovable.

---
*Part of the [DBMS Research catalog](../../README.md).*
