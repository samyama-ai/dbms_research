# Elastic scaling without transaction stalls

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/elastic-scaling-no-stalls` · **Status:** empirically-open

## 1. Problem Statement
Add or remove nodes (and the data ranges they own) from a running distributed SQL cluster *without aborting, blocking, or visibly stalling in-flight distributed transactions*, while preserving the cluster's isolation level (serializable or SI) and its consistency guarantees throughout the membership change.

- **Decision variant.** Given a transactional protocol and a rebalancing plan, decide whether the plan can execute with *zero* forced aborts and bounded added latency.
- **Optimization variant.** Minimize peak tail-latency degradation (or maximize sustained goodput) during a scale event subject to a data-movement deadline.
- **Online variant.** Choose, online, which ranges to move and when, under an adversarial or stochastic workload, to minimize total transaction disruption.

The core tension: moving a key range changes which node is the leaseholder/coordinator for keys that open transactions may read or write; naive handoff forces those transactions to retry. The goal is a *non-stalling* ownership transfer.

## 2. Mathematical Foundations
Model the keyspace as ranges $R_1,\dots,R_m$ each with an owner (Raft leaseholder) $\text{own}(R_k)$. A transaction $T$ touches a set $K(T)$ of keys spanning ranges $\rho(T)=\{R_k : K(T)\cap R_k \neq \emptyset\}$. A scale event is a sequence of ownership transitions $\text{own}(R_k): n_a \to n_b$.

Correctness during transfer reduces to maintaining a single *linearizable owner* per key at all times — formalized as a **lease/epoch invariant**: at most one node holds a valid lease for $R_k$ at epoch $e$, and reads/writes carry the epoch so stale-owner operations are rejected. Non-stalling requires a *lease handoff* primitive that (i) drains or forwards in-flight ops and (ii) overlaps old and new owner during a quiescence-free window.

This connects to **online bipartite matching / load balancing** (assign ranges to nodes minimizing movement and conflict, an NP-hard partitioning objective) and to **consensus reconfiguration** theory: changing a Raft/Paxos configuration safely requires a joint-consensus or single-server-change protocol whose correctness is the membership-change problem. Competitive analysis frames the online placement as minimizing $\sum_t \text{disruption}(t)$ vs. an offline optimum.

## 3. State of the Art (SOTA)
- **Systems-SOTA.** Spanner/F1, CockroachDB, YugabyteDB, and TiDB perform online range splits/merges and lease transfers; they move data via Raft snapshots + log catch-up and transfer leases without typically aborting, but cross-range distributed transactions can still hit retries (e.g., uncertainty/transaction-record relocation). Vitess/MySQL sharding does live resharding with cutover. VoltDB/H-Store elastic work (Squall, Elmore et al., SIGMOD 2015) explicitly studies live reconfiguration minimizing migration impact.
- **Theory-SOTA.** Raft membership change (Ongaro & Ousterhout, ATC 2014) and Vertical/Stoppable Paxos give safe reconfiguration. Albatross/Zephyr (Elmore et al.) provide live migration for multi-tenant databases with bounded downtime.

## 4. Upper Bound
Squall and Zephyr achieve live reconfiguration with *sub-second* or near-zero unavailability and bounded latency spikes; Raft single-server changes complete in $O(1)$ consensus rounds plus data-transfer time $O(|R_k|/B)$ for bandwidth $B$. Best-known guarantees give *bounded added latency and zero downtime* but not *provably zero aborts* for arbitrary multi-range transactions — transactions whose keys straddle a moving range may still abort in the worst case.

## 5. Lower Bound
Reconfiguration inherits consensus lower bounds: a safe configuration change cannot complete during a partition that isolates a quorum (CAP). Any protocol guaranteeing a single owner per key across a transition needs at least one consensus decision, costing $\Omega(1)$ round-trips on the critical path. Choosing an optimal data placement to minimize cross-node (and thus transfer-affected) transactions is NP-hard (graph/hypergraph partitioning, Schism-style). There is no known protocol that guarantees zero aborts for *all* concurrent distributed transactions during an arbitrary topology change without unbounded blocking.

## 6. The Gap
Systems demonstrate *empirically* low disruption, but there is no protocol with a *proof* of zero forced aborts plus bounded tail latency for arbitrary workloads and topology changes. The gap is between "rarely stalls in benchmarks" and "provably never stalls in-flight transactions." Closing it likely requires an ownership-handoff primitive with formal non-blocking guarantees (perhaps via transaction forwarding or deterministic re-routing) plus a tight online placement competitive ratio.

## 7. Current Research (as of June 2026)
Directions: disaggregated/shared-storage architectures (Aurora, Neon, AlloyDB) that decouple compute scaling from data movement, sidestepping range handoff *(frontier — verify)*; learned and workload-driven autosharding; serverless elastic OLTP with sub-second cold-add. The CMU (Pavlo) and Elmore (UChicago) lineage, and the CockroachDB/TiDB engineering teams are active. *(frontier — verify)* recent VLDB/SIGMOD 2025 papers report "stall-free rebalancing" via lease pipelining, but formal zero-abort guarantees remain unpublished.

## 8. Future Work
- A non-blocking ownership-transfer primitive with a machine-checked zero-abort proof.
- Competitive online placement minimizing disruption with provable regret.
- Disaggregated-storage designs where elasticity never touches transaction ownership.

## 9. Key References
- **[Foundational]** Ongaro, Ousterhout. *In Search of an Understandable Consensus Algorithm (Raft).* USENIX ATC, 2014. — [USENIX](https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro)
- **[SOTA]** Elmore, Arora, Taft, Pavlo, Agrawal, El Abbadi. *Squall: Fine-Grained Live Reconfiguration for Partitioned Main Memory Databases.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2723726)
- **[SOTA]** Elmore, Das, Agrawal, El Abbadi. *Zephyr: Live Migration in Shared Nothing Databases for Elastic Cloud Platforms.* SIGMOD, 2011. — [DOI](https://doi.org/10.1145/1989323.1989356)
- **[SOTA]** Taft et al. *CockroachDB: The Resilient Geo-Distributed SQL Database.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3386134)
- **[Foundational]** Curino, Jones, Zhang, Madden. *Schism: a Workload-Driven Approach to Database Replication and Partitioning.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920853)

## 10. Worked Example

A 3-node cluster owns range $R_5 = [\texttt{k500}, \texttt{k600})$ on node $n_a$ (Raft leaseholder, epoch $e{=}7$). We add node $n_b$ and transfer ownership of $R_5$.

Trace of a non-stalling lease handoff while transaction $T$ (reading `k540`, `k710`) is in flight:

1. $n_b$ catches up via a Raft snapshot + log replay of $R_5$ ($O(|R_5|/B)$ time).
2. $n_a$ proposes a single-server lease transfer through Raft; on commit the epoch bumps to $e{=}8$ and $n_b$ becomes leaseholder. One consensus decision — the $\Omega(1)$ critical-path round.
3. $T$'s read of `k540` arrives at $n_a$ stamped with stale epoch $e{=}7$; $n_a$ rejects-and-forwards to $n_b$ rather than aborting. $T$ re-issues at $e{=}8$ and proceeds.

The lease/epoch invariant holds throughout: exactly one valid leaseholder per epoch. The residual risk is `k710` on a *second* moving range — if both straddle $T$, worst-case the transaction record relocation can still force a retry, which is precisely why a provable zero-abort guarantee remains open.

---
*Part of the [DBMS Research catalog](../../README.md).*
