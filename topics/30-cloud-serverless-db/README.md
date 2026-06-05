# Cloud & Serverless Databases

Cloud and serverless databases disaggregate storage from compute, scale resources elastically with demand, and multiplex many tenants over shared infrastructure while billing for fine-grained usage. The defining tensions are sustaining transactional and analytical performance over high-latency remote storage, scaling to and from zero without cold-start penalties, isolating tenants under contention, and letting cost become a first-class objective the optimizer can reason about.

This catalog collects 30 research-grade open problems at the intersection of theory (complexity, bounds, expressiveness) and systems (real engineering challenges studied at PODS/SIGMOD/VLDB/ICDE/CIDR/EDBT).

| Problem | Status | Scope |
|---------|--------|-------|
| [Optimal storage-compute disaggregation boundary](./disaggregation-boundary.md) | open | Where to place each operator/function across the compute-storage divide to minimize data movement under remote-access latency. |
| [Provable cold-start lower bounds](./cold-start-lower-bounds.md) | open | Fundamental bounds relating scale-to-zero cost, state size, and the unavoidable latency of resuming a paused database engine. |
| [Cost-optimal autoscaling policies](./cost-optimal-autoscaling.md) | empirically-open | Online resource-allocation policies that provably minimize dollar cost under SLO constraints with unknown future load. |
| [Multi-tenant performance isolation guarantees](./multitenant-isolation-guarantees.md) | open | Schedulers that bound a tenant's worst-case latency degradation from noisy neighbors on shared compute and buffer pools. |
| [Cost-based execution with a dollar objective](./dollar-cost-optimization.md) | open | A query optimizer cost model whose objective is monetary spend across heterogeneous priced resources rather than abstract cost units. |
| [Cache coherence over disaggregated storage](./disaggregated-cache-coherence.md) | empirically-open | Maintaining a coherent buffer cache across many stateless compute nodes reading shared remote log-structured storage. |
| [Elastic transaction processing without downtime](./elastic-oltp-repartition.md) | empirically-open | Repartitioning and rescaling an OLTP system live while preserving serializability and bounded transaction latency. |
| [Serverless OLAP shuffle without warm workers](./serverless-shuffle.md) | partially-solved | Exchanging intermediate data among ephemeral, non-addressable function workers that cannot communicate directly. |
| [Disaggregated-memory transaction protocols](./disaggregated-memory-txn.md) | empirically-open | Concurrency control and recovery when working memory itself is a remote, RDMA-attached, failure-independent resource. |
| [Pay-per-query pricing-truthfulness](./pricing-truthfulness.md) | open | Pricing functions for query-as-a-service that are incentive-compatible and robust to tenants gaming the cost estimator. |
| [Predictive vs. reactive elasticity bounds](./predictive-elasticity-bounds.md) | open | The competitive-ratio gap between forecasting-driven and purely reactive scaling for bursty, heavy-tailed workloads. |
| [Right-sizing serverless function memory](./function-right-sizing.md) | empirically-open | Choosing per-invocation memory/CPU that minimizes cost-latency product for DB operators with data-dependent footprints. |
| [Cross-region replicated cloud-database consistency](./cross-region-consistency.md) | open | Achieving low-latency reads with bounded staleness across geo-distributed replicas under per-region pricing asymmetry. |
| [Log-as-the-database durability bounds](./log-is-database.md) | partially-solved | Formalizing the latency/throughput limits of shipping only redo log to storage that materializes pages independently. |
| [Workload-forecasting for scale-to-zero](./workload-forecasting-scaling.md) | empirically-open | Predicting idle and burst intervals accurately enough to pause/resume databases without violating tail-latency SLOs. |
| [Fair resource allocation across tenants](./fair-multitenant-allocation.md) | open | Allocation rules that are simultaneously fair, work-conserving, and SLO-respecting under fluctuating per-tenant demand. |
| [Cost-aware materialized-view and cache placement](./cost-aware-view-caching.md) | open | Deciding what to materialize/cache when storage, recomputation, and egress each carry separate cloud prices. |
| [Stateful serverless query checkpointing](./serverless-checkpointing.md) | empirically-open | Cheap, frequent checkpoint/restore of long analytical queries to survive function timeouts and spot reclamation. |
| [Spot-instance-resilient query execution](./spot-instance-resilience.md) | empirically-open | Executing distributed queries on preemptible nodes with bounded re-execution cost under stochastic reclamation. |
| [Tenant-aware buffer-pool partitioning theory](./tenant-buffer-partitioning.md) | partially-solved | Optimal shared-cache partitioning across tenants with distinct hit-rate curves and SLA-weighted miss penalties. |
| [Disaggregated-storage I/O cost models](./remote-io-cost-model.md) | partially-solved | Optimizer cost models capturing remote-storage latency, parallelism, request pricing, and prefetch effectiveness. |
| [Elastic index build and maintenance](./elastic-index-maintenance.md) | empirically-open | Building and incrementally maintaining indexes whose compute scales independently of the serving tier. |
| [Serverless join-algorithm selection](./serverless-join-selection.md) | open | Choosing join strategies when worker count, network, and intermediate-result materialization are all elastic and priced. |
| [Cold-data tiering with access-cost guarantees](./cold-data-tiering.md) | partially-solved | Online tiering across hot/warm/cold storage classes that bounds expected retrieval cost under unknown access patterns. |
| [Multi-tenant query-result and plan sharing](./multitenant-work-sharing.md) | partially-solved | Safely sharing scans, intermediate results, and cached plans across tenants without leaking data or skewing billing. |
| [SLO-aware admission control under bursts](./slo-admission-control.md) | empirically-open | Admitting or shedding queries to protect tail-latency SLOs when aggregate demand transiently exceeds provisioned capacity. |
| [Disaggregated MVCC garbage collection](./disaggregated-mvcc-gc.md) | open | Reclaiming obsolete versions correctly when readers, writers, and the version store live on separate elastic tiers. |
| [Energy- and carbon-aware cloud query scheduling](./carbon-aware-scheduling.md) | empirically-open | Scheduling elastic database work to minimize carbon/energy cost while honoring latency SLOs across regions and time. |
| [Bin-packing tenants to minimize machines](./tenant-bin-packing.md) | open | Consolidating tenants onto the fewest nodes subject to SLO, isolation, and resource-correlation constraints. |
| [Verifiable billing for cloud query services](./verifiable-billing.md) | open | Cryptographic proofs that a serverless query's reported resource consumption and bill are accurate and non-inflated. |

---
[Back to taxonomy](../../TAXONOMY.md)
