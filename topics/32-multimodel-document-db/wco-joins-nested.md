---
id: 32-multimodel-document-db/wco-joins-nested
title: "Worst-case-optimal joins over nested data"
topic: 32-multimodel-document-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Worst-case-optimal joins over nested data

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/wco-joins-nested` · **Status:** open

## 1. Problem Statement
Worst-case-optimal (WCO) join algorithms (NPRR, Leapfrog Triejoin, Generic-Join) run in time bounded by the **AGM bound** — the tight worst-case output size of a flat conjunctive query. The problem is to extend this theory and these algorithms to *nested* data: documents whose attributes may themselves be arrays, maps, or sub-documents, and queries that join, unnest (`UNWIND`/`json_table`), and re-nest such values.

- **Counting variant:** what is the tight worst-case size of the output of a multi-model conjunctive query that mixes equi-joins with array containment / unnest? (the AGM analogue)
- **Algorithmic variant:** is there an algorithm matching that bound, including the cost of materializing nested outputs?
- **Decision variant:** for a fixed query shape, can the output be enumerated with constant/poly delay?

The core obstacle: nesting breaks the flat-relation assumption. An array-valued attribute is both a value (atom for equality) and a relation (set for unnest), so a single tuple can participate in joins at multiple "arities," and the AGM linear program over a flat hypergraph no longer directly applies.

## 2. Mathematical Foundations
The **AGM bound**: for a join query $Q$ with hypergraph $H=(V,E)$ and relation sizes $|R_e|$, the output is at most $\prod_e |R_e|^{x_e}$ where $\mathbf{x}$ is an optimal *fractional edge cover* — minimize $\sum_e x_e \log|R_e|$ subject to $\sum_{e \ni v} x_e \ge 1\ \forall v$. The optimum equals $N^{\rho^*}$ for the fractional cover number $\rho^*$. WCO algorithms achieve $\tilde O(N^{\rho^*} + |\mathrm{out}|)$.

Nesting requires a *typed/nested hypergraph* where vertices carry a model (atom vs. collection) and the cover LP must price unnest as a Cartesian-like blow-up. Connections: the entropy-LP / **Shearer's lemma** view of AGM (Gogacz–Toruńczyk), factorized representations (whose succinct output size is $N^{\mathrm{fhtw}}$, below AGM), and **information-theoretic bounds** via Shannon and *polymatroid* relaxations. For nested outputs the natural cost measure is the *factorized* size, since a re-nested result can be exponentially smaller than its flat unnesting.

## 3. State of the Art (SOTA)
- **Theory-SOTA (flat):** Ngo–Porat–Ré–Rudra (PODS 2012) and *Generic-Join* (Ngo–Ré–Rudra, SIGMOD Record 2013); PANDA (Abo Khamis–Ngo–Suciu, PODS 2017) handles degree constraints and functional dependencies via the polymatroid/entropy bound.
- **Nested/array:** *array* and *tensor* WCO work (e.g., functional aggregate queries, FAQ, by Abo Khamis–Ngo–Rudra, PODS 2016) generalizes joins with semiring aggregation but assumes flat domains. WCO over graph/property data exists, but a clean AGM analogue with *unnest + re-nest* operators and array-containment predicates is not established.
- **Systems-SOTA:** RelationalAI, Umbra, and *DuckDB* ship WCO-style joins for flat queries; document engines (MongoDB `$lookup`/`$unwind`, SQL/JSON `json_table`) use classic binary-join plans with no WCO guarantee.

## 4. Upper Bound
For the *flat* fragment (unnest everything first, then join), Generic-Join gives $\tilde O(N^{\rho^*}+|\mathrm{out}|)$, but $|\mathrm{out}|$ here is the *flattened* output, which can be exponentially larger than a factorized nested result — so this upper bound is not tight for the nested-output measure. FAQ/factorized evaluation yields $O(N^{\mathrm{fhtw}})$ representation size for the result, the best known succinct upper bound, but does not yet account for array-containment semijoins as first-class operators.

## 5. Lower Bound
The flat AGM bound is *tight* (matching instances exist), giving an unconditional output-size lower bound $\Omega(N^{\rho^*})$. For algorithms, any join algorithm must spend $\Omega(N^{\rho^*})$ in the worst case (output-size lower bound), and pairwise-join plans are provably suboptimal (the triangle query: binary plans need $\Omega(N^2)$ vs. $N^{1.5}$). For the nested setting there is **no published matching lower bound** that accounts for unnest blow-up and factorized output; whether array-containment joins admit a strictly larger exponent is open.

## 6. The Gap
Flat WCO is essentially closed (matching $N^{\rho^*}$). The nested case is open on *both* ends: (i) no agreed-upon AGM analogue/output-size bound for queries mixing equality and unnest/containment, and (ii) no algorithm proven optimal for the *factorized nested output* measure. Closing it needs a cover/entropy LP over typed nested hypergraphs plus a matching enumeration algorithm with provable delay.

## 7. Current Research (as of June 2026)
Directions: extending PANDA/polymatroid bounds to nested and degree-constrained array data; factorized evaluation of SQL/JSON and GQL queries; *(frontier — verify)* groups around Suciu (UW), Ngo/Abo Khamis (RelationalAI), Olteanu (Zurich), and Toruńczyk are pushing entropy-LP techniques toward semistructured and graph patterns. Work on *constant-delay enumeration* for nested results and on WCO joins inside lakehouse engines is active 2025–2026.

## 8. Future Work
A clean nested-AGM theorem; WCO algorithms whose cost is the factorized output size including re-nesting; degree/FD-aware bounds for array containment; integration with property-graph pattern matching (GQL) so multi-model joins share one optimality theory; practical WCO operators in document engines.

## 9. Key References
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008 (AGM bound). — [DBLP](https://dblp.org/rec/conf/focs/AtseriasGM08.html) · [DOI](https://doi.org/10.1137/110859440)
- **[Foundational]** Ngo, Porat, Ré, Rudra. *Worst-case Optimal Join Algorithms.* PODS, 2012 (JACM 2018). — [arXiv](https://arxiv.org/abs/1203.1952) · [DOI](https://doi.org/10.1145/3180143)
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another? (PANDA).* PODS, 2017. — [arXiv](https://arxiv.org/abs/1612.02503) · [DOI](https://doi.org/10.1145/3034786.3056105)
- **[SOTA]** Abo Khamis, Ngo, Rudra. *FAQ: Questions Asked Frequently.* PODS, 2016. — [arXiv](https://arxiv.org/abs/1504.04044) · [DOI](https://doi.org/10.1145/2902251.2902280)
- **[Survey]** Ngo, Ré, Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013. — [arXiv](https://arxiv.org/abs/1310.3314) · [DOI](https://doi.org/10.1145/2590989.2590991)

## 10. Worked Example

The classic **triangle query** $Q = R(a,b)\bowtie S(b,c)\bowtie T(c,a)$ over three relations each of size $N$. The hypergraph has vertices $\{a,b,c\}$ and edges $\{ab, bc, ca\}$. The fractional edge cover LP minimizes $x_{ab}+x_{bc}+x_{ca}$ subject to each vertex being covered, e.g. for $a$: $x_{ab}+x_{ca}\ge 1$. The symmetric optimum is $x_e = \tfrac12$ for all edges, giving $\rho^* = \tfrac32$, so the AGM bound is $N^{3/2}$. A worst-case-optimal algorithm (Generic-Join) runs in $\tilde O(N^{3/2})$, whereas any binary-join plan first materializes an intermediate of size up to $\Theta(N^2)$ — provably worse.

Now make it **nested**: let $T$'s `a`-column instead be an *array* `a_list`, and the third join be `a ∈ T.a_list` (array containment) rather than equality. A single $T$ tuple with a length-$k$ list now behaves like $k$ flat tuples, so unnest-first inflates $|T|$ from $N$ to $\sum_t k_t$. The flat AGM exponent $\tfrac32$ no longer prices this blow-up directly — and the *re-nested* output may be far smaller than its flat unnesting. This is exactly the open gap of Section 6: the cover LP must be redefined over a typed nested hypergraph.

---
*Part of the [DBMS Research catalog](../../README.md).*
