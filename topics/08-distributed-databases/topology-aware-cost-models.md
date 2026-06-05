# Bandwidth-Tagged Cost Models

> **Topic:** Distributed Query Processing · **ID:** `08-distributed-databases/topology-aware-cost-models` · **Status:** open

## 1. Problem Statement

A query optimizer needs a **cost model** that, for any candidate distributed plan, predicts execution cost (latency and/or dollars) accurately enough to rank plans correctly. Classic models assume a single, flat network cost per byte. Real clusters are **tiered**: intra-node ≫ intra-rack ≫ cross-rack ≫ cross-zone ≫ cross-region bandwidth, with WAN egress also priced in money. The problem is to design a **bandwidth-tagged cost model** that:

1. Tags each data movement with the topology tier it traverses and that tier's bandwidth/price.
2. Composes per-operator costs into a plan cost that is **monotone and rank-faithful** (preserves the true ordering of competing plans).
3. Is **robust** to cardinality-estimation error and bandwidth variability, yielding plans whose worst-case regret is bounded.

- **Modeling variant:** define the model + parameters that minimize plan-ranking error.
- **Optimization-coupled variant:** ensure the model admits an efficient optimizer (see *Distributed Join Order with Network Cost*).
- **Robustness variant:** minimize maximum regret over an uncertainty set of cardinalities/bandwidths.

## 2. Mathematical Foundations

Model the topology as a weighted graph $T=(N, \text{bw}, \text{price})$ with tiers $\mathcal{T}=\{$node, rack, zone, region$\}$ and per-tier bandwidth $b_t$. The transfer cost of moving $D$ bytes along an edge of tier $t$ is $D / b_t$ (latency) or $D \cdot \pi_t$ (price), and a plan's cost aggregates over its exchange edges:
$$\text{Cost}(P) = \sum_{e \in \text{exch}(P)} \frac{\text{bytes}(e)}{b_{\text{tier}(e)}} \;+\; \alpha \cdot \text{maxload}(P).$$
Cardinality inputs $\text{bytes}(e)$ derive from selectivity estimation; worst-case sizes are bounded by **AGM / fractional edge cover**. Robust planning frames cost under an **uncertainty set** $\mathcal{U}$ of $(\hat n, \hat b)$ and seeks $\min_P \max_{u\in\mathcal U} \text{Cost}(P,u)$ — a robust optimization / minimax-regret formulation. Faithfulness is a **rank-preservation** property: for the model to be useful it suffices that $\text{Cost}$ orders plans as true latency does (a weaker condition than absolute accuracy), connecting to learning-to-rank and to the theory of *plan robustness* (plan diagrams, parametric query optimization).

## 3. State of the Art (SOTA)

- **Theory-SOTA:** the **MPC / BSP** models (Beame–Koutris–Suciu; Valiant's BSP with parameters $g$ for bandwidth gap, $L$ latency) provide a *flat* communication cost abstraction with matching bounds; hierarchical/multi-tier MPC variants exist but are not standard in optimizers.
- **Systems-SOTA:** production cost models with explicit shuffle/broadcast/egress terms — Spark Catalyst, Trino, Greenplum, SQL Server PDW, CockroachDB locality cost, Snowflake/BigQuery cross-region egress pricing. Geo-distributed planners **Iridium** (SIGCOMM 2015) and **Clarinet/Tetrium** explicitly model WAN link bandwidth. Learned cost models (**Bao**, **Neo**, end-to-end learned optimizers) replace hand-tuned constants with models trained on telemetry but are mostly single-cluster.

## 4. Upper Bound

- **Faithfulness under correct stats:** with accurate cardinalities and bandwidths, a linear bandwidth-tagged model is *exactly* rank-faithful for bytes-dominated plans (cost equals predicted latency up to the maxload term).
- **Robust regret:** minimax-regret plan selection over a box uncertainty set is solvable as an LP/robust program for fixed plan shapes; gives plans with bounded worst-case regret.
- **Learned:** learned models empirically cut estimation error by large factors but offer no formal accuracy bound.

## 5. Lower Bound

- **Estimation barrier:** cost-model error is lower-bounded by **cardinality-estimation error**, which is provably hard — multi-join selectivity estimation has worst-case error that compounds; no estimator is accurate for all instances (classic result: estimation errors grow exponentially in join depth).
- **Model-class limits:** any *linear* per-tier model cannot capture congestion/contention (cost is non-additive when concurrent transfers share links) — a representational lower bound; faithful modeling of shared-link congestion needs non-additive (e.g., max-flow) terms.
- **Robustness:** minimax regret over an adversarial cardinality set has an unavoidable gap from the omniscient optimum (price of robustness).

## 6. The Gap

**Open.** No cost model simultaneously (a) tags all topology tiers, (b) models shared-link congestion, (c) remains efficiently optimizable, and (d) carries a provable rank-faithfulness or regret guarantee under estimation error. Practical models are tier-aware but additive (ignore congestion) and unproven; learned models are accurate-in-distribution but unbounded out-of-distribution. Closing the gap means a model with congestion-aware non-additive terms that still admits an optimizer with bounded regret — currently neither a tight upper construction nor a matching impossibility is established.

## 7. Current Research (as of June 2026)

- Learned and hybrid (analytical + learned) cost models extended to multi-tier / cross-region topologies and dollar-cost objectives. *(frontier — verify)*
- Robust and risk-aware query optimization (minimax-regret, plan robustness) integrated with bandwidth tags. *(frontier — verify)*
- Congestion-aware planning borrowing from coflow scheduling (Varys/Aalo) to make the cost model account for shared-link contention.

## 8. Future Work

- A congestion-aware, tier-tagged cost model with provable rank-faithfulness.
- Bounded-regret distributed optimization under joint cardinality + bandwidth uncertainty.
- Unified latency-and-dollars objective for cloud/geo-distributed lakehouses.

## 9. Key References

- **[Foundational]** Valiant. *A Bridging Model for Parallel Computation (BSP).* CACM, 1990.
- **[SOTA]** Beame, Koutris, Suciu. *Communication Steps for Parallel Query Processing.* PODS / JACM, 2013/2017.
- **[SOTA]** Pu et al. *Low Latency Geo-distributed Data Analytics (Iridium).* SIGCOMM, 2015.
- **[SOTA]** Marcus et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021.
- **[Foundational]** Chu, Ioannidis, et al. / Leis et al. *How Good Are Query Optimizers, Really?* VLDB, 2015 (cardinality-estimation error study).

---
*Part of the [DBMS Research catalog](../../README.md).*
