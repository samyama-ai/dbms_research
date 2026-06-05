# Accelerator-aware cardinality and cost estimation

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/accelerator-cost-estimation` · **Status:** open

## 1. Problem Statement

A query optimizer chooses plans by estimating, for each physical operator, its **cardinality** (output size) and **cost** (runtime / resource use). On CPUs the cost is roughly affine in input/output cardinalities and a few constants. On **GPUs and FPGAs** this breaks: operator runtime depends *nonlinearly* on hardware-execution factors that are not captured by cardinality alone —

- **Occupancy** (how many warps/threads fit and run concurrently — a step/threshold function of register and shared-memory usage);
- **Control-flow / branch divergence** (within a SIMT warp, divergent predicates serialize, so cost depends on *data distribution*, not just count);
- **Memory-coalescing and bank conflicts** (access pattern, not volume, sets effective bandwidth);
- **Host↔device transfers** (PCIe/NVLink/CXL movement, often the dominant term);
- **Kernel-launch / pipeline-fill overhead** and **FPGA reconfiguration** time.

The problem: build a cost (and supporting cardinality) model $\hat{C}(o, I, \theta_{\text{hw}})$ that predicts accelerator operator runtime accurately enough to drive **plan selection and device-placement** decisions, where $\theta_{\text{hw}}$ are hardware parameters and the dependence on input statistics $I$ is nonlinear and non-monotone. Decision variant: is plan $P_1$ cheaper than $P_2$ on this device? Optimization variant: pick the min-cost plan + placement; the underlying *cardinality* sub-problem inherits all classical estimation hardness.

## 2. Mathematical Foundations

Cardinality estimation rests on **selectivity** $\sigma$ with the AGM bound (Atserias–Grohe–Marx) bounding join output by the fractional edge cover LP: $|Q| \le \prod_e R_e^{x_e}$ for a fractional cover $x$; estimation error compounds multiplicatively along a plan (Ioannidis–Christodoulakis: errors propagate exponentially in join depth). The accelerator layer adds a **piecewise / threshold** cost surface. Occupancy is a step function of resource use $r$: $\text{occ}(r) = \lfloor R_{\max}/r \rfloor / W_{\max}$, so runtime $\propto \lceil N / (\text{occ}\cdot P) \rceil$ has discontinuities. Divergence cost depends on the *distribution* of a predicate over a warp of width $w$: expected serialization $\mathbb{E}[\#\text{distinct branch targets per warp}]$, a function of data, not cardinality — making cost a functional of the underlying distribution. A **roofline model** ($\text{perf} = \min(\text{peak FLOP/s}, \text{AI}\cdot\text{BW})$, Williams–Waterman–Patterson) bounds achievable throughput by arithmetic intensity AI and bandwidth BW, giving a principled but coarse ceiling. The combined model is thus a *nonlinear, non-convex, distribution-dependent* surface, unlike the affine CPU cost.

## 3. State of the Art (SOTA)

**Systems-SOTA.** GPU DB engines — *Crystal* (Shanbhag–Madden–Yu, SIGMOD 2020, tile-based primitives), *HeavyDB/OmniSciDB*, *BlazingSQL*, *TQP/Velox-GPU*, *HetExchange* (Chrysogelos et al., VLDB 2019) for CPU-GPU plan parallelism — mostly use *hand-tuned* or *micro-benchmark-calibrated* cost constants and heuristics rather than predictive models. FPGA DB work (*Mondrian*, *DoppioDB*, ETH/Alonso; *Centaur*) similarly relies on per-operator profiling.

**Learned cost models.** ML-based query cost/latency predictors — *QPP-Net* (Marcus–Papaemmanouil), *Neo* / *Bao* (Marcus et al., VLDB 2019/SIGMOD 2021) learn cost from execution feedback; on CPUs they outperform analytic models. Their extension to capture occupancy/divergence on accelerators is nascent. Cardinality learning: *MSCN* (Kipf et al., CIDR 2019), *DeepDB*, *NeuroCard*.

**Theory-SOTA.** Cardinality bounds are well developed (AGM, degree/Lp bounds, Cardinality Estimation via entropic bounds); *accelerator runtime* cost has **no clean theory** — it is the open gap.

## 4. Upper Bound

There is no tight analytical upper bound on prediction error. Best practical results: learned models (Bao-style, gradient-boosted or DNN regressors over hardware counters + plan features) achieve median runtime-prediction errors competitive with calibrated analytic models on fixed hardware; the *roofline* gives a hard, provable upper bound on achievable throughput (hence a lower bound on runtime) per operator given AI and BW. For cardinality, AGM and its refinements give provable worst-case output-size upper bounds, which upper-bound any downstream cost.

## 5. Lower Bound

**Cardinality estimation is provably hard.** Distinct-value / frequency-moment estimation has streaming **space lower bounds** ($\Omega(1/\varepsilon^2)$, AMS); exact join-size requires worst-case $\Theta(\text{AGM})$ work; and *no sampling-based estimator* can give bounded multiplicative error for all queries within sublinear samples (information-theoretic). For the **runtime** target, the dependence on data distribution (divergence) means a cost predictor that uses only cardinalities is information-theoretically insufficient — two inputs with identical cardinalities but different value distributions have different runtimes, so any model ignoring distribution has unbounded relative error. The discontinuity of occupancy implies non-Lipschitz cost, so smooth/affine surrogates have irreducible error near thresholds.

## 6. The Gap

**Wide open.** Classical cardinality estimation already lacks tight error guarantees; the accelerator layer compounds this with a non-convex, distribution-dependent, threshold-laden runtime surface for which there is *neither a validated analytic model nor a learned model with guarantees*. The gap: between (a) per-operator micro-benchmark calibration (accurate but non-portable, brittle to new hardware and new data) and (b) a *predictive, transferable* model usable inside an optimizer. No lower bound currently bounds how much accuracy a model with full distribution access *could* achieve, and no upper-bounding algorithm matches such a target. Closing it requires both a principled cost model class (capturing occupancy/divergence/transfer) and learning-theoretic guarantees on its sample complexity and transfer.

## 7. Current Research (as of June 2026)

- **Learned + roofline hybrids**: combine a hard roofline ceiling with a learned residual over hardware counters and data-distribution features *(frontier — verify)*.
- **Transfer-aware optimizers** that treat PCIe/NVLink/CXL movement as a first-class plan cost and co-optimize device placement (heir to HetExchange) *(frontier — verify)*.
- **Distribution-aware divergence models** estimating expected warp serialization from histograms/sketches.
- Cross-hardware **transfer learning** of cost models so a model trained on one GPU generation predicts on the next (overlaps with the portable-performance problem).
- Groups: MIT (Madden, Kraska — Crystal, learned models), ETH Zürich (Alonso, FPGA), TUM (Neumann), Microsoft Research (Bao/learned optimizers), CWI (Boncz).

## 8. Future Work

- A cost-model *class* with provable approximation guarantees for occupancy/divergence-dominated operators.
- Sample-complexity and transfer bounds for learned accelerator cost models across generations.
- Integrating accelerator cost into a unified CPU+GPU+FPGA optimizer with placement.
- Robust cardinality estimators whose error propagates gracefully into nonlinear accelerator cost.

## 9. Key References

- **[Foundational]** Selinger, P. G. et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Atserias, A., Grohe, M., Marx, D. *Size Bounds and Query Plans for Relational Joins (AGM bound).* FOCS, 2008. — [DBLP](https://dblp.org/rec/conf/focs/AtseriasGM08.html) · [arXiv](https://arxiv.org/abs/1711.03860)
- **[Foundational]** Williams, S., Waterman, A., Patterson, D. *Roofline: An Insightful Visual Performance Model for Multicore Architectures.* CACM, 2009. — [DOI](https://doi.org/10.1145/1498765.1498785)
- **[SOTA]** Shanbhag, A., Madden, S., Yu, X. *A Study of the Fundamental Performance Characteristics of GPUs and CPUs for Database Analytics (Crystal).* SIGMOD, 2020. — [arXiv](https://arxiv.org/abs/2003.01178) · [DBLP](https://dblp.org/rec/conf/sigmod/ShanbhagMY20.html)
- **[SOTA]** Marcus, R. et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DBLP](https://dblp.org/rec/conf/sigmod/MarcusNMTAK21.html)
- **[SOTA]** Kipf, A. et al. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677) · [DBLP](https://dblp.org/rec/conf/cidr/KipfKRLBK19.html)
- **[SOTA]** Chrysogelos, P. et al. *HetExchange: Encapsulating Heterogeneous CPU-GPU Parallelism in JIT Compiled Engines.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3303753.3303760) · [DBLP](https://dblp.org/rec/journals/pvldb/ChrysogelosKAA19.html)

## 10. Worked Example

Consider a GPU filter `SELECT * FROM R WHERE x > c` over $N = 2^{26}$ rows ($\approx$ 256 MB at 4 B/row). The classical optimizer's affine model predicts cost $\propto N$, identical for *any* value distribution. The accelerator reality differs.

Suppose the GPU has internal bandwidth $\beta = 800$ GB/s, but the data must first cross PCIe 4.0 at $\beta_{io} = 25$ GB/s. Transfer alone: $256\text{ MB} / 25\text{ GB/s} \approx 10.2$ ms, which *dwarfs* the on-device scan time $256\text{ MB}/800\text{ GB/s} \approx 0.32$ ms. So the cardinality-only model (which ignores PCIe) under-predicts runtime by $\sim 30\times$.

Now divergence. With warp width $w = 32$, take two inputs of identical cardinality but different layouts:

- **Sorted** by $x$: each warp sees rows mostly all-pass or all-fail $\Rightarrow$ expected distinct branch targets per warp $\approx 1$, no serialization.
- **Random** with selectivity $\sigma = 0.5$: $\Pr[\text{warp is uniform}] = 2\cdot 0.5^{32}\approx 0$, so essentially every warp hits both branches $\Rightarrow$ $\approx 2\times$ serialization on the predicate body.

Same $N$, same $\sigma$ — yet runtime differs by a factor of 2 purely from distribution. This concretely shows why a cost model $\hat C(o, I, \theta_{hw})$ keyed only on cardinality has *unbounded* relative error (Section 5): the missing variable is the data distribution itself.

---
*Part of the [DBMS Research catalog](../../README.md).*
