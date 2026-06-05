# Approximate Median and Quantile Queries

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/approximate-quantiles` · **Status:** partially-solved

## 1. Problem Statement
Given a stream or large relation of $n$ items from a totally ordered universe, build a compact summary that answers **quantile** queries: for a target rank $\phi\in[0,1]$, return an item whose true rank is close to $\phi n$. The goal is a data structure of **optimal space** subject to an accuracy guarantee, supporting one-pass streaming construction and — crucially — **mergeability** (two summaries of disjoint inputs combine into one summary of the union without accuracy loss), so it parallelizes/distributes cleanly.

Error models (the key distinction):
- **Rank (additive) error $\varepsilon$:** the returned item's rank is within $\pm\varepsilon n$ of $\phi n$.
- **Relative (multiplicative) error $\varepsilon$:** rank within $\pm\varepsilon\cdot(\phi n)$ — far harder near the tails, where it must be very accurate.

Variants: deterministic vs. randomized; fixed-universe vs. comparison-based; insert-only vs. fully dynamic (with deletes/sliding window); single quantile (median) vs. all-quantiles summary.

## 2. Mathematical Foundations
A summary answers all quantiles with **rank error $\varepsilon$** if for every $x$ it returns $\hat r(x)$ with $|\hat r(x)-r(x)|\le\varepsilon n$, where $r(x)=|\{y\le x\}|$. **Mergeability** (Agarwal et al.) requires that combining summaries $S_1,S_2$ yields error no worse than $\varepsilon$ for $S_1\cup S_2$.

Space landscape (comparison model, $N$ items, error $\varepsilon$):
- **Deterministic:** the GK (Greenwald–Khanna) summary uses $O(\frac1\varepsilon\log(\varepsilon N))$ space; the deterministic **mergeable** lower bound is $\Omega(\frac1\varepsilon\log(\varepsilon N))$ (Cormode–Veselý 2020), matched up to constants.
- **Randomized:** the **KLL** sketch (Karnin–Lang–Liberty, FOCS 2016) achieves $O(\frac1\varepsilon\log\log\frac1\delta)$ space — optimal — using a hierarchy of randomly-sampled compactors; the $\Omega(\frac1\varepsilon\log\log\frac1\delta)$ lower bound matches.
- **Relative error:** requires $\Theta(\frac1\varepsilon\log(\varepsilon N)\cdot\text{polylog})$-type space; the **ReqSketch** / relative-error KLL variants (Cormode, Karnin, Liberty, Thaler, Veselý, 2021) give near-optimal relative-error guarantees. Tools: Chernoff/Bernstein concentration, compactor analysis, **information-theoretic** counting lower bounds.

## 3. State of the Art (SOTA)
- **Theory-SOTA (rank error):** **KLL** sketch — $O(\frac1\varepsilon\log\log\frac1\delta)$ words, mergeable, randomized, *space-optimal*. Deterministic optimum is **GK** matched by the Cormode–Veselý lower bound.
- **Theory-SOTA (relative error):** **ReqSketch** (relative-error quantiles), near-optimal, mergeable.
- **Systems-SOTA:** **t-digest** (Dunning) — widely deployed (Elasticsearch, Spark, etc.), excellent tail accuracy in practice though without a tight worst-case rank bound; **KLL** ships in **Apache DataSketches** (used by Druid, Spark, Pinot); **Q-digest** (Shrivastava et al.) for fixed integer universes in sensor networks; Postgres/BigQuery `APPROX_QUANTILES`.

## 4. Upper Bound
- Randomized rank error: **KLL** — $O(\frac1\varepsilon\log\log\frac1\delta)$ space, $O(\log\log\frac1\delta)$ amortized update, fully **mergeable** (Karnin–Lang–Liberty, FOCS 2016).
- Deterministic rank error: **GK** — $O(\frac1\varepsilon\log(\varepsilon n))$ space, comparison model (Greenwald–Khanna, SIGMOD 2001).
- Relative error: $O(\frac1\varepsilon\log^{1.5}(\varepsilon n))$-type space, mergeable, randomized (ReqSketch / Cormode et al. 2021).
- Fixed universe $[U]$: **Q-digest** $O(\frac1\varepsilon\log U)$ (Shrivastava et al., SenSys 2004).

## 5. Lower Bound
- **Randomized rank error:** $\Omega(\frac1\varepsilon\log\log\frac1\delta)$ words for a mergeable / streaming summary (Karnin–Lang–Liberty 2016) — KLL is optimal.
- **Deterministic mergeable:** $\Omega(\frac1\varepsilon\log(\varepsilon N))$ (Cormode–Veselý, PODS 2020) — GK-tight; deterministic comparison-based summaries cannot beat the $\log$ factor.
- **Relative error:** $\Omega(\frac1\varepsilon\log(\varepsilon N))$-type lower bounds (information-theoretic counting; tail accuracy forces extra space).
- These are **communication/encoding (information-theoretic)** bounds in the streaming/comparison model.

## 6. The Gap
For **rank (additive) error** the gap is **closed**: KLL (randomized) and GK (deterministic) match their respective $\Omega$ lower bounds up to constants. The **open** frontier is: (i) tightening *relative-error* space to remove remaining polylog factors; (ii) fully **dynamic** quantiles (arbitrary deletes, sliding windows) with optimal space; (iii) multi-dimensional / vector quantiles and quantiles under correlated streams; and (iv) practical structures (t-digest) lacking matching worst-case proofs. Hence "partially solved": the headline 1-D streaming case is settled, the harder regimes are not.

## 7. Current Research (as of June 2026)
Active directions: (1) **relative-error and tail-accurate** mergeable sketches with provably optimal space (ReqSketch lineage) and closing remaining polylog gaps *(frontier — verify)*; (2) **differentially-private quantiles** (private KLL/median selection) and their utility-space-privacy trade-offs; (3) quantiles over **sliding windows** and fully dynamic streams; (4) hardware/GPU and distributed-merge-optimized implementations in Apache DataSketches. Groups: Cormode (Warwick) and Veselý on quantile lower bounds and relative error; the Liberty/Karnin/Lang (DataSketches) lineage; Dunning (t-digest); the differential-privacy community (e.g., private selection).

## 8. Future Work
- Optimal-space relative-error and biased (tail-focused) quantile sketches.
- Fully dynamic and sliding-window quantiles with tight bounds.
- Multivariate / functional quantiles and quantiles over joins.
- Closing the theory-vs-practice gap for deployed structures (t-digest worst-case analysis).

## 9. Key References
- **[Foundational]** M. Greenwald, S. Khanna. *Space-Efficient Online Computation of Quantile Summaries (GK).* SIGMOD, 2001.
- **[SOTA]** Z. Karnin, K. Lang, E. Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016.
- **[SOTA]** G. Cormode, Z. Karnin, E. Liberty, J. Thaler, P. Veselý. *Relative Error Streaming Quantiles (ReqSketch).* PODS, 2021 / JACM, 2023.
- **[Foundational]** P. K. Agarwal, G. Cormode, Z. Huang, J. Phillips, Z. Wei, K. Yi. *Mergeable Summaries.* PODS, 2012 / ACM TODS, 2013.
- **[SOTA]** G. Cormode, P. Veselý. *A Tight Lower Bound for Comparison-Based Quantile Summaries.* PODS, 2020.
- **[Foundational]** N. Shrivastava, C. Buragohain, D. Agrawal, S. Suri. *Medians and Beyond: New Aggregation Techniques for Sensor Networks (Q-digest).* SenSys, 2004.
- **[SOTA]** T. Dunning, O. Ertl. *Computing Extremely Accurate Quantiles Using t-Digests.* 2019 (preprint / Software: Practice and Experience).

---
*Part of the [DBMS Research catalog](../../README.md).*
