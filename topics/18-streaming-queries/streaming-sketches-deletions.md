# Streaming sketches under deletions and expiry

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/streaming-sketches-deletions` · **Status:** open

## 1. Problem Statement

A *sketch* is a small, fixed-size summary supporting approximate queries (frequencies, heavy hitters, distinct counts, quantiles, set membership) over a stream. Many sketches handle **insertions** well and some handle **arbitrary deletions** (the *turnstile* model). Separately, sliding-window techniques handle **expiry** (the oldest elements leave). The open problem is a single class of **mergeable, bounded-error sketches that simultaneously support (a) arbitrary deletions of explicitly identified items and (b) automatic window expiry**, while remaining small and composable across distributed shards.

Why it's hard: deletions can drive true counts to zero or negative regions (signed model), breaking monotone/decay-based expiry tricks; expiry needs per-element age information that most linear sketches discard; and **mergeability** (combine sketches from different partitions into one valid summary) constrains the structure to be (near-)linear, which conflicts with age-thresholding.

Variants:
- **Strict turnstile** (counts stay $\ge 0$) vs. **general turnstile** (signed).
- **Hard expiry** (exactly drop items older than $w$) vs. **time-decay** (down-weight by age).
- Per-query type: frequency/heavy-hitters (Count-Min/CountSketch), distinct ($F_0$/$\ell_0$), quantiles (KLL/GK), membership (Bloom/Cuckoo).
- **Optimization:** minimize space for $(\epsilon,\delta)$ error under both deletions and expiry; **decision:** does a mergeable, expiry-and-deletion-supporting sketch with given space exist for a query class?

## 2. Mathematical Foundations

Linear sketches $Sx$ (Count-Min, CountSketch, AMS, $\ell_0$-samplers) are inherently **deletion-friendly and mergeable** because $S(x+y)=Sx+Sy$; this is the algebraic reason turnstile updates "just work." Count-Min gives frequency estimates with error $\epsilon\|x\|_1$ in $O(\frac{1}{\epsilon}\log\frac{1}{\delta})$ counters; CountSketch gives $\epsilon\|x\|_2$ error. **AGM / $\ell_0$-samplers** (Cormode–Firmani; Jowhari–Sağlam–Tardos) support distinct counting and graph connectivity under deletions.

Expiry breaks linearity: "drop items with timestamp $< t-w$" is not a linear operation on the count vector. The reconciling frameworks are:
- **Exponential / smooth histograms** (DGIM 2002; Braverman–Ostrovsky 2007) for windows, but classically insertion-only.
- **Time-decaying sketches** (Cormode–Korn–Tirthapura 2008; forward-decay): weight an element by $g(\text{age})$, which *can* be made linear for exponential decay, giving mergeable decayed sketches — but exponential decay is "soft" expiry, not a hard window.
- **Robust / adversarial sketching** (Ben-Eliezer–Jayaram–Woodruff–Yogev, PODS 2020) addresses adaptive deletions.

The tension is captured information-theoretically: hard-window + deletions must encode, per surviving item, both value and age, while remaining mergeable — pushing toward $\ell_0$-sampling with timestamps, but with no tight space characterization.

## 3. State of the Art (SOTA)

- **Count-Min Sketch** (Cormode, Muthukrishnan; 2005): turnstile frequency/heavy-hitter sketch — deletions yes, expiry no.
- **CountSketch / AMS** (Charikar–Chen–Farach-Colton 2002; Alon–Matias–Szegedy 1996): $\ell_2$/$F_2$ under deletions.
- **$\ell_0$-samplers and graph sketches** (Ahn–Guha–McGregor 2012; Jowhari–Sağlam–Tardos 2011): distinct and connectivity under fully dynamic (deletion) streams.
- **Time-decaying / forward-decay sketches** (Cormode, Korn, Tirthapura 2008; Cormode, Shkapenyuk, Srivastava, Xu 2009): age-weighted aggregates, mergeable for exponential decay — the closest thing to deletions+expiry.
- **KLL quantile sketch** (Karnin, Lang, Liberty; FOCS 2016): optimal mergeable quantiles, but **insertion-only / comparison-based**, no deletions.
- **Mergeability theory** (Agarwal, Cormode, Huang, Phillips, Wei, Yi; PODS 2012): formal framework for which summaries merge with bounded error.

## 4. Upper Bound

- **Deletions only (turnstile), mergeable:** Count-Min in $O(\frac{1}{\epsilon}\log\frac{1}{\delta})$ counters ($\epsilon\|x\|_1$ error); $\ell_0$-sampling distinct in $\tilde{O}(\log^2 m)$ space. These are tight or near-tight in the turnstile model.
- **Expiry only (sliding window), insertion-only:** smooth histograms give $(1\pm\epsilon)$ for $F_p$/distinct in $\tilde{O}(\frac{1}{\epsilon}\log N)\times(\text{sub-sketch})$ space.
- **Time-decay (soft expiry) + deletions:** exponential-forward-decay sketches are linear, hence support both, in space comparable to the underlying sketch — but only for **smooth exponential decay**, not a hard window boundary.
- **Hard window + arbitrary deletions, mergeable:** no general construction with clean worst-case bounds is known; best are timestamped $\ell_0$-sampler hybrids for specific queries.

## 5. Lower Bound

- **Turnstile space:** frequency estimation to $\epsilon\|x\|_1$ needs $\Omega(\frac{1}{\epsilon})$ counters; $F_0$/$F_2$ under deletions need $\Omega(\epsilon^{-2})$ (AMS/gap-Hamming, Kane–Nelson–Woodruff).
- **Window penalty:** sliding-window statistics carry an extra $\Omega(\frac{1}{\epsilon}\log N)$ (DGIM communication lower bounds) over their unbounded counterparts.
- **No deletions in comparison-based quantile sketches:** KLL-style mergeable quantile sketches are provably incompatible with deletions in the comparison model; supporting deletions forces a different (counting-based) model with worse bounds.
- **Combined hardness (folklore/open):** maintaining mergeable summaries under *both* general-turnstile deletions and *hard* expiry appears to require $\Omega$(window-penalty $\times$ turnstile-cost), but no matching upper bound exists — the combination is conjectured strictly harder than either alone, and a clean lower bound separating "deletions+expiry" from "deletions only" is not established.

## 6. The Gap

**Open.** Each ingredient is solved in isolation (turnstile linear sketches; sliding-window smooth histograms; time-decay), but their **conjunction — mergeable, bounded-error, *hard*-window *and* arbitrary-deletion sketches — has neither a general algorithm nor a tight lower bound** for most query classes (heavy hitters, quantiles, distinct). The crux: linearity gives deletions+mergeability but is incompatible with hard age-thresholding; timestamped sampling gives expiry but loses the clean linear-merge guarantees and tight space. Closing the gap means either (a) a new summary structure reconciling linearity with hard expiry, or (b) lower bounds proving the conjunction inherently costs more than the sum of parts.

## 7. Current Research (as of June 2026)

- **Timestamped $\ell_0$/$\ell_p$ samplers** that retain the most-recent occurrence per sampled coordinate, giving distinct/heavy-hitter estimates under deletions *and* expiry — formal space bounds still open *(frontier — verify)*.
- **Adversarially robust dynamic sketches** extending Ben-Eliezer et al. to windowed+deletion settings *(frontier — verify)*.
- **Differentially private** versions of deletion-and-expiry sketches (privacy under the "right to be forgotten" deletion semantics) *(frontier — verify)*.
- **Quantiles under deletions:** counting-based mergeable quantile structures aiming to recover KLL-like space with deletion support.
- Active researchers: Cormode, Woodruff, Nelson, Tirthapura, Liberty/Karnin (quantiles), McGregor (dynamic graph sketches).

## 8. Future Work

- A general mergeable summary supporting hard expiry + arbitrary deletions with provable $(\epsilon,\delta)$ bounds.
- Tight lower bounds separating "deletions + hard expiry" from each ingredient alone.
- Deletion-capable optimal quantile sketches.
- Robust and private deletion-and-expiry sketches with formal guarantees.
- Distributed/communication-optimal merging of windowed turnstile sketches.

## 9. Key References

- **[Foundational]** Cormode, Muthukrishnan. *An Improved Data Stream Summary: The Count-Min Sketch and its Applications.* J. Algorithms, 2005. — [DOI](https://doi.org/10.1016/j.jalgor.2003.12.001)
- **[Foundational]** Charikar, Chen, Farach-Colton. *Finding Frequent Items in Data Streams.* ICALP / TCS, 2002. — [DOI](https://doi.org/10.1007/3-540-45465-9_59)
- **[SOTA]** Karnin, Lang, Liberty. *Optimal Quantile Approximation in Streams.* FOCS, 2016. — [DOI](https://doi.org/10.1109/FOCS.2016.17) — [arXiv](https://arxiv.org/abs/1603.05346)
- **[SOTA]** Agarwal, Cormode, Huang, Phillips, Wei, Yi. *Mergeable Summaries.* ACM TODS, 2013. — [DOI](https://doi.org/10.1145/2500128)
- **[Foundational]** Cormode, Korn, Tirthapura. *Time-Decaying Aggregates in Out-of-Order Streams.* PODS, 2008. — [DBLP](https://dblp.org/rec/conf/pods/CormodeKT08.html)
- **[SOTA]** Ben-Eliezer, Jayaram, Woodruff, Yogev. *A Framework for Adversarially Robust Streaming Algorithms.* PODS, 2020. — [arXiv](https://arxiv.org/abs/2003.14265)
- **[Foundational]** Jowhari, Sağlam, Tardos. *Tight Bounds for $L_p$ Samplers, Finding Duplicates, and Streaming Algorithms.* PODS, 2011. — [DOI](https://doi.org/10.1145/1989284.1989289) — [arXiv](https://arxiv.org/abs/1012.4889)

## 10. Worked Example

Take a tiny Count-Min sketch with $d=2$ rows, $w=3$ columns, hash functions $h_1,h_2:\text{item}\to\{0,1,2\}$. It is **linear**, so deletions are just negative updates. Process the turnstile stream: $+5$ of item $a$, $+3$ of $b$, then a deletion $-2$ of $a$.

Suppose $h_1(a)=0,h_2(a)=1$ and $h_1(b)=0,h_2(b)=2$ (so $a,b$ collide in row 1, col 0). After all updates the true count of $a$ is $5-2=3$.

Counters:
- Row 1: col0 $= (5{-}2)+3 = 6$, col1 $=0$, col2 $=0$.
- Row 2: col0 $=0$, col1 $=(5{-}2)=3$, col2 $=3$.

Estimate $\hat a = \min(\text{row1}[h_1(a)],\ \text{row2}[h_2(a)]) = \min(6,3) = 3$ — exact here, because row 2 avoids the $a/b$ collision; the $\min$ discards the inflated estimate $6$. The error bound is $\hat a \le a + \epsilon\|x\|_1$ with $\|x\|_1 = 3+3 = 6$.

Now add **hard expiry**: drop $b$ because it is older than window $w$. There is no linear operation on these counters that removes only $b$'s contribution from col0 without knowing $b$'s value and age — illustrating the core tension (Section 6): linearity gives deletions for free but cannot, by itself, perform age-based hard expiry.

---
*Part of the [DBMS Research catalog](../../README.md).*
