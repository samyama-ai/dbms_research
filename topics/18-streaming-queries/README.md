# Streaming & Continuous Queries

Streaming and continuous query processing studies how to evaluate long-running queries over unbounded, time-evolving, often out-of-order data streams under tight memory, latency, and ordering constraints. Core tensions run between completeness and timeliness (watermarks, punctuation), accuracy and resource bounds (load shedding, sketches), and correctness under failure (exactly-once, deterministic replay). The field sits at the intersection of streaming-algorithm theory (space lower bounds, sliding-window models) and hard distributed-systems engineering (state management, elastic rescaling, backpressure).

| Problem | Status | Scope |
|---|---|---|
| [Optimal sliding-window aggregation under arbitrary aggregates](./sliding-window-aggregation-optimal.md) | partially-solved | Amortized-optimal in-order maintenance of non-invertible/non-commutative aggregates over sliding windows. |
| [A semantics-complete algebra for windowing](./windowing-semantics-algebra.md) | open | A compositional algebra capturing tumbling, sliding, session, and custom windows with sound rewrite rules. |
| [Watermark generation with provable lateness bounds](./watermark-lateness-bounds.md) | open | Deriving watermarks that bound result lateness and incompleteness under unknown source skew. |
| [Punctuation inference from data streams](./punctuation-inference.md) | partially-solved | Automatically inferring correct punctuations/watermarks without explicit source cooperation. |
| [The latency-completeness-cost trade-off frontier](./latency-completeness-tradeoff.md) | empirically-open | Characterizing the Pareto frontier among result latency, completeness, and resource cost for windowed queries. |
| [Optimal load shedding under quality objectives](./load-shedding-optimal.md) | partially-solved | Choosing what/when/how much to drop to maximize a query-quality objective under overload. |
| [Semantic load shedding with answer guarantees](./semantic-load-shedding-guarantees.md) | open | Load shedding that preserves bounded-error guarantees on aggregate or join answers. |
| [Out-of-order stream processing without buffering blowup](./out-of-order-processing.md) | partially-solved | Producing correct results for disordered streams with provably bounded reordering state. |
| [Exactly-once semantics at minimal coordination cost](./exactly-once-minimal-coordination.md) | partially-solved | Achieving exactly-once output with the least snapshot/commit overhead across operators and sinks. |
| [Consistent distributed snapshots for stateful operators](./distributed-snapshots-streaming.md) | partially-solved | Low-overhead, non-blocking consistent snapshots of large evolving operator state. |
| [Sliding-window distinct counting space bounds](./sliding-window-distinct-count.md) | partially-solved | Tight space lower/upper bounds for approximate distinct counting over sliding windows. |
| [Streaming sketches under deletions and expiry](./streaming-sketches-deletions.md) | open | Mergeable, bounded-error sketches that support both arbitrary deletions and window expiry. |
| [Streaming theta/band joins with bounded state](./streaming-band-joins-bounded-state.md) | open | Evaluating non-equi (theta/band) stream joins with provable state and latency bounds. |
| [Adaptive symmetric-hash join memory management](./adaptive-hash-join-memory.md) | partially-solved | Online state eviction/spill policies for symmetric-hash stream joins under memory pressure. |
| [Multi-way stream join ordering at runtime](./multiway-stream-join-ordering.md) | empirically-open | Continuously re-optimizing the order/shape of multi-way stream joins as rates and selectivities drift. |
| [Elastic operator rescaling with state migration](./elastic-rescaling-state-migration.md) | empirically-open | Repartitioning and migrating large operator state during rescaling without correctness or latency violations. |
| [Backpressure that preserves end-to-end SLOs](./backpressure-slo-preserving.md) | open | Flow-control mechanisms that maintain latency/throughput SLOs across heterogeneous operator graphs. |
| [Continuous query containment and equivalence](./continuous-query-equivalence.md) | open | Deciding equivalence/containment of continuous (windowed, recursive) queries for caching and rewriting. |
| [Multi-query optimization for continuous queries](./continuous-multiquery-optimization.md) | partially-solved | Sharing windows, state, and operators across many concurrent continuous queries optimally. |
| [Expressiveness of streaming query languages](./streaming-language-expressiveness.md) | open | Characterizing what a bounded-memory streaming language can compute versus relational/temporal logics. |
| [Lower bounds for window-join state](./window-join-state-lower-bounds.md) | partially-solved | Communication/space lower bounds for exact and approximate windowed equi-joins. |
| [Provenance and explanations for streaming results](./streaming-provenance.md) | open | Tracking why/how provenance for windowed, approximated, and shed streaming results with bounded overhead. |
| [Disorder-resilient event-pattern (CEP) matching](./cep-disorder-resilient.md) | partially-solved | Complex-event-pattern matching that is correct and bounded under out-of-order and late events. |
| [Retraction and incremental view maintenance over streams](./streaming-retraction-ivm.md) | partially-solved | Correct, efficient negative-tuple/retraction propagation for streaming materialized views. |
| [Deterministic replay for nondeterministic operators](./deterministic-replay.md) | partially-solved | Reproducible recovery when operators depend on processing time, randomness, or external calls. |
| [Quantile and heavy-hitter tracking over windows](./windowed-quantiles-heavy-hitters.md) | partially-solved | Continuous, mergeable quantile/frequent-item tracking with tight window-aware error bounds. |
| [Cost-based watermark/window placement in plans](./watermark-window-placement.md) | open | Optimizing where watermark, window, and aggregation operators sit in distributed dataflow plans. |
| [Streaming cardinality and rate estimation for optimization](./streaming-cardinality-estimation.md) | empirically-open | Online estimation of selectivities, rates, and skew to drive continuous-query re-optimization. |
| [Approximate sliding-window correlation/similarity joins](./windowed-similarity-joins.md) | open | High-dimensional similarity/correlation joins over sliding windows with sublinear-state guarantees. |
| [End-to-end exactly-once with external side effects](./exactly-once-side-effects.md) | open | Guaranteeing exactly-once semantics when operators perform non-idempotent external writes/calls. |

---
*Back to [Taxonomy](../../TAXONOMY.md).*
