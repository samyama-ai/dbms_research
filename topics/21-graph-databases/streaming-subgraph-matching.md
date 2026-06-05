# Continuous subgraph matching on streaming graphs

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/streaming-subgraph-matching` · **Status:** partially-solved

## 1. Problem Statement
A query pattern $Q$ (a small connected graph, possibly labeled and with temporal constraints) is registered against a **graph stream**: an unbounded sequence of edge insertions and deletions $\langle \pm e_1, \pm e_2, \dots\rangle$ over a (possibly windowed) data graph $G_t$. **Continuously report every newly appearing match (and disappearing match)** of $Q$ as each update arrives, with:
- **low per-update latency** (ideally proportional to the number of affected matches, not $|G_t|$),
- **bounded state** (memory sublinear in the full stream, e.g., window-bounded), and
- correctness under a window or time-decay model.
Variants: insertion-only vs. fully-dynamic; *count* vs. *enumerate* incremental matches; exact vs. **approximate** (sampled) match counting under one-pass/limited-memory constraints.

## 2. Mathematical Foundations
This couples **incremental subgraph isomorphism** with the **graph-streaming model** (Henzinger–Raghavan–Rajagopalan; semi-streaming with $O(n\,\mathrm{polylog}\,n)$ space, Feigenbaum et al.). Match maintenance uses **matching orders** and partial-embedding indexes; the core hardness is subgraph isomorphism (NP-hard in pattern size, but data-complexity polynomial for fixed $Q$). Fine-grained limits come from **triangle/clique detection** and the **OMv conjecture** (dynamic triangle detection). Approximate counting leans on **AGM/fractional-cover** sampling and on streaming triangle estimators (**Bar-Yossef–Kumar–Sivakumar; Tsourakakis; Pavan et al.; McGregor–Vorotnikova**), whose space–accuracy trade-offs are governed by concentration bounds. Temporal/window semantics adds a sliding-window dimension (exponential-histogram / DGIM-style summaries). Worst-case-optimal join theory ($\rho^*(Q)$) bounds the intermediate state a delta evaluator must hold.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **TurboFlux** (SIGMOD 2018, data-centric transition index), **SymBi** (VLDB 2021, directed DAG dynamic programming), **RapidFlow** and **CaLiG** (2022–2023) improve filtering and reduce redundant partial matches; **Graphflow** (SIGMOD 2017) pioneered worst-case-optimal delta joins for continuous queries; **TC/IncIsoMatch** maintain triangles/cliques.
- **Theory/streaming-SOTA:** semi-streaming triangle/subgraph **counting** with $(1\pm\epsilon)$ guarantees (McGregor–Vorotnikova–Vu, PODS 2016; Kallaugher–Price). Tight space bounds for triangle counting in insertion-only and turnstile streams are known.

## 4. Upper Bound
For fixed pattern $Q$, continuous **enumeration** via worst-case-optimal delta joins yields per-update cost $O(\rho^*\text{-bounded})$ intermediate work and output-sensitive reporting (Graphflow / SymBi). For **approximate triangle counting** in the semi-streaming model: $(1\pm\epsilon)$ estimate in $\tilde O(m/\sqrt{T})$ space (where $T$ = #triangles), and one-pass turnstile estimators with provable variance bounds. Windowed match maintenance achieves state bounded by window size $\times$ partial-embedding fan-out.

## 5. Lower Bound
Dynamic detection of even a triangle requires $\Omega(m^{1-\epsilon})$ amortized update time unless the **OMv conjecture** fails (Henzinger–Krinninger–Nanongkai–Saranurak). Exact triangle counting in one streaming pass needs $\Omega(m)$ space (communication-complexity reduction from set-disjointness); distinguishing $0$ vs many triangles has tight multi-pass trade-offs. Subgraph isomorphism is NP-hard in $|Q|$, so combined complexity is intractable. These are **conditional fine-grained** and **information-theoretic / communication-complexity** bounds.

## 6. The Gap
For **single fixed small patterns** (triangles, paths) the picture is close to *tight* — hence "partially-solved." The open gaps: (1) **fully-dynamic** (insert+delete) exact maintenance of larger/cyclic patterns with provably output-sensitive per-update cost matching OMv lower bounds; (2) **multi-query** sharing — registering thousands of patterns with sublinear aggregate state; (3) **temporal-pattern** matching (motifs with time-order constraints) where stream order is itself a constraint; (4) closing the constant factors / passes for approximate counting of patterns beyond triangles (4-cliques, 5-cycles).

## 7. Current Research (as of June 2026)
Continuous-matching systems work by **Han, Kim, Lee, Park** (TurboFlux/SymBi lineage) and **Özsu, Salihoglu** (Waterloo); streaming-counting theory by **McGregor, Vorotnikova, Kallaugher, Price**. *(frontier — verify)* 2025–2026 directions include **temporal motif** continuous matching with bounded delay, GPU/SIMD continuous matchers, learned matching-order selection under drift, and **shared** multi-pattern indexes for thousands of registered queries. Integration of continuous matching into GQL/streaming-SQL engines (Flink-style graph operators) is emerging.

## 8. Future Work
- Output-sensitive fully-dynamic enumeration matching OMv lower bounds for cyclic patterns.
- Streaming approximate counting for general $k$-vertex patterns with tight space.
- Temporal/order-constrained continuous motif matching.
- Multi-query plan sharing and skew-adaptive partial-embedding eviction.

## 9. Key References
- **[Foundational]** Feigenbaum, Kannan, McGregor, Suri, Zhang. *On Graph Problems in a Semi-Streaming Model.* ICALP 2004 / TCS 2005.
- **[SOTA]** Kim et al. *TurboFlux: A Fast Continuous Subgraph Matching System for Streaming Graph Data.* SIGMOD 2018.
- **[SOTA]** Min et al. *Symmetric Continuous Subgraph Matching with Bidirectional Dynamic Programming (SymBi).* VLDB 2021.
- **[SOTA]** McGregor, Vorotnikova, Vu. *Better Algorithms for Counting Triangles in Data Streams.* PODS 2016.
- **[Foundational]** Henzinger, Krinninger, Nanongkai, Saranurak. *Unifying and Strengthening Hardness for Dynamic Problems via the Online Matrix-Vector Conjecture.* STOC 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
