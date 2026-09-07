---
id: 05-concurrency-control/mvcc-version-gc
title: "MVCC Garbage Collection Theory"
topic: 05-concurrency-control
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# MVCC Garbage Collection Theory

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/mvcc-version-gc` · **Status:** empirically-open

## 1. Problem Statement

In multi-version concurrency control (MVCC), each update creates a new tuple version; readers see a snapshot defined by a timestamp/visibility predicate. A version is **dead** (reclaimable) when no current or future transaction can ever read it. **Garbage collection (GC)** must reclaim dead versions to bound space and keep version-chain traversal cheap. The core problems:

- **Decision/identification:** which versions are dead given the set of active snapshots?
- **Optimization:** reclaim dead versions while *minimizing* scan/CPU cost and *bounding* version-chain length — ideally without scanning live data.
- **Adversarial / online:** under *long-running readers* that pin old snapshots, bound the worst-case bloat and the competitive ratio of any online GC policy.

The empirical gap: production GC (vacuum, watermark/epoch reclamation) works but lacks tight theory connecting reader behavior, chain length, and reclamation cost.

## 2. Mathematical Foundations

Let active transactions hold snapshot timestamps $t_1 < \dots < t_k$; define the **recycling watermark** $\tau = \min_i t_i$ (oldest active snapshot). A version $v$ with validity interval $[b_v, e_v)$ is dead iff $e_v \le \tau$ and no active snapshot lies in $[b_v, e_v)$. The simplest safe rule reclaims all versions wholly older than $\tau$:

$$\text{Dead}_\tau = \{\, v : e_v \le \tau \,\}.$$

Tighter (interval-based) GC reclaims versions whose intervals contain no active snapshot, requiring a stabbing-query structure over $\{t_i\}$. Worst-case chain length per key is bounded by the number of updates since $\tau$; under a single stuck reader, $\tau$ freezes and bloat grows linearly with update rate — an unbounded *space* blow-up in the worst case, formalizable as an online/competitive problem against an adversary controlling reader longevity.

## 3. State of the Art (SOTA)

**Systems-SOTA:** PostgreSQL autovacuum (heap rewrite + visibility map); HyPer/Umbra's precise, predicate-based **fine-grained MVCC GC** (Neumann, Mühlbauer, Kemper, SIGMOD 2015); Hekaton's cooperative epoch GC (Diaconu et al., SIGMOD 2013); **Steam / two-version and group GC** for HTAP (Böttcher, Leis, Neumann, Kemper, VLDB 2019) which proposed *eager* interval-based pruning to bound chains. **Theory-SOTA:** epoch-based reclamation and hazard-pointer analyses from concurrent-data-structure theory provide safety and progress guarantees; tight *cost-optimal* GC theory remains thin. Wu et al. (VLDB 2017) empirically dissected MVCC design including GC overhead.

## 4. Upper Bound

Watermark GC runs in $O(\text{reclaimed})$ amortized with $O(k \log k)$ to maintain the active-snapshot set. Interval-based GC (stabbing queries) reclaims the *maximum* safe set with $O(\log k)$ per version using an interval tree. Steam-style background pruning keeps expected chain length $O(1)$ under bounded reader staleness, but the bound degrades to $O(\Delta)$ (updates since oldest reader) when a reader is long-lived. No known online algorithm beats this linear dependence in the adversarial reader model.

## 5. Lower Bound

Information-theoretically, *no* GC policy can reclaim a version while any active snapshot can still observe it — so under an adversary that keeps a snapshot at timestamp $\tau$ pinned, worst-case space is $\Omega(\Delta)$ (linear in updates since $\tau$): a hard, model-independent bound. For the *scan-free* requirement, identifying dead versions without touching them is impossible in general because deadness depends on per-key version intervals; there is a cell-probe-style lower bound on the index structure needed to answer "is this key's chain prunable" without enumeration. Tight constants and a formal competitive-ratio lower bound for online GC are open.

## 6. The Gap

The decision rule (deadness given watermark) is **closed**. What is **empirically-open**: a theory that (i) tightly bounds expected/worst-case chain length as a function of the *reader-longevity distribution*, (ii) gives a provably optimal online GC competitive ratio against adversarial long readers, and (iii) characterizes the minimum auxiliary index needed for scan-free reclamation. Systems demonstrate heuristics work well in practice, but matching upper/lower bounds and an optimal policy under long-running readers are unresolved.

## 7. Current Research (as of June 2026)

Active work continues on HTAP engines (Umbra, CedarDB) refining interval/epoch GC and *non-blocking* version pruning *(frontier — verify)*, and on disaggregated/cloud-native MVCC (e.g., Aurora-style, Neon) where version GC interacts with log-structured storage and separate compute/storage scaling. Concurrent-data-structure theorists study optimal memory reclamation (hazard eras, IBR) whose analyses transfer to MVCC GC.

## 8. Future Work

- Competitive analysis of online MVCC GC under adversarial/stochastic reader longevity.
- Provably scan-free reclamation indexes with matching cell-probe lower bounds.
- Co-design of GC with workload-aware snapshot scheduling to cap chain length.
- GC theory for disaggregated storage and long analytical readers over OLTP.

## 9. Key References

- **[SOTA]** Neumann, T.; Mühlbauer, T.; Kemper, A. *Fast Serializable Multi-Version Concurrency Control for Main-Memory Database Systems.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2749436)
- **[SOTA]** Böttcher, J.; Leis, V.; Neumann, T.; Kemper, A. *Scalable Garbage Collection for In-Memory MVCC Systems.* PVLDB, 2019. — [DOI](https://doi.org/10.14778/3364324.3364328)
- **[SOTA]** Diaconu, C.; Freedman, C.; Ismert, E.; Larson, P.-Å.; et al. *Hekaton: SQL Server's Memory-Optimized OLTP Engine.* SIGMOD, 2013. — [DOI](https://doi.org/10.1145/2463676.2463710)
- **[Survey]** Wu, Y.; Arulraj, J.; Lin, J.; Xian, R.; Pavlo, A. *An Empirical Evaluation of In-Memory Multi-Version Concurrency Control.* PVLDB, 2017. — [DOI](https://doi.org/10.14778/3067421.3067427)
- **[Foundational]** Bernstein, P. A.; Goodman, N. *Multiversion Concurrency Control — Theory and Algorithms.* ACM TODS, 1983. — [DOI](https://doi.org/10.1145/319996.319998)

## 10. Worked Example

Key $k$ has a version chain with validity intervals (begin, end):

$$v_1[0,5),\quad v_2[5,12),\quad v_3[12,20),\quad v_4[20,\infty)$$

Active snapshots: $t_1=8$, $t_2=18$. Watermark $\tau = \min(8,18) = 8$.

**Naive watermark GC** ($\text{Dead}_\tau=\{v:e_v\le\tau\}$): only $v_1$ qualifies ($e_{v_1}=5\le 8$). It reclaims 1 version, leaving chain length 3.

**Interval-based GC** reclaims any version whose interval contains *no* active snapshot. Stab-test each: $v_1[0,5)$ — no snapshot, dead. $v_2[5,12)$ — contains $t_1=8$, **live**. $v_3[12,20)$ — contains $t_2=18$, **live**. $v_4$ — newest, live. So it also reclaims only $v_1$ here, but note it would reclaim a middle version if, say, $t_1$ moved to $15$: then $v_2[5,12)$ contains no active snapshot and becomes reclaimable even though $e_{v_2}=12>\tau$.

**Adversarial pin:** if $t_1$ stays stuck at $8$ while writes continue, $\tau$ freezes at $8$ and every new version after timestamp $8$ is retained, giving worst-case space $\Omega(\Delta)$, $\Delta$ = updates since $8$ — the model-independent lower bound.

---
*Part of the [DBMS Research catalog](../../README.md).*
