---
id: 14-main-memory-db/wait-free-range-scans
title: "Wait-Free Range Scans on Concurrent Trees"
topic: 14-main-memory-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Wait-Free Range Scans on Concurrent Trees

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/wait-free-range-scans` · **Status:** open

## 1. Problem Statement
A consistent **range scan** returns a linearizable snapshot of all keys (or key–value pairs) in $[a,b]$ from an in-memory ordered tree that is being concurrently modified by other threads. The problem: **can such a scan be made wait-free — guaranteed to complete in a bounded number of its own steps regardless of other threads' behavior — while imposing only bounded (ideally $O(1)$ amortized) overhead on concurrent updates, and bounded space?**

Variants: (a) *single-scanner wait-freedom* vs *every-operation wait-freedom* (updates also wait-free); (b) *report* (return all $k$ keys) vs *aggregate* (return a fold such as count/sum) scans, where aggregates may permit cheaper structures; (c) bounded vs unbounded version-space. The obstacle: an asynchronous scanner can be lapped arbitrarily many times by fast updaters, so a naive retry-based scan is not wait-free, and pinning a snapshot risks blocking memory reclamation.

## 2. Mathematical Foundations
Setting: asynchronous shared memory with CAS and `fetch-&-add`; correctness = **linearizability** (Herlihy–Wing 1990); progress = **wait-freedom** (Herlihy 1991): each operation finishes in a finite, bounded number of its own steps.

Key constructs:
- **Multi-version concurrency control (MVCC)** modeled as a per-key version chain ordered by a monotone global timestamp $\tau$; a scan at timestamp $\tau_0$ reads the latest version $\le \tau_0$ of each key.
- **vCAS / version lists** (Wei–Ben-David–Blelloch et al. 2021): a *constant-time snapshot* object turning any CAS-based structure into one supporting wait-free, constant-overhead snapshots, with reads at a snapshot costing $O(1)$ amortized per version step.
- **Helping** mechanisms and **announcement arrays** are the standard route from lock-free to wait-free (Herlihy universal construction); the cost is the parameter to bound.
- **Memory reclamation** (epoch-based, hazard pointers, interval-based) interacts: a wait-free scan must not be starved by, nor indefinitely block, reclamation.

Define overhead $\rho$ = extra steps an update performs to support scans, and version-space $\sigma$ = retained obsolete versions; the target is $\rho = O(1)$ amortized and $\sigma$ bounded by live snapshots.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** MVCC engines (HANA, Hekaton, HyPer, Silo/SiloR) provide snapshot scans but typically rely on timestamps + lock-free, not strictly wait-free, scans. **Persistent/functional trees** (immutable, copy-on-write) give trivially consistent scans at update cost.
- **Theory/structure-SOTA:** **vCAS constant-time snapshots** (PPoPP 2021) give wait-free range scans with $O(1)$-amortized update overhead — the strongest general positive result. **KiWi** (PPoPP 2017) gives lock-free maps with linearizable atomic scans. **PNB-tree / lock-free B+-trees** and **Bw-tree** support scans but not full wait-freedom. **BST snapshots** via "lazy snapshot" and **Bronson et al.** optimistic BSTs give consistent iteration with weaker progress.

## 4. Upper Bound
Using vCAS-style version lists over a balanced concurrent search tree yields: range scan that is **wait-free** with cost $O(\log N + k)$ for $k$ reported keys, update overhead $O(1)$ amortized CAS plus a version node, and version-space proportional to the number of concurrent active snapshots times update rate. This establishes feasibility of wait-free scans with bounded amortized overhead — the best known upper bound; tightening the *worst-case* (non-amortized) update overhead and the space bound remains open.

## 5. Lower Bound
*Laws of Order* (Attiya et al., POPL 2011) forces at least one RAW/AWAR fence per linearizable scan (it is strongly non-commutative with in-interval updates), so fence-free wait-free scans are impossible. Herlihy's universal-construction and helping arguments imply that wait-freedom against $p$ processes generally costs $\Omega(p)$ in space/work in the worst case for naive helping; whether ordered range scans *require* $\Omega(p)$ or super-constant update overhead is **not settled**. There is no known matching lower bound to the $O(1)$-amortized vCAS upper bound.

## 6. The Gap
Feasibility is settled (wait-free scans exist with $O(1)$ amortized overhead), but the **worst-case** per-update overhead, the **tight space** for retained versions, and whether *all* operations (not just scans) can be wait-free with these costs are open. The amortized-vs-worst-case gap and the version-space lower bound are the crux; closing them needs both a starvation-free reclamation analysis and a structure-specific lower bound.

## 7. Current Research (as of June 2026)
Active: (i) integrating wait-free snapshots with wait-free memory reclamation (interval-based reclamation, VBR) *(frontier — verify)*; (ii) reducing worst-case (de-amortized) update overhead for version lists; (iii) wait-free *aggregate* scans for analytical (HTAP) workloads. Groups: CMU (Blelloch, Ben-David, Wei), Technion (Petrank), Waterloo (Brown), Tel Aviv (Attiya).

## 8. Future Work
- De-amortized, worst-case $O(1)$ update overhead for wait-free scans.
- Tight space lower bound for snapshot versions under bounded live readers.
- Fully wait-free trees (updates + scans) with practical constants and SIMD/NUMA awareness.

## 9. Key References
- **[Foundational]** Herlihy, M. *Wait-Free Synchronization.* TOPLAS, 1991. — [DOI](https://doi.org/10.1145/114005.102808)
- **[Foundational]** Herlihy, M., Wing, J. *Linearizability.* TOPLAS, 1990. — [DOI](https://doi.org/10.1145/78969.78972)
- **[SOTA]** Wei, Y., Ben-David, N., Blelloch, G., Fatourou, P., Ruppert, E., Sun, Y. *Constant-Time Snapshots with Applications to Concurrent Data Structures.* PPoPP, 2021. — [arXiv](https://arxiv.org/abs/2007.02372)
- **[SOTA]** Basin, D., Bortnikov, E., Braginsky, A., et al. *KiWi: A Key-Value Map for Scalable Real-Time Analytics.* PPoPP, 2017. — [DOI](https://doi.org/10.1145/3018743.3018761)
- **[SOTA]** Bronson, N., Casper, J., Chafi, H., Olukotun, K. *A Practical Concurrent Binary Search Tree.* PPoPP, 2010. — [DOI](https://doi.org/10.1145/1693453.1693488)
- **[Foundational]** Attiya, H., et al. *Laws of Order.* POPL, 2011. — [DOI](https://doi.org/10.1145/1926385.1926442)

## 10. Worked Example

A concurrent ordered tree holds keys $\{10,20,30,40\}$. Scanner $T_S$ wants the range $[15,35]$ — expecting $\{20,30\}$ — as a linearizable snapshot. Using vCAS, $T_S$ grabs a snapshot handle at timestamp $\tau_0=7$ in $O(1)$ (just reads the global counter).

Meanwhile updater $U$ at $\tau=8$ deletes 20 and inserts 25, appending a new version node to each affected key's version list (an $O(1)$ amortized CAS, the update overhead $\rho$).

When $T_S$ reads key 20, it walks that key's version list and takes the latest version with timestamp $\le \tau_0=7$ — i.e. the *pre-delete* value. So $T_S$ still returns $\{20,30\}$, ignoring $U$'s concurrent changes: linearizable at $\tau_0$.

Wait-freedom: $T_S$ finishes in $O(\log N + k)$ of its *own* steps ($\log 4$ to locate $15$, then $k=2$ reports) no matter how often $U$ laps it — a naive retry-scan would instead restart forever. The version of 20 is reclaimable only once no live snapshot $\le \tau_0$ remains, linking version-space $\sigma$ to active scanners.

---
*Part of the [DBMS Research catalog](../../README.md).*
