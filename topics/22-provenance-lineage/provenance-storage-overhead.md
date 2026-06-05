# Provenance Storage Overhead Bounds

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/provenance-storage-overhead` · **Status:** open

## 1. Problem Statement
To answer provenance queries — *which base data witnessed this result*, or *recompute this result under a hypothetical base edit* — a system stores annotations alongside (or instead of) query outputs. The question is **how much space this fundamentally requires**. Given a query $Q$ and database $D$, let a provenance representation be **recomputation-complete** if it suffices to recompute $Q$'s output under any deletion of base tuples (equivalently, it stores the full semiring polynomial $\mathbb{N}[X]$ for each output tuple). 

Variants: **(worst-case)** over all $D$ of size $n$, what is $\max$ space for recomputation-complete provenance of a fixed $Q$? **(instance-optimal)** for a *given* $D$, what is the smallest representation, and can we get within a constant/log factor of it? **(decision)** does a representation of size $\le k$ exist? **(trade-off)** the space–query-time Pareto frontier between verbose (fast-query) and factorized/deduplicated (compact, slow-query) encodings.

## 2. Mathematical Foundations
Provenance lives in the **commutative semiring** $\mathbb{N}[X]$ (Green–Karvounarakis–Tannen): each output tuple carries a multivariate polynomial; "+" combines alternative derivations (union, projection), "$\times$" combines joint dependence (join). The verbose **sum-of-monomials** form has size $\Theta$(number of derivations). 

The key compression tool is **factorized representation** (Olteanu–Závodný): a provenance polynomial admits a nested $\sum/\prod$ circuit (an arithmetic circuit / d-DNNF-like structure) whose size depends on query structure. For a join query $Q$ with **fractional hypertree width** $\mathsf{fhtw}$,
$$ |\text{factorized prov}| \le O\!\big(|D|^{\mathsf{fhtw}(Q)}\big), \qquad |\text{flat prov}| \le O\!\big(|D|^{\rho^*(Q)}\big), $$
where $\rho^*$ is the fractional edge cover (the **AGM bound** exponent). Since $1 \le \mathsf{fhtw} \le \rho^*$, factorization can be exponentially smaller. Deduplication (sharing common subexpressions) corresponds to a **read-once / circuit** representation; information-theoretically, the lower bound is the **entropy / Kolmogorov complexity** of the answer-plus-recomputation function relative to $Q$.

## 3. State of the Art (SOTA)
- **Theory:** Factorized databases and provenance circuits (Olteanu, Schleich, Závodný; Amarilli–Bourhis–Senellart on provenance circuits for bounded-treewidth) give the tightest known structural compression. The AGM bound (Atserias–Grohe–Marx, FOCS 2008) and worst-case-optimal joins (Ngo–Porat–Ré–Rudra) pin down flat-output worst cases.
- **Systems:** **ProvSQL** stores provenance circuits in PostgreSQL; **GProM/Perm** materialize provenance via query rewriting; **Smoke** (Psallidas–Wu, SIGMOD 2018) and **Lineage-backed** engines compress via index-style lineage capture; column stores deduplicate via dictionary/RLE on annotation columns.

## 4. Upper Bound
For acyclic / bounded-fractional-hypertree-width queries, recomputation-complete provenance is storable in $O(|D|^{\mathsf{fhtw}})$ via factorized circuits, with constant- or log-overhead per gate. For unions of conjunctive queries, the bound is the max over the disjuncts. Deduplicated d-DNNF provenance supports linear-time recomputation in the circuit size after a base deletion. In the **deterministic-monomial / "PosBool"** semiring (why-provenance only), provenance compresses to a Boolean circuit of size $O(|D|^{\mathsf{fhtw}})$.

## 5. Lower Bound
Information-theoretic: there exist instances where flat provenance has size $\Theta(|D|^{\rho^*})$ — matched by AGM-tight worst-case instances (Cartesian-product-like joins) — so no recomputation-complete encoding can beat the query's intrinsic output entropy. For **factorized** size, lower bounds come from circuit complexity: certain provenance polynomials require $\Omega(|D|^{\mathsf{fhtw}})$ factorized size (Olteanu–Závodný give matching bounds for hierarchical/acyclic classes). Computing the *minimum* circuit (instance-optimal encoding) is at least as hard as **minimum-circuit-size / read-once factorization**, conjectured intractable; deciding minimum d-DNNF size is not known to be in PTIME. Communication-complexity arguments give space lower bounds for streaming provenance.

## 6. The Gap
For bounded-width queries the worst-case gap between factorized upper bound and circuit lower bound is **closed up to constants**. The **open** core is *instance-optimality*: no PTIME algorithm is known to produce a provenance encoding within an $o(\log n)$ factor of the smallest possible for a given $D$, and there is no dichotomy classifying which $(Q,D)$ admit polynomial-size recomputation-complete provenance. The trade-off between deduplication-savings and the cost of *querying* the compressed form is not characterized as a tight Pareto curve.

## 7. Current Research (as of June 2026)
- Tight space–time trade-offs for **provenance circuits under updates** (incremental maintenance of the factorization) — Olteanu, Amarilli, Senellart circles.
- **Semiring provisioning / approximate provenance**: storing a lossy summary sufficient for top-$k$ or probability estimates within $\epsilon$ *(frontier — verify)*.
- Learned / instance-adaptive compression of lineage columns in column stores; sketch-based provenance for high-multiplicity aggregates *(frontier — verify)*.

## 8. Future Work
A dichotomy theorem: which CQ/UCQ classes admit polynomial-size recomputation-complete provenance. Instance-optimal factorization with approximation guarantees. Unified accounting that charges both storage *and* recomputation cost. Provenance compression bounds under bag semantics and aggregation, where the semiring is $\mathbb{N}$-weighted and current circuit bounds are loose.

## 9. Key References
- **[Foundational]** Todd Green, Grigoris Karvounarakis, Val Tannen. *Provenance Semirings.* PODS, 2007.
- **[Foundational]** Albert Atserias, Martin Grohe, Dániel Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008 (AGM bound).
- **[SOTA]** Dan Olteanu, Jakub Závodný. *Size Bounds for Factorised Representations of Query Results.* ACM TODS, 2015.
- **[SOTA]** Antoine Amarilli, Pierre Bourhis, Pierre Senellart. *Provenance Circuits for Trees and Treelike Instances.* ICALP, 2015.
- **[SOTA]** Fotis Psallidas, Eugene Wu. *Smoke: Fine-grained Lineage at Interactive Speed.* PVLDB, 2018.
- **[Survey]** Hung Q. Ngo, Christopher Ré, Atri Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
