---
id: 18-streaming-queries/watermark-lateness-bounds
title: "Watermark generation with provable lateness bounds"
topic: 18-streaming-queries
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Watermark generation with provable lateness bounds

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/watermark-lateness-bounds` · **Status:** open

## 1. Problem Statement

A **watermark** $W(p)$ at processing-time $p$ is a claim that no future element with event-time $\le W(p)$ will arrive (or that the probability/quantity of such *late* elements is bounded). Watermarks drive when windowed results fire. The problem: from an observed, out-of-order, multi-source stream with **unknown and time-varying source skew**, generate watermarks that come with a *provable* guarantee relating to:

- **Lateness** $L$: how far past a window's close the firing decision is delayed (latency cost), and
- **Incompleteness** $I$: the fraction/weight of records that arrive *after* their window has fired and are therefore dropped or require retraction.

Formally: **given a target incompleteness $\epsilon$ (or a target lateness budget $L$), produce a watermark policy minimizing the other quantity, with a high-probability or worst-case guarantee, under an adversarial or stochastic delay model.** Decision variant: "does a watermark policy with lateness $\le L$ and incompleteness $\le \epsilon$ exist for this delay distribution?" Optimization variant: trace the $(L,\epsilon)$ trade-off.

## 2. Mathematical Foundations

Model each source $s$ as emitting events with event-times $t_e$ and observed processing-times $t_p$; the **delay** is $D_s = t_p - t_e$, a random variable (or adversarial sequence) with unknown distribution $F_s$. A **perfect watermark** would track $\inf$ over in-flight event-times; a **heuristic watermark** estimates a quantile $q_\alpha$ of $D_s$. If $W(p) = p - \delta$ for a fixed lag $\delta$, then incompleteness equals $\Pr[D_s > \delta]$ and lateness equals $\delta$. Thus the core object is the **tail of the delay distribution** $\bar F_s(\delta) = \Pr[D_s>\delta]$, and watermark design is **online quantile estimation under distribution shift**.

With $k$ sources, $W(p)=\min_s W_s(p)$ (the slowest source dominates), so heterogeneity and **stragglers/idle partitions** create the hard cases. Adversarial-skew bounds connect to **online learning / regret** (track a shifting quantile) and to **concentration inequalities** (DKW for empirical CDF: $\Pr[\sup_x |\hat F_n(x)-F(x)|>\eta]\le 2e^{-2n\eta^2}$) which gives finite-sample guarantees *only* under stationarity. Under unbounded adversarial delay, a clean impossibility appears: **no finite watermark can guarantee both completeness and progress** — a CAP/FLP-flavored tension between liveness (must advance) and safety (must not drop).

## 3. State of the Art (SOTA)

- **Heuristic watermarks** (Google MillWheel — Akidau et al., VLDB 2013; Beam/Flink): percentile-of-observed-lateness estimators with *allowed lateness* + retraction as a safety net. Widely deployed, **no formal lateness/incompleteness guarantee**.
- **Low-watermark / punctuation** lineage (Tucker, Maier, Sheard, Fegaras; TKDE 2003) gives the semantic substrate.
- **Adaptive watermark estimators**: quantile-tracking and ML-predicted watermarks (e.g., per-partition delay models). Systems-SOTA in Flink/Beam uses idle-source detection + bounded-out-of-orderness assigners.
- **AWARE / strategy-driven watermarks** *(frontier — verify)* and recent work on **watermark accuracy vs latency** quantify the trade-off empirically.

## 4. Upper Bound

Constructively, under a **stochastic stationary** delay model with i.i.d. samples per source, a DKW-based empirical-quantile watermark achieves incompleteness $\le \epsilon$ with confidence $1-\beta$ using $n = O\!\big(\tfrac{1}{\eta^2}\log\tfrac1\beta\big)$ samples and lateness equal to the empirical $(1-\epsilon)$-quantile plus an $\eta$ slack. Under **bounded delay** $D_s \le \Delta$, a watermark $W(p)=p-\Delta$ gives **zero incompleteness** with lateness exactly $\Delta$ — an exact upper bound, but $\Delta$ is rarely known and often pessimistic.

## 5. Lower Bound

Under **unbounded adversarial delay**, there is an **impossibility**: any watermark policy that guarantees liveness (advances within finite processing-time) must admit nonzero incompleteness, since an adversary can place an event just below the watermark arbitrarily late — analogous to FLP-style impossibility of simultaneous safety+liveness. Information-theoretically, with no assumption on $F_s$, no finite sample bounds the tail $\bar F_s(\delta)$ (the "black swan" event), so **no nontrivial worst-case incompleteness guarantee** is achievable distribution-free. Under shift/non-stationarity, online-quantile regret lower bounds (from prediction-with-experts) apply.

## 6. The Gap

The gap is between **strong stationary/bounded-delay guarantees** (achievable, but assumptions rarely hold) and the **adversarial/non-stationary reality** (where impossibility bites). What is genuinely open: characterizing the *weakest realistic assumption* (e.g., bounded delay *moments*, sub-exponential tails, or bounded distribution drift) under which a watermark policy attains a provable $(L,\epsilon)$ pair, and giving matching online lower bounds. No deployed system today ships a provable lateness bound; closing the gap means a principled estimator with finite-sample, shift-aware guarantees plus a tight impossibility frontier.

## 7. Current Research (as of June 2026)

Directions: (i) **learned/predictive watermarks** with conformal-prediction-style coverage guarantees giving distribution-free *marginal* incompleteness control under exchangeability *(frontier — verify)*; (ii) **per-key / progressive watermarks** that avoid the slowest-source bottleneck; (iii) integrating watermarks with **retraction/revision** so incompleteness is recoverable rather than fatal (DBSP / differential dataflow). Groups: TU Berlin (Markl, Grulich), Google Dataflow team, and CMU/IBM streaming. Conformal-watermark coverage is the most promising bridge between heuristics and provable bounds *(frontier — verify)*.

## 8. Future Work

- Distribution-free watermarks with conformal coverage and adaptive recalibration under drift.
- Tight regret lower bounds for online watermark quantile tracking.
- Compositional lateness bounds through operator graphs (how watermark error propagates across joins/aggregations).
- Cost-aware watermarks that jointly optimize the latency–completeness–resource frontier (see companion problem).

## 9. Key References

- **[Foundational]** Tyler Akidau et al. *MillWheel: Fault-Tolerant Stream Processing at Internet Scale.* PVLDB, 2013. — [DOI](https://doi.org/10.14778/2536222.2536229)
- **[Foundational]** Peter A. Tucker, David Maier, Tim Sheard, Leonidas Fegaras. *Exploiting Punctuation Semantics in Continuous Data Streams.* IEEE TKDE, 2003. — [DOI](https://doi.org/10.1109/TKDE.2003.1198390)
- **[SOTA]** Tyler Akidau et al. *The Dataflow Model.* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2824032.2824076)
- **[Foundational]** A. Dvoretzky, J. Kiefer, J. Wolfowitz. *Asymptotic Minimax Character of the Sample Distribution Function (DKW inequality).* Annals of Math. Statistics, 1956. — [DOI](https://doi.org/10.1214/aoms/1177728174)
- **[Survey]** Martin Hirzel, Robert Soulé, Scott Schneider, Buğra Gedik, Robert Grimm. *A Catalog of Stream Processing Optimizations.* ACM Computing Surveys, 2014. — [DOI](https://doi.org/10.1145/2528412)

## 10. Worked Example

A single source has i.i.d. processing delays (in seconds) sampled as $D = \{1, 2, 2, 3, 8\}$ — four "normal" events and one straggler. We use the fixed-lag watermark $W(p) = p - \delta$, so **lateness** $= \delta$ and **incompleteness** $= \Pr[D > \delta]$, estimated by the empirical tail $\hat{\bar F}(\delta)$.

Pick $\delta = 3$: events with delay $>3$ (just the $D{=}8$ event) miss their window. Empirical incompleteness $= 1/5 = 0.20$ at lateness $3$s. Pick $\delta = 8$: incompleteness $= 0/5 = 0$, but lateness jumps to $8$s — the straggler dominates the cost. This is the $(L,\epsilon)$ trade-off traced by the quantile of $D$.

How many samples justify a target? DKW says $\Pr[\sup_x|\hat F_n(x)-F(x)|>\eta]\le 2e^{-2n\eta^2}$. To pin the empirical CDF within $\eta=0.05$ at confidence $1-\beta=0.95$, solve $2e^{-2n(0.05)^2}=0.05 \Rightarrow n = \ln(40)/(2\cdot 0.0025) \approx 738$ samples. With unbounded adversarial delay, no finite $\delta$ guarantees $\epsilon=0$ (the straggler can be arbitrarily late) — the FLP-flavored impossibility of section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
