---
id: 30-cloud-serverless-db/tenant-buffer-partitioning
title: "Tenant-aware buffer-pool partitioning theory"
topic: 30-cloud-serverless-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Tenant-aware buffer-pool partitioning theory

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/tenant-buffer-partitioning` · **Status:** partially-solved

## 1. Problem Statement

A multi-tenant database (or shared serverless cache) holds a buffer pool of $M$ pages serving $n$ tenants. Tenant $i$ has a **miss-ratio curve (MRC)** $m_i(x)$ — the fraction of accesses that miss when given $x$ pages — and an SLA weight $W_i$ (cost per miss, e.g., latency-penalty or $/IO to remote storage). We must partition (or weight) the cache to minimize SLA-weighted miss cost while respecting per-tenant minimums and fairness.

Variants:
- **Optimization (static):** Choose $x_1,\dots,x_n$ with $\sum x_i = M$ minimizing $\sum_i W_i\,r_i\,m_i(x_i)$ (request rate $r_i$).
- **Decision:** Is there an allocation meeting all tenants' SLA targets simultaneously within $M$?
- **Online/dynamic:** MRCs drift; reallocate without thrashing, possibly under bandit feedback (only realized hit rates observed).
- **Fair variant:** Maximize min weighted utility, or enforce max-min / proportional fairness rather than pure cost.

## 2. Mathematical Foundations

The static problem is **separable resource allocation**: minimize $\sum_i f_i(x_i)$ s.t. $\sum_i x_i = M$, $x_i\ge \ell_i$, where $f_i(x)=W_i r_i m_i(x)$.

The decisive structural fact: empirical MRCs $m_i(x)$ are typically **non-increasing and convex** (diminishing returns — LRU MRCs derived from reuse-distance histograms are convex in the common case). When all $f_i$ are convex, the optimum satisfies an **equimarginal (water-filling) condition**: allocate so marginal miss-cost reductions $-f_i'(x_i)$ are equalized across tenants,
$$ -W_i r_i\, m_i'(x_i) = \mu \quad \forall i \text{ with } x_i>\ell_i. $$
A greedy/marginal-gain or Galil–Megiddo–style algorithm solves the integer convex case exactly in $O(M\log n)$ (priority queue of marginal gains) or via discrete convex (L-natural / **Frank–Wolfe / scaling**) methods.

The complication: real MRCs are **not always convex** (working-set "knees", non-LRU policies). Non-convex separable allocation is the **knapsack-like** territory, solvable in pseudo-polynomial $O(nM)$ by DP but NP-hard to approximate arbitrarily if costs are arbitrary. Reuse-distance theory (Mattson stack distances) underpins MRC estimation; **submodularity** of cache-hit utility under stack-based policies justifies greedy guarantees.

## 3. State of the Art (SOTA)

- **MRC estimation:** **Mattson stack distances** (1970) for exact MRCs; **SHARDS** (Waldspurger et al., FAST 2015) and **AET** (Hu et al., USENIX ATC 2016) for sub-linear, online MRC approximation — the practical enabler.
- **Allocation systems:** Memcached/Redis multi-tenant slabs; **Cliffhanger** (NSDI 2016) hill-climbs per-tenant allocations using gradient estimates; **RobinHood** (OSDI 2018) reallocates cache to the tail-latency-critical tenant. DB buffer-pool sizing in Oracle/SQL Server uses simulation-based advisors.
- **Theory:** Convex separable resource allocation is classical (Ibaraki–Katoh); equimarginal allocation is provably optimal under convexity.

## 4. Upper Bound

Under convex MRCs, the static weighted optimum is found **exactly** in $O(M\log n)$ time (greedy marginal allocation) or $O(n\log(M/n))$ with continuous relaxation + rounding. For non-convex MRCs, DP gives an exact pseudo-polynomial $O(nM)$ solution; with an FPTAS available for the bounded-cost knapsack-structured case. Online, no-regret hill-climbing (Cliffhanger-style) converges to the convex optimum; bandit/gradient methods give $\tilde O(\sqrt{T})$ regret under stationarity.

## 5. Lower Bound

The general (non-convex, arbitrary-cost) tenant allocation is **NP-hard** by reduction from multiple-choice knapsack / partition, so no poly-time exact algorithm unless P=NP, and pseudo-polynomial DP is essentially the best one can hope for absent structure. Online with drifting MRCs inherits **adversarial regret lower bounds** of $\Omega(\sqrt{T})$ (and full reallocation incurs unavoidable migration/thrashing cost, a metrical-task-system $\Omega(\log n)$-style barrier). MRC approximation has an information-theoretic sampling lower bound (you cannot estimate $m_i$ to error $\epsilon$ with fewer than $\Omega(1/\epsilon^2)$-scale samples).

## 6. The Gap

For the **convex** regime the problem is essentially **solved** — upper and lower bounds meet at the equimarginal optimum, hence "partially-solved". The genuine open gaps: (1) **non-convex MRCs** — no clean characterization of when greedy is near-optimal vs. when NP-hardness bites; (2) the **online** setting with non-stationary, correlated tenant behavior and reallocation/thrashing cost has no tight competitive ratio; (3) jointly optimizing cache partition *and* SLA-weighted **remote-storage miss penalties** (coupling to disaggregated I/O pricing) is unstudied formally.

## 7. Current Research (as of June 2026)

Directions: learned MRC predictors feeding allocators; ML-for-systems cache admission (LRB, **GL-Cache**) extended to multi-tenant fairness *(frontier — verify)*; serverless/function caches where tenants appear and vanish, needing online allocation under churn; fairness-aware variants (proportional / max-min weighted utility) studied at CMU (Mor Harchol-Balter's group, RobinHood lineage) and VMware/Broadcom research (SHARDS lineage) *(frontier — verify)*. Cloud DBaaS vendors (Aurora, AlloyDB) explore SLA-weighted buffer sharing across tenants on shared hosts.

## 8. Future Work

- Tight competitive analysis for online reallocation with thrashing cost.
- Characterizing the non-convex MRC regime; structural conditions for greedy optimality.
- Joint cache-partition + remote-miss-pricing optimization.
- Strategy-proof allocation when tenants can misreport access patterns.
- Robust allocation under MRC-estimation uncertainty (distributionally robust).

## 9. Key References

- **[Foundational]** R. L. Mattson, J. Gecsei, D. R. Slutz, I. L. Traiger. *Evaluation techniques for storage hierarchies.* IBM Systems Journal, 1970. — [DOI](https://doi.org/10.1147/sj.92.0078)
- **[SOTA]** C. Waldspurger et al. *Efficient MRC construction with SHARDS.* USENIX FAST, 2015. — [USENIX](https://www.usenix.org/conference/fast15/technical-sessions/presentation/waldspurger)
- **[SOTA]** A. Cidon et al. *Cliffhanger: Scaling Performance Cliffs in Web Memory Caches.* USENIX NSDI, 2016. — [USENIX](https://www.usenix.org/conference/nsdi16/technical-sessions/presentation/cidon)
- **[SOTA]** D. Berger, B. Berg, et al. *RobinHood: Tail Latency Aware Caching.* USENIX OSDI, 2018. — [USENIX](https://www.usenix.org/conference/osdi18/presentation/berger)
- **[Foundational]** T. Ibaraki, N. Katoh. *Resource Allocation Problems: Algorithmic Approaches.* MIT Press, 1988. — [DBLP search](https://dblp.org/search?q=Resource+Allocation+Problems+Algorithmic+Approaches+Ibaraki+Katoh)

## 10. Worked Example

Two tenants share $M = 4$ pages. Their miss-ratio curves $m_i(x)$ (convex, decreasing):

| pages $x$ | $m_A(x)$ | $m_B(x)$ |
|---|---|---|
| 0 | 1.00 | 1.00 |
| 1 | 0.50 | 0.80 |
| 2 | 0.30 | 0.65 |
| 3 | 0.20 | 0.55 |
| 4 | 0.15 | 0.50 |

Weights/rates $W_A r_A = 10$, $W_B r_B = 10$. **Greedy marginal allocation:** start at $x_A=x_B=0$ and repeatedly give the next page to the tenant with the largest marginal miss-cost drop $-W_i r_i\,[m_i(x_i{+}1)-m_i(x_i)]$.

- Page 1: A gains $10(1.00-0.50)=5.0$; B gains $10(1.00-0.80)=2.0$. Give to A → $x_A=1$.
- Page 2: A gains $10(0.50-0.30)=2.0$; B gains $2.0$. Tie; give to A → $x_A=2$.
- Page 3: A gains $10(0.30-0.20)=1.0$; B gains $2.0$. Give to B → $x_B=1$.
- Page 4: A gains $1.0$; B gains $10(0.80-0.65)=1.5$. Give to B → $x_B=2$.

Result $x_A=2, x_B=2$, total weighted miss cost $10(0.30)+10(0.65)=9.5$. Check the equimarginal condition: next marginal gains are A$=1.0$, B$=1.5$ — within one page of equalized, confirming optimality of the integer convex allocation. Any reassignment (e.g. $3/1$) raises cost to $10(0.20)+10(0.80)=10.0$.

---
*Part of the [DBMS Research catalog](../../README.md).*
