# Compiled vs. vectorized execution unification

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/compiled-vs-vectorized` · **Status:** empirically-open

## 1. Problem Statement

Modern analytical engines realize a physical plan through one of two dominant execution
paradigms. **Data-centric compilation** (HyPer/Umbra style) fuses the operators of a
pipeline into tight, branch-minimized machine code, keeping tuples in registers across
operator boundaries and eliminating interpretation overhead. **Vectorized interpretation**
(MonetDB/X100, DuckDB style) executes pre-compiled primitives over column-oriented batches
of a few thousand values, amortizing the per-operator dispatch cost over a batch and
exposing data-level parallelism (SIMD) and easy profiling.

The problem: **construct a principled framework — and an engine — that obtains the best of
both paradigms simultaneously**, rather than picking one statically. Concretely, given a
physical plan $P$, a target hardware profile $H$, and a compile-time budget $B$, decide
per pipeline (and possibly per operator) whether to *compile* or *vectorize* (or hybridize),
and *what* to generate, so as to minimize total query latency $T_{\text{compile}} + T_{\text{run}}$
while preserving adaptivity (profiling, late binding) and tolerable compile latency.

Variants: **decision** (compile vs. vectorize per pipeline given a cost model);
**optimization** (jointly minimize compile + run time over the space of code shapes);
**online** (switch paradigm mid-execution using runtime feedback, e.g., adaptive
recompilation when a tier's profile indicates a long-running pipeline).

## 2. Mathematical Foundations

Model a pipeline as a sequence of operators $o_1,\dots,o_k$ producing $n$ tuples. A
vectorized execution pays $\sum_i (c^{\text{disp}}_i \cdot \lceil n/v\rceil + c^{\text{prim}}_i \cdot n)$
where $v$ is the vector width, $c^{\text{disp}}$ the per-batch dispatch/materialization cost,
and $c^{\text{prim}}$ the per-tuple primitive cost. Compilation drives $c^{\text{disp}}\to 0$
and lowers $c^{\text{prim}}$ via fusion and keeping state in registers, but adds a fixed
$T_{\text{compile}}$ (often tens of ms for LLVM; ~$\mu$s for a custom code generator or a
bytecode/copy-and-patch JIT). The crossover tuple count satisfies roughly
$n^\* \approx T_{\text{compile}} / \Delta c$, where $\Delta c$ is the per-tuple saving from
compilation. The unification question is whether a *single* lowering (e.g., compiling to a
vector-of-fused-primitives IR) can dominate both extremes for all $(n,H)$ — an
**instance-optimality**-flavored objective over the code-shape space.

Relevant theory: this is an instance of **multi-tier JIT** scheduling (cf. tracing/tiered
compilers in managed runtimes), and of cost-model-driven **algorithm selection**, where the
selection itself is uncertain because $n$ is typically unknown before execution.

## 3. State of the Art (SOTA)

- **Systems SOTA.** *Umbra* (Neumann et al., CIDR 2020) uses a custom **flying-start** code
  generator with adaptive tier-up to LLVM-optimized code for long pipelines, explicitly
  trading compile latency against runtime. *DuckDB* (Raasveldt & Mühleisen, SIGMOD 2019)
  is fully vectorized and competitive without compilation. *Velox* (Pedreira et al., VLDB
  2022) is a vectorized execution library shared across engines.
- The seminal head-to-head is Kersten et al., **"Everything You Always Wanted to Know About
  Compiled and Vectorized Queries But Were Afraid to Ask"** (VLDB 2018), which isolates the
  effects of data-centric compilation vs. vectorization on the *same* engine and finds
  neither dominates: compilation wins on compute-heavy, vectorization on memory-bound and
  SIMD-friendly work.
- **Copy-and-patch** compilation (Xu & Kjolstad, OOPSLA 2021) gives near-interpreter compile
  latency with near-JIT code quality, narrowing the unification gap.

## 4. Upper Bound

No closed-form optimality result exists; the practical upper bound is the **adaptive,
tiered** approach: start interpreting/vectorizing immediately (latency $\approx$ vectorized),
and tier up to compiled code only for pipelines whose observed cardinality exceeds the
crossover $n^\*$. This guarantees latency within a constant factor of $\min(T_{\text{vec}},
T_{\text{comp}}) + T_{\text{compile}}$ per pipeline in the RAM/cost-model setting, and is
realized by Umbra. Hybrid IRs that compile *to* vector primitives (vectorized compilation)
upper-bound both by construction on compute-light, SIMD-heavy operators.

## 5. Lower Bound

Lower bounds here are **information-theoretic / online** rather than complexity-theoretic.
Because the deciding quantity (pipeline cardinality, data distribution, predicate
selectivity) is unknown before execution, any *static* paradigm choice has an unbounded
competitive ratio against the offline optimum: an adversary sets $n$ just past or just below
$n^\*$. This is the standard **ski-rental / online algorithm-selection** lower bound: no
deterministic static policy is better than 2-competitive on the compile-or-not decision, and
the constant depends on $T_{\text{compile}}/\Delta c$, which is hardware-dependent. There is
no NP-hardness barrier; the difficulty is empirical and online, hence the *empirically-open*
status.

## 6. The Gap

The gap is not a complexity gap but an **engineering-and-modeling** gap: (i) we lack a cost
model accurate enough to predict $n^\*$ and $\Delta c$ across architectures and operators,
and (ii) no single IR has been shown to weakly dominate both paradigms across the full TPC-H/
TPC-DS/ClickBench spectrum. Adaptive tier-up closes the *worst-case regret* but at the cost
of carrying two execution engines. A truly unified lowering that needs only one codegen path
and never loses to either extreme remains undemonstrated.

## 7. Current Research (as of June 2026)

- **Vectorized compilation / fused-primitive IRs**: generating compiled code that operates on
  batches to retain SIMD and profiling while removing dispatch (Umbra line; Menon/Pavlo's
  "relaxed operator fusion," VLDB 2017). Active in the TUM group (Neumann, Leis) and CMU
  (Pavlo). *(frontier — verify)* Several 2025 systems explore copy-and-patch back-ends for
  sub-millisecond compile latency inside vectorized engines.
- **Hardware-adaptive crossover learning**: using lightweight runtime profiling to set the
  tier-up threshold per machine; overlaps with adaptive reoptimization.
- **Substrait/Velox-style portable plans** decoupling logical plan from the chosen execution
  paradigm, enabling per-deployment paradigm choice. *(frontier — verify)*

## 8. Future Work

- A formal cost model with provable competitive guarantees for the online compile-or-vectorize
  decision under unknown cardinality.
- A single IR that provably weakly dominates both paradigms operator-by-operator.
- Co-design with NUMA/SIMD batch sizing (see sibling problems) so paradigm choice and batch
  granularity are optimized jointly rather than independently.

## 9. Key References

- **[Foundational]** Neumann. *Efficiently Compiling Efficient Query Plans for Modern Hardware.* VLDB 2011.
- **[SOTA]** Kersten, Leis, Kemper, Neumann, Pavlo, Boncz. *Everything You Always Wanted to Know About Compiled and Vectorized Queries But Were Afraid to Ask.* VLDB 2018.
- **[SOTA]** Neumann, Freitag. *Umbra: A Disk-Based System with In-Memory Performance.* CIDR 2020.
- **[Foundational]** Boncz, Zukowski, Nes. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR 2005.
- **[SOTA]** Xu, Kjolstad. *Copy-and-Patch Compilation.* OOPSLA 2021.
- **[SOTA]** Menon, Mowry, Pavlo. *Relaxed Operator Fusion for In-Memory Databases.* VLDB 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
