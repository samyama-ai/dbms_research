# Optimal radix partitioning fan-out

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/radix-partition-fanout` · **Status:** partially-solved

## 1. Problem Statement
Radix partitioning splits a relation into $F$ buckets by hashing on a window of radix bits, possibly over several passes. **Fan-out** $F$ per pass and the **number of passes** $k$ jointly determine cache and TLB behavior: too large a fan-out thrashes the TLB and cache (too many simultaneously-written output streams); too small a fan-out needs more passes (more total data movement). The problem: **choose $k$ and the per-pass fan-out to minimize total TLB + cache misses** for partitioning $N$ tuples down to cache-sized buckets, given hardware parameters (TLB entries $T$, cache size $C$, line size $B$) and data skew.

Variants: (a) **optimization** — minimize total miss cost (or runtime) over $(k, F_1,\dots,F_k)$; (b) **decision** — is a $\le \tau$-miss schedule achievable? (c) **skew-robust** — same under non-uniform key distributions.

## 2. Mathematical Foundations
To partition $N$ tuples into final buckets of size $\le C$ (so build/probe is cache-resident), total fan-out must satisfy $\prod_i F_i \ge N/C$, hence $k \ge \log_{F}(N/C)$ for uniform per-pass fan-out $F$. Each pass scans $N$ tuples: $O(N/B)$ sequential cache misses are unavoidable per pass. **TLB constraint:** writing to $F$ output partitions touches $F$ distinct pages concurrently; if $F > T$ (TLB entries), each write risks a TLB miss, so the *cache/TLB-conscious* rule is $F \le T$ (often $F\le 2^{6\text{–}8}$). Total cost $\approx k\cdot\frac{N}{B} + (\text{TLB penalty if }F>T)$, minimized by the largest $F\le T$ that keeps software write-combine buffers resident, giving optimal passes $k^\* = \lceil \log_{T}(N/C)\rceil$. Skew enters through the **maximum bucket size**, which inflates effective $N/C$ and motivates per-bucket adaptive fan-out. The structure mirrors **MSD radix sort** I/O analysis.

## 3. State of the Art (SOTA)
The canonical analysis is **Manegold–Boncz–Kersten**, *"Optimizing Main-Memory Join on Modern Hardware"* (TKDE 2002) and the **radix-cluster/radix-decluster** of MonetDB, which first derived the TLB-bounded multi-pass partitioning rule. **Kim et al.** (VLDB 2009, "Sort vs. Hash Revisited") tuned fan-out for SIMD/multicore. **Balkesen–Teubner–Alonso–Özsu** (ICDE 2013) and **Schuh–Chen–Dittrich** (SIGMOD 2016) gave the definitive empirical sweeps showing 1–2 pass partitioning with fan-out $\approx 2^7$–$2^{11}$ and **software-managed buffers / non-temporal streaming stores** as the practical optimum. **Polychroniou–Ross** (SIGMOD 2014, "Comprehensive Study of Main-Memory Partitioning") is the most thorough fan-out study, including range and hash partitioning with prefetching.

## 4. Upper Bound
With software write-combine buffers (one cache-line buffer per partition) and non-temporal stores, partitioning achieves $O(k\cdot N/B)$ cache misses with $k=\lceil\log_{F}(N/C)\rceil$ passes and TLB misses bounded by keeping $F\le$ (TLB reach), i.e. effectively $O(N/B)$ TLB misses total — optimal up to constants. The practical optimum is **1–2 passes** for typical $N$, $C$, $T$, which the studies above confirm matches the analytic $k^\*$.

## 5. Lower Bound
Reading and writing each tuple at least once per pass gives an unconditional $\Omega(N/B)$ I/O per pass; reducing to cache-sized buckets requires $\Omega(\log_{M/B}(N/C))$ passes in the external-memory model — the same sorting-style $\Omega\!\big(\frac{N}{B}\log_{M/B}\frac{N}{B}\big)$ bound (Aggarwal–Vitter) when full partitioning is needed. The TLB-miss lower bound is architectural: writing to $F>T$ live partitions forces $\Omega(N)$ TLB misses absent buffering, motivating the $F\le T$ ceiling. No NP-hardness — the difficulty is constant-factor and skew, not combinatorial.

## 6. The Gap
For **uniform** data the optimal $(k,F)$ is essentially **closed**: the analytic $k^\*=\lceil\log_T(N/C)\rceil$ with $F\le$ TLB reach plus software buffers matches both the I/O lower bound and measured performance. What keeps it **partially-solved**: (i) **data skew** — a single heavy bucket can violate the size target, and optimal *adaptive per-bucket* fan-out under arbitrary skew lacks a clean characterization; (ii) cross-architecture portability of the constants (TLB reach, huge pages, prefetcher behavior, NUMA write bandwidth) means the "optimal" fan-out must be re-derived per CPU/GPU; (iii) interaction with concurrency/NUMA. Closing it: a skew- and architecture-parametric model giving provably optimal adaptive fan-out.

## 7. Current Research (as of June 2026)
Directions: **adaptive / learned fan-out** that detects skew at runtime and varies per-bucket pass count *(frontier — verify)*; huge-page and TLB-reach-aware partitioning on modern server CPUs with very large TLBs that raise the safe fan-out ceiling *(frontier — verify)*; GPU radix partitioning where the analogous constraints are shared-memory size and coalescing rather than TLB; CXL/NUMA-aware write placement. Groups: TUM, ETH Zürich, Columbia (Ross), TU Dortmund (Dittrich).

## 8. Future Work
A unified skew-and-hardware-parametric model for optimal adaptive fan-out with guarantees; automatic fan-out tuning portable across CPU TLB regimes and GPU shared-memory; integration with worst-case-optimal multi-way join partitioning; co-tuning fan-out with vectorized/streaming-store kernels.

## 9. Key References
- **[Foundational]** S. Manegold, P. Boncz, M. Kersten. *Optimizing Main-Memory Join on Modern Hardware.* IEEE TKDE, 2002.
- **[SOTA]** C. Kim, T. Kaldewey, V. W. Lee, E. Sedlar, A. D. Nguyen et al. *Sort vs. Hash Revisited: Fast Join Implementation on Modern Multi-Core CPUs.* VLDB, 2009.
- **[SOTA]** O. Polychroniou, K. A. Ross. *A Comprehensive Study of Main-Memory Partitioning and Its Application to Large-Scale Comparison- and Radix-Sort.* SIGMOD, 2014.
- **[SOTA]** C. Balkesen, J. Teubner, G. Alonso, M. T. Özsu. *Main-Memory Hash Joins on Multi-Core CPUs: Tuning to the Underlying Hardware.* ICDE, 2013.
- **[Survey]** S. Schuh, X. Chen, J. Dittrich. *An Experimental Comparison of Thirteen Relational Equi-Joins in Main Memory.* SIGMOD, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
