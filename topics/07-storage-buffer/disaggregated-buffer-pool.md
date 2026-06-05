# Buffer Management for Disaggregated Memory

> **Topic:** Storage & Buffer Management · **ID:** `07-storage-buffer/disaggregated-buffer-pool` · **Status:** empirically-open

## 1. Problem Statement
In **memory-disaggregated** architectures the database buffer pool spans (i) a small pool of **local DRAM** attached to the compute node and (ii) a large pool of **far memory** reached over **CXL** (cache-coherent load/store at ~150–400 ns) or **RDMA** (one-sided reads/writes at ~1–3 µs). Far memory is cheaper and larger but has **non-uniform, asymmetric latency** and limited bandwidth.

The problem: manage a multi-level buffer pool where the question is not just *evict vs. keep* but *which tier* a page lives in. On a miss you may fetch from storage; on a "near-miss" the page is in far memory and must be promoted/demoted. Decisions: admission, promotion (far→local), demotion (local→far), and eviction to storage — under read/write asymmetry, bandwidth caps, and the option to access a far page **in place** rather than promoting it.

Variants: (a) **optimization** — minimize total stall/access time (weighted by tier latency); (b) **decision** — meet a tail-latency SLO under a DRAM budget; (c) the **placement** variant — given access traces, statically partition hot/cold pages across tiers. Because the cost model has 3+ latency classes with bandwidth and coherence constraints, no clean competitive theory yet matches practice — hence *empirically-open*.

## 2. Mathematical Foundations
Model tiers $T_0$ (local DRAM, capacity $k_0$, access cost $a_0$), $T_1$ (far memory, $k_1$, cost $a_1>a_0$), $T_2$ (storage, cost $a_2\gg a_1$). This generalizes **weighted caching** to a **multi-level / hierarchical caching** problem with movement (promotion/demotion) costs $m_{ij}$.

A faithful abstraction is the **$k$-server / Metrical Task System** on a metric where serving a request from tier $T_i$ costs $a_i$ and moving a page costs $m_{ij}$, or equivalently **caching with multiple cache levels and inter-level transfer costs**. The bandwidth cap turns it into a *constrained* online problem (rate limits on movement per unit time), and read/write asymmetry makes the cost matrix non-symmetric — breaking metric assumptions that $k$-server analyses rely on.

Relevant theory: hierarchical/multi-level caching competitive bounds, the **file-bundle / interval** LP for caching with movement, and **online convex optimization with switching costs** when modeling continuous promotion budgets. The asymmetry connects to the *cache-oblivious* and *external-memory* (Aggarwal–Vitter) lineage, here with three populated levels rather than two.

## 3. State of the Art (SOTA)
**Systems-SOTA:** This is where progress is. CXL-aware buffer pools and far-memory tiering: AIFM (Ruan et al., OSDI 2020) and follow-ons (application-integrated far memory), TPP (Maruf et al., ASPLOS 2023, transparent page placement for CXL), Pond (Li et al., ASPLOS 2023, CXL memory pooling at Azure), and Memtis/Colloid-style hotness-tiering. DB-specific: LeanStore/Umbra-style pointer-swizzling buffer managers extended to far memory, and disaggregated-memory DB engines (PolarDB Serverless, and RDMA buffer pools). These rely on **hotness sampling + threshold heuristics**, not provable policies.

**Theory-SOTA:** multi-level / hierarchical caching has $O(\log k)$-type online results for restricted cost models, but none capture CXL/RDMA asymmetry, bandwidth, and coherence jointly.

## 4. Upper Bound
For hierarchical caching with uniform per-level costs and free intra-tier movement, online primal-dual gives $O(\log(k_0+k_1))$-competitive bounds. With explicit movement costs the problem reduces to a $k$-server instance on a weighted metric, inheriting $O(\text{poly}\log)$ competitive ratios (via Bansal–Buchbinder–Madry–Naor's $k$-server bound) — but only in the *symmetric metric* idealization, ignoring bandwidth and write asymmetry. No upper bound is known for the realistic asymmetric, bandwidth-limited model.

## 5. Lower Bound
Inherits paging lower bounds: deterministic $\ge \min(k_0,\ldots)$ and randomized $\Omega(\log k)$. The $k$-server lower bound $\Omega(\log k / \log\log k)$ (randomized) applies to the metric abstraction. Bandwidth constraints make even the *offline* placement problem NP-hard (it embeds a constrained assignment/knapsack). No tight lower bound exists for the asymmetric three-tier model with movement caps — the model itself is not yet standardized.

## 6. The Gap
The gap is **definitional and empirical**, not a clean upper/lower mismatch. We lack (a) an agreed cost model that captures CXL vs. RDMA asymmetry, bandwidth, and coherence; (b) competitive or learning-augmented guarantees in that model; and (c) a demonstration that any policy with guarantees beats production hotness-threshold heuristics on real DB workloads. Closing it requires formalizing the model, then proving guarantees or showing impossibility — and validating empirically.

## 7. Current Research (as of June 2026)
- **CXL memory tiering** is the hottest systems frontier: TPP, Pond, Colloid, and DB-engine integrations *(frontier — verify which ship in 2025–2026)*; groups at Microsoft Research, Meta, CMU (Berger, Pavlo), and Wisconsin.
- **Disaggregated DBMS** designs (compute–memory separation) revisiting buffer management from scratch (LeanStore far-memory variants, Umbra, PolarDB) *(frontier — verify)*.
- Learning-augmented and reinforcement-learning tiering controllers for far memory.
- Theory side: extending $k$-server / MTS to asymmetric metrics and bandwidth-constrained online caching.

## 8. Future Work
Standardize a benchmark and cost model for tiered far-memory buffer pools; prove competitive/learning-augmented bounds for asymmetric multi-tier caching with movement caps; co-design with coherence (when to access-in-place vs. promote); integrate write-back and recovery (dirty pages in far memory); tail-latency SLO-aware admission.

## 9. Key References
- **[Foundational]** A. Aggarwal, J. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. (external-memory / hierarchy model) — [DOI](https://doi.org/10.1145/48529.48535)
- **[SOTA]** Z. Ruan, M. Schwarzkopf, et al. *AIFM: High-Performance, Application-Integrated Far Memory.* USENIX OSDI 2020. — [USENIX](https://www.usenix.org/conference/osdi20/presentation/ruan)
- **[SOTA]** H. A. Maruf et al. *TPP: Transparent Page Placement for CXL-Enabled Tiered-Memory.* ASPLOS 2023. — [DOI](https://doi.org/10.1145/3582016.3582063)
- **[SOTA]** H. Li et al. *Pond: CXL-Based Memory Pooling Systems for Cloud Platforms.* ASPLOS 2023. — [DOI](https://doi.org/10.1145/3575693.3578835)
- **[SOTA]** V. Leis et al. *LeanStore: In-Memory Data Management Beyond Main Memory.* ICDE 2018. — [DBLP](https://dblp.uni-trier.de/rec/conf/icde/LeisHK018.html)
- **[Foundational]** N. Bansal, N. Buchbinder, A. Madry, J. Naor. *A Polylogarithmic-Competitive Algorithm for the k-Server Problem.* JACM, 2015. — [DOI](https://doi.org/10.1145/2783434)

## 10. Worked Example

Three tiers: $T_0$ local DRAM (capacity $k_0 = 1$ page, access $a_0 = 100$ ns), $T_1$ CXL far memory ($k_1 = 2$, $a_1 = 300$ ns), $T_2$ storage ($a_2 = 10000$ ns). Promotion $T_1\to T_0$ costs $m = 300$ ns.

Access trace on pages $\{A, B\}$, both initially in $T_1$: $A, A, A, B, A, A, A$ ($A$ is hot).

Policy 1 — **access-in-place** (never promote): every access pays $a_1 = 300$. Total $= 7 \times 300 = 2100$ ns.

Policy 2 — **promote-on-touch** $A$ into $T_0$: first $A$ costs $m + a_0 = 300 + 100 = 400$; the next two $A$ hits cost $a_0 = 100$ each; $B$ from $T_1$ costs $300$; remaining three $A$ hits cost $100$ each. Total $= 400 + 200 + 300 + 300 = 1200$ ns.

Promotion wins here ($1200 < 2100$) because $A$'s reuse ($6$ accesses) amortizes the one-time $300$ ns move. Flip the trace to $A,B,A,B,\dots$ with $k_0=1$ and promotion thrashes — each promote is immediately evicted, so access-in-place becomes better. The open problem: choosing promote-vs-in-place online, under bandwidth caps and read/write asymmetry, with a provable competitive ratio.

---
*Part of the [DBMS Research catalog](../../README.md).*
