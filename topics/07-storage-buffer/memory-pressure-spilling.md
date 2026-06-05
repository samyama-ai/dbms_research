# Buffer Management Under Strict Memory Pressure (Spilling)

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/memory-pressure-spilling` · **Status:** empirically-open

## 1. Problem Statement
Under a fixed RAM budget, two consumers compete: the **buffer pool** (caching base-table/index pages) and **query operators** (hash tables, sort runs, aggregation state) that receive *memory grants*. When demand exceeds capacity, the system must decide what gives: evict buffer pages, shrink operator grants (forcing **spill-to-disk** of hash/sort state), or admit/queue fewer queries. These decisions are coupled — evicting buffer pages raises future miss I/O, while spilling an operator raises immediate I/O and may cascade (grace-hash recursion). The problem: **jointly schedule buffer eviction, operator memory grants, and spill decisions** to minimize total I/O / latency under a hard memory bound, across concurrent queries.

Variants:
- **Decision:** Given concurrent operators with memory demand curves and a RAM bound $M$, is there a grant+eviction allocation keeping total spill+miss I/O under budget $B$?
- **Optimization (offline):** Minimize total I/O given known demands.
- **Online/admission:** Decide grants and spills as queries arrive with uncertain (estimated) memory needs.

## 2. Mathematical Foundations
This couples three classics. **(1) Buffer caching** — paging, LRU $k$-competitive / randomized $O(\log k)$. **(2) Operator memory & spilling** — external-memory (I/O) model (Aggarwal–Vitter): sorting/joining $N$ elements with $M$ memory and block size $B$ costs $\Theta(\frac{N}{B}\log_{M/B}\frac{N}{B})$ I/Os; a hash join spilling under memory $M$ has I/O cost that grows as partitions recurse when $M$ is too small (cost $\propto$ number of grace-hash passes $= \lceil \log_{M/B}(N/M)\rceil$). **(3) Memory allocation among competing jobs** — modeled as resource allocation / knapsack-style grant assignment, or as a **convex cost-sharing** problem since each operator's I/O cost is a (convex, decreasing) function $f_i(g_i)$ of its grant $g_i$ subject to $\sum g_i \le M$. Minimizing $\sum_i f_i(g_i)$ under the budget is a separable convex resource-allocation problem solvable by a **water-filling / marginal-cost (greedy on $-f_i'$)** argument when $f_i$ are convex — but operator cost curves are **step functions** (spill thresholds), making the exact problem a discrete (NP-hard knapsack-flavored) allocation. Online, with uncertain demands, it is a **bin-packing / online scheduling with reservations** problem.

## 3. State of the Art (SOTA)
- **Systems:** *Memory grant* mechanisms in SQL Server (grant feedback, learned grant sizing in recent versions), Oracle PGA automatic memory management, PostgreSQL `work_mem` per-operator (notoriously hard to set globally). *DB2 STMM* (Self-Tuning Memory Manager, Storm et al., VLDB 2006) — feedback-control allocation across buffer pools and sort heaps. Spark/Tungsten unified memory manager (execution vs storage memory with borrowing/eviction). *Umbra/LeanStore* (TUM) — buffer manager that lets operator state and buffered pages share one pointer-swizzled pool, blurring the boundary.
- **Adaptive/learned:** SQL Server **memory grant feedback** (adjusts grants from prior execution actuals); learned/ML grant prediction *(frontier — verify)*. Robust/adaptive operators (e.g. adaptive hybrid hash that spills gracefully) — Graefe's work on robust query processing.
- **Theory:** external-memory join/sort bounds (Aggarwal–Vitter); convex resource allocation (Ibaraki–Katoh).

## 4. Upper Bound
The **offline separable-convex** grant allocation (continuous, convex $f_i$) is solvable optimally in $O(n\log n)$ by greedy marginal allocation (Ibaraki–Katoh). With step-function (discrete spill-threshold) costs the offline problem is NP-hard but admits FPTAS via knapsack DP. External-memory hash/sort gives matching upper bounds on per-operator spill I/O. For the **online** coupled buffer+grant problem there is **no known competitive algorithm with a tight ratio**; systems use feedback control (STMM, grant feedback) that converges empirically but lacks worst-case guarantees. Best practical results: SQL Server grant feedback and Spark unified memory empirically cut spill I/O substantially versus static splits.

## 5. Lower Bound
The discrete grant-allocation (which operators to fully fund vs spill) is **NP-hard** (reduction from knapsack/partition). The buffer-caching component carries the paging lower bounds ($\Omega(k)$ det., $\Omega(\log k)$ rand.). External-memory sorting/joining has the **tight** $\Omega(\frac{N}{B}\log_{M/B}\frac{N}{B})$ I/O lower bound (Aggarwal–Vitter), so once memory is fixed below the working set, spill I/O is unavoidable and lower-bounded — a hard floor. Online, with uncertain demands, an adversary can make any non-clairvoyant grant policy spill an operator that would have fit, giving an $\Omega(\log)$-type competitive lower bound inherited from online scheduling/bin-packing.

## 6. The Gap
**Empirically-open.** Each *component* is well understood (paging bounds, AV external-memory bounds, convex allocation), but the **coupled online problem** — buffer eviction ↔ grant sizing ↔ spill decisions across concurrent queries under uncertain estimates — has no unified competitive theory and no system with guarantees; production memory managers are feedback-control heuristics that work well in practice yet can pathologically thrash or over-spill. The gap is between strong per-component bounds and the absence of a joint model. Closing it needs an online competitive analysis coupling caching, convex grant allocation, and external-memory spill cost, ideally prediction-augmented (using grant-feedback actuals).

## 7. Current Research (as of June 2026)
- **Learned/feedback memory-grant sizing** beyond SQL Server's feedback, predicting per-operator high-water memory and confidence *(frontier — verify)*.
- Unified buffer/operator memory pools (Umbra, Spark, Velox) that dynamically rebalance with eviction+spill under one policy *(frontier — verify)*.
- Robust/adaptive operators that spill gracefully and re-absorb memory as pressure eases (Graefe-style robustness).
- Admission control + memory as joint resource scheduling for multi-tenant/serverless DBMS.
- Groups: TUM (Neumann/Leis — Umbra), Microsoft (grant feedback, robust QP), Databricks/Meta (Velox, Photon), Wisconsin/CMU on resource scheduling.

## 8. Future Work
- A competitive model jointly covering caching, grant allocation, and spill I/O.
- Prediction-augmented memory management with consistency/robustness guarantees from grant feedback.
- Multi-tenant fairness vs efficiency under shared memory pressure.
- Spilling for heterogeneous tiers (NVM/CXL as a spill target cheaper than disk; links to NVM and GPU buffer problems).

## 9. Key References
- **[Foundational]** Aggarwal, Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** Storm, Garcia-Arellano, Lightstone, et al. *Adaptive Self-Tuning Memory in DB2 (STMM).* VLDB, 2006. — [PDF](https://www.vldb.org/conf/2006/p1081-storm.pdf)
- **[SOTA]** Neumann, Freitag. *Umbra: A Disk-Based System with In-Memory Performance.* CIDR, 2020. — [DBLP](https://dblp.org/rec/conf/cidr/NeumannF20.html)
- **[SOTA]** Graefe. *Robust Query Processing.* (tutorial/survey line), 2011. — [Dagstuhl 10381](https://www.dagstuhl.de/10381)
- **[Foundational]** Ibaraki, Katoh. *Resource Allocation Problems: Algorithmic Approaches.* MIT Press, 1988. — [MIT Press](https://mitpress.mit.edu/9780262090278/resource-allocation-problems/)
- **[Survey]** Sleator, Tarjan. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. — [DOI](https://doi.org/10.1145/2786.2793)

## 10. Worked Example

Memory bound $M=100$ pages. Two hash joins compete; block size $B=10$. Each operator's spill I/O is a step function of its grant $g_i$: if $g_i\ge$ its build side it stays in memory (0 I/O); else it grace-partitions, costing $2\lceil\log_{g_i/B}(N_i/g_i)\rceil\cdot N_i/B$ I/Os.

- $J_1$: build side $N_1=600$ pages. Fully fit needs $g_1=60$.
- $J_2$: build side $N_2=800$ pages. Fully fit needs $g_2=80$.

Both can't fit ($60+80=140>100$). Compare:
- Fund $J_1$ ($g_1=60$), give $J_2$ the rest ($g_2=40$): $J_2$ spills, passes $=\lceil\log_{4}(800/40)\rceil=\lceil\log_4 20\rceil=3$, cost $\approx 2\cdot3\cdot80=480$ I/Os.
- Fund $J_2$ ($g_2=80$), $g_1=20$: $J_1$ passes $=\lceil\log_2(600/20)\rceil=\lceil\log_2 30\rceil=5$, cost $\approx 2\cdot5\cdot60=600$.

Funding the *larger* operator and spilling the smaller wins (480 < 600) — the marginal-value/knapsack intuition. A static even split (50/50) spills both and does worse.

---
*Part of the [DBMS Research catalog](../../README.md).*
