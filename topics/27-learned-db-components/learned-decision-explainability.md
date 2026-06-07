---
id: 27-learned-db-components/learned-decision-explainability
title: "Explainability and Debuggability of Learned Decisions"
topic: 27-learned-db-components
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Explainability and Debuggability of Learned Decisions

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/learned-decision-explainability` · **Status:** open

## 1. Problem Statement

When a *classical* query optimizer picks a bad plan, a DBA can read the cost model, inspect cardinality estimates, and pin the error to a specific selectivity assumption or join-order rule. When a *learned* optimizer, index, or knob-tuner makes the same costly mistake, the decision is an opaque function $f_\theta$ of high-dimensional features. The **explainability/debuggability problem**: produce faithful, actionable explanations of *why* a learned component made a specific decision, sufficient to (a) audit it for correctness/safety, (b) localize the cause of a regression, and (c) repair or guard it.

- **Decision variant:** Was a specific costly choice (this plan, this hint, this knob) caused by a recognizable input pattern or by model error?
- **Attribution variant:** Which features/training examples are responsible for the prediction (feature attribution, influence functions)?
- **Counterfactual variant:** What minimal change to the input would have flipped the decision to the correct one?
- **Verification variant:** Certify that $f_\theta$ never violates a safety invariant (e.g. never proposes a Cartesian product on huge inputs) over an input region.

## 2. Mathematical Foundations

Feature attribution rests on the **Shapley value** from cooperative game theory. For prediction $f(x)$ over features $\mathcal{N}$, the attribution to feature $i$ is

$$
\phi_i = \sum_{S \subseteq \mathcal{N}\setminus\{i\}} \frac{|S|!\,(|\mathcal{N}|-|S|-1)!}{|\mathcal{N}|!}\big[f(S\cup\{i\}) - f(S)\big],
$$

the unique attribution satisfying efficiency, symmetry, dummy, and additivity (Shapley 1953; SHAP, Lundberg–Lee 2017). Exact computation is **#P-hard** in general, forcing sampling/approximation. **Influence functions** (Koh–Liang 2017) attribute a prediction to training points via $\mathcal{I}(z, z_{\text{test}}) = -\nabla_\theta \ell(z_{\text{test}})^\top H_\theta^{-1} \nabla_\theta \ell(z)$ with $H_\theta$ the Hessian — exact in convex models, approximate otherwise.

Verification of safety invariants over input polytopes reduces to **mixed-integer feasibility** for ReLU networks (Reluplex/Marabou), which is **NP-complete** (Katz et al., 2017). Counterfactual explanations are the optimization $\min_{x'} d(x,x') \text{ s.t. } f(x') = y^\*$, again NP-hard for piecewise-linear $f$.

## 3. State of the Art (SOTA)

- **Theory/ML-SOTA:** SHAP/KernelSHAP and integrated gradients (Sundararajan et al., 2017) for attribution; Reluplex/**Marabou** (Katz et al., CAV 2017/2019) and $\alpha,\beta$-CROWN for neural verification; influence functions for training-data attribution.
- **Systems-SOTA:** explainability is *nascent* for DB. **Bao** (SIGMOD 2021) is deliberately interpretable — it learns to *choose among optimizer hint-sets*, so every decision is a named, human-readable hint and falls back to the classical optimizer. **Steering/LEON**-style approaches expose the model's plan-cost prediction so DBAs can compare to the cost model. Most learned cardinality estimators (MSCN, DeepDB) offer little native explanation.

## 4. Upper Bound

For *constrained-action* learned optimizers (Bao), explanation is essentially free: the action space is a small set of named hint-sets, so an explanation is $O(1)$ — "the model selected hint-set $k$ because its predicted cost was lowest." For attribution, KernelSHAP gives unbiased estimates in $O(m)$ model evaluations for $m$ coalitions; TreeSHAP computes exact Shapley values for tree ensembles in $O(TLD^2)$ (polynomial) — relevant since many DB learned components (Bao, gradient-boosted estimators) are tree-based.

## 5. Lower Bound

Exact Shapley attribution is **#P-hard** for general models (Deng–Papadimitriou 1994 for the game-value setting; carries to SHAP). Verifying a single safety property of a ReLU network is **NP-complete** (Katz et al. 2017). Computing minimal counterfactuals for piecewise-linear models is **NP-hard**. These hold in the standard model of Boolean/MILP encodings; thus *faithful, exact* explanation of an expressive learned DB component is intractable in the worst case — only approximate or restricted-architecture explanations are efficient.

## 6. The Gap

Two gaps. (1) **Faithfulness vs. tractability:** exact explanations are #P/NP-hard, while cheap approximations (LIME, sampled SHAP) can be *unfaithful* — no DB-specific result bounds the approximation error against optimizer regret. (2) **Decision-relevance:** generic ML attribution explains the *prediction* (e.g. an estimated cardinality) but DBAs need to explain the *downstream consequence* (the chosen plan, the latency regression). Bridging from feature attribution to plan-level causal blame is **open**. Closing it needs DB-aware explanation primitives with error guarantees tied to query cost.

## 7. Current Research (as of June 2026)

Directions: constrained/interpretable-by-design optimizers (Bao, hint-steering) preferred over end-to-end black boxes; provenance-style "why this plan" tracing of model inputs; influence-function debugging to find the training queries that caused a regression; formal verification of safety guards on learned knob tuners *(frontier — verify)*. Groups: Marcus/Kraska (interpretable optimization), Katz/Barrett (neural verification, Stanford/Hebrew U.), Lundberg (SHAP). There is rising interest in LLM-generated natural-language explanations of plan choices, with the open worry that such narratives are *plausible but unfaithful* *(frontier — verify)*.

## 8. Future Work

- Plan-level causal attribution: trace a latency regression to a specific model error with a guaranteed bound.
- Certified safety guards (never propose obviously catastrophic plans) via cheap verification.
- Faithfulness metrics for DB explanations tied to realized query cost, not surrogate fidelity.
- Influence-based "training-set debugging" tools integrated into the optimizer feedback loop.

## 9. Key References

- **[Foundational]** Lundberg, Lee. *A Unified Approach to Interpreting Model Predictions (SHAP).* NeurIPS 2017. — [arXiv](https://arxiv.org/abs/1705.07874)
- **[Foundational]** Koh, Liang. *Understanding Black-box Predictions via Influence Functions.* ICML 2017. — [arXiv](https://arxiv.org/abs/1703.04730)
- **[SOTA]** Katz, Barrett, Dill, Julian, Kochenderfer. *Reluplex: An Efficient SMT Solver for Verifying Deep Neural Networks.* CAV 2017. — [arXiv](https://arxiv.org/abs/1702.01135)
- **[SOTA]** Marcus, Negi, Mao, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[Foundational]** Shapley. *A Value for n-Person Games.* In Contributions to the Theory of Games, 1953. — [DOI](https://doi.org/10.1515/9781400881970-018)
- **[Survey]** Sundararajan, Taly, Yan. *Axiomatic Attribution for Deep Networks (Integrated Gradients).* ICML 2017. — [arXiv](https://arxiv.org/abs/1703.01365)

## 10. Worked Example

A Bao-style optimizer chooses among three hint-sets for a join query; a gradient-boosted model predicts plan cost from three features: $x_1$ = estimated rows of relation $A$, $x_2$ = join selectivity, $x_3$ = whether an index on $B$ exists. For a query it picks **hint-set 2** (force nested-loop), which runs in 9s instead of the optimal 1.2s — a regression. We attribute the cost prediction via Shapley values. Suppose the model's predicted cost (log-seconds) over feature subsets $S$:

$$f(\emptyset)=1.0,\; f(\{1\})=1.0,\; f(\{2\})=2.0,\; f(\{3\})=1.5,\; f(\{1,2,3\})=2.2.$$

Feature 2 (selectivity) alone lifts the prediction from $1.0\to 2.0$. Its Shapley contribution, averaging marginal gains over orderings, dominates: $\phi_2 \approx +1.0$, versus $\phi_1\approx 0$, $\phi_3\approx +0.2$. The explanation: "the model predicted nested-loop was cheap *because* it read selectivity as low ($x_2$)." A DBA checks the true selectivity, finds the estimate was 100× off, and pins the regression to a cardinality-estimation error — not a planning bug. Exact $\phi$ over all $2^3=8$ subsets is cheap here, but grows as $\\#$P-hard with feature count, motivating KernelSHAP sampling.

---
*Part of the [DBMS Research catalog](../../README.md).*
