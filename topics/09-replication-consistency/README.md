# Replication & Consistency

Replicated data stores trade off consistency, availability, and latency under the constraints of the CAP and PACELC theorems, and a large design space sits between strong serializability and pure eventual consistency. This topic catalogs open and hard problems spanning the theory of consistency models, conflict-free replicated data types (CRDTs), causal and eventual consistency, anti-entropy and reconciliation, read/write quorum systems, and the systems engineering needed to make these guarantees efficient and verifiable at scale.

| Problem | Status | Scope |
|---------|--------|-------|
| [Tight metadata lower bounds for causal consistency](./causal-consistency-metadata-lower-bounds.md) | open | Establishing tight worst-case bounds on the metadata each message/version must carry to guarantee causal consistency under partial replication. |
| [Space-optimal CRDTs with garbage collection](./crdt-space-optimal-gc.md) | open | Designing CRDTs whose tombstone/metadata overhead is provably bounded and safely reclaimable without coordination. |
| [Verifying convergence of arbitrary CRDT designs](./crdt-convergence-verification.md) | partially-solved | Automatically proving strong eventual consistency (commutativity/associativity/idempotence) for user-defined replicated data types. |
| [Expressiveness limits of coordination-free computation](./coordination-free-expressiveness.md) | partially-solved | Characterizing exactly which queries/computations are computable monotonically without coordination (CALM frontier and its decidability). |
| [Optimal anti-entropy reconciliation bandwidth](./anti-entropy-optimal-bandwidth.md) | open | Minimizing communication for set/state reconciliation between replicas as a function of the symmetric difference and error tolerance. |
| [Dynamic quorum reconfiguration without stalls](./dynamic-quorum-reconfiguration.md) | partially-solved | Changing quorum membership/sizes online while preserving consistency and availability with no read/write pause. |
| [Latency-optimal quorum placement on real topologies](./quorum-placement-latency-optimal.md) | empirically-open | Choosing replica/quorum placement to minimize tail latency under realistic, time-varying WAN latency matrices. |
| [Tunable consistency with provable SLA guarantees](./tunable-consistency-sla.md) | open | Mapping per-operation consistency knobs to enforceable, composable staleness/latency SLA guarantees. |
| [Bounded-staleness reads with tight bounds](./bounded-staleness-tight-bounds.md) | partially-solved | Providing reads bounded by t time / k versions with minimal metadata and provably tight staleness under failures. |
| [Mixing strong and weak consistency safely](./mixed-consistency-safety.md) | partially-solved | Programming models and static analyses that let strong and weak operations coexist without invariant violations. |
| [Invariant-preserving eventual consistency](./invariant-preserving-eventual-consistency.md) | partially-solved | Statically determining which application invariants survive concurrent updates and inserting minimal coordination (RedBlue/Indigo style). |
| [Genuine partial replication with causal+ consistency](./partial-replication-causal-plus.md) | open | Achieving causal consistency where replicas store only data subsets and exchange no metadata about keys they do not hold. |
| [Read-your-writes across heterogeneous sessions](./session-guarantees-heterogeneous.md) | partially-solved | Enforcing session guarantees (RYW, monotonic reads/writes) across client migration, sharding, and caching layers. |
| [Convergent secondary indexes over CRDTs](./crdt-secondary-indexes.md) | open | Maintaining queryable, convergent secondary indexes/materialized views derived from replicated CRDT state. |
| [Transactional causal consistency at scale](./transactional-causal-consistency.md) | partially-solved | Supporting multi-key transactions with causal+ guarantees while keeping throughput and metadata practical. |
| [Conflict resolution beyond last-writer-wins](./semantic-conflict-resolution.md) | open | Principled, application-semantic merge functions with formal correctness rather than timestamp-based LWW data loss. |
| [Quantifying observable anomalies under weak consistency](./weak-consistency-anomaly-quantification.md) | empirically-open | Measuring and predicting the rate/severity of consistency anomalies users actually observe in production workloads. |
| [Optimal read/write quorum systems for skewed workloads](./quorum-systems-skewed-workloads.md) | open | Constructing quorum systems minimizing load/availability cost under non-uniform access and failure correlation. |
| [Consistency model checking at runtime](./runtime-consistency-checking.md) | partially-solved | Efficiently checking observed histories against a target consistency model online with low overhead. |
| [Complexity of verifying consistency from histories](./consistency-verification-complexity.md) | partially-solved | Settling the computational complexity of deciding whether a history satisfies causal/PRAM/snapshot/serializable models. |
| [Hybrid logical clocks with bounded drift guarantees](./hlc-bounded-drift.md) | partially-solved | Clock schemes giving causality tracking plus close-to-physical-time ordering with provable size/drift bounds. |
| [Self-tuning replication factor and quorum sizing](./adaptive-replication-factor.md) | empirically-open | Online control loops that adapt replication factor and R/W quorum sizes to durability, latency, and cost targets. |
| [Geo-replicated multi-master conflict minimization](./geo-multimaster-conflict-minimization.md) | open | Reducing cross-region write conflicts via placement, partitioning, and scheduling without serializing writers. |
| [Delta-state CRDTs with optimal delta propagation](./delta-crdt-optimal-propagation.md) | partially-solved | Computing and shipping minimal delta-groups for state-based CRDTs with anti-entropy and causal stability. |
| [Causal stability and safe garbage collection](./causal-stability-gc.md) | open | Determining when causal metadata/tombstones are globally stable and reclaimable under churn and partitions. |
| [Consistency-aware caching at the edge](./edge-cache-consistency.md) | empirically-open | Providing defined consistency (session/causal/bounded) through multi-tier edge caches without central coordination. |
| [Byzantine-tolerant eventual consistency](./byzantine-eventual-consistency.md) | open | CRDT/anti-entropy protocols that converge correctly despite equivocating or malicious replicas. |
| [Energy/cost-aware PACELC operating points](./pacelc-cost-aware-tuning.md) | empirically-open | Choosing per-workload PACELC operating points that jointly optimize latency, consistency, and dollar/energy cost. |
| [Formal composition of consistency guarantees](./consistency-composition-theory.md) | open | A compositional theory predicting end-to-end guarantees when layers/services with different models are stacked. |
| [Lower bounds on staleness-availability-latency tradeoffs](./staleness-availability-latency-bounds.md) | open | Proving tight three-way tradeoff bounds extending CAP/PACELC to quantitative staleness, availability, and latency. |

> Back to [Taxonomy](../../TAXONOMY.md)
