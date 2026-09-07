---
id: 11-nosql-kv/compaction-write-stall-theory
title: "Compaction Write-Stall Theory"
topic: 11-nosql-kv
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
refs_unverified: 1
---

# Compaction Write-Stall Theory

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/compaction-write-stall-theory` · **Status:** open

## 1. Problem Statement

In a log-structured merge-tree (LSM) store, incoming writes land in an in-memory memtable, are flushed to L0 SSTables, and are progressively merged into deeper levels by **compaction**. When ingestion outpaces compaction throughput, the system must apply **backpressure** (throttle or stall writers) to bound read amplification and L0 file count. A **write stall** is a sharp, often catastrophic latency cliff where client write latency jumps by orders of magnitude.

We seek a **theory** that:
- **Decision variant:** Given an ingestion rate $\lambda(t)$, a compaction budget (I/O bandwidth $B$), and an LSM shape, decide whether a stall is reachable within horizon $T$.
- **Optimization variant:** Schedule compaction work and admission control to **minimize stall probability / tail latency** subject to bounded space and read amplification.
- **Characterization variant:** Identify the exact phase boundary (the "cliff") in the $(\lambda, B, \text{level config})$ parameter space separating stable operation from runaway L0 accumulation.

The goal is *provable* stall avoidance: an admission/compaction policy with a guaranteed latency or stability bound, not just empirical tuning.

## 2. Mathematical Foundations

An LSM with size ratio $T$ and $L$ levels has classic amortized costs (Dayan–Idreos–Athanassoulis, *Monkey/Dostoevsky*):
$$\text{write amp} = O\!\left(\frac{T \cdot L}{B}\right),\quad \text{read amp (point, leveled)} = O(L),\quad L = \Theta\!\left(\log_T \frac{N}{M}\right)$$
where $N$ is data size, $M$ memtable size, $B$ block size.

The stall phenomenon is naturally a **queueing / fluid-limit** problem. Model compaction as a server draining the L0 queue at rate $\mu$ (bounded by $B$ and merge fan-in) against arrivals $\lambda$. Stability requires $\rho = \lambda/\mu < 1$; but compaction $\mu$ is **state-dependent** (deeper levels steal bandwidth), giving a coupled multi-class queueing network. Write stalls correspond to a **metastability** / **bistable** regime: a transient overload pushes L0 past a threshold from which the system cannot recover without throttling — analogous to **metastable failures in distributed systems** (Bronson et al., HotOS 2021).

Relevant tools: fluid and diffusion limits of queueing networks, Lyapunov stability ($\exists$ Lyapunov function $V$ with negative drift outside a bounded region $\Rightarrow$ positive recurrence), and control-theoretic backpressure (Lyapunov drift-plus-penalty, Neely).

## 3. State of the Art (SOTA)

- **Theory-SOTA** for LSM cost is the Dayan et al. line (**Monkey**, SIGMOD 2017; **Dostoevsky**, SIGMOD 2018; **Spooky/lazy leveling**) which gives tight Pareto bounds on read/write/space amplification but treats compaction as amortized, *not* the transient stall dynamics.
- **SILK** (Balmau et al., USENIX ATC 2019) directly targets stalls via an I/O scheduler that prioritizes flushes/L0 compactions and opportunistically schedules deep compactions — strong empirical results, limited formal guarantee.
- **RocksDB** uses heuristic stall triggers (`level0_slowdown/stop_writes_trigger`, pending-compaction-bytes throttling) — the de-facto systems baseline, hand-tuned.
- **ADOC** (Yu et al., FAST 2023) auto-tunes batching/compaction concurrency to reduce stalls via a data-overflow-aware controller.
- Theoretical stall characterization remains largely **open**: no widely accepted closed-form for the stall boundary.

## 4. Upper Bound

No general matching upper bound on stall-free throughput is known. Partial results: for a single-level fluid model with constant compaction bandwidth, an admission controller that caps $\lambda \leq \mu_{\min}$ (the worst-case state-dependent compaction rate) trivially guarantees no stall, but is pessimistic (wastes burst capacity). SILK-style prioritization empirically sustains throughput within a small factor of peak without stalls. The achievable bound under bursty arrivals — e.g., a $(\sigma,\rho)$ token-bucket-constrained guarantee on max write latency — is conjectured but not proven tight.

## 5. Lower Bound

Lower bounds here are mostly **structural / impossibility**: 
- Any policy bounding read amplification at $O(L)$ while admitting unbounded burst ingestion must eventually stall (a counting argument: L0 files cannot exceed a threshold without violating the read-amp invariant, so once arrival integral exceeds compaction integral the queue must be shed — i.e., throttled).
- The metastability framing implies the absence of a *memoryless* stall-free controller: because compaction rate depends on accumulated state, no admission policy ignoring LSM internal state can be both work-conserving and stall-free (analogous to metastable-failure inevitability without load-shedding).
- No SETH/3SUM-style fine-grained lower bound is established; the hardness is dynamical, not combinatorial-reduction-based.

## 6. The Gap

The gap is **wide and genuinely open**. We have (a) tight *amortized* amplification bounds and (b) effective *empirical* schedulers, but **no theory connecting them to transient stall dynamics**. Missing: a closed-form or tight characterization of the stall phase boundary in $(\lambda, B, T, L)$ space, and a provably near-optimal online compaction+admission policy with a competitive-ratio or regret guarantee against burst adversaries. Closing it requires importing queueing/metastability/control theory and proving stability (Lyapunov) plus a matching impossibility.

## 7. Current Research (as of June 2026)

- Control-theoretic and learning-based compaction scheduling (Harvard DASlab — Idreos; EPFL — Balmau lineage) *(frontier — verify)*.
- Formal metastability analysis applied to storage backpressure, extending Bronson et al. *(frontier — verify)*.
- Disaggregated/tiered LSMs reshaping the bandwidth model and thus the stall boundary (see tiered-storage problem).
- RocksDB/Speedb production work on smoother, predictive stall avoidance and write throttling curves.

## 8. Future Work

- A Lyapunov-stable, work-conserving admission + compaction controller with provable tail-latency bounds under $(\sigma,\rho)$ arrivals.
- Phase-diagram characterization of the stall cliff and early-warning signals.
- Competitive-analysis / regret bounds for online compaction scheduling.
- Integration with learned ingestion forecasting.

## 9. Key References

- **[Foundational]** O'Neil, P., Cheng, E., Gawlick, D., O'Neil, E. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996. — [DOI](https://doi.org/10.1007/s002360050048)
- **[SOTA]** Dayan, N., Athanassoulis, M., Idreos, S. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DBLP](https://dblp.org/rec/conf/sigmod/DayanAI17.html)
- **[SOTA]** Dayan, N., Idreos, S. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based KV Stores.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196927)
- **[SOTA]** Balmau, O., et al. *SILK: Preventing Latency Spikes in Log-Structured Merge Key-Value Stores.* USENIX ATC, 2019. — [USENIX](https://www.usenix.org/conference/atc19/presentation/balmau)
- **[SOTA]** Yu, J., et al. *ADOC: Automatically Harmonizing Dataflow for LSM-based KV Stores.* FAST, 2023. — [USENIX](https://www.usenix.org/conference/fast23/presentation/yu)
- **[Foundational]** Bronson, N., et al. *Metastable Failures in Distributed Systems.* HotOS, 2021. — [DOI](https://doi.org/10.1145/3458336.3465286)

## 10. Worked Example

Model L0 as a single queue. Flushes arrive at rate $\lambda$ files/s; compaction drains L0 at $\mu$ files/s. RocksDB stalls when L0 file count hits `level0_stop_writes_trigger` $= 36$, and slows at $20$.

**Stable regime.** Let $\lambda = 8$, $\mu = 10$. Utilization $\rho = \lambda/\mu = 0.8 < 1$: the queue is positive-recurrent, mean L0 depth stays near $\rho/(1-\rho) = 4$ files — comfortably below 20.

**Metastable trigger.** Now a burst pushes L0 to 22 files, crossing the slowdown line. Deeper-level compaction steals bandwidth, so the *state-dependent* drain rate drops to $\mu' = 6$. Suddenly $\rho' = 8/6 = 1.33 > 1$: the queue grows at $\lambda - \mu' = 2$ files/s. From 22 files it reaches the stop trigger 36 in $(36-22)/2 = 7$ s, after which writers stall — and removing the original burst does *not* help, because the system is now in the self-sustaining $\rho'>1$ basin (the bistable cliff).

The fix: admission control capping $\lambda \le \mu' = 6$ keeps $\rho' < 1$ and provably avoids the runaway, at the cost of burst throughput.

---
*Part of the [DBMS Research catalog](../../README.md).*
