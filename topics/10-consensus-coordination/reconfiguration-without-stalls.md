# Reconfiguration Without Quorum Stalls

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/reconfiguration-without-stalls` · **Status:** open

## 1. Problem Statement
A replicated state machine must change its membership (add/remove replicas, move shards, replace failed nodes) while remaining **safe** (no two configurations decide conflicting values for the same slot) and **live** (commands keep committing). Classical reconfiguration either (a) stops the world — drains in-flight commands, installs the new configuration, resumes (Raft's joint-consensus and single-server change both involve careful sequencing), or (b) uses an auxiliary mechanism (Vertical Paxos, an external configuration master) that can itself stall.

The problem: *design a reconfiguration mechanism that never pauses command processing and never loses liveness during the overlap of old and new configurations, under crash faults and partial synchrony.* Variants: **decision** — does a safe stall-free reconfiguration protocol exist for a given fault model? **optimization** — minimize the number of slots / time during which both configurations must be consulted, and the extra message rounds per command in the overlap window.

## 2. Mathematical Foundations
Let configurations $C_0, C_1, \dots$ each be a quorum system over a replica set; consensus proceeds over a sequence of **slots** $s=1,2,\dots$. A reconfiguration at activation slot $a$ means slots $<a$ are decided under $C_i$ and slots $\ge a$ under $C_{i+1}$. **Safety** requires that the decision for every slot is determined by exactly one configuration's quorums, and that the activation point $a$ is itself agreed (chicken-and-egg: agreeing on $a$ is a consensus decision under $C_i$). During overlap, a command may need intersection guarantees across $C_i$ and $C_{i+1}$:
$$\forall Q\in\mathcal{Q}(C_i),\ Q'\in\mathcal{Q}(C_{i+1}):\ Q\cap Q' \ne \varnothing \quad(\text{joint-consensus condition}).$$
**Liveness** under FLP is conditional on partial synchrony / eventual leader (Ω failure detector). The hazard is a *configuration-change deadlock*: the protocol blocks waiting for a quorum that no live configuration can form (e.g., removed-but-not-yet-deactivated nodes counted in the old quorum). The "$\alpha$-bounded pipelining" approach decides the new configuration but defers its activation by $\alpha$ slots so commands $a..a+\alpha-1$ keep flowing under $C_i$.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Lamport, Malkhi, Zhou's *Vertical Paxos* and *Reconfiguring a State Machine* (PODC 2010) formalize safe reconfiguration via an auxiliary master and stop-sign decisions. SMART (EuroSys 2006) reconfigures by running overlapping replica instances. DynaStore (JACM 2011) gives reconfigurable atomic storage *without* consensus, using a lattice of configurations. RAMBO provides reconfigurable read/write registers.
- **Systems-SOTA:** Raft (2014) supports single-server membership changes and joint consensus but momentarily restricts concurrent changes. Production systems (etcd, CockroachDB, TiKV) use Raft learner/joint-config flows; many still effectively serialize changes and can stall briefly. Matchmaker Paxos (2020) separates the configuration-acquisition path to reduce stalls.

## 4. Upper Bound
Best-known: reconfiguration with **zero added rounds on the steady-state command path** is achievable by deciding the next configuration ahead of time and activating it after a bounded pipeline of $\alpha$ slots (Lamport-style), so command processing never pauses in the *failure-free* case. For reconfigurable storage without consensus, DynaStore achieves wait-free reconfiguration with $O(\text{number of proposed configs})$ overhead. These hold in **partial synchrony** (consensus path) or **asynchrony** (DynaStore, storage-only, no SMR ordering).

## 5. Lower Bound
Agreeing on the activation point is itself a consensus instance, so FLP forbids a deterministic, always-terminating stall-free reconfiguration in pure asynchrony with one crash. Any consensus-based SMR reconfiguration inherits the $\ge 2$ message-delay decision cost and an Ω-failure-detector liveness requirement. For storage, results around reconfigurable registers show consensus is *not* required (DynaStore), but full SMR ordering during reconfiguration provably needs the joint-intersection condition above; violating it permits split-brain (a CAP-style safety violation under partition). No protocol can guarantee liveness if both configurations simultaneously lack a live quorum.

## 6. The Gap
**Open.** Steady-state stall-free reconfiguration exists in the *failure-free* case, but the open gap is guaranteeing *no liveness loss when a reconfiguration is itself triggered by failures* — exactly when nodes are crashing, agreeing on $a$ and forming overlap quorums is hardest. No protocol simultaneously gives: (i) never pausing command processing, (ii) supporting arbitrary overlapping/concurrent configuration changes, and (iii) provable liveness under the same fault model that motivated the change. Closing it needs a protocol whose configuration-agreement path cannot be starved by the very failures being repaired.

## 7. Current Research (as of June 2026)
Directions: decoupling configuration management from the data path (Matchmaker Paxos); lattice/CRDT-style consensus-free reconfiguration extended toward ordered SMR; learner-based smooth membership transitions in production Raft. Groups: MSR (Lamport/Malkhi lineage), Technion, UC Berkeley (Matchmaker), and the etcd/TiKV/Cockroach engineering communities. *(frontier — verify)* Recent proposals claim fully non-blocking reconfiguration under concurrent failures by precomputing overlap quorums, but rigorous liveness proofs under adversarial failure timing are still being established.

## 8. Future Work
- A reconfiguration protocol with proven liveness under the failure model that triggered it.
- Unifying consensus-free reconfigurable storage with totally-ordered SMR.
- Minimizing the overlap window and per-command overhead to provably zero in all (not just failure-free) executions.
- Reconfiguration that composes safely with flexible/weighted quorums and geo-placement.

## 9. Key References
- **[Foundational]** Leslie Lamport, Dahlia Malkhi, Lidong Zhou. *Reconfiguring a State Machine.* SIGACT News / PODC, 2010.
- **[Foundational]** Marcos K. Aguilera, Idit Keidar, Dahlia Malkhi, Alexander Shraer. *Dynamic Atomic Storage Without Consensus (DynaStore).* JACM, 2011.
- **[SOTA]** Diego Ongaro, John Ousterhout. *In Search of an Understandable Consensus Algorithm (Raft).* USENIX ATC, 2014.
- **[SOTA]** Michael Whittaker et al. *Matchmaker Paxos: A Reconfigurable Consensus Protocol.* JSys / 2020.
- **[Foundational]** Lorenzo Alvisi et al. *SMART: A Technique for Smart Reconfiguration of Replicated State Machines.* EuroSys, 2006.

---
*Part of the [DBMS Research catalog](../../README.md).*
