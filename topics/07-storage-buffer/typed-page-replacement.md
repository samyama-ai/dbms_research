# Buffer Replacement for Index vs Heap Pages

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/typed-page-replacement` · **Status:** empirically-open

## 1. Problem Statement

A single buffer pool holds pages of **heterogeneous structural roles**: B-tree **internal (root/branch) nodes**, B-tree **leaf nodes**, **heap/data pages**, plus auxiliary pages (free-space maps, visibility maps, undo/version pages). Classical replacement (LRU, CLOCK, LRU-K, ARC) treats all frames *uniformly* — eviction value is inferred only from observed access recency/frequency. But the *structural type* carries strong priors about eviction value:

- A B-tree **root** is touched by *every* index traversal; evicting it is catastrophic, yet its access *frequency* per byte may not stand out under a scan-heavy workload that floods the pool with heap pages.
- An **internal node** caches the navigation cost of a whole subtree; a **leaf** caches one key range; a **heap page** caches a few tuples. Their *miss costs and reuse likelihoods differ systematically*.

**Problem:** should a buffer manager **differentiate eviction value by page type**, and if so, by how much, *provably or measurably*? **Decision variant:** does type-aware weighting strictly improve hit-weighted miss cost over a type-blind policy on a given workload? **Optimization variant:** assign per-type retention priorities (or a per-type partition of the pool) minimizing expected total I/O cost. The status is **empirically-open**: practitioners already special-case index pages, but there is no agreed model of *how much* differentiation is right, nor bounds that say type-blindness is provably suboptimal.

## 2. Mathematical Foundations

The right abstraction is **weighted caching / file caching** (Young's *Landlord*, Cao–Irani's *GreedyDual-Size*): page $p$ has fetch cost $w_p$ and the policy minimizes total weighted miss cost. Here the *weight is type-correlated*: internal nodes have high $w$ because a miss may trigger a chain of dependent misses; heap pages have low $w$. Formally, model a query as a **root-to-leaf path plus a heap fetch**; the *amortized value* of caching an internal node at depth $d$ scales with the size of its subtree ($\propto$ fan-out$^{(\text{height}-d)}$), giving a geometric prior favoring shallow nodes — this is exactly why **pinning the upper B-tree levels** is near-optimal and why LRU-style recency *approximately recovers* it (shallow nodes are hit more often). Key machinery: GreedyDual-Size competitiveness ($k$-competitive deterministic, $O(\log k)$ randomized for weighted caching), **dependent/chained miss cost** (a miss on a leaf is conditioned on its ancestors being resident), and the observation that the access process is **not i.i.d. across types** — internal-node accesses are *derived* from leaf/heap accesses (a Markov-on-paths structure). Submodularity of "subtree coverage" supports greedy retention of high-fan-out nodes.

## 3. State of the Art (SOTA)

**Systems-SOTA:** essentially every production engine already does *ad hoc* type differentiation. PostgreSQL's clock-sweep gives no formal type weight but the upper B-tree levels stay hot via frequency; InnoDB keeps an **adaptive hash index** and effectively pins index roots; **RocksDB** caches index/filter blocks separately with `cache_index_and_filter_blocks` + high-priority pinning of top levels (a explicit two-class scheme). **LeanStore/Umbra** (CIDR'18/'20) use pointer-swizzling so hot inner nodes are resident by construction, sidestepping eviction for the hot upper tree. SQL Server/Oracle keep separate accounting for index vs data. **Theory-SOTA:** there is *no* dedicated competitive theory for "typed" buffer pools; the closest is weighted/file caching (GreedyDual-Size, Landlord) and cost-aware caching, which *can* express type weights but are not specialized to the tree-derived dependency structure. Empirically, ARC/LIRS/CLOCK-Pro improve scan resistance (helping the index-vs-heap-flood case) without an explicit type model.

## 4. Upper Bound

Cast as **weighted caching** with per-type weights, the best-known online guarantees transfer directly: **GreedyDual-Size / Landlord** is $k$-competitive (deterministic) and $O(\log k)$-competitive (randomized) against the offline weighted optimum — and this *already* captures "evict cheap heap pages before expensive index pages" if weights are set to true miss costs. For the special structure (root-to-leaf path dependency), pinning the top $\log_F(\text{pool budget})$ B-tree levels is **provably within a constant factor** of optimal for traversal-dominated workloads, because the expected traversal I/O with the top levels pinned matches the unavoidable leaf+heap fetches up to lower-order terms. No tighter *type-aware* upper bound (beating generic weighted caching by exploiting the Markov-on-paths structure) is known.

## 5. Lower Bound

The weighted-caching lower bounds apply: deterministic online weighted caching is $\ge k$-competitive and randomized $\ge H_k = \Omega(\log k)$ (inherited from paging via Sleator–Tarjan / Fiat et al.), so no type-aware online policy can beat $\Omega(\log k)$ in the worst case. There is, however, **no lower bound proving type-blindness is asymptotically suboptimal** — and that absence is precisely the open scientific question: an adversary can make recency-based LRU *coincide* with the type-optimal policy (shallow nodes are genuinely hotter), so it is unclear whether explicit type information yields more than constant-factor gains in the worst case. The offline *partition-the-pool-by-type* optimization (choose per-type capacities) is NP-hard via reduction from weighted knapsack/partition, but the online competitive separation between typed and type-blind policies is **unresolved** — hence *empirically-open*.

## 6. The Gap

The gap is unusual: it is **not** a missing upper-vs-lower bound (generic weighted caching brackets both), but a missing **separation result**. We do not know whether a *type-aware* policy is provably (asymptotically or by a meaningful constant) better than a well-tuned *type-blind* one, because recency/frequency already implicitly recovers most type structure (hot inner nodes get accessed more). The **empirical** evidence (engines bother to special-case index pages, swizzling helps) suggests a real constant-factor win, but there is no model that (a) quantifies the gain from type information, (b) says when LRU/ARC already captures it, and (c) bounds the cost of mislabeling under workload shift (e.g., a scan that makes a "hot" index suddenly cold). Closing it needs either a provable separation (typed beats blind by factor $> c$ on a realistic access model) or a proof that recency dominates type information up to constants.

## 7. Current Research (as of June 2026)

- **Pointer swizzling / out-of-pool hot trees** (LeanStore, Umbra; TU Munich) effectively making the index-vs-heap question moot for the hottest nodes *(frontier — verify)*.
- **Two-class and priority caches** in LSM/columnar engines (RocksDB index/filter pinning; learned block reuse) generalized toward principled per-type weights *(frontier — verify)*.
- **Learned eviction with type features** — feeding page-type as an input to ML-guided replacement (CMU self-driving DB; CDN learned-cache lineage adapted to DB pages).
- Workload-shift robustness: bounding misclassification cost when type-priors break (scans over indexes, vacuum/compaction).

## 8. Future Work

- A formal separation: prove typed replacement beats type-blind by a quantified factor on a realistic root-to-leaf-plus-heap access model — or prove it cannot.
- Competitive analysis that exploits the *Markov-on-paths* dependency (a miss on a leaf is conditioned on ancestor residency), beyond generic weighted caching.
- Online per-type pool partitioning with bounded reconfiguration cost under drift.
- Extending the typing to MVCC/version pages, free-space maps, and LSM filter blocks within one unified weighted model.
- Empirical benchmarks isolating the marginal value of *type information* over recency/frequency.

## 9. Key References

- **[Foundational]** Pei Cao, Sandy Irani. *Cost-Aware WWW Proxy Caching Algorithms (GreedyDual-Size).* USENIX Symposium on Internet Technologies and Systems, 1997. — [USENIX](https://www.usenix.org/conference/usits-97/cost-aware-www-proxy-caching-algorithms)
- **[Foundational]** Neal E. Young. *On-Line File Caching (Landlord).* Algorithmica, 2002. — [DOI](https://doi.org/10.1007/s00453-001-0124-5)
- **[Foundational]** Elizabeth J. O'Neil, Patrick E. O'Neil, Gerhard Weikum. *The LRU-K Page Replacement Algorithm for Database Disk Buffering.* SIGMOD, 1993. — [DOI](https://doi.org/10.1145/170035.170081)
- **[SOTA]** Viktor Leis, Michael Haubenschild, Alfons Kemper, Thomas Neumann. *LeanStore: In-Memory Data Management Beyond Main Memory.* ICDE, 2018. — [DBLP](https://dblp.org/rec/conf/icde/LeisHK018.html)
- **[SOTA]** Nimrod Megiddo, Dharmendra S. Modha. *ARC: A Self-Tuning, Low Overhead Replacement Cache.* FAST, 2003. — [USENIX](https://www.usenix.org/conference/fast-03/arc-self-tuning-low-overhead-replacement-cache)
- **[Foundational]** Daniel Sleator, Robert Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. — [DOI](https://doi.org/10.1145/2786.2793)
- **[Survey]** Goetz Graefe. *Modern B-Tree Techniques.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000028)

## 10. Worked Example

Take a B-tree with fan-out $F=100$ and height $4$: 1 root, 100 internal nodes, $10^4$ leaves, plus $10^6$ heap pages. Each point lookup touches a root-to-leaf path (4 index pages) then 1 heap page.

**Pinning the top 2 levels** costs $1+100=101$ frames. Every lookup then guarantees the root and its child are resident, so the per-query *forced* I/O drops to the 2 lower index levels + heap = at most 3 misses, versus 5 under a cold cache — and crucially, a heap scan flooding the pool cannot evict those 101 pinned pages.

**Weighted-caching view.** Set fetch weight $w$ by subtree coverage: root covers $10^4$ leaves, an internal node covers $100$. Under GreedyDual-Size, a page's eviction priority is $H + c/w$; with $w_{\text{root}}=10^4 \gg w_{\text{heap}}=1$, the root's credit is enormous, so it is evicted last — recovering the pinning policy automatically. With only $101$ of $\sim10^6$ frames spent, the geometric prior $\propto F^{\,\text{height}-d}$ makes pinning shallow nodes near-optimal.

---
*Part of the [DBMS Research catalog](../../README.md).*
