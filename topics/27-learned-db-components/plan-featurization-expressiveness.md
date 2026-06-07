---
id: 27-learned-db-components/plan-featurization-expressiveness
title: "Plan Featurization Expressiveness"
topic: 27-learned-db-components
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Plan Featurization Expressiveness

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/plan-featurization-expressiveness` · **Status:** open

## 1. Problem Statement

Every learned DB component first **encodes** a query/plan into a feature vector or graph that a model consumes. The expressiveness problem: **characterize which classes of plan-and-data interactions a given encoding can and cannot represent.** If two operationally different plans (with different true costs) map to the same features, no downstream model — however large — can distinguish them. Featurization is therefore an *information bottleneck* that upper-bounds all learned components built on it.

Variants:

- **Representability (decision):** given encoding $\phi$, do there exist plans $p\ne p'$ with $\phi(p)=\phi(p')$ but $\text{cost}(p)\ne\text{cost}(p')$? (a *collision* certifying a blind spot).
- **Separation (characterization):** characterize the equivalence classes $\phi$ induces and which cost-relevant predicates they conflate (e.g., correlation between predicates, data skew, physical-property/interesting-orders effects).
- **Expressiveness hierarchy (counting/comparison):** order encodings (flat featurization < tree models < message-passing GNNs < higher-order GNNs) by the interaction classes they separate.

## 2. Mathematical Foundations

An encoding $\phi:\text{Plans}\to\mathcal X$ partitions plans into fibers $\phi^{-1}(x)$. A downstream model can realize a target cost $c:\text{Plans}\to\mathbb R$ **iff** $c$ is constant on every fiber, i.e. $c$ factors through $\phi$. The *expressiveness ceiling* is thus $\min_{f}\,\mathbb E\,|c - f\circ\phi|$, lower-bounded by within-fiber cost variance — a purely information-theoretic limit independent of model capacity.

Foundations:

- **Graph isomorphism / WL hierarchy:** plans and join graphs are graphs; message-passing GNNs are bounded by the **1-Weisfeiler–Leman** test (Xu et al. 2019; Morris et al. 2019) — they cannot distinguish WL-equivalent graphs. Two non-isomorphic join graphs that are 1-WL-indistinguishable receive identical embeddings, so any cost difference between them is invisible. Higher-order ($k$-WL) GNNs raise the ceiling at polynomial cost.
- **Data-interaction expressiveness:** cost depends on *data* statistics (joint distributions, correlations), but most encodings inject only per-column marginals (NDV, histograms). Then any cost effect of cross-column correlation lies in the within-fiber variance — unrepresentable. This mirrors the AGM-vs-actual gap: marginals bound but cannot pin down join size under correlation.
- **Physical properties:** interesting orders, partitioning, and pipelining create cost effects (sort avoidance, materialization) that a tree/flat encoding omitting these annotations cannot represent — Selinger's "interesting orders" are an *expressiveness* requirement, not a heuristic.

## 3. State of the Art (SOTA)

- **Systems-SOTA encodings:** *Bao*'s tree-convolution over plan trees (Marcus et al. 2021); *Neo*'s tree-LSTM plan encoding + per-predicate vectors; *QPP-Net*'s plan-structured composition; *RTOS*/GNN encoders over join graphs; *Zero-shot* transferable data-feature encodings (Hilprecht & Binnig 2022). Each makes different, mostly *implicit*, expressiveness choices.
- **Theory-SOTA:** the GNN expressiveness program (1-WL bound, $k$-WL hierarchy, GIN) supplies the formal tools, but a *DB-specific* expressiveness characterization — which cost-relevant interactions each encoding separates — is largely unwritten.

## 4. Upper Bound

- **GNN encoders:** expressiveness $\le$ 1-WL for standard message passing (Xu et al. 2019); $k$-WL with higher-order variants, separating strictly more join-graph structures at $O(n^k)$ cost — **graph-learning model**.
- **Universal-approximation caveat:** given an injective $\phi$ (no collisions on the plan space of interest), a sufficiently large MLP/tree model can approximate any cost function on that space (universal approximation). So the *binding* limit is $\phi$'s injectivity, not the regressor.

## 5. Lower Bound

- **WL lower bound:** message-passing GNNs *provably cannot* distinguish 1-WL-equivalent graphs (Morris et al. 2019) — a hard separation limit, model-size-independent. Constructing two cost-different, 1-WL-equivalent join graphs certifies a blind spot.
- **Marginal-only barrier:** an encoding carrying only per-column marginals cannot represent any cost function whose value depends on cross-column joint mass — information-theoretic (the joint is not a function of the marginals). Adversarial correlated data realizes arbitrary within-fiber cost variance (links to **learned-component-robustness**).
- **Omitted-property barrier:** dropping physical properties (orders/partitioning) makes order-sensitive cost effects unrepresentable; trivially provable by exhibiting two plans differing only in an interesting order.

## 6. The Gap

Open and largely **uncharted for the DB setting**. The graph-ML community has a clean expressiveness hierarchy; the DB community has many encodings but no map of *which cost-relevant data/plan interactions each one separates*. The gap is descriptive: produce, for each standard encoding, (a) the exact collision classes and (b) the minimal feature augmentation that removes a named blind spot (e.g., add a correlation sketch to capture join-size effects). This is a prerequisite for honest generalization and convergence guarantees in the sibling problems.

## 7. Current Research (as of June 2026)

- Applying the WL/GNN-expressiveness lens to query-plan encoders to certify and remove blind spots (intersection of graph-ML and DB groups) *(frontier — verify)*.
- Richer data features: correlation/joint sketches and sample-based features injected into encodings to break the marginal-only barrier (TU Darmstadt, MIT) *(frontier — verify)*.
- Plan encoders that preserve physical properties (orders, partitioning) and operator-level structure for cost fidelity.
- Probing studies: measuring within-fiber cost variance empirically to quantify an encoding's ceiling.

## 8. Future Work

- A formal expressiveness hierarchy of DB plan/query encodings analogous to the WL hierarchy.
- Minimal sufficient statistics for cost prediction — the smallest feature set that makes cost a function of $\phi$ for a stated query class.
- Encoding-design theorems linking added features to provably removed blind spots.
- Tie-in: expressiveness ceiling as the formal upper bound for **optimizer-unseen-query-generalization** and **learned-optimizer-convergence**.

## 9. Key References

- **[Foundational]** Xu, Hu, Leskovec, Jegelka. *How Powerful Are Graph Neural Networks? (GIN).* ICLR, 2019. — [arXiv](https://arxiv.org/abs/1810.00826)
- **[Foundational]** Morris, Ritzert, Fey, Hamilton, Lenssen, Rattan, Grohe. *Weisfeiler and Leman Go Neural: Higher-Order Graph Neural Networks.* AAAI, 2019. — [arXiv](https://arxiv.org/abs/1810.02244)
- **[Foundational]** Selinger, Astrahan, Chamberlin, Lorie, Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DBLP](https://dblp.org/rec/conf/sigmod/SelingerACLP79.html)
- **[SOTA]** Marcus, Negi, Mao, Tatbul, Alizadeh, Kraska. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008. — [arXiv](https://arxiv.org/abs/1711.03860)
- **[SOTA]** Hilprecht, Binnig. *Zero-Shot Cost Models for Out-of-the-Box Learned Cost Prediction.* VLDB, 2022. — [arXiv](https://arxiv.org/abs/2201.00561)

## 10. Worked Example

A **marginal-only collision**. Two columns $X,Y$, each Boolean, $N=100$ rows. Encoding $\phi$ carries only per-column marginals: $\Pr[X{=}1]=0.5,\ \Pr[Y{=}1]=0.5$ — identical for both datasets below.

- **Dataset A (independent):** the 4 cells $(X,Y)\in\{0,1\}^2$ each have 25 rows. Join $\sigma_{X=1}\bowtie\sigma_{Y=1}$ selectivity $=0.5\cdot0.5=0.25\Rightarrow 25$ output rows.
- **Dataset B (perfectly correlated, $X{=}Y$):** cells $(0,0)$ and $(1,1)$ have 50 rows each; $(0,1),(1,0)$ empty. Same marginals, but $\Pr[X{=}1\wedge Y{=}1]=0.5\Rightarrow 50$ output rows — **2× the cost**.

Both map to the *same* feature vector $\phi$, so $\phi(p_A)=\phi(p_B)$ while $\text{cost}(p_A)\ne\text{cost}(p_B)$ — a certified collision (section 1's representability variant). The within-fiber cost variance is nonzero, so *no* downstream model on $\phi$ can separate them: the expressiveness ceiling is breached. The fix from section 6: inject a 1-cell correlation sketch (the joint $\Pr[X{=}1,Y{=}1]$), which makes cost a function of the augmented $\phi$ and removes exactly this blind spot — mirroring the AGM-vs-actual gap of Atserias–Grohe–Marx.

---
*Part of the [DBMS Research catalog](../../README.md).*
