# Bug-Inducing Query Minimization

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/bug-query-minimization` · **Status:** partially-solved

## 1. Problem Statement

Given a failing triple $(q, S, I)$ — a query $q$, schema $S$, and data instance $I$ that together trigger a bug (crash, wrong result, assertion) in DBMS $D$ — produce a **smallest** still-failing reproducer $(q', S', I')$. "Smallest" is measured by a size functional (query AST nodes + schema columns + rows/bytes). The goal is a minimal, human-debuggable reproducer, ideally with **minimality guarantees**.

Variants:
- **1-minimality (decision-feasible):** no single deletion still fails (local minimum).
- **Global-minimality (optimization):** smallest over all failing sub-instances — generally intractable.
- **Joint minimization:** simultaneously shrink query, schema, and data (coupled constraints: dropping a column may invalidate $q$).

## 2. Mathematical Foundations

Let the **test predicate** $\psi(x)=1$ iff variant $x$ still triggers the same bug. The configuration space is a lattice over deletions of AST nodes, schema elements, and rows, with a *validity* constraint $V(x)$ (must parse, bind, type-check). We seek
$$ x^\star = \arg\min_{x:\ \psi(x)\wedge V(x)} \text{size}(x). $$

$\psi$ is a black-box, **non-monotone** oracle (removing an element may break or restore the failure), which is what makes global minimization hard. **Delta Debugging (ddmin)** computes a **1-minimal** subset in $O(n^2)$ predicate evaluations worst case (often $O(n\log n)$), guaranteeing only local minimality. Reduction respecting grammar (validity $V$) is **Hierarchical/Perses-style** reduction over the parse tree, giving 1-tree-minimality. Coupled query+schema+data minimization is a constrained reduction where edits must preserve binding — formally a closure condition $V$ over the lattice.

Global minimality is essentially a smallest-witness problem; with a non-monotone oracle it has no sub-exponential guarantee in general.

## 3. State of the Art (SOTA)

- **Delta Debugging / ddmin** (Zeller & Hildebrand, IEEE TSE 2002): general 1-minimal input reduction; the backbone of bug reduction.
- **HDD — Hierarchical Delta Debugging** (Misherghi & Su, ICSE 2006): tree-aware reduction, far fewer invalid variants for structured inputs like SQL.
- **Perses** (Sun et al., ICSE 2018) and **Vulcan/ProbDD**: grammar-guided, syntactically-valid-by-construction reducers; strong on programs and SQL.
- **SQLancer reducers** and **SQLReduce** specialize Perses/ddmin to SQL, jointly shrinking query and (sometimes) schema/data; widely used to file minimal DBMS bug reports.
- **C-Reduce** lineage shows the systems-SOTA for aggressive, validity-preserving reduction (transferable techniques).

## 4. Upper Bound

ddmin is **1-minimal** in $O(n^2)$ oracle calls (worst case), typically near $O(n\log n)$. HDD/Perses preserve validity, cutting wasted oracle calls by orders of magnitude and yielding 1-tree-minimal outputs. No polynomial algorithm guarantees **global** minimality under a non-monotone oracle; with $k$ independent dimensions (query/schema/data) the lattice is $2^{n_q}\times2^{n_S}\times2^{n_I}$, and only local optima are reachable in poly oracle-calls.

## 5. Lower Bound

- Finding the **globally smallest** failing input under a black-box non-monotone predicate requires $\Omega(2^{n})$ oracle queries in the worst case (no structure to exploit) — an information-theoretic / query-complexity lower bound.
- If $\psi$ encodes satisfiability (e.g., minimal failing `WHERE` clause), minimization is **NP-hard**.
- 1-minimality $\neq$ global minimality: there exist instances with exponentially many 1-minimal configurations of differing size, so local procedures cannot certify global optimality.

## 6. The Gap

We have provable **1-minimality** (ddmin) and validity-preserving tree-minimality (HDD/Perses) efficiently; we **lack** efficient *global* minimality with guarantees, which is provably out of reach under the black-box non-monotone model. The practical gap is for the *coupled* query+schema+data triple: current tools shrink the query well but reduce data/schema less aggressively, and there is no near-minimality certificate. *Partially-solved*: local guarantees are solid; global/near-minimality with certificates is open. Probabilistic reducers (ProbDD) improve empirical size but still without provable bounds.

## 7. Current Research (as of June 2026)

- **Joint query+schema+data** reduction with binding-aware edits and SMT-assisted data shrinking *(frontier — verify)*.
- **ProbDD / learned** reducers giving smaller outputs and (sought) probabilistic near-minimality guarantees *(frontier — verify)*.
- LLM-assisted transformation generation (e.g., rewriting subqueries to constants) to escape local minima.
- Groups: Zhendong Su / Chengnian Sun (Perses, ProbDD lineage), Andreas Zeller (delta debugging), Manuel Rigger (NUS, SQL-specific reducers).

## 8. Future Work

- Certificates of near-minimality (e.g., "within factor $c$ of optimal") for SQL reducers.
- Unified cost model trading query vs. data vs. schema size for debuggability.
- Reducers that also *generalize* a bug to a minimal failing *class*, not one instance.
- Reproducer minimization that preserves the *root cause*, not merely the symptom.

## 9. Key References

- **[Foundational]** A. Zeller, R. Hildebrandt. *Simplifying and Isolating Failure-Inducing Input (Delta Debugging).* IEEE TSE, 2002.
- **[Foundational]** G. Misherghi, Z. Su. *HDD: Hierarchical Delta Debugging.* ICSE, 2006.
- **[SOTA]** C. Sun, Y. Li, Q. Zhang, T. Gu, Z. Su. *Perses: Syntax-Guided Program Reduction.* ICSE, 2018.
- **[SOTA]** G. Wang, R. Shen, J. Chen, Y. Xiong, L. Zhang. *Probabilistic Delta Debugging (ProbDD).* ESEC/FSE, 2021.
- **[SOTA]** J. Regehr et al. *Test-Case Reduction for C Compiler Bugs (C-Reduce).* PLDI, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
