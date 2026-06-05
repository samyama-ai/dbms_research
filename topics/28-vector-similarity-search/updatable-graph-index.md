# Updatable graph indexes under churn

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/updatable-graph-index` · **Status:** empirically-open

## 1. Problem Statement
Graph ANN indexes (HNSW, DiskANN/Vamana) are built for largely static corpora, but production workloads churn: continuous **inserts** (new embeddings) and **deletes** (expired/removed items), often at high rate. The problem: **maintain graph navigability, recall, and latency under sustained insert/delete churn without periodic full rebuilds**, ideally with bounded per-operation cost and bounded recall drift.

Specifically: design update procedures so that after an arbitrary interleaving of insertions and deletions, (a) the graph remains navigable (greedy search reaches true neighbors), (b) recall stays within $\varepsilon$ of the freshly-built index, and (c) amortized update cost stays sublinear, **without** the recall decay that motivates the standard "rebuild every $X\%$" operational hack.

Variants: insert-only (append), delete-heavy (tombstoning vs. true removal), and full dynamic (arbitrary churn); with/without a memory budget; single-node vs. distributed.

## 2. Mathematical Foundations
- **Deletion damages navigability.** Removing a node from HNSW/Vamana orphans paths that routed *through* it. Naive tombstoning (mark-deleted, skip at query time) preserves edges but inflates the graph with dead nodes; true deletion requires **edge repair** among the deleted node's neighbors to restore monotonic search paths.
- **Vamana/$\alpha$-RNG pruning.** DiskANN's edges satisfy an $\alpha$-relative-neighborhood rule; FreshDiskANN's delete consolidation re-runs this prune over the affected neighborhood to re-establish the diversity/reachability invariant. The cost is local but the *amortized* invariant maintenance is not fully analyzed.
- **Drift as graph property.** Recall is a function of graph connectivity/monotonicity; churn induces a random process on the graph whose stationary navigability is the object of interest. No clean potential-function argument bounds recall drift under adversarial churn.
- **Distribution shift.** Beyond structural churn, the *embedding distribution itself* shifts over time, so even a perfectly maintained graph can lose recall against an evolving query distribution — coupling index maintenance to concept drift.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **FreshDiskANN / FreshVamana** (Singh et al., 2021) introduced streaming inserts plus a delete-consolidation algorithm that repairs edges and empirically holds recall over long update streams. HNSW supports inserts natively; deletes are handled by **tombstoning + lazy repair** in hnswlib/FAISS, with periodic compaction. Vector DBs (Milvus, Weaviate, Qdrant, Vespa) use **segment/LSM-style architectures**: immutable built segments + a writable buffer, with background merge/rebuild — trading freshness latency for amortized cost.
- **Theory-SOTA:** No graph-ANN structure has proven recall-preservation guarantees under arbitrary churn. Dynamic metric data structures (dynamic cover trees, dynamic navigating nets) have update bounds but are not the structures deployed.

## 4. Upper Bound
- **Cover trees** support insert/delete in $O(\lambda^{O(1)}\log n)$ time with maintained query bounds $2^{O(\lambda)}\log n$ — a *provable* dynamic upper bound, but for a structure rarely used in practice.
- **FreshDiskANN:** empirically bounded per-insert and per-delete-consolidation cost (local prune over affected neighborhoods) with recall held near the static index over millions of updates — an experimental, not proven, bound.
- **LSM/segment designs:** amortize updates to background merges; per-query overhead $O(\#\text{segments})$, bounded by merge policy. Upper bounds here are on system throughput, not recall preservation.

## 5. Lower Bound
- No ANN-specific churn lower bound is established. Relevant analogues: dynamic data-structure lower bounds (cell-probe, Pătraşcu–Demaine style) give $\Omega(\log n)$ amortized update/query tradeoffs for many dynamic problems; an adversarial delete sequence can force $\Omega(\text{degree})$ repair work per deletion to preserve reachability — an informal structural lower bound.
- The fundamental tension recall-vs-update-cost (cheap tombstoning degrades recall; thorough repair costs time) is observed but not formalized as a proven tradeoff — hence **empirically-open**.

## 6. The Gap
Systems demonstrate that churn *can* be absorbed with acceptable recall (FreshDiskANN, segment merges), but there is **no guarantee** on long-run recall drift, no proven amortized cost for the repair invariant on HNSW/Vamana, and no characterization of when rebuilds become unavoidable. The gap: between provably-dynamic-but-impractical structures (cover trees) and practical-but-unproven graph indexes. Closing it needs a potential-function analysis of $\alpha$-RNG repair under churn, plus a lower bound on the recall–repair-cost tradeoff.

## 7. Current Research (as of June 2026)
Active: streaming/fresh graph indexes (FreshDiskANN line, Microsoft Research; StreamingDiskANN), out-of-distribution and drift-robust ANN (the big-ann-benchmarks "streaming" and "OOD" tracks, NeurIPS 2023+) *(frontier — verify)*. Work on **filtered + streaming** combined (label-aware updates) and on disk/SSD-resident dynamic graphs with bounded write amplification *(frontier — verify)*. Interest in formal analysis of $\alpha$-RNG repair and in incremental reconstruction to avoid full rebuilds is emerging at SIGMOD/VLDB *(frontier — verify)*.

## 8. Future Work
- Provable amortized cost + recall-drift bounds for HNSW/Vamana under churn.
- A formal recall-vs-repair-cost lower bound.
- Drift-aware maintenance coupling index updates to embedding-distribution shift.
- Eliminate periodic full rebuilds with guaranteed incremental repair.

## 9. Key References
- **[SOTA]** A. Singh, S. J. Subramanya, R. Krishnaswamy, H. V. Simhadri. *FreshDiskANN: A Fast and Accurate Graph-Based ANN Index for Streaming Similarity Search.* arXiv:2105.09613, 2021.
- **[Foundational]** Y. Malkov, D. Yashunin. *Efficient and robust approximate nearest neighbor search using HNSW graphs.* IEEE TPAMI, 2020.
- **[Foundational]** S. J. Subramanya, et al. *DiskANN.* NeurIPS, 2019.
- **[Foundational]** A. Beygelzimer, S. Kakade, J. Langford. *Cover Trees for Nearest Neighbor.* ICML, 2006.
- **[Systems]** J. Wang, et al. *Milvus: A Purpose-Built Vector Data Management System.* SIGMOD, 2021.
- **[Survey]** H. V. Simhadri, et al. *Results of the NeurIPS Big-ANN Benchmarks (Streaming/OOD tracks).* NeurIPS Competition Track, 2023.

---
*Part of the [DBMS Research catalog](../../README.md).*
