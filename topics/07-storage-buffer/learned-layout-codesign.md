---
id: 07-storage-buffer/learned-layout-codesign
title: "End-to-End Learned Storage-Layout Co-Design"
topic: 07-storage-buffer
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# End-to-End Learned Storage-Layout Co-Design

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/learned-layout-codesign` · **Status:** open
> **Verification note:** The Qd-tree (SIGMOD 2020) author list was corrected — the actual authors are Yang, Chandramouli, Wang, Gehrke, Li, Minhas, Larson, Kossmann, Acharya (the prior list mixed in unrelated names).

## 1. Problem Statement

Compression scheme, physical layout (row/column/PAX, sort order, partitioning), and tiering (DRAM/NVM/SSD/object-store placement) are today tuned **independently**, yet they interact: a layout that compresses well may scan poorly; a tier choice changes the cost of a layout's access pattern. The problem: **jointly learn** all three decisions to minimize **total query cost** over a workload, end-to-end.

Formally: given a dataset, a workload distribution $\mathcal{W}$, and a cost model, choose a configuration $x = (\text{compression } c, \text{layout } \ell, \text{tiering } \tau)$ from a combinatorial space $\mathcal{X}$ minimizing expected cost $\mathbb{E}_{q\sim\mathcal{W}}[\text{cost}(q; x)] + \lambda\cdot\text{storage}(x)$, subject to a memory/budget constraint, possibly online as $\mathcal{W}$ drifts and with bounded reorganization cost.

Variants:
- **Static optimization:** best fixed configuration for a known workload.
- **Decision:** does some configuration achieve cost $\le C$ within budget $B$?
- **Online/adaptive:** reconfigure under drift, amortizing migration I/O (a metrical-task-system / rent-or-buy flavor).

## 2. Mathematical Foundations

**Combinatorial configuration search.** The joint space is exponential: compression ∈ {dict, RLE, FOR, bit-pack, …}, layout ∈ orderings × partitions × format, tiering ∈ placements. Selecting layout alone subsumes **physical database design** (index/partition selection), known NP-hard. The objective is generally **non-submodular and non-convex** because of cross-term interactions (compression × scan × tier), so clean greedy guarantees do not transfer.

**Cost-model surrogates.** Learned cost models approximate $\text{cost}(q;x)$; the search becomes **black-box / Bayesian optimization** or **RL over configurations** (state = current layout, action = transform, reward = $-\Delta\text{cost}$). Sample complexity is governed by the surrogate's generalization (Rademacher/VC complexity of the cost-predictor class).

**Information-theoretic floor.** Compression cannot beat the workload-conditioned **entropy** $H(\text{data}\mid\text{schema})$; layout cannot reduce scanned bytes below what the query's selectivity and the data's **sort-order entropy** permit — these bound achievable cost from below.

**Tiering as caching/assignment.** The placement subproblem is a **generalized assignment / weighted caching** instance (each fragment to a tier with capacity and access-cost), NP-hard, $O(\log)$-competitive online.

## 3. State of the Art (SOTA)

**Systems-SOTA.** **Qd-tree** (Yang et al., SIGMOD 2020) learns layouts via RL; **learned/automatic physical design** (Microsoft's **AutoAdmin** lineage, **DBA bandits**, Marcus et al. on learned optimizers/**Bao**, **Neo**); **MutableDB / self-driving** layout reorg (CMU **NoisePage/Peloton** self-driving DB, Pavlo et al.). **Lakehouse formats** (Delta liquid clustering, Iceberg, Hudi) co-decide partitioning + clustering + compaction. Per-component learning exists (learned compression e.g. **CorBit/BtrBlocks** column encodings, Kuschewski et al. VLDB 2023; learned tiering); **joint** end-to-end learning of all three is largely aspirational — hence **open**.

**Theory-SOTA.** Approximation theory for the constituent subproblems (physical design NP-hardness; submodular index selection special cases; $O(\log)$-competitive tiering). No unified approximation for the joint objective.

## 4. Upper Bound

- **Per-subproblem:** physical/index design has greedy heuristics with **submodular guarantees only in restricted models**; tiering as weighted caching is $O(\log k)$-competitive (Bansal–Buchbinder–Naor).
- **Joint search:** Bayesian optimization / RL converge empirically (Qd-tree, Bao) but carry **no worst-case approximation guarantee** for the joint cost.
- **Compression:** entropy coders reach $H+\epsilon$ bits/symbol; learned encodings approach the conditional-entropy floor empirically.
- Net: the best *provable* upper bounds are per-component; the joint problem has only **heuristic/empirical** upper bounds.

## 5. Lower Bound

- **Physical design / partition+index selection is NP-hard** (reduction from set cover / knapsack); the joint problem is at least as hard.
- **Tiering/assignment** is NP-hard (generalized assignment) and online-competitive-bounded by $\Omega(\log k)$ (weighted caching).
- **Compression** is bounded below by source entropy $H$ (Shannon — information-theoretic).
- Under **Unique-Games/SSE**, layout-partition objectives lack constant-factor approximation (inherited from partitioning hardness).
- No lower bound is known *specific* to the *joint, cost-model-driven* objective beyond what the components imply — itself open.

## 6. The Gap

**Genuinely open.** Each component (compression near entropy, layout/index NP-hard with heuristics, tiering $O(\log)$-competitive) is individually understood, but the **joint** problem has (i) no approximation algorithm capturing cross-term interactions, (ii) no lower bound specific to the joint objective, and (iii) reliance on **learned cost surrogates** whose error invalidates any guarantee derived assuming an exact cost oracle. Closing it requires a tractable structured model of the interactions (e.g., conditions under which the joint objective is submodular or admits a PTAS), generalization bounds tying surrogate error to regret, and an online theory bounding reconfiguration cost under drift. Today's evidence is empirical, workload-specific, and guarantee-free.

## 7. Current Research (as of June 2026)

- **Unified self-driving storage** co-deciding compression + layout + tiering via RL with learned cost models (CMU self-driving DB, MIT DSAIL, Microsoft GSL). *(frontier — verify)*
- **Learned column encodings** (BtrBlocks successors) feeding layout/tiering jointly. *(frontier — verify)*
- **Lakehouse auto-optimization** (Delta/Iceberg) merging clustering, compaction, and tier placement under cost. *(frontier — verify)*
- **LLM/foundation-model-driven** configuration agents proposing layouts from schema+workload text. *(frontier — verify)*

## 8. Future Work

- A structural characterization (submodularity / PTAS conditions) of the joint compression-layout-tiering objective.
- Generalization bounds linking learned-cost-model error to end-to-end regret.
- Online co-design with provable competitive bounds against reconfiguration (migration) cost under workload drift.
- A reproducible, cost-faithful benchmark quantifying the gap between learned joint design and the optimal configuration.

## 9. Key References

- **[SOTA]** Yang, Chandramouli, Wang, Gehrke, Li, Minhas, Larson, Kossmann, Acharya. *Qd-tree: Learning Data Layouts for Big Data Analytics.* SIGMOD, 2020. — [arXiv](https://arxiv.org/abs/2004.10898)
- **[Foundational]** Chaudhuri, Narasayya. *AutoAdmin "What-If" Index Analysis and Automated Physical Design.* SIGMOD/VLDB, 1997–1998. — [DOI](https://doi.org/10.1145/276305.276337)
- **[SOTA]** Marcus, Negi, Mao, et al. *Bao: Learned Query Optimization with Steering.* SIGMOD, 2021. — [arXiv](https://arxiv.org/abs/2004.03814)
- **[SOTA]** Kuschewski, Sauerwein, Alhomssi, Leis. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3589263)
- **[SOTA]** Pavlo, Angulo, Arulraj, et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/PavloAALLMMMPQS17.html)
- **[Foundational]** Shannon. *A Mathematical Theory of Communication.* Bell System Technical Journal, 1948. — [DOI](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x)

## 10. Worked Example

A column of 1M integers, workload = full scans (90%) + occasional point lookups (10%). Three coupled decisions, with a learned cost model giving per-query bytes:

| Config $x$ | Compression | Layout | Tier | Scan cost | Storage |
|---|---|---|---|---|---|
| $x_1$ | none | column | DRAM | 4.0 MB | 4.0 MB |
| $x_2$ | dict+RLE | column, sorted | DRAM | 0.5 MB | 0.6 MB |
| $x_3$ | dict+RLE | column, sorted | SSD | 0.5 MB read + 5x SSD latency | 0.6 MB |

The **cross-term** is visible: sorting (layout) is what makes RLE (compression) effective — choosing them independently misses the $8\times$ scan win of $x_2$. Objective $\mathbb{E}[\text{cost}] + \lambda\,\text{storage}$ with $\lambda=1$:
$$x_1: 0.9(4.0)+0.1(4.0)+4.0 = 8.0,\quad x_2: 0.9(0.5)+0.1(0.5)+0.6 = 1.1.$$
$x_2$ wins ($7\times$). But naively tiering to SSD ($x_3$) to save DRAM inflates the dominant scan latency — illustrating why placement cannot be optimized after layout. The joint space here is just $|\text{compr}|\times|\text{layout}|\times|\text{tier}|$, yet real schemas make $|\mathcal{X}|$ exponential, and no approximation captures these interactions.

---
*Part of the [DBMS Research catalog](../../README.md).*
