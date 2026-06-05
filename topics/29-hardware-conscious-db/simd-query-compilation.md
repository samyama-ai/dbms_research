# SIMD-vectorizable query compilation

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/simd-query-compilation` · **Status:** empirically-open

## 1. Problem Statement
Given a relational query, automatically generate operator code that is **fully vectorized** — every hot loop executes as wide SIMD (AVX-512, SVE, NEON) or SIMT (GPU warp) lanes — while correctly handling **control-flow divergence** (predicates, NULLs, variable-length strings, hash collisions, mixed data types) and avoiding gather/scatter and masking penalties. The challenge: relational operators are full of data-dependent branches, but SIMD wants branch-free, lane-uniform work.

Variants: (a) **decision/feasibility** — can a given operator pipeline be lowered to divergence-free vector code? (b) **optimization** — generate code minimizing executed-mask waste / maximizing lane utilization across the type-heterogeneous plan; (c) the practical question — do it *automatically* rather than by hand-written intrinsics per operator.

## 2. Mathematical Foundations
The formal substrate is **dataflow vectorization / if-conversion**: replacing control flow by predicated (masked) execution, and **selection-vector** semantics where an operator carries a set of active lane indices. Lane utilization is $U = \mathbb{E}[\,|\text{active lanes}|/w\,]$ for vector width $w$; under predicate selectivity $\sigma$ and independent lanes, naive masking gives $U=1$ but *useful* throughput $\sigma$, while compaction restores density at the cost of a permute. Divergence cost on SIMT is the number of distinct paths a warp serially executes. The relevant theory borrows from **polyhedral compilation** (loop nests as integer polyhedra, affine scheduling) and **SLP/loop vectorization** legality (dependence analysis); divergence handling connects to branch-divergence reconvergence analysis. Type heterogeneity makes lane width itself a per-column variable.

## 3. State of the Art (SOTA)
**Systems-SOTA:** the vectorized-vs-compiled debate is anchored by MonetDB/X100 (Boncz–Zukowski–Nes, CIDR 2005) and HyPer's data-centric LLVM compilation (Neumann, VLDB 2011); their synthesis is the *relaxed operator fusion / explicit SIMD vectorization in compiled engines* line — Menon, Mowry, Pavlo, "Relaxed Operator Fusion" (VLDB 2017) and the **Voila / "Everything You Always Wanted to Know About Compiled and Vectorized Queries"** study (Kersten, Leis, Neumann et al., VLDB 2018). DuckDB and Velox are the modern vectorized engines; Photon (Databricks, SIGMOD 2022) is the production vectorized C++ engine. For SIMD-by-construction, Polychroniou–Raman–Ross (SIGMOD 2015) gave hand-tuned "Rethinking SIMD Vectorization for In-Memory Databases."

## 4. Upper Bound
No clean asymptotic bound — vectorization is a constant-factor (throughput) game. The best *automatic* result is that operator pipelines expressible over **selection vectors + masked primitives** can be lowered to vector code achieving near-peak lane utilization after a **compaction/permute** step, with overhead $O(1)$ permutes per branch. Polychroniou et al. and Menon et al. demonstrate within-small-constant-of-peak SIMD for scans, hashing, and partitioning; the upper bound is "linear passes with bounded gather/scatter," but constants depend heavily on the hardware permute/gather latency.

## 5. Lower Bound
Lower bounds here are about **inherent divergence**, not asymptotics. Some operators have data-dependent control flow that *no* lowering removes (e.g., variable-length UTF-8 decoding, regex, hash-probe collision chains): worst-case useful throughput is $\le \sigma w$ for selectivity $\sigma$, and divergent warps pay up to $w\times$ on SIMT. There is no NP-hardness landmark; rather, the limit is information-theoretic/architectural — gather/scatter bandwidth and permute throughput cap achievable speedup (a Roofline-style bound), and **optimal vectorizing schedule selection** (which branches to predicate vs. compact vs. split) is combinatorially hard in the polyhedral framework.

## 6. The Gap
The math gap is small (constant factors); the gap that keeps it **empirically open** is the *automation* gap: hand-written intrinsics still beat compiler auto-vectorization on real operator code, especially across data types and with NULLs/strings. We lack a compiler that, from declarative operator specs, reliably emits divergence-managed vector code matching expert intrinsics on AVX-512 *and* SVE *and* SIMT. Closing it needs cost-modeled lowering choices (mask vs. compact vs. scalar-fallback) and portable abstractions.

## 7. Current Research (as of June 2026)
Directions: portable SIMD abstractions (std::simd, Google Highway, ISPC-style SPMD) integrated into query compilers; **Voila/auto-vectorizing IRs** for DBs *(frontier — verify)*; SVE/RVV (scale-vector) length-agnostic codegen for ARM/RISC-V servers *(frontier — verify)*; LLM/auto-tuning-assisted intrinsic synthesis. Groups: TUM (Neumann/Leis/Kersten), CMU (Pavlo/Menon), Columbia (Ross), Databricks (Photon), and the DuckDB/Velox communities.

## 8. Future Work
A retargetable, cost-driven vectorizing operator compiler with provable lane-utilization guarantees per selectivity; first-class divergence/compaction cost models; unified handling of variable-length and mixed-type columns; auto-tuning across AVX-512/SVE/RVV/SIMT from one source.

## 9. Key References
- **[Foundational]** P. Boncz, M. Zukowski, N. Nes. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR, 2005.
- **[Foundational]** T. Neumann. *Efficiently Compiling Efficient Query Plans for Modern Hardware.* VLDB, 2011.
- **[SOTA]** O. Polychroniou, A. Raman, K. A. Ross. *Rethinking SIMD Vectorization for In-Memory Databases.* SIGMOD, 2015.
- **[SOTA]** P. Menon, T. C. Mowry, A. Pavlo. *Relaxed Operator Fusion for In-Memory Databases.* VLDB, 2017.
- **[Survey]** T. Kersten, V. Leis, A. Kemper, T. Neumann, A. Pavlo, P. Boncz. *Everything You Always Wanted to Know About Compiled and Vectorized Queries But Were Afraid to Ask.* VLDB, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
