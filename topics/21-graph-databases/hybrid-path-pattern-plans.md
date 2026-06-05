# Multiway join plans mixing paths and patterns

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/hybrid-path-pattern-plans` · **Status:** open

## 1. Problem Statement
Design a **cost-based query optimizer for graph pattern + path queries** (GQL / SQL-PGQ / Cypher / SPARQL) that **interleaves** three execution paradigms optimally:
1. **Worst-case-optimal joins (WCOJ)** for dense, cyclic subgraph patterns,
2. **Path navigation** (regular-path / variable-length traversals, BFS/DFS/automaton product),
3. **Binary (hash/merge) joins** for tree-like, selective sub-patterns.

Decision/optimization variants:
- **Plan search (optimization):** over the hybrid plan space, minimize estimated cost.
- **Cardinality/cost estimation (statistical):** estimate intermediate sizes for cyclic patterns and paths — the dominant source of error.
- **Worst-case-optimality (theoretical):** when must a plan switch to WCOJ to retain the AGM guarantee, and how to cost paths so binary joins are used only when provably safe?

It is open because no optimizer is known to be simultaneously *worst-case-optimal*, *path-aware*, and *practically cost-effective*, and the unified cost model is missing.

## 2. Mathematical Foundations
**AGM bound.** For a join/pattern query $Q$ with hypergraph $\mathcal{H}$, the worst-case output size is $|Q|\le \prod_e |R_e|^{x_e}$ where $\{x_e\}$ is an optimal **fractional edge cover**; the exponent $\rho^*(Q)$ is the LP optimum. **WCOJ** algorithms (NPRR / **Leapfrog Triejoin**, Veldhuizen) run in $O(\mathrm{IN}^{\rho^*}+\mathrm{OUT})$ — *optimal* for the worst case, whereas any binary-join tree can be **super-polynomially** worse (e.g., triangle query: binary joins $\Theta(n^2)$ vs WCOJ $\Theta(n^{1.5})$).

**Beyond worst case.** **Tree decompositions / fractional hypertree width** $\mathsf{fhw}$ and **submodular width** $\mathsf{subw}$ (Marx) give the **PANDA** algorithm bound $\tilde{O}(\mathrm{IN}^{\mathsf{subw}}+\mathrm{OUT})$, the current theoretical frontier; binary joins are optimal only for $\alpha$-acyclic queries (**Yannakakis**' algorithm, linear in IN+OUT). **Factorized databases** (Olteanu–Závodný) compress intermediate results and change the cost calculus.

**Paths** add an automaton dimension: an RPQ contributes a product with $\mathcal{A}_R$, and transitive-closure subgoals have output sizes not captured by AGM. A unified cost model must combine AGM/$\mathsf{subw}$ exponents, path-output estimates, and factorized sizes — no closed framework does this.

## 3. State of the Art (SOTA)
- **WCOJ systems:** **EmptyHeaded** (Aberger et al., SIGMOD 2017) — GHD + WCOJ hybrid; **GraphflowDB / Kùzu** mixing WCOJ and binary joins via cost; **Umbra** WCOJ integration (Freitag et al., VLDB 2020) showing how to embed WCOJ in a relational optimizer.
- **Path-aware engines:** **MillenniumDB**, **Avantgraph**, SPARQL property-path optimizers; automaton + WCOJ fusion.
- **Optimizers:** classic **Selinger** dynamic-programming join ordering; graph-specific cardinality estimation (**G-CARE** benchmark, Park et al., SIGMOD 2020) exposing large estimation errors; **factorized** query processing (Olteanu et al.).
- **Adaptive hybrids:** cost models choosing per-edge WCOJ vs binary join (GraphflowDB, Mhedhbi–Salihoglu, VLDB 2019).

## 4. Upper Bound
- **Pattern matching:** $O(\mathrm{IN}^{\rho^*}+\mathrm{OUT})$ via Leapfrog Triejoin; $\tilde{O}(\mathrm{IN}^{\mathsf{subw}}+\mathrm{OUT})$ via PANDA (best known, beyond-worst-case).
- **Acyclic queries:** $O(\mathrm{IN}+\mathrm{OUT})$ (Yannakakis).
- **Hybrid plans:** EmptyHeaded/Umbra achieve worst-case optimality for the cyclic core while using binary joins on acyclic parts — provably no worse than $\mathrm{IN}^{\rho^*}$ when the WCOJ core is chosen correctly.
- **Paths:** product-graph reachability $O(|E|\cdot|\mathcal{A}_R|)$; no unified optimal bound combining paths + patterns is known.

## 5. Lower Bound
- **Binary-join suboptimality:** any binary-join plan for the triangle (and more generally cyclic queries) is $\Omega(\mathrm{IN}^{\rho^*-\epsilon})$ worse — *unconditional* in the binary-join model — motivating WCOJ.
- **Optimal join lower bound:** $\Omega(\mathrm{IN}^{\rho^*}+\mathrm{OUT})$ is information-theoretically necessary in the worst case (matching AGM).
- **Cardinality estimation:** provably hard — no estimator avoids large worst-case error; pattern counting is **#W[1]-hard** parameterized by pattern size, and exact subgraph counting is **#P-hard**.
- **Subgraph detection:** $k$-clique detection conditional hardness (no $O(n^{k(\omega/3)-\epsilon})$ via combinatorial methods; **SETH/3SUM** lower bounds for specific patterns).

## 6. The Gap
Each paradigm is *individually* near-optimal (WCOJ for cyclic patterns, Yannakakis for acyclic, product graphs for paths), but the **interleaving** is open on two fronts: (1) **theory** — no algorithm/optimizer is known to be worst-case-optimal over the *combined* path+pattern plan space, since path outputs escape the AGM/$\mathsf{subw}$ framework; (2) **practice** — cardinality estimation for cyclic patterns and variable-length paths is so error-prone (G-CARE) that cost-based choices are unreliable. The gap is genuinely open: closing it needs a *unified cost model* and either a provably optimal hybrid algorithm or matching lower bounds showing none exists.

## 7. Current Research (as of June 2026)
- Embedding WCOJ + factorization into mainstream cost-based optimizers (Umbra, DuckDB-PGQ, Kùzu) *(frontier — verify)*.
- Learned and sampling-based cardinality estimators for graph patterns; robust/pessimistic estimation with guarantees *(frontier — verify)*.
- Optimizing GQL/SQL-PGQ bounded-path patterns jointly with subgraph patterns.
- Groups: Waterloo (Salihoglu, Kùzu), TUM (Neumann/Freitag, Umbra), Oxford (Olteanu, factorized DBs), Washington/RelationalAI (Ré, Ngo, WCOJ + PANDA), SNU (Park, G-CARE).

## 8. Future Work
- A unified cost/size model spanning AGM, submodular width, factorization, and path outputs.
- Provably optimal (or conditionally optimal) hybrid path+pattern algorithms.
- Robust, guarantee-bearing cardinality estimation for cyclic + path queries.
- Adaptive runtime re-optimization that switches paradigms mid-execution.

## 9. Key References
- **[Foundational]** Selinger, P. G., et al. *Access Path Selection in a Relational Database Management System.* SIGMOD 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Atserias, A., Grohe, M., Marx, D. *Size Bounds and Query Plans for Relational Joins.* FOCS 2008 / SICOMP (the AGM bound). — [DOI](https://doi.org/10.1137/110859440)
- **[SOTA]** Ngo, H. Q., Porat, E., Ré, C., Rudra, A. *Worst-Case Optimal Join Algorithms.* PODS 2012 / JACM 2018. — [DOI](https://doi.org/10.1145/3180143)
- **[SOTA]** Abo Khamis, M., Ngo, H. Q., Suciu, D. *What Do Shannon-Type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* (PANDA) PODS 2017. — [DOI](https://doi.org/10.1145/3034786.3056105)
- **[SOTA]** Aberger, C. R., Lamb, A., Tu, S., Nötzli, A., Olukotun, K., Ré, C. *EmptyHeaded: A Relational Engine for Graph Processing.* SIGMOD 2017 / ACM TODS. — [DOI](https://doi.org/10.1145/3129246)
- **[SOTA]** Freitag, M., Bandle, M., Schmidt, T., Kemper, A., Neumann, T. *Adopting Worst-Case Optimal Joins in Relational Database Systems.* VLDB 2020. — [DOI](https://doi.org/10.14778/3407790.3407797)
- **[Survey/Benchmark]** Park, Y., Ko, S., Bhowmick, S. S., Kim, K., Hong, K., Han, W.-S. *G-CARE: A Framework for Performance Benchmarking of Cardinality Estimation Techniques for Subgraph Matching.* SIGMOD 2020. — [DOI](https://doi.org/10.1145/3318464.3389702)

## 10. Worked Example

**Why the triangle forces WCOJ.** The triangle query $Q_\triangle = R(a,b)\bowtie S(b,c)\bowtie T(a,c)$ over relations each of size $N$. The AGM bound uses the fractional edge cover LP: assign weight $x_e$ to each of the three edges of the query hypergraph (a triangle), minimizing $\sum_e x_e$ subject to covering every vertex. Setting $x_R=x_S=x_T=\tfrac12$ covers each of $a,b,c$ with total weight $1$, so $\rho^*=\tfrac32$ and the output is bounded by $N^{3/2}$.

- **Binary-join plan:** materialize $R\bowtie S$ first. On a worst-case instance this intermediate has $\Theta(N^2)$ tuples even though the final answer is only $O(N^{3/2})$ — so any binary plan does $\Omega(N^2)$ work.
- **WCOJ (Leapfrog Triejoin):** runs in $O(N^{3/2}+\mathrm{OUT})$, matching $\rho^*$.

For $N=10^6$: binary $\approx 10^{12}$ vs. WCOJ $\approx 10^9$ — a $1000\times$ gap. Now add a path subgoal, e.g. $a \xrightarrow{ab^*} c$: its output size is *not* captured by $\rho^*$, so a unified optimizer must cost the automaton product separately — exactly the open modeling gap.

---
*Part of the [DBMS Research catalog](../../README.md).*
