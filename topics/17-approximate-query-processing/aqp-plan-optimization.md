# AQP Cost-Accuracy Plan Optimization

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/aqp-plan-optimization` · **Status:** open

## 1. Problem Statement

A query optimizer for approximate query processing must choose, for each query, *how* to answer it: from a uniform sample, a stratified sample, one of several sketches, a learned synopsis, or an exact plan — and at *what* parameter (sample size, sketch width). The goal is to select a plan that **meets an error service-level objective (SLO)** — e.g. relative error $\le \varepsilon$ with confidence $1-\delta$, or interval half-width $\le h$ — at **minimum cost** (latency / resource use), or symmetrically, *minimize error subject to a cost budget*.

Variants:
- **Optimization:** minimize cost s.t. predicted error $\le$ SLO (or minimize error s.t. cost $\le$ budget).
- **Decision:** does any available synopsis/plan satisfy the SLO, or must we fall back to exact?
- **Online / workload:** allocate a fixed synopsis-storage budget across a *query workload* to maximize aggregate SLO satisfaction (a knapsack/coverage problem).
- **Anytime:** progressively refine an estimate, deciding when the SLO is met (online aggregation).

## 2. Mathematical Foundations

The optimizer needs, for each candidate plan $P$, a **cost model** $\mathrm{cost}(P)$ and an **error model** $\mathrm{err}(P)$ — both *predicted before execution*. Error prediction is the hard part: for a sample of size $n$ it derives from estimator variance ($O(\sigma/\sqrt{n})$), but $\sigma$ and the post-predicate survivor count are themselves unknown (linking to *Predicate Pushdown Bias* and to **cardinality estimation**). The selection is a constrained optimization

$$\min_{P \in \mathcal{P}} \ \mathrm{cost}(P) \quad \text{s.t.}\quad \mathrm{err}(P) \le \varepsilon,$$

over a discrete plan space $\mathcal P$ (which sample/sketch, which size). For a *workload* under a storage budget $B$, choosing which synopses to materialize to cover query classes is a **weighted set-cover / budgeted maximum coverage** problem (NP-hard, $(1-1/e)$-approximable via the submodularity of coverage). Classical optimization theory — Selinger-style cost-based plan enumeration with dynamic programming — must be extended with an **accuracy dimension**, turning a single-objective search into a constrained / multi-objective (Pareto) one. Online aggregation frames it as **optimal stopping** under a confidence sequence.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** **BlinkDB** (Agarwal et al., EuroSys 2013) selects among offline stratified samples to meet an error or time bound — the canonical accuracy-aware optimizer, but over a *fixed sample menu*. **VerdictDB** (Park et al., SIGMOD 2018) and **DBEst** add model-based answers. **Online Aggregation** (Hellerstein, Haas, Wang, SIGMOD 1997) and **Ripple Joins** (Haas–Hellerstein, 1999) give anytime estimates with running intervals — the optimizer becomes a stopping rule. Recent learned-optimizer work (Bao, Neo, Balsa) optimizes *latency* but not yet *accuracy SLOs* jointly. **ML-AQP / DeepDB** route between model and data.
- **Theory-SOTA:** budgeted synopsis selection as submodular coverage with $(1-1/e)$ guarantees; constrained plan selection is otherwise mostly heuristic. No optimizer with end-to-end *provable* SLO satisfaction across samples+sketches+exact is established.

## 4. Upper Bound

For a fixed, finite plan menu with *known* per-plan error and cost, plan selection is trivial ($O(|\mathcal P|)$ scan) and exact. For *workload* synopsis selection under a storage budget, the greedy algorithm gives a $(1-1/e)$-approximation to coverage (optimal for the problem unless P=NP). Online aggregation with empirical-Bernstein confidence sequences meets an SLO using $O(\sigma^2/\varepsilon^2)$ rows in expectation and stops *validly* (always-valid intervals). BlinkDB-style selection meets the SLO whenever its offline samples' error models are accurate.

## 5. Lower Bound

The hardness is inherited from **cardinality/error estimation**: predicting $\mathrm{err}(P)$ for a sample under an arbitrary multi-table predicate is provably hard — join cardinality estimation has worst-case error that no polynomial sketch can bound tightly (related to the **AGM bound** being the only tight worst-case handle, and to known impossibility of accurate selectivity estimation from limited statistics). Hence the *decision* variant ("can plan $P$ meet the SLO?") cannot be answered exactly without partial execution. **Budgeted workload synopsis selection is NP-hard** (set-cover reduction), so no poly-time optimizer matches the offline optimum unless P=NP; $(1-1/e)$ is the best constant. For online/anytime stopping, $\Omega(\sigma^2/\varepsilon^2)$ samples are information-theoretically necessary.

## 6. The Gap

The gap is **open and structural**, not merely quantitative. (1) Plan *selection* is easy *given* accurate per-plan error predictions, but those predictions are the unsolved part — error/cardinality estimation under predicates and joins has no tight bound, so optimizers either over-provision (waste cost) or violate the SLO. (2) Workload synopsis selection is NP-hard with a known $(1-1/e)$ ceiling, but real optimizers don't even reach it under realistic query drift. (3) No system gives *end-to-end provable* SLO satisfaction across the full menu (samples + sketches + learned + exact). Closing it needs trustworthy *a-priori* error models — exactly the hard estimation problem — plus a planner that hedges under estimation uncertainty (e.g. robust/distributionally-robust plan choice).

## 7. Current Research (as of June 2026)

Active: **learned query optimizers extended with accuracy SLOs** — routing among synopses using learned error predictors with calibrated uncertainty *(frontier — verify)*; **robust plan selection** that accounts for error-model uncertainty rather than trusting a point estimate; **progressive / anytime AQP** with always-valid confidence sequences as the stopping oracle; co-optimization with DP budgets (links to *Error-Bounded AQP Under DP Noise*). Groups: Mozafari (VerdictDB), Chaudhuri/Narasayya (Microsoft Research, self-tuning), Kraska (MIT, learned systems), Stoica/Berkeley lineage (BlinkDB), Triantafillou (Warwick). The explicit "single optimizer, full plan menu, provable SLO at minimum cost" formulation is recognized as open *(frontier — verify)*.

## 8. Future Work

- Calibrated, uncertainty-aware per-plan error predictors usable as optimizer inputs.
- Robust / distributionally-robust plan selection under error-estimation uncertainty.
- A unified optimizer over samples, sketches, learned synopses, and exact with end-to-end SLO guarantees.
- Joint cost / accuracy / privacy / freshness plan optimization (cross-links to DP and sample-maintenance problems).
- Workload-aware online synopsis materialization with regret bounds against the offline $(1-1/e)$ optimum.

## 9. Key References

- **[Foundational]** P. G. Selinger, M. M. Astrahan, D. D. Chamberlin, R. A. Lorie, T. G. Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** J. M. Hellerstein, P. J. Haas, H. J. Wang. *Online Aggregation.* SIGMOD, 1997. — [DOI](https://doi.org/10.1145/253260.253291)
- **[SOTA]** S. Agarwal, B. Mozafari, A. Panda, H. Milner, S. Madden, I. Stoica. *BlinkDB: Queries with Bounded Errors and Bounded Response Times on Very Large Data.* EuroSys, 2013. — [DOI](https://doi.org/10.1145/2465351.2465355)
- **[SOTA]** Y. Park, B. Mozafari, J. Sorenson, J. Wang. *VerdictDB: Universalizing Approximate Query Processing.* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196905)
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins (the AGM bound).* FOCS, 2008 / SICOMP, 2013. — [DOI](https://doi.org/10.1137/110859440)
- **[Survey]** S. Chaudhuri, B. Ding, S. Kandula. *Approximate Query Processing: No Silver Bullet.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3056097)

## 10. Worked Example

**SLO-constrained plan choice.** A query `SELECT AVG(amount) FROM Sales` must meet relative-error SLO $\varepsilon=2\%$ at $1-\delta=95\%$. Data: $N=10^8$ rows, true $\mu=500$, $\sigma=300$ (so coefficient of variation $c=\sigma/\mu=0.6$). The optimizer has three plans:

| Plan | Sample size $n$ | Cost (s) | Predicted rel. half-width $\approx \frac{1.96\,c}{\sqrt n}$ |
|------|------|------|------|
| $P_1$ (1% sample) | $10^6$ | 1.2 | $1.96\cdot 0.6/1000 = 0.12\%$ |
| $P_2$ (0.01% sample) | $10^4$ | 0.05 | $1.96\cdot 0.6/100 = 1.18\%$ |
| $P_3$ (0.0025% sample) | $2.5{\times}10^3$ | 0.02 | $1.96\cdot 0.6/50 = 2.35\%$ |

Selection rule: $\min \text{cost s.t. err}\le \varepsilon$. $P_3$ violates ($2.35\% > 2\%$); $P_2$ satisfies ($1.18\%\le 2\%$) at cost 0.05s; $P_1$ over-provisions. The optimizer picks $P_2$.

The catch (section 6): this assumes $\sigma$ is *known*. If a `WHERE` predicate cuts survivors to an unknown count, the post-predicate $\sigma$ and $n$ are themselves estimates — mispredicting $\sigma$ by $2\times$ flips $P_2$ from satisfying to violating the SLO. That a-priori error model is the unsolved hard part.

---
*Part of the [DBMS Research catalog](../../README.md).*
