# Snapshot/MVCC Version Page Caching

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/mvcc-version-caching` · **Status:** open

## 1. Problem Statement

Under multi-version concurrency control (MVCC), a logical tuple has a **version chain** of physical records, and each transaction reads at a **snapshot** (a commit timestamp / visibility predicate). The buffer pool caches *version pages*. The problem: design admission/eviction that minimizes misses **accounting for which versions are visible to which live snapshots** — a version cached but invisible to all active transactions is dead weight; a version still reachable by a long-running reader must be retained.

Formally: pages carry versions tagged with valid-time intervals $[begin_v, end_v)$. Active transactions hold snapshots $\{s_1,\dots,s_k\}$. A version $v$ is **live** if $\exists s_i : begin_v \le s_i < end_v$. Choose a resident set maximizing weighted hits where a request is "(snapshot $s$, tuple key $t$)" resolving to the *visible* version. Coupled subproblem: which obsolete versions can be **garbage-collected** (no snapshot can ever see them again).

Variants:
- **Optimization:** minimize miss cost given the visibility structure.
- **Decision (GC):** is version $v$ dead for all current/future snapshots? (the "watermark" test).
- **Online:** snapshots and version chains evolve as transactions begin/commit.

## 2. Mathematical Foundations

**Visibility as interval stabbing.** A version's liveness is an **interval-stabbing** condition over active snapshot timestamps; the set of live versions is maintained as snapshots advance — an instance of **temporal/interval data structures**. The GC frontier is the **low watermark** $w = \min_i s_i$: versions with $end_v \le w$ are unconditionally dead.

**Caching with weighted, request-dependent value.** Requests target *logical* keys but resolve to *physical* versions depending on the requesting snapshot, so the page's value is a function of the live-snapshot multiset — a **weighted caching** instance where weights drift with the transaction mix. Offline optimum is **Belady-with-weights** (furthest reuse, value-scaled); but version validity makes the request stream **non-stationary by construction**.

**Competitive caching.** Deterministic weighted caching is $k$-competitive (Chrobak–Karloff–Payne–Vishwanathan / Young's Landlord), $O(\log k)$ randomized — these bound any version-aware policy that ignores future snapshots. The novelty is that **future visibility is partially predictable** from the active-transaction set, so a *predictions-augmented* (learning-augmented) model applies.

**Interaction with GC.** Eviction and GC interact: evicting a still-live version forces a refetch; GC'ing it is permanent. This is a **joint retention problem** over two horizons (cache residency vs. logical liveness).

## 3. State of the Art (SOTA)

**Systems-SOTA.** **HyPer / Umbra** (Neumann et al.) use precise version chains with serializability validation; **Hekaton** (Diaconu et al., SIGMOD 2013) and **PostgreSQL**'s heap-with-tuple-versions inform GC watermark design. **Steam** (Böttcher et al., SIGMOD 2019) is the SOTA on *scalable MVCC garbage collection*, pruning version chains eagerly. Most engines, however, treat the buffer pool as **version-agnostic** (LRU/CLOCK over raw pages) — version-awareness in *replacement* is largely unexploited.

**Theory-SOTA.** Weighted/file caching with $O(\log k)$ randomized competitiveness (Bansal–Buchbinder–Naor) and learning-augmented caching (Lykouris–Vassilvitskii 2018; Rohatgi 2020) are the relevant theory, but none is specialized to snapshot visibility.

## 4. Upper Bound

- **Generic version-as-weighted-caching:** $k$-competitive deterministic, $O(\log^2 k)$ randomized (file caching, Bansal–Buchbinder–Naor 2012) — applies but ignores visibility predictability.
- **GC decision:** watermark test is $O(1)$ per version given the min active snapshot; Steam achieves near-linear chain pruning empirically.
- **Learning-augmented:** with a predictor of snapshot lifetimes, consistency/robustness trade-offs of Lykouris–Vassilvitskii give $O(\min(\eta/\text{OPT}, \log k))$ — but only as a *plausible adaptation*, not a published bound for the MVCC objective.

## 5. Lower Bound

- **Weighted caching** has a deterministic competitive lower bound of $k$ and randomized $\Omega(\log k)$ (Fiat et al.; metrical-task-system bounds) — inherited.
- **Snapshot-visibility-aware optimal eviction offline** is at least as hard as **weighted interval scheduling under online snapshot arrivals**; with adversarial transaction lifetimes, no online policy beats the $\Omega(\log k)$ randomized bound.
- The **joint cache+GC** decision (retain physically vs. collect logically) under uncertain future long-running readers has no known sub-$k$ competitive guarantee; we are not aware of a matching lower bound *specific* to the visibility structure — itself an open question.

## 6. The Gap

**Open.** No replacement policy with provable guarantees exploits MVCC visibility structure; production systems use version-agnostic LRU/CLOCK, leaving an unquantified gap to the visibility-aware offline optimum. The theory side offers only generic weighted-caching bounds that (i) do not use the *predictable* component of future visibility (active-snapshot set) and (ii) do not model the cache/GC coupling. Closing the gap needs: a formal competitive model for snapshot-aware caching, an algorithm beating generic weighted caching by using the live-snapshot set as a prediction, and a matching lower bound that pins down how much visibility information helps.

## 7. Current Research (as of June 2026)

- **Visibility-aware buffer management** in HTAP engines where long analytic readers pin old versions while OLTP churns new ones. *(frontier — verify)*
- **Learning-augmented caching with transaction-lifetime predictors** for version retention. *(frontier — verify)*
- **Unified version GC + buffer eviction** controllers (Umbra/CedarDB, TUM lineage; CMU). *(frontier — verify)*
- Time-travel / historical-snapshot caching in lakehouse and versioned stores (Iceberg/Delta time travel).

## 8. Future Work

- A competitive analysis framework for snapshot-visibility-aware caching with matching upper/lower bounds.
- Learning-augmented policies using active-snapshot sets as side information, with consistency/robustness guarantees.
- Joint optimization of buffer eviction and MVCC garbage collection under uncertain long-running readers.
- Multi-version-aware tiering across DRAM/NVM/SSD for HTAP version chains.

## 9. Key References

- **[Foundational]** Bernstein, Goodman. *Multiversion Concurrency Control — Theory and Algorithms.* ACM TODS, 1983.
- **[SOTA]** Böttcher, Leis, Neumann, Kemper. *Scalable Garbage Collection for In-Memory MVCC Systems (Steam).* VLDB, 2019.
- **[SOTA]** Diaconu, Freedman, Ismert, et al. *Hekaton: SQL Server's Memory-Optimized OLTP Engine.* SIGMOD, 2013.
- **[Foundational]** Bansal, Buchbinder, Naor. *Randomized Competitive Algorithms for Generalized Caching.* SIAM J. Computing, 2012.
- **[SOTA]** Lykouris, Vassilvitskii. *Competitive Caching with Machine Learned Advice.* ICML, 2018.
- **[Survey]** Wu, Arulraj, Lin, Xian, Pavlo. *An Empirical Evaluation of In-Memory MVCC.* VLDB, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
