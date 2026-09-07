---
id: 17-approximate-query-processing/sublinear-aggregation-bounds
title: "Sublinear-Time Aggregation Lower Bounds"
topic: 17-approximate-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Sublinear-Time Aggregation Lower Bounds

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/sublinear-aggregation-bounds` · **Status:** partially-solved

## 1. Problem Statement
Given a relation $R$ of $n$ tuples and an aggregate query $Q$ (e.g. `SUM`, `AVG`, `COUNT`, `MEDIAN`, `DISTINCT`, `VARIANCE`, or `SUM` under a selection predicate), we want a randomized algorithm that returns $\hat{Q}$ with $(1\pm\varepsilon)$ relative error with probability $\ge 1-\delta$ while reading only $o(n)$ tuples (ideally $\mathrm{poly}(1/\varepsilon,\log(1/\delta))$, independent of $n$). The central question is a **characterization**: which aggregates admit such sublinear-time approximation, and at what *query complexity* (number of tuple probes / samples) and *sample-access model* (uniform random sample, weighted sample, index-assisted probe).

Three variants matter. The **estimation/optimization** variant asks for minimal sample complexity to hit a target $(\varepsilon,\delta)$. The **decision** variant asks whether $Q$ exceeds a threshold $\tau$. The **counting** variant (e.g. `COUNT(DISTINCT)`, set cardinality) is provably the hardest. The answer depends sharply on the aggregate's *sensitivity* and *coverage*: mean-like statistics are sample-friendly; max/min, distinct-count, and rare-predicate sums are not, because a single unseen tuple can dominate the answer.

## 2. Mathematical Foundations
Model the relation as a vector $f\in\mathbb{R}^n$ of per-tuple values. For `SUM`/`AVG`, a uniform sample of size $m$ gives a Hoeffding/Bernstein bound: error $\le O\!\big(\sigma\sqrt{\tfrac{\log(1/\delta)}{m}}\big)$ where $\sigma$ is the value standard deviation, so $m=O(\sigma^2\varepsilon^{-2}\log\tfrac1\delta)$ samples suffice for additive error $\varepsilon\cdot$range. Relative error requires controlling *signal-to-noise*: for skewed $f$, the coefficient of variation $\mathrm{cv}=\sigma/\mu$ enters, and $m=\Theta(\mathrm{cv}^2\varepsilon^{-2})$.

Quantiles need $O(\varepsilon^{-2}\log\tfrac1\delta)$ samples for $\varepsilon$-rank error (DKW inequality). `COUNT(DISTINCT)` over a domain probed by sampling needs $\Omega(\sqrt{D})$ to even constant-approximate cardinality $D$ — a *birthday-paradox* lower bound (Charikar–Chaudhuri–Motwani–Narasayya, PODS 2000). The decision-theoretic frame uses the **distinguishability** of two input distributions under $m$ probes; Le Cam's two-point method and Yao's minimax principle yield lower bounds, and property-testing tools (the "missing mass," Good–Turing estimation) bound learnability of rare-event aggregates.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Tight $\Theta(\sqrt D)$ bounds for distinct-count from sampling; $\Theta(\varepsilon^{-2})$ for mean/quantile under bounded variance; symmetric-property estimation (Valiant–Valiant, STOC 2011 / Acharya–Orlitsky–Suresh) gives sublinear-sample estimators for entropy, support size, and distinct elements that are *sample-optimal* up to $\log$ factors at $n/\log n$ samples.
- **Systems-SOTA:** `BlinkDB` (EuroSys 2013) and online-aggregation engines (`G-OLA`, Wander Join's online estimators) exploit precomputed stratified samples to deliver sublinear-cost `SUM`/`AVG`/`COUNT` with confidence intervals; modern warehouses (`APPROX_COUNT_DISTINCT`, `APPROX_PERCENTILE`) ship sketch-backed versions but read full data once at sketch-build time.

## 4. Upper Bound
For `SUM`/`AVG`/`COUNT` with bounded value range and variance, $O(\mathrm{cv}^2\varepsilon^{-2}\log\tfrac1\delta)$ uniform samples — $O(1)$ in $n$ — in the **random-access RAM with uniform-sampling oracle** model. Quantiles: $O(\varepsilon^{-2}\log\tfrac1\delta)$. Distinct-count and entropy: $O(n/\log n)$ samples (Valiant–Valiant), sublinear but *not* $\mathrm{poly}(1/\varepsilon)$. Predicate-restricted `SUM` with selectivity $p$ costs $O(\tfrac{1}{p}\mathrm{cv}^2\varepsilon^{-2})$ — sublinear only when $p$ is not too small, or with an index providing weighted sampling.

## 5. Lower Bound
In the **sampling/query-complexity model**: distinct-count requires $\Omega(\sqrt{D})$ and entropy/support-size require $\Omega(n/\log n)$ samples (Valiant–Valiant matching lower bound). For low-selectivity predicate sums, $\Omega(1/p)$ samples are needed just to *see* a qualifying tuple — information-theoretic, via indistinguishability of an all-zero vs. one-spike input. `MAX`/`MIN` admit **no** finite-sample relative approximation without structural assumptions (a single unsampled outlier breaks it). These are unconditional, not complexity-conjecture-based.

## 6. The Gap
For mean/quantile the gap is essentially **closed** ($\Theta(\varepsilon^{-2})$). The open frontier is a *unified dichotomy theorem* mapping an aggregate's algebraic/statistical structure (additive vs. holistic, decomposable vs. not, distributive per Gray's CUBE taxonomy) to its exact sample complexity — including the right dependence on data skew and predicate selectivity. For distinct-count-like symmetric properties, constants and the precise $n/\log n$ threshold under *weighted* (not uniform) sampling remain partially open.

## 7. Current Research (as of June 2026)
Work continues on instance-optimal estimators (per-instance rather than worst-case sample complexity), on sample-access models richer than uniform (index-assisted weighted, conditional sampling), and on bridging property-testing lower bounds with practical AQP cost models. *(frontier — verify)* Several 2025 results refine symmetric-property estimation under adaptive/conditional sampling oracles, narrowing constants for support-size and distinct-count, but a complete aggregate-by-aggregate dichotomy has not been published in a peer-reviewed venue.

## 8. Future Work
- A formal dichotomy: which SQL aggregates are sublinear-approximable and at what complexity, parameterized by skew and selectivity.
- Lower bounds in *index-assisted* models that reflect real AQP engines (B-trees, measure indexes).
- Sublinear estimators robust to adversarial value distributions and correlated samples.

## 9. Key References
- **[Foundational]** Charikar, M., Chaudhuri, S., Motwani, R., Narasayya, V. *Towards Estimation Error Guarantees for Distinct Values.* PODS, 2000. — [DOI](https://doi.org/10.1145/335168.335230)
- **[Foundational]** Valiant, G., Valiant, P. *Estimating the Unseen: An $n/\log n$-Sample Estimator for Entropy and Support Size.* STOC, 2011. — [DOI](https://doi.org/10.1145/1993636.1993727)
- **[SOTA]** Agarwal, S., Mozafari, B., Panda, A., Milner, H., Madden, S., Stoica, I. *BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data.* EuroSys, 2013. — [DOI](https://doi.org/10.1145/2465351.2465355)
- **[Foundational]** Hellerstein, J., Haas, P., Wang, H. *Online Aggregation.* SIGMOD, 1997. — [DOI](https://doi.org/10.1145/253262.253291)
- **[Survey]** Cormode, G., Garofalakis, M., Haas, P., Jermaine, C. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

**Why `MAX` defeats sampling but `AVG` does not.** Relation $R$ has $n = 10^6$ salary values. Consider two adversarial instances:

- $A$: all values $= 100$.
- $B$: $999{,}999$ values $= 100$, and **one** value $= 10^9$.

Draw a uniform sample of size $m = 10{,}000$. The probability the sample misses the single spike in $B$ is $(1 - 10^{-6})^{10^4} \approx e^{-0.01} \approx 0.99$. So with $99\%$ probability the samples from $A$ and $B$ are **identical** — no estimator can tell them apart. Yet $\mathrm{MAX}(A)=100$ while $\mathrm{MAX}(B)=10^9$, a $10^7\times$ gap. Hence no relative-error CI for `MAX` from $o(n)$ samples (the $\Omega(1/p)$ "see the spike" bound, section 5).

Contrast `AVG`: $\mu_A = 100$, $\mu_B = 100 + (10^9-100)/10^6 \approx 1100$. Here the spike contributes only $\approx 900$ to a mean of order $10^3$ — a *bounded* shift. With variance $\sigma^2$ and Bernstein's bound, $m = O(\mathrm{cv}^2\varepsilon^{-2}\log\tfrac1\delta)$ samples suffice; e.g. $\mathrm{cv}\approx 30$, $\varepsilon=0.1$, $\delta=0.05$ gives $m \approx 30^2 \cdot 100 \cdot 3 \approx 2.7\times10^5$ — still independent of $n$. Sensitivity, not the SQL keyword, decides sample-friendliness.

---
*Part of the [DBMS Research catalog](../../README.md).*
