---
id: 07-storage-buffer/compression-aware-buffering
title: "Compression-Aware Buffer Accounting"
topic: 07-storage-buffer
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Compression-Aware Buffer Accounting

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/compression-aware-buffering` · **Status:** empirically-open

## 1. Problem Statement

Classical buffer management assumes uniform-size frames: a pool of $C$ frames holds $C$ pages. When pages are stored compressed in memory (or kept in both compressed and decompressed forms), the **effective capacity** depends on data: a page $p$ occupies $s_p = B / r_p$ bytes where $r_p$ is its compression ratio. The pool holds a **variable, content-dependent number of pages**, and admitting a poorly-compressing page evicts more well-compressing pages.

The problem: design a replacement/admission policy over a byte-budget $M$ (not a frame count) that minimizes miss-induced I/O, given per-page sizes that (a) vary across pages and (b) can change when a page is updated or recompressed.

Variants:
- **Decision/offline:** size-aware caching — given the request sequence and sizes, is total miss cost $\le k$?
- **Online:** competitive policy without future knowledge.
- **Two-form variant:** decide *per page* whether to keep it compressed (small, CPU cost on access) or decompressed (large, fast), a knapsack-with-access-cost over the byte budget.

## 2. Mathematical Foundations

This is **weighted caching with size** — the **general(ized) caching / file caching** problem: items have size $s_p$ and fetch cost $c_p$, cache capacity $M$ bytes, minimize total fetch cost. Special cases: the **Bit model** ($c_p = s_p$), **Fault model** ($c_p = 1$), and **General model** (arbitrary $c_p$). Offline general caching is **NP-hard**; with an $O(1)$ resource-augmentation it admits an LP-rounding $O(1)$-approximation (**Bar-Noy et al.; Albers, Arora, Khanna**).

Online competitiveness is bounded below by $k = M/\min_p s_p$ for deterministic policies (the size-1 paging bound generalizes). Let $h_t$ be the budget under a fractional relaxation; the **primal-dual** framework gives $O(\log k)$-competitive randomized algorithms for weighted/file caching (**Bansal, Buchbinder, Naor**).

With recompression, sizes are time-varying: $s_p(t)$ is revealed on touch, making this an **online problem with stochastic, endogenous item sizes** — outside the clean general-caching model, since admitting $p$ changes future $s_p$.

## 3. State of the Art (SOTA)

**Theory-SOTA.** Online weighted/general caching: $O(\log k)$-competitive randomized (Bansal–Buchbinder–Naor, primal-dual, STOC/JACM 2012); $k$-competitive deterministic via LANDLORD (**Young, 1998/2002**) and GreedyDual-Size (**Cao–Irani, 1997**), which directly handle size+cost.

**Systems-SOTA.** Buffer pools that store compressed pages: **DB2 with adaptive compression**, **SQL Server columnstore**, **LeanStore/Umbra** (variable-size pages, pointer swizzling), and **redis/CDN object caches** using GreedyDual-Size-Frequency (GDSF). RocksDB/InnoDB keep a compressed + uncompressed LRU split. No system provides a competitive guarantee under content-dependent capacity; accounting is heuristic (e.g., reserve by average ratio).

## 4. Upper Bound

Offline: $O(1)$-approximation with $(1+\epsilon)$ cache augmentation for general caching (LP rounding, Bar-Noy et al. 2001 / Albers–Arora–Khanna 1999). Online: LANDLORD / GreedyDual-Size is $k$-competitive deterministic ($k = M/\min s_p$); randomized primal-dual is $O(\log k)$-competitive — both in the **standard online file-caching model with fixed sizes**. These transfer to compression-aware buffering only when ratios are static.

## 5. Lower Bound

- **Offline general caching is NP-hard** (reduction from partition/knapsack-flavored packing); no FPTAS unless P=NP for the general model.
- **Online deterministic:** $k$-competitive is tight; no deterministic policy beats $k = M/\min_p s_p$ (adversary on smallest items, paging lower bound).
- **Online randomized:** $\Omega(\log k)$ lower bound inherited from paging (Fiat et al.).
- The **time-varying-size / two-form** variant has **no known competitive lower bound matching an algorithm** — it is the empirically-open core.

## 6. The Gap

For *static* sizes the picture is essentially tight ($\Theta(\log k)$ randomized, $\Theta(k)$ deterministic). The open gap is the **endogenous, content-dependent capacity**: when admitting a page changes the realizable byte budget and recompression alters $s_p(t)$, no model cleanly captures it and **no policy has a proven competitive ratio**. Hence status *empirically-open* — systems show wins, theory lacks a matching model. Closing it needs a formalization of "caching with state-dependent capacity" plus matching bounds.

## 7. Current Research (as of June 2026)

- **Variable-size buffer managers:** LeanStore/Umbra (Leis, Neumann, TUM) variable-page work; integrating compression into the same byte-budgeted pool. *(frontier — verify)* on competitive analysis for swizzled variable pages.
- **Learning-augmented caching:** ML predictions with robustness/consistency bounds (Lykouris–Vassilvitskii line) extended to sized items. *(frontier — verify)*
- **Compute-vs-capacity trade-off:** keeping pages compressed to fit more vs. decompression CPU under CXL/near-data decompression. *(frontier — verify)*

## 8. Future Work

- A formal "caching with content-dependent capacity" model and tight competitive bounds.
- Online two-form (compressed/decompressed) management as knapsack-over-time with guarantees.
- Recompression-cost-aware eviction (amortize the cost of changing a page's size).
- Robust learning-augmented byte-budget caching with consistency/robustness trade-off.

## 9. Key References

- **[Foundational]** Cao, Irani. *Cost-Aware WWW Proxy Caching Algorithms (GreedyDual-Size).* USENIX Symp. on Internet Technologies and Systems, 1997. — [USENIX](https://www.usenix.org/conference/usits-97/cost-aware-www-proxy-caching-algorithms)
- **[Foundational]** Young. *On-Line File Caching (LANDLORD).* Algorithmica, 2002. — [DOI](https://doi.org/10.1007/s00453-001-0124-5)
- **[SOTA]** Bansal, Buchbinder, Naor. *A Primal-Dual Randomized Algorithm for Weighted Paging.* JACM, 2012. — [DOI](https://doi.org/10.1145/2339123.2339126)
- **[Foundational]** Albers, Arora, Khanna. *Page Replacement for General Caching Problems.* SODA, 1999. — [ACM](https://dl.acm.org/doi/10.5555/314500.314528)
- **[SOTA]** Leis, Haubenschild, Alhomssi, Neumann. *LeanStore: In-Memory Data Management Beyond Main Memory.* ICDE, 2018. — [DBLP](https://dblp.uni-trier.de/rec/conf/icde/LeisHK018.html)
- **[Survey]** Lykouris, Vassilvitskii. *Competitive Caching with Machine Learned Advice.* JACM, 2021. — [DOI](https://doi.org/10.1145/3447579)

## 10. Worked Example

Byte budget $M = 10$ KB. Uncompressed page size $B = 4$ KB. Three pages compress differently:
$p_1$ ($r=4 \Rightarrow s_1 = 1$ KB), $p_2$ ($r=2 \Rightarrow s_2 = 2$ KB), $p_3$ ($r=1 \Rightarrow s_3 = 4$ KB, incompressible). Fetch cost $c_p = 1$ (fault model).

Request stream: $p_1, p_2, p_3, p_1, p_2$. Start empty.

- $p_1$ miss: cache $\{p_1\}$, used $1$ KB.
- $p_2$ miss: cache $\{p_1,p_2\}$, used $3$ KB.
- $p_3$ miss: used would be $7$ KB $\le 10$ — fits, cache $\{p_1,p_2,p_3\}$, used $7$ KB.
- $p_1$ hit, $p_2$ hit. Total misses $= 3$.

Contrast a frame-count pool sized to $\lfloor M/B \rfloor = 2$ frames: it holds only 2 pages, evicting $p_1$ before its reuse and paying $4$ misses. GreedyDual-Size keys eviction on $H = \text{clock} + c_p/s_p$, so the cheap-to-evict bulky $p_3$ ($c/s = 0.25$) loses to $p_1$ ($c/s = 1$) — exactly the content-dependent capacity win. Here the worst-case bound is $k = M/\min_p s_p = 10/1 = 10$.

---
*Part of the [DBMS Research catalog](../../README.md).*
