# Heterogeneous-memory data placement (HBM/DRAM/NVM)

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/tiered-memory-placement` · **Status:** empirically-open

## 1. Problem Statement
Modern servers expose a memory hierarchy of distinct tiers — on-package **HBM** (very high bandwidth, small capacity), **DRAM** (large, moderate), and **persistent / far memory** (NVM, CXL-attached memory; large, durable, slower) — each with its own capacity $C_t$, bandwidth $B_t$, latency $L_t$, and \$/GB. Given a workload's access pattern over data objects (pages, columns, partitions, index nodes), decide **which tier holds each object** to optimize a cost-per-access objective.

- **Optimization variant (primary):** choose a placement $\pi: \text{objects} \to \text{tiers}$ minimizing total expected access cost $\sum_o \text{freq}(o)\cdot \text{cost}(\pi(o))$ subject to per-tier capacity constraints $\sum_{o:\pi(o)=t} \text{size}(o) \le C_t$.
- **Decision variant:** given a cost budget, does a feasible placement exist? (This is the knapsack/GAP feasibility question.)
- **Online variant:** the access pattern is revealed over time; minimize competitive ratio against the offline optimum, including **migration (write-back) cost** between tiers.

## 2. Mathematical Foundations
The static problem is a **multiple-knapsack / generalized assignment problem (GAP)**: objects with sizes and per-tier values must be packed into capacity-bounded tiers — NP-hard, with a known $(1-1/e)$-style or PTAS-for-fixed-tiers approximation landscape. With a single fast tier and one slow backing store it reduces to the classic **0/1 knapsack** of "which hot objects fit in fast memory."

The online version is exactly **weighted caching / $k$-server-flavored paging** generalized to multiple capacities and asymmetric tiers. The competitive ratio for caching is $\Theta(k)$ deterministic and $\Theta(\log k)$ randomized (Fiat et al.); with **asymmetric read/write and migration costs** (NVM writes cost more than reads, persistence adds write-back), the model becomes weighted caching / metrical task systems, where LRU/Marking guarantees and the **$O(\log k)$** randomized bound frame the achievable region.

Let access frequency follow a heavy-tailed law $\text{freq}_{(i)} \propto i^{-z}$ (Zipf). Then the optimal "fill fastest tier with hottest objects" greedy is optimal for **uniform object sizes**; with heterogeneous sizes it is the knapsack relaxation, and the LP-rounding gap quantifies suboptimality. The objective generalizes Denning's working-set theory: minimize **cost-per-access** $= \frac{\sum_t L_t \cdot a_t}{\sum_t a_t}$ where $a_t$ is the access count served from tier $t$.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Linux **AutoNUMA / tiered-memory** promotion-demotion and **TPP / Memtis** (page-temperature-based migration) for CXL/NVM; Intel **Memory Mode/App-Direct** for Optane. SAP HANA NSE (Native Storage Extension) and Oracle in-memory tiering place hot columns in fast memory.
- **DB-specific:** **Siberia / hot-cold classification** (Levandoski et al., ICDE 2013) logs access and classifies records hot/cold for placement. **Anti-caching** (DeBrabant et al., VLDB 2013) evicts cold tuples to disk in main-memory DBs. **X-Engine / LeanStore / Umbra** use pointer-swizzling and second-chance buffer management that generalize to tiers.
- HBM-aware analytics: bandwidth-binding scans/joins to HBM (links to Intel Xeon Max / Grace-Hopper studies).

## 4. Upper Bound
Static placement admits a **PTAS for a fixed number of tiers** (multiple knapsack with constant bins) and a fast greedy/LP-rounding algorithm with constant-factor approximation for the general GAP form; for uniform-size objects under a single fast tier, the hot-first greedy is **exactly optimal**. Online, randomized marking achieves an $O(\log k)$-competitive ratio for weighted caching, and LRU is $k$-competitive; these transfer to two-tier placement with $k$ = fast-tier capacity in objects. With migration costs, $O(\log k)$ remains achievable up to the read/write asymmetry factor. All bounds are in the standard external-memory / competitive-analysis model assuming known per-tier costs.

## 5. Lower Bound
Static feasibility is **NP-hard** (knapsack/GAP), so exact optimal placement is intractable in general; the PTAS is essentially the best possible short of P=NP for the multi-tier case (strong NP-hardness rules out an FPTAS for $\ge 2$ knapsacks). Online, **no deterministic algorithm beats $k$-competitive** and **no randomized algorithm beats $\Omega(\log k)$-competitive** for (weighted) caching — a classic lower bound (Sleator–Tarjan; Fiat–Karp–Luby–McGeoch–Sleator–Young). For the migration-aware problem, metrical-task-system lower bounds ($\Omega(\log n / \log\log n)$ randomized on general metrics) bound any tier-migration policy. These are information-theoretic / adversary-argument bounds, independent of hardware.

## 6. The Gap
Theory cleanly bounds the abstract caching/knapsack problem, yet **real placement remains empirically open** because the model's inputs are unknown and non-stationary: access frequencies must be *predicted*, tier costs are not a single scalar (bandwidth contention makes effective $B_t$ load-dependent and non-linear), and migration is bursty. The competitive-ratio guarantees assume a fixed metric, but bandwidth saturation makes the cost function workload-coupled (placing too much in HBM saturates it, raising effective latency for everyone). Closing the gap needs: online learning of $\text{freq}(o)$ with regret bounds, a **bandwidth-aware (congestion) cost model** rather than per-object additive cost, and migration policies whose write-back amortization is provably bounded under churn. No current system has an end-to-end guarantee under these realistic conditions.

## 7. Current Research (as of June 2026)
- **CXL-attached memory** placement and pooling: learned/profiled page-temperature migration (TPP, Memtis, and successors) extended to disaggregated CXL pools *(frontier — verify)*.
- Learned and reinforcement-learning placement policies that predict object hotness and pre-migrate (groups at CMU-DB, MIT, TUM/Umbra, Microsoft Research) *(frontier — verify)*.
- HBM-DRAM hybrid analytics on Grace-Hopper / Xeon-Max: bandwidth-binding operator placement and NUMA-aware scheduling *(frontier — verify)*.
- Persistent-memory-aware index and log placement post-Optane (shift to CXL persistent regions) *(frontier — verify)*.

## 8. Future Work
- Congestion/bandwidth-aware competitive analysis (load-dependent tier cost) closing the model-reality gap.
- Regret-bounded online placement integrating workload forecasting with migration cost.
- Co-optimization of placement with query plans (operator-aware, not just object-frequency-aware).
- Durability-aware placement: cost models that price persistence and crash-recovery, not just access latency.

## 9. Key References
- **[Foundational]** D. Sleator, R. Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. (Competitive caching, $k$-competitiveness.) — [DOI](https://doi.org/10.1145/2786.2793)
- **[Foundational]** A. Fiat, R. Karp, M. Luby, L. McGeoch, D. Sleator, N. Young. *Competitive Paging Algorithms.* J. Algorithms, 1991. ($\Theta(\log k)$ randomized bound.) — [DOI](https://doi.org/10.1016/0196-6774(91)90041-V)
- **[Foundational]** P. Denning. *The Working Set Model for Program Behavior.* CACM, 1968. — [DOI](https://doi.org/10.1145/363095.363141)
- **[SOTA]** J. Levandoski, P.-A. Larson, R. Stoica. *Identifying Hot and Cold Data in Main-Memory Databases (Siberia).* ICDE, 2013. — [DOI](https://doi.org/10.1109/ICDE.2013.6544811)
- **[SOTA]** J. DeBrabant, A. Pavlo, S. Tu, M. Stonebraker, S. Zdonik. *Anti-Caching: A New Approach to Database Management System Architecture.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2556549.2556575)
- **[SOTA]** H. A. Maruf, et al. *TPP: Transparent Page Placement for CXL-Enabled Tiered-Memory.* ASPLOS, 2023. — [arXiv](https://arxiv.org/abs/2206.02878)
- **[Survey]** A. van Renen, V. Leis, et al. *Persistent Memory I/O Primitives* / managing NVM in DBMS. VLDB/DaMoN, 2019. — [DBLP](https://dblp.org/rec/conf/damon/RenenVL0K19.html)

## 10. Worked Example

Two tiers: **HBM** (latency $L_{\text{HBM}} = 1$, capacity 2 objects) and **DRAM** ($L_{\text{DRAM}} = 5$). Five equal-size column partitions have access frequencies following a Zipf law, $\text{freq}_{(i)} \propto i^{-1}$:

$$\text{freq} = (1.00,\ 0.50,\ 0.33,\ 0.25,\ 0.20)\ \text{(unnormalized)}.$$

With uniform object sizes, the §2 "fill fastest tier with hottest objects" greedy is **optimal**: place partitions 1 and 2 in HBM, the rest in DRAM.

- Cost $= \sum_o \text{freq}(o)\cdot L_{\pi(o)} = \underbrace{(1.00+0.50)\cdot 1}_{\text{HBM}} + \underbrace{(0.33+0.25+0.20)\cdot 5}_{\text{DRAM}} = 1.50 + 3.90 = 5.40.$
- Any swap is worse: moving partition 3 into HBM in place of partition 2 gives $(1.00+0.33)\cdot1 + (0.50+0.25+0.20)\cdot5 = 1.33 + 4.75 = 6.08 > 5.40$.

**Congestion twist (the §6 gap).** Suppose HBM bandwidth saturates at total demand $> 1.4$. Our hot pair demands $1.50 > 1.4$, so effective HBM latency inflates (say to $1.8$), raising true cost to $(1.50)\cdot1.8 + 3.90 = 6.60$. The additive model mispredicted the optimum — exactly why bandwidth-aware cost is open.

---
*Part of the [DBMS Research catalog](../../README.md).*
