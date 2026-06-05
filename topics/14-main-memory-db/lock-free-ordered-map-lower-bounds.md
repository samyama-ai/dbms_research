# Lower Bounds for Lock-Free Ordered Maps

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/lock-free-ordered-map-lower-bounds` · **Status:** open

## 1. Problem Statement
A main-memory database's index is a concurrent ordered map supporting `get`, `insert`, `delete`, `predecessor`, and **consistent range scan** (a scan that returns a linearizable snapshot of the keys in $[a,b]$). The question is to establish **tight time and space lower bounds** for *linearizable, lock-free* implementations of such a map when range scans must be consistent.

Concretely: (decision/cost variant) *What is the minimum worst-case number of remote-memory references (RMRs), or the minimum number of expensive synchronization primitives (CAS/fetch-add) per operation, that any lock-free linearizable ordered map with consistent range scans must incur?* (space variant) *What is the minimum extra space (versioning/epoch metadata) needed so that a range scan of $k$ keys is consistent without blocking writers?* The difficulty is that consistency of a multi-key scan seems to force coordination with concurrent single-key updates, which collides with the lock-freedom progress requirement.

## 2. Mathematical Foundations
We work in the **asynchronous shared-memory model** with atomic read/write, CAS, and `fetch-&-φ` primitives. **Linearizability** (Herlihy–Wing 1990) is the correctness condition; **lock-freedom** is the progress condition (some operation always completes in a finite number of steps system-wide); **wait-freedom** is the stronger per-operation guarantee.

Lower-bound machinery:
- **Consensus number / universality** (Herlihy 1991): objects are ranked by the number of processes among which they solve wait-free consensus; CAS has consensus number $\infty$.
- **RMR complexity** in the CC/DSM models for measuring cache-coherence traffic.
- **Covering arguments** and **information-theoretic / indistinguishability** arguments à la Attiya–Hendler–Woelfel give per-operation step lower bounds.
- The **"perturbation"/influence lower bound** (Attiya et al.) shows expensive synchronization (atomic operations or memory barriers, RAW/AWAR patterns) is *necessary* for any linearizable implementation of objects whose operations are not commutative — formalized by Attiya, Guerraoui, Hendler, Kuznetsov, Michael, Vechev, *Laws of Order* (POPL 2011): every linearizable strongly-non-commutative method must use a RAW or AWAR pattern, i.e. at least one fence/atomic.

A range scan returning a snapshot over $[a,b]$ is *strongly non-commutative* with inserts/deletes in that interval, which is the lever for lower bounds.

## 3. State of the Art (SOTA)
- **Upper-bound systems/structures:** lock-free skip lists (Fraser 2004; Herlihy–Shavit), the **Bw-tree** (Levandoski et al., ICDE 2013), **lock-free B+-tree** variants, and **EBR/RCU/epoch** schemes provide practical consistent scans. Snapshot-supporting structures: **KiWi** (Basin et al., PPoPP 2017) gives lock-free maps with linearizable atomic scans; **vCAS / version lists** (Wei, Ben-David, Blelloch, et al., PPoPP 2021) give wait-free snapshots with constant-overhead reads.
- **Theory-SOTA:** *Laws of Order* (POPL 2011) and Attiya–Hendler–Woelfel-type RMR bounds are the strongest general lower bounds; matching tight bounds *specifically for ordered maps with range scans* remain incomplete.

## 4. Upper Bound
Best constructions: KiWi achieves lock-free `put`/`get` with linearizable scans at $O(\log N)$ expected work per operation and scans proportional to range size; version-list / vCAS techniques (PPoPP 2021) give **wait-free** range scans with $O(1)$ amortized overhead on the update path and $O(k + \log N)$ scan cost, using $O(1)$ extra words per version. These show consistent scans are achievable without sacrificing lock-freedom of updates, at the cost of versioning space.

## 5. Lower Bound
*Laws of Order* (Attiya et al., POPL 2011) proves any linearizable implementation of a strongly-non-commutative operation — which a consistent range scan over a mutable interval is — must execute a memory barrier or atomic (RAW/AWAR) pattern; thus $\Omega(1)$ fences per such operation are unavoidable, ruling out fence-free linearizable scans. RMR lower bounds (Attiya–Hendler–Woelfel; Fan–Lynch) give $\Omega(\log N / \log\log N)$ style bounds for related synchronization. No bound, however, is known to be *tight* against the KiWi/vCAS upper bounds for the combined insert+delete+range-scan signature.

## 6. The Gap
The general non-commutativity bound ($\Omega(1)$ fence) is far below the $O(\log N)$ + versioning-space cost of the best constructions. It is **open** whether range-scan consistency forces super-constant per-update overhead, or whether the vCAS-style $O(1)$ amortized overhead is provably optimal, and what the minimum *space* for snapshot metadata is. Closing it needs an ordered-map-specific lower bound that accounts for both the multi-key scan and the unbounded key space.

## 7. Current Research (as of June 2026)
Directions: (i) tight space lower bounds for versioned snapshots *(frontier — verify)*; (ii) extending vCAS wait-free snapshot reads to multi-dimensional and interval scans; (iii) "history-bounded" lower bounds tying scan cost to concurrency degree. Groups: CMU (Blelloch, Ben-David), Technion (Petrank, Basin/Bortnikov), Tel Aviv (Attiya), Calgary/MPI (Woelfel).

## 8. Future Work
- A provably tight per-operation and per-byte lower bound for lock-free ordered maps with consistent scans.
- Separating lock-free vs wait-free *cost* (not just feasibility) for range scans.
- Bounds parameterized by interval width and contention.

## 9. Key References
- **[Foundational]** Herlihy, M., Wing, J. *Linearizability: A Correctness Condition for Concurrent Objects.* TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[Foundational]** Herlihy, M. *Wait-Free Synchronization.* TOPLAS, 1991. — [DOI](https://doi.org/10.1145/114005.102808)
- **[SOTA]** Attiya, H., Guerraoui, R., Hendler, D., Kuznetsov, P., Michael, M., Vechev, M. *Laws of Order: Expensive Synchronization in Concurrent Algorithms Cannot Be Eliminated.* POPL, 2011. — [DOI](https://doi.org/10.1145/1925844.1926442)
- **[SOTA]** Basin, D., et al. *KiWi: A Key-Value Map for Scalable Real-Time Analytics.* PPoPP, 2017. — [DOI](https://doi.org/10.1145/3018743.3018761)
- **[SOTA]** Wei, Y., Ben-David, N., Blelloch, G., et al. *Constant-Time Snapshots with Applications to Concurrent Data Structures.* PPoPP, 2021. — [arXiv](https://arxiv.org/abs/2007.02372)
- **[SOTA]** Levandoski, J., Lomet, D., Sengupta, S. *The Bw-Tree: A B-tree for New Hardware Platforms.* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544834)

## 10. Worked Example

**Why a consistent scan is strongly non-commutative.** Map holds $\{1{\to}a,\ 3{\to}c\}$. Two operations race: a scan $S=\texttt{range}[1,3]$ and an insert $I=\texttt{put}(2,b)$.

Consider the two linearization orders:
- $S$ before $I$: $S$ returns $\{1,3\}$, then state becomes $\{1,2,3\}$.
- $I$ before $S$: state becomes $\{1,2,3\}$, then $S$ returns $\{1,2,3\}$.

The results differ ($\{1,3\}$ vs. $\{1,2,3\}$) *and* the final states are reached differently, so $S$ and $I$ do not commute on key $2\in[1,3]$. By *Laws of Order* (§5), this strong non-commutativity forces at least one RAW/AWAR fence in any linearizable implementation — a fence-free scan is impossible.

**Upper-bound side.** A vCAS-style snapshot tags each version with an epoch. $S$ grabs a snapshot handle in $O(1)$, then reads key $2$: since $I$ wrote it after the snapshot epoch, $S$ skips $b$ and returns $\{1,3\}$ — wait-free, cost $O(k+\log N)$ with $O(1)$ extra words per version. The gap of §6 is between this $\Omega(1)$ fence floor and the $O(\log N)$ achievable cost.

---
*Part of the [DBMS Research catalog](../../README.md).*
