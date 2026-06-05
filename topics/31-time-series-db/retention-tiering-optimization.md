# Retention and tiering as an optimization problem

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/retention-tiering-optimization` · **Status:** open

## 1. Problem Statement
A TSDB must continuously decide, for every chunk/series at every resolution, one of: *keep raw on hot storage*, *downsample to a coarser rollup and drop raw*, *migrate to a colder/cheaper tier* (SSD → object store → archive), or *evict entirely*. The **retention–tiering problem** asks for a policy that minimizes total cost (storage \$ + retrieval/egress \$ + query latency penalty) subject to (a) per-query **accuracy constraints** (e.g., percentile error $\le \varepsilon$ on a class of queries), (b) hard **legal/SLA retention** floors, and (c) a global **budget** $B$.

Variants: **Decision** — does a tiering assignment meeting all accuracy and retention constraints cost $\le B$? **Optimization** — minimize expected cost over a query distribution. **Online** — make irreversible (downsample/evict) decisions as data ages without knowing future queries. The irreversibility of lossy downsampling and eviction is what makes this distinct from ordinary cache/tier management.

## 2. Mathematical Foundations
Each chunk $i$ has size $s_i$, age, and a menu of *representations* $r \in R_i$ (raw, 1-min rollup, 1-hour rollup, sketch, evicted), each with storage cost $c_{i,r}$, residual error $e_{i,r}$ for queries touching it, and a tier placement with access cost $a_{i,r}$. Let query class $q$ arrive with weight $w_q$ and demand accuracy $\varepsilon_q$. We seek an assignment $x_{i,r}\in\{0,1\}$, $\sum_r x_{i,r}=1$, minimizing
$$ \sum_{i,r} x_{i,r}\,(c_{i,r} + \textstyle\sum_q w_q\,a_{i,r}\,\mathbf{1}[q \text{ reads } i]) \quad \text{s.t. } \forall q:\ \mathrm{err}_q(x) \le \varepsilon_q,\ \ \text{retention floors},\ \ \text{budget}. $$
This is a **multiple-choice / multidimensional knapsack** (NP-hard) when constraints are budget-shaped, and a **facility-location / caching** problem when access locality dominates. If error is **submodular/decomposable** across chunks (coverage-like), the constrained selection admits a $(1-1/e)$ greedy via submodular maximization (Nemhauser–Wolsey–Fisher 1978). The online variant maps to **ski-rental / online caching with eviction** and to **competitive paging** (Sleator–Tarjan), with the twist that downsampling is a *partial, irreversible* eviction.

## 3. State of the Art (SOTA)
**Systems-SOTA:** retention is configured by hand — Prometheus/Thanos/Cortex use fixed retention + downsample-at-fixed-resolutions (5m, 1h); InfluxDB retention policies + continuous queries; TimescaleDB *continuous aggregates* + *data-tiering* to object storage; M3DB/VictoriaMetrics multi-resolution retention. All use **static rule tables**, not constrained optimization. Cloud TSDBs (Amazon Timestream, Azure Data Explorer/Kusto) expose hot/warm tier policies with automatic age-based migration but no accuracy-constrained objective. **Theory-SOTA:** the closest formal results are in *materialized-view selection* (Harinarayan–Rajaraman–Ullman, SIGMOD 1996, greedy with bound) and *cache replacement competitive analysis* — neither models irreversible lossy downsampling with per-query error budgets.

## 4. Upper Bound
For the **offline** constrained-selection problem with submodular, decomposable error coverage and a single budget: a greedy algorithm gives a $(1-1/e)$-approximation (monotone submodular maximization under a knapsack constraint, with the standard partial-enumeration refinement) in the RAM model. With a fixed constant number of tiers and an FPTAS-amenable knapsack structure, $(1+\epsilon)$ is achievable per chunk but the *coupled* multi-query version retains the $(1-1/e)$ barrier. **Online:** age-based migration with ski-rental thresholds is $2$-competitive for the *migration-only* (lossless tiering) sub-problem.

## 5. Lower Bound
The general assignment is **NP-hard** (reduction from multidimensional knapsack / partition). Under submodular coverage, $(1-1/e)$ is **tight** unless P=NP (Feige 1998, max-coverage hardness). The online lossy-downsample variant inherits the $\Omega(\log k)$ competitive lower bound of online caching/paging when irreversible decisions can be adversarially punished by future queries; with *irreversible eviction under unknown future queries*, no deterministic policy is $o(\log k)$-competitive. Accuracy-constrained feasibility itself can be NP-hard when error terms interact non-additively across overlapping rollups.

## 6. The Gap
For the offline submodular case the gap is **closed** at $(1-1/e)$. The open frontier is the **online, irreversible, accuracy-constrained** problem: there is no tight competitive ratio, and no algorithm that provably trades query-accuracy for cost as future queries are revealed. Closing it needs either a competitive online policy with matching lower bound, or a learning-augmented (predictions) analysis showing graceful degradation between optimistic and robust regimes.

## 7. Current Research (as of June 2026)
Threads: **learning-augmented online algorithms** (Lykouris–Vassilvitskii style) applied to tiering, using query-frequency predictors with worst-case fallback *(frontier — verify)*; accuracy-aware downsampling where rollups carry error sketches so downstream error is composable (Timescale/VictoriaMetrics engineering); and DP/RL retention planners in commercial observability platforms (Datadog, Grafana) that have not published guarantees *(frontier — verify)*. Connections to differentially-private release of coarse rollups (see `privacy-preserving-rollups.md`) are emerging.

## 8. Future Work
- A unified cost model coupling storage \$, egress \$, latency penalty, and per-query error into a single constrained optimization with proven approximation.
- Competitive / learning-augmented analysis of irreversible downsample+evict under unknown queries.
- Error-composability theory: bounding end-to-end query error from per-chunk residual errors across mixed resolutions and sketches.
- Joint optimization with chunking (`time-chunking-policy.md`) and rollup materialization (`rollup-materialization-optimal.md`).

## 9. Key References
- **[Foundational]** V. Harinarayan, A. Rajaraman, J. D. Ullman. *Implementing Data Cubes Efficiently.* SIGMOD, 1996.
- **[Foundational]** G. L. Nemhauser, L. A. Wolsey, M. L. Fisher. *An analysis of approximations for maximizing submodular set functions—I.* Mathematical Programming, 1978.
- **[Foundational]** D. Sleator, R. E. Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985.
- **[SOTA]** T. Lykouris, S. Vassilvitskii. *Competitive Caching with Machine Learned Advice.* JACM / ICML, 2018/2021.
- **[SOTA]** Timescale. *Continuous Aggregates and Tiered Storage.* (system documentation/engineering), 2021–.
- **[Survey]** U. Feige. *A Threshold of ln n for Approximating Set Cover.* JACM, 1998.

---
*Part of the [DBMS Research catalog](../../README.md).*
