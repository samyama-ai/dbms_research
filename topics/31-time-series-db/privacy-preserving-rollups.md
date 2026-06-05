# Privacy-preserving release of rollups

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/privacy-preserving-rollups` · **Status:** open

## 1. Problem Statement
A TSDB downsamples raw events into **rollups** — per-interval counts, sums, averages, percentiles — and publishes them (dashboards, shared metrics, exported aggregates). Even aggregated, rollups can leak fine-grained events: a count that increments by one reveals a single user's action; sparse buckets expose presence; a sequence of running sums admits differencing attacks that reconstruct individual contributions.

Goal: release downsampled series so that an adversary cannot infer whether any individual event/record was present, while preserving aggregate utility (trends, totals, rates).

Variants: **decision** — does a release mechanism satisfy $(\epsilon,\delta)$-DP at the chosen granularity? **optimization** — minimize utility loss (e.g. expected squared error of published rollups) subject to a privacy budget; **continual-release / streaming** — publish a *running* aggregate over an unbounded stream under a fixed total budget. Privacy granularity must be specified: **event-level**, **user-level**, or **w-event** (any window of $w$ timesteps).

## 2. Mathematical Foundations
**Differential privacy** (Dwork–McSherry–Nissim–Smith, TCC 2006): mechanism $M$ is $(\epsilon,\delta)$-DP if for neighboring streams $D\sim D'$, $\Pr[M(D)\in S]\le e^{\epsilon}\Pr[M(D')\in S]+\delta$. For a count/sum rollup with per-event sensitivity $\Delta_1$, the **Laplace mechanism** adds $\mathrm{Lap}(\Delta_1/\epsilon)$; the **Gaussian mechanism** gives $(\epsilon,\delta)$-DP with noise $\sigma \propto \Delta_2\sqrt{2\ln(1.25/\delta)}/\epsilon$.

The streaming/continual-release crux is **composition**: naively perturbing each of $T$ rollups costs budget $\propto T$. The **binary-tree / continual-counting mechanism** (Dwork–Naor–Pitassi–Rothblum, STOC 2010; Chan–Shi–Song, 2011) releases a running sum over $T$ steps with error only $O\!\big(\tfrac{1}{\epsilon}\log^{1.5} T\big)$ — *polylogarithmic* in stream length, the foundational result for private time-series. **w-event privacy** (Kellaris et al., VLDB 2014) protects any window of $w$ timesteps for infinite streams via budget redistribution. Utility lower bounds come from the **fingerprinting/discrepancy** framework: error $\Omega(\sqrt{T})$ for $T$ adaptive linear queries without structure, and $\Omega(\log T)$ even for a single monotone running count.

## 3. State of the Art (SOTA)
**Theory-SOTA.** The binary-tree continual-counting mechanism (DNPR 2010 / CSS 2011) with the recent *(near-)optimal factorization* constants (Henzinger–Upadhyay–Upadhyay, SODA 2023; "smooth" / matrix-mechanism factorizations) gives the best known continual-release error, with matching $\Omega(\log T)$ lower bounds. The **matrix mechanism** (Li–Hay–Rastogi–Miklau–McGregor, PODS 2010) optimizes correlated linear-query (rollup) workloads. **w-event** and **PeGaSus** (Chen et al., SIGMOD 2017) handle infinite event streams.

**Systems-SOTA.** Google's **differential-privacy** library and **Plume**, Apple's local-DP telemetry, and Tumult Analytics provide DP aggregation primitives; OpenMined / OpenDP offer DP query engines. Production TSDBs (Prometheus, InfluxDB, Druid) ship **no** built-in DP — privacy is bolted on externally, and most "anonymized" dashboards rely on $k$-anonymity-style minimum-bucket thresholds, which are known-insufficient against differencing attacks.

## 4. Upper Bound
Continual release of a running count/sum over $T$ rollup steps: $(\epsilon,0)$-DP with mean-squared error $O\!\big(\tfrac{1}{\epsilon^2}\log^{3} T\big)$ (binary tree), improved constants via optimal factorization (Henzinger et al. 2023). Single batch of $m$ linear rollup queries: Gaussian/matrix mechanism error scaling with the workload's $\gamma_2$/factorization norm. w-event privacy over infinite streams: per-window error $O\!\big(\tfrac{w}{\epsilon}\big)$-class bounds via budget allocation. These hold in the central (trusted-curator) DP model; local-DP variants pay an extra $\sqrt{n}$ factor.

## 5. Lower Bound
Continual counting requires error $\Omega(\log T)$ for pure DP — *no* mechanism beats polylog (DNPR 2010; matching the upper bound up to the exponent). Releasing $m$ accurate linear aggregates over a database forces error $\Omega(\sqrt{m})$ via **fingerprinting codes** (Bun–Ullman–Vadhan, STOC 2014) and the **reconstruction/discrepancy** lower bounds (Dinur–Nissim, PODS 2003): too many accurate aggregates enable exact reconstruction of individual events, an information-theoretic impossibility. Local-DP incurs an additional $\Omega(\sqrt{n})$ accuracy penalty (Duchi–Jordan–Wainwright, FOCS 2013). These are unconditional (info-theoretic), not complexity-conditional.

## 6. The Gap
For the canonical **continual-counting** primitive the gap is essentially **closed** ($\Theta(\mathrm{polylog}\,T)$, with constants now near-tight). The problem is **open** at the *systems and modeling* level: (i) no TSDB natively enforces DP across its rollup/downsample pipeline; (ii) realistic rollups mix counts, sums, *percentiles*, and *rates* (high-sensitivity, reset-prone — see `counter-reset-handling`) whose joint private release lacks tight mechanisms; (iii) the right privacy granularity for telemetry (event vs. user vs. w-event) and budget management across multi-resolution tiers is unsettled; (iv) utility-vs-privacy for high-cardinality label spaces is poorly characterized. Closing it requires private rollup operators integrated with downsampling, with end-to-end budget accounting.

## 7. Current Research (as of June 2026)
Directions: near-optimal factorization mechanisms for continual release applied to streaming telemetry and to DP-SGD-style training on metrics *(frontier — verify)*; private quantile/percentile rollups and private histograms over streams; DP integrated into observability pipelines and federated/aggregated telemetry *(frontier — verify)*. Groups: Microsoft Research / IST Austria (Henzinger, Upadhyay) on optimal continual release; Google DP team (Thakurta, Kairouz); Miklau/McGregor (UMass) on the matrix mechanism and workload optimization; OpenDP/Tumult.

## 8. Future Work
- Native DP rollup operators (count/sum/quantile/rate) with composition-aware budgeting inside TSDBs.
- Tight mechanisms for percentile and counter-rate release under resets.
- Multi-resolution budget allocation across rollup tiers and retention levels.
- Utility characterization for high-cardinality, label-partitioned telemetry; local vs. central tradeoffs at the edge.

## 9. Key References
- **[Foundational]** Dwork, McSherry, Nissim, Smith. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC, 2006. — [DOI](https://doi.org/10.1007/11681878_14)
- **[Foundational]** Dwork, Naor, Pitassi, Rothblum. *Differential Privacy under Continual Observation.* STOC, 2010. — [DOI](https://doi.org/10.1145/1806689.1806787)
- **[Foundational]** Dinur, Nissim. *Revealing Information while Preserving Privacy.* PODS, 2003. — [DOI](https://doi.org/10.1145/773153.773173), [DBLP](https://dblp.org/rec/conf/pods/DinurN03.html)
- **[SOTA]** Henzinger, Upadhyay, Upadhyay. *Almost Tight Error Bounds on Differentially Private Continual Counting.* SODA, 2023. — [DOI](https://doi.org/10.1137/1.9781611977554.ch183)
- **[SOTA]** Kellaris, Papadopoulos, Xiao, Papadias. *Differentially Private Event Sequences over Infinite Streams (w-event).* VLDB, 2014. — [DOI](https://doi.org/10.14778/2732977.2732989), [DBLP](https://dblp.org/rec/journals/pvldb/KellarisPXP14.html)
- **[Foundational]** Li, Hay, Rastogi, Miklau, McGregor. *Optimizing Linear Counting Queries under Differential Privacy (The Matrix Mechanism).* PODS, 2010. — [DOI](https://doi.org/10.1145/1807085.1807104)
- **[Survey]** Dwork, Roth. *The Algorithmic Foundations of Differential Privacy.* Foundations and Trends in TCS, 2014. — [DOI](https://doi.org/10.1561/0400000042)

## 10. Worked Example

Publish a **running count** of logins over $T=8$ rollup buckets, true increments $c=(1,0,1,1,0,1,0,1)$, so the prefix sums are $S=(1,1,2,3,3,4,4,5)$. Each user contributes to one bucket, so per-step sensitivity is $\Delta=1$. Target $\epsilon=1$ pure DP.

**Naive per-step Laplace.** Add $\mathrm{Lap}(1/\epsilon)$ independently to each of the $T$ released prefix sums. But the prefixes overlap, so to keep the *whole sequence* $\epsilon$-DP you must split the budget: each release gets $\epsilon/T = 1/8$, hence noise scale $T/\epsilon = 8$ and per-prefix variance $2(T/\epsilon)^2 = 128$. Error grows **linearly** in $T$.

**Binary-tree mechanism.** Build a tree of partial sums over the 8 buckets: 8 leaves, 4 pair-nodes, 2 quad-nodes, 1 root — height $\log_2 8 = 3$. Each bucket participates in only $3$ tree nodes, so the budget splits just $3$ ways: noise scale $3/\epsilon = 3$ per node. Any prefix $S_k$ is reconstructed by summing at most $\log_2 T = 3$ noisy nodes, giving variance $\approx 3\cdot 2\cdot 3^2 = 54$, and asymptotically error $O\!\big(\tfrac{1}{\epsilon}\log^{1.5}T\big)$ — **polylogarithmic**, not linear.

For $S_7=4$ the released value might be $4 + \text{Lap}(3)\approx 4.6$. The matching lower bound says no mechanism beats $\Omega(\log T)$ error, so the tree is order-optimal — the gap is closed for this primitive.

---
*Part of the [DBMS Research catalog](../../README.md).*
