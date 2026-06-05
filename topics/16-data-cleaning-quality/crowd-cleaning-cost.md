# Crowd-Powered Cleaning Cost Optimization

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/crowd-cleaning-cost` · **Status:** partially-solved

## 1. Problem Statement
Human-in-the-loop cleaning pipelines (entity resolution, error detection, value repair) issue *questions* to humans or a crowd—each costing money and latency—to resolve uncertainty that automatic methods cannot. The problem: **minimize total human cost subject to a target output quality**, or dually, **maximize quality subject to a budget $B$**.

Variants:
- **Decision:** Given a question pool, budget $B$, and target error $\epsilon$, does a feasible questioning policy exist?
- **Optimization (budgeted):** Choose a (possibly adaptive) sequence of $\le B$ questions maximizing expected quality.
- **Counting/active:** Which subset of candidate pairs/cells to verify so that transitively-inferred labels cover the rest under a constraint model (e.g., cluster consistency in ER).

Difficulty stems from noisy/adversarial workers, correlated answers (transitivity in ER), and the adaptive nature of optimal policies.

## 2. Mathematical Foundations
Model the value of a question set $S$ by a set function $f: 2^{Q} \to \mathbb{R}_{\ge 0}$ (uncertainty reduction, expected labels resolved). When $f$ is **monotone submodular**—$f(S\cup\{q\}) - f(S) \ge f(T\cup\{q\}) - f(T)$ for $S\subseteq T$—the greedy rule gives the classic guarantee
$$f(S_{\text{greedy}}) \ge (1 - 1/e)\, \mathrm{OPT}.$$
Adaptive settings use **adaptive submodularity** (Golovin–Krause), where greedy achieves $(1-1/e)$ of the optimal *policy*. Worker noise is modeled via the **Dawid–Skene** latent-confusion-matrix model; EM and spectral methods recover worker reliabilities $\pi_w$ and true labels $z_i$. In ER, transitivity makes the label space a **partition** (correlation-clustering structure), so independent per-pair questions are wasteful—optimal selection is correlation-clustering-hard.

## 3. State of the Art (SOTA)
- **CrowdER / CrowdDB** (Wang et al., VLDB 2012; Franklin et al., SIGMOD 2011): hybrid human-machine ER and crowd-enabled query operators.
- **Corleone / Falcon** (Gokhale, Das et al., SIGMOD 2014 / 2017): crowdsourced end-to-end ER with machine-learned blocking, scaling crowd cost via active learning.
- **Transitive-relation crowdsourcing** (Wang et al., SIGMOD 2013; Vesdapunt et al., VLDB 2014): exploit transitivity to cut questions, with near-optimal expected-question results.
- **Waldo / quality-aware task assignment** and budget-allocation work (Karger–Oh–Shah, NeurIPS 2011) give order-optimal worker-reliability/budget tradeoffs.

Systems-SOTA combines active learning + transitivity pruning; theory-SOTA gives adaptive-submodular and budget-allocation guarantees that rarely match deployed heuristics.

## 4. Upper Bound
For monotone (adaptive) submodular objectives, greedy yields a $(1-1/e)\approx 0.632$ approximation to optimal expected quality at fixed budget (Nemhauser–Wolsey–Fisher 1978; Golovin–Krause 2011). For ER under transitivity, Vesdapunt et al. give algorithms whose expected number of questions is within a constant factor of the information-theoretic optimum for the partition. Karger–Oh–Shah achieve label error decaying as $e^{-\Theta(q\,\bar{\pi})}$ in budget per task $q$, order-optimal up to constants.

## 5. Lower Bound
Selecting an optimal question set for ER subsumes **correlation clustering**, which is **NP-hard** and **APX-hard**; minimizing questions to certify a partition inherits this. For general submodular maximization under cardinality constraints, $(1-1/e)$ is **tight** under standard assumptions (Feige 1998 for max-coverage; value-oracle lower bound by Nemhauser–Wolsey). Reliability/budget estimation has an **information-theoretic** floor: no policy beats the $e^{-\Theta(q\bar\pi)}$ rate (matching Karger–Oh–Shah). Adaptive policies can also be PSPACE-flavored to compute exactly.

## 6. The Gap
For pure submodular objectives the gap is **closed** ($(1-1/e)$ tight). The genuine openness is in **realistic composite objectives**: transitivity-correlated answers, latency-budget joint optimization, and adversarial/colluding workers break submodularity, so no tight approximation is known. Closing it requires either showing the practical objective is (weakly/adaptive) submodular with a provable curvature bound, or a new hardness reduction capturing the correlation structure.

## 7. Current Research (as of June 2026)
- **LLMs as oracle substitutes:** routing easy questions to an LLM and hard ones to humans, with cost/quality calibration—reframing the budget as a *machine+human* portfolio *(frontier — verify)*.
- **Conformal/abstention-based triggering:** decide which cells to escalate using conformal prediction guarantees on uncertainty *(frontier — verify)*.
- Groups: Berkeley/UW-Madison ER lineage (AnHai Doan, Michael Franklin), Stanford HCI/HoloClean lineage (Christopher Ré, Theodoros Rekatsinas), MIT (Sam Madden).

## 8. Future Work
- Tight approximation for transitivity-correlated, latency-aware budgets.
- Robust policies under colluding/strategic workers (game-theoretic incentive-compatible pricing).
- Unified human+LLM cost models with formal quality certificates (links to repair-quality-certification).
- Online/streaming budget allocation with regret bounds.

## 9. Key References
- **[Foundational]** D. Golovin, A. Krause. *Adaptive Submodularity: Theory and Applications in Active Learning and Stochastic Optimization.* JAIR, 2011. — [arXiv](https://arxiv.org/abs/1003.3967)
- **[Foundational]** A. P. Dawid, A. M. Skene. *Maximum Likelihood Estimation of Observer Error-Rates Using the EM Algorithm.* Applied Statistics, 1979. — [DOI](https://doi.org/10.2307/2346806)
- **[SOTA]** J. Wang, T. Kraska, M. J. Franklin, J. Feng. *CrowdER: Crowdsourcing Entity Resolution.* VLDB, 2012. — [arXiv](https://arxiv.org/abs/1208.1927)
- **[SOTA]** N. Vesdapunt, K. Bellare, N. Dalvi. *Crowdsourcing Algorithms for Entity Resolution.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2732977.2732982)
- **[SOTA]** S. Das et al. *Falcon: Scaling Up Hands-Off Crowdsourced Entity Matching to Build Cloud Services.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3035960)
- **[Foundational]** D. R. Karger, S. Oh, D. Shah. *Iterative Learning for Reliable Crowdsourcing Systems.* NeurIPS, 2011. — [DBLP](https://dblp.org/rec/conf/nips/KargerOS11.html)

## 10. Worked Example

Entity resolution over 4 records $\{a,b,c,d\}$. Blocking proposes 4 candidate pairs as questions, budget $B=2$. Define $f(S)$ = number of record pairs whose match-status becomes *certain* after asking $S$, where transitivity lets answers chain.

Suppose ground truth is $\{a,b,c\}$ one entity, $d$ alone. Marginal gains:
- Ask $(a,b)$: confirms 1 pair → $f=1$.
- Then ask $(b,c)$: confirms $(b,c)$ **and** by transitivity $(a,c)$ → gain $2$, $f=3$.

Greedy picks $(a,b)$ then $(b,c)$ (each the best remaining marginal), certifying 3 of the 3 true-match pairs in $B=2$ questions instead of asking all 3 directly — transitivity saved one question.

The set function here is monotone submodular, so greedy guarantees $f(S_{\text{greedy}}) \ge (1-1/e)\,\mathrm{OPT} \approx 0.63\,\mathrm{OPT}$. But the *partition* structure (correlation clustering) means a worker error on $(b,c)$ also corrupts the inferred $(a,c)$ — the correlated-noise regime of Section 6 where the clean $(1-1/e)$ bound no longer holds.

---
*Part of the [DBMS Research catalog](../../README.md).*
