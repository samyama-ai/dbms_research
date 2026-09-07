---
id: 18-streaming-queries/windowed-similarity-joins
title: "Approximate sliding-window correlation/similarity joins"
topic: 18-streaming-queries
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Approximate sliding-window correlation/similarity joins

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/windowed-similarity-joins` · **Status:** open

## 1. Problem Statement

Given two (or one self-) high-rate streams of high-dimensional vectors and a sliding window $W$, continuously report pairs $(x,y)$ with $x\in S_1\cap W$, $y\in S_2\cap W$ whose similarity exceeds a threshold — cosine/Euclidean similarity, Pearson correlation over recent series values, or set similarity (Jaccard). The goal is to maintain the (approximate) join result as the window slides, using **sublinear state** in the window size and **sublinear-per-update** time, rather than the $O(N^2)$ all-pairs recomputation.

Variants: **threshold join** (report pairs with $\mathrm{sim} \ge \theta$), **top-$k$ correlation** (the $k$ most-correlated pairs in the window — the "StatStream/BRAID" problem), **decision** (does any pair exceed $\theta$?), and **counting** (how many such pairs?). The defining difficulty is *deletion*: window expiry forces the index to support efficient removal while preserving recall guarantees, which most ANN structures handle poorly.

## 2. Mathematical Foundations

Items are vectors in $\mathbb{R}^d$ (or sets over a universe). Similarity join asks for pairs within distance $r$ (or above similarity $\theta$). Core tools:

- **Locality-Sensitive Hashing (LSH)** (Indyk–Motwani 1998; Andoni–Indyk 2006): a hash family where $\Pr[h(x)=h(y)]$ is monotone in similarity; gives $(r,c r)$-approximate near-neighbor in $O(n^{\rho})$ query, $\rho = \log(1/p_1)/\log(1/p_2)$, with $\rho \to 1/c^2$ for Euclidean (Andoni–Indyk). Optimal data-dependent LSH gives $\rho = 1/(2c^2-1)$ (Andoni–Razenshteyn 2015).
- **Graph ANN** (HNSW, Malkov–Yashunin 2018): empirically dominant for static/append-only ANN; deletions are the open weakness.
- **Correlation over series:** sketch the series with random projections / **DFT/wavelet** coefficients; the **JL lemma** preserves inner products, so cosine/correlation is estimable from $O(\epsilon^{-2}\log n)$-dim sketches. StatStream (Zhu–Shasha 2002) and BRAID (Sakurai et al. 2005) use DFT + grid pruning for windowed correlation.
- **Lower-bound substrate:** similarity join is intimately tied to the hardness of near-neighbor and to **OVP/SETH** fine-grained reductions for high-dimensional pair-finding.

## 3. State of the Art (SOTA)

- **Theory-SOTA (static):** optimal data-dependent LSH (Andoni–Razenshteyn 2015) and LSH-forest/multiprobe variants. For *windowed* similarity join, no construction matches static optimality under deletions.
- **Systems-SOTA:** Streaming/vector engines (Milvus, Vespa, FAISS-based pipelines) support incremental ANN but handle window expiry by periodic rebuild or tombstoning, not principled sliding-window guarantees. For correlation, StatStream/BRAID-style DFT-grid methods remain the reference; Apache Flink + LSH UDFs are used ad hoc.
- General-purpose **streaming similarity self-join** systems give heuristic recall; sublinear-state *guarantees* under sliding windows are not provided.

## 4. Upper Bound

- **Static near-neighbor (per query):** $O(d\,n^{\rho})$ time, $O(n^{1+\rho})$ space, $\rho = 1/(2c^2-1)$ (data-dependent LSH), giving an all-pairs similarity join in $\tilde O(n^{1+\rho})$.
- **Windowed via LSH with expiry:** maintaining LSH buckets with deletion gives amortized $O(n^{\rho})$ per update and $O(n^{1+\rho})$ state over a window of $n$ live items — sublinear *query* but not sublinear *state* in general.
- **Correlation:** JL sketching gives $O(\epsilon^{-2}\log n)$ state per series and $O(\epsilon^{-2})$ inner-product estimates; top-$k$ correlation via grid pruning is output-sensitive but worst-case quadratic.

## 5. Lower Bound

- **High-dimensional similarity join** is **SETH-hard** to solve much faster than quadratic: under SETH, no $O(n^{2-\delta})$ algorithm decides whether two sets of $n$ vectors in dimension $d=\omega(\log n)$ contain a close pair (via reductions from Orthogonal Vectors; Williams 2005, Rubinstein 2018 for approximate bichromatic closest pair). This makes *exact, low-state* sliding-window joins essentially impossible at scale.
- **LSH optimality:** $\rho \ge 1/(2c^2-1) - o(1)$ for data-dependent hashing (Andoni–Razenshteyn–Waingarten 2017) — you cannot beat this query exponent.
- **Sliding-window state:** an encoding/communication argument forces $\Omega(N)$ state for *exact* windowed near-neighbor maintenance, so approximation is mandatory.

## 6. The Gap

**Genuinely open.** The static near-neighbor problem has tight LSH bounds, but the *sliding-window, deletion-supporting, sublinear-state* version does not. The gap is between (a) upper bounds that achieve sublinear *query* time but $\Omega(N)$-ish *state*, and (b) the desire for truly sublinear state with recall guarantees under adversarial expiry. SETH closes the door on exact fast joins, so the open question is: what is the optimal *approximation–state–update-time* trade-off for windowed similarity joins, and can graph-ANN-quality recall be retained under deletions with provable bounds? No accepted answer exists.

## 7. Current Research (as of June 2026)

- **Deletion-robust graph ANN** (filtered/updatable HNSW, FreshDiskANN — Singh et al.) extended toward sliding-window semantics *(frontier — verify)*.
- **Streaming LSH with windowed buckets** and decayed counts for correlation discovery; sketch-based top-$k$ correlation under drift.
- **Fine-grained complexity of approximate similarity join** (Rubinstein lineage) sharpening what approximation buys past the SETH barrier.
- Hardware-accelerated (GPU) windowed all-pairs for moderate $N$ as a pragmatic baseline *(frontier — verify)*.

## 8. Future Work

- Sublinear-state sliding-window ANN indexes with recall guarantees under deletions.
- Tight approximation–state–time trade-offs for windowed correlation/similarity joins.
- Output-sensitive algorithms whose cost scales with the number of qualifying pairs, not $N^2$.
- Integration with watermarks/out-of-order arrival (late vectors entering an already-evicted window).

## 9. Key References

- **[Foundational]** P. Indyk, R. Motwani. *Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality.* STOC, 1998. — [DOI](https://doi.org/10.1145/276698.276876)
- **[Foundational]** A. Andoni, P. Indyk. *Near-Optimal Hashing Algorithms for Approximate Nearest Neighbor in High Dimensions.* FOCS, 2006 / CACM, 2008. — [DOI](https://doi.org/10.1109/FOCS.2006.49)
- **[SOTA]** A. Andoni, I. Razenshteyn. *Optimal Data-Dependent Hashing for Approximate Near Neighbors.* STOC, 2015. — [arXiv](https://arxiv.org/abs/1501.01062)
- **[SOTA]** Y. Malkov, D. Yashunin. *Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs (HNSW).* IEEE TPAMI, 2018. — [arXiv](https://arxiv.org/abs/1603.09320)
- **[Foundational]** Y. Zhu, D. Shasha. *StatStream: Statistical Monitoring of Thousands of Data Streams in Real Time.* VLDB, 2002. — [DBLP](https://dblp.org/rec/conf/vldb/ZhuS02.html)
- **[SOTA]** A. Rubinstein. *Hardness of Approximate Nearest Neighbor Search (SETH-based).* STOC, 2018. — [arXiv](https://arxiv.org/abs/1803.00904)

## 10. Worked Example

**Cosine-LSH over a sliding window.** Window holds the last $W=3$ unit vectors per stream; threshold $\theta = 0.9$ (angle $\le 25.8^\circ$). Use one sign-random-projection (SimHash) hash with random hyperplane $u=(1,1)/\sqrt2$: $h(x)=\text{sign}(u\cdot x)$.

$S_1$ live: $x_1=(1,0),\,x_2=(0,1),\,x_3=(-1,0)$. $S_2$ arrives with $y=(0.71,0.71)$.

Hashes: $u\cdot x_1=0.71\Rightarrow h{=}1$; $u\cdot x_2=0.71\Rightarrow h{=}1$; $u\cdot x_3=-0.71\Rightarrow h{=}0$; $u\cdot y=1.0\Rightarrow h{=}1$.

Probing $y$ visits bucket $1 = \{x_1,x_2\}$, skipping $x_3$ entirely — only 2 of 3 candidates examined. Verify exact cosines: $\cos(y,x_1)=0.71<\theta$, $\cos(y,x_2)=0.71<\theta$ — neither qualifies, no pair emitted. The SimHash collision probability is $\Pr[h(x){=}h(y)] = 1-\tfrac{\angle(x,y)}{\pi}$, monotone in similarity, so close pairs collide more often; stacking $L$ independent tables drives recall up at $O(n^{\rho})$ query cost, $\rho=1/(2c^2-1)$.

**The deletion pain:** when $x_1$ expires, we must remove it from its bucket. A graph-ANN index (HNSW) has no clean way to do this without degrading the navigation graph — the open sliding-window difficulty.

---
*Part of the [DBMS Research catalog](../../README.md).*
