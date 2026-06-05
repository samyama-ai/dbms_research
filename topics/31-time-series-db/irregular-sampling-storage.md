# Irregular and event-driven sampling storage

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/irregular-sampling-storage` · **Status:** partially-solved

## 1. Problem Statement

Much real time-series data is **not** sampled on a fixed grid: event-driven sensors report on change, IoT devices sleep and burst, financial ticks arrive at irregular instants, and different series in the same measurement advance **asynchronously**. The problem: design **storage, compression, and query models** for non-uniformly sampled, per-series-asynchronous data that (a) compress timestamps *and* values well, (b) support efficient time-range and aggregate queries, and (c) give a clean account of cross-series alignment.

Variants:
- **Encoding (optimization):** minimize bits for a sequence of (timestamp, value) pairs with irregular $\Delta t$.
- **Query model (semantic):** how do range/aggregate/join queries behave over per-series-irregular grids without forcing a global resample?
- **Random access (decision/structural):** support seek-to-time-$t$ and range scans on the compressed form with bounded probes.

Marked **partially-solved**: timestamp delta-of-delta coding and columnar layouts work well for *near-regular* data; truly irregular, asynchronous, sparse data is handled ad hoc.

## 2. Mathematical Foundations

A series is a sequence $(t_i, v_i)$ with strictly increasing $t_i$. Two streams to encode: timestamps $t_i$ and values $v_i$. Timestamps under near-regular sampling have small **second differences** $\Delta^2 t_i = (t_{i+1}-t_i)-(t_i-t_{i-1})\approx 0$; Gorilla/Facebook encodes these with variable-length **delta-of-delta** codes, near-optimal when jitter is small. For genuinely irregular $t_i$, the relevant quantity is the entropy of the inter-arrival distribution $P(\Delta t)$; a renewal/Poisson model gives expected code length $\approx H(\Delta t)$ bits per timestamp (Shannon bound).

The **asynchrony** problem is representational: a "table" of $K$ series over a shared time axis is dense only after alignment; natively the data is a union of sparse per-series supports $\bigcup_k \mathrm{dom}(x_k)$. Materializing a dense grid costs $O(K \cdot |\bigcup_k \mathrm{dom}(x_k)|)$ and is mostly NULL — a sparse-matrix storage problem (CSR/CSC analogues). Query correctness over irregular grids ties back to **as-of join** semantics ($\theta$-join on $\le$) and interval/temporal algebra. Random access on compressed runs is governed by **block-decodable** coding: a space–access trade-off (succinct-data-structure regime, $O(1)$ or $O(\log n)$ probes with $o(n)$ redundancy).

## 3. State of the Art (SOTA)

- **Systems-SOTA:** **Gorilla** delta-of-delta timestamps + XOR values (Pelkonen et al., VLDB 2015); **Apache IoTDB / TsFile** (event-driven IoT, aligned vs. **non-aligned** time series as a first-class storage mode); **InfluxDB IOx / Apache Arrow + Parquet** columnar with run-length/dictionary; **kdb+/q** with `aj` as-of joins for native asynchrony; **TimescaleDB** hypertables + native compression (segment-by/order-by).
- **Encoding-SOTA:** delta-of-delta, **simple-8b**, FOR/bit-packing, run-length for sparse/state series; **Sprintz** (Blalock et al., 2018) for low-power integer IoT streams; **TSXor / Chimp / Elf / ALP** for value floats.
- **Theory-SOTA:** succinct/compressed-index theory for random access; renewal-process entropy bounds for inter-arrivals.

## 4. Upper Bound

- **Timestamps:** delta-of-delta achieves $O(1)$ bits/sample on regular data and $\approx H(\Delta t)+O(1)$ under stationary inter-arrivals (entropy-coded). 
- **Values:** XOR/ALP-class bounds (see compression problems) apply per series.
- **Random access:** compressed columnar blocks give $O(\log n)$-probe seek-to-time with $o(n)$ redundancy using sampled offsets; range scan is output-sensitive $O(k)$ after seek.
- **Asynchronous join:** as-of join is $O(n_a + n_b)$ with merge over sorted supports.

## 5. Lower Bound

- **Information-theoretic:** no timestamp code beats $H(\Delta t)$ per sample in expectation; for incompressible jitter, $\Omega(\log(\text{range}))$ bits/timestamp are unavoidable (Shannon).
- **Cell-probe (random access):** for predecessor/seek-to-time on $n$ keys, **Pătraşcu–Thorup** lower bounds give $\Omega(\log\log)$–$\Omega(\log/\log)$ probe trade-offs depending on space — any seek-to-time index inherits these.
- **Sparse alignment:** materializing $K$ asynchronous series into a dense grid is information-theoretically wasteful by a factor up to the sparsity ratio; no encoding avoids paying for the union support.

## 6. The Gap

For **near-regular** data the gap is essentially closed (delta-of-delta + XOR near entropy). It is open for **bursty/heavy-tailed irregular** timestamps (no codec proven near-optimal across inter-arrival regimes) and for **asynchronous multi-series** storage where there is no agreed compressed layout that simultaneously (i) avoids dense materialization, (ii) supports fast range-aggregates, and (iii) gives clean join semantics. Closing it needs a sparse-time-matrix storage format with proven space–query trade-offs.

## 7. Current Research (as of June 2026)

- **IoTDB non-aligned series** and TsFile v3 encodings; columnar formats (Arrow/Parquet, Lance, FastLanes) adding irregular-friendly run/delta encodings *(frontier — verify)*.
- Learned/adaptive timestamp codecs selecting per-block schemes by inter-arrival statistics (CWI FastLanes/ALP line; InfluxData IOx; Timescale).
- Event-driven sketches and approximate range-aggregates over sparse supports.

## 8. Future Work

- Provably near-optimal timestamp codecs across inter-arrival regimes (bursty, heavy-tailed).
- A compressed sparse-multi-series format with random access + range-aggregate + as-of-join guarantees.
- Query languages that make per-series asynchrony first-class without forced resampling.

## 9. Key References

- **[Foundational]** T. Pelkonen et al. *Gorilla: A Fast, Scalable, In-Memory Time Series Database.* VLDB, 2015. — [DOI](https://doi.org/10.14778/2824032.2824078) — [DBLP](https://dblp.org/rec/journals/pvldb/PelkonenFCHMTV15.html)
- **[SOTA]** D. Blalock, S. Madden, J. Guttag. *Sprintz: Time Series Compression for the Internet of Things.* IMWUT/UbiComp, 2018. — [arXiv](https://arxiv.org/abs/1808.02515) — [DBLP](https://dblp.org/rec/journals/imwut/BlalockMG18.html)
- **[SOTA]** C. Wang et al. *Apache IoTDB: A Time Series Database for IoT.* (TsFile / IoTDB), VLDB/SIGMOD, 2020–2023. — [DOI](https://doi.org/10.14778/3415478.3415504) — [DBLP](https://dblp.org/rec/journals/pvldb/WangHSXSKSZK20.html)
- **[Foundational]** M. Pătraşcu, M. Thorup. *Time–Space Trade-Offs for Predecessor Search.* STOC, 2006. — [arXiv](https://arxiv.org/abs/cs/0603043) — [DBLP](https://dblp.org/rec/conf/stoc/PatrascuT06.html)
- **[Foundational]** T. Cover, J. Thomas. *Elements of Information Theory.* Wiley, 2006. — [DOI](https://doi.org/10.1002/047174882X)

## 10. Worked Example

Consider an event-driven sensor reporting at irregular times (seconds): $t = 100, 160, 220, 280, 345$, jitter near a 60 s nominal period. **Delta-of-delta** coding: first store $t_0=100$ and the first delta $\Delta_1 = 60$. Then second differences are $\Delta^2 t_i = \Delta_i - \Delta_{i-1}$:

| $i$ | $t_i$ | $\Delta_i$ | $\Delta^2 t_i$ | bits |
|---|---|---|---|---|
| 1 | 160 | 60 | — | 9 (header delta) |
| 2 | 220 | 60 | 0 | 1 (`0`) |
| 3 | 280 | 60 | 0 | 1 (`0`) |
| 4 | 345 | 65 | +5 | 9 (control + value) |

Three of four deltas are stored in a single bit each (Gorilla uses `0` for $\Delta^2=0$), and only the one jittered point costs a full control word — roughly $9+1+1+9 = 20$ bits for 4 timestamps vs. $4\times 64 = 256$ bits raw, a $\sim 12\times$ saving. Now contrast a **bursty** stream $t = 100, 101, 102, 500, 501$: the second differences are $\{-59, 398, -398\}$ — large and sign-flipping, so delta-of-delta degrades toward $\Omega(\log(\text{range}))$ bits/sample, matching the Shannon floor $H(\Delta t)$ for the heavy-tailed inter-arrival distribution. This is exactly the regime section 6 flags as open.

---
*Part of the [DBMS Research catalog](../../README.md).*
