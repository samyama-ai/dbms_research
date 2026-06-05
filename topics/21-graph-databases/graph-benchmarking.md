# Benchmarking and workload generation for graphs

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/graph-benchmarking` · **Status:** empirically-open

## 1. Problem Statement
Design **graph generators** and **query/workload generators** that (i) produce graphs with controllable, realistic structure (degree distribution, clustering, community structure, label/attribute correlations, temporal evolution) at arbitrary scale, and (ii) produce parameterizable query workloads (pattern queries, path/RPQ queries, updates, analytics) whose difficulty is *predictable and tunable*, together with **metrics** that expose true engine weaknesses (cardinality-estimation errors, intermediate-result blow-up, skew handling, path-query cost, freshness under updates) rather than rewarding narrow optimizations or memorized plans.

Variants / sub-goals:
- **Generation variant:** sample a graph matching target statistics (a constraint-satisfaction / random-graph-model problem).
- **Query-difficulty variant:** generate queries with a *target* selectivity / intermediate-blow-up profile (choke-point design).
- **Evaluation-metric variant:** define scores that are robust to overfitting and correlate with real production cost.
Status is **empirically open**: many benchmarks exist (LDBC, WatDiv, etc.), but no principled, generative theory ties graph parameters to query hardness, and engines routinely overfit.

## 2. Mathematical Foundations
Graph generation rests on random-graph models: **Erdős–Rényi** (no structure), **Barabási–Albert** preferential attachment (power-law degree), **Chung–Lu** / configuration model (target degree sequence), **stochastic block models** and **degree-corrected SBM** (communities), **Kronecker graphs** (R-MAT, used by Graph500) for self-similar structure, and **LFR** for community benchmarks. Realism is measured by matching statistics: degree distribution (often power-law with exponent $\gamma\in(2,3)$), global/local **clustering coefficient**, assortativity, and motif/graphlet frequency vectors.

Query hardness is grounded in **AGM/fractional-edge-cover** (max intermediate size), **treewidth/submodular width** (structural complexity), and selectivity estimation theory; a benchmark is *discriminating* if its queries span the spectrum of these parameters. The benchmarking-methodology side draws on the notion of **choke points** (LDBC: technical challenges each query is designed to stress), and on statistical guards against overfitting (held-out parameter draws, query-template randomization). Metrics like the **q-error** (multiplicative cardinality-estimation error, Moerkotte–Neumann–Steidl) quantify estimator quality independent of a specific plan.

## 3. State of the Art (SOTA)
- **Systems/benchmark-SOTA:** **LDBC** Social Network Benchmark (SNB — interactive + business-intelligence workloads) and **LDBC Graphalytics** (Iosup et al., VLDB 2016) for analytics; **DATAGEN/Spinner** and the newer **LDBC FinBench**; **WatDiv** (Aluç–Hartig–Özsu–Daudjee, ISWC 2014) for stress-testing RDF/SPARQL with tunable query templates; **gMark** (Bagan–Bonifati–Ciucanu–Fletcher–Lemay–Advokaat, IEEE TKDE 2017) — a schema-driven, *query-workload* generator with selectivity control for path queries; **Graph500** (R-MAT BFS) and **GraphBLAS** kernels; **SNAP** generators; **TrillionG** and **PaRMAT** for scalable R-MAT.
- **Theory-SOTA:** selectivity-aware path-query generation (gMark) and degree-constrained generation; choke-point-driven benchmark design methodology (LDBC).

## 4. Upper Bound
This is a methodology/empirical problem, so "upper bound" means *generation efficiency and controllability*: Chung–Lu / configuration-model graphs with a target degree sequence are sampled in near-linear time $O(n+m)$; R-MAT/Kronecker generate $m$ edges in $O(m\log n)$; gMark generates workloads with controlled *path-query selectivity* in time polynomial in schema and target size. Constant-selectivity path-query generation is achievable for chain-shaped RPQs; for arbitrary shapes the control becomes heuristic.

## 5. Lower Bound
- **Exact** generation hitting *multiple* target statistics simultaneously (e.g., a prescribed joint degree–clustering–community profile) is generally **NP-hard** (graph realization with clustering constraints; many joint-degree-matrix realization variants are hard).
- Predicting query hardness exactly is as hard as the underlying evaluation/counting problems (e.g., setting an exact target output size for a cyclic pattern is $\#P$-hard, since it requires knowing the count).
- No information-theoretic barrier per se, but **anti-overfitting** guarantees (a benchmark provably not gameable) face an impossibility flavor: any fixed finite workload can be overfit, so robustness requires randomized/generative families.

## 6. The Gap
The gap is **conceptual, not numeric**: there is no validated theory mapping generator parameters → *query difficulty* → *engine differentiation*. Open problems: (a) generators that jointly control degree, clustering, community, *and* label/attribute correlations at scale; (b) query generators that hit a *target* intermediate-blow-up / q-error profile rather than just output selectivity; (c) metrics provably correlated with production cost and robust to plan memorization; (d) realistic **dynamic/temporal** and **transactional** workloads. Whether a single benchmark can be both realistic and discriminating across engine classes is itself unresolved.

## 7. Current Research (as of June 2026)
LDBC continues evolving (FinBench, SNB BI refresh, and work toward a **GQL/SQL-PGQ** path-query benchmark) *(frontier — verify)*. Active groups: Bonifati (Lyon) and Fletcher (TU Eindhoven) on query-workload generation and *empirical studies of real Cypher/SPARQL query logs* (e.g., large-scale analyses of Wikidata SPARQL logs); Özsu/Daudjee (Waterloo) on RDF benchmarking; Iosup (TU Delft) on Graphalytics/LDBC. Emerging frontiers: generators conditioned on *learned* models of real graphs (deep generative graph models / diffusion) to match higher-order structure *(frontier — verify)*; benchmarks targeting **cardinality-estimation** and **adaptive reoptimization** directly; hybrid graph+vector workload benchmarks tracking the vector-graph problem *(frontier — verify)*.

## 8. Future Work
- Parameterizable generators with joint control over structural *and* attribute/label correlations.
- "Difficulty-targeted" query synthesis (specify desired q-error / blow-up / treewidth).
- Overfitting-resistant metrics and randomized template families with statistical validity.
- Standard dynamic/temporal/transactional graph benchmarks and a GQL-era path-query suite.
- Generators validated to reproduce engine performance *rankings* seen on real data.

## 9. Key References
- **[SOTA]** Bagan, Bonifati, Ciucanu, Fletcher, Lemay, Advokaat. *gMark: Schema-Driven Generation of Graphs and Queries.* IEEE TKDE, 2017. — [arXiv](https://arxiv.org/abs/1511.08386)
- **[SOTA]** Aluç, Hartig, Özsu, Daudjee. *Diversified Stress Testing of RDF Data Management Systems (WatDiv).* ISWC, 2014. — [DOI](https://doi.org/10.1007/978-3-319-11964-9_13)
- **[SOTA]** Iosup, Hegeman, Ngai et al. *LDBC Graphalytics: A Benchmark for Large-Scale Graph Analysis.* VLDB, 2016. — [DOI](https://doi.org/10.14778/3007263.3007270)
- **[SOTA]** Erling, Averbuch, Larriba-Pey, Chafi, Gubichev, Prat, Pham, Boncz. *The LDBC Social Network Benchmark: Interactive Workload.* SIGMOD, 2015. — [ACM](https://doi.org/10.1145/2723372.2742786)
- **[Foundational]** Chakrabarti, Zhan, Faloutsos. *R-MAT: A Recursive Model for Graph Mining.* SDM, 2004. — [DOI](https://doi.org/10.1137/1.9781611972740.43)
- **[Foundational]** Moerkotte, Neumann, Steidl. *Preventing Bad Plans by Bounding the Impact of Cardinality Estimation Errors (q-error).* VLDB, 2009. — [DOI](https://doi.org/10.14778/1687627.1687738)

## 10. Worked Example

Illustrate the **q-error** metric that benchmarks use to score cardinality estimation, and how it bounds plan cost. Suppose a query has a join whose *true* output cardinality is $|R \bowtie S| = 10{,}000$ tuples. The optimizer's estimate is $\hat n = 2{,}500$. The q-error is the symmetric multiplicative deviation

$$q(\hat n, n) = \max\!\left(\frac{\hat n}{n}, \frac{n}{\hat n}\right) = \max\!\left(\frac{2500}{10000}, \frac{10000}{2500}\right) = \max(0.25, 4) = 4.$$

The Moerkotte–Neumann–Steidl theorem says the chosen plan's cost is at most $q^4$ times optimal — here $4^4 = 256\times$ worse in the worst case. A 4x under-estimate can therefore make the optimizer pick a nested-loop where a hash join was right.

Why this matters for **benchmark design**: a discriminating workload should include query templates whose *intermediate* cardinalities (governed by the AGM/fractional-edge-cover bound) span a wide range, forcing estimators into high-q-error regions. A generator like gMark tunes path-query selectivity to hit, say, a target $10^4$ intermediate size; reporting per-template q-error then exposes which engine's estimator degrades — rather than rewarding one that memorized a plan for a fixed query.

---
*Part of the [DBMS Research catalog](../../README.md).*
