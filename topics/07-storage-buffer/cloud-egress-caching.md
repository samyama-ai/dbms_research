---
id: 07-storage-buffer/cloud-egress-caching
title: "Cloud Storage Caching with Egress Cost"
topic: 07-storage-buffer
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-07
last_substantive_update: 2026-07
stale_since: ""
provenance: synthesized
---

# Cloud Storage Caching with Egress Cost

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/cloud-egress-caching` · **Status:** empirically-open

## 1. Problem Statement

A compute node caches objects/pages locally; misses fetch from cloud object storage (S3/GCS/Azure Blob), which **bills per GET request and per byte of egress/cross-zone transfer**, not just latency. Design admission and eviction to minimize **total dollar cost** = (request charges) + (egress charges) + (local-cache rent) + (miss-induced latency penalty), under a fixed local cache budget.

This differs from classic caching: the cost of a miss is **heterogeneous** (large objects cost more egress; cross-region fetches cost more than same-region; request count matters independently of bytes), and admission can be *selective* (fetch-but-don't-cache, or coalesce small reads into one ranged GET).

Variants:
- **Optimization:** minimize expected total billed cost given a price vector.
- **Decision:** can total cost be kept $\le \$C$ for the workload?
- **Online:** prices and access patterns known only as requests arrive; bound competitive ratio against the cost-optimal offline policy.
- **Request-coalescing:** group/batch fetches to amortize per-request fees (a covering subproblem).

## 2. Mathematical Foundations

**Weighted / file caching.** Objects have size $s_i$ and miss cost $c_i$ (here $c_i = \text{req fee} + s_i \cdot \text{egress rate} + \text{latency penalty}$). Minimizing total fetch cost under a size-$k$ cache is **generalized (file/weighted-size) caching** — the most general form, subsuming Bit (cost $=s_i$), Fault (cost $=1$), and Weighted ($s_i=1$) models.

**Competitive theory.** Generalized caching is **$O(\log k)$-competitive** randomized (Bansal–Buchbinder–Naor, via the primal-dual / online LP method) and $k$-competitive deterministic; the offline optimum is poly-time via min-cost flow / LP for the *cost* objective (Belady is *not* optimal for weighted sizes).

**Per-request fees and coalescing.** The fixed per-GET fee makes this an **online covering with setup costs** / **TCP-acknowledgment / rent-or-buy** flavored problem: batching defers fetches to amortize the request fee, trading latency for cost — analyzable via **ski-rental / online rent-or-buy** ($2$-competitive deterministic, $e/(e-1)$ randomized).

**Billing is non-metric.** Cross-region prices need not satisfy triangle inequality, so the cost space is a general (non-metric) weighted-caching instance; learning-augmented bounds (consistency/robustness) carry over from Lykouris–Vassilvitskii.

## 3. State of the Art (SOTA)

**Systems-SOTA.** Cloud-native engines cache aggressively: **Snowflake** and **Amazon Redshift Spectrum** cache S3 results on local SSD; **Databricks Delta Cache**, **Alluxio**, and **AWS S3 Express One Zone** target egress/latency. **Crystal / cache-cost-aware autoscaling** and FaaS data caches consider request fees. Academic: **cost-aware caching** for CDNs and cloud (e.g., greedy-dual-size-cost, GDSF) weights by miss cost/size — the practical workhorse. But evaluations are largely **empirical / workload-specific** with no dollar-optimality guarantee — hence *empirically-open*.

**Theory-SOTA.** Generalized caching $O(\log k)$-competitive (Bansal–Buchbinder–Naor 2012); learning-augmented caching (Lykouris–Vassilvitskii 2018; Antoniadis et al. 2020) for predicted reuse.

## 4. Upper Bound

- **Generalized (size+cost) caching:** $O(\log k)$ randomized, $k$ deterministic competitive (RAM/online model). The egress+request cost is exactly the per-object miss cost, so these bounds apply directly.
- **Offline cost-optimal:** poly-time via LP / min-cost flow.
- **Request-coalescing:** rent-or-buy / ski-rental gives $2$-competitive (det.), $e/(e-1)$ (rand.) for the batching subproblem.
- **GDSF / Greedy-Dual:** $k$-competitive and excellent empirically for cost-weighted miss minimization.

## 5. Lower Bound

- Any deterministic caching policy is $\ge k$-competitive; any randomized policy $\ge \Omega(\log k)$ (metrical-task-system / weighted-caching lower bounds — information-theoretic, online model).
- The **per-request-fee batching** subproblem inherits the ski-rental $2$ (det.) and $e/(e-1)$ (rand.) lower bounds.
- We are **not aware** of a lower bound that captures the *joint* request-fee + egress + coalescing structure tighter than the generic weighted-caching $\Omega(\log k)$ — establishing one is open.

## 6. The Gap

Marked **empirically-open**. Generic generalized-caching theory supplies tight-up-to-constants competitive bounds for the *miss-cost* objective, but the **full billing model** — per-request fees, cross-region tiers, coalescing, latency-vs-dollar trade-offs, and local-cache rent simultaneously — has **no validated algorithm with guarantees on real cloud price structures**, and no benchmark establishing how far deployed heuristics (GDSF, Delta Cache) sit from the cost optimum. The gap is less "unknown asymptotics" and more "no principled, evaluated policy for the actual cost function." Closing it needs (a) a unified online model with request fees + coalescing + tiered egress, (b) an algorithm with competitive or learning-augmented guarantees in that model, and (c) a billing-faithful empirical benchmark.

## 7. Current Research (as of June 2026)

- **Cost-aware caching for lakehouse query engines** (Databricks, Snowflake, Starburst) optimizing S3 request + transfer bills. *(frontier — verify)*
- **Learning-augmented caching with cost predictions** specialized to egress-billed misses. *(frontier — verify)*
- **Cross-cloud / multi-region** placement+caching to minimize inter-region egress (data-gravity economics). *(frontier — verify)*
- Serverless data caches that amortize per-invocation fetch fees via batching/coalescing.
- An **exact offline dollar-optimum** now supplies the billing-faithful reference §6/§8 call for: the uniform-object-size cost optimum is an integral interval LP (totally unimodular; equivalently a min-cost flow on the time line), with a *cost-FOO* bound for variable sizes. Measured against it, deployed heuristics show a **heterogeneity-regret law** (LRU dollar-regret grows with miss-cost CV, Spearman $0.87$; cost-aware GDSF cuts it), a **contention frontier** (GDSF residual regret collapses to $\approx0$ at budget $B=N_\text{exp}$), and a **crossover** $s^\star=\text{GET\_fee}/\text{egress\_rate}$ predicting when dollar-aware caching pays. On real Twitter-twemcache and Wikipedia-CDN traces the large-regret regime needs high heterogeneity, high reuse, *and* a tight budget simultaneously — which neither trace hits (an honest negative). GDSF, Bansal–Buchbinder–Naor, and FOO all credited (Samyama, arXiv:2606.20539) *(frontier — verify)*.

## 8. Future Work

- A competitive (or learning-augmented) algorithm for the *full* cost model: request fee + egress tier + rent + coalescing.
- A billing-faithful, public benchmark to quantify the gap between deployed heuristics and the dollar-optimal offline policy.
- Joint placement-and-caching across regions minimizing total egress under data-gravity constraints.
- Robustness to **price changes** (providers re-tier egress) as an adversarial/online-cost component.

## 9. Key References

- **[Foundational]** Bansal, Buchbinder, Naor. *Randomized Competitive Algorithms for Generalized Caching.* SIAM J. Computing, 2012. — [DOI](https://doi.org/10.1137/090779000)
- **[Foundational]** Cao, Irani. *Cost-Aware WWW Proxy Caching Algorithms (GreedyDual-Size).* USENIX Symp. Internet Tech., 1997. — [USENIX](https://www.usenix.org/conference/usits-97/cost-aware-www-proxy-caching-algorithms)
- **[SOTA]** Lykouris, Vassilvitskii. *Competitive Caching with Machine Learned Advice.* JACM, 2021 (orig. ICML 2018). — [DOI](https://doi.org/10.1145/3447579)
- **[SOTA]** Antoniadis, Coester, Eliáš, Polak, Simon. *Online Metric Algorithms with Untrusted Predictions.* ICML, 2020. — [arXiv](https://arxiv.org/abs/2003.02144)
- **[SOTA]** Dageville, Cruanes, Zukowski, et al. *The Snowflake Elastic Data Warehouse.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2903741)
- **[Survey]** Karlsson, Mahalingam. *Do We Need Replacement Algorithms? Cost-Aware Caching Surveys.* (cost-aware caching literature), 2000s. *(unverified)* — [DBLP search](https://dblp.org/search?q=cost-aware%20caching%20replacement)
- **[SOTA]** Samyama Research. *Caching for Dollars, Not Hits: An Exact Offline Reference for Cloud-Egress Caching and the Crossover That Decides When It Pays.* arXiv:2606.20539 (cs.DB), 2026. — [arXiv](https://arxiv.org/abs/2606.20539) · [code](https://github.com/samyama-ai/cloud-egress-cache)

## 10. Worked Example

Cache holds 1 object. Two objects compete, with S3-style pricing: GET fee $\$0.0004$ per 1000 requests $=\$4\times10^{-7}$/request, egress $\$0.09$/GB.

- Object $X$: size $1\,$KB, accessed 100 times. Miss cost $c_X = 4\times10^{-7} + (10^{-6}\,\text{GB})(\$0.09) = 4.9\times10^{-7}$.
- Object $Y$: size $1\,$GB, accessed 10 times. Miss cost $c_Y = 4\times10^{-7} + (1\,\text{GB})(\$0.09) = \$0.09000040$.

A hit-rate-maximizing policy (LRU/LFU) favors the *frequently* accessed $X$, saving $100\times c_X \approx \$4.9\times10^{-5}$. But GreedyDual-Size-Cost ranks by $\text{cost}/\text{size}$ or total cost saved: caching $Y$ for its 10 accesses saves $10\times c_Y \approx \$0.90$ — over **18,000$\times$ more dollars** despite fewer hits.

This is exactly why classic (Belady/LRU) hit-rate objectives are *wrong* under egress billing: the miss-cost vector $c_i$ is heterogeneous, the offline optimum is the min-cost-flow solution (not furthest-in-future), and generalized caching's $O(\log k)$ bound is the relevant guarantee.

---
*Part of the [DBMS Research catalog](../../README.md).*
