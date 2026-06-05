# Cross-Shard Consensus Composition

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/cross-shard-consensus` · **Status:** open

## 1. Problem Statement
Sharded transactional systems replicate each shard with its own consensus group (Paxos/Raft) and stitch shards together with an atomic-commit protocol (typically 2PC) for transactions that span multiple shards. The composition problem asks: **what is the minimum coordination cost — message rounds, message count, and latency — to execute a cross-shard transaction while preserving strict serializability (one-copy serializability + linearizable real-time order) across all shards?**

Variants:
- **Decision:** Given a workload of single- and multi-shard transactions and a target isolation level, does a composition exist that commits every multi-shard transaction in $\le k$ wide-area round trips while remaining strictly serializable under $f$ faults per shard?
- **Optimization:** Minimize expected commit latency (or wide-area message count) subject to the strict-serializability constraint.
- **Counting/structural:** Characterize which transaction-conflict graphs admit a "fused" protocol that avoids stacking 2PC *on top of* per-shard consensus (the 2-round-of-consensus penalty).

The crux is that naïve layering pays for *both* the cross-shard 2PC rounds *and* a per-shard consensus round to durably log each 2PC vote/decision, and must order cross-shard commits consistently with single-shard commits.

## 2. Mathematical Foundations
Model: $S$ shards, each a replicated state machine with replica set $R_i$ tolerating $f_i$ crash faults, $|R_i| \ge 2f_i+1$. A transaction $T$ reads/writes a key set partitioned across a subset $\sigma(T)\subseteq[S]$. Correctness target is **strict serializability**: there is a total order $<$ on committed transactions consistent with (i) the per-key value semantics and (ii) real-time precedence ($T_1$ returns before $T_2$ begins $\Rightarrow T_1 < T_2$).

Layered cost: a multi-shard commit requires a 2PC prepare/commit ($\ge 2$ wide-area rounds) where each phase is itself durably replicated, giving latency $\approx 2\cdot W + 2\cdot C$ ($W$ = wide-area RTT, $C$ = intra-shard consensus latency). The classic lower bound for *non-blocking* atomic commit is that it requires a failure detector at least as strong as $\Diamond \mathcal{S}$ / consensus (Guerraoui), so the consensus cost cannot be wished away.

Fusion insight: 2PC's coordinator log and a shard's consensus log can be **collapsed** when the participant set and the replica set coincide or overlap, reducing $2C \to C$ — formalized via the "consensus + commit = atomic commit" decomposition (Gray–Lamport, *Consensus on Transaction Commit*), where each 2PC participant is replaced by a Paxos instance and the TM by Paxos over the decision.

## 3. State of the Art (SOTA)
- **Spanner** (Corbett et al., OSDI 2012): per-shard Paxos + 2PC, with TrueTime giving external consistency; the canonical layered design.
- **Gray–Lamport Paxos Commit** (TODS 2006): folds the TM into Paxos so a fault no longer blocks commit; same latency class but non-blocking.
- **Janus** (Mu et al., OSDI 2016) and **Tapir** (Zhang et al., SOSP 2015): *unify* concurrency control, replication, and commit into one round, eliminating the layered penalty for many transactions — strongest systems-SOTA for one-round strict-serializable cross-shard commit.
- **Carousel** (Yan et al., SIGMOD 2018), **SLOG** (Ren et al., VLDB 2019), and **Detock** (SIGMOD 2023) reduce or deterministically order cross-shard conflicts. *(frontier — verify for 2024–2026 successors.)*

## 4. Upper Bound
Best known: **one wide-area round trip** for the fast path. Tapir (inconsistent replication + OCC) and Janus (dependency tracking) commit a strictly-serializable multi-shard transaction in a single round when there are no conflicts, i.e. latency $\approx 1\cdot \max_i(\text{quorum RTT})$, with a fallback two-round path under contention. Holds in the partially-synchronous crash-fault model with $|R_i|\ge 2f_i+1$. Deterministic systems (Calvin/SLOG family) achieve cross-shard commit without 2PC at all by pre-agreeing a global order, at the cost of a sequencing layer.

## 5. Lower Bound
Non-blocking atomic commit requires the $?\!P$/$\Diamond\mathcal{S}$ failure-detection power — strictly between perfect detection and pure asynchrony — and is impossible in pure asynchrony (FLP, 1985; Guerraoui 1995). Any protocol preserving real-time order across shards inherits a **one-RTT-to-a-quorum** latency floor for the contended case (the geo-consensus latency bound). For conflicting transactions, two messages delays are necessary in the worst case (lower bound on non-trivial agreement, Lamport, *Lower Bounds for Asynchronous Consensus*).

## 6. The Gap
The fast path is essentially optimal (one round), but no protocol is simultaneously optimal on **all** axes — fast-path latency, contended-path latency, message count $O(n)$ vs $O(n^2)$, and absence of a separate sequencing layer. Whether a single protocol can match the one-round fast path *and* a constant-factor-optimal contended path *without* a global sequencer, under realistic skewed conflict rates, is open. Closing it likely requires a lower bound tying conflict-graph structure to unavoidable extra rounds.

## 7. Current Research (as of June 2026)
- DAG-based / deterministic ordering to amortize cross-shard coordination (Detock and successors). *(frontier — verify.)*
- Co-design of CRDT-style commutativity with sharded consensus to certify which cross-shard transactions need *no* agreement (links to coordination-avoidance).
- Groups: MIT PDOS (Morris/Kaashoek lineage, Tapir/Janus), Maryland (Mu), UMD/Yale (Abadi, Calvin/SLOG/Detock), Google Spanner team.

## 8. Future Work
- A unifying lower bound: round complexity as a function of the cross-shard conflict-graph topology.
- Strict-serializable composition under Byzantine shards (links to hybrid BFT-CFT and cross-shard BFT).
- Cost models that price wide-area messages by cloud egress dollars, not just count.

## 9. Key References
- **[Foundational]** Jim Gray, Leslie Lamport. *Consensus on Transaction Commit.* ACM TODS, 2006.
- **[Foundational]** Michael Fischer, Nancy Lynch, Michael Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985.
- **[SOTA]** Irene Zhang et al. *Building Consistent Transactions with Inconsistent Replication (TAPIR).* SOSP, 2015.
- **[SOTA]** Shuai Mu et al. *Consolidating Concurrency Control and Consensus for Commits under Conflicts (Janus).* OSDI, 2016.
- **[SOTA]** James Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012.
- **[SOTA]** Cuong Nguyen, Daniel Abadi et al. *Detock: High Performance Multi-region Transactions.* SIGMOD, 2023.

---
*Part of the [DBMS Research catalog](../../README.md).*
