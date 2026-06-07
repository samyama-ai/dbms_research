---
id: 29-hardware-conscious-db/fpga-partial-reconfiguration
title: "Partial reconfiguration for query acceleration"
topic: 29-hardware-conscious-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Partial reconfiguration for query acceleration

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/fpga-partial-reconfiguration` · **Status:** open

## 1. Problem Statement

FPGAs accelerate relational operators (filter, hash-join, regex, decompression, sort networks) but the fabric is finite: only a subset of an operator library fits at once. **Partial reconfiguration (PR)** lets the host swap a *region* of the fabric to a new operator bitstream while the rest keeps running, but each swap costs a non-trivial loading time $r$ (milliseconds: bitstream is megabytes streamed over PCIe/ICAP). Given a stream of queries whose operator demand changes over time, the problem is to **schedule which operator bitstreams occupy which reconfigurable regions, and when to reconfigure**, so that reconfiguration time is *amortized* across the workload rather than paid per query.

Variants: (i) **decision** — does a feasible schedule exist that keeps reconfiguration overhead below a budget while meeting per-query deadlines? (ii) **optimization (offline)** — given the full query/operator demand sequence, minimize total runtime = compute + reconfiguration; (iii) **online/competitive** — demand revealed incrementally, minimize cost against an offline optimum; (iv) **caching variant** — which bitstreams to keep "resident" in regions, a form of paging where page sizes (region areas) and fault costs (load times) are heterogeneous.

## 2. Mathematical Foundations

Model the fabric as a set of reconfigurable regions $\{R_1,\dots,R_k\}$ with areas $a_i$ (slices/columns). An operator $o$ has a bitstream of size $s_o$ fitting regions with $a_i \ge \text{area}(o)$; its load cost is $r_o \propto s_o/\beta_{\text{cfg}}$ where $\beta_{\text{cfg}}$ is configuration bandwidth. A query $q_t$ demands a set of operators $D_t$. The online problem generalizes **weighted caching / $k$-server**: regions are cache slots, loading a bitstream is a page fault of cost $r_o$, and the heterogeneous region/bitstream sizes make this **weighted caching with non-uniform sizes**, i.e., the **$k$-server / file caching** family.

Key foundations: competitive analysis (Sleator–Tarjan), the $O(\log k)$ randomized and $k$-deterministic bounds for weighted caching, and **generalized caching** results (Bansal–Buchbinder–Naor) giving $O(\log^2 k)$ via primal–dual LP rounding. The offline schedule, with placement constraints and deadlines, is an **interval scheduling / bin-packing hybrid**: packing time-varying operator sets into a fixed-area fabric is a 2D strip-packing relative, hence the offline decision variant is NP-hard. Useful structure: if reconfiguration of disjoint regions overlaps with compute (PR is concurrent with running logic), the schedule has a **partial-order/overlap** structure amenable to list scheduling with bounds via Graham-style $(2-1/m)$ arguments.

## 3. State of the Art (SOTA)

- **Systems:** **DoppioDB / Centaur** (ETH Zürich, Alonso group) integrate FPGA operators into a DBMS with a host-managed operator scheduler. **Fletcher** (TU Delft) and **AmorphOS** (UT Austin, OSDI 2018) provide OS-level multi-tenant FPGA region management and PR. **Coyote** (ETH, 2020) gives a shell with dynamic PR and virtual memory for FPGA databases.
- **Operator libraries:** hash-join, partitioning, and compression accelerators (Mueller, Teubner, Istvan, Sidler at ETH/TUM). Cloud FPGA (AWS F1, Azure) and the newer **AMD/Xilinx Versal** ACAP fabric make PR practical at column granularity.
- **Scheduling:** most systems use heuristic LRU-style bitstream caching plus static partitioning; principled competitive schedulers are largely absent — the planning gap is the open part.

## 4. Upper Bound

For the **caching abstraction**, online bitstream replacement admits an $O(\log^2 k)$-competitive randomized algorithm via generalized caching (Bansal–Buchbinder–Naor, FOCS 2008 line), and $k$-competitive deterministically (with $k$ regions). With uniform region sizes it collapses to standard weighted caching: $O(\log k)$ randomized, $k$ deterministic. For the **offline scheduling** optimization, list/area-packing heuristics give constant-factor approximations under restricted region models; exact optima are obtainable by ILP for small operator sets. With concurrent PR overlapping compute, a Graham-style list scheduler yields a $(2-1/k)$ guarantee on makespan in the model where reconfiguration latency is hidden behind unrelated running operators.

## 5. Lower Bound

The offline placement-and-schedule decision is **NP-hard** by reduction from 2D bin packing / strip packing (heterogeneous bitstream areas into fixed fabric). The online caching abstraction inherits the classic **lower bound of $k$** on deterministic competitive ratio and $\Omega(\log k)$ on randomized competitive ratio for (weighted) caching (Sleator–Tarjan; Fiat et al.) — no online policy can do asymptotically better in the adversarial model. These are the relevant hardness anchors; tighter database-specific lower bounds (accounting for compute/reconfiguration overlap and deadlines) are not established.

## 6. The Gap

For the pure caching view the gap is *closed up to logs*: $\Omega(\log k)$ vs $O(\log^2 k)$ randomized. But the realistic problem adds **placement (2D area) constraints, deadlines, and PR/compute overlap**, for which no algorithm achieves a proven competitive ratio matching a lower bound — it is **genuinely open**. Closing it requires either a competitive online scheduler for heterogeneous-area regions with overlapping reconfiguration, or a hardness result showing the overlap/deadline structure forces a worse ratio than plain caching.

## 7. Current Research (as of June 2026)

- Cost-model-driven PR scheduling co-optimized with the query optimizer's operator choice, so the planner avoids demanding un-resident operators *(frontier — verify)*.
- Versal ACAP and AIE-array-aware operator mapping (AMD), shifting PR granularity from regions to compute tiles *(frontier — verify)*.
- Multi-tenant FPGA-as-a-service region scheduling in cloud DBMS (ETH Coyote line, Alonso/Istvan).
- Learned demand predictors that prefetch bitstreams ahead of workload phase changes.

## 8. Future Work

- Provably competitive online schedulers integrating area packing, deadlines, and concurrent reconfiguration.
- Joint query-optimizer / PR-scheduler models that price reconfiguration into plan cost.
- Bitstream compression and differential reconfiguration to cut $r_o$ and shift the amortization threshold.
- Benchmarks with realistic phase-changing workloads to make the empirical gap reproducible.

## 9. Key References

- **[Foundational]** Sleator, D. D., Tarjan, R. E. *Amortized Efficiency of List Update and Paging Rules.* CACM, 1985. — [DOI](https://doi.org/10.1145/2786.2793)
- **[Foundational]** Bansal, N., Buchbinder, N., Naor, J. *A Primal-Dual Randomized Algorithm for Weighted Paging.* FOCS, 2007 / JACM. — [DOI](https://doi.org/10.1145/2339123.2339126)
- **[SOTA]** Istvan, Z., Sidler, D., Alonso, G. *Caribou / Doppio: Active Storage and FPGA Operators for Databases.* VLDB / FPGA, 2017–2020. — [DOI](https://doi.org/10.14778/3137628.3137632)
- **[SOTA]** Khawaja, A., et al. *Sharing, Protection, and Compatibility for Reconfigurable Fabric with AmorphOS.* OSDI, 2018. — [USENIX](https://www.usenix.org/conference/osdi18/presentation/khawaja)
- **[SOTA]** Korolija, D., Roscoe, T., Alonso, G. *Do OS Abstractions Make Sense on FPGAs? (Coyote).* OSDI, 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/roscoe)
- **[Survey]** Fang, J., Mulder, Y. T. B., Hidders, J., Lee, J., Hofstee, H. P. *In-Memory Database Acceleration on FPGAs: A Survey.* VLDB Journal, 2020. — [DOI](https://doi.org/10.1007/s00778-019-00581-w)

## 10. Worked Example

Model the fabric as $k = 2$ identical reconfigurable regions (cache slots), each holding one operator bitstream; loading a bitstream (a "page fault") costs $r = 5$ ms. The query stream demands this operator sequence:

$$ \text{filter},\ \text{join},\ \text{filter},\ \text{sort},\ \text{join},\ \text{sort},\ \text{filter} $$

Run **LRU** (= the move-to-front paging rule of Sleator–Tarjan), regions start empty:
- filter → miss (load), regions {filter}
- join → miss (load), {filter, join}
- filter → **hit**
- sort → miss, evict LRU=join → {filter, sort}
- join → miss, evict LRU=filter → {sort, join}
- sort → **hit**
- filter → miss, evict LRU=join → {sort, filter}

LRU faults = 5, costing $5 \times 5 = 25$ ms of reconfiguration.

Belady's optimal offline (evict the operator reused farthest in the future) on the same trace: filter(miss), join(miss), filter(hit), sort(miss, evict join), join(miss, evict sort), sort(miss), filter(hit with {join... }) — careful accounting gives 5 faults here too, since every operator recurs. The point: with $k=2$ slots and 3 distinct operators cycling, thrashing is unavoidable, and LRU is $k$-competitive — no deterministic policy beats ratio $k=2$ in the worst case. Adding a third region ($k=3$) would let all of {filter, join, sort} stay resident, dropping steady-state faults to zero — illustrating why region count, not just policy, governs amortized reconfiguration cost.

---
*Part of the [DBMS Research catalog](../../README.md).*
