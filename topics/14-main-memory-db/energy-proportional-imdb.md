---
id: 14-main-memory-db/energy-proportional-imdb
title: "Energy-Proportional In-Memory Storage"
topic: 14-main-memory-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Energy-Proportional In-Memory Storage

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/energy-proportional-imdb` · **Status:** open

## 1. Problem Statement
A large in-memory database keeps its working set (and often the entire dataset) in DRAM. DRAM is **not energy-proportional**: it consumes substantial power even when idle, dominated by *refresh* (periodic recharge of capacitor cells to prevent bit decay, every ~64 ms) plus background/static power. A 1 TB DRAM footprint can draw tens of watts at zero query load. Yet the value proposition of an IMDB is *instant availability* — sub-microsecond access with no warm-up.

**Problem:** keep a large in-memory database simultaneously (a) **energy-efficient at low/idle load** — power should scale toward zero as utilization drops (energy proportionality) — and (b) **instantly available** — no measurable latency penalty when a request arrives for any datum. These goals conflict: the standard low-power levers (powering down ranks, self-refresh, partial-array self-refresh, migrating to NVM/SSD) all impose wake-up latency or lose data. Variants:
- **Optimization:** Minimize expected energy $\mathbb{E}[P]$ subject to a tail-latency SLO.
- **Online:** Decide per-region power state without knowing future accesses (rent-or-buy / spin-down style).
- **Placement:** Which tuples live in always-on DRAM vs. low-refresh/NVM tiers.

## 2. Mathematical Foundations
Partition memory into regions (ranks/banks) $r_1,\dots,r_m$, each in a power state $\sigma \in \{\text{active}, \text{self-refresh}, \text{partial-refresh}, \text{off}\}$ with power $P(\sigma)$, retention guarantee, and transition (wake) latency $\tau(\sigma)$. Access to a datum in a low state pays a *miss penalty*. With access process $\{a_t\}$ (often Zipfian — hot/cold tuple distribution), the controller chooses a schedule of states minimizing
$$\mathbb{E}\Big[\textstyle\int P(\sigma_t)\,dt\Big] \quad \text{s.t.} \quad \Pr[\text{latency} > \ell] \le \delta.$$
This is an instance of **online power management / spin-down**, classically modeled as a *rent-or-buy* (ski-rental) decision per region: keep refreshing (rent) vs. power down and pay wake cost (buy). Refresh energy scales with temperature and capacity; *approximate-DRAM* relaxes retention for cold/error-tolerant data, trading refresh energy for a controlled bit-error rate, connecting to coding/information theory (retention as a channel with erasure probability rising as refresh interval lengthens).

## 3. State of the Art (SOTA)
- **Systems-SOTA.** Hardware: **RAIDR** (Liu, Jaiyen, Veras, Mutlu, ISCA 2012) groups rows by retention time and refreshes weak rows more often, cutting refresh energy substantially. **Partial Array Self-Refresh (PASR)** and rank-level power-down are standard DDR features. DB-side: **anti-caching** (DeBrabant, Pavlo, Tu, Stonebraker, Zdonik, VLDB 2013) evicts cold tuples from memory entirely, shrinking the always-resident footprint; **Siberia** (Hekaton cold-data classification, Eldawy/Levandoski/Larson, ICDE 2014) similarly tiers cold data. **NVM/PMEM and CXL-attached memory** offer near-DRAM access with lower idle/refresh energy for cold tiers.
- **Theory-SOTA.** Online power-down with bounded competitive ratio (Irani, Shukla, Gupta and the dynamic-power-management literature).

No system delivers *provably* energy-proportional IMDB storage with an instant-availability guarantee — it remains open.

## 4. Upper Bound
For the per-region online spin-down decision, the classic **rent-or-buy** result gives a deterministic **2-competitive** algorithm and a randomized $\frac{e}{e-1}\approx 1.58$-competitive algorithm against energy (when wake latency is folded into cost). RAIDR-style retention-aware refresh reduces refresh energy by a constant factor (reported ~70% of refreshes elided in favorable cases) with no latency penalty. Anti-caching/tiering reduces always-on DRAM to the hot working-set size $W$, giving energy $\approx P_{\text{DRAM}}\cdot W + P_{\text{cold-tier}}\cdot(D-W)$ for dataset $D$ — but availability of cold data degrades to the cold tier's latency.

## 5. Lower Bound
The **online lower bound** for deterministic power management is $2 - o(1)$ (ski-rental), and $\frac{e}{e-1}$ for randomized — so no online controller can be energy-proportional *and* latency-safe better than these factors without future knowledge. Physically, **DRAM retention** imposes a hard floor: any cell holding data must be refreshed within its retention time or lose it, so *non-approximate* storage cannot drive refresh energy to zero — a thermodynamic/information lower bound $P_{\text{refresh}} \ge f(\text{retained bits}, T)$. Instant availability forbids deep power-down for any potentially-accessed region, so the always-available footprint cannot be powered below its active floor — establishing a fundamental tension (an *availability–energy uncertainty*): you cannot have both zero idle power and zero wake latency for the same data.

## 6. The Gap
Hardware techniques (RAIDR, PASR) and software tiering (anti-caching, Siberia) each attack one side, but there is **no unified scheme** with a provable energy-proportionality guarantee under a tail-latency SLO. The online competitive bounds are clean but assume a single region in isolation; the *joint* multi-region, workload-skewed, retention-aware problem with an availability constraint has no matching upper/lower bound. It is genuinely open whether NVM/CXL tiering can asymptotically close the gap — i.e., make idle energy scale with the hot-set size while preserving sub-microsecond access to cold data.

## 7. Current Research (as of June 2026)
Directions: CXL memory pooling and tiered DRAM/NVM to make cold capacity cheap in idle energy without warm-up cliffs; approximate-DRAM and retention-relaxed storage for error-tolerant analytics; learned hot/cold classification driving fine-grained power states; and refresh-elision via in-memory ECC. Groups: CMU SAFARI (Mutlu — RAIDR lineage), CMU DB (Pavlo — anti-caching), Microsoft Research (Hekaton/Siberia tiering), and the CXL/disaggregated-memory community. Energy-proportional tiering over CXL with availability SLOs is an active 2025-2026 frontier *(frontier — verify)*.

## 8. Future Work
- A controller with provable energy proportionality under a tail-latency SLO across many regions.
- Tight competitive analysis of multi-region retention-aware power management with workload prediction (learning-augmented).
- Co-design of approximate-DRAM bit-error budgets with DB correctness (which columns tolerate decay).
- CXL/NVM tiering that eliminates the warm-up cliff entirely.

## 9. Key References
- **[Foundational]** Liu, Jaiyen, Veras, Mutlu. *RAIDR: Retention-Aware Intelligent DRAM Refresh.* ISCA, 2012. — [DBLP](https://dblp.org/rec/conf/isca/LiuJVM12.html)
- **[SOTA]** DeBrabant, Pavlo, Tu, Stonebraker, Zdonik. *Anti-Caching: A New Approach to Database Management System Architecture.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2556549.2556575)
- **[SOTA]** Eldawy, Levandoski, Larson. *Trekking Through Siberia: Managing Cold Data in a Memory-Optimized Database.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2732967.2732968)
- **[Foundational]** Irani, Shukla, Gupta. *Online Strategies for Dynamic Power Management in Systems with Multiple Power-Saving States.* ACM TECS, 2003. — [DOI](https://dl.acm.org/doi/10.1145/860176.860180)
- **[Survey]** Mutlu. *Memory Scaling: A Systems Architecture Perspective.* IMW, 2013. — [DOI](https://doi.org/10.1109/IMW.2013.6582088)

## 10. Worked Example

**Ski-rental for one DRAM rank.** A rank costs $P_{\text{idle}} = 1$ unit/sec to keep refreshed. Powering it down saves that, but waking it on the next access costs a fixed penalty $B = 10$ units (energy of refill + the latency tax). The controller, seeing no access, must decide each second: keep refreshing (rent) or power down now (buy the wake-up).

The classic deterministic rule: keep refreshing until accumulated idle cost equals the buy cost $B$, then power down. Here, refresh for $10$ s, then spin down. Worst case the access arrives just after you spin down: you paid $10$ (refreshing) $+ 10$ (wake) $= 20$, versus the offline optimum of $10$ (had you spun down immediately). Ratio $20/10 = 2$ — matching the **2-competitive** upper and lower bound of sections 4-5.

**Tiering arithmetic.** Dataset $D = 1$ TB, hot set $W = 50$ GB, $P_{\text{DRAM}} = 0.04$ W/GB, cold-tier (CXL/NVM) $P_{\text{cold}} = 0.005$ W/GB. Idle power $\approx 0.04 \times 50 + 0.005 \times 950 = 2 + 4.75 = 6.75$ W, versus all-DRAM $0.04 \times 1000 = 40$ W — a $5.9\times$ idle reduction, but cold accesses now pay the tier's wake latency.

---
*Part of the [DBMS Research catalog](../../README.md).*
