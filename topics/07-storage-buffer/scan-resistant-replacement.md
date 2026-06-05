# Scan-Resistant Replacement with Optimality Bounds

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/scan-resistant-replacement` · **Status:** partially-solved

## 1. Problem Statement
A pure-LRU buffer pool suffers **sequential flooding**: a large one-shot scan (e.g. a full table scan touching $n \gg k$ pages once) evicts the entire hot working set, even though the scanned pages will never be reused. A scan-resistant replacement policy must **immunize the cache against single-use floods** while retaining near-LRU hit rate on workloads with genuine reuse (loops, hot tuples, index roots). The design tension: distinguishing "this page will be reused soon" from "this is a one-shot scan page" online, without future knowledge.

Variants:
- **Decision/feasibility:** Does a policy exist that is simultaneously (a) immune to flooding (a scan of any length cannot evict a page accessed $\ge 2$ times within a window) and (b) $O(1)$-competitive with OPT on reuse-heavy traces?
- **Optimization:** Maximize hit rate (minimize misses) over a trace mixing scans and reuse.
- **Online (the real one):** All of the above with no lookahead.

## 2. Mathematical Foundations
Replacement is the **paging/caching** problem: cache size $k$, request sequence over pages; minimize misses. Bélády's MIN (evict the page used farthest in the future) is the **offline optimum**. Online, LRU is $k$-competitive and this is optimal for deterministic policies; randomized MARK / equitable policies achieve $O(\log k)$ (Fiat et al.; Achlioptas–Chrobak–Noga). Scan resistance is formalized via the notion of **reuse distance / stack distance**: a one-shot scan has unbounded reuse distance, so any policy that prioritizes recency-of-*second*-reference (correlated reference) over recency-of-first naturally resists it.

Key structural idea: maintain frequency/recency state so that single-reference pages occupy a *probationary* region of bounded size. LRU-K orders by the time of the $K$-th-most-recent reference, formally tracking the backward $K$-distance $b_t(p)$. ARC partitions the cache into recency list $T_1$ and frequency list $T_2$ with a self-tuning split, maintaining ghost lists $B_1,B_2$; its adaptation provably tracks the better of LRU/LFU within the workload. CLOCK-Pro approximates LRU-2 with $O(1)$ amortized ops via reuse-distance classification (hot/cold/test).

## 3. State of the Art (SOTA)
- **LRU-K** (O'Neil, O'Neil, Weikert, SIGMOD 1993) — the foundational scan-resistant policy; LRU-2 is the practical sweet spot.
- **2Q** (Johnson, Shasha, VLDB 1994) — A1in/A1out/Am queues, constant-time, scan-resistant.
- **ARC** (Megiddo, Modha, FAST 2003) — adaptive, self-tuning, scan-resistant; widely deployed (ZFS, PostgreSQL-influenced). Provably within a constant factor of OPT on its model and adapts online.
- **CLOCK-Pro** (Jiang, Chen, Zhang, USENIX ATC 2005) — reuse-distance CLOCK approximation, low overhead.
- **LIRS** (Jiang, Zhang, SIGMETRICS 2002) — low inter-reference recency set; strong scan/loop resistance. *LIRS2* (2021) addresses LIRS's weak spots.
- **Learned:** *LeCaR* (Vietri et al., HotStorage 2018) and *CACHEUS* (Rodriguez et al., FAST 2021) use reinforcement learning to combine experts (recency vs frequency), achieving scan resistance adaptively.

## 4. Upper Bound
Deterministic online: LRU and all the above are $k$-competitive (the optimal deterministic competitive ratio for paging). Randomized: MARK-type policies are $2H_k = O(\log k)$-competitive, and this is tight. Scan-resistant policies (LRU-K, ARC, LIRS) match the $k$-competitive bound **and** additionally guarantee that a scan of length $L$ evicts at most the probationary region (bounded, workload-independent), so steady-state hot pages survive arbitrary-length scans — a property plain LRU lacks. ARC is provably within a constant factor of the offline optimal *fixed* partition between recency and frequency.

## 5. Lower Bound
No deterministic online policy can be better than $k$-competitive (classic adversary: request the one page just evicted). No randomized policy beats $H_k = \Omega(\log k)$ (Fiat–Karp–Luby–McGeoch–Sleator–Young lower bound). These hold against **any** policy, scan-resistant or not — so scan resistance buys robustness, not a better worst-case competitive ratio. Information-theoretically, without lookahead a policy *cannot* always distinguish a one-shot scan page from the first reference of a soon-reused page (they are indistinguishable until the second reference), so some single-use admission is unavoidable.

## 6. The Gap
This is **partially solved**: the worst-case competitive theory is closed ($\Theta(k)$ det., $\Theta(\log k)$ rand.), and practical policies (ARC, LIRS, CACHEUS) deliver near-optimal hit rates with provable flood immunity. The remaining gap is *characterizing optimality on structured (non-adversarial) workloads*: there is no tight, workload-parameterized bound saying "policy X is within $1+\epsilon$ of OPT for traces with reuse-distance distribution $D$." Learned policies empirically dominate but lack such guarantees. Closing it means a **beyond-worst-case / instance-optimal** theory for caching with scans.

## 7. Current Research (as of June 2026)
- **Instance-optimal / learning-augmented caching**: caching with ML predictions (Lykouris–Vassilvitskii line) giving consistency+robustness bounds; extending these to scan-aware predictors *(frontier — verify)*.
- RL-based and lightweight learned admission (CACHEUS successors) tuned for mixed OLTP/scan workloads *(frontier — verify)*.
- Reviving LIRS2 and Sieve (NSDI 2024) — simple, scan-resistant FIFO-with-reinsertion policies competitive with LRU-family at lower cost.
- Groups: Ohio State (Zhang/Jiang lineage), IBM Research (Modha), Emory/UChicago (Yang on Sieve/cache simulation), Google/Meta caching teams.

## 8. Future Work
- Tight instance-optimal bounds parameterized by reuse-distance distributions.
- Combining learned predictions with provable robustness against adversarial scans.
- Scan resistance for compressed/heterogeneous buffer pools (interacts with recompression and NVM tiers).
- Standard scan-heavy benchmarks separating flood-immunity from raw hit rate.

## 9. Key References
- **[Foundational]** O'Neil, O'Neil, Weikert. *The LRU-K Page Replacement Algorithm for Database Disk Buffering.* SIGMOD, 1993. — [DOI](https://doi.org/10.1145/170035.170081)
- **[Foundational]** Megiddo, Modha. *ARC: A Self-Tuning, Low Overhead Replacement Cache.* FAST, 2003. — [USENIX](https://www.usenix.org/conference/fast-03/arc-self-tuning-low-overhead-replacement-cache)
- **[SOTA]** Jiang, Zhang. *LIRS: An Efficient Low Inter-Reference Recency Set Replacement Policy.* SIGMETRICS, 2002. — [DOI](https://doi.org/10.1145/511334.511340)
- **[SOTA]** Rodriguez, Vietri, et al. *Learning Cache Replacement with CACHEUS.* FAST, 2021. — [USENIX](https://www.usenix.org/conference/fast21/presentation/rodriguez)
- **[SOTA]** Yang, Zhang, et al. *FIFO Queues Are All You Need for Cache Eviction (SIEVE).* SOSP/NSDI, 2024. — [USENIX](https://www.usenix.org/conference/nsdi24/presentation/zhang-yazhuo)
- **[Foundational]** Fiat, Karp, Luby, McGeoch, Sleator, Young. *Competitive Paging Algorithms.* J. Algorithms, 1991. — [arXiv](https://arxiv.org/abs/cs/0205038)
- **[Survey]** Lykouris, Vassilvitskii. *Competitive Caching with Machine Learned Advice.* ICML/JACM, 2018/2021. — [DOI](https://doi.org/10.1145/3447579)

## 10. Worked Example

Cache size $k=3$. Hot working set $\{A,B,C\}$ is accessed repeatedly; then a one-shot scan touches $S_1,S_2,S_3,S_4$ (each once, never reused).

Trace: $A,B,C,A,B,C,\;S_1,S_2,S_3,S_4,\;A,B,C$.

**Plain LRU.** After the loop, cache is $[C,B,A]$ (MRU→LRU). The scan evicts the entire hot set: $S_1$ evicts $A$, $S_2$ evicts $B$, $S_3$ evicts $C$, $S_4$ evicts $S_1$. Final cache $\{S_4,S_3,S_2\}$. The closing $A,B,C$ are all **misses**: 3 extra misses from flooding.

**LRU-2 (scan-resistant).** It evicts by the time of the *2nd*-most-recent reference; the singly-referenced scan pages have backward-2 distance $=\infty$, so they sit in a probationary slot and are evicted first. $A,B,C$ (each referenced $\ge 2$ times) survive every scan page. Closing $A,B,C$ are all **hits**.

Flood immunity saves $3$ misses here; on a scan of length $L\gg k$ it saves up to $k$ hot pages regardless of $L$.

---
*Part of the [DBMS Research catalog](../../README.md).*
