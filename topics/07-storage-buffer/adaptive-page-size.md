# Self-Tuning Page Size Selection

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/adaptive-page-size` · **Status:** empirically-open

## 1. Problem Statement

A storage engine must fix (or adapt) the **physical page granularity** $B$ — the unit of allocation, I/O transfer, and buffer-frame sizing. The choice trades off three competing costs under an unknown, possibly drifting workload:

- **Read amplification:** a point lookup of a small record on a large page transfers $B$ bytes to use a few; amplification $\approx B / \text{useful bytes}$.
- **Fill factor / internal fragmentation:** records and B-tree nodes rarely tile $B$ exactly; wasted space grows with $B$ for variable-length data, and small $B$ raises per-page header overhead.
- **Metadata / structural cost:** smaller $B$ means more pages, taller B-trees (more index levels $\approx \log_{B/k} N$), larger page tables, more buffer-frame bookkeeping, and more I/O operations per scan.

**Goal:** choose $B$ (statically, or **online** per table / per region of the key space) to minimize expected total cost over the workload, possibly allowing **multiple coexisting page sizes**.

Variants:
- **Decision:** Is there a single $B$ achieving total cost $\le k$?
- **Optimization:** Find cost-minimizing $B$ (or a partition of data into size classes).
- **Online:** Adapt $B$ as read/write/scan mix drifts, with bounded reorganization cost.

## 2. Mathematical Foundations

Model expected per-access cost as a sum of three terms in $B$. With record size $r$, point-read fraction $\rho_p$, scan fraction $\rho_s$, and $N$ records:

$$
\mathbb{E}[\text{cost}(B)] \;=\; \underbrace{\rho_p\big(\alpha + \beta B\big)}_{\text{read amp (seek}+\text{transfer)}} \;+\; \underbrace{\rho_s \frac{N r}{B}\,(\alpha + \beta B)}_{\text{scan I/O ops}} \;+\; \underbrace{\gamma \log_{B/r} N}_{\text{tree height}} \;+\; \underbrace{\delta\,\frac{N r}{B}}_{\text{per-page metadata}} .
$$

Here $\alpha$ is fixed per-I/O latency, $\beta$ per-byte transfer. The point-read term **increases** in $B$ while scan-op and metadata terms **decrease** in $B$, giving a (typically) **quasi-convex** objective with an interior optimum $B^\star$ governed by the $\alpha/\beta$ ratio (the device's access/transfer break-even point) and the read/scan mix. This is structurally the same trade-off as the **disk-access-model (DAM) / external-memory** block-size choice (Aggarwal–Vitter) and the cache-oblivious **tall-cache** assumption — except here $B$ is a *decision variable*, not a hardware constant. Allowing size classes turns it into a **partitioning / bin-design** problem; online adaptation makes it an **online convex / metrical-task** problem with switching (reorganization) cost.

## 3. State of the Art (SOTA)

**Systems-SOTA.** Most engines fix $B$ at create time: PostgreSQL 8 KB, InnoDB 16 KB (configurable 4–64 KB), SQL Server 8 KB, Oracle multiple block sizes per tablespace. **LeanStore/Umbra** (Leis, Neumann, TUM) use *variable-size pages* with pointer swizzling, effectively letting large objects use larger frames. **Bw-tree / LLAMA** (Levandoski et al., ICDE/VLDB 2013) decouple logical pages from physical deltas, blurring fixed granularity. LSM engines tune **block size** (RocksDB `block_size`, typ. 4–32 KB) and **SSTable** sizing per level; **Monkey/Dostoevsky** (Dayan et al., SIGMOD 2017/2018) co-tune block and Bloom-filter budgets analytically.

**Theory-SOTA.** The static optimum is the classic external-memory block-size analysis; no published policy gives a *competitive guarantee* for online page-size adaptation, so the topic is **empirically-open**.

## 4. Upper Bound

- **Static:** the quasi-convex cost is minimized by 1-D search (ternary search over $B$) in $O(\log B_{\max})$ evaluations — exact optimum for a fixed, known mix in the **DAM model**.
- **Size classes:** for $K$ classes, a DP over sorted record/access profiles gives the optimal class boundaries in $O(N K)$ (the standard $K$-segmentation / multiple-choice partition), or an **FPTAS** for the knapsack-flavored fill-factor variant.
- **Online:** cast as online convex optimization with switching cost, **work-function / OCO-with-switching** yields $O(\sqrt{T})$ regret or constant-competitive ratios *only under convexity assumptions*; these have not been instantiated for real page-size cost models with reorganization.

## 5. Lower Bound

- **Online:** any policy that physically re-pages data pays an $\Omega(\text{reorg cost})$ that an offline optimum (knowing the drift) avoids — a **metrical-task-system** lower bound forces a competitive ratio bounded below by the switching/movement cost, so no online policy is 1-competitive.
- **Information-theoretic:** distinguishing the cost-minimizing $B$ from a near-tie requires observing enough of the access stream; estimating the read/scan mix to additive $\epsilon$ needs $\Omega(1/\epsilon^2)$ samples (Chernoff/streaming).
- No NP-hardness is known for the single-$B$ static problem (it is a 1-D search); the **multi-size-class with packing** variant inherits **knapsack/bin-packing NP-hardness**.

## 6. The Gap

For a *fixed, known* workload the static optimum is computable exactly, so the gap is not in the offline problem. The genuine, **empirically-open** gap is the **online** case: there is no policy with a proven competitive ratio for adapting $B$ under drift with bounded reorganization cost, and no matching lower bound beyond the generic metrical-task switching penalty. Production systems pick $B$ by rule-of-thumb or one-shot calibration; whether an online self-tuner can provably approach the best dynamic page-size schedule is unresolved. Closing it needs (i) a faithful convex/quasi-convex cost model validated on real devices and (ii) a competitive online algorithm with matching impossibility.

## 7. Current Research (as of June 2026)

- **Variable-size and decoupled-page engines:** LeanStore/Umbra and Bw-tree lineage explore per-object granularity; extending this to *workload-driven, key-range-local* page sizing. *(frontier — verify)*
- **Zoned/ZNS SSD and CXL:** device write-unit (zone) and CXL line sizes reshape the $\alpha/\beta$ break-even, reopening optimal $B$ for new hardware. *(frontier — verify)*
- **Auto-tuning / self-driving DBs:** RL and Bayesian-optimization knob tuners (OtterTune, CMU self-driving) include page/block size among tuned parameters, but without guarantees. *(frontier — verify)*

## 8. Future Work

- A competitive online page-size scheduler with bounded reorganization cost.
- Co-optimization of page size with compression scheme, Bloom-filter budget, and buffer admission as one objective (extending the Monkey/Dostoevsky analytic approach).
- Heterogeneous, per-key-range page sizing with provable benefit over any single global $B$.
- Device-model-aware tuning that transfers across HDD/SSD/ZNS/CXL without recalibration.

## 9. Key References

- **[Foundational]** Aggarwal, Vitter. *The Input/Output Complexity of Sorting and Related Problems (External-Memory / DAM model).* CACM, 1988.
- **[Foundational]** Frigo, Leiserson, Prokop, Ramachandran. *Cache-Oblivious Algorithms.* FOCS, 1999.
- **[SOTA]** Leis, Haubenschild, Alhomssi, Neumann. *LeanStore: In-Memory Data Management Beyond Main Memory.* ICDE, 2018.
- **[SOTA]** Levandoski, Lomet, Sengupta. *The Bw-Tree: A B-tree for New Hardware Platforms.* ICDE, 2013.
- **[SOTA]** Dayan, Athanassoulis, Idreos. *Monkey: Optimal Navigable Key-Value Store.* SIGMOD, 2017.
- **[Survey]** Graefe. *Modern B-Tree Techniques.* Foundations and Trends in Databases, 2011.

---
*Part of the [DBMS Research catalog](../../README.md).*
