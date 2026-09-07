---
id: 15-data-integration/crowd-er-question-selection
title: "Crowd/Human-in-the-Loop ER Optimization"
topic: 15-data-integration
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Crowd/Human-in-the-Loop ER Optimization

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/crowd-er-question-selection` · **Status:** partially-solved

## 1. Problem Statement

Machine matchers leave an **uncertain region** of record pairs. Crowd/human-in-the-loop ER asks an oracle (crowd worker, expert, or LLM judge) boolean questions "$a \equiv b$?" to **certify** the final clustering, exploiting **transitivity** to skip questions whose answers are logically implied. The objective: select the **minimum number (or cost) of questions** whose answers determine the entire ER partition with the required confidence.

Two regimes. **Deterministic / oracle-correct:** answers are perfect; minimize questions to fully resolve the partition exploiting transitivity (if $a\equiv b$ and $b\equiv c$ then $a\equiv c$ is free; if $a\not\equiv b$ and $b\equiv c$ then $a\not\equiv c$ is free). **Noisy:** answers err independently with probability $p$; minimize questions (with repetition for confidence) to recover the partition with error $\le \delta$.

Variants: **batch / non-adaptive** (choose all questions up front) vs. **adaptive / sequential** (choose next question given prior answers); **decision** (can the partition be certified within budget $B$?) and **optimization** (minimize expected cost). This is a **query-complexity** problem on an unknown partition / clustering oracle.

## 2. Mathematical Foundations

The hidden ground truth is a partition $\mathcal{P}^\star$ of $n$ records into $k$ clusters; questions reveal the **same-cluster relation**, an equivalence relation. **Transitive closure** turns answers into a partial knowledge state; the task is **active learning of an equivalence relation / clustering with same-cluster queries**.

- **Lower bound:** even with a perfect oracle, $\Omega(nk)$ same-cluster queries are needed to learn an arbitrary $k$-partition; with a side **similarity matrix** of quality (e.g., a margin/SDP signal), Mazumdar–Saha showed query complexity drops to $O(nk \cdot \frac{\log n}{\text{signal}})$ and characterized **information-theoretic thresholds** tied to the SDP/spectral gap.
- **Adaptivity & transitivity:** Wang et al.'s *CrowdER* and Vesdapunt–Bellare–Dalvi (VLDB 2014) analyze the **expected number of questions** under transitivity; ordering by "likely-match-first" minimizes wasted queries because confirming a match collapses many pairs.
- **Noise:** repetition + majority/Bayesian aggregation yields per-edge confidence; combining noisy edges into a clustering is **correlation clustering / community detection** with query access, with thresholds governed by **information theory (KL divergence of the answer channel)**.

## 3. State of the Art (SOTA)

- **Foundational systems.** Wang, Kraska, Franklin, Feng — *CrowdER: Crowdsourcing Entity Resolution* (VLDB 2012); Whang, Lofgren, Garcia-Molina — *Question Selection for Crowd ER* (VLDB 2013) (probabilistic question ordering); Vesdapunt, Bellare, Dalvi — *Crowdsourcing Algorithms for Entity Resolution* (VLDB 2014) (transitive-closure-optimal ordering, hybrid human-machine).
- **Theory-SOTA.** Mazumdar, Saha — *Clustering with Noisy Queries* (NeurIPS 2017) — tight query-complexity with side information and noise. Firmani, Saha, Srivastava — *Online Entity Resolution Using an Oracle* (VLDB 2016) — adaptive labeling with recall guarantees.
- **Hybrid/learned.** *Corleone/Falcon* (Doan group) hands-off crowd ER; LLMs increasingly serve as the oracle.

## 4. Upper Bound

With a perfect oracle and a clustering side-signal, **$O\!\big(nk \cdot \frac{\log n}{\gamma}\big)$** same-cluster queries suffice to recover a $k$-partition ($\gamma$ = signal strength; Mazumdar–Saha), RAM/query model. Pure-oracle, no side info: $O(nk)$ adaptive queries are sufficient and necessary. For ER with transitivity, **"benefit-first" adaptive ordering** (label highest-match-probability pairs first) yields near-optimal expected question count (Vesdapunt et al.), and **non-adaptivity costs at most a logarithmic factor** in many regimes. Under i.i.d. noise $p<1/2$, $O(\log(1/\delta))$ repetitions per decisive edge achieve global error $\delta$.

## 5. Lower Bound

Learning an arbitrary $k$-partition requires **$\Omega(nk)$ same-cluster queries** (adversary / information-theoretic), tight against the upper bound. With noisy answers, recovery below an **information-theoretic threshold** (function of the channel KL divergence and cluster sizes) is impossible regardless of query budget (Mazumdar–Saha; community-detection thresholds). Selecting the **minimum certifying question set** offline (knowing answers) is NP-hard in the weighted/cost version (reduces to weighted set-cover-like minimum transitive-reduction certification). **Adaptivity gap** lower bounds show some instances force non-adaptive strategies to spend a $\Theta(\log n)$ factor more.

## 6. The Gap

The **pure-oracle** query complexity is **closed** ($\Theta(nk)$), and noisy thresholds are tight in the planted/SBM model. Open pieces: (1) **exact optimal adaptive cost** under realistic, *correlated, non-i.i.d.* worker errors and per-worker reliability; (2) tight bounds when the side-information matcher is **miscalibrated** (real ER scores, not idealized signal); (3) the **non-adaptive vs. adaptive gap** for transitivity-aware ER with heterogeneous question costs is not pinned down. Closing requires error models that match real crowds/LLMs and matching lower bounds for cost-weighted, transitivity-constrained selection.

## 7. Current Research (as of June 2026)

- **LLMs as the oracle:** minimizing prompt/$ cost to certify ER, modeling LLM answers as a *biased, correlated* channel (self-consistency, calibration). *(frontier — verify)*
- **Active correlation clustering with same-cluster queries** at scale, combining ANN-blocking side signal with query-efficient recovery (Saha, Srivastava, Mazumdar lines). *(frontier — verify)*
- Worker-reliability-aware adaptive selection (EM over worker confusion matrices) with PAC-style certification. *(frontier — verify)*

## 8. Future Work

- Optimal cost-weighted, transitivity-aware question selection under correlated noise.
- Tight adaptivity gaps for heterogeneous-cost human/LLM oracles.
- Certified ER ("here is a proof the partition is correct with prob. $\ge 1-\delta$") with minimal human effort.
- Integrating question selection with progressive/incremental ER pipelines.

## 9. Key References

- **[Foundational]** J. Wang, T. Kraska, M. J. Franklin, J. Feng. *CrowdER: Crowdsourcing Entity Resolution.* VLDB, 2012. — [DOI](https://doi.org/10.14778/2350229.2350263)
- **[Foundational]** S. E. Whang, P. Lofgren, H. Garcia-Molina. *Question Selection for Crowd Entity Resolution.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2536336.2536337)
- **[SOTA]** N. Vesdapunt, K. Bellare, N. Dalvi. *Crowdsourcing Algorithms for Entity Resolution.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2732977.2732982)
- **[SOTA]** A. Mazumdar, B. Saha. *Clustering with Noisy Queries.* NeurIPS, 2017. — [arXiv](https://arxiv.org/abs/1706.07510)
- **[SOTA]** D. Firmani, B. Saha, D. Srivastava. *Online Entity Resolution Using an Oracle.* VLDB, 2016. — [DOI](https://doi.org/10.14778/2876473.2876474)
- **[Survey]** A. Doan, et al. *Human-in-the-Loop Data Integration.* VLDB tutorial / Magellan papers, 2017–2018. — [DOI](https://doi.org/10.14778/3137765.3137833)

## 10. Worked Example

Five records $\{a,b,c,d,e\}$ with hidden ground-truth partition $\{a,b,c\},\{d,e\}$ ($k=2$ clusters). A perfect oracle answers "$x\equiv y$?". Naively, all $\binom{5}{2}=10$ pairs could be asked — but transitivity makes most free.

**Benefit-first adaptive trace** (label highest-match-probability pairs first):

1. Ask $a\equiv b$ → **yes**. Knowledge: $\{a,b\}$.
2. Ask $b\equiv c$ → **yes**. By transitivity $a\equiv c$ is **free**. Knowledge: $\{a,b,c\}$.
3. Ask $d\equiv e$ → **yes**. Knowledge: $\{d,e\}$.
4. Ask $a\equiv d$ → **no**. By transitivity $a\not\equiv e,\ b\not\equiv d,\ b\not\equiv e,\ c\not\equiv d,\ c\not\equiv e$ are **all free** (a $-$ between any member of $\{a,b,c\}$ and any of $\{d,e\}$).

Total: **4 questions** instead of 10. This matches the $\Theta(nk)$ bound: with $n=5,k=2$, $nk=10$, and the constant is small here because clusters are large. A bad (random) order — e.g. asking cross-cluster pairs early — wastes queries that transitivity cannot later collapse, illustrating the adaptivity advantage.

---
*Part of the [DBMS Research catalog](../../README.md).*
