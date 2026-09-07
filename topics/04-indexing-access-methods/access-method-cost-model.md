---
id: 04-indexing-access-methods/access-method-cost-model
title: "Unified cost model for access-method design"
topic: 04-indexing-access-methods
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Unified cost model for access-method design

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/access-method-cost-model` · **Status:** open

## 1. Problem Statement
The space of data-structure/access-method designs (B-trees, LSM-trees, hash indexes, learned indexes, tries, skip lists, bitmap/zone maps, and their countless hybrids) is enormous and combinatorially structured. The problem is to build a **unified, predictive cost model** that, given a design point $d$ in this space, a workload $W$ (read/write/range/point mix, skew, update rate), and a hardware profile $H$ (cache/memory/SSD/NVM/GPU latencies and bandwidths), predicts performance metrics (latency, throughput, space, write amplification, energy) accurately enough to **automatically synthesize or search for** the best structure. Variants: the **prediction** variant (estimate cost of a *given* design), the **synthesis/optimization** variant (find $\arg\min_d \mathrm{cost}(d, W, H)$ over a design space), and the **what-if/tuning** variant (recommend index sets/configurations). It is *open* whether a model can be simultaneously **general** (spanning the design space), **accurate** (matching measured performance), and **tractable** to optimize over.

## 2. Mathematical Foundations
The conceptual basis is the **"design space as first-class object"** view (Idreos et al., *The Periodic Table of Data Structures*, IEEE Data Eng. Bull. 2018; *Design Continuums*, CIDR 2019): a structure is a point in a space of **design primitives** (fanout, node layout, filters, buffering, partitioning, key/model representation), and cost is a function over this space. Foundational sub-models: the **external-memory / I/O model** (Aggarwal–Vitter, 1988) giving I/O complexity in terms of block size $B$ and memory $M$; the **cache-oblivious** model (Frigo–Leiserson–Prokop–Ramachandran, 1999) for multi-level hierarchies; and **LSM-tree cost theory** (Dostoevsky/Monkey: O'Neil et al. 1996; Dayan–Athanassoulis–Idreos, SIGMOD 2017/2018) which expresses read/write/space as closed-form functions of merge policy, size ratio $T$, and Bloom-filter bit allocation, yielding $O(\log_T N)$-style trade-offs and **Pareto frontiers**. Query optimization's **cardinality/selectivity** estimation (Selinger et al., SIGMOD 1979) feeds the workload term. The unified model is essentially a (possibly learned) function $c:\mathcal{D}\times\mathcal{W}\times\mathcal{H}\to\mathbb{R}^k$ whose **smoothness/Lipschitzness** over $\mathcal{D}$ would make synthesis tractable.

## 3. State of the Art (SOTA)
- **Design-space frameworks:** *Periodic Table of Data Structures* and *Design Continuums* (Idreos et al., 2018–2019); the **Data Calculator** (Idreos et al., SIGMOD 2018) — interactively computes the cost of a design from primitives and learned cost models, a partial realization of synthesis.
- **LSM tuning:** **Monkey** (Dayan et al., SIGMOD 2017) and **Dostoevsky** (SIGMOD 2018) give closed-form, navigable cost models and Pareto-optimal merge/filter configurations; **"Log-Structured Merge-Tree" design space** continued by Dayan/Athanassoulis.
- **Learned cost models:** ML-based cost/latency predictors for query and storage engines; *self-driving DBMS* (Pavlo et al., CMU **NoisePage/OtterTune**, CIDR 2017 / SIGMOD 2017) and learned what-if index advisors.
- **Index advisors (industrial):** Microsoft **AutoAdmin** (Chaudhuri–Narasayya, VLDB 1997) and modern DBA tooling for index selection — the optimization variant at the configuration level.

## 4. Upper Bound
For **constrained** sub-spaces, sharp results exist: Monkey/Dostoevsky give *provably Pareto-optimal* LSM configurations via closed-form cost in the I/O model, and the index-selection problem can be solved optimally for small candidate sets. The Data Calculator computes a design's cost in time roughly linear in the number of primitives, enabling **bounded local search** over the continuum. Thus, *within* a parametric family the model is accurate and the optimizer tractable. No general result gives an efficiently optimizable, provably accurate model across the *whole* heterogeneous design space.

## 5. Lower Bound
The general synthesis variant is hard: **index selection** (choosing an index set under a storage budget to minimize workload cost) is **NP-hard** (reduction from set-cover/knapsack; Chaudhuri–Narasayya and follow-ups), and the broader "synthesize the optimal data structure" is at least as hard. Cost itself inherits structural lower bounds — e.g., the **predecessor cell-probe bound** $\Omega(\log_w N/\log\log N)$ (Pătrașcu–Thorup 2006) caps any range-index design, and LSM read/write/space obey a provable **three-way trade-off** (you cannot optimize all of point-read, range-read, and write simultaneously; Dayan–Idreos). Selectivity/cardinality estimation, the model's input, is itself worst-case hard to bound, injecting irreducible error.

## 6. The Gap
The gap is between **per-family accuracy + tractability** (LSM Pareto models, Data Calculator within a continuum) and a **global, cross-family, hardware-portable model that is both accurate and optimizable**. We lack a smooth, composable cost function spanning B-tree/LSM/hash/learned/GPU designs whose minima can be found efficiently, and lack tight handling of skew, correlation, and concurrency. Because index selection is NP-hard and the design space is non-convex and discrete, an *exact* global optimizer is unlikely; the realistic open target is a **provably-bounded-error model + good approximation/search** with quality guarantees. This is genuinely open.

## 7. Current Research (as of June 2026)
Active: **learned and hybrid analytical/ML cost models** that generalize across hardware (transfer learning over device profiles); design-synthesis tools extending the Data Calculator toward automatic structure generation; **reinforcement-learning index/structure advisors**; and energy-/CXL-/GPU-aware cost terms *(frontier — verify)*. Groups: Idreos (Harvard — design space, Data Calculator, design continuums), Dayan/Athanassoulis (BU — LSM cost theory), Pavlo/Ma (CMU — self-driving DBMS, behavior modeling), Kraska/Marcus (MIT — learned components and benchmarking), and Microsoft/industrial auto-tuning. Reproducibility and cross-hardware portability of learned cost models are recurring concerns.

## 8. Future Work
- A composable, hardware-portable cost model spanning the full primitive design space.
- Approximation algorithms for structure synthesis with provable quality guarantees despite NP-hardness.
- Unified treatment of concurrency, skew, correlation, and energy in one model.
- Tight integration with cardinality estimation uncertainty (robust/risk-aware optimization).
- Auto-synthesis pipelines that emit and deploy custom access methods for a given $W,H$.

## 9. Key References
- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** P. G. Selinger, M. M. Astrahan, D. D. Chamberlin, R. A. Lorie, T. G. Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DBLP](https://dblp.org/rec/conf/sigmod/SelingerACLP79.html)
- **[SOTA]** S. Idreos, K. Zoumpatianos, et al. *The Data Calculator: Data Structure Design and Cost Synthesis from First Principles.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3199671)
- **[SOTA]** N. Dayan, M. Athanassoulis, S. Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064054)
- **[SOTA]** N. Dayan, S. Idreos. *Dostoevsky: Better Space-Time Trade-Offs for LSM-Tree Based Key-Value Stores.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196927)
- **[Foundational]** S. Chaudhuri, V. Narasayya. *An Efficient Cost-Driven Index Selection Tool for Microsoft SQL Server (AutoAdmin).* VLDB, 1997. — [DBLP](https://dblp.org/rec/conf/vldb/ChaudhuriN97.html)
- **[Survey]** S. Idreos, et al. *The Periodic Table of Data Structures.* IEEE Data Engineering Bulletin, 2018. — [DBLP](https://dblp.org/db/journals/debu/debu41.html)

## 10. Worked Example

Consider an LSM-tree holding $N/B = 10^6$ entries, size ratio $T$, and a Monkey-style cost model in the I/O model. Point-lookup I/O cost under leveling is $\approx \log_T(N/B)$ levels each guarded by a Bloom filter; write amplification is $\approx T\log_T(N/B)$.

Evaluate two design points:

- $T = 2$: read $\log_2(10^6) \approx 20$ levels; write amp $\approx 2 \times 20 = 40$.
- $T = 10$: read $\log_{10}(10^6) = 6$ levels; write amp $\approx 10 \times 6 = 60$.

So raising $T$ from 2 to 10 cuts read levels $3.3\times$ (20 → 6) but raises write amplification $1.5\times$ (40 → 60) — a concrete Pareto trade-off the unified cost function $c(d,W,H)$ must expose. A write-heavy workload picks small $T$; a read-heavy one picks large $T$. The open challenge: make this same closed-form navigability hold *across* families (LSM vs. B-tree vs. learned) and across hardware $H$, not just within the LSM continuum.

---
*Part of the [DBMS Research catalog](../../README.md).*
