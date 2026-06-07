---
id: 26-cardinality-estimation/anti-join-selectivity
title: "Negative & Anti-Join Selectivity"
topic: 26-cardinality-estimation
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Negative & Anti-Join Selectivity

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/anti-join-selectivity` · **Status:** open

## 1. Problem Statement

Estimate the output cardinality of **negative** relational operations:
- **Anti-join** $R \triangleright S$ (`NOT EXISTS` / `NOT IN`): tuples of $R$ with **no** matching tuple in $S$.
- **Set difference** $R \setminus S$ and negated predicates $\sigma_{\neg p}(R)$.
- Correlated `NOT EXISTS` subqueries.

These are systematically mis-estimated because the result depends on the **absence** of matches, which is governed by the *distinct values present in $S$* and their overlap with $R$ — information that semi-join / positive-join estimators do not capture. Naively, $|R \triangleright S| = |R| - |R \ltimes S|$ (semi-join), so error in the semi-join estimate is *inherited and often amplified* (it appears as a difference of two large, correlated quantities).

Variants: **estimation** (approximate count), **decision** (is the anti-join empty? i.e., does $R \subseteq \pi(S)$?), and the **bounding** variant (provable upper/lower envelopes for safe planning).

## 2. Mathematical Foundations

Let $D_R, D_S$ be the sets of distinct join-key values in $R, S$. Then
$$|R \triangleright S| = \sum_{v \in D_R \setminus D_S} \mathrm{freq}_R(v),$$
i.e. the result is driven by keys present in $R$ but **absent** from $S$. This makes anti-join estimation fundamentally a problem about the **set difference of active domains** and the **frequency distribution over the non-matching keys** — not just cardinalities. The relevant primitive is estimating $|D_R \setminus D_S|$ and the mass on it.

Foundations:
- **Distinct-value / containment** estimation; the classic optimizer heuristic assumes containment ($D_R \subseteq D_S$ or $D_S \subseteq D_R$), which makes the anti-join estimate collapse to extremes.
- **KMV / HyperLogLog** sketches estimate $|D_R \cup D_S|, |D_R \cap D_S|$ (hence $|D_R \setminus D_S|$) via mergeability and inclusion–exclusion.
- **Set-difference / sparse-recovery** sketches (Invertible Bloom Lookup Tables, Eppstein–Goodrich) recover small symmetric differences exactly.
- Inclusion–exclusion ties anti-join to semi-join, inheriting its variance.

## 3. State of the Art (SOTA)

**Systems-SOTA:** Most cost-based optimizers estimate anti-joins as $|R| \cdot (1 - \text{semijoin selectivity})$ with crude distinct-value statistics and containment assumptions — a well-documented source of large errors (Leis et al., VLDB 2015, flags anti-/semi-join and complex predicates among the worst cases).

**Theory/sketch-SOTA:**
- **KMV (k-minimum-values)** and **HLL** distinct/union/intersection estimation (Beyer–Haas–Reinwald–Sismanis, SIGMOD 2007) give principled $|D_R \setminus D_S|$ estimates.
- **IBLT / set-difference sketches** (Eppstein, Goodrich, Uyeda, Varghese, SIGCOMM 2011) exactly recover small differences.
- **Learned join estimators** (NeuroCard, FactorJoin, MSCN) increasingly handle correlations but treat anti-joins weakly; few learned models are trained explicitly on negation.
- **AGM-style bounds** adapt poorly to negation (the result is a difference, not a join), so principled *bounds* for anti-joins are underdeveloped.

## 4. Upper Bound

Distinct set-difference mass: with KMV/HLL of size $O(\varepsilon^{-2})$, estimate $|D_R \setminus D_S|$ to relative error $\varepsilon$ via mergeable inclusion–exclusion; combined with per-key frequency sketches (Count-Min, $O(\varepsilon^{-2})$) this bounds the anti-join mass. IBLT recovers a symmetric difference of size $d$ exactly with $O(d)$ space and $O(d)$ time. A sample of $R$ probed against an index/sketch of $D_S$ gives an unbiased estimator of the non-matching fraction with variance $O(1/\text{sample size})$. No *distribution-free multiplicative* bound is known when the difference mass is tiny relative to $|R|$ (a needle-in-haystack regime).

## 5. Lower Bound

Estimating set difference / disjointness is communication-complexity hard: **set disjointness** requires $\Omega(n)$ communication, so deciding whether an anti-join is empty (whether $D_R \setminus D_S = \emptyset$) over distributed inputs needs $\Omega(\min(|D_R|,|D_S|))$ bits — no small sketch decides emptiness exactly. Multiplicatively estimating a **small** difference (few non-matching keys carrying small mass) is information-theoretically hard: distinguishing "0 non-matches" from "$\varepsilon$ non-matches" can require $\Omega(1/\varepsilon)$ or more samples/space, since rare keys evade sampling. Inclusion–exclusion of two large estimates yields error proportional to the *operands*, not the (small) result — an inherent variance lower bound.

## 6. The Gap

**Open.** Positive joins enjoy tight worst-case theory (AGM) and strong learned/sketch estimators; the **negative** operators have neither tight bounds nor reliable estimators, and the *difference-of-large-quantities* structure makes small results provably hard to estimate multiplicatively. The gap is widest precisely where it matters — highly selective anti-joins (almost all of $R$ matches, the result is small) — exactly the needle-in-haystack regime the lower bounds forbid solving cheaply. Closing it needs estimators that target the difference mass *directly* (sparse-recovery / set-difference sketches feeding the optimizer) with quantified error, plus a bound theory for negation analogous to AGM.

## 7. Current Research (as of June 2026)

- **Sketch-native anti-join estimation**: feeding KMV/HLL/IBLT set-difference estimates directly into optimizer cost models *(frontier — verify)*.
- **Learned estimators trained on negation**: extending autoregressive/factorized models to `NOT EXISTS` and set difference.
- **Bound frameworks for negation** analogous to AGM/SafeBound for safe anti-join planning.
- Robustness studies isolating semi/anti-join error in benchmark suites (JOB, CEB).

## 8. Future Work

- Provable multiplicative guarantees for selective anti-joins via direct difference-mass estimation.
- A worst-case output-size bound theory for negation and set difference.
- Learned models that natively represent absence/negation with consistency to their positive counterparts.
- Tight characterization of the sketch space needed for $\varepsilon$-accurate anti-join mass.

## 9. Key References

- **[Foundational]** Beyer, Haas, Reinwald, Sismanis, Gemulla. *On Synopses for Distinct-Value Estimation Under Multiset Operations (KMV).* SIGMOD, 2007. — [DOI](https://doi.org/10.1145/1247480.1247504)
- **[Foundational]** Eppstein, Goodrich, Uyeda, Varghese. *What's the Difference? Efficient Set Reconciliation Without Prior Context (IBLT).* SIGCOMM, 2011. — [DOI](https://doi.org/10.1145/2018436.2018462)
- **[Foundational]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog.* AofA, 2007. — [DOI](https://doi.org/10.46298/dmtcs.3545)
- **[Survey]** Leis, Gubichev, Mirchev, Boncz, Kemper, Neumann. *How Good Are Query Optimizers, Really?* VLDB, 2015. — [DOI](https://doi.org/10.14778/2850583.2850594), [DBLP](https://dblp.org/rec/journals/pvldb/LeisGMBK015.html)
- **[Foundational]** Kalyanasundaram, Schnitger. *The Probabilistic Communication Complexity of Set Intersection.* SIAM J. Discrete Math, 1992. — [DOI](https://doi.org/10.1137/0405044)
- **[SOTA]** Wu, Negi, Alizadeh, Kraska, Madden. *FactorJoin: A New Cardinality Estimation Framework for Join Queries.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3588721), [arXiv](https://arxiv.org/abs/2212.05526)

## 10. Worked Example

Let $R(\text{cust})$ list orders and $S(\text{cust})$ list customers with a complaint. We want `customers in R with NO complaint`: $R \triangleright S$.

| key $v$ | $\mathrm{freq}_R(v)$ | in $S$? |
|---|---|---|
| 1 | 40 | yes |
| 2 | 35 | yes |
| 3 | 3  | no  |
| 4 | 2  | no  |

So $|R| = 80$, $D_R=\{1,2,3,4\}$, $D_S=\{1,2,5,6\}$, and the answer is the mass on $D_R\setminus D_S=\{3,4\}$:
$$|R \triangleright S| = \mathrm{freq}_R(3)+\mathrm{freq}_R(4) = 3+2 = 5.$$

Now watch the **inclusion–exclusion amplification**. The semi-join $|R \ltimes S| = 40+35 = 75$, and $|R\triangleright S| = |R| - |R\ltimes S| = 80-75 = 5$. Suppose a sample-based semi-join estimate errs by just $\pm 6$ (an $8\%$ relative error on $75$): $\widehat{|R\ltimes S|}=69$. Then $\widehat{|R\triangleright S|} = 80-69 = 11$, a $120\%$ error on the true value $5$. The small result is the difference of two large, correlated quantities, so absolute error in the operand becomes relative catastrophe in the result — exactly the §5 needle-in-haystack regime.

---
*Part of the [DBMS Research catalog](../../README.md).*
