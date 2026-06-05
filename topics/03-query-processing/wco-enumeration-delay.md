# Worst-case-optimal enumeration with delay guarantees

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/wco-enumeration-delay` · **Status:** partially-solved

## 1. Problem Statement

Many applications need query answers *streamed* — produce the first answer fast, then each subsequent answer after a small **delay**, rather than materializing the whole (possibly huge) result. The **enumeration with preprocessing** model splits cost into a *preprocessing* phase (build a data structure) and an *enumeration* phase (emit answers one by one). The gold standard is **constant-delay enumeration after linear preprocessing** ($\mathrm{CD}\circ\mathrm{lin}$): $O(N)$ preprocessing, then $O(1)$ delay between consecutive distinct answers, no duplicates.

The problem: **for which conjunctive (and broader) queries can we achieve near-linear preprocessing and constant/polylog delay, and where this is impossible, what is the tight preprocessing/delay trade-off — including under updates (dynamic enumeration) and for queries with projection/aggregation/ordering?** Variants: (a) **full CQs** (no projection) vs. (b) **CQs with free variables** (projection makes it hard); (c) **static** vs. **dynamic** (maintain constant delay under tuple insertions/deletions); (d) **ranked/ordered** enumeration (emit in score order). It is **partially solved**: tight dichotomies exist for self-join-free CQs (free-connex acyclicity), but general queries, ordering, and dynamic maintenance remain open.

## 2. Mathematical Foundations

For a CQ $Q$ with free variables (head) $\mathrm{free}(Q)$, the key structural property is **free-connex acyclicity**: $Q$ is $\alpha$-acyclic *and* remains acyclic after adding a hyperedge covering exactly $\mathrm{free}(Q)$. The central dichotomy (Bagan–Durand–Grandjean) states: a **self-join-free** acyclic CQ admits $\mathrm{CD}\circ\mathrm{lin}$ enumeration **iff** it is free-connex (assuming Boolean matrix multiplication is not in $O(n^2)$ combinatorially, and sparse triangle hypotheses for the cyclic case). Formally, if $Q$ is acyclic but **not** free-connex, constant-delay-after-linear-preprocessing would imply a faster-than-known algorithm for Boolean matrix multiplication / sparse triangle detection. For cyclic queries, preprocessing inherits width: $\tilde O(N^{\mathrm{fhw}})$ or $\tilde O(N^{\mathrm{subw}})$ before constant-delay enumeration becomes possible. Worst-case-optimal *enumeration* combines this with the AGM/Generic-Join machinery so total emitted-cost is output-sensitive and preprocessing is width-bounded.

## 3. State of the Art (SOTA)

**Theory-SOTA:** **Bagan–Durand–Grandjean** (CSL 2007) established the free-connex dichotomy for acyclic CQs. **Brault-Baron** extended characterizations to cyclic queries. For **dynamic** enumeration, **Berkholz–Keppeler–Schweikardt** (PODS 2017) characterize CQs maintainable with constant delay under updates (the $q$-hierarchical fragment) with constant update time. **Ranked enumeration** with logarithmic delay in score order (Tziavelis–Ajwani–Gatterbauer–Riedewald–Yannakakis, "any-$k$", VLDB 2020) gives $O(\log k)$-delay top-$k$ join enumeration. **Idris–Ugarte–Vansummeren** handle dynamic conjunctive query enumeration ("dynamic constant-delay"). **Systems-SOTA:** Factorized databases (Olteanu–Schleich, FDB/LMFAO) and any-$k$ ranked-enumeration prototypes implement these ideas; mainstream engines pipeline answers but offer no delay *guarantees*.

## 4. Upper Bound

For **free-connex acyclic** self-join-free CQs: $O(N)$ preprocessing and **$O(1)$ delay** enumeration, no duplicates, in the RAM model (Bagan–Durand–Grandjean). For **acyclic but non-free-connex** or projected CQs, the best is a preprocessing/delay trade-off, e.g., factorized representations giving delay polylog in the factorized size. For **cyclic** CQs: $\tilde O(N^{\mathrm{subw}(Q)})$ preprocessing then constant/polylog delay (combining PANDA-style decomposition with constant-delay enumeration over the resulting acyclic structure). For **ranked** enumeration: $\tilde O(N)$ preprocessing, $O(\log k)$ delay to emit the $k$-th best answer (any-$k$). **Dynamic**: $q$-hierarchical CQs admit $O(1)$ update and $O(1)$ delay (Berkholz et al.).

## 5. Lower Bound

The dichotomy's hardness side is **conditional/fine-grained**. For self-join-free acyclic non-free-connex CQs (e.g., the "path" query $\pi_{a,c}\,R(a,b)\bowtie S(b,c)$), constant-delay-after-linear-preprocessing is impossible **unless** Boolean matrix multiplication has a combinatorial $O(n^{2})$ algorithm (refuting the **combinatorial BMM conjecture**). For cyclic queries, lower bounds come from **sparse triangle detection** / the **3SUM** and **Hyperclique** hypotheses: e.g., constant-delay enumeration of triangles after linear preprocessing would contradict triangle-detection hardness. For **dynamic** enumeration, queries outside the $q$-hierarchical fragment provably cannot have $O(1)$ update + $O(1)$ delay under the **Online Matrix-Vector (OMv)** conjecture (Berkholz–Keppeler–Schweikardt). These are conditional fine-grained lower bounds, not unconditional.

## 6. The Gap

The static, self-join-free picture is **essentially closed**: the free-connex dichotomy is tight (up to the BMM/triangle hypotheses). The genuinely **open** parts: (1) **self-joins** break the dichotomy's assumptions — full characterization with self-joins is open; (2) **fine-grained delay/preprocessing trade-offs** for non-free-connex and cyclic queries (the exact Pareto frontier between preprocessing exponent and delay) are not fully tight; (3) **dynamic + ranked** simultaneously, and enumeration under aggregation/comparisons (FAQ-style), lack tight bounds; (4) bringing constant-delay enumeration to **practical engines** with real constants. So: partially solved — sharp for the core case, open at the edges and in practice.

## 7. Current Research (as of June 2026)

Directions: (1) **ranked / any-$k$ enumeration** with tighter delay and dynamic updates (Gatterbauer, Yannakakis, Riedewald groups); (2) **dynamic constant-delay** beyond $q$-hierarchical, and trade-offs between amortized update time and delay (Schweikardt, Berkholz, Keppeler); (3) **enumeration for unions of CQs, queries with negation, and aggregation** (Kröll–Pichler–Skritek; Carmeli–Kröll on UCQ enumeration); (4) **direct-access** structures (return the $i$-th answer in sorted order in polylog time) generalizing enumeration (Carmeli et al., Bringmann–Carmeli–Mengel); (5) factorized/worst-case-optimal **systems** integration. *(frontier — verify)* 2025–2026 work reportedly tightens direct-access and dynamic ranked-enumeration trade-offs and explores enumeration under degree/FD constraints (PANDA-aware preprocessing). Groups: Schweikardt (HU Berlin), Carmeli/Kimelfeld (Technion), Olteanu (Zurich), Gatterbauer (Northeastern), Yannakakis.

## 8. Future Work

- Complete dichotomies *with self-joins* and for UCQs/queries with negation and aggregation.
- Tight Pareto frontiers between preprocessing exponent and delay for non-free-connex and cyclic CQs.
- Unified **dynamic + ranked + direct-access** enumeration with provable bounds.
- Degree/FD-aware (PANDA-style) preprocessing that lowers the preprocessing exponent below $\mathrm{subw}$ under constraints.
- Practical constant-delay operators inside vectorized engines, with measured (not just asymptotic) delay.

## 9. Key References

- **[Foundational]** Bagan, Durand, Grandjean. *On Acyclic Conjunctive Queries and Constant Delay Enumeration.* CSL 2007.
- **[Foundational]** Segoufin. *Enumerating with Constant Delay the Answers to a Query.* ICDT 2013 (survey of the model).
- **[SOTA]** Berkholz, Keppeler, Schweikardt. *Answering Conjunctive Queries under Updates.* PODS 2017 ($q$-hierarchical / OMv lower bound).
- **[SOTA]** Tziavelis, Ajwani, Gatterbauer, Riedewald, Yannakakis. *Optimal Algorithms for Ranked Enumeration of Answers to Full Conjunctive Queries (any-$k$).* VLDB 2020.
- **[SOTA]** Carmeli, Zeevi, Berkholz, Kimelfeld, Schweikardt. *Answering (Unions of) Conjunctive Queries using Random Access and Random-Order Enumeration.* PODS 2020 / ACM TODS 2022 (direct access).
- **[Survey]** Schweikardt, Segoufin, Vigny. *Enumeration for FO Queries over Nowhere Dense Graphs / enumeration surveys.* PODS, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
