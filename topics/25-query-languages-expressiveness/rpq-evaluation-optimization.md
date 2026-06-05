# Regular Path Query Evaluation and Optimization

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/rpq-evaluation-optimization` · **Status:** empirically-open

## 1. Problem Statement
A **regular path query (RPQ)** over an edge-labeled graph $G=(V,E)$ with $E \subseteq V \times \Sigma \times V$ returns pairs $(s,t)$ connected by a path whose label word lies in a regular language $L$: $\mathsf{RPQ}_L(G) = \{(s,t) : s \xrightarrow{w} t,\ w \in L\}$. Extensions: **two-way** RPQs (2RPQ, allow inverse edges), **conjunctive** RPQs (**CRPQ**, joins of RPQs with shared variables), and **UCRPQ**. Semantics variants: **arbitrary paths**, **simple paths**, **trails**, and **shortest paths** (the GQL/SQL-PGQ path modes).

The problem has a decision/enumeration core (compute the answer set) and an **optimization** core: produce an evaluation **plan** (automaton-guided traversal, join ordering, source/target pruning) minimizing time/IO **with provable guarantees** at scale (billions of edges). It is **empirically open**: theory is well understood for arbitrary-path semantics, but no system delivers worst-case-optimal, robust evaluation across path modes and skewed real graphs.

## 2. Mathematical Foundations
Arbitrary-path RPQ evaluation = reachability in the **product graph** $G \times A$, where $A$ is an NFA for $L$. A pair $(s,t)$ is in the answer iff $(t, q_f)$ is reachable from $(s, q_0)$ in $G \times A$, giving $O(|G|\cdot|A|)$ per source. Single-source = BFS in the product; all-pairs uses transitive closure or **algebraic** ($\alpha$-semiring / matrix) formulations, linking to Boolean matrix multiplication and the **Context-Free Path Querying** generalization.

CRPQ evaluation joins multiple RPQ relations; combined complexity is **NP-hard** (it subsumes CQ evaluation), and **worst-case optimal join (WCOJ)** theory (AGM bound, Ngo–Porat–Ré–Rudra) applies to the conjunctive structure. **Simple-path / trail** semantics change the picture drastically: deciding existence of a simple path with a given regular label is **NP-complete** for some fixed languages (Mendelzon–Wood 1995).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** arbitrary-path RPQ in $O(|G|\cdot|A|)$ (Mendelzon–Wood 1989); CRPQ combined complexity NP-complete; fine-grained results tie all-pairs RPQ to BMM/OMv.
- **Systems-SOTA:** automaton-product BFS with **frontier** strategies; bidirectional/landmark pruning; multi-source batching. Engines: **Neo4j** (Cypher variable-length / `*` paths), **MillenniumDB** (path-aware), **RedisGraph/FalkorDB** (GraphBLAS matrix algebra), **Kùzu**, **TigerGraph**, and research systems for WCOJ graph patterns (**EmptyHeaded**, **GraphflowDB**). RDF stores (Virtuoso, Stardog, GraphDB) implement SPARQL **property paths**.
- The **SQL/PGQ** and **GQL** ISO standards (2023–2024) fix RPQ-style path patterns, spurring conforming engines.

## 4. Upper Bound
- Arbitrary-path RPQ single-pair / single-source: $O(|E|\cdot|A|)$ time, linear space, via product-graph BFS.
- All-pairs RPQ: reducible to transitive closure / BMM, hence $O(n^{\omega})$-style bounds in the algebraic model; GraphBLAS implementations exploit this.
- CRPQ: WCOJ algorithms (Generic Join, Leapfrog Triejoin) achieve **AGM-bound** runtime $O(\mathrm{AGM}(Q))$ for the conjunctive skeleton; combined with automaton products for the path atoms.

## 5. Lower Bound
- **Simple-path RPQ** is **NP-complete** for fixed regular languages (Mendelzon–Wood 1995); trail semantics similarly hard.
- All-pairs/Boolean RPQ inherits **OMv- and BMM-conditional** lower bounds: no truly subcubic combinatorial all-pairs reachability under regular constraints unless BMM conjecture fails.
- CRPQ evaluation is **NP-hard in combined complexity** (CQ subsumption); query containment is **PSPACE/EXPSPACE-complete** (see recursive-query-containment), bounding what optimizers can statically decide.

## 6. The Gap
Theory gives tight bounds for arbitrary-path semantics, but **practice lags**: (i) no evaluator is simultaneously WCOJ-optimal for CRPQs *and* efficient for the GQL **trail/shortest/simple** modes; (ii) cardinality estimation for path patterns is poor, so plans are fragile on skewed graphs; (iii) provable IO/parallel guarantees for billion-edge external-memory/distributed RPQ are missing. This is why the page is **empirically-open**: closing it means evaluators with *provable* guarantees matching the algebraic lower bounds across all standardized path modes.

## 7. Current Research (as of June 2026)
Hot directions: **WCOJ + automaton** integration for UCRPQ; **GraphBLAS / linear-algebraic** RPQ at scale; **path-index** and **2-hop/landmark labeling** for reachability under regular constraints; **factorized** and **rank-aware** enumeration with delay guarantees; and robust **cardinality estimation** for path patterns. *(frontier — verify)* GQL-conformant engines (Neo4j, MillenniumDB, Kùzu) are publishing benchmarks on trail-semantics evaluation, and there is active work on **(C)RPQ enumeration with constant delay** and on context-free path querying. Groups: Vrgoč/MillenniumDB, Salihoglu/Kùzu, Bonifati, Martens, Vansummeren, Reutter, Hogan.

## 8. Future Work
- Evaluators with provable guarantees for **all** GQL path modes (trail, simple, shortest).
- Learned and worst-case-robust **cardinality estimation** for path patterns.
- External-memory / distributed RPQ with IO and communication lower-bound-matching plans.
- Constant-delay enumeration and **factorized** outputs for UCRPQ; incremental/streaming RPQ maintenance.

## 9. Key References
- **[Foundational]** A. Mendelzon, P. Wood. *Finding regular simple paths in graph databases.* SIAM J. Computing, 1995.
- **[Foundational]** H. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-case optimal join algorithms.* JACM, 2018.
- **[SOTA]** A. Bonifati, G. Fletcher, H. Voigt, N. Yakovets. *Querying Graphs.* Morgan & Claypool (Synthesis Lectures), 2018.
- **[SOTA]** D. Vrgoč et al. *MillenniumDB: An open-source graph database system.* Data Intelligence / SIGMOD demos, 2023.
- **[Survey]** R. Angles, M. Arenas, P. Barceló, A. Hogan, J. Reutter, D. Vrgoč. *Foundations of modern query languages for graph databases.* ACM Computing Surveys, 2017.
- **[SOTA]** N. Francis et al. *GQL and SQL/PGQ: The ISO standards for property graph querying.* SIGMOD, 2023.

---
*Part of the [DBMS Research catalog](../../README.md).*
