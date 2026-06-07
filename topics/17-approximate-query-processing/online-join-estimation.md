---
id: 17-approximate-query-processing/online-join-estimation
title: "Ripple-Join and Online Join Estimation"
topic: 17-approximate-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Ripple-Join and Online Join Estimation

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/online-join-estimation` · **Status:** partially-solved

## 1. Problem Statement
Extend online aggregation from a single relation to **joins**: given a query such as `SELECT AVG(f) FROM R ⋈ S ⋈ T WHERE p`, produce a continuously refined estimate of the aggregate over the join result, with a **valid running confidence interval**, using a **non-blocking, memory-bounded** execution that never materializes the full join. The estimator must be **unbiased** (or provably consistent) and the CI must remain valid at every interim point the user inspects.

Variants:
- **Two-table vs. multi-way (chain / star / arbitrary acyclic):** difficulty grows with the number of relations and the join graph topology.
- **Memory-bounded variant:** when sampled tuples exceed RAM, the estimator must degrade gracefully (the "flushing" problem of ripple join).
- **Estimation target:** `SUM`/`AVG`/`COUNT` over the join, or the join *cardinality* itself.

The crux: a uniform sample of $R$ and a uniform sample of $S$ does **not** give a uniform sample of $R\bowtie S$ — join-output tuples are weighted by join multiplicity, so naive sampling is biased and high-variance.

## 2. Mathematical Foundations
Let $R\bowtie S$ on key $A$. For a value $a$ with $r_a=|\sigma_{A=a}R|$ and $s_a=|\sigma_{A=a}S|$, the join contributes $r_a s_a$ tuples. The **ripple join** estimator draws growing prefixes of $R$ and $S$ and forms the cross-product of the sampled corner, giving the unbiased estimator
$$\hat\mu = \frac{|R|\,|S|}{|S_R|\,|S_S|}\sum_{(i,j)\in \text{sampled}} \mathbb{1}[\text{join}]\cdot f(i,j),$$
with variance derived from a **finite-population two-stage (ratio) sampling** analysis (Haas–Hellerstein 1999). Key facts:
- Join-output variance depends on the **second moment** $\sum_a r_a^2 s_a^2$ / skew of $r_a,s_a$ — high-degree (heavy-hitter) keys dominate variance.
- The **AGM bound** $|R\bowtie S \bowtie\cdots| \le \prod \|R_e\|$ (Atserias–Grohe–Marx) bounds worst-case output and underlies worst-case-optimal sampling effort.
- Multi-way: variance compounds; *index-assisted* ripple join (using an index on the inner) reduces it, but maintaining unbiasedness across $\ge 3$ tables and bounded memory is delicate.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** unbiased estimators with closed-form variance for 2-table ripple join (Haas–Hellerstein); CLT-based and large-deviation CIs for the ripple estimator. **Wander Join** (random-walk sampling along join paths, Li–Wu–Yu–Nakayama, SIGMOD 2016) gives lower-variance, index-assisted estimates for chain/acyclic joins and is the de-facto theory+systems baseline for multi-way online join estimation.
- **Systems-SOTA:** **DBO / Turbo-DBO** (Jermaine, Arumugam, Pol, Dobra) extended OLA to multi-table with disk-based, memory-bounded execution and running CIs; **XDB** integrated Wander Join into PostgreSQL; sampling operators ship in research forks of Spark/Quickr. Production engines still lack first-class online-join CIs.

## 4. Upper Bound
- 2-table ripple join: unbiased estimate with half-width $O(\sigma_J n^{-1/2})$ where $\sigma_J$ is the join-output standard deviation and $n$ the number of sampled pairs; *index/hash ripple* lowers the constant by avoiding wasted non-matching pairs.
- Multi-way acyclic (Wander Join): unbiased estimator; per-walk cost bounded by path length, variance controllable via index-guided trial sampling; for **acyclic** joins the sampling cost is tied to the **AGM / fractional-edge-cover** bound on output size.
- Worst-case-optimal join sampling: sampling a uniform join tuple in expected time $\tilde O(\text{AGM}/\text{OUT})$ for acyclic and bounded-fractional-cover queries (Chen–Yi and successors).

## 5. Lower Bound
- **Variance / sample-complexity:** estimating join `COUNT` to relative error $\varepsilon$ requires $\Omega(\text{AGM}/(\varepsilon^2\,\text{OUT}))$ samples in the worst case — heavy-hitter keys force large samples (information-theoretic, via the second-moment argument).
- **Communication complexity:** in the multi-party / streaming model, estimating join size has $\Omega(\sqrt N)$-type lower bounds (set-disjointness reductions; Alon–Matias–Szegedy frequency-moment hardness for $F_2$/join-size).
- **Conditional hardness:** exact and near-exact join-size computation inherits **fine-grained** lower bounds; for cyclic joins, beating AGM-based sampling cost would contradict known worst-case-optimal join lower bounds.

## 6. The Gap
The 2-table case is **essentially closed** (matching unbiased upper bound and second-moment lower bound). For **multi-way** joins the gap is **open in practice**: Wander Join and worst-case-optimal samplers give strong bounds for *acyclic* / bounded-fractional-cover queries, but (i) **cyclic** joins, (ii) tight *running* (anytime-valid) CIs across many tables, and (iii) **memory-bounded** unbiasedness under flushing remain only partially resolved. Closing it needs sampling whose variance provably tracks the AGM/output ratio for *arbitrary* join graphs together with valid sequential CIs.

## 7. Current Research (as of June 2026)
Active directions: (1) **worst-case-optimal join sampling** — uniform/near-uniform sampling of join answers in time near the AGM bound, extended to cyclic queries via tree decompositions / fractional hypertree width *(frontier — verify)*; (2) combining Wander Join with learned indexes and degree-aware walk biasing to cut variance on skewed data; (3) anytime-valid CIs for join OLA; (4) join sampling under updates. Groups: Yi (HKUST) and collaborators on join sampling complexity, Wu (online join), Jermaine (Rice, DBO lineage), and the worst-case-optimal-join community (Ngo, Ré, Rudra).

## 8. Future Work
- Provably variance-optimal, memory-bounded online estimators for **cyclic** and arbitrary multi-way joins.
- Unified anytime-valid CIs spanning joins + `GROUP BY` + filters.
- Skew/heavy-hitter-robust sampling that adapts walk probabilities online.
- Integration with worst-case-optimal join *plans* so sampling and execution share work.

## 9. Key References
- **[Foundational]** P. J. Haas, J. M. Hellerstein. *Ripple Joins for Online Aggregation.* SIGMOD, 1999. — [DOI](https://doi.org/10.1145/304182.304208)
- **[Foundational]** N. Alon, Y. Matias, M. Szegedy. *The Space Complexity of Approximating the Frequency Moments.* STOC, 1996. — [DOI](https://doi.org/10.1145/237814.237823)
- **[SOTA]** F. Li, B. Wu, K. Yu, A. Nakayama. *Wander Join: Online Aggregation via Random Walks.* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2915235)
- **[SOTA]** C. Jermaine, S. Arumugam, A. Pol, A. Dobra. *Scalable Approximate Query Processing with the DBO Engine.* SIGMOD, 2007 / TODS, 2008. — [DOI](https://doi.org/10.1145/1412331.1412335)
- **[SOTA]** Y. Chen, K. Yi. *Random Sampling and Size Estimation Over Cyclic Joins.* ICDT, 2020. — [DOI](https://doi.org/10.4230/LIPIcs.ICDT.2020.7)
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins (AGM bound).* FOCS, 2008 / SIAM J. Computing, 2013. — [DOI](https://doi.org/10.1137/110859440)
- **[Survey]** G. Cormode, M. Garofalakis, P. Haas, C. Jermaine. *Synopses for Massive Data.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

Let $R(A)$ and $S(A)$ join on $A$. Take $|R| = |S| = 100$. Key value $a_1$ appears $r_{a_1} = 90$ times in $R$ and $s_{a_1} = 90$ in $S$; key $a_2$ appears $r_{a_2} = 10$, $s_{a_2} = 10$. The true join size is
$$|R \bowtie S| = 90\cdot 90 + 10\cdot 10 = 8{,}100 + 100 = 8{,}200.$$

Estimate it by sampling one tuple from each side and forming the ripple corner. A uniform pair $(t_R, t_S)$ matches iff both share a key; $\Pr[\text{both } a_1] = 0.9 \times 0.9 = 0.81$, $\Pr[\text{both } a_2] = 0.1\times 0.1 = 0.01$, so match probability $= 0.82$. The HT estimator scales an indicator by $|R||S| = 10{,}000$:
$$\hat C = 10{,}000 \cdot \mathbb{1}[\text{match}], \quad \mathbb{E}[\hat C] = 10{,}000 \times 0.82 = 8{,}200. \checkmark$$

Notice the variance is dominated by the heavy key $a_1$: a single sampled $a_1$-pair contributes $10{,}000$ to the estimate, mirroring the second-moment term $\sum_a r_a^2 s_a^2 = 90^2 90^2 + 10^2 10^2$ of Section 2 — exactly why skew inflates ripple-join variance.

---
*Part of the [DBMS Research catalog](../../README.md).*
