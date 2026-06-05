# Tiered-Storage Compaction Placement

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/tiered-storage-compaction` · **Status:** empirically-open

## 1. Problem Statement

Modern KV stores run over a **storage hierarchy**: DRAM (cache/memtable), local SSD/NVMe, and remote **object storage** (S3-class), each with different cost-per-GB, bandwidth, latency, and durability. The placement problem: decide, for each LSM level (or SSTable, or block), **which tier holds it**, and how compaction moves data between tiers, so as to **minimize total cost** (storage \$ + I/O \$ + compute) subject to a **latency SLO** (e.g., $p99$ read latency $\leq \tau$) and a write/compaction throughput target.

Variants:
- **Static optimization:** Given a workload distribution (key access frequencies, read/write mix), choose a fixed level-to-tier assignment minimizing \$/month at SLO.
- **Online / dynamic:** Access patterns drift; place and migrate adaptively (a caching/eviction + compaction co-design).
- **Decision variant:** Does a feasible placement exist meeting SLO under a cost budget $C$?

This couples three classically separate problems: caching, LSM compaction policy, and data placement, under a cloud cost model where object-storage requests (GET/PUT) and egress are billed per operation.

## 2. Mathematical Foundations

Let tiers $t \in \{1,\dots,T\}$ have per-GB cost $c_t$, per-op cost $g_t$, latency $\ell_t$, bandwidth $b_t$. Let LSM levels $0..L$ have sizes $S_i$ and access rates (point + range) $r_i$. The static placement minimizes:
$$\min_{x_{i,t}\in\{0,1\}} \sum_{i,t} x_{i,t}\big(c_t S_i + g_t r_i + \text{compaction-IO}_i\big)\quad \text{s.t.}\ \sum_t x_{i,t}\ell_t r_i \leq \text{(SLO budget)},\ \sum_t x_{i,t}=1.$$

This is a **generalized assignment / facility-location-flavored** integer program, NP-hard in general. The caching subproblem is the classic **competitive paging** problem ($k$-server / weighted caching), with known competitive bounds. Because deeper LSM levels hold exponentially more data but are accessed exponentially less (under leveling, level $i$ holds $\sim T^i$ data accessed for a $1/T^i$ fraction of bloom-filtered point lookups), there is strong structure: an **optimal monotone tiering** (hot levels in fast tiers) is plausibly near-optimal, echoing the **Monkey** insight that Bloom-filter memory should be allocated non-uniformly across levels.

Cost-latency trade-offs invoke the **RUM conjecture** (Athanassoulis et al.): Read, Update, Memory amplification cannot all be minimized simultaneously — tiering adds a fourth axis ($\$$).

## 3. State of the Art (SOTA)

- **Systems-SOTA:** Cloud-native disaggregated KV stores — **RocksDB-Cloud** (Rockset), **Neon**, **CockroachDB** ranges over object storage, **TiKV/TiFlash**, and especially designs that put cold SSTable levels on S3 while keeping L0–L_k on NVMe.
- **Nova-LSM** (Huang et al., SIGMOD 2021): disaggregated, dynamically scalable LSM separating compaction/storage components.
- **PrismDB** (Raina et al.) and **MutantDB / Mutant** (Yoon et al., SoCC 2018): SSTable-granularity placement across heterogeneous storage to hit a cost target — directly this problem, solved heuristically.
- **WiscKey / key-value separation** (Lu et al., FAST 2016) changes the placement unit (values vs. keys), relevant to where large values live.
- Cloud vendors expose tiering (S3 Intelligent-Tiering) but it is request-frequency heuristic, not SLO-aware or compaction-aware.

## 4. Upper Bound

No provably optimal polynomial algorithm; the exact IP is NP-hard. Practical upper bounds are **approximation/heuristic**: monotone level-to-tier assignment computed greedily by access-rate density yields strong empirical cost reductions (Mutant reports large \$ savings at bounded latency). For the caching component, deterministic LRU/competitive paging gives a $k$-competitive guarantee and randomized marking gives $O(\log k)$-competitive — these bound the DRAM/SSD cache layer rigorously, but not the joint compaction-placement objective.

## 5. Lower Bound

- The static placement IP is **NP-hard** (reduction from generalized assignment / knapsack-with-coupling); even 2-tier with a latency constraint is a knapsack variant.
- The online component inherits caching lower bounds: any deterministic online algorithm is at least $k$-competitive, and any randomized at least $\Omega(\log k)$-competitive (Fiat et al.) — so no online tiering policy can beat these against an adaptive adversary on the cache tier.
- No fine-grained (SETH/3SUM) conditional lower bound is known for the coupled compaction+placement objective; the hardness established so far is classical NP-hardness + competitive-ratio impossibility.

## 6. The Gap

Status is **empirically-open**: systems demonstrate large real-world cost savings, but there is **no theory** giving (a) the optimal or provably near-optimal tiering as a function of the LSM access profile and cloud cost vector, nor (b) tight online competitive bounds for the *joint* migrate-and-compact problem under drift. The gap is between effective heuristics (Mutant, Nova-LSM) and any approximation guarantee or matching lower bound. Closing it needs a clean cost model + an LP-rounding or primal-dual approximation, plus competitive analysis of compaction-aware migration.

## 7. Current Research (as of June 2026)

- Disaggregated/serverless LSM compaction offloaded to elastic compute, billed separately from storage (Rockset/RocksDB-Cloud lineage; CMU, MIT DSAIL) *(frontier — verify)*.
- Learned/ML cost models predicting per-SSTable access to drive placement *(frontier — verify)*.
- SLO-aware autoscaling of the SSD cache tier in front of object storage; "compute-storage disaggregation" panels at VLDB/SIGMOD 2025.
- Integration with write-stall theory (shared compaction-bandwidth budget across tiers).

## 8. Future Work

- A provable approximation algorithm for SLO-constrained tier placement with a cloud cost objective.
- Competitive online tiering under distribution drift with compaction-aware migration cost.
- Co-optimizing Bloom-filter/cache memory (Monkey) with tier placement jointly.
- Workload-forecasting-driven prefetch/demotion between SSD and object storage.

## 9. Key References

- **[Foundational]** Athanassoulis, M., et al. *Designing Access Methods: The RUM Conjecture.* EDBT, 2016. — [DBLP](https://dblp.org/rec/conf/edbt/AthanassoulisKM16.html)
- **[SOTA]** Yoon, H., et al. *Mutant: Balancing Storage Cost and Latency in LSM-Tree Data Stores.* SoCC, 2018. — [DOI](https://doi.org/10.1145/3267809.3267846)
- **[SOTA]** Huang, H., Ghandeharizadeh, S. *Nova-LSM: A Distributed, Component-based LSM-Tree KV Store.* SIGMOD, 2021. — [arXiv](https://arxiv.org/abs/2104.01305)
- **[SOTA]** Lu, L., et al. *WiscKey: Separating Keys from Values in SSD-Conscious Storage.* FAST, 2016. — [USENIX](https://www.usenix.org/conference/fast16/technical-sessions/presentation/lu)
- **[SOTA]** Dayan, N., Athanassoulis, M., Idreos, S. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DBLP](https://researchr.org/publication/DayanAI17)
- **[Foundational]** Fiat, A., et al. *Competitive Paging Algorithms.* Journal of Algorithms, 1991. — [PDF](https://www.cs.cmu.edu/~sleator/papers/competitive-paging.pdf)

## 10. Worked Example

A 3-level LSM tree, fanout $T=10$, with two tiers: NVMe ($c_1=\$0.20$/GB-month, $\ell_1=0.1$ ms) and S3 ($c_2=\$0.02$/GB-month, $\ell_2=20$ ms per GET). Level sizes and access rates:

| Level | Size $S_i$ | Reads/s $r_i$ |
|-------|-----------|--------------|
| L0 | 1 GB | 900 |
| L1 | 10 GB | 90 |
| L2 | 100 GB | 10 |

Total 111 GB. **All-NVMe** storage cost: $111 \times 0.20 = \$22.2$/month. **All-S3**: $\$2.22$/month but L0 reads now pay $20$ ms each — $p99$ blows past a $\tau = 5$ ms SLO.

Monotone tiering: keep hot L0+L1 (11 GB) on NVMe, demote cold L2 (100 GB) to S3. Storage cost $= 11\times0.20 + 100\times0.02 = \$2.2 + \$2.0 = \$4.2$/month — an $81\%$ saving versus all-NVMe. Only $10$ reads/s hit S3 latency, and a Bloom filter keeps most of those from a real GET, so $p99$ on the hot path stays NVMe-fast. This greedy access-rate-density assignment captures most of the cost win, but lacks an approximation guarantee versus the optimal IP.

---
*Part of the [DBMS Research catalog](../../README.md).*
