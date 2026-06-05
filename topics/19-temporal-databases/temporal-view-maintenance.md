# Incremental Maintenance of Temporal Views

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-view-maintenance` · **Status:** partially-solved

## 1. Problem Statement

A materialized temporal view $V = q(R_1,\dots,R_k)$ is defined by a temporal query (selection with period predicates, temporal join, temporal aggregation, coalescing) over **bitemporal** base tables carrying both valid-time and transaction-time periods. When the bases change — a tuple is inserted, logically deleted (its valid/transaction period closed), or back-dated/corrected — the goal is to compute $\Delta V$ and apply it **incrementally**, i.e. with cost proportional to the change rather than recomputing $q$ from scratch.

The temporal twist over classical incremental view maintenance (IVM): (i) a single base change is an interval event that can split, merge, or coalesce existing view periods; (ii) **corrections in transaction time** create new transaction-time versions, so $\Delta V$ must itself be appended bitemporally, never overwritten; (iii) temporal aggregates and coalesced views are *not* deltas-distributive in the ordinary sense, because endpoint geometry changes. Variants: **self-maintainable** (compute $\Delta V$ from $\Delta R$ and $V$ alone, no base access), **decision** (is $V$ self-maintainable for this $q$?), **optimization** (minimize work/I/O per change), **streaming/continuous** (bounded-state maintenance as time advances and `NOW` moves).

## 2. Mathematical Foundations

Classical IVM rests on the **delta rules**: for a query $q$, $q(R\cup\Delta R) = q(R) \uplus \Delta q$, with $\Delta q$ computed by differentiating $q$ operator-by-operator (Gupta–Mumick–Subrahmanian, *SIGMOD 1993*; bag semantics via Z-relations and the **DBToaster** higher-order delta calculus of Koch et al., 2014). For temporal queries, the algebra is extended with period-preserving operators; the key object is the **snapshot-reducible** form: a temporal operator $\theta^T$ is snapshot-reducible iff $\tau_t(\theta^T(R)) = \theta(\tau_t(R))$ for every snapshot time $t$, where $\tau_t$ is the timeslice. Snapshot reducibility lets one *lift* a classical incremental rule to its temporal counterpart provided the lift commutes with timeslicing.

Temporal join and selection are snapshot-reducible, so they admit lifted delta rules; **coalescing** and **temporal aggregation** are not pointwise — they depend on interval adjacency, formalized via the *temporal alignment / scaling* primitives (Dignös–Böhlen–Gamper) that split base intervals on a set of *change points* $C \subseteq \mathbb{T}$ so that downstream operators become snapshot-reducible on the split relation. Incremental cost is then governed by $|\Delta C|$, the change-point churn induced by one update. Bitemporal correctness uses the *append-only transaction-time* invariant: $V$ at transaction time $t'$ equals $q$ evaluated against the base state as of $t'$, so $\Delta V$ is monotone in transaction time even when valid-time facts are retracted.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Lifted/snapshot-reducible delta rules for temporal selection–projection–join and "since" views are well understood; the alignment-based decomposition (Dignös et al., *SIGMOD 2012*; *VLDB J. 2014*) gives a systematic route to incrementalize temporal aggregation and coalescing by reducing to interval-split classical IVM.
- **Systems-SOTA:** Higher-order IVM engines — **DBToaster** (Koch et al., *VLDB J. 2014*) and the **Differential Dataflow / Materialize** lineage (McSherry–Murray et al.) — provide general incremental maintenance with timestamped, partially-ordered progress, and are the practical substrate on which bitemporal views are built. **Snowflake/Databricks/Materialize** materialized views handle append-heavy temporal data but offer limited support for back-dated corrections. PostgreSQL has no native incremental temporal MV; pg_ivm and extensions cover the non-temporal core.

## 4. Upper Bound

For snapshot-reducible SPJ temporal views, $\Delta V$ is computable in time $O(|\Delta R|\cdot \text{(non-temporal join delta cost)} + |\Delta C|\log|\Delta C|)$ — i.e. the classical IVM upper bound plus a sort over the change points each update touches. With DBToaster-style recursive delta materialization, point queries / single-tuple updates over acyclic temporal joins are maintainable in **amortized $O(\text{polylog})$ to $O(1)$ per update** for the maintained aggregate, at the cost of auxiliary materialized sub-views. Coalesced views are maintainable in time proportional to the number of intervals adjacent to the changed endpoint, $O(\log n + a)$ with an interval index over $V$.

## 5. Lower Bound

Incremental maintenance is provably hard for the hardest views: maintaining the result of a Boolean **conjunctive query under single-tuple updates** cannot be done in $O(n^{1/2-\epsilon})$ time per update for some queries (the triangle/3-path family) unless the **Online Matrix–Vector (OMv) conjecture** fails (Berkholz–Keppmann–Schweikardt, *PODS 2017*); temporal SPJ inherits this since it generalizes the static query at each snapshot. Self-maintainability is *not always achievable*: there exist temporal views (e.g. with temporal aggregation over retracted valid-time) that require base access on deletion (info-theoretic: the view does not retain enough state), matching the classical Gupta–Mumick characterization. Thus a fully incremental, self-maintainable solution for arbitrary bitemporal aggregate views is impossible.

## 6. The Gap

For **SPJ and coalesced bitemporal views** the gap is essentially closed: lifted delta rules match the OMv-conditional lower bound. The genuinely **open** region is (a) **temporal aggregation with retraction** (back-dated corrections that shrink groups), where current methods often degrade toward recomputation and the optimal per-update bound is unknown; and (b) the interaction with a **moving `NOW`**, where the view changes even with *no* base update (time advances), and bounded-state continuous maintenance is not fully characterized. Closing it needs either a stronger self-maintainability characterization for temporal aggregates or matching fine-grained lower bounds.

## 7. Current Research (as of June 2026)

- Differential-dataflow / **Materialize** and **Feldera (DBSP)** pushing recursive incremental computation with explicit time semantics; DBSP's circuit calculus (Budiu et al.) is being applied to interval/temporal operators *(frontier — verify)*.
- Alignment-based temporal IVM integrated into research forks of PostgreSQL and Spark (Dignös–Böhlen–Gamper group, U. Bozen-Bolzano) *(frontier — verify)*.
- Fine-grained complexity of *temporal* IVM (extending Berkholz–Keppmann–Schweikardt to interval predicates) as an active PODS/ICDT thread *(frontier — verify)*.

## 8. Future Work

- Tight per-update bounds for temporal aggregation under retraction, with matching OMv/3SUM-conditional lower bounds.
- Bounded-state continuous maintenance of now-relative views with provable freshness guarantees.
- A cost-based optimizer that chooses between recomputation, lifted-delta IVM, and DBSP circuits per temporal sub-view.

## 9. Key References

- **[Foundational]** A. Gupta, I. S. Mumick, V. S. Subrahmanian. *Maintaining Views Incrementally.* ACM SIGMOD, 1993.
- **[SOTA]** C. Koch, Y. Ahmad, O. Kennedy, M. Nikolic, A. Nötzli, D. Lupei, A. Shaikhha. *DBToaster: Higher-Order Delta Processing for Dynamic, Frequently Fresh Views.* VLDB Journal, 23(2), 2014.
- **[SOTA]** A. Dignös, M. H. Böhlen, J. Gamper. *Temporal Alignment* / *Overlap Interval Partition Join.* ACM SIGMOD, 2012 / 2014.
- **[SOTA]** C. Berkholz, J. Keppmann (Gerhardt), N. Schweikardt. *Answering Conjunctive Queries under Updates.* ACM PODS, 2017.
- **[SOTA]** F. McSherry, D. Murray, R. Isaacs, M. Isard. *Differential Dataflow.* CIDR, 2013.
- **[SOTA]** M. Budiu et al. *DBSP: Automatic Incremental View Maintenance for Rich Query Languages.* VLDB, 2023.

---
*Part of the [DBMS Research catalog](../../README.md).*
