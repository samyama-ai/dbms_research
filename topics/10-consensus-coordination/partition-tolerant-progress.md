---
id: 10-consensus-coordination/partition-tolerant-progress
title: "Consensus Under Network Partitions"
topic: 10-consensus-coordination
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Consensus Under Network Partitions

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/partition-tolerant-progress` · **Status:** partially-solved

## 1. Problem Statement
When a network partition splits replicas, classic quorum consensus lets only the majority side make progress; the minority side is blocked entirely. Yet some useful work — reads of recently-quiesced data, commutative/escrow operations, locally-confined updates — could safely proceed in the minority *if* the system can guarantee that, **when the partition heals, the merged history is still linearizable (or the agreed weaker isolation level) with no lost or conflicting commits.** The problem: **maximize useful minority-partition progress subject to recovering a linearizable global history on heal.**

Variants:
- **Decision:** Given an operation and current state, can the minority side certify *now* that committing it locally will never conflict with majority-side commits, for all admissible heal orders?
- **Optimization:** Maximize the fraction (or value) of operations admissible in the minority without violating the target consistency level.
- **Trade-off characterization:** Map the Pareto frontier between consistency strength and minority availability — a refinement of CAP into a quantitative spectrum.

This is the operational, quantitative version of the CAP theorem: CAP says you cannot have C and A under P; the question is *how much* A is recoverable while keeping the C you actually need.

## 2. Mathematical Foundations
CAP (Gilbert–Lynch, 2002) formalizes: no register can be simultaneously linearizable (C) and available (A) under partitions (P). The PACELC refinement (Abadi) adds the no-partition latency/consistency trade-off. Quorum systems require read/write quorums to intersect ($|Q_r|+|Q_w|>n$), so at most one partition holds a write quorum — only that side may write under linearizability.

Escrow/commutativity theory (the "I-confluence" result of Bailis et al., VLDB 2015) precisely characterizes which operations preserve a global invariant *without* coordination: a set of transactions is invariant-confluent for invariant $I$ iff their effects can be merged in any order while preserving $I$. I-confluent operations may proceed in *any* partition safely. CRDTs (Shapiro et al.) give a lattice/join-semilattice structure $(S,\sqcup)$ guaranteeing convergent merge. The minority-progress question is then: maximize the admissible operation set $A$ such that every $a\in A$ is I-confluent w.r.t. the application invariant *and* the post-heal serialization order can place $a$ consistently with majority commits.

## 3. State of the Art (SOTA)
- **CAP/PACELC** (Gilbert–Lynch 2002; Abadi 2012): the impossibility and its refinement.
- **CRDTs** (Shapiro, Preguiça, Baquero, Zawirski, 2011): minority-side updates that always converge — used in Riak, Redis, Azure Cosmos DB.
- **Invariant Confluence** (Bailis et al., VLDB 2015): static decision procedure for which transactions need coordination; **Blazes / Bloom^L** (Alvaro, Hellerstein) confluence analysis.
- **Escrow transactions** (O'Neil, TODS 1986) and **Generic Broadcast / commutativity-aware replication** for partial-order agreement. Systems like **Cassandra/Dynamo** (eventual) vs **Spanner** (CP) bracket the spectrum; **PNUTS/Pileus** offer tunable consistency SLAs. *(frontier — verify latest mixed-consistency engines.)*

## 4. Upper Bound
For I-confluent / CRDT operations, **100% availability on every partition side with no coordination** is achievable, and merge on heal is provably convergent and invariant-preserving (Bailis 2015; Shapiro 2011). For mixed workloads, "RedBlue consistency" (Li et al., OSDI 2012) labels operations *blue* (commutative, available everywhere) or *red* (need coordination), achieving the maximal blue set for a given invariant; **Quelea/MixT/IPA** push tunable per-operation consistency. This holds in the asynchronous message-passing model with arbitrary partitions, *only* for the certified-commutative subset.

## 5. Lower Bound
CAP (Gilbert–Lynch): any operation that must be linearizable cannot be available on the minority side under partition — a hard impossibility in the asynchronous model. More finely, an operation that is *not* I-confluent w.r.t. the invariant *provably requires coordination* (Bailis et al. prove I-confluence is both necessary and sufficient), so no protocol can safely run non-confluent ops in the minority. FLP further forbids deterministic agreement to resolve conflicts in pure asynchrony.

## 6. The Gap
The boundary is *characterized* (I-confluence is the exact line), which is why this is "partially-solved": we know precisely which operations are safe. The open part is (a) making the I-confluence/commutativity test *automatic, sound, and complete* for rich application invariants and SQL workloads (currently semi-automatic, conservative), and (b) handling operations near the boundary by *transforming* them (escrow, reservations, tokens) to push more of the workload into the available set — the optimization frontier of "how much red can be turned blue."

## 7. Current Research (as of June 2026)
- Automated invariant-confluence analysis over SQL/ORM workloads and verified CRDT compilers. *(frontier — verify.)*
- Reservation/escrow synthesis to mechanically convert coordinating operations into partition-available ones (Hydroflow/Anna lineage, Hellerstein group). *(frontier — verify.)*
- Mixed-consistency type systems (MixT, IPA) and conflict-free transactional bundles.
- Groups: UC Berkeley (Hellerstein, Bailis lineage), MPI-SWS (Rodrigues, CRDTs), Cornell (Myers, MixT), INRIA (Shapiro, Preguiça).

## 8. Future Work
- Sound-and-complete static analyzers for invariant confluence on production schemas.
- Quantitative CAP: provable bounds on the *value* of recoverable minority availability given an invariant.
- Heal-time conflict-resolution that minimizes user-visible compensation/rollback.

## 9. Key References
- **[Foundational]** Seth Gilbert, Nancy Lynch. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)
- **[Foundational]** Marc Shapiro, Nuno Preguiça, Carlos Baquero, Marek Zawirski. *Conflict-Free Replicated Data Types.* SSS, 2011. — [DOI](https://doi.org/10.1007/978-3-642-24550-3_29)
- **[SOTA]** Peter Bailis et al. *Coordination Avoidance in Database Systems (Invariant Confluence).* VLDB, 2015. — [arXiv](https://arxiv.org/abs/1402.2237)
- **[SOTA]** Cheng Li et al. *Making Geo-Replicated Systems Fast as Possible, Consistent when Necessary (RedBlue).* OSDI, 2012. — [USENIX](https://www.usenix.org/conference/osdi12/technical-sessions/presentation/li)
- **[Survey]** Daniel Abadi. *Consistency Tradeoffs in Modern Distributed Database System Design (PACELC).* IEEE Computer, 2012. — [DOI](https://doi.org/10.1109/MC.2012.33)

## 10. Worked Example

A bank account replicated across 5 nodes, invariant $I$: *balance $\ge 0$*. A network partition splits the replicas into a majority $\{A,B,C\}$ and a minority $\{D,E\}$. Start: balance $= 100$.

**Deposit** `+50` is I-confluent: applied in any order it only raises the balance, never breaking $I\,(\ge 0)$. So $D$ can accept it locally during the partition; on heal, merging $+50$ from the minority with any majority history is safe. Minority availability for deposits: **100%, no coordination**.

**Withdraw** `-80` is *not* I-confluent: suppose majority $\{A,B,C\}$ withdraws `-80` (balance $100 \to 20$) while minority $\{D,E\}$ independently withdraws `-80` ($100 \to 20$). On heal, both apply: $100 - 80 - 80 = -60 < 0$ — invariant violated. By Bailis et al., withdrawal therefore *provably requires coordination* and cannot run on the minority.

**Pushing red→blue:** give each side an *escrow* reservation of $50$. Now each partition may withdraw up to its $50$ budget without coordination, and the merge can never overdraw — converting a red operation into a partition-available blue one, exactly the optimization frontier of Section 6.

---
*Part of the [DBMS Research catalog](../../README.md).*
