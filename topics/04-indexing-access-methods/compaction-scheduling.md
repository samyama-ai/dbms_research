# Compaction scheduling under bursty writes

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/compaction-scheduling` · **Status:** empirically-open

## 1. Problem Statement
An **LSM-tree** absorbs writes into a memory buffer and periodically **compacts** sorted runs to bound the number of runs a read must inspect. Compaction is the central scheduling lever: too little and read amplification (and write stalls when buffers fill) explode; too much and CPU/I/O bandwidth is consumed, also stalling writes. Under **bursty arrivals** — write rate spiking far above steady state — the scheduler must decide *when, what, and how much* to compact, online and without knowledge of future bursts.

The problem: **design an online compaction scheduler that simultaneously bounds read tail latency (e.g., p99) and bounds write-stall duration under adversarial or stochastic bursts**, subject to fixed device bandwidth.

- **Optimization variant:** minimize a cost $\alpha \cdot \text{p99-read} + \beta \cdot \text{stall-time}$ over an online request sequence; measure **competitive ratio** vs. an offline optimum.
- **Decision variant:** given bandwidth $B$ and burst envelope, does a schedule exist keeping both metrics under thresholds?
- **Control variant:** as a feedback-control / queueing problem, keep run-count and buffer occupancy within bounds.

*Empirically-open:* heuristics (leveled, tiered, hybrid, rate-limited) are widely deployed and tuned; no scheduler has a proven competitive guarantee on the joint read-tail / write-stall objective under bursts.

## 2. Mathematical Foundations
Model the LSM as levels $0..L$ with size ratio $T$; total write amplification under leveling is $\Theta(T \log_T (N/B))$ and read amplification $\Theta(\log_T(N/B))$ — the **Dostoevsky / Monkey** analyses (Dayan et al.) make these tradeoffs precise via a tunable merge policy. Scheduling adds a **temporal/queueing** layer:

- **Queueing model:** writes arrive as a (possibly self-similar / heavy-tailed) process; the buffer is a queue drained by flushes, and compaction is a service process competing for bandwidth. Stalls = buffer-full events; tail read latency ∝ number of unmerged runs.
- **Online/competitive framing:** an adversary controls the burst sequence; the scheduler is an online algorithm whose **competitive ratio** bounds its cost vs. a clairvoyant offline scheduler. Related to **online scheduling with deadlines** and **smoothed analysis** of bursts.
- **Control theory:** rate-limited compaction is a feedback loop; stability and overshoot bounds (e.g., via Lyapunov arguments) bound buffer occupancy.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **RocksDB** rate limiters, subcompactions, and dynamic level sizing; **Universal/tiered** vs. **leveled** policies; **SILK** (Balmau et al., USENIX ATC 2019) prioritizes/schedules I/O to *prevent latency spikes* by giving flushes/low-level compactions bandwidth priority during bursts; **ScyllaDB** controllers (backlog-based) and **Cassandra** UCS (Unified Compaction Strategy).
- **Theory-SOTA:** **Dostoevsky / Lethe / Spooky** (Dayan, Athanassoulis et al.) optimize *which* runs to merge and tombstone handling, characterizing the amplification frontier; **Wacky** continuum and **Endure** (Huynh et al., VLDB 2022) make compaction-policy choice *robust to workload uncertainty*. These optimize steady-state amplification, not online burst scheduling guarantees.

## 4. Upper Bound
Per-operation amplification upper bounds are tight in the **external-memory model**: leveled merging gives write amp $O(T\log_T(N/B))$, read amp $O(\log_T(N/B))$; the Bender et al. write-optimization frontier ($B^\varepsilon$-trees) gives the Pareto-optimal point/range vs. update tradeoff. For *scheduling*, the strongest results are **empirical SLA guarantees** (SILK bounds tail latency under tested bursts by I/O prioritization) and **robust-policy** bounds (Endure bounds worst-case cost over an uncertainty set). No online scheduler has a proven $O(1)$- or polylog-competitive ratio on the joint read-tail/stall objective.

## 5. Lower Bound
Lower bounds exist for the *static* tradeoff: the write-optimized lower bound (Brodal–Fagerberg) shows update/query amplification cannot both be made small — any structure improving updates pays on queries. For *scheduling under bursts*, the relevant impossibility is **bandwidth conservation**: under a fixed device bandwidth and an adversarial burst exceeding it, *some* metric must degrade (a flow/scheduling lower bound), and competitive-ratio lower bounds from **online scheduling with bandwidth constraints** apply. No model-specific tight competitive lower bound for the joint LSM objective has been established.

## 6. The Gap
The gap is between (a) **steady-state amplification theory** (tight) and **robust-policy selection** (Endure), and (b) the **online, temporal scheduling problem under bursts**, which is treated heuristically with empirical SLAs but no competitive guarantee. It is open whether a scheduler can be provably $O(\text{polylog})$-competitive on joint p99-read and write-stall under bounded-burst-envelope arrivals. Closing it needs a formal online/queueing model with matching upper and lower competitive bounds.

## 7. Current Research (as of June 2026)
- **Learned / RL-based compaction schedulers** that predict bursts and pre-compact, evaluated on tail latency *(frontier — verify)*.
- **Burst-envelope-aware admission and bandwidth partitioning** with provable stall bounds (control-theoretic) *(frontier — verify)*.
- **Disaggregated / remote-storage compaction** where bandwidth and latency are shared and metered (ties to disaggregated-index).
- Groups: Athanassoulis (BU), Dayan (Pliops/industry), EPFL (Balmau, SILK lineage), CMU (Pavlo / self-driving DB), ScyllaDB/RocksDB teams.

## 8. Future Work
- A competitive-analysis framework for online compaction scheduling under bounded bursts.
- Joint optimization of *policy* (which runs) and *schedule* (when/how much) with guarantees.
- SLA-driven schedulers with provable p99 read and stall bounds on disaggregated storage.

## 9. Key References
- **[Foundational]** P. O'Neil, E. Cheng, D. Gawlick, E. O'Neil. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996. — [DOI](https://doi.org/10.1007/s002360050048)
- **[Foundational]** G. Brodal, R. Fagerberg. *Lower Bounds for External Memory Dictionaries.* SODA, 2003. — [DBLP](https://dblp.org/rec/conf/soda/BrodalF03.html)
- **[SOTA]** N. Dayan, S. Idreos. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196927)
- **[SOTA]** O. Balmau, et al. *SILK: Preventing Latency Spikes in Log-Structured Merge Key-Value Stores.* USENIX ATC, 2019. — [USENIX](https://www.usenix.org/conference/atc19/presentation/balmau)
- **[SOTA]** A. Huynh, et al. *Endure: A Robust Tuning Paradigm for LSM Trees Under Workload Uncertainty.* VLDB, 2022. — [arXiv](https://arxiv.org/abs/2110.13801)
- **[Survey]** C. Luo, M. Carey. *LSM-based Storage Techniques: A Survey.* VLDB Journal, 2020. — [DOI](https://doi.org/10.1007/s00778-019-00555-y)

## 10. Worked Example

Device bandwidth $= 100$ MB/s, shared between flushing the write buffer and compaction. Steady write rate is 30 MB/s; a leveled LSM with size ratio $T=10$ pays write amplification $\approx T\log_T(N/B)$. Take a small tree with $\log_T(N/B) = 3$ levels, so each logical MB written triggers $\approx 30$ MB of compaction I/O. Steady-state I/O demand $= 30 + 30\times? $ — more precisely flush 30 MB/s plus compaction $\approx 30 \times (\text{per-level merge})$; budget it as $\approx 90$ MB/s, just under 100.

Now a **burst** lifts the write rate to 80 MB/s for 2 s. Required I/O jumps to $\approx 80 \times 3 = 240$ MB/s $\gg 100$. By bandwidth conservation, something must give: in those 2 s the deficit is $(240-100)\times 2 = 280$ MB of unserved work. A SILK-style scheduler spends the scarce 100 MB/s on **flushes + low-level compactions first** (keeping the buffer from filling, avoiding write stalls) and *defers* deep-level compaction — trading a temporary rise in read amplification (more runs to probe, higher p99) for zero stalls. The open question: prove a competitive ratio bounding the worst-case $\alpha\cdot\text{p99-read} + \beta\cdot\text{stall}$ over any burst envelope, which no deployed heuristic yet guarantees.

---
*Part of the [DBMS Research catalog](../../README.md).*
