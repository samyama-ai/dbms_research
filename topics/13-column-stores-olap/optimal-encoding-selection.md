# Optimal Lightweight Encoding Selection

> **Topic:** Column Stores & OLAP · **ID:** `13-column-stores-olap/optimal-encoding-selection` · **Status:** open

## 1. Problem Statement

Given a column (or block) of values and a query workload, choose an **encoding cascade** — a sequence of lightweight compression schemes (run-length, dictionary, bit-packing, frame-of-reference, delta, FOR-delta, null suppression, patched schemes like PFOR) — that minimizes a combined objective of **storage footprint** and **expected decode/scan cost** under the workload.

- **Optimization variant:** Given a column partitioned into blocks $B_1,\dots,B_m$, a library of encodings $\mathcal{E}$ (each composable up to depth $d$), and per-block access frequencies $f_i$, find an assignment $e: \{B_i\} \to \mathcal{E}^{\le d}$ minimizing $\sum_i \big(\alpha\, \mathrm{size}(e(B_i)) + \beta\, f_i\, \mathrm{decode}(e(B_i))\big)$.
- **Decision variant:** Does an assignment exist with combined cost $\le C$?
- **Counting variant:** How many distinct cost-equivalent cascades exist (relevant to search-space pruning)?

The difficulty is that encodings **compose** (a cascade), interact with hardware (SIMD width, cache, vectorized predicate evaluation), and the optimal choice depends on **data distribution per block** and on **which operators** run directly on the encoded form.

## 2. Mathematical Foundations

Model a cascade as a path in a DAG of transformations $T: \mathbb{Z}^n \to \mathbb{Z}^{n'}$. The storage term is governed by the **empirical entropy** of the block: bit-packing approaches $\lceil \log_2(\max - \min + 1)\rceil$ bits/value (frame-of-reference), while dictionary encoding approaches $H_0$ of the value distribution. The information-theoretic floor is the $k$-th order empirical entropy $H_k$.

Formally the per-block choice is a small problem, but the **global** assignment with shared dictionaries and cross-block run continuity makes it combinatorial. If encodings were independent and the objective were monotone + submodular over a matroid of resource constraints, greedy would give a $(1-1/e)$ guarantee; in practice the decode-cost term breaks submodularity because cascaded decoders share unpacking work, creating **supermodular savings**.

$$
\min_{e}\ \sum_{i=1}^{m} \Big(\alpha\,s_i(e_i) + \beta f_i\, c_i(e_i)\Big)\quad\text{s.t. } \sum_i s_i(e_i)\le S,\ \text{shared-dict constraints.}
$$

## 3. State of the Art (SOTA)

- **Systems-SOTA:** C-Store / Vertica's encoding picker, Apache Parquet/ORC heuristics, and Google's **Artus**/Procella column formats use rule-based or sampling-based selection. **BtrBlocks** (Kuschewski et al., SIGMOD 2023) does greedy recursive cascade selection by sampling and estimating compression ratio, achieving strong scan throughput.
- **Learned selection:** **CodecDB** and learned cost models predict the best encoding per column from sampled features. **CorBit / White-box ML** approaches (frontier) treat selection as classification.
- **Theory-SOTA:** No exact polynomial algorithm for the cascaded, workload-aware objective; the per-block, fixed-depth, no-sharing case is solvable optimally by DP over the cascade DAG.

## 4. Upper Bound

For a **single block** with cascade depth bounded by constant $d$ and an encoding library of size $|\mathcal{E}|$, exhaustive DP over the transformation DAG runs in $O(|\mathcal{E}|^d \cdot n)$ — polynomial for constant $d$. BtrBlocks-style greedy sampling runs in $O(n \cdot |\mathcal{E}|)$ per block with no global guarantee. Under independence + matroid resource constraints, greedy yields a $(1-1/e)$-approximation to the combined objective.

## 5. Lower Bound

The general workload-aware variant with **shared dictionaries across blocks** is NP-hard: it embeds a constrained set-cover/facility-location structure (shared dictionary = shared facility), and the budgeted form is hard to approximate beyond the set-cover $\ln n$ barrier under standard assumptions. The shared-run/cross-block continuity constraint additionally makes the assignment non-separable, ruling out per-block independent optimality. No fine-grained conditional lower bound is established for the per-block case (it is in P).

## 6. The Gap

The per-block constant-depth problem is **closed** (poly DP). The **global, shared-state, workload-aware** problem is open: we have NP-hardness on one side and only heuristics/greedy with no matching approximation guarantee on the other. Closing it requires either a constant-factor approximation for the shared-dictionary facility structure or a proof that no such ratio exists under realistic constraints.

## 7. Current Research (as of June 2026)

- Learned, **distribution-aware** selectors that jointly optimize storage and vectorized-scan latency *(frontier — verify)*, building on BtrBlocks and FSST string compression (Boncz, Neumann et al.).
- GPU-decode-aware cascade selection for analytics on accelerators *(frontier — verify)*.
- Integration with **direct-on-compressed** execution so that the decode-cost term reflects operators that never decompress (links to the compressed-operator problem).
- Groups: CWI Database Architecture (Boncz), TUM (Neumann/Kuschewski), CMU (Pavlo) on format auto-tuning.

## 8. Future Work

- A principled cost model unifying entropy bounds with SIMD/cache decode costs.
- Provable approximation for the shared-dictionary global assignment.
- Online/adaptive re-encoding as workloads drift, with bounded re-encoding amortization.
- Co-design of encoding with predicate pushdown and late materialization.

## 9. Key References

- **[SOTA]** Kuschewski, Sauerwein, Alhomssi, Leis. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD, 2023.
- **[Foundational]** Abadi, Madden, Ferreira. *Integrating Compression and Execution in Column-Oriented Database Systems.* SIGMOD, 2006.
- **[Foundational]** Zukowski, Heman, Nes, Boncz. *Super-Scalar RAM-CPU Cache Compression.* ICDE, 2006.
- **[SOTA]** Boncz, Neumann, Leis. *FSST: Fast Static Symbol Table String Compression.* PVLDB, 2020.
- **[Survey]** Abadi, Boncz, Harizopoulos, Idreos, Madden. *The Design and Implementation of Modern Column-Oriented Database Systems.* Foundations and Trends in Databases, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
