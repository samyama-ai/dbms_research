---
id: 31-time-series-db/lsm-ingest-tuning
title: "High-ingest LSM tuning for time-series"
topic: 31-time-series-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# High-ingest LSM tuning for time-series

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/lsm-ingest-tuning` · **Status:** empirically-open
> **Verification note:** Endure (VLDB 2022) authors are Huynh, Chaudhari, Terzi, Athanassoulis (not Idreos); corrected in §9.

## 1. Problem Statement
Most write-heavy TSDBs store data in **Log-Structured Merge (LSM)** trees (RocksDB-backed, or bespoke TSM/chunk engines). Writes append to an in-memory memtable, flush to sorted on-disk runs, and background **compaction** merges runs to bound the number a read must consult. The tuning problem: choose flush and compaction policies that **sustain peak append throughput** while keeping **read amplification** (runs touched per query) and **space amplification** (bytes on disk / bytes of live data) bounded.

The LSM design space is governed by a three-way **RUM/amplification trade-off** (read, update/write, space): you cannot minimize all three at once. Time-series workloads have special structure — append-mostly, near-time-ordered keys, heavy range-scans by (series, time), TTL/retention deletes — that *should* permit better operating points than general KV, but exploiting it under variable ingest is hard.

- **Decision variant:** does a given policy sustain append rate $\lambda$ without unbounded memtable/L0 backlog (stability)?
- **Optimization variants:** minimize write amplification $W$ subject to read-amp $\le R$ and space-amp $\le S$; or minimize a weighted cost $\alpha W + \beta R + \gamma S$ under throughput $\lambda$.

**Empirically-open:** tuning is dominated by workload-specific knob-twiddling and online controllers; closed-form optimal policies under bursty, time-ordered ingest are not established.

## 2. Mathematical Foundations
For a leveled LSM with size ratio (fanout) $T$ and $L$ levels over $N$ entries with buffer $B$: $L = \lceil \log_T \frac{N}{B}\rceil$. The standard amplification model (Dayan–Athanassoulis–Idreos, *Monkey/Dostoevsky*):

- **Write amplification** $\approx O(T\cdot L) = O\!\big(T\log_T \tfrac{N}{B}\big)$ for leveling; tiering gives $O(L)=O(\log_T\frac NB)$ writes but higher read cost.
- **Point read** consults $O(L)$ runs (leveling) or $O(T\cdot L)$ (tiering), each gated by a **Bloom filter** with false-positive rate $\epsilon$; *Monkey* shows optimal memory allocation gives each level a *different* FPR, minimizing total read I/O for a fixed memory budget.
- **Space amplification:** leveling $\le 1+\frac1T$; tiering up to $T$.

**Lazy leveling / Fluid LSM** (Dostoevsky) interpolates between tiering and leveling per level to Pareto-dominate the classic designs. Time-ordered ingest changes the model: if keys arrive monotonically in time, compaction can be near-append-only (sorted runs rarely overlap in the time dimension), collapsing write amp toward $O(1)$ — but **out-of-order** arrival (see companion problem) reintroduces overlap and forces rewrites. Stability under arrival rate $\lambda$ is a queueing condition: flush+compaction service rate must exceed $\lambda$ or L0 backlog grows unboundedly (write stalls).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** *Monkey* (SIGMOD 2017) — optimal Bloom-filter memory allocation across levels; *Dostoevsky*/Fluid LSM (SIGMOD 2018) — lazy leveling Pareto frontier; *Wacky/Endure* — robust tuning under workload uncertainty. These give the cleanest amplification trade-off characterizations.
- **Systems-SOTA:** RocksDB (universal vs. leveled compaction, rate limiters, dynamic-level-bytes) underpins many TSDBs. InfluxDB TSM and Prometheus's chunk+head design are bespoke time-partitioned LSM-like engines; VictoriaMetrics uses an LSM-style merge tuned for metrics. Time-window compaction (Cassandra's TWCS, and TSDB block compaction in Prometheus where whole time-blocks merge then become immutable) exploits time-ordering and TTL alignment.

## 4. Upper Bound
Best-known *characterized* operating points: leveled LSM gives point-read $O(L)$ runs with per-level-tuned Bloom filters (Monkey) and write-amp $O(T\log_T\frac NB)$; lazy leveling (Dostoevsky) achieves a strictly better $(W,R,S)$ Pareto point — e.g. tiering-like writes with leveling-like point reads for the last level. For **purely time-ordered** ingest, time-window compaction achieves near-$O(1)$ write amplification and $O(\text{windows in range})$ read amplification, with space-amp $\approx 1$. Bloom/range filters (SuRF) bound wasted reads.

## 5. Lower Bound
The **RUM conjecture** (Athanassoulis et al., EDBT 2016) posits an unavoidable three-way trade-off: no access method simultaneously minimizes read, update, and memory/space amplification — an *empirical/structural* lower bound rather than a proven one. External-memory lower bounds (the **B-tree / buffer-tree** $\Omega(\log_B N)$ bounds, Brodal–Fagerberg) show a provable insert/query trade-off in the I/O model: you cannot get both $O(1/B)$-amortized inserts and $O(\log_B N)$ queries beyond the established frontier. For time-ordered data these worst-case bounds are pessimistic, but **no tight lower bound exists for the bursty, partially-ordered ingest regime** — which is exactly why the problem is empirically-open.

## 6. The Gap
For general KV, the $(W,R,S)$ frontier is well-mapped (Monkey/Dostoevsky/Endure) and close to the RUM-conjectured limit. The **open gap is the time-series-specific regime**: there is no closed-form optimal compaction policy for *bursty, mostly-ordered-with-late-arrivals* ingest, nor a proven lower bound for it. Closing it requires (a) a formal model of partially-ordered arrival (an "out-of-orderness" parameter) and (b) policies provably optimal in that parameter, instead of today's hand-tuned TWCS windows and online stall-avoidance controllers.

## 7. Current Research (as of June 2026)
Active: **learned / reinforcement-learned compaction** controllers that adapt fanout, trigger thresholds, and filter memory online to a measured workload; **Endure**-style robust tuning under workload uncertainty; **disaggregated / tiered-storage LSMs** (compaction offloaded to remote object storage, e.g. cloud-native TSDBs) reshaping the cost model *(frontier — verify)*. Time-window compaction refinements and Prometheus/Mimir block-compaction tuning continue empirically. Groups: Idreos's DASlab (Harvard) — Monkey/Dostoevsky/Endure; Athanassoulis (BU) — RUM/access-method design; RocksDB team (Meta); VictoriaMetrics/Grafana engineering.

## 8. Future Work
- A formal "out-of-orderness" parameter and compaction policy provably optimal in it.
- Online controllers with stability guarantees under bursty $\lambda$ (no unbounded L0 backlog).
- Compaction co-designed with TTL/retention so deletes are free.
- Disaggregated-storage amplification models and the new Pareto frontier they imply.
- Bridging the proven external-memory lower bounds to the partially-ordered TS regime.

## 9. Key References
- **[Foundational]** O'Neil, Cheng, Gawlick, O'Neil. *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica, 1996. — [DOI](https://doi.org/10.1007/s002360050048)
- **[Foundational]** Athanassoulis, Kester, Maas, Stoica, Idreos, Ailamaki, Callaghan. *Designing Access Methods: The RUM Conjecture.* EDBT, 2016. — [DOI](https://doi.org/10.5441/002/edbt.2016.42) — [DBLP](https://dblp.org/rec/conf/edbt/AthanassoulisKM16.html)
- **[SOTA]** Dayan, Athanassoulis, Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064054)
- **[SOTA]** Dayan, Idreos. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores via Adaptive Removal of Superfluous Merging.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196927)
- **[SOTA]** Huynh, Chaudhari, Terzi, Athanassoulis. *Endure: A Robust Tuning Paradigm for LSM Trees Under Workload Uncertainty.* VLDB, 2022. — [DOI](https://doi.org/10.14778/3529337.3529345) — [arXiv](https://arxiv.org/abs/2110.13801)
- **[Foundational]** Brodal, Fagerberg. *Lower Bounds for External Memory Dictionaries.* SODA, 2003. — [DBLP](https://dblp.org/rec/conf/soda/BrodalF03.html)

## 10. Worked Example

Take a leveled LSM with buffer $B = 10^6$ entries, fanout $T = 10$, and $N = 10^{10}$ entries. Number of levels:
$$L = \lceil \log_T (N/B) \rceil = \lceil \log_{10}(10^{10}/10^6) \rceil = \lceil \log_{10} 10^4 \rceil = 4.$$

- **Leveling write amp** $\approx O(T\cdot L) = 10\times 4 = 40$: each entry is rewritten ~40 times on its way to the bottom level.
- **Point read** consults $O(L) = 4$ runs; with a Bloom filter per level at FPR $\epsilon$, expected wasted I/O $\approx L\cdot\epsilon$. *Monkey* reallocates the same total filter memory so deeper (larger) levels get *lower* FPR, minimizing $\sum_i \epsilon_i$ instead of using a uniform $\epsilon$.
- **Tiering** instead gives write amp $O(L) = 4$ (10$\times$ cheaper writes) but point reads now probe $O(T\cdot L) = 40$ runs — the RUM trade-off in numbers.

**Time-series twist:** if timestamps arrive monotonically, each new flush covers a disjoint time range, so runs never overlap and compaction is near append-only: write amp collapses toward $O(1)$ instead of $40$. A burst of *late* (out-of-order) points reintroduces overlap on a few levels, forcing partial rewrites — exactly the partially-ordered regime §6 flags as lacking a proven optimal policy.

---
*Part of the [DBMS Research catalog](../../README.md).*
