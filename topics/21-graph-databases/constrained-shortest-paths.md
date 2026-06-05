# Labeled-constrained and approximate shortest paths

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/constrained-shortest-paths` · **Status:** partially-solved

## 1. Problem Statement
In an edge-labeled graph $G=(V,E,\ell)$ with $\ell:E\to\Sigma$, answer distance/path queries **constrained by a label predicate**:
- **Label-Constrained Reachability (LCR), decision:** given $(s,t,A)$ with $A\subseteq\Sigma$, is there an $s\rightsquigarrow t$ path using only edges labeled in $A$?
- **Label-Constrained Shortest Path (LCSP), optimization:** the minimum-length such path.
- **Regular-Path-Query (RPQ) distance:** the constraint is a regular language $R$ over $\Sigma$; accept paths whose label string $\in L(R)$ — the navigational core of GQL/SPARQL property paths.

We want an **index** giving sublinear query time with provable **space** and (for approximate variants) **stretch/accuracy** guarantees, on large dynamic graphs. Counting variant: number of constraint-satisfying paths (generally #P-hard).

## 2. Mathematical Foundations
RPQ evaluation is the **intersection of a graph (an NFA over $V$) with the query automaton** $\mathcal{A}_R$: build the product graph $G\times\mathcal{A}_R$ on $V\times Q_R$ and run reachability/BFS; cost $O(|E|\cdot|\mathcal{A}_R|)$ — the **Mendelzon–Wood** framework. Data complexity of RPQ reachability is **NL-complete**; combined complexity is **PSPACE** for full regular expressions but tractable per fixed query.

LCR is a *monotone* special case (label *sets*, no order): the answer is monotone in $A$, enabling **landmark/2-hop indexes with label-set annotations** — each label entry $(h,A_{\min})$ records a minimal label set sufficient to reach hub $h$. The number of *minimal* label sets per pair can be exponential in $|\Sigma|$ in the worst case, which is the core hardness driver. Approximate distance under constraints connects to **spanners/emulators** and the **Thorup–Zwick** stretch–space tradeoff lifted to the product/labeled setting; provable accuracy uses Dijkstra-rank and hop-bounded relaxations.

## 3. State of the Art (SOTA)
- **LCR indexes:** **Landmark Indexing for LCR** (Valstar–Fletcher–Yoshida, SIGMOD 2017) — pruned landmark labeling with minimal label sets; **P2H+** and follow-ups (Peng, Zhang, Lin, Qin et al., VLDB 2020–2022) pushing scalability; **LC-2Hop** variants.
- **LCSP / weighted:** extensions of contraction hierarchies and hub labeling with edge restrictions; **multi-criteria / resource-constrained shortest path** (RCSP) solvers (label-correcting, Lagrangian).
- **RPQ systems:** **MillenniumDB** (worst-case-optimal path enumeration), **Avantgraph**, SPARQL property-path engines (Virtuoso, Blazegraph); **automaton-based product** with WCOJ.
- **Provably-bounded RPQ enumeration:** Martens et al. (PODS) on **enumeration with polynomial delay** for restricted RPQ classes; Casel–Schmid on enumeration delay.

## 4. Upper Bound
- **RPQ reachability:** $O(|E|\cdot|\mathcal{A}_R|)$ online (product-graph BFS); data complexity NL, so $O(\log n)$ space online.
- **LCR (indexed):** landmark + minimal-label-set labeling answers queries in time near $O(|L_s|+|L_t|)$ proportional to stored minimal sets; construction polynomial, but label size worst-case exponential in $|\Sigma|$, practically small for $|\Sigma|$ in the tens.
- **Path enumeration:** simple-path RPQ enumeration with **polynomial delay** for the tractable cases (e.g., $A^*$, $a^* b a^*$); WCOJ-style $O(\mathrm{IN}^{\rho^*}+\mathrm{OUT})$ for pattern-shaped fragments.
- **Approximate constrained distance:** stretch-$(2k-1)$ oracles adapted to label-restricted subgraphs, space $O(k\,n^{1+1/k}\cdot 2^{|\Sigma|})$ in the naive lift.

## 5. Lower Bound
- **Simple-path RPQ:** finding a *simple* path matching a regular expression is **NP-complete** for languages like $(aa)^*$ (Mendelzon–Wood, 1995) — semantics matter critically.
- **Enumeration:** counting RPQ-paths is **#P-hard**; some RPQ classes admit *no* polynomial-delay enumeration unless P=NP (Martens–Niewerth–Trautner; Bagan–Bonifati–Groz).
- **LCR labeling space:** the number of distinct minimal label sets gives an $\Omega(2^{|\Sigma|})$ worst-case index-size barrier; conditional hardness from **OMv** for dynamic LCR.
- **Approximate distance:** the stretch-2 / $\Omega(n^2)$-space barrier (Pătraşcu–Roditty) carries over.

## 6. The Gap
For **trail/walk (homomorphism) semantics** — the GQL default for reachability — the problem is tractable and largely solved in theory, with strong practical indexes (P2H+) for moderate $|\Sigma|$. For **simple-path / counting** semantics it is NP-/#P-hard, so the gap is between hardness and useful restricted-class or approximate algorithms. Genuinely open: index structures that are *simultaneously* sublinear in space, robust to large alphabets, and fully dynamic — current methods pay $2^{|\Sigma|}$ in the worst case. Closing it needs alphabet-parameterized lower bounds matched by adaptive indexes.

## 7. Current Research (as of June 2026)
- Scalable dynamic LCR/LCSP labeling on billion-edge graphs *(frontier — verify)*.
- GQL/SQL-PGQ-aligned **bounded-path-pattern** semantics and their tractable enumeration (Martens, Bonifati, Vrgoč) *(frontier — verify)*.
- WCOJ + automaton fusion in MillenniumDB/Avantgraph for path patterns.
- Groups: TU Eindhoven (Fletcher), Bayreuth/Dortmund (Martens), Lyon (Bonifati), PUC Chile/IMFD (Vrgoč, Arenas), HKUST (Qin, Lin).

## 8. Future Work
- Alphabet- and language-parameterized space lower bounds for LCR/RPQ indexes.
- Approximate constrained distance oracles with provable stretch independent of $|\Sigma|$.
- Unified cost model integrating RPQ navigation with pattern joins (see hybrid-plans problem).
- Practical simple-path enumeration heuristics with anytime guarantees.

## 9. Key References
- **[Foundational]** Mendelzon, A. O., Wood, P. T. *Finding Regular Simple Paths in Graph Databases.* SIAM J. Computing, 1995.
- **[Foundational]** Abiteboul, S., Hull, R., Vianu, V. *Foundations of Databases.* Addison-Wesley, 1995 (RPQ / datalog navigation).
- **[SOTA]** Valstar, L., Fletcher, G., Yoshida, Y. *Landmark Indexing for Evaluation of Label-Constrained Reachability Queries.* SIGMOD 2017.
- **[SOTA]** Peng, Y., Zhang, Y., Lin, X., Qin, L., Zhang, W. *Answering Billion-Scale Label-Constrained Reachability Queries within Microsecond.* VLDB 2020.
- **[SOTA]** Bagan, G., Bonifati, A., Groz, B. *A Trichotomy for Regular Simple Path Queries on Graphs.* PODS 2013 / JCSS.
- **[Survey]** Angles, R., Arenas, M., Barceló, P., Hogan, A., Reutter, J., Vrgoč, D. *Foundations of Modern Query Languages for Graph Databases.* ACM Computing Surveys, 2017.
- **[SOTA]** Vrgoč, D. et al. *MillenniumDB: An Open-Source Graph Database System.* 2023.

---
*Part of the [DBMS Research catalog](../../README.md).*
