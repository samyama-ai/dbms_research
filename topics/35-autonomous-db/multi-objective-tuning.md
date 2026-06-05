# Multi-Objective Autonomous Tuning

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/multi-objective-tuning` · **Status:** partially-solved

## 1. Problem Statement
Autonomous tuning rarely optimizes a single scalar. Operators care simultaneously about **latency** (often multiple percentiles), **throughput**, **dollar cost**, **energy**, and storage — objectives that **conflict** (more memory cuts latency but raises cost; aggressive indexing helps reads but hurts writes and storage). The problem: given a configuration space $\Theta$ (knobs, indexes, resource sizing) and objective vector $f(\theta) = (f_1,\dots,f_m)$, **discover and navigate the Pareto frontier** efficiently, returning configurations that are *Pareto-optimal* and letting the operator (or a higher-level policy) pick a principled trade-off.

Formally: find $\mathcal{P} = \{\theta : \nexists\,\theta' \text{ with } f(\theta')\preceq f(\theta),\ f(\theta')\ne f(\theta)\}$ (Pareto set), or approximate it. Variants. **(i) Scalarization:** optimize $\sum_k w_k f_k$ for a given preference $w$ — easiest, but linear scalarization misses non-convex frontier regions. **(ii) Frontier approximation:** return an $\epsilon$-approximate Pareto set with bounded hypervolume error. **(iii) Constrained:** optimize one objective subject to bounds on others ($\epsilon$-constraint method). The status is **partially solved**: multi-objective Bayesian optimization gives strong empirical and some theoretical frontier coverage, but sample complexity and worst-case guarantees for the full DBMS setting remain incomplete.

## 2. Mathematical Foundations
- **Pareto dominance & hypervolume:** quality of an approximate frontier is measured by the **hypervolume indicator** (dominated volume w.r.t. a reference point) — the only indicator that is Pareto-compliant; maximizing it is the canonical surrogate objective.
- **Scalarization theory:** Chebyshev/augmented-Tchebycheff scalarizations can recover the *entire* (even non-convex) frontier as weights vary, unlike linear weighting (which only reaches the convex hull).
- **Multi-objective Bayesian optimization (MOBO):** GP surrogates with acquisitions like **EHVI** (Expected Hypervolume Improvement), **ParEGO** (random Chebyshev scalarizations), **qNEHVI**; regret/coverage analyzed via information gain $\gamma_T$.
- **$\epsilon$-constraint method:** converts to single-objective with constraints — links to the SLA-constrained problem.
- **Submodularity of hypervolume gain** supports greedy batch selection guarantees.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **OtterTune** optimizes a single combined metric; **CDBTune/QTune** use RL with a scalar reward. **MorphTune / ResTune** (Zhang et al., SIGMOD 2021) tune for *resource-oriented* objectives. **LlamaTune** reduces dimensionality. Multi-objective DBMS tuners using MOBO (Tchebycheff/EHVI) now report Pareto fronts over latency–throughput–cost; cloud right-sizing tools navigate cost–performance frontiers. **OnlineTune** addresses safe, context-aware tuning *(frontier — verify)*.
- **Theory-SOTA:** MOBO with **qNEHVI/qEHVI** (Daulton et al., NeurIPS 2020/2021) and **Pareto-frontier active learning** (PAL, Zuluaga et al., ICML 2013) give the best frontier-discovery algorithms with coverage guarantees; ParEGO (Knowles, 2006) is the classic scalarization baseline.

## 4. Upper Bound
**PAL / $\epsilon$-PAL** (Zuluaga et al.) returns an $\epsilon$-accurate Pareto set with a bounded number of evaluations that depends on the GP information gain $\gamma_T$ and the dimension of the objective space — a provable sample-complexity upper bound for frontier identification under RKHS smoothness. Hypervolume-based MOBO (qNEHVI) is, empirically, near sample-optimal and admits **no-regret** guarantees (cumulative hypervolume regret $\tilde O(\sqrt{T\gamma_T})$) under standard GP assumptions. Chebyshev scalarization guarantees recovery of *every* Pareto point as weights sweep the simplex (completeness of the frontier).

## 5. Lower Bound
- **Frontier size:** the Pareto set can be **exponentially large** (or a continuum); exactly enumerating it is intractable, so $\epsilon$-approximation is forced — and even an $\epsilon$-Pareto set can have size exponential in $m$ in the worst case (Papadimitriou–Yannakakis trade-off-curve theory).
- **Scalarization incompleteness:** linear scalarization provably **cannot** reach concave regions of the frontier — an unconditional impossibility motivating Chebyshev methods.
- **Sample-complexity floor:** identifying the frontier inherits the bandit $\Omega(\sqrt{T})$ regret floor per scalarization, and the information gain $\gamma_T$ can be $\Omega(T)$ for rough kernels, defeating no-regret guarantees.

## 6. The Gap
**Partially closed.** For smooth, low-objective-dimension problems, $\epsilon$-PAL and qNEHVI essentially match the achievable frontier-identification bound — the theory and practice align. The **open** residue is DBMS-specific: many objectives ($m\ge 4$, e.g. p50/p99 latency, throughput, \$, energy), **noisy/expensive** evaluations, **non-stationary** workloads, and the exponential blow-up of the $\epsilon$-Pareto set as $m$ grows. No method gives tight, distribution-free frontier-coverage guarantees at the objective counts and noise levels real systems face. Closing it needs many-objective MOBO with provable, drift-robust coverage.

## 7. Current Research (as of June 2026)
Threads: (a) **many-objective** MOBO with cheap-to-evaluate surrogates and preference learning to focus on operator-relevant frontier regions *(frontier — verify)*; (b) **context-aware / online** multi-objective tuning that re-discovers the frontier as workloads shift (OnlineTune lineage); (c) resource- and energy-aware tuning (ResTune) folding \$/energy directly into the objective vector; (d) interactive Pareto navigation where a higher-level controller picks trade-offs against SLAs. Groups: Pavlo/CMU, Li/Cui (PKU, ResTune/OnlineTune), Krause/ETH and Bakshy/Meta (Ax/BoTorch qNEHVI), Trummer/Cornell.

## 8. Future Work
- Distribution-free, drift-robust frontier-coverage guarantees for $m\ge 4$ objectives.
- Preference elicitation that minimizes evaluations to the operator-preferred trade-off.
- Joint Pareto navigation with hard SLA constraints (link to SLA-constrained tuning).
- Energy and carbon as first-class, well-calibrated objectives.

## 9. Key References
- **[Foundational]** C. H. Papadimitriou, M. Yannakakis. *On the Approximability of Trade-offs and Optimal Access of Web Sources.* FOCS, 2000.
- **[Foundational]** M. Zuluaga, A. Krause, G. Sergent, M. Püschel. *Active Learning for Multi-Objective Optimization (PAL).* ICML, 2013.
- **[SOTA]** S. Daulton, M. Balandat, E. Bakshy. *Differentiable Expected Hypervolume Improvement for Parallel Multi-Objective Bayesian Optimization (qNEHVI).* NeurIPS, 2021.
- **[SOTA]** X. Zhang et al. *ResTune: Resource Oriented Tuning Boosted by Meta-Learning for Cloud Databases.* SIGMOD, 2021.
- **[Foundational]** J. Knowles. *ParEGO: A Hybrid Algorithm with On-line Landscape Approximation for Expensive Multiobjective Optimization Problems.* IEEE Trans. Evolutionary Computation, 2006.

---
*Part of the [DBMS Research catalog](../../README.md).*
