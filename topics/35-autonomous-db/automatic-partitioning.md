---
id: 35-autonomous-db/automatic-partitioning
title: "Automatic Partitioning & Co-Partitioning"
topic: 35-autonomous-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Automatic Partitioning & Co-Partitioning

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/automatic-partitioning` · **Status:** open

## 1. Problem Statement
For a distributed/parallel DBMS over $N$ nodes, automatically choose:
- **horizontal partitioning** (which attribute(s) and scheme — hash/range/list — partition each table),
- **vertical partitioning** (column grouping),
- **co-partitioning** (aligning partition keys across tables so joins are local), and
- **replica layout** (which partitions to replicate, and where),

to **minimize distributed query cost** — dominated by network shuffle / repartition cost — while keeping **load skew** bounded and respecting storage/replication budgets.

Variants:
- **Decision:** Is there a layout with communication cost $\le t$ and max-load $\le L$?
- **Optimization:** Min (shuffle + scan) cost subject to skew/space budgets.
- **Counting:** Enumerate distinct co-partition-compatible schemes.
- **Online/repartitioning:** Adapt layout under workload/data drift with migration cost (links *online-index-selection-regret*).

## 2. Mathematical Foundations
Two coupled cores:

**(a) Communication minimization.** Model the workload as a hypergraph $H=(V,E)$: tuples/records are vertices, each query/join is a hyperedge over the data it co-accesses. Partitioning into $N$ balanced parts minimizing cut hyperedges is **balanced $k$-way hypergraph partitioning** — exactly the Schism (Curino et al.) formulation. Co-partitioning adds *alignment* constraints between tables' key domains.

**(b) Skew / load balance.** Partition sizes/load must satisfy $\max_p \mathrm{load}(p) \le (1+\epsilon)\frac{1}{N}\sum_p \mathrm{load}(p)$ — a **bin-packing / scheduling** constraint; data and request skew (heavy hitters) make perfect balance impossible, invoking **makespan minimization** lower bounds.

Relevant theory:
- **Balanced graph/hypergraph partition:** NP-hard; best approximations $O(\sqrt{\log n \cdot \log k})$ (Krauthgamer–Naor–Schwartz) for balanced cut.
- **Communication-cost models** for joins: the **AGM bound** and the **MPC (Massively Parallel Communication) model** (Beame–Koutris–Suciu) give *load* lower bounds $\Omega(\,|R|/N^{1/\tau^\*}\,)$ for one-round join computation, where $\tau^\*$ is the fractional edge cover number — connecting partitioning quality to worst-case optimal join theory.
- **Skew:** MPC results show skewed values force higher load or more rounds; HyperCube/Shares partitioning is load-optimal for skew-free instances.

## 3. State of the Art (SOTA)
**Theory-SOTA:** The **MPC model** characterizes per-round communication load for join queries (tight for many query shapes), and balanced hypergraph-partition approximations bound replication-free layouts. These give *lower bounds and idealized schemes*, not a full physical layout selector with guarantees.

**Systems-SOTA:** **Schism** (Curino–Jones–Zhang–Madden, VLDB 2010) — workload-graph min-cut partitioning; **SWORD**, **AdaptDB**, **Clay** (skew-aware repartitioning), and cloud-DW automatic clustering / distribution-key advisors. Modern MPP engines (Redshift, Snowflake micro-partitions, Spark/AQE) auto-tune distribution and handle skew at runtime heuristically; learned partition advisors are emerging. *(frontier — verify)*

## 4. Upper Bound
- **Balanced partition core:** $O(\sqrt{\log n \log k})$-approximation for minimum balanced cut (KNS); hypergraph variants via multilevel heuristics (hMETIS/KaHyPar) with no worst-case ratio but strong practice.
- **Join load (MPC):** HyperCube/Shares is **load-optimal** ($O(|\mathrm{IN}|/N^{1/\tau^\*})$) for skew-free single-round computation; optimal layout for a *single* join query is achievable.
- **Full workload layout:** only heuristic (Schism-style min-cut + lookup-table compression). No poly-time constant-factor guarantee for joint horizontal+vertical+replica selection over a workload.

## 5. Lower Bound
- **NP-hard:** balanced (hyper)graph partitioning, and vertical partitioning (reduces from graph partitioning / set problems) are NP-hard; co-partitioning compounds this.
- **MPC communication lower bound:** $\Omega(|\mathrm{IN}|/N^{1/\tau^\*})$ per-node load for one-round join, and stronger bounds under data skew — an *information/communication-complexity* impossibility independent of layout cleverness.
- **Skew:** makespan / bin-packing hardness implies no layout avoids $\Omega(\text{heavy-hitter weight})$ max-load; perfect balance is NP-hard to even approximate below the largest-item bound.

## 6. The Gap
**Genuinely open.** Tight bounds exist for *single-query* communication (MPC) and for the *isolated* balanced-partition core, but not for the **joint, workload-level** problem combining horizontal + vertical + co-partition + replication under simultaneous communication *and* skew budgets. The gap is between idealized per-query optimality and heuristic full-layout selectors. Closing it requires a multi-objective approximation unifying MPC load bounds with balanced-partition guarantees over a query mix.

## 7. Current Research (as of June 2026)
- **Skew-aware, online repartitioning** with migration-cost-bounded adaptation (Clay lineage; learned/RL layout agents). *(frontier — verify)*
- Bridging **worst-case-optimal join** theory and physical layout: choosing partitions to realize MPC-optimal loads for whole workloads. *(frontier — verify)*
- Groups: UW (Suciu, Koutris — MPC theory), MIT (Madden — Schism/AdaptDB), CMU, HPI; cloud-DW teams on automatic clustering. *(frontier — verify)*

## 8. Future Work
- A joint approximation for workload layout under combined communication + skew + replication budgets.
- Multi-round vs. single-round tradeoffs in layout choice (MPC rounds vs. replication).
- Online co-partitioning with regret and bounded migration.
- Layout co-design with indexes/MVs (feeds *joint-physical-design*).

## 9. Key References
- **[Foundational]** C. Curino, E. Jones, Y. Zhang, S. Madden. *Schism: A Workload-Driven Approach to Database Replication and Partitioning.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920853)
- **[Foundational]** P. Beame, P. Koutris, D. Suciu. *Communication Steps for Parallel Query Processing (the MPC model).* PODS, 2013 / JACM, 2017. — [DOI](https://doi.org/10.1145/3125644)
- **[Foundational]** F. N. Afrati, J. D. Ullman. *Optimizing Joins in a Map-Reduce Environment (Shares/HyperCube).* EDBT, 2010. — [DOI](https://doi.org/10.1145/1739041.1739056)
- **[SOTA]** M. Serafini, et al. *Clay: Fine-Grained Adaptive Partitioning for General Database Schemas.* VLDB, 2016. — [DOI](https://doi.org/10.14778/3025111.3025125)
- **[SOTA]** R. Krauthgamer, J. Naor, R. Schwartz. *Partitioning Graphs into Balanced Components.* SODA, 2009. — [DOI](https://doi.org/10.1137/1.9781611973068.102)
- **[Survey]** H. Ngo, C. Ré, A. Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013. — [DOI](https://doi.org/10.1145/2590989.2590991)

## 10. Worked Example

**MPC load for a co-partitioned join.** Consider the triangle query $R(a,b)\bowtie S(b,c)\bowtie T(c,a)$ run on $N$ servers in one round, with each relation of size $|\mathrm{IN}|=M$ tuples. The hypergraph has three edges over three variables; its fractional edge-cover number is $\tau^*=3/2$ (put weight $1/2$ on each edge). The MPC one-round load lower bound (§5) is
$$L \;=\; \Omega\!\left(\frac{M}{N^{1/\tau^*}}\right) \;=\; \Omega\!\left(\frac{M}{N^{2/3}}\right).$$

The HyperCube/Shares scheme matches it: arrange the $N$ servers as a $p\times p\times p$ cube with $p=N^{1/3}$, hashing each variable $a,b,c$ into $p$ buckets. Tuple $R(a,b)$ is sent to every server whose $(a\text{-coord},b\text{-coord})$ matches — i.e. $p$ servers (one per $c$-bucket), so each tuple replicates $p=N^{1/3}$ times. Total bytes moved $= 3 M N^{1/3}$, giving per-server load $\approx 3MN^{1/3}/N = 3M/N^{2/3}$, meeting the bound.

**Why skew breaks it.** If one value $b_0$ appears in $M/2$ tuples of both $R$ and $S$, the $b$-slice $b_0$ alone routes to only $p^2=N^{2/3}$ servers, each receiving $\Omega(M/N^{2/3})$ heavy-hitter tuples — and the makespan/bin-packing floor (§5) means no co-partition layout removes that hot slice without extra replication or a second round. This is precisely the joint communication-plus-skew obstruction of §6.

---
*Part of the [DBMS Research catalog](../../README.md).*
