# Graph analytics vs. query engine unification

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/analytics-query-unification` · **Status:** empirically-open

## 1. Problem Statement
Graph workloads split into two paradigms with mismatched execution models:

- **Pattern/path queries** (subgraph matching, regular-path queries, joins) — set-oriented, output-sensitive, optimized by relational/WCOJ techniques over indexed adjacency.
- **Iterative analytics** (PageRank, connected components, shortest paths, label propagation, GNN propagation) — fixpoint computations expressed in vertex-centric / Gather-Apply-Scatter (GAS) or linear-algebra (semiring) form, dominated by sequential memory bandwidth.

The problem: design **one engine and one programming abstraction** that expresses and executes *both* classes efficiently, so that a single declarative query can mix, e.g., a path/pattern filter feeding a PageRank-style fixpoint, without paying a large overhead versus a specialized system for either side. It is **empirically open**: candidates exist but none matches best-of-breed specialized performance across both classes on standard benchmarks (LDBC SNB/Graphalytics).

## 2. Mathematical Foundations
Two unifying algebras are candidates:

- **Relational algebra + recursion (Datalog / the chase):** pattern queries are conjunctive queries; analytics are recursive Datalog with aggregation (semi-naïve evaluation, stratified/monotonic aggregation, semiring provenance). Convergence of monotone aggregate recursion rests on *pre-fixpoint* lattice theory (Knaster–Tarski) and the $\mathrm{lfp}$ operator.
- **Linear algebra over semirings (GraphBLAS):** BFS, SSSP, PageRank, components are matrix-vector products $y = A \otimes x$ over a semiring $(\oplus,\otimes)$; pattern matching becomes masked matrix multiplication. The challenge: cyclic *joins* need AGM-optimal evaluation, which plain sparse matmul does **not** achieve, so the algebra must subsume **worst-case-optimal joins** plus fixpoint iteration.

Cost models must reconcile **output-sensitive** join cost ($O(\mathrm{AGM})$) with **iteration-bound** analytics cost ($O(\#\text{iters}\cdot |E|)$).

## 3. State of the Art (SOTA)
**Theory-SOTA:** Recursive Datalog with WCOJ subroutines (e.g., **Recstep**, **DCDatalog**, and "FAQ/AggroFAQ" framework of Abo Khamis–Ngo–Rudra) provides a single semantics covering joins, aggregation, and recursion. **GraphBLAS** (Mathematical Foundations: Kepner et al.) gives a closed semiring algebra for both.

**Systems-SOTA:** Unified-leaning systems include **GraphflowDB/Kùzu** (Salihoğlu, Waterloo — WCOJ + columnar + recursive), **TigerGraph GSQL** (accumulators unify pattern + iteration), **Grasper/Gemini/GraphScope** (Alibaba — fuses Gremlin/GQL with GAS analytics), **Differential Dataflow / Timely** (incremental fixpoint), and **DuckPGQ** (property-graph queries on DuckDB). None yet dominates both the LDBC SNB (BI/interactive) and Graphalytics suites simultaneously.

## 4. Upper Bound
- Pattern side: $O(\mathrm{AGM}(H)+|\text{out}|)$ per query in RAM via WCOJ — matches specialized engines.
- Analytics side: $O(I\cdot(|V|+|E|))$ for $I$ iterations of vertex-centric PageRank/components; $\tilde O(|E|)$ for components with union-find or label-prop with $O(\mathrm{diam})$ rounds.
- A unified engine inherits both bounds *additively* in principle; the empirical question is the **constant-factor / memory-system overhead** of expressing analytics through a relational/columnar runtime versus a hand-tuned GAS kernel.

## 5. Lower Bound
No clean impossibility forbids unification; the barriers are **conditional and empirical**:
- Cyclic pattern queries inherit subgraph-isomorphism NP-hardness and AGM-tightness lower bounds.
- Iterative analytics inherit communication/round lower bounds (see *Distributed iterative analytics communication bounds*) and APSP/SETH-conditional dynamic barriers.
- Abstraction-overhead lower bounds are not formalized: there is no proven separation showing a *single* abstraction must asymptotically lose to specialized ones — making the gap genuinely empirical.

## 6. The Gap
The gap is engineering-and-cost-model, not asymptotic: a relational/columnar runtime tuned for set-oriented joins typically pays cache/branch overhead on tight vertex-centric loops, while a GAS runtime lacks AGM-optimal join machinery. Closing it requires (a) a cost model that picks per-operator physical strategies (join-style vs. matmul-style vs. GAS), and (b) a runtime whose data layout serves both. Whether one abstraction can be *provably* overhead-free for both remains open.

## 7. Current Research (as of June 2026)
GQL/SQL:2023 PGQ standardization is driving convergence onto relational engines (DuckPGQ, Umbra/PG, Kùzu). *(frontier — verify)* Active work on **factorized / FAQ-based execution** that natively expresses aggregation-over-joins and recursion (Olteanu, Schleich, Abo Khamis, Ngo). *(frontier — verify)* GraphBLAS-backed property-graph engines and "sparse-tensor compilers" (TACO/MLIR sparse, Finch) aiming to compile both pattern and analytics kernels from one IR. Differential Dataflow continues to anchor incremental unified execution.

## 8. Future Work
- A formal overhead-separation result (or proof of none) between unified and specialized engines.
- One IR (factorized/semiring) compiling to AGM-optimal joins *and* bandwidth-optimal analytics.
- Cost-based per-operator strategy selection inside GQL/SQL-PGQ optimizers.
- Standard mixed benchmark combining LDBC SNB pattern queries with Graphalytics fixpoints.

## 9. Key References
- **[Foundational]** Abiteboul, Hull, Vianu. *Foundations of Databases* (Datalog, fixpoint semantics). Addison-Wesley, 1995. — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[Foundational]** Kepner et al. *Mathematical foundations of the GraphBLAS.* IEEE HPEC, 2016. — [arXiv](https://arxiv.org/abs/1606.05790)
- **[SOTA]** Abo Khamis, Ngo, Rudra. *FAQ: Questions asked frequently.* PODS, 2016. — [arXiv](https://arxiv.org/abs/1504.04044)
- **[SOTA]** Mhedhbi, Salihoğlu et al. *GraphflowDB / Optimizing subgraph queries by combining binary and worst-case optimal joins.* PVLDB, 2019. — [arXiv](https://arxiv.org/abs/1903.02076)
- **[SOTA]** McSherry, Murray, Isaacs, Isard. *Differential dataflow.* CIDR, 2013. — [PDF](https://www.cidrdb.org/cidr2013/Papers/CIDR13_Paper111.pdf)
- **[Survey]** Sahu, Mhedhbi, Salihoğlu, Lin, Özsu. *The ubiquity of large graphs and surprising challenges of graph processing.* PVLDB, 2017. — [arXiv](https://arxiv.org/abs/1709.03188)

## 10. Worked Example

Take a 4-vertex graph with directed edges $A=\{1\!\to\!2, 2\!\to\!3, 3\!\to\!1, 3\!\to\!4\}$ and a mixed query: *"find all directed triangles, then run one PageRank step seeded on their vertices."*

**Pattern side (WCOJ/relational):** the triangle $T(a,b,c)\leftarrow E(a,b),E(b,c),E(c,a)$ has one match $\{1,2,3\}$. A binary-join plan first computes $E\bowtie E$ ($4$ two-hop paths) then filters; a worst-case-optimal plan intersects adjacency lists vertex-by-vertex, touching $O(\mathrm{AGM})=O(|E|^{3/2})=O(4^{1.5})=8$ work units — no wasted two-hop materialization.

**Analytics side (semiring/GAS):** seed $x_0=(\tfrac13,\tfrac13,\tfrac13,0)^\top$ on the triangle vertices and apply one matmul $y=A^\top \otimes x_0$ over the $(\,+,\times)$ semiring with damping $d=0.85$. Vertex $4$ receives mass $0.85\cdot\tfrac13\cdot\tfrac12 \approx 0.14$ from vertex $3$ (out-degree $2$).

The unification pain point: the WCOJ intersection wants sorted adjacency lists (random-access, set-oriented), while the PageRank step wants a contiguous CSR sweep (sequential bandwidth). A single engine must serve both layouts without a $2\times$ penalty on either — the empirically open question this problem captures.

---
*Part of the [DBMS Research catalog](../../README.md).*
