# Optimal IVF partitioning and probing

> **Topic:** Vector Databases & Similarity Search · **ID:** `28-vector-similarity-search/ivf-partition-probing` · **Status:** partially-solved

## 1. Problem Statement

An inverted-file (IVF) index partitions $n$ vectors into $C$ buckets (typically by a coarse quantizer / centroids $\{c_1,\dots,c_C\}$). A query probes the $p$ ("`n_probe`") closest buckets and scans their contents. Two coupled sub-problems:

- **Partitioning.** Choose the partition $\{P_1,\dots,P_C\}$ so that (i) buckets are balanced (no bucket dominates scan cost) and (ii) true neighbors of a query concentrate in few buckets (low *spillover*). Decision variant: does a balanced partition with bounded spillover exist? Optimization variant: minimize expected scanned vectors at target recall.
- **Adaptive probing.** Choose $p = p(q)$ *per query* (rather than a global constant) to reach recall $R@k$ while minimizing $\sum_{i\in \text{probed}} |P_i|$. Some queries (near a centroid) need $p=1$; boundary queries need many.

The objective is to minimize expected vectors scanned subject to a recall floor, with provable balance so worst-case latency is bounded.

## 2. Mathematical Foundations

Partitioning by Lloyd's algorithm ($k$-means) minimizes quantization distortion $\sum_x \|x-c_{q(x)}\|^2$ but gives **no balance guarantee** — cell sizes follow the data density and can be wildly skewed. Balance is a **balanced clustering / capacitated $k$-means** problem; the balanced version reduces to min-cost flow / assignment once centers are fixed (Bradley–Bennett–Demiriz constrained $k$-means), and balanced graph partitioning is NP-hard in general (related to minimum bisection).

Spillover is governed by the geometry: a query's true $k$-NN may straddle Voronoi boundaries; the probability that the $j$-th neighbor lies outside the top-$p$ probed cells depends on the distance distribution and the centroid configuration. The recall-vs-probe curve $R(p)$ is concave; under a Poisson/Cox process model of cell occupancy, expected scanned $= p\cdot \mathbb{E}|P_i|$, and the optimal **adaptive** rule probes until the marginal probability of capturing a missing neighbor falls below a threshold — a classic *optimal stopping* / sequential testing problem. Lower-bounding distances to unprobed cells (the bucket-to-query distance) yields a *certifiable* stopping rule (used in VBASE/relaxed-monotonicity): stop when the $k$-th candidate is closer than the nearest unprobed cell boundary.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** *Faiss* IVF/IVF-PQ (Johnson, Douze, Jégou, 2017) with $k$-means coarse quantizer and fixed `n_probe`; *SCANN* (Guo et al., ICML 2020) adds anisotropic vector quantization and learned partitioning that optimizes the inner-product-aware loss, pushing the recall–speed Pareto frontier. *SPANN* uses balanced, closure-augmented posting lists with replication of boundary points to cut spillover. Learned/early-termination: *LAET* and *Auncel* predict per-query `n_probe`.
- **Theory-SOTA.** Constrained/balanced $k$-means with min-cost-flow assignment (Bradley et al.); $(1+\epsilon)$-approximate balanced clustering via local search. Adaptive probing with certified stopping via distance lower bounds.

## 4. Upper Bound

Balanced assignment (fixed centers) is solvable optimally in polynomial time via min-cost flow; with the capacity constraint $|P_i|\le n/C(1+\delta)$, worst-case bucket scan is bounded by $n(1+\delta)/C$. For the joint center+assignment problem, local search gives $(1+\epsilon)$-approximation to the balanced $k$-means objective. Adaptive probing with a certified lower-bound stopping rule is **optimal per query** in the sense that it never scans a cell it can prove cannot contain a top-$k$ point — i.e., it matches the offline-optimal probe set under that certificate. SCANN's anisotropic quantization yields provably better inner-product distortion than isotropic PQ.

## 5. Lower Bound

Unconstrained balanced minimum bisection is NP-hard and hard to approximate within any constant under plausible assumptions (no PTAS for min-bisection believed). Hence *jointly* optimal balanced partitioning with minimal spillover is NP-hard. The recall–scan tradeoff inherits the high-dimensional barrier: achieving recall $1-\delta$ may require probing $p=\Omega(C^{1-o(1)})$ cells for adversarial near-boundary queries (concentration fails as dimension grows), reflecting the cell-probe/curse-of-dimensionality lower bounds. No instance can guarantee high recall with $p=O(1)$ for *all* queries.

## 6. The Gap

This is **partially solved**: balanced assignment and certified adaptive probing have clean optimal/near-optimal results, and SCANN-style anisotropic partitioning is well understood. What remains open: a *joint* partition+probe optimizer with end-to-end guarantees that adapts to the query distribution, and tight instance-dependent bounds on the minimal probe count for a recall target (the constant in $p$). The gap between balanced-assignment guarantees and the NP-hardness of joint partitioning is the genuinely open piece.

## 7. Current Research (as of June 2026)

- Learned coarse quantizers and partitioners that directly optimize recall@scan (SCANN successors) *(frontier — verify)*.
- Per-query adaptive `n_probe` via cheap learned predictors and certified early termination (Auncel/LAET line).
- Boundary-point replication and closure clustering (SPANN) to reduce spillover without unbalancing.
- Hybrid IVF+graph (e.g., IVF cells searched by mini-graphs) reducing scan within probed cells.
- Groups: Google Research (SCANN), Meta FAISS, Microsoft (SPANN), academic ANN-benchmark community.

## 8. Future Work

- Tight, distribution-aware lower bounds on probe count for a recall target.
- Online rebalancing of partitions under streaming inserts (links to streaming-ANN problem).
- Joint optimization of $C$, balance slack $\delta$, and adaptive probe policy as a single objective.
- Theoretical analysis of anisotropic / score-aware quantization's recall gains.

## 9. Key References

- **[SOTA]** Ruiqi Guo, Philip Sun, Erik Lindgren, Quan Geng, David Simcha, Felix Chern, Sanjiv Kumar. *Accelerating Large-Scale Inference with Anisotropic Vector Quantization (SCANN).* ICML, 2020.
- **[SOTA]** Jeff Johnson, Matthijs Douze, Hervé Jégou. *Billion-scale Similarity Search with GPUs (Faiss).* IEEE Big Data / arXiv:1702.08734, 2017.
- **[Foundational]** Hervé Jégou, Matthijs Douze, Cordelia Schmid. *Product Quantization for Nearest Neighbor Search.* IEEE TPAMI, 2011.
- **[Foundational]** Paul S. Bradley, Kristin P. Bennett, Ayhan Demiriz. *Constrained K-Means Clustering.* Microsoft Research TR, 2000.
- **[SOTA]** Qi Chen et al. *SPANN: Highly-efficient Billion-scale Approximate Nearest Neighbor Search.* NeurIPS, 2021.

---
*Part of the [DBMS Research catalog](../../README.md).*
