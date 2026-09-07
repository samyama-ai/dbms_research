---
id: 22-provenance-lineage/where-provenance-characterization
title: "Where-Provenance Formal Characterization"
topic: 22-provenance-lineage
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Where-Provenance Formal Characterization

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/where-provenance-characterization` · **Status:** open

## 1. Problem Statement

*Where-provenance* answers, for a value appearing in a query output, the question "from which input cell(s) was this value **copied**?" Unlike *why*-provenance (which input tuples *witness* an output) or *how*-provenance (the semiring polynomial), where-provenance tracks the literal physical origin of a datum. The open problem is to give a **query-rewrite-stable, invariant** definition: a formal characterization of where-provenance that is preserved under semantically equivalent query reformulations, together with a **decidable equivalence** test ("do two queries induce the same where-provenance on all databases?").

Variants:
- **Definitional:** axiomatize where-provenance so it is independent of syntactic query form.
- **Decision:** given $Q_1 \equiv Q_2$ (equivalent answers), decide whether they carry identical where-provenance annotations.
- **Optimization:** find a canonical (minimal-rewrite-invariant) provenance witness when multiple copy paths exist.

## 2. Mathematical Foundations

Following Buneman, Khanna, and Tan, where-provenance is modeled over a data model with *locations*: each cell carries an identity $\ell \in L$. A query $Q$ induces a partial map $\omega_Q : \text{out-locations} \to 2^{L}$. The central pathology is **non-invariance**: two equivalent queries can yield different $\omega$. For example $\sigma_{A=5}(R)$ and $\pi(\ldots)$ rewrites copy values from different cells, so $\omega$ is not a function of the input/output relation alone.

Where-provenance is the *coarsest* of the classical hierarchy and does **not** factor through the provenance semiring $\mathbb{N}[X]$ of Green–Karvounarakis–Tannen; it is sub-polynomial information. Formally, for monotone relational algebra (SPJU), how-provenance is the polynomial $p \in \mathbb{N}[X]$, why-provenance is its set of monomials' supports, and where-provenance is a strictly finer *copy relation* that is **not** recoverable from $p$.

A clean characterization seeks an equivalence $\equiv_{\omega}$ on queries with:
$$ Q_1 \equiv_\omega Q_2 \iff \forall D,\ \omega_{Q_1}(D) = \omega_{Q_2}(D). $$
Key tools: the **chase** for testing query equivalence under integrity constraints, homomorphism theorems for conjunctive queries (CQ equivalence is via homomorphism), and a notion of *location-preserving homomorphism* that refines the standard one.

## 3. State of the Art (SOTA)

- **Buneman, Khanna, Tan (ICDT 2001)** introduced where- and why-provenance for the deterministic/copy semantics and showed where-provenance is query-syntax dependent.
- **Green, Karvounarakis, Tannen (PODS 2007)** gave the semiring framework; where-provenance sits *below* it and is explicitly noted as not captured by commutative semirings.
- **Cheney, Chiticariu, Tan (FnTDB 2009 survey)** consolidated definitions and is the canonical reference distinguishing the three notions and their (non-)invariance.
- Systems: **DBNotes / Mondrian** (Tan et al.) propagate where-provenance as annotations through SQL; **Perm/GProM** (Glavic, Alawini) support where/why/how but with syntactic, not invariant, semantics.

No system computes a *canonical* invariant where-provenance; all are tied to a chosen query plan.

## 4. Upper Bound

For conjunctive queries, computing the syntactic where-provenance of a fixed query is in **PTIME** (linear in output size with an annotation pass). Deciding CQ *answer* equivalence is **NP-complete** (homomorphism). For the refined location-preserving equivalence $\equiv_\omega$ over CQs, the best-known upper bound is **$\Pi_2^p$** / NP-style search over location-homomorphisms — established only for restricted fragments. No completeness result is known for full SPJU.

## 5. Lower Bound

Where-provenance equivalence inherits **NP-hardness** from CQ-equivalence (3-colorability reduction via canonical databases). For queries with inequalities or union, equivalence climbs the polynomial hierarchy; under unions of CQs, equivalence is **$\Pi_2^p$-hard**. For full relational algebra with difference, query equivalence is **undecidable** (Trakhtenbrot/Di Paola), so invariant where-provenance equivalence is *undecidable* in that fragment — a hard impossibility ceiling.

## 6. The Gap

The gap is largely **definitional**, not just complexity-theoretic: there is no agreed invariant semantics, so "equivalence" is under-specified for the full language. For CQs the gap between the PTIME computation of syntactic provenance and the NP-to-$\Pi_2^p$ equivalence test is understood, but the *invariant* characterization remains open. Closing it requires (a) an axiomatic definition robust to rewrite, and (b) a decidability frontier mapping each algebra fragment to decidable/undecidable.

## 7. Current Research (as of June 2026)

Active threads: integrating where-provenance into **provenance for SQL with bag semantics and nulls** (Glavic's GProM group), and *categorical/lens-based* treatments where where-provenance arises from bidirectional transformations (Cheney, McKinna). There is renewed interest in where-provenance for **ML feature lineage** and **data debugging**, pushing for invariant semantics so explanations survive query optimization. *(frontier — verify)* Work on linking where-provenance to **provenance semirings with location-annotated generators** (a "located semiring") is being explored to unify the hierarchy.

## 8. Future Work

- An axiomatic, rewrite-stable definition and a proof it is the coarsest invariant refinement of why-provenance.
- A precise decidability map across RA fragments (CQ, UCQ, RA$^-$, full RA).
- Canonical-form algorithms producing a unique minimal copy-witness.
- Practical propagation that survives a cost-based optimizer's plan choice.

## 9. Key References

- **[Foundational]** Buneman, Khanna, Tan. *Why and Where: A Characterization of Data Provenance.* ICDT, 2001. — [DBLP](https://dblp.org/rec/conf/icdt/BunemanKT01.html)
- **[Foundational]** Green, Karvounarakis, Tannen. *Provenance Semirings.* PODS, 2007. — [DBLP](https://dblp.org/rec/conf/pods/GreenKT07.html)
- **[Survey]** Cheney, Chiticariu, Tan. *Provenance in Databases: Why, How, and Where.* Foundations and Trends in Databases, 2009. — [DOI](https://doi.org/10.1561/1900000006)
- **[SOTA]** Bhagwat, Chiticariu, Tan, Vijayvargiya. *An Annotation Management System for Relational Databases (DBNotes).* VLDB Journal, 2005. — [DOI](https://doi.org/10.1007/s00778-005-0156-6)
- **[SOTA]** Arab, Glavic, et al. *GProM: A Swiss Army Knife for Your Provenance Needs.* IEEE Data Eng. Bulletin, 2018. — [PDF](http://sites.computer.org/debull/A18mar/p51.pdf)

## 10. Worked Example

Let $R(A,B)$ have one tuple at locations $\ell_1,\ell_2$:

| | A | B |
|---|---|---|
| | $5_{\ell_1}$ | $7_{\ell_2}$ |

Consider two queries that return the same answer relation $\{(5)\}$ on every database where $A=5$:

- $Q_1 = \pi_A(\sigma_{A=5}(R))$ — the output value $5$ is **copied** from cell $\ell_1$, so $\omega_{Q_1} = \{\ell_1\}$.
- $Q_2 = \pi_A(\sigma_{A=5}(R)) \cup \{(5)\}$ where the constant $5$ is supplied by the query literal — that output value is copied from *no input cell*, so $\omega_{Q_2} = \varnothing$ (or a constant location).

Although $Q_1(D) = Q_2(D)$ as relations for all such $D$, their where-provenance differs: $\omega_{Q_1} \ne \omega_{Q_2}$. This is the **non-invariance** pathology — where-provenance is not a function of input/output relations alone. It also shows why $\omega$ cannot be recovered from the how-provenance polynomial (both queries have the same $\mathbb{N}[X]$ annotation $x_{\text{tuple}}$), placing where-provenance strictly below the semiring. An invariant characterization must quotient queries by a *location-preserving* equivalence so that rewrites preserving answers also preserve $\omega$.

---
*Part of the [DBMS Research catalog](../../README.md).*
