# Epoch-based durability commit

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/epoch-based-durability` · **Status:** partially-solved

## 1. Problem Statement
Per-transaction synchronous durability (one fsync per commit) caps throughput at the storage's fsync rate and serializes commits behind log persistence. **Epoch-based durability** replaces per-commit persistence with *coarse, epoch-grained* persistence: wall-clock or counter time is partitioned into epochs of length $E$; transactions are stamped with the current epoch; all transactions in epoch $e$ become durable atomically when epoch $e$'s log is persisted. Results are released to clients only once their epoch is stable. The problem is to provide this with **provable bounds** on (i) data loss after a crash and (ii) recovery latency, while preserving serializability/recoverability and high throughput.

**Variants.** *Decision:* given epoch length $E$ and persistence rate, is the worst-case loss $\le B$ and recovery $\le T$? *Optimization:* choose $E$ minimizing client-visible latency subject to loss/recovery bounds. *Distributed:* coordinate epoch boundaries across shards/replicas so a globally consistent epoch is the unit of durability. Because the core mechanism is **established and shipping** (Silo/SiloR, FOEDUS) with clear bounds, this is **partially-solved**; open issues are distributed coordination, optimal epoch sizing, and integration with replication.

## 2. Mathematical Foundations
Let epochs be intervals $[t_0+iE,\ t_0+(i+1)E)$ with current epoch number $\mathcal{E}(t)=\lfloor (t-t_0)/E\rfloor$. A global epoch counter is advanced by a single coordinator (or via a barrier); a transaction commits *logically* in epoch $e$ but is *released* only after the **durable epoch** $D(t) = $ (highest epoch whose log is fully persisted) reaches $e$. Key invariant: results released $\Rightarrow$ epoch persisted, so a crash loses only transactions in epochs $> D$. Since at most the in-flight epochs are un-persisted, the **data-loss bound** is the work of $\le \lceil \text{persist-latocy}/E\rceil$ epochs; with single-epoch lag, loss $\le$ one epoch ($\approx E\cdot\lambda$ transactions).

**Serializability/recoverability:** epoch boundaries provide a coarse total order; Silo's optimistic concurrency uses transaction IDs whose high bits are the epoch, ensuring read-from-uncommitted is never *externalized* (anti-dependencies that would violate recoverability are confined within an epoch and never released early). Recovery replays only the durable log up to $D$; **recovery latency** $T_{\text{rec}} = O(\text{log bytes since last checkpoint}/\text{replay bw})$, and parallel replay (SiloR) divides by core count. The latency–loss tradeoff is monotone in $E$: larger $E$ ⇒ better throughput (fewer barriers/fsyncs) but larger loss window and higher commit latency (clients wait up to $E$ for epoch release).

## 3. State of the Art (SOTA)
**Systems-SOTA.** *Silo* (Tu et al., SOSP 2013) introduced epoch-based group commit with decentralized, scalable OCC; *SiloR* (Zheng et al., OSDI 2014) added parallel logging, checkpointing, and recovery, achieving fast durability and recovery on multicore. *FOEDUS* (Kimura, SIGMOD 2015) uses epoch-based durability with dual in-memory/SSD pages. *Hekaton*/MVCC and many in-memory engines adopt epoch-style group commit. Epoch-based **reclamation** (RCU/EBR) is the dual technique used for safe memory reclamation, sharing the same epoch-advance machinery. Deterministic systems and many cloud OLTP engines use coarse persistence boundaries for batched durability.

**Theory-SOTA.** The loss/recovery bounds for the single-node case are clean and proven (one-epoch loss window; parallel-replay recovery). Distributed/cross-shard epoch agreement borrows from consistent-snapshot (Chandy–Lamport) and barrier theory.

## 4. Upper Bound
Single-node epoch durability achieves: commit throughput limited by epoch-batched fsync (one persist per epoch, amortizing fsync cost over $E\lambda$ transactions), client-visible commit latency $\le E + (\text{persist latency})$, **data-loss bound $\le$ one epoch of transactions** ($\approx E\lambda$), and recovery $T_{\text{rec}} = O(\text{redo since checkpoint}/(\text{replay bw}\times \text{cores}))$ via SiloR-style parallel replay. These are constructive, achieved bounds in the shared-memory multicore model. Epoch length $E$ is the single tunable trading throughput/latency against the loss window.

## 5. Lower Bound
Information-theoretically, *any* batched-durability scheme that releases an epoch's results only after persisting that epoch must lose at least the un-persisted in-flight epoch on a single-domain crash — so the loss window cannot be smaller than the persistence latency without reverting toward per-commit fsync (recovering the latency–durability impossibility from the bounded-staleness problem). Releasing results *before* epoch persistence would violate recoverability (a crash could erase a transaction whose effects clients observed), an FLP/recoverability-style impossibility. In the distributed setting, agreeing on a global epoch boundary under asynchrony is bounded by consensus lower bounds (FLP: no deterministic async consensus with one crash). The hardness is *information-theoretic and consensus-theoretic*, not computational.

## 6. The Gap
For single-node in-memory OLTP, upper and lower bounds essentially meet — hence *partially-solved*: the mechanism is optimal up to the persistence-latency floor. Open gaps: (i) **optimal/adaptive epoch sizing** under shifting load (links to self-tuning recovery); (ii) **distributed epoch durability** that bounds loss across shards without a global stall (cross-shard barrier cost vs. loss window) lacks a tight characterization; (iii) interaction with **replication/quorum durability** (epoch + quorum bounds composed) is not fully formalized. Closing these needs a distributed epoch-agreement protocol with proven loss/latency bounds under realistic partial synchrony.

## 7. Current Research (as of June 2026)
Active: adaptive epoch length controllers reacting to load; epoch-based durability on persistent memory / CXL where the persist boundary is cache-line FLUSH+FENCE rather than fsync *(frontier — verify)*; integrating epoch commit with Raft/quorum replication so the durable epoch is the quorum-acked epoch *(frontier — verify)*. Groups: MIT (the Silo/SiloR lineage — Liskov, Kohler, Morris, Tu, Zheng), HP/FOEDUS lineage (Hideaki Kimura), and in-memory-engine teams. Epoch-based reclamation research feeds back into durability epoch machinery.

## 8. Future Work
(i) Provably optimal adaptive epoch sizing under bounded-burst load. (ii) Distributed/cross-shard epoch durability with tight loss bounds. (iii) Composing epoch durability with quorum replication and bounded-staleness frontiers. (iv) PM/CXL-native epoch persistence. (v) Formal verification of epoch-release recoverability invariants.

## 9. Key References
- **[Foundational]** Tu, S., Zheng, W., Kohler, E., Liskov, B., Madden, S. *Speedy Transactions in Multicore In-Memory Databases (Silo).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522713)
- **[SOTA]** Zheng, W., Tu, S., Kohler, E., Liskov, B. *Fast Databases with Fast Durability and Recovery through Multicore Parallelism (SiloR).* OSDI, 2014. — [USENIX](https://www.usenix.org/conference/osdi14/technical-sessions/presentation/zheng_wenting)
- **[SOTA]** Kimura, H. *FOEDUS: OLTP Engine for a Thousand Cores and NVRAM.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2746480)
- **[Foundational]** Fischer, M., Lynch, N., Paterson, M. *Impossibility of Distributed Consensus with One Faulty Process (FLP).* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[Foundational]** Chandy, K.M., Lamport, L. *Distributed Snapshots: Determining Global States of Distributed Systems.* ACM TOCS, 1985. — [DOI](https://doi.org/10.1145/214451.214456)

## 10. Worked Example

Take epoch length $E = 40$ ms, arrival rate $\lambda = 50{,}000$ txns/s, and persist (fsync) latency $= 10$ ms, with single-epoch lag ($D = \mathcal{E}-1$).

**Throughput / fsync amortization.** Transactions per epoch $= E\cdot\lambda = 0.040 \times 50{,}000 = 2000$. One fsync persists the whole epoch, so the fsync cost is amortized over 2000 commits instead of paying $10$ ms per commit — a per-commit log-flush of $10/2000 = 5\ \mu$s of fsync time.

**Loss bound.** A crash can lose only epochs $> D$. With single-epoch lag that is at most one in-flight epoch $\approx E\lambda = 2000$ transactions.

**Client-visible latency.** A txn that commits logically just after epoch $e$ opens waits up to $E$ for the epoch to close, plus the persist latency: $\le 40 + 10 = 50$ ms before its result is released.

**Tuning trade-off.** Halving to $E = 20$ ms cuts the loss window and commit latency ($\le 30$ ms) but doubles the fsync rate (now 1000 txns amortize each fsync, $10\ \mu$s/commit). This is the monotone latency-loss-vs-throughput dial in $E$; the loss window cannot fall below the $10$ ms persist latency without reverting toward per-commit fsync.

---
*Part of the [DBMS Research catalog](../../README.md).*
