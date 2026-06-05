# Optimal hybrid binary/WCOJ plans

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/hybrid-binary-wcoj-optimization` · **Status:** open

## 1. Problem Statement

Given a conjunctive query $Q$, an engine has at least three evaluation paradigms: classical **binary (two-way) join trees** (great for acyclic/low-width subqueries, decades of tuning), **worst-case-optimal joins** (Generic Join / LFTJ / Free Join — necessary for dense cyclic subqueries), and **tree/hypertree decompositions** (Yannakakis on a GHD with fractional/submodular width). The *optimal* plan is almost always a **hybrid**: decompose $Q$ into bags, run WCOJ inside dense bags, binary-join across an acyclic skeleton, materializing some intermediate results and pipelining others.

The problem: **given $Q$, statistics on $D$, and a cost model, choose the decomposition, the per-bag algorithm (binary vs. WCOJ), the global variable/join order, and the materialize-vs-pipeline boundaries so as to minimize true (constant-factor-real) running time** — provably or near-optimally. This is the *query optimization* problem for the modern join-algorithm zoo. It is **open** even in restricted forms: there is no cost model that correctly ranks WCOJ vs. binary plans across real instances, and the search space (decompositions × orders × algorithm choices) is enormous.

## 2. Mathematical Foundations

Two width parameters bound achievable cost. The **fractional hypertree width** gives $\tilde O(N^{\mathrm{fhw}(Q)}+\mathrm{OUT})$ via a single GHD + Yannakakis. The **submodular width** $\mathrm{subw}(Q)\le\mathrm{fhw}(Q)$ is achieved by *adaptively* partitioning the instance and using different decompositions per part (PANDA / InsideOut). A plan is a triple $(\mathcal{T}, \sigma, \alpha)$: a tree decomposition $\mathcal T$ of the query hypergraph, a global attribute order $\sigma$, and a per-bag algorithm choice $\alpha$. Cost is
$$\mathrm{cost}(Q,D)=\sum_{b\in\mathcal T}\mathrm{cost}_{\alpha(b)}(b,D)+\sum_{\text{edges}}\mathrm{cost}_{\bowtie}(\text{join of bag results}),$$
where each bag's cost is AGM-bounded if $\alpha(b)=$ WCOJ and product-of-cardinalities-bounded if binary. The optimizer must estimate intermediate sizes (which, for cyclic bags, means estimating AGM/entropic bounds, not just two-way join cardinalities).

## 3. State of the Art (SOTA)

**Theory-SOTA:** InsideOut / PANDA (Abo Khamis–Ngo–Suciu) give the asymptotically best width ($\mathrm{subw}$) but are not cost-based optimizers. **Systems-SOTA:** EmptyHeaded's GHD optimizer picks decompositions then runs WCOJ per bag; **Free Join** (SIGMOD 2023) makes the binary/WCOJ choice *continuous* via trie schedules, reducing the discrete choice to scheduling — but still relies on heuristics for the schedule. Umbra/DuckDB and graph systems (Kùzu, Graphflow) implement cost-based switching with hand-tuned heuristics. **Adopt** (and successors) explored adaptive plan selection. No system or theory gives a *provably near-optimal* hybrid plan under a realistic cost model.

## 4. Upper Bound

Best known *algorithmic* guarantee: $\tilde O(N^{\mathrm{subw}(Q)}+\mathrm{OUT})$ for full CQ evaluation (PANDA + Yannakakis), RAM model — a guarantee on the *best* hybrid plan's runtime, not on the optimizer's ability to find it cheaply. For the *optimization* problem itself, no polynomial-time algorithm with a constant-factor approximation to the optimal hybrid plan's true cost is known; current optimizers are heuristic with no worst-case ratio. Free Join shows the *space* of plans contains one that is never worse than the best binary plan and never worse than the WCOJ plan, but finding it optimally is the open part.

## 5. Lower Bound

Computing $\mathrm{fhw}(Q)$ and related width parameters is **NP-hard** (Fischl–Gottlob–Pichler for checking $\mathrm{fhw}\le k$ in general; tractable for fixed small $k$ via GHD-checking, which is itself NP-hard for general queries). General join-order optimization (the discrete search) is NP-hard (Ibaraki–Kameda style results for cyclic queries). Thus the *plan-search* problem inherits NP-hardness from width computation and join ordering. There is no fine-grained lower bound separating hybrid-plan quality from binary-plan quality on real instances — precisely the missing piece.

## 6. The Gap

The gap is **wide and genuinely open**. We have (i) asymptotically optimal evaluation given the right plan, and (ii) heuristic optimizers, but no bridge: no cost model proven to rank WCOJ vs. binary correctly, no approximation algorithm for the hybrid-plan search, and weak cardinality estimation for cyclic bags (estimating AGM/entropic intermediate sizes is itself unsolved). Closing it needs both a *predictive* cost model (constants, not just exponents) and a *tractable* search with quality guarantees.

## 7. Current Research (as of June 2026)

Directions: (1) **continuous-relaxation optimizers** built on Free Join trie schedules, searched with cost models; (2) **learned cost models / learned optimizers** that predict WCOJ vs. binary crossover from features; (3) **decomposition-aware cardinality estimation** producing AGM/degree-aware intermediate bounds usable by the optimizer; (4) **adaptive runtime switching** that defers the binary/WCOJ choice to execution based on observed intermediate sizes. Groups: Suciu/Willsey (UW), Ngo/Abo Khamis (RelationalAI), Salihoglu (Waterloo/Kùzu), Gottlob/Pichler (TU Wien — width theory), Olteanu (Zurich). *(frontier — verify)* 2025–2026 prototypes report learned or hybrid cost models choosing WCOJ on cyclic subqueries within a vectorized engine, but none with proven optimality.

## 8. Future Work

- A cost model with *calibrated constants* that correctly predicts the WCOJ/binary/decomposition crossover on real data.
- A polynomial-time approximation (or strong heuristic with guarantees) for the hybrid-plan search.
- Cardinality estimation for cyclic bags (AGM/entropic/degree-aware intermediates).
- Runtime-adaptive hybrid execution that provably never regresses below the chosen static plan.
- Extending the choice to include aggregation pushdown (FAQ) and semiring evaluation.

## 9. Key References

- **[Foundational]** Abo Khamis, Ngo, Rudra. *FAQ: Questions Asked Frequently.* PODS 2016 (InsideOut, decomposition-driven evaluation). — [arXiv](https://arxiv.org/abs/1504.04044)
- **[Foundational]** Marx. *Tractable Hypergraph Properties for CSP and Conjunctive Queries.* JACM, 2013 (submodular width). — [DOI](https://doi.org/10.1145/2535926)
- **[SOTA]** Aberger, Tu, Olukotun, Ré. *EmptyHeaded: A Relational Engine for Graph Processing.* ACM TODS, 2017 (GHD optimizer + WCOJ). — [DOI](https://doi.org/10.1145/3129246)
- **[SOTA]** Wang, Willsey, Suciu. *Free Join: Unifying Worst-Case Optimal and Traditional Joins.* SIGMOD 2023. — [arXiv](https://arxiv.org/abs/2301.10841)
- **[Foundational]** Fischl, Gottlob, Pichler. *General and Fractional Hypertree Decompositions: Hard and Easy Cases.* PODS 2018 / JACM 2021. — [arXiv](https://arxiv.org/abs/1611.01090)
- **[Survey]** Gottlob, Greco, Leone, Scarcello. *Hypertree Decompositions: Questions and Answers.* PODS 2016. — [DOI](https://doi.org/10.1145/2902251.2902309)

## 10. Worked Example

Take the "triangle-plus-tail" query
$$Q = R(a,b)\bowtie S(b,c)\bowtie T(a,c)\bowtie U(c,d)$$
with $|R|=|S|=|T|=N$ and $|U|=N$. The hypergraph has a **cyclic** core $\{R,S,T\}$ (a triangle) and an **acyclic tail** $U(c,d)$ hanging off attribute $c$.

A pure binary plan can blow up: $R\bowtie S$ alone can produce $\Theta(N^2)$ tuples (e.g., a star-shaped instance), so any join order through the triangle risks an $N^2$ intermediate even though the final triangle count is only $\Theta(N^{3/2})$ (the AGM bound, edge cover $1.5$).

The optimal **hybrid** plan decomposes $Q$ into two bags: bag $\{a,b,c\}$ holding the triangle, bag $\{c,d\}$ holding $U$. Inside the triangle bag, run a WCOJ (Generic Join) in $\tilde O(N^{3/2})$, never materializing the $N^2$ pair-join. Then **binary-join** the triangle result with $U$ along the shared attribute $c$ — an acyclic Yannakakis step. Total: $\tilde O(N^{3/2}+\mathrm{OUT})$ versus the binary plan's $\Theta(N^2)$. The open problem is getting a cost model to *predict* this crossover from statistics rather than hard-coding it.

---
*Part of the [DBMS Research catalog](../../README.md).*
