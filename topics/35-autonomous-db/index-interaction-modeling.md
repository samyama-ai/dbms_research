# Interaction-Aware Configuration Search

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/index-interaction-modeling` · **Status:** open

## 1. Problem Statement
Physical-design structures **interact**: the marginal benefit of an index, materialized view (MV), or partition depends on which others are already present. The benefit function $\mathrm{ben} : 2^{\mathcal{I}} \to \mathbb{R}_{\ge 0}$ is therefore **not additive** and frequently **not submodular**.

The problem: *model* these interactions compactly and *exploit* them to search the configuration space $2^{|\mathcal{I}|}$ (often $10^6$–$10^{12}$ candidates) without an exponential number of optimizer "what-if" calls.

Formal questions:
- **Decision:** Given a partial configuration, does adding structure set $T$ change query $q$'s plan (i.e., do members of $T$ interact for $q$)?
- **Optimization:** Maximize benefit when benefit can have positive (synergy: index-only plans, AND/OR index intersection) and negative (substitution: two redundant covering indexes) interactions.
- **Counting/structure-learning:** Recover the *interaction hypergraph* — which subsets jointly determine cost — from limited cost-function probes.

## 2. Mathematical Foundations
Define **degree-of-interaction** for a query $q$ over structures $a,b$ (Schnaitter–Polyzotis–Getoor):
$$ \mathrm{doi}_q(a,b) = \frac{\big| (c_{\{a\}} - c_{\{a,b\}}) - (c_{\{b\}} - c_{\{a,b,\dots\}}) \big|}{c_q} ,$$
generalized via the **discrete second derivative** $\Delta_b \Delta_a \mathrm{ben}(S)$. Submodularity $\equiv$ all such cross-derivatives $\le 0$; supermodular synergy means some are $> 0$.

Representations:
- **Interaction hypergraph / pseudo-Boolean function:** $\mathrm{ben}(S) = \sum_{T \subseteq \mathcal{I}} \alpha_T \prod_{i\in T} x_i$; a *bounded-degree* (degree-$k$) expansion is learnable with $O(|\mathcal{I}|^k)$ coefficients.
- **Möbius / Fourier (Walsh–Hadamard) analysis** of set functions: sparsity in the Fourier domain bounds sample complexity for learning $\mathrm{ben}$.
- **$\epsilon$-approximate submodularity / submodularity ratio $\gamma$** (Das–Kempe): greedy retains a $(1 - e^{-\gamma})$ guarantee when the function is *near*-submodular.
- **Supermodular degree** (Feige–Izsak): parameter controlling approximability of non-submodular maximization.

The combinatorial obstacle: the number of *interacting* subsets can be super-polynomial even when each query touches few structures.

## 3. State of the Art (SOTA)
**Theory-SOTA:** Approximation parameterized by submodularity ratio $\gamma$ or supermodular degree $d$: greedy gives $\frac{1}{d+1}$-type or $(1-e^{-\gamma})$ bounds. These degrade gracefully but provide no guarantee when interactions are dense.

**Systems-SOTA:** Schnaitter et al.'s **degree-of-interaction** model and the *Index Interaction*-aware tuners; Microsoft DTA prunes via merged/atomic configurations and "what-if" caching. Learned cost models (e.g., neural plan-cost estimators, Bao/Balsa-style learned optimizers) implicitly capture interaction but are not used to *prove* search efficiency. Recent work learns the interaction graph to seed local search. *(frontier — verify)*

## 4. Upper Bound
For benefit with **submodularity ratio $\gamma$**, greedy achieves $(1 - e^{-\gamma})\cdot\mathrm{OPT}$ in $O(|\mathcal{I}|\cdot m)$ what-if calls. For **supermodular degree $d$**, a $(d+1)$-approximation (or better via local search) is known. If the interaction hypergraph has **bounded treewidth $w$**, dynamic programming gives exact optimization in $2^{O(w)} \cdot \mathrm{poly}$ time. None of these is efficient for general dense interactions.

## 5. Lower Bound
- Optimizing a general non-submodular set function given only value-oracle access requires **exponentially many queries** to approximate within any constant (information-theoretic, via indistinguishable hidden-clique-style instances).
- The interaction-aware problem captures **Densest-$k$-Subgraph** (pairwise synergies) — believed to admit no $n^{\epsilon}$-approximation under standard assumptions — and **Maximum Coverage with bonuses**.
- Learning a degree-$k$ pseudo-Boolean benefit needs $\Omega(|\mathcal{I}|^k)$ probes in the worst case (Fourier-sparsity lower bound).

## 6. The Gap
**Open and wide.** Upper bounds need a tameness parameter ($\gamma$, supermodular degree, treewidth, Fourier sparsity) whose value for *real* optimizers is unknown and unbounded in adversarial cases; lower bounds (DkS-hardness, oracle exponentiality) bite precisely when those parameters blow up. The gap closes only if real DBMS cost functions provably exhibit low interaction degree — an empirical-meets-theoretical question with no current proof.

## 7. Current Research (as of June 2026)
- **Measuring** interaction sparsity in production workloads to justify bounded-degree models. *(frontier — verify)*
- Learned set-function regression (deep submodular functions, graph neural nets over the interaction hypergraph) with sample-complexity analysis. *(frontier — verify)*
- Active groups: UW-Madison/CMU learned-systems labs, HPI, TU Darmstadt; theory side draws on Feldman, Vondrák, and the submodularity-ratio community.

## 8. Future Work
- A *certified* low-interaction structural assumption for SQL optimizers and matching approximation.
- Probe-efficient algorithms that learn the interaction hypergraph and optimize within a what-if budget.
- Negative-interaction-aware pruning with guarantees (substitution/redundancy).
- Unifying interaction modeling across indexes + MVs + partitions (feeds *joint-physical-design*).

## 9. Key References
- **[Foundational]** K. Schnaitter, N. Polyzotis, L. Getoor. *Index Interactions in Physical Design Tuning: Modeling, Analysis, and Applications.* VLDB, 2009.
- **[Foundational]** A. Das, D. Kempe. *Submodular meets Spectral: Greedy Algorithms for Subset Selection... (submodularity ratio).* ICML, 2011.
- **[Foundational]** U. Feige, R. Izsak. *Welfare Maximization and the Supermodular Degree.* ITCS, 2013.
- **[SOTA]** R. Marcus, et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021.
- **[SOTA]** S. Chaudhuri, V. Narasayya. *Anytime Algorithm of Database Tuning Advisor (DTA).* Microsoft, 2020.
- **[Survey]** F. Bach. *Learning with Submodular Functions: A Convex Optimization Perspective.* Foundations and Trends in ML, 2013.

---
*Part of the [DBMS Research catalog](../../README.md).*
