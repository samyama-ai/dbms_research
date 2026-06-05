# Provably Fault-Tolerant Query Restart

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/fault-tolerant-query-restart` · **Status:** partially-solved

## 1. Problem Statement
A long-running distributed query executes as a DAG of stages (scans, shuffles, joins, aggregations) over $p$ workers. When a subset of workers or stages fails mid-execution, we want to **recover and complete the query without full re-execution**, with *provable bounds* on the extra work and time relative to a failure-free run.

Variants:
- **Decision:** given a checkpoint/materialization policy, is the recovery work bounded by a factor $\rho$ of failure-free cost?
- **Optimization:** choose which intermediate results to persist (and at what granularity) to minimize expected total cost $= \text{failure-free cost} + \mathbb{E}[\text{recovery cost}]$ under a failure model.
- **Competitive / online:** without knowing failures in advance, bound the competitive ratio of a restart policy against an offline optimum.

The central tension is the **materialization–recomputation tradeoff**: persisting more lineage/intermediates raises baseline cost but shrinks recovery; persisting less is cheap until a failure forces cascading recomputation.

## 2. Mathematical Foundations
Model execution as a DAG $G=(V,E)$ where vertices are tasks with work $w_v$ and edges encode data dependencies. **Lineage** (RDD-style) lets a lost partition be recomputed from its parents. Recovery cost on failure of set $F$ is the work of the *recomputation closure* — the ancestors of $F$ whose outputs were not persisted.

For an independent per-task failure probability $q$, the expected recovery cost under a checkpoint set $S \subseteq V$ is
$$\mathbb{E}[\text{recov}] = \sum_{v} q \cdot \mathrm{work}(\text{ancestors}(v) \setminus \mathrm{persisted}(S)).$$
Optimal checkpoint placement generalizes **Young/Daly's formula** $\tau^* \approx \sqrt{2\,\delta\, M}$ (checkpoint interval $\tau$, checkpoint cost $\delta$, MTBF $M$) from linear chains to DAGs, where the DAG case is **NP-hard** (relates to weighted vertex cut / min-cut placement). Wide shuffle dependencies cause *cascading* recomputation; narrow (pipelined) dependencies localize it.

## 3. State of the Art (SOTA)
- **Systems:** *MapReduce* (Dean–Ghemawat, OSDI 2004) — materialize every stage, recover by re-running tasks. *Spark RDD lineage* (Zaharia et al., NSDI 2012) — recompute lost partitions from lineage; checkpoint to truncate long lineages. *Dryad*, *FlumeJava*, *Naiad/timely* (coordinated checkpoints), *Flink* (Chandy–Lamport asynchronous barrier snapshots for streaming). *Spark with adaptive query execution* re-materializes shuffle stages. Cloud warehouses (BigQuery, Snowflake, *Presto/Trino with fault-tolerant execution / Project Tardigrade*, 2022) add task-level retry and spill-to-disk exchange for long ETL queries.
- **Theory:** checkpoint-interval optimization (Daly 2006), DAG checkpoint scheduling, and competitive analyses of restart for malleable/online jobs.

## 4. Upper Bound
With full stage materialization (MapReduce-style), a single stage failure costs only re-running the failed tasks: recovery $\le$ (failed work) $+$ (re-read of persisted inputs), giving a $1 + o(1)$ overhead in the single-failure regime at the price of persisting all shuffle output. Lineage-based recovery (Spark) bounds recovery to the *narrow* ancestor work for narrow dependencies; periodic checkpointing at the Daly-optimal interval yields expected total overhead $\Theta(\sqrt{\delta/M})$ for chain-structured plans. Chandy–Lamport snapshots give consistent global checkpoints with overhead independent of the number of in-flight messages, enabling streaming-query restart with bounded replay.

## 5. Lower Bound
- **Impossibility:** the **FLP** result (Fischer–Lynch–Paterson, 1985) shows no deterministic protocol guarantees consensus (hence coordinated commit/recovery agreement) in an asynchronous system with even one crash failure — so perfectly coordinated restart cannot be guaranteed without timing/failure-detector assumptions. **CAP** (Gilbert–Lynch) constrains availability under partitions.
- **Hardness:** optimal checkpoint placement on general DAGs to minimize expected recovery is **NP-hard**.
- **Communication / replay:** in the worst case (all shuffle outputs un-persisted, root failure) recovery work is $\Omega$(total query work) — no policy avoids near-full re-execution if nothing was materialized.

## 6. The Gap
Practice has strong *engineering* solutions (materialize-everything, lineage, ABS snapshots) but lacks **tight provable competitive bounds** for adaptive restart on general query DAGs under realistic correlated-failure models. The gap between the NP-hard offline optimum and deployed heuristics is uncharacterized; there is no known constant-competitive online checkpointing policy for arbitrary DAGs with correlated failures. Closing it requires either an approximation algorithm with provable ratio for DAG checkpoint placement, or matching hardness-of-approximation results, plus a model bridging FLP-style impossibility with the throughput goals of batch analytics.

## 7. Current Research (as of June 2026)
- Fault-tolerant execution in serverless/disaggregated analytics where exchange data lands in object storage, making mid-query restart cheap *(frontier — verify)*.
- Provable competitive analysis of speculative re-execution and partial restart.
- Correlated/spot-instance failure models (cloud preemption) driving cost-aware checkpoint policies.
- Snapshot-based restart for incremental and streaming queries (Flink, Materialize, Arroyo).
- Groups: Pavlo/Zhou (CMU), the Trino/Presto fault-tolerant-execution team (Starburst), Carbone/Katsifodimos (Flink ABS), Stoica/RISELab descendants (Ray, Sky), Apache Spark/Databricks.

## 8. Future Work
- Constant-competitive online checkpoint placement for DAGs.
- Cost models unifying baseline + expected-recovery + cloud preemption pricing.
- Verified recovery protocols reconciling FLP limits with practical liveness via failure detectors.
- Fine-grained (sub-stage / operator-level) lineage with bounded space.

## 9. Key References
- **[Foundational]** M. Fischer, N. Lynch, M. Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. (FLP.) — [DOI](https://doi.org/10.1145/3149.214121)
- **[Foundational]** K. M. Chandy, L. Lamport. *Distributed Snapshots: Determining Global States of Distributed Systems.* ACM TOCS, 1985. — [DOI](https://doi.org/10.1145/214451.214456)
- **[Foundational]** J. Dean, S. Ghemawat. *MapReduce: Simplified Data Processing on Large Clusters.* OSDI, 2004. — [USENIX](https://www.usenix.org/conference/osdi-04/mapreduce-simplified-data-processing-large-clusters)
- **[SOTA]** M. Zaharia et al. *Resilient Distributed Datasets: A Fault-Tolerant Abstraction for In-Memory Cluster Computing.* NSDI, 2012. — [USENIX](https://www.usenix.org/conference/nsdi12/technical-sessions/presentation/zaharia)
- **[SOTA]** P. Carbone, S. Ewen, G. Fóra, S. Haridi, S. Richter, K. Tzoumas. *State Management in Apache Flink: Consistent Stateful Distributed Stream Processing.* VLDB, 2017. — [DOI](https://doi.org/10.14778/3137765.3137777)
- **[Foundational]** J. T. Daly. *A Higher Order Estimate of the Optimum Checkpoint Interval for Restart Dumps.* Future Generation Computer Systems, 2006. — [DOI](https://doi.org/10.1016/j.future.2004.11.016)

## 10. Worked Example

**Daly checkpoint interval.** A long ETL query runs $T = 10$ hours on a cluster with mean time between failures $M = 5$ h. A checkpoint costs $\delta = 6$ min $= 0.1$ h. Young/Daly's first-order optimum is

$$\tau^* \approx \sqrt{2\,\delta\,M} = \sqrt{2 \cdot 0.1 \cdot 5} = 1\text{ h}.$$

So checkpoint every ~1 hour. With no checkpointing, an expected failure at the $M=5$ h mark forces re-running from scratch: $\approx 5$ h of lost work. With $\tau^*=1$ h checkpoints, a failure loses only the work since the last checkpoint, expected $\approx \tau/2 = 0.5$ h, plus the $0.1$ h-per-checkpoint write overhead across the run.

**DAG cascade.** Now consider a 4-stage lineage chain $S_1\!\to\!S_2\!\to\!S_3\!\to\!S_4$, none persisted, each $w=1$ unit of work. If $S_4$'s worker fails, the recomputation closure is $\{S_1,S_2,S_3,S_4\}$ = 4 units (full re-execution). Persisting only $S_3$'s output cuts the closure to $\{S_4\}$ = 1 unit. This is the materialization–recomputation tradeoff in miniature; choosing the persist set optimally over a general DAG is the NP-hard part.

---
*Part of the [DBMS Research catalog](../../README.md).*
