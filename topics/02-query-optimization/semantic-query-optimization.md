---
id: 02-query-optimization/semantic-query-optimization
title: "Optimizing under integrity constraints and semantics"
topic: 02-query-optimization
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimizing under integrity constraints and semantics

> **Topic:** Query Optimization · **ID:** `02-query-optimization/semantic-query-optimization` · **Status:** partially-solved

## 1. Problem Statement

**Semantic Query Optimization (SQO)** uses the database's *integrity constraints* — keys, foreign keys, functional dependencies (FDs), inclusion dependencies (INDs), check constraints, and general tuple-/equality-generating dependencies (TGDs/EGDs) — to transform a query $Q$ into a semantically equivalent but cheaper query $Q'$ *on every database instance satisfying the constraints*. Typical rewrites: **join elimination** (a key/FK join that adds no rows can be dropped), **predicate introduction** (derive a selective predicate implied by constraints), **predicate elimination** (a redundant or contradictory predicate), **detecting empty/unsatisfiable queries**, and **scan/index redirection**.

- **Decision variant:** given $Q$ and constraint set $\Sigma$, is a proposed rewrite $Q'$ **equivalent under $\Sigma$** (i.e., $Q \equiv_\Sigma Q'$)?
- **Optimization variant:** find the minimum-cost query equivalent to $Q$ under $\Sigma$.
- **Soundness requirement:** every rewrite must be valid on *all* $\Sigma$-consistent instances — unsound rewrites silently return wrong answers.

## 2. Mathematical Foundations

The engine of SQO is the **chase** (Maier–Mendelzon–Sagiv; Aho–Beeri–Ullman). To test $Q \equiv_\Sigma Q'$ for conjunctive queries under TGDs/EGDs $\Sigma$, one **chases** the queries with $\Sigma$ and checks for **containment via homomorphisms** (Chandra–Merlin theorem: $Q \sqsubseteq Q'$ iff a homomorphism $Q' \to Q$ exists on frozen bodies). Constraint *implication* — does $\Sigma \models$ (a derived dependency)? — is decided by the chase when it terminates.

Key facts:
- **Containment of conjunctive queries** is NP-complete (Chandra–Merlin).
- **Implication of FDs** is decidable in *linear time* (Beeri–Bernstein closure algorithm); FDs+INDs implication is **undecidable** in general (Chandra–Vardi), but acyclic/key-based fragments are decidable.
- The **chase terminates** under *weak acyclicity* of $\Sigma$ (Fagin–Kolaitis–Miller–Popa), giving a decidable equivalence test; for arbitrary TGDs the chase may not terminate and equivalence is **undecidable**.

Join elimination is the canonical example: an inner join on a foreign key referencing a non-null primary key is a **lossless** semijoin and can be removed — provable by chasing the FK IND.

## 3. State of the Art (SOTA)

- **Foundational SOTA:** King's **QUIST** (1981) introduced rule-based SQO; Chakravarthy–Grant–Minker gave the **residue method** formalizing constraint-based rewriting; Shenoy–Ozsoyoglu, and Sun–Yu advanced cost-based SQO.
- **Systems SOTA:** Production optimizers implement *constraint-aware* rewrites: **join elimination / FK-join removal**, **NOT NULL / CHECK-driven predicate simplification**, and **constraint-implied predicate inference** in IBM DB2, Oracle, Microsoft SQL Server, and PostgreSQL (e.g., removing redundant joins to a unique-keyed table). **Apache Calcite** has FK/PK-aware rules. **Magic-set** and **predicate move-around** (Levy–Mumick–Sagiv) propagate constraints/predicates across a query graph. Star/snowflake-schema warehouses rely heavily on FK-join elimination.

## 4. Upper Bound

For **conjunctive queries under weakly-acyclic TGDs+EGDs**, equivalence-under-constraints is decidable via the chase; the chase produces a universal instance of size at most polynomial in the data for a *fixed* schema (data complexity in PTIME), but **exponential** in the query/constraint size (combined complexity). FD closure and key-based join elimination run in **linear / polynomial time**. Thus the practically important rewrites (key/FK join elimination, FD-implied predicate inference) are *polynomial* and are what systems deploy.

## 5. Lower Bound

- **CQ containment / equivalence** (the soundness test) is **NP-complete** (Chandra–Merlin); under constraints it is at least as hard.
- **CQ equivalence/containment under TGDs+EGDs** is **undecidable** in general (the chase need not terminate); even **deciding chase termination** is undecidable (Deutsch–Nash–Remmel; Gogacz–Marcinkowski).
- **FD + IND implication** is **undecidable** (Chandra–Vardi; Mitchell). These results bound *general* SQO: there is no algorithm that soundly performs *all* constraint-implied rewrites for arbitrary constraint languages.

## 6. The Gap

The problem is **partially solved**: for *restricted, decidable* constraint classes (keys, FKs, FDs, weakly-acyclic TGDs) the equivalence test is decidable and the high-value rewrites are polynomial — these are deployed and effectively "closed." For *general* constraint languages (arbitrary TGDs, FD+IND) soundness is **undecidable**, so no complete SQO exists. The open frontier is (a) characterizing the *maximal decidable fragment* worth supporting, and (b) doing **cost-based** SQO — choosing *which* sound rewrite actually lowers cost, which couples back to cardinality estimation.

## 7. Current Research (as of June 2026)

- SQO over **denormalized lakehouse / star schemas**: aggressive FK-join elimination and constraint inference where constraints are *declared but unenforced* (Iceberg/Delta), raising soundness-under-unenforced-constraints questions. *(frontier — verify)*
- Constraint-aware rewriting integrated with **learned cardinality estimation** so rewrites that change cardinalities are costed correctly.
- SQO for **graph/RDF and Datalog** under ontological constraints (existential rules / Datalog±; Calì–Gottlob–Lukasiewicz). *(frontier — verify)*
- Verified/sound rewrite engines using SMT to discharge equivalence-under-constraints obligations (e.g., Cosette-style provers).

## 8. Future Work

- Cost-based selection among sound semantic rewrites with guarantees.
- Tight decidability map of "useful" constraint fragments for SQO.
- Sound SQO when constraints are *probabilistic* or *approximate* (dirty data).
- Machine-checked soundness for optimizer rewrite rules at scale.

## 9. Key References

- **[Foundational]** A. K. Chandra, P. M. Merlin. *Optimal Implementation of Conjunctive Queries in Relational Data Bases.* STOC, 1977. — [ACM](https://dl.acm.org/doi/10.1145/800105.803397)
- **[Foundational]** J. J. King. *QUIST: A System for Semantic Query Optimization in Relational Databases.* VLDB, 1981. — [DBLP](https://dblp.org/db/conf/vldb/vldb81.html)
- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data Exchange: Semantics and Query Answering.* ICDT/TCS, 2003–2005 (chase termination via weak acyclicity). — [DOI](https://doi.org/10.1007/3-540-36285-1_14)
- **[SOTA]** A. Levy, I. Mumick, Y. Sagiv. *Query Optimization by Predicate Move-Around.* VLDB, 1994. — [PDF](https://www.vldb.org/conf/1994/P096.PDF)
- **[SOTA]** U. S. Chakravarthy, J. Grant, J. Minker. *Logic-Based Approach to Semantic Query Optimization.* ACM TODS, 1990. — [ACM](https://dl.acm.org/doi/10.1145/78922.78924)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (chase, dependencies, containment). — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)

## 10. Worked Example

Schema: `Orders(oid PK, cid FK→Customers.cid NOT NULL)`, `Customers(cid PK, region)`. The FK is enforced and `cid` is `NOT NULL`. Query:

```sql
SELECT o.oid FROM Orders o JOIN Customers c ON o.cid = c.cid;
```

Each `Orders` row has exactly one matching `Customers` row (FK to a unique, non-null key), so the join neither drops nor duplicates any `Orders` tuple — it is a **lossless semijoin**. SQO rewrites it to just `SELECT oid FROM Orders;`, eliminating the join.

Soundness proof via the chase: freeze the body, then chase the IND $\text{Orders}.cid \subseteq \text{Customers}.cid$ plus the key EGD on `Customers.cid`. The chase forces the existential `c` to be uniquely determined by `o.cid`, so the frozen body maps homomorphically onto `Orders` alone — confirming $Q \equiv_\Sigma Q'$. With 3 orders pointing at 2 customers, both queries return the same 3 `oid`s, but the rewrite reads one table instead of two. If the FK were *declared but unenforced* (a lakehouse hazard, §7), an orphan `cid` would make the rewrite unsound.

---
*Part of the [DBMS Research catalog](../../README.md).*
