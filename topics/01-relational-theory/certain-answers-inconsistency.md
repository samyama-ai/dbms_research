# Certain Answers Over Inconsistent Databases

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/certain-answers-inconsistency` · **Status:** partially-solved

## 1. Problem Statement

A database $D$ may **violate** its integrity constraints $\Sigma$ (keys, functional dependencies, denial constraints, inclusion dependencies). Rather than rejecting $D$, *consistent query answering* (CQA) asks: which answers to a query $Q$ hold no matter how $D$ is minimally "repaired" into a consistent instance.

- **Repair**: a consistent instance $D'$ that differs from $D$ minimally (subset/superset/symmetric-difference of tuples, or attribute-level updates).
- **Consistent / certain answer**: a tuple $\bar t$ that is an answer to $Q$ over *every* repair $D'$ of $D$ w.r.t. $\Sigma$.

**Decision variant** ($\mathrm{CERTAINTY}(Q)$): given $D$ and (for Boolean $Q$) decide whether $Q$ holds in all repairs. **Counting variant** ($\sharp\mathrm{CERTAINTY}(Q)$): count repairs satisfying $Q$ — a proxy for probabilistic semantics. The central goal is to identify, for fixed constraints and query class, when CQA has **tractable data complexity** (PTIME in $|D|$) and to draw the exact tractability frontier.

## 2. Mathematical Foundations

The semantics is the AGM-style "certain truth over all minimal-change models." For **subset repairs** under denial constraints, repairs correspond to **maximal independent sets** of the *conflict hypergraph* whose hyperedges are minimal violating tuple sets. Certainty of a Boolean self-join-free conjunctive query (sjfBCQ) under a single key per relation reduces to reasoning over this conflict graph.

A landmark result is the **trichotomy** (Koutris–Wijsen) for $\mathrm{CERTAINTY}(Q)$ with primary keys and sjfBCQ $Q$: every such $Q$ is either in **PTIME** (often expressible in first-order logic, sometimes requiring Datalog/least-fixpoint), or **coNP-complete**, with a decidable syntactic criterion on the *attack graph* of $Q$ separating the cases. Formally, FO-rewritability holds iff the attack graph is acyclic; PTIME (via fixpoint) holds under a "weak-cycle" condition; otherwise coNP-complete.

For counting, $\sharp\mathrm{CERTAINTY}(Q)$ under primary keys obeys a **dichotomy** (Maslowski–Wijsen): $\sharp P$-complete or in FP.

## 3. State of the Art (SOTA)

- **Theory SOTA**: the Koutris–Wijsen attack-graph trichotomy (sjfBCQ, primary keys) and its counting dichotomy are essentially complete and effective. Extensions to **multiple/foreign keys**, self-joins, and **denial constraints** remain partial.
- **Systems SOTA**: CQA is solved in practice by reduction to **Answer Set Programming** (ASP) or to **SAT/MaxSAT/ILP**. The **CAvSAT** system (Dixit–Kolaitis, 2019) reduces CQA to (partitioned weighted) SAT and handles arbitrary denial constraints, performing well even on coNP-hard instances. **LinCQA** (2021) compiles FO-rewritable cases to efficient SQL.

## 4. Upper Bound

For sjfBCQ under primary keys in the PTIME side of the trichotomy: **FO-rewritable** cases run in $\mathrm{AC}^0$ data complexity (a single SQL query); fixpoint cases run in PTIME via Datalog. General CQA under denial constraints sits in **coNP** (data complexity) because non-certainty is witnessed by one counterexample repair, checkable in PTIME. Under set-based repairs the combined complexity is typically $\Pi^p_2$.

## 5. Lower Bound

The hard side of the trichotomy is **coNP-complete in data complexity** (reductions from MONOTONE-3SAT / independent-set on the conflict hypergraph). With foreign keys (inclusion dependencies) plus keys, CQA jumps to $\Pi^p_2$-complete and can become **undecidable** for unrestricted tgd+egd sets. Counting hardness is $\sharp P$-completeness for the non-FP queries.

## 6. The Gap

The frontier is **closed** for sjfBCQ + single primary key (decision and counting). It is **open** for: (i) conjunctive queries *with self-joins* — only fragments are classified; (ii) sets mixing keys and **inclusion dependencies**; (iii) **operational/attribute-level** repairs and preference-based repairs; (iv) practical gap — many coNP-hard instances are easy for SAT solvers, so a *parameterized/instance* complexity theory is missing.

## 7. Current Research (as of June 2026)

Active groups: **Wijsen (Mons)**, **Kolaitis (UCSC)**, **Koutris (Wisconsin)**, **Bertossi (Chile)**. Directions: self-join trichotomies *(frontier — verify)*; CQA under **functional + inclusion** dependency interaction; **probabilistic/most-probable-repair** semantics linking CQA to PDBs; and CQA as a benchmark for **Shapley-value attributions** of tuples to inconsistency. CAvSAT-style portfolio solvers continue to be the systems baseline.

## 8. Future Work

(1) Complete the self-join CQA classification. (2) A fine-grained / instance-optimal account explaining solver success on coNP-hard queries. (3) CQA over **incomplete + inconsistent** data jointly (nulls + violations). (4) Repair semantics for **graph/RDF** and JSON. (5) Scalable approximate certain answers with error guarantees.

## 9. Key References

- **[Foundational]** Arenas, Bertossi, Chomicki. *Consistent Query Answers in Inconsistent Databases.* PODS 1999.
- **[SOTA]** Koutris, Wijsen. *Consistent Query Answering for Primary Keys and Conjunctive Queries* / *The Data Complexity of Consistent Query Answering for Self-Join-Free Conjunctive Queries.* PODS/TODS, 2015–2021.
- **[SOTA]** Maslowski, Wijsen. *A Dichotomy in the Complexity of Counting Database Repairs.* JCSS, 2013.
- **[SOTA]** Dixit, Kolaitis. *A SAT-Based System for Consistent Query Answering (CAvSAT).* SAT 2019.
- **[Survey]** Bertossi. *Database Repairing and Consistent Query Answering.* Morgan & Claypool, 2011.
- **[Survey]** Wijsen. *Foundations of Query Answering on Inconsistent Databases.* SIGMOD Record, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
