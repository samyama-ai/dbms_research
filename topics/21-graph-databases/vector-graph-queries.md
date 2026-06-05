# Vector-augmented graph query processing

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/vector-graph-queries` · **Status:** empirically-open

## 1. Problem Statement
Process queries that mix **structural graph patterns / path navigation** with **approximate-nearest-neighbor (ANN) similarity predicates** over high-dimensional vector attributes attached to vertices or edges (e.g., embeddings). A typical query: "find vertices $v$ matching pattern $H$ such that $v.\mathrm{emb}$ is among the top-$k$ closest to a query vector $q$, where matched neighbors also satisfy a similarity threshold." The goal is a **joint** evaluation strategy — a unified cost model, indexing, and plan space — that decides when to drive evaluation from the structural side (graph traversal first, then filter by similarity) versus the vector side (ANN search first, then verify structure), or to interleave them, while respecting recall guarantees on the ANN portion.

Variants:
- **Top-$k$ variant:** rank matches by a (possibly path-aggregated) distance score.
- **Threshold/range variant:** all matches with similarity $\ge \tau$.
- **Predicate-pushdown / filtered-ANN variant:** ANN search constrained by structural/attribute predicates (the "filtered vector search" problem) embedded in a larger pattern.
Status is **empirically open**: systems exist (hybrid vector+graph engines), but there is no agreed cost model, no optimality theory, and no benchmark consensus.

## 2. Mathematical Foundations
ANN rests on **proximity graphs** — HNSW (Malkov–Yashunin, TPAMI 2020) and the navigating-spreading-out-graph / DiskANN (Vamana) family — which give *empirical* $O(\log n)$-ish greedy-search behavior but **no worst-case recall guarantee**; and on **LSH** (Indyk–Motwani 1998; Andoni–Indyk data-dependent hashing), which gives provable $(c,r)$-approximate guarantees with query time $O(n^{\rho})$, $\rho<1$. The structural side rests on conjunctive-query/AGM theory (see WCOJ page). The crux is a **joint cost/selectivity model**: estimating the size of $\{v: H\text{-match}\} \cap \{v: \mathrm{ANN}_k(q)\}$ — the correlation between graph-structural selectivity and vector-distance selectivity is generally unknown and non-independent.

Formally one wants a cost function $C(\text{plan}) = C_{\text{struct}} + C_{\text{ANN}} + C_{\text{glue}}$ minimized over plans, with the ANN component parameterized by a recall target $R$; because ANN error compounds with structural joins, the end-to-end answer is an **approximate** answer set whose recall must itself be bounded — an open modeling question (no clean composition of per-operator recall into query-level recall).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** vector-capable graph/relational DBs — **Neo4j** (vector index, 2023+), **TigerGraph**, **Kùzu** (vector + WCOJ), **Weaviate** and **Milvus** (vector-first with metadata/graph-ish filtering), **pgvector**/**Lantern** in Postgres, and OLAP engines adding ANN. Filtered-ANN systems: **Filtered-DiskANN** (Microsoft, 2023), **ACORN** (Stanford, SIGMOD 2024) for predicate-agnostic filtered HNSW, **SeRF/iRangeGraph** for range-filtered ANN.
- **Theory-SOTA:** approximate top-$k$ with predicate constraints is studied as *filtered/attribute-constrained ANN*; provable guarantees remain limited to range/single-predicate filters. No published WCO-style theory for joint pattern + ANN.
- GNN/embedding-driven query answering (CLQA — complex logical query answering over embeddings, e.g., Query2Box, GQE) is a parallel approximate line that answers structural queries *in embedding space*.

## 4. Upper Bound
- ANN subproblem: LSH gives query time $n^{\rho(c)} + $ output, $\rho \approx 1/c^2$ for Euclidean (Andoni–Indyk), with provable approximation $c$; HNSW/DiskANN give strong empirical recall at $O(\log n)$ hops but **no proven worst-case bound**.
- Structural subproblem: $\tilde{O}(\mathrm{AGM})$ via WCOJ.
- Joint: best known are *heuristic* plans; "ANN-first then verify" costs $O(\text{ANN}(k') + k'\cdot \text{verify})$ for an enlarged candidate set $k'$ chosen to hit recall $R$ — but $k'$ depends on the unknown correlation, so the bound is data-dependent and unproven in general.

## 5. Lower Bound
- Exact NN in high dimensions suffers the **curse of dimensionality**: under SETH, no algorithm solves exact NN (or even $c$-approximate for $c$ close to 1) in truly sublinear time with subquadratic space for general metrics (Rubinstein STOC 2018; Williams; Alman–Williams) — the *approximate near-neighbor* fine-grained barrier.
- The structural side inherits AGM/BMM/3SUM conditional lower bounds (see WCOJ page).
- Composition: deciding whether a pattern match with a similarity threshold exists is at least as hard as the harder of the two subproblems; no separation/lower bound is known for the *joint optimization* itself — this is part of why the problem is "empirically open."

## 6. The Gap
The gap is not a clean upper-vs-lower number but a **structural one**: (a) no validated **joint cost/selectivity model** correlating structural and vector selectivity; (b) no **recall-composition theory** (how per-operator ANN recall propagates through joins/paths); (c) no agreed **index** that serves both navigational and similarity access efficiently; (d) plan-space and optimality are uncharted. Closing it requires both a theory of approximate-answer quality for compound queries and engineering of hybrid indexes/optimizers.

## 7. Current Research (as of June 2026)
Hot area driven by **RAG / GraphRAG**: retrieval that walks knowledge-graph structure and ranks by embedding similarity. Active directions: filtered-ANN with arbitrary predicates pushed into HNSW (ACORN line, Stanford; Microsoft DiskANN team) *(frontier — verify)*; cost-based optimizers that treat ANN as a first-class operator with a recall knob inside graph engines (Kùzu, LanceDB, Weaviate) *(frontier — verify)*; learned joint cardinality estimators for "structure ∩ similarity" selectivity *(frontier — verify)*; CLQA/neural query answering scaling to larger KGs (Ren, Leskovec at Stanford; Galkin). GQL/SQL-PGQ vendors adding vector predicates is pushing standardization of the operator semantics *(frontier — verify)*.

## 8. Future Work
- A composable recall/error model for ANN operators embedded in joins and paths.
- Unified indexes (proximity graph that also encodes navigational adjacency / labels).
- Cost-based optimizers choosing struct-first vs ANN-first vs interleaved, with provable competitive guarantees.
- Standard benchmarks for hybrid graph+vector workloads (overlaps with the benchmarking problem page).
- Worst-case-optimal-style guarantees for joint pattern + similarity queries.

## 9. Key References
- **[Foundational]** Malkov, Yashunin. *Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs (HNSW).* IEEE TPAMI, 2020. — [DOI](https://doi.org/10.1109/TPAMI.2018.2889473)
- **[Foundational]** Indyk, Motwani. *Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality.* STOC, 1998. — [DBLP](https://dblp.org/rec/conf/stoc/IndykM98.html)
- **[SOTA]** Subramanya, Devvrit, Kadekodi, Krishaswamy, Simhadri. *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node.* NeurIPS, 2019. — [NeurIPS](https://proceedings.neurips.cc/paper/2019/hash/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Abstract.html)
- **[SOTA]** Patel, Kraft, Guestrin, Zaharia. *ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data.* SIGMOD, 2024. — [DOI](https://doi.org/10.1145/3654923)
- **[SOTA]** Ren, Hu, Leskovec. *Query2box: Reasoning over Knowledge Graphs in Vector Space Using Box Embeddings.* ICLR, 2020. — [arXiv](https://arxiv.org/abs/2002.05969)
- **[Lower bound]** Rubinstein. *Hardness of Approximate Nearest Neighbor Search.* STOC, 2018. — [DOI](https://doi.org/10.1145/3188745.3188916)

## 10. Worked Example

Struct-first vs. ANN-first plan choice. Query: "find users $v$ who *follow* the account $h$ AND whose profile embedding is in the top-$k{=}5$ closest to query vector $q$."

Suppose the graph has $n=10^6$ users. The structural predicate "follows $h$" matches $|S|=200$ users. The vector index (HNSW) answers a top-$k'$ ANN query in $\approx c\log n \approx 20\,k'$ distance evaluations.

**Plan A (struct-first):** fetch the 200 followers, compute $\|v.\mathrm{emb}-q\|$ for each, keep top-5. Cost $\approx 200$ distance evals — cheap, exact recall.

**Plan B (ANN-first):** ask HNSW for top-$k'$ globally, then filter to followers of $h$. Because only $200/10^6 = 0.02\%$ of users follow $h$, to expect 5 survivors after filtering we need $k' \approx 5/0.0002 = 25{,}000$ candidates — cost $\approx 20 \cdot 25{,}000 = 5{\times}10^5$ evals, and *no* recall guarantee (HNSW may miss followers ranked just outside $k'$).

Here struct-first wins by $2500\times$. But flip the selectivity — if "follows $h$" matched $400{,}000$ users — struct-first costs $400{,}000$ evals while ANN-first needs only $k'\approx 13$, so ANN-first wins. The crux (Section 6): the optimal choice depends on the *joint* selectivity $|\,\{v:\text{follows }h\}\cap \mathrm{ANN}_k(q)\,|$, which no current cost model reliably estimates.

---
*Part of the [DBMS Research catalog](../../README.md).*
