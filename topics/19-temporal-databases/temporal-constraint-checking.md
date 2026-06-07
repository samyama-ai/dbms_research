---
id: 19-temporal-databases/temporal-constraint-checking
title: "Temporal Integrity Constraint Checking"
topic: 19-temporal-databases
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Temporal Integrity Constraint Checking

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-constraint-checking` · **Status:** open

## 1. Problem Statement
SQL:2011 introduced **application-time period tables** with `PRIMARY KEY ... WITHOUT OVERLAPS`
and period-aware foreign keys. Enforcing these *sequenced* constraints is harder than ordinary
key checking. A **sequenced primary key** on $(K, \text{period})$ requires that no two tuples
with the same $K$ have overlapping periods (the key holds at *every* instant). A **sequenced
foreign key** requires that for each child tuple, the *entire* child period is covered by the
**union** of parent periods sharing the referenced key — coverage by possibly many parent rows.
The problem: enforce these efficiently and incrementally under inserts/updates/deletes, ideally
without full re-evaluation, and characterize the cost relative to non-temporal constraints.
Variants: (a) **decision** — does relation $r$ satisfy the sequenced constraint? (b)
**incremental** — given a $\Delta$, is the new state still valid, touching minimal data?
(c) **repair/counting** — minimal modification to restore consistency; count violating instants.

## 2. Mathematical Foundations
Let tuples carry periods $[s,e)$. **Sequenced PK** on $K$: for all $t$,
$\pi_K(\sigma_{\text{valid at } t}(r))$ is a key — equivalently, intervals within each $K$-group
are pairwise **non-overlapping**, an interval-disjointness condition checkable by sweep.
**Sequenced FK** from child $C$ to parent $P$ on key $K$: for every $c \in C$,
$[c.s, c.e) \subseteq \bigcup \{ [p.s, p.e) : p \in P,\, p.K = c.K \}$ — an **interval-cover /
containment-in-union** condition.

Formally these are first-order constraints over the period-endpoint structure
$(\,T; <, +, \text{relations}\,)$; sequenced semantics means the constraint must hold in every
snapshot $r(t)$. The cover check per child is the complement-emptiness test: $c$'s period minus
the parent union must be empty, computable by endpoint sweep in $O(m \log m)$ for $m$ parent
rows in the group. Incremental maintenance connects to **first-order incremental view
maintenance (DReD / DBToaster)** and to the theory of **constraint databases** (Kanellakis–
Kuper–Revesz) since periods are linear constraints over $\mathbb{Q}$. Coalescing interacts:
adjacency vs overlap must be defined consistently with the time domain (discrete vs dense).

## 3. State of the Art (SOTA)
**Theory SOTA:** the semantics are pinned by the **temporal-constraint** literature — Snodgrass's
sequenced constraints, and Toman/Weddell's use of description logics / first-order temporal
logic to specify temporal keys and inclusion dependencies. Böhlen–Gamper alignment recasts
constraint checking as aligned non-temporal checks. **Systems SOTA:** SQL:2011 implementations —
**IBM Db2** (business-time `WITHOUT OVERLAPS` and period FKs), **MariaDB** application-time
periods, **Teradata**, **Oracle** (valid-time via Temporal Validity + Workspace Manager),
**PostgreSQL** (range types + exclusion constraints `EXCLUDE USING gist (k WITH =, period WITH &&)`
give sequenced PK directly; periods/`WITHOUT OVERLAPS` arrived more recently) *(frontier —
verify)*. Exclusion constraints over GiST are the most practical disjointness enforcement today.

## 4. Upper Bound
Sequenced **PK** enforcement on insert of one tuple is a stabbing/overlap query against the
$K$-group: $O(\log n)$ with an interval index (GiST, interval tree) plus $O(\log n)$ update, in
the **RAM/external-memory model**; bulk validation is $O(n \log n)$ by per-group sweep. Sequenced
**FK** on an inserted child is one **containment-in-union** test, $O(m \log m)$ over the matching
parent group, or $O(\log m + \text{output})$ amortized with a maintained coverage structure;
parent deletes need re-checking children whose coverage may break, bounded by overlap count.
These are the best-known and are near-optimal up to the index/sweep factors.

## 5. Lower Bound
Single-insert PK overlap check inherits the **interval stabbing** lower bound: $\Omega(\log n)$
per query in the comparison/pointer-machine and a cell-probe $\Omega(\log n / \log\log n)$ for
dynamic predecessor-style structures (Pătraşcu–Thorup-type bounds). Full validation is
$\Omega(n \log n)$ in the comparison model (element-distinctness over endpoints). FK coverage
maintenance under arbitrary parent deletes is at least as hard as **dynamic interval union /
connectivity**, with conditional polynomial lower bounds (OMv-conjecture territory) for fully
dynamic worst-case bounds. No NP-hardness arises for checking; the *minimal-repair* (consistent
update) variant becomes hard — related to minimum interval modification, NP-hard in general.

## 6. The Gap
Checking a *single* constraint is essentially solved (index + sweep, near tight). The genuinely
**open** parts: (i) *incremental* maintenance of sequenced FKs under bulk, interleaved
parent/child changes with provable sub-linear bounds — current engines often fall back to
re-evaluation; (ii) *interaction* of multiple sequenced constraints + coalescing + `NOW`-relative
periods, where no clean complexity characterization exists; (iii) the standard underspecifies
dense vs discrete adjacency, so "correct" enforcement is engine-dependent. Closing it needs a
unified incremental-maintenance theory for period constraints with matching dynamic lower bounds.

## 7. Current Research (as of June 2026)
PostgreSQL's incremental rollout of SQL:2011 `WITHOUT OVERLAPS` / `PERIOD` and period FKs is an
active engineering frontier with ongoing community work *(frontier — verify)*. Academic work
(Bolzano; Waterloo) continues on temporal constraint specification via temporal logic / DLs and
on alignment-based enforcement. There is interest in **incremental temporal constraint
maintenance** atop IVM engines (DBToaster-style) and in **consistency under bitemporal updates**
where valid-time FKs must hold as transaction time advances *(frontier — verify)*. Data-lake
table formats are beginning to add period-key validation in catalog layers *(frontier — verify)*.

## 8. Future Work
- Sub-linear incremental enforcement of sequenced FKs under fully dynamic updates, with
  matching dynamic lower bounds.
- A unified complexity theory for combined sequenced PK/FK + coalescing + `NOW`/indeterminate time.
- Standardized dense/discrete adjacency semantics for portable enforcement.
- Efficient minimal-repair algorithms (or hardness proofs) for inconsistent temporal states.

## 9. Key References
- **[Foundational]** R. Snodgrass. *Developing Time-Oriented Database Applications in SQL.*
  Morgan Kaufmann, 2000. — [DBLP search](https://dblp.org/search?q=Developing+Time-Oriented+Database+Applications+in+SQL+Snodgrass)
- **[Foundational]** ISO/IEC 9075:2011 (SQL:2011) — application-time period tables,
  `WITHOUT OVERLAPS`, period predicates. ISO, 2011.
- **[SOTA]** K. Kulkarni, J.-E. Michels. *Temporal Features in SQL:2011.* SIGMOD Record, 2012. — [ACM](https://dl.acm.org/doi/10.1145/2380776.2380786)
- **[Foundational]** P. Kanellakis, G. Kuper, P. Revesz. *Constraint Query Languages.* JCSS, 1995. — [DOI](https://doi.org/10.1006/jcss.1995.1051)
- **[SOTA]** A. Dignös, M. Böhlen, J. Gamper, C. Jensen. *Extending the Kernel of a Relational
  DBMS with Comprehensive Support for Sequenced Temporal Queries.* ACM TODS, 2016. — [DOI](https://doi.org/10.1145/2967608)

## 10. Worked Example

**Sequenced PK** on `Employee(emp_id, period)` with `emp_id WITHOUT OVERLAPS`. Existing rows for `emp_id = 7`:

| emp_id | period |
|--------|--------------|
| 7 | $[2020, 2022)$ |
| 7 | $[2023, 2025)$ |

Insert $7, [2021, 2024)$. The stabbing query against the `emp_id = 7` group finds $[2021,2024)$ overlaps both $[2020,2022)$ (share $[2021,2022)$) and $[2023,2025)$ (share $[2023,2024)$) — **rejected**. Insert $7, [2022, 2023)$ instead: it overlaps neither (intervals are half-open, so $[2020,2022)$ and $[2022,2023)$ only *meet*) — **accepted**. With a GiST/interval index this is one $O(\log n)$ overlap probe.

**Sequenced FK**: child `Assignment(emp_id=7, period=[2020,2025))` must be covered by the *union* of parent periods. The two original rows give union $[2020,2022) \cup [2023,2025)$, leaving the gap $[2022,2023)$ **uncovered** — the containment-in-union test ($\text{child} \setminus \text{union} = [2022,2023) \neq \emptyset$) fails. The FK is violated precisely on that instant-set, illustrating why coverage, not single-row matching, is required.

---
*Part of the [DBMS Research catalog](../../README.md).*
