---
id: 09-replication-consistency/dynamic-quorum-reconfiguration
title: "Dynamic quorum reconfiguration without stalls"
topic: 09-replication-consistency
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Dynamic quorum reconfiguration without stalls

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/dynamic-quorum-reconfiguration` · **Status:** partially-solved

## 1. Problem Statement

A quorum-replicated store keeps data linearizable as long as every read quorum intersects every write quorum (the **intersection property**). Operators must change membership and quorum sizes online — to add/remove replicas, shrink a degraded majority, or rebalance — **without ever pausing reads/writes** and without violating consistency. Naive reconfiguration stalls: it stops the world, agrees on the new configuration, then resumes, sacrificing availability exactly when the system is already stressed.

The problem: **Change quorum membership and quorum sizes online while (a) preserving linearizability/consistency across the configuration switch, (b) maintaining availability with no read/write stall, and (c) tolerating failures and concurrent reconfigurations.**

- **Safety variant:** prove that no two operations in old/new configs observe inconsistent state across the handover.
- **Liveness/availability variant:** guarantee progress (no stall) under bounded asynchrony and $f$ failures, including during reconfiguration itself.
- **Optimization variant:** minimize the latency/round overhead and the window during which both configurations are active.

## 2. Mathematical Foundations

A configuration $C$ is a set of members with a **quorum system** $\mathcal{Q}(C)$ (e.g., majorities). Linearizability across a sequence $C_0 \to C_1 \to \dots$ requires a **cross-configuration intersection** discipline: an operation in $C_{i+1}$ must observe the effects of completed operations in $C_i$. Classical impossibilities frame the difficulty: **FLP** (no deterministic consensus under one crash in pure asynchrony) means agreeing on the next configuration cannot be both safe and live without partial synchrony or randomization; **CAP** forces an availability/consistency choice under partition during the switch.

State-machine-replication reconfiguration treats config changes as special log entries (Lamport's Paxos "$\alpha$"-bounded reconfiguration; Raft joint consensus). The intersection invariant generalizes to **Read-impose / Write-quorum** lattices and to the *abstract MWMR atomic register* model of RAMBO (Lynch & Shvartsman), where overlapping old/new configs are kept live until a **garbage-collection** step proves the old config is no longer needed. Vertical Paxos separates a *steady-state* quorum from a *reconfiguration master*, letting the master use a different (smaller) quorum to install configs.

## 3. State of the Art (SOTA)

- **Theory SOTA:** RAMBO / RAMBO-II (Lynch, Shvartsman; Gilbert, Lynch) — atomic MWMR memory with on-the-fly reconfiguration and old-config GC; Vertical Paxos (Lamport, Malkhi, Zhou, PODC 2009) — reconfiguration as a separate, lighter consensus layer. DynaStore (Aguilera, Keidar, Malkhi, Shraer, JACM 2011) — **reconfiguration without consensus**, using a weaker "speculating" object, sidestepping FLP for the config-change subproblem.
- **Systems SOTA:** Raft joint consensus / single-server changes (Ongaro & Ousterhout, 2014); Apache ZooKeeper dynamic reconfiguration (Shraer et al., USENIX ATC 2012); MongoDB/etcd online membership changes; Spanner/TrueTime Paxos-group movement. SMART and Matchmaker Paxos (Whittaker et al., 2021) reduce reconfiguration latency/coupling.

## 4. Upper Bound

DynaStore reconfigures **without consensus** (no FLP barrier for the config change itself), with each operation taking $O(1)$ communication rounds amortized and convergence to a unique config sequence under eventual stability. Vertical Paxos installs a new config in a single steady-state round plus a master decision, decoupling config latency from data-path latency. Matchmaker Paxos removes reconfiguration from the critical path so that **steady-state read/write latency is unchanged during a reconfiguration** — effectively stall-free in the common case. Old-config GC adds $O(1)$ background rounds.

## 5. Lower Bound

FLP: deterministic agreement on a *total order* of configurations is impossible in pure asynchrony with one crash — so consensus-based reconfiguration needs partial synchrony or randomization for liveness (safety always holds). CAP: during a network partition, a reconfiguration that requires the old quorum cannot be both consistent and available. Any safe handover requires the new configuration to *learn* completed old-config writes — a read-quorum intersection that imposes at least one cross-config round-trip on the first new-config operation (an unavoidable latency floor). Lower bounds on reconfiguration message complexity tie to quorum-intersection size $\Omega(|Q|)$.

## 6. The Gap

The *safety* side is essentially solved: multiple protocols (RAMBO, Vertical/Matchmaker Paxos, DynaStore, Raft) reconfigure with proven linearizability. The open part is **fully stall-free, optimal-latency reconfiguration under adversarial conditions**: avoiding any availability dip during *concurrent* reconfigurations, partitions overlapping the handover, and rapid churn; and characterizing the *minimum* cross-config overhead. Whether one can reconfigure with **zero** added latency on every operation (not just the common case) and with optimal message complexity is not tightly settled — hence partially-solved.

## 7. Current Research (as of June 2026)

Matchmaker Paxos / reconfiguration-off-the-critical-path (Whittaker, Hellerstein, et al.) and verified reconfiguration in TLA+/Ivy for Raft and Paxos variants are active *(frontier — verify)*. Interest in **leaderless** (EPaxos-style) and Byzantine reconfiguration (BFT-SMaRt, dynamic DAG-BFT like Narwhal/Bullshark membership changes) is rising *(frontier — verify)*. Groups: UC Berkeley (Hellerstein), MIT/Technion (Keidar, Malkhi lineage), VMware Research, and the etcd/raft and consensus-verification communities.

## 8. Future Work

- Provably zero-stall reconfiguration on *every* operation, with optimal message complexity, under concurrent reconfigurations and partitions.
- Stall-free Byzantine and leaderless quorum reconfiguration.
- Mechanically verified reconfiguration protocols integrated with auto-scaling / failure-driven membership policies.

## 9. Key References

- **[Foundational]** N. Lynch, A. Shvartsman. *RAMBO: A Reconfigurable Atomic Memory Service for Dynamic Networks.* DISC, 2002. — [DOI](https://doi.org/10.1007/3-540-36108-1_12)
- **[Foundational]** L. Lamport, D. Malkhi, L. Zhou. *Vertical Paxos and Primary-Backup Replication.* PODC, 2009. — [DOI](https://doi.org/10.1145/1582716.1582783)
- **[SOTA]** M. K. Aguilera, I. Keidar, D. Malkhi, A. Shraer. *Dynamic Atomic Storage Without Consensus (DynaStore).* JACM, 2011. — [DOI](https://doi.org/10.1145/1944345.1944348)
- **[SOTA]** D. Ongaro, J. Ousterhout. *In Search of an Understandable Consensus Algorithm (Raft).* USENIX ATC, 2014. — [USENIX](https://www.usenix.org/conference/atc14/technical-sessions/presentation/ongaro)
- **[SOTA]** M. Whittaker, et al. *Matchmaker Paxos: A Reconfigurable Consensus Protocol.* JSys / arXiv:2007.09468, 2021. — [arXiv](https://arxiv.org/abs/2007.09468)

## 10. Worked Example

Old config $C_0 = \{a,b,c\}$ with majority quorums (any 2 of 3). We reconfigure to $C_1 = \{a,b,c,d,e\}$ (any 3 of 5).

A write $W$ completes in $C_0$ by reaching $\{a,b\}$ — value $v$, version 7. Now suppose we naively switched and a read in $C_1$ contacted $\{c,d,e\}$. None of those saw $W$: $\{c,d,e\}$ does **not** intersect $\{a,b\}$, so the read returns the stale version 6 — a **linearizability violation**.

The fix is the cross-configuration intersection discipline: the first $C_1$ operation must first read a quorum of $C_0$ to learn completed old-config writes before $C_1$ becomes authoritative. A $C_0$-read of any 2 nodes intersects $\{a,b\}$ (e.g. $\{a,c\}$ sees $W$), so version 7 propagates into $C_1$. RAMBO/DynaStore keep $C_0$ live until a GC step proves no operation still needs it.

Cost: this imposes exactly **one** cross-config round-trip on the first new-config operation — the unavoidable latency floor from the lower bound. Steady-state operations afterward pay nothing extra, which is what "stall-free in the common case" (Matchmaker Paxos) means.

---
*Part of the [DBMS Research catalog](../../README.md).*
