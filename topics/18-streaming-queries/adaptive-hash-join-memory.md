# Adaptive symmetric-hash join memory management

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/adaptive-hash-join-memory` · **Status:** partially-solved

## 1. Problem Statement
The **symmetric (double-pipelined) hash join** maintains a hash table per input so each arriving tuple probes the opposite table and is inserted into its own; it is non-blocking and produces early results. Under unbounded or windowed streams, the two tables can exceed memory $M$. The problem: design an **online policy** that decides, per tuple, whether to keep it in memory, **spill** it to disk/secondary state, or **evict** it (under window/approximation semantics) so as to maximize result completeness (or throughput) subject to $M$, while preserving correctness for the kept results.

Variants: (i) *exact windowed* — every tuple-pair within window $w$ must eventually be emitted, so eviction must respect window expiry only; the choice is purely *spill scheduling* (which partitions go to disk, when to flush back). (ii) *approximate / best-effort* — under overload, drop tuples to maximize an answer-quality objective (the load-shedding flavor). (iii) *competitive* — bound the policy's loss against an offline optimum that knows the future stream.

## 2. Mathematical Foundations
Treat the join state as a cache of tuples; the **spill scheduling** problem is an online paging/caching problem where the "page" is a hash partition and the cost is I/O to bring a partition back to match late-arriving probes. This connects to **online competitive analysis**: classic paging is $k$-competitive (deterministic) / $H_k$-competitive (randomized, marking). With future-rate uncertainty, the relevant model is the **$k$-server / weighted caching** family, and for value-weighted tuples the **online knapsack / submodular maximization** under a cardinality (memory) constraint, where a greedy by marginal join-contribution yields a $(1-1/e)$ guarantee when contributions are submodular.

Formally, let $X(t)$ be resident state; throughput $\Theta = f(X)$ where $f$ is concave in retained join-relevant tuples; the policy solves $\max_{\pi}\,\mathbb{E}[\text{completeness}]$ s.t. $|X(t)|\le M$. For windowed exact joins, optimal spill ordering reduces to scheduling flushes minimizing back-reads, related to the **minimization of cache misses (Belady)** whose optimum is offline-clairvoyant.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** XJoin's reactive/cleanup phases and the competitive-paging lens; the load-shedding optimum for joins (Srivastava–Widom, Das et al., "Semantic Approximate Joins", VLDB 2003/2005) gives age- and frequency-based shedding with quality bounds.
- **Systems-SOTA:** **XJoin** (Urhan & Franklin, 1999) — three-phase symmetric hash join with disk spill. **Hash-Merge Join / RPJ (Rate-based Progressive Join)** (Tao et al., 2005) — flush the partition that maximizes future output rate. Flink/Spark use **state backends** (RocksDB) with LSM spill + TTL as the de-facto adaptive spill mechanism; modern engines add memory-pressure-driven eviction.

## 4. Upper Bound
For exact windowed symmetric-hash joins, **RPJ** provably maximizes expected output rate under a flush-one-partition policy given a stationary arrival model; XJoin guarantees eventual completeness with $O(1)$ amortized I/O per spilled tuple. Under the online-paging abstraction, a marking/LRU spill policy is **$H_k$-competitive** (randomized) on miss count, $k$ being the number of in-memory partitions. For value-weighted retention with submodular contribution, streaming greedy gives a **$(1-1/e-\epsilon)$** approximation to completeness in one pass.

## 5. Lower Bound
No deterministic online spill policy can be better than **$k$-competitive** on partition back-reads (lower bound inherited from paging). For best-effort joins, achieving optimal completeness requires clairvoyance: an information-theoretic gap exists between any online policy and Belady-optimal offline flushing, and adversarial rate patterns force $\Omega(k)$ competitive loss. Maximizing a general (non-submodular) quality objective under the memory cap is **NP-hard** (reduction from knapsack).

## 6. The Gap
The exact-windowed case is **well-understood** (spill = paging, near-tight competitive bounds), hence *partially-solved*. The open gap is in the **best-effort / overload** regime: no policy is known to be simultaneously near-optimal for completeness, robust to non-stationary and adversarial rates, and cheap to compute per tuple. Tight competitive ratios for *value-weighted, window-expiring* caching — the actual streaming-join setting — are not established; current systems rely on heuristic LRU+TTL with no guarantees.

## 7. Current Research (as of June 2026)
Directions: memory-pressure-aware RocksDB state backends and incremental compaction tuning in Flink *(frontier — verify)*; learned eviction/admission policies (e.g. learned cache replacement) imported into streaming join state *(frontier — verify)*; spill-aware query optimization that co-designs operator placement with state budgets. Groups: Databricks/Flink engineering, TU Berlin DIMA, Wisconsin and Brown data-systems labs continuing the XJoin/RPJ line.

## 8. Future Work
- Tight competitive bounds for window-expiring, value-weighted join caching.
- Online learned admission/eviction with worst-case fallbacks.
- Co-optimization of memory budget allocation across many operators in a dataflow.
- Provable completeness guarantees for best-effort joins under bounded non-stationarity.

## 9. Key References
- **[Foundational]** T. Urhan, M. Franklin. *XJoin: A Reactively-Scheduled Pipelined Join Operator.* IEEE Data Eng. Bulletin, 2000.
- **[SOTA]** Y. Tao, M. L. Yiu, D. Papadias, M. Hadjieleftheriou, N. Mamoulis. *RPJ: Producing Fast Join Results on Streams using Rate-based Optimization.* SIGMOD, 2005.
- **[Foundational]** M. A. Hammad, W. G. Aref, A. K. Elmagarmid. *Hash-Merge Join for Streaming.* (Stream join scheduling.) 2003.
- **[SOTA]** A. Das, J. Gehrke, M. Riedewald. *Approximate Join Processing over Data Streams.* SIGMOD, 2003.
- **[Foundational]** A. Borodin, R. El-Yaniv. *Online Computation and Competitive Analysis.* Cambridge Univ. Press, 1998.

---
*Part of the [DBMS Research catalog](../../README.md).*
