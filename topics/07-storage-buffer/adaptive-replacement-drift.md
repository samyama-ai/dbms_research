---
id: 07-storage-buffer/adaptive-replacement-drift
title: "Optimal Buffer Replacement Under Workload Drift"
topic: 07-storage-buffer
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Optimal Buffer Replacement Under Workload Drift

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/adaptive-replacement-drift` · **Status:** open

## 1. Problem Statement
A database buffer manager holds $k$ pages of a much larger relation/index set in DRAM and must, on each fault, evict one resident page. Classical analysis assumes either an adversarial sequence (online competitive setting) or a *stationary* reuse distribution (each page $p$ has a fixed reuse probability). Real OLTP/HTAP workloads are **non-stationary**: the reuse distribution drifts as hot keys migrate, scans sweep through, and tenants come and go.

The problem: design a replacement policy $\pi$ that, **without manual tuning**, provably tracks a slowly-drifting reuse distribution and stays within a bounded factor of the *best dynamic policy in hindsight* (the policy allowed to re-tune at every step). Variants:
- **Optimization (regret) variant:** minimize cumulative miss rate relative to the best sequence of stationary policies that changes at most $S$ times (switching/tracking regret).
- **Competitive variant:** bound the fault ratio against the offline optimal (Belady) on drifting inputs.
- **Decision variant:** given a drift budget, decide whether a target miss-rate is achievable online.

The tuning-free requirement rules out policies whose parameters (e.g., ARC's target split, LIRS' stack size, 2Q's queue ratios) must be hand-set per workload.

## 2. Mathematical Foundations
Model the request stream as drawn from a time-varying distribution $\{\mathcal{D}_t\}$ over pages with total-variation drift $\sum_t \|\mathcal{D}_{t+1}-\mathcal{D}_t\|_{TV} \le V$ (a *path-length* / variation budget). A policy is a sequence of cache states $C_t \subseteq U$, $|C_t|\le k$.

**Belady's offline optimum (MIN):** evict the page whose next use is farthest in the future; optimal for unit-cost paging.

**Competitive ratio:** $\pi$ is $c$-competitive if $\text{cost}_\pi(\sigma) \le c\cdot\text{OPT}(\sigma) + O(1)$ for all $\sigma$. The deterministic lower bound for paging is $k$; randomized marking achieves $O(\log k)$ (against an oblivious adversary).

**Tracking/shifting regret:** for an experts/online-learning formulation over candidate policies, the relevant bound is dynamic regret $R_T = \sum_t \ell_t(\pi_t) - \min_{u_t}\sum_t \ell_t(u_t)$ with $S$ switches, where Fixed-Share / strongly-adaptive algorithms give $R_T = \tilde O(\sqrt{T(S+1)})$ or $\tilde O(\sqrt{TV})$ under variation $V$.

The open question is whether buffer replacement — which has *state* (the cache contents couple decisions across time, unlike standard prediction-with-experts) — admits comparable variation-dependent guarantees. The coupling makes the loss non-oblivious: today's eviction changes tomorrow's feasible action set.

## 3. State of the Art (SOTA)
**Systems-SOTA:** ARC (Megiddo–Modha, FAST 2003) self-balances recency vs. frequency; LIRS (Jiang–Zhang, SIGMETRICS 2002) uses reuse distance; CAR/CART, 2Q, and LeCaR (Vietri et al., HotStorage 2018) — the last casts the recency-vs-frequency choice as a two-expert online-learning problem with regret-style updates, and CACHEUS (Rodriguez et al., FAST 2021) makes LeCaR adaptive and parameter-light. These are the closest practical embodiments of "tuning-free adaptive."

**Theory-SOTA:** the *online learning with experts* view (LeCaR's basis) inherits Fixed-Share / AdaNormalHedge tracking-regret bounds, but only over a small fixed pool of base policies — not against the full dynamic optimum.

## 4. Upper Bound
For the experts-over-policies formulation with $N$ base policies and $S$ switches, Fixed-Share yields miss-rate regret $\tilde O(\sqrt{T S \log N})$, and variation-bounded mirror descent gives $\tilde O(T^{1/3}V^{2/3})$ against the path-length comparator. For raw paging, randomized marking remains $H_k = O(\log k)$-competitive even on drifting inputs (drift cannot make a marking algorithm worse than the worst case). No upper bound is known that simultaneously is (a) tuning-free, (b) variation-adaptive, and (c) accounts for the stateful coupling.

## 5. Lower Bound
The deterministic competitive ratio is $\ge k$ (folklore, Sleator–Tarjan 1985) and the randomized ratio is $\ge H_k = \Omega(\log k)$ (Fiat et al., 1991) — these hold a fortiori under drift. For tracking regret, $\Omega(\sqrt{TS})$ is information-theoretically necessary in prediction-with-experts (lower bound transfers). No lower bound separates the *stateful* buffer problem from stateless experts, leaving open whether coupling forces strictly worse variation dependence.

## 6. The Gap
There is no matching pair. Upper bounds are either worst-case competitive (ignoring that drift is benign, not adversarial) or experts-regret (ignoring cache-state coupling and competing only against a weak base-policy pool). A satisfying result would be a variation-parameterized bound $f(V,k,T)$ with a matching lower bound, achieved by a parameter-free algorithm. Closing it requires reconciling online-learning regret with the metrical/stateful structure of paging — likely via Metrical Task Systems or online convex optimization with switching costs.

## 7. Current Research (as of June 2026)
- Bridging **online learning and caching** continues from LeCaR/CACHEUS toward provable adaptivity *(frontier — verify)*; groups at UC Santa Cruz (Miller, Paris-Carrillo) and Stony Brook are active on adaptive caching.
- **MTS / online-convex-optimization with switching costs** as a unifying lens (work descending from Bansal, Buchbinder, Naor on the $k$-server/paging duality).
- **Smoothed / beyond-worst-case** analysis of paging treating drift as the smoothing parameter.
- Self-tuning buffer pools in production systems (LeanStore, Umbra) increasingly borrow learned/adaptive eviction *(frontier — verify)*.

## 8. Future Work
Formalize the drift budget that real workloads satisfy (measure $V$ empirically). Prove a tuning-free policy with variation-optimal tracking regret. Extend to non-unit page costs and to write-back (dirty-page) asymmetry. Connect to learned eviction (see `learned-eviction-guarantees`) so predictions handle drift while a fallback preserves competitiveness.

## 9. Key References
- **[Foundational]** D. Sleator, R. Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. — [DOI](https://doi.org/10.1145/2786.2793)
- **[Foundational]** N. Megiddo, D. Modha. *ARC: A Self-Tuning, Low Overhead Replacement Cache.* USENIX FAST, 2003. — [USENIX](https://www.usenix.org/conference/fast-03/arc-self-tuning-low-overhead-replacement-cache)
- **[Foundational]** S. Jiang, X. Zhang. *LIRS: An Efficient Low Inter-reference Recency Set Replacement Policy.* SIGMETRICS, 2002. — [DOI](https://doi.org/10.1145/511334.511340)
- **[SOTA]** G. Vietri et al. *Driving Cache Replacement with ML-based LeCaR.* USENIX HotStorage, 2018. — [USENIX](https://www.usenix.org/conference/hotstorage18/presentation/vietri)
- **[SOTA]** L. Rodriguez et al. *Learning Cache Replacement with CACHEUS.* USENIX FAST, 2021. — [USENIX](https://www.usenix.org/conference/fast21/presentation/rodriguez)
- **[Survey]** N. Cesa-Bianchi, G. Lugosi. *Prediction, Learning, and Games.* Cambridge Univ. Press, 2006. (tracking/shifting regret) — [Cambridge](https://www.cambridge.org/core/books/prediction-learning-and-games/A05C9F6ABC752FAB8954C885D0065C8F)

## 10. Worked Example

Let cache size $k = 2$ over pages $\{A,B,C\}$. The reuse distribution drifts: **phase 1** the stream is hot on $\{A,B\}$ ($\sigma_1 = A\,B\,A\,B$), **phase 2** it shifts to $\{B,C\}$ ($\sigma_2 = C\,B\,C\,B$).

Trace LRU (start with $A,B$ resident):

- Phase 1: $A,B,A,B$ — all hits. Misses: 0.
- Phase 2: $C$ miss (evict LRU $=A$, cache $\{B,C\}$); $B$ hit; $C$ hit; $B$ hit. Misses: 1.

Total misses = 1. Belady (offline) would also keep $\{B,C\}$ across the boundary, also 1 miss — so on this *benign* drift LRU is near-optimal.

Now contrast a frequency-only policy (LFU) that locked $A$ in (count 2 after phase 1): at $C$ it evicts $B$ (count 1) instead, then thrashes $B$ vs $C$ for two more misses. This shows the recency-vs-frequency tension a tuning-free policy must resolve: the drift budget here is $\|\mathcal{D}_2-\mathcal{D}_1\|_{TV} = 0.5$ (mass moved from $A$ to $C$), and tracking it well is exactly what ARC/LeCaR-style adaptivity targets.

---
*Part of the [DBMS Research catalog](../../README.md).*
