---
id: 21-graph-databases/native-vs-relational-storage
title: "Native graph storage vs. relational backing"
topic: 21-graph-databases
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Native graph storage vs. relational backing

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/native-vs-relational-storage` · **Status:** empirically-open

## 1. Problem Statement
Does a *native* graph storage engine — one built on **index-free adjacency (IFA)**, where each vertex holds direct physical pointers to its incident edges — deliver a robust, asymptotic or constant-factor advantage over a well-tuned relational/columnar engine executing the same graph workload via joins?

The question has several variants:
- **Decision / qualitative:** Is there any workload class where IFA is *necessarily* faster than the best relational plan, or can a sufficiently good optimizer + physical design always match it?
- **Optimization / quantitative:** For workload mix $W$ (traversals, pattern matching, analytics, updates), data distribution $D$, and hardware $H$, which storage layout minimizes expected cost $\mathbb{E}_{q\sim W}[\text{cost}(q)]$?
- **Update/space variant:** How do the layouts trade query latency against update throughput and memory footprint under skew and churn?

This is fundamentally an *empirical/systems* question constrained by *theoretical* models of locality and join cost, not a single closed mathematical conjecture.

## 2. Mathematical Foundations
A property graph $G=(V,E,\ell,\pi)$ has labels $\ell$ and properties $\pi$. A $k$-hop traversal from a seed touches $O(\bar{d}^{\,k})$ vertices for average degree $\bar{d}$. **IFA claim:** neighbor lookup is $O(1)$ per edge (pointer chase), independent of $|V|,|E|$ — so a $k$-hop traversal is $O(\bar{d}^{\,k})$ with no $\log|V|$ index factor.

Relational execution models the same query as a chain of joins on an edge relation $\mathsf{E}(\text{src},\text{dst})$. With a clustered B-tree / sorted column, neighbor access is $O(\log|V|)$ or $O(1)$ amortized via hash; a $k$-hop traversal is $k-1$ joins whose cost is governed by the **AGM bound** $\;\rho^*(Q)$ on worst-case output size and by **worst-case-optimal join (WCOJ)** runtimes $O(\mathrm{IN}^{\rho^*}+\mathrm{OUT})$ (Ngo–Porat–Ré–Rudra).

The crux is the **memory hierarchy**, formalized by the **external-memory (I/O) model** (Aggarwal–Vitter): cost is the number of block transfers $\mathrm{scan}(n)=n/B$, $\mathrm{sort}(n)=\frac{n}{B}\log_{M/B}\frac{n}{B}$. IFA trades sequential bandwidth for pointer-chasing random I/O; columnar trades random access for vectorized sequential scans. Whether IFA wins reduces to whether traversal locality beats columnar bandwidth/SIMD for the given $W,D,H$ — a constant-factor question no asymptotic separation has settled.

## 3. State of the Art (SOTA)
- **Native systems:** Neo4j (IFA, fixed-size record store), TigerGraph, Memgraph.
- **Relational/columnar-backed graph engines:** SQL Server / Oracle graph extensions, **GraphframeS/GraphX**, **Umbra** and **DuckDB-based** graph processing, **SQLGraph** (Sun et al., SIGMOD 2015) showing RDBMS competitiveness, **GRainDB** (Jin et al., CIDR/VLDB) adding predefined join pointers ("semi-native") to DuckDB.
- **WCOJ-native graph DBs:** **Kùzu** (Feng et al., 2023–) and **GraphflowDB** combine columnar storage with factorized/WCOJ processing, arguably dissolving the dichotomy.
- **Benchmarks:** **LDBC SNB** (interactive/BI) and **LSQB** are the de-facto evaluation harnesses; results are mixed and highly workload-dependent.

## 4. Upper Bound
No layout dominates universally. WCOJ + factorized representations give pattern-matching cost $\tilde{O}(\mathrm{IN}^{\rho^*}+\mathrm{OUT})$ — *layout-agnostic*, achievable on a columnar engine. For pure pointer-chasing $k$-hop traversal, IFA achieves $O(|\text{output}|)$ random accesses; a relational hash-join chain matches this asymptotically (amortized $O(1)$ probe) but with larger constants and worse cache behavior. Thus the best *provable* upper bound is shared; differences are constant factors tied to locality, vectorization, and update cost.

## 5. Lower Bound
There is no super-linear lower bound separating the two for in-memory access. In external memory, **predecessor/pointer-chasing** lower bounds (cell-probe, Pătraşcu–Thorup) show $\Omega(\log_B n)$ per query is sometimes unavoidable for ordered access, but this binds *both* designs. The honest statement: **no known lower bound establishes an asymptotic separation** between IFA and relational storage; any gap is constant-factor and hardware-dependent, making it an empirical rather than complexity-theoretic question.

## 6. The Gap
The "gap" is not between matching bounds but between **marketing claims and reproducible evidence**. IFA's advantage is real for deep, selective, low-fan-out traversals with poor predictability; it erodes or reverses for high-fan-out pattern matching (where WCOJ wins), analytics (where columnar bandwidth wins), and update-heavy or memory-constrained settings. Closing it requires controlled, layout-isolated benchmarks separating *storage* from *optimizer* and *execution-engine* effects — rarely done cleanly.

## 7. Current Research (as of June 2026)
- Kùzu and DuckDB-PGQ blur the line by adding SQL/PGQ + WCOJ over columnar storage *(frontier — verify)*.
- "Semi-native" join indices (GRainDB-style predefined pointers bolted onto relational engines) are an active sweet spot.
- LDBC's SQL/PGQ-aligned workloads and **GQL (ISO/IEC 39075:2024)** standardization drive head-to-head evaluation.
- Groups: CWI (Boncz/DuckDB), Waterloo (Salihoglu, Kùzu), TUM (Neumann, Umbra), Oracle Labs (PGX). *(frontier — verify exact 2025–26 results)*

## 8. Future Work
- A taxonomy mapping $(W,D,H)$ regions to the dominant layout, with a model-driven crossover predictor.
- Adaptive/hybrid engines that morph between IFA and columnar per query fragment.
- Standardized layout-isolating benchmarks (fix optimizer + engine, vary only storage).
- Cost models incorporating SIMD, NUMA, and persistent memory.

## 9. Key References
- **[Foundational]** Codd, E. F. *A Relational Model of Data for Large Shared Data Banks.* CACM, 1970. — [DOI](https://doi.org/10.1145/362384.362685)
- **[Foundational]** Aggarwal, A., Vitter, J. S. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[SOTA]** Ngo, H. Q., Porat, E., Ré, C., Rudra, A. *Worst-Case Optimal Join Algorithms.* PODS 2012 / JACM 2018. — [arXiv](https://arxiv.org/abs/1203.1952) · [DOI](https://doi.org/10.1145/3180143)
- **[SOTA]** Sun, W. et al. *SQLGraph: An Efficient Relational-Based Property Graph Store.* SIGMOD 2015. — [DOI](https://doi.org/10.1145/2723372.2723732)
- **[SOTA]** Jin, G., Feng, X., Chen, Z., Liu, C., Salihoğlu, S. *Kùzu Graph Database Management System.* CIDR 2023. — [PDF](https://www.cidrdb.org/cidr2023/papers/p48-jin.pdf)
- **[Survey]** Angles, R., Gutiérrez, C. *Survey of Graph Database Models.* ACM Computing Surveys, 2008. — [DOI](https://doi.org/10.1145/1322432.1322433)
- **[Survey]** LDBC. *The LDBC Social Network Benchmark.* (LDBC Council technical report / VLDB-affiliated), 2015–2024. — [DBLP](https://dblp.org/rec/conf/sigmod/ErlingALCGPPB15.html)

## 10. Worked Example

A social graph with $|V| = 10^7$ users, average degree $\bar d = 50$. Query: "friends-of-friends" — a 2-hop traversal from a seed user, expected to touch $\bar d^2 = 2500$ vertices.

**Native / IFA (e.g., Neo4j):** the seed record holds a direct pointer to its adjacency list. Step 1 chases $50$ pointers; step 2 chases $50 \times 50 = 2500$. Total $\approx 2550$ pointer dereferences, each $O(1)$, with **no** $\log|V|$ index lookup. If each dereference is a cache-missing random read, cost $\approx 2550$ random memory accesses.

**Relational (edge table $\mathsf{E}(\text{src},\text{dst})$, B-tree on src):** each hop is an index nested-loop join. Hop 1: one B-tree probe of depth $\lceil \log_{2} 10^7 \rceil \approx 24$ comparisons, returning $50$ rows. Hop 2: $50$ probes returning $2500$ rows. Index probes $\approx 51$, comparisons $\approx 51 \times 24 \approx 1224$, plus $2500$ row materializations.

Asymptotically both are $O(\bar d^2 + \text{output})$; the difference is the constant $\log|V|$ factor on probes and cache behavior. Now switch to a **high-fan-out triangle pattern** ($u\!-\!v$, $v\!-\!w$, $w\!-\!u$): the AGM bound gives worst-case output $\le |E|^{3/2}$, and a WCOJ plan on columnar storage achieves $\tilde O(|E|^{3/2})$ — beating naive IFA pairwise traversal that can blow up intermediate results. This is precisely the regime where the "native always wins" claim reverses.

---
*Part of the [DBMS Research catalog](../../README.md).*
