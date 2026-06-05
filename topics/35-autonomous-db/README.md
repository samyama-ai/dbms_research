# Self-Driving / Autonomous Databases

Self-driving databases close the loop from observation to action: they forecast workloads, choose
physical designs (indexes, partitions, materialized views), tune configuration knobs, and apply those
changes autonomously while the system serves live traffic. This topic spans the theory of the
underlying optimization and learning problems (complexity, regret, identifiability, achievability) and
the systems engineering of the control loop itself (action planning, safe deployment, rollback,
observability, and verification). The problems below are the hard, open, or empirically-unsettled
questions that PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT communities continue to study.

| Problem | Status | Scope |
|---|---|---|
| [Index Selection Complexity & Approximability](./index-selection-complexity.md) | partially-solved | Tight hardness and approximation bounds for budget-constrained index selection beyond the classic NP-hardness result. |
| [Online Index Selection with Regret Bounds](./online-index-selection-regret.md) | open | No-regret online algorithms for index creation/dropping under shifting workloads with build and storage costs. |
| [Interaction-Aware Configuration Search](./index-interaction-modeling.md) | open | Modeling and exploiting index/MV/partition interactions whose benefit is non-additive and combinatorially large. |
| [Materialized View Selection Bounds](./mv-selection-bounds.md) | partially-solved | Approximation and inapproximability results for view selection under maintenance-cost and space budgets. |
| [Joint Physical Design Optimization](./joint-physical-design.md) | open | Co-selecting indexes, views, and partitions together rather than greedily, with provable joint-optimality guarantees. |
| [Automatic Partitioning & Co-Partitioning](./automatic-partitioning.md) | open | Choosing horizontal/vertical partitions and replica layouts that minimize distributed query and skew cost. |
| [What-If Cost Model Fidelity](./what-if-cost-fidelity.md) | empirically-open | Whether optimizer what-if estimates are accurate enough to drive design choices, and how to bound their error. |
| [Workload Forecasting Under Drift](./workload-forecasting-drift.md) | open | Forecasting query arrival, mix, and shape far enough ahead to act, with calibrated uncertainty under regime change. |
| [Workload Compression & Representativeness](./workload-compression.md) | partially-solved | Compressing a trace to a small representative workload with provable bounds on the design decisions it induces. |
| [Safe Online Action Deployment](./safe-action-deployment.md) | open | Applying tuning actions on live systems with bounded worst-case regression risk and guaranteed rollback. |
| [Control-Loop Stability & Oscillation](./control-loop-stability.md) | open | Preventing thrashing/oscillation when a feedback controller repeatedly creates and drops the same structures. |
| [Credit Assignment Across Actions](./action-credit-assignment.md) | open | Attributing observed performance change to the responsible autonomous action amid concurrent changes and noise. |
| [Counterfactual Action Evaluation](./counterfactual-evaluation.md) | open | Estimating the effect of an action not taken (or to be taken) from logged, non-randomized production data. |
| [Exploration Cost on Production Systems](./production-exploration-cost.md) | open | Bounding the latency/SLA damage of exploratory actions a self-driving agent must take to learn online. |
| [Action-Planning Horizon & Sequencing](./action-planning-horizon.md) | open | Planning ordered sequences of design changes over time, accounting for build cost and transient states. |
| [Multi-Objective Autonomous Tuning](./multi-objective-tuning.md) | partially-solved | Tuning under conflicting objectives (latency, throughput, cost, energy) with principled Pareto navigation. |
| [SLA-Constrained Self-Tuning](./sla-constrained-tuning.md) | open | Guaranteeing per-tenant SLAs as hard constraints while an autonomous controller optimizes a global objective. |
| [Verifiable Safety of Control Loops](./verifiable-control-safety.md) | open | Formal guarantees (invariants, reachability) that an autonomous controller never drives the DB into unsafe states. |
| [Reward / Objective Specification](./reward-specification.md) | open | Specifying a tuning objective that captures true operator intent without reward hacking or perverse optima. |
| [Forecast-Driven Resource Provisioning](./forecast-resource-provisioning.md) | empirically-open | Autoscaling compute/memory/storage ahead of demand from workload forecasts with bounded over/under-provisioning. |
| [Cold-Start & Few-Shot Tuning](./cold-start-tuning.md) | open | Reaching good configurations on a new database/workload with little or no historical observation. |
| [Cross-System Transfer of Policies](./cross-system-transfer.md) | empirically-open | Transferring self-driving policies across DBMS engines, versions, and hardware without full retraining. |
| [Observability & Workload Modeling Granularity](./observability-granularity.md) | open | What must be measured, and at what granularity, for a controller to act correctly without crushing overhead. |
| [Concept Drift Detection for Triggers](./drift-detection-triggers.md) | open | Detecting when forecasts/models have degraded enough to re-plan, with formal staleness/false-trigger bounds. |
| [Concurrency Control for Online Reconfiguration](./online-reconfiguration-concurrency.md) | open | Applying schema/index/partition changes concurrently with live transactions without blocking or correctness loss. |
| [Benchmarking & Reproducible Evaluation](./autonomous-benchmarking.md) | empirically-open | Workloads, metrics, and protocols that fairly compare self-driving agents against strong human/heuristic baselines. |
| [Human-in-the-Loop & Trust Calibration](./human-in-the-loop.md) | open | When to defer to operators, how to explain proposed actions, and how to calibrate operator trust over time. |
| [Adversarial Robustness of Self-Driving DBs](./adversarial-robustness.md) | open | Resilience of forecasting and tuning to crafted workloads that induce harmful or costly autonomous actions. |
| [Multi-Tenant Shared-Resource Tuning](./multi-tenant-tuning.md) | open | Autonomous tuning under shared resources where one tenant's actions externalize cost onto others. |
| [End-to-End Self-Driving Architecture](./end-to-end-architecture.md) | open | A unified control architecture coordinating forecasting, planning, action, and monitoring as composable, verifiable parts. |

---
[← Back to taxonomy](../../TAXONOMY.md)
