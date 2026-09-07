---
id: 25-query-languages-expressiveness/nested-relational-calculi
title: "Nested-Relational and Higher-Order Query Calculi"
topic: 25-query-languages-expressiveness
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Nested-Relational and Higher-Order Query Calculi

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/nested-relational-calculi` · **Status:** partially-solved

## 1. Problem Statement

Real query languages (SQL with arrays/JSON, XQuery, LINQ, Spark/DataFrame APIs, GraphQL) manipulate **complex objects** — nested sets, bags, tuples, and functions — not just flat relations. The problem is to **characterize the expressive power and conservativity** of nested-relational and *comprehension-based* (monad/collection) calculi:

- **Expressive power:** what query class does the nested-relational calculus (NRC) capture, with and without features such as powerset, aggregation/summation, recursion, and higher-order functions?
- **Conservativity:** does the ability to build deep intermediate nesting let you express more *flat-to-flat* queries than a language restricted to shallow data? (The "conservative extension" question over nesting depth.)
- **Higher-order:** what does adding $\lambda$-abstraction / function-valued attributes (higher-order NRC, simply-typed query calculi) add, and when can it be *normalized away*?

Status **partially-solved**: the set-based NRC story (Wong's conservativity, normalization) is essentially complete; bag/aggregate, recursive, and higher-order extensions are characterized only in fragments.

## 2. Mathematical Foundations

The **NRC** is a typed $\lambda$-calculus over collection types built from a **monad** (the set or bag monad): types $\;t ::= b \mid t \times t \mid \{t\}$, with operations $\eta(x)=\{x\}$ (singleton), $\biguplus$ (flatten/union), and the **comprehension** $\{\,e \mid x \in e'\,\}$ (the monadic *bind*). Booleans/equality and emptiness test give selection.

**Wong's normalization / conservativity theorem (1996):** every NRC expression is equivalent to one in normal form whose intermediate types have **nesting depth bounded by the max of input and output depth**. Consequence: NRC (no powerset) is a **conservative extension** over nesting depth — flat-to-flat NRC = flat relational algebra = **FO**. Nesting buys expressiveness *only* when outputs are themselves nested; it never increases flat-query power.

Adding **powerset** ($\mathcal{P}: \{t\} \to \{\{t\}\}$) breaks conservativity and yields a strictly larger, elementary class (expresses transitive closure, parity). Adding a **summation/aggregate** operator $\Sigma$ over a bag monad gives $\mathrm{NRC}(\mathrm{aggr})$, whose flat fragment corresponds to **$\mathrm{FO}+$counting / aggregate logic** (Libkin–Wong) and captures relational algebra with grouping/aggregation. Adding bounded fixpoint gives nested Datalog-like power.

For **higher-order** query calculi (e.g. Cooper's *language-integrated query* with first-class functions), the key result is **normalization to first-order NRC**: under suitable typing, higher-order features are *eliminable* — they are syntactic sugar that does not change the captured query class, which is essential for translating LINQ/Links queries to SQL.

## 3. State of the Art (SOTA)

- **Set NRC:** Buneman–Naqvi–Tannen–Wong (TCS 1995) comprehension calculus; **Wong (JCSS 1996)** normalization & conservativity — the canonical SOTA.
- **Aggregation:** Libkin–Wong (*"Query languages for bags and aggregate functions,"* JCSS 1997) characterize NRC+aggregates ≈ flat $\mathrm{FO}$+counting fragment.
- **Higher-order / language-integrated:** Cooper (*"The Script-Writer's Dream,"* DBPL 2009) and the **Links** project (Cheney, Lindley, Wadler) — *query normalization* guaranteeing higher-order queries compile to single SQL statements; Suzuki–Kiselyov–Kameyama "Finally, safely-extensible..." for shredding.
- **Shredding** (Cheney, Lindley, Wadler, ICFP 2014): translate nested results to a bounded number of flat SQL queries — the systems-relevant constructive form of conservativity.

## 4. Upper Bound

- Set NRC without powerset: flat-data complexity **$\mathrm{AC}^0$ / LOGSPACE** (= FO), by Wong normalization; combined complexity matches RA (PSPACE-complete in expression size).
- NRC + aggregation: flat fragment in **uniform $\mathrm{TC}^0$** (FO+counting upper bound).
- NRC + powerset: **elementary**, with intermediate sizes that can be non-elementary in nesting depth (a tight worst case).
- Higher-order NRC (normalizing fragment): same bounds as first-order NRC, since normalization eliminates the higher-order layer; **shredding** guarantees $O(\text{output nesting depth})$ flat SQL queries.

## 5. Lower Bound

- **Flat NRC = FO inherits all FO inexpressibility lower bounds:** no transitive closure, no parity, no counting — unconditional, via locality / Ehrenfeucht–Fraïssé.
- **Powerset is genuinely needed** for the larger class: a strict expressiveness separation (NRC vs. NRC+powerset) is provable, again unconditionally.
- Aggregate NRC still **cannot** express recursion/TC (counting does not give recursion) — separation via order-invariance / locality of FO+C.
- Worst-case **non-elementary blowup** for powerset NRC is a lower bound on evaluation cost.

## 6. The Gap

The **set-based, non-recursive** picture is closed (tight conservativity + normalization). The open parts are: (1) a fully general conservativity/normalization theory for **bag + aggregation + grouping + recursion combined** (each is understood in isolation, not jointly); (2) characterizing **higher-order query calculi** whose normalization is *not* known to terminate (e.g. with general recursion or effects), where it is open whether higher-order power is always eliminable; and (3) conservativity for **semistructured/JSON** and **graph** data models with heterogeneous nesting. Closing these requires new normalization or game-based separation arguments.

## 7. Current Research (as of June 2026)

- **Language-integrated query** at scale: Links / DSH / **Cheney–Lindley–Wadler** normalization extended to grouping, aggregation, and provenance; *(frontier — verify)* effect-typed query calculi that normalize to SQL with window functions.
- **JSON/semistructured expressiveness** (SQL/JSON, JSONiq) and nested-data conservativity for lakehouse/DataFrame engines. *(frontier — verify)*
- **Higher-order Datalog** and nested fixpoint calculi (Charalambidis, Rondogiannis; the FLIX/Datafun line by Arntzenius–Krishnaswami) characterizing power of monotone higher-order recursion.

## 8. Future Work

- A unified conservativity/normalization theorem for NRC with bags, aggregation, *and* recursion.
- Decidable normalization for higher-order query calculi with controlled recursion/effects.
- Cost-aware shredding and nested-result optimization for distributed engines.

## 9. Key References

- **[Foundational]** Buneman, Naqvi, Tannen, Wong. *Principles of Programming with Complex Objects and Collection Types.* TCS, 1995. — [DOI](https://doi.org/10.1016/0304-3975(95)00024-Q)
- **[Foundational]** Wong. *Normal Forms and Conservative Extension Properties for Query Languages over Collection Types.* JCSS, 1996. — [DOI](https://doi.org/10.1006/jcss.1996.0037)
- **[Foundational]** Libkin, Wong. *Query Languages for Bags and Aggregate Functions.* JCSS, 1997. — [DOI](https://doi.org/10.1006/jcss.1997.1523)
- **[SOTA]** Cheney, Lindley, Wadler. *Query Shredding: Efficient Relational Evaluation of Queries over Nested Multisets.* SIGMOD/ICFP, 2014. — [arXiv](https://arxiv.org/abs/1404.7078) — [DOI](https://doi.org/10.1145/2588555.2612186)
- **[SOTA]** Cooper. *The Script-Writer's Dream: How to Write Great SQL in Your Own Language (Links query normalization).* DBPL, 2009. — [DOI](https://doi.org/10.1007/978-3-642-03793-1_3)
- **[Survey]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (complex-object models). — [book site](http://webdam.inria.fr/Alice/)

## 10. Worked Example

**Conservativity in action.** Flat input: `Emp = {(Ann,d1),(Bob,d1),(Cy,d2)}` and `Dept = {d1,d2}`. A *nested* NRC query groups employees by department:
$$Q \;=\; \{\,(d,\ \{\,n \mid (n,d')\in \text{Emp},\ d'=d\,\})\ \mid\ d\in\text{Dept}\,\}$$
yielding the **nested** result $\{(d1,\{Ann,Bob\}),\ (d2,\{Cy\})\}$ — output type $\{ \text{dept}\times\{\text{name}\}\}$ has nesting depth 2.

Now a *flat-to-flat* query: "names in some department of size $\ge 2$." One could write it by building the nested grouping above and then unnesting. **Wong's normalization** rewrites any such expression so intermediate types never exceed $\max(\text{input depth},\text{output depth}) = \max(1,1)=1$: the powerset-free detour through depth-2 collections is *eliminable*. The normalized query is the flat relational expression
$$\{\,n \mid (n,d)\in\text{Emp},\ (n',d)\in\text{Emp},\ n\ne n'\,\} = \{Ann,Bob\},$$
pure FO. So nesting bought us nothing for this flat answer — exactly the conservative-extension theorem.

**Where it breaks:** add powerset $\mathcal P$. Then $\{\,S \mid S\in\mathcal P(\text{Dept})\,\}$ has $2^{|\text{Dept}|}$ elements; iterating it lets NRC+powerset express transitive closure and parity, escaping FO — and intermediate sizes blow up non-elementarily in nesting depth, the matching lower bound.

---
*Part of the [DBMS Research catalog](../../README.md).*
