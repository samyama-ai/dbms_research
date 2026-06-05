# Subgraph counting and homomorphism complexity

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/subgraph-counting-complexity` · **Status:** partially-solved

## 1. Problem Statement
Given a small pattern graph $H$ (the *motif*) and a large host graph $G$, count occurrences of $H$ in $G$. Several distinct variants must be separated:

- **Homomorphism counting** $\hom(H,G)$: count edge-preserving maps $V(H)\to V(G)$.
- **Subgraph (embedding) counting** $\mathrm{sub}(H,G)$: count injective homomorphisms (labeled copies).
- **Induced subgraph counting** $\mathrm{ind}(H,G)$: count vertex subsets inducing a copy of $H$.

Each has *exact*, *approximate* (with relative error $\varepsilon$), and *decision* (subgraph isomorphism: does even one copy exist?) variants. The practical research goal is exact or $(1\pm\varepsilon)$-approximate counting of motifs (triangles, cliques, cycles, small dense patterns) on graphs with billions of edges, exploiting structural parameters of $H$ — treewidth, and the homomorphism basis — to beat naive enumeration.

## 2. Mathematical Foundations
Homomorphism counts form a linear basis: subgraph and induced counts are fixed integer linear combinations of homomorphism counts over the *spasm* (quotients) of $H$ (Lovász; Curticapean–Dell–Marx 2017). Thus the complexity of counting $\mathrm{sub}(H,G)$ is governed by the **maximum treewidth** appearing in this basis.

Key results:
- $\hom(H,G)$ is computable in $f(H)\cdot n^{\mathrm{tw}(H)+1}$ time (Díaz–Serna–Thilikos), where $\mathrm{tw}(H)$ is treewidth.
- **#W[1]-hardness:** counting $k$-cliques and the general parameterized clause is #W[1]-hard; under ETH no $f(k)n^{o(k/\log k)}$ algorithm exists (Chen–Thurley–Weyer, Curticapean–Marx).
- For triangles, the count relates to matrix multiplication: $\mathrm{tr}(A^3)/6$, giving $O(n^\omega)$ exact and $O(m^{2\omega/(\omega+1)})$ (Alon–Yuster–Zwick).
- The **AGM bound** $\prod$ via fractional edge cover $\rho^*(H)$ upper-bounds the number of embeddings: $|\mathrm{sub}(H,G)|\le \prod_e |G|^{x_e}$, foundational to worst-case-optimal join (WCOJ) evaluation.

## 3. State of the Art (SOTA)
**Theory-SOTA:** The Curticapean–Dell–Marx homomorphism-basis framework gives a complete dichotomy — counting $\mathrm{sub}(H,\cdot)$ is FPT iff the basis has bounded treewidth, else #W[1]-hard. Tight ETH lower bounds for cliques.

**Systems-SOTA:** WCOJ engines (LeapFrog Triejoin in LogicBlox; EmptyHeaded, Aberger et al. SIGMOD 2017; GraphFlow/Kùzu) evaluate cyclic patterns near the AGM bound. For approximate triangle/motif counting at scale, sampling estimators (DOULION; colorful triangle sampling; ESCAPE, Pinar–Seshadhri–Vishal WWW 2017 for exact 5-vertex via cut decomposition) and graphlet samplers (MOSS, PGD, Ahmed et al.) dominate.

## 4. Upper Bound
- Exact $\hom(H,G)$: $O(f(H)\cdot n^{\mathrm{tw}(H)+1})$ time, $O(n^{\mathrm{tw}(H)})$ space.
- Exact $\mathrm{sub}(H,G)$: $O(n^{\mathrm{tw}^*(H)+1})$ where $\mathrm{tw}^*$ is the max treewidth over the spasm of $H$.
- Triangle counting: $O(m^{2\omega/(\omega+1)}) = O(m^{1.41})$ (AYZ 1997).
- WCOJ join evaluation of $H$: $O(\mathrm{AGM}(H) + \text{output})$ in the RAM model.
- $(1\pm\varepsilon)$ triangle approximation: $\tilde O(m/\varepsilon^2)$ via sampling; streaming one-pass estimators in $\tilde O(m/\sqrt{T})$ space where $T$ is the triangle count (Pavan et al., McGregor et al.).

## 5. Lower Bound
- **Subgraph isomorphism (decision)** is NP-complete (generalizes clique/Hamiltonicity).
- **Counting:** #W[1]-hard parameterized by $k=|V(H)|$; under ETH, no $n^{o(k/\log k)}$ algorithm for $k$-clique counting (Curticapean–Marx 2014).
- **Fine-grained:** detecting/counting $k$-cliques in $O(n^{(\omega/3)k - \delta})$ would beat the best matrix-multiplication-based algorithm; triangle detection in $O(m^{4/3-\delta})$ is conjectured hard and ties to APSP/3SUM-style barriers. Combinatorial triangle detection in $O(m^{4/3-\delta})$ would refute popular conjectures.
- Streaming: exact triangle counting requires $\Omega(m)$ space.

## 6. The Gap
For *fixed* $H$ the parameterized picture is essentially **closed** (dichotomy with matching ETH bounds). Genuine gaps remain in: (i) the dependence on $\omega$ vs. combinatorial algorithms for clique counting; (ii) whether AGM-bound-tightness can be retained while also exploiting functional dependencies and degree skew (the "beyond worst-case" join problem); (iii) approximate induced-subgraph counting for patterns of size $\ge 6$, where no practical near-linear estimators with provable error exist at scale.

## 7. Current Research (as of June 2026)
Active directions: GPU/WCOJ hybrids and learned cardinality estimation for cyclic queries (Madelyn Olteanu/Olteanu group, Oxford; Semih Salihoğlu, Waterloo). Color-coding and "graph homomorphism convergence" estimators for streaming motif counts. *(frontier — verify)* Recent work on **counting under differential privacy** and on **degeneracy-ordered** clique counters scaling to trillion-edge graphs. The fine-grained complexity of detecting bounded-treewidth patterns "beyond AGM" using submodular width (Marx) and the PANDA algorithm (Abo Khamis–Ngo–Suciu) remains a hot interface between databases and parameterized complexity.

## 8. Future Work
- Close the $\omega$-gap for clique counting or prove a conditional lower bound.
- Practical estimators for induced 6+ vertex graphlets with rigorous variance bounds.
- Unify WCOJ, submodular-width, and FD-aware bounds into one cost model usable by query optimizers.
- Dynamic/streaming motif maintenance under edge updates with sublinear work.

## 9. Key References
- **[Foundational]** Curticapean, Dell, Marx. *Homomorphisms are a good basis for counting small subgraphs.* STOC, 2017. — [arXiv](https://arxiv.org/abs/1705.01595)
- **[Foundational]** Alon, Yuster, Zwick. *Finding and counting given length cycles.* Algorithmica, 1997. — [DOI](https://doi.org/10.1007/BF02523189)
- **[Foundational]** Atserias, Grohe, Marx. *Size bounds and query plans for relational joins (AGM bound).* FOCS 2008 / SICOMP, 2013. — [DBLP](https://dblp.org/rec/conf/focs/AtseriasGM08.html)
- **[SOTA]** Aberger, Lamb, Tu, Nötzli, Olukotun, Ré. *EmptyHeaded: A relational engine for graph processing.* ACM TODS, 2017. — [DOI](https://doi.org/10.1145/3129246)
- **[SOTA]** Pinar, Seshadhri, Vishal. *ESCAPE: Counting all 5-vertex subgraphs.* WWW, 2017. — [arXiv](https://arxiv.org/abs/1610.09411)
- **[Survey]** Ngo, Re, Rudra. *Skew strikes back: New developments in the theory of join algorithms.* SIGMOD Record, 2013. — [DOI](https://doi.org/10.1145/2590989.2590991)

## 10. Worked Example

Count triangles via the trace formula on a tiny graph. Let $G=K_4$ minus one edge: vertices $\{1,2,3,4\}$ with all edges except $(3,4)$. Adjacency matrix

$$A=\begin{pmatrix}0&1&1&1\\1&0&1&1\\1&1&0&0\\1&1&0&0\end{pmatrix}.$$

The number of (labeled, ordered) closed 3-walks is $\mathrm{tr}(A^3)$, and each triangle is counted $3!=6$ times, so $\\#\triangle = \mathrm{tr}(A^3)/6$.

Compute $\mathrm{tr}(A^3)=\sum_i (A^3)_{ii}$. By hand, $(A^2)_{ii}=\deg(i)$, giving diagonal $(3,3,2,2)$. The diagonal of $A^3$ equals twice the number of triangles through each vertex: vertex 1 is in triangles $\{1,2,3\},\{1,2,4\}$ (degree-2 in the triangle-incidence sense), similarly vertex 2; vertices 3 and 4 are each in one triangle. So $(A^3)_{ii}=(4,4,2,2)$, $\mathrm{tr}(A^3)=12$, and $\\#\triangle = 12/6 = 2$ — namely $\{1,2,3\}$ and $\{1,2,4\}$. Correct.

Complexity check: this costs one matrix product, $O(n^\omega)$ with fast multiplication, illustrating the $\mathrm{tr}(A^3)/6$ route that beats the naive $\binom{n}{3}$ enumeration for triangle counting.

---
*Part of the [DBMS Research catalog](../../README.md).*
