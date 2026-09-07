---
id: 21-graph-databases/gql-expressiveness
title: "Expressiveness and gaps in GQL/SQL-PGQ"
topic: 21-graph-databases
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Expressiveness and gaps in GQL/SQL-PGQ

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/gql-expressiveness` · **Status:** open

## 1. Problem Statement
Pin down the **exact expressive power** of the new ISO standards **GQL** (ISO/IEC 39075:2024) and **SQL/PGQ** (the property-graph extension of SQL:2023): which graph properties and transformations can their core query languages express, which provably cannot, and what primitives are *missing* relative to natural workloads. Concretely:
- Characterize the **pattern-matching core** (GPML — Graph Pattern Matching Language) against yardstick logics (FO, transitive closure, Datalog, fragments of fixpoint logic).
- Determine **closure** properties: is the language graph-to-graph composable (closed under composition), and is GQL's graph-construction fragment as expressive as needed for views?
- Identify **decidable static analysis** boundaries (containment, equivalence, satisfiability) for the standardized fragments.
This is a *language-expressiveness* problem, not an algorithmic one: separations are proved, not benchmarked.

## 2. Mathematical Foundations
Property graphs are finite structures with labeled nodes/edges and key–value records. GPML's navigational core corresponds to **unions of conjunctive regular path queries (UCRPQ)** extended with *trail/shortest* restrictors and *bounded repetition*. Yardsticks: **FO** (no recursion), **FO + transitive closure (FO+TC)**, **Datalog / monadic Datalog**, and **GXPath**-style navigational logics. RPQs sit between FO and FO+TC; UC2RPQ (two-way) adds inverse navigation. Expressive-power tools: **Ehrenfeucht–Fraïssé / pebble games**, **locality** (Gaifman, Hanf), and **0-1 laws** to prove inexpressibility (e.g., RPQ-free fragments cannot test connectivity or parity-length paths). Containment of UC2RPQs is **EXPSPACE-complete** (Calvanese–De Giacomo–Lenzerini–Vardi). The data-value dimension (joins on property values across a pattern) pushes toward **register automata** and theories with infinite alphabets, where decidability of static analysis becomes fragile.

## 3. State of the Art (SOTA)
- **Formal semantics:** Francis–Gheerdink–Libkin–Lindaaker–Marsault–Plantikow–Rydberg–Vandevoort–Vrgoč et al. give the reference operational semantics of GQL/SQL-PGQ pattern matching (SIGMOD/PODS 2023, 2024).
- **Expressiveness results:** characterizations of GPML's pattern core as (extended) UCRPQ; separations showing GQL cannot express general fixpoint/Datalog recursion (no arbitrary recursive views), and cannot count beyond what bounded repetition allows.
- **Static analysis:** containment/satisfiability results inherited from C(2)RPQ theory; targeted decidability for restricted GPML fragments.

## 4. Upper Bound
GPML pattern evaluation is in **NL data complexity** for the navigational (walk-semantics) core and in **PSPACE** combined complexity, matching UC2RPQ. The *full* language with grouping/aggregation/horizontal composition is expressible within an extension of relational algebra plus transitive closure, giving a clean upper yardstick: **GQL-core $\subseteq$ FO+TC (+ aggregation)**. Containment for the C2RPQ fragment is in EXPSPACE.

## 5. Lower Bound
Inexpressibility results form the "lower bounds": by locality/EF games, GQL's non-recursive fragments **cannot express connectivity, transitive closure of derived relations, or even cardinality of unbounded recursion** — properties expressible in Datalog. Thus GQL is strictly **less expressive than Datalog** and incomparable with full FO+LFP. Containment of UC2RPQs is **EXPSPACE-hard**, so optimization/static analysis cannot be cheap. With data-value joins (register-automata semantics), satisfiability becomes **undecidable** in general fragments.

## 6. The Gap
The pattern-matching core is fairly well understood, but the **exact expressive power of the *whole* standardized language** — pattern matching composed with `RETURN`/grouping, graph construction, optional/negation, and horizontal/vertical composition — is *open*. No published theorem says "GQL = logic $\mathcal L$." Missing primitives are debated: no general recursion (Datalog-style), limited path aggregation, no native shortest-path-tree construction, weak support for graph-to-graph views. Closing the gap requires a canonical logical characterization and a precise map of decidable static-analysis fragments.

## 7. Current Research (as of June 2026)
Groups at **Edinburgh (Libkin, Vrgoč), DCC Chile (Reutter, Vrgoč), TU Berlin / DBIS, Bayreuth (Martens), RelationalAI (Plantikow, Lindaaker)** and the LDBC formal-semantics working group are formalizing GQL conformance and expressiveness. *(frontier — verify)* 2025–2026 papers reportedly establish that **GQL-core $\equiv$ a guarded fixpoint-free fragment with bounded recursion** and isolate decidable containment for *linear* GPML; proposals for a standardized recursive extension ("GQL with fixpoints") are circulating. LDBC is producing an authoritative semantics document.

## 8. Future Work
- A definitive logical characterization of full GQL/SQL-PGQ (with composition + aggregation).
- A principled **recursive extension** (Datalog/fixpoint) for the next standard revision.
- Decidable static-analysis fragments to enable query optimization and access control.
- Expressiveness of **graph-construction** (view/closure) semantics.

## 9. Key References
- **[Foundational]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)
- **[Foundational]** Calvanese, De Giacomo, Lenzerini, Vardi. *Containment of Conjunctive Regular Path Queries with Inverse.* KR 2000. — [paper](https://www.inf.unibz.it/~calvanese/papers-html/KR-2000.html)
- **[SOTA]** Francis et al. *A Researcher's Digest of GQL.* ICDT 2023. — [DOI](https://doi.org/10.4230/LIPIcs.ICDT.2023.1)
- **[SOTA]** Deutsch et al. *Graph Pattern Matching in GQL and SQL/PGQ.* SIGMOD 2022. — [ACM](https://doi.org/10.1145/3514221.3526057)
- **[Survey]** Angles et al. *Foundations of Modern Query Languages for Graph Databases.* ACM Computing Surveys, 2017. — [arXiv](https://arxiv.org/abs/1610.06264)

## 10. Worked Example

Show concretely why GQL's non-recursive fragment **cannot express connectivity**, using an Ehrenfeucht–Fraïssé locality argument. Consider two undirected graphs with no node/edge labels:

- $G_1$: a single cycle on $2m$ vertices, $C_{2m}$.
- $G_2$: two disjoint cycles on $m$ vertices each, $C_m \sqcup C_m$.

"Is the graph connected?" must answer **yes** on $G_1$, **no** on $G_2$. But every vertex in both graphs has degree 2, and the radius-$r$ neighborhood of any vertex is identical — a simple path of $2r{+}1$ vertices — for both graphs once $m > 2r{+}1$. By Hanf locality, any **FO** sentence of quantifier rank $r$ (and hence any non-recursive GQL-core predicate, which evaluates in $\mathrm{FO}$ over the navigational closure with *fixed-length* patterns) cannot distinguish $G_1$ from $G_2$: a winning duplicator strategy maps each $r$-neighborhood to an isomorphic one.

A fixed GPML pattern like `()-[]->{1,k}()` only tests reachability up to a **bounded** length $k$; with $m>k$ neither graph yields a closing match the other lacks. Connectivity needs *unbounded* transitive closure — expressible in Datalog (`reach(x,y) :- edge(x,y); reach(x,y):-reach(x,z),edge(z,y)`) but not in the standardized non-recursive core. This is exactly the GQL $<$ Datalog separation of section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
