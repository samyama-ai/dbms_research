---
id: 15-data-integration/correlation-clustering-er
title: "Correlation Clustering for ER at Scale"
topic: 15-data-integration
status: solved-but-impractical
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Correlation Clustering for ER at Scale

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/correlation-clustering-er` · **Status:** solved-but-impractical

## 1. Problem Statement

Given a graph $G=(V,E)$ where $V$ are records and each pair carries a "$+$" (likely same entity) or "$-$" (likely different) label — optionally weighted by matcher confidence — **correlation clustering (CC)** partitions $V$ to minimize **disagreements**: the number (or weight) of $+$ edges across clusters plus $-$ edges inside clusters,
$$\min_{\text{partition }\mathcal{P}} \sum_{\substack{(u,v)\in E^+ \\ \text{sep}}} w_{uv} \;+\; \sum_{\substack{(u,v)\in E^- \\ \text{together}}} w_{uv}.$$
The dual MAX-AGREE objective maximizes agreements. CC is the principled, **transitivity-respecting** ER objective: it needs **no preset number of clusters** and directly tolerates inconsistent pairwise verdicts.

The problem is "solved" in approximation theory — constant-factor algorithms exist — but **impractical at billions of nodes**: classical algorithms need the full $O(n^2)$ signed graph, multiple passes, LP rounding, or sequential pivoting that resists distribution. The open *systems* problem: achieve **provable constant-factor CC in near-linear time/space, in few rounds, on $10^9$-node ER graphs**.

## 2. Mathematical Foundations

CC on **complete** signed graphs is APX-hard but constant-approximable. The **PIVOT** algorithm (Ailon–Charikar–Newman) — repeatedly pick a random pivot, form its $+$-neighborhood as a cluster — is a **3-approximation** for MIN-DISAGREE in expectation on complete graphs, and the **LP-rounding** variant gives **2.5**; recent work pushes below 2. On **general (incomplete) weighted** graphs, MIN-DISAGREE is equivalent to **MultiCut**, hence $O(\log n)$-approximable and no better unless the Unique Games Conjecture fails.

Key tools: the **LP relaxation** with triangle (metric) constraints; **region-growing / ball-cutting** for MultiCut; **probabilistic pivoting** and its derandomizations. For scale, the analysis migrates to **massively parallel computation (MPC)**, **streaming (semi-streaming, $\tilde O(n)$ space)**, and **sublinear/local** models. The CC objective is the natural Bayes-optimal ER partition when pairwise scores are log-likelihood ratios.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Ailon, Charikar, Newman, *Aggregating inconsistent information: ranking and clustering* (JACM 2008) — PIVOT 3-approx, LP 2.5. Chawla, Makarychev, Schramm, Yaroslavtsev (STOC 2015) improved weighted bounds. Cohen-Addad, Lee, Newman, et al. (FOCS 2021–2023) broke the **2-approximation barrier** for complete unweighted CC via the *cluster LP* / Sherali–Adams.
- **Scalable-SOTA.** Behnezhad, Charikar, Ma, Tan and Cohen-Addad, Lattanzi et al. give **MPC / parallel / dynamic** CC with $O(1)$-approx in $O(\log\log n)$ rounds; **single-pass semi-streaming** $O(1)$-approx (Behnezhad et al., FOCS 2022/2023). Systems: **Google's distributed CC** (Lattanzi et al., NeurIPS 2021) on graphs with billions of edges.
- **ER systems.** CC used inside **Dedoop**, **JedAI** clustering layer, and industrial MDM.

## 4. Upper Bound

For **complete unweighted** graphs: best-known approximation is now **below 2** (Cohen-Addad et al., via the cluster-LP / Sherali–Adams hierarchy, $\approx 1.43$–$1.9$ depending on the result), RAM model. PIVOT gives **3** in **linear time, one pass of randomness**, and parallelizes to $O(\log\log n)$ MPC rounds with $O(1)$-approx. **Semi-streaming** ($\tilde O(n)$ space, single pass) achieves $O(1)$-approx. For **general weighted** graphs the best is $O(\log n)$ via MultiCut LP region growing. These guarantees are on expected MIN-DISAGREE.

## 5. Lower Bound

CC MIN-DISAGREE on complete graphs is **APX-hard** (Charikar–Guruswami–Wirth): no PTAS unless P=NP, so a constant $>1$ inapproximability holds. On **general weighted** graphs it is equivalent to MultiCut, hence **$\Omega(\log n)$-hard** under the Unique Games Conjecture (no constant-factor approximation). In the **streaming** model, $\Omega(n)$ space is required for any nontrivial approximation in one pass (communication-complexity lower bounds), so semi-streaming is essentially optimal in space. Exact CC is **NP-hard**.

## 6. The Gap

The **theory is essentially closed**: complete-graph CC is APX-hard with sub-2 upper bounds nearly matching, and weighted CC is $\Theta(\log n)$ under UGC. The remaining gap is **practicality at $10^9$ scale**, not approximability: (i) constructing/storing the **signed similarity graph** is itself $O(n^2)$ absent blocking; (ii) the sub-2 algorithms rely on **LP / Sherali–Adams** rounding that does not scale; (iii) the fast PIVOT-style methods are **sequential in their pivot dependency**, and parallel versions trade approximation for rounds. Closing it means **constant-factor, few-round, near-linear-space CC integrated with blocking**, with stable (low-churn) outputs.

## 7. Current Research (as of June 2026)

- **Sublinear-round MPC and fully-dynamic CC** with worst-case $O(1)$-approx, poly-log update (Behnezhad, Cohen-Addad, Lattanzi). *(frontier — verify)*
- **Breaking 2** further on complete CC via tighter cluster-LP / local-search hybrids. *(frontier — verify)*
- ER-specific: feeding **deep/LLM matcher log-odds** as CC edge weights, then scalable weighted CC — bridging the weighted-graph $\Omega(\log n)$ barrier with **bounded-degree (blocked)** instances where better constants are provable. *(frontier — verify)*

## 8. Future Work

- Practical sub-2 algorithms that avoid LP rounding (combinatorial / local-search with certificates).
- CC that consumes blocking output directly, never materializing $O(n^2)$ edges.
- Stable/Lipschitz CC: small input change ⇒ small output change, for incremental ER.
- Tight bounds for **bounded-arboricity / blocked** signed graphs typical of real ER.

## 9. Key References

- **[Foundational]** N. Bansal, A. Blum, S. Chawla. *Correlation Clustering.* Machine Learning / FOCS, 2004. — [DOI](https://doi.org/10.1023/B:MACH.0000033116.57574.95)
- **[Foundational]** N. Ailon, M. Charikar, A. Newman. *Aggregating Inconsistent Information: Ranking and Clustering.* JACM, 2008. (PIVOT 3-approx, LP 2.5.) — [DOI](https://doi.org/10.1145/1411509.1411513)
- **[Foundational]** M. Charikar, V. Guruswami, A. Wirth. *Clustering with Qualitative Information.* JCSS / FOCS, 2005. (APX-hardness, MultiCut equivalence.) — [DOI](https://doi.org/10.1016/j.jcss.2004.10.012)
- **[SOTA]** V. Cohen-Addad, E. Lee, A. Newman, et al. *Correlation Clustering with Sherali–Adams / breaking the 2-approximation barrier.* FOCS, 2022–2023. — [arXiv](https://arxiv.org/abs/2207.10889)
- **[SOTA]** S. Lattanzi, et al. *Scalable Correlation Clustering with the PIVOT algorithm at scale.* NeurIPS, 2021. — [DBLP search](https://dblp.org/search?q=Lattanzi+scalable+correlation+clustering+pivot)
- **[SOTA]** S. Behnezhad, M. Charikar, W. Ma, L.-Y. Tan. *Single-Pass Streaming Correlation Clustering.* SODA, 2023. — [DOI](https://doi.org/10.1137/1.9781611977554.ch33)

## 10. Worked Example

Four records $\{1,2,3,4\}$ on a complete signed graph (unit weights). Matcher verdicts: $+$ on $(1,2),(2,3),(1,3),(3,4)$ and $-$ on $(1,4),(2,4)$.

Note the inconsistency: $3\!+\!4$ and $1\!+\!3$ suggest $1,3,4$ together, but $1\!-\!4$ contradicts it — no partition agrees with every edge, so we minimize disagreements.

**Candidate A** $\{1,2,3\},\{4\}$: cut $+$ edge $(3,4)$ = **1 disagreement** ($-$ edges $(1,4),(2,4)$ are correctly separated).

**Candidate B** $\{1,2,3,4\}$ all together: violates $-$ edges $(1,4),(2,4)$ = **2 disagreements**.

**Candidate C** $\{1,2\},\{3,4\}$: cuts $+$ edges $(2,3),(1,3)$ = **2 disagreements**.

So **A is optimal** with cost 1.

**PIVOT trace.** Pick random pivot $3$; its $+$-neighborhood $\{1,2,3,4\}$? — pivot forms cluster from $3$'s $+$-edges: $\{1,2,3,4\}$ would be picked, giving cost 2. Picking pivot $1$ instead: $+$-neighbors $\{2,3\}$ → cluster $\{1,2,3\}$, leftover $\{4\}$ → cost 1. This illustrates PIVOT's randomization: expected cost is within $3\times$ optimum, but a lucky pivot hits the optimum directly.

---
*Part of the [DBMS Research catalog](../../README.md).*
