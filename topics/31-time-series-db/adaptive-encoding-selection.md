---
id: 31-time-series-db/adaptive-encoding-selection
title: "Adaptive encoding selection per block"
topic: 31-time-series-db
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Adaptive encoding selection per block

> **Topic:** Time-Series Databases · **ID:** `31-time-series-db/adaptive-encoding-selection` · **Status:** partially-solved

## 1. Problem Statement

A column/stream is partitioned into blocks $B_1, B_2, \dots$. For each block we must choose one codec from a finite palette $\mathcal{C}$ (e.g. delta, delta-of-delta, XOR/Gorilla, dictionary, RLE, bit-packing, FOR, double-delta-zigzag), to **minimize total cost** (encoded bits, or bits subject to a decode-throughput constraint).

Variants:
- **Online:** choose $c_j$ for $B_j$ before seeing later blocks; commitment is irrevocable. Goal: **competitive ratio** vs. the offline best-per-block choice.
- **Offline / per-block optimal:** with all data available, pick $\arg\min_{c}\text{cost}(c, B_j)$ independently — trivial if blocks are independent, but cross-block state (dictionaries, FOR reference) breaks independence.
- **Counting/structure:** how block size interacts with codec choice (the segmentation-and-selection joint problem).

## 2. Mathematical Foundations

Let $\text{cost}(c, B)$ be the encoded size of block $B$ under codec $c$. If blocks are independent, the offline optimum is $\sum_j \min_c \text{cost}(c,B_j)$, achievable by trial encoding (the "exhaustive" or "sampled" approach in real systems).

Online selection without cross-block dependence is a **metrical task / experts** problem: treat each codec as an expert; regret bounds from **Multiplicative Weights / Hedge** give $\sum_j \text{cost}(c_j,B_j) \le (1+\eta)\min_c \sum_j \text{cost}(c,B_j) + O(\tfrac{\log|\mathcal{C}|}{\eta})$ when competing against the best *single fixed* codec. Competing against the best *per-block* choice (a shifting/tracking expert) costs an extra factor depending on the number of switches — captured by **Fixed-Share / tracking-experts** regret $O(m\log(|\mathcal{C}|T))$ for $m$ switches.

When codecs share state (dictionary reuse across blocks, FOR reference frames), the problem becomes a **shortest-path / DP over a layered graph** whose edges carry state-transition cost — solvable offline in $O(T\,|\mathcal{C}|^2)$, but the online version inherits metrical-task-system lower bounds (competitive ratio $\Omega(|\mathcal{C}|)$ in the worst case for deterministic algorithms, $\Omega(\log|\mathcal{C}|)$ randomized).

## 3. State of the Art (SOTA)

- **Systems-SOTA:** **Apache Parquet / ORC** encoding selection; **Apache IoTDB** and **Apache TsFile** per-chunk encoder choice; **ClickHouse** codec pipelines (`Delta`, `DoubleDelta`, `Gorilla`, `T64`, `LZ4`); **BtrBlocks** (Kuschewski et al., SIGMOD 2023) — recursive, sampling-based per-block scheme selection for columnar storage; **FastLanes** (Afroozeh & Boncz, VLDB 2023) unified encoding layout. Selection is typically **sample-then-trial** heuristics, not regret-bounded.
- **Theory-SOTA:** the experts/MTS framework gives the provable side, but is rarely wired into systems with explicit guarantees — hence "partially-solved."

## 4. Upper Bound

- **Offline, independent blocks:** optimal in $O(T\,|\mathcal{C}|)$ by exhaustive per-block encode; sampling reduces the constant (BtrBlocks).
- **Online, fixed-comparator:** Multiplicative Weights gives $(1+\eta)$-competitive plus $O(\log|\mathcal{C}|/\eta)$ additive vs. the best single codec.
- **Online, per-block comparator with $m$ switches:** Fixed-Share regret $O(m\log(|\mathcal{C}|T))$. With cross-block state, layered-DP is offline-optimal; online competitiveness degrades to the MTS bound.

## 5. Lower Bound

- Selecting among stateful codecs online is a **metrical task system**: deterministic competitive ratio is $\Omega(|\mathcal{C}|)$ (lower bound for MTS on $|\mathcal{C}|$ states), randomized $\Omega(\log|\mathcal{C}|/\log\log|\mathcal{C}|)$.
- For the **joint segmentation + selection** problem (choosing block boundaries *and* codecs to minimize bits), offline optimality is polynomial via DP, but no codec system implements it; approximation hardness of jointly optimal boundaries under realistic codec-cost oracles is not characterized.
- Information-theoretically, no selection beats the per-block entropy floor.

## 6. The Gap

For **independent blocks** the gap is essentially closed offline (trial encoding) and online (experts regret). The genuinely open part is (1) **provable competitive guarantees under cross-block shared state** matching the MTS lower bounds in real codec palettes, and (2) the **joint block-sizing + codec-selection** optimization, where systems use heuristics far from the DP optimum. No deployed system advertises a competitive ratio.

## 7. Current Research (as of June 2026)

- Learned codec selectors and cost models replacing exhaustive trial encoding *(frontier — verify)*.
- BtrBlocks/FastLanes-line work on cascaded/recursive schemes and SIMD-decodable layouts (CWI Boncz group; TUM Neumann/Kuschewski).
- Workload-aware selection trading compression ratio against decode/query throughput.
- Integration of selection with compressed-domain execution (see companion problem).

## 8. Future Work

- Regret/competitive analysis tied to actual columnar codec palettes with state.
- Joint segmentation + selection with approximation guarantees.
- Multi-objective (ratio vs. random-access vs. SIMD throughput) Pareto selection with bounds.

## 9. Key References

- **[SOTA]** M. Kuschewski, D. Sauerwein, A. Alhomssi, V. Leis. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3589263)
- **[SOTA]** A. Afroozeh, P. Boncz. *The FastLanes Compression Layout.* VLDB, 2023. — [DOI](https://doi.org/10.14778/3598581.3598587)
- **[Foundational]** N. Cesa-Bianchi, G. Lugosi. *Prediction, Learning, and Games.* Cambridge University Press, 2006. — [ACM](https://dl.acm.org/doi/book/10.5555/1137817)
- **[Foundational]** A. Borodin, R. El-Yaniv. *Online Computation and Competitive Analysis.* Cambridge University Press, 1998. — [ACM](https://dl.acm.org/doi/book/10.5555/290169)
- **[Foundational]** M. Herbster, M. Warmuth. *Tracking the Best Expert.* Machine Learning, 1998. — [DOI](https://doi.org/10.1023/A:1007424614876)

## 10. Worked Example

Palette $\mathcal{C}=\{\text{Delta},\text{RLE}\}$, four blocks of 100 integers each. Trial-encode sizes (bytes):

| Block | Delta | RLE | per-block best |
|-------|------|-----|----------------|
| $B_1$ (smooth ramp) | 40 | 180 | Delta (40) |
| $B_2$ (constant 7) | 120 | 6 | RLE (6) |
| $B_3$ (constant 7) | 120 | 6 | RLE (6) |
| $B_4$ (noisy ramp) | 55 | 200 | Delta (55) |

Offline per-block optimum $=40+6+6+55=107$ bytes, computed in $O(T\,|\mathcal{C}|)=O(4\cdot2)=8$ encode trials.

Online with Multiplicative Weights ($\eta$ tuned) competing against the best *single fixed* codec: best fixed codec is Delta with $40+120+120+55=335$, so MW pays $\approx(1+\eta)\cdot335$ — far worse than 107 because no single codec fits all blocks. To approach 107 you need the *per-block* comparator: Fixed-Share tracks the $B_2\!\to\!B_3$ run as RLE and the ramps as Delta. Here there are $m=2$ codec switches ($B_1\!\to\!B_2$, $B_3\!\to\!B_4$), so the tracking regret is $O(m\log(|\mathcal{C}|T))=O(2\log 8)$ additive bytes over the 107 optimum — showing why switching cost, not raw codec count, drives the online gap.

---
*Part of the [DBMS Research catalog](../../README.md).*
