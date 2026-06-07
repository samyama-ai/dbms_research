---
id: 03-query-processing/cache-simd-hash-join
title: "Cache- and SIMD-optimal hash joins"
topic: 03-query-processing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Cache- and SIMD-optimal hash joins

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/cache-simd-hash-join` · **Status:** empirically-open

## 1. Problem Statement

The in-memory hash join — build a hash table on the smaller relation $R$, then probe it with
the larger relation $S$ — is the workhorse of analytical execution, and on modern hardware its
cost is dominated not by instructions but by **memory stalls** (random hash-table accesses miss
cache and TLB) and by under-utilized **SIMD/gather** units. The problem: design hash-table
**layouts** and **probing schedules** that minimize cache/TLB misses *and* maximize SIMD
throughput (vectorized hashing, gather/scatter, software prefetching), **portably across
microarchitectures** (cache hierarchy, SIMD width, gather latency, NUMA distance).

Variants: **partitioned vs. non-partitioned** (radix-partition so each partition's table fits
in cache, vs. a single shared table with prefetching); **layout** (open-addressing vs.
chained, key/payload packing, AoS vs. SoA); **SIMD probing** (process $W$ probe keys per
vector with gather and conflict detection). "Solving" means an algorithm that is provably or
empirically near-optimal in cache transfers and SIMD utilization without per-machine tuning.

## 2. Mathematical Foundations

In the **external-memory / cache model** (block size $B$, cache size $M$), a join of $|R|+|S|$
tuples requires $\Omega(\frac{|R|+|S|}{B})$ transfers (one scan) and the partitioned hash join
attains $O\!\left(\frac{|R|+|S|}{B}\big(1 + \log_{M/B}\frac{|R|}{M}\big)\right)$ — i.e., a
constant number of passes when $|R|$ is within a few factors of $M$, matching sort up to the
base of the log. The key design quantity is the **radix fan-out** $f$: with $p$ partitioning
passes, $f^p \approx |R|/M$, and each pass must keep its $f$ output buffers within TLB/cache to
avoid thrashing (the *TLB-miss cliff* at $f \gtrsim$ #TLB entries). Probing a table of $g$
distinct keys with random access costs $\Theta(1)$ instructions but $\Theta(1)$ cache miss per
probe when $g$ exceeds $M$; prefetching hides this latency only if enough independent probes
are in flight (memory-level parallelism). SIMD gather processes $W$ keys per instruction but
its effective throughput depends on the gather's hardware latency and on hash collisions
(conflict detection).

## 3. State of the Art (SOTA)

- **Foundational systems result.** Manegold, Boncz, Kersten, *"Optimizing Main-Memory Join on
  Modern Hardware"* (TKDE 2002), introduced **radix-partitioned** joins to make each partition
  cache-resident and modeled the cost in cache misses.
- **Hardware-conscious vs. hardware-oblivious debate.** Balkesen et al., *"Main-Memory Hash
  Joins on Multi-Core CPUs"* (ICDE 2013) and Blanas et al. (SIGMOD 2011) gave dueling
  empirical results on whether radix partitioning beats a simple prefetched non-partitioned
  join — the answer is workload- and machine-dependent.
- **SIMD/vectorized hashing.** Polychroniou, Raghavan, Ross, *"Rethinking SIMD Vectorization
  for In-Memory Databases"* (SIGMOD 2015) gave gather/scatter-based vectorized hash probing.
- **Comprehensive comparison.** Schuh, Chen, Dittrich, *"An Experimental Comparison of Thirteen
  Relational Equi-Joins in Main Memory"* (SIGMOD 2016) is the reference benchmark; no single
  algorithm wins everywhere.

## 4. Upper Bound

The radix-partitioned hash join achieves the **cache-oblivious/aware near-optimal**
$O\!\left(\frac{N}{B}\log_{M/B}\frac{N}{M}\right)$ cache-transfer bound (typically 1–2 passes
in practice), matching the external-memory sorting bound and within a constant of the scan
lower bound when $R$ nearly fits in cache. SIMD vectorized probing achieves up to $W\times$
instruction throughput where gather is not the bottleneck. Software write-combine buffers and
non-temporal stores bound partitioning's write traffic. These are the best *known* bounds;
they are tight against the model but the *constants* (and which variant wins) depend on the
machine.

## 5. Lower Bound

- **I/O lower bound.** Any join must read all inputs: $\Omega(N/B)$ transfers; and a
  multi-pass partitioning to cache-resident pieces inherits the permutation/sorting I/O lower
  bound $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$ when $|R|\gg M$ (Aggarwal–Vitter, 1988).
- **Random-probe cache cost.** With a table larger than cache, an information-theoretic /
  cell-probe argument forces $\Omega(1)$ expected cache miss per uncorrelated probe;
  prefetching reduces *latency* but not the *miss count*.
- **No worst-case-optimal portable algorithm** is known: the partition-vs-prefetch crossover
  shifts with cache size, TLB reach, gather latency, and NUMA distance, so any *fixed*
  algorithm is provably suboptimal on some machine in this empirical sense — hence
  *empirically-open*.

## 6. The Gap

Both partitioned and non-partitioned variants are within constant factors of the cache and
SIMD bounds; the open part is **portability and auto-tuning**: there is no algorithm that
provably (or even reliably empirically) dominates across the cross-product of cache hierarchies,
SIMD widths, gather latencies, and NUMA topologies without per-machine tuning of fan-out,
prefetch distance, and partition/no-partition choice. Closing it means either an
auto-tuning/learned selector with guarantees, or a single layout that is robust across all
these axes.

## 7. Current Research (as of June 2026)

- **Architecture-portable auto-tuning** of radix fan-out, prefetch distance, and the
  partition/no-partition decision via lightweight micro-benchmarks or learned cost models.
  Active in the TUM (Leis/Neumann), CWI (Boncz), and ETH (Alonso) lines.
- **Wide-SIMD and SVE/AVX-512 gather-conflict-aware probing**, and **AMX/accelerator** offload
  of hashing. *(frontier — verify)*
- **NUMA-coupled join layouts** that co-optimize partitioning with socket-local placement
  (see numa-aware-execution). *(frontier — verify)*

## 8. Future Work

- A portable, auto-tuned hash join with provable near-optimality across the architecture space.
- Co-design with SIMD batch sizing and NUMA placement rather than tuning each in isolation.
- Robustness to key skew folded into the cache-optimal layout (heavy-hitter side tables).

## 9. Key References

- **[Foundational]** Manegold, Boncz, Kersten. *Optimizing Main-Memory Join on Modern Hardware.* IEEE TKDE 2002. — [DOI](https://doi.org/10.1109/TKDE.2002.1019210)
- **[Foundational]** Aggarwal, Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[SOTA]** Balkesen, Teubner, Alonso, Özsu. *Main-Memory Hash Joins on Multi-Core CPUs: Tuning to the Underlying Hardware.* ICDE 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544839)
- **[SOTA]** Polychroniou, Raghavan, Ross. *Rethinking SIMD Vectorization for In-Memory Databases.* SIGMOD 2015. — [DOI](https://doi.org/10.1145/2723372.2747645)
- **[Survey]** Schuh, Chen, Dittrich. *An Experimental Comparison of Thirteen Relational Equi-Joins in Main Memory.* SIGMOD 2016. — [DOI](https://doi.org/10.1145/2882903.2882917)
- **[SOTA]** Blanas, Li, Patel. *Design and Evaluation of Main Memory Hash Join Algorithms for Multi-core CPUs.* SIGMOD 2011. — [DOI](https://doi.org/10.1145/1989323.1989328)

## 10. Worked Example

Join build side $R$ with $|R|=2^{27}$ tuples (16 B each $=2$ GB), probe $|S|=2^{30}$. Cache $M=2^{23}$ tuples (128 MB); the hash table is $\approx 2|R|=2^{28}$ slots $\gg M$.

**Non-partitioned probe.** Each of the $2^{30}$ probes hits a random slot $>$ cache, so $\approx 2^{30}$ cache misses at $\sim 100$ cycles $=10^{11}$ cycles — memory-stall bound.

**Radix-partitioned.** Choose fan-out so each partition fits in cache: need $f^p\gtrsim |R|/M = 2^{27}/2^{23}=16$, so a **single pass** with $f=16$ suffices. Cost: $O(\tfrac{|R|+|S|}{B})$ streaming transfers, then probes that hit cache-resident sub-tables. With $B=8$ tuples/line, $\tfrac{|R|+|S|}{B}\approx \tfrac{2^{30}}{8}=2^{27}$ transfers — roughly $1000\times$ fewer misses than the random-probe approach.

**The TLB cliff.** If instead we picked $f=4096$ to one-pass a larger $R$, the 4096 output buffers exceed a typical 64-entry data-TLB reach, so each scatter write triggers a TLB miss — the partitioning pass itself thrashes. This is exactly why the optimal fan-out is machine-specific (TLB reach, cache size), and no single fixed $f$ is portable.

---
*Part of the [DBMS Research catalog](../../README.md).*
