---
id: 18-streaming-queries/elastic-rescaling-state-migration
title: "Elastic operator rescaling with state migration"
topic: 18-streaming-queries
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Elastic operator rescaling with state migration

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/elastic-rescaling-state-migration` · **Status:** empirically-open

## 1. Problem Statement
A stateful streaming operator is partitioned by key across $p$ parallel instances, each holding a shard of operator state (hash tables, windows, aggregates). When load changes, the system **rescales** to $p'$ instances, which requires **repartitioning the keyspace** and **migrating state** between instances. The problem: perform rescaling so that (i) results remain **correct** (exactly-once, no lost/duplicated keys, consistent watermarks), (ii) the **latency/throughput SLO is not violated** during migration, and (iii) the **volume of state moved** is minimized.

Decision variant: given a target parallelism change and a latency budget $\tau$, does a migration plan exist that never stalls processing beyond $\tau$? Optimization variants: minimize bytes moved (a partition-assignment problem), minimize peak latency spike, or minimize total reconfiguration time. The "empirically-open" status: production systems do this, but always with tradeoffs (stop-the-world pauses, or live migration with weaker guarantees) and no policy is provably optimal across all three objectives simultaneously.

## 2. Mathematical Foundations
Keyspace partitioning is typically **consistent hashing** or a **key-group** map (Flink's model: a fixed large number $g$ of key-groups assigned to instances). Rescaling = reassigning key-groups to instances; minimizing moved state under a balance constraint is a **load-balanced graph/partition assignment** problem — a variant of bin-packing / minimum-transfer repartitioning that is **NP-hard** in general, with consistent-hashing giving an $O(1/p)$ expected fraction moved.

Correctness rests on **epoch / barrier alignment**: migration must be serialized against the checkpoint/snapshot protocol (Chandy–Lamport-style, as in Flink's asynchronous barriers) so the moved state corresponds to a consistent cut. Live migration overlaps state transfer with processing; modeling the latency spike uses **queueing theory** (the migrating partition's backlog drains at the destination's service rate), and the **CAP/availability** tension appears as a pause-vs-staleness choice. Watermark/punctuation correctness requires that no key be simultaneously "owned" by two instances — a mutual-exclusion invariant over the keyspace.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** consistent hashing minimal-movement bounds; the snapshot-consistency framework (Chandy–Lamport) underpinning correctness.
- **Systems-SOTA:** **Apache Flink** key-groups + reactive/adaptive scheduler (stop-and-restart from checkpoint by default). **Megaphone** (Hoffmann et al., VLDB 2019) — fine-grained, latency-controlled live state migration on Timely Dataflow, minimizing latency spikes via small migration batches. **Dhalion** (Floratou et al., VLDB 2017) — policy/controller for self-regulating elasticity in Heron. **DS2** (Kalavri et al., OSDI 2018) — accurate auto-scaling controller computing true processing rates. **Rhino / ChronoStream** — live migration with reconfiguration guarantees.

## 4. Upper Bound
With consistent hashing / key-groups, an instance change from $p$ to $p'$ moves an **expected $O(|state|/\max(p,p'))$** fraction of state — near-minimal. **Megaphone** bounds the per-migration latency spike to a tunable constant by splitting a key-group's migration into many small "fluid" batches, achieving sub-second p99 impact while migrating GBs (Timely Dataflow model). DS2 reaches an accurate target parallelism in a single scaling step under its rate model, avoiding oscillation.

## 5. Lower Bound
Minimum-transfer rebalancing under a hard load-balance constraint is **NP-hard** (bin-packing reduction), so optimal migration plans are intractable in the worst case. By **FLP impossibility**, no asynchronous protocol can guarantee both progress (no stall) and consistency under arbitrary timing without some synchronization assumption — hence either a (bounded) pause or weaker freshness is unavoidable during reconfiguration. Any migration of $B$ bytes across links of bandwidth $\beta$ has an information-theoretic floor of $B/\beta$ transfer time, lower-bounding the reconfiguration window for large state.

## 6. The Gap
Movement-minimization and snapshot-correctness are individually well-understood; the **empirically-open** gap is the *joint* objective: provably minimizing latency disruption **and** moved bytes **and** preserving exactly-once, **online**, under live (non-stop) migration of very large (multi-GB) state. Megaphone shows latency control is achievable but does not give global optimality; auto-scaling controllers (DS2/Dhalion) decide *when/how much* to scale but treat migration cost as a black box. Closing it needs a unified model coupling the scaling controller, the partition-assignment optimizer, and the migration scheduler with end-to-end SLO guarantees.

## 7. Current Research (as of June 2026)
Active: serverless/cloud-native elastic streaming with disaggregated state stores enabling cheaper rescaling (state in remote KV / object storage so migration becomes re-pointing rather than copying) *(frontier — verify)*; learned/predictive auto-scaling controllers extending DS2; incremental, SLO-aware live migration for windowed-join state. Groups: ETH Zürich (Megaphone / Timely lineage, Roscoe/Hoffmann), KTH/Edinburgh (Kalavri — DS2), TU Berlin DIMA, and the Flink community (adaptive scheduler, disaggregated state).

## 8. Future Work
- A single optimizer jointly minimizing moved bytes, latency spike, and reconfiguration time with SLO guarantees.
- Disaggregated/remote state designs that make rescaling near-free, with consistency proofs.
- Predictive scaling that pre-migrates state ahead of load shifts.
- Formal verification of exactly-once across live migration + checkpointing.

## 9. Key References
- **[SOTA]** M. Hoffmann, A. Lattuada, F. McSherry, et al. *Megaphone: Latency-conscious State Migration for Distributed Streaming Dataflows.* VLDB, 2019. — [arXiv](https://arxiv.org/abs/1812.01371)
- **[SOTA]** V. Kalavri, J. Liagouris, M. Hoffmann, D. Dimitrova, et al. *Three Steps is All You Need: Fast, Accurate, Automatic Scaling Decisions (DS2).* OSDI, 2018. — [USENIX](https://www.usenix.org/conference/osdi18/presentation/kalavri)
- **[SOTA]** A. Floratou, A. Agrawal, B. Graham, S. Rao, K. Ramasamy. *Dhalion: Self-Regulating Stream Processing in Heron.* VLDB, 2017. — [DOI](https://doi.org/10.14778/3137765.3137786)
- **[Foundational]** K. M. Chandy, L. Lamport. *Distributed Snapshots: Determining Global States of Distributed Systems.* ACM TOCS, 1985. — [DOI](https://doi.org/10.1145/214451.214456)
- **[Foundational]** P. Carbone, S. Ewen, G. Fóra, S. Haridi, et al. *State Management in Apache Flink: Consistent Stateful Distributed Stream Processing.* VLDB, 2017. — [DOI](https://doi.org/10.14778/3137765.3137777)

## 10. Worked Example

Suppose a keyed aggregation uses $g=12$ key-groups, currently spread over $p=3$ instances (4 groups each):

| Instance | Key-groups |
|---|---|
| $I_0$ | 0,1,2,3 |
| $I_1$ | 4,5,6,7 |
| $I_2$ | 8,9,10,11 |

Load rises, so we rescale to $p'=4$. A balanced assignment gives 3 groups each. A *minimal-movement* plan keeps groups in place where possible and peels off only the surplus:

| Instance | New key-groups | Moved in |
|---|---|---|
| $I_0$ | 0,1,2 | — |
| $I_1$ | 4,5,6 | — |
| $I_2$ | 8,9,10 | — |
| $I_3$ | 3,7,11 | 3 (from $I_0$), 7 (from $I_1$), 11 (from $I_2$) |

Only 3 of 12 groups move, i.e. fraction $\tfrac{1}{4} = O(1/\max(p,p'))$, matching the consistent-hashing bound. During the cut, group 3 must be owned by exactly one of $I_0$/$I_3$ (mutual exclusion), so migration is serialized against a checkpoint barrier. If group 3 holds $B=200$ MB and the link runs at $\beta=1$ GB/s, the transfer floor is $B/\beta = 0.2$ s. Megaphone splits this into many small fluid batches so the p99 latency spike stays sub-second instead of a single 0.2 s stall.

---
*Part of the [DBMS Research catalog](../../README.md).*
