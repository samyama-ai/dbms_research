---
id: 14-main-memory-db/bandwidth-optimal-scans
title: "Memory-Bandwidth-Optimal Scans"
topic: 14-main-memory-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Memory-Bandwidth-Optimal Scans

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/bandwidth-optimal-scans` · **Status:** open
> **Verification note:** The ByteSlice (SIGMOD 2015) fourth author is Wenjian Xu, not "Li"; corrected in section 3 and the references.

## 1. Problem Statement
In a main-memory database, a full-table or large-segment scan with predicate evaluation is no longer disk-bound — it is **memory-bandwidth-bound**. Once a column does not fit in cache, the dominant cost is moving bytes from DRAM (and across NUMA/UPI interconnects) into the cores. **The problem:** design scan and predicate-evaluation kernels that *provably saturate* the available memory bandwidth — driving the achieved fraction of peak STREAM bandwidth toward 1 — across all sockets of a NUMA machine, for realistic predicates (range, equality, conjunctions, LIKE, expression trees) and physical layouts (row, column, PAX, compressed, bit-packed).

Formally:
- **Optimization variant:** maximize achieved bandwidth $\beta_{\text{ach}}$ (bytes/s of useful column data consumed) subject to producing the correct selection vector / aggregate, ideally proving $\beta_{\text{ach}} \ge (1-\epsilon)\,\beta_{\text{peak}}$.
- **Decision variant:** given a predicate $P$, a layout $\mathcal{L}$, and a NUMA topology, does a schedule exist that keeps every memory controller at $\ge \theta$ utilization with no core stalling on remote latency?
- **Counting/work variant:** minimize *bytes touched* (the real lower bound) via compression, zone maps, and early pruning, since the true optimum is to read fewer bytes, not just read them faster.

A solution must be robust to selectivity, NUMA placement, prefetch behavior, and compression.

## 2. Mathematical Foundations
Model the machine by the **Roofline**: achievable performance $\le \min(\pi,\ \beta_{\text{peak}}\cdot I)$ where $\pi$ is peak compute (ops/s), $\beta_{\text{peak}}$ peak bandwidth (bytes/s), and $I$ the **operational intensity** (ops/byte). A scan predicate has low $I$ (a few compares per loaded value), so it sits on the *bandwidth-bound* slope: runtime $\ge V/\beta_{\text{peak}}$ where $V$ is bytes that must be read. The optimal kernel is one whose runtime equals this floor.

On a $p$-socket NUMA machine, peak aggregate bandwidth is $\sum_{s=1}^{p}\beta_s$ only if each socket's cores read **local** memory; a remote access pays interconnect latency $\ell_{\text{remote}}$ and shares limited inter-socket bandwidth $\beta_{\text{xnode}}$. Achieved bandwidth is

$$\beta_{\text{ach}} = \sum_{s=1}^{p} \min\!\bigl(\beta_s,\ \tfrac{\text{cores}_s \cdot \text{MLP}}{\ell_s}\bigr),$$

where $\textbf{MLP}$ (memory-level parallelism) is the number of outstanding misses per core (bounded by Line-Fill Buffers / MSHRs). Saturation requires enough independent in-flight requests ($\text{MLP}\cdot\text{cores} \ge \beta_{\text{peak}}\cdot\ell$, **Little's Law** for the memory system) — this is why software prefetching, wide SIMD, and many cores matter. Compression reduces $V$ (lowering the floor itself), trading decode compute ($I$ rises) against bytes moved; the optimum balances them at the Roofline ridge point.

## 3. State of the Art (SOTA)
- **MonetDB/X100 (Vectorwise)** — Boncz, Zukowski, Nes (CIDR 2005): vectorized, cache-resident batch processing; the foundational bandwidth-conscious execution model.
- **SIMD scans / BitWeaving** — Li, Patel (SIGMOD 2013): bit-parallel predicate evaluation packing many values per word, approaching one cycle per several values.
- **ByteSlice / column-scan kernels** — Feng, Lo, Kao, Xu (SIGMOD 2015): byte-decomposed layout for early-exit SIMD scans at near-bandwidth rates.
- **NUMA-aware operators** — Leis, Boncz, Kemper, Neumann (*Morsel-Driven Parallelism*, SIGMOD 2014): morsel scheduling that keeps work NUMA-local and load-balanced — the canonical systems answer to multi-socket saturation.
- Hardware-conscious aggregation/joins: Balkesen, Teubner, Alonso, Özsu (ICDE 2013) establish bandwidth/cache-bound kernel design methodology.

## 4. Upper Bound
The achievable upper bound is the **Roofline floor**: a well-engineered SIMD column scan reads each needed byte once and evaluates the predicate at compute cost hidden under memory latency, achieving $\beta_{\text{ach}} \to \beta_{\text{peak}}$ on a single socket (BitWeaving/ByteSlice demonstrate $>80$–$95\%$ of STREAM for selective range predicates). With **morsel-driven** scheduling, this extends to $p$ sockets at $\approx \sum_s \beta_s$ when data is partitioned NUMA-locally and morsels are small enough to balance load. With zone maps / compression, the *effective* bound drops below the raw-bytes floor because $V$ shrinks. Best known: near-peak local bandwidth with linear NUMA scaling on partitioned, predicate-prunable columns.

## 5. Lower Bound
Any correct scan must read every byte not excludable by metadata: an **information-theoretic / I/O-complexity** floor of $\Omega(V/\beta_{\text{peak}})$ time where $V$ is the non-pruned column footprint — you cannot answer a predicate over data you never load (adversary: a predicate satisfied by the last element forces reading all). In the **external-memory / cache-oblivious** model (Aggarwal–Vitter), a scan is $\Theta(V/B)$ block transfers, optimal and unimprovable. Across NUMA, the **cross-socket bandwidth** $\beta_{\text{xnode}} \ll \sum_s \beta_s$ imposes a structural penalty: any schedule with a fraction $f$ of remote accesses is capped at $\beta_{\text{ach}} \le \beta_{\text{xnode}}/f$, so adversarial placement (data not co-located with consuming cores) provably prevents saturation — a communication-bandwidth lower bound. Latency-bound stalls give a further floor when MLP is insufficient (Little's Law).

## 6. The Gap
For a **single socket, simple predicates, columnar layout**, the problem is effectively closed — kernels hit the Roofline floor. The genuine open gap is **multi-socket robustness under adverse placement and complex predicates**: there is no scan engine that *provably* saturates aggregate NUMA bandwidth when data is not perfectly partitioned (e.g., shared dimension tables, skewed access, dynamic repartitioning cost), nor a tight characterization of the achievable $\beta_{\text{ach}}$ as a function of predicate structure (expression trees, string/regex, dictionary-coded columns with variable decode cost). Closing it requires either a placement-and-schedule algorithm with a proven competitive ratio against the cross-socket bandwidth bound, or a proof that worst-case placement is inherently sub-saturating.

## 7. Current Research (as of June 2026)
- **CXL-attached and disaggregated memory** scans, where a new, slower tier with its own bandwidth/latency reshapes the Roofline and placement problem entirely *(frontier — verify)*.
- Scans on **GPU/FPGA/SmartNIC** and near-memory/processing-in-memory (PIM) units that move predicate evaluation to the bytes, sidestepping the interconnect *(frontier — verify)*.
- **Learned/adaptive layout and zone-map** selection that minimizes $V$ per workload, fusing pruning with bandwidth saturation *(frontier — verify)*.
- Groups: TUM (Neumann/Leis), CWI Database Architectures (Boncz), Wisconsin (Patel lineage), ETH Zürich (Alonso/Teubner), MIT.

## 8. Future Work
- A NUMA scan scheduler with a proven competitive ratio against the cross-socket bandwidth lower bound under arbitrary placement.
- Tight per-predicate-class models of achievable bandwidth (regex, expression trees, variable-length decode).
- Co-optimizing compression, pruning, and bandwidth so the *bytes-touched* floor and the *bytes/s* ceiling are jointly minimized.
- Roofline-style analysis extended to CXL/PIM tiers and energy (bandwidth per joule).

## 9. Key References
- **[Foundational]** P. Boncz, M. Zukowski, N. Nes. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR, 2005. — [PDF](https://www.cidrdb.org/cidr2005/papers/P19.pdf)
- **[SOTA]** V. Leis, P. Boncz, A. Kemper, T. Neumann. *Morsel-Driven Parallelism: A NUMA-Aware Query Evaluation Framework for the Many-Core Age.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2610507)
- **[SOTA]** Y. Li, J. M. Patel. *BitWeaving: Fast Scans for Main Memory Data Processing.* SIGMOD, 2013. — [DOI](https://doi.org/10.1145/2463676.2465322)
- **[SOTA]** Z. Feng, E. Lo, B. Kao, W. Xu. *ByteSlice: Pushing the Envelope of Main Memory Data Processing with a New Storage Layout.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2747642)
- **[Foundational]** S. Williams, A. Waterman, D. Patterson. *Roofline: An Insightful Visual Performance Model for Multicore Architectures.* CACM, 2009. — [DOI](https://doi.org/10.1145/1498765.1498785)
- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)

## 10. Worked Example

A column of $V = 4\,\text{GiB}$ of `int32` values is scanned for `x > 100` on one socket with peak bandwidth $\beta_{\text{peak}} = 40\,\text{GB/s}$. The Roofline floor is runtime $\ge V/\beta_{\text{peak}} = 4.29\times10^9 / 40\times10^9 \approx 0.107\,\text{s}$. Operational intensity is tiny: $\sim 1$ compare per 4 bytes, $I \approx 0.25$ ops/byte, so $\pi$ never binds — the kernel is bandwidth-bound and the floor is the target.

Little's Law check: to keep $40\,\text{GB/s}$ in flight at DRAM latency $\ell \approx 80\,\text{ns}$ over 64-byte lines, the needed in-flight lines are $\beta_{\text{peak}}\cdot\ell / 64 = (40\times10^9 \cdot 80\times10^{-9})/64 \approx 50$ outstanding misses. With $\sim 10$ MSHRs/core, that needs $\ge 5$ cores issuing independent prefetched streams. A zone map pruning 75\% of blocks cuts $V$ to $1\,\text{GiB}$, dropping the floor to $\approx 0.027\,\text{s}$ — reading fewer bytes beats reading them faster.

---
*Part of the [DBMS Research catalog](../../README.md).*
