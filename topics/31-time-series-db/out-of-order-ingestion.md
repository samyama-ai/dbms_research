---
id: 31-time-series-db/out-of-order-ingestion
title: "Out-of-order and late-arrival ingestion"
topic: 31-time-series-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Out-of-order and late-arrival ingestion

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/out-of-order-ingestion` · **Status:** partially-solved

## 1. Problem Statement
TSDB storage is **time-partitioned and append-optimized**: data is laid out by (series, ascending time) into immutable blocks/chunks so that range scans are sequential and compression (delta-of-delta, XOR) is maximal. **Out-of-order (OOO)** points — a sample whose timestamp precedes the latest already-ingested timestamp for its series — break this invariant. Causes: clock skew, multi-source merges, retries, network delay, and deliberate **backfill** of historical data.

The problem: **absorb OOO and late-arriving points into time-ordered, append-optimized storage efficiently**, without (a) rejecting valid data, (b) forcing rewrites of immutable blocks, (c) degrading compression, or (d) corrupting already-emitted rollups/continuous aggregates.

- **Decision variant:** given a lateness bound $\tau$, can all points within $\tau$ be absorbed without block rewrite?
- **Optimization variants:** minimize write amplification (bytes rewritten per late point) subject to a query-correctness/freshness SLO; minimize the staleness of rollups that must be repaired after backfill.
- **Streaming-semantics variant:** define correct **watermarks** and emit/retract semantics so query results converge as late data lands.

**Partially-solved:** modern TSDBs ship OOO support (separate OOO heads, tolerance windows), but unbounded backfill, rollup repair, and the OOO-vs-compression/amplification trade-off remain open.

## 2. Mathematical Foundations
Model the stream per series as timestamped values $(t_i, v_i)$. **Out-of-orderness** can be quantified by $K = \max_i (\text{position in arrival order} - \text{position in time order})$ (the *disorder* / $K$-sortedness parameter from sorting-with-bounded-disorder theory), or by a **lateness bound** $\tau$: a point with event-time $t$ arriving at processing-time $p$ has lateness $p-t$. Append-optimized layout assumes $K=0$; cost grows with $K$.

**Watermarks** (Dataflow model, Akidau et al.) formalize completeness: a watermark $W(p)$ asserts no event with $t<W(p)$ will arrive after processing time $p$. Late data ($t<W(p)$) triggers either **drop**, **allowed-lateness buffering**, or **retraction/recomputation** of windows already emitted — a trade-off between latency and correctness. Out-of-order absorption maps to **external-memory near-sorting**: merging a bounded-disorder stream costs $O(N\log_B K)$-style I/O rather than full re-sort, which is the lever TSDBs exploit by keeping a small in-memory OOO buffer of width $\tau$ and merging only overlapping blocks.

Compression matters because delta-of-delta and **Gorilla** XOR encoding assume monotone time; an OOO insert into a sealed chunk either forces decode-merge-recode (write amplification) or storage in a parallel, less-compressed OOO chunk later reconciled at compaction.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **Prometheus** added native OOO ingestion (2.39+, an explicit `out_of_order_time_window`) keeping a separate **OOO head** and merging at compaction. **InfluxDB**'s TSM tolerates OOO within the active shard. **TimescaleDB** writes late points into existing chunks (Postgres rows, so OOO is cheap) but late data invalidates **continuous aggregates**, repaired via an invalidation log. **Grafana Mimir** and **Cortex** added per-tenant OOO windows. **Apache Flink / Beam / Kafka Streams** implement the Dataflow watermark/allowed-lateness/retraction model for the streaming-aggregation side.
- **Theory-SOTA:** the **Dataflow model** (Akidau et al., VLDB 2015) is the canonical formal treatment of event-time, watermarks, and late-data triggers.

## 4. Upper Bound
With a bounded lateness window $\tau$, OOO points are buffered in an in-memory OOO head and flushed/merged at compaction: amortized write amplification $O(1)$ per point and merge cost $O(\log B)$-style for the overlapping blocks only — i.e. you pay disorder, not full re-sort. Continuous-aggregate repair is bounded by an **invalidation log**: only the affected buckets are recomputed, $O(\\#\text{dirty buckets})$. Streaming side: allowed-lateness $\tau$ gives bounded state $O(\tau\cdot \text{key-rate})$ with correct retraction emission.

## 5. Lower Bound
**Unbounded** out-of-orderness has no append-optimal solution: absorbing arbitrarily-late data into immutable, time-sorted, maximally-compressed blocks forces block rewrite, so worst-case write amplification is $\Omega(\text{block size})$ per late point — an inherent cost of the layout. From streaming theory, **FLP-style / watermark impossibility**: with no bound on lateness you cannot decide *completeness* of a window (you can never know no later point will arrive), so exact one-shot windowed aggregates are impossible without either a lateness bound or unbounded retraction state. Near-sorting a $K$-disordered stream has an $\Omega(N\log K)$ comparison lower bound, the floor on reorder work.

## 6. The Gap
For **bounded** lateness ($\tau$ fixed) the gap is largely **closed**: OOO heads + compaction merge + invalidation-driven rollup repair give amortized-$O(1)$ ingestion and incremental repair — this is why the status is partially-solved. The **open** gaps: (1) **unbounded backfill** (loading months of history into a system tuned for live data) still triggers heavy rewrite/recompaction and rollup recomputation, with no policy provably minimizing amplification; (2) **rollup/continuous-aggregate correctness** under late data for non-linear aggregates (a late point silently invalidates a previously emitted p99 — see nonlinear-rollup problem) lacks clean incremental-repair theory; (3) a principled choice point between drop / buffer / retract under an SLO is still heuristic.

## 7. Current Research (as of June 2026)
Active: maturing Prometheus/Mimir OOO support toward larger/elastic windows and efficient backfill paths; **incremental view maintenance** for continuous aggregates under late data (invalidation-log optimization, partial-aggregate repair); unifying the **streaming watermark/retraction model with persistent TSDB storage** so one system gives both low-latency and eventually-correct late-data results *(frontier — verify)*. Research on disorder-aware compaction (co-designed with the LSM-tuning problem) and on bulk-backfill ingestion paths is ongoing. Groups: Grafana Labs (Mimir OOO), Timescale (continuous-aggregate invalidation), the Apache Beam/Flink/Dataflow community (Akidau and successors), InfluxData.

## 8. Future Work
- Provably amplification-optimal **bulk backfill** ingestion for time-partitioned stores.
- Incremental, correct repair of **non-linear rollups** under late arrivals.
- A unified persistent + streaming model with watermarks, retractions, and durable correctness.
- Disorder-aware compaction policies parameterized by a measured lateness distribution.
- SLO-driven automatic drop/buffer/retract decisions.

## 9. Key References
- **[Foundational]** Akidau, Bradshaw, Chambers, Chernyak, Fernández-Moctezuma, Lax, McVeety, Mills, Perry, Schmidt, Whittle. *The Dataflow Model: A Practical Approach to Balancing Correctness, Latency, and Cost in Massive-Scale, Unbounded, Out-of-Order Data Processing.* VLDB, 2015. — [DOI](https://doi.org/10.14778/2824032.2824076)
- **[Foundational]** Pelkonen, Franklin, Teller, Cavallaro, Huang, Meza, Veeraraghavan. *Gorilla: A Fast, Scalable, In-Memory Time Series Database.* VLDB, 2015 (XOR compression assuming order). — [DOI](https://doi.org/10.14778/2824032.2824078), [DBLP](https://dblp.org/rec/journals/pvldb/PelkonenFCHMTV15.html)
- **[SOTA]** Prometheus Team. *Out-of-Order Sample Ingestion (TSDB OOO Head).* Prometheus 2.39 release / design docs, 2022. — [GitHub PR #11075](https://github.com/prometheus/prometheus/pull/11075)
- **[SOTA]** Carbone, Katsifodimos, Ewen, Markl, Haridi, Tzoumas. *Apache Flink: Stream and Batch Processing in a Single Engine.* IEEE Data Engineering Bulletin, 2015 (watermarks, event-time). — [PDF](https://asterios.katsifodimos.com/assets/publications/flink-deb.pdf), [DBLP](https://dblp.org/rec/journals/debu/CarboneKEMHT15.html)
- **[Survey]** Jensen, Pedersen, Thomsen. *Time Series Management Systems: A Survey.* IEEE TKDE, 2017. — [DOI](https://doi.org/10.1109/TKDE.2017.2740932), [arXiv](https://arxiv.org/abs/1710.01077)

## 10. Worked Example

A series ingests samples in arrival order with event-times:

$$t = 100,\ 110,\ 120,\ \mathbf{105},\ 130.$$

The 4th arrival ($t=105$) is **out-of-order**: it precedes the latest stored timestamp $120$. Quantify disorder by the displacement $K = \max_i(\text{arrival rank} - \text{time rank})$. Here $105$ arrives 4th but belongs 2nd in time order, so $K = 4-2 = 2$.

**Without OOO support:** the active chunk $[100,110,120]$ was Gorilla-XOR encoded assuming monotone time. Inserting $105$ forces decode-merge-recode of the sealed chunk — write amplification $\Omega(\text{block size})$.

**With a tolerance window $\tau$:** set $\tau = 30$. Since lateness $= 120-105 = 15 \le \tau$, the point is accepted into a small in-memory OOO head rather than rejected, and merged with the overlapping block only at the next compaction — amortized $O(1)$ per late point.

**Rollup repair:** suppose a 1-minute `avg` rollup already emitted the bucket $[100,120)$ as $(100+110)/2 = 105$ over 2 points. The late $105$ lands in that same bucket, so the invalidation log marks exactly **one** dirty bucket; recomputing it gives $(100+110+105)/3 = 105$ over 3 points. Repair cost is $O(\\#\text{dirty buckets}) = O(1)$, not a full re-aggregation.

If instead $t=105$ arrived after the window had advanced past $\tau$, completeness is undecidable without unbounded retraction state — the watermark/FLP-style barrier.

---
*Part of the [DBMS Research catalog](../../README.md).*
