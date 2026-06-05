# Consensus & Coordination

Consensus and coordination protocols are the agreement substrate beneath replicated databases, distributed transactions, and fault-tolerant services: Paxos/Raft/EPaxos for state-machine replication, 2PC/3PC for atomic commit, leases and locks for mutual exclusion, group membership and failure detectors for liveness, and Byzantine agreement for adversarial settings. The field sits at the intersection of deep impossibility theory (FLP, lower bounds on rounds/messages/processes) and brutal systems engineering (latency tails, reconfiguration, geo-distribution, hardware acceleration). The problems below span both: complexity/expressiveness bounds that remain genuinely open, and engineering challenges where no protocol yet dominates across the relevant cost dimensions.

| Problem | Status | Scope |
|---------|--------|-------|
| [Tight Latency Bounds for Geo-Consensus](./geo-consensus-latency-bounds.md) | open | Whether wide-area consensus can beat one-RTT-to-quorum without sacrificing fault tolerance under realistic asymmetric network delays. |
| [Leaderless Consensus Conflict Scaling](./leaderless-conflict-scaling.md) | partially-solved | How dependency-graph size and contention degrade EPaxos-style leaderless protocols as conflict rates rise. |
| [Reconfiguration Without Quorum Stalls](./reconfiguration-without-stalls.md) | open | Safe membership changes that never pause command processing nor lose liveness across overlapping configurations. |
| [Optimal Flexible Quorum Systems](./flexible-quorum-optimality.md) | partially-solved | Characterizing the full Pareto frontier of read/write quorum intersections under heterogeneous failure and latency models. |
| [Byzantine Consensus Message Complexity](./byzantine-message-complexity.md) | open | Closing the gap between O(n) and O(n^2) authenticated message bounds for partially-synchronous BFT with optimal resilience. |
| [Adaptive Failure Detector Accuracy](./adaptive-failure-detectors.md) | empirically-open | Failure detectors that provably track changing network conditions while bounding both false positives and detection latency. |
| [Weakest Failure Detector for Commit](./weakest-fd-atomic-commit.md) | partially-solved | Pinpointing the exact failure-detection power required for non-blocking atomic commit versus consensus. |
| [Non-Blocking Atomic Commit at Scale](./nonblocking-atomic-commit.md) | open | Atomic commit that tolerates coordinator failure without 3PC's message-round and assumption costs in real deployments. |
| [Deterministic FLP Circumvention](./flp-deterministic-circumvention.md) | open | How much synchrony or randomness is truly minimal to solve consensus deterministically in practice. |
| [Lease Safety Under Clock Drift](./lease-safety-clock-drift.md) | partially-solved | Bounding the unsafe window of leases when bounded-drift clock assumptions are violated adversarially. |
| [Consensus Throughput vs Tail Latency](./throughput-tail-latency-tradeoff.md) | empirically-open | The fundamental tension between batching for throughput and per-command tail latency in replicated logs. |
| [Quorum Reads Without Round Trips](./local-quorum-reads.md) | partially-solved | Serving linearizable reads from a single replica without a quorum round or unbounded lease assumptions. |
| [Cross-Shard Consensus Composition](./cross-shard-consensus.md) | open | Composing per-shard consensus with cross-shard atomic commit while preserving strict serializability cheaply. |
| [RDMA-Accelerated Consensus Limits](./rdma-consensus-limits.md) | empirically-open | Whether one-sided RDMA can break classic message-round lower bounds and what failure semantics that costs. |
| [Hybrid BFT-CFT Protocols](./hybrid-bft-cft.md) | open | Protocols that pay BFT cost only when Byzantine faults actually occur and degrade gracefully otherwise. |
| [Consensus Under Network Partitions](./partition-tolerant-progress.md) | partially-solved | Maximizing useful minority-partition progress without violating linearizability when partitions heal. |
| [Formal Verification of Live Reconfig](./verified-reconfiguration.md) | partially-solved | Machine-checked safety and liveness proofs for production reconfiguration code, not just abstract protocols. |
| [Randomized Consensus Round Complexity](./randomized-round-complexity.md) | open | Closing expected-round gaps for asynchronous randomized Byzantine agreement against adaptive adversaries. |
| [Witness/Flexible Replica Cost Models](./witness-replica-cost.md) | partially-solved | When witness/learner replicas reduce cost without hidden liveness or durability penalties. |
| [Speculative Execution Rollback Bounds](./speculative-execution-bounds.md) | empirically-open | Bounding wasted work and rollback cascades when consensus commits speculatively before agreement. |
| [Membership Under Asymmetric Failures](./asymmetric-failure-membership.md) | open | Group membership that handles gray failures and asymmetric reachability without flapping or split views. |
| [Consensus Energy/Cost Optimality](./consensus-energy-cost.md) | empirically-open | Minimizing dollar/energy cost of consensus on cloud pricing, not just message or round counts. |
| [Heterogeneous-Latency Leader Election](./latency-aware-leader-election.md) | partially-solved | Electing leaders that minimize expected client latency under skewed geo-distributed access patterns. |
| [Consensus for Disaggregated Memory](./disaggregated-memory-consensus.md) | open | Agreement protocols when state lives in shared remote memory rather than per-node logs. |
| [Bounded Staleness Coordination](./bounded-staleness-coordination.md) | partially-solved | Coordination primitives giving tunable, provable staleness bounds between strong and eventual consistency. |
| [Asynchronous BFT Throughput Limits](./async-bft-throughput.md) | empirically-open | How close asynchronous (DAG-based) BFT can get to network-bandwidth-bound throughput at scale. |
| [Consensus Liveness Under Adaptive Attacks](./adaptive-attack-liveness.md) | open | Guaranteeing liveness when an adversary adaptively targets leaders/quorums within partial synchrony. |
| [Self-Tuning Consensus Parameters](./self-tuning-consensus.md) | empirically-open | Online tuning of batch size, timeouts, and quorum choice without manual operator intervention. |
| [Lower Bounds for Reconfiguration](./reconfiguration-lower-bounds.md) | open | Tight message/round lower bounds for safe online membership change in asynchronous systems. |
| [Consensus-Free Coordination Avoidance](./coordination-avoidance.md) | partially-solved | Statically certifying which operations can skip consensus entirely while preserving application invariants. |

---
[← Back to taxonomy](../../TAXONOMY.md)
