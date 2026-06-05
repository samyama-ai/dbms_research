# Enumerating paths with bag and trail semantics

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/path-enumeration-semantics` · **Status:** partially-solved

## 1. Problem Statement
Given a directed (multi-)graph $G=(V,E)$, source/target nodes (or node-set predicates), and a path pattern (a regular path query, RPQ, or a richer GPML pattern), **enumerate the matching paths** under a chosen *path semantics*:
- **walk/bag semantics** (arbitrary paths; vertices/edges may repeat),
- **trail semantics** (no edge repeats),
- **simple-path semantics** (no vertex repeats),
- restricted to **shortest** paths, **all** paths, or a top-$k$ slice.

The goal is an enumeration algorithm with **polynomial delay** (time between consecutive outputs is polynomial in $|G|$) and ideally polynomial preprocessing, or a proof that no such algorithm exists. Decision/counting variants: *does a trail/simple path matching $R$ exist?* and *count* such paths (often #P-hard). The practical driver is that GQL and SQL/PGQ (ISO 2023/2024) standardize these semantics and require engines to materialize path bindings.

## 2. Mathematical Foundations
An RPQ is a regular language $R$ over edge labels; a path $p$ matches if its label word $\lambda(p)\in L(R)$. Evaluation under walk semantics reduces to a product construction $G\times A_R$ (the NFA $A_R$), reachability in which is in NL / polynomial time. Under **simple-path** semantics, even fixed regular expressions become intractable: deciding existence of a simple path matching $R=(aa)^*$ is **NP-complete** (Mendelzon–Wood, 1995); the dichotomy of which $R$ stay tractable was settled by **Bagan–Bonifati–Groz (2013, 2020)**. Counting simple paths/trails of given length is **#P-complete** (Valiant). Enumeration complexity uses classes **DelayP** (polynomial delay) and **OutputP**; for trails, Eulerian-style and color-coding arguments apply. Trail semantics is generally easier than simple-path because edge-disjointness interacts more gracefully with the product automaton, but is still hard for general patterns. The Yen / Eppstein top-$k$ shortest-path machinery underlies shortest-path enumeration: Eppstein gives $k$ shortest *walks* in $O(m+n\log n+k)$.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Bagan–Bonifati–Groz give a trichotomy and DelayP enumeration for *simple-path* RPQ answers in the tractable cases; Martens–Trautner / Martens–Niewerth study enumeration of RPQ *paths* (not just endpoint pairs) with delay guarantees, including **shortest-path** binding enumeration in polynomial delay.
- **Standards-SOTA:** GQL/SQL-PGQ adopt **walk** semantics by default for unbounded quantification, **trail** as the headline restrictor for arbitrary patterns, and **shortest/all shortest/any** modes — chosen precisely to dodge simple-path #P-hardness.
- **Systems-SOTA:** Neo4j (Cypher), TigerGraph, RedisGraph, DuckPGQ, Kùzu implement trail/shortest enumeration with worklist + automaton-product engines.

## 4. Upper Bound
For **walk** and **shortest-walk** semantics, RPQ-path enumeration is in **polynomial delay** with polynomial preprocessing via the product graph + Eppstein-style $k$-shortest expansion (Martens–Niewerth–Trautner, ICDT/PODS 2022–2023). For **trail** semantics under arbitrary RPQs, enumeration is solvable but the best general bound is FPT in pattern size with potentially exponential dependence; for **all-shortest trails** polynomial delay is achievable. Model: RAM, data complexity.

## 5. Lower Bound
**Simple-path** existence for $R=(aa)^*$ is NP-complete (Mendelzon–Wood 1995); hence no polynomial-delay enumeration unless P=NP for those patterns. **Counting** simple paths/trails is #P-complete (Valiant 1979). Two-disjoint-paths-style and $k$-cycle reductions give fine-grained barriers; detecting a simple path of length $k$ is W[1]-hard without color-coding tricks. Under SETH, listing all matches of some patterns cannot beat the trivial output-sensitive bound. These hold in the standard sequential RAM model.

## 6. The Gap
The dichotomy for **simple-path** RPQs is *closed* (tractable iff $R$ is in the Bagan–Bonifati–Groz tractable class). The genuinely **open** region is **trail** semantics for full GPML patterns (conjunctions of RPQs, with grouping, repetition, and data-value predicates): no tight characterization separates DelayP from hardness, and the exact delay for *all trails* (not just shortest) under arbitrary $R$ is unknown. Reconciling the standard's per-binding requirements (variable bindings, not just paths) with worst-case-optimal delay is unresolved.

## 7. Current Research (as of June 2026)
Active work on enumeration complexity of GPML by **Martens, Niewerth, Trautner, Popp** (Bayreuth) and **Bonifati, Groz** (Lyon); formal-semantics teams (**Libkin, Vrgoč, Hartig, Reutter**) refining GQL path-mode semantics. *(frontier — verify)* recent results extend polynomial-delay enumeration to bounded-repetition GPML and to "any shortest" modes, and explore "ranked trail" enumeration. Work on DuckPGQ/Kùzu pushes WCOJ-backed path materialization into columnar engines.

## 8. Future Work
- Tight DelayP-vs-hardness dichotomy for **trail** GPML patterns.
- Enumeration under **data-value** joins (property predicates) inside paths.
- Approximate / sampled path enumeration with statistical guarantees when exact counting is #P-hard.
- Cost models that let optimizers choose semantics-aware physical plans.

## 9. Key References
- **[Foundational]** Mendelzon, Wood. *Finding Regular Simple Paths in Graph Databases.* SIAM J. Comput., 1995.
- **[Foundational]** Bagan, Bonifati, Groz. *A Trichotomy for Regular Simple Path Queries on Graphs.* PODS 2013 / ACM TODS 2020.
- **[SOTA]** Martens, Niewerth, Trautner, Popp. *Representing Paths in Graph Database Pattern Matching / Enumeration for RPQs.* PODS–ICDT 2022–2023.
- **[Foundational]** Eppstein. *Finding the k Shortest Paths.* SIAM J. Comput., 1998.
- **[Survey]** Francis et al. *GQL and SQL/PGQ: Theoretical Models and Semantics.* SIGMOD/PODS 2023.

---
*Part of the [DBMS Research catalog](../../README.md).*
