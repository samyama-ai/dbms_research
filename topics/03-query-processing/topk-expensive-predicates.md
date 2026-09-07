---
id: 03-query-processing/topk-expensive-predicates
title: "Top-k with expensive or ML predicates"
topic: 03-query-processing
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Top-k with expensive or ML predicates

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/topk-expensive-predicates` · **Status:** open

## 1. Problem Statement

Return the $k$ highest-scoring objects when the scoring function — or a filtering predicate — is an **expensive UDF or model inference** (an LLM call, a CNN/embedding model, a remote API, a costly numerical kernel). Unlike the classic top-$k$ middleware model, the dominant cost is not list access but **invoking the scorer**, which may cost milliseconds to seconds per tuple and have variable latency. The objective is to return the exact (or guaranteed-correct) top-$k$ while **minimizing the number/cost of expensive predicate evaluations**, exploiting cheap proxies, ordering, and early termination ("short-circuiting").

Variants: (a) **expensive boolean predicate + cheap score** (predicate placement / ordering); (b) **expensive score itself** (the score *is* the model output); (c) **probabilistic / approximate guarantees** (return the true top-$k$ with probability $\ge 1-\delta$ using a cheap proxy + selective exact calls); (d) **batched inference** where the cost is sub-additive (GPU batching changes the cost algebra). Decision: is the cheap-proxy top-$k$ provably the true top-$k$? Optimization: minimize total inference cost (or dollar cost / latency) subject to a correctness guarantee.

## 2. Mathematical Foundations

Classic **predicate ordering** (Hellerstein–Stonebraker "predicate migration"; Krishnamurthy–Boral–Zaniolo) models a conjunctive filter of predicates $p_i$ with cost $c_i$ and selectivity $s_i$; the optimal serial order sorts by **rank** $\frac{1-s_i}{c_i}$ (the "rank ordering" / pipelined-filter problem), provably optimal for independent predicates; with correlations it becomes NP-hard. For **expensive scoring**, the relevant frame is an **optimal stopping / probing** problem: a cheap proxy $\hat f(o)$ bounds the true $f(o)$ within $[\hat f - \epsilon, \hat f + \epsilon]$; an object can be pruned without an exact call if its upper bound $< $ the $k$-th largest confirmed lower bound — a Fagin-style threshold on *bounds*, not list positions. Probabilistic guarantees use **concentration (Hoeffding/Bernstein)** and **PAC-style** sample bounds; cascade design connects to **Wald's SPRT** and learned-cascade theory (Viola–Jones). Batched cost is modeled as a **submodular** cost over evaluation sets, making optimal batch selection an instance of submodular minimization under correctness constraints.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Optimal serial predicate ordering by rank is solved for independent predicates; with conditional/expensive predicates and joins, optimal placement is NP-hard and only approximation/heuristics exist. There is **no clean instance-optimality theory** for top-$k$ where the scorer is the expensive object. **Systems-SOTA:** ML-in-DB systems pioneered the practical techniques: **NoScope** and **probabilistic predicates** (Lu–Chowdhery–Kandula–Chaudhuri) train cheap proxy models / specialized filters to short-circuit expensive CNN calls with statistical guarantees; **BlazeIt**, **TASTI**, and **SUPG** (Kang et al., Stanford) give approximate selection/aggregation with probabilistic top-$k$/recall guarantees over video. Modern **LLM-query engines** — Lotus/semantic operators (Stanford), Palimpzest (MIT), LOTUS/DocETL — push semantic top-$k$/filter with proxy-ranking and cascade short-circuiting *(frontier — verify)*. Vector databases use ANN as the cheap proxy then re-rank with the exact model.

## 4. Upper Bound

For **independent expensive boolean predicates**, the rank ordering $\frac{1-s_i}{c_i}$ is provably cost-optimal (RAM / serial-pipeline cost model). For **expensive scoring with a bounded-error proxy** $|\hat f - f|\le \epsilon$, a threshold algorithm on bounds evaluates the exact model only on the "uncertain band" — objects whose $[\,\hat f-\epsilon, \hat f+\epsilon\,]$ interval overlaps the current $k$-th threshold — giving cost $O(k + |\text{band}|)$ exact calls, which is *output-/instance-sensitive* but has no proven constant-factor optimality in general. **Probabilistic** variants (SUPG-style) return a top-$k$ with recall $\ge \tau$ at confidence $1-\delta$ using $O(\epsilon^{-2}\log\frac1\delta)$ proxy-calibration samples, exact calls only near the boundary. Cascades give expected cost = $\sum_i (\prod_{j<i}\text{pass}_j)\,c_i$, minimized by ordering and threshold tuning.

## 5. Lower Bound

Optimal **predicate placement with correlations / joins** is NP-hard (reduction from sequencing/scheduling and from optimal join+selection ordering). For **adversarial proxy error**, no algorithm can prune any object without an exact call: if the proxy is uninformative, $\Omega(N)$ exact evaluations are forced (information-theoretic — the scorer is a black box, so any unevaluated object could be the maximum; adversary argument). Probabilistic guarantees inherit **sample-complexity lower bounds** $\Omega(\epsilon^{-2}\log\frac1\delta)$ from PAC/concentration theory. Thus there is **no instance-optimal exact algorithm** in the black-box-scorer model without proxy assumptions — the hardness is intrinsic to treating the model as an oracle.

## 6. The Gap

This is **genuinely open**. The classic theory (rank ordering, TA) does not cover the regime where (1) the score *is* the expensive object, (2) cheap proxies have *learned, data-dependent* error rather than worst-case bounds, and (3) **batched GPU/LLM inference** makes per-tuple cost non-additive and order-dependent. We lack: a cost model unifying proxy error, batch economics, and dollar/latency budgets; an instance-optimality notion for expensive-scorer top-$k$; and provable end-to-end guarantees for cascades of learned proxies. Systems (NoScope, SUPG, Lotus, Palimpzest) deliver empirical wins but with guarantees that are either heuristic or rely on calibration assumptions that adversarial inputs can violate. Closing it requires a theory of **optimal oracle-probing under learned bounds with batch-aware cost**.

## 7. Current Research (as of June 2026)

Hot directions: **semantic query operators over LLMs** with cost-based optimization and proxy cascades — Lotus / semantic operators and Palimpzest emphasize optimizing accuracy–cost–latency tradeoffs for LLM top-$k$/filter/join *(frontier — verify)*; **model cascades and learned proxies with statistical guarantees** (Stanford DAWN lineage: Kang, Zaharia, Bailis); **approximate selection/aggregation with confidence** (SUPG, TASTI); **ANN-as-proxy + exact re-rank** in vector DBs. Batch-aware and budget-aware planning, and conformal-prediction-style guarantees for proxy calibration, are emerging. People/groups: Zaharia, Guestrin, Bailis (Stanford/DBOS), Madden, Cafarella (MIT, Palimpzest), Kandula/Chaudhuri (Microsoft, probabilistic predicates), Kang (Illinois).

## 8. Future Work

- A cost model and optimizer that jointly schedules proxy and exact calls under batch (GPU/LLM) economics and dollar/latency budgets.
- Provable instance- or competitive-optimality for top-$k$ with learned proxies (e.g., via conformal bounds) rather than heuristic thresholds.
- Robust guarantees under distribution shift, where calibrated proxy error no longer holds.
- Integration of semantic/LLM operators into relational optimizers with cardinality- and cost-estimation for inference.
- Adaptive cascades that learn proxy thresholds online with regret bounds.

## 9. Key References

- **[Foundational]** Hellerstein, Stonebraker. *Predicate Migration: Optimizing Queries with Expensive Predicates.* SIGMOD, 1993. — [DOI](https://doi.org/10.1145/170036.170078)
- **[Foundational]** Fagin, Lotem, Naor. *Optimal Aggregation Algorithms for Middleware.* PODS 2001 / JCSS, 2003. — [arXiv](https://arxiv.org/abs/cs/0204046)
- **[SOTA]** Lu, Chowdhery, Kandula, Chaudhuri. *Accelerating Machine Learning Inference with Probabilistic Predicates.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3183751)
- **[SOTA]** Kang, Emmons, Abuzaid, Bailis, Zaharia. *NoScope: Optimizing Neural Network Queries over Video at Scale.* VLDB, 2017. — [arXiv](https://arxiv.org/abs/1703.02529)
- **[SOTA]** Kang, Guibas, Bailis, Hashimoto, Zaharia. *Approximate Selection with Guarantees using Proxies (SUPG).* VLDB, 2020. — [arXiv](https://arxiv.org/abs/2004.00827)
- **[SOTA]** Liu, Russo, Cafarella, Madden et al. *Palimpzest: Optimizing AI-Powered Analytics with Declarative Query Processing.* CIDR, 2025 *(frontier — verify)*. — [arXiv](https://arxiv.org/abs/2405.14696)

## 10. Worked Example

Find the top-$k=1$ image by an expensive scorer $f$ (1 s/call). A cheap proxy $\hat f$ obeys $|\hat f - f|\le \epsilon=0.1$. Five images:

| obj | $\hat f$ | bound $[\hat f-\epsilon,\hat f+\epsilon]$ |
|-----|------|------|
| A | 0.92 | [0.82, 1.02] |
| B | 0.70 | [0.60, 0.80] |
| C | 0.55 | [0.45, 0.65] |
| D | 0.30 | [0.20, 0.40] |
| E | 0.15 | [0.05, 0.25] |

Probe in proxy order. Call $f(A)=0.85$ (confirmed lower bound $L=0.85$). Now prune any object whose **upper** bound $<L$: B's upper $0.80<0.85$, so are C, D, E. All four are pruned without an exact call. So only **1 exact call** instead of 5 — cost $O(k+|\text{band}|)$, where the uncertain band (intervals overlapping $L=0.85$) is empty here. Had $f(A)$ returned $0.78$, B's interval $[0.60,0.80]$ would overlap, forcing a second exact call on B to break the tie.

---
*Part of the [DBMS Research catalog](../../README.md).*
