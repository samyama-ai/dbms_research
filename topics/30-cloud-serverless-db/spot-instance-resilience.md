---
id: 30-cloud-serverless-db/spot-instance-resilience
title: "Spot-instance-resilient query execution"
topic: 30-cloud-serverless-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Spot-instance-resilient query execution

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/spot-instance-resilience` · **Status:** empirically-open

## 1. Problem Statement

Cloud providers sell **preemptible / spot** compute at 60–90% discounts, but reclaim nodes with little notice (e.g., AWS gives a 2-minute warning; GCP ~30s; some markets none). We want to execute a distributed analytical query DAG on a pool of such nodes so that the **total expected cost** (compute-time × spot price + re-execution overhead) is minimized while the **makespan** stays within a deadline with high probability, despite stochastic reclamation.

Variants:
- **Decision:** Given a query plan, node reclamation hazard rates, and a deadline $D$, does a scheduling/checkpointing policy exist achieving completion by $D$ with probability $\ge 1-\delta$ within budget $B$?
- **Optimization:** Minimize $\mathbb{E}[\text{cost}]$ subject to a deadline-violation probability cap, choosing checkpoint placement, task replication, and on-demand fallback.
- **Online:** Reclamations and price changes are revealed over time; commit decisions irrevocably (competitive-analysis framing).

The key tension: checkpointing/materializing intermediate results bounds re-execution cost but adds I/O to (slow, priced) remote storage; replication hides preemptions but multiplies compute spend.

## 2. Mathematical Foundations

Model the query as a DAG $G=(V,E)$ of tasks with work $w_v$. Each node $i$ runs until reclaimed; lifetime $L_i$ is often modeled **memoryless / exponential** with hazard $\lambda_i$, though empirical spot lifetimes are heavy-tailed (Weibull/log-normal), breaking memorylessness.

For a single task of work $w$ on a node with hazard $\lambda$ and checkpoint interval $\tau$ (checkpoint cost $c$), the classic **Young–Daly** optimum gives $\tau^\* \approx \sqrt{2c/\lambda}$, with expected wall-time
$$ \mathbb{E}[T] \approx w\left(1 + \tfrac{1}{2}\lambda\tau + \tfrac{c}{\tau}\right). $$
This is a building block; the open difficulty is the **DAG-coupled, multi-node, price-varying** generalization where re-execution of one stage may force re-reads of upstream intermediates.

The online version is naturally a **Markov decision process** over (DAG progress, node-set, price) states; exact solution is intractable, so the question is near-optimal policies with provable guarantees. Competitive ratios connect to **ski-rental / metrical task systems** (checkpoint-or-gamble is a rent-or-buy decision under uncertainty).

## 3. State of the Art (SOTA)

- **Systems-SOTA.** Spark/Hadoop lineage-based recomputation tolerates losses but with unbounded, plan-dependent recovery cost. **SparkLens / SpotOn**, **Tributary** (NSDI 2018, server allocation from spot), and cloud-native warehouses (Snowflake, BigQuery, Redshift Serverless) use *on-demand fallback + coarse checkpoint to object storage*. **Pando**, **TR-Spark** and similar add transience-awareness via task-level replication heuristics.
- **Theory-SOTA.** Young–Daly checkpointing and its DAG extensions (Bouguerra et al.); spot-pricing decision frameworks modeling lifetimes as Markov chains. No tight competitive policy for the coupled DAG + pricing + heavy-tailed-lifetime problem.

There is a real gap: production systems use tuned heuristics; theory solves clean single-task or homogeneous cases.

## 4. Upper Bound

For a single linear chain with exponential lifetimes, Young–Daly gives an asymptotically optimal checkpoint interval with overhead $1+O(\sqrt{\lambda c})$. For homogeneous fork-join DAGs, list-scheduling plus periodic checkpointing yields makespan within a constant factor of the failure-free optimum in expectation when $\lambda$ is known. Online ski-rental-style checkpoint-vs-recompute decisions are **2-competitive** in the rent-or-buy abstraction; randomization improves this toward $e/(e-1)\approx 1.58$.

These bounds assume known/stationary hazard and ignore pricing coupling.

## 5. Lower Bound

No deterministic online policy can beat the **2-competitive** ski-rental bound for the rent-or-buy core (and $e/(e-1)$ for randomized), giving an unconditional lower bound on any reclamation-checkpoint policy reducible to it. Scheduling the DAG to minimize makespan under failures inherits **NP-hardness** from precedence-constrained scheduling ($P\,|\,prec\,|\,C_{\max}$). Under heavy-tailed lifetimes the memoryless assumption fails, and the optimal-policy problem becomes a POMDP with **PSPACE-hard** flavor in general. There is no matching lower bound for the full coupled cost objective — that absence is precisely why the problem is empirically open.

## 6. The Gap

For the idealized single-task / known-hazard slice, upper and lower bounds essentially meet (Young–Daly optimality; ski-rental competitiveness). The gap is in the **realistic regime**: (a) heavy-tailed, non-stationary, correlated reclamations across a node *fleet*; (b) DAG coupling where re-execution cost depends on what intermediates survived; (c) joint optimization with *time-varying spot prices and on-demand fallback*. No policy is known to be provably near-optimal here, and no conditional lower bound rules one out. Closing it requires either a competitive online algorithm against an adversarial/heavy-tailed reclamation model or a hardness result tying it to MTS/POMDP lower bounds.

## 7. Current Research (as of June 2026)

Active directions: (i) learning-augmented scheduling that feeds spot-lifetime/price predictions into checkpoint policies with worst-case fallback (Mitzenmacher–Vassilvitskii "algorithms with predictions" lens) *(frontier — verify)*; (ii) serverless analytics over functions (Lambda/Cloud Run) where workers vanish even more aggressively, studied by groups around UC Berkeley RISELab/Sky Computing and CMU; (iii) cost-aware checkpoint placement to disaggregated storage in lakehouse engines. Industrial work in Snowflake/Databricks/Google focuses on transparent recovery and adaptive on-demand fallback *(frontier — verify)*.

## 8. Future Work

- Competitive analysis under **heavy-tailed, correlated** fleet reclamations (beyond memoryless).
- DAG-aware checkpoint placement that jointly bounds *re-read* and *re-compute* cost.
- Learning-augmented policies with provable consistency/robustness tradeoffs and price prediction.
- Benchmarks with public spot-reclamation traces for reproducible evaluation.
- Integration with disaggregated-storage cost models (see remote-io-cost-model).

## 9. Key References

- **[Foundational]** John W. Young. *A first order approximation to the optimum checkpoint interval.* CACM, 1974. — [DOI](https://doi.org/10.1145/361147.361115)
- **[Foundational]** Jack Daly. *A higher order estimate of the optimum checkpoint interval for restart dumps.* FGCS, 2006. — [DOI](https://doi.org/10.1016/j.future.2004.11.016)
- **[SOTA]** A. Harlap et al. *Tributary: spot instances for predictable response.* USENIX ATC, 2018. — [USENIX](https://www.usenix.org/conference/atc18/presentation/harlap)
- **[SOTA]** Y. Yan et al. *TR-Spark: Transient Computing for Big Data Analytics.* ACM SoCC, 2016. — [DOI](https://doi.org/10.1145/2987550.2987576)
- **[Survey]** T. Herault, Y. Robert (eds.). *Fault-Tolerance Techniques for High-Performance Computing.* Springer, 2015. — [DOI](https://doi.org/10.1007/978-3-319-20943-2)

## 10. Worked Example

Consider one task with work $w = 100$ minutes on a spot node whose lifetime is exponential with hazard $\lambda = 0.01$ per minute (mean lifetime $100$ min). Each checkpoint to object storage costs $c = 1$ minute.

**No checkpointing.** If reclaimed mid-run we restart from scratch. Expected restarts inflate runtime sharply; with $\lambda w = 1$ the work often does not finish in one lifetime.

**Young–Daly optimum.** The optimal interval is
$$ \tau^\* \approx \sqrt{2c/\lambda} = \sqrt{2\cdot 1/0.01} = \sqrt{200} \approx 14.1 \text{ min}. $$
So checkpoint every $\approx 14$ minutes ($\lceil 100/14.1\rceil = 8$ segments). The expected wall-time overhead factor is
$$ 1 + \tfrac{1}{2}\lambda\tau^\* + \tfrac{c}{\tau^\*} = 1 + 0.5(0.01)(14.1) + \tfrac{1}{14.1} \approx 1 + 0.0705 + 0.0709 \approx 1.14, $$
i.e. only $\sim 14\%$ overhead versus the failure-free $100$ min, giving $\mathbb{E}[T]\approx 114$ min. Checkpointing too often ($\tau=2$) would cost $\tfrac{c}{\tau}=0.5$ alone ($+50\%$); too rarely ($\tau=100$) risks losing nearly the whole run on a single preemption. The $\sqrt{2c/\lambda}$ balance is the sweet spot — but only under the memoryless assumption this example relies on.

---
*Part of the [DBMS Research catalog](../../README.md).*
