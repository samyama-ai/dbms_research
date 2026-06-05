# Sample Maintenance Under Updates

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/sample-maintenance-updates` · **Status:** partially-solved

## 1. Problem Statement

Maintain a sample $S$ of a mutating relation $R$ so that $S$ remains a *correct* sample (uniform, or of a prescribed stratified/weighted design) of the **current** $R$, under a stream of inserts, updates, and deletes, **without** periodically rescanning $R$. "Correct" means the inclusion distribution after each operation matches the target design exactly (or within a stated tolerance), and the sample size stays within $[k_{\min}, k_{\max}]$.

Variants:
- **Insert-only (append):** classic reservoir sampling — essentially solved.
- **General (insert/update/delete) on bounded storage:** the hard case; deletes shrink $S$ and break uniformity.
- **Distinct-value / stratified maintenance:** keep per-stratum counts and allocations valid as strata grow and shrink.
- **Decision variant:** can a uniform sample of size $\ge k$ be maintained with $O(1)$ amortized work and $o(|R|)$ extra state given the observed delete rate?

## 2. Mathematical Foundations

A sample is **uniform of size $k$** if every $k$-subset of $R$ is equally likely; equivalently each $t$ has inclusion probability $k/|R|$. **Reservoir sampling** (Vitter, 1985) maintains this under inserts: the $i$-th arrival replaces a random reservoir slot with probability $k/i$. Deletes break the invariant because a deleted reservoir tuple cannot be replaced from data already discarded.

**Random pairing** (Gemulla, Lehner, Haas, VLDB 2006/2008) repairs this: track a count $c$ of "uncompensated" deletions; a new insert either fills a deleted slot or is itself skipped, restoring exact uniformity in expectation while bounding work. For **weighted/streaming** designs, **priority sampling** and **VarOpt** (Cohen et al.) assign each tuple a key $u_t^{1/w_t}$ ($u_t \sim \mathrm{Unif}(0,1)$) and keep the top-$k$; deletes correspond to key removal and re-thresholding. Formally, maintaining a bottom-$k$ sketch under deletions requires either *invertible* sketches (e.g. **$\ell_0$/$\ell_p$-samplers** built from linear sketches, which support turnstile deletions natively) or an auxiliary backing store. The relevant model is the **turnstile streaming model**: an $\ell_p$-sampler returns an element with probability $\propto |x_i|^p$ over a vector $x$ updated by $\pm$ increments.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** $\ell_p$-samplers (Monemizadeh–Woodruff, Jowhari–Sağlam–Tardos, SODA 2011) maintain perfect/near-perfect samples under fully dynamic (turnstile) updates in $\mathrm{polylog}(n)$ space — the strongest delete-robust result.
- **Systems-SOTA:** *random pairing* (Gemulla et al.) is the practical standard for bounded-size uniform samples under insert/delete and ships in sampling middleware. *VarOpt* and *priority sampling* for weighted maintenance. Materialized-view-style **incremental sample maintenance** in BlinkDB/VerdictDB-class systems refreshes stratified samples lazily. Distinct-value maintenance uses **HyperLogLog** / KMV sketches, which are insert-mergeable but *not* delete-friendly without sliding-window or invertible variants.

## 4. Upper Bound

- Insert-only uniform size-$k$: $O(1)$ amortized (skip-based reservoir), optimal.
- Insert/delete bounded uniform: random pairing maintains *exact* uniformity with $O(1)$ expected work per operation, provided the sample doesn't underflow; underflow probability is controllable by the insert/delete ratio.
- Fully dynamic turnstile: a perfect $\ell_0$-sampler in $O(\log^2 n)$ space and $O(\log n)$ update time succeeds w.h.p. (Jowhari–Sağlam–Tardos).

## 5. Lower Bound

In the turnstile model, any $\ell_0$/$\ell_p$-sampler requires $\Omega(\log^2 n)$ bits of space (matching the upper bound up to constants) — a *communication-complexity* lower bound. For bounded-storage uniform sampling under adversarial deletes, no algorithm can avoid eventual underflow without re-reading data when the **delete rate exceeds the insert rate over a window**: an information-theoretic impossibility, since the discarded tuples carry the only mass that could refill the reservoir. Thus "maintain size $\ge k$ with $o(|R|)$ state under arbitrary deletes and no rescans" is **impossible** in the worst case — the partial-solution status reflects exactly this boundary.

## 6. The Gap

For the *fully dynamic, polylog-space* sketch setting the gap is essentially **closed** ($\Theta(\log^2 n)$). The remaining open territory is the **bounded-size, rescan-free** setting under adversarial or bursty deletes: we have exact methods (random pairing) that work until underflow and impossibility once deletes dominate, but **no tight characterization of the achievable size-vs-state-vs-rescan frontier** as a function of the delete/insert ratio. Also open: maintaining *stratified* samples with provable per-stratum guarantees under skewed update streams without periodic global re-stratification.

## 7. Current Research (as of June 2026)

Active directions: delete-aware **sliding-window** and **expiring** sketches; merging sample maintenance with **CDC / change-data-capture** pipelines so the AQP layer rides the same log; "self-tuning" stratified samples that re-allocate online as workload and data drift *(frontier — verify)*. The streaming-algorithms community (Woodruff, Indyk, Cohen) continues to tighten dynamic samplers; the systems community (Mozafari, Chaudhuri/Narasayya) focuses on incremental refresh tied to materialized views. Emerging: maintaining samples for **learned** components (training-set drift) so a learned synopsis stays calibrated under updates *(frontier — verify)*.

## 8. Future Work

- A tight theory of the size/state/rescan trade-off under bounded delete rates.
- Stratified-sample maintenance with provable allocation invariants under drift.
- Mergeable *and* deletable distinct-count sketches with practical constants.
- Co-maintenance of samples and learned models so both stay calibrated as $R$ mutates.

## 9. Key References

- **[Foundational]** J. S. Vitter. *Random Sampling with a Reservoir.* ACM TOMS, 1985.
- **[Foundational]** R. Gemulla, W. Lehner, P. J. Haas. *Maintaining Bounded-Size Sample Synopses of Evolving Datasets.* VLDB Journal, 2008.
- **[SOTA]** H. Jowhari, M. Sağlam, G. Tardos. *Tight Bounds for $L_p$ Samplers, Finding Duplicates in Streams, and Related Problems.* PODS, 2011.
- **[SOTA]** E. Cohen, N. Duffield, H. Kaplan, C. Lund, M. Thorup. *Stream Sampling for Variance-Optimal Estimation of Subset Sums (VarOpt).* SODA, 2009.
- **[Survey]** G. Cormode, M. Garofalakis, P. J. Haas, C. Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011.

---
*Part of the [DBMS Research catalog](../../README.md).*
