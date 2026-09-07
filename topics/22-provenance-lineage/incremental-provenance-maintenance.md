---
id: 22-provenance-lineage/incremental-provenance-maintenance
title: "Incremental Provenance Maintenance"
topic: 22-provenance-lineage
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Incremental Provenance Maintenance

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/incremental-provenance-maintenance` · **Status:** open

## 1. Problem Statement

Provenance — how-provenance polynomials, why-provenance witness sets, or where-provenance annotations — is expensive to compute and can be far larger than the answer it explains. When base data changes (insertions, deletions, updates), recomputing provenance from scratch is wasteful. **Incremental provenance maintenance (IPM)** asks: given stored provenance for a view/query result and a base update $\Delta D$, produce the updated provenance with cost bounded by the *size of the change and its effect*, not by the database.

This is the provenance analogue of incremental view maintenance (IVM), but harder: the maintained object is not just the answer multiset but its full semiring annotation, which can grow super-linearly and whose factorized (circuit) form must be edited in place.

Variants:
- **Decision:** Is a query/semiring incrementally maintainable with bounded update cost?
- **Optimization:** Minimize amortized/worst-case update time and stored provenance size.
- **Counting:** Maintain provenance polynomials / witness counts under updates (the semiring is $\mathbb{N}[X]$ or $\mathbb{N}$).

## 2. Mathematical Foundations

Under the Green–Tannen semiring model, a query $Q$ maps a $K$-annotated database to $K$-annotated output. For positive RA, evaluation is a semiring homomorphism, so provenance is a polynomial in source variables. Updates are deltas in the semiring: for a union/projection the delta is additive, but **joins induce a product rule**
$$\Delta(P\cdot Q) = (\Delta P)\cdot Q \;+\; P\cdot(\Delta Q)\;+\;(\Delta P)(\Delta Q),$$
mirroring DBToaster's higher-order IVM, but now over *polynomials* rather than counts.

Key machinery:
- **Provenance circuits / factorized representations** (Olteanu–Závodný) bound size by the query's **fractional hypertree width** ($\mathsf{fhw}$); incremental edits should preserve factorization.
- **Higher-order IVM** (recursively materialize deltas) — DBToaster.
- **Dynamic Yannakakis / worst-case-optimal joins** give the static cost target ($O(\mathrm{AGM})$).
- For recursive/Datalog provenance, semi-naïve evaluation and **DRed**/counting algorithms handle deletions; absorptive semirings ($\mathbb{N}^\infty$, tropical) need care under deletion.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Fine-grained dynamic-query results (Berkholz–Keppeler–Schweikardt, PODS 2017) characterize which CQs admit constant-time updates with logarithmic enumeration delay; q-hierarchical queries are maintainable in $O(1)$, others provably not (under fine-grained assumptions). Provenance-aware extensions inherit these bounds for positive fragments.
- **Systems-SOTA:** **DBToaster** (higher-order IVM, VLDBJ 2014); **GProM** (Glavic et al.) for provenance via query rewriting that can be combined with IVM; **ProvSQL** (Senellart et al.) maintains semiring/provenance circuits inside PostgreSQL and supports incremental update of the circuit; **DDlog / differential dataflow** (Timely/Differential Dataflow, McSherry) for incrementally maintained recursive computations with implicit lineage.
- Datalog provenance maintenance via **DRed** and **Provenance-aware DRed** for deletions.

## 4. Upper Bound

For **q-hierarchical** conjunctive queries, provenance (as maintained annotation circuits) can be updated in **constant time per single-tuple update** with constant-delay enumeration of annotated answers (Berkholz–Keppeler–Schweikardt). For general acyclic CQs, dynamic Yannakakis gives $O(\Delta \cdot \mathrm{poly})$ updates. Factorized provenance circuits keep size $O(N^{\mathsf{fhw}})$ and support batched delta application proportional to the affected sub-circuit. Higher-order IVM (DBToaster) achieves amortized cost matching the materialized delta hierarchy, polynomial in update size for any positive query.

## 5. Lower Bound

Under the **OMv (Online Matrix-Vector) conjecture**, non-q-hierarchical CQs (e.g. the 4-cycle, or $Q = R(x),S(x,y),T(y)$) cannot be maintained with $O(N^{1/2-\epsilon})$ update *and* query time simultaneously — so constant-time provenance maintenance is impossible for these (Berkholz–Keppeler–Schweikardt). Maintaining how-provenance is at least as hard as maintaining the answer count, so all IVM lower bounds transfer. For provenance *size*, queries with $\mathsf{fhw} > 1$ force super-linear stored provenance (AGM/factorization lower bounds), giving an unconditional space floor. Deletion in absorptive semirings can require recomputation (no efficient inverse), an algebraic obstruction.

## 6. The Gap

For positive CQs the dichotomy is essentially **tight** (q-hierarchical = $O(1)$, else hard under OMv) — closed up to fine-grained conjectures. The genuinely **open** territory: (1) **recursive / Datalog provenance** under deletion with bounded cost — no clean dichotomy; (2) provenance over **non-positive** queries (difference/aggregation) where the semiring lacks inverses; (3) maintaining *factorized* provenance circuits with edit cost provably proportional to circuit change rather than recomputation. No matching upper/lower bounds exist for these, and absorptive-semiring deletion may be inherently hard.

## 7. Current Research (as of June 2026)

- Incremental maintenance of semiring provenance circuits in ProvSQL and successors *(frontier — verify)*.
- Differential-dataflow-style lineage for recursive analytics at scale (McSherry and collaborators).
- Fine-grained dynamic complexity of provenance for recursive/aggregate queries (Schweikardt, Keppeler groups).
- Provenance maintenance for streaming/temporal data and for ML feature pipelines *(frontier — verify)*.

## 8. Future Work

- A maintainability dichotomy for recursive (Datalog) provenance.
- Efficient deletion in absorptive/idempotent semirings (tropical, why-provenance).
- Edit-cost-optimal updates to factorized provenance.
- Provenance maintenance under schema/query evolution, not just data updates.
- Memory-bounded approximate provenance maintenance with error guarantees.

## 9. Key References

- **[Foundational]** Green, Karvounarakis, Tannen. *Provenance Semirings.* PODS 2007. — [DBLP](https://dblp.org/rec/conf/pods/GreenKT07.html)
- **[Foundational]** Gupta, Mumick, Subrahmanian. *Maintaining Views Incrementally.* SIGMOD 1993 (and DRed for recursion). — [DOI](https://doi.org/10.1145/170035.170066)
- **[SOTA]** Koch et al. *DBToaster: Higher-Order Delta Processing for Dynamic, Frequently Fresh Views.* VLDB Journal, 2014. — [DOI](https://doi.org/10.1007/s00778-013-0348-4)
- **[SOTA]** Berkholz, Keppeler, Schweikardt. *Answering Conjunctive Queries under Updates.* PODS 2017. — [DOI](https://doi.org/10.1145/3034786.3034789) · [arXiv](https://arxiv.org/abs/1702.06370)
- **[SOTA]** Senellart, Jachiet, Maniu, Ramusat. *ProvSQL: Provenance and Probability Management in PostgreSQL.* VLDB 2018. — [DOI](https://doi.org/10.14778/3229863.3236253)
- **[SOTA]** Olteanu, Závodný. *Size Bounds for Factorised Representations of Query Results.* ACM TODS, 2015. — [DOI](https://doi.org/10.1145/2656335)
- **[Survey]** McSherry, Murray, Isaacs, Isard. *Differential Dataflow.* CIDR 2013. — [DBLP](https://dblp.org/rec/conf/cidr/McSherryMII13.html)

## 10. Worked Example

Take the join view $V = R(x,y) \bowtie S(y,z)$ under $\mathbb{N}[X]$ provenance. Base tuples carry variables:
$R = \{(1,2)\!:\!r_1,\ (1,3)\!:\!r_2\}$, $S = \{(2,9)\!:\!s_1,\ (3,9)\!:\!s_2\}$.

The result $V$ on $z=9$ has provenance polynomial
$$ P = r_1 s_1 + r_2 s_2. $$

*Insertion update.* Insert $\Delta S = \{(2,9)\!:\!s_3\}$. By the product rule $\Delta(R\cdot S) = R\cdot \Delta S$ (the $\Delta R\cdot S$ and $\Delta R \cdot \Delta S$ terms vanish since $\Delta R=\varnothing$), the delta provenance is
$$ \Delta P = r_1 s_3, $$
so the maintained polynomial becomes $P' = r_1 s_1 + r_2 s_2 + r_1 s_3$. Cost is proportional to the affected tuples ($1$ join probe), **not** a re-scan of $R\bowtie S$.

*Why the dichotomy bites.* This query $R(x,y),S(y,z)$ is q-hierarchical (the atoms' variable sets are nested/disjoint per the hierarchy condition on $y$), so each single-tuple update is $O(1)$ with constant-delay enumeration (Berkholz–Keppeler–Schweikardt). Contrast the 4-cycle $R(x,y),S(y,z),T(z,w),U(w,x)$: it is *not* q-hierarchical, so under the OMv conjecture no algorithm achieves both $O(N^{1/2-\epsilon})$ update and query time — provenance maintenance inherits this hardness.

---
*Part of the [DBMS Research catalog](../../README.md).*
