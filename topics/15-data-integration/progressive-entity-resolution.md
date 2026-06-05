# Progressive Entity Resolution Scheduling

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/progressive-entity-resolution` · **Status:** partially-solved

## 1. Problem Statement

**Entity resolution (ER)** identifies records that refer to the same real-world entity. *Progressive* (a.k.a. *pay-as-you-go*) ER targets settings where the full quadratic comparison space cannot be exhausted within the available budget: the goal is to **order/schedule candidate comparisons** so that, at any prefix of the schedule, as many true matches as possible have been discovered.

Formally, let $C = \{c_1, \dots, c_m\}$ be candidate record pairs, each with an unknown ground-truth label $y(c) \in \{\text{match}, \text{non-match}\}$ and a known cost $w(c) > 0$ (comparison/labeling work). Given a budget $B$, choose an ordering $\pi$ of (a subset of) $C$ to **maximize matches recovered as a function of cumulative cost**:
$$\max_{\pi}\; \int_0^{B} \big|\{c : \pi\text{-prefix cost} \le t,\; y(c)=\text{match}\}\big|\, dt \quad\text{(area under the recall–cost curve).}$$

Variants: **decision** (can $k$ matches be found within cost $B$?); **optimization** (maximize AUC of recall–cost, or matches-at-$B$); **anytime** with **quality bounds** (report, at each step, a certified lower/upper bound on remaining recall). The labels $y$ are revealed only upon spending $w(c)$, making this an **online/sequential decision** problem under uncertainty.

## 2. Mathematical Foundations

The offline oracle problem (labels known) is a **knapsack/scheduling** problem; maximizing matches-at-budget with uniform cost is trivial offline but the realistic objective — maximizing the **area under the recall–cost curve** — is equivalent to **min-sum / weighted-completion-time scheduling** ($1\,|\,|\sum w_j C_j$-style), solvable offline by Smith's ratio rule.

Online, candidates are scored by a **match probability** $p(c)=\Pr[y(c)=\text{match}]$ from a learned model or blocking signal. Greedy scheduling by **expected benefit-per-cost** $p(c)/w(c)$ is the canonical heuristic. When the discovery objective exhibits **submodularity** (diminishing returns from resolving overlapping clusters), greedy attains a $(1-1/e)$ guarantee against the offline-expectation optimum; with matroid/knapsack budget constraints, $(1-1/e)$ via continuous-greedy applies. **Transitivity** couples decisions: resolving $a\!\sim\!b$ and $b\!\sim\!c$ implies $a\!\sim\!c$, so the realized benefit is the size of newly merged clusters — naturally modeled as coverage over a dynamically revealed graph, where anytime bounds come from optimistic (all-remaining-match) and pessimistic completions.

## 3. State of the Art (SOTA)

- **Theory/algorithms.** Whang, Marmaros, Garcia-Molina, *Pay-As-You-Go ER* (ICDE 2013) introduced hints and progressive sorted-neighborhood/blocking schedules. Altowim, Kalashnikov, Mehrotra, *Progressive Approach to Relational ER* (VLDB 2014) optimize a benefit/cost schedule over a resolution plan.
- **Systems.** Papenbrock, Heise, Naumann, *Progressive Duplicate Detection* (TKDE 2015) — progressive sorted neighborhood and progressive blocking. **JedAI** (Papadakis et al.) and **pyJedAI** provide progressive/meta-blocking pipelines; **Magellan/DeepMatcher** ecosystems add learned matchers. Simonini et al., *Schema-agnostic progressive ER* (TKDE 2019).
- **Learned schedulers.** Recent work uses deep matcher confidence and bandit-style ordering to drive the schedule.

## 4. Upper Bound

For the **submodular coverage** formulation under a knapsack budget, greedy / lazy-greedy and continuous-greedy give a $\big(1 - 1/e\big)$-approximation to the expected number of resolved entities, in the RAM model, with near-linear evaluations using **lazy (CELF) evaluation** of marginal gains. For the recall–cost AUC objective with known scores, Smith-rule ordering by $p(c)/w(c)$ is **optimal for the expected-completion-time relaxation**. Blocking reduces the candidate set from $O(n^2)$ to near-linear, after which scheduling is over $m \ll n^2$ pairs.

## 5. Lower Bound

Maximizing coverage/matches under a budget is **NP-hard** (reduction from max-coverage / knapsack), and **inapproximable beyond $1-1/e$** unless P=NP (Feige's threshold for max-coverage). The genuinely online variant — where labels and even existence of profitable comparisons are revealed only on payment — admits **no constant competitive ratio without distributional assumptions** (adversarial label placement defeats any deterministic order); meaningful guarantees require stochastic/Bayesian models or secretary-style arrival assumptions. Certifying anytime recall bounds is at least as hard as estimating the unseen match mass, linking it to **unseen-species / support estimation** lower bounds (Valiant–Valiant).

## 6. The Gap

Offline-expectation greedy is tight ($1-1/e$). The open gap is the **online–offline gap**: how much recall is lost because scores $p(c)$ are imperfect and labels are revealed sequentially, and what **anytime certified bounds** are achievable without ground truth. No matching upper/lower bound is known for the adversarial-but-calibrated regime, and the dependence on **blocking quality** (recall ceiling of the candidate set) is not characterized tightly.

## 7. Current Research (as of June 2026)

- Learned, **uncertainty-aware progressive ordering** combining deep matcher calibration with bandit/active-learning schedulers (Papadakis, Naumann, Christophides groups). *(frontier — verify)*
- **LLM-assisted matchers** as the comparison oracle, where cost is token/$ budget and progressive scheduling minimizes LLM calls per recovered match. *(frontier — verify)*
- Progressive ER with **provable anytime recall estimators** via capture–recapture sampling of the unresolved space. *(frontier — verify)*

## 8. Future Work

- Tight competitive analysis under calibrated-score / stochastic-arrival models.
- Joint optimization of **blocking + scheduling** (closing the recall ceiling and the order simultaneously).
- Cost models that mix human, LLM, and rule-based oracles with heterogeneous accuracy.
- Distribution-free, certified anytime recall/precision bounds.

## 9. Key References

- **[Foundational]** S. E. Whang, D. Marmaros, H. Garcia-Molina. *Pay-As-You-Go Entity Resolution.* IEEE TKDE / ICDE, 2013.
- **[SOTA]** Y. Altowim, D. V. Kalashnikov, S. Mehrotra. *Progressive Approach to Relational Entity Resolution.* VLDB, 2014.
- **[SOTA]** T. Papenbrock, A. Heise, F. Naumann. *Progressive Duplicate Detection.* IEEE TKDE, 2015.
- **[Survey]** G. Papadakis, E. Ioannou, E. Thanos, T. Palpanas. *The Four Generations of Entity Resolution.* Morgan & Claypool (Synthesis Lectures), 2021.
- **[Foundational]** G. L. Nemhauser, L. A. Wolsey, M. L. Fisher. *An analysis of approximations for maximizing submodular set functions.* Math. Programming, 1978. ($1-1/e$ greedy.)
- **[Foundational]** U. Feige. *A threshold of $\ln n$ for approximating set cover.* JACM, 1998.

---
*Part of the [DBMS Research catalog](../../README.md).*
