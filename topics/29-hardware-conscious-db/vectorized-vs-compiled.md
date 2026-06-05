# Vectorized vs compiled execution unification

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/vectorized-vs-compiled` · **Status:** partially-solved

## 1. Problem Statement
Two dominant query-execution paradigms exist. **Vectorized interpretation** (MonetDB/X100, Vectorwise) processes data in cache-resident batches of tuples through pre-compiled primitive operators, amortizing interpretation overhead across a vector. **Data-centric compilation** (HyPer's produce/consume model, LLVM-JIT) generates tight machine code that fuses operators and keeps tuples in registers across a pipeline. Each wins on different queries and hardware. The problem: a **principled, predictive model** that, given a query and a target machine, says which paradigm (or which hybrid) executes fastest — and a unified engine that can choose per-pipeline.

- **Optimization variant (primary):** for query $Q$ on hardware $H$, predict and select the execution strategy $s\in\{\text{vectorized}, \text{compiled}, \text{hybrid}\}$ minimizing execution time, including compilation latency for short queries.
- **Decision variant:** given $Q$, $H$, is vectorized strictly faster than compiled? (The crossover-prediction question.)

This is "partially-solved": the trade-offs are well characterized empirically and a unifying framework (Voila / "Everything you always wanted to know...") exists, but a closed-form predictive cost model remains incomplete.

## 2. Mathematical Foundations
Model execution cost as $T = T_\text{cpu} + T_\text{mem} + T_\text{compile}$. The two paradigms trade these terms differently:

- **Vectorized** maximizes per-primitive throughput via SIMD and out-of-order parallelism; cost $\approx \sum_{op} \frac{n}{w_{op}} c_{op} + n\cdot m_\text{materialize}$, where $w_{op}$ is vector/SIMD width and $m_\text{materialize}$ is the cost of writing intermediate vectors to L1/L2 between operators (the **materialization tax**).
- **Compiled** fuses operators so intermediates stay in registers: cost $\approx \sum_{op} n\cdot c'_{op}$ with little materialization but a fixed $T_\text{compile}$ and worse **instruction-level parallelism / SIMD auto-vectorization** for complex pipelines.

The crossover is governed by the **memory hierarchy** (cache miss penalty), **SIMD width**, **branch predictability** (selective operators favor vectorized branch-free primitives), and **pipeline depth**. Formally it is a min over two convex-ish cost surfaces in the parameters $(n, \text{selectivity}, \text{pipeline length}, w, \text{cache latency})$; the predictive model seeks the crossover manifold $T_\text{vec} = T_\text{comp}$. The roofline model frames both as approaching memory-bandwidth bound for scans, diverging on compute-heavy or branch-heavy pipelines.

## 3. State of the Art (SOTA)
- **Foundational paradigms:** Boncz, Zukowski, Nes, *MonetDB/X100: Hyper-Pipelining Query Execution* (CIDR 2005) — vectorization. Neumann, *Efficiently Compiling Efficient Query Plans for Modern Hardware* (VLDB 2011) — data-centric compilation (HyPer).
- **The unifying study:** Kersten, Leis, Kemper, Neumann, Pavlo, Boncz, *Everything You Always Wanted to Know About Compiled and Vectorized Queries But Were Afraid to Ask* (VLDB 2018) — an apples-to-apples comparison establishing that the two are closer than assumed and each wins in specific regimes; this is the reference framing of the problem.
- **Voila** (Gubner & Boncz, VLDB 2021) — a DSL/framework generating both vectorized and compiled (and hybrid) engines from one specification, demonstrating a *continuum* rather than a binary.
- **Systems:** DuckDB (vectorized), Umbra (compiled, adaptive), Velox (vectorized library), SingleStore/Photon (hybrid). **Adaptive execution** (Kohn, Leis, Neumann, *Adaptive Execution of Compiled Queries*, ICDE 2018) switches between interpreted and compiled code at runtime based on query duration.

## 4. Upper Bound
There is no asymptotic complexity gap — both paradigms perform $\Theta(\text{plan-cost})$ work; the difference is **constant-factor** (instructions per tuple, cache traffic, compile latency). The strongest positive result is **adaptive/morsel-driven execution** (Kohn et al. 2018; Leis et al. *Morsel-Driven Parallelism*, SIGMOD 2014): start interpreting/vectorizing immediately, compile in the background, and switch — guaranteeing performance within a constant factor of the better of the two *for any query duration*, eliminating the compile-latency penalty for short queries. Voila shows a single code-generator can reach the better paradigm's performance per pipeline. Thus the "upper bound" is essentially solved operationally: you can get $\approx \min(T_\text{vec}, T_\text{comp})$ up to constants by adaptivity.

## 5. Lower Bound
Both paradigms are bounded below by the **roofline / memory-bandwidth limit** for scan-heavy queries: $\Omega(\text{bytes}/B)$, achieved by both, so neither can asymptotically dominate. The genuine lower bound is on **prediction**: choosing the optimal paradigm a priori requires predicting cache-miss rates, branch-misprediction rates, and auto-vectorization success, which depend on data distribution and the specific microarchitecture — quantities not known until execution and not captured by a closed-form cost model (a modeling/epistemic barrier, not a complexity one). There is no NP-hardness here; the "hardness" is the absence of an accurate static predictor across hardware generations.

## 6. The Gap
**Partially solved.** The operational gap is closed by adaptive execution and Voila-style unification: a modern engine can approach the minimum of the two strategies at runtime. What remains open is the **predictive cost model** — a portable, closed-form (or learned) function $T(Q, H, s)$ accurate enough to choose per pipeline *before* execution and to guide the optimizer, across CPUs, GPUs, and SIMD widths (AVX-512, SVE). Today's selection is heuristic (query duration, pipeline shape) or learned per-system, not a principled theory. Closing it means a microarchitecture-parameterized model whose crossover manifold matches measured behavior within tight error on unseen hardware — bridging the gap between "we can switch at runtime" and "we can predict the right choice in advance."

## 7. Current Research (as of June 2026)
- Voila and successor "one-spec, many-engines" code generators extended to GPUs and SIMD ISAs (SVE, AVX-512) (Boncz/CWI, Neumann/TUM) *(frontier — verify)*.
- Learned cost models that predict the vectorized/compiled crossover from query features and hardware counters, feeding the optimizer *(frontier — verify)*.
- Velox and DuckDB pushing vectorized execution as a portable library while exploring selective JIT for hot pipelines *(frontier — verify)*.
- Flying-start / adaptive compilation (Umbra's tiered compilation: interpret → fast baseline → optimized) refined for sub-millisecond queries *(frontier — verify)*.

## 8. Future Work
- A portable, microarchitecture-parameterized predictive model validated across CPU generations and GPUs.
- Per-pipeline (not per-query) paradigm selection with guarantees.
- Unifying GPU SIMT execution into the same vectorized/compiled continuum.
- Compilation-cost models accurate enough to make the compile-vs-interpret decision optimal for short and ad-hoc queries.

## 9. Key References
- **[Foundational]** P. Boncz, M. Zukowski, N. Nes. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR, 2005.
- **[Foundational]** T. Neumann. *Efficiently Compiling Efficient Query Plans for Modern Hardware.* VLDB, 2011.
- **[SOTA]** T. Kersten, V. Leis, A. Kemper, T. Neumann, A. Pavlo, P. Boncz. *Everything You Always Wanted to Know About Compiled and Vectorized Queries But Were Afraid to Ask.* VLDB, 2018.
- **[SOTA]** T. Gubner, P. Boncz. *Charting the Design Space of Query Execution Using VOILA.* VLDB, 2021.
- **[SOTA]** A. Kohn, V. Leis, T. Neumann. *Adaptive Execution of Compiled Queries.* ICDE, 2018.
- **[Foundational]** V. Leis, P. Boncz, A. Kemper, T. Neumann. *Morsel-Driven Parallelism: A NUMA-Aware Query Evaluation Framework for the Many-Core Age.* SIGMOD, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
