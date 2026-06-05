# Distinct-Value (NDV) Estimation Across Joins

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/ndv-estimation-joins` · **Status:** open

## 1. Problem Statement

Given a relational query, estimate the number of distinct values (NDV, a.k.a. domain cardinality $D$) of an attribute or attribute set in the *output* of joins, projections, and `GROUP BY` clauses. Three flavors arise:

- **Counting variant:** compute $D = |\pi_A(R)|$ exactly. Trivial with a hash set, but prohibitive at scale and impossible from a sample.
- **Estimation variant:** given a sample (or per-base-table sketches/statistics), estimate $D$ for derived expressions such as $\pi_A(R \bowtie S)$ or the number of groups produced by `GROUP BY A,B`.
- **Composition variant:** propagate NDV through a plan: given NDV of inputs and join selectivity, predict NDV of outputs.

NDV estimation feeds (i) `GROUP BY` and `DISTINCT` cardinality, (ii) join-size estimation via the containment/uniformity assumptions, and (iii) memory sizing for hash aggregation. Errors compound multiplicatively up a plan, so NDV is a foundational sub-problem of cardinality estimation.

## 2. Mathematical Foundations

Let attribute $A$ over relation $R$ with $n = |R|$ rows have $D$ distinct values with multiplicities $f_1,\dots,f_D$, so $\sum_i f_i = n$. The **frequency moments** $F_k = \sum_i f_i^k$ give $F_0 = D$, $F_1 = n$. From a uniform sample of size $r$ that observes $d$ distinct values with $d_1$ singletons (values seen once), classical estimators include Goodman's unbiased estimator and the **Chao–Lee / GEE** family. A central negative result:

> **Theorem (Charikar–Chaudhuri–Motwani–Narasayya, PODS 2000).** Any (possibly randomized) estimator of $D$ from a uniform sample of size $r$ has worst-case multiplicative ratio error $\Omega(\sqrt{n/r})$ with constant probability.

So *sampling alone cannot give tight NDV* without near-full scans. Streaming changes the picture: $F_0$ admits an $(\varepsilon,\delta)$ approximation in $O(\varepsilon^{-2}\log n + \log m)$ space (**Kane–Nelson–Woodruff**, optimal). For joins, NDV interacts with the **AGM bound** $|R\bowtie S|\le \prod_e |R_e|^{x_e}$ and with the standard textbook propagation rule for a key/foreign-key join $R \bowtie_A S$: $\mathrm{NDV}_B(\text{out}) \approx \mathrm{NDV}_B(S)\cdot\big(1-(1-1/\mathrm{NDV}_B(S))^{n_{out}/n_S}\big)$ (the "Yao/bucket" formula), which assumes value independence — the main source of error.

## 3. State of the Art (SOTA)

- **Theory-SOTA (streaming):** KMV / HyperLogLog sketches give mergeable, near-optimal $F_0$ estimates per column; HLL (Flajolet et al. 2007) is ubiquitous in systems.
- **Systems-SOTA:** Most optimizers (PostgreSQL, Oracle, SQL Server) keep per-column NDV via HLL or sampling, then apply uniformity + containment propagation. Multi-column NDV is captured by *extended/column-group statistics* (Oracle, SQL Server "auto-create stats", PostgreSQL `CREATE STATISTICS ... (ndistinct)` since v10).
- **Sketch-composition for joins:** "Distinct sampling" (Gibbons VLDB 2001) and recent **join-NDV via correlated sketches / Bloom-filter intersections** improve over independence. *(frontier — verify)* learned and sketch-hybrid NDV propagation is an active systems thread.

## 4. Upper Bound

- **Single-column $F_0$:** $(1\pm\varepsilon)$ approximation in $O(\varepsilon^{-2}+\log m)$ bits, one streaming pass (Kane–Nelson–Woodruff, PODS 2010) — optimal.
- **Mergeable estimate (for joins/unions):** HLL gives relative standard error $1.04/\sqrt{m}$ with $m$ registers in $O(m\log\log n)$ bits, and registers compose under union; intersection NDV is recovered via inclusion–exclusion or MinHash Jaccard.
- **From samples:** Chao–Lee/GEE achieve the $\Theta(\sqrt{n/r})$ bound — provably the best possible ratio from a size-$r$ sample.

## 5. Lower Bound

- **Sampling:** $\Omega(\sqrt{n/r})$ multiplicative error (CCMN 2000) — information-theoretic; no estimator escapes it.
- **Streaming exact:** computing $F_0$ exactly or deterministically within $1\pm\varepsilon$ requires $\Omega(n)$ space (Alon–Matias–Szegedy 1996); the $\varepsilon^{-2}$ dependence is tight (Indyk–Woodruff / Woodruff lower bounds).
- **Join NDV:** estimating $|\pi_A(R\bowtie S)|$ from independent per-table sketches is provably impossible to bound tightly in general — intersection cardinality has communication-complexity lower bounds ($\Omega(m)$ for set-disjointness-style hardness), so cross-table correlations cannot be reconstructed from marginal sketches.

## 6. The Gap

For a *single column* in streaming, the gap is **closed** ($\Theta(\varepsilon^{-2})$). For *derived NDV across joins/group-by under sampling*, the gap is wide and **genuinely open**: the $\sqrt{n/r}$ barrier kills pure sampling, while sketch composition is tight only for unions, not for join outputs where value correlation dominates. Closing it requires either (a) richer joint sketches (multi-column MinHash, correlated KMV) with provable join-NDV guarantees, or (b) hardness results showing per-table statistics are fundamentally insufficient.

## 7. Current Research (as of June 2026)

- Sketch algebra for joins: composing KMV/Theta sketches through joins with error bounds (Apache DataSketches community; Cormode and collaborators).
- Learned NDV: neural and deep-set estimators for group counts in `GROUP BY`, e.g. extensions of cardinality models to the $F_0$ target *(frontier — verify)*.
- Hybrid sketch+sample estimators that beat $\sqrt{n/r}$ by mixing a small exact sketch with a sample (the "stable distinct" line).
- Multi-column NDV maintenance under updates and its interaction with PostgreSQL/SQL Server extended statistics.

## 8. Future Work

- Provable join-output NDV bounds from compact, mergeable, *multi-attribute* sketches.
- Tight propagation rules that replace the uniformity assumption with measured skew (frequency-moment-aware composition).
- Differentially private NDV that remains usable by an optimizer.
- Online NDV with bounded memory under arbitrary update streams and deletions (turnstile $F_0$).

## 9. Key References

- **[Foundational]** Charikar, Chaudhuri, Motwani, Narasayya. *Towards Estimating the Number of Distinct Values of an Attribute.* PODS / VLDB, 2000. — [DBLP](https://dblp.org/rec/conf/pods/CharikarCMN00.html)
- **[Foundational]** Alon, Matias, Szegedy. *The Space Complexity of Approximating the Frequency Moments.* STOC, 1996. — [DOI](https://doi.org/10.1145/237814.237823)
- **[SOTA]** Kane, Nelson, Woodruff. *An Optimal Algorithm for the Distinct Elements Problem.* PODS, 2010. — [DOI](https://doi.org/10.1145/1807085.1807094)
- **[SOTA]** Flajolet, Fusy, Gandouet, Meunier. *HyperLogLog: the Analysis of a Near-Optimal Cardinality Estimation Algorithm.* AofA, 2007. — [HAL](https://hal.science/hal-00406166)
- **[SOTA]** Gibbons. *Distinct Sampling for Highly-Accurate Answers to Distinct Values Queries and Event Reports.* VLDB, 2001. — [DBLP](https://dblp.org/rec/conf/vldb/Gibbons01.html)
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

A column $A$ has $n=10^6$ rows. Two distributions share the *same sample* of size $r=100$ in which all $100$ rows are distinct ($d=100$, all singletons):

- **Distribution X:** every value in $A$ is unique, so $D=10^6$.
- **Distribution Y:** there are only $D=10^4$ distinct values, but they are skewed so a size-$100$ sample happens to draw $100$ distinct singletons.

From this sample the two cases are *indistinguishable*, yet the truths differ by $100\times$. This is the CCMN barrier in action: the ratio error scales as
$$\sqrt{n/r}=\sqrt{10^6/100}=\sqrt{10^4}=100,$$
so no sample-based estimator can pin $D$ to better than a $\sim100\times$ multiplicative factor here.

**Contrast — streaming sketch.** HyperLogLog with $m=1024$ registers reads all $10^6$ rows in one pass and gives relative standard error $1.04/\sqrt{m}=1.04/32\approx3.3\%$ — independent of $n$, using $\sim1.5$ KB. **Composition limit:** if $R.A$ and $S.A$ each have an HLL sketch, union NDV $|\pi_A(R)\cup\pi_A(S)|$ merges exactly by register-wise max, but the *join-output* NDV $|\pi_A(R\bowtie S)|$ cannot be recovered from the two marginal sketches — that requires cross-table value correlation, the genuinely open case.

---
*Part of the [DBMS Research catalog](../../README.md).*
