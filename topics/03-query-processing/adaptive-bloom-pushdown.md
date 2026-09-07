---
id: 03-query-processing/adaptive-bloom-pushdown
title: "Optimal learned/adaptive Bloom-filter pushdown"
topic: 03-query-processing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Optimal learned/adaptive Bloom-filter pushdown

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/adaptive-bloom-pushdown` · **Status:** empirically-open

## 1. Problem Statement

Runtime (Bloom/semijoin/min-max) filters built on a join's build side and **pushed down** to the probe side — or all the way to the storage scan — can prune enormous amounts of work, but they are not free: building costs CPU and memory, probing costs per-tuple lookups, and an *ineffective* filter (low selectivity, or built on a key that doesn't prune) is pure overhead. The problem: *decide, adaptively and ideally with learning, **whether** to build a runtime filter, **how large** (bits/key, false-positive rate) to make it, and **how far** to push it (probe operator vs. scan vs. storage I/O), so as to maximize (pruned work) − (build + probe + memory overhead).*

Variants: (a) **decision** — is filter $F$ net-positive for this query/edge?; (b) **sizing** — optimal $m$ (and $k$) trading false-positive rate against memory/probe cost and downstream savings; (c) **placement/push depth** — operator, scan, or storage-skipping; (d) **online/adaptive** — start building, sample effectiveness, and *abort* or *resize* mid-flight; (e) **learned** — predict effectiveness from query features / historical workload. The objective is a net-benefit function, and the difficulty is that effectiveness depends on *runtime* selectivity unknown at planning time.

## 2. Mathematical Foundations

A Bloom filter with $m$ bits and $n$ keys at $k$ hashes has false-positive rate $f(m,n,k)=\big(1-(1-1/m)^{kn}\big)^k \approx (1-e^{-kn/m})^k$, minimized at $k^\star=\frac{m}{n}\ln 2$ giving $f \approx (0.6185)^{m/n}$; equivalently $\approx 1.44\log_2(1/f)$ bits/key. Net benefit of pushing $F$ to a probe of size $N_p$ with true probe selectivity $\sigma$ (fraction surviving): $\text{savings}=N_p(1-\sigma)\,c_{\text{down}} - \big(c_{\text{build}}(n) + N_p c_{\text{probe}} + f\cdot N_p\,c_{\text{down}}\big)$, where the $f\cdot N_p$ term is wasted downstream work from false positives. Optimal sizing maximizes this over $m$ — a smooth convex-ish tradeoff once $\sigma$ is known; the catch is $\sigma$ is a *random/unknown* quantity, making this an **online decision under uncertainty** (bandit/optimal-stopping). **Learned filters** (Kraska et al.) replace/augment the bit array with a model predicting membership, achieving lower space at given $f$ when keys are learnable; **adaptive filters** (Bender et al.) repair false positives online. Sizing under unknown $\sigma$ connects to **prophet inequalities / secretary** style stopping.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Optimal *static* Bloom sizing is textbook; **learned Bloom filters** (Kraska–Beutel–Chi–Dean–Polyzotis, SIGMOD 2018) and the **sandwiched learned Bloom filter** (Mitzenmacher) give analyzed space/FPR tradeoffs; **adaptive cuckoo/quotient filters** (Bender et al.) and **telescoping/broom filters** fix false positives and adapt to query distributions. **Systems-SOTA:** Cost-based runtime-filter decisions in **Trino/Presto, Impala, Spark (runtime Bloom + DPP), Snowflake, Oracle, SQL Server batch-mode Bloom**, plus **LIP**'s adaptive ordering/gating (Zhu et al.). Engines use cardinality thresholds and runtime sampling to disable unprofitable filters, and push min/max + Bloom into Parquet/ORC/Iceberg data skipping. Decisions are largely **heuristic** (build if estimated build-side small and selectivity high).

## 4. Upper Bound

Given the *true* probe selectivity $\sigma$ and cardinalities, the net-benefit objective is maximized in closed form over filter size $m$ (the bits/key vs. false-positive tradeoff is convex in the relevant regime), so the *offline* sizing/placement decision is polynomial. **Online**, an adaptive scheme that samples the first $\Theta(\log(1/\delta)/\gamma^2)$ probe tuples estimates $\sigma$ to $\pm\gamma$ and then commits to build/size/abort, giving near-offline-optimal expected net benefit w.h.p. **LIP** gives a *robustness* guarantee: adaptive filter ordering competitive with the best fixed order. Learned Bloom filters achieve the same FPR at empirically lower space when keys are model-learnable. No general algorithm provably matches the *best-in-hindsight* build/size/push decision across arbitrary workloads.

## 5. Lower Bound

Approximate membership requires at least $n\log_2(1/f)$ bits (Carter–Floyd–Gill–Markowsky–Wegman, STOC 1978) — the information-theoretic optimum; a *standard* Bloom filter pays a $1.44\times$ overhead ($\approx 1.44\log_2(1/f)$ bits/key), and Pagh–Pagh–Rao *remove* that overhead, achieving close to the $\log_2(1/f)$ optimum — so no filter is more compact than $n\log_2(1/f)$ for given $f$, capping achievable overhead reduction. Learned filters only beat it by *assuming structure* (and their worst-case is bounded below by the same bound on the "backup" filter). **Online** decisions face an information-theoretic barrier: distinguishing a high-selectivity from a low-selectivity probe can require seeing $\Omega(1/\Delta^2)$ tuples (Chernoff/sampling lower bound), so any adaptive scheme must pay some exploration cost — *strict* no-regret build decisions are impossible. These are information-theoretic / space lower bounds, not NP-hardness.

## 6. The Gap

Offline (known $\sigma$) sizing and placement is **closed**. The **empirically-open** gap is the *adaptive, learned, workload-aware* decision: production systems and learned-filter research show large practical wins, but there is **no algorithm with a proven competitive ratio / regret bound** for the full build-vs-skip, size, and push-depth decision against the best-in-hindsight policy on general join plans — and the sampling lower bound says some exploration regret is unavoidable. Closing it means a regret-bounded online policy (with learning) plus a validated cost model that engines can adopt, replacing today's hand-tuned thresholds.

## 7. Current Research (as of June 2026)

(1) **Learned & adaptive AMQ structures** — learned Bloom successors, adaptive cuckoo/quotient/broom filters that repair false positives and track shifting query distributions (Bender, Mitzenmacher, Kraska lineage). (2) **Cost-based & cardinality-driven runtime-filter planning** in Trino/Spark/Velox, increasingly using runtime sampling to gate filters. (3) **Storage-level pushdown** — runtime Bloom/min-max driving Iceberg/Delta/Parquet data skipping, with net-benefit accounting for I/O saved. (4) **Bandit / optimal-stopping formulations** of the build/size/abort decision. Groups: Mitzenmacher (Harvard), Bender (Stony Brook), Kraska/Marcus (MIT), the Trino/Presto and Databricks runtime-filter teams. *(frontier — verify)* 2025–2026 efforts report learned, self-sizing runtime filters that abort unprofitable builds via early sampling and beat static thresholds across TPC-H/DS; regret guarantees remain partial.

## 8. Future Work

- A regret-bounded online policy for the joint build/size/push-depth decision, charging exploration cost.
- Validated, engine-adoptable cost models replacing hand-tuned cardinality thresholds.
- Learned filters with worst-case guarantees under distribution shift across a workload.
- Net-benefit accounting that spans operator, scan, and storage-I/O pushdown uniformly.
- Co-design of filter sizing with memory budgets and concurrency (filters competing for cache).

## 9. Key References

- **[Foundational]** Bloom. *Space/Time Trade-offs in Hash Coding with Allowable Errors.* CACM, 1970. — [DOI](https://doi.org/10.1145/362686.362692)
- **[Foundational]** Carter, Floyd, Gill, Markowsky, Wegman. *Exact and Approximate Membership Testers.* STOC 1978. *(the $n\log_2(1/f)$ space lower bound)* — [DOI](https://doi.org/10.1145/800133.804332)
- **[Foundational]** Pagh, Pagh, Rao. *An Optimal Bloom Filter Replacement.* SODA 2005. — [DBLP](https://dblp.org/rec/conf/soda/PaghPR05.html)
- **[SOTA]** Kraska, Beutel, Chi, Dean, Polyzotis. *The Case for Learned Index Structures (learned Bloom filters).* SIGMOD 2018. — [arXiv](https://arxiv.org/abs/1712.01208)
- **[SOTA]** Mitzenmacher. *A Model for Learned Bloom Filters and Optimizing by Sandwiching.* NeurIPS 2018. — [NeurIPS](https://papers.nips.cc/paper_files/paper/2018/hash/0f49c89d1e7298bb9930789c8ed59d48-Abstract.html)
- **[SOTA]** Bender, Farach-Colton, et al. *Bloom Filters, Adaptivity, and the Dictionary Problem (Adaptive AMQ / Broom Filters).* FOCS 2018. — [arXiv](https://arxiv.org/abs/1711.01616)
- **[SOTA]** Zhu, Potti, Saurabh, Patel. *Looking Ahead Makes Query Plans Robust (LIP).* PVLDB 2017. — [PVLDB](https://www.vldb.org/pvldb/vol10/p889-zhu.pdf)
- **[Survey]** Broder, Mitzenmacher. *Network Applications of Bloom Filters: A Survey.* Internet Mathematics, 2004. — [DOI](https://doi.org/10.1080/15427951.2004.10129096)

## 10. Worked Example

Join `orders ⋈ customers` on `cust_id`. Build side `customers` has $n=10^5$ keys; probe side `orders` has $N_p=10^7$ rows. Suppose only $\sigma=2\%$ of orders match a built filter, so the filter could prune $0.98\cdot N_p = 9.8{\times}10^6$ rows. Take $c_{\text{down}}=5$ ns saved per pruned row, $c_{\text{probe}}=1$ ns, and build cost $c_{\text{build}}(n)\approx n\cdot 5\,\text{ns}=0.5$ ms.

Size the filter at $m/n=10$ bits/key ($m=10^6$ bits $\approx 125$ KB). Optimal hashes $k^\star=\tfrac{m}{n}\ln 2\approx 7$, giving $f\approx 0.6185^{10}\approx 0.0082$.

- Savings: $9.8{\times}10^6 \times 5\,\text{ns} = 49$ ms.
- Costs: build $0.5$ ms $+$ probe $10^7\times 1\,\text{ns}=10$ ms $+$ false-positive waste $f\cdot N_p\cdot c_{\text{down}} = 0.0082\times10^7\times5\,\text{ns}\approx 0.41$ ms.

Net benefit $\approx 49 - 10.9 = 38.1$ ms: clearly build it. But if runtime sampling revealed $\sigma=90\%$ instead, savings shrink to $10^7\cdot0.1\cdot5\,\text{ns}=5$ ms $<$ the $10.9$ ms cost — the adaptive policy should *abort* the build.

---
*Part of the [DBMS Research catalog](../../README.md).*
