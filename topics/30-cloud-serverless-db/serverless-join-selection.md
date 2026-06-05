# Serverless join-algorithm selection

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/serverless-join-selection` · **Status:** open

## 1. Problem Statement

In serverless analytics (queries executed by ephemeral functions / autoscaling worker pools over disaggregated storage), the optimizer must choose a join strategy when the resources themselves are decision variables: **worker count $K$** is elastic, **network/shuffle bandwidth** scales with $K$ (and is priced), and **intermediate results** must be **materialized** to remote storage or exchanged over the network (also priced). Classic join selection (hash vs. sort-merge vs. broadcast vs. partitioned/shuffle) assumed fixed parallelism and local exchange. The problem: jointly choose join algorithm, worker count, partitioning, and materialization strategy to minimize dollar cost (or time-under-budget) for a query.

Variants:
- **Optimization:** min $\$$-cost (or time) over (algorithm, $K$, partition scheme, materialize-vs-pipeline) per join, and over the whole join tree.
- **Decision:** Is there a configuration achieving time $\le T$ within budget $B$?
- **Online/adaptive:** Cardinalities revealed at runtime (re-optimization, adaptive join), worker count adjusted mid-query.

## 2. Mathematical Foundations

Output size is governed by the **AGM bound**: for a join query (hypergraph $H$ with fractional edge cover $\mathbf{x}$), $|{\bowtie}| \le \prod_R |R|^{x_R}$, tight in the worst case, and achieved by **worst-case-optimal join** algorithms (NPRR / LeapFrog-TrieJoin, Ngo–Ré–Rudra). This bounds intermediate-result size — the quantity that drives materialization $ and shuffle volume.

Cost of a shuffle (partitioned) join across $K$ workers in the **Massively Parallel Computation (MPC)** model: with $p$ workers and load $L$ per worker, a single round needs $L = \tilde O(|\text{IN}|/p)$ for skew-free data; **Koutris–Suciu** parallel-join theory gives round/load lower bounds and the optimal load for conjunctive queries (the "HyperCube"/shares algorithm) as a function of the AGM exponent. The dollar model adds:
$$ \$ \approx \underbrace{K\cdot t\cdot p_{\text{cpu}}}_{\text{compute}} + \underbrace{V_{\text{shuffle}}\cdot p_{\text{net}}}_{\text{network}} + \underbrace{V_{\text{mat}}\cdot(p_{\text{req}}+p_{\text{byte}})}_{\text{materialize}}, $$
turning algorithm selection into a constrained optimization where $K$ trades compute time against fixed network/materialization volume. **Skew** breaks the uniform-load assumption (heavy hitters), invoking skew-resilient (residual/HyperCube) variants.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** Serverless query engines — **Starling** (SIGMOD 2020, queries on AWS Lambda + S3), **Lambada** (SIGMOD 2020), **Flint**, **Cloudburst**-style — characterize shuffle-via-object-storage cost and pick worker counts heuristically. Snowflake/BigQuery/Redshift Spectrum do shuffle joins with elastic slots; Spark/Photon adaptively switch broadcast vs. shuffle hash join (**Adaptive Query Execution**) based on runtime sizes.
- **Theory-SOTA.** Worst-case-optimal joins (Ngo–Ré–Rudra, NPRR 2012; LeapFrog-TrieJoin); parallel join complexity in the MPC model (Beame–Koutris–Suciu, PODS 2013–2017); these give load/round-optimal algorithms but **not** dollar-cost-aware, elastic-K selection.

## 4. Upper Bound

Worst-case-optimal joins run in $\tilde O(\text{AGM bound})$ time, optimal in the worst case for the output volume. In the MPC model, conjunctive queries compute in **$O(1)$ rounds** with per-worker load $\tilde O(|\text{IN}|/p^{1/\rho^\*})$ (HyperCube/shares), where $\rho^\*$ is the fractional edge-cover number — load-optimal for skew-free inputs. Choosing $K$ to minimize $\$$ given a convex time-vs-$K$ curve has a closed-form crossover (compute-bound until network/materialization-bound). Adaptive execution achieves near-optimal algorithm choice once true cardinalities are observed.

## 5. Lower Bound

Join evaluation cannot beat the **AGM bound** in the worst case (it is tight), so any algorithm pays $\Omega(\text{AGM})$ output cost. In the MPC model, **Beame–Koutris–Suciu** prove load **lower bounds** $\Omega(|\text{IN}|/p^{1/\tau})$ for one-round computation of conjunctive queries (communication-complexity-based), and multi-round lower bounds for specific queries — fundamental limits on how much elastic parallelism can help. Optimal join *ordering* is **NP-hard** (Ibaraki–Kameda). Cardinality estimation feeding the choice has no worst-case guarantee (info-theoretic). No tight lower bound is known for the *priced, elastic-K, materialize-vs-pipeline* objective — the problem is genuinely **open**.

## 6. The Gap

Theory gives tight bounds on *volume* (AGM) and *parallel load/rounds* (MPC). Systems give working heuristics for $K$ and adaptive algorithm switches. But the **integrated decision** — algorithm × worker-count × partitioning × materialization, optimized for *dollars* under elastic, priced resources — has **no formal optimality characterization and no matching lower bound**. We don't know the optimal $K$-vs-cost policy under skew + pricing, nor whether the problem is poly-time solvable given accurate cardinalities, nor a hardness result. This is the open core: connect MPC/AGM theory to a priced, elastic optimization objective.

## 7. Current Research (as of June 2026)

Directions: serverless-shuffle cost reduction (object-store vs. ephemeral-VM exchange, **Pocket/Locus**-style fast ephemeral storage); learned/adaptive worker right-sizing per query stage *(frontier — verify)*; extending worst-case-optimal and MPC results toward cost-/skew-aware execution (groups around Dan Suciu / Paris Koutris, Hung Ngo / RelationalAI, Semih Salihoglu at Waterloo) *(frontier — verify)*; adaptive query execution in Photon/Velox generalizing broadcast/shuffle choice. Budget-aware "cost-of-cloud" optimization is an emerging industrial theme.

## 8. Future Work

- A cost model + optimizer that selects algorithm, $K$, partitioning, and materialization jointly with provable guarantees.
- Skew-resilient elastic joins with dollar-cost bounds.
- Lower bounds for the priced elastic-parallelism join objective (extending MPC communication arguments).
- Adaptive mid-query re-provisioning of workers with stability guarantees.
- Worst-case-optimal joins under remote-storage and pricing constraints.

## 9. Key References

- **[Foundational]** H. Q. Ngo, C. Ré, A. Rudra. *Worst-case Optimal Join Algorithms.* JACM, 2018 (PODS 2012).
- **[Foundational]** P. Beame, P. Koutris, D. Suciu. *Communication Steps for Parallel Query Processing.* JACM, 2017 (PODS 2013).
- **[SOTA]** M. Perron et al. *Starling: A Scalable Query Engine on Cloud Functions.* ACM SIGMOD, 2020.
- **[SOTA]** I. Müller, R. Marroquín, G. Alonso. *Lambada: Interactive Data Analytics on Cold Data Using Serverless Cloud Infrastructure.* ACM SIGMOD, 2020.
- **[Survey]** P. Koutris, S. Salihoglu, D. Suciu. *Algorithmic Aspects of Parallel Query Processing.* Foundations and Trends in Databases, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
