---
id: 19-temporal-databases/allen-relation-optimization
title: "Allen-Relation Query Optimization"
topic: 19-temporal-databases
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Allen-Relation Query Optimization

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/allen-relation-optimization` · **Status:** open

## 1. Problem Statement

Queries over interval-timestamped data are expressed in terms of **Allen's 13 interval relations** — `before`, `meets`, `overlaps`, `starts`, `during`, `finishes`, their inverses, and `equals`. A temporal join such as "find pairs of orders whose validity intervals *overlap*" is a $\theta$-join with a band/interval predicate, and a sequence query (`A meets B meets C`) is a chain of such joins. The problem has three coupled parts:

1. **Algebraic rewriting:** find a sound, ideally complete set of equivalences that rewrite Boolean combinations of Allen predicates into a normal form an optimizer can cost — including pushing Allen selections through joins, merging consecutive predicates (transitivity of the Allen composition table), and converting disjunctions of relations into range/band predicates.
2. **Selectivity estimation:** estimate the result cardinality of each Allen predicate (a precondition for join ordering) — see also *Temporal Selectivity Estimation*.
3. **Physical operator choice:** decide between sort-merge interval joins, index-nested-loop on interval trees, and partition/forward-scan plans.

The decision variant: given a conjunctive temporal query and a cost model, does a plan of cost $\le k$ exist? The optimization variant: find the minimum-cost plan. Allen composition turns predicate simplification into a constraint-network consistency problem, which is the source of hardness.

## 2. Mathematical Foundations

Each interval $I=[I^-,I^+]$, $I^-\le I^+$, lives in $\mathbb{T}$. The 13 Allen relations partition $\{(I,J)\}$ exactly; e.g. $I \;\mathsf{overlaps}\; J \iff I^- < J^- < I^+ < J^+$. Each relation is a conjunction of $\le$/$<$ inequalities on the four endpoints, so an Allen predicate is a **band predicate** in endpoint space. **Allen's composition table** gives, for relations $R,S$, the set $R\circ S$ of possible relations between $I$ and $K$ given $I\,R\,J$ and $J\,S\,K$; this is the algebra used to simplify predicate chains.

Key results:
- Deciding consistency of a network of **disjunctive** Allen constraints is **NP-complete** (Vilain–Kautz), but the **ORD-Horn** subclass and the pointizable / continuous-endpoint fragment are tractable (Nebel–Bürckert), bounding which rewrites are cheap.
- A conjunctive Allen predicate maps to a constant number of inequalities, so a temporal join is a **multi-band join**; the AGM bound and worst-case-optimal join theory (Ngo–Ré–Rudra) apply when several interval predicates are combined.
- Sort-merge over interval endpoints exploits the sweep-line paradigm; the *overlap* join has output-sensitive lower bounds $\Omega(n\log n + k)$ for $k$ outputs.

## 3. State of the Art (SOTA)

- **Theory:** Allen (CACM 1983) interval algebra; Vilain–Kautz (AAAI 1986) NP-completeness; **Nebel–Bürckert (JACM 1995)** maximal tractable ORD-Horn class. These bound which predicate simplifications the optimizer may do in PTIME.
- **Systems / interval joins:** **Overlap Interval Partition Join (OIP)** and **Endpoint-Index / Disjoint-Interval-Partitioning (DIP)** joins (Dignös, Böhlen, Gamper, SIGMOD 2014 — *Overlap Interval Partition Join*); **Forward-scan based plane-sweep** interval joins (Piatov, Helmer, Dignös, VLDB 2016); **lazy/eager interval-tree** plans. The **temporal algebra with "scaling/aligning"** of Dignös et al. (SIGMOD 2012) reduces all 13 relations to a normalized timestamp-propagation, enabling reuse of relational operators.
- **Systems:** PostgreSQL `range` types + GiST/SP-GiST indexes; SQL:2011 `OVERLAPS`/`PERIOD`; HANA and Db2 interval support.

## 4. Upper Bound

A single Allen-predicate **overlap join** over $n+m$ intervals producing $k$ pairs runs in $O((n+m)\log(n+m) + k)$ via plane sweep / forward scan (Piatov et al.), which is **output-optimal**. Simplifying a *conjunctive* chain of Allen predicates via the composition table is polynomial. For the **ORD-Horn** fragment, network consistency and thus predicate minimization is in PTIME (Nebel–Bürckert). Multi-predicate temporal joins admit worst-case-optimal evaluation in $O(\text{AGM} + \text{out})$ via WCOJ algorithms treating endpoints as variables.

## 5. Lower Bound

For **disjunctive** Allen constraint networks (e.g. predicates of the form "$\mathsf{before} \lor \mathsf{meets} \lor \mathsf{overlaps}$"), deciding satisfiability/minimal-network is **NP-complete** (Vilain–Kautz 1986; full classification by Nebel–Bürckert), so optimal predicate simplification across disjunctions cannot be polynomial unless P=NP. Interval-overlap join has an $\Omega(n\log n)$ comparison lower bound from element-distinctness, plus the unavoidable $\Omega(k)$ output term. Certain self-join temporal patterns reduce to **3SUM / set-intersection** style problems, giving fine-grained $n^{2-o(1)}$ conditional lower bounds for listing all triangle-like `meets`-chains *(frontier — verify)*.

## 6. The Gap

For *conjunctive* single-predicate joins the gap is essentially **closed** — plane-sweep is output-optimal. The open gap is (a) **cost-based choice across the full disjunctive Allen algebra**, where optimal simplification is NP-hard yet practical queries need good heuristics with guarantees, and (b) **selectivity-aware join ordering** for multi-way temporal joins, which is bottlenecked by estimation quality (cross-reference *Temporal Selectivity Estimation*). Whether a tight approximation algorithm exists for cost-optimal disjunctive-Allen plans is unknown.

## 7. Current Research (as of June 2026)

Active: GPU/SIMD-vectorized interval joins; integrating WCOJ into temporal engines so multi-way Allen joins avoid intermediate blow-up *(frontier — verify)*; learned cost models for interval predicates; and pushing Dignös-style temporal normalization into mainstream optimizers (PostgreSQL range-join planning). Central groups: Böhlen/Dignös/Gamper (Zurich/Bolzano), Piatov/Helmer, and the AI side (Nebel) for the algebra. Recent VLDB/SIGMOD work targets temporal joins on modern hardware *(frontier — verify)*.

## 8. Future Work

- A complete, optimizer-friendly rewrite calculus covering all disjunctive Allen relations with approximation guarantees.
- Worst-case-optimal multi-way temporal join operators shipped in real engines.
- Joint optimization of Allen rewriting with selectivity estimation and physical operator selection.
- Fine-grained complexity classification of common temporal-join patterns.

## 9. Key References

- **[Foundational]** Allen, J.F. *Maintaining Knowledge about Temporal Intervals.* CACM, 1983. — [DOI](https://doi.org/10.1145/182.358434)
- **[Foundational]** Vilain, M., Kautz, H. *Constraint Propagation Algorithms for Temporal Reasoning.* AAAI, 1986. — [DBLP](https://dblp.org/rec/conf/aaai/VilainK86.html)
- **[Foundational]** Nebel, B., Bürckert, H.-J. *Reasoning about Temporal Relations: A Maximal Tractable Subclass of Allen's Interval Algebra.* JACM, 1995. — [DOI](https://doi.org/10.1145/200836.200848)
- **[SOTA]** Dignös, A., Böhlen, M.H., Gamper, J. *Overlap Interval Partition Join.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2612175)
- **[SOTA]** Piatov, D., Helmer, S., Dignös, A. *An Interval Join Optimized for Modern Hardware.* VLDB / ICDE, 2016. — [DOI](https://doi.org/10.1109/ICDE.2016.7498316)
- **[Foundational]** Ngo, H.Q., Ré, C., Rudra, A. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013. — [arXiv](https://arxiv.org/abs/1310.3314)

## 10. Worked Example

**An `overlaps` join via plane sweep, plus a transitivity rewrite.** Two interval relations on a shared timeline:

$R = \{r_1{=}[1,4],\ r_2{=}[6,9]\}$, $S = \{s_1{=}[3,7],\ s_2{=}[8,10]\}$. We want pairs with $r\;\mathsf{overlaps}\;s$, i.e. $r^- < s^- < r^+ < s^+$.

Sort all $4+4=8$ endpoints and sweep left to right, keeping an *active set* of open intervals. When $s_1$ opens at $3$, $r_1=[1,4]$ is active and $r_1^- {=}1 < s_1^- {=}3 < r_1^+{=}4 < s_1^+{=}7$ holds — emit $(r_1,s_1)$. When $s_2$ opens at $8$, $r_2=[6,9]$ is active and $6<8<9<10$ — emit $(r_2,s_2)$. Total cost $O((n{+}m)\log(n{+}m)+k)$ with $n{+}m{=}4$ intervals and $k{=}2$ outputs: the $\log$ term is the endpoint sort, $k$ the result writes — matching the output-optimal bound of §4.

**Composition-table rewrite:** if a query asks `A meets B` and `B meets C`, Allen's table gives $\mathsf{meets}\circ\mathsf{meets}=\{\mathsf{before}\}$, so the optimizer infers $A\;\mathsf{before}\;C$ as a derived (cheaper, indexable) range predicate instead of recomputing it — a sound conjunctive simplification done in PTIME, unlike the NP-complete disjunctive case of §5.

---
*Part of the [DBMS Research catalog](../../README.md).*
