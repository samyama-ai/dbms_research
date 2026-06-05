# Concurrent B-tree with optimal contention

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/concurrent-btree-contention` · **Status:** partially-solved

## 1. Problem Statement
Concurrent B-trees serialize updates near the same keys, but naive locking (e.g., latching the root or whole root-to-leaf path) makes synchronization cost scale with **tree structure** (height, fan-out, total size) rather than with **actual contention** (the number of operations that truly conflict). The problem: design a concurrent B-tree (or B+/B$^\text{link}$-tree) whose synchronization overhead provably scales with the **conflict graph** of the workload — concurrent, non-conflicting operations should proceed with $O(1)$ contention, while only genuinely conflicting ones pay.

Formally, bound per-operation **contention** (e.g., in the *adaptive* contention or *work-stealing* sense) by a function of overlapping accesses, not $n$ or tree height $h$. Variants:

- **Optimization variant:** minimize total contention / cache-line transfers as a function of the conflict structure.
- **Decision/lower-bound variant:** is there an inherent contention cost any linearizable ordered dictionary must pay?

*Partially solved:* lock-free/optimistic designs (B$^\text{link}$-trees, OLC, Bw-tree) achieve excellent practical scalability and largely localize contention, but a **matching theoretical bound** "synchronization = $\Theta(\text{conflict})$" is not established.

## 2. Mathematical Foundations
Model: **asynchronous shared memory** with linearizability (Herlihy–Wing) as correctness. Cost measured in **CAS/atomic operations**, **cache-coherence traffic** (cache-line transfers in the MESI/contention model), or **step/contention complexity**.

- **B$^\text{link}$-tree** (Lehman–Yao, 1981): right-link pointers + high-keys let readers and writers avoid lock-coupling, so most operations need only a single node latch — a structural decoupling of concurrency from height.
- **Optimistic Lock Coupling (OLC)** and **optimistic latch-free index traversal (OLFIT):** version counters allow read traversal without latches; validation detects conflict — cost proportional to retries, which correlate with actual contention.
- Relevant theory: the **CLRS / Dwork–Herlihy–Waarts** *contention* model lower-bounding atomic-operation hot spots; **universal construction** and the cost of consensus on contended cells.

## 3. State of the Art (SOTA)
- **Theory:** Lehman–Yao B$^\text{link}$-tree correctness; lock-free B-tree constructions; contention lower bounds for shared counters/stacks (Dwork–Herlihy–Waarts; Attiya et al.).
- **Systems:** **Bw-tree** (Microsoft Hekaton/LLAMA, ICDE 2013) — latch-free via delta records + mapping table; **OLC/OLFIT** B-trees; **Masstree** (trie-of-B-trees, EuroSys 2012); **ART** with OLC; in practice these scale near-linearly on modern multicores. Benchmarks (Wang et al., "Building a Bw-Tree Takes More Than Just Buzzwords," SIGMOD 2018) compare contention behavior.

## 4. Upper Bound
B$^\text{link}$-trees and OLC achieve: read-mostly traversals with $O(1)$ latches per node and no coupling, so uncontended operations incur essentially $O(h)$ uncoordinated reads + $O(1)$ writes. Optimistic schemes retry only on real version conflicts, so amortized contention tracks the **conflict rate** empirically. These are strong **systems-SOTA** upper bounds; a clean theorem "contention $= O(\text{conflicts})$ regardless of $n$" holds informally but is not fully formalized for the dynamic ordered-dictionary case.

## 5. Lower Bound
General contention lower bounds: any linearizable implementation of a strongly-non-commutative object (e.g., a counter or queue) has operations that must access a **common contended memory location**, incurring $\Omega(\cdot)$ stalls (Dwork–Herlihy–Waarts 1997; Attiya, Hendler, et al.). For ordered dictionaries, splits/merges that touch shared structural nodes (parent pointers, the root on rebalancing) create unavoidable contention under adversarial split patterns — but **no tight bound** matching the B$^\text{link}$ upper bound exists.

## 6. The Gap
Partially open. Practice strongly suggests synchronization can be made proportional to actual conflict; the **gap** is the missing two-sided theorem in a realistic contention/cache model: (i) an upper bound proving a specific design pays $O(\text{conflicts})$ for *all* workloads including adversarial split cascades, and (ii) a matching lower bound on structural-modification contention. Root/internal-node updates during rebalancing are the crux.

## 7. Current Research (as of June 2026)
- **Optimistic, latch-free** ordered indexes pushed to disaggregated/RDMA and persistent memory; contention under remote memory *(frontier — verify)*.
- **Hardware transactional memory (HTM)** and RCU-based B-trees; analysis of abort rates as a contention proxy *(frontier — verify)*.
- Renewed theory on **contention-adaptive** data structures and the cost of rebalancing under concurrency.
- Groups: CMU DB (Pavlo), Microsoft Research (Bw-tree lineage), TUM (Leis/Neumann, OLC/ART), MIT (Masstree lineage).

## 8. Future Work
- A provable contention-optimal concurrent ordered dictionary with worst-case (including adversarial split) bounds.
- Tight lower bounds for structural-modification contention in B-trees.
- Energy/coherence-traffic models beyond step complexity.

## 9. Key References
- **[Foundational]** P. Lehman, S. B. Yao. *Efficient Locking for Concurrent Operations on B-Trees.* ACM TODS, 1981. — [DOI](https://doi.org/10.1145/319628.319663)
- **[Foundational]** C. Dwork, M. Herlihy, O. Waarts. *Contention in Shared Memory Algorithms.* JACM, 1997. — [DOI](https://doi.org/10.1145/268999.269000)
- **[Foundational]** M. Herlihy, J. Wing. *Linearizability: A Correctness Condition for Concurrent Objects.* ACM TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[SOTA]** J. Levandoski, D. Lomet, S. Sengupta. *The Bw-Tree: A B-tree for New Hardware Platforms.* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544834)
- **[SOTA]** V. Leis, M. Haubenschild, T. Neumann. *Optimistic Lock Coupling.* IEEE Data Eng. Bull., 2019. — [PDF](http://sites.computer.org/debull/A19mar/p73.pdf)
- **[SOTA]** Y. Mao, E. Kohler, R. Morris. *Cache Craftiness for Fast Multicore Key-Value Storage (Masstree).* EuroSys, 2012. — [DOI](https://doi.org/10.1145/2168836.2168855)

## 10. Worked Example

Consider a B$^\text{link}$-tree leaf $L$ holding keys $\{10,20,30\}$ with right-link to $L'$ (high-key $30$). Two threads run concurrently: $T_1$ inserts $25$, $T_2$ looks up $20$.

*Lock-coupling (naive):* both latch root→internal→leaf; $T_2$ blocks on $T_1$'s leaf latch even though $20$ and $25$ don't conflict — synchronization cost scales with height $h=3$.

*OLC / B$^\text{link}$:* $T_2$ reads $L$ optimistically, records version $v=7$, finds $20$, re-validates $v$ still $=7$ at exit — **zero latches, zero stalls**. $T_1$ latches only $L$, bumps $v\to 8$, inserts $25$. The two operations touch the *same node* but are non-conflicting, so contention is $O(1)$, not $\Theta(h)$.

Now suppose $T_1$ instead triggers a split that rewrites the parent: $T_2$ may read stale $L$, but the right-link + high-key let it *follow the link* to find $25$ without restarting from root. Contention appears only on the genuinely shared parent cell — illustrating why the open gap is precisely the adversarial **split-cascade** case where many threads contend on rebalanced internal nodes.

---
*Part of the [DBMS Research catalog](../../README.md).*
