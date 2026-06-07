---
id: 01-relational-theory/fd-aware-query-minimization
title: "FD-Aware Query Minimization"
topic: 01-relational-theory
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# FD-Aware Query Minimization

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/fd-aware-query-minimization` · **Status:** partially-solved

## 1. Problem Statement

The classical Chandra–Merlin result minimizes a **conjunctive query** (CQ) by removing redundant atoms to obtain its unique (up to isomorphism) **core** under set semantics with *no* integrity constraints. In real schemas, **functional dependencies (FDs) and keys** hold on the base relations, enabling *more* aggressive minimization: atoms or joins that are redundant *given the FDs* can be dropped even though they are not redundant over arbitrary databases.

**Problem (optimization):** given a CQ $Q$ and a set $\Sigma$ of FDs/keys on its relations, compute a $\Sigma$-equivalent CQ $Q'$ with the fewest atoms (or fewest joins). **Decision variant:** is there a $\Sigma$-equivalent CQ with $\le k$ atoms? **Containment variant:** decide $Q\sqsubseteq_\Sigma Q'$ (containment under FDs), the primitive minimization relies on. Goals: a canonical minimal form, its complexity, and exploitation in optimizers (eliminating redundant joins / self-joins enabled by keys).

## 2. Mathematical Foundations

**CQ containment** $Q_1\sqsubseteq Q_2$ holds iff there is a **homomorphism** $Q_2\to Q_1$ (Chandra–Merlin). With FDs, the right tool is the **chase**: chase $Q$'s canonical (frozen) database with $\Sigma$ (FDs become **egds** that equate variables). Then

$$Q_1 \sqsubseteq_\Sigma Q_2 \iff \exists\, \text{homomorphism } Q_2 \to \mathrm{chase}_\Sigma(Q_1).$$

Minimization under $\Sigma$ = compute the **core of the chased canonical instance**. The chase with FDs/egds **terminates** (it only merges variables), so $\mathrm{chase}_\Sigma(Q)$ is well-defined and the $\Sigma$-minimal form is unique up to isomorphism. Keys are a special case: a key on $R$ lets one merge two $R$-atoms agreeing on the key, collapsing self-joins.

## 3. State of the Art (SOTA)

- **Theory SOTA**: CQ containment under FDs is **NP-complete** (Aho–Sagiv–Ullman 1979 established the egd-chase characterization). Minimization under FDs is computed by chase-then-core; the minimal form is canonical. Extensions cover **inclusion dependencies** (containment becomes undecidable in general, decidable for restricted/acyclic IDs), and **bag/multiset** semantics where FD-aware minimization differs.
- **Systems SOTA**: real optimizers exploit FDs/keys heavily but **heuristically**: key-based **join elimination** (foreign-key to primary-key joins removed when only key-side columns are projected), **redundant self-join removal**, and **functional-dependency propagation** for group-by/order-by simplification. SQL Server, Oracle, DB2, and Postgres-derived engines implement subsets; none compute the provably minimal core in general.

## 4. Upper Bound

Given $\Sigma$ as FDs, the **egd-chase terminates in PTIME** (data complexity in query size for variable-merging), and core extraction of the chased query is the dominant cost. Computing the minimal CQ under FDs is in **NP** (guess the small subquery, verify $\Sigma$-equivalence by chase + homomorphism). For **acyclic** queries or **bounded treewidth**, both containment and minimization drop to PTIME. Key-driven join elimination is detectable in time polynomial in the query.

## 5. Lower Bound

Plain CQ minimization (no constraints) is **NP-complete** (Chandra–Merlin); adding FDs keeps **$\Sigma$-containment NP-complete** (Aho–Sagiv–Ullman). Hence FD-aware minimization is **NP-hard** as soon as the query has a non-trivial homomorphism structure. With **inclusion dependencies** added, containment becomes **undecidable** (implication of CQs under IDs+FDs is undecidable), so optimal minimization in that richer setting has an absolute (recursion-theoretic) barrier.

## 6. The Gap

For FDs/keys alone the problem is **essentially closed in theory** (NP-complete; canonical minimal core via chase) but **only partially solved in practice**: optimizers apply narrow, pattern-based rules and miss minimizations requiring multi-step chase reasoning. The open gaps: (i) tractable islands beyond acyclicity; (ii) cost-aware minimization (fewest *expensive* joins, not fewest atoms); (iii) minimization under **FD + ID** mixtures where the line between decidable and undecidable is not exploited by engines.

## 7. Current Research (as of June 2026)

Groups: **Suciu / Khamis / Ngo (worst-case-optimal joins, where FDs/keys shrink the AGM/polymatroid bound)**, **Pichler / Sallinger (TU Wien)**, **ten Cate / Kolaitis (mappings & rewriting)**, optimizer teams at **CockroachDB / DuckDB / Umbra**. Threads: FD-aware **cardinality bounds** via entropic/AGM inequalities tightened by keys; learned detection of redundant joins; FD propagation through window functions and lateral joins; and minimization in **semiring / provenance** semantics where set-minimization no longer applies *(frontier — verify)*.

## 8. Future Work

(1) Cost-based optimal minimization (join cost, not atom count) with guarantees. (2) Practical, complete FD-aware join-elimination in mainstream optimizers. (3) Exploiting **approximate / soft FDs** mined from data, with correctness fallbacks. (4) Minimization under bag semantics and aggregation. (5) Tighter integration with AGM/submodular-width cardinality estimation so minimization and costing share the dependency model.

## 9. Key References

- **[Foundational]** Chandra, Merlin. *Optimal Implementation of Conjunctive Queries in Relational Data Bases.* STOC 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Foundational]** Aho, Sagiv, Ullman. *Equivalences Among Relational Expressions.* SIAM J. Computing, 1979. — [DOI](https://doi.org/10.1137/0208017)
- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* PODS 2017. — [DOI](https://doi.org/10.1145/3034786.3056105)
- **[SOTA]** Ngo, Porat, Ré, Rudra. *Worst-Case Optimal Join Algorithms.* PODS 2012 / JACM 2018. — [arXiv](https://arxiv.org/abs/1203.1952)
- **[Survey]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [book site](http://webdam.inria.fr/Alice/)

## 10. Worked Example

Schema: $\text{Emp}(\underline{eid}, dept)$ with key $eid$, and $\text{Dept}(\underline{did}, name)$ with key $did$, plus the foreign key $\text{Emp}.dept \subseteq \text{Dept}.did$. Query (find employee ids that have a department record):

$$Q(e) \,:\!-\, \text{Emp}(e, d),\ \text{Dept}(d, n).$$

Without constraints the $\text{Dept}$ atom is *not* redundant (an employee might reference a non-existent department). With the FK + key, every $d$ from $\text{Emp}.dept$ is guaranteed a matching $\text{Dept}(d,n)$, so the join cannot eliminate rows. Chase the frozen body: the IND adds nothing new beyond what the FK guarantees, and since $n$ is not in the output and $did$ is a key, the $\text{Dept}$ atom is provably joined to exactly one tuple. Homomorphism check confirms $Q \equiv_\Sigma Q'(e)\,:\!-\,\text{Emp}(e,d)$ — a 2-atom query minimized to 1 atom. This is precisely the *join-elimination* rule optimizers apply: cost drops from one join to a single scan, but only the FK+key (not set-minimization alone) licenses it.

---
*Part of the [DBMS Research catalog](../../README.md).*
