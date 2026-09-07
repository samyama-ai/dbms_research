---
id: 03-query-processing/vector-batch-sizing
title: "Optimal vector batch and morsel sizing"
topic: 03-query-processing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Optimal vector batch and morsel sizing

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/vector-batch-sizing` · **Status:** empirically-open

## 1. Problem Statement

Vectorized and morsel-driven engines process data in two nested granularities. The **vector
(batch)** is the unit on which SIMD primitives operate — a few hundred to a few thousand
values per column. The **morsel** is the unit of work a worker thread grabs for
parallel scheduling — typically tens to hundreds of thousands of tuples. Both sizes are
tuning knobs that trade off three effects: **cache residency** (a batch's working set must
fit in L1/L2 so intermediate columns are not evicted), **SIMD/throughput utilization** (large
batches amortize loop setup and keep vector lanes full), and **per-batch instruction
overhead** (dispatch, function-call, and bounds-check costs amortized over the batch).

Problem: given a pipeline, hardware profile $H$ (cache sizes, SIMD width, core count, NUMA
topology), and data characteristics, **choose the vector size $v$ and morsel size $m$
(possibly per operator and per pipeline) that minimize end-to-end latency** while keeping
load balance and memory bounded.

Variants: **static** (pick $v,m$ at plan time from a cost model); **adaptive** (adjust $v,m$
online from observed cache-miss / IPC counters); **per-operator** (different $v$ for a hash
build vs. a filter scan).

## 2. Mathematical Foundations

Let a pipeline maintain $w$ active intermediate columns of width $b$ bytes. The per-batch
working set is $\approx w \cdot v \cdot b$; cache residency requires $w\cdot v\cdot b \lesssim
C_{L2}$, giving an upper bound $v \le C_{L2}/(w b)$. Runtime per tuple modeled as
$$t(v) = \underbrace{\frac{c_{\text{fixed}}}{v}}_{\text{dispatch/setup}} + \underbrace{c_{\text{simd}}(v)}_{\text{SIMD eff.}} + \underbrace{c_{\text{miss}}(v)}_{\text{cache misses}},$$
where $c_{\text{fixed}}/v$ decreases with $v$, $c_{\text{simd}}$ saturates once $v$ exceeds a
small multiple of the SIMD width $W$, and $c_{\text{miss}}$ jumps once $v$ exceeds the
residency bound. The optimum $v^\*$ sits in the plateau between "too small to amortize
dispatch" and "too large to stay cache-resident" — a convex-ish trade-off with a sharp cliff
at the cache boundary.

For morsels, the scheduling model is **morsel-driven / work-stealing parallelism** (Leis et
al., SIGMOD 2014): with $P$ workers and total work $T$, makespan $\approx T/P + m\cdot
c_{\text{tuple}}$ (granularity tax) plus stealing overhead $O(P\log(T/m))$. Smaller $m$
improves load balance (lower skew tail) but raises scheduling overhead — a granularity
trade-off analyzed in classic parallel-scheduling theory (Graham's bound, Blumofe–Leiserson
work-stealing).

## 3. State of the Art (SOTA)

- **Systems SOTA.** *MonetDB/X100* (CIDR 2005) introduced the cache-resident vector and
  empirically fixed $v\approx 1024$. *DuckDB* uses a default vector size of 2048 (a tuned
  compile-time constant). *HyPer/Umbra* morsel-driven execution (Leis et al., SIGMOD 2014)
  uses morsels of ~$10^5$ tuples with work-stealing dispatch.
- The defining empirical result is Zukowski et al., showing a broad **plateau** where any
  $v$ from a few hundred to a few thousand is near-optimal, with steep degradation only when
  $v$ leaves cache or shrinks below the dispatch-amortization point.
- No engine ships a *provably* optimal adaptive sizer; values are hand-tuned constants.

## 4. Upper Bound

The best-understood guarantee is the **cache-residency upper bound**: choosing $v$ so the
batch working set fits in L2 bounds $c_{\text{miss}}$ at the L1/L2 miss rate, and choosing
$v \ge \Theta(c_{\text{fixed}}/c_{\text{tuple}})$ bounds dispatch overhead by a constant
fraction. Together they place $t(v)$ within a small constant factor of the per-tuple optimum
in the cache-aware (RAM with cache) model. For morsels, **work-stealing achieves
$O(T/P + \text{span})$ expected makespan** (Blumofe–Leiserson, JACM 1999), and morsel-driven
scheduling inherits near-linear speedup when $m$ is small relative to $T/P$.

## 5. Lower Bound

There is no NP-hardness here; the lower bounds are **structural**. (i) Cache lower bounds:
any execution touching $w$ columns over $n$ tuples incurs $\Omega(wn/B)$ cache-line transfers
in the external-memory model, so no $v$ avoids the bandwidth floor — sizing only controls the
*multiplier*. (ii) Scheduling: for $P$ workers and a load-skewed morsel distribution, any
oblivious fixed granularity has makespan $\ge (1 + (m/\bar{m})\cdot s)\cdot T/P$ where $s$ is
the skew — the granularity tax is unavoidable without adaptive splitting (cf.
skew-resilient-parallel-join). (iii) The cache cliff is a hard nonconvexity: once $v$ exceeds
$C/(wb)$ miss cost rises by a constant factor, so the optimal-$v$ region is data- and
machine-dependent and cannot be fixed statically with worst-case optimality.

## 6. The Gap

The gap is **empirical**: a wide plateau means simple constants are "good enough" most of the
time, so there has been little pressure to close a precise bound. But the plateau's *edges*
move with $w$ (pipeline width), $b$ (type width), SIMD generation, and NUMA placement, and no
model predicts the optimal $(v,m)$ across this space. The open question is whether a
lightweight online controller (using hardware counters) can provably track $v^\*,m^\*$ within
a constant factor as pipeline width and skew vary — and whether $v$ and $m$ should be chosen
jointly with NUMA placement and SIMD layout rather than independently.

## 7. Current Research (as of June 2026)

- **Adaptive vector sizing** driven by runtime IPC and cache-miss counters; shrinking batches
  for wide pipelines and growing them for narrow SIMD-bound ones. Active in the CWI (Boncz)
  and TUM (Leis/Neumann) lines.
- **Morsel-size adaptation under skew**: dynamically splitting morsels when stealing rates
  spike (overlaps with skew-resilient join scheduling). *(frontier — verify)* recent
  many-core results report sub-linear scaling fixes from adaptive morsel splitting.
- **SIMD-width-aware sizing** for AVX-512 / SVE / wide GPU warps, where the residency cliff
  and the SIMD-saturation point interact differently. *(frontier — verify)*

## 8. Future Work

- A predictive cost model mapping $(w, b, H)$ to $(v^\*, m^\*)$ with a proven competitive
  ratio under unknown skew.
- Joint optimization of batch size, morsel size, and NUMA placement in one scheduler.
- Hardware-counter-driven controllers with stability guarantees (no oscillation).

## 9. Key References

- **[Foundational]** Boncz, Zukowski, Nes. *MonetDB/X100: Hyper-Pipelining Query Execution.* CIDR 2005. — [DBLP](https://dblp.org/rec/conf/cidr/BonczZN05.html)
- **[Foundational]** Leis, Boncz, Kemper, Neumann. *Morsel-Driven Parallelism: A NUMA-Aware Query Evaluation Framework for the Many-Core Age.* SIGMOD 2014. — [DOI](https://doi.org/10.1145/2588555.2610507)
- **[Foundational]** Blumofe, Leiserson. *Scheduling Multithreaded Computations by Work Stealing.* JACM 1999. — [DOI](https://doi.org/10.1145/324133.324234)
- **[SOTA]** Raasveldt, Mühleisen. *DuckDB: An Embeddable Analytical Database.* SIGMOD 2019. — [DOI](https://doi.org/10.1145/3299869.3320212)
- **[Survey]** Kersten, Leis, Kemper, Neumann, Pavlo, Boncz. *Everything You Always Wanted to Know About Compiled and Vectorized Queries.* VLDB 2018. — [DOI](https://doi.org/10.14778/3275366.3284966)

## 10. Worked Example

A filter pipeline keeps $w=4$ active columns of $b=8$ bytes, on a CPU with $C_{L2}=256$ KB. The residency bound is
$$v \le \frac{C_{L2}}{w\,b} = \frac{262144}{4\cdot 8} = 8192 \text{ tuples.}$$
Take per-tuple cost $t(v)=\frac{c_{\text{fixed}}}{v}+c_{\text{simd}}+c_{\text{miss}}(v)$ with $c_{\text{fixed}}=200$ ns/batch, $c_{\text{simd}}=0.5$ ns, and $c_{\text{miss}}=0$ while resident but $+2$ ns once $v>8192$.

| $v$ | dispatch $200/v$ | simd | miss | $t(v)$ (ns) |
|------|------|------|------|------|
| 64 | 3.13 | 0.5 | 0 | **3.63** |
| 1024 | 0.20 | 0.5 | 0 | **0.70** |
| 8192 | 0.024 | 0.5 | 0 | **0.52** |
| 16384 | 0.012 | 0.5 | 2 | **2.51** |

The optimum sits at the plateau just under the cache cliff: $v^\*\approx 8192$. Note the steep jump at $v=16384$ once the working set spills L2 — exactly the nonconvex cliff Section 5 describes. DuckDB's default $v=2048$ lands safely on the plateau ($t\approx 0.60$ ns).

---
*Part of the [DBMS Research catalog](../../README.md).*
