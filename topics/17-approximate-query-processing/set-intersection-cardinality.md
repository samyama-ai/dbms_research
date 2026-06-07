---
id: 17-approximate-query-processing/set-intersection-cardinality
title: "Set-Intersection Cardinality Estimation"
topic: 17-approximate-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Set-Intersection Cardinality Estimation

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/set-intersection-cardinality` · **Status:** partially-solved

## 1. Problem Statement
Given per-set summaries built independently for sets $A_1,\dots,A_r$ over a universe $\mathcal{U}$, estimate the cardinality of their intersection $|A_1\cap\cdots\cap A_r|$ (or, for $r=2$, the join-key overlap $|A\cap B|$ that drives join-size and selectivity estimation). The summaries must be small (sublinear), built without coordination beyond a shared hash function, and yield an estimator with **provable relative-error** $\hat I=(1\pm\varepsilon)\,|A\cap B|$.

Variants:
- **Counting variant:** output $\widehat{|A\cap B|}$ with bounded relative error.
- **Decision variant:** is $|A\cap B|\ge \tau$? (disjointness when $\tau=1$).
- **Multi-way variant:** $r$-fold intersection, central to multi-join cardinality estimation.

The fundamental tension: HLL-style sketches force inclusion–exclusion ($|A\cap B|=|A|+|B|-|A\cup B|$), whose error scales with the *union* size, so relative error explodes when the intersection is small. Coordinated samples (minhash/KMV/Theta) instead estimate the Jaccard index directly and convert it to an intersection size — provably better in the small-overlap regime but still error-amplified as overlap $\to 0$.

## 2. Mathematical Foundations
With a shared hash $h:\mathcal{U}\to[0,1]$ and bottom-$k$ samples $K_A,K_B$ (the $k$ smallest hashes), the **bottom-$k$ estimator** computes over the $k$ smallest values of $A\cup B$ the fraction $\hat J$ that lie in both, an unbiased estimator of Jaccard $J=\tfrac{|A\cap B|}{|A\cup B|}$, with $\widehat{|A\cap B|}=\hat J\cdot\widehat{|A\cup B|}$. The variance is $\mathrm{Var}(\hat J)\approx J(1-J)/k$, so the **relative** error on the intersection is $\Theta\!\big(\tfrac{1}{\sqrt{k}}\cdot\sqrt{\tfrac{|A\cup B|}{|A\cap B|}}\big)$ — bounded only when overlap is not vanishing.

**MinHash** (Broder, 1997) is the $k=1$/$k$-permutation special case underpinning LSH. **AKMV** (Beyer et al., SIGMOD 2007) augments KMV with multiplicities for unbiased compound set operations. **Theta sketches** generalize the sampling threshold for variance-optimal unions and intersections (DataSketches). The hard regime is governed by communication complexity: **set-disjointness** requires $\Omega(n)$ bits, so no small independent summary decides emptiness of intersection exactly.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Cohen's coordinated/bottom-$k$ sampling estimators give unbiased, variance-bounded intersection/Jaccard estimates; tug-of-war and $\ell_2$-sampling sketches give inner-product (a proxy for weighted intersection) estimates with $\varepsilon$ relative error in $O(1/\varepsilon^2)$ space.
- **Systems-SOTA:** Apache **DataSketches Theta/Tuple** ship documented intersection estimators with error formulas; database optimizers (e.g., research prototypes and some columnar engines) use 2-set minhash overlap for **join-cardinality** estimation. Correlated/coordinated sampling underlies join-size estimators in learned-CE literature.

## 4. Upper Bound
Bottom-$k$/Theta with $k$ samples per set: $\widehat{|A\cap B|}$ unbiased with relative standard error $\approx \tfrac{1}{\sqrt k}\sqrt{1/J}$; for fixed target relative error $\varepsilon$ on intersections of Jaccard $\ge J_0$, $k=\Theta(\tfrac{1}{\varepsilon^2 J_0})$ samples suffice. Inner-product/$\ell_2$ sketches estimate weighted overlap to $\varepsilon$ relative error in $O(\tfrac1{\varepsilon^2}\log\tfrac1\delta)$ space. Multi-way $r$-intersection via shared bottom-$k$: $O(rk)$ time.

## 5. Lower Bound
**Set-disjointness** communication lower bound: deciding whether $|A\cap B|=0$ requires $\Omega(n)$ bits of communication / sketch size in the worst case (Razborov; Kalyanasundaram–Schnitger; Bar-Yossef et al.), so exact or even constant-factor intersection size from independent sublinear sketches is impossible for small overlaps. Estimating Jaccard to additive $\varepsilon$ needs $\Omega(1/\varepsilon^2)$ samples (Gap-Hamming connection). Hence **relative**-error intersection guarantees inherently depend on a lower bound on the overlap fraction.

## 6. The Gap
For non-vanishing overlap, the problem is **closed**: $\Theta(1/\varepsilon^2 J_0)$ samples are necessary and sufficient up to constants. The open gap is the **small-overlap / multi-way regime**: provable relative error when $|A\cap B|\ll |A\cup B|$ requires sketch size growing with $1/J$, and no method escapes this (it is a true information-theoretic barrier). Practical multi-join chains accumulate this error multiplicatively; tight bounds for $r$-way correlated estimation under realistic data skew remain open.

## 7. Current Research (as of June 2026)
Active directions: combining coordinated sampling with learned models for join-cardinality (CMU, MIT, TUM lineage), correlated sketches that share randomness across many columns, and *(frontier — verify)* "sketch-aware" optimizers that propagate intersection-error bounds through multi-way joins. Robustness of Jaccard/minhash estimators under adversarial/streaming updates is studied by Woodruff, Ben-Eliezer, and collaborators.

## 8. Future Work
- Provable multi-way ($r>2$) intersection estimators with error not multiplicative in $r$.
- Optimizer-grade overlap estimators robust to data skew and correlation.
- Combining coordinated sampling with learned priors to beat worst-case sample bounds on real data.

## 9. Key References
- **[Foundational]** Broder, A. *On the Resemblance and Containment of Documents (MinHash).* SEQUENCES 1997. — [DOI](https://doi.org/10.1109/SEQUEN.1997.666900)
- **[Foundational]** Beyer, K., Haas, P., Reinwald, B., Sismanis, Y., Gemulla, R. *On Synopses for Distinct-Value Estimation Under Multiset Operations (AKMV).* SIGMOD 2007. — [DOI](https://doi.org/10.1145/1247480.1247504)
- **[SOTA]** Cohen, E. *Min-Hash Sketches / Coordinated Sampling.* (estimators for intersections and weighted overlap), 2014–2018. — [DOI](https://doi.org/10.1007/978-1-4939-2864-4_576)
- **[Foundational]** Bar-Yossef, Z., Jayram, T.S., Kumar, R., Sivakumar, D. *An Information Statistics Approach to Data Stream and Communication Complexity (Set-Disjointness).* JCSS 2004. — [DOI](https://doi.org/10.1016/j.jcss.2003.11.006)
- **[SOTA]** Apache DataSketches. *Theta and Tuple Sketch Set Operations.* Apache Software Foundation, 2015–. — [Apache](https://datasketches.apache.org/docs/Theta/ThetaSketches.html)

## 10. Worked Example

**Bottom-$k$ Jaccard from independent sketches.** Let $A=\{1,\dots,100\}$ and $B=\{51,\dots,150\}$, so $|A\cap B|=50$, $|A\cup B|=150$, true Jaccard $J=50/150=1/3$. Each side keeps a bottom-$k$ sketch with $k=6$ under a shared hash $h$.

Take the 6 globally smallest hash values across $A\cup B$ — call this sample $L$ (the merge of the two bottom-$k$ sets, then re-truncated to 6). Suppose, among those 6 items, 2 lie in $A\cap B$. The estimator is $\hat J = 2/6 = 0.33$, and $\widehat{|A\cap B|}=\hat J\cdot\widehat{|A\cup B|}$.

Variance check: $\mathrm{Var}(\hat J)\approx J(1-J)/k = (1/3)(2/3)/6 = 0.037$, so relative std on $\hat J$ is $\sqrt{0.037}/0.33 \approx 0.58$ — large for $k=6$. To pin intersection of Jaccard $\ge J_0=1/3$ to $\varepsilon=0.1$ relative error, Section 4 needs $k=\Theta(1/(\varepsilon^2 J_0)) = 1/(0.01\cdot0.33)\approx 300$ samples per set.

Now shrink the overlap to $|A\cap B|=2$ (so $J=2/198\approx0.01$): the required $k$ balloons to $\approx 1/(0.01\cdot0.01)=10^4$ — the small-overlap barrier, ultimately the $\Omega(n)$ set-disjointness wall as $J\to0$.

---
*Part of the [DBMS Research catalog](../../README.md).*
