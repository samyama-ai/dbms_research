---
id: 35-autonomous-db/observability-granularity
title: "Observability & Workload Modeling Granularity"
topic: 35-autonomous-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Observability & Workload Modeling Granularity

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/observability-granularity` · **Status:** open

## 1. Problem Statement
A self-driving controller can only act on what it measures. The **observability-granularity problem**: determine *what* signals (query text/plans, per-operator counters, lock/latch waits, buffer hit rates, arrival times) and at *what granularity* (per-query, per-template, per-table, per-time-bucket) and *what sampling rate* must be collected so the controller acts correctly—i.e., the state representation is a *sufficient statistic* for good decisions—while keeping monitoring overhead bounded.

Variants:
- **Optimization:** minimize monitoring cost subject to a bound on decision regret induced by partial observability.
- **Decision:** does a given instrumentation set make the control MDP $\epsilon$-observable (a near-sufficient statistic)?
- **Counting / sketch sizing:** what is the minimum sketch size to answer the controller's queries (heavy hitters, distinct counts, quantiles) to accuracy $\epsilon$?

## 2. Mathematical Foundations
Under full state $s_t$ the controller solves an MDP; with instrumentation $o_t=\mathcal{O}(s_t)$ it solves a **POMDP**. A representation is *decision-sufficient* if the optimal policy under $o$ matches that under $s$ — formally a **bisimulation / sufficient-statistic** condition: $\mathbb{E}[\,\text{future reward}\mid o]$ is invariant to within-$o$ state differences. The control-relevant loss from coarsening is bounded by the bisimulation discrepancy.

Granularity trades information against overhead. Workload-summary primitives are streaming sketches with proven space–accuracy laws:
- **Heavy hitters / hot queries:** Count-Min sketch answers point queries with error $\epsilon\lVert f\rVert_1$ using $O(\tfrac1\epsilon\log\tfrac1\delta)$ space (Cormode–Muthukrishnan).
- **Distinct values (table/column cardinalities):** HyperLogLog estimates with relative error $\approx 1.04/\sqrt{m}$ using $m$ registers (Flajolet et al.).
- **Quantiles (latency SLOs):** KLL/$t$-digest sketches give $\epsilon$-approximate quantiles in $O(\tfrac1\epsilon\log\log\tfrac1\delta)$ space (Karnin–Lang–Liberty).

The sampling-rate question is an estimation problem: estimating an arrival rate or a selectivity to relative error $\epsilon$ needs $\Theta(1/\epsilon^2)$ samples (concentration), setting a floor on telemetry volume. The *value of information* of an extra signal is $V^\*_{\text{with}}-V^\*_{\text{without}}$, weighable against its overhead.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** QB5000 forecaster (Ma et al., SIGMOD 2018) chooses *query-template* granularity as its workload model—an explicit granularity decision. DBSeer (Mozafari et al., SIGMOD 2013) models resource use from coarse signals. Always-on profilers (pg_stat_statements, eBPF/USDT probes, Microsoft Query Store, Snowflake query history) define what's cheaply observable in production. Sampling-based always-on profiling (e.g., low-overhead statistical profilers) bound CPU overhead to single-digit percent.
- **Theory-SOTA:** Streaming sketches (Count-Min, HLL, KLL) and POMDP/bisimulation state-abstraction theory (Li, Walsh, Littman 2006) underpin granularity choices.

## 4. Upper Bound
Each summary the controller needs has a sublinear sketch: heavy hitters in $O(\epsilon^{-1}\log\tfrac1\delta)$, distinct counts in $O(\epsilon^{-2})$ registers, quantiles in $O(\epsilon^{-1}\log\log\tfrac1\delta)$ space, all with rigorous guarantees and constant per-update time—so the *measurement* side has near-optimal upper bounds. On the control side, state abstraction that preserves an $\epsilon$-bisimulation yields value loss $\le \tfrac{\epsilon}{(1-\gamma)^2}$, giving a principled coarsening with bounded decision regret.

## 5. Lower Bound
Sketch sizes are tight: distinct-count estimation to relative error $\epsilon$ requires $\Omega(\epsilon^{-2}+\log n)$ bits (Kane–Nelson–Woodruff); $\ell_1$ heavy hitters require $\Omega(\epsilon^{-1}\log\tfrac1\epsilon)$; quantile summaries have matching $\Omega(\epsilon^{-1})$ lower bounds — proven via communication complexity / cell-probe arguments. On the decision side, partial observability is fundamental: solving general POMDPs optimally is PSPACE-hard (Papadimitriou–Tsitsiklis), and there exist workloads where *any* sub-sufficient instrumentation forces $\Omega(1)$ decision regret (info-theoretic indistinguishability of states with different optimal actions).

## 6. The Gap
The measurement-side bounds are essentially closed (tight sketches). The *open* gap is on the control side: we lack a constructive theory that, given a tuning objective, outputs the **minimal sufficient instrumentation set and granularity** with a certified decision-regret bound—today this is chosen by engineering judgment. Bridging streaming lower bounds to POMDP value-of-information for DB control, and doing it adaptively as workloads shift, is unresolved. The problem is open.

## 7. Current Research (as of June 2026)
- eBPF-based always-on, low-overhead DB observability feeding controllers *(frontier — verify)*.
- Value-of-information-driven adaptive instrumentation that turns telemetry up/down per controller need *(frontier — verify)*.
- Learned compact workload representations (template embeddings) replacing hand-chosen granularity.
- Groups: CMU NoisePage line, the streaming-algorithms community (Cormode, Nelson, Woodruff), and observability/eBPF practitioners crossing into DB autonomy.

## 8. Future Work
- A constructive "minimal sufficient instrumentation" synthesizer with regret certificates per objective.
- Joint optimization of sketch budget and control regret under an overhead cap.
- Adaptive granularity that responds to drift and rare-event coverage.
- Privacy/multi-tenant-aware telemetry with bounded leakage.

## 9. Key References
- **[Foundational]** G. Cormode, S. Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch and its Applications.* Journal of Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Foundational]** P. Flajolet, É. Fusy, O. Gandouet, F. Meunier. *HyperLogLog: The Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA, 2007. — [HAL](https://hal.science/hal-00406166v1)
- **[Foundational]** D. Kane, J. Nelson, D. Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS, 2010. — [DOI](https://doi.org/10.1145/1807085.1807094)
- **[SOTA]** Z. Karnin, K. Lang, E. Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** L. Ma et al. *Query-based Workload Forecasting for Self-Driving Database Management Systems.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196908)
- **[Foundational]** C. Papadimitriou, J. Tsitsiklis. *The Complexity of Markov Decision Processes.* Mathematics of Operations Research, 1987. — [DOI](https://doi.org/10.1287/moor.12.3.441)

## 10. Worked Example

**Sizing a Count-Min sketch for hot-query detection.** A controller wants to spot heavy-hitter query templates to decide what to index. Telemetry stream has $\lVert f\rVert_1 = 10^{7}$ executions over the window. We want point-frequency estimates with additive error $\le \epsilon\lVert f\rVert_1 = 10^{4}$ (so error $\epsilon = 10^{-3}$) and failure probability $\delta = 0.01$.

Count-Min uses a $d \times w$ counter table with
$$w = \Big\lceil \tfrac{e}{\epsilon} \Big\rceil = \lceil 2.718\times 10^{3}\rceil = 2719, \qquad d = \Big\lceil \ln\tfrac1\delta \Big\rceil = \lceil \ln 100 \rceil = \lceil 4.605\rceil = 5.$$

Total counters $= d\cdot w = 5 \times 2719 = 13{,}595$. At 8 bytes each that is $\approx 109$ KB — independent of the $10^7$ executions or the number of distinct templates. Each update touches $d=5$ cells: $O(1)$ time.

A template run $4\times10^4$ times is reported with count in $[4\times10^4,\ 5\times10^4]$ with probability $\ge 0.99$ — comfortably above the $10^4$ noise floor, so it is reliably flagged "hot." This is the §4 upper bound $O(\epsilon^{-1}\log\tfrac1\delta)$ instantiated; the §5 lower bound says no summary beats this asymptotically.

---
*Part of the [DBMS Research catalog](../../README.md).*
