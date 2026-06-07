---
id: 26-cardinality-estimation/recursive-query-estimation
title: "Cardinality Estimation for Recursive / Graph Queries"
topic: 26-cardinality-estimation
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Cardinality Estimation for Recursive / Graph Queries

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/recursive-query-estimation` · **Status:** open

## 1. Problem Statement
Estimate the **result size** of recursive and graph-navigational queries: **transitive closure**, **reachability**, **fixed-/variable-length paths** (regular path queries, RPQs), and **recursive CTEs** (`WITH RECURSIVE`). Given a graph/relation $G$ and a recursive query $q$, predict $|q(G)|$ — e.g. the number of reachable pairs, the number of matching paths, or the cardinality of each iteration's delta — without evaluating $q$ to fixpoint.

Variants:
- **Estimation variant:** predict final and per-iteration cardinality to drive plan/memory/iteration choices.
- **Decision variant:** will the closure exceed a memory threshold (will the recursion "blow up")?
- **Counting variant (exact):** counting paths/path-matches is **`#P`-hard**; counting simple paths is `#P`-complete.

The defining difficulty: cardinality **compounds across iterations** and depends on global graph structure (degree distribution, connectivity, presence of cycles/dense components) that local statistics cannot capture. A small change in branching factor produces exponential differences in closure size.

## 2. Mathematical Foundations
A recursive query computes a **least fixpoint** of a monotone operator $T$: $q(G)=\bigcup_{n\ge0} T^n(\emptyset)$. For transitive closure, $|q(G)|$ is the number of reachable pairs $=\sum_v |\text{Reach}(v)|$, governed by the **condensation DAG** and its strongly connected components — within an SCC the contribution is quadratic, across the DAG it is determined by reachability counts.

Formal anchors:
- **Path counting & matrix powers:** the number of length-$\ell$ walks is $\mathbf 1^\top A^\ell \mathbf 1$ ($A$ = adjacency matrix); path (no-repeat) counting is `#P`-hard (Valiant), but *walk* counts and reachable-set sizes are tractable-but-expensive ($O(\text{nnz}\cdot\ell)$ or transitive-closure cost).
- **Reachable-set-size estimation:** the number of distinct reachable vertices per source is exactly a **distinct-counting over a frontier**, enabling **HyperLogLog/MinHash counting** — the basis of *ANF/HyperANF* neighborhood-function estimation (Palmer et al.; Boldi–Rosa–Vigna), which estimate $|N_{\le \ell}(v)|$ in near-linear time with sketches.
- **Branching-process / generating-function** models: under a configuration/degree-sequence model, expected frontier size at depth $\ell$ follows the branching factor $\mathbb E[\text{out-deg} \mid \text{reached}]^\ell$, the analytic source of exponential blow-up.

Datalog/`WITH RECURSIVE` semantics (Abiteboul–Hull–Vianu) and **semi-naïve evaluation** define the per-iteration delta whose size is what optimizers must predict.

## 3. State of the Art (SOTA)
**Theory-SOTA:** **HyperANF** (Boldi–Rosa–Vigna, WWW 2011) and **ANF** (Palmer–Gibbons–Faloutsos, KDD 2002) estimate per-distance reachable-set sizes (and thus closure size and neighborhood function) using HyperLogLog counters in $O(m\cdot\text{diam})$ time and near-linear space — the canonical scalable estimator. For RPQs, automaton-based size estimation over product graphs.

**Systems-SOTA:** mature systems estimate recursion poorly. Postgres/most SQL engines apply a **fixed magic multiplier** per recursive iteration (often assuming a constant fan-out), a notorious source of error. Graph engines (Neo4j, TigerGraph, DuckDB-style recursive CTE, GraphX) use degree-based and sampling heuristics. **Learned/GNN-based** estimators for subgraph/path counts (e.g. NeurSC, LSS, GNN cardinality estimators for subgraph matching) are emerging in research systems.

## 4. Upper Bound
Per-distance reachable-set sizes (and total closure size) estimable to relative error $\varepsilon$ in $O(m\cdot d \cdot \varepsilon^{-2}\log\log n)$ time via HyperANF (model: HLL sketches propagated over $d$ BFS rounds). Walk/path-of-length-$\ell$ counts: exact via sparse matrix powers in $O(\ell\cdot\text{nnz})$. Sampling-based path-count estimation gives unbiased estimates with variance controlled by importance sampling over the search tree. Exact transitive-closure size: $O(n\cdot m)$ or $O(n^\omega)$ via boolean matrix multiplication.

## 5. Lower Bound
- **Exact path counting:** `#P`-complete (counting simple paths/cycles; Valiant 1979), so exact cardinality for path/RPQ queries is intractable.
- **Fine-grained:** computing transitive closure / all-pairs reachability is **equivalent to Boolean Matrix Multiplication** (combinatorially $\Omega(n^{3-o(1)})$ under the BMM hypothesis); deciding reachability-size thresholds inherits this. APSP/3SUM-style barriers apply to related path-counting subproblems.
- **From-local-statistics impossibility:** closure size depends on global connectivity; no estimator from bounded-radius local statistics can predict it within any factor on adversarial graphs (a single bridge edge changes closure size by $\Theta(n^2)$).

## 6. The Gap
**Open.** Reachable-set-*size* estimation is well-handled by sketches (HyperANF), but **general recursive-query cardinality** — paths with labels/predicates, RPQs, recursive CTEs with joins and filters inside the recursion, and *per-iteration delta sizes* — has no compact, provably-accurate estimator. The exact problem is `#P`-hard / BMM-hard; the practical problem (good estimates for plan choice) lacks both tight upper bounds beyond restricted cases and a clean hardness characterization. Closing it requires estimators that exploit graph structure (low treewidth, expander/community structure, degree distribution) with error guarantees.

## 7. Current Research (as of June 2026)
- **GNN / learned subgraph-and-path cardinality estimators** with generalization to unseen graphs and queries *(frontier — verify)*.
- **Sketch-based per-iteration estimation** integrated into semi-naïve evaluation to predict (and cap) recursion blow-up adaptively at runtime.
- **RPQ and property-graph (SQL/PGQ, GQL) cardinality estimation** as the new GQL standard drives optimizer needs *(frontier — verify)*.
- **Structure-aware bounds** (treewidth / fractional hypertree width, AGM-style bounds extended to recursive and path queries).

## 8. Future Work
- Compact synopses with provable error for labeled-path/RPQ result sizes.
- Per-iteration delta-size prediction enabling adaptive recursion with memory guarantees.
- Hardness/approximation dichotomy for recursive-query cardinality parameterized by graph and query structure.
- Robust estimators that detect and bound exponential blow-up before it happens.

## 9. Key References
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. *(Datalog, fixpoint semantics, recursion)*
- **[Foundational]** L. G. Valiant. *The Complexity of Enumeration and Reliability Problems.* SIAM J. Computing, 1979. *(#P-completeness of counting)* — [DOI](https://doi.org/10.1137/0208032)
- **[SOTA]** P. Boldi, M. Rosa, S. Vigna. *HyperANF: Approximating the Neighbourhood Function of Very Large Graphs.* WWW, 2011. — [arXiv](https://arxiv.org/abs/1011.5599) — [PDF](https://ra.ethz.ch/CDstore/www2011/proceedings/p625.pdf)
- **[SOTA]** C. Palmer, P. Gibbons, C. Faloutsos. *ANF: A Fast and Scalable Tool for Data Mining in Massive Graphs.* KDD, 2002. — [DOI](https://doi.org/10.1145/775047.775059)
- **[SOTA]** H. Q. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-case Optimal Join Algorithms.* PODS 2012 / JACM 2018. *(AGM bounds underpinning path/join size limits)* — [arXiv](https://arxiv.org/abs/1203.1952) — [DOI](https://doi.org/10.1145/3180143)
- **[Survey]** A. Bonifati, G. Fletcher, H. Voigt, N. Yakovets. *Querying Graphs.* Morgan & Claypool, 2018. *(RPQ evaluation and cardinality context)* — [DOI](https://doi.org/10.2200/S00873ED1V01Y201808DTM051) — [DBLP](https://dblp.org/rec/series/synthesis/2018Bonifati.html)

## 10. Worked Example

Take a directed graph on 5 vertices: a 3-cycle $\{a\to b\to c\to a\}$ plus a "bridge" $c\to d$ and $d\to e$. Estimate the transitive-closure size $|q(G)|=\sum_v|\text{Reach}(v)|$ (reachable pairs, excluding self).

Condensation: the SCC $\{a,b,c\}$ is one node; $d$ and $e$ are singletons. Within the SCC every vertex reaches the other two, contributing $3\times2=6$ ordered pairs. Each of $a,b,c$ also reaches $d$ and $e$: $3\times2=6$ more. Then $d$ reaches $e$: $1$ pair. Total $|q(G)|=6+6+1=13$.

**Per-iteration deltas** of semi-naïve closure on edges (length-$\ell$ reachable new pairs): $\Delta_1=$ the 5 edges; $\Delta_2$ adds length-2 reaches ($a\!\to\!c$, $b\!\to\!a$, $c\!\to\!b$, $c\!\to\!e$, ...); the recursion reaches fixpoint at $\ell=$ diameter.

Now delete the single bridge edge $c\to d$. The SCC still gives $6$ pairs, but $\{a,b,c\}$ no longer reach $d,e$, and $d\to e$ stays: $|q(G)|=6+0+1=7$. One edge changed the closure by $\Theta(n^2)$ in the worst case — concretely from $13$ to $7$ here — illustrating §5's "from-local-statistics impossibility": no bounded-radius synopsis around $a$ could have predicted this.

---
*Part of the [DBMS Research catalog](../../README.md).*
