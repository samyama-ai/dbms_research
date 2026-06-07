---
id: 30-cloud-serverless-db/remote-io-cost-model
title: "Disaggregated-storage I/O cost models"
topic: 30-cloud-serverless-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Disaggregated-storage I/O cost models

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/remote-io-cost-model` · **Status:** partially-solved

## 1. Problem Statement

In disaggregated (storage-compute-separated) databases — Aurora, Snowflake, BigQuery, lakehouses over S3/GCS — the query optimizer's classic disk cost model (sequential vs. random I/O on local spindles) is wrong. Remote object storage has **high, variable latency**, **massive request parallelism**, **per-request pricing** ($ per GET/PUT plus per-byte transfer), and benefits from **prefetching and caching tiers**. The problem: build an optimizer cost model that accurately predicts the *time and dollar* cost of a physical plan over remote storage, so plan selection (scan vs. index, join order, parallelism degree, prefetch aggressiveness) is correct.

Variants:
- **Optimization:** Given the cost model, choose the min-cost (or min-time-under-budget) plan — the standard optimizer search, but over a richer cost space.
- **Modeling/estimation:** Produce a cost function $C(\text{plan})$ that is *calibrated* and *monotone* enough for safe plan ranking.
- **Pareto:** Plans trade latency against dollar cost; produce the Pareto frontier rather than a single optimum.

## 2. Mathematical Foundations

Extend Selinger-style cost $C = c_{cpu}\cdot n_{cpu} + c_{io}\cdot n_{io}$ to a **multi-resource, queueing-aware** model. For a scan issuing $R$ remote requests of size $b$ over $p$ parallel in-flight slots against a service with per-request latency distribution $L$ (mean $\mu_L$, tail $L_{99}$) and bandwidth cap $B$:
$$ T_{\text{scan}} \approx \max\!\Big(\tfrac{R}{p}\,\mu_L,\ \tfrac{R\,b}{B}\Big) + L_{\text{startup}}, \qquad \$_{\text{scan}} = R\cdot p_{\text{req}} + R\,b\cdot p_{\text{byte}}. $$
The $\max$ captures the **latency-bound vs. bandwidth-bound** crossover; Little's law ($L = \lambda W$) governs how parallelism $p$ hides latency until bandwidth saturates. Prefetch effectiveness is a hit probability $h$ on a lookahead window, turning effective per-page latency into $h\cdot \mu_{\text{cache}} + (1-h)\mu_L$. Cardinality estimation (the AGM bound for joins, histogram-based selectivity) still feeds $R$; the new content is the **per-operator I/O-to-time** transfer function and the **dollar axis**.

Two objectives (time, $) make the optimizer a **multi-objective / constrained** search; under a budget it is a constrained shortest-plan problem, and the achievable set is a Pareto frontier.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** Snowflake and Redshift use cost models tuned for columnar scans over object storage with local SSD caches; **PrestoDB/Trino** and **Apache Spark (Photon, Velox)** model remote-scan cost with parallelism. **FoundationDB / Aurora** push log/page logic to storage. **AnyBlob / cloud-native scan** work (Durner et al., VLDB 2023) characterizes S3 throughput vs. request concurrency and informs cost models. BigQuery's planner accounts for shuffle and remote read.
- **Theory-SOTA.** Queueing-theoretic and roofline-style models of remote I/O; the **external-memory / I/O model** (Aggarwal–Vitter) and **parallel external memory (PEM)** give asymptotic grounding, but real pricing/latency tails are empirical.

## 4. Upper Bound

Given a calibrated cost model, optimizer search remains the classical complexity: dynamic-programming join ordering (Selinger/DPccp) is exponential in relations in the worst case but practical with pruning; the *cost evaluation* per plan is polynomial. With a convex, monotone time-vs-parallelism model, the optimal parallelism degree per operator has a closed form (the latency/bandwidth crossover). Pareto-frontier enumeration over the time/$ axes is polynomial in plan count when costs are monotone. Calibration error is bounded empirically to within tens of percent by recent S3-throughput studies, not provably.

## 5. Lower Bound

Join-order optimization (the search the cost model feeds) is **NP-hard** even for the simple linear cost in the number of relations (Ibaraki–Kameda; cross-product-free ordering). Cardinality estimation underlying $R$ has **no bounded-error guarantee** in general — adversarial data makes selectivity estimation arbitrarily wrong (an information-theoretic barrier without distributional assumptions). The I/O-model lower bounds (Aggarwal–Vitter sorting/permutation $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$) lower-bound the *I/O volume* any plan must pay, hence a floor on remote cost. There is no formal lower bound on *cost-model accuracy* — that is empirical.

## 6. The Gap

The **modeling** is partially solved: queueing/roofline models predict the latency-vs-bandwidth crossover and dollar cost reasonably, and S3-characterization papers calibrate them. The open gaps: (1) **tail-latency** and stochastic-variance modeling — current models use means and mispredict $p99$; (2) **prefetch effectiveness** $h$ is hard to predict a priori and depends on access pattern and cache state; (3) **joint time-and-dollar** optimization is rarely implemented — most optimizers still minimize a single scalar; (4) robustness of plan choice to cost-model error (the classic optimizer-robustness problem, now amplified by pricing). Closing it needs calibrated stochastic models with plan-robustness guarantees.

## 7. Current Research (as of June 2026)

Directions: learned cost models (Bao, learned optimizers from MIT DSAIL / Tim Kraska's group) retargeted to remote-storage features *(frontier — verify)*; empirical S3/object-store throughput characterization (TU Munich / Thomas Neumann, Durner et al.) feeding analytical models; budget-aware/cost-of-cloud optimizers in lakehouse engines (Databricks Photon, Velox) *(frontier — verify)*; multi-objective (time-vs-dollar) plan selection. The "FORWARD/Cloud cost" line and serverless-warehouse pricing transparency are active in industry.

## 8. Future Work

- Stochastic, tail-aware remote-I/O cost models with calibrated $p99$.
- Predictive prefetch-effectiveness models integrated into the optimizer.
- Plan robustness under cost-model and price uncertainty (distributionally robust optimization).
- First-class Pareto (time/dollar) plan enumeration and user-facing budget knobs.
- Unifying with tenant cache partitioning and tiering cost models.

## 9. Key References

- **[Foundational]** P. G. Selinger et al. *Access Path Selection in a Relational DBMS.* ACM SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[SOTA]** D. Durner, V. Leis, T. Neumann. *Exploiting Cloud Object Storage for High-Performance Analytics.* PVLDB, 2023. — [DOI](https://doi.org/10.14778/3611479.3611486)
- **[SOTA]** R. Marcus et al. *Bao: Making Learned Query Optimization Practical.* ACM SIGMOD, 2021. — [DBLP](https://dblp.org/rec/conf/sigmod/MarcusNMTAK21.html)
- **[Survey]** V. Leis et al. *How Good Are Query Optimizers, Really?* PVLDB, 2015. — [DBLP](https://dblp.org/rec/journals/pvldb/LeisGMBK015.html)

## 10. Worked Example

Scan a 16 GB columnar table from S3 as $R = 16{,}384$ GET requests of $b = 1$ MB each. Take per-request latency $\mu_L = 30$ ms, per-connection bandwidth such that the aggregate cap is $B = 4$ GB/s, GET price $p_{\text{req}} = \$0.0000004$, transfer $p_{\text{byte}} = 0$ (same-region). Apply the model with $p$ in-flight slots:

$$T_{\text{scan}} \approx \max\!\Big(\tfrac{R}{p}\mu_L,\ \tfrac{Rb}{B}\Big).$$

- Bandwidth floor: $\tfrac{Rb}{B} = \tfrac{16\text{ GB}}{4\text{ GB/s}} = 4.0$ s (independent of $p$).
- Latency term at $p=64$: $\tfrac{16384}{64}\times 0.03 = 256\times0.03 = 7.68$ s $\Rightarrow T \approx 7.68$ s (latency-bound).
- At $p=128$: $\tfrac{16384}{128}\times0.03 = 3.84$ s $<4.0$ s $\Rightarrow T \approx 4.0$ s (bandwidth-bound).

The crossover is $p^\* = \lceil R\mu_L B /(Rb)\rceil = \lceil \mu_L B/b\rceil = \lceil 0.03\times4000/1\rceil = 120$ slots; beyond it, more parallelism cannot help. Dollar cost is flat at $\$_{\text{scan}} = R\,p_{\text{req}} = 16384\times\$4\!\times\!10^{-7} \approx \$0.0066$, independent of $p$ — so the optimizer should pick $p=120$: minimal time at no extra dollar cost.

---
*Part of the [DBMS Research catalog](../../README.md).*
