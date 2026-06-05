# Safe Exploration in Learned Optimizers

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/safe-exploration-optimizers` · **Status:** open

## 1. Problem Statement

An online learned optimizer must *explore* — execute plans it is uncertain about — to improve. Exploration risks running catastrophically slow plans on production queries. The safe-exploration problem: **design an exploration strategy that learns a near-optimal policy while provably bounding the damage** (excess latency, SLA violations) caused by exploratory plan choices.

Variants:

- **Bounded regret (optimization):** minimize cumulative excess latency $R(T)=\sum_t(\text{cost}(\pi_t(q_t))-\text{cost}(\pi^\*(q_t)))$ with $R(T)=o(T)$.
- **Per-query safety (constraint):** guarantee $\text{cost}(\pi_t(q_t))\le \beta\cdot\text{cost}_{\text{baseline}}(q_t)$ for every $t$ w.h.p. (never more than $\beta\times$ slower than the trusted optimizer).
- **Anytime fallback (decision):** detect at plan time, or mid-execution, that a chosen plan is going bad and fall back to a safe plan with bounded wasted work.

These distinguish *cumulative* (regret) from *worst-case-per-step* (constraint) safety; production systems need the latter, but learning theory most naturally delivers the former.

## 2. Mathematical Foundations

Frame online learning as **regret minimization** against the best plan in hindsight. For a contextual-bandit relaxation (context = query features, arm = plan/hint set, loss = latency), EXP4 / LinUCB give $R(T)=\tilde O(\sqrt{KT})$ or $\tilde O(d\sqrt{T})$ regret. Per-query safety maps to **constrained / conservative bandits**: the *conservative bandit* guarantee (Wu et al. 2016, Kazerouni et al. 2017) keeps cumulative reward above $(1-\alpha)$ times a known baseline at all times, by only exploring when an accumulated "safety budget" permits.

Key constructs:

- **Safe set / shielding:** restrict actions to those whose certified cost is within $\beta$ of baseline; explore only inside it (cf. safe RL, Berkenkamp et al. 2017, using Lyapunov / region-of-attraction arguments).
- **High-probability cost certificate:** exploration safety requires an *upper* bound on a candidate plan's latency *before* running it — i.e., a pessimistic/calibrated cost estimate (links to **learned-cost-model-calibration** and AGM-style envelopes). Without a valid upper bound, no per-query guarantee is possible.
- **Optimism vs. caution:** UCB explores by acting on optimistic estimates (latency lower bound), which is the *opposite* of safety (which needs a latency upper bound); reconciling them requires two-sided confidence intervals.

Formally, safe exploration is feasible only if the cost model yields intervals $[\ell(q,p),u(q,p)]$ with valid coverage; safety uses $u$, optimization uses $\ell$.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** *Bao* (Marcus et al., SIGMOD 2021) restricts exploration to a small set of hint sets, each a complete sound plan, bounding worst-case blowup by construction; this is the de facto safe-exploration mechanism in practice. *Steering*/*HybridQO* and timeout-based "kill and replan" loops add anytime fallback. Microsoft's *Steering the query optimizer* line and Amazon Redshift's learned components use conservative deployment (shadow execution, A/B with guardrails) *(frontier — verify)*.
- **Theory-SOTA:** conservative/constrained contextual bandits provide the cleanest provable guarantee, but assume a known reliable baseline and stochastic (not adversarial/drifting) contexts.

## 4. Upper Bound

- **Conservative LinUCB / EXP4:** $\tilde O(d\sqrt{T})$ regret *while* keeping cumulative cost within $(1+\alpha)$ of the baseline for all $T$, in the **stochastic contextual-bandit model** with a known baseline policy (Kazerouni et al. 2017). This transfers to hint-set selection where each arm is a sound plan.
- **Shadow execution:** zero production regret at the cost of $2\times$ resource usage — a trivial but real upper bound on damage (run learned and baseline, commit baseline).

## 5. Lower Bound

- **Exploration is necessary:** any algorithm achieving sublinear regret must occasionally play suboptimal arms; in the worst case a "trap" plan is $\Omega(1)\times$ worse, so *some* per-step damage is unavoidable without a valid cost upper bound — pure information-theoretic exploration lower bound $\Omega(\sqrt{KT})$.
- **No-baseline impossibility:** without a trusted safe fallback or a valid pre-execution latency upper bound, per-query $\beta$-safety is impossible — an adversary can make any unexplored plan arbitrarily slow (OOD/adversarial barrier; links to **learned-component-robustness**).
- **Calibration dependence:** if cost-model intervals lack coverage (miscalibration probability $\eta$), worst-case safety violation probability is $\ge\eta$ — safety inherits the cost model's calibration lower bound.

## 6. The Gap

Open. We can bound *cumulative* damage against a known baseline (conservative bandits) and we can bound *per-query* damage by restricting to sound hint sets (Bao), but we lack a regime that gives **simultaneous** sublinear regret *and* tight per-query safety while still exploring genuinely novel plans (beyond a fixed hint set) under workload drift. Closing it needs valid, tight pre-execution cost upper bounds — tying safe exploration to progress on calibrated/pessimistic cost models.

## 7. Current Research (as of June 2026)

- Hint-set / safe-action-set design as the deployable safety mechanism; learned component as re-ranker with a hard fallback to the native optimizer (MIT Kraska/Marcus group).
- Anytime mid-execution monitoring: detect cardinality/latency divergence at runtime and re-optimize (adaptive query processing meets learned optimizers) — robust query execution / re-optimization (TUM, MSR) *(frontier — verify)*.
- Conservative / constrained bandit and safe-RL formulations imported into optimizer learning, with shielding by a pessimistic cost envelope *(frontier — verify)*.
- Shadow/canary deployment and counterfactual (off-policy) evaluation to learn without online risk.

## 8. Future Work

- Tight two-sided cost certificates enabling exploration outside a fixed hint set with per-query safety.
- Regret bounds under *adversarial / drifting* contexts, not just stochastic.
- Formal "safety budget" accounting integrated with SLA semantics (latency percentiles, not means).
- Composable safety when multiple learned components (optimizer + cost model + index advisor) explore simultaneously.

## 9. Key References

- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838) — [DBLP](https://dblp.org/rec/conf/sigmod/MarcusNMTAK21.html)
- **[Foundational]** Kazerouni, Ghavamzadeh, Abbasi-Yadkori, Van Roy. *Conservative Contextual Linear Bandits.* NeurIPS, 2017. — [arXiv](https://arxiv.org/abs/1611.06426) — [DBLP](https://dblp.org/rec/conf/nips/KazerouniGAR17.html)
- **[Foundational]** Wu, Shariff, Lattimore, Szepesvári. *Conservative Bandits.* ICML, 2016. — [arXiv](https://arxiv.org/abs/1602.04282) — [PMLR](http://proceedings.mlr.press/v48/wu16.html)
- **[Foundational]** Berkenkamp, Turchetta, Schoellig, Krause. *Safe Model-Based Reinforcement Learning with Stability Guarantees.* NeurIPS, 2017. — [arXiv](https://arxiv.org/abs/1705.08551) — [NeurIPS](https://proceedings.neurips.cc/paper/2017/hash/766ebcd59621e305170616ba3d3dac32-Abstract.html)
- **[Foundational]** Markl, Raman, et al. *Robust Query Processing Through Progressive Optimization.* SIGMOD, 2004. — [DOI](https://doi.org/10.1145/1007568.1007642)

## 10. Worked Example

Take a Bao-style learner with $K=3$ hint sets per query; the native optimizer is the trusted baseline. For one query $q$ the true latencies are: baseline $\text{cost}_{\text{base}}=100$ ms, arm $a_1=70$ ms (a genuine win), arm $a_2=400$ ms (a trap). Set per-query safety factor $\beta=1.5$, so any plan above $150$ ms is unsafe.

Suppose the calibrated cost model returns intervals $[\ell,u]$: $a_1\to[60,95]$, $a_2\to[120,460]$. The safe set keeps only arms with **upper** bound $u\le\beta\cdot\text{cost}_{\text{base}}=150$. Then $a_1$ qualifies ($u=95\le150$) but $a_2$ is excluded ($u=460>150$) — even though its optimistic $\ell=120$ would tempt a UCB explorer. Playing $a_1$ gives realized excess latency $70-100=-30$ ms (a saving), never violating $\beta$.

Conservative-bandit accounting: with budget slack $\alpha=0.1$, after $t$ safe-or-better plays the accumulated cushion is $\sum(\text{cost}_{\text{base}}-\text{cost})\ge \alpha\sum\text{cost}_{\text{base}}$; only once the cushion exceeds the worst-case downside of an untried arm may the learner spend it on exploration. Here the $-30$ ms per query builds cushion while $a_2$ stays shielded until its interval tightens below $150$ ms — illustrating safety from the **upper** bound, exploration value from the **lower**.

---
*Part of the [DBMS Research catalog](../../README.md).*
