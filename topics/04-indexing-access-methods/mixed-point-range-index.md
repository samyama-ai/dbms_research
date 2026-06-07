---
id: 04-indexing-access-methods/mixed-point-range-index
title: "Optimal index for mixed point/range workloads"
topic: 04-indexing-access-methods
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimal index for mixed point/range workloads

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/mixed-point-range-index` · **Status:** empirically-open

## 1. Problem Statement
Workloads rarely consist of pure point lookups or pure range scans; they mix the two in unknown, time-varying proportions. A **hash index** serves points in $O(1)$ but cannot scan a range; a **B-tree/LSM** serves ranges in $O(\log n + r/B)$ but pays sortedness overhead on points; a **learned index** approximates the CDF for both but degrades under updates and skew. The problem: **construct (or prove the impossibility of) a single index structure that is provably near-optimal — within a constant or polylog factor — across the entire spectrum from point-heavy to range-heavy workloads simultaneously**, under realistic update and memory budgets.

- **Optimization variant:** minimize expected cost $\mathbb{E}_{q\sim D}[\text{cost}(q)]$ over a workload distribution $D$ mixing point and range queries, relative to the per-instance optimum.
- **Decision variant:** does a structure of size $O(n)$ achieve point cost $O(1)$ *and* range cost $O(\log n + r/B)$ simultaneously under updates?
- **Counting variant:** support `COUNT(range)` and point existence with one shared structure near-optimally.

*Empirically-open:* hybrids (e.g., learned + B-tree, filters over sorted runs) win on benchmarks, but no structure is *proven* near-optimal across the mixed spectrum, and the achievable Pareto frontier is uncharacterized.

## 2. Mathematical Foundations
Formalize a workload as a distribution $D$ over queries with point-fraction $p$ and range-fraction $1-p$. The **RUM tradeoff** (Athanassoulis et al., EDBT 2016) posits that read, update, and memory overheads cannot be simultaneously minimized; mixed point/range adds an orthogonal *access-pattern* axis. Lower bounds draw on:

- **Predecessor/successor complexity** (Pătraşcu–Thorup): range queries reduce to predecessor search, which in the cell-probe model costs $\Theta(\min(\log_w n, \log w / \log\log w \dots))$ — points need not pay this.
- **Instance optimality** (Fagin et al.; Lipton): an index is *instance-optimal* if its cost on every input is within a constant of the best index for that input. Learned indexes target this empirically.
- **Information-theoretic floor:** a structure resolving $r$-element ranges and existence must encode order information ($\Omega(n\log n)$ bits unless keys are succinctly structured) while a pure hash needs only $\Theta(n)$ bits for membership — a tension between membership-optimal and order-optimal layouts.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** no proven simultaneously-optimal structure. The **RUM** framework characterizes the tradeoff space; **cache-oblivious B-trees** (Bender et al.) achieve optimal range I/O without tuning but pay $\Theta(\log n)$ on points; **fusion trees / van Emde Boas** improve predecessor but not points-plus-ranges jointly.
- **Systems-SOTA:** the **Recursive Model Index (RMI)** (Kraska et al., SIGMOD 2018) and updatable successors **ALEX** (Ding et al., SIGMOD 2020), **PGM-index** (Ferragina–Vinciguerra, VLDB 2020), and **LIPP** approximate both query types well; **Hist-Tree / filtered LSM** hybrids and **Bourbon** (learned LSM) integrate point filters with range structure. **SOSD** benchmarks compare them empirically.

## 4. Upper Bound
The PGM-index gives **provable** worst-case range bounds: $O(\log n)$ query with $O(n/B)$ space and a tunable error $\varepsilon$ controlling the last-mile scan, matching optimal range I/O up to the model. For points, hash and filtered structures give $O(1)$ expected. The best *combined* upper bound currently is a **composite**: maintain a learned/B-tree backbone ($O(\log n + r/B)$ range) plus an auxiliary filter or hash giving $O(1)$ expected points — at additive space cost. This holds in the **external-memory (DAM) and word-RAM models** but is a construction, not a proven optimum.

## 5. Lower Bound
Range queries inherit the **cell-probe predecessor lower bound** of Pătraşcu–Thorup (2006): for static predecessor with space $n^{O(1)}$, query time is $\Omega(\log w/\log\log w)$-type, unavoidable for the range component. No single lower bound proves that *combining* points and ranges forces a super-constant penalty on points; the open question is whether there is a **cell-probe separation** showing that any $O(n)$-space structure achieving optimal range scans must pay $\omega(1)$ on points (or vice versa). Membership lower bounds (Buhrman et al.) bound the point side independently.

## 6. The Gap
The gap is between rich *empirical* Pareto frontiers (learned hybrids dominate on SOSD-style mixes) and the *absence of a matching optimality theorem or impossibility result*. It is genuinely open whether a single $O(n)$-space dynamic structure can be simultaneously instance-optimal for points and ranges, or whether a provable tradeoff forbids it. Closing it requires either (a) a construction with a two-sided optimality proof, or (b) a cell-probe lower bound separating the combined object.

## 7. Current Research (as of June 2026)
- **Workload-adaptive / self-designing** indexes that morph between hash-like and tree-like layouts as $p$ shifts (Idreos's "data calculator" lineage) *(frontier — verify)*.
- **Learned indexes with worst-case guarantees** (PGM descendants) extended to mixed workloads with provable range *and* point bounds *(frontier — verify)*.
- **Robustness to skew and adversarial inserts** in learned hybrids — closing the gap between average-case wins and worst-case guarantees.
- Groups: Tim Kraska (MIT), Stratos Idreos (Harvard DASlab), Ferragina–Vinciguerra (Pisa), Athanassoulis (BU).

## 8. Future Work
- A provably instance-optimal dynamic structure for mixed point/range workloads.
- A cell-probe separation theorem quantifying any unavoidable point↔range penalty.
- Online learning of $p$ with regret bounds against the best fixed structure.

## 9. Key References
- **[Foundational]** M. Pătraşcu, M. Thorup. *Time-Space Trade-Offs for Predecessor Search.* STOC, 2006. — [arXiv](https://arxiv.org/abs/cs/0603043)
- **[Foundational]** M. Athanassoulis, et al. *Designing Access Methods: The RUM Conjecture.* EDBT, 2016. — [DBLP](https://dblp.org/rec/conf/edbt/AthanassoulisKM16.html)
- **[SOTA]** T. Kraska, A. Beutel, E. Chi, J. Dean, N. Polyzotis. *The Case for Learned Index Structures.* SIGMOD, 2018. — [arXiv](https://arxiv.org/abs/1712.01208)
- **[SOTA]** P. Ferragina, G. Vinciguerra. *The PGM-index: A Fully-Dynamic Compressed Learned Index with Provable Worst-Case Bounds.* VLDB, 2020. — [DOI](https://doi.org/10.14778/3389133.3389135)
- **[SOTA]** J. Ding, et al. *ALEX: An Updatable Adaptive Learned Index.* SIGMOD, 2020. — [arXiv](https://arxiv.org/abs/1905.08898)
- **[Survey]** R. Marcus, et al. *Benchmarking Learned Indexes (SOSD).* VLDB, 2020. — [PDF](https://vldb.org/pvldb/vol14/p1-marcus.pdf)

## 10. Worked Example

Take $n=8$ keys $\{3,7,12,18,25,31,40,52\}$, block size $B=4$. A workload sends $p=0.5$ point lookups and $0.5$ range scans.

- **Pure hash index:** point lookup of key $25$ costs $O(1)$ = ~1 probe. But a range query $[12,40]$ cannot be answered — you must scan all 8 keys.
- **Pure B-tree:** range $[12,40]$ descends $\lceil\log_2 8\rceil = 3$ levels, then scans $r=4$ matches in $\lceil r/B\rceil = 1$ block I/O: cost $\approx 3+1$. But point lookup of $25$ also pays the full $\log_2 8 = 3$ descent instead of $O(1)$.
- **Composite (B-tree backbone + hash filter):** point lookup of $25$ hits the hash in ~1 probe; range $[12,40]$ uses the backbone at cost $\approx 4$.

Expected cost: hash-only $= 0.5(1)+0.5(8)=4.5$; B-tree-only $=0.5(3)+0.5(4)=3.5$; composite $\approx 0.5(1)+0.5(4)=2.5$ — but the composite pays extra space for the auxiliary filter, exactly the unproven tradeoff at the heart of the problem.

---
*Part of the [DBMS Research catalog](../../README.md).*
