---
id: 13-column-stores-olap/vectorized-vs-compiled
title: "Vectorized vs. Compiled Execution Frontier"
topic: 13-column-stores-olap
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Vectorized vs. Compiled Execution Frontier

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/vectorized-vs-compiled` · **Status:** empirically-open
> **Verification note:** The VLDB 2018 "Compiled and Vectorized Queries" study's fifth author is Andrew Pavlo, not Mühleisen (DBLP KerstenLKNPB18); the reference list has been corrected accordingly.

## 1. Problem Statement
Analytical query engines realize a physical plan in one of two dominant paradigms:
- **Vectorized (interpreted) execution** (MonetDB/X100–Vectorwise style): operators process **batches** (vectors of ~1K–4K values) through pre-compiled, type-specialized primitives; control flow is interpreted at batch granularity.
- **Data-centric JIT compilation** (HyPer style): the plan is compiled to native code (LLVM/Cranelift/C++) that fuses operators into tight **pipelines**, keeping tuples in registers across operator boundaries ("push" model, produce/consume).

The problem: **for a given query, plan fragment, hardware, and data, decide which paradigm — or which hybrid — minimizes end-to-end latency (and compilation + runtime cost), and how to construct that hybrid.** Sub-questions:
- **Decision/classification:** per pipeline, choose interpret vs. compile (the "adaptive execution" decision).
- **Construction:** how to *fuse* the two so vectorized primitives run inside compiled pipelines and vice versa.
- **Cost modeling:** predict the crossover point as a function of cardinality, selectivity, operator mix, instruction cache, and compile latency.

It is **empirically-open**: there is broad experimental understanding but no closed-form or provably-optimal decision procedure.

## 2. Mathematical Foundations
The frontier is fundamentally a **microarchitectural cost model**, not a complexity-class question. Relevant formalisms:
- **Roofline model:** an operator's achievable throughput is $\min(\text{peak FLOP/s or ops/s},\ \text{AI} \times \text{bandwidth})$ where arithmetic intensity $\text{AI} = \text{ops}/\text{bytes}$. Vectorized execution maximizes memory-bandwidth utilization and SIMD width but materializes intermediate vectors (more bytes); compilation maximizes **data locality / register residency** (fewer bytes) but risks instruction-cache pressure and loses easy SIMD.
- **Amortization model:** total time $T = c_{\text{compile}} + n \cdot t_{\text{exec}}$. Compilation wins iff $n \cdot (t^{\text{vec}}_{\text{exec}} - t^{\text{jit}}_{\text{exec}}) > c_{\text{compile}}$ — a per-query **break-even cardinality**.
- **Pipeline-parallelism / instruction-level-parallelism** arguments: vectorized loops expose ILP and auto-vectorization to the compiler; fused pipelines expose **data locality** but tight dependency chains can stall. The trade-off is captured by tuple-at-a-time vs. operator-at-a-time **interpretation-overhead vs. materialization-overhead** decomposition (Boncz et al.; Kersten et al.).

## 3. State of the Art (SOTA)
- **Foundational systems:** MonetDB/X100 (Boncz, Zukowski, Nes, CIDR 2005) — vectorized; HyPer (Neumann, VLDB 2011) — "Efficiently Compiling Efficient Query Plans for Modern Hardware," data-centric LLVM compilation.
- **Head-to-head study:** Kersten, Leis, Kemper, Neumann, Mühleisen, Boncz — *"Everything You Always Wanted to Know About Compiled and Vectorized Queries But Were Afraid to Ask"* (VLDB 2018) — the definitive empirical comparison; conclusion: both reach similar peak performance, differ on compile latency, profiling, and operator mix.
- **Hybrids:** **Umbra** (Neumann/Freitag) — adaptive execution that starts interpreted and compiles hot pipelines; **Flounder/ROF**; **DuckDB** — vectorized push-based with morsel parallelism; Velox (Meta) vectorized library; Photon (Databricks, SIGMOD 2022) — vectorized C++ engine chosen over codegen for engineering reasons; LingoDB / MLIR-based query compilation *(frontier)*.

## 4. Upper Bound
There is **no complexity-theoretic upper bound**; the meaningful "bound" is the **roofline ceiling** — an operator cannot exceed memory bandwidth or peak SIMD throughput. Empirically, both paradigms reach within a small constant factor of this ceiling on well-tuned kernels (Kersten et al. 2018), so the *achievable* upper bound on per-tuple cost is set by hardware, and the open question is which paradigm reaches it for a given operator/selectivity, and whether a hybrid strictly dominates both — currently shown only empirically, per-workload.

## 5. Lower Bound
No nontrivial lower bound is known beyond the trivial $\Omega(n)$ scan and the hardware roofline ceiling. The decision of *which* paradigm is faster is **not** known to be hard — it is a regression/modeling problem, and the absence of a clean lower bound is precisely why the problem is "empirically-open": we lack a model that *provably* identifies the optimal paradigm, and adversarial workloads can be constructed where any fixed static rule is far from optimal (motivating adaptivity).

## 6. The Gap
The gap is **not** between matching mathematical bounds but between **empirical understanding and a predictive theory**. We know *that* the crossover exists and roughly *where* (compile-latency amortization, operator mix, data size), but no portable, hardware-parameterized model predicts the optimal interpret/compile/hybrid choice per pipeline with guarantees. Closing it requires either (a) a validated analytical cost model spanning microarchitectures, or (b) an adaptive runtime with provable competitive ratio vs. the offline-optimal paradigm choice. Adaptive systems (Umbra) close it pragmatically but without guarantees.

## 7. Current Research (as of June 2026)
Active directions: **MLIR/LLVM-based unified IRs** (LingoDB, Apache DataFusion's evolving codegen, Velox + compilation experiments) that let a single plan emit either vectorized or compiled code; learned cost models / bandits choosing paradigm per pipeline; **adaptive recompilation** triggered by observed cardinalities (Umbra's flying-start). GPU/accelerator execution (HeavyDB, Crystal, Proteus) reopens the question since SIMT changes the roofline. Groups: TUM (Neumann, Kemper), CWI (Boncz, Mühleisen/DuckDB), Databricks (Photon), Meta (Velox). Frontier claim: MLIR-lowered engines matching hand-tuned both paradigms with one codebase *(frontier — verify)*.

## 8. Future Work
- A portable, microarchitecture-parameterized analytical model with prediction error bounds.
- Adaptive executors with **provable competitive ratios** against offline-optimal paradigm selection.
- Fine-grained **intra-pipeline** hybridization (compiled control flow calling vectorized SIMD kernels) as the default.
- Extending the frontier analysis to GPUs/FPGAs and to disaggregated / cloud storage where I/O dominates.

## 9. Key References
- **[Foundational]** Boncz, Zukowski, Nes. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR 2005. — [PDF](https://www.cidrdb.org/cidr2005/papers/P19.pdf)
- **[Foundational]** Neumann. *Efficiently Compiling Efficient Query Plans for Modern Hardware.* VLDB 2011. — [PDF](https://www.vldb.org/pvldb/vol4/p539-neumann.pdf)
- **[SOTA/Survey]** Kersten, Leis, Kemper, Neumann, Pavlo, Boncz. *Everything You Always Wanted to Know About Compiled and Vectorized Queries But Were Afraid to Ask.* VLDB 2018. — [DBLP](https://dblp.org/rec/journals/pvldb/KerstenLKNPB18.html)
- **[SOTA]** Kohn, Leis, Neumann. *Adaptive Execution of Compiled Queries.* ICDE 2018. — [DBLP](https://dblp.org/rec/conf/icde/KohnL018.html)
- **[SOTA]** Behm et al. *Photon: A Fast Query Engine for Lakehouse Systems.* SIGMOD 2022. — [DOI](https://doi.org/10.1145/3514221.3526054)

## 10. Worked Example

Consider one pipeline executed $n$ times (one invocation per output tuple group). Measured per-tuple execution: vectorized $t^{\text{vec}}_{\text{exec}}=5$ ns, compiled $t^{\text{jit}}_{\text{exec}}=2$ ns, with a one-time JIT cost $c_{\text{compile}}=30{,}000$ ns (30 µs).

Apply the amortization model $T = c_{\text{compile}} + n\cdot t_{\text{exec}}$. Break-even cardinality:
$$ n^* = \frac{c_{\text{compile}}}{t^{\text{vec}}_{\text{exec}} - t^{\text{jit}}_{\text{exec}}} = \frac{30{,}000}{5-2} = 10{,}000 \text{ tuples}. $$

- At $n=1{,}000$: vectorized $T=5{,}000$ ns vs compiled $T=30{,}000+2{,}000=32{,}000$ ns. **Interpret wins** (small query — compile cost dominates).
- At $n=100{,}000$: vectorized $T=500{,}000$ ns vs compiled $T=30{,}000+200{,}000=230{,}000$ ns. **Compile wins** (~$2.2\times$).

The crossover at $n^*=10{,}000$ is exactly what adaptive systems like Umbra exploit: start interpreting, and only pay $c_{\text{compile}}$ once a pipeline is observed to exceed $n^*$. Note $n^*$ shifts with hardware ($t_{\text{exec}}$) and operator mix, which is why no single static rule is optimal.

---
*Part of the [DBMS Research catalog](../../README.md).*
