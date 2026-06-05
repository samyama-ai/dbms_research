# Self-Driving Continuous Schema Tuning

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/self-driving-schema-tuning` · **Status:** empirically-open

## 1. Problem Statement
Continuously and autonomously adapt a database's **physical schema** (indexes, materialized views, partitions, layouts, sort orders) to a **drifting workload**, online, **without disruptive reorganizations**. Unlike one-shot advisors, a self-driving tuner must: forecast workload changes, decide *what* to build/drop and *when*, and **schedule** the physical changes so that reorganization cost and contention do not degrade live performance below SLOs.

- **Online optimization variant:** at each step choose a configuration to minimize cumulative (query cost + transition/reorganization cost), competing against the best offline sequence (a **metrical task system / MTS** with switching costs).
- **Control variant:** forecast + plan changes over a horizon; guarantee bounded disruption.
- The defining constraints are **switching/transition cost** and **non-disruption** (no long locks, no offline rebuilds).

## 2. Mathematical Foundations
This is online optimization **with switching costs**: minimize $\sum_t \big[\,\text{servicecost}(X_t, w_t) + d(X_{t-1}, X_t)\,\big]$, where $d$ is the (often metric) reorganization cost between configurations. This is precisely the **Metrical Task System (MTS)** / **convex body chasing / smoothed online learning** framework, where competitive ratios are the natural guarantee. For $N$ states, deterministic MTS has competitive ratio $\Theta(N)$ and randomized $\Theta(\log N / \log\log N)$-ish bounds — directly bounding how well any online tuner can track shifts.

Workload forecasting is a time-series prediction problem (the **QB5000 / Query2Vec** forecasting line). Deciding builds is the (NP-hard) selection problem from sibling pages, now wrapped in **regret** (vs. best dynamic configuration) and **competitive-ratio** analysis. Non-disruption ties to concurrency theory: online/incremental index build, MVCC-friendly schema change, and bounded-contention reorganization.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** CMU **NoisePage / Self-Driving DBMS** vision (Pavlo et al., CIDR 2017) and its **action-planning + forecasting** components (QB5000, Ma et al., SIGMOD 2018); **Peloton** self-driving prototype; cloud autonomous offerings — **Oracle Autonomous Database**, **Azure SQL Database automatic tuning** (auto create/drop index with automatic rollback on regression), **Amazon Aurora/Redshift** auto-tuning. Online/incremental index creation (e.g., PostgreSQL `CREATE INDEX CONCURRENTLY`) provides the low-disruption mechanisms.
- **Theory-SOTA:** Online algorithms with switching costs / MTS / online convex optimization give competitive and regret bounds applicable to the abstract tuning loop, though rarely instantiated with realistic DB cost models.

"Empirically-open": deployed self-tuners work well in practice but lack end-to-end guarantees on regret + disruption under arbitrary drift.

## 4. Upper Bound
Cast as MTS/OCO with switching costs, online algorithms achieve **competitive ratios** (e.g., $O(\log N)$-style randomized bounds for $N$ candidate configurations) and **sublinear dynamic regret** under bounded drift (path-length budget). Cloud systems achieve the practical "upper bound" via **safe auto-tuning with automatic rollback**: apply a change, monitor, revert on regression — empirically bounding disruption but without a closed-form competitive guarantee over the true combinatorial config space. The best *provable* bounds apply only after restricting to a small candidate set.

## 5. Lower Bound
Two compounding lower bounds: (1) the per-step selection problem is **NP-hard** (index/view selection), and (2) the online tracking problem inherits **MTS competitive-ratio lower bounds** — deterministic online algorithms with switching costs cannot beat $\Omega(N)$ competitiveness in general, and randomized lower bounds of order $\Omega(\log N/\log\log N)$ hold for general metrics. Under **adversarial** (unbounded) workload drift, no online tuner can guarantee bounded regret — an information-theoretic limit: future workload is not predictable from the past. Live, non-disruptive reorganization is further bounded by concurrency-control limits (you cannot reorganize hot data without some contention).

## 6. The Gap
The gap is **genuinely open**: between deployed self-driving systems that empirically track drift with rollback safety, and a theory delivering simultaneous guarantees on (a) low dynamic regret vs. the best configuration sequence, (b) bounded reorganization/switching cost, and (c) non-disruption SLOs — all under realistic, possibly adversarial drift. Closing it requires online algorithms instantiated with validated DB cost+transition models, drift-robust forecasting with confidence, and provably non-disruptive reorganization primitives.

## 7. Current Research (as of June 2026)
- Forecast-driven action planning with horizon optimization and switching-cost awareness (QB5000 lineage) *(frontier — verify)*.
- Safe continuous tuning with automatic regression detection + rollback as a first-class guarantee *(frontier — verify)*.
- Online convex optimization / MTS theory applied with realistic transition cost models *(frontier — verify)*.
- Low-disruption / incremental reorganization primitives (lock-free, MVCC-aware schema change) *(frontier — verify)*.
- Groups: Pavlo (CMU self-driving DB), cloud autonomous-DB teams (Oracle, Microsoft, AWS), Aboulnaga (Apple/Waterloo), Kraska (MIT).

## 8. Future Work
- End-to-end competitive/regret guarantees combining selection hardness + switching costs.
- Drift detection with confidence and bounded-disruption scheduling of changes.
- Provably non-disruptive online reorganization (indexes, partitions, layout).
- Robustness to adversarial / concept-drifting workloads with graceful degradation.

## 9. Key References
- **[Foundational]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [PDF](https://www.cidrdb.org/cidr2017/papers/p42-pavlo-cidr17.pdf), [DBLP](https://dblp.org/rec/conf/cidr/PavloAALLMMMPQS17.html)
- **[SOTA]** L. Ma, D. Van Aken, A. Hefny, G. Mezerhane, A. Pavlo, G. Gordon. *Query-based Workload Forecasting for Self-Driving Database Management Systems (QB5000).* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196908)
- **[Foundational]** A. Borodin, N. Linial, M. Saks. *An Optimal On-line Algorithm for Metrical Task Systems.* JACM, 1992. — [DOI](https://doi.org/10.1145/146585.146588)
- **[Foundational]** N. Bansal, N. Buchbinder, J. Naor. *A Primal-Dual Randomized Algorithm for Weighted Paging / Online Algorithms.* (online with switching costs lineage), FOCS/JACM, 2007–2012. — [DOI](https://doi.org/10.1145/2339123.2339126)
- **[SOTA]** S. Das et al. *Automatically Indexing Millions of Databases in Microsoft Azure SQL Database.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3314035)
- **[Survey]** P. Bernstein, et al. / G. Graefe. (autonomous & adaptive physical design surveys) — see also X. Zhou et al. *Database Meets AI: A Survey.* IEEE TKDE, 2022. — [DOI](https://doi.org/10.1109/TKDE.2020.2994641)

## 10. Worked Example

A tuner picks among $N=2$ index configurations: $X_A$ (index on column A) and $X_B$ (index on B). Building/dropping an index costs a switching penalty $d(X_A,X_B)=d(X_B,X_A)=10$. Per-query service cost: under $X_A$, an A-query costs 1 and a B-query costs 8; symmetrically under $X_B$.

Workload over 4 steps: $w = [A, B, B, B]$. Start in $X_A$.

**Greedy "rebuild every step" policy.** Step 1 ($A$): stay $X_A$, cost 1. Step 2 ($B$): switch to $X_B$, pay $10 + 1 = 11$. Steps 3,4 ($B$): stay, $1+1$. Total $= 1+11+1+1 = 14$.

**Hysteretic policy** (only switch when accumulated regret exceeds the switching cost). Step 1: $X_A$, cost 1. Steps 2-3 ($B,B$) staying in $X_A$: pay $8+8=16$ in service. By step 3 the gap $16 > 10$ justifies a switch; switching at step 2 was the better call. The **offline optimum** here switches once at step 2: $1 + (10+1) + 1 + 1 = 14$.

This is exactly the MTS objective $\sum_t [\text{service}(X_t,w_t) + d(X_{t-1},X_t)]$. With $N=2$ the deterministic competitive ratio is $2N-1 = 3$: no online tuner, ignorant of the future $B$-heavy run, can guarantee better than $3\times$ the offline cost on an adversarial workload.

---
*Part of the [DBMS Research catalog](../../README.md).*
