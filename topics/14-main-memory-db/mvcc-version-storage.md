# In-Memory MVCC Version Storage

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/mvcc-version-storage` · **Status:** open

## 1. Problem Statement
Multi-Version Concurrency Control (MVCC) lets readers proceed without blocking writers by retaining multiple physical versions of each logical tuple. In a main-memory database (IMDB), versions live in RAM, so the central tension is sharp: **how do we organize version chains and reclaim dead versions so that (a) a long-running reader cannot force unbounded memory growth, while (b) scan-time and point-access latency are not degraded by version-chain traversal?**

Concretely we must jointly choose:
- a **version-chain layout** (newest-to-oldest vs. oldest-to-newest, delta vs. full-tuple storage, in-place vs. append-only);
- a **garbage-collection (GC) policy** that identifies and frees versions no longer visible to any active transaction;
- a **visibility-check mechanism** evaluated per tuple per scan.

Variants: *(optimization)* minimize peak memory subject to a bound on per-tuple visibility cost; *(decision)* given a workload and a memory budget $M$, does a GC schedule exist that never exceeds $M$? *(online)* make GC decisions without knowing future transaction lifetimes.

## 2. Mathematical Foundations
Let transactions $T_1,\dots,T_n$ each carry a snapshot timestamp $\mathrm{ts}(T_i)$. A version $v$ of tuple $k$ has a validity interval $[\mathrm{begin}(v),\mathrm{end}(v))$. Version $v$ is **live** iff some active $T_i$ has $\mathrm{begin}(v) \le \mathrm{ts}(T_i) < \mathrm{end}(v)$; the **recycling watermark** is $W=\min_i \mathrm{ts}(T_i)$, and any version with $\mathrm{end}(v)\le W$ is provably dead.

Peak version count is governed by the oldest live snapshot: if $L=\max_i(\text{wall-clock now}-\text{start}(T_i))$ is the longest reader lifetime and $r$ the version-creation rate, retained versions scale as $\Theta(r\cdot L)$ in the worst case. Bounding memory therefore requires bounding the product $r\cdot L$ — i.e., either aborting/snapshotting long readers or compacting chains.

Visibility cost is the expected chain depth a scan must walk: $\mathbb{E}[\text{depth}] = \Theta(r \cdot (\text{now}-W))$ for newest-first chains, which is exactly the quantity GC must keep small. This is the formal statement of the **scan-vs-GC** coupling.

## 3. State of the Art (SOTA)
- **Hekaton** (Larson et al., VLDB 2011/2012): lock-free, append-only, newest-to-oldest chains in SQL Server's in-memory engine; cooperative GC where worker threads encountering dead versions unlink them.
- **HyPer / Neumann-Mühlbauer-Kemper** (SIGMOD 2015): serializable MVCC with in-place newest version + backward delta chains and precise, low-overhead validation; the canonical IMDB MVCC design.
- **Empirical taxonomy** — Wu, Arulraj, Lin, Xian, Pavlo (VLDB 2017, *An Empirical Evaluation of In-Memory MVCC*): systematically separates version-storage (append-only / time-travel / delta), GC (tuple- vs. transaction-level, background-vacuum vs. cooperative), and index-management dimensions. Still the reference framework.
- **Steam / Böttcher et al.** (VLDB 2019): *Scalable Garbage Collection for In-Memory MVCC* — eager pruning of intermediate versions and bounded chain lengths under long readers.

## 4. Upper Bound
With **delta (backward) chains + in-place newest version**, point reads of the latest version are $O(1)$ and GC frees a version in $O(1)$ amortized via a precise watermark. STEAM-style eager pruning bounds expected live chain length to $O(\text{number of concurrent writers})$ rather than $O(r\cdot L)$, decoupling memory from reader lifetime for non-conflicting keys. Best-known peak memory is $O(\text{db size} + \text{live deltas})$ with live deltas pruned to writer-concurrency, not wall-clock, scale.

## 5. Lower Bound
No unconditional super-linear lower bound is known; the hardness is *adversarial-workload* and *information-theoretic*. If a single reader holds snapshot $\mathrm{ts}=W$ for duration $L$ and a disjoint hot set is updated at rate $r$, any **correct** snapshot-isolation implementation must retain enough state to reconstruct every value as of $W$, forcing $\Omega(\min(r\cdot L,\ |\text{updated keys}|))$ retained versions — you cannot GC below the information a live snapshot is entitled to read. Optimal *online* GC under unknown reader lifetimes is competitive-ratio bounded against an offline adversary; tight competitive ratios for IMDB GC are unresolved.

## 6. The Gap
The retention lower bound is fundamental, but it only bites for keys actually touched by both the long reader's snapshot and the writers. The open question is the gap between worst-case $\Omega(r\cdot L)$ and achievable per-key, per-workload retention: can GC provably track the *minimal* live set (the information-theoretic floor) online, without scan-time penalty and without aborting long readers? STEAM closes much of this empirically for OLTP; a workload-independent algorithm with a proven competitive ratio, and tight bounds for HTAP scan-heavy workloads, remain open.

## 7. Current Research (as of June 2026)
- Decoupling OLAP snapshots from OLTP version chains so analytic long-runners do not pin OLTP GC — extensions of HyPer/Umbra-style separate columnar snapshots *(frontier — verify)*.
- GC for disaggregated / CXL-attached memory tiers, where dead-version migration cost reshapes the policy *(frontier — verify)*.
- Learned / lifetime-predicting GC schedulers that anticipate reader durations to pre-compact chains *(frontier — verify)*.
- Groups: CMU Database Group (Pavlo), TUM (Neumann/Kemper), Microsoft Research (Larson lineage), and the Umbra effort at TUM.

## 8. Future Work
- A provably competitive online GC algorithm parameterized by reader-lifetime distribution.
- Formal cost model unifying memory, scan-depth, and abort rate into one optimizable objective.
- Hardware-assisted (HTM / persistent-memory) version reclamation with crash-consistent dead-version freeing.
- Visibility-check vectorization so deep chains do not break SIMD scans.

## 9. Key References
- **[SOTA]** Y. Wu, J. Arulraj, J. Lin, R. Xian, A. Pavlo. *An Empirical Evaluation of In-Memory Multi-Version Concurrency Control.* VLDB, 2017. — [DOI](https://doi.org/10.14778/3067421.3067427)
- **[Foundational]** T. Neumann, T. Mühlbauer, A. Kemper. *Fast Serializable Multi-Version Concurrency Control for Main-Memory Database Systems.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2749436)
- **[Foundational]** P.-Å. Larson, S. Blanas, C. Diaconu, C. Freedman, J. Patel, M. Zwilling. *High-Performance Concurrency Control Mechanisms for Main-Memory Databases.* VLDB, 2011. — [DOI](https://doi.org/10.14778/2095686.2095689)
- **[SOTA]** J. Böttcher, V. Leis, T. Neumann, A. Kemper. *Scalable Garbage Collection for In-Memory MVCC Systems (STEAM).* VLDB, 2019. — [DOI](https://doi.org/10.14778/3364324.3364328)
- **[Survey]** A. Pavlo et al. *Self-Driving Database Management Systems / In-Memory OLTP lectures.* CMU 15-721 course materials. — [course site](https://15721.courses.cs.cmu.edu/)

## 10. Worked Example

One tuple $k$ is updated every timestep, building a newest-to-oldest chain. After 6 updates the versions have validity intervals:

$$v_6:[6,\infty)\ \to\ v_5:[5,6)\ \to\ v_4:[4,5)\ \to\ v_3:[3,4)\ \to\ v_2:[2,3)\ \to\ v_1:[1,2)$$

A long reader $T_L$ started at $\mathrm{ts}=3$ and is still active; all other transactions have finished. The recycling watermark is $W=\min_i \mathrm{ts}(T_i)=3$.

**Visibility for $T_L$.** It needs the version live at timestamp 3, i.e. $v_3$ with $[3,4)$. A newest-first scan walks $v_6\to v_5\to v_4\to v_3$ — depth 4.

**GC.** Any version with $\mathrm{end}(v)\le W=3$ is provably dead: $v_1\,[1,2)$ and $v_2\,[2,3)$ qualify and are freed. Versions $v_3,\dots,v_6$ must be retained because $v_3$ is visible to $T_L$ and $v_4,v_5,v_6$ lie between $W$ and now.

**The coupling (§2).** With creation rate $r=1$/step and reader lag $\mathrm{now}-W = 6-3 = 3$, expected chain depth $\Theta(r\cdot(\mathrm{now}-W))=3$, and retained versions $\Theta(r\cdot L)$ with $L=3$. If $T_L$ commits, $W$ jumps to 6 and $v_3,v_4,v_5$ become collectable — illustrating why a single long reader pins memory.

---
*Part of the [DBMS Research catalog](../../README.md).*
