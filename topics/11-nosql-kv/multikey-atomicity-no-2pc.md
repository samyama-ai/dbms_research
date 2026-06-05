# Multi-Key Atomicity Without 2PC

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/multikey-atomicity-no-2pc` · **Status:** partially-solved

## 1. Problem Statement

Given a sharded key-value store where keys are partitioned across $N$ independent nodes, we want to execute multi-key operations (read-modify-write transactions touching a set $K = \{k_1,\dots,k_m\}$ spanning multiple shards) that are **atomic** (all-or-nothing) and provide a defined isolation level, while paying **strictly less coordination cost** than classical two-phase commit (2PC).

We distinguish:
- **Decision variant:** Given a transaction schedule and an isolation target $I$, is there a commit order satisfying $I$ with no blocking/prepare round?
- **Optimization variant:** Minimize the number of cross-shard message round-trips (or the tail latency / abort rate) subject to atomicity and a bounded set of permitted anomalies.
- **Cost-bounding variant:** For a fixed anomaly budget (e.g., serializable vs. read-committed vs. read-atomic), what is the minimum achievable coordination?

The core tension: 2PC requires a prepare round (durable vote) plus a commit round, holding locks across a network round-trip and blocking under coordinator failure. We seek protocols that are non-blocking, lower-latency, or coordinator-free, while explicitly characterizing which anomalies are admitted.

## 2. Mathematical Foundations

Model a transaction as a partial function over a key space; a history $H$ is a set of operations with a partial order. **Serializability** requires the conflict graph $\mathit{CG}(H)$ to be acyclic; **strict serializability** additionally respects real-time order.

Key intermediate guarantee: **Read Atomicity (RA)** (Bailis et al., RAMP) forbids *fractured reads* — a transaction must not observe the write of $T$ to $k_1$ but miss $T$'s write to $k_2$. RA is strictly weaker than serializability and is achievable in a bounded, fixed number of round-trips without locks.

Coordination lower bounds rest on the **CAP** and **CALM** theorems: a query/update is coordination-free iff it is **monotone** (expressible without negation/aggregation that is not confluent). Formally (Hellerstein–Ameloot), a program has a coordination-free distributed evaluation iff it is monotone. Non-monotone integrity constraints (e.g., uniqueness, balance $\geq 0$) provably require coordination.

The blocking impossibility derives from **FLP**: no deterministic atomic commit protocol is both non-blocking and live under asynchronous network with one crash without additional assumptions (failure detectors / leader). 2PC is blocking; 3PC and Paxos-Commit (Gray–Lamport) trade rounds for non-blocking behavior.

$$\text{Latency}_{2PC} \approx 2 \cdot \mathrm{RTT} + \text{log forces}, \qquad \text{Latency}_{RAMP} = 2 \cdot \mathrm{RTT}, \text{ lock-free}$$

## 3. State of the Art (SOTA)

- **RAMP** (Bailis et al., SIGMOD 2014): read-atomic multi-partition transactions in 1–2 RTT, lock-free, using metadata to detect and repair fractured reads.
- **Calvin** (Thomson et al., SIGMOD 2012): deterministic execution via a global input log removes the need for a commit vote — atomicity by agreement on order, not on outcome.
- **TAPIR** (Zhang et al., SOSP 2015): inconsistent replication + transaction layer collapses consensus and 2PC into one round.
- **Janus / MDCC / Replicated Commit** (Mu et al. OSDI 2016; Kraska et al.): unify concurrency control and replication consensus to save round-trips.
- **FoundationDB** (2021): production OCC with a sequencer; commit is a validated single round rather than classic 2PC locking.
- Systems-SOTA: DynamoDB transactions (one-shot, single round, no separate prepare), Google Spanner (still 2PC + Paxos, but uses TrueTime to shrink lock-hold windows).

## 4. Upper Bound

For **read-atomic** isolation, RAMP achieves multi-partition atomic visibility in **2 RTT worst case, 1 RTT fast path**, lock-free, with metadata size $O(|K|)$ per transaction (RAMP-Fast) down to $O(1)$ amortized (RAMP-Hybrid via Bloom filters). For **strict serializability**, TAPIR/Janus achieve **1 round-trip in the fault-free fast path** by overlapping ordering and durability, versus 2PC's 2 sequential rounds + Paxos per shard. Deterministic systems (Calvin) achieve atomic commit with **zero commit-time coordination** at the cost of pre-declared read/write sets and a sequencing layer.

## 5. Lower Bound

Coordination is **unavoidable** for any guarantee enforcing a non-monotone invariant (CALM theorem; Ameloot–Neven–Van den Bussche, PODS 2011) — no number of clever rounds removes it. **FLP impossibility** (1985) forbids a non-blocking, always-terminating commit protocol in pure asynchrony. Communication-complexity arguments give a fundamental floor: enforcing serializability across $p$ partitions touched by a conflict requires $\Omega(1)$ inter-partition messages on the conflict path — coordination-free serializability is impossible whenever histories admit cyclic conflicts (impossibility of coordination-free strong serializability, Bailis et al.). Thus read-atomic/causal levels are the strongest **coordination-free** guarantees.

## 6. The Gap

The gap is now largely *characterized rather than open* at the extremes: we know coordination-free is achievable exactly up to RA/causal (monotone) guarantees, and impossible above. The genuinely open region is the **middle**: for mixed workloads where *most* transactions are monotone but a few are not, what is the minimum coordination as a function of the conflict structure? No tight per-workload bound (matching upper/lower message complexity parameterized by conflict-graph density) is known. Closing it requires a fine-grained, workload-parameterized coordination-complexity theory.

## 7. Current Research (as of June 2026)

- Workload-aware **invariant confluence** (I-confluence) analysis extending Bailis' work to automatically partition transactions into coordination-free vs. coordinated classes *(frontier — verify)*.
- Deterministic databases (Abadi/Thomson lineage) and Aria-style (Lu et al., VLDB 2020) deterministic OCC reducing aborts without 2PC.
- RDMA / programmable-NIC commit offload to cut prepare-round latency (FaRM lineage, Microsoft Research).
- Causal+RA hybrid stores at scale (Princeton — Lloyd/Freedman lineage). Production: FoundationDB and TiKV communities refining single-round commit; DynamoDB transactional throughput improvements.

## 8. Future Work

- A tight communication-complexity lower bound parameterized by conflict density.
- Automated invariant analysis to certify which application transactions are safely coordination-free.
- Non-blocking commit with provably minimal extra rounds under realistic failure detectors.
- Hardware-accelerated (RDMA/SmartNIC) atomic visibility with formal guarantees.

## 9. Key References

- **[Foundational]** Gray, J., Lamport, L. *Consensus on Transaction Commit.* ACM TODS, 2006.
- **[Foundational]** Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985.
- **[SOTA]** Bailis, P., et al. *Scalable Atomic Visibility with RAMP Transactions.* SIGMOD, 2014.
- **[SOTA]** Zhang, I., et al. *Building Consistent Transactions with Inconsistent Replication (TAPIR).* SOSP, 2015.
- **[SOTA]** Thomson, A., et al. *Calvin: Fast Distributed Transactions for Partitioned Database Systems.* SIGMOD, 2012.
- **[Survey]** Ameloot, T., Neven, F., Van den Bussche, J. *Relational Transducers for Declarative Networking (CALM).* PODS, 2011 / JACM, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
