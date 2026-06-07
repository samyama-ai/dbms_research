---
id: 07-storage-buffer/delayed-hits-caching
title: "Competitive Caching with Delayed Hits"
topic: 07-storage-buffer
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Competitive Caching with Delayed Hits

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/delayed-hits-caching` · **Status:** partially-solved
> **Verification note:** The Atre et al. delayed-hits paper appeared at ACM SIGCOMM 2020 (not SIGMOD); the §3 venue tag has been corrected accordingly.

## 1. Problem Statement

Classical caching charges a request **one unit (or fixed cost) per miss**. But when fetching a page from the backing store takes latency $Z > 0$ and multiple requests for the *same* page arrive **while a fetch is in flight**, those later requests are neither plain hits nor independent misses: they are **delayed hits** that wait for the outstanding fetch and incur a cost proportional to their remaining wait. The aggregate cost of a burst of $q$ near-simultaneous misses to one page is therefore *not* $q\cdot Z$ and *not* $Z$, but the sum of each request's residual wait — a quantity that depends on **arrival times within the fetch window**.

The problem: design a cache **admission/eviction** policy minimizing total (aggregate-latency) cost under this delayed-hit model, on a cache of $k$ pages, for an online request sequence with per-page fetch latency $Z$ (uniform or page-dependent).

Variants:
- **Decision/offline:** Given the full timed sequence and latencies, is total latency $\le L$? (Offline optimum is *not* Bélády's MIN — MIN is provably suboptimal here.)
- **Online optimization:** minimize competitive ratio against the offline optimum.
- **Variable-latency variant:** $Z_p$ differs per page (tiered/disaggregated backends), coupling delayed hits with weighted caching.

## 2. Mathematical Foundations

Let requests arrive at times $t_1 < t_2 < \dots$. When page $p$ is requested at $t_i$ and absent, a fetch completing at $t_i + Z$ begins (if none is outstanding). A later request at $t_j \in (t_i, t_i+Z)$ for $p$ is a **delayed hit** costing $(t_i + Z) - t_j$. The objective is total latency

$$
\mathrm{Cost} = \sum_{\text{misses } i} Z \;+\; \sum_{\text{delayed hits } j} \big((t_{\text{fetch}(j)} + Z) - t_j\big),
$$

so caching decisions affect cost **across requests coupled in time** — eviction value depends not on a single future reuse (as in MIN) but on the *temporal density* of future reuses relative to $Z$. This breaks the **independence assumption** underlying paging's potential-function analyses and the optimality of Bélády's MIN. Key parameter: $Z$ measured in **inter-arrival units** — as $Z\to 0$ the model collapses to classical paging; as $Z\to\infty$ bursts dominate. The structure connects to **scheduling with release times**, **online caching with delays/rent-or-buy**, and **batched/aggregated request** models.

## 3. State of the Art (SOTA)

**Systems-SOTA.** The phenomenon was named and quantified by **Atre, Sherry, Wang, Berger — "Caching with Delayed Hits"** (SIGCOMM 2020), who showed delayed hits dominate latency in high-bandwidth CDN/edge caches (where $Z \gg$ inter-arrival time) and proposed **MAD (Minimum-Aggregate-Delay)**, a delay-aware ranking policy with strong empirical gains over LRU/Bélády-style policies. Production CDN and RDMA/disaggregated-memory caches face exactly this regime.

**Theory-SOTA.** Subsequent work formalized competitive analysis: **Zhang, Berger et al.** and follow-ups gave offline structural results and online algorithms; the offline problem's hardness and approximability, and tight online ratios as a function of $Z$ and $k$, were partially characterized — hence **partially-solved**. *(frontier — verify)* for the exact best-known ratios in the latest variants.

## 4. Upper Bound

- **Offline:** the optimum departs from Bélády; offline delayed-hit caching admits polynomial structural characterizations and approximation/exact DP in special cases (uniform $Z$), with constant-factor approximations for the general timed objective. *(frontier — verify)*
- **Online:** delay-aware policies (MAD and descendants) are analyzed with competitive ratios that **degrade gracefully with $Z$** — recovering the classical $\Theta(k)$ deterministic / $\Theta(\log k)$ randomized paging bounds as $Z\to 0$, and incurring an additional factor that grows with the latency-to-inter-arrival ratio. Best-known online ratios are stated in the **online caching model with fetch latency**. *(frontier — verify)* for exact constants.

## 5. Lower Bound

- All classical paging lower bounds apply as a floor (the $Z\to 0$ limit *is* paging): deterministic $\Omega(k)$, randomized $\Omega(\log k)$ (Fiat, Karp, Luby, McGeoch, Sleator, Young).
- The delayed-hit coupling **strictly increases** the achievable lower bound: there exist timed instances where any online policy pays $\Omega(Z)$-scaled extra cost an offline optimum avoids, giving a competitive lower bound that **grows with the latency-to-inter-arrival ratio** — proven via adversarial burst constructions. *(frontier — verify)* for the precise dependence.
- No NP-hardness for the uniform-$Z$ offline case is established as folklore; the **variable-latency** (weighted) variant inherits **general-caching NP-hardness**.

## 6. The Gap

This is **partially-solved**: the model is formalized, the offline optimum's divergence from Bélády is understood, and online policies with latency-dependent competitive ratios exist with matching adversarial lower bounds in limiting regimes. The remaining gaps: (i) a **tight** online competitive ratio as a *joint* function of $k$ and $Z$ (current upper and lower bounds do not meet for intermediate $Z$); (ii) **per-page variable latency** $Z_p$ unifying delayed hits with weighted/general caching, where neither side is tight; (iii) **randomized and learning-augmented** delayed-hit policies with consistency/robustness guarantees. Closing it requires matching upper/lower bounds across the full $(k, Z)$ regime.

## 7. Current Research (as of June 2026)

- **Disaggregated / far-memory caching:** CXL and RDMA backends make $Z \gg$ inter-arrival, putting delayed hits at the center of buffer-pool design. *(frontier — verify)*
- **Learning-augmented delayed-hit caching:** combining predicted reuse with delay-aware fallback to get consistency + robustness. *(frontier — verify)*
- **Variable- and stochastic-latency** extensions, and connections to **online-with-delay / rent-or-buy** scheduling theory (Azar, Touitou lineage). *(frontier — verify)*

## 8. Future Work

- Tight competitive ratio parameterized by both $k$ and latency $Z$ (close the intermediate-regime gap).
- Unified theory of delayed hits + weighted/general caching for tiered backends with per-page $Z_p$.
- Randomized and prediction-augmented delayed-hit policies with provable guarantees.
- Empirical-to-theory bridge: validate worst-case-optimal policies against real CDN/disaggregated-memory traces.

## 9. Key References

- **[Foundational/SOTA]** Atre, Sherry, Wang, Berger. *Caching with Delayed Hits.* ACM SIGCOMM, 2020. — [DOI](https://doi.org/10.1145/3387514.3405883)
- **[Foundational]** Belady. *A Study of Replacement Algorithms for a Virtual-Storage Computer (MIN).* IBM Systems Journal, 1966. — [DOI](https://doi.org/10.1147/sj.52.0078)
- **[Foundational]** Sleator, Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. — [DOI](https://doi.org/10.1145/2786.2793)
- **[Foundational]** Fiat, Karp, Luby, McGeoch, Sleator, Young. *Competitive Paging Algorithms.* Journal of Algorithms, 1991. — [arXiv](https://arxiv.org/abs/cs/0205038)
- **[SOTA]** Bansal, Buchbinder, Naor. *A Primal-Dual Randomized Algorithm for Weighted Paging.* JACM, 2012. — [DOI](https://doi.org/10.1145/2339123.2339126)
- **[Survey]** Lykouris, Vassilvitskii. *Competitive Caching with Machine Learned Advice.* JACM, 2021. — [DOI](https://doi.org/10.1145/3447579)

## 10. Worked Example

Fetch latency $Z = 10$ time units. Page $p$ (not cached) is requested at times $t = 0, 3, 7$.

- $t=0$: miss for $p$; a fetch is launched, completing at $t = 0 + Z = 10$. Cost $= Z = 10$.
- $t=3$: $p$ still in flight (arrives at $10$). This is a **delayed hit**, costing the residual wait $10 - 3 = 7$.
- $t=7$: again in flight. Delayed hit, cost $10 - 7 = 3$.

Aggregate latency $= 10 + 7 + 3 = 20$.

Contrast the two naive models. Treating all three as **independent misses** predicts $3Z = 30$ (overcount — only one fetch actually runs). Treating the burst as **one miss** predicts $Z = 10$ (undercount — it ignores the queued waits). The true cost $20$ lies strictly between, and depends on *arrival times within the window*. This is why Bélády's MIN is suboptimal: MIN minimizes the miss count, but here eviction value hinges on temporal density — clustering reuses inside one $Z$-window is cheaper than spreading them, something a miss-count objective cannot see.

---
*Part of the [DBMS Research catalog](../../README.md).*
