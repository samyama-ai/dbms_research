# Compressed Page Recompression Scheduling

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/recompression-scheduling` · **Status:** open

## 1. Problem Statement
Database pages can be stored under different compression schemes that trade **decompression cost against footprint**: light encodings (RLE, dictionary, FOR/frame-of-reference, LZ4) decompress fast but compress less; heavy encodings (Zstd-high, delta+bitpacking, PFor, gzip) compress more but cost more CPU to decode (and far more to encode). As a page's access pattern evolves — hot pages read frequently, cold pages rarely — the *optimal* encoding changes. The problem: **schedule re-encoding (recompression) of pages between light and heavy schemes** so that hot pages stay cheap to read while cold pages free buffer/storage capacity, amortizing the (significant) re-encoding cost against future savings.

Variants:
- **Decision:** Given access frequencies and scheme costs, does a recompression schedule keep total cost (read decode + storage + recompress) below budget $B$?
- **Optimization:** Minimize total cost over a horizon / workload.
- **Online:** Decide recompression with no knowledge of future access frequency (the page may heat up again right after you heavily compress it).

## 2. Mathematical Foundations
This is structurally a **ski-rental / metrical-task-system (MTS)** problem. For each page, choosing a heavier scheme is a one-time "buy" cost $C_{\text{recompress}}$ that lowers the per-read "rent" (decode + footprint penalty); if future reads are unknown, deciding when to pay is exactly **rent-or-buy**. The classic deterministic ski-rental is **2-competitive**; randomized achieves $e/(e-1)\approx 1.58$. Across many pages with state (current scheme) and switching costs between schemes, the problem generalizes to a **metrical task system** over the "scheme state" of each page, with movement cost = recompression cost and service cost = per-access decode/footprint cost. General MTS on $N$ states has a tight $\Theta(N)$ deterministic competitive ratio and $\Theta(\log^2 N/\log\log N)$ randomized (Bartal et al.; Bubeck et al.).

The footprint term couples to buffer capacity: heavier compression $\Rightarrow$ more pages fit $\Rightarrow$ higher effective $k$, improving hit rate (a submodular-ish capacity benefit) at the cost of CPU. Formally, let scheme $j$ give compression ratio $\rho_j$ and decode cost $\delta_j$; a page read at rate $\lambda$ has steady-state cost $\lambda\delta_j + \alpha/\rho_j$ (footprint price $\alpha$); recompression switches $j$ at cost $C_{i\to j}$.

## 3. State of the Art (SOTA)
- **Foundational compression:** Abadi, Madden, Ferreira (SIGMOD 2006) — integrating compression and execution; *C-Store* (Stonebraker et al., VLDB 2005) encoding choices; *BtrBlocks* (Kuschewski, Leis et al., SIGMOD 2023) — cascaded/encoding-cascade column compression.
- **Adaptive/tiered:** *Hot/cold data tiering* with differential compression — e.g. SQL Server columnstore (compressed vs compressed-archive), Oracle Hybrid Columnar Compression (HCC) **Heat-Map / Automatic Data Optimization (ADO)** which moves data between compression tiers by access heat. Apache Parquet/ORC per-column codec selection; ClickHouse codec cascades.
- **Learned encoding selection:** *CodecDB*, learned per-column codec selection (Jiang et al.); workload-driven encoding advisors.
- The *scheduling-over-time* dimension (when to flip schemes online) is mostly handled by **heuristic heat thresholds** in production; principled competitive treatment is scarce.

## 4. Upper Bound
The single-page light↔heavy decision is **2-competitive** deterministically (ski-rental) and $1.58$-competitive randomized — these are tight for rent-or-buy. With multiple discrete schemes and switching costs it is an MTS; the work-function algorithm is $(2N-1)$-competitive on $N$ states. Offline (known access trace) the optimal recompression schedule is computable by DP in $O(T\cdot N^2)$ (Viterbi over scheme states per page). Systems-SOTA (Oracle ADO, SQL Server) uses heat thresholds with no competitive guarantee but strong empirical capacity savings; BtrBlocks optimizes the *static* encoding choice, not the temporal schedule.

## 5. Lower Bound
Ski-rental's deterministic lower bound is **2** (no online algorithm beats it); randomized lower bound is $e/(e-1)$. General MTS on $N$ states has a deterministic competitive lower bound of $2N-1$ and a randomized lower bound of $\Omega(\log N/\log\log N)$ — so with many schemes, no online recompression policy can be uniformly close to OPT without future knowledge. Information-theoretically, an adversary can heat a page immediately after it is heavily (expensively) recompressed, forcing wasted encode work; thus worst-case regret is bounded below by the recompression cost itself.

## 6. The Gap
Open. The *single-page* rent-or-buy theory is tight, but the realistic problem — **many pages, multiple schemes, shared buffer capacity, and footprint-coupled hit rates** — has no tight competitive characterization, and the capacity-coupling (heavier compression raises effective $k$) is not modeled in standard MTS. Production systems schedule recompression by hand-tuned heat thresholds with no guarantees, and learned advisors optimize the static choice rather than the online schedule. Closing the gap needs an online model that couples per-page rent-or-buy with the global capacity benefit of compression, plus learning-augmented (heat-prediction) bounds.

## 7. Current Research (as of June 2026)
- **Learning-augmented ski-rental / MTS** using access-heat predictions to beat worst-case 2-competitiveness when predictions are good *(frontier — verify)*.
- Encoding-cascade auto-tuning (BtrBlocks successors) extended to *temporal* re-encoding as workloads drift *(frontier — verify)*.
- Recompression co-scheduled with NVM/GPU tier placement (heavier compression on cold tiers; links to NVM and GPU buffer problems).
- Groups: TUM (Leis — BtrBlocks), MIT (Madden — compression+execution lineage), Oracle/Microsoft storage-engine teams, CMU.

## 8. Future Work
- Competitive bounds for multi-scheme, capacity-coupled online recompression.
- Heat-prediction-augmented schedules with consistency/robustness guarantees.
- Energy- and endurance-aware recompression on NVM/flash (encode cost vs wear).
- Recompression integrated with buffer eviction: evict-by-recompress as a third option beside keep/drop.

## 9. Key References
- **[Foundational]** Stonebraker et al. *C-Store: A Column-Oriented DBMS.* VLDB, 2005. — [ACM](https://dl.acm.org/doi/10.5555/1083592.1083658)
- **[Foundational]** Abadi, Madden, Ferreira. *Integrating Compression and Execution in Column-Oriented Database Systems.* SIGMOD, 2006. — [DOI](https://doi.org/10.1145/1142473.1142548)
- **[SOTA]** Kuschewski, Sauerwein, Alhomssi, Leis. *BtrBlocks: Efficient Columnar Compression for Data Lakes.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3589263)
- **[Foundational]** Karlin, Manasse, McGeoch, Owicki. *Competitive Randomized Algorithms for Nonuniform Problems (Ski-Rental).* Algorithmica, 1994. — [DOI](https://doi.org/10.1007/BF01189993)
- **[Foundational]** Borodin, Linial, Saks. *An Optimal Online Algorithm for Metrical Task Systems.* JACM, 1992. — [DOI](https://doi.org/10.1145/146585.146588)
- **[Survey]** Bubeck, Cohen, Lee, Lee, Madry. *k-server via Multiscale Entropic Regularization / MTS advances.* STOC, 2018. — [arXiv](https://arxiv.org/abs/1711.01085)

## 10. Worked Example

One page, two schemes. **Light** (LZ4): decode cost $\delta_L = 1$ per read, footprint penalty $\alpha/\rho_L = 4$. **Heavy** (Zstd-high): decode $\delta_H = 1$ (decompression is cheap), footprint $\alpha/\rho_H = 1$, but a one-time recompress cost $C = 10$ to switch L$\to$H.

Per-read steady-state cost: light $= \delta_L + \text{footprint} = 1+4 = 5$; heavy $= 1+1 = 2$. Switching saves $3$ per read but costs $10$ up front. **Break-even** read count $n^*$: $10 = 3n^* \Rightarrow n^* \approx 3.3$ reads.

This is exactly ski-rental with buy cost $10$ and rent savings $3$. The deterministic $2$-competitive rule "switch once accumulated rent savings reach the buy cost" recompresses after the page has been read $\lceil 10/3 \rceil = 4$ times. Worst case (section 5): an adversary lets the page go cold right after we pay the $10$ to compress it — we never recoup the encode work, and total cost is $2\times$ the offline optimum (which, knowing the future, would never have switched). Randomized rent-or-buy improves this to $e/(e-1)\approx 1.58$.

---
*Part of the [DBMS Research catalog](../../README.md).*
