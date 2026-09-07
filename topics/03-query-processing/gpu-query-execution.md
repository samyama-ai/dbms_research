---
id: 03-query-processing/gpu-query-execution
title: "GPU-resident join and aggregation execution"
topic: 03-query-processing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# GPU-resident join and aggregation execution

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/gpu-query-execution` · **Status:** empirically-open
> **Verification note:** The TQP reference conflates two real Microsoft papers — *Query Processing on Tensor Computation Runtimes* (PVLDB 15(11), 2022, the actual TQP system) and *The Tensor Data Platform: Towards an AI-centric Database System* (CIDR 2023); the linked DOI points to the former.

## 1. Problem Statement

Execute full relational query pipelines — chiefly hash joins, grouped aggregation, and
sorting — on GPUs end-to-end, rather than as isolated kernels, while contending with the
defining bottlenecks of the device: limited high-bandwidth memory (HBM), the comparatively
narrow and high-latency PCIe (or NVLink/CXL) link to host memory, massive thread-level
parallelism that punishes irregular/random memory access, and the need to **spill** when
working sets exceed device memory.

The problem: **given a query plan and a heterogeneous CPU+GPU memory hierarchy, produce an
execution strategy (operator placement, data layout, transfer schedule, and spill policy)
that minimizes end-to-end time** including transfer, and degrades gracefully when inputs
exceed GPU memory.

- **Decision variant:** does there exist a placement/transfer schedule completing within
  time $T$ given device-memory budget $M$ and link bandwidth $\beta$?
- **Optimization variant:** minimize $T_{\text{transfer}} + T_{\text{compute}} + T_{\text{spill}}$
  over operator-placement and data-movement plans.
- **Out-of-core variant:** when $|R| \gg M$, choose a partitioning/streaming schedule that
  keeps the GPU compute-bound, not transfer-bound.

"Solving" means a planner+runtime that is robustly faster than a tuned CPU engine across
join/aggregation workloads, including the larger-than-memory regime, not just on
cherry-picked in-HBM microbenchmarks.

## 2. Mathematical Foundations

Model the device as a parallel machine with $p$ lanes, HBM bandwidth $B_{\text{hbm}}$, and a
host link of bandwidth $\beta \ll B_{\text{hbm}}$ (often $10$–$50\times$ slower). For an
operator touching $n$ tuples of width $w$, a roofline-style lower bound on time is

$$T \;\ge\; \max\!\left(\frac{\text{FLOPs}}{F_{\text{peak}}},\; \frac{n\,w}{B_{\text{hbm}}},\; \frac{V_{\text{host}}}{\beta}\right),$$

where $V_{\text{host}}$ is bytes that must cross PCIe. Hash joins are **memory-latency
bound**: probing a hash table induces random HBM access whose effective bandwidth collapses
under uncoalesced reads, so achieved throughput is governed by *latency × outstanding
requests*, not peak $B_{\text{hbm}}$. The **transfer-vs-compute crossover** determines
whether GPU offload pays: offload wins only when $\frac{V_{\text{host}}}{\beta} <
T_{\text{cpu}} - T_{\text{gpu-compute}}$. Out-of-core execution maps to the
**external-memory (I/O) model** with HBM as "cache" of size $M$ and host memory as slow
store; radix/partitioning joins minimize the number of $M$-sized passes, echoing classic
I/O-complexity $\Theta\big(\frac{n}{B}\log_{M/B}\frac{n}{B}\big)$ sorting bounds with
$B$ the transfer block.

## 3. State of the Art (SOTA)

- **Systems SOTA:** **Crystal** (Shanbhag, Madden, Yu, SIGMOD 2020) is the canonical study
  of a "tile-based" GPU query-execution library showing in-HBM analytical queries run an
  order of magnitude faster than CPUs *when data fits*. **HeavyDB/OmniSci** and **BlazingSQL**
  are production GPU SQL engines. **TQP / Tensor Query Processor** (Microsoft, VLDB 2022)
  compiles relational operators onto tensor runtimes.
- Foundational kernels: **Kaldewey et al.** (SIGMOD 2012) and **He et al.** *Relational Joins
  on Graphics Processors* (SIGMOD 2008) established GPU hash/sort-merge join primitives.
- **Transfer-aware / out-of-core:** Yuan et al. and **Sioulas et al.** *Hardware-Conscious
  Hash-Joins on GPUs* (ICDE 2019) optimize partitioning to fit HBM and hide PCIe latency.
  Recent work exploits **NVLink/UVM and GPUDirect** to overlap transfer with compute, and
  pipelined PCIe streaming to stay compute-bound *(frontier — verify)*.

## 4. Upper Bound

For the in-HBM case the upper bound matches CPU asymptotics: a partitioned hash join is
$O(|R|+|S|)$ expected work, parallelized to $O((|R|+|S|)/p)$ span with $p$ lanes, plus
$O(\log)$-depth prefix sums for partition offsets. The interesting upper bound is the
**out-of-core/transfer** one: a radix-partitioned streaming join achieves
$O\!\big(\frac{(|R|+|S|)w}{\beta}\big)$ transfer time with $O(1)$ passes over host memory
when partitions fit $M$, and is provably **transfer-bound-optimal** under the
external-memory model once partitions are $M$-sized. No tight closed form exists for the
latency-bound probe phase — it is governed by achievable memory-level parallelism, a
constant-factor (microarchitectural) quantity.

## 5. Lower Bound

There is no nontrivial complexity-theoretic separation between GPU and CPU join execution —
both compute the same relational operator with the same asymptotic work. The binding lower
bounds are **architectural and information-theoretic within the I/O model**:

1. **Transfer floor:** any GPU plan must move $\Omega(V_{\text{host}})$ bytes across the
   link, so $T \ge V_{\text{host}}/\beta$ — unconditional; this is why naive offload of a
   single scan never beats CPU.
2. **Random-access floor:** probing $n$ keys into a table larger than cache costs
   $\Omega(n)$ uncoalesced HBM transactions; coalescing/MLP only changes the constant.
3. **External-memory sorting/partitioning** inherits the classic $\Omega\big(\frac{n}{B}
   \log_{M/B}\frac{n}{B}\big)$ I/O lower bound (Aggarwal–Vitter), bounding out-of-core
   joins from below.

These hold unconditionally in the external-memory and parallel-RAM models; none yields an
asymptotic CPU/GPU *separation*, hence *empirically-open*.

## 6. The Gap

The gap is constant-factor and engineering, not asymptotic. We lack (a) a portable
cost model that predicts, per query and hardware generation, whether GPU offload beats CPU
*including* transfer and spill, and (b) a runtime that keeps the GPU compute-bound in the
larger-than-memory regime without falling off a "data doesn't fit HBM" cliff. Closing it
means principled co-scheduling of PCIe transfer, HBM residency, and spill — with regret
bounds against the better of CPU-only and idealized in-HBM GPU execution.

## 7. Current Research (as of June 2026)

- **MIT DSAIL (Madden, Shanbhag)** and the Crystal line continue on tile-based GPU
  operators and out-of-core extensions.
- **EPFL DIAS (Ailamaki)** and the Sioulas/Chrysogelos work on hardware-conscious,
  heterogeneous CPU+GPU query engines (Proteus) span multiple devices in one plan.
- **CXL-attached and disaggregated memory** as a third tier to relax the HBM cliff is an
  active 2025–2026 direction *(frontier — verify)*.
- **GPU-native vectorized/compiled hybrids** and using **tensor cores** for joins/group-by
  (sort, hash via matrix ops) following TQP *(frontier — verify)*.

## 8. Future Work

- A unified cost model + planner that places each operator on CPU/GPU and schedules
  transfers with provable competitiveness.
- Spill/eviction policies for HBM with worst-case guarantees in the I/O model.
- Exploiting NVLink/CXL coherence to treat host+device as one tier and overlap transfer
  fully with compute.
- Energy-aware GPU offload (joint with energy-optimal execution).

## 9. Key References

- **[Foundational]** B. He, K. Yang, R. Fang, M. Lu, N. Govindaraju, Q. Luo, P. Sander. *Relational Joins on Graphics Processors.* SIGMOD, 2008. — [DOI](https://doi.org/10.1145/1376616.1376670)
- **[SOTA]** A. Shanbhag, S. Madden, X. Yu. *A Study of the Fundamental Performance Characteristics of GPUs and CPUs for Database Analytics.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3380595) · [arXiv](https://arxiv.org/abs/2003.01178)
- **[SOTA]** P. Sioulas, P. Chrysogelos, M. Karpathiotakis, R. Appuswamy, A. Ailamaki. *Hardware-Conscious Hash-Joins on GPUs.* ICDE, 2019. — [DBLP](https://dblp.org/pid/233/6232.html)
- **[SOTA]** D. Yan et al. / Microsoft. *The Tensor Data Platform: Towards an Algebraically Defined GPU-Native Query Engine (TQP).* PVLDB / CIDR, 2022. — [Query Processing on Tensor Computation Runtimes, PVLDB 15(11) 2022, DOI](https://doi.org/10.14778/3551793.3551833)
- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Survey]** B. Gowanlock et al. / S. Breß et al. *GPU-Accelerated Database Systems: Survey and Open Challenges.* TLDKS, 2014. — [DOI](https://doi.org/10.1007/978-3-662-45761-0_1) · [DBLP](https://dblp.org/rec/journals/tlsdkcs/BressHSBS14.html)

## 10. Worked Example

Should we offload a hash join $R \bowtie S$ to the GPU? Suppose $V_{\text{host}} = 8$ GB must
cross PCIe at $\beta = 16$ GB/s, while HBM bandwidth is $B_{\text{hbm}} = 1600$ GB/s
($100\times$ faster). The CPU runs the join in $T_{\text{cpu}} = 0.9$ s.

Transfer time: $T_{\text{transfer}} = V_{\text{host}}/\beta = 8/16 = 0.5$ s.

GPU compute (in HBM, $\sim$$100\times$ the link's effective rate for this data):
$T_{\text{gpu-compute}} \approx 0.05$ s.

Offload pays only if $T_{\text{transfer}} < T_{\text{cpu}} - T_{\text{gpu-compute}}$, i.e.
$0.5 < 0.9 - 0.05 = 0.85$. True, so GPU wins: $0.5 + 0.05 = 0.55$ s vs. $0.9$ s.

Now widen the join to $V_{\text{host}} = 16$ GB: $T_{\text{transfer}} = 1.0$ s, and
$1.0 \not< 0.85$ — the PCIe link dominates and CPU-only is faster. This is the
**transfer-vs-compute crossover**: the $\beta \ll B_{\text{hbm}}$ link, not raw GPU FLOPs,
decides offload, which is why a naive single-scan offload never beats CPU.

---
*Part of the [DBMS Research catalog](../../README.md).*
