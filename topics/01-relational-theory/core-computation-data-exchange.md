---
id: 01-relational-theory/core-computation-data-exchange
title: "Core Computation for Data Exchange"
topic: 01-relational-theory
status: solved-but-impractical
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Core Computation for Data Exchange

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/core-computation-data-exchange` · **Status:** solved-but-impractical

## 1. Problem Statement

In **data exchange**, a source instance $I$ is translated to a target instance $J$ via a schema mapping $\mathcal{M}=(\mathbf{S},\mathbf{T},\Sigma_{st},\Sigma_t)$, where $\Sigma_{st}$ are source-to-target tgds and $\Sigma_t$ target tgds+egds. The **chase** produces a *universal solution* (a most-general target instance, with labeled nulls). Universal solutions are not unique; they differ by redundant nulls. The **core** is the unique (up to isomorphism) smallest universal solution — the canonical, redundancy-free materialization.

**Problem**: given $\mathcal{M}$ and $I$, compute the core of a universal solution **efficiently**. *Decision sub-problem*: core identification / "is $J$ the core?". *Optimization framing*: minimize target size while preserving certain answers to all unions of conjunctive queries (UCQs), since the core gives the same certain answers as any universal solution but is minimal.

## 2. Mathematical Foundations

A **core** of a structure $J$ is a minimal substructure $J'$ such that there is a homomorphism $J\to J'$; equivalently $J'$ is a retract with no proper endomorphism onto a smaller image. Core computation generalizes the classic **conjunctive-query minimization** (Chandra–Merlin): minimizing a CQ = computing the core of its canonical instance. Key facts:

- For *fixed* schema, the certain answers to a UCQ $Q$ equal $Q$ evaluated on **any** universal solution, then keeping null-free tuples: $\mathrm{certain}(Q,I)=Q(J)_{\downarrow}$.
- Computing/recognizing the core of an arbitrary graph is **NP-hard / DP-complete**, but in data exchange the universal solution already comes from a **terminating chase**, which constrains structure.
- **Theorem (Fagin–Kolaitis–Popa; Gottlob–Nash).** For mappings with st-tgds and target egds + **weakly acyclic** target tgds, the core can be computed in **polynomial time (data complexity)**.

## 3. State of the Art (SOTA)

- **Theory SOTA**: the **Gottlob–Nash** "FindCore"/blocks algorithm (and Fagin–Kolaitis–Popa greedy/blocks results) give PTIME core computation for st-tgds with weakly acyclic target tgds and egds — the definitive positive result.
- **Systems SOTA**: direct core algorithms are *impractical* — the polynomial has high degree and large constants (repeated endomorphism search). Practical exchange systems instead generate **core-or-near-core SQL** up front. **Clio / ++Spicy / Llunatic** (Mecca, Papotti, ten Cate, Kolaitis) rewrite mappings so a single SQL/script directly produces the core (or a small superset), avoiding post-hoc minimization. This is the only scalable route in practice.

## 4. Upper Bound

Core computation is in **PTIME (data complexity)** for st-tgds + weakly acyclic target tgds + egds (Gottlob–Nash). The dominant cost is repeated **homomorphism/endomorphism** checks; the best general bounds are high-degree polynomials in $|J|$, e.g., the blocks algorithm runs in time polynomial in the number of nulls but with exponents tied to mapping size. Mapping-driven SQL rewriting (++Spicy) runs in time comparable to evaluating the mapping itself, but only *approximates* the guarantee in general schemas.

## 5. Lower Bound

**Core identification** for general instances is **coNP-hard**, and recognizing cores of arbitrary graphs is **DP-complete** — so the PTIME result genuinely exploits the chase structure. In **combined complexity**, deciding properties of the core is intractable. With **non-weakly-acyclic** target tgds the chase may not terminate and core existence/computation becomes **undecidable**. Even when polynomial, the exponent depends on mapping arity, giving an effective lower bound on practical performance.

## 6. The Gap

Theoretically the problem is **solved** (PTIME for the standard class). The remaining gap is **practical**: the polynomial-time algorithms are too slow for large targets, and SQL-rewriting systems only *match* the core for restricted mappings. Closing the gap means either a low-degree, constant-friendly core algorithm or a proof that mapping-driven rewriting computes exact cores for a precisely characterized, broad mapping class.

## 7. Current Research (as of June 2026)

Groups: **Kolaitis (UCSC)**, **ten Cate (ILLC Amsterdam)**, **Mecca / Papotti (Basilicata / EURECOM)**, **Pichler / Sallinger (TU Wien)**. Threads: incremental/streaming core maintenance under source updates; cores for **GLAV mappings with disjunction and richer target constraints**; **provenance-aware** exchange; and using mapping rewriting to push core computation into modern engines / dataframes *(frontier — verify)*. Renewed interest from schema mapping in **knowledge-graph integration** and ELT pipelines.

## 8. Future Work

(1) Practical, low-exponent core algorithms or a sharp dichotomy on when SQL rewriting yields exact cores. (2) Incremental core maintenance. (3) Cores under existential rules with terminating-chase variants beyond weak acyclicity (e.g., model-faithful acyclicity). (4) Cores for nested/graph data exchange. (5) Cost-based choice between materializing the core vs. a larger universal solution given a query workload.

## 9. Key References

- **[Foundational]** Fagin, Kolaitis, Miller, Popa. *Data Exchange: Semantics and Query Answering.* ICDT 2003 / TCS 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[Foundational]** Fagin, Kolaitis, Popa. *Data Exchange: Getting to the Core.* PODS 2003 / TODS 2005. — [DOI](https://doi.org/10.1145/1061318.1061323)
- **[SOTA]** Gottlob, Nash. *Efficient Core Computation in Data Exchange.* JACM 55(2), 2008. — [DOI](https://doi.org/10.1145/1346330.1346334) (conf. version PODS 2006: [DOI](https://doi.org/10.1145/1142351.1142358))
- **[SOTA]** Mecca, Papotti, Raunich, et al. *++Spicy / Core Schema Mappings.* SIGMOD 2009 / VLDB. — [DOI](https://doi.org/10.1145/1559845.1559914)
- **[Foundational]** Chandra, Merlin. *Optimal Implementation of Conjunctive Queries in Relational Data Bases.* STOC 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Survey]** Arenas, Barceló, Libkin, Murlak. *Foundations of Data Exchange.* Cambridge Univ. Press, 2014. — [DOI](https://doi.org/10.1017/CBO9781139060158)

## 10. Worked Example

Source $S=\{E(\text{alice},\text{bob})\}$; st-tgd $E(x,y)\to\exists z\,M(x,z)\wedge M(y,z)$. The chase fires once, inventing a labeled null $z_0$:
$$J=\{M(\text{alice},z_0),\,M(\text{bob},z_0)\}.$$
Now add a *redundant* trigger by also chasing a second copy with fresh null $z_1$, giving the (still universal) solution
$$J'=\{M(\text{alice},z_0),M(\text{bob},z_0),\,M(\text{alice},z_1),M(\text{bob},z_1)\}.$$
$J'$ has 4 tuples but is not minimal: the endomorphism $h(z_1)=z_0$, identity elsewhere, maps $J'\to J'$ with image $J$. No proper homomorphism shrinks $J$ further, so $J$ (2 tuples) is the **core**. Certain answers agree: for $Q()\leftarrow\exists u,v,w\,M(u,w)\wedge M(v,w)$, both $J$ and $J'$ yield *true*. Computing the core means finding that folding endomorphism — here trivial, but in general each fold needs a homomorphism search, which is why the PTIME bound carries a large exponent.

---
*Part of the [DBMS Research catalog](../../README.md).*
