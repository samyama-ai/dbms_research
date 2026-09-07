---
id: 22-provenance-lineage/aggregate-query-provenance
title: "Aggregate-Query Provenance Semantics"
topic: 22-provenance-lineage
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Aggregate-Query Provenance Semantics

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/aggregate-query-provenance` · **Status:** partially-solved

## 1. Problem Statement
Queries that mix `GROUP BY`, aggregation (`SUM`, `COUNT`, `MIN`, `MAX`, `AVG`), and ordinary relational operators dominate analytics, yet the semiring framework annotates *tuples*, not the *values* aggregation produces. The problem is to give a **compositional algebraic model of provenance for aggregate queries** such that: (a) each aggregated output value carries provenance explaining how source tuples contributed (and with what multiplicity/weight); (b) provenance commutes with the relational and aggregation operators so equivalent plans agree; (c) the model supports **incremental recomputation** — when a source tuple's annotation changes (insert/delete/update), the aggregate's provenance and value update without full recomputation. Variants: a *semantics* variant (what algebra captures aggregation provenance?), a *complexity* variant (delta cost of incremental update), and a *querying* variant (can we ask "which sources affected this average by more than 5%?").

## 2. Mathematical Foundations
The Amsterdamer–Deutch–Tannen (PODS 2011) construction tensors the provenance semiring $K$ with the aggregation monoid. An aggregated value is an element of the **semimodule** $K \otimes M$, where $M$ is the commutative monoid of the aggregation domain (e.g., $(\mathbb{R}, +)$ for `SUM`, $(\mathbb{R}, \min)$ for `MIN`). A group's aggregate is a formal sum $\sum_i k_i \otimes v_i$ pairing each contributing value $v_i$ with its provenance annotation $k_i \in K$. Key identities: $k \otimes (v + v') = k\otimes v + k \otimes v'$ and $(k+k')\otimes v = k\otimes v + k'\otimes v$ make $\otimes$ bilinear, giving compositionality. `SUM` and `COUNT` fit cleanly (the monoid is a commutative group or naturally ordered); `MIN`/`MAX` need a *semilattice* and lose invertibility (problematic for deletion); `AVG` is a derived ratio of `SUM`/`COUNT` and is not directly a monoid homomorphism, so it requires lazy/symbolic handling.

For incrementality, the relevant theory is *differential/incremental view maintenance*: provenance-annotated aggregates form a structure where a delta $\Delta R$ induces a delta $\Delta(\text{agg})$ computable from the algebraic ring/group structure (z-relations, DBSP's $\mathbb{Z}$-sets and linear operators).

## 3. State of the Art (SOTA)
Theory-SOTA: Amsterdamer–Deutch–Tannen (PODS 2011) is the canonical model; Fink–Huang–Olteanu, *Aggregation in Probabilistic Databases via Knowledge Compilation* (VLDB 2012) handles aggregation under uncertainty using the same tensoring idea over compiled circuits. Systems-SOTA: GProM (Arab et al., 2018) and ProvSQL (Senellart et al., 2018) implement aggregate provenance for `SUM`/`COUNT`; DBSP (Budiu et al., VLDB 2023) and the earlier DBToaster (Koch et al.) give incremental aggregation that, combined with $\mathbb{N}$/$\mathbb{Z}$ annotations, yields incremental provenance for the linear fragment. Factorized databases (Olteanu–Schleich, F-IVM) support aggregate maintenance with provenance-style factorization.

## 4. Upper Bound
For `SUM`/`COUNT` and the linear aggregation fragment, provenance-annotated evaluation is PTIME data complexity and *fully incremental*: a single-tuple delta updates the aggregate value and its $K\otimes M$ provenance in $O(1)$ amortized per affected group (z-set / DBSP linear-operator bound). For `MIN`/`MAX`, deletion can force recomputation of a group, giving $O(\log n)$ per update with an auxiliary tournament/heap, or $O(n)$ worst case without. Provenance polynomials for an aggregate over a group of size $g$ have size $O(g)$ before factorization.

## 5. Lower Bound
`MIN`/`MAX` maintenance under deletions is provably *non-incremental in the worst case*: there is no constant-delta algorithm because removing the current minimum requires the second-smallest, an inherently non-invertible (semilattice) operation — this matches the well-known hardness of maintaining `MIN` in dynamic settings. For `AVG` and ratio aggregates, exact provenance tracking of "sensitivity" (which sources move the average by $> \epsilon$) relates to subset-selection and is **NP-hard** in the influence-set variant. Under probabilistic semantics, computing the exact distribution of an aggregate is **#P-hard** (Fink–Olteanu).

## 6. The Gap
The **linear, additive fragment is essentially solved** (sound, compositional, incremental). The open part is the **non-invertible/non-linear fragment**: `MIN`/`MAX` deletions, `AVG`/median/percentile provenance, and aggregates nested inside recursion. There is no uniform compositional model that is simultaneously sound *and* incremental for these, and the right algebraic object (beyond ad-hoc semilattice patches) is not settled. Closing it needs either an incremental structure for semilattice aggregates with provenance, or a lower bound proving none exists better than recompute-on-delete.

## 7. Current Research (as of June 2026)
The DBSP/Feldera line (Budiu, McSherry) and F-IVM (Olteanu, Schleich, Nikolic) are converging incremental computation with semiring/factorized provenance. *(frontier — verify)* recent efforts target provenance for **windowed/streaming aggregates** and for **differential-privacy-aware aggregation** where provenance bounds per-source sensitivity. Deutch's group (Tel Aviv) works on explaining aggregate query answers to end users (natural-language and counterfactual explanations over aggregates). Open thread: unifying *approximate* provenance (sketches, sampling) with exact algebraic provenance for big aggregates.

## 8. Future Work
Articulated directions: a sound+incremental model for `MIN`/`MAX`/percentile provenance; provenance for `AVG` and other ratio/holistic aggregates; aggregate provenance under recursion and windows; sketch-based approximate provenance with error guarantees; and integration with differential privacy (provenance as a sensitivity certificate).

## 9. Key References
- **[Foundational]** Y. Amsterdamer, D. Deutch, V. Tannen. *Provenance for Aggregate Queries.* PODS, 2011. — [arXiv](https://arxiv.org/abs/1101.1110) · [DOI](https://doi.org/10.1145/1989284.1989302)
- **[SOTA]** R. Fink, L. Han, D. Olteanu. *Aggregation in Probabilistic Databases via Knowledge Compilation.* VLDB, 2012. — [arXiv](https://arxiv.org/abs/1201.6569) · [DOI](https://doi.org/10.14778/2140436.2140445)
- **[SOTA]** M. Budiu, T. Chajed, F. McSherry, et al. *DBSP: Automatic Incremental View Maintenance for Rich Query Languages.* VLDB, 2023. — [DOI](https://doi.org/10.14778/3587136.3587137)
- **[SOTA]** M. Nikolic, D. Olteanu. *Incremental View Maintenance with Triple Lock Factorization (F-IVM).* SIGMOD, 2018. — [arXiv](https://arxiv.org/abs/1703.07484) · [DOI](https://doi.org/10.1145/3183713.3183758)
- **[Survey]** B. Glavic. *Data Provenance: Origins, Applications, Algorithms, and Models.* Foundations and Trends in Databases, 2021. — [DOI](https://doi.org/10.1561/1900000068)

## 10. Worked Example

Source relation `Sales(item, region, amt)`, each tuple annotated with a provenance variable in the semiring $K = \mathbb{N}[x_1,x_2,x_3]$:

| tuple | item | region | amt | annot |
|-------|------|--------|-----|-------|
| $x_1$ | pen | west | 10 | $x_1$ |
| $x_2$ | pen | west | 30 | $x_2$ |
| $x_3$ | pen | east | 20 | $x_3$ |

Query: `SELECT item, SUM(amt) FROM Sales GROUP BY item`. There is one group, `pen`. In the Amsterdamer–Deutch–Tannen model the aggregate lives in the semimodule $K \otimes (\mathbb{R},+)$ as the formal sum

$$ s = x_1\otimes 10 \;+\; x_2\otimes 30 \;+\; x_3\otimes 20. $$

The output value is the projection $10+30+20 = 60$, but $s$ records *how* each source contributed. Now delete $x_2$ (set its annotation to $0$). By bilinearity $0\otimes 30 = 0$, so the new sum is $x_1\otimes 10 + x_3\otimes 20$, value $30$ — an $O(1)$ incremental update: subtract the contribution of the changed tuple, no recomputation of the group. Contrast `MIN(amt)`: deleting the current min ($x_1=10$) needs the *second*-smallest ($x_3=20$), which the semilattice value alone does not retain — illustrating why `MIN`/`MAX` deletion is non-incremental.

---
*Part of the [DBMS Research catalog](../../README.md).*
