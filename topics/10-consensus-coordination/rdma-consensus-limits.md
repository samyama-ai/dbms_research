# RDMA-Accelerated Consensus Limits

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/rdma-consensus-limits` · **Status:** empirically-open

## 1. Problem Statement
One-sided RDMA (`READ`/`WRITE`/`CAS` that the remote NIC services without involving the remote CPU) changes the communication primitive that classic consensus lower bounds assume: those bounds count *message delays* in a two-sided send/receive model where the receiver actively participates in each round. The question is: **can one-sided RDMA verbs lower the effective round/message-delay complexity of consensus below the classic two-sided bounds, and if so, what failure-detection and safety semantics must be sacrificed?**

Variants:
- **Decision:** Does there exist a linearizable, fault-tolerant ($f$ crashes, $2f+1$ replicas) consensus protocol whose *commit critical path* uses only one-sided verbs and completes in fewer network delays than the two-sided lower bound, without weakening the fault model?
- **Empirical/optimization:** Minimize median and tail commit latency on real RDMA hardware while bounding the unsafe window introduced by memory-permission races, NIC failures, and the absence of remote-CPU liveness signals.
- **Semantics:** Precisely characterize the failure model induced by one-sided access (a passive remote replica whose CPU may be dead but whose memory is still served by the NIC).

## 2. Mathematical Foundations
Two-sided model: a "message delay" is the time for a send→receive pair; consensus needs $\ge 2$ message delays in the fault-free case and the proposer cannot decide in $1$ (Lamport lower bound). One-sided RDMA replaces the remote receive step with NIC-serviced memory access, so a single round trip becomes a *read-modify-write on remote memory* rather than a request answered by remote logic.

Formally one models the remote node as exposing a register/CAS object directly: the system becomes shared-memory-like, where consensus among $n$ processes requires objects of **consensus number** $\ge n$ (Herlihy's hierarchy). RDMA `CAS` has consensus number $\infty$ in principle — but only over the words the NIC can atomically update, and *only while the remote NIC is alive even if its CPU is not*. This decouples "node liveness" into NIC-liveness vs CPU-liveness, breaking the single fail-stop assumption $p_i \in \{\text{up},\text{down}\}$ into a richer failure lattice. Permission revocation (re-registering memory regions) becomes the mechanism for fencing stale leaders, analogous to epoch/ballot numbers but enforced in NIC hardware.

## 3. State of the Art (SOTA)
- **DARE** (Poke & Hoefler, HPDC 2015): RDMA state-machine replication; leader uses one-sided writes to followers' logs.
- **APUS** (Wang et al., SoCC 2017): scalable RDMA Paxos.
- **Mu** (Aguilera et al., OSDI 2020): sub-microsecond *failover* using RDMA permissions to fence the old leader; demonstrates one-sided replication on the critical path with ~1.3 µs replication latency.
- **Hermes** (Katsarakis et al., ASPLOS 2020) and **Kite** for RDMA-based replication/consistency; **FaRM** (Dragojević et al., NSDI 2014) for RDMA transactions. Systems-SOTA shows order-of-magnitude latency wins, but each makes hardware-specific safety arguments rather than matching a classic bound. *(frontier — verify newest CXL/SmartNIC variants 2024–2026.)*

## 4. Upper Bound
Best demonstrated: **leader writes the committed entry to a quorum of followers' memory with one-sided WRITEs and a single round trip on the fast path** (DARE/Mu), giving commit latency dominated by one RDMA RTT (~1–2 µs). Failover is reduced to a permission change rather than a consensus round (Mu). This holds in a partially-synchronous crash model on RDMA-capable hardware with reliable-connection (RC) transport; it does not beat the *information-theoretic* delay count so much as shrink the *constant* (RDMA RTT ≪ kernel TCP RTT) and move fencing into the NIC.

## 5. Lower Bound
The classic two-message-delay lower bound for fault-free consensus (Lamport; Keidar–Rajsbaum) still applies when "delay" is measured in round trips, because a one-sided op is itself a round trip. Thus RDMA is widely believed *not* to break the asymptotic delay bound — only the constant. FLP impossibility is untouched: asynchrony still forbids deterministic termination. The open formal question is whether the *shared-memory* view RDMA exposes admits a genuinely sub-two-round-trip linearizable decision under any non-trivial failure model — currently no protocol does so without assuming NIC-never-fails, which is the semantic cost.

## 6. The Gap
There is no proven round-complexity *separation* between two-sided and one-sided consensus; empirically RDMA wins on constants and on failover, but whether one-sided access can save a *round trip* (not just a kernel crossing) under realistic NIC-failure semantics is unresolved. Closing it requires (a) a formal failure model that captures NIC-alive/CPU-dead states, and (b) either a protocol achieving sub-2-RTT decision in that model or a matching impossibility.

## 7. Current Research (as of June 2026)
- Pushing consensus logic into SmartNICs/DPUs and exploring CXL shared memory as a stronger one-sided substrate. *(frontier — verify.)*
- Formal models of RDMA failures (the "RDMA shared-memory with crash" model) to prove safety of Mu-style fencing rigorously.
- Groups: ETH Zürich (Hoefler), VMware Research / MIT (Aguilera, Castro), Edinburgh (Vasilakis/Katsarakis lineage), Microsoft Research (FaRM team).

## 8. Future Work
- A clean impossibility-or-separation theorem for one-sided consensus delay complexity.
- Byzantine-tolerant RDMA consensus (NICs as semi-trusted hardware).
- Standardizing the NIC-failure semantics so portable safety proofs are possible across vendors.

## 9. Key References
- **[Foundational]** Maurice Herlihy. *Wait-Free Synchronization.* ACM TOPLAS, 1991.
- **[Foundational]** Leslie Lamport. *Lower Bounds for Asynchronous Consensus.* Distributed Computing, 2006.
- **[SOTA]** Marius Poke, Torsten Hoefler. *DARE: High-Performance State Machine Replication on RDMA Networks.* HPDC, 2015.
- **[SOTA]** Marcos K. Aguilera et al. *Microsecond Consensus for Microsecond Applications (Mu).* OSDI, 2020.
- **[SOTA]** Aleksandar Dragojević et al. *FaRM: Fast Remote Memory.* NSDI, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
