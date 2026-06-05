# Quantile and heavy-hitter tracking over windows

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/windowed-quantiles-heavy-hitters` · **Status:** partially-solved
> **Verification note:** The KLL sketch is Karnin–Lang–**Liberty** (Edo Liberty); occurrences of "Liviu" are a name typo for "Liberty."

## 1. Problem Statement

Given a high-rate stream and a window (sliding, tumbling, or session), continuously maintain approximate answers to two classical summaries:

- **Quantiles:** for query rank $\phi \in (0,1)$, return an item whose true rank is within $\epsilon N$ of $\phi N$ (rank error), where $N$ is the current window size.
- **Heavy hitters / frequent items:** report all items with frequency $\ge \phi N$, none with frequency $< (\phi-\epsilon)N$ (the $(\phi,\epsilon)$-heavy-hitters guarantee).

The window-aware twist: bounds and state must hold *with respect to the live window*, despite expiry of old elements, and the summaries should be **mergeable** so that per-partition sketches combine into a global answer with no error blowup.

Variants: **counting/estimation** (frequency/rank), **decision** (is item $x$ a heavy hitter?), and **optimization** (minimize space for a target $\epsilon$). Sliding windows make this strictly harder than the infinite-stream case because deletions (expiries) are adversarially timed.

## 2. Mathematical Foundations

Stream $\sigma = a_1, a_2, \dots$ over universe $[m]$; window $W_t$ of size $N$ (count-based) or duration. Frequency vector $\mathbf{f}\in\mathbb{N}^m$ restricted to $W_t$.

- **Rank / $\epsilon$-approximate quantile:** an item $x$ with $|\mathrm{rank}(x) - \phi N| \le \epsilon N$.
- **Mergeability** (Agarwal et al. 2013): a summary class is *mergeable* if $\mathrm{merge}(S(A), S(B))$ has the same error guarantee as $S(A\cup B)$, enabling distributed/parallel construction. The **KLL sketch** (Karnin–Lang–Liberty 2016) is fully mergeable with optimal space $O(\tfrac{1}{\epsilon}\log\log\tfrac{1}{\delta})$ for rank error $\epsilon$ w.p. $1-\delta$.
- **Heavy hitters in $\ell_1$:** Misra–Gries / SpaceSaving give deterministic $O(1/\epsilon)$ counters; **Count-Min** (Cormode–Muthukrishnan 2005) gives $O(\tfrac{1}{\epsilon}\log\tfrac1\delta)$ space with $\ell_1$ error $\epsilon\|\mathbf f\|_1$.
- **Sliding windows:** the **Exponential Histogram** (Datar–Gionis–Indyk–Motwani 2002) maintains $\epsilon$-approximate counts over windows in $O(\tfrac1\epsilon \log^2 N)$ bits; **smooth histograms** (Braverman–Ostrovsky 2007) extend this to a broad class of functions including frequency moments.

## 3. State of the Art (SOTA)

- **Theory-SOTA quantiles:** KLL achieves optimal $O(\tfrac1\epsilon\log\log\tfrac1\delta)$ words; relative-error variants (Cormode et al., Zhang–Wang) handle tail quantiles. Sliding-window quantiles via DGIM/smooth-histogram frameworks.
- **Theory-SOTA heavy hitters:** SpaceSaving (Metwally et al. 2005) and Misra–Gries are deterministic optimal $O(1/\epsilon)$; BPTree (Braverman et al. 2017) gives optimal $\ell_2$ heavy hitters in near-optimal space.
- **Systems-SOTA:** Apache DataSketches (KLL, Theta, Frequent-Items) is the de facto production library, integrated in Druid, Spark, Flink. Count-Min/HLL ship in Redis, ClickHouse, Snowflake `APPROX_*`.

## 4. Upper Bound

- **Quantiles (infinite stream):** $O(\tfrac1\epsilon \log\log\tfrac1\delta)$ words (KLL), randomized, comparison model — matching the $\Omega$ lower bound.
- **Sliding-window quantiles:** $O(\tfrac1\epsilon \log N \log\tfrac1\epsilon)$-type bounds via exponential/smooth histograms.
- **Heavy hitters:** $O(1/\epsilon)$ counters deterministic (Misra–Gries/SpaceSaving) for $\ell_1$; merge preserves the guarantee.

## 5. Lower Bound

- **Quantiles:** $\Omega(\tfrac1\epsilon \log\log\tfrac1\delta)$ for randomized rank approximation (Karnin–Lang–Liberty 2016); $\Omega(\tfrac1\epsilon\log\tfrac1\epsilon)$ for deterministic comparison-based summaries — proven via communication-complexity / encoding arguments.
- **Sliding windows:** any algorithm exactly maintaining a count over a window of size $N$ needs $\Omega(N)$ bits; approximation is *necessary* (Datar et al. 2002), and $\Omega(\tfrac1\epsilon\log^2 N)$-style bits are required for $\epsilon$-counts.
- **Heavy hitters:** $\Omega(1/\epsilon)$ space via a reduction from INDEX/set-disjointness in communication complexity.

## 6. The Gap

For *infinite streams* the problem is essentially **closed** (KLL, SpaceSaving match lower bounds). The genuinely open part is **sliding windows under exact mergeability**: smooth-histogram constructions add log factors and are *not* cleanly mergeable, so distributed sliding-window quantiles still carry a gap between the $O(\tfrac1\epsilon\log^2 N)$ upper bounds and $\Omega(\tfrac1\epsilon\log N)$-type lower bounds. Tight window-aware *and* mergeable bounds for relative-error (tail) quantiles remain open.

## 7. Current Research (as of June 2026)

- Continued work on **relative-error / fully-mergeable sliding-window quantiles** building on KLL (Cormode, Mitzenmacher, and the DataSketches community) *(frontier — verify)*.
- **Learning-augmented sketches** (Hsu–Indyk–Katabi–Vakilian 2019 lineage): using predicted frequencies to beat worst-case space on real workloads, now extended to windows.
- GPU/SIMD-vectorized KLL and SpaceSaving for line-rate ingestion in ClickHouse/Druid *(frontier — verify)*.
- Differentially-private window quantiles/heavy hitters (continual observation under DP, Dwork et al. lineage).

## 8. Future Work

- Provably mergeable sliding-window quantile sketches with no log-factor penalty.
- Unified window-aware bounds across tumbling/sliding/session windows.
- Adaptive (input-aware) heavy-hitter detection with formal guarantees under concept drift.
- Tight composition of DP + window-decay error.

## 9. Key References

- **[Foundational]** M. Datar, A. Gionis, P. Indyk, R. Motwani. *Maintaining Stream Statistics over Sliding Windows.* SIAM J. Computing, 2002. — [DOI](https://doi.org/10.1137/S0097539701398363)
- **[Foundational]** G. Cormode, S. Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch and its Applications.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Foundational]** A. Metwally, D. Agrawal, A. El Abbadi. *Efficient Computation of Frequent and Top-k Elements in Data Streams (Space-Saving).* ICDT, 2005. — [DOI](https://doi.org/10.1007/978-3-540-30570-5_27)
- **[SOTA]** Z. Karnin, K. Lang, E. Liberty. *Optimal Quantile Approximation in Streams (KLL).* FOCS, 2016. — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** P. K. Agarwal, G. Cormode, Z. Huang, J. Phillips, Z. Wei, K. Yi. *Mergeable Summaries.* ACM TODS, 2013. — [DOI](https://doi.org/10.1145/2500128)
- **[Survey]** G. Cormode, M. Garofalakis, P. Haas, C. Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2012. — [DOI](https://doi.org/10.1561/1900000004)

## 10. Worked Example

**Misra–Gries heavy hitters** with $\epsilon = 1/3$, so $k = \lceil 1/\epsilon\rceil - 1 = 2$ counters, on the stream $a,b,a,c,a,b,d$ ($N=7$).

| arrive | counters after step |
|--------|---------------------|
| $a$ | $\{a{:}1\}$ |
| $b$ | $\{a{:}1, b{:}1\}$ |
| $a$ | $\{a{:}2, b{:}1\}$ |
| $c$ | full + new key $\Rightarrow$ decrement all: $\{a{:}1\}$ |
| $a$ | $\{a{:}2\}$ |
| $b$ | $\{a{:}2, b{:}1\}$ |
| $d$ | decrement all: $\{a{:}1\}$ |

Final estimate $\hat f(a)=1$; true counts are $f(a)=3,\,f(b)=2,\,f(c)=f(d)=1$. Misra–Gries guarantees $f(x)-\epsilon N \le \hat f(x) \le f(x)$, i.e. each estimate undercounts by at most $\epsilon N = 7/3 \approx 2.33$. Check: $\hat f(a)=1 \in [3-2.33,\,3]$. Any true $\phi$-heavy hitter with $\phi > \epsilon$ survives with a positive counter, so querying $\phi = 1/2$ ($\ge \lceil 3.5\rceil$ occurrences) correctly returns no false negatives. The structure uses only $O(1/\epsilon)=2$ counters regardless of $N$, and two such tables **merge** by summing then keeping the top $k$ — the property that makes it usable per-window and across partitions.

---
*Part of the [DBMS Research catalog](../../README.md).*
