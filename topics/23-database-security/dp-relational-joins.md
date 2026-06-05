# Differential Privacy under Foreign Keys

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/dp-relational-joins` · **Status:** open

## 1. Problem Statement

Differential privacy (DP) calibrates noise to a query's **sensitivity** — how much one individual's data can change the answer. For a single table this is bounded: a `COUNT` has sensitivity 1, a bounded `SUM` has sensitivity equal to the clamp range. **Joins break this.** When relations are connected by foreign keys, a single tuple in a parent relation can join with — and therefore influence — an *unbounded* number of output rows (high-degree nodes, e.g. one popular user matched to millions of events). The **global sensitivity of a join query can be unbounded**, so naive Laplace/Gaussian noise is either infinite (useless) or unsound (not actually DP).

The problem: define the correct **privacy unit** (tuple-, user-, or entity-level under multiple foreign keys), and calibrate noise to queries over **joined relations** so that the mechanism is provably $(\varepsilon,\delta)$-DP yet yields *usable accuracy* despite worst-case influence. Variants: *counting/aggregation* queries (the core case), *self-joins* (a tuple appears on both sides), *multi-way joins* (sensitivity compounds), and the *optimization* variant — minimize added noise / maximize utility subject to the DP constraint.

## 2. Mathematical Foundations

A mechanism $M$ is **$(\varepsilon,\delta)$-DP** if for neighboring databases $D \sim D'$ and all events $S$, $\Pr[M(D)\in S] \le e^{\varepsilon}\Pr[M(D')\in S] + \delta$ (Dwork–McSherry–Nissim–Smith, TCC 2006). The *neighbor* relation encodes the privacy unit; under foreign keys, **user-level DP** removes *all* tuples linked to one entity, which can cascade across joins.

**Global sensitivity** $\Delta f = \max_{D\sim D'} \lVert f(D)-f(D')\rVert_1$ is unbounded for joins. Two principled fixes:

- **Local / smooth sensitivity** (Nissim–Raskhodnikova–Smith, STOC 2007): calibrate to instance-specific sensitivity $LS_f(D)$, smoothed to remain DP. For joins, $LS$ relates to the **maximum degree** of join keys.
- **Lipschitz extensions / truncation:** for graph-pattern and join counting, **restricted sensitivity** on bounded-degree instances and Lipschitz extensions to all instances (Blocki–Blum–Datta–Sheffet; Kasiviswanathan et al. on subgraph counting) give finite, tight sensitivity. Counting join results is essentially **counting homomorphisms / subgraph occurrences**, whose sensitivity is governed by degree bounds and connects to the **AGM bound** on join size $\prod_e |R_e|^{x_e}$ over a fractional edge cover $x$.

The general engine is **truncation + sensitivity analysis**: bound each entity's contribution (degree/multiplicity cap $\tau$), making sensitivity $\propto \tau$ (or a function of the join structure), then add noise scaled to that bound and pay a (small, DP-accounted) cost for the truncation bias.

## 3. State of the Art (SOTA)

**Theory-SOTA.** Johnson–Near–Song's **elastic sensitivity** (VLDB 2018, the *FLEX* system) upper-bounds local sensitivity of general SQL joins without running the data, enabling practical DP-SQL. **Residual sensitivity** (Dong–Fang–Yi, ICDE/SIGMOD 2021–2022) tightens this for multi-way joins. Tao–McKenna–Miklau–Hay–Machanavajjhala and the **R2T (Race-to-the-Top)** framework (SIGMOD 2022) give instance-optimal truncation for self-join-free and joined aggregation queries with near-optimal utility.

**Systems-SOTA.** Google's **DP SQL** / PipelineDP and the **Zetasql DP** operators implement bounded-contribution (per-user row capping) for joins; **Tumult Analytics** and **OpenDP** support truncation-based join DP; PINQ/wPINQ (McSherry; Proserpio–Goldberg–McSherry, VLDB 2014) pioneered DP query operators with weighted sensitivity for joins.

## 4. Upper Bound

For aggregation over joins, **R2T** (Dong–Yi, SIGMOD 2022) achieves a $(\varepsilon,\delta)$-DP answer with error that is **instance-optimal up to a logarithmic factor** relative to the best truncation threshold — error scaling roughly as $O(\Delta_\tau \cdot \mathrm{polylog})$ where $\Delta_\tau$ is the sensitivity at the optimally chosen contribution cap $\tau$. Elastic/residual sensitivity yields finite, data-independent-to-compute noise scales for arbitrary SQL joins (sound DP), at the cost of looser-than-optimal constants on adversarial high-degree instances. Linear queries over a single relation remain the easy $O(1/\varepsilon)$ baseline.

## 5. Lower Bound

The unbounded-influence pathology is fundamental: for a query whose **global sensitivity is infinite**, *no* DP mechanism can answer with bounded error in the worst case without contribution bounding — an information-theoretic impossibility, since neighboring databases can be made arbitrarily far in output. Even with truncation, error must scale with the *true* maximum degree on worst-case instances; for **subgraph/join counting** there are matching lower bounds showing dependence on the maximum-degree / arboricity is unavoidable (lower bounds via packing/coupling arguments, Kasiviswanathan–Nissim–Raskhodnikova–Smith). For multi-way joins the sensitivity can grow with the AGM bound, forcing error polynomial in degree. These are *accuracy* lower bounds (not hardness of computation), and they are believed but not fully tight for general acyclic vs. cyclic joins.

## 6. The Gap

Genuinely **open**. We have sound mechanisms (elastic/residual sensitivity) and instance-optimal-up-to-log results for important fragments (self-join-free aggregation, R2T), but: (i) **self-joins and cyclic multi-way joins** lack instance-optimal mechanisms with tight accuracy; (ii) the right **privacy unit under multiple foreign keys** (e.g. an entity appearing as both a user and a counterparty) is unsettled, and composition across a schema graph is hard to account tightly; (iii) the **upper/lower-bound gap is the log factor (and worse for cyclic joins)** plus the unquantified utility cost of truncation bias. Closing it needs mechanisms whose error matches the join-structure-dependent lower bound for *all* (including cyclic, self-) joins, with a clean schema-level privacy semantics.

## 7. Current Research (as of June 2026)

Active threads: **instance-optimal DP for self-joins and cyclic queries** extending R2T/residual sensitivity *(frontier — verify)*; **schema-aware / multi-relation privacy units** and per-entity contribution accounting across foreign-key graphs *(frontier — verify)*; integration into production DP-SQL engines (Tumult, Google PipelineDP, OpenDP) with join support; and connections between **worst-case-optimal join algorithms** and DP sensitivity (using AGM/fractional-edge-cover structure to bound noise). Groups/people: Xiao & Yi (HKUST), Gerome Miklau, Ashwin Machanavajjhala, Michael Hay (UMass/Tumult Labs), Joseph Near (Vermont), Frank McSherry, and the OpenDP/Harvard group.

## 8. Future Work

- Instance-optimal, tight-accuracy DP mechanisms for self-joins, cyclic, and general multi-way joins.
- A principled, composable **schema-level privacy unit** under multiple foreign keys.
- Tight upper/lower bounds expressed via fractional edge cover / arboricity of the join.
- DP join *operators* that compose inside a query planner with end-to-end accounting (links to authorization-aware optimization).
- Empirical accuracy benchmarks on realistic skewed-degree foreign-key data.

## 9. Key References

- **[Foundational]** Dwork, C., McSherry, F., Nissim, K., Smith, A. *Calibrating Noise to Sensitivity in Private Data Analysis.* TCC, 2006.
- **[Foundational]** Nissim, K., Raskhodnikova, S., Smith, A. *Smooth Sensitivity and Sampling in Private Data Analysis.* STOC, 2007.
- **[SOTA]** Johnson, N., Near, J.P., Song, D. *Towards Practical Differential Privacy for SQL Queries.* VLDB, 2018.
- **[SOTA]** Dong, W., Fang, J., Yi, K. *Residual Sensitivity for Differentially Private Multi-Way Joins.* SIGMOD, 2021.
- **[SOTA]** Dong, W., Yi, K. *R2T: Instance-Optimal Truncation for Differentially Private Query Evaluation with Foreign Keys.* SIGMOD, 2022.
- **[SOTA]** Proserpio, D., Goldberg, S., McSherry, F. *Calibrating Data to Sensitivity in Private Data Analysis (wPINQ).* VLDB, 2014.
- **[Survey]** Dwork, C., Roth, A. *The Algorithmic Foundations of Differential Privacy.* Foundations and Trends in TCS, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
