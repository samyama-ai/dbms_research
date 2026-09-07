---
id: 11-nosql-kv/secondary-index-selection
title: "Secondary Index Selection for KV"
topic: 11-nosql-kv
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Secondary Index Selection for KV

> **Topic:** NoSQL & Key-Value Stores · **ID:** `11-nosql-kv/secondary-index-selection` · **Status:** open

## 1. Problem Statement

A key-value store natively indexes only the primary key. Many workloads query by **non-key attributes** (e.g., "all users with `status=active`"), requiring **secondary indexes**. Each materialized secondary index speeds matching reads but adds **write amplification** (every base write updates its indexes) and storage. The selection problem: given a workload (a set of queries with frequencies and a stream of writes) and a **write budget** (max tolerable extra write amplification / index-maintenance throughput) plus a space budget, choose the **subset of indexes to materialize** that minimizes total expected query cost.

Variants:
- **Decision:** Is there an index set $S$ with maintenance cost $\leq W$ and total query cost $\leq Q$?
- **Optimization (budgeted):** $\max$ benefit (query speedup) s.t. write-maintenance + space $\leq B$.
- **Online:** workload drifts; create/drop indexes adaptively (index tuning as a sequential decision problem).
- Index *type* choice (covering vs. non-covering, composite, partial/filtered, global vs. local-per-shard) widens the candidate space combinatorially.

## 2. Mathematical Foundations

Let candidate indexes be $\mathcal{I}=\{I_1,\dots,I_n\}$. Query $q$ has frequency $f_q$ and cost $\mathrm{cost}(q,S)$ given selected set $S\subseteq\mathcal{I}$. Maintenance cost of $S$ is $\sum_{I\in S} m_I$ (writes touching $I$). The budgeted objective:
$$\max_{S}\ \mathrm{Benefit}(S)=\sum_q f_q\big(\mathrm{cost}(q,\varnothing)-\mathrm{cost}(q,S)\big)\quad\text{s.t.}\ \sum_{I\in S} m_I \leq W,\ |S|\text{ or space}\leq K.$$

The benefit function is typically **monotone submodular** in $S$ (diminishing returns: an index helps less once a related one exists), bringing the **submodular maximization under a knapsack/cardinality constraint** machinery: the greedy algorithm gives a $(1-1/e)$ approximation for cardinality (Nemhauser–Wolsey–Fisher) and $(1-1/e)$ via cost-benefit greedy + partial enumeration for knapsack (Sviridenko). However, **query-index interactions** (a query usable by multiple indexes, index intersection) can break pure submodularity, making it the harder **maximum coverage / facility-location** regime.

Classic framing: this is the database **index selection problem** (ISP), known NP-hard, historically attacked with the optimizer's **what-if** cost estimates (Chaudhuri–Narasayya, AutoAdmin).

## 3. State of the Art (SOTA)

- **Theory-SOTA:** submodular greedy with $(1-1/e)$ guarantee when benefit is submodular; generalized to multiple knapsack/matroid constraints with $\approx 1/2$ or $(1-1/e)$ bounds.
- **Systems-SOTA (relational):** Microsoft **AutoAdmin / Database Tuning Advisor** (Chaudhuri–Narasayya, VLDB 1997+), DB2 Design Advisor, Oracle Access Advisor — what-if-cost-driven, heuristic enumeration.
- **Learned/RL index tuning:** **DBA Bandits** and reinforcement-learning index advisors (e.g., **SWIRL**, Kossmann et al.; **DRLindex**), and Microsoft's RL tuners — treat selection as MAB / RL.
- **KV-specific:** global vs. local secondary indexes in **Cassandra** (SASI), **DynamoDB GSIs/LSIs**, **MongoDB** index advisor, **HBase/Phoenix**. DynamoDB exposes GSI write-capacity coupling explicitly, making the write-budget tradeoff first-class.

## 4. Upper Bound

For the **budgeted submodular** formulation, greedy yields a provable $(1-1/e)\approx 0.632$ approximation under a cardinality constraint, and Sviridenko's cost-effective greedy with enumeration gives $(1-1/e)$ under a single knapsack (write budget) constraint, in polynomial time. Lazy/accelerated greedy (Minoux) makes it scalable. For multiple linear constraints (write + space), continuous-greedy + rounding gives $(1-1/e-\epsilon)$. These are the strongest guarantees and require the benefit oracle (what-if cost), which is itself approximate.

## 5. Lower Bound

- **NP-hardness:** index selection is NP-hard (reduction from set cover / knapsack), so no exact poly algorithm unless P=NP.
- **Inapproximability:** because the problem generalizes **maximum coverage**, it is NP-hard to approximate within $(1-1/e+\epsilon)$ (Feige's $(1-1/e)$ hardness for max-coverage) — the greedy bound is *tight* in the worst case under standard assumptions.
- When query-index benefit is non-submodular (index intersection / interaction), the problem can become as hard as general constrained set optimization with no constant-factor guarantee.
- The online variant inherits **MAB regret lower bounds** $\Omega(\sqrt{KT})$ for $K$ candidate configurations over $T$ rounds.

## 6. The Gap

For the **submodular** model the gap is essentially **closed**: greedy $(1-1/e)$ matches Feige's $(1-1/e)$ hardness. The genuinely **open** parts are: (1) accurate, cheap **benefit estimation** for KV/LSM stores where maintenance cost depends on compaction dynamics (not a static what-if model), (2) handling **non-submodular interactions** (covering indexes, intersection) with guarantees, and (3) the **online/drifting** setting where create/drop has switching cost — no tight regret-vs-reconfiguration-cost bound exists. The "open" status reflects that the *static relational* theory does not transfer cleanly to *write-heavy LSM KV stores* with compaction-coupled maintenance cost.

## 7. Current Research (as of June 2026)

- RL / contextual-bandit index advisors with safety/regret guarantees (Kossmann, Schlosser — HPI; Microsoft Research) *(frontier — verify)*.
- Learned cost models replacing what-if calls for LSM write amplification *(frontier — verify)*.
- Workload-drift-aware online index tuning with bounded switching cost; "self-driving" databases (Pavlo — CMU, OtterTune lineage).
- KV-native global secondary index maintenance protocols minimizing write fan-out (DynamoDB, TiDB, Cassandra communities).

## 8. Future Work

- Approximation guarantees under non-submodular index interactions.
- Compaction-aware maintenance-cost models feeding selection.
- Online index tuning with provable regret + bounded reconfiguration churn.
- Joint selection of index type (covering/partial/composite) and tier placement.

## 9. Key References

- **[Foundational]** Chaudhuri, S., Narasayya, V. *An Efficient Cost-Driven Index Selection Tool for Microsoft SQL Server.* VLDB, 1997. — [DBLP](https://dblp.uni-trier.de/rec/conf/vldb/ChaudhuriN97.xml)
- **[Foundational]** Nemhauser, G., Wolsey, L., Fisher, M. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)
- **[Foundational]** Feige, U. *A Threshold of ln n for Approximating Set Cover.* JACM, 1998. — [DOI](https://doi.org/10.1145/285055.285059)
- **[SOTA]** Sviridenko, M. *A Note on Maximizing a Submodular Set Function Subject to a Knapsack Constraint.* Operations Research Letters, 2004. — [DOI](https://doi.org/10.1016/S0167-6377(03)00062-2)
- **[SOTA]** Kossmann, J., Schlosser, R., et al. *SWIRL: Selection of Workload-aware Indexes using Reinforcement Learning.* EDBT, 2022. — [PDF](https://openproceedings.org/2022/conf/edbt/paper-37.pdf)
- **[Survey]** Chaudhuri, S., Narasayya, V. *Self-Tuning Database Systems: A Decade of Progress.* VLDB, 2007. — [DBLP](https://dblp.org/rec/conf/vldb/ChaudhuriN07.html)

## 10. Worked Example

Three candidate indexes $\{A,B,C\}$ on a `users` table, write budget $W=2$ (each index costs 1 maintenance unit). Per-query benefit (cost saved $\times$ frequency):

| Set | Benefit |
|-----|---------|
| $\{A\}$ | 10 |
| $\{B\}$ | 8 |
| $\{C\}$ | 7 |
| $\{A,B\}$ | 15 |
| $\{A,C\}$ | 14 |
| $\{B,C\}$ | 12 |

Note diminishing returns: $A{+}B$ gives 15, not $10{+}8=18$ (overlapping queries) — the function is submodular. Greedy under cardinality $K=2$: pick $A$ (best singleton, +10), then the best marginal addition — $B$ adds $15-10=5$, $C$ adds $14-10=4$ — so pick $B$, yielding $\{A,B\}=15$.

Is greedy optimal here? The best pair is $\{A,B\}=15$, so yes. The $(1-1/e)$ guarantee bounds the worst case: greedy $\ge 0.632 \cdot \text{OPT}$. Here greedy hits OPT exactly. The third index $C$ is rejected: adding it would breach $W=2$.

---
*Part of the [DBMS Research catalog](../../README.md).*
