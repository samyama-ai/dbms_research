---
id: 02-query-optimization/adaptive-reoptimization
title: "Adaptive mid-query re-optimization"
topic: 02-query-optimization
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Adaptive mid-query re-optimization

> **Topic:** Query Optimization · **ID:** `02-query-optimization/adaptive-reoptimization` · **Status:** empirically-open

## 1. Problem Statement

A cost-based optimizer commits to a physical plan $P$ before execution, using *estimated* cardinalities $\hat{c}$. During execution, the engine observes *actual* cardinalities $c$ for materialized or pipelined intermediate results. **Mid-query re-optimization** is the problem of deciding, at one or more checkpoints during execution, whether the remaining plan $P_{\text{rem}}$ should be replaced by a cheaper plan given the now-known prefix results, and how to do so without discarding useful work.

Three variants must be distinguished:

- **Decision variant:** given observed cardinalities at a checkpoint, decide *yes/no* whether re-optimizing can reduce expected remaining cost below the current plan's, net of switching cost.
- **Optimization variant:** choose the checkpoint placement, the materialization points, and the replacement plan to minimize total end-to-end cost (already-spent + remaining + re-optimization overhead).
- **Online/competitive variant:** with no distributional assumptions, bound the ratio between the adaptive policy's cost and the cost of the offline-optimal plan that knew all true cardinalities in advance.

The key tension: re-optimization is only valuable when estimates were wrong, but the engine cannot know they were wrong without (partly) executing — a classic explore/exploit and stopping problem.

## 2. Mathematical Foundations

Model the query as a plan DAG with operators $o_1,\dots,o_n$; each edge carries a true cardinality $c_e$ and an estimate $\hat{c}_e$. Operator cost is $\text{cost}(o_i)=f_i(\{c_e : e \in \text{in}(o_i)\})$. A **checkpoint** at materialization boundary $B$ reveals $\{c_e : e \in B\}$ and induces a residual optimization over the sub-DAG downstream of $B$, conditioned on the realized intermediate relations.

Validity ranges follow Selinger-style **parametric/robust** reasoning: a plan $P$ is optimal over a region $R \subseteq \mathbb{R}^k_{\ge 0}$ of the cardinality parameter space. Re-optimization is provably worthwhile only when observed $c$ leaves the current plan's optimality region $R(P)$. The structure of these regions (POSP — *parametric optimal set of plans*) is the foundation; for many cost models they are unions of polytopes.

The online variant connects to **competitive analysis**: an adaptive scheduler that may switch plans is a metrical task system / online algorithm against an oblivious adversary. The "work thrown away on switch" is the metric-space movement cost; this yields lower bounds of the form $\Omega(\log)$-competitiveness in the worst case under arbitrary cost functions.

## 3. State of the Art (SOTA)

**Systems-SOTA.** Kabra–DeWitt (SIGMOD 1998) introduced runtime collection of statistics with re-optimization at materialization points. The **POP / progressive optimization** line (Markl et al., VLDB 2004) defines *validity ranges* (check operators / CHECK) that trigger re-optimization only on statistically significant deviation. **Eddies** (Avnur–Hellerstein, SIGMOD 2000) and the **RDBMS adaptive** family go further to per-tuple routing, eliminating fixed plans entirely. Modern engines — SQL Server's *adaptive joins* and *interleaved execution* for MSTVFs, Oracle's *adaptive plans* and *automatic reoptimization*, and Spark's *Adaptive Query Execution (AQE)* (re-planning at shuffle boundaries) — embody checkpoint-based re-optimization in production.

**Theory-SOTA.** Robust/parametric optimization (Hulgeri–Sudarshan; Reddy–Haritsa *Plan Diagrams*, VLDB 2005) characterizes the plan-space geometry that re-optimization navigates; *Plan Bouquets* (Dutt–Haritsa, SIGMOD 2014) give the first cost-guaranteed (bounded sub-optimality) execution without selectivity estimation.

## 4. Upper Bound

For the cost-guaranteed execution variant, **Plan Bouquets** achieve a worst-case performance guarantee of $\text{MSO} \le 4\rho$ where $\rho$ is the number of plans on the cost-doubling "bouquet" contour (and an information-theoretic-style $O(\log)$ factor in the 1-D selectivity case), independent of the optimizer's estimates. In the general multi-dimensional case the guarantee degrades with dimension $D$, with anorexic/bounded variants giving constant-factor MSO for fixed small $D$. For checkpoint-based re-optimization with materialization, the upper bound on overhead is bounded by re-running the optimizer at each of $O(n)$ materialization boundaries — additive optimizer cost, no asymptotic blow-up of execution.

## 5. Lower Bound

No constant-competitive guarantee is possible for fully general online plan-switching: against an oblivious adversary choosing cardinalities adversarially, any deterministic policy that commits to a plan can be forced to pay $\Omega$ of the offline optimum, and randomization buys only logarithmic improvements (metrical-task-system lower bounds). For estimation-free execution, Plan Bouquets show the MSO guarantee is tied to the bouquet cardinality $\rho$, and matching lower bounds (Dutt–Haritsa) show $\Omega(\rho)$ MSO is unavoidable for any deterministic estimation-free scheme on the same selectivity space — establishing near-tightness in 1-D. The decision variant is at least as hard as the underlying join-order optimization (NP-hard).

## 6. The Gap

In 1-D estimation-free execution, upper and lower MSO bounds are essentially matched (constant factor). The genuine openness is **multidimensional and dynamic**: no scheme achieves dimension-independent bounded sub-optimality, and there is no tight characterization of *optimal checkpoint placement* (how many, where) that balances information gained against materialization cost. Empirically, re-optimization helps dramatically on skewed/correlated data but can thrash; there is no accepted theory predicting when to stop re-optimizing. The gap is genuinely open and is as much a modeling gap (what is the right adversary/distribution) as an algorithmic one.

## 7. Current Research (as of June 2026)

Active directions: (i) **learned cardinality + re-optimization hybrids** — using ML estimators to shrink validity ranges so fewer checkpoints fire (work from CMU, TUM, MIT, Microsoft GSL); (ii) **AQE generalization** beyond shuffle boundaries in Spark/Photon and Velox, toward pipelined re-planning *(frontier — verify)*; (iii) **bandit / RL formulations** of the explore-exploit checkpoint decision (Marcus–Kraska Bao/Neo lineage). Haritsa's group continues robustness-guarantee work; TUM (Neumann/Leis) studies re-optimization in compiled, morsel-driven engines. Open question receiving attention: provable guarantees for re-optimization under *learned* estimators with calibrated uncertainty *(frontier — verify)*.

## 8. Future Work

- A clean online-competitive theory of plan switching that accounts for sunk pipelined work (not just materialized).
- Optimal/automatic checkpoint placement with theoretical guarantees rather than heuristics.
- Dimension-robust estimation-free guarantees (closing the multidimensional MSO gap).
- Integration with calibrated learned cardinality uncertainty to trigger re-optimization with confidence bounds.
- Re-optimization under concurrency, where resource availability (not just cardinality) shifts mid-query.

## 9. Key References

- **[Foundational]** N. Kabra, D. J. DeWitt. *Efficient Mid-Query Re-Optimization of Sub-Optimal Query Execution Plans.* SIGMOD, 1998. — [ACM](https://dl.acm.org/doi/10.1145/276304.276315)
- **[Foundational]** R. Avnur, J. M. Hellerstein. *Eddies: Continuously Adaptive Query Processing.* SIGMOD, 2000. — [ACM](https://dl.acm.org/doi/10.1145/342009.335420)
- **[SOTA]** V. Markl, V. Raman, D. Simmen, G. Lohman, H. Pirahesh, M. Cilimdzic. *Robust Query Processing through Progressive Optimization.* SIGMOD, 2004. — [ACM](https://dl.acm.org/doi/10.1145/1007568.1007642)
- **[SOTA]** A. Dutt, J. R. Haritsa. *Plan Bouquets: Query Processing without Selectivity Estimation.* SIGMOD, 2014. — [PDF](https://dsl.cds.iisc.ac.in/publications/conference/bouquet.pdf)
- **[SOTA]** Naveen Reddy, J. R. Haritsa. *Analyzing Plan Diagrams of Database Query Optimizers.* VLDB, 2005. — [DBLP](https://dblp.org/rec/conf/vldb/ReddyH05.html)
- **[Survey]** A. Deshpande, Z. Ives, V. Raman. *Adaptive Query Processing.* Foundations and Trends in Databases, 2007. — [PDF](https://www.cs.umd.edu/~amol/papers/fnt-aqp.pdf)

## 10. Worked Example

Query: $A \bowtie B \bowtie C$. The optimizer estimates $|A\bowtie B| = 1{,}000$ rows and chooses the plan $(A\bowtie B)\bowtie C$ with a hash join on $C$, costed at $\approx 1{,}000 + |C|$ probes.

At the materialization checkpoint after $A\bowtie B$ completes, the engine observes the **actual** cardinality $c = 200{,}000$ (a $200\times$ underestimate, q-error $200$). The current plan's residual cost is now $200{,}000 + |C|$ probe operations against $C$ — far worse than estimated.

Re-optimization: with $c$ now known exactly, the residual optimizer reconsiders join order and finds that building the hash table on the small relation $C$ ($|C| = 500$) and probing with the 200k-row stream costs $\approx 500$ build $+ 200{,}000$ probe, but switching the build side avoids re-hashing 200k rows, saving roughly $40\%$.

Decision rule: switch only if $\text{cost}(P_{\text{rem}}) - \text{cost}(P'_{\text{rem}}) > \text{switch cost}$. Here the materialized $A\bowtie B$ is reused (no work discarded), so switch cost is just one extra build, and re-optimization fires.

---
*Part of the [DBMS Research catalog](../../README.md).*
