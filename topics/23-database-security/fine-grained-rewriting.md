---
id: 23-database-security/fine-grained-rewriting
title: "Query Rewriting for Fine-Grained Access"
topic: 23-database-security
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Query Rewriting for Fine-Grained Access

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/fine-grained-rewriting` · **Status:** partially-solved

## 1. Problem Statement

Fine-grained access control (FGAC) attaches policies at the granularity of **rows, columns, or individual cells** (e.g., "a manager sees salaries only of their own department; everyone else sees NULL"). The enforcement mechanism is **query rewriting**: an arbitrary user query $Q$ is transformed into a query $Q'$ that runs against the base data but returns only authorized information.

The problem: produce a rewriting that is **sound** (never returns unauthorized data) *and* **complete** (returns all authorized data the user is entitled to), for **arbitrary SQL** — including aggregation, subqueries, negation, ordering, and `LIMIT` — **without side-channel leakage**. Side channels include:
- **Error-based leakage:** a filtered row triggering (or *not* triggering) a runtime error (divide-by-zero, type cast, constraint) reveals masked values.
- **Cardinality/timing leakage:** `COUNT(*)`, result size, or query latency revealing the existence of rows the policy hides.
- **Semantic distortion:** masking that breaks query semantics (e.g., `AVG` over partially masked columns) producing a result that *implies* the hidden values.

This is **partially solved**: sound-and-complete rewriting exists for the **Non-Truman** model on CQ/SPJ queries (Rizvi et al.), and row-level security is widely deployed; the open part is closing the side-channel and full-SQL gaps with provable guarantees.

## 2. Mathematical Foundations

Two semantic models (Rizvi et al.):
- **Truman model:** the system silently rewrites $Q$ to $Q'$ presenting a "true for this user" sub-world; risk is *misleading completeness* (e.g., `AVG` computed over a filtered table differs from the user's expectation).
- **Non-Truman model:** the system *rejects* a query unless it is **valid** — i.e., equivalent to its rewriting under the authorization views. Validity is *query equivalence under views*:
$$Q \text{ is valid} \iff Q \equiv Q' \text{ on every database, given authorization views } \mathcal{A}.$$

Rewriting correctness is the conjunction of:
1. **Soundness:** $Q'(D) \subseteq$ authorized($Q$, $D$) for all $D$.
2. **Completeness:** $Q'(D) \supseteq$ authorized($Q$, $D$).
3. **Non-interference:** the *observable behavior* (results, errors, cardinality, timing) is a function only of authorized data — formalized as an indistinguishability / non-interference property: for databases $D_1, D_2$ agreeing on the user's authorized projection, the observable outcome is identical.

The hard cases involve **aggregation** (where masking interacts with semantics) and **three-valued logic / NULLs** introduced by cell masking, which can change predicate evaluation in subtle ways.

## 3. State of the Art (SOTA)

- **Rizvi–Mendelzon–Sudarshan–Roy (SIGMOD 2004):** the Truman/Non-Truman framework; sound rewriting via authorization views and a validity test based on query equivalence under views — the canonical theory result.
- **Oracle VPD / FGAC and predicated grants (Chaudhuri–Dutta–Sudarshan, ICDE 2007):** predicate-based grants with row/column policies, with rewriting semantics analyzed.
- **Disclosure-aware rewriting / labeled databases:** systems tracking provenance/labels to enforce cell-level policies.
- Systems-SOTA: **PostgreSQL Row-Level Security (RLS)**, **Oracle VPD**, **SQL Server RLS + Dynamic Data Masking**, and cloud warehouse policies (**Snowflake** row-access/masking policies, **BigQuery** column-level security). These are sound for row filtering but documented to leak via masking-vs-filtering subtleties and via error/cardinality channels.

## 4. Upper Bound

- **Truman-model rewriting for SPJ + aggregation:** polynomial-time syntactic rewriting (predicate injection), sound by construction; widely deployed (RLS).
- **Non-Truman validity for CQ/UCQ:** decidable via query equivalence under views; complexity **NP-complete** to **$\Pi_2^p$** in query size.
- Cell-masking with NULL semantics: rewriting is polynomial but completeness/non-interference holds only on restricted fragments (no masked column inside an error-raising or aggregate context).

## 5. Lower Bound

- **Validity testing reduces to query equivalence**, which is **undecidable** for full relational algebra (with negation/inequality) and **NP-hard** already for CQs — lower-bounding any complete Non-Truman rewriter.
- **Determinacy/rewritability divergence** (Nash–Segoufin–Vianu) implies some authorized queries are *not first-order rewritable*, so a sound-and-complete FOL/SQL rewriting **provably cannot exist** for those cases.
- Side channels are an **information-flow non-interference** problem; eliminating timing/cardinality leakage in general is as hard as enforcing non-interference, with known impossibility for unrestricted programs.

## 6. The Gap

For **row filtering and the CQ/SPJ core, the problem is solved** (sound, often complete, deployed). The gap is threefold and **open**: (1) **full SQL** with aggregation/negation/`LIMIT` lacks a sound *and* complete rewriting because rewritability can fail; (2) **side-channel-free** enforcement (error, cardinality, timing) is not achieved by current systems and runs into non-interference hardness; (3) **cell-level masking under NULL/3-valued logic** can silently distort or leak through aggregates. Closing it requires either new fragments that are provably rewritable and side-channel-closed, or a principled "reject-or-rewrite" (Non-Truman) discipline extended to aggregation with quantified leakage guarantees.

## 7. Current Research (as of June 2026)

- **Information-flow type systems for SQL** that certify non-interference of rewritten queries, catching error/cardinality channels at compile time *(frontier — verify)*.
- Formal verification of **cloud-warehouse masking/row-access policies** (Snowflake/BigQuery) for cell-level correctness under joins and aggregation *(frontier — verify)*.
- Integration with **differential privacy** for the aggregation side channel: bounding what cardinalities/aggregates can leak.
- Lineage of Sudarshan, Chaudhuri, and the data-security/PL non-interference communities remains active.

## 8. Future Work

- Sound-and-complete (or provably-best-effort) rewriting for SQL with aggregation, with a precise characterization of the rewritable fragment.
- Side-channel-closed enforcement: formal guarantees against error-, cardinality-, and timing-based leakage.
- Correct cell-masking semantics under three-valued logic, with verified aggregate behavior.
- End-to-end certified FGAC compilers emitting machine-checkable soundness/non-interference proofs.

## 9. Key References

- **[Foundational]** Shariq Rizvi, Alberto Mendelzon, S. Sudarshan, Prasan Roy. *Extending Query Rewriting Techniques for Fine-Grained Access Control.* SIGMOD, 2004. — [DOI](https://doi.org/10.1145/1007568.1007631)
- **[SOTA]** Surajit Chaudhuri, Tanmoy Dutta, S. Sudarshan. *Fine Grained Authorization Through Predicated Grants.* ICDE, 2007. — [DBLP](https://dblp.org/rec/conf/icde/ChaudhuriDS07.html)
- **[Foundational]** Alan Nash, Luc Segoufin, Victor Vianu. *Views and Queries: Determinacy and Rewriting.* ACM TODS, 2010. — [DOI](https://doi.org/10.1145/1806907.1806913)
- **[Foundational]** Arnon Rosenthal, Edward Sciore. *View Security as the Basis for Data Warehouse Security.* DMDW, 2000. — [CEUR](https://ceur-ws.org/Vol-28/paper8.pdf)
- **[Survey]** Andrei Sabelfeld, Andrew C. Myers. *Language-Based Information-Flow Security.* IEEE Journal on Selected Areas in Communications, 2003. — [DOI](https://doi.org/10.1109/JSAC.2002.806121)

## 10. Worked Example

Table `Emp(name, dept, salary)`, four rows:

| name | dept | salary |
|------|------|--------|
| Ann  | HR   | 90     |
| Bob  | HR   | 120    |
| Cara | IT   | 200    |
| Dan  | IT   | 110    |

Policy for manager *Ann* of HR: "see salaries only of your own department." The authorization view is
`V = SELECT name, dept, salary FROM Emp WHERE dept='HR'`.

**Row filtering (Truman, sound):** Ann's query `SELECT name, salary FROM Emp` is silently rewritten to run against $V$, returning `{Ann:90, Bob:120}`. Correct and side-channel-free for this query.

**Aggregate distortion:** Ann issues `SELECT AVG(salary) FROM Emp`. Rewritten over $V$ it returns $\tfrac{90+120}{2}=105$. But Ann may *believe* it is the company-wide average; the true value is $\tfrac{90+120+200+110}{4}=130$. The rewriting is sound (no unauthorized cell shown) yet *misleadingly complete* — the hidden IT salaries silently change the answer.

**Non-Truman response:** instead of silently answering, the system tests validity — is `AVG(salary) FROM Emp` $\equiv$ its rewrite under $V$ on *every* database? It is not (IT rows matter), so the query is **rejected**, forcing Ann to phrase `... WHERE dept='HR'` explicitly. This trades completeness for honesty, and is the crux of the open gap for aggregation.

---
*Part of the [DBMS Research catalog](../../README.md).*
