# GPU-accelerated spatial indexing

> **Topic:** Spatial & Spatiotemporal Databases · **ID:** `20-spatial-databases/gpu-spatial-index` · **Status:** empirically-open

## 1. Problem Statement
Design spatial index layouts and traversal algorithms that exploit massive GPU (SIMT) parallelism to answer **range**, **$k$NN**, and **spatial join** queries on $n$ objects in $\mathbb{R}^2/\mathbb{R}^3$ at high throughput, *without* the control-flow divergence and uncoalesced-memory penalties that cripple naive ports of CPU trees (R-tree, kd-tree, quadtree).

Variants:
- **Single-query latency** (one large range/$k$NN) vs **batched throughput** (millions of small queries).
- **Static index** (build once, query many) vs **streaming/updatable**.
- **Decision flavor:** map each query to a bounded, branch-uniform amount of work so warps stay coherent; **optimization flavor:** minimize $\max$ over a warp of per-thread work (load balance) subject to memory-coalescing constraints.

The core difficulty: tree search is inherently *irregular* (variable fanout, variable depth, data-dependent pruning) while GPUs reward *regular*, divergence-free, coalesced work.

## 2. Mathematical Foundations
Model the GPU abstractly as a **bulk-synchronous / massively-parallel** machine: $p$ threads in warps of width $w$ (e.g. 32). A warp's cost is the *maximum* over its threads (divergence: if a fraction execute a branch, all pay), and memory cost is the number of distinct cache lines touched (coalescing). Useful cost models include the **PRAM** family, **work–depth** ($W$ = total ops, $D$ = critical path; ideal speedup $W/p + D$), and external-memory style **$(M, B)$** models adapted to GPU shared memory and coalesced segments of $B$ words.

Range/join selectivity sets the *work*; the challenge is bounding *divergence* $\Delta$ and *uncoalesced accesses*. Space-filling curves (Z-order/Hilbert) reduce $d$-dimensional locality to 1-D so that nearby objects map to nearby, coalescible addresses; the relevant property is the curve's **dilation/locality bound**, $\|p-q\|$ vs. curve-distance, which controls how often a query interval fragments. $k$NN reduces to bounded priority selection; spatial join to a filter (MBR overlap) + refinement, with output size governed by the **AGM-style** bound on intersecting pairs.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** cuSpatial (RAPIDS) for point-in-polygon, trajectory ops, and quadtree-based joins; GPU LBVH (linear BVH over Morton codes, Karras-style radix construction) for range/ray/overlap; STIG and G-PICS for spatiotemporal/grid indexing; GPU $k$NN via FAISS / sorting-network selection. Grid- and SFC-based methods generally beat ported R-trees on GPUs because they are divergence-friendly.
- **Theory-SOTA:** work-optimal parallel BVH/Morton construction ($O(n)$ work, $O(\log n)$ depth) and parallel sorting underpin most systems.

## 4. Upper Bound
LBVH construction: $O(n)$ work and $O(\log n)$ depth (Karras 2012) in the work–depth model. Batched range/join via Morton sort + segmented intersection: $O(n\log n + K)$ work for $K$ reported pairs. $k$NN over a grid/LBVH: $O(\log n + k)$ expected per query under bounded density. These are *parallel* upper bounds; the open quantity is the **divergence-aware** constant: no analysis tightly bounds achieved warp efficiency $\Delta$ for adversarial spatial skew.

## 5. Lower Bound
In comparison-based settings, sorting (which SFC indexing relies on) is $\Omega(n\log n)$ work / $\Omega(\log n)$ depth. Reporting-style range queries inherit the output-sensitive $\Omega(\log n + K)$ barrier. There is **no tight lower bound on divergence/coalescing** for irregular tree traversal on the SIMT model — the practical gap is empirical, not a proven separation. $k$NN inherits decision-tree lower bounds for selection.

## 6. The Gap
Asymptotic work/depth bounds are essentially met by existing GPU constructions, yet *measured* performance is dominated by divergence and memory traffic that the asymptotics ignore. The problem is **empirically open**: we lack (a) a cost model whose predictions match observed warp efficiency, and (b) index layouts provably minimizing divergence for skewed/clustered data. Closing it means a divergence-aware model plus layouts that are simultaneously work-optimal *and* coherence-optimal.

## 7. Current Research (as of June 2026)
Directions: ray-tracing-core (RT-core) repurposing — encoding spatial range/$k$/join as BVH ray queries to offload traversal to fixed-function hardware *(frontier — verify)*; learned/partitioned grids that adapt cell size to local density to equalize warp load; GPU-resident updatable spatial indexes for streaming trajectories; and multi-GPU / out-of-core joins. Active groups: NVIDIA RAPIDS/cuSpatial, the G-PICS/STIG lineage (Gao, UT-Arlington area), and HPC-DB groups exploring RT-core acceleration *(frontier — verify)*.

## 8. Future Work
- A predictive divergence-and-coalescing cost model validated against hardware.
- Provably load-balanced layouts for clustered/skewed spatial data.
- Efficient *updates* (insert/delete) on GPU spatial indexes without full rebuild.
- Exploiting tensor/RT cores for spatial predicates; energy-per-query as an objective.

## 9. Key References
- **[Foundational]** Guttman. *R-trees: A Dynamic Index Structure for Spatial Searching.* SIGMOD, 1984. — [DOI](https://doi.org/10.1145/971697.602266)
- **[Foundational]** Karras. *Maximizing Parallelism in the Construction of BVHs, Octrees, and k-d Trees.* High-Performance Graphics, 2012. — [DBLP](https://dblp.org/rec/conf/egh/Karras12.html)
- **[SOTA]** Doraiswamy, Freire. *A GPU-Friendly Geometric Data Model and Algebra for Spatial Queries.* SIGMOD, 2020. — [arXiv](https://arxiv.org/abs/2004.03630), [DOI](https://doi.org/10.1145/3318464.3389774)
- **[SOTA]** RAPIDS cuSpatial. *GPU-Accelerated Spatial and Trajectory Data Management.* NVIDIA, 2019–2024. — [docs](https://docs.rapids.ai/api/cuspatial/stable/)
- **[Survey]** Blelloch, Maggs. *Parallel Algorithms.* (work–depth model), ACM Computing Surveys lineage. — [DBLP search](https://dblp.org/search?q=Blelloch+Maggs+Parallel+Algorithms)

## 10. Worked Example

Consider 4 points on a $4\times4$ grid, indexed by 2-bit-per-axis **Z-order (Morton)** codes, interleaving bits as $z = y_1x_1y_0x_0$:

| point | $(x,y)$ | bits $x{=}x_1x_0,\,y{=}y_1y_0$ | Morton $z$ |
|-------|---------|------------------|-----------|
| A | $(0,0)$ | $00,00$ | $0000=0$ |
| B | $(1,0)$ | $01,00$ | $0001=1$ |
| C | $(0,1)$ | $00,01$ | $0010=2$ |
| D | $(3,3)$ | $11,11$ | $1111=15$ |

Sorting by $z$ gives order $A(0),B(1),C(2),D(15)$ — contiguous in memory, so a warp reading them is **coalesced**. A range query for the box $x\in[0,1],y\in[0,1]$ covers Morton interval $[0,3]$, which is *one* contiguous run capturing $A,B,C$ (and correctly excludes $D$ at $z=15$). One contiguous interval = zero divergence: every thread in the warp does identical work.

As a contrast, the geometrically adjacent cells $(1,1)$ and $(2,1)$ have Morton codes $z=0011=3$ and $z=0110=6$ — the curve "jumps" by 3 across a column boundary even though the cells touch. So a wider query box can split into **several disjoint Morton runs**, each a separate coalesced segment. This is the **dilation/locality** term of Section 2: a geometrically simple query can fragment into up to $O(n^{1-1/d})$ runs, the unavoidable SFC penalty that pushes warp work above the ideal single-run case.

---
*Part of the [DBMS Research catalog](../../README.md).*
