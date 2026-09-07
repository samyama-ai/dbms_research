---
id: 22-provenance-lineage/low-overhead-runtime-capture
title: "Low-Overhead Runtime Provenance Capture"
topic: 22-provenance-lineage
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Low-Overhead Runtime Provenance Capture

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/low-overhead-runtime-capture` · **Status:** empirically-open

## 1. Problem Statement
Instrument a production query engine so that, while executing arbitrary queries, it records **fine-grained lineage** — for each output row (and ideally each output *cell*), the set of base rows/cells that produced it — with overhead that is **bounded and predictable**: a small multiplicative slowdown in latency and throughput, and bounded extra memory, *without* falling back to full re-execution. The capture must be *always-on* (production, not a debug rerun) so it can serve auditing, debugging, GDPR deletion-impact, and incremental-recompute use cases.

Variants: **(row-level)** capture only output→input row mappings. **(cell-level / where-provenance)** capture which source cell flows to which output cell. **(decision)** is there a capture scheme meeting a slowdown budget $\le (1+\epsilon)$? **(optimization)** minimize overhead subject to a completeness/precision requirement, or maximize precision under a fixed overhead budget. **(predictability)** bound *tail* latency, not just the mean.

## 2. Mathematical Foundations
Capture is a homomorphic side-channel: alongside the relational semiring $(K,+,\times)$ for *values*, lineage flows in the provenance semiring $\mathbb{N}[X]$ via the **same operator algebra**, so instrumentation is a functor on the physical plan — each operator $\mathit{op}$ gets a paired $\mathit{op}^{\text{prov}}$ that maps input annotations to output annotations. Overhead is governed by the **annotation size per tuple**: a join's output annotation is the $\times$ of its inputs, so naive eager capture inflates a tuple of width $w$ to carry up to $O(\text{join-arity})$ identifiers. The space cost over a pipeline is bounded by the **factorized size** ($O(|D|^{\mathsf{fhtw}})$) if shared, or the **flat AGM size** ($O(|D|^{\rho^*})$) if materialized per output. Predictability is an *amortized vs. worst-case* question: capture inserts work proportional to data movement, so latency overhead $\approx c\cdot(\text{bytes moved})$, but operators with output blow-up (joins, cross products) break the linear model. Sampling/approximation introduces a precision–overhead trade governed by a coverage probability $1-\delta$.

## 3. State of the Art (SOTA)
- **Systems:** **Smoke** (Psallidas–Wu, SIGMOD 2018) builds *lineage indexes* inline during execution, achieving near-interactive capture overhead by tightly integrating capture with operator code. **Perm/GProM** (Glavic et al.) achieve capture by query rewriting (portable, but overhead varies). **Titian** (Interlandi et al., VLDB 2015) adds data lineage to **Apache Spark** with reported modest overhead via per-stage tracking. **Lima / Ariadne / RAMP** track lineage in dataflow (Pig/MapReduce). **Provenance in Trio** and **DBNotes** carry annotations natively.
- **Production reality:** most OLTP/OLAP engines (Postgres, Snowflake, Spark SQL) offer *coarse* table-level lineage (catalog/metadata), not always-on row/cell capture, precisely because the fine-grained overhead budget is unproven at scale.

## 4. Upper Bound
For **SPJ** pipelines, inline index-based capture (Smoke) demonstrates overhead within a **small constant factor** (often <2x, sometimes near-zero with the right index) of uninstrumented execution, and supports backward/forward queries in time near-proportional to the answer size. By the semiring functor, capture adds $O(1)$ work per tuple per operator for row-level lineage, so total capture time is $O(\text{plan work})$ — i.e., a *constant multiplicative* overhead — when annotations are pointers and sharing is exploited. Cell-level (where-provenance) adds a factor of the output arity. Sampling-based capture reduces overhead to any target $(1+\epsilon)$ at the cost of $(1-\delta)$ coverage.

## 5. Lower Bound
No nontrivial *unconditional* lower bound forbids cheap row-level capture, but **worst-case space is forced**: to be recomputation-complete on join-heavy queries, stored lineage must reach $\Omega(|D|^{\rho^*})$ (AGM-tight instances), so *predictable, bounded* overhead is impossible in the worst case without approximation — a space lower bound inherited from output-size lower bounds and **communication-complexity** arguments for streaming. Cell-probe lower bounds on the lineage index imply that supporting both fast capture *and* fast backward queries cannot both be $O(1)$ for adversarial workloads. Hence the *predictability* guarantee is provably unattainable in the strong (worst-case) sense — the problem is empirically-open at the *typical-workload* level.

## 6. The Gap
The theory says worst-case overhead is unbounded (join blow-up); systems show typical-case overhead is small (Smoke, Titian). The **open gap is empirical**: no engine demonstrates *always-on, cell-level* capture with **provably bounded tail latency** across mixed production workloads, and there is no accepted model predicting which queries will blow up. Closing it needs (a) a tail-latency-aware cost model, (b) adaptive fallback to approximate/sampled capture when blow-up is detected, with measured guarantees.

## 7. Current Research (as of June 2026)
- Pushing fine-grained capture into **vectorized/columnar and JIT-compiled** engines (DuckDB-, Velox-class), where per-tuple annotation cost can be amortized over batches *(frontier — verify)*.
- **Approximate / sampled lineage** with coverage guarantees for high-fanout operators; sketch-backed where-provenance *(frontier — verify)*.
- Hardware- and OS-level capture (eBPF, instrumentation) for predictable overhead; lineage as a first-class column managed by the storage engine.

## 8. Future Work
A tail-latency SLA for provenance capture and an admission-control mechanism that degrades to sampling under blow-up. Standard overhead benchmarks (row vs cell, OLTP vs OLAP vs streaming). Co-design of physical operators with capture so annotation flows for free. Cell-level capture through expression evaluation (UDF-aware).

## 9. Key References
- **[SOTA]** Fotis Psallidas, Eugene Wu. *Smoke: Fine-grained Lineage at Interactive Speed.* PVLDB, 2018. — [DOI](https://doi.org/10.14778/3199517.3199522) · [arXiv](https://arxiv.org/abs/1801.07237)
- **[SOTA]** Matteo Interlandi, et al. *Titian: Data Provenance Support in Spark.* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2850583.2850595)
- **[Foundational]** Boris Glavic, Gustavo Alonso. *Perm: Processing Provenance and Data Through Query Rewriting.* ICDE, 2009. — [DOI](https://doi.org/10.1109/ICDE.2009.15)
- **[Foundational]** Yingwei Cui, Jennifer Widom, Janet Wiener. *Tracing the Lineage of View Data in a Warehousing Environment.* ACM TODS, 2000. — [DOI](https://doi.org/10.1145/357775.357777)
- **[Foundational]** Albert Atserias, Martin Grohe, Dániel Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008 (AGM bound). — [DBLP](https://dblp.org/rec/conf/focs/AtseriasGM08.html) · [arXiv](https://arxiv.org/abs/1711.03860)
- **[Survey]** Boris Glavic. *Data Provenance: Origins, Applications, Algorithms, and Models.* Foundations and Trends in Databases, 2021. — [DOI](https://doi.org/10.1561/1900000068)

## 10. Worked Example

Run a self-join $Q = R(x,y) \bowtie_y R(y,z)$ where $R$ is a "star": one hub node $h$ with $R = \{(h, v_i)\} \cup \{(v_i, h)\}$ for $i=1..k$, so $|R| = 2k$.

*Row-level capture, cheap case.* Most engine pipelines move tuples linearly; the semiring functor adds $O(1)$ pointer-tagging per tuple per operator. For an SPJ plan over $N=|R|$ tuples the capture work is $O(\text{plan work})$ — a small constant-factor slowdown, matching Smoke's observed $<2\times$.

*The blow-up that breaks predictability.* But this query's output is large: every $(h,v_i)$ joins with every $(v_j,h)$ through the hub, giving $\Theta(k^2)$ output rows, each needing a lineage record $\{(h,v_i),(v_j,h)\}$. So stored lineage is $\Theta(k^2) = \Theta(N^2)$. The AGM/fractional-edge-cover bound here is $\rho^* = 2$, and indeed $|D|^{\rho^*} = (2k)^2 = \Theta(k^2)$ — the worst-case space floor of section 5 is realized.

*Takeaway.* With $k = 10^4$ the input is $2\!\times\!10^4$ rows but lineage is $\sim\!10^8$ records: a $5000\times$ space inflation on a single operator. A row-count-only cost model would not have predicted it; this is exactly why always-on, bounded-tail capture needs blow-up-aware admission control and a fallback to sampled lineage.

---
*Part of the [DBMS Research catalog](../../README.md).*
