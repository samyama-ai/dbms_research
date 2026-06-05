# Instance-optimal ANN index selection

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/instance-optimal-ann` · **Status:** open

## 1. Problem Statement
The space of ANN index *configurations* is enormous: graph family (HNSW, NSG, Vamana, NN-Descent), out-degree $R$, build beam width, search beam $L$, quantization scheme (none/SQ/PQ/OPQ/RaBitQ) and bit-rate, partitioning (IVF lists, SPANN clusters), and re-rank depth. Given a concrete dataset $P$ and a query distribution $\mathcal{Q}$, **does there exist a single index (or a learnable selector) that provably matches — up to a constant factor — the best configuration in hindsight** on the cost/recall objective?

- **(Optimization)** Build an index $I$ minimizing expected query cost subject to recall $\ge\rho$ over $\mathcal{Q}$, competitive against the offline-optimal configuration $\text{OPT}(P,\mathcal{Q})$.
- **(Decision)** Given budget $b$ (build time/space), is recall $\rho$ at per-query cost $t$ achievable for $(P,\mathcal{Q})$?
- **(Meta-learning)** Learn a mapping (dataset, query stats) $\to$ configuration with regret guarantees vs. per-instance optimal.

"Instance-optimal" is in the sense of Fagin et al. and Afshani–Barbay–Chan: optimal not in the worst case but on *every* input up to a constant.

## 2. Mathematical Foundations
Instance optimality formalizes "as good as the best algorithm on this very input." For comparison-based geometric problems, **Afshani–Barbay–Chan** built instance-optimal algorithms (e.g., for convex hulls/maxima) using the *structural entropy* of the input. ANN lacks such a theory because the cost of a graph index on $(P,\mathcal{Q})$ depends on the intrinsic dimension and clusterability of $P$, captured by quantities like the **doubling dimension** $\dim_d(P)$, the **local intrinsic dimension** (LID), and the **expansion/spread**. The achievable recall–cost frontier is governed by these data-dependent parameters; e.g., navigable-graph search cost scales with doubling dimension, and quantization distortion with the spectrum of $P$.

The selection problem is also a **hyperparameter optimization / algorithm-configuration** problem (Kleinberg–Leyton-Brown–Lucier, Gupta–Roughgarden's data-driven algorithm design), where one bounds the **pseudo-dimension** of the configuration class to get sample-complexity (generalization) guarantees: how many sample datasets/queries suffice to pick a near-optimal config for the distribution.

## 3. State of the Art (SOTA)
**Systems-SOTA.** Auto-tuners are practical but heuristic: FAISS auto-tuning, Milvus AutoIndex, and **AutoFAISS** pick IVF/PQ params from heuristics. The **ANN-Benchmarks** (Aumüller–Bernhardsson–Faithfull) and **BigANN** competition (NeurIPS) frameworks empirically map config $\to$ recall/QPS Pareto fronts, and learned cost models (e.g., for HNSW $L$ vs. recall) predict where a config lands. **VBASE** and recent query optimizers in vector DBs choose between brute-force, IVF, and graph paths per query. None come with instance-optimality guarantees.

**Theory-SOTA.** Data-driven algorithm design (Balcan and collaborators) gives generalization bounds for tuning over a parameterized algorithm family, the closest formal handle — but it has not been instantiated for the full ANN configuration space with a competitive guarantee against per-instance optimal.

## 4. Upper Bound
No instance-optimal ANN index is known. The strongest positive results are **distribution-dependent**: data-dependent LSH (Andoni–Razenshteyn) achieves the optimal exponent $\rho=1/(2c^2-1)$, beating data-oblivious LSH, i.e. it adapts to the data's near-neighbor structure — a partial form of adaptivity but not full instance optimality across the whole config space. Data-driven configuration (Gupta–Roughgarden / Balcan) gives a *learnable selector* with sample complexity $\tilde O(\text{pdim}/\epsilon^2)$ that is near-optimal *in expectation over the distribution*, not pointwise-instance-optimal, and only when the cost function's pseudo-dimension is bounded.

## 5. Lower Bound
Lower bounds are largely **negative/structural**. (i) ANN cell-probe and LSH lower bounds (Andoni–Razenshteyn; O'Donnell–Wu–Zhou) cap what *any* configuration can do in the worst case, so no index beats these — but they say nothing about per-instance gaps. (ii) Algorithm-configuration impossibility: when the cost-vs-parameter function class has unbounded pseudo-dimension or is discontinuous (graph-build is highly discontinuous in $R$), no learner can be sample-efficient — Balcan et al. show pathological families where no generalization is possible. (iii) Selecting the offline-optimal configuration exactly is at least as hard as the underlying combinatorial build (NP-hard graph constructions), so any tractable selector must be approximate.

## 6. The Gap
Wide and genuinely open. We lack even the *right definition*: instance optimality requires a notion of the input's "difficulty" (analogous to structural entropy) for ANN — likely some combination of LID, doubling dimension, and query-distribution alignment — and a single algorithm provably $O(1)$-competitive against the best config given that difficulty. Today we have empirical Pareto fronts and distribution-level learning bounds, but no pointwise guarantee, no canonical difficulty measure, and discontinuity of graph-build cost obstructs the data-driven-design machinery. Closing it needs (a) a difficulty parameterization, (b) a self-tuning index achieving the frontier as a function of it, (c) matching lower bounds.

## 7. Current Research (as of June 2026)
Active: (i) learned cost/recall models per index family feeding query-level planners (vector-DB query optimizers — VBASE, AnalyticDB-V, and academic systems); (ii) data-driven algorithm-design applied to ANN tuning *(frontier — verify)*; (iii) intrinsic-dimension estimators (LID, Two-NN of Facco et al.) as predictive features; (iv) auto-config in BigANN-benchmarks and FAISS. People/groups: Maria-Florina Balcan (data-driven design theory), Andoni–Razenshteyn (data-dependent hashing), the ANN-Benchmarks/BigANN organizers (Aumüller, Simhadri), and vector-DB query-optimizer teams. *(frontier — verify)* A few 2025 papers claim per-query index routing with learned selectors approaching the per-query oracle on standard benchmarks.

## 8. Future Work
- Define an input-difficulty measure for ANN and prove instance-optimality relative to it.
- Self-tuning indices that smoothly interpolate graph/quantization regimes (avoiding build discontinuities).
- Sample-complexity bounds for the full ANN config class via bounded pseudo-dimension.
- Per-query (not just per-dataset) routing with regret guarantees.

## 9. Key References
- **[Foundational]** R. Fagin, A. Lotem, M. Naor. *Optimal Aggregation Algorithms for Middleware.* JCSS, 2003.
- **[Foundational]** P. Afshani, J. Barbay, T. M. Chan. *Instance-Optimal Geometric Algorithms.* FOCS, 2009 / JACM, 2017.
- **[Foundational]** R. Gupta, T. Roughgarden. *A PAC Approach to Application-Specific Algorithm Selection.* SIAM J. Computing, 2017.
- **[SOTA]** A. Andoni, I. Razenshteyn. *Optimal Data-Dependent Hashing for Approximate Near Neighbors.* STOC, 2015.
- **[SOTA]** M.-F. Balcan, T. Dick, T. Sandholm, E. Vitercik. *Learning to Branch / Data-Driven Algorithm Design.* (various) ICML/JACM, 2018–2021.
- **[Survey]** M. Aumüller, E. Bernhardsson, A. Faithfull. *ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms.* Information Systems, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
