# Cache-oblivious in-memory sorting

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/cache-oblivious-sorting` · **Status:** partially-solved

## 1. Problem Statement

Sort $N$ keys in main memory so that the algorithm is **simultaneously** (a) **cache-efficient** — optimal block transfers across an *unknown* multi-level memory hierarchy (no tuning of cache size $M$ or line size $B$); (b) **SIMD-efficient** — exploits wide vector units (AVX-512, SVE, GPU lanes); and (c) **branch-efficient** — avoids unpredictable branches that stall deep pipelines. The challenge is that these three goals pull in different directions: cache-oblivious algorithms (funnelsort) use recursive merging with irregular control flow that resists vectorization, while the fastest SIMD sorts (bitonic networks, vectorized quicksort) are cache- and architecture-*specific*. The problem: a single sorting routine, **portable across architectures**, that is provably I/O-optimal *and* practically SIMD/branch-optimal without per-machine retuning.

Variants: (a) **comparison sort** of fixed-width keys; (b) **key+payload / row sort** (movement cost dominates); (c) **integer/radix** sort (different lower bounds); (d) **string sort**. Decision/optimization: minimize cache misses, instructions, and branch mispredicts jointly — a multi-objective target where the "optimum" depends on the architecture's cost vector.

## 2. Mathematical Foundations

Two models coexist. **Cache-oblivious (ideal-cache) model** (Frigo–Leiserson–Prokop–Ramachandran): two levels, cache of $M$ words and lines of $B$ words, **optimal replacement**, and the algorithm *does not know* $M,B$. Optimal sorting cost is
$$\Theta\!\Big(\tfrac{N}{B}\log_{M/B}\tfrac{N}{B}\Big) \ \text{cache misses},$$
matching the external-memory bound (Aggarwal–Vitter) but achieved obliviously by **funnelsort** / **lazy funnelsort** (Brodal–Fagerberg) under the **tall-cache assumption** $M = \Omega(B^2)$. In the comparison model, work is $\Theta(N\log N)$ (information-theoretic $\log N!$ bound). **SIMD sorting** rests on **sorting networks** — Batcher's bitonic ($O(N\log^2 N)$ comparators) and AKS ($O(\log N)$ depth, impractical constants) — which are *data-oblivious* and thus branch-free. **Branch efficiency** is captured by counting mispredictions; randomized/oblivious partitioning (e.g., **BlockQuicksort**, Edelkamp–Weiß) converts data-dependent branches into predicated SIMD/cmov operations, trading comparisons for predictable control flow.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Lazy funnelsort is cache-oblivious-optimal and cache-oblivious-optimal for the cache-oblivious model; multicore/parallel cache-oblivious sorting (low-depth cache-oblivious, Blelloch–Gibbons–Simhadri) is span- and cache-optimal. **Systems-SOTA:** The fastest in-memory sorts are explicitly vectorized: **AVX-512 sorting** (Bramas; Intel's **x86-simd-sort**, the AVX-512 quicksort behind NumPy's `np.sort` since 2023), **vectorized quicksort with bitonic small-array networks**, and **IPS⁴o** (In-place Parallel Super Scalar Samplesort, Axtmann–Witt–Ferizovic–Sanders) — the de-facto fastest parallel comparison sort, samplesort with branch-free $k$-way distribution. GPU sorting (CUB radix sort) dominates on accelerators. Databases (DuckDB, Umbra, ClickHouse) use radix/MSD sorts and vectorized merge for sort-merge join and `ORDER BY`. These are fast but **architecture-tuned**, not cache-oblivious.

## 4. Upper Bound

Cache misses: $O\!\big(\frac{N}{B}\log_{M/B}\frac{N}{B}\big)$ achieved obliviously by lazy funnelsort (ideal-cache model, tall-cache assumption); work $O(N\log N)$. Bitonic sort gives a **data-oblivious, branch-free, SIMD-friendly** sort with $O(N\log^2 N)$ work and depth $O(\log^2 N)$ — extra $\log N$ work traded for perfect predictability and vectorizability. **Samplesort/IPS⁴o** achieves $O(N\log N)$ work with branch-free $k$-way partitioning and near-optimal cache behavior *with* knowledge of cache parameters (tuned, not oblivious), and scales to many cores in-place. Vectorized AVX-512 quicksort reaches the practical instruction-throughput frontier on its target ISA. No single published algorithm provably attains all three optima simultaneously and portably.

## 5. Lower Bound

Comparison sorting requires $\Omega(N\log N)$ comparisons (information-theoretic decision-tree bound). Cache misses are lower-bounded by $\Omega\!\big(\frac{N}{B}\log_{M/B}\frac{N}{B}\big)$ in the external-memory/cache model (Aggarwal–Vitter; carries to cache-oblivious), and Brodal–Fagerberg show the **tall-cache assumption is necessary** — without $M=\Omega(B^2)$, no cache-oblivious algorithm can match the optimal cache-aware sorting bound (a *separation* between cache-oblivious and cache-aware sorting). Sorting-network **depth** lower bounds (any comparator network sorting $N$ has depth $\Omega(\log N)$) bound SIMD parallel-step counts. Branch-misprediction lower bounds tie to the comparison count for data-dependent algorithms. These bounds live in distinct models, and a *combined* lower bound over the joint (cache × SIMD × branch) cost is not established.

## 6. The Gap

Each axis is individually well-understood, but the **joint optimum is open and partly impossible**: Brodal–Fagerberg prove cache-oblivious sorting *cannot* match cache-aware sorting without the tall-cache assumption, so perfect obliviousness has a provable cost. In practice the gap is that the fastest sorts (IPS⁴o, AVX-512 quicksort, CUB radix) are **architecture-tuned** — they pick fan-out, base-case size, and vector width per machine — whereas cache-oblivious funnelsort is portable but slower in absolute instructions and hard to vectorize (irregular merging). No published routine is simultaneously cache-oblivious-optimal, branch-free, and SIMD-saturating with portable performance. Closing it means either a vectorizable cache-oblivious sort competitive with tuned samplesort, or a principled auto-tuning theory that recovers obliviousness's portability with tuned speed.

## 7. Current Research (as of June 2026)

Directions: **portable SIMD sorting** via libraries like Google **Highway** (`vqsort`) abstracting over AVX-512/SVE/NEON, narrowing the architecture-specific gap *(frontier — verify)*; continued refinement of **IPS⁴o** and branch-free samplesort for many-core and NUMA; **learned / adaptive base-case selection**; GPU and heterogeneous sorting (CUB, ONESweep radix). Theory: cache-oblivious + parallel (low-span) sorting, and whether vectorizable funnel structures can close the constant-factor gap. People/groups: Sanders (KIT, IPS⁴o/samplesort), Brodal–Fagerberg (Aarhus, cache-oblivious), Bramas / Intel x86-simd-sort, Blelloch–Gibbons (CMU, parallel cache-oblivious), database engine teams (Neumann/Leis TUM, DuckDB) for sort-merge and `ORDER BY`.

## 8. Future Work

- A provably cache-oblivious sort that is also SIMD-saturating and branch-free with portable constants — or a sharp impossibility separating the three goals.
- Tight *joint* lower bounds in a combined cache×SIMD×branch cost model.
- Auto-tuning / learned cost models that recover near-optimal parameters per architecture from a single portable kernel.
- Cache-oblivious *parallel* (low-span) sorting matching tuned IPS⁴o on real many-core hardware.
- Payload-aware sorting (heavy rows) and string/integer-radix variants under the same joint criteria.

## 9. Key References

- **[Foundational]** Frigo, Leiserson, Prokop, Ramachandran. *Cache-Oblivious Algorithms.* FOCS 1999 / ACM TALG, 2012. — [DOI](https://doi.org/10.1145/2071379.2071383)
- **[Foundational]** Brodal, Fagerberg. *Cache Oblivious Distribution Sweeping* and *On the Limits of Cache-Obliviousness.* ICALP 2002 / STOC, 2003. — [DOI (ICALP)](https://doi.org/10.1007/3-540-45465-9_37), [DBLP (STOC)](https://dblp.org/rec/conf/stoc/BrodalF03.html)
- **[Foundational]** Aggarwal, Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[SOTA]** Axtmann, Witt, Ferizovic, Sanders. *In-Place Parallel Super Scalar Samplesort (IPS⁴o).* ESA, 2017 / J. ACM-style journal version. — [arXiv](https://arxiv.org/abs/1705.02257)
- **[SOTA]** Edelkamp, Weiß. *BlockQuicksort: Avoiding Branch Mispredictions in Quicksort.* ESA 2016 / ACM JEA, 2019. — [arXiv](https://arxiv.org/abs/1604.06697), [DOI (JEA)](https://doi.org/10.1145/3274660)
- **[SOTA]** Bramas. *A Novel Hybrid Quicksort Algorithm Vectorized using AVX-512.* IJACSA, 2017; Intel *x86-simd-sort* (NumPy backend), 2023. — [arXiv](https://arxiv.org/abs/1704.08579)

## 10. Worked Example

Sort $N=2^{30}\approx 10^9$ 8-byte keys. Cache line $B=64$ B $=8$ keys; last-level cache $M=2^{23}$ keys (64 MB). Tall-cache holds since $M=2^{23}\gg B^2=64$.

**Cache-oblivious bound.** Optimal misses $=\Theta\!\big(\tfrac{N}{B}\log_{M/B}\tfrac{N}{B}\big)$. Here $\tfrac{N}{B}=2^{27}$, and $\log_{M/B}\tfrac{N}{B}=\log_{2^{20}}2^{27}=\tfrac{27}{20}\approx 1.35$. So $\approx 2^{27}\times 1.35\approx 1.8{\times}10^8$ cache misses — essentially **two passes** over memory. Lazy funnelsort achieves this *without knowing* $M$ or $B$.

**Contrast with naive merge sort** (oblivious to cache, leaf runs of size 1): merging at the line granularity costs $\Theta(\tfrac{N}{B}\log_2\tfrac{N}{B})=2^{27}\times 27\approx 3.6{\times}10^9$ misses — a $20\times$ penalty, because the merge fan-in of 2 ignores that $M/B=2^{20}$ runs could be merged per pass.

**SIMD tension.** A Batcher bitonic base case for 16 keys uses $\tfrac{1}{4}\log^2 16=4$ comparator stages, fully branch-free and AVX-512-vectorizable — but its $O(N\log^2 N)$ work loses the $\log N$ factor that funnelsort keeps, illustrating why no single routine yet wins on all three axes.

---
*Part of the [DBMS Research catalog](../../README.md).*
