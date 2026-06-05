# Tight Competitive Ratio for Weighted Caching with Variable Page Sizes

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/weighted-caching-variable-size` · **Status:** partially-solved

## 1. Problem Statement
In **general caching** (a.k.a. the *file caching* or *web caching* problem), each page $p$ has a **size** $w_p \in \mathbb{Z}_{>0}$ and a **fetch cost** $c_p \ge 0$. A cache of capacity $k$ must, on a request to a non-resident page, fetch it (paying $c_p$) and evict a subset whose total size frees room. The goal is to minimize total fetch cost over an online request sequence.

This subsumes a hierarchy of classical models:
- **Paging:** $w_p=c_p=1$.
- **Weighted caching (Cost model):** $w_p=1$, arbitrary $c_p$.
- **Fault model / Bit model:** $c_p$ tied to $w_p$.
- **General caching:** arbitrary $w_p$ *and* arbitrary $c_p$ — the hardest case.

Two cost-accounting conventions exist: the **bit model** (cost $=$ size) and the **fault model** (cost $=1$ per fetch). Variants: decision (achieve cost $\le B$?), optimization (minimize cost), and the offline approximation question (general caching is NP-hard, so offline asks for the best polynomial-time approximation). The headline open question: **what is the exact competitive ratio for online general caching, and the offline approximability?**

## 2. Mathematical Foundations
Let the cache hold pages with $\sum_{p\in C} w_p \le k$. A schedule is feasible if at each request the requested page is resident.

**Competitive ratio** $c$: $\text{ALG}(\sigma)\le c\cdot\text{OPT}(\sigma)+O(1)$. For *weighted caching* ($w_p=1$), the deterministic optimum is exactly $k$ (Chrobak–Karloff–Payne–Vishwanathan via the *primal–dual* / Landlord algorithm, Young), and the randomized optimum is $\Theta(\log k)$ (Bansal–Buchbinder–Naor primal-dual, FOCS 2007/2010).

**LP relaxation and rounding.** General caching has a natural covering/interval LP. The integrality gap and the difficulty of rounding under variable sizes drive both the offline and online gaps. Offline general caching is **NP-hard** (reduction from a packing problem); the best offline approximation is a constant:
$$\text{OPT}_{\text{offline}} \le 4\cdot\text{LP} \quad\text{(Bar-Noy–Bar-Yehuda–Freund–Naor–Schieber, local-ratio)},$$
later improved to a $(2+\epsilon)$ / near-2 approximation via LP rounding (Adamaszek, Czumaj, Englert, Räcke; Chrobak–Woeginger and follow-ups).

**Online via online primal-dual.** The $O(\log k)$ randomized bound for weighted caching extends to general caching with an extra dependence; the exact constant for variable sizes is where the gap lives.

## 3. State of the Art (SOTA)
**Theory-SOTA (online):** randomized $O(\log k)$ for weighted caching (Bansal–Buchbinder–Naor); for **general caching**, online primal-dual gives $O(\log k)$ in the fault model with constant-factor resource augmentation, and $O(\log^2 k)$-type bounds without augmentation in some regimes *(frontier — verify exact constants)*. Deterministic Landlord is $k$-competitive for the cost model.

**Theory-SOTA (offline):** constant-factor approximation; the best published constants are small (around $2$ with $\epsilon$-augmentation; constants without augmentation are larger).

**Systems-SOTA:** GDSF (Greedy-Dual-Size-Frequency) and Greedy-Dual-Size (Cao–Irani, Young's Landlord) are the deployed heuristics in CDNs and tiered DB caches; modern key-value caches (e.g., variable-object caches) use size-aware admission (TinyLFU, S3-FIFO).

## 4. Upper Bound
- Deterministic, cost model (sizes $=1$, weights arbitrary): $k$-competitive (Landlord / Greedy-Dual, Young 1994).
- Randomized weighted caching: $O(\log k)$ (Bansal–Buchbinder–Naor, FOCS 2007).
- General caching online: $O(\log k)$ via online primal-dual **with $O(1)$ resource augmentation** in the fault model; offline $O(1)$-approximation ($\approx 2$ with augmentation).

## 5. Lower Bound
- Deterministic paging $\ge k$; randomized $\ge H_k = \Omega(\log k)$ (Fiat et al. 1991) — these lower-bound all richer models.
- Offline general caching is **NP-hard** (Chrobak–Karloff–Payne–Vishwanathan / via subset-sum-style packing), and APX-hardness arguments constrain how small the offline constant can be.
- No super-logarithmic online lower bound is known beyond $\Omega(\log k)$, so the *online* general-caching constant is the open part.

## 6. The Gap
For **weighted caching** the picture is closed: $\Theta(\log k)$ randomized, exactly $k$ deterministic. For **general caching** (variable size *and* cost) the gap is genuinely open: we have $O(\log k)$ upper bounds that often need $O(1)$ resource augmentation, but no augmentation-free matching bound, and the *exact* offline approximation constant is not pinned down. Closing it means either an augmentation-free $O(\log k)$ randomized online algorithm with a matching lower bound, or proving augmentation is necessary.

## 7. Current Research (as of June 2026)
- Online primal-dual and the **covering-LP / $k$-server** lens continue to drive progress (Bansal, Buchbinder, Naor, Coester, Koutsoupias) *(frontier — verify latest constants)*.
- **Learning-augmented general caching** (predictions for next request, robust+consistent ratios) is very active (Lykouris–Vassilvitskii line, FAST/ICML 2023–2025) and increasingly handles variable sizes.
- Caching-with-**reduced/limited adaptivity** and the connection to the *Allocation/MTS* framework.

## 8. Future Work
Eliminate resource augmentation in online general caching; settle the exact offline approximation constant; tighten learning-augmented bounds (Pareto-optimal consistency/robustness) under variable sizes; bridge to deployed size-aware admission policies with provable guarantees.

## 9. Key References
- **[Foundational]** N. Young. *On-Line File Caching (Landlord).* SODA, 1998 / Algorithmica. — [DOI](https://doi.org/10.1007/s00453-001-0124-5)
- **[Foundational]** P. Cao, S. Irani. *Cost-Aware WWW Proxy Caching Algorithms (GreedyDual-Size).* USENIX Symp. Internet Tech., 1997. — [USENIX](https://www.usenix.org/conference/usits-97/cost-aware-www-proxy-caching-algorithms)
- **[Foundational]** M. Chrobak, H. Karloff, T. Payne, S. Vishwanathan. *New Results on Server Problems.* SIAM J. Discrete Math, 1991. — [DOI](https://doi.org/10.1137/0404017)
- **[SOTA]** N. Bansal, N. Buchbinder, J. Naor. *Randomized Competitive Algorithms for Generalized Caching.* STOC 2008 / SIAM J. Comput. — [DOI](https://doi.org/10.1137/090779000)
- **[SOTA]** A. Adamaszek, A. Czumaj, M. Englert, H. Räcke. *An $O(\log k)$-Competitive Algorithm for Generalized Caching.* SODA 2012. — [DBLP](https://dblp.org/rec/conf/soda/AdamaszekCER12.html)
- **[Survey]** A. Borodin, R. El-Yaniv. *Online Computation and Competitive Analysis.* Cambridge Univ. Press, 1998. — [ACM](https://dl.acm.org/doi/book/10.5555/290169)

## 10. Worked Example

Cache capacity $k=10$. Three pages: $A$ (size $w_A=8$, cost $c_A=8$), $B$ ($w_B=2$, $c_B=2$), $C$ ($w_C=2$, $c_C=10$). Request sequence: $A,B,C,B,A,C$ (bit model, cost = size unless noted; here $C$ is expensive relative to its size).

**Step trace under Landlord / GreedyDual-Size** (evict the page with smallest credit $H+c/w$, decrement others):
- $A$: miss, fetch (cost 8). Cache $\{A\}$, used 8/10.
- $B$: miss, fetch (cost 2). Cache $\{A,B\}$, used 10/10.
- $C$: miss; need 2 units. $A$ has credit $8/8=1$, $B$ has $2/2=1$, but $C$'s value $10/2=5$ is high. Evict $B$ (low credit), fetch $C$ (cost 10). Cache $\{A,C\}$.
- $B$: miss again, evict $A$? $A$ credit $1 < C$ credit $5$, so evict $A$, fetch $B$. Cache $\{C,B\}$.
- $A$: miss, fetch (cost 8) — evict $B$. Cache $\{C,A\}$.
- $C$: **hit** (retained because cost/size $=5$ kept it resident).

The high-$c/w$ page $C$ survives churn; total fetch cost $=8+2+10+2+8=30$, versus a size-blind FIFO that would have re-fetched $C$ (extra $+10$). This shows why weighting by $c/w$, not size alone, matters.

---
*Part of the [DBMS Research catalog](../../README.md).*
