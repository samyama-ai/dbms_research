# GPU group-by and aggregation under skew

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/gpu-aggregation-skew` · **Status:** empirically-open

## 1. Problem Statement
Given a relation $R$ with $n$ tuples, a grouping key set $G$, and an aggregate function $f$ (SUM, COUNT, MIN/MAX, or a holistic/distinct aggregate), compute $\gamma_{G, f}(R)$ on a GPU while keeping all SIMT lanes (warps/wavefronts) productively utilized. The hard instances are **heavy-hitter skew**: a small number of keys absorb a large fraction of tuples, so the standard parallel strategy — per-thread or per-group atomic updates into a shared hash table — serializes on the contended slots.

- **Optimization variant (primary):** minimize wall-clock time (equivalently maximize effective aggregate throughput, tuples/s) subject to a fixed device memory budget.
- **Decision variant:** given a time budget $T$ and skew profile, does an atomics-free schedule exist that finishes within $T$?
- **Counting variant:** for distinct-style aggregates (COUNT DISTINCT, quantiles), the per-group state itself is a sketch; the problem couples placement with approximate-counting accuracy.

"Atomics-free" is the design constraint: avoid global-memory `atomicAdd` contention as the throughput-limiting resource under skew.

## 2. Mathematical Foundations
Let the multiset of group sizes be $\{n_1 \ge n_2 \ge \dots \ge n_k\}$ with $\sum_i n_i = n$, often modeled as Zipfian, $n_i \propto i^{-z}$. The **skew** is captured by the largest group fraction $\rho = n_1/n$ and by the entropy $H = -\sum_i (n_i/n)\log(n_i/n)$.

A work-depth (PRAM-style) model bounds an aggregation schedule by work $W = \Theta(n)$ and depth $D$. Naive atomic accumulation on the hottest key forces a critical path $D = \Omega(n_1) = \Omega(\rho n)$ when updates to one location must serialize (a contention/CRCW-arbitration cost). A **partial-aggregation tree** over $p$ lanes reduces hot-key depth to $D = \Omega(\log p + n_1/p)$ by combining within thread-local/warp-local accumulators before a final reduction — exploiting the algebraic monoid structure $(f, \oplus)$ of decomposable aggregates (SUM/COUNT/MIN/MAX are commutative monoids; AVG is a pair; holistic aggregates are not decomposable, which is what makes them hard).

The achievable throughput is also bounded by the roofline model: $\text{perf} \le \min(\text{peak FLOP/s},\, I \cdot \text{BW})$ where $I$ is arithmetic intensity and BW is HBM bandwidth; group-by is memory-bound ($I$ small), so the objective is effectively to convert random-access atomic traffic into coalesced, contention-free streaming.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Per-thread/per-warp local hash tables with a final merge, used in HeavyDB/OmniSciDB, BlazingSQL, and **NVIDIA cuDF / libcudf** (RAPIDS) hash-based and sort-based group-by. Crystal (Shanbhag et al., SIGMOD 2020) gives a tiled, atomics-minimizing GPU operator library that is a common baseline.
- Two-phase aggregation (local partial aggregation then global merge) and **sort-based group-by** (radix/merge sort then segmented reduction) sidestep contention entirely; sort-based wins under extreme distinctness, hash wins under low cardinality.
- Karnagel et al. and Rui & Tu studied GPU hash aggregation contention; **shuffle/ballot-based warp-cooperative aggregation** (using `__shfl`/`__match_any` to pre-combine identical keys inside a warp) is the standard atomics-reduction trick.

## 4. Upper Bound
With a partial-aggregation tree across $p = \Theta(n/\log n)$ lanes, decomposable aggregates run in $O(n)$ work and $O(\log n)$ depth in the CREW-PRAM / work-depth model — **skew-independent**, because hot keys are folded locally before any shared write. Warp-level pre-aggregation reduces global atomic traffic for the hottest key by up to the warp width (32/64). Sort-based group-by achieves $O(n)$ work via radix sort (bounded key width) plus an $O(n)$ segmented scan, again independent of $\rho$. These bounds assume the per-lane accumulator state $O(k_\text{local})$ fits in registers/shared memory.

## 5. Lower Bound
Any comparison/aggregation must read every tuple: $\Omega(n)$ work, and on a bandwidth-bound device $\Omega(n/\text{BW})$ time (a roofline lower bound). For atomic-update schemes specifically, concurrent updates to a single location are serialized by the CRCW arbitration model, giving the $\Omega(\rho n)$ critical path that motivates the problem. When per-group state cannot be merged cheaply (holistic aggregates such as MEDIAN, or COUNT DISTINCT requiring exact answers), an information-theoretic argument forces $\Omega(n)$ state in the worst case, and sketch-based relaxations trade a provable $(\varepsilon,\delta)$ error for sublinear state. No unconditional super-linear lower bound is known; the difficulty is constant-factor and contention-structural, which is why the problem is **empirically-open** rather than closed.

## 6. The Gap
Theory says decomposable aggregation is skew-independent at $O(\log n)$ depth. In practice, throughput on adversarial Zipfian inputs still collapses by large factors versus uniform, because: (a) local accumulator tables overflow shared memory when cardinality $k$ is large, forcing spills to high-latency global atomics; (b) the merge phase becomes the new bottleneck; (c) materializing a static partial-aggregation tree wastes lanes when skew is unknown until runtime. The gap is between the model (unlimited cheap local state) and hardware (tiny register/shared-memory budget, fixed warp width). Closing it means an **adaptive** operator that detects skew online and switches between warp-shuffle pre-aggregation, local hashing, and sort-based fallback without a global barrier — with a competitive-ratio guarantee against the unknown skew profile.

## 7. Current Research (as of June 2026)
- Adaptive hybrid hash/sort group-by that profiles cardinality and skew in a sampling pass, in cuDF and academic prototypes *(frontier — verify)*.
- Use of `__match_any_sync` / cooperative-groups reductions to push warp-level pre-aggregation further, and persistent-kernel designs that keep accumulators resident across tiles *(frontier — verify)*.
- Heterogeneous CPU+GPU aggregation that ships hot keys to the CPU and streams the long tail on the GPU (groups around Jens Teubner / TU Dortmund, Gustavo Alonso / ETH systems group, and the Heidelberg/HPI GPU-DB efforts) *(frontier — verify)*.
- Sketch-aware grouped aggregation (HyperLogLog/Count-Min as per-group state) for distinct and quantile aggregates on GPU.

## 8. Future Work
- A provable competitive-ratio scheduler against worst-case skew that is oblivious to the distribution at launch.
- Holistic and distinct aggregates with bounded, mergeable per-group sketch state and end-to-end error guarantees.
- Co-design with HBM3/grace-hopper unified memory so accumulator spills don't cliff into PCIe traffic.
- Cost-model integration so the query optimizer picks hash vs sort vs hybrid from cardinality/skew estimates.

## 9. Key References
- **[SOTA]** A. Shanbhag, S. Madden, X. Yu. *A Study of the Fundamental Performance Characteristics of GPUs and CPUs for Database Analytics.* SIGMOD, 2020. (Crystal operator library.)
- **[SOTA]** T. Karnagel, R. Mueller, G. Lohman, et al. *Optimizing GPU-accelerated Group-By and Aggregation.* ADMS @ VLDB, 2015.
- **[SOTA]** B. Rui, Y.-C. Tu. *Fast Equi-Join Algorithms on GPUs: Design and Implementation* / hash-aggregation studies. (GPU contention analysis.)
- **[Foundational]** G. Graefe. *Query Evaluation Techniques for Large Databases.* ACM Computing Surveys, 1993. (Partial aggregation, decomposable aggregates.)
- **[Survey]** S. Breß, M. Heimel, N. Siegmund, et al. *GPU-Accelerated Database Systems: Survey and Open Challenges.* TLDKS, 2014.
- **[Foundational]** S. Williams, A. Waterman, D. Patterson. *Roofline: An Insightful Visual Performance Model for Multicore Architectures.* CACM, 2009.

---
*Part of the [DBMS Research catalog](../../README.md).*
