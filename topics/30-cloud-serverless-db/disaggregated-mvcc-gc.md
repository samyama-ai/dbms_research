# Disaggregated MVCC garbage collection

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/disaggregated-mvcc-gc` · **Status:** open
> **Verification note:** The "Hekaton" VLDB 2011 concurrency-control paper is by Larson, Blanas, Diaconu, Freedman, Patel & Zwilling; Lomet is not an author of that specific paper (he authored other Hekaton-era recovery work).

## 1. Problem Statement
Multi-version concurrency control (MVCC) keeps multiple physical versions of each tuple so readers see a consistent snapshot without blocking writers. A version becomes **garbage** once no current or future transaction can observe it. **GC** reclaims such versions to bound space and keep version chains short.

In **disaggregated** cloud databases (compute separated from a shared, elastic **version/log store** on separate scalable tiers — Aurora, Socrates, Neon, PolarDB-style), the classic single-process GC assumptions break:
- readers, writers, and the version store live on **different nodes** that fail and scale independently;
- the "oldest active snapshot" (the **watermark**) is distributed and changes as compute elastically appears/disappears;
- reclaiming a version requires a **globally safe** decision under partial information and message delay.

Variants:
- **Decision (safety):** is version $v$ safe to reclaim given the (distributed) set of live snapshots?
- **Optimization:** maximize reclaimed space / minimize chain length while *never* reclaiming a version some reader can still read, and minimizing coordination/RTT cost.
- **Online/streaming:** maintain the watermark continuously as snapshots and nodes churn.

## 2. Mathematical Foundations
Let transactions take snapshots with begin-timestamps from a (logical or hybrid) clock. A version $v$ of tuple $t$ is valid over interval $[\text{begin}(v), \text{end}(v))$. Define the **low-water mark**
$$\tau^* = \min_{T \in \text{Active} \cup \text{Future-reachable}} \text{snap}(T).$$
A version is reclaimable iff it is *superseded* and invisible to all snapshots $\ge \tau^*$: there exists a newer committed version covering the same key for every snapshot in $[\,\tau^*, \infty)$. Correctness is a **safety property** (never reclaim a visible version); progress is a **liveness property** (eventually reclaim dead versions).

Computing $\tau^*$ across nodes is a **distributed minimum / aggregate watermark** problem, formally equivalent to computing a consistent **global snapshot** (Chandy–Lamport) of the active-snapshot multiset, under asynchrony and failures. With unreliable channels and crash faults this inherits **FLP**-style limits: you cannot both guarantee safe reclamation and guaranteed progress in a fully asynchronous system with failures without some synchrony/lease assumption. Hybrid Logical Clocks (HLC) and bounded-clock-skew (TrueTime-style $\epsilon$) assumptions convert the problem into bounded-staleness watermark maintenance, where space overhead is $O(\epsilon \cdot \text{write-rate})$ extra retained versions.

GC scheduling itself (which chains to compact when, to minimize space under a coordination budget) is an online problem reducible to interval/segment cleaning, with **competitive-ratio** analysis analogous to log-structured-storage cleaning.

## 3. State of the Art (SOTA)
- **Systems-SOTA (single-node):** HyPer/Hekaton/SAP-HANA-style MVCC GC — the **Steam/HANA** cleaning and the precise visibility-based GC studied by Böttcher et al. (*Scalable Garbage Collection for In-Memory MVCC Systems*, VLDB 2019) is the reference for fine-grained, low-overhead reclamation.
- **Disaggregated systems:** Amazon **Aurora** (log-is-the-database; storage applies redo and GCs old pages), Microsoft **Socrates/SQL DB Hyperscale** (XLOG + page servers), **Neon** (separate Pageserver + Safekeepers with PITR retention), **PolarDB**, and **TiKV/Percolator**-style GC with a centralized GC-safe-point timestamp from a placement driver (PD). These ship working GC but with **conservative, centralized safe-points** and coarse retention windows.
- **Theory-SOTA:** epoch-based reclamation (EBR), quiescent-state and interval-based reclamation (QSBR/IBR) from concurrent-data-structure literature provide the safety framework adapted here.

## 4. Upper Bound
- Single-node **precise** MVCC GC runs in amortized $O(1)$ per reclaimed version with the Böttcher-style interval bookkeeping; watermark recomputation is $O(\\#\text{active txns})$.
- In the distributed setting, a **centralized lease-based safe-point** (TiKV/PD model) gives correct GC with $O(1)$ coordination per epoch and retention overhead $O(\text{lease} \times \text{write-rate})$ — i.e., you can always be *safe* by retaining anything newer than the global min snapshot computed each epoch, at the cost of staleness-proportional space.
- Epoch/grace-period reclamation guarantees reclamation within one bounded grace period after the last reader leaves (assuming partial synchrony).

## 5. Lower Bound
- **FLP impossibility:** in a fully asynchronous disaggregated system with crash failures, no GC protocol can guarantee both never-reclaim-visible *and* bounded-time progress — some synchrony (leases, bounded skew) is necessary; this is a genuine impossibility, not just hardness.
- **Coordination lower bound:** to *immediately* reclaim a version after the last reader departs requires at least one round-trip of agreement on the watermark; in the worst case any safe scheme retains versions for at least the message-delay / clock-uncertainty window (an $\Omega(\epsilon)$ or $\Omega(\text{RTT})$ space floor).
- Deciding an *optimal* GC/compaction schedule minimizing total I/O under a coordination budget is **NP-hard** (reduces from interval/segment-cleaning scheduling), analogous to optimal log cleaning.

## 6. The Gap
There is **no consensus protocol or algorithm** that gives *precise* (HyPer-class) reclamation with *provable* bounds on retention, coordination cost, and progress in the elastic-disaggregated, fault-prone setting. Production systems sit at the conservative-but-safe corner (centralized safe-points, fixed retention) and pay space/staleness; precise single-node theory pays unacceptable coordination if lifted naïvely. The open question: **what is the optimal trade-off curve between coordination rounds, clock-uncertainty $\epsilon$, and retained-version space for safe GC** — and is there a protocol matching it? This is genuinely **open**.

## 7. Current Research (as of June 2026)
- **Watermark/safe-point protocols** that are decentralized and failure-aware (gossip- or epoch-vector-based) rather than single-PD *(frontier — verify)*.
- Serverless/auto-suspend compute that vanishes and resumes: GC must reason about *future* compute that may re-attach an old snapshot (Neon-style PITR retention semantics).
- Bounded-staleness GC under HLC/TrueTime to shrink the retention floor.
- Co-design of GC with **multi-version index** maintenance and tiered (hot/cold/object-store) version placement.

## 8. Future Work
- A formal model + protocol with tight bounds on (coordination, $\epsilon$, space) for disaggregated MVCC GC.
- Reclamation correct under elastic scale-to-zero and re-attachment of stale readers.
- Cost-/carbon-aware GC scheduling (when to spend I/O to compact).
- Verifiable GC (proving no live version was reclaimed) for compliance.

## 9. Key References
- **[Foundational]** David Lomet, et al. / Per-Åke Larson et al. *High-Performance Concurrency Control Mechanisms for Main-Memory Databases (Hekaton).* VLDB, 2011. — [DOI](https://doi.org/10.14778/2095686.2095689) · [arXiv](https://arxiv.org/abs/1201.0228)
- **[SOTA]** Jan Böttcher, Viktor Leis, Thomas Neumann, Alfons Kemper. *Scalable Garbage Collection for In-Memory MVCC Systems.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3364324.3364328)
- **[SOTA]** Alexandre Verbitski, et al. *Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3056101)
- **[SOTA]** Panagiotis Antonopoulos, et al. *Socrates: The New SQL Server in the Cloud.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3314047)
- **[Foundational]** Michael J. Fischer, Nancy A. Lynch, Michael S. Paterson. *Impossibility of Distributed Consensus with One Faulty Process.* JACM, 1985. — [DOI](https://doi.org/10.1145/3149.214121)
- **[Foundational]** K. Mani Chandy, Leslie Lamport. *Distributed Snapshots: Determining Global States of Distributed Systems.* ACM TOCS, 1985. — [DOI](https://doi.org/10.1145/214451.214456)

## 10. Worked Example

A key $k$ has three committed versions: $v_1$ valid over $[5,9)$, $v_2$ over $[9,14)$, $v_3$ over $[14,\infty)$ (begin-timestamps from a logical clock). Three compute nodes hold active snapshots: $T_a@7$, $T_b@12$, $T_c@20$.

*Low-water mark.* $\tau^* = \min\{7, 12, 20\} = 7$.

*Reclaimability check.* A version is collectible only if it is invisible to **every** snapshot $\ge \tau^*$.
- $v_1$ ($[5,9)$) is read by $T_a@7$ ($7 \in [5,9)$) → **not** collectible.
- $v_2$ ($[9,14)$) is read by $T_b@12$ → **not** collectible.
- $v_3$ is the latest → never collectible.

So nothing is reclaimed yet, even though $v_1$ looks "old."

*Watermark advance.* $T_a$ commits and leaves. New low-water mark $\tau^* = \min\{12, 20\} = 12$. Re-check $v_1$ ($[5,9)$): is any live snapshot $\ge 12$ inside $[5,9)$? No — $12 \notin [5,9)$ and $20 \notin [5,9)$. Now $v_1$ is **safe to reclaim**.

*Distributed cost.* Computing the new $\tau^*=12$ requires aggregating the active-snapshot set across nodes — a consistent global-min (Chandy–Lamport-style) computation. Under a centralized lease safe-point refreshed every epoch of length $L$, we conservatively retain anything newer than the last-computed min, so up to $L \times (\text{write-rate})$ extra dead versions linger — the $\Omega(\text{RTT})$/$\Omega(\epsilon)$ space floor of section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
