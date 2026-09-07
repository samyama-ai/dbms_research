---
id: 03-query-processing/recursive-fixpoint-execution
title: "Recursive and fixpoint query execution"
topic: 03-query-processing
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Recursive and fixpoint query execution

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/recursive-fixpoint-execution` · **Status:** open

## 1. Problem Statement

Efficiently evaluate **recursive queries** — Datalog programs and SQL `WITH RECURSIVE` — by
computing the least fixpoint of a monotone (or stratified) operator over the database, using
**set-at-a-time** (bulk, vectorized/relational) execution rather than tuple-at-a-time
iteration. The canonical engine technique is **semi-naive evaluation**, which avoids
recomputing already-derived facts each round; the open problem is to go *beyond* semi-naive:
to evaluate recursion with the right joins, the right delta representation, optimal
scheduling of rules, and worst-case-optimal join machinery, while integrating aggregation
and negation.

Formally: given a Datalog program $\Pi$ with immediate-consequence operator $T_\Pi$ and an
input database $D$, compute the least fixpoint $T_\Pi^\omega(D) = \bigcup_k T_\Pi^k(D)$.

- **Decision variant:** is a given fact $a$ in the least fixpoint? (Datalog evaluation is
  P-complete in combined-with-program / data complexity is in PTIME.)
- **Optimization variant:** minimize total work (joins, materialized deltas, iterations) to
  reach the fixpoint — choose join orders, magic-set rewrites, and worst-case-optimal plans.
- **Maintenance variant:** incrementally maintain the fixpoint under updates (DRed, etc.).

It is **open** in the sense that we lack provably work-optimal recursive execution: the best
asymptotic bounds for evaluating recursive programs (and even reachability-style queries)
are not known to be tight, and integrating WCOJ + factorization + aggregation into recursion
remains unsettled.

## 2. Mathematical Foundations

A Datalog program defines a monotone operator $T_\Pi:\,2^{B}\to 2^{B}$ over the Herbrand
base $B$; by **Knaster–Tarski**, $T_\Pi$ has a least fixpoint reached in $\le |B|$ steps,
and naive iteration computes $T_\Pi^{k+1}=T_\Pi(T_\Pi^k)$ until $T_\Pi^{k+1}=T_\Pi^k$.
**Semi-naive** evaluation tracks the *delta* $\Delta^k = T_\Pi^k \setminus T_\Pi^{k-1}$ and
re-evaluates each rule using the differential

$$\delta R \;=\; \bigcup_i \big(R_1 \bowtie \cdots \bowtie \Delta R_i \bowtie \cdots \bowtie R_m\big),$$

so each derivation fires once, giving total join work proportional to the number of
*new* derivations rather than re-deriving everything every round. Complexity is governed by
**data complexity** (PTIME, in fact in $\mathsf{NC}$/P-complete for linear vs. general
recursion) and by the **join structure** of each rule body — to which the **AGM bound** and
**worst-case-optimal join** (Ngo–Porat–Ré–Rudra) apply per iteration. **Magic sets** rewrite
$\Pi$ to push query bindings (sideways information passing) so that only relevant facts are
derived, mimicking top-down (SLD) goal-directedness in a bottom-up engine. For semiring-/
aggregate recursion the operator must be over an **$\omega$-continuous semiring** (e.g.
tropical for shortest paths), and **stratified negation** orders strata to preserve a
well-defined fixpoint.

## 3. State of the Art (SOTA)

- **Theory/foundational:** **Bancilhon, Maier, Sagiv, Ullman** *Magic Sets* (PODS 1986) and
  the semi-naive evaluation framework (Bancilhon–Ramakrishnan) are the bedrock; Abiteboul–
  Hull–Vianu's text is canonical.
- **Systems SOTA:** **Soufflé** (Scholz et al., CC 2016) compiles Datalog to high-performance
  parallel C++ with specialized data structures (Brie/B-tree) and is the modern reference;
  **DDlog** and **Differential Dataflow / DBSP** (McSherry et al.; Budiu et al., VLDB 2023)
  give *incremental* fixpoint maintenance with strong theoretical guarantees. **LogicBlox**
  and **RecStep** scaled Datalog over relational engines. **DuckDB / SQL `WITH RECURSIVE`**
  brings semi-naive into mainstream SQL engines.
- **WCOJ + recursion:** worst-case-optimal joins inside recursive rules and **free-join**
  ideas (Wang, Willsey, Suciu, SIGMOD 2023) are the current frontier for per-iteration
  optimality; **egglog** unifies Datalog with e-graph (equality saturation) execution.

## 4. Upper Bound

In data complexity, Datalog evaluation is in **PTIME** (and the least fixpoint is reached in
$\le |D|^{a}$ iterations where $a$ is the max arity / number of IDB variables). Per
iteration, semi-naive bounds work by the number of new derivations; combined with WCOJ each
rule body of fractional edge cover number $\rho^\ast$ costs $O(N^{\rho^\ast})$, so a round is
$O(\sum_{\text{rules}} N^{\rho^\ast} )$ and the whole evaluation is that times the number of
rounds. For **linear recursion** (e.g. transitive closure) this gives the classic
$O(n^3)$-style (or $O(n^\omega)$ via matrix multiplication for reachability/closure) bounds.
The general upper bound is "polynomial in $|D|$" with exponent tied to arity and
$\rho^\ast$; no universally tight, output-sensitive upper bound is known for arbitrary $\Pi$.

## 5. Lower Bound

- **P-completeness:** general (non-linear) Datalog evaluation is **P-complete** (under
  log-space reductions), so it is inherently sequential — *no efficient parallel (NC)
  algorithm unless $\mathsf{NC}=\mathsf{P}$*. This is the central lower bound on
  parallelizability.
- **Fine-grained:** transitive closure / reachability fixpoints are subject to the
  **APSP and Boolean-matrix-multiplication** barriers — combinatorial BMM is conjectured to
  need $n^{3-o(1)}$, so truly subcubic combinatorial closure would be a breakthrough; thus
  recursive reachability execution inherits these conditional lower bounds.
- Per-iteration joins inherit the **AGM** output-size lower bound, so a round cannot beat
  $\Omega(N^{\rho^\ast})$ in the worst case (matching WCOJ).

## 6. The Gap

For *linear* recursion and well-behaved programs, semi-naive plus WCOJ is close to optimal
per round, but the **number-of-iterations × per-round-cost** product is not known to be
tight, and we lack output-sensitive, *instance-optimal* recursive execution. The deeper gap:
P-completeness blocks generic parallel speedup, yet many practical programs *are*
parallelizable — characterizing which programs admit sublinear-depth (NC) evaluation is open.
Integrating factorized representations, aggregation over $\omega$-continuous semirings, and
incremental maintenance into one provably-optimal recursive engine is unsolved. Closing it
needs both a tighter complexity theory of fixpoints and engines unifying WCOJ + semi-naive +
factorization.

## 7. Current Research (as of June 2026)

- **Suciu / Willsey (UW)** — *free join*, egglog, and equality-saturation-as-Datalog,
  bringing WCOJ-optimal execution into recursive/e-graph settings *(frontier — verify)*.
- **Soufflé group (Scholz, Jordan)** — compiled parallel Datalog, specialized index data
  structures, and provenance for recursion.
- **DBSP / Materialize (McSherry, Budiu)** — incremental, differential fixpoint computation
  with a clean algebra (Z-sets), now formalized for full recursive SQL *(frontier — verify)*.
- **Semiring/aggregate recursion** (pre-/post-fixpoint with monotone aggregation, e.g.
  *Datalog$^\circ$* of Abo Khamis–Ngo–Pichler–Suciu) generalizing shortest-path-style
  recursion *(frontier — verify)*.

## 8. Future Work

- Output-sensitive / instance-optimal recursive evaluation bounds.
- A characterization of parallelizable (low-depth) recursive programs beyond linear recursion.
- Unified engine: WCOJ + factorization + monotone-aggregate semiring recursion + incremental
  maintenance.
- Adaptive scheduling of rule/strata evaluation and magic-set vs. bottom-up choice.

## 9. Key References

- **[Foundational]** F. Bancilhon, D. Maier, Y. Sagiv, J. D. Ullman. *Magic Sets and Other Strange Ways to Implement Logic Programs.* PODS, 1986. — [DOI](https://doi.org/10.1145/6012.15399)
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[SOTA]** B. Scholz, H. Jordan, P. Subotić, T. Westmann. *On Fast Large-Scale Program Analysis in Datalog (Soufflé).* CC, 2016. — [DOI](https://doi.org/10.1145/2892208.2892226)
- **[SOTA]** Y. R. Wang, M. Willsey, D. Suciu. *Free Join: Unifying Worst-Case Optimal and Traditional Joins.* SIGMOD, 2023. — [arXiv](https://arxiv.org/abs/2301.10841) — [DOI](https://doi.org/10.1145/3589295)
- **[SOTA]** M. Budiu, T. Chajed, F. McSherry, et al. *DBSP: Automatic Incremental View Maintenance for Rich Query Languages.* PVLDB, 2023. — [DOI](https://doi.org/10.14778/3587136.3587137)
- **[SOTA]** M. Abo Khamis, H. Q. Ngo, R. Pichler, D. Suciu, et al. *Convergence of Datalog over (Pre-)Semirings (Datalog°).* PODS, 2022. — [arXiv](https://arxiv.org/abs/2105.14435) — [DOI](https://doi.org/10.1145/3517804.3524140)

## 10. Worked Example

**Semi-naive transitive closure.** Rules: $T(x,y) \leftarrow E(x,y)$ and $T(x,z) \leftarrow T(x,y), E(y,z)$. Edge relation: a path $E = \{(1,2),(2,3),(3,4)\}$.

| iter | $\Delta T$ (new facts) |
|------|------------------------|
| 0    | $(1,2),(2,3),(3,4)$ |
| 1    | $\Delta T \bowtie E$: $(1,3),(2,4)$ |
| 2    | $(1,3),(2,4)\bowtie E$: $(1,4)$ |
| 3    | $(1,4)\bowtie E$: $\varnothing$ — fixpoint |

Each round the differential $\delta T = \Delta T \bowtie E$ joins **only the new** $T$ tuples against $E$, never re-deriving old pairs. Total derivations $= 3+2+1 = 6 = \binom{4}{2}$, exactly the reachable pairs — no fact derived twice.

Naive evaluation would instead recompute the full $T \bowtie E$ each round, re-deriving $(1,3)$ and $(2,4)$ repeatedly. The number of iterations equals the longest path length ($\le n-1$), and each round's join cost is bounded per-rule by its AGM/$\rho^\ast$ bound — illustrating the "iterations $\times$ per-round-cost" product whose tightness remains open.

---
*Part of the [DBMS Research catalog](../../README.md).*
