---
id: 14-main-memory-db/tail-latency-compaction
title: "Tail-Latency Bounds Under Compaction"
topic: 14-main-memory-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Tail-Latency Bounds Under Compaction

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/tail-latency-compaction` · **Status:** empirically-open

## 1. Problem Statement
In-memory stores run continuous background reorganization: log-structured **compaction/merge**, **garbage collection** (epoch/MVCC version reclamation), **checkpointing**, and index rebuilds. These steal CPU, cache, and memory bandwidth from foreground requests, producing latency spikes precisely at the tail. The problem: **can a main-memory store provide a provable upper bound on $p99/p999$ (or worst-case) request latency while sustaining the throughput needed to keep background work from falling behind?**

Formally, with foreground arrival process $\lambda$, service requirement, and a background reclamation rate constraint (GC must keep up with garbage-generation rate $g$ to bound memory), give a scheduler such that $\Pr[\text{latency} > L] \le \delta$ for stated $L,\delta$.

Variants:
- *Decision:* given $(\lambda, g, \text{cores})$ and target $(L,\delta)$, does a feasible schedule exist?
- *Optimization:* minimize $p999$ subject to GC-keep-up (memory-bounded) and throughput floor.
- *Counting:* bound the number of background-induced preemptions per request.

## 2. Mathematical Foundations
This is **scheduling under interference + queueing theory**. Background work and foreground requests contend for shared resources (cores, LLC, memory bandwidth), so per-request service time is *stochastic with heavy tails* induced by interference. Tail latency under such interference is governed by the **fork-join / max-of-many** effect: a request touching $k$ shards has latency $\approx \max$ of $k$ component latencies, so even rare per-shard stalls dominate the tail (Dean–Barroso, "The Tail at Scale", CACM 2013).

For GC keep-up, treat garbage as a fluid: reclamation must satisfy rate $\mu_{gc} \ge g$ to keep live memory bounded (a stability/utilization condition $\rho < 1$). The scheduler must reserve bandwidth $\ge g$ for GC while leaving foreground tail bounded — a **mixed real-time scheduling** problem. Log-structured merge amplification: write amplification $\Theta(\log_T N)$ over $L$ levels with size ratio $T$ creates periodic merge bursts whose worst-case stall is $\Omega(\text{level size}/\text{bandwidth})$ unless work is fragmented. Epoch-based reclamation (Fraser; McKenney RCU) bounds reclamation delay by the *grace period* = slowest active thread's epoch lag, linking tail latency of GC to the slowest reader.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **Silo/SiloR** epoch GC; **MVCC version pruning** in Hekaton (Diaconu et al., SIGMOD 2013) and HyPer/Umbra (Neumann–Mühlbauer–Kemper, SIGMOD 2015) with serializable snapshot isolation; **Bw-tree** (Levandoski et al., ICDE 2013) defers structure modification via delta records (epoch-reclaimed). LSM tail mitigation: **SILK** (Balmau et al., ATC 2019) schedules compaction in I/O-idle gaps to bound tail; **PebblesDB**, **Dostoevsky/Monkey** (Dayan et al., SIGMOD 2017/2018) tune the merge policy frontier. Real-time GC literature (Metronome, Bacon et al., POPL 2003) bounds pause time by incrementalization.
- **Theory-SOTA:** Bigtable/LSM amplification tradeoffs (Dayan–Idreos) characterize the read/write/space frontier; per-request worst-case interference bounds are mostly absent.

## 4. Upper Bound
**Incrementalized / time-sliced** background work gives a controllable bound: Metronome-style real-time GC guarantees a minimum mutator utilization (MMU) — e.g. foreground gets $\ge x\%$ of every $T$-window — bounding pause to a tunable quantum. SILK empirically holds $p99$ within a small factor of the no-compaction baseline by prioritizing flushes and pacing compaction. Epoch reclamation bounds memory blow-up to garbage created within one grace period. These yield *conditional* upper bounds: bounded tail **if** background work is finely preemptible and cores are reserved at rate $\ge g$.

## 5. Lower Bound
No request-level worst-case bound can beat the shared-resource interference floor: if background work needs memory bandwidth $B_{gc}$ and total bandwidth is $B$, foreground throughput is capped at $B - B_{gc}$, and any request whose working set is evicted by a merge burst pays an $\Omega(\text{footprint}/B)$ refill stall — an information-theoretic lower bound on the spike. Queueing gives the classic result: as utilization $\rho \to 1$, tail latency $\to \infty$ (waiting time $\sim 1/(1-\rho)$ for M/G/1), so keeping GC at rate $g$ forces $\rho$ up and provably worsens the tail — a genuine throughput-vs-tail tradeoff. The fork-join max-of-$k$ effect lower-bounds multi-shard tail relative to single-shard.

## 6. The Gap
We have incremental-GC pause bounds and empirical LSM pacing, but **no closed-form, system-realistic $\Pr[\text{lat}>L]\le\delta$ guarantee** that simultaneously respects GC-keep-up, cache/bandwidth interference, and the queueing tail under high utilization. The gap between "tunable MMU pause bound" and "end-to-end request $p999$ bound under interference" is open and currently bridged only by measurement and heuristics.

## 7. Current Research (as of June 2026)
Threads: interference-aware schedulers using LLC/bandwidth partitioning (Intel RDT/CAT) to isolate background work; learned/feedback compaction pacing; microsecond-scale OS scheduling (Shenango/Caladan lineage) applied to DB background tasks *(frontier — verify)*; formal MMU-style bounds extended to bandwidth, not just CPU. Groups: EPFL (Falsafi/Balmau-LSM lineage), Harvard DASlab (Idreos/Dayan), MIT (Belay–Caladan), TUM (Neumann), CMU-DB (Pavlo).

## 8. Future Work
- An end-to-end tail bound combining queueing, cache/bandwidth interference, and GC-keep-up.
- Provably tail-optimal compaction-scheduling policies (not just empirical pacing).
- Co-designing MVCC version pruning with the scheduler to bound grace-period-induced tails.

## 9. Key References
- **[Foundational]** Dean, J., Barroso, L. A. *The Tail at Scale.* CACM, 2013. — [DOI](https://doi.org/10.1145/2408776.2408794)
- **[Foundational]** Bacon, D., Cheng, P., Rajan, V. *A Real-Time Garbage Collector with Low Overhead and Consistent Utilization (Metronome).* POPL, 2003. — [DOI](https://doi.org/10.1145/604131.604155)
- **[SOTA]** Balmau, O., et al. *SILK: Preventing Latency Spikes in Log-Structured Merge Key-Value Stores.* USENIX ATC, 2019. — [USENIX](https://www.usenix.org/conference/atc19/presentation/balmau)
- **[SOTA]** Dayan, N., Athanassoulis, M., Idreos, S. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064054)
- **[SOTA]** Levandoski, J., Lomet, D., Sengupta, S. *The Bw-Tree: A B-Tree for New Hardware Platforms.* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544834)
- **[SOTA]** Neumann, T., Mühlbauer, T., Kemper, A. *Fast Serializable Multi-Version Concurrency Control for Main-Memory Database Systems.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2749436)

## 10. Worked Example

Model the foreground as M/G/1 with mean service $S=10\,\mu s$. At arrival rate $\lambda=70{,}000$/s, utilization $\rho=\lambda S=0.70$. Mean queue wait (M/M/1 approximation) is $W_q \approx \frac{\rho}{1-\rho}S = \frac{0.70}{0.30}\cdot10 \approx 23\,\mu s$.

Now GC must keep up. Garbage is generated at $g$ requiring reclamation bandwidth equal to $20\%$ of a core. Reserving it pushes effective foreground utilization to $\rho'=0.70/0.80 = 0.875$, so $W_q' \approx \frac{0.875}{0.125}\cdot10 = 70\,\mu s$ — a $3\times$ tail-wait jump from the same arrival rate. This is the throughput-vs-tail tradeoff: as $\rho\to1$, $W_q\to\infty$.

Add interference: a merge burst evicts a request's $256\,$KB working set. With memory bandwidth $B=20$ GB/s, the refill stall is $256\text{KB}/B \approx 12.8\,\mu s$ — an additive spike on top of the queueing tail, exactly the $\Omega(\text{footprint}/B)$ floor of section 5. SILK-style pacing schedules the burst into an idle gap to dodge the eviction.

---
*Part of the [DBMS Research catalog](../../README.md).*
