---
id: 10-consensus-coordination/disaggregated-memory-consensus
title: "Consensus for Disaggregated Memory"
topic: 10-consensus-coordination
status: open
first_added: 2026-06
last_reviewed: 2026-09
last_substantive_update: 2026-09
stale_since: ""
provenance: synthesized
---

# Consensus for Disaggregated Memory

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/disaggregated-memory-consensus` · **Status:** open

## 1. Problem Statement

Classic state-machine replication assumes a **shared-nothing** model: each replica owns a private log on its local disk/DRAM, and consensus exchanges *messages* to make those private logs agree. **Memory disaggregation** — CXL-attached memory pools, RDMA-reachable far memory, and pooled memory appliances — inverts this. State no longer lives as per-node logs; it lives in a **shared remote memory** that many compute nodes read and write directly via one-sided operations (RDMA READ/WRITE/CAS, CXL.mem loads/stores), often with little or no CPU on the memory side. The memory side is *passive*: it cannot run a protocol, vote, or detect failures.

The problem: **design agreement protocols when the durable state is shared, remotely-addressable memory accessed by one-sided primitives, and the compute nodes contending over it can fail independently of the memory.** Variants: (a) *decision* — given a set of one-sided primitives (READ/WRITE/CAS/FAA, with or without persistence) and a failure model (compute crashes, memory-node crashes, partitions), is wait-free or obstruction-free consensus solvable? (b) *optimization* — minimize the number of remote round trips / RDMA verbs per decided command; (c) *resource variant* — characterize the minimum **consensus number** (à la Herlihy) of the available remote primitives.

The crux: a passive memory pool gives you *shared registers and conditional writes*, not active acceptors — and a single CXL/RDMA memory node is a **shared-fate** durability and availability dependency the message model never had.

## 2. Mathematical Foundations

The natural model is **shared-memory distributed computing**: $n$ asynchronous processes (compute nodes) communicate through **shared base objects** exposed by the memory pool. The available objects determine solvability via **Herlihy's consensus hierarchy** (Herlihy, 1991): atomic **read/write registers have consensus number $1$** — they cannot solve wait-free consensus for $\ge 2$ processes — whereas **compare-and-swap (CAS)** has consensus number $\infty$. RDMA exposes one-sided WRITE/READ (register-like) and atomic **CAS/FAA**; CXL 3.0 adds hardware atomics. So the *primitive set* of the fabric directly bounds what is achievable.

Formally, with registers only, the **FLP-style impossibility for shared memory** (Loui–Abu-Amara; Herlihy) forbids deterministic wait-free consensus; randomization or stronger primitives are required. A protocol is **wait-free** if every non-faulty process decides in a finite number of its own steps regardless of others; **obstruction-free** if it decides when run in isolation. RDMA's distinguishing power is that it can **dynamically grant/revoke access permissions** to memory regions — Aguilera et al. (PODC 2019) show this *permission-change* ability lets RDMA solve consensus with optimal resilience tolerating **both crash and network failures**, beating the message- and shared-memory-only models. Cost is measured in **remote-access complexity**: number of one-sided verbs and round trips per decision, plus the persistence cost of flushing to durable far memory (e.g., CXL persistence domains).

## 3. State of the Art (SOTA)

- **Theory-SOTA:** **Herlihy's wait-free hierarchy** (TOPLAS 1991) is the foundation. The **RDMA consensus model** of **Aguilera, Ben-David, Gelashvili, Guerraoui, Keidar, Lentz, Lentz, Spiegelman et al.** (*Microsecond Consensus for Microsecond Applications*, OSDI 2020; *The Impact of RDMA on Agreement*, PODC 2019) characterizes how one-sided RDMA with permission changes shifts solvability and resilience.
- **Systems-SOTA:** **Mu** (Aguilera et al., OSDI 2020) — RDMA SMR with ~1µs replication using one-sided writes and a permission-based leader. **DARE** and **APUS** (RDMA Paxos/Raft). For disaggregation specifically: **FaRM** (Dragojević et al., NSDI 2014) on RDMA shared memory with transactions; **Clover/Sherman/dLSM** and CXL-memory KV stores; **Pangolin/Pasha** and emerging **CXL shared-memory consensus** prototypes *(frontier — verify)*. Most production "disaggregated" systems still bolt a message-based Raft on top rather than agree *in* the shared memory.

## 4. Upper Bound

With strong remote atomics, consensus is solvable with low remote-access complexity: **Mu** commits in a **single one-sided RDMA WRITE to a quorum** on the common path (≈1.3µs), using permission revocation rather than acceptor logic — effectively **$O(1)$ remote round trips** per decision when the leader is stable. Theoretically, RDMA's permission-change power yields consensus with **optimal resilience** against combined crash + partition failures (Aguilera et al., PODC 2019), which the pure message model cannot match at the same resilience. For CAS-equipped pooled memory, standard $\Omega(1)$-RTT lock-free agreement on a shared decision cell applies. These are the best constructive results; they assume the fabric exposes the needed atomics and a reliable (or replicated) memory tier.

## 5. Lower Bound

- **Consensus-number floor (information-theoretic, shared-memory model):** if the pool exposes only read/write registers (no atomic CAS), **wait-free deterministic consensus is impossible for $n\ge 2$** (Herlihy 1991; Loui–Abu-Amara) — a hard limit set by the *primitive set*, not the implementation.
- **FLP** (Fischer–Lynch–Paterson, 1985) carries over: asynchronous + one crash ⇒ no deterministic message-only solution; in shared memory the analogous result forbids register-only wait-freedom, forcing randomization or stronger objects.
- **Shared-fate / durability floor:** a single memory node holding the shared state is a single point of failure; surviving its loss requires replication *of the memory*, which reintroduces a quorum and at least the intersection lower bound $|Q_1|+|Q_2|>n$ and ≥1 remote RTT — the disaggregated layout cannot evade the durability cost of $\ge f+1$ copies.
- **Remote-access lower bounds:** even with CAS, contended consensus on a shared cell incurs $\Omega(\log n)$-style step complexity under heavy contention in known shared-memory lower-bound models.

## 6. The Gap

Genuinely open. We have (a) a clean primitive-driven solvability map (Herlihy) and (b) one-sided-RDMA SMR that is fast in practice (Mu) — but **no general theory of fault-tolerant agreement for the disaggregated regime** where compute nodes, memory nodes, and the fabric fail *independently* and memory is passive. Open pieces: consensus that tolerates **memory-node** failure (not just compute failure) without collapsing back to message-passing replication; tight remote-access complexity bounds across the CXL/RDMA primitive zoo (CAS vs. FAA vs. permission-change vs. CXL.mem atomics); and persistence-aware bounds that count flushes to durable far memory. Closing it needs a unified model spanning passive-memory failure modes plus matching protocols and impossibility results.

## 7. Current Research (as of June 2026)

Active directions: consensus and transactions natively over **CXL 3.0 shared/fabric-attached memory** with hardware atomics, and whether CXL multi-host coherence changes the consensus number of the fabric *(frontier — verify)*; failure-resilient disaggregated KV/log stores that replicate the memory tier (EPFL — Guerraoui/Aguilera lineage; MIT, UW, MSR, and CXL-systems groups) *(frontier — verify)*; one-sided-only protocols minimizing CPU on both ends; persistence-domain-aware consensus for CXL/PMEM durability. The Mu/RDMA-agreement line and FaRM remain the practical anchors, with CXL prototypes the emerging frontier.

## 8. Future Work

- A solvability + resilience map for agreement under *independent* compute-, memory-, and fabric-failure with passive memory.
- Tight remote-access (verb/RTT/flush) lower and upper bounds parameterized by the available CXL/RDMA primitive set.
- Protocols that tolerate memory-node loss with minimal extra copies, unifying disaggregation with quorum durability.
- Persistence-aware consensus exploiting CXL persistence domains, with bounds counting durable flushes, not just round trips.
- Reconfiguration and membership when "replicas" are memory regions whose access permissions, not whose processes, are revoked.

## 9. Key References

- **[Foundational]** Maurice Herlihy. *Wait-Free Synchronization.* ACM TOPLAS, 1991. — [DOI](https://doi.org/10.1145/114005.102808)
- **[Foundational]** Michael Fischer, Nancy Lynch, Michael Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[SOTA]** Marcos K. Aguilera, Naama Ben-David, Rachid Guerraoui, Virendra Marathe, Igor Zablotchi. *The Impact of RDMA on Agreement.* PODC, 2019. — [DOI](https://doi.org/10.1145/3293611.3331601)
- **[SOTA]** Marcos K. Aguilera, Naama Ben-David, Rachid Guerraoui, Virendra Marathe, Athanasios Xygkis, Igor Zablotchi. *Microsecond Consensus for Microsecond Applications (Mu).* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/aguilera)
- **[SOTA]** Aleksandar Dragojević, Dushyanth Narayanan, Miguel Castro, Orion Hodson. *FaRM: Fast Remote Memory.* NSDI, 2014. — [USENIX](https://www.usenix.org/system/files/conference/nsdi14/nsdi14-paper-dragojevic.pdf)
- **[Foundational]** Michael C. Loui, Hosame H. Abu-Amara. *Memory Requirements for Agreement Among Unreliable Asynchronous Processes.* Advances in Computing Research, 1987. — [DBLP search](https://dblp.org/search?q=Memory+Requirements+for+Agreement+Among+Unreliable+Asynchronous+Processes)

## 10. Worked Example

Two compute nodes $p_1, p_2$ race to decide one value in a shared remote cell `D` (initially $\bot$) on a passive memory pool.

**Registers only (consensus number 1).** Suppose the pool exposes only one-sided READ/WRITE. $p_1$ READs `D` = $\bot$, intends to write $v_1$; concurrently $p_2$ READs `D` = $\bot$, intends $v_2$. Both then WRITE; the last writer wins, but neither can *agree* on the outcome wait-free — Herlihy's hierarchy puts atomic registers at consensus number $1$, so deterministic wait-free consensus for $n\ge 2$ is **impossible** (Loui–Abu-Amara). No protocol over plain READ/WRITE fixes this.

**With CAS (consensus number $\infty$).** Now the pool supports atomic compare-and-swap. $p_1$ issues `CAS(D, ⊥, v1)` and $p_2$ issues `CAS(D, ⊥, v2)`. Exactly one succeeds atomically — say $p_1$ — installing $v_1$; $p_2$'s CAS fails (sees $v_1 \ne \bot$) and adopts $v_1$. One winner, agreement reached in **$O(1)$ remote round trips**. This is the Mu-style fast path: a single one-sided atomic verb decides, with no acceptor CPU on the memory side — but a single memory node holding `D` remains a shared-fate failure point, so durability still needs $\ge f+1$ replicated copies.

---
*Part of the [DBMS Research catalog](../../README.md).*
