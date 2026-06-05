# Out-of-order stream processing without buffering blowup

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/out-of-order-processing` · **Status:** partially-solved

## 1. Problem Statement

Tuples in a real stream arrive out of timestamp order due to network reordering, parallel sources, and merge of multiple partitions. Order-sensitive operators — windowed aggregates, windowed joins, sequence/pattern (CEP) matching, top-k — must still produce results consistent with **event-time** ordering. The naive fix, buffering until order can be guaranteed, can require unbounded state if lateness is unbounded.

The problem: design operators and a progress mechanism that **emit correct (or bounded-error) results for disordered input while keeping reordering/buffer state provably bounded.** Inputs:
- a stream with bounded or stochastic *lateness* (delay between event time and arrival),
- an operator with event-time semantics,
- a completeness/latency policy.

Variants:
- **Exact-with-bounded-lateness:** given a hard skew bound $K$, guarantee correct windowed output using $O(K)$ buffer.
- **Approximate / probabilistic:** lateness is heavy-tailed; bound the probability of emitting incomplete results vs. memory.
- **Progress-tracking:** compute *watermarks* / punctuations that lower-bound the minimum future event time, deciding when a window can close.
- **Retraction model:** emit early then correct (revisions / retractions) to bound latency without dropping late data.

## 2. Mathematical Foundations

Let each tuple carry event time $\tau$ and arrival index $i$. Define **skew/lateness** $\ell_i = w_i - \tau_i$ where $w_i$ is a monotone arrival clock. A **watermark** at arrival point $i$ is a value $W_i$ asserting "no future tuple has $\tau < W_i$"; correctness of closing window $[a,b)$ at $W_i \ge b$ requires the watermark to be a valid lower bound. **K-slack** assumes $\ell_i \le K$, giving deterministic correctness with buffer $O(K)$.

The dataflow-progress foundation is **timely dataflow** (Murray et al., SOSP 2013): a partially ordered set of *timestamps* with a *frontier* (an antichain) and *pointstamp* capability counts; progress is the guarantee that no message at or before a frontier timestamp can still appear. This generalizes punctuations (Tucker, Maier; 2003) and is the formal basis for low-watermarks.

Approximate variants model $\ell$ as a random variable; choosing $W_i = w_i - q$ for the $(1-\alpha)$-quantile $q$ of lateness bounds the **probability of dropping a late tuple** by $\alpha$ while keeping buffer $\approx$ the quantile. **Punctuation semantics** (the "dribble"/grouping/keeping properties) give an algebra for which operators can unblock under partial order.

## 3. State of the Art (SOTA)

- **Theory/semantics:** Tucker, Maier, Sheard, Fegaras — *Exploiting Punctuation Semantics in Continuous Data Streams* (TKDE 2003): formal framework for unblocking operators on disordered streams.
- **Timely / Differential Dataflow** (Murray, McSherry et al. 2013; McSherry, Murray, Isaacs 2013): the cleanest progress model with frontiers; differential dataflow handles arbitrary partial orders with incremental retractions.
- **Google Dataflow / Beam model** (Akidau et al., VLDB 2015): watermarks + triggers + accumulation modes — the de-facto **systems SOTA**, separating *what/where/when/how* and supporting allowed-lateness and retractions.
- **Apache Flink** (Carbone et al., 2015–): watermarks, allowed lateness, and side-output for late data; production standard.
- **Out-of-order processing (OOP)** (Li, Tufte, Shkapenyuk, Papadimos, Johnson, Maier; SIGMOD 2008): replaced stall/disorder-handling with *low-watermark* punctuations for windowed aggregates — the canonical academic OOP design.

## 4. Upper Bound

Under a **hard skew bound $K$** (max lateness), exact windowed aggregation and equi-join over windows of length $w$ require buffer $O(w + K)$ per key/partition and $O(1)$ amortized work per tuple — this is *tight up to constants* and is the basis of K-slack and the OOP low-watermark operators (model: deterministic bounded disorder).

Under **stochastic lateness**, watermarking at the $(1-\alpha)$ lateness quantile yields buffer proportional to that quantile with probability $\ge 1-\alpha$ of including any given late tuple; combined with retractions, latency is bounded *and* eventual correctness is achieved with state $O(\text{active windows})$.

Differential dataflow supports incremental updates under arbitrary partial orders with per-update work proportional to the change ("work proportional to the size of the difference"), not the whole state.

## 5. Lower Bound

- **Unbounded lateness ⇒ unbounded state (impossibility):** if lateness is truly unbounded and exact, complete, low-latency results are required simultaneously, no finite-state operator suffices — a window can never provably close. This is the fundamental *completeness vs. latency vs. memory* trilemma; any two are achievable, not all three (folklore, formalized via punctuation/progress theory).
- **Communication / streaming space:** windowed exact distinct/quantile under disorder inherits the $\Omega(1/\epsilon^2)$ and sliding-window lower bounds (Datar–Gionis–Indyk–Motwani; Indyk lower bounds), so even approximate order-sensitive stats cannot be done in $o(\frac{1}{\epsilon^2}\log n)$ space.
- For sequence/CEP queries, NFA state under disorder can blow up combinatorially with overlapping partial matches; worst-case match enumeration is output-size bound (no sublinear-in-output algorithm possible).

## 6. The Gap

**Partially solved.** For bounded-disorder (K-slack) and the watermark+trigger+retraction model, the gap between upper and lower bounds is essentially closed — $O(w+K)$ is optimal and the trilemma is well-understood. The genuinely open part is **heavy-tailed / adversarial lateness**: how to choose watermarks to *minimize expected (latency + correction cost)* with provable competitive ratios, and how to bound state for **CEP / pattern** queries under disorder without enumerating exponential partial matches. Adaptive, learning-based watermark estimators lack formal regret/competitive guarantees.

## 7. Current Research (as of June 2026)

- **Adaptive / learned watermarks:** predicting lateness distributions online to set watermarks minimizing a latency–completeness loss; the open challenge is competitive-ratio guarantees *(frontier — verify)*.
- **Disorder-resilient CEP:** bounded-state pattern matching tolerating reordering, with speculative matching + retraction (work in the CEP community at DEBS/VLDB) *(frontier — verify)*.
- **Watermark robustness in disaggregated/cloud-native streaming** (idle-source and skew handling across autoscaled tasks).
- Active groups: McSherry/ETH timely-dataflow lineage, Google Dataflow/Beam team, Flink community (TU Berlin/dataArtisans alumni), Portland State (Maier/Tufte) OOP lineage.

## 8. Future Work

- Competitive online watermark policies with provable latency/correctness tradeoffs under unknown heavy-tailed lateness.
- Bounded-state, retraction-based CEP for disordered streams.
- Tight space bounds for approximate order-sensitive statistics (quantiles, distinct) under disorder.
- Unified semantics linking timely-dataflow frontiers, Beam triggers, and database event-time models.
- Cost models that trade buffer memory against retraction volume automatically.

## 9. Key References

- **[Foundational]** Tucker, Maier, Sheard, Fegaras. *Exploiting Punctuation Semantics in Continuous Data Streams.* IEEE TKDE, 2003.
- **[Foundational]** Li, Tufte, Shkapenyuk, Papadimos, Johnson, Maier. *Out-of-order Processing: A New Architecture for High-performance Stream Systems.* SIGMOD / PVLDB, 2008.
- **[SOTA]** Murray, McSherry, Isaacs, Isard, Barham, Abadi. *Naiad: A Timely Dataflow System.* SOSP, 2013.
- **[SOTA]** Akidau, Bradshaw, Chambers, et al. *The Dataflow Model.* PVLDB, 2015.
- **[Foundational]** Datar, Gionis, Indyk, Motwani. *Maintaining Stream Statistics over Sliding Windows.* SIAM J. Comput., 2002.
- **[SOTA]** Carbone, Katsifodimos, Ewen, Markl, Haridi, Tzoumas. *Apache Flink: Stream and Batch Processing in a Single Engine.* IEEE Data Eng. Bull., 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
