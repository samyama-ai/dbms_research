---
id: 29-hardware-conscious-db/portable-accelerator-performance
title: "Portable performance across accelerator generations"
topic: 29-hardware-conscious-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Portable performance across accelerator generations

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/portable-accelerator-performance` · **Status:** open

## 1. Problem Statement

Hand-tuned database operator kernels for GPUs and FPGAs extract near-peak performance by hard-coding hardware parameters — tile sizes, shared-memory budgets, warp/wavefront width, register blocking, memory-coalescing patterns, pipeline depth, and (for FPGAs) the synthesized dataflow. When the **hardware generation changes** (new GPU SM count / cache sizes / tensor units, new FPGA fabric, or a different vendor), these constants are wrong and performance collapses, requiring manual rewrites. The problem: produce operator code and a tuning strategy that retains **near-peak performance across accelerator generations and vendors without manual rewriting** — i.e., *performance portability*.

Formally: let $\mathcal{H}$ be a family of accelerator targets and $\Pi$ a space of code/tuning configurations. For an operator $o$ and target $H$, let $\text{perf}(o, \pi, H)$ be achieved throughput and $\text{peak}(o, H)$ the attainable ceiling (roofline). A configuration generator $g$ is **performance-portable** if for all $H \in \mathcal{H}$, $\frac{\text{perf}(o, g(H), H)}{\text{peak}(o,H)} \ge 1 - \varepsilon$ for small $\varepsilon$, using *no* per-$H$ human effort. Variants: (a) *single-source* — one code base, compiler/JIT specializes; (b) *auto-tuning* — search $\Pi$ per target within a time budget (optimization problem over a huge, irregular, expensive-to-evaluate space); (c) *cost-model-driven* — predict the best $\pi$ without exhaustive search (ties to accelerator cost estimation).

## 2. Mathematical Foundations

The performance-portability metric is commonly the **harmonic mean of efficiency** across targets (Pennycook–Sewall–Lee): $\Phi(o,\mathcal{H}) = |\mathcal{H}| / \sum_{H} \frac{1}{e(o,H)}$ where $e(o,H)=\text{perf}/\text{peak} \in (0,1]$ — harmonic mean punishes any target where efficiency collapses, formalizing "near-peak *everywhere*." The achievable ceiling per target is the **roofline** $\min(\text{peak FLOP/s}, \text{AI}\cdot\text{BW})$. Auto-tuning is **black-box optimization** over a discrete, non-convex configuration space with expensive evaluations: model it as bandit / Bayesian optimization or as combinatorial search; the number of distinct configs is exponential in the number of tunable parameters, so exhaustive search is infeasible and sample-efficiency (regret bounds) is the relevant theory. Generation-to-generation transfer is a **domain-adaptation / transfer-learning** problem: a cost or autotuning model trained on $H_1$ must predict on $H_2$; its error is bounded by a divergence between the hardware-parameter distributions ($\mathcal{H}$-divergence, Ben-David et al. domain-adaptation bounds). FPGA reconfiguration adds a *compile-time* cost (place-and-route hours), making per-target search far costlier than on GPUs.

## 3. State of the Art (SOTA)

**Single-source / portability layers.** *SYCL/DPC++*, *Kokkos* (Edwards–Trott, JPDC 2014), *RAJA*, *OpenCL*, and *OpenMP target* offload provide one source over multiple backends — portability of *code* but not always of *performance*. *Triton* (Tillet et al., MAPL 2019) and *TVM* (Chen et al., OSDI 2018) compile high-level kernels with autotuned schedules; *Halide*'s decoupling of algorithm from schedule (Ragan-Kelley et al., PLDI 2013) is the conceptual root.

**DB-specific.** *Crystal* (Shanbhag–Madden, SIGMOD 2020) builds GPU DB operators from a small set of *tile-based primitives* designed to be retargetable; *Voodoo* (Pirk et al., VLDB 2016) is a vector algebra IR that compiles portable data-parallel DB operators to CPU/GPU; *HorseQC*, *HetExchange* (Chrysogelos et al., VLDB 2019) compile JIT operators across CPU/GPU. FPGA DB: ETH Zürich (Alonso) generators (*Mondrian*, fpgaDB), and HLS-based query-to-circuit compilers.

**Autotuning.** *OpenTuner* (Ansel et al., PACT 2014), *ATF*, ML-guided schedule search (*Ansor* / Auto-scheduler in TVM, Zheng et al., OSDI 2020) are the practical SOTA for cross-target tuning.

## 4. Upper Bound

No closed-form bound on achievable portable efficiency exists. Empirically, schedule-search compilers (TVM/Ansor, Triton) reach within a small constant of hand-tuned peak on *seen* GPU generations after autotuning; Crystal/Voodoo demonstrate that a *primitive-library* upper-bounds rewrite effort to re-tuning the primitives rather than the operators. The roofline gives the hard per-target ceiling that any portable configuration is measured against. Bayesian/bandit autotuners give sublinear-regret guarantees (e.g. $O(\sqrt{T\log|\Pi|})$ for finite config sets) on *search* cost, an upper bound on tuning effort, not on portability gap.

## 5. Lower Bound

The portability gap is **information-theoretically irreducible** in general: two hardware generations with different ratios of compute-to-bandwidth or different cache hierarchies have *different optimal configurations*, so a single fixed configuration cannot be near-peak on both — a formal **no-free-lunch / lower bound** on static portability (achievable efficiency of any fixed $\pi$ is bounded below 1 across a sufficiently diverse $\mathcal{H}$). Autotuning per target therefore is necessary, and its cost is lower-bounded by the **black-box query complexity** of optimizing a non-convex function (exponential configs ⇒ no sublinear search without structure/transfer). Transfer-learning error is lower-bounded by the domain divergence (Ben-David): if $H_2$ differs enough from training targets, predicted configs have bounded-below error. FPGA place-and-route makes the per-evaluation cost itself a hard wall.

## 6. The Gap

**Open.** There is no method that provably retains near-peak efficiency across *unseen* future accelerator generations without per-target search, and the static no-free-lunch bound says one cannot exist for a fixed configuration — so the real question is whether **automatic, low-cost re-specialization** (cost-model- or transfer-learning-driven) can close the gap with little human effort and few/no expensive evaluations. The divide is between (a) single-source code portability (solved by SYCL/Kokkos) and (b) *performance* portability with guarantees (unsolved). Closing it requires transfer-learnable cost models (overlaps with accelerator cost estimation) plus search algorithms with regret/transfer bounds, validated across real GPU/FPGA generations.

## 7. Current Research (as of June 2026)

- **ML-guided, transfer-learning autotuners** that warm-start search on a new generation from prior generations' data, targeting near-zero manual effort *(frontier — verify)*.
- **Triton/TVM-style DB operator IRs** specialized for relational operators, retargeting to new GPUs and to non-NVIDIA accelerators (AMD ROCm, Intel) *(frontier — verify portability claims)*.
- Decoupled **algorithm/schedule** DB engines extending Halide/Voodoo ideas; LLM-assisted schedule generation *(frontier — verify)*.
- FPGA HLS generators that re-place-and-route automatically with predicted directives to cut search cost.
- Groups: MIT (Madden, Amarasinghe — Halide/auto-scheduling lineage; Crystal), ETH Zürich (Alonso, Pirk-adjacent — Voodoo, FPGA), UW (TVM, Ceze), TUM/CWI (vectorized engines), NVIDIA/AMD research.

## 8. Future Work

- Autotuners with provable transfer/regret bounds across accelerator generations.
- A relational operator IR with a performance-portability *guarantee* under a stated hardware family.
- Unified cost-model + search that re-specializes operators at deploy time for new hardware with no human in the loop.
- Extending portability targets to CXL/DPU heterogeneity, not just GPU/FPGA.

## 9. Key References

- **[Foundational]** Ragan-Kelley, J. et al. *Halide: A Language and Compiler for Optimizing Parallelism, Locality, and Recomputation in Image Processing Pipelines.* PLDI, 2013. — [DBLP](https://dblp.uni-trier.de/rec/conf/pldi/Ragan-KelleyBAPDA13.html)
- **[Foundational]** Pennycook, S. J., Sewall, J. D., Lee, V. W. *A Metric for Performance Portability.* arXiv:1611.07409, 2016. — [arXiv](https://arxiv.org/abs/1611.07409)
- **[SOTA]** Chen, T. et al. *TVM: An Automated End-to-End Optimizing Compiler for Deep Learning.* OSDI, 2018. — [arXiv](https://arxiv.org/abs/1802.04799)
- **[SOTA]** Tillet, P., Kung, H. T., Cox, D. *Triton: An Intermediate Language and Compiler for Tiled Neural Network Computations.* MAPL, 2019. — [DOI](https://doi.org/10.1145/3315508.3329973)
- **[SOTA]** Pirk, H., Moll, O., Zaharia, M., Madden, S. *Voodoo: A Vector Algebra for Portable Database Performance on Modern Hardware.* VLDB, 2016. — [DOI](https://doi.org/10.14778/3007328.3007336)
- **[SOTA]** Ansel, J. et al. *OpenTuner: An Extensible Framework for Program Autotuning.* PACT, 2014. — [DOI](https://doi.org/10.1145/2628071.2628092)
- **[Foundational]** Ben-David, S. et al. *A Theory of Learning from Different Domains.* Machine Learning, 2010. — [DOI](https://doi.org/10.1007/s10994-009-5152-4)

## 10. Worked Example

Consider a memory-bound DB scan kernel auto-tuned on GPU generation $H_1$ (peak BW $900$ GB/s) where the best tile size hits $e(o,H_1)=\frac{\text{perf}}{\text{peak}}=0.90$. Ship the *same* fixed config to $H_2$ (a newer GPU, peak BW $2000$ GB/s, more SMs); the stale tile under-fills the wider memory subsystem and achieves only $e(o,H_2)=0.40$.

Pennycook's performance-portability metric is the harmonic mean of efficiencies:
$$\Phi = \frac{|\mathcal{H}|}{\sum_H 1/e(o,H)} = \frac{2}{\frac{1}{0.90}+\frac{1}{0.40}} = \frac{2}{1.111+2.5} = \frac{2}{3.611} \approx 0.554.$$

The harmonic mean ($0.554$) sits far below the arithmetic mean ($0.65$): it *punishes* the collapse on $H_2$. Re-running the autotuner on $H_2$ (warm-started from $H_1$'s data) recovers $e(o,H_2)=0.88$, lifting $\Phi$ to $\frac{2}{1.111+1.136}\approx 0.890$. This quantifies why a single static config cannot be near-peak everywhere (Section 5) and why low-cost per-target re-specialization is the open lever (Section 6).

---
*Part of the [DBMS Research catalog](../../README.md).*
