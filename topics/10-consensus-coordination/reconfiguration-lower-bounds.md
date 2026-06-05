# Lower Bounds for Reconfiguration

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/reconfiguration-lower-bounds` · **Status:** open

## 1. Problem Statement

A long-lived replicated system must **reconfigure** — add/remove replicas, change quorums, migrate to new hardware — *while serving requests*, without ever losing safety (no split-brain, no lost committed data) and without halting (liveness during the change). Reconfiguration is where many consensus systems are subtly wrong. The theory question:

> What are **tight message- and round-complexity lower bounds** for *safe online membership change* in the **asynchronous** (crash- or Byzantine-)model — i.e., the minimum coordination cost to atomically switch from configuration $C$ to $C'$ while preserving linearizability and availability?

Variants:
- **Decision:** is a given reconfiguration protocol *safe* under asynchrony and overlapping reconfigurations?
- **Optimization (lower bound):** minimize messages/rounds per reconfiguration; minimize the *quiescence* required (must the old config stop?).
- **Counting:** how many distinct configurations can be "in flight" concurrently while safety holds?

## 2. Mathematical Foundations

Model: asynchronous message passing; a **configuration** $C$ is a set of replicas with quorum system $\mathcal{Q}(C)$ (intersecting quorums). Reconfiguration is a sequence $C_0 \to C_1 \to \cdots$; safety requires **quorum continuity** — read/write quorums across the active configuration set must still intersect, so committed values survive the handover. Two paradigms:

- **Consensus-based** (Raft joint consensus, Vertical/Stoppable Paxos): treat each config change as a decided command in the log; ordering of reconfigurations is total.
- **Consensus-free / SMART / RAMBO / DynaStore**: reconfiguration of *read/write registers* needs only the (weaker) abstraction of **lattice agreement**, *not* full consensus — DynaStore showed reconfigurable atomic storage is solvable **wait-free** in pure asynchrony, *circumventing FLP*, because installing a new config does not require agreeing on a single value, only on an upper bound in the configuration lattice.

Cost is measured in **messages**, **communication rounds**, and **register/RMW operations**. The Dolev–Reischuk $\Omega(f^2)$ floor applies to any Byzantine variant; for crash models the open question is the exact constant/round cost of *safe, concurrent* reconfiguration.

## 3. State of the Art (SOTA)

**Theory-SOTA.** *RAMBO* (Lynch–Shvartsman, 2002) — reconfigurable atomic memory with garbage-collected old configs. *DynaStore* (Aguilera, Keidar, Malkhi, Shraer; JACM 2011) — first **consensus-free** dynamic atomic storage, proving reconfiguration is strictly easier than consensus. *SmartMerge* and follow-ups optimized the lattice-agreement core; recent work gives reconfiguration via **(generalized) lattice agreement** with improved round complexity.

**Systems-SOTA.** Raft *joint consensus* (Ongaro–Ousterhout 2014) and the simpler single-server-change membership; *Vertical Paxos* and *Stoppable Paxos* (Lamport, Malkhi, Zhou); production reconfiguration in etcd/ZooKeeper, Spanner (Paxos group membership), and BFT systems (BFT-SMaRt reconfiguration). These differ from theory-SOTA: systems mostly route reconfiguration *through consensus* for simplicity, paying its cost even when lattice agreement would suffice.

## 4. Upper Bound

Consensus-free reconfigurable atomic storage (DynaStore / lattice-agreement reconfiguration) is achievable **wait-free** in the asynchronous crash model: each reconfiguration completes in a *constant number* of communication rounds over the relevant quorums, with messages $O(n)$ per round in the active configuration(s), and old configurations garbage-collected after a bounded number of rounds. Generalized-lattice-agreement reconfiguration improves the round complexity for *concurrent* proposals. For consensus-routed reconfiguration, the cost is exactly one consensus instance per change plus quorum-transfer of state.

## 5. Lower Bound

**FLP** does *not* forbid reconfiguration of registers (DynaStore's headline result), so the interesting lower bounds are *not* FLP-style impossibility but **complexity** bounds. Known: any safe reconfiguration must contact **intersecting quorums of the configurations it bridges**, giving an $\Omega(\text{quorum size})$ message floor per change, and concurrent reconfigurations require *lattice agreement*, which has its own round lower bounds. In the **Byzantine** setting, **Dolev–Reischuk** forces $\Omega(f^2)$ messages. What is **not** pinned down: a *tight* round/message lower bound matching the upper bounds for safe, *concurrent* asynchronous reconfiguration — e.g., whether 2 rounds are necessary and sufficient, and the exact trade-off between allowing $k$ concurrent in-flight configs and per-reconfiguration cost.

## 6. The Gap

Genuinely open. We know reconfiguration is *strictly weaker* than consensus (DynaStore) and have wait-free upper bounds, but a **matching tight lower bound** on rounds and messages for safe online reconfiguration — especially under concurrent/competing reconfigurations and in the Byzantine model — is missing. The gap is between "constant rounds, $O(n)$ messages" upper bounds and the absence of a proven optimal constant. Closing it requires either an optimal protocol meeting a proven lower bound, or a separation showing concurrency inherently costs extra rounds.

## 7. Current Research (as of June 2026)

(1) **Lattice-agreement-based reconfiguration** with improved round complexity and formal optimality arguments *(frontier — verify)*; (2) **Byzantine reconfiguration** lower bounds extending Dolev–Reischuk to dynamic membership; (3) **formally verified** reconfiguration (TLA+/Ivy proofs of Raft joint consensus and Paxos reconfiguration, addressing well-known bugs); (4) reconfiguration in **DAG-BFT / blockchain epoch changes** at scale. Groups/people: Idit Keidar & Alexander Spiegelman (Technion), Marcos Aguilera, Dahlia Malkhi, Alexander Shraer, the lattice-agreement line (Faleiro, Garg), and verification groups (Ivy/TLA+ — Padon, Wilcox/Verdi).

## 8. Future Work

- Tight round/message lower bounds for concurrent asynchronous reconfiguration.
- Byzantine-model reconfiguration complexity beyond the $\Omega(f^2)$ floor.
- Reconfiguration that is *both* consensus-free *and* supports rich SMR (not just registers).
- Mechanized proofs of optimality, not just safety.
- Cost of reconfiguration *under partition/adaptive adversary* (interaction with the liveness-attack problem).

## 9. Key References

- **[Foundational]** N. Lynch, A. Shvartsman. *RAMBO: A Reconfigurable Atomic Memory Service for Dynamic Networks.* DISC, 2002.
- **[SOTA]** M. K. Aguilera, I. Keidar, D. Malkhi, A. Shraer. *Dynamic Atomic Storage Without Consensus (DynaStore).* JACM, 2011.
- **[Foundational]** L. Lamport, D. Malkhi, L. Zhou. *Vertical Paxos and Primary-Backup Replication.* PODC, 2009.
- **[SOTA]** D. Ongaro, J. Ousterhout. *In Search of an Understandable Consensus Algorithm (Raft) — Joint Consensus Membership Change.* USENIX ATC, 2014.
- **[Foundational]** D. Dolev, R. Reischuk. *Bounds on Information Exchange for Byzantine Agreement.* JACM, 1985.
- **[SOTA]** J. M. Faleiro, S. Rajamani, K. Rajan, G. Ramalingam, K. Vaswani / V. K. Garg et al. *Generalized Lattice Agreement* and reconfiguration applications. PODC, 2012 and follow-ups.

---
*Part of the [DBMS Research catalog](../../README.md).*
