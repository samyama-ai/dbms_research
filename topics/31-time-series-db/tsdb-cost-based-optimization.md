# Cost-based optimization for TSDB query plans

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/tsdb-cost-based-optimization` · **Status:** open

## 1. Problem Statement
A time-series engine has decisions a classical optimizer never faces: which **compression codec** a chunk uses (delta-of-delta, XOR/Gorilla, RLE, dictionary), which **rollup/downsample** level (raw, 1m, 1h pre-aggregates) to answer from, which **index** (inverted label index, time-partition skip index, min/max zonemaps) to probe, and which **storage tier** (memory, SSD, object store) holds each chunk. A query's true cost depends on the *interaction* of these: a coarse rollup avoids decompression but may be on a slower tier; a codec that compresses well costs more CPU to scan.

Goal: a **cost model** $\mathrm{cost}(P)$ over plans $P$ and an optimizer that jointly chooses scan source (raw vs. rollup), codec-aware scan cost, index access path, and tier-aware I/O, minimizing latency (or $/query) subject to result-correctness and freshness.

Variants: **decision** — does a plan with cost $\le C$ and staleness $\le \delta$ exist? **optimization** — minimize expected cost over the workload; **physical-design counting** — choose which rollups/indexes to *materialize* (links to `workload-adaptive-layout`).

## 2. Mathematical Foundations
Plan enumeration over rollup-level $\times$ codec $\times$ access-path $\times$ tier is a product space; classical **Selinger** dynamic-programming join ordering (SIGMOD 1979) extends but the cost terms are new. Scan cost is *codec-dependent*: $\mathrm{cost_{scan}} = \beta_{\text{io}}\cdot \mathrm{bytes}(codec) + \beta_{\text{cpu}}\cdot \mathrm{decode}(codec, n)$, where $\mathrm{bytes}(codec)\ge n\cdot H(X)$ (empirical entropy lower bound) and decode cost trades against bytes.

**Rollup selection** is the *view-selection / answering-queries-using-views* problem: given materialized aggregate views $V$ (rollups), pick the cheapest rewriting — NP-hard in general (Harinarayan–Rajaraman–Ullman, *Implementing Data Cubes Efficiently*, SIGMOD 1996), with a greedy $(1-1/e)$ benefit guarantee under the submodular cube-lattice benefit function. **Tier placement** is constrained knapsack/caching. **Cardinality estimation** for time-range $\times$ label predicates drives the model; errors propagate multiplicatively as in classical optimizers (Leis et al., *How Good Are Query Optimizers, Really?*, VLDB 2015), but here label-set cardinality is extreme (high-cardinality tags) and time-correlated, breaking independence assumptions.

## 3. State of the Art (SOTA)
**Systems-SOTA.** Most TSDBs use **rule-based**, not cost-based, plan selection: Prometheus/Mimir push down by label index then scan; InfluxDB IOx uses **DataFusion**'s cost-ish optimizer but rollup choice is manual (continuous queries). TimescaleDB rides PostgreSQL's cost-based optimizer and adds **continuous aggregates** with a *real-time* rewrite that unions a materialized rollup with fresh raw data — a genuine cost-relevant rewrite, but the rollup *choice* is declared, not optimized. Druid/Pinot pick segments and pre-aggregations by rule. ClickHouse has a partial cost-based optimizer and projection (rollup) auto-selection.

**Theory-SOTA.** AQUV / view-selection theory, learned cardinality estimation (**MSCN**, Kipf et al., CIDR 2019; **Naru/NeuroCard**, Yang et al., VLDB 2019–2020), and learned cost models (Marcus et al., **Neo**, VLDB 2019; **Bao**, SIGMOD 2021) are the closest, but none model codec/rollup/tier jointly for telemetry.

## 4. Upper Bound
For a *fixed* plan space, Selinger-style DP optimizes in time exponential in join count but polynomial in the (small) per-scan codec/tier/rollup choices, so single-table telemetry scans optimize in $O(|codecs|\cdot|tiers|\cdot|rollups|)$ — effectively constant per chunk. Rollup *materialization* under storage budget: greedy $(1-1/e)$-approximate (submodular). Tier assignment: $O(\log k)$-competitive online (weighted caching). These are the best general guarantees; an *exact* joint optimum is only tractable because telemetry plans are scan-dominated rather than join-dominated.

## 5. Lower Bound
Choosing the optimal set of rollups/views to materialize is **NP-hard** (view selection / data-cube selection, Harinarayan et al. 1996) and inapproximable below the submodular $(1-1/e)$ barrier for monotone-submodular-max (Feige, JACM 1998) unless P=NP. Cardinality estimation that the cost model needs has no worst-case sub-multiplicative-error guarantee: distinguishing selectivities can require reading the data (information-theoretic), and learned estimators have no worst-case bound. Thus the *physical-design* layer is provably hard and the *estimation* layer is provably unbounded in the worst case — a two-sided obstruction.

## 6. The Gap
**Genuinely open.** There is no published cost model that unifies codec-aware scan cost, rollup rewrite choice, index path, and tier I/O in one optimizer for TSDBs; systems make these decisions in disconnected rule-based layers. The gap between the tractable per-chunk plan choice (Section 4) and the NP-hard global physical design (Section 5) is real and unbridged: nobody has shown a principled approximation for the *joint* online problem (query-plan optimization co-designed with rollup/tier physical design) with end-to-end guarantees. Closing it needs (i) a validated telemetry cost model, (ii) high-cardinality, time-correlated cardinality estimation, and (iii) an optimizer coupling plan choice to adaptive physical design.

## 7. Current Research (as of June 2026)
Directions: DataFusion-based cost-based optimization maturing inside InfluxDB IOx and other Arrow engines *(frontier — verify)*; learned cardinality estimation for high-cardinality label spaces; auto-rollup / projection selection (ClickHouse, Mimir) driven by observed query mix *(frontier — verify)*; tier-aware (object-store) cost modeling for "data lakehouse for metrics" designs. Groups: CMU DB (learned optimizers, Pavlo/Marcus lineage), MIT (Madden/Kraska, learned components), TSDB vendors (InfluxData, Grafana Labs, ClickHouse, Timescale).

## 8. Future Work
- A published, benchmarked TSDB cost model spanning codec, rollup, index, and tier.
- Cardinality estimation robust to high-cardinality, time-correlated tags.
- Joint online optimization of plan choice and physical design with approximation guarantees.
- Cost models that price object-store latency/$ and decompression CPU together.

## 9. Key References
- **[Foundational]** Selinger, Astrahan, Chamberlin, Lorie, Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DBLP](https://dblp.uni-trier.de/rec/conf/sigmod/SelingerACLP79.html)
- **[Foundational]** Harinarayan, Rajaraman, Ullman. *Implementing Data Cubes Efficiently.* SIGMOD, 1996. — [DOI](https://doi.org/10.1145/235968.233333)
- **[SOTA]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really?* VLDB, 2015. — [DOI](https://doi.org/10.14778/2850583.2850594)
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[SOTA]** Kipf, Kipf, Radke, Leis, Boncz, Kemper. *Learned Cardinalities (MSCN).* CIDR, 2019. — [arXiv](https://arxiv.org/abs/1809.00677)
- **[Survey]** Jensen, Pedersen, Thomsen. *Time Series Management Systems: A Survey.* IEEE TKDE, 2017. — [DOI](https://doi.org/10.1109/TKDE.2017.2740932)

## 10. Worked Example

A query asks for the **hourly average** of a metric over the last 24h. The optimizer weighs three plan sources, costing $\mathrm{cost}=\beta_{io}\cdot\text{bytes}+\beta_{cpu}\cdot\text{decode}$ with $\beta_{io}=1,\ \beta_{cpu}=2$ (per million ops):

| Plan | Source | Bytes (MB) | Decode (M ops) | Tier factor | Cost |
|---|---|---|---|---|---|
| A | Raw, Gorilla XOR, on SSD | 50 | 30 | 1.0 | $50+2\cdot30=110$ |
| B | 1m rollup, dictionary, SSD | 4 | 2 | 1.0 | $4+2\cdot2=8$ |
| C | 1m rollup, on object store | 4 | 2 | tier $\times4$ I/O | $4\cdot4+2\cdot2=20$ |

Plan B wins (cost 8): the pre-aggregated 1-minute rollup is exact for an hourly average (1m cleanly rolls up to 1h) and avoids decompressing raw XOR. Plan C is the same rollup but on a slower tier, so the $4\times$ I/O penalty makes it cost $20$.

**Why this is hard:** suppose the query needed a **freshness** $\le 30s$ but the 1m rollup lags 90s. Then B/C become invalid and the optimizer must fall back to raw (A, cost 110) or union a materialized rollup with fresh raw data (TimescaleDB's real-time aggregate). The *rollup-materialization* choice upstream — which levels to keep under a storage budget — is the NP-hard view-selection problem (greedy $(1-1/e)$), coupling per-query planning to physical design.

---
*Part of the [DBMS Research catalog](../../README.md).*
