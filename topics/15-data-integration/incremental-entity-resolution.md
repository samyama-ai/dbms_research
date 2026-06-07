---
id: 15-data-integration/incremental-entity-resolution
title: "Incremental Entity Resolution Maintenance"
topic: 15-data-integration
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Incremental Entity Resolution Maintenance

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/incremental-entity-resolution` · **Status:** partially-solved

## 1. Problem Statement

Given an entity-resolution **clustering** $\mathcal{C}$ over a record set $R$ (a partition of $R$ into entities), and a stream of updates $\Delta = \langle u_1, u_2, \dots\rangle$ of types **insert**, **update** (attribute change), and **delete**, **incremental ER** maintains a clustering $\mathcal{C}_t$ that is consistent with the batch result $\textsf{ER}(R_t)$ on the current record set $R_t$, while performing **work sublinear in $|R_t|$ per update** and avoiding full recomputation.

The challenge is that ER decisions are **non-local and non-monotone**: a single inserted record can merge previously separate clusters, an attribute update can split a cluster, and a delete can remove a "bridge" record whose absence splits a cluster. The decision variant: *does update $u$ change the clustering, and if so which clusters?* The optimization variant: *minimize maintenance work / cluster churn while staying within a quality envelope of the from-scratch result.* A key formal target is **order-independence / determinism**: $\mathcal{C}_t$ should (ideally) equal $\textsf{ER}(R_t)$ regardless of update order.

## 2. Mathematical Foundations

Model ER as maintaining the **connected components / correlation-clustering optimum** of a similarity graph $G_t=(R_t,E_t)$ whose edges are match decisions. For **threshold/transitive-closure ER**, $\mathcal{C}_t$ = connected components of $G_t$; inserts add edges (incremental connectivity), deletes remove edges (decremental connectivity — provably harder).

Foundational guarantees come from Benjelloun et al.'s **ICAR properties** — *Idempotence, Commutativity, Associativity, Representativity* of the match/merge functions — which make ER a confluent rewriting system and license incremental, order-independent maintenance. For **clustering-based** ER (correlation clustering objective $\min \sum_{\text{disagreements}}$), incremental maintenance is a **dynamic graph clustering** problem; bounds borrow from **dynamic connectivity** (Holm–de Lichtenberg–Thorup, $O(\log^2 n)$ amortized for fully-dynamic connectivity) and **dynamic minimum-cut / clustering** lower bounds (OMv-conditional). Merges/splits propagate through transitive closure, whose **fully dynamic maintenance** is subject to known hardness.

## 3. State of the Art (SOTA)

- **Foundational model.** Benjelloun, Garcia-Molina, Menestrina, Su, Whang, Widom — *Swoosh: a generic approach to entity resolution* (VLDBJ 2009) defines ICAR and generic/incremental merge.
- **Incremental algorithms.** Whang, Garcia-Molina, *Incremental Entity Resolution on Rules and Data* (VLDBJ 2014) handle rule/data evolution. Gruenheid, Dong, Srivastava, *Incremental Record Linkage* (VLDB 2014) maintain a clustering under inserts/updates/deletes with greedy/connected-component and correlation-clustering repair.
- **Systems.** Streaming/online ER in **JedAI**, **Dedupe** (incremental active learning), Oracle/Informatica MDM incremental match-merge; **ZeroER**, **DITTO** matchers retrofitted into incremental loops.

## 4. Upper Bound

Under **ICAR** match/merge, incremental insertion is handled by **incremental transitive closure / union-find**, giving near-constant amortized work per match edge and **provable order-independence** (the maintained result equals batch ER). For correlation-clustering-style ER, Gruenheid et al. give **localized repair** touching only clusters in the neighborhood of an update, with empirical sublinear cost; fully-dynamic connectivity supports inserts and deletes in $O(\log^2 n)$ amortized (RAM model) for the transitive-closure variant. With blocking, each update touches only its block(s), bounding work by block size.

## 5. Lower Bound

**Deletes are the hard case.** Maintaining the clustering under edge deletions reduces to **fully dynamic / decremental connectivity and transitive closure**, for which **OMv-conditional lower bounds** rule out $O(n^{1-\epsilon})$ worst-case update time for general graphs (Henzinger–Krinninger–Nanongkai–Saranurak, STOC 2015). Maintaining the **correlation-clustering optimum** dynamically is at least as hard as its static NP-hard objective, so exact maintenance is NP-hard; approximate dynamic maintenance inherits OMv-style barriers. Order-independence can be **impossible** to preserve cheaply when merge functions violate ICAR (associativity failures force recomputation).

## 6. The Gap

For ICAR/insert-only workloads the problem is essentially **solved** (cheap, order-independent). The genuine gap is the **fully-dynamic regime with deletes and attribute updates**: there is a wide span between near-constant insert maintenance and the $\Omega(n^{1-\epsilon})$ OMv barrier for general deletes, and **no tight characterization** of which similarity-graph structures (bounded degree, blocked, bounded cluster diameter) admit truly sublinear fully-dynamic maintenance with quality guarantees. Quantifying the **quality vs. work** trade-off (how far maintained $\mathcal{C}_t$ may drift from batch) is open.

## 7. Current Research (as of June 2026)

- **Fully-dynamic correlation clustering** with poly-log update time and $O(1)$-approximation (Cohen-Addad, Lattanzi, et al.) being transferred to ER pipelines. *(frontier — verify)*
- Streaming ER with **learned/embedding-based blocking** maintained incrementally (HNSW/ANN index updates) so neighbor candidate sets stay fresh under updates. *(frontier — verify)*
- Incremental ER under **LLM matchers**, caching past match verdicts to avoid re-querying on each delta. *(frontier — verify)*

## 8. Future Work

- Tight sublinear bounds for fully-dynamic ER on **blocked / bounded-degree** similarity graphs.
- Principled **split detection** on deletes without full cluster recomputation.
- Confluent semantics for non-ICAR (learned) matchers; bounded-drift approximate maintenance.
- Provenance-aware incremental ER enabling explanations of why a record's cluster changed.

## 9. Key References

- **[Foundational]** O. Benjelloun, H. Garcia-Molina, D. Menestrina, Q. Su, S. E. Whang, J. Widom. *Swoosh: a generic approach to entity resolution.* VLDB Journal, 2009. — [DOI](https://doi.org/10.1007/s00778-008-0098-x)
- **[SOTA]** A. Gruenheid, X. L. Dong, D. Srivastava. *Incremental Record Linkage.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2732939.2732943)
- **[SOTA]** S. E. Whang, H. Garcia-Molina. *Incremental Entity Resolution on Rules and Data.* VLDB Journal, 2014. — [DOI](https://doi.org/10.1007/s00778-013-0315-0)
- **[Foundational]** J. Holm, K. de Lichtenberg, M. Thorup. *Poly-logarithmic deterministic fully-dynamic algorithms for connectivity, minimum spanning tree, 2-edge, and biconnectivity.* JACM, 2001. — [DOI](https://doi.org/10.1145/502090.502095)
- **[Foundational]** M. Henzinger, S. Krinninger, D. Nanongkai, T. Saranurak. *Unifying and strengthening hardness for dynamic problems via the online matrix-vector multiplication conjecture.* STOC, 2015. — [arXiv](https://arxiv.org/abs/1511.06773)
- **[Survey]** G. Papadakis, E. Ioannou, E. Thanos, T. Palpanas. *The Four Generations of Entity Resolution.* Morgan & Claypool, 2021. — [Semantic Scholar](https://www.semanticscholar.org/paper/The-Four-Generations-of-Entity-Resolution-Papadakis-Ioannou/61c1dd89dd999eb6056a8b2bec595425d92d7b99)

## 10. Worked Example

Records $r_1,\dots,r_5$, threshold-ER on similarity edges $E=\{(r_1,r_2),(r_2,r_3),(r_4,r_5)\}$. Connected components give clusters $\{r_1,r_2,r_3\}$ and $\{r_4,r_5\}$.

**Insert** $r_6$ matching $r_3$ and $r_4$: add edges $(r_3,r_6),(r_4,r_6)$. Union-find merges the two components into one cluster $\{r_1,\dots,r_6\}$ — $r_6$ is a *bridge*. Insert cost is near-$O(\alpha(n))$ amortized; order-independent under ICAR.

**Delete** $r_6$: now remove its edges. Is the giant cluster still connected? We must recheck connectivity between $\{r_1,r_2,r_3\}$ and $\{r_4,r_5\}$. With no other path, the cluster **splits** back into two. This is decremental connectivity — Holm–de Lichtenberg–Thorup gives $O(\log^2 n)$ amortized, but adversarial deletes hit the OMv barrier $\Omega(n^{1-\epsilon})$.

Lesson: the insert touched 1 union; the delete required a connectivity re-test across the whole component — the asymmetry that makes deletes the hard case.

---
*Part of the [DBMS Research catalog](../../README.md).*
