# Sequenced Semantics Query Rewriting

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/sequenced-semantics-rewriting` · **Status:** partially-solved

## 1. Problem Statement
Temporal queries come in three semantics (Snodgrass/TSQL2): **nonsequenced** (treat time as an ordinary attribute), **sequenced** (apply a nontemporal query *independently at every instant*, producing a time-varying result), and **current/as-of** (snapshot). The **sequenced** semantics is what users usually want — "the answer to $Q$ at each point in time" — but writing it directly in SQL is error-prone: it requires interval splitting/alignment, careful handling of joins over overlapping periods, and coalescing of the result.

The problem: **given an arbitrary nontemporal query $Q$ (relational algebra / SQL), automatically and *correctly* rewrite it into a query $Q^{seq}$ over interval-timestamped relations that computes the sequenced answer** — provably equivalent, at every instant, to evaluating $Q$ on the snapshot at that instant, then coalesced.

Variants:
- **Decision/equivalence:** is a candidate rewrite $Q^{seq}$ sequenced-equivalent to $Q$?
- **Optimization:** among correct rewrites, pick the cheapest (fewest splits/joins).
- **Coverage:** which fragments of SQL (negation, aggregation, outer join, subqueries, recursion) admit a correct automatic rewrite?

## 2. Mathematical Foundations
Let a temporal relation be a snapshot-indexed family $r = (r_\tau)_{\tau \in T}$ encoded by interval-timestamped tuples. The **sequenced** answer of operator $\theta$ is defined by the *snapshot-reducibility* criterion:
$$\tau^\tau(\theta^{seq}(r)) \;=\; \theta(\tau^\tau(r)) \quad \text{for all } \tau \in T,$$
where $\tau^\tau$ is the *timeslice* (snapshot at $\tau$). A rewriting is **correct** iff it is snapshot-reducible to the original operator. The key algebraic tool is the **temporal alignment / temporal splitting** primitive (Dignös–Böhlen–Gamper, SIGMOD 2012 / TODS 2016): every nontemporal operator $\theta$ has a sequenced counterpart obtained by *aligning* the period boundaries of the operands (splitting intervals at all relevant endpoints) and then applying $\theta$ attribute-wise, followed by coalescing. This yields a **reduction theorem**: temporal selection, projection, (anti)join, union, difference, and aggregation each reduce to their nontemporal versions over aligned inputs.

Foundations rest on the **point-based vs interval-based** duality (Toman; Chomicki–Toman): point-based semantics gives the gold-standard meaning; interval encodings must be *coalescing-normalized* so that interval representation does not leak into the result. SQL:2011 `PERIOD` predicates and `WITHOUT OVERLAPS` constraints provide the surface syntax over which the rewrite is expressed.

## 3. State of the Art (SOTA)
**Theory-SOTA:** The **alignment-based reduction** of Dignös, Böhlen, Gamper (and Dignös et al., "Temporal Query Processing", TODS 2016) gives a *complete, compositional* rewriting for sequenced relational algebra including aggregation and set difference — the strongest correctness result. Earlier, Toman's *point-based* SQL and Chomicki–Toman's temporal-logic foundations established the equivalence criteria. TSQL2 and the ATSQL "statement modifier" approach (Böhlen–Jensen–Snodgrass) proposed a *syntactic flag* (`SEQUENCED VALIDTIME`) that an engine expands into the rewrite.

**Systems-SOTA:** **Teradata** implements ANSI/ATSQL-style temporal statement modifiers (`SEQUENCED VALIDTIME`) doing the rewrite internally; **MariaDB** and **SQL Server** support SQL:2011 system-/application-time tables with period predicates but leave sequenced joins/aggregation largely to the user. The Dignös et al. techniques were prototyped in **PostgreSQL** (the "tpg"/temporal-PostgreSQL line) realizing aligned operators as rewrites; range/multirange types in PG make alignment expressible. No mainstream optimizer yet *cost-optimizes* among correct sequenced rewrites.

## 4. Upper Bound
For sequenced relational algebra (SPJUD + aggregation) the alignment reduction gives a **polynomial-size rewrite**: each operand is split at the $O(n)$ relevant endpoints, increasing tuple count by at most the number of overlapping boundaries, and the operator is applied once per aligned fragment — overall PTIME construction and evaluation cost within a polynomial factor of the nontemporal query, in the RAM model. Coalescing the output adds the $O(n\log n)$ coalescing cost. Thus every operator in the fragment has a *correct, polynomial* automatic rewrite (the rewrite problem is "solved" for this fragment); the residual cost is the splitting blow-up, bounded by total endpoint count.

## 5. Lower Bound
The splitting/alignment blow-up is intrinsic: a sequenced join of relations with $n$ and $m$ overlapping intervals can produce $\Omega(n+m)$ aligned fragments and an output whose interval structure is $\Omega(\text{intersections})$, lower-bounding any correct encoding by the **output size** of the point-based answer. For richer fragments the picture darkens: deciding **sequenced-equivalence** of two queries inherits the **undecidability** of containment/equivalence for relational calculus with negation, and is **NP-hard already for conjunctive** queries (containment is NP-complete). For queries with **aggregation and arithmetic** over dense time, exact equivalence checking is undecidable in general. These are NP-/undecidability bounds in the standard logical model, not fine-grained.

## 6. The Gap
Why **partially-solved**: for the well-behaved fragment — sequenced SPJUD plus standard aggregation under SQL:2011/ATSQL semantics — the alignment reduction provides a *provably correct, polynomial, compositional* automatic rewrite, essentially closing the correctness question and matching the output-size lower bound up to coalescing. The **open gap** lies in (i) **full SQL**: correlated subqueries, outer joins, window functions, recursion (temporal Datalog), and `NULL`/three-valued logic interacting with periods; (ii) **cost-based optimization** among correct rewrites (no principled optimizer); and (iii) **bitemporal** sequenced semantics (two time axes simultaneously). Equivalence-checking undecidability blocks a fully general verified rewriter.

## 7. Current Research (as of June 2026)
Active: (i) extending alignment-based rewriting to **window functions, outer joins, and recursive/temporal Datalog**, and integrating it into a **cost-based optimizer** (Dignös, Böhlen, Gamper at Free University of Bozen-Bolzano; Zürich); (ii) **bitemporal** sequenced operators and their normalization; (iii) standard-tracking of SQL:2011/202x application-time features across engines. *(frontier — verify)* Recent efforts apply *verified compilation* (proof-carrying rewrites, mechanized in Coq/Lean against the snapshot-reducibility criterion) and explore LLM-assisted generation of sequenced SQL checked against the alignment semantics as an oracle. Groups: Bozen-Bolzano temporal-DB group, Snodgrass/Dyreson (Arizona/Utah State), Toman (Waterloo) on point-based foundations.

## 8. Future Work
- Correct automatic rewrites for **full SQL** (outer joins, window functions, recursion, 3-valued logic).
- **Cost-based** selection among sequenced rewrites; minimizing split blow-up adaptively.
- **Bitemporal** sequenced semantics and its compositional reduction.
- **Mechanically verified** rewriters with snapshot-reducibility proof certificates.

## 9. Key References
- **[SOTA]** Dignös, A., Böhlen, M., Gamper, J., Jensen, C. S. *Extending the Kernel of a Relational DBMS with Comprehensive Support for Sequenced Temporal Queries.* ACM TODS, 2016. — [DOI](https://doi.org/10.1145/2967608)
- **[Foundational]** Dignös, A., Böhlen, M., Gamper, J. *Temporal Alignment.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213886)
- **[Foundational]** Böhlen, M., Jensen, C. S., Snodgrass, R. *Temporal Statement Modifiers.* ACM TODS, 2000. — [DOI](https://doi.org/10.1145/377674.377665)
- **[Foundational]** Chomicki, J., Toman, D. *Temporal Databases.* (Handbook of Temporal Reasoning in AI / point-based semantics), 2005. — [DOI](https://doi.org/10.1016/S1574-6526(05)80016-1)
- **[Foundational]** Snodgrass, R. T. (ed.). *The TSQL2 Temporal Query Language.* Kluwer, 1995. — [DBLP](https://dblp.org/db/books/collections/snodgrass95.html)
- **[Survey]** Kulkarni, K., Michels, J.-E. *Temporal Features in SQL:2011.* SIGMOD Record, 2012. — [DOI](https://doi.org/10.1145/2380776.2380786)

## 10. Worked Example

Take two temporal relations under valid-time intervals $[t_s,t_e)$:

`Emp` (who works) — Ann: $[1,6)$.
`Dept` (which dept is active) — Sales: $[3,9)$.

We want the **sequenced join** "who works in an active dept, at each instant." A naive nontemporal join ignoring time would wrongly pair them over all time. The alignment rewrite **splits at every relevant endpoint** $\{1,3,6,9\}$ touching each operand:

- `Emp` Ann $[1,6)$ → fragments $[1,3),[3,6)$.
- `Dept` Sales $[3,9)$ → fragments $[3,6),[6,9)$.

Join applies on aligned, **equal-period** fragments only; the single surviving overlap is $[3,6)$:

$$\text{(Ann, Sales)} \;\text{on}\; [3,6).$$

Check snapshot-reducibility: at $\tau=2$ the result is empty (Dept not yet active); at $\tau=4$ it is $\{(Ann,Sales)\}$; at $\tau=7$ empty (Ann gone) — exactly the nontemporal join of each timeslice. No adjacent equal-value fragments remain, so coalescing leaves $[3,6)$ unchanged. Endpoint count $=4$, so the split blow-up is $O(n+m)$ as the upper bound predicts.

---
*Part of the [DBMS Research catalog](../../README.md).*
