---
id: 18-streaming-queries/streaming-band-joins-bounded-state
title: "Streaming theta/band joins with bounded state"
topic: 18-streaming-queries
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Streaming theta/band joins with bounded state

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/streaming-band-joins-bounded-state` · **Status:** open

## 1. Problem Statement
Given two unbounded streams $R$ and $S$, evaluate a **non-equi join** $R \bowtie_\theta S$ where the predicate $\theta$ is an inequality (band) condition such as $|R.a - S.b| \le \varepsilon$, $R.a < S.b$, or a conjunction of such bands, producing each output tuple incrementally and (under exactly-once) exactly once. The decision/feasibility variant: given a memory budget $M$ and a tardiness budget $\tau$, does there exist an eviction policy under which every join result whose two inputs arrive within window $w$ is emitted within $\tau$ while resident state never exceeds $M$? The optimization variant: minimize peak state (or maximize result completeness) subject to a latency SLO. The counting variant — continuously maintaining $|R \bowtie_\theta S|$ — is the basis for selectivity estimation and downstream sizing.

Unlike equi-joins, band predicates are **not partitionable by hash**: a probe tuple can match an unbounded fraction of the opposite window, so the naive symmetric approach buffers entire windows and the per-tuple probe cost is not constant. The open question is whether provable state *and* latency bounds are simultaneously achievable for general theta predicates, or only for restricted (1-D band, monotone) cases.

## 2. Mathematical Foundations
Model each stream as a sequence of timestamped tuples; a **time-based window** of length $w$ keeps tuples with $t \ge t_{now}-w$. For a 1-D band $|R.a-S.b|\le\varepsilon$, sorting both windows by key turns probing into a range query, so an interval/segment-tree or sorted-list index gives $O(\log n + k)$ per probe for $k$ matches. The intrinsic output rate is governed by the join's instantaneous selectivity; by an **AGM-style** argument the worst-case result size over windows of size $n$ can be $\Theta(n^2)$, so any exact operator has an $\Omega(\text{output})$ unavoidable cost — the question is the *state* (resident memory), not just the work.

Lower bounds come from **communication complexity**: deciding emptiness of a band join across a partition relates to set-disjointness / gap-Hamming variants, giving $\Omega(n)$ space for exact answers in the one-pass sliding-window model. For approximate counting, $\varepsilon$-approximate range-summability via dyadic decomposition (à la $q$-digest / ECM-sketch) yields polylog-space estimators. Submodularity of "coverage" is exploited when choosing which tuples to retain under a memory cap.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** band-join-aware indexing and the sliding-window communication lower bounds frame what is achievable; ECM-sketch (Papapetrou et al., VLDB 2012) gives sketch-based approximate windowed joins.
- **Systems-SOTA:** Apache Flink and Spark Structured Streaming implement **interval joins** (time-bounded band on event time) with state TTL; **BiStream / partitioned band-join** parallelizations (e.g. the "join-matrix" / random-shuffle scheme of Elseidy et al., VLDB 2014) handle theta joins by replicating tuples across a grid of workers. Handshake/symmetric and **PRB (partitioned random band)** schemes underlie distributed theta-join engines.

## 4. Upper Bound
For 1-D band joins with a time window of $w$ and at most $n$ live tuples per side, a balanced search tree indexed on the band key gives **$O(\log n)$ amortized state-maintenance per tuple plus $O(k)$ to emit $k$ matches**, with $O(n)$ resident state — optimal up to logs for exact answers. Distributed join-matrix replication achieves load balance with $O(\sqrt{p})$-factor tuple replication on $p$ workers (RAM/BSP model). Approximate windowed band counts are maintainable in $O(\varepsilon^{-1}\,\mathrm{polylog})$ space.

## 5. Lower Bound
In the **one-pass sliding-window model**, exact band-join emptiness/cardinality across an adversarial split requires $\Omega(n)$ bits by reduction from set-disjointness (communication complexity), so no exact operator beats linear state in general. For multi-dimensional / conjunctive theta predicates, even approximate range counting inherits the **partial-match / cell-probe** hardness, ruling out constant-state exact solutions. No NP-hardness is needed — the obstruction is information-theoretic space, not computational.

## 6. The Gap
For 1-D bands the gap is essentially **closed** ($O(n)$ state is necessary and sufficient). The genuinely open territory is: (a) general multi-attribute theta predicates with *simultaneous* state and latency guarantees; (b) tight bounds for *approximate* band joins with bounded relative error per output; and (c) whether adaptive eviction can guarantee a target completeness under a sub-linear memory cap when the workload is skewed but not adversarial. Closing it likely needs new lower bounds for conjunctive-band sliding windows and matching adaptive-index data structures.

## 7. Current Research (as of June 2026)
Active threads: event-time **interval-join** state minimization and TTL tuning in Flink/Spark; learned/​adaptive indexes for range-predicate probing inside streaming operators *(frontier — verify)*; sketch-based approximate theta joins extending ECM-sketches to disorder. Groups at EPFL (data-systems lab, descendants of the theta-join-matrix work), TU Berlin / DIMA, and the Flink/Databricks engineering communities are most active.

## 8. Future Work
- Provable joint (state, latency) trade-off curves for conjunctive band predicates.
- Approximate band joins with per-output relative-error guarantees and mergeable state.
- Skew-adaptive eviction with completeness guarantees below the linear-state bound.
- Cost models exposing band selectivity to multi-way and multi-query optimizers.

## 9. Key References
- **[Foundational]** N. Polyzotis et al. / J. Kang, J. Naughton, S. Viglas. *Evaluating Window Joins over Unbounded Streams.* ICDE, 2003. — [DOI](https://doi.org/10.1109/ICDE.2003.1260804)
- **[SOTA]** O. Papapetrou, M. Garofalakis, A. Deligiannakis. *Sketch-based Querying of Distributed Sliding-Window Data Streams (ECM-sketch).* VLDB, 2012. — [DOI](https://doi.org/10.14778/2336664.2336672)
- **[SOTA]** K. Elseidy, A. Elguindy, A. Vitorovic, C. Koch. *Scalable and Adaptive Online Joins (theta-join matrix).* VLDB, 2014. — [DOI](https://doi.org/10.14778/2732279.2732281)
- **[Foundational]** A. Okcan, M. Riedewald. *Processing Theta-Joins using MapReduce.* SIGMOD, 2011. — [DOI](https://doi.org/10.1145/1989323.1989423)
- **[Survey]** L. Golab, M. T. Özsu. *Issues in Data Stream Management.* SIGMOD Record, 2003. — [DOI](https://doi.org/10.1145/776985.776986)

## 10. Worked Example

**A 1-D band join and why state stays linear.** Predicate $|R.a - S.b| \le \varepsilon$ with $\varepsilon = 2$, time window $w$. Live $R$ tuples (key $a$): $\{10, 14, 21\}$. An $S$ tuple with $b=12$ arrives.

Probe: matches are $R$ tuples in $[b-\varepsilon,\,b+\varepsilon]=[10,14]$. With $R$'s keys held in a balanced BST sorted on $a$, a range query returns $\{10,14\}$ in $O(\log n + k)$ time, here $k=2$. Emit $(12,10)$ and $(12,14)$. The tuple $21$ is outside the band, untouched.

**Selectivity blow-up.** Suppose instead all $n$ live $R$ keys cluster inside one $2\varepsilon$-wide band and $n$ matching $S$ tuples arrive. Each $S$ probe matches all $n$, so output size is $\Theta(n^2)$ — the AGM-style worst case. No operator can beat $\Omega(\text{output})$ work, but **resident state** is still just the $O(n)$ live tuples per side; that linear state is what the communication lower bound (Section 5) shows is also *necessary* for exact answers.

Contrast an equi-join: a hash on $a$ would let a probe touch only the matching bucket. The band has no such hash — $12$ can match keys $10,11,\dots,14$, a contiguous range, not one value — which is exactly why band joins resist constant-state and hash-partitioned parallelism.

---
*Part of the [DBMS Research catalog](../../README.md).*
