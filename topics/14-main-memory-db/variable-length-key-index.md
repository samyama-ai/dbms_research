---
id: 14-main-memory-db/variable-length-key-index
title: "In-Memory Index for Variable-Length Keys"
topic: 14-main-memory-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# In-Memory Index for Variable-Length Keys

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/variable-length-key-index` · **Status:** open
> **Verification note:** Wormhole's third author is Song Jiang (not "Jin"); corrected in the reference list.

## 1. Problem Statement
Main-memory databases index keys that are often **variable-length strings** of arbitrary length (URLs, identifiers, composite keys). We want an *ordered* in-memory index supporting `lookup`, `insert`, `delete`, `range/scan`, and **prefix queries** (predecessor/successor, all keys with a given prefix), with **worst-case guarantees** that do not degrade with key length or adversarial key distributions, while being cache- and SIMD-friendly on modern CPUs.

The tension: comparison-based balanced trees (red-black, B+-tree) pay $O(\log n)$ *string comparisons*, each up to $O(L)$ for key length $L$, giving $O(L \log n)$ — and pointer chasing kills cache locality. Tries (radix trees) give $O(L)$ traversal independent of $n$ and natural prefix support, but naive tries waste space and suffer poor cache behavior. Variants:
- **Decision/membership** vs. **predecessor** (ordered) — the latter is strictly harder in the cell-probe model.
- **Static** (build once, query) vs. **dynamic** (updates).
- **Worst-case** vs. **expected** under random keys.

We seek the optimal point: $o(L\log n)$-or-better query time, near-information-theoretic space, and prefix-query support with provable bounds.

## 2. Mathematical Foundations
Let $S \subseteq \Sigma^*$ be a set of $n$ keys over alphabet $\Sigma$ (size $\sigma$), with maximum length $L$ and total length $N=\sum_{k\in S}|k|$. Operations are studied in the **word RAM** ($w$-bit words, typically $w=\Theta(\log n)$ or $w = 64$) and the **cell-probe** model (counting only memory accesses). The **predecessor problem** — given $q$, find $\max\{k \in S : k \le q\}$ — is the canonical hardness anchor.

Key structures:
- **Tries / Patricia (radix) trees:** traversal $O(L/\log_\sigma w)$ with path compression; prefix queries are subtree enumerations.
- **van Emde Boas / x-fast/y-fast tries:** predecessor in $O(\log\log U)$ for integer universe $U=2^w$, but require fixing key width.
- **String B-trees** (Ferragina–Grossi): combine B-trees with Patricia tries (blind tries) to get $O(\frac{L}{B} + \log_B n)$ I/Os — the canonical worst-case-optimal external string index, adaptable in-memory.
- **ART** (Adaptive Radix Tree): adaptive node fan-out (4/16/48/256) for space-time balance.

The fundamental lower-bound machinery is the **Pătrașcu–Thorup** predecessor lower bounds, which give tight tradeoffs between space and query time in the cell-probe model.

## 3. State of the Art (SOTA)
- **Systems-SOTA.** **ART — the Adaptive Radix Tree** (Leis, Kemper, Neumann, ICDE 2013) is the de facto main-memory index for variable-length keys: adaptive nodes, path compression, lazy expansion; used in HyPer/DuckDB-style engines. **Masstree** (Mao, Kohler, Morris, EuroSys 2012) is a trie-of-B+-trees concatenating 8-byte key slices, concurrent and cache-aware. **HOT** (Height Optimized Trie, Binna et al., SIGMOD 2018) bounds node fan-out to maximize cache-line utilization and gives strong worst-case height. **Wormhole** (Wu et al., EuroSys 2019) achieves $O(\log L)$ search by combining a trie with a hash table over prefixes.
- **Theory-SOTA.** **String B-tree** (Ferragina, Grossi, JACM 1999) and **blind tries** give worst-case-optimal string predecessor bounds.

## 4. Upper Bound
- **String predecessor (theory):** String B-tree / blind-trie gives $O\!\left(\frac{L}{B} + \log_B n\right)$ I/Os; in the in-memory word-RAM, Wormhole gives expected $O(\log L)$ to locate the target leaf node plus $O(L)$ to confirm, i.e. effectively $O(L + \log L)$ with cache-resident hashing.
- **ART:** worst-case $O(L)$ (independent of $n$) per point operation, space $O(N)$ with small constants via adaptive nodes.
- **HOT:** worst-case height $O(\log_k n)$ with controllable fan-out $k$, bounding cache misses to $O(\log_k n)$.
The best combined bound is essentially $O(L)$ traversal with $O(N)$ space and prefix queries by subtree scan; the open question is shaving the $L$ factor and the $n$-dependence simultaneously.

## 5. Lower Bound
In the **cell-probe / word-RAM** model, **Pătrașcu–Thorup** (STOC 2006; *Time-Space Trade-offs for Predecessor Search*) prove tight predecessor lower bounds: with near-linear space, predecessor search requires $\Omega(\log\log U)$ (equiv. $\Omega(\log_w n)$) probes, and richer space-time tradeoffs are tight. For strings, any index must read enough of the query to distinguish it: an $\Omega(L/w)$ term is unavoidable in the worst case simply to read a length-$L$ query. Membership (hashing) escapes the predecessor bound — $O(1)$ expected — which is why *ordered* prefix queries are strictly harder than point lookup. Comparison-based structures inherit the $\Omega(\log n)$ comparison lower bound, each comparison costing up to $\Theta(L)$.

## 6. The Gap
Practical structures (ART, HOT, Wormhole, Masstree) achieve excellent empirical performance but each makes a different tradeoff and none is *simultaneously* worst-case optimal in time, space-optimal to the information-theoretic bound, fully concurrent, and provably cache-optimal for prefix/range queries. The theoretical optima (Pătrașcu–Thorup, String B-tree) are not realized by a single deployed structure. The gap — closing the distance between the $O(L)$/$O(\log L)$ practical bounds and the $\Omega(L/w + \log_w n)$ cell-probe floor while supporting dynamic updates, concurrency, and prefix scans — is **genuinely open**.

## 7. Current Research (as of June 2026)
Directions: succinct/compressed tries that approach the information-theoretic space bound while keeping $O(L)$ traversal; SIMD- and GPU-accelerated radix structures; learned indexes (RMI/ALEX/PGM-index) extended to string keys with worst-case fallbacks; and concurrency (ROWEX, optimistic lock coupling) for ART/HOT. Groups: TU Munich (Neumann, Leis, Kemper), Innsbruck (Binna/HOT), MIT (learned indexes — Kraska), CWI/DuckDB Labs. Learned string indexes with provable worst-case guarantees are an active 2025-2026 frontier *(frontier — verify)*.

## 8. Future Work
- A single dynamic structure matching Pătrașcu–Thorup time with succinct space and prefix support.
- Provable worst-case bounds for learned string indexes.
- Cache-/SIMD-optimal concurrent radix trees with formal contention analysis.
- Tight bounds for prefix-range counting (not just predecessor).

## 9. Key References
- **[SOTA]** Leis, Kemper, Neumann. *The Adaptive Radix Tree: ARTful Indexing for Main-Memory Databases.* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544812)
- **[SOTA]** Binna, Zangerle, Pichl, Specht, Leis. *HOT: A Height Optimized Trie Index for Main-Memory Database Systems.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196896)
- **[SOTA]** Mao, Kohler, Morris. *Cache Craftiness for Fast Multicore Key-Value Storage (Masstree).* EuroSys, 2012. — [DOI](https://doi.org/10.1145/2168836.2168855)
- **[Foundational]** Ferragina, Grossi. *The String B-tree: A New Data Structure for String Search in External Memory and Its Applications.* JACM, 1999. — [DOI](https://doi.org/10.1145/301970.301973)
- **[Foundational]** Pătrașcu, Thorup. *Time-Space Trade-Offs for Predecessor Search.* STOC, 2006. — [arXiv](https://arxiv.org/abs/cs/0603043)
- **[SOTA]** Wu, Ni, Jiang. *Wormhole: A Fast Ordered Index for In-Memory Data Management.* EuroSys, 2019. — [arXiv](https://arxiv.org/abs/1805.02200)

## 10. Worked Example

Index the strings $S=\{$`"car"`, `"card"`, `"care"`, `"dog"`$\}$ over $\Sigma=\{a..z\}$. Build a Patricia (path-compressed) radix trie:

```
root
 ├─ "ca" ─ "r" ─┬─ ""  → car
 │              ├─ "d" → card
 │              └─ "e" → care
 └─ "dog"        → dog
```

Lookup `"care"` ($L=4$): descend `ca` $\to$ `r` $\to$ branch on `e` — $O(L)$ work, independent of $n$. Contrast a comparison B+-tree: $O(\log n)$ node visits, each a full string compare up to $L$ chars, i.e. $O(L\log n)$.

Prefix query `"car*"`: navigate to the `"r"` node, then enumerate its subtree — returning `{car, card, care}` as a contiguous range scan, the trie's natural advantage.

Lower-bound check: any index must read enough of the $L=4$ query to distinguish it, giving the unavoidable $\Omega(L/w)$ cell-probe term — here trivially small, but it dominates for long URL-style keys. ART realizes this $O(L)$ traversal with adaptive 4/16/48/256-child nodes to keep space at $O(N)$.

---
*Part of the [DBMS Research catalog](../../README.md).*
