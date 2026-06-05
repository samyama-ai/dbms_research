# Joint Physical Design Optimization

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/joint-physical-design` · **Status:** open

## 1. Problem Statement
Rather than choosing indexes, materialized views (MVs), and partitions in separate or greedily-ordered passes, **joint physical design** co-selects all structure types $\mathcal{S} = \mathcal{I} \cup \mathcal{V} \cup \mathcal{P}$ simultaneously to minimize workload cost subject to a shared storage (and possibly maintenance) budget $B$:
$$ \min_{C \subseteq \mathcal{S},\ \mathrm{size}(C)\le B}\ \sum_j f_j\, c_C(q_j) + \lambda \cdot \mathrm{maint}(C). $$

The motivation: structures **compete for budget** and **substitute/complement** across types — a covering index may obviate an MV; a partition may make an index redundant or essential; an MV's maintenance may be cheaper given a particular partition. Greedy per-type selection provably leaves value on the table.

Variants:
- **Decision:** Is there a feasible $C$ achieving cost $\le t$?
- **Optimization:** Min total cost under joint budget (the practical goal).
- **Guarantee question:** Is there a poly-time algorithm with a *joint* approximation ratio better than the product/serial composition of per-type ratios?

## 2. Mathematical Foundations
Joint benefit is a set function over a **heterogeneous ground set** with a single knapsack (or matroid, if per-type caps exist) constraint. Cross-type interactions (see *index-interaction-modeling*) make it **non-submodular** in general: an MV and a partition can be supermodular (jointly enable a plan neither enables alone).

Relevant frameworks:
- **Matroid-constrained submodular max:** if budget is a partition matroid (caps per type), continuous greedy gives $(1-1/e)$ *when* benefit is submodular.
- **$k$-system / intersection of matroids:** joint storage + per-type caps + maintenance form an intersection of constraints; local search gives $\frac{1}{k+\epsilon}$.
- **Submodularity ratio $\gamma$ / supermodular degree** govern degradation under cross-type synergy.
- **Integer programming / Lagrangian relaxation:** the exact problem is an ILP; LP-relaxation gap quantifies how far joint-optimal sits from serial heuristics.

A key theoretical object is the **price of decomposition**: the worst-case ratio between the best *joint* configuration and the best achievable by any *serial, per-type* greedy pipeline. Bounding it (above and below) is the crux of the problem.

## 3. State of the Art (SOTA)
**Theory-SOTA:** No joint approximation guarantee beating serial composition is known. The per-type results ($(1-1/e)$ for index-only and MV-only submodular cores) compose to weaker joint factors; matroid-constrained submodular max gives $(1-1/e)$ *only* under the (false-in-general) submodularity assumption.

**Systems-SOTA:** **AutoAdmin / DTA** (Agrawal–Chaudhuri–Narasayya, VLDB 2000) pioneered *integrated* index+MV selection with candidate merging and joint enumeration — the de facto industrial state of the art, but heuristic. DB2 Design Advisor jointly recommends indexes, MVs (MQTs), partitions, and MDC. Cloud autonomous services and learned/RL co-tuners explore joint spaces empirically. None provides a joint optimality bound. *(frontier — verify)*

## 4. Upper Bound
- **Joint knapsack, submodular core:** $(1-1/e-\varepsilon)$ via continuous greedy + rounding — but only under the submodularity assumption that cross-type interactions violate.
- **Partition-matroid (per-type caps) + submodular:** $(1-1/e)$ (Calinescu–Chekuri–Pál–Vondrák).
- **General (non-submodular) joint:** only $\frac{1}{1 + d}$-type bounds via supermodular-degree $d$, or treewidth-bounded exact DP. No poly-time constant-factor guarantee for the fully general joint problem.

## 5. Lower Bound
- **NP-hard** (contains index-only and MV-only selection, themselves NP-hard).
- Inherits **Feige's $(1-1/e+\varepsilon)$** inapproximability from the coverage core.
- Cross-type **supermodular synergy** embeds **Densest-$k$-Subgraph** / hidden-clique instances ⇒ no known $n^{\epsilon}$-approximation under standard assumptions.
- The **price of decomposition** has an $\Omega(\text{constant})$ lower bound: explicit instances exist where serial per-type greedy is a constant factor worse than joint — proving joint solving is necessary, not just convenient.

## 6. The Gap
**Genuinely open.** We lack (a) any poly-time *joint* approximation beating serial composition for the realistic non-submodular case, and (b) tight bounds on the price of decomposition (only loose constants known). Lower bounds (DkS, Feige) bite under synergy; upper bounds need submodularity. Closing the gap means either a structural tameness result for cross-type interactions or a sharper hardness reduction specific to heterogeneous physical design.

## 7. Current Research (as of June 2026)
- **Learned/RL co-tuners** selecting indexes+MVs+partitions in one policy; analysis of when joint policies provably dominate serial ones is nascent. *(frontier — verify)*
- ILP/Lagrangian solvers with budget sharing and anytime guarantees; column-generation over candidate structures.
- Microsoft GSL (DTA lineage), IBM (Design Advisor), HPI, CMU/MIT learned-systems labs; theory contributions from the submodular-optimization community (Vondrák, Chekuri, Feldman). *(frontier — verify)*

## 8. Future Work
- Tight bounds on the price of decomposition across structure types.
- Joint approximation parameterized by cross-type interaction degree.
- Online/continuous joint tuning with regret (links *online-index-selection-regret*).
- Maintenance- and freshness-aware joint design for HTAP/lakehouse engines.

## 9. Key References
- **[Foundational]** S. Agrawal, S. Chaudhuri, V. Narasayya. *Automated Selection of Materialized Views and Indexes for SQL Databases.* VLDB, 2000. — [PDF](https://www.vldb.org/conf/2000/P496.pdf)
- **[Foundational]** D. Zilio, et al. *DB2 Design Advisor: Integrated Automatic Physical Database Design.* VLDB, 2004. — [DBLP](https://dblp.org/rec/conf/vldb/ZilioRLLSGF04.html)
- **[Foundational]** G. Calinescu, C. Chekuri, M. Pál, J. Vondrák. *Maximizing a Monotone Submodular Function Subject to a Matroid Constraint.* SIAM J. Computing, 2011. — [DOI](https://doi.org/10.1137/080733991)
- **[SOTA]** S. Papadomanolakis, A. Ailamaki. *An Integer Linear Programming Approach to Database Design.* ICDE Workshops, 2007. — [PDF](https://www.cs.cmu.edu/~ddash/papers/smdb07.pdf)
- **[SOTA]** S. Chaudhuri, V. Narasayya. *Anytime Algorithm of Database Tuning Advisor (DTA).* Microsoft, 2020. — [PDF](https://www.microsoft.com/en-us/research/wp-content/uploads/2020/06/Anytime-Algorithm-of-Database-Tuning-Advisor-for-Microsoft-SQL-Server.pdf)
- **[Survey]** S. Chaudhuri, V. Narasayya. *Self-Tuning Database Systems: A Decade of Progress.* VLDB, 2007. — [DBLP](https://dblp.org/rec/conf/vldb/ChaudhuriN07.html)

## 10. Worked Example

**Price of decomposition in one instance.** Budget $B=2$ units. Workload has one query $q$. Three candidate structures, each size 1:
- Index $I$ alone: cost $c(q)=80$.
- MV $V$ alone: cost $c(q)=80$.
- Partition $P$ alone: cost $c(q)=80$.
- But $V{+}P$ together enable a partition-pruned MV plan: $c(q)=10$ (strong **supermodular synergy**).
- Any other pair ($I{+}V$, $I{+}P$): cost $70$.

Baseline (nothing): $c(q)=100$.

**Serial per-type greedy** picks the single best marginal structure first. Each of $I,V,P$ alone gives the same marginal gain $100-80=20$; say it picks $I$. With 1 unit left it adds the best remaining single structure: $I{+}V$ or $I{+}P$ gives cost $70$. Serial cost $=70$.

**Joint optimum** evaluates pairs directly and picks $V{+}P$: cost $=10$.

Price of decomposition $=\frac{70}{10}=7$. Greedy's first move ($I$) is locally optimal yet poisons the budget: the synergistic pair $V{+}P$ is unreachable once $I$ is fixed. This is exactly the $\Omega(\text{constant})$ separation of §5 — and because $f$ is supermodular here, the $(1-1/e)$ guarantee of §4 does **not** apply.

---
*Part of the [DBMS Research catalog](../../README.md).*
