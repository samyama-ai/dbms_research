---
id: 31-time-series-db/workload-adaptive-layout
title: "Workload-adaptive physical layout"
topic: 31-time-series-db
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Workload-adaptive physical layout

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/workload-adaptive-layout` · **Status:** empirically-open
> **Verification note:** The STOC 2019 "Competitively Chasing Convex Bodies" author list was corrected to Bubeck, Lee, Li, Sellke (arXiv:1811.00887).

## 1. Problem Statement
A time-series store partitions data into *chunks* (time ranges) physically encoded as row groups, column segments, or sub-columnar tiles, and placed across a memory/SSD/object-store hierarchy. The **layout** $L$ assigns, per chunk, an encoding, a column-grouping, a sort/cluster order, and a storage tier. The workload is a stream of queries whose mix of **wide scans** (range aggregations, downsampling) versus **selective point/last-value lookups** drifts over time.

We want an *online* reorganization policy that, observing query stream $Q_1, Q_2, \dots$, chooses layouts $L_t$ to minimize cumulative cost (I/O bytes + decompression CPU + reorg amortization) without offline knowledge of future queries.

- **Decision variant:** does there exist a layout reachable within reorg budget $B$ achieving total cost $\le C$?
- **Optimization variant:** minimize expected steady-state query cost subject to a reorganization-write budget.
- **Online/competitive variant:** minimize competitive ratio against the offline optimum that knows the full query sequence.

## 2. Mathematical Foundations
Model layout selection per chunk as choosing $L_t \in \mathcal{L}$; query cost $c(q, L)$ is bytes scanned plus CPU. Switching cost $w(L, L')$ (rewrite bytes) makes this **Metrical Task Systems (MTS)** / **convex body chasing**: minimize $\sum_t c(q_t, L_t) + \sum_t w(L_{t-1}, L_t)$. For a metric on $|\mathcal{L}|=N$ states, the deterministic MTS competitive ratio is $2N-1$ and randomized is $\Theta(\log^2 N / \log\log N)$ (Bartal–Blum–Burch–Tomkins; Bubeck et al. for the polylog regime).

Choosing which columns to co-locate and which to materialize is a **submodular** coverage problem: benefit of caching/clustering a set $S$ of column-projections is monotone submodular, so greedy gives a $(1-1/e)$ approximation. Encoding choice interacts with access skew via entropy: the achievable scan cost is lower-bounded by per-column empirical entropy $H(X)$ under any prefix-free decodable layout. Tier placement is a constrained **knapsack/caching** instance (file size vs. access frequency vs. tier $/$GB), with online competitive bounds inherited from weighted caching ($k$-competitive deterministic, $O(\log k)$ randomized).

## 3. State of the Art (SOTA)
**Systems-SOTA.** Production TSDBs reorganize layout *heuristically*: InfluxDB IOx and TimescaleDB compress/recompress chunks on age triggers; Apache Druid/Pinot re-segment and roll up by retention policy; Gorilla/Prometheus TSDB use fixed delta-of-delta + XOR encodings with no query-driven re-layout. Self-driving DB work (Pavlo et al., *Peloton/NoisePage*, CIDR 2017) and **OtterTune** apply ML to knob/index tuning but not chunk-granular TSDB layout. Database cracking (Idreos–Kersten–Manegold, CIDR 2007) and adaptive merging are the closest *query-driven* reorganization primitives; **H2O** (Alagiannis et al., SIGMOD 2014) adapts row/column layout to workload. None target the scan-vs-last-value drift specific to telemetry.

**Theory-SOTA.** MTS/convex-body-chasing and online caching give the formal scaffolding but are not instantiated with TSDB cost models at scale.

## 4. Upper Bound
For the per-chunk tier/encoding selection cast as MTS over $N$ discrete layouts, randomized $O(\log^2 N/\log\log N)$-competitive, deterministic $O(N)$-competitive. For the caching/tiering sub-problem, randomized $O(\log k)$-competitive ($k$ = cache capacity in chunks). For static (workload-known) layout, greedy materialization is $(1-1/e)$-optimal under submodular benefit. These are model-clean but ignore reorg-write amplification; with rewrite cost $w$ folded in, only MTS-style bounds survive.

## 5. Lower Bound
Offline optimal layout selection with co-location constraints generalizes **weighted set cover / facility location**, hence NP-hard, with set-cover inapproximability $(1-o(1))\ln n$ (Dinur–Steurer, STOC 2014) for the materialization sub-problem. Online deterministic MTS has a matching $\Omega(N)$ lower bound; randomized caching has $\Omega(\log k)$. Thus even *offline* the static problem is hard to approximate below $\ln n$, and online no policy beats $\Omega(\log k)$ on tiering alone.

## 6. The Gap
The gap is **largely open and empirical**. MTS bounds depend on $N=|\mathcal{L}|$, which is astronomically large (encoding × ordering × grouping × tier per chunk), so worst-case competitive ratios are vacuous in practice; no TSDB-specific cost model closes the analytic gap. What would close it: (i) a structured cost metric exploiting that TSDB layouts form a *low-dimensional* parameter space (amenable to convex-body chasing with $O(\sqrt{d})$ or $O(d)$ competitive bounds), and (ii) a regret bound for the realistic *predictable-drift* setting rather than adversarial.

## 7. Current Research (as of June 2026)
Active directions: learned/RL chunk compaction and tier-eviction policies in IOx-style engines *(frontier — verify)*; instance-optimal and "self-organizing" stores extending cracking to columnar telemetry; learned cost models for object-store I/O. Groups: CMU DB (Pavlo), CWI/cracking lineage (Idreos now at Harvard), MIT (Madden, instance-optimality), and TSDB vendors (InfluxData, Timescale, Grafana/Mimir). Convex-body-chasing community (Bubeck, Sellke) provides the cleanest online primitives but has not been applied to storage layout *(frontier — verify)*.

## 8. Future Work
- A TSDB-specific competitive analysis exploiting low-dimensional, structured layout space.
- Joint optimization of encoding + tiering + rollup under a single online regret objective (links to `tsdb-cost-based-optimization`).
- Drift detectors that trigger reorganization with provable amortized-write guarantees.
- Benchmarks capturing realistic scan/last-value drift (TSBS extensions).

## 9. Key References
- **[Foundational]** Borodin, Linial, Saks. *An Optimal On-Line Algorithm for Metrical Task Systems.* JACM, 1992. — [DOI](https://doi.org/10.1145/146585.146588)
- **[Foundational]** Idreos, Kersten, Manegold. *Database Cracking.* CIDR, 2007. — [DBLP](https://dblp.uni-trier.de/pid/i/StratosIdreos.html)
- **[SOTA]** Alagiannis, Idreos, Ailamaki. *H2O: A Hands-free Adaptive Store.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2610502)
- **[SOTA]** Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [DBLP](https://dblp.uni-trier.de/rec/conf/cidr/PavloAALLMMMPQS17.html)
- **[SOTA]** Bubeck, Lee, Li, Sellke. *Competitively Chasing Convex Bodies.* STOC, 2019. — [arXiv](https://arxiv.org/abs/1811.00887)
- **[Survey]** Nemhauser, Wolsey, Fisher. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Math. Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)

## 10. Worked Example

Suppose a chunk can hold one of $N=2$ layouts: $L_A$ = sorted-by-time + heavy compression (great for **wide scans**, slow for point lookups) and $L_B$ = sorted-by-series-id + light compression (great for **last-value lookups**, costly to scan). Per-query costs:

$$c(\text{scan}, L_A)=1,\quad c(\text{scan}, L_B)=5,\quad c(\text{lookup}, L_A)=4,\quad c(\text{lookup}, L_B)=1.$$

Reorganizing between layouts costs $w(L_A,L_B)=w(L_B,L_A)=3$ (rewrite bytes). The query stream drifts: $\langle\text{scan},\text{scan},\text{lookup},\text{lookup},\text{lookup}\rangle$.

**Stay in $L_A$ the whole time:** $1+1+4+4+4=14$.
**Stay in $L_B$:** $5+5+1+1+1=13$.
**Switch $L_A\!\to\!L_B$ after query 2:** $\underbrace{1+1}_{L_A}+\underbrace{3}_{\text{reorg}}+\underbrace{1+1+1}_{L_B}=8$.

The switching policy wins (8 vs 13–14) by paying a one-time reorg of 3 to match the drift. This is exactly the **MTS** objective $\sum_t c(q_t,L_t)+\sum_t w(L_{t-1},L_t)$. An online policy that does not see the future must decide *when* to pay the 3; for $N$ states the deterministic competitive ratio is $2N-1$ (here $=3$), illustrating why large layout spaces $\mathcal{L}$ make worst-case bounds loose.

---
*Part of the [DBMS Research catalog](../../README.md).*
