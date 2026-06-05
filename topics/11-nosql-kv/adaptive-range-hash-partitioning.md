# Adaptive Range vs Hash Partitioning

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/adaptive-range-hash-partitioning` · **Status:** open

## 1. Problem Statement

A distributed key-value/wide-column store must map a key to a shard. Two canonical strategies trade off:
- **Hash partitioning** spreads keys uniformly → excellent load balance and point-lookup distribution, but **destroys locality**: range scans must fan out to all shards.
- **Range partitioning** preserves key order → efficient range scans and prefix queries, but is **skew-prone**: hot key ranges and monotonic-insert hotspots overload single shards.

The problem: **automatically choose, and dynamically switch between, range and hash partitioning per region of the key-space**, driven by observed workload (point vs range query mix, insert pattern, access skew), so as to minimize a cost combining query latency, load imbalance, and re-partitioning (data-movement) cost.

Variants: **decision** (does a per-region partitioning policy exist achieving cost $\le C$?); **offline optimization** (known workload → optimal partition of the key-space into range-managed vs hash-managed segments with chosen granularity); **online** (workload drifts; minimize regret/competitive ratio against re-partitioning cost).

## 2. Mathematical Foundations

Model the key-space $K$ partitioned into contiguous regions $R_1,\dots,R_r$; each region gets a policy $\pi_i \in \{\text{range},\text{hash}\}$ and a shard count. Let the workload be a distribution over queries; a point query costs $1$ shard touch, a range query of selectivity $s$ costs $1$ shard under range (if it fits a region) but $\Theta(\text{shards})$ under hash. Load on shard $j$ is $\ell_j$; imbalance is $\max_j \ell_j / \overline{\ell}$.

The offline segmentation is a **1-D partitioning / dynamic-program** problem: choose breakpoints and per-segment policy to minimize $\sum_i \big(w_{\text{scan}}\cdot \text{scanCost}(\pi_i) + w_{\text{bal}}\cdot \text{imbalance}(\pi_i)\big) + w_{\text{move}}\cdot \text{repartitionCost}$. With additive segment costs this is solvable by DP in $O(r^2)$ over candidate breakpoints, but choosing breakpoints under skew and the online drift makes it hard.

Workload skew is captured by entropy/Zipf parameters; the **Lp-norm load** objective and **balls-into-bins** analysis bound hash imbalance ($\max$ load $\approx \overline{\ell} + \Theta(\sqrt{\overline{\ell}\log n})$). The online switching problem is **metrical / ski-rental-flavored**: re-partition (pay movement) vs. tolerate suboptimal cost — admitting $O(1)$-competitive thresholds in simple cases.

$$ \min_{\{R_i,\pi_i\}} \; \sum_i \text{Cost}(R_i,\pi_i \mid W) \; + \; \lambda \cdot \text{MovementCost}. $$

## 3. State of the Art (SOTA)

**Systems-SOTA:** Most stores fix one scheme — Cassandra/DynamoDB (hash), HBase/Bigtable/CockroachDB/TiKV/Spanner (range with auto-split/merge). Hybrid approaches exist: **YugabyteDB** lets the schema declare `HASH` or `ASC/DESC` (range) per column, and composite hash-then-range. CockroachDB and TiKV do automatic *range* split/merge and load-based rebalancing but do not switch a region to hashing. **Learned partitioning** (e.g., learned partition advisors, Flood/Tsunami multi-dimensional layouts by Nathan, Ding, Kraska et al., SIGMOD 2020/2021) optimize layout to a workload but assume a fixed family. No production system performs *automatic, per-region, online* switching between hash and range.

**Theory-SOTA:** the offline DP segmentation and online ski-rental framing are folklore-level; no published tight competitive algorithm for the joint problem.

## 4. Upper Bound

Offline, additive-cost segmentation admits an exact $O(r^2)$ (or $O(r\log r)$ with monotonicity) DP, or a $(1+\epsilon)$-approximation via coarsened breakpoints. Online, a threshold "re-partition once accumulated regret exceeds movement cost" yields a constant-competitive ratio for the *single-region* policy-switch (ski-rental: 2-competitive deterministic, $e/(e-1)$ randomized). Learned layout methods give strong empirical query-cost reductions but no worst-case guarantee.

## 5. Lower Bound

No NP-hardness is needed for the additive 1-D offline case (DP solves it). Hardness arises when (a) **breakpoint granularity** interacts with replication and multi-column keys → the multi-dimensional layout selection is NP-hard (reductions from partition/layout problems, akin to optimal indexing). Online, any deterministic switching policy is $\ge 2$-competitive against movement cost (ski-rental lower bound); under adversarial drift no constant-competitive policy can also guarantee balance. Communication/CAP-style impossibilities do not directly apply, but **no algorithm can simultaneously minimize scan cost and worst-case imbalance** (a RUM-like tension between locality and uniformity).

## 6. The Gap

The offline single-dimension case is essentially closed; the **online, multi-column, replication-aware, drift-adaptive** problem is genuinely open. Missing: (1) a principled online algorithm with a competitive ratio against re-partitioning cost *and* a balance guarantee; (2) a learned model that predicts when a region should flip policy with provable regret bounds; (3) any production validation of automatic switching.

## 7. Current Research (as of June 2026)

Active directions: learned and instance-optimized data layouts (Kraska/MIT DSAIL — Flood, Tsunami, and successors), workload-driven auto-partitioning advisors, and HTAP systems exposing hybrid hash+range keys. Self-driving DBMS efforts (Pavlo/CMU — NoisePage/OtterTune lineage) target automatic physical-design changes including partitioning *(frontier — verify)*. Emerging interest in *salting* hot range prefixes (a manual hash/range hybrid) suggests demand for automation. No consensus framework yet for per-region policy switching with guarantees.

## 8. Future Work

- An online algorithm with proven competitive ratio for per-region hash↔range switching under drift.
- Regret bounds for learned partitioning advisors.
- Joint optimization with replication, secondary indexes, and multi-column keys.
- Cost models that fold in re-partitioning network cost and SLO-violation penalties.

## 9. Key References

- **[Foundational]** Fay Chang, Jeffrey Dean, Sanjay Ghemawat, et al. *Bigtable: A Distributed Storage System for Structured Data.* OSDI 2006. — [USENIX](https://www.usenix.org/conference/osdi-06/bigtable-distributed-storage-system-structured-data)
- **[Foundational]** Giuseppe DeCandia et al. *Dynamo: Amazon's Highly Available Key-Value Store.* SOSP 2007. — [DOI](https://doi.org/10.1145/1294261.1294281)
- **[SOTA]** Vikram Nathan, Jialin Ding, Mohammad Alizadeh, Tim Kraska. *Learning Multi-Dimensional Indexes (Flood).* SIGMOD 2020. — [DOI](https://doi.org/10.1145/3318464.3380579)
- **[SOTA]** Jialin Ding, Vikram Nathan, Mohammad Alizadeh, Tim Kraska. *Tsunami: A Learned Multi-Dimensional Index for Correlated Data and Skewed Workloads.* VLDB 2020. — [arXiv](https://arxiv.org/abs/2006.13282)
- **[Survey]** Andrew Pavlo et al. *Self-Driving Database Management Systems.* CIDR 2017. — [PDF](https://db.cs.cmu.edu/papers/2017/p42-pavlo-cidr17.pdf)

## 10. Worked Example

Keys $1\dots 1000$ over $S = 4$ shards, workload = 60% point lookups + 40% range scans (each scan spans $\sim 100$ contiguous keys).

**Range partitioning** ($[1,250],[251,500],\dots$): a point query touches 1 shard; a 100-key scan usually fits within one region, touching 1 shard. Average shards/query $\approx 1.0$. But if inserts are monotonic (keys arriving in order), every new key lands on the *last* shard → load imbalance $\max_j \ell_j/\bar\ell \to 4$ (one shard does all writes).

**Hash partitioning**: point query still 1 shard; balls-into-bins keeps imbalance near $1 + \Theta(\sqrt{\log S / (\bar\ell)}) \approx 1.1$. But a 100-key range scan now fans out to all $\Theta(S)=4$ shards. Average shards/query $\approx 0.6(1) + 0.4(4) = 2.2$.

The adaptive answer: keep the cold, scan-heavy ranges **range**-partitioned (cost 1.0, good locality) but **hash** the monotonic-insert hot tail to break the write hotspot. With cost weights $w_{\text{scan}}=w_{\text{bal}}=1$, the hybrid beats either pure scheme — the per-region decision the problem formalizes.

---
*Part of the [DBMS Research catalog](../../README.md).*
