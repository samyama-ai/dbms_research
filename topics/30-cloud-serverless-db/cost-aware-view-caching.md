---
id: 30-cloud-serverless-db/cost-aware-view-caching
title: "Cost-aware materialized-view and cache placement"
topic: 30-cloud-serverless-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Cost-aware materialized-view and cache placement

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/cost-aware-view-caching` · **Status:** open

## 1. Problem Statement
In a cloud data warehouse the optimizer can answer queries from base tables, from **materialized views/results**, or from a **cache** (memory or local SSD), and data may live in object storage in another region. Each option carries a *separately priced* cloud resource: **storage** (\$/GB-month to keep a materialization), **recomputation** (\$ of compute to (re)build or refresh it), and **egress/transfer** (\$/GB to move bytes across regions or out of object storage). The problem: **given a query workload, decide which views to materialize and which results/pages to cache, where, to minimize total dollar cost (storage + compute + egress) subject to a freshness/staleness bound and a latency SLO.**

- **Decision variant:** Given a budget $B$ and a set of candidate views, is there a selection meeting all query SLOs with cost $\le B$?
- **Optimization variant:** Minimize $\text{cost} = \alpha\cdot\text{storage} + \beta\cdot\text{compute} + \gamma\cdot\text{egress}$ over what to materialize/cache and where.
- **Online (caching) variant:** Maintain the cache under a stream of queries minimizing competitive cost ratio, where eviction/admission costs are price-weighted.

## 2. Mathematical Foundations
This is the **view-selection problem** (Harinarayan–Rajaraman–Ullman, SIGMOD 1996), classically on the **data-cube lattice**: views form a partial order by derivability, and choosing $k$ views to materialize to minimize query cost is the canonical setting where the benefit function is **monotone submodular** — so the **greedy algorithm gives a $(1-1/e)$-approximation** (Nemhauser–Wolsey–Fisher). With a knapsack-style budget over heterogeneous prices, the cost–benefit greedy still yields $(1-1/e)$ via the Sviridenko/cost-benefit analysis.

Formally, let $Q$ be queries with frequencies $f_q$, $V$ candidate views with storage cost $s_v$, build cost $b_v$, and per-query egress saving. The objective
$$
\min_{M\subseteq V}\ \sum_{v\in M}\big(\alpha s_v + \beta b_v\big) \;+\; \sum_{q}f_q\Big(\beta\,\text{recompute}_q(M) + \gamma\,\text{egress}_q(M)\Big)
$$
is a **prize-collecting / facility-location-flavored** problem; the answer-from-cache choice adds an online **weighted caching** layer where eviction costs differ per item — the **weighted caching / $k$-server on a star** model, for which the deterministic competitive ratio is $k$ and randomized is $O(\log k)$ (Bansal–Buchbinder–Naor primal-dual).

Freshness adds a constraint: a materialized view at staleness $\Delta$ avoids per-query recompute but incurs refresh compute at rate tied to base-table change rate $\mu$ — a renewal-reward tradeoff between refresh frequency and staleness penalty.

## 3. State of the Art (SOTA)
**Theory-SOTA.** Submodular view selection with greedy $(1-1/e)$; AGM-bound-aware cost models for the recomputation term (worst-case join output size $\le \prod$ fractional-edge-cover bound, so recompute cost of a view is bounded by the AGM bound). Weighted/online caching primal-dual results (Bansal–Buchbinder–Naor, FOCS 2007).

**Systems-SOTA.** **Snowflake** result cache + automatic clustering + (search-optimization/materialized views) with usage-based billing exposing the exact storage/compute/egress prices. **AWS Redshift** automated materialized views and **autonomous** refresh; **Databricks** Delta caching and materialized views/`ENZYME` incremental view maintenance; **BigQuery** materialized views + BI Engine cache + smart result reuse. **Microsoft SQL Server** *Database Tuning Advisor* and the classic **AutoAdmin** index/view recommendation lineage. Cloud-cost-aware autonomous-tuning research (e.g., learned advisors).

## 4. Upper Bound
Offline static selection: **$(1-1/e)$-approximation** by greedy under monotone submodular benefit with a knapsack/budget — best known and, given the hardness below, essentially optimal. Online cache layer: **$O(\log k)$-competitive** randomized for weighted caching (price-weighted eviction), $k$-competitive deterministic, both matching their lower bounds.

## 5. Lower Bound
View/index selection is **NP-hard** (it generalizes set cover / weighted maximum coverage); maximizing coverage is **NP-hard to approximate better than $1-1/e$** (Feige 1998), so the greedy ratio is tight — you provably cannot beat $1-1/e$ in poly time unless P = NP. The online caching component has a deterministic competitive lower bound of $k$ and randomized $\Omega(\log k)$ (Fiat et al.). The recomputation-cost term inherits join-evaluation lower bounds; under fine-grained hypotheses, computing certain view contents cannot be done faster than the AGM/worst-case-optimal-join bound.

## 6. The Gap
Each *component* (static submodular selection, online weighted caching) is closed — tight $(1-1/e)$ and $\Theta(\log k)$. The **open** gap is the **joint, multi-price, freshness-constrained** problem: there is no algorithm with a proven approximation guarantee for simultaneously optimizing storage + compute + egress *with* a staleness constraint *and* an online query stream. The interaction (a cached result is also a candidate to materialize; egress price changes which copy to read) destroys submodularity in general. Closing it requires either a structural condition restoring submodularity or a combined competitive analysis for "buy (materialize) vs. rent (recompute) vs. fetch (egress)" — a multi-option rent-or-buy generalization.

## 7. Current Research (as of June 2026)
- Learned cost models that price recompute vs. egress vs. storage per query and feed an RL or bandit selector. *(frontier — verify)*
- Semantic/result caching for LLM-and-analytics pipelines, where cache hits avoid expensive recomputation. *(frontier — verify)*
- Incremental view maintenance (DBToaster/DBSP-style) lowering the refresh-compute term so materialization wins more often.
- Groups: AutoAdmin lineage (Microsoft Research, Chaudhuri/Narasayya), Snowflake/Databricks/BigQuery autonomous-tuning teams, view-maintenance theory (Koch, DBSP).

## 8. Future Work
- A unified approximation guarantee for the storage+compute+egress objective with freshness constraints.
- Online "materialize-or-cache-or-recompute" with competitive bounds against egress-price changes.
- Workload-drift-robust selection (re-selecting views without thrashing).

## 9. Key References
- **[Foundational]** Harinarayan, V., Rajaraman, A., Ullman, J. *Implementing Data Cubes Efficiently.* SIGMOD, 1996. — [DOI](https://doi.org/10.1145/235968.233333)
- **[Foundational]** Nemhauser, G., Wolsey, L., Fisher, M. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Mathematical Programming, 1978. — [DOI](https://doi.org/10.1007/BF01588971)
- **[Foundational]** Feige, U. *A Threshold of ln n for Approximating Set Cover.* JACM, 1998. — [DOI](https://doi.org/10.1145/285055.285059)
- **[SOTA]** Bansal, N., Buchbinder, N., Naor, J. *A Primal-Dual Randomized Algorithm for Weighted Paging.* FOCS, 2007. — [DOI](https://doi.org/10.1145/2339123.2339126)
- **[SOTA]** Ngo, H., Porat, E., Ré, C., Rudra, A. *Worst-Case Optimal Join Algorithms.* JACM, 2018. — [DOI](https://doi.org/10.1145/3180143)

## 10. Worked Example

**Greedy view selection on a tiny cube.** A sales cube over dimensions {Product, Store, Time} has a small lattice of candidate views with these row counts (the recompute cost of answering a query equals the size of the smallest materialized ancestor):

| View | Rows |
|------|------|
| $v_0$ = (P,S,T) base | 6,000,000 |
| $v_1$ = (P,S) | 800,000 |
| $v_2$ = (P,T) | 100,000 |
| $v_3$ = (none) total | 1 |

The base $v_0$ is always materialized (cost 0 to keep). We may materialize **one** extra view to speed every query. Greedy picks the view with the largest *benefit* = (rows saved per dependent query) × (#queries served). Materializing $v_2$ lets queries on (P,T) and (T) read $100{,}000$ rows instead of $6{,}000{,}000$ — benefit $\approx 5.9\text{M}$ per query over $2$ views $= 11.8\text{M}$. Materializing $v_1$ gives $(6\text{M}-0.8\text{M})\times 2 = 10.4\text{M}$. Greedy picks $v_2$.

By Nemhauser–Wolsey–Fisher, because this benefit function is monotone submodular, greedy is within $1 - 1/e \approx 0.63$ of the optimal $k$-view selection; by Feige, no poly-time algorithm beats $1-1/e$ unless P=NP — so $v_2$'s greedy choice is essentially optimal here. Add a per-GB egress price and the same cost-benefit greedy still holds its $(1-1/e)$ guarantee.

---
*Part of the [DBMS Research catalog](../../README.md).*
