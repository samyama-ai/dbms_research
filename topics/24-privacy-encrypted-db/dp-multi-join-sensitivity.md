# Optimal DP Mechanisms for Multi-Join Queries

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/dp-multi-join-sensitivity` · **Status:** open

## 1. Problem Statement

Given a SQL counting/aggregation query $Q$ containing one or more (possibly self-) joins over a relational database $D$, release an $(\varepsilon,\delta)$-differentially private answer whose error is as small as possible. The central obstacle is **sensitivity**: a single tuple participating in a join can multiply into arbitrarily many output rows (join amplification), so global sensitivity $\Delta_{\mathrm{GS}}(Q)$ can be $\Theta(n)$ or unbounded, making naive Laplace/Gaussian noise useless.

Variants:
- **Counting variant:** answer `COUNT(*)` over a (cyclic or acyclic) join.
- **Optimization variant:** compute the noise distribution / mechanism minimizing expected error subject to a DP constraint.
- **Sensitivity-computation variant (decision/counting):** compute or approximate the *local* sensitivity $\mathrm{LS}_Q(D)$, the *smooth* sensitivity $S^*_{Q,\beta}(D)$, or the *downward/elastic/residual* sensitivity at $D$. Deciding tight local sensitivity for multi-join queries is itself computationally hard.

Self-joins (e.g., triangle/path counting) are the canonical hard case because one tuple appears in multiple join positions.

## 2. Mathematical Foundations

DP: $M$ is $(\varepsilon,\delta)$-DP if for neighbors $D\sim D'$ and all $S$, $\Pr[M(D)\in S]\le e^{\varepsilon}\Pr[M(D')\in S]+\delta$. **Neighboring** is typically *tuple add/remove* (unbounded DP) at the granularity of one base-relation row.

Global sensitivity $\Delta_{\mathrm{GS}}(Q)=\max_{D\sim D'}\lvert Q(D)-Q(D')\rvert$. Local sensitivity $\mathrm{LS}_Q(D)=\max_{D'\sim D}\lvert Q(D)-Q(D')\rvert$. Nissim–Raskhodnikova–Smith smooth sensitivity $S^*_{Q,\beta}(D)=\max_{k}e^{-k\beta}\max_{D'':d(D,D'')\le k}\mathrm{LS}_Q(D'')$ gives a noise-calibration upper envelope usable with the Cauchy/Laplace add-noise framework.

For a join query, output multiplicity is governed by **degrees**: the change from adding a tuple $t$ to relation $R_i$ is bounded by the number of completions of $t$ in $Q$, related to the **AGM bound** $|Q|\le \prod_e |R_e|^{x_e}$ over a fractional edge cover $\{x_e\}$. **Residual sensitivity** (Dong–Yi) bounds the effect via residual queries over witness subsets; **elastic sensitivity** (Johnson–Near–Song) upper-bounds local sensitivity using max-frequency metrics on join keys. Truncation/Lipschitz-extension mechanisms (restricting per-entity degree to $\tau$) trade bias for bounded sensitivity.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** *Residual sensitivity* (Dong, Fang, Yi, ICDE/PODS 2021–2023) gives the tightest known polynomially-computable smooth upper bound on local sensitivity for full acyclic and self-join-free conjunctive queries, dominating elastic sensitivity. For self-joins, Dong–Yi extend with worst-case-optimal-join-style accounting.
- **Systems-SOTA:** **Flex/elastic sensitivity** (Uber, VLDB 2018) shipped DP for general SQL; **PrivateSQL** (Kotsogiannis et al., VLDB 2019) handles multi-relation schemas with a privacy "view"; **R2T** (Dong, Yi et al., SIGMOD 2022) uses Lipschitz extensions + LP relaxation for near-instance-optimal join aggregation.

## 4. Upper Bound

For self-join-free acyclic conjunctive counting queries, residual-sensitivity + smooth-noise yields error $\tilde{O}(\mathrm{LS}_Q(D)\cdot \mathrm{poly}(1/\varepsilon))$ with $\mathrm{LS}$ approximated within a query-dependent constant; computation is polynomial in $|D|$. **R2T** achieves error within an $O(\log n)$ factor of the *instance-optimal* truncation mechanism for Sum-over-joins under add/remove neighbors. Sensitivity itself is poly-time approximable for these classes.

## 5. Lower Bound

Computing exact local sensitivity for general (cyclic / self-join) conjunctive queries is **NP-hard** (reduces from subgraph counting / clique). Information-theoretically, instance-optimal error for join counts is $\Omega(\mathrm{DS}_Q(D))$ (downward local sensitivity); no mechanism beats the smooth-sensitivity envelope by more than constants for self-join-free CQs. For triangle counting in graphs (a 3-way self-join), $(\varepsilon,0)$-DP error is $\Omega(n)$ in the worst case and $\Omega(\sqrt{n})$-type bounds arise from packing arguments; matching tightness for general cyclic queries is open.

## 6. The Gap

For **self-join-free acyclic** queries the gap is essentially **closed** (constant/log factors). The genuinely **open** region is **self-joins and cyclic joins**: no poly-time mechanism is known to be instance-optimal, and the hardness of computing tight sensitivity (vs. usable upper bounds) leaves a multiplicative gap that can be polynomial in $n$. Closing it requires either a worst-case-optimal-join-aware noise calibration with provable instance-optimality, or a hardness result ruling it out.

## 7. Current Research (as of June 2026)

- Worst-case-optimal-join + DP unification: calibrating noise to fractional-cover degree sequences for cyclic queries *(frontier — verify)*.
- Per-query *individual/personalized* sensitivity and "sensitivity sampling" to dodge worst-case degree blowup (Yi, Dong; HKUST). 
- DP for joins under the **shuffle model** and within DP-SQL engines (Tumult Analytics, Google's PipelineDP / differential-privacy library) extending to multi-table pipelines *(frontier — verify)*.

## 8. Future Work

- Instance-optimal mechanisms for self-joins (triangles, paths) with provable guarantees.
- Tight smooth sensitivity for cyclic CQs via AGM/polymatroid bounds.
- Sensitivity that respects FK constraints (see companion problem) rather than treating all tuples as independent.
- Practical noise-vs-bias optimization for truncation thresholds $\tau$ under composition.

## 9. Key References

- **[Foundational]** Nissim, Raskhodnikova, Smith. *Smooth Sensitivity and Sampling in Private Data Analysis.* STOC, 2007.
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008 (AGM bound).
- **[SOTA]** Johnson, Near, Song. *Towards Practical Differential Privacy for SQL Queries (Elastic Sensitivity / Flex).* VLDB, 2018.
- **[SOTA]** Dong, Fang, Yi. *Residual Sensitivity for Differentially Private Multi-Way Joins.* SIGMOD/PODS, 2021.
- **[SOTA]** Dong, Yi, et al. *R2T: Instance-optimal Truncation for Differentially Private Query Evaluation with Foreign Keys.* SIGMOD, 2022.
- **[Survey]** Kotsogiannis et al. *PrivateSQL: A Differentially Private SQL Query Engine.* VLDB, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
