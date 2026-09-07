---
id: 28-vector-similarity-search/disk-ann-io-bounds
title: "Disk-resident ANN I/O lower bounds"
topic: 28-vector-similarity-search
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Disk-resident ANN I/O lower bounds

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/disk-ann-io-bounds` · **Status:** partially-solved

## 1. Problem Statement
Given a set $P$ of $n$ vectors in $\mathbb{R}^d$ stored out-of-core (the index plus data exceed RAM and reside on SSD/NVMe), and a query $q$, we want to return an $(1+\epsilon)$-approximate or $\ge \rho$-recall@$k$ answer while minimizing the number of **random page reads** (I/Os) to the external memory, the dominant cost on flash. The central questions:

- **(Optimization)** What is the minimum expected number of random page reads $B(n,d,\rho,\epsilon)$ needed to achieve recall $\rho$ on a query, as a function of index space $S$ (pages) and page size $B$?
- **(Decision)** Does there exist an index of $S$ pages answering recall-$\rho$ ANN in $\le t$ random reads?
- **(Tradeoff)** Characterize the achievable region in the (space $S$, build cost, per-query I/O $t$, recall $\rho$) space.

The model matters: we count I/Os in the **External Memory (EM)** model of Aggarwal–Vitter with memory $M$, block size $B$, and we are interested in the *random*-read regime (no sequential prefetch amortization), which is what graph-based traversal incurs.

## 2. Mathematical Foundations
We work in the EM / I/O model: cost = number of block transfers between RAM ($M$ words) and disk; a block holds $B$ vectors (or graph adjacency). For exact nearest-neighbor reporting, lower bounds inherit from the **partial-match / indexability** framework of Hellerstein–Koutsoupias–Papadimitriou and the asymmetric-communication bounds for high-dimensional NN (Borodin–Ostrovsky–Rabani; Barkol–Rabani). The *indexability* model formalizes the achievable (redundancy $r$, access overhead $A$) tradeoff for a workload as a set system, giving I/O lower bounds independent of algorithmic cleverness.

For approximate NN, the relevant tools are LSH cell-probe tradeoffs and the **locality** of graph indices: a greedy walk on a navigable graph of out-degree $R$ visits $L$ nodes, each adjacency list and vector residing on (potentially) distinct pages, so per-query I/O $\approx L$ unless layout co-locates neighbors. The combinatorial object is a graph $G$ with the *navigability* property (monotonic path to any $q$'s NN). DiskANN's Vamana shows such graphs exist with bounded degree; the open quantity is the *page-fault* count of the walk under any disk layout, a graph-partitioning / bandwidth question: minimize expected cut edges crossed along greedy paths, related to **min-linear-arrangement** and **balanced-partition** hardness.

## 3. State of the Art (SOTA)
**Systems-SOTA.** DiskANN (Subramanya et al., NeurIPS 2019) and its successors (FreshDiskANN; Filtered-DiskANN, WWW 2023) achieve ~95% recall@10 on billion-scale SIFT with **single-digit** random 4KB reads/query by keeping a compressed (PQ) copy of all vectors in RAM for navigation and reading only full-precision vectors for re-ranking from SSD. SPANN (Chen et al., NeurIPS 2021) uses an in-memory centroid index plus disk posting lists, also achieving a handful of reads. Starling (SIGMOD 2024) optimizes block layout to co-locate graph neighbors, cutting I/O further. *(frontier — verify)* Recent NVMe-aware layouts report 2–4 reads at 90% recall.

**Theory-SOTA.** Tight I/O bounds are known only for special cases (exact NN in low $d$ via kd-tree/range structures in EM). For high-$d$ approximate NN, no matching upper/lower I/O bound exists.

## 4. Upper Bound
With a PQ-compressed navigation graph resident in RAM and Vamana's bounded-degree navigability, DiskANN gives an **$O(1)$-random-reads** query for fixed target recall when the compressed index fits in $M$: navigation incurs no I/O, and only $O(k)$ full vectors are fetched, i.e. $O(k/B + k)$ block reads. In the pure EM model (no compressed copy in RAM), greedy graph search yields $O(L)$ random reads where $L = O(\log n / \log(1/\text{slack}))$ under graph navigability assumptions; with neighbor co-location (Starling) the constant improves but the asymptotic stays $O(L)$.

## 5. Lower Bound
For **exact** high-dimensional NN, asymmetric communication complexity (Borodin–Ostrovsky–Rabani; Barkol–Rabani; Pătrașcu–Thorup cell-probe) implies that any polynomial-space structure needs query time/probes growing with $d$ — effectively $\Omega(d/\log n)$ cell probes, ruling out $O(1)$-I/O exact NN at scale. For **approximate** NN, the partial-match lower bounds and the LSH lower bound of O'Donnell–Wu–Zhou (and Andoni–Razenshteyn optimality of $\rho = 1/(2c^2-1)$) constrain the number of candidate buckets, but **no I/O-model lower bound** matches the single-digit-reads upper bounds — the in-RAM-compressed-navigation trick sidesteps the pure-EM regime, so the right lower bound must charge for the RAM budget jointly.

## 6. The Gap
The gap is genuine and structural. Practice achieves $O(1)$ reads by amortizing navigation into a RAM-resident compressed index; theory's lower bounds either assume no such RAM (EM-only, too weak vs. practice) or target exact NN (too strong). What is missing is a **joint $(M, B, S, \rho)$ lower bound** in a model that charges for the compressed-index RAM and the recall guarantee simultaneously — a "compressed indexability" theorem. Closing it requires proving that any structure achieving recall $\rho$ with $M$ words of RAM needs $\Omega(f(\rho,\epsilon))$ random reads, matching DiskANN-style upper bounds up to constants.

## 7. Current Research (as of June 2026)
Active threads: (i) layout optimization to minimize random reads via graph-partitioning (Starling, SIGMOD 2024); (ii) information-theoretic accounting of the RAM-resident PQ navigator vs. on-disk re-rank, formalizing the budget split *(frontier — verify)*; (iii) CXL / NVMe-oF and computational-storage offload that change the cost model (Microsoft Research, and academic groups at UW, CMU, and IIT). (iv) Theoretical work extending Andoni–Razenshteyn data-dependent LSH bounds into the EM model. People/groups: Harsha Vardhan Simhadri and the DiskANN/BigANN-benchmarks team, Andoni–Razenshteyn (LSH theory), the SPANN/SPTAG group at MSRA.

## 8. Future Work
- A clean lower-bound model (joint RAM+I/O+recall) with matching upper bounds.
- Adaptive layouts provably minimizing greedy-walk page faults (linear-arrangement approximation guarantees).
- I/O bounds for *streaming/fresh* indices where inserts perturb layout.
- Extending bounds to filtered/hybrid ANN where predicates restrict the candidate set.

## 9. Key References
- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** J. M. Hellerstein, E. Koutsoupias, C. H. Papadimitriou. *On the Analysis of Indexing Schemes.* PODS, 1997. — [DOI](https://doi.org/10.1145/263661.263688) · [PDF](http://gist.cs.berkeley.edu/PODS97.pdf)
- **[SOTA]** S. J. Subramanya, Devvrit, R. Kadekodi, R. Krishnaswamy, H. V. Simhadri. *DiskANN: Fast Accurate Billion-point Nearest Neighbor Search on a Single Node.* NeurIPS, 2019. — [PDF](https://suhasjs.github.io/files/diskann_neurips19.pdf)
- **[SOTA]** Q. Chen et al. *SPANN: Highly-efficient Billion-scale Approximate Nearest Neighbor Search.* NeurIPS, 2021. — [arXiv](https://arxiv.org/abs/2111.08566)
- **[SOTA]** M. Wang et al. *Starling: An I/O-Efficient Disk-Resident Graph Index Framework.* SIGMOD, 2024. — [arXiv](https://arxiv.org/abs/2401.02116) · [DOI](https://doi.org/10.1145/3639269)
- **[Foundational]** A. Andoni, I. Razenshteyn. *Optimal Data-Dependent Hashing for Approximate Near Neighbors.* STOC, 2015. — [arXiv](https://arxiv.org/abs/1501.01062)

## 10. Worked Example

Why the in-RAM PQ navigator collapses random reads. Consider $n=10^9$ vectors in $d=128$, page size $B=4$ KB. A Vamana graph walk visits $L\approx 12$ nodes to reach the answer.

**Pure-EM (no compression in RAM):** each visited node needs its full vector ($128\times4$ B $=512$ B) and adjacency list, scattered across the SSD — so $\approx L = 12$ random 4 KB reads/query just to navigate, plus $k$ reads to fetch the top-$k$ results.

**DiskANN trick:** keep a PQ-compressed copy of *all* vectors in RAM. At $m=32$ subspaces, $b=8$ bits, each vector is $32$ B, so the navigator is $10^9\times32\text{ B}=32$ GB — fits in RAM. Navigation now scores PQ codes in memory with **zero I/O**; only the final $k=10$ full vectors are read from SSD for re-rank: $\lceil k\cdot 512\text{ B}/B\rceil \approx 2$ page reads. Total query I/O drops from $\sim$12 to $O(1)$ ($\approx 2$ reads), the empirically observed "single-digit reads."

The lower-bound gap: this $O(1)$-reads result is *bought with* $M=32$ GB of RAM. A meaningful lower bound must charge for that $M$ jointly with recall $\rho$ — pure-EM bounds (assuming no such RAM) are too weak to forbid it.

---
*Part of the [DBMS Research catalog](../../README.md).*
