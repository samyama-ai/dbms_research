# Worst-case-optimal RDF/SPARQL evaluation

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/sparql-wco-evaluation` · **Status:** partially-solved

## 1. Problem Statement
Evaluate SPARQL **basic graph patterns** (BGPs) — sets of triple patterns over an RDF graph, i.e., conjunctive queries over a ternary relation `triple(s,p,o)` — and BGPs extended with **property paths** (regular expressions over predicates), so that the running time matches the *worst-case-optimal* (WCO) bound: $O(\mathrm{AGM}(Q))$ up to log/poly factors, where $\mathrm{AGM}(Q)$ is the fractional-edge-cover bound on the maximum output size. The optimization goal is to never be asymptotically worse than any traditional binary-join plan and, ideally, to also exploit **tree/hypertree decompositions** for acyclic and bounded-width queries (yielding output-sensitive $O(\mathrm{poly}(|D|) + |Q(D)|)$).

Variants:
- **Pure BGP (CQ) evaluation:** join-only, the classic WCOJ target.
- **BGP + property paths:** add transitive closure / RPQs, which break the AGM framework (infinite/regular intermediate relations).
- **Aggregation/OPTIONAL:** WCO bounds for the full SPARQL algebra (left-outer-join, projection) — much less understood.
Status is *partially solved*: WCOJ is well understood and deployed for pure BGPs; combining it cleanly with property paths and decompositions at scale is open.

## 2. Mathematical Foundations
The **AGM bound** (Atserias–Grohe–Marx, FOCS 2008 / SICOMP 2013): for a join query $Q$ with hypergraph $\mathcal{H}$ and a fractional edge cover $x$, $|Q(D)| \le \prod_R |R|^{x_R}$, and the minimum over covers is tight. **Worst-case-optimal join** algorithms (NPRR — Ngo–Porat–Ré–Rudra, PODS 2012; **Leapfrog Triejoin** — Veldhuizen, ICDT 2014; **Generic Join** — Ngo–Ré–Rudra) run in $\tilde{O}(\mathrm{AGM}(Q))$, beating binary-join plans whose intermediate results can blow up (the classic triangle query: binary joins are $\Theta(m^2)$, WCOJ is $\Theta(m^{3/2})$).

Beyond worst case: **fractional hypertree width** $\mathrm{fhw}$ and **submodular width** $\mathrm{subw}$ (Marx, J. ACM 2013) give $O(|D|^{\mathrm{subw}} + |Q(D)|)$ via the *PANDA* algorithm (Abo Khamis–Ngo–Suciu, PODS 2017), the information-theoretic generalization using Shannon-inequality-based bounds. Property paths add the **algebraic-path** layer: an RPQ is evaluated as the transitive closure of an automaton-product graph, with provenance/semiring structure; WCO theory does not natively bound regular relations, requiring hybrid analyses.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Generic Join / LFTJ for CQs; PANDA for $\mathrm{subw}$-optimality; *FAQ/AJAR* framework (Abo Khamis–Ngo–Rudra, PODS 2016) unifying joins+aggregation over semirings. For RPQs, the automaton-times-graph product with WCO inner joins.
- **Systems-SOTA:** **Graphflow** and **Kùzu** (Salihoglu et al., Waterloo) implement WCOJ + factorized processing for property graphs; **EmptyHeaded** (Aberger–Lamb–Tu–Ré, SIGMOD 2017) combines WCOJ with GHD plans; **Umbra/DuckDB** and **RDF-3X / gStore / Blazegraph / Virtuoso** for RDF (mostly binary-join + indexing). MillenniumDB and avantgraph push WCOJ + path-query integration. Apache Jena/rdf4x are reference SPARQL engines without WCOJ.

## 4. Upper Bound
- Pure BGP/CQ: $\tilde{O}(\mathrm{AGM}(Q))$ time, $O(|D|)$ extra space via Generic Join/LFTJ (PODS 2012, ICDT 2014).
- Acyclic CQ (Yannakakis 1981): $O(|D|\cdot|Q(D)|)$, with constant-delay enumeration after linear preprocessing (free-connex case, Bagan–Durand–Grandjean).
- Bounded submodular width: $O(|D|^{\mathrm{subw(Q)}}\cdot \log|D| + |Q(D)|)$ via PANDA (PODS 2017).
- Property paths: each RPQ predicate evaluated in $O(|automaton|\cdot|E|)$ for the closure; combined plans use WCOJ over precomputed/lazy path relations — no clean single AGM-style bound yet.

## 5. Lower Bound
- BGP/CQ evaluation (combined complexity) is **NP-hard** (CQ containment / Boolean CQ); $\mathrm{AGM}(Q)$ is a *tight* worst-case output bound, so no comparison-based join can beat $\Omega(\mathrm{AGM}(Q))$ in general.
- Constant-delay enumeration is impossible for non-free-connex acyclic CQs unless **Boolean matrix multiplication** has truly subcubic combinatorial algorithms (Berkholz–Keppmann–Schweikardt; Bagan et al.) — a fine-grained conditional lower bound.
- Property-path / RPQ evaluation under **simple-path** semantics is **NP-complete** (Mendelzon–Wood 1995); SPARQL chose *walk* (arbitrary-path) semantics to stay in PTIME, but counting paths is still $\#P$-hard.
- Triangle-type BGPs inherit the $3$SUM/BMM-conditional barriers for listing.

## 6. The Gap
For pure BGPs the gap is essentially **closed** (matching AGM upper/lower; $\mathrm{subw}$ optimality known). Genuinely open: (a) a **unified cost model and algorithm** that is simultaneously WCO for joins *and* optimal for property-path closures, rather than a two-phase hack; (b) WCO bounds for the **full SPARQL algebra** with OPTIONAL/negation/aggregation; (c) practical $\mathrm{subw}$-optimal evaluation (PANDA is not yet competitive in systems); (d) cardinality estimation good enough to *choose* WCOJ vs binary plans adaptively on real RDF.

## 7. Current Research (as of June 2026)
Kùzu and MillenniumDB are actively integrating WCOJ with path/recursive queries and the new **GQL/SQL-PGQ** path semantics *(frontier — verify)*. The Waterloo (Salihoglu), Oxford (Reutter, Vrgoč, Cuenca Grau), and Washington (Suciu, Abo Khamis at RelationalAI) groups push factorized + information-theoretic (PANDA/$\#$SMW) evaluation toward systems readiness. Work on **bounding intermediate results for RPQs via degree constraints** and on combining WCOJ with learned cardinality estimators is an open frontier *(frontier — verify)*. Standardization (SPARQL 1.2, ISO GQL 2024) is sharpening the target semantics.

## 8. Future Work
- A single optimality notion covering joins + Kleene-star path predicates.
- Engineering PANDA / submodular-width plans to beat WCOJ on cyclic queries in practice.
- WCO-aware cost-based optimizers with degree/cardinality constraints for RDF.
- Extending WCO + provenance/semiring evaluation to OPTIONAL, aggregation, and property-path counting.

## 9. Key References
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS 2008 / SIAM J. Comput., 2013.
- **[Foundational]** Ngo, Porat, Ré, Rudra. *Worst-Case Optimal Join Algorithms.* PODS, 2012 (J. ACM, 2018).
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-Type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another? (PANDA).* PODS, 2017.
- **[SOTA]** Aberger, Lamb, Tu, Nötzli, Olukotun, Ré. *EmptyHeaded: A Relational Engine for Graph Processing.* SIGMOD / ACM TODS, 2017.
- **[SOTA]** Feng, Ko, Mhedhbi, Salihoglu et al. *Kùzu / Graphflow: Worst-Case-Optimal Joins for Property Graphs.* CIDR / SIGMOD, 2019–2023.
- **[Foundational]** Mendelzon, Wood. *Finding Regular Simple Paths in Graph Databases.* SIAM J. Comput., 1995.
- **[Survey]** Ngo, Ré, Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
