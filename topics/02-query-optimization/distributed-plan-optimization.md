---
id: 02-query-optimization/distributed-plan-optimization
title: "Distributed and cloud-aware plan optimization"
topic: 02-query-optimization
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Distributed and cloud-aware plan optimization

> **Topic:** Query Optimization · **ID:** `02-query-optimization/distributed-plan-optimization` · **Status:** open

## 1. Problem Statement

Given a query $Q$ over relations partitioned across $m$ compute nodes (and, in the cloud, over a *disaggregated* storage layer), produce an execution plan that minimizes end-to-end cost, where cost includes not only local CPU/IO but **network transfer**, **shuffle (repartition) volume**, **data-placement / co-location** effects, and **storage-access latency and \$-cost** to remote object stores. A plan must specify, for each operator: the physical algorithm, the *partitioning scheme* of its output (hash, range, broadcast, replicated), the *placement* (which nodes execute it), and the parallelism degree.

- **Decision variant:** does a plan with total cost $\le B$ exist (under a fixed cost model and resource budget)?
- **Optimization variant:** find the minimum-cost plan; in the cloud, "cost" is multi-objective (latency vs. dollar spend vs. provisioned resources).
- **Counting/enumeration variant:** enumerate Pareto-optimal plans over the (latency, \$) trade-off frontier.

"Solving" means choosing join order, partitioning, and placement *jointly* — the interactions are what make the problem hard.

## 2. Mathematical Foundations

Model the plan space as the set of operator trees (or DAGs, with shared subexpressions) over $Q$'s relations. Add a **distribution annotation** $\delta(o) \in \{\textsf{hash}(A), \textsf{range}(A), \textsf{broadcast}, \textsf{replicated}, \textsf{single}\}$ to every operator output. A join $R \bowtie_A S$ is *local* (no shuffle) iff $\delta(R)$ and $\delta(S)$ agree on the join key; otherwise one or both inputs must be **redistributed**, contributing a shuffle cost $\approx \frac{m-1}{m}\,|{\cdot}|$ bytes.

The classic **System R** dynamic program over join orders extends to a DP over (join order × interesting orders × interesting *partitions*) — the notion of *interesting properties* of Selinger generalizes to physical-property optimization à la **Cascades/Volcano** (Graefe). Output cardinalities still obey the **AGM bound** $|{\bowtie}| \le \prod_e |R_e|^{x_e}$ for a fractional edge cover $\{x_e\}$; cardinality error propagates multiplicatively through the cost terms.

For disaggregated storage, cost is $C = \alpha\,C_{\text{cpu}} + \beta\,C_{\text{net}} + \gamma\,C_{\text{storage-IO}} + \kappa\,C_{\$}$, and the optimizer must reason about caching state (what is already local) — a stateful, online flavor absent in shared-nothing.

## 3. State of the Art (SOTA)

- **Systems SOTA:** Spark Catalyst / AQE, Presto/Trino, Snowflake, Google BigQuery (Dremel), Amazon Redshift, and AnalyticDB perform cost-based join ordering plus shuffle-aware exchange placement; many use *adaptive* re-optimization at shuffle boundaries to correct estimation error. SCOPE/Cosmos (Microsoft) pioneered cost-based optimization of massively parallel DAGs.
- **Theory SOTA:** parallel-query results give communication-optimal algorithms in the **MPC (Massively Parallel Communication)** model — the **HyperCube / shares** algorithm (Afrati–Ullman; Beame–Koutris–Suciu) computes a conjunctive query in $O(1)$ rounds with provably near-optimal load, and multi-round tradeoffs are characterized for specific query classes.

## 4. Upper Bound

For a single conjunctive query in the MPC model, the **HyperCube** algorithm achieves one-round load $O\!\big(|\mathbf{R}|/p^{1/\psi^*}\big)$ where $\psi^*$ is the fractional edge-cover-derived optimal share exponent (Beame–Koutris–Suciu), which is load-optimal among one-round algorithms for many queries. For *plan selection* itself, join-order optimization is solved exactly by DP in $O(3^n)$ time over $n$ relations (Selinger DP); adding partition/placement annotations multiplies by the (constant-bounded) number of interesting partitions, keeping it $2^{O(n)}$.

## 5. Lower Bound

- **Plan selection** is NP-hard: optimal join ordering with cross-products is NP-hard (Ibaraki–Kameda; Cluet–Moerkotte), and adding placement/partitioning only enriches the search space.
- **Communication:** in the MPC model, one-round CQ evaluation has a load lower bound matching HyperCube for many queries; some queries provably *require* multiple rounds to beat a load threshold (Beame–Koutris–Suciu lower bounds via information-theoretic / friends-and-strangers arguments).
- Distributed coordination inherits **FLP impossibility** and **CAP** constraints when the optimizer's plan spans nodes that may fail or partition.

## 6. The Gap

There is no unified theory that *jointly* optimizes join order, partitioning, placement, and disaggregated-storage caching with provable guarantees. Theory bounds (MPC load) assume a *fixed* algorithm and known statistics; systems pick plans heuristically under unknown, drifting statistics and dynamic prices. The gap is genuinely open: we lack both (a) a cost model whose optima are robust to cardinality error, and (b) approximation guarantees for the joint placement+ordering problem. Closing it likely requires combining MPC lower bounds with robust/parametric optimization.

## 7. Current Research (as of June 2026)

- Robust and adaptive distributed re-optimization (re-shuffle decisions at runtime) in Spark AQE and Trino. *(frontier — verify)*
- Cost models for storage-disaggregated and serverless warehouses that price object-store IO and elastic compute jointly; work from Snowflake, Databricks (Photon), and academic groups (UW, CMU, TU Munich/Umbra) on cloud-cost-aware planning. *(frontier — verify)*
- Learned cost/cardinality components plugged into distributed optimizers; caution about extrapolation under shuffle.
- Tighter multi-round MPC tradeoffs and Pareto round/load characterizations (Suciu, Koutris, and collaborators).

## 8. Future Work

- A provable approximation algorithm for joint ordering + partitioning + placement.
- Cost models that are *monotone* under cardinality misestimation (robust plan selection).
- Cross-layer optimization spanning caching state in disaggregated storage and elastic scaling.
- Multi-objective (latency, \$, carbon) Pareto optimization with online price signals.

## 9. Key References

- **[Foundational]** P. G. Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** G. Graefe. *The Cascades Framework for Query Optimization.* IEEE Data Eng. Bull., 1995. — [DBLP](https://dblp.org/rec/journals/debu/Graefe95a.html)
- **[SOTA]** P. Beame, P. Koutris, D. Suciu. *Communication Steps for Parallel Query Processing.* JACM, 2017 (PODS 2013). — [arXiv](https://arxiv.org/abs/1306.5972)
- **[SOTA]** F. N. Afrati, J. D. Ullman. *Optimizing Joins in a Map-Reduce Environment.* EDBT, 2010. — [DOI](https://doi.org/10.1145/1739041.1739056)
- **[SOTA]** J. Zhou et al. *SCOPE: Parallel Databases Meet MapReduce.* VLDB Journal, 2012. — [DOI](https://doi.org/10.1007/s00778-012-0280-z)
- **[Survey]** P. Koutris, S. Salihoglu, D. Suciu. *Algorithmic Aspects of Parallel Data Processing.* Foundations and Trends in Databases, 2018. — [DOI](https://doi.org/10.1561/1900000055)

## 10. Worked Example

Join $R(a,b)\bowtie_b S(b,c)$ on $m=4$ nodes. $R$ is hash-partitioned on $a$ (so $b$ is scattered randomly); $S$ is hash-partitioned on $b$. Sizes: $|R|=400$ MB, $|S|=40$ MB.

- **Plan A — shuffle $R$ on $b$:** repartition $R$ so it co-locates with $S$. Shuffle cost $\approx \frac{m-1}{m}|R| = \frac34(400)=300$ MB across the network, then a local join.
- **Plan B — broadcast $S$:** ship all of $S$ to every node: cost $(m-1)\cdot|S| = 3(40)=120$ MB. $R$ never moves.

Plan B wins ($120 < 300$ MB) because $S$ is small — exactly the broadcast-vs-shuffle decision an exchange-aware optimizer must make. Now suppose a later filter shrinks $R$ to 30 MB at runtime: adaptive re-optimization (AQE) would flip back to shuffling $R$ ($\frac34(30)=22.5$ MB $<120$ MB). The optimal $\delta$ annotation is data-dependent, which is why static cost models miss it.

---
*Part of the [DBMS Research catalog](../../README.md).*
