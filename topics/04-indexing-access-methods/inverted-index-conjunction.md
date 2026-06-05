# Inverted-index compression for conjunctions

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/inverted-index-conjunction` · **Status:** empirically-open

## 1. Problem Statement
An inverted index stores, per term, a sorted **posting list** of document IDs. Conjunctive ("AND") queries require **intersecting** several sorted lists. The problem: design **compressed** posting-list layouts that make multi-term intersection **faster than the galloping/​merge and SIMD baselines**, ideally with cost sublinear in the smallest list or near the **output size**, while keeping space close to gap-entropy. The tension is that the most compact encodings (delta + entropy coding) are sequential-decode and resist random access, whereas skip/​block layouts that enable galloping cost space.

Variants: (a) two-list intersection; (b) $k$-way conjunction (order/​plan matters); (c) ranked top-$k$ conjunction (WAND/​BMW); (d) decision/​existence vs. full enumeration. Status is **empirically-open**: practical systems keep improving via SIMD and layout tricks, but no scheme provably beats the known intersection lower bounds across regimes.

## 2. Mathematical Foundations
Posting lists are monotone integer sequences; compressed via delta-gaps + VByte, PForDelta, Simple-9/16, Elias–Fano, or partitioned Elias–Fano. **Elias–Fano** encodes a monotone sequence of $n$ values in $[0,u)$ in $n\lceil\log(u/n)\rceil + 2n + o(n)$ bits with $O(1)$ access and $O(\log)$ predecessor — enabling *skip* without decompression.

Intersection complexity:
- **Adaptive / instance-optimal merging:** Demaine–López-Ortiz–Munro bound intersection cost by the **encoding of the proof** (the number of "comparisons" any algorithm must make for that instance); galloping is near-instance-optimal for two lists.
- For sorted-set intersection, the comparison/​I-O lower bound for two lists of sizes $m\le n$ is $\Omega(m\log(n/m))$ (via galloping) and $\Omega(\text{output})$ trivially.
- **SIMD** intersection (Lemire–Boytsov–Kurz; Inoue et al.) cuts constants by comparing blocks in parallel but does not change asymptotics.
- Fine-grained conditional bounds: sorted-set intersection / batch-conjunction relate to **Orthogonal Vectors** and SETH, suggesting strong sub-quadratic barriers for certain dense regimes.

## 3. State of the Art (SOTA)
- **Elias–Fano & Partitioned Elias–Fano** — Vigna (WSDM 2013); Ottaviano, Venturini (SIGIR 2014): compact + skippable, strong space/​speed point.
- **PForDelta / Simple families** — Zukowski et al.; Anh–Moffat; Lemire–Boytsov (SIMD-BP128, "Stream-VByte").
- **SIMD set intersection** — Lemire, Boytsov, Kurz (2016); Inoue, Ohara, Taura (vectorized).
- **Ranked conjunction (systems-SOTA):** WAND (Broder et al. 2003), Block-Max WAND / BMW (Ding–Suel, SIGIR 2011); used in Lucene/​Elasticsearch, PISA research engine.
- **Recursive / partitioned graphs:** BP (bipartite graph partitioning) document reordering (Dhulipala et al., KDD 2016) shrinks gaps and speeds intersection.

## 4. Upper Bound
Two-list galloping over skippable (Elias–Fano) layouts achieves $O(m\log(n/m))$ comparisons, instance-optimal up to constants; SIMD reduces wall-clock constants by $2$–$8\times$. Block-Max WAND prunes ranked conjunctions to far below full intersection in practice. Space is within $2n+o(n)$ bits of gap entropy for Elias–Fano. These are the best *guaranteed* bounds; layout/​reordering further reduces constants empirically.

## 5. Lower Bound
- **Comparison model:** $\Omega(m\log(n/m))$ for intersecting two sorted lists (matched by galloping) and the adaptive bound of Demaine–López-Ortiz–Munro shows galloping is instance-optimal in a strong sense — so you *cannot* asymptotically beat it in the comparison/​pointer model.
- **Output-sensitive floor:** $\Omega(\text{output} + \text{smallest input touched})$.
- **Fine-grained:** batched/​dense set-intersection and conjunctive top-$k$ inherit OV/​SETH-conditional barriers against strongly sub-quadratic total work in worst case.

## 6. The Gap
The asymptotic two-list bound is essentially **closed** (galloping is instance-optimal). What is **empirically open**: (i) whether *compressed*, cache- and SIMD-friendly layouts can consistently beat galloping/​SIMD constants across $k$-way and skewed-length regimes; (ii) the right model that captures memory bandwidth + branch prediction where real speedups live; (iii) provable guarantees for *learned*/​reordered layouts that exploit document-ID assignment. No proof says current SIMD intersection is constant-optimal under the RAM-with-SIMD cost model.

## 7. Current Research (as of June 2026)
Directions: GPU/​AVX-512 intersection; clustering/​recursive-graph-bisection document reordering to minimize gaps and maximize skip; learned posting-list partitioning; integrating compression with dense/​learned retrieval (hybrid sparse-dense), and PISA-based reproducible benchmarking. *(Frontier — verify)* recent claims of SIMD/​GPU conjunction kernels beating Block-Max WAND on multi-term queries via succinct skip structures + learned reordering. People: Suel (NYU), Ottaviano/​Venturini/​Vigna (Pisa/​Meta), Lemire (Québec), Mallia/​PISA team, Dhulipala (graph reordering).

## 8. Future Work
- A realistic SIMD/​memory-hierarchy cost model with matching lower bounds for compressed conjunction.
- Provably-beneficial document-ID reordering for intersection (not just compression).
- $k$-way and ranked-conjunction instance-optimality under compression.
- Co-design with learned/​dense retrieval for hybrid conjunctive queries.

## 9. Key References
- **[Foundational]** Demaine, López-Ortiz, Munro. *Adaptive Set Intersections, Unions, and Differences.* SODA, 2000.
- **[SOTA]** Ottaviano, Venturini. *Partitioned Elias-Fano Indexes.* SIGIR, 2014.
- **[SOTA]** Ding, Suel. *Faster Top-k Document Retrieval Using Block-Max Indexes (BMW).* SIGIR, 2011.
- **[SOTA]** Lemire, Boytsov, Kurz. *SIMD Compression and the Intersection of Sorted Integers.* Software: Practice & Experience, 2016.
- **[Foundational]** Dhulipala, Kabiljo, Karrer, Ottaviano, Pandey, et al. *Compressing Graphs and Indexes with Recursive Graph Bisection.* KDD, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
