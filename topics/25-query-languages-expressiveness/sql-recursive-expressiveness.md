---
id: 25-query-languages-expressiveness/sql-recursive-expressiveness
title: "Expressive Power and Limits of SQL Recursion"
topic: 25-query-languages-expressiveness
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Expressive Power and Limits of SQL Recursion

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/sql-recursive-expressiveness` · **Status:** partially-solved

## 1. Problem Statement

SQL gained recursion via `WITH RECURSIVE` (SQL:1999, the recursive **common table expression**, CTE). The question is: **what exactly can recursive SQL express**, and how does it compare to Datalog and to the fixpoint logics of descriptive complexity? Sub-questions:

- **Linear vs. mutual/non-linear recursion:** the SQL standard mandates *linear* recursion (the recursive table referenced once, non-nested, no aggregation/`DISTINCT`-violating constructs) — does this restrict expressiveness relative to general (non-linear) Datalog?
- **With vs. without negation/aggregation in the recursive step:** vendors permit non-standard extensions (`UNION ALL` vs `UNION`, aggregates, window functions); what do these add?
- **Placement in the hierarchy:** is recursive SQL = transitive closure logic, = (stratified) Datalog, = $\mathrm{FO}{+}\mathrm{LFP}$, or somewhere between?

This is **partially solved**: the core inflationary/transitive-closure correspondence is understood, but the precise expressiveness of real-world recursive SQL (with its aggregation, ordering, and termination semantics) is not fully characterized.

## 2. Mathematical Foundations

Foundations sit in **descriptive complexity**:

- Pure relational algebra / SQL `SELECT` (no recursion) $\equiv \mathrm{FO}$ (with aggregates: $\mathrm{FO}{+}\text{counting/arithmetic}$). FO cannot express **transitive closure** (reachability) — a classic Ehrenfeucht–Fraïssé / locality (Hanf/Gaifman) result.
- **Transitive-closure logic** $\mathrm{FO}{+}\mathrm{TC}$ captures NLOGSPACE on ordered structures (Immerman); **deterministic** $\mathrm{FO}{+}\mathrm{DTC}$ captures LOGSPACE.
- **(Inflationary) fixpoint logic** $\mathrm{FO}{+}\mathrm{IFP}$ captures PTIME on ordered structures (Immerman–Vardi).
- **Datalog** = monotone $\exists$-positive least-fixpoint logic; with stratified negation $\equiv \mathrm{FO}{+}\mathrm{IFP}$ on ordered structures.

**Recursive SQL semantics** is *iterative*: the working table is seeded by the non-recursive term, then the recursive term is applied repeatedly until no new rows appear (`UNION` = set, deduplicating, guarantees termination on finite structures; `UNION ALL` accumulates and may not terminate). Linear recursion with `UNION` over set semantics computes a **least fixpoint** and corresponds to **linear Datalog**, which over ordered structures captures exactly the queries expressible by **(linear) transitive-closure**-style fixpoints. Aggregates inside recursion (non-standard) push beyond monotone Datalog toward **Datalog with aggregation / stratified counting**.

## 3. State of the Art (SOTA)

- **Theory:** Standard-conforming `WITH RECURSIVE` (linear, set semantics, no aggregation) is equivalent in expressive power to **linear Datalog** (least fixpoint of a linear program). Linear Datalog $\subsetneq$ full Datalog in general (e.g., **same-generation** style and certain path problems separate linear from non-linear) — though many natural queries (reachability/TC) are already linear. Reference points: Abiteboul–Hull–Vianu (1995); Libkin's *Elements of Finite Model Theory* (2004).
- **Systems:** PostgreSQL, SQL Server, Oracle (`CONNECT BY` and CTE), DB2 implement linear recursive CTEs; many now allow aggregates/window functions in/around recursion, and some optimize recursive CTEs into semi-naïve evaluation. Engines like **Umbra/HyPer** and **DuckDB** implement efficient recursive CTE evaluation; research systems compile SQL recursion to Datalog-style semi-naïve plans.
- A recognized fact: standard SQL forbids non-linear (mutual) recursion and aggregation in the recursive term, so **full Datalog is not directly expressible** in standard SQL, though vendor extensions and rewrites narrow the gap.

## 4. Upper Bound

- Standard linear recursive SQL is contained in **linear Datalog** $\subseteq \mathrm{FO}{+}\mathrm{LFP}$, hence **PTIME data complexity** (semi-naïve evaluation runs in polynomial time; reachability-style queries in $O(|E|\cdot|V|)$ worst case, often near-linear with indexing).
- With set semantics and finite domains, termination is guaranteed; the number of iterations is bounded by the size of the (finite) least fixpoint.
- Permitting **stratified aggregation/negation** around recursion lifts the upper bound to **stratified Datalog** $\equiv \mathrm{FO}{+}\mathrm{IFP}$ on ordered structures = **PTIME**. So recursive SQL with stratified aggregation does not exceed PTIME data complexity.

## 5. Lower Bound

- **FO cannot express transitive closure** (locality / Ehrenfeucht–Fraïssé) — so non-recursive SQL is strictly weaker; recursion is genuinely needed. This is the foundational *separation* lower bound.
- **Linear vs. non-linear Datalog separation:** there exist Datalog-expressible queries **not** expressible by any linear Datalog program (Afrati–Cosmadakis; Kanellakis), implying standard linear `WITH RECURSIVE` is strictly less expressive than full Datalog. The classic witnesses involve "branching" recursions not reducible to linear chains.
- Data-complexity lower bound: reachability is **NLOGSPACE-complete**, so any system expressing it faces the corresponding space lower bound; full linear-recursion least fixpoints are **PTIME-hard** under appropriate reductions.

## 6. The Gap

The gap is between **clean theory** and **real SQL**. The linear-Datalog correspondence is established, and linear-vs-full separations are known. What remains open/partially-solved: a *precise* expressiveness characterization of **recursive SQL as actually specified and implemented** — including `UNION ALL` accumulation, aggregation/window functions in the recursive term, ordering-dependent semantics, and non-termination. There is no fully agreed formal semantics-and-expressiveness theorem covering vendor recursive SQL with aggregation. Closing it requires a formal model of these features and matching upper/lower expressiveness bounds.

## 7. Current Research (as of June 2026)

- **Formal semantics of recursive SQL with aggregation/window functions** and its expressive characterization, building on monotonic-aggregation theory (Datalog$^\circ$ / semi-naïve over semirings; Khamis, Ngo, Pichler, Suciu) *(frontier — verify)*.
- **Compilation of SQL recursion to Datalog engines** (Soufflé, RecStep, Umbra) and worst-case-optimal recursive joins; mutual-recursion rewrites *(frontier — verify)*.
- **Recursive SQL for graph workloads** and its interplay with SQL:2023 **property-graph queries (SQL/PGQ)** and GQL — relating path-pattern recursion to CTE recursion.
- Monotone-aggregation (`Datalog°`, pre-mappable semirings) to make aggregation-in-recursion well-defined and PTIME.
- Groups: Washington (Suciu), RelationalAI (Khamis, Ngo), TU Munich (Neumann/Umbra), Edinburgh (Libkin — semantics of SQL nulls/recursion).

## 8. Future Work

- A definitive **expressiveness theorem for vendor recursive SQL** including aggregation and `UNION ALL`.
- Standardizing **safe mutual/non-linear recursion** with guaranteed termination.
- Optimization: **worst-case-optimal** and incremental evaluation of recursive CTEs.
- Bridging recursive SQL with **SQL/PGQ + GQL** path semantics under one fixpoint theory.

## 9. Key References

- **[Foundational]** E. F. Codd. *A relational model of data for large shared data banks.* CACM, 1970. — [DOI](https://doi.org/10.1145/362384.362685)
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (Datalog, fixpoint logics, linear recursion). — [book](http://webdam.inria.fr/Alice/)
- **[Foundational]** L. Libkin. *Elements of Finite Model Theory.* Springer, 2004 (locality, TC, fixpoint capture). — [DOI](https://doi.org/10.1007/978-3-662-07003-1)
- **[Foundational]** F. Afrati, S. Cosmadakis. *Expressiveness of restricted recursive queries.* STOC 1989 (linear vs. non-linear Datalog). — [DOI](https://doi.org/10.1145/73007.73018)
- **[SOTA]** M. A. Khamis, H. Ngo, R. Pichler, D. Suciu, et al. *Convergence of Datalog over (pre-)semirings / Datalog°.* PODS 2022 (monotone aggregation in recursion). — [arXiv](https://arxiv.org/abs/2105.14435) · [DOI](https://doi.org/10.1145/3517804.3524140)
- **[Survey]** N. Immerman. *Descriptive Complexity.* Springer, 1999 (TC, DTC, IFP capture results). — [DOI](https://doi.org/10.1007/978-1-4612-0539-5)

## 10. Worked Example

Let $\mathsf{Edge}(src,dst)$ hold a chain $1\!\to\!2,\;2\!\to\!3,\;3\!\to\!4$. The standard linear recursive CTE for reachability:

```sql
WITH RECURSIVE reach(s, d) AS (
  SELECT src, dst FROM Edge                         -- seed (non-recursive)
  UNION                                             -- set semantics: dedup, terminates
  SELECT r.s, e.dst FROM reach r JOIN Edge e ON r.d = e.src
)
SELECT * FROM reach;
```

**Semi-naïve trace** (working set $\Delta$ of *new* tuples each round):

- Round 0 (seed): $\{(1,2),(2,3),(3,4)\}$.
- Round 1 (join $\Delta$ with Edge): $(1,2){\bowtie}(2,3)\to(1,3)$, $(2,3){\bowtie}(3,4)\to(2,4)$. New: $\{(1,3),(2,4)\}$.
- Round 2: $(1,3){\bowtie}(3,4)\to(1,4)$. New: $\{(1,4)\}$.
- Round 3: no new tuples — fixpoint reached.

Result $= \{(1,2),(1,3),(1,4),(2,3),(2,4),(3,4)\}$, exactly the transitive closure.

This is **linear Datalog**: the recursive rule references $\mathsf{reach}$ once. The iteration count $3$ equals the longest path length, bounded by $|V|-1$, giving **PTIME** data complexity. The key expressiveness point: this query is provably **not** expressible in FO (no recursion) — `reach` separates recursive from non-recursive SQL. Switching `UNION` to `UNION ALL` on a cyclic graph would lose the dedup and **not terminate**.

---
*Part of the [DBMS Research catalog](../../README.md).*
