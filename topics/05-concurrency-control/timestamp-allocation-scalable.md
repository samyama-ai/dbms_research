# Time-Stamp Allocation Without Global Clocks

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/timestamp-allocation-scalable` · **Status:** empirically-open

## 1. Problem Statement
Multi-Version Concurrency Control (MVCC) and timestamp-ordering (T/O) protocols require each transaction to obtain a **timestamp** used to order reads against versions and to commit. The classic implementation is a single global monotonic counter (atomic fetch-and-add). On many-core and distributed systems this counter becomes a **scalability bottleneck**: the cache line holding it ping-pongs across cores, and remote allocation adds latency.

The problem: generate timestamps that are **(a) monotonic enough to define a correct serialization order, (b) allocated with $O(1)$ uncontended cost / no single hot point, and (c) scalable to hundreds of cores and many nodes**, while preserving external consistency (linearizability of commit order) where required.

Variants:
- *Single-node many-core:* eliminate the atomic-counter cache contention.
- *Distributed:* assign timestamps across nodes with bounded skew and no central sequencer, preserving real-time order (external consistency).
- *Trade-off variant:* how much **uncertainty / waiting** (clock skew bound $\epsilon$) must be paid to avoid centralization?

This is marked **empirically-open**: the theory of logical clocks is settled, but no allocation scheme simultaneously achieves cheap, scalable, *and* externally-consistent timestamps without a hardware or uncertainty cost — and which design wins is decided empirically.

## 2. Mathematical Foundations
- **Lamport logical clocks** (1978): a counter per process incremented on events and on message receipt guarantees the *happens-before* partial order $\to$, but not real-time order. **Vector clocks** (Fidge/Mattern) capture causality exactly with $O(n)$ space.
- **Serialization correctness** needs only a total order consistent with conflict dependencies (an acyclic serialization graph), so *logical* monotonicity suffices for serializability; **external consistency** additionally requires order to respect real-time, which logical clocks cannot give without synchronization.
- **TrueTime model (Spanner):** timestamps are intervals $[t-\epsilon, t+\epsilon]$ from GPS/atomic clocks; *commit-wait* of duration $2\epsilon$ enforces that if $T_1$ commits before $T_2$ starts in real time, $ts(T_1) < ts(T_2)$. Correctness rests on a bounded-skew assumption $|\text{true time} - \text{local}| \le \epsilon$.
- **Hybrid Logical Clocks (HLC)** (Kulkarni et al. 2014): $\langle \text{physical}_\text{pt}, \text{logical}_l\rangle$ pairs that track causality while staying close to physical time, in $O(1)$ space, tolerant of unsynchronized clocks.

## 3. State of the Art (SOTA)
**Theory-SOTA.** HLC gives bounded divergence from physical time with logical-clock causality guarantees and constant space — the cleanest theoretical answer for distributed causal+near-physical timestamps.

**Systems-SOTA.**
- **Google Spanner / TrueTime** (OSDI 2012): bounded-uncertainty hardware clocks + commit-wait for external consistency — the gold standard but requires special infrastructure.
- **CockroachDB:** HLC + bounded clock offset, restarts transactions caught in the uncertainty window (no commit-wait, no special hardware).
- **Many-core single node:** Tu et al. **Silo** (SOSP 2013) avoids a global counter entirely using *epoch-based* timestamps — a coarse global epoch advances periodically, fine ordering is decided locally at commit via read/write-set validation. **TicToc** (Yu et al., SIGMOD 2016) computes timestamps *lazily from data* (data-driven timestamping) with no centralized allocation. **Cicada** (Lim et al., SIGMOD 2017) uses loosely-synchronized per-core software clocks.

## 4. Upper Bound
- **Silo epochs:** global synchronization cost amortized to $O(1)$ per transaction by advancing one shared epoch every ~40 ms; uncontended commit path touches no globally-shared counter. Scales near-linearly to dozens of cores empirically.
- **TicToc:** zero centralized allocation; timestamp derived from per-tuple `wts/rts` metadata, $O(|\text{read+write set}|)$ work, no global hot spot — provably serializable.
- **TrueTime:** commit latency lower-bounded by $2\epsilon$ (commit-wait); with $\epsilon \approx 1\text{–}7\,\text{ms}$ this is the explicit cost of centralization-free external consistency.

## 5. Lower Bound
- **External consistency requires waiting:** any protocol providing linearizable commit order *without* a perfectly synchronized global clock must pay an uncertainty cost proportional to the clock-skew bound $\epsilon$ — formalized by Spanner's commit-wait and by the observation that you cannot order two real-time-disjoint transactions without either communication or waiting out the uncertainty. This is an **information-theoretic / timing lower bound**, not merely engineering.
- **Coordination for total order:** producing a *single agreed* total order is equivalent to consensus / atomic broadcast; FLP-style impossibility means no asynchronous wait-free total-order timestamp service exists without failure detectors. A purely causal (partial-order) timestamp avoids this but does not give external consistency.

## 6. The Gap
There is no scheme that is simultaneously (1) free of any central/hot allocation point, (2) externally consistent, and (3) zero added latency. TrueTime buys (1)+(2) by paying latency $2\epsilon$; HLC/CockroachDB buy (1)+low latency by *weakening* (2) to a restart-on-uncertainty model; Silo/TicToc buy (1)+(2) for serializability on a *single node* but do not provide cross-node real-time order. The open empirical/theoretical question: characterize the **Pareto frontier** of (centralization, latency, consistency) and whether hardware (synchronized NICs, PTP, atomic clocks) can push it. Genuinely open in the distributed externally-consistent regime.

## 7. Current Research (as of June 2026)
- **Sub-microsecond clock sync** (PTP/White Rabbit, and datacenter projects like Sundial / cloud "Time Appliance") shrinking $\epsilon$ to push commit-wait toward zero — narrowing the gap toward TrueTime-without-GPS. *(frontier — verify)*
- Data-driven / decentralized timestamping (TicToc lineage) extended to multi-node and to RDMA/disaggregated-memory settings. *(frontier — verify)*
- Groups: Stonebraker/Pavlo (CMU) on many-core MVCC benchmarking; Spanner/Cloud Spanner team; CockroachDB engineering; PTP/Sundial datacenter-clock researchers (MIT/Microsoft).

## 8. Future Work
- Tight lower bound relating achievable commit latency to provable clock-skew bound across realistic failure models.
- Hardware-assisted (NIC/PTP) timestamp allocation with software-fallback correctness proofs.
- Unified theory connecting Silo-style epochs, TicToc data-driven stamps, and HLC under one cost model.

## 9. Key References
- **[Foundational]** L. Lamport. *Time, Clocks, and the Ordering of Events in a Distributed System.* CACM, 1978.
- **[SOTA]** J. C. Corbett et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012.
- **[SOTA]** S. Tu, W. Zheng, E. Kohler, B. Liskov, S. Madden. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013.
- **[SOTA]** X. Yu, A. Pavlo, D. Sanchez, S. Devadas. *TicToc: Time Traveling Optimistic Concurrency Control.* SIGMOD, 2016.
- **[Foundational]** S. S. Kulkarni, M. Demirbas, D. Madappa, B. Avva, M. Leone. *Logical Physical Clocks (HLC).* OPODIS, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
