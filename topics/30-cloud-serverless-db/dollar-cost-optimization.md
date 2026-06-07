---
id: 30-cloud-serverless-db/dollar-cost-optimization
title: "Cost-based execution with a dollar objective"
topic: 30-cloud-serverless-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Cost-based execution with a dollar objective

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/dollar-cost-optimization` · **Status:** open

## 1. Problem Statement

Classical query optimizers (Selinger-style) minimize an *abstract* cost — a weighted sum of CPU, IO, and network in arbitrary units — chosen to *rank* plans, not to predict spend. In the cloud, every resource has an explicit **price**: compute-seconds, GB scanned (e.g., \$5/TB), IOPS, cross-AZ bytes, request counts, and sometimes a latency-priced SLO. The **dollar-objective optimization problem**: build a cost model and plan-search whose objective is **monetary spend** (possibly subject to a latency constraint, or jointly trading dollars against latency on a Pareto frontier) across *heterogeneously priced* resources.

Variants: (a) **min-dollar** — cheapest plan meeting a latency bound; (b) **min-latency under budget** — fastest plan costing $\le B$; (c) **Pareto** — enumerate the dollar-vs-latency skyline; (d) **provisioning-coupled** — choose plan *and* resource shape (e.g., how many serverless workers) jointly, since price depends on the shape.

## 2. Mathematical Foundations

Let a physical plan $p$ consume resource vector $u(p)=(u_1,\dots,u_k)$ (CPU-s, bytes scanned, IO, network) with price vector $\pi$; dollar cost is $\langle \pi, u(p)\rangle$. The optimizer is the classic **plan-enumeration over a join lattice**, but with a *linear-in-priced-resources* objective. Because price couples to *parallelism* (more workers finish faster but cost the same compute-seconds, except for fixed per-request and spin-up charges), the objective becomes a **multi-objective / constrained** optimization: minimize cost subject to latency $\le \tau$, where latency is a non-linear (max over parallel stages, plus critical-path) function. This yields a **multi-criteria shortest-plan** problem; the dollar-vs-latency skyline can be exponential in the worst case, and constrained variants (cheapest plan with latency $\le\tau$) are NP-hard via reduction from constrained shortest path / knapsack. Pricing also makes the objective **non-additive** when tiered or with free-tier thresholds (piecewise-linear, non-convex).

## 3. State of the Art (SOTA)

- **Systems-SOTA:** BigQuery prices by *bytes scanned*, making partition/cluster pruning the dominant cost lever; Snowflake prices by *credits* (warehouse-seconds), making concurrency/right-sizing central; Athena/Presto-on-S3, Redshift Spectrum, and Databricks expose similar bytes/compute pricing. Some optimizers expose "dry-run" byte estimates. Research prototypes add monetary cost models to Calcite/Presto-style optimizers and "what-if" budget advisors.
- **Theory-SOTA:** multi-objective query optimization (Trummer & Koch) formalizes Pareto plan enumeration; this is the closest rigorous treatment, though dollar-pricing specifics are usually folded into a single weighted cost.

## 4. Upper Bound

For a *single linear* dollar objective with additive resource costs, plan search is no harder than classical optimization — the same DP / Cascades enumeration finds the optimum, polynomial in plans considered (exponential in relations in the worst case, as usual). For the **constrained** (min-dollar s.t. latency) and **Pareto** variants, approximate-skyline algorithms (Trummer–Koch) compute an $\epsilon$-approximate Pareto frontier in time polynomial in $1/\epsilon$ and the plan space, giving an FPTAS-style guarantee per the multi-objective framework.

## 5. Lower Bound

The constrained cheapest-plan problem is **NP-hard** (reduction from *constrained shortest path* / *0-1 knapsack*: choose operators/indexes to minimize price under a latency budget). The exact Pareto frontier can have **exponentially many** plans, so any algorithm that materializes it is exponential in the worst case — hence approximation is necessary. With tiered/free-tier (piecewise-linear non-convex) pricing, the objective loses additivity and standard DP optimality (principle of optimality) can fail, an additional hardness source.

## 6. The Gap

The unconstrained linear-dollar case is *closed* (reduces to classical optimization). The genuinely open part: (i) accurate dollar **cost estimation** under cloud pricing (bytes-scanned and credit models depend on data layout and concurrency, which are hard to predict, compounding cardinality-estimation error with price error); (ii) jointly optimizing **plan + provisioning shape** where price and latency are coupled; (iii) non-convex tiered pricing. No optimizer provably picks the dollar-optimal (plan, resource-shape) pair under realistic pricing.

## 7. Current Research (as of June 2026)

Active: budget-aware query optimization, learned cost models calibrated to *money* not units, multi-objective optimizers in Calcite/Presto, and "FinOps for data" cost advisors. Groups: Saarland/Cornell (Trummer), CMU, Microsoft (cost-based "what-if"), and cloud-vendor optimizer teams. *(frontier — verify)* 2025–2026 work calibrates learned cardinality+cost models directly against cloud billing telemetry and adds LLM-assisted SQL-cost advisors; provable dollar-optimality guarantees remain absent.

## 8. Future Work

- Calibrated monetary cost models that compose cardinality error with price error and bound the result.
- Joint plan-and-provisioning optimization under coupled price/latency.
- Handling non-convex tiered/free-tier pricing without losing DP optimality.
- User-facing dollar-vs-latency skylines as a first-class optimizer output.

## 9. Key References

- **[Foundational]** Selinger, Astrahan, Chamberlin, Lorie, Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Trummer, Koch. *Multi-Objective Parametric Query Optimization.* VLDB, 2015 / CACM, 2017. — [VLDB PDF](http://www.vldb.org/pvldb/vol8/p221-trummer.pdf)
- **[SOTA]** Dageville, Cruanes, et al. *The Snowflake Elastic Data Warehouse.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2903741)
- **[SOTA]** Melnik, Gubarev, et al. *Dremel: Interactive Analysis of Web-Scale Datasets.* VLDB, 2010 (basis of BigQuery's bytes-scanned model). — [DOI](https://doi.org/10.14778/1920841.1920886)
- **[Survey]** Chaudhuri. *An Overview of Query Optimization in Relational Systems.* PODS, 1998. — [DOI](https://doi.org/10.1145/275487.275492)

## 10. Worked Example

Consider `SELECT * FROM events WHERE day = '2026-06-01'` on a 2 TB table, priced at **\$5/TB scanned** (BigQuery-style).

- **Plan A — full scan:** scans all $2\,000$ GB. Cost $= 2.0 \text{ TB} \times \$5 = \$10.00$.
- **Plan B — partitioned by `day` (365 partitions):** prunes to one day $\approx 2000/365 \approx 5.5$ GB. Cost $= 0.0055 \text{ TB} \times \$5 = \$0.027$ — a $\approx 365\times$ saving. Latency drops too, so it dominates A on the Pareto frontier.

Now add a **latency constraint** and a *credit-priced* (Snowflake-style) engine at \$3/warehouse-hour. Plan B on 1 worker takes $40$ s; on 4 workers it takes $12$ s (serial merge fraction limits Amdahl speedup to $40/12 \approx 3.3\times$). Compute cost is roughly invariant: $1 \times 40\text{s} = 40$ worker-s vs $4 \times 12 = 48$ worker-s, i.e. $\$0.033$ vs $\$0.040$. So under an SLO of $\tau = 15$ s, the cheapest *feasible* plan is **4 workers** at \$0.040 — the constraint forces the slightly pricier shape. This is exactly the *constrained shortest-plan* / knapsack structure that makes the constrained variant NP-hard.

---
*Part of the [DBMS Research catalog](../../README.md).*
