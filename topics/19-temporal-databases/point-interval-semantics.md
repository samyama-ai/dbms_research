# Point-vs-Interval Semantics Reconciliation

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/point-interval-semantics` · **Status:** open

## 1. Problem Statement
Temporal data can be modeled two ways. In the **point-based** (snapshot) model a temporal
relation is a function $t \mapsto r_t$ from time points to ordinary relations; a tuple's
timestamp is the *set of instants* at which the fact holds. In the **interval-based**
(period) model a tuple carries an explicit period $[s, e)$ and the *representation itself*
is data. The two coincide on which facts hold *when*, but disagree on operations sensitive
to representation: duplicate elimination, aggregation, `COUNT`, and any operator that can
"see" interval boundaries. The problem: define a single algebra (or a translation discipline)
under which user queries written against one model yield the *snapshot-equivalent* result of
the other, with no boundary, coalescing, or duplicate anomalies — and characterize exactly
which operators force a choice. Variants: (a) **decision** — given a query, is it
*representation-independent* (snapshot-reducible)? (b) **synthesis** — rewrite an
interval query into a provably point-faithful one. (c) **counting** — count distinct
representations of a given snapshot history.

## 2. Mathematical Foundations
Let $T$ be a linear time domain (discrete $\mathbb{Z}$ or dense $\mathbb{Q}$). A point-based
temporal relation is $R: T \to 2^{\text{Tuples}}$. **Snapshot equivalence**: $R_1 \equiv_s R_2$
iff $R_1(t) = R_2(t)$ for all $t$. An interval relation $I$ *represents* $R$ iff
$R(t) = \{ \bar{a} \mid (\bar{a}, [s,e)) \in I,\ s \le t < e \}$. The canonical normal form is
the **coalesced** form (value-equivalent overlapping/adjacent periods merged), unique per
snapshot history.

A temporal operator $\mathit{op}$ is **snapshot-reducible** (Snodgrass; Böhlen–Jensen–Snodgrass)
iff $\mathit{op}^T(I)(t) = \mathit{op}(I(t))$ pointwise — i.e. the diagram
$\mathit{op}^T$ then snapshot $=$ snapshot then $\mathit{op}$ commutes. Selection/projection
are reducible; duplicate-eliminating projection and aggregation are *not* without coalescing.
On dense time, point semantics needs intervals anyway (a snapshot history with finitely many
"change points" is finitely representable iff piecewise-constant), linking the question to
**$o$-minimality** and **constraint databases** (Kanellakis–Kuper–Revesz): point relations
expressible in $\mathrm{FO}(<, +)$ over $\mathbb{Q}$ have semi-linear (interval-union)
representations, giving a representation theorem $R \cong \text{finite interval set}$.

## 3. State of the Art (SOTA)
The cleanest theory line is **sequenced semantics** (Snodgrass, TSQL2, 1995) plus the
**Böhlen–Jensen–Snodgrass** reducibility framework (TODS 1996, "Evaluating and Enhancing the
Completeness of TSQL2"). Toman's **point-based temporal logic / SQL-TP** (1996–2003) is the
most thoroughgoing point-based system, with a compiler that maps point queries to interval
evaluation and back, proving the two views agree on a well-defined fragment. Dignös–Böhlen–Gamper's
**temporal alignment & normalization primitives** (SIGMOD 2012) give a systems-grade bridge:
arbitrary non-temporal operators are lifted by *splitting* intervals on relevant endpoints,
recovering snapshot reducibility for the full relational algebra. SQL:2011 period predicates
sit on the interval side and deliberately punt on coalescing.

## 4. Upper Bound
For the *reducibility check* on conjunctive/relational-algebra queries, Toman's translation
runs in time polynomial in query size; per-tuple evaluation via alignment (Dignös et al.) adds
only a factor proportional to the number of distinct endpoints touched, giving
$O(n \log n)$ alignment per binary operator in the **RAM model** (sort-merge on endpoints).
Coalescing-to-normal-form is $O(n \log n)$ per value group. These are upper bounds on
*producing point-faithful results*, not on deciding representation-independence in general.

## 5. Lower Bound
Deciding snapshot-reducibility / representation-independence for full $\mathrm{FO}$ temporal
queries is **undecidable**, inherited from undecidability of $\mathrm{FO}$ equivalence over
ordered infinite domains and from constraint-database results (KKR). For dense time, deciding
whether two point queries are snapshot-equivalent reduces from $\mathrm{FO}(<)$ satisfiability.
Even restricting to relational algebra, the boundary-anomaly elimination forces coalescing,
whose *streaming* one-pass detection of value-equivalence has an $\Omega(n)$ space lower bound
(distinctness, communication-complexity model). No NP/SETH separation is known to sharpen the
PTIME upper bounds; the hardness is expressiveness/decidability, not fine-grained.

## 6. The Gap
The *operational* gap is essentially closed for relational algebra (alignment gives faithful
results in $O(n\log n)$). The *open* gap is the **decision/characterization** side: there is no
syntactic, decidable characterization of which temporal queries are representation-independent
beyond conjunctive fragments, no agreed canonical algebra that is simultaneously point-faithful,
closed, and free of coalescing artifacts under aggregation, and no consensus on dense-time vs
discrete-time semantics in the SQL standard. Closing it needs either a decidable syntactic class
capturing "all and only" reducible queries, or a proof that the natural classes are undecidable.

## 7. Current Research (as of June 2026)
Active work continues in the Böhlen–Gamper (Free University of Bozen-Bolzano) line on temporal
algebra normalization and its push-down into engines; Toman/Weddell (Waterloo) on point-based
semantics and description-logic-backed temporal constraints. There is renewed interest in
reconciling SQL:2011 period semantics with point semantics in mainstream engines (MariaDB,
Db2, recently DuckDB/temporal extensions) *(frontier — verify)*. Constraint-database
representation theorems are being revisited for ML feature-store "as-of" joins, where
point-faithfulness silently matters *(frontier — verify)*.

## 8. Future Work
- A decidable syntactic characterization of representation-independent temporal queries above
  the conjunctive level.
- A standard-blessed closed algebra unifying point and interval semantics with coalescing-free
  aggregation.
- Dense-vs-discrete reconciliation, including `NOW`-relative and indeterminate timestamps.
- Cost-aware compilers that choose point vs interval physical representation per subquery.

## 9. Key References
- **[Foundational]** R. Snodgrass et al. *The TSQL2 Temporal Query Language.* Kluwer, 1995. — [DBLP](https://dblp.org/db/books/collections/snodgrass95.html)
- **[Foundational]** M. Böhlen, C. Jensen, R. Snodgrass. *Evaluating and Enhancing the
  Completeness of TSQL2.* (and related TODS work on snapshot reducibility), 1996. — [DBLP search](https://dblp.org/search?q=Evaluating%20and%20Enhancing%20the%20Completeness%20of%20TSQL2)
- **[Foundational]** D. Toman. *A Point-Based Temporal Extension of SQL.* DOOD, 1997. — [DOI](https://doi.org/10.1007/3-540-63792-3_11)
- **[SOTA]** A. Dignös, M. Böhlen, J. Gamper. *Temporal Alignment.* SIGMOD, 2012. — [DOI](https://doi.org/10.1145/2213836.2213886)
- **[Foundational]** P. Kanellakis, G. Kuper, P. Revesz. *Constraint Query Languages.* JCSS, 1995. — [DOI](https://doi.org/10.1006/jcss.1995.1051)
- **[Survey]** C. Jensen, R. Snodgrass. *Temporal Database Entries* in the Encyclopedia of
  Database Systems, Springer, 2009/2018. — [DOI](https://doi.org/10.1007/978-0-387-39940-9)

## 10. Worked Example

Let `Emp(name, dept)` hold over discrete time. Interval relation $I$:

| name | dept | $[s,e)$ |
|------|------|---------|
| Ann  | Sales | $[1,4)$ |
| Ann  | Sales | $[4,7)$ |
| Bob  | Sales | $[2,5)$ |

**Snapshot equivalence vs representation.** Ann's two adjacent tuples coalesce to one period $[1,7)$ — same *snapshot history* ($\forall t,\ I(t)$ unchanged), different representation.

Now run a temporal `SELECT DISTINCT dept`. Pointwise (snapshot-reducible target): at each $t$ the set of departments is $\{$Sales$\}$, so the faithful answer is the single period $[1,7)$ with `Sales`. But evaluated *per stored tuple* the engine emits three `Sales` rows over $[1,4),[4,7),[2,5)$ — duplicates the user shouldn't see. Duplicate-eliminating projection is **not** snapshot-reducible without coalescing.

**Alignment fix.** Split all intervals on the distinct endpoints $\{1,2,4,5,7\}$, dedupe per resulting chunk, then re-coalesce: $[1,2),[2,4),[4,5),[5,7)$ all carry `Sales`, merging back to $[1,7)$ — the point-faithful result. Cost: a sort-merge on $\le 5$ endpoints, i.e. $O(n\log n)$.

---
*Part of the [DBMS Research catalog](../../README.md).*
