# Exact Functional-Dependency Discovery at Scale

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/scalable-fd-discovery` · **Status:** partially-solved

## 1. Problem Statement

Given a relation **instance** $r$ over attributes $R$ (with $|R|=n$ columns and $|r|=m$ rows), discover **all minimal, nontrivial functional dependencies** $X \to A$ that hold on $r$ (i.e., no two tuples agree on $X$ but differ on $A$), where minimality means no proper subset of $X$ also determines $A$. This is the data-driven inverse of normalization: we are handed data and must recover $\Sigma$ to drive schema design.

- **Enumeration variant:** output the complete set of minimal FDs (the "positive border" of the FD lattice).
- **Decision/existence subroutines:** test whether a given $X \to A$ holds; find the closure of a candidate.

The challenge is **scale**: the search space is the powerset lattice $2^R$, exponential in $n$, while validation is linear-to-quadratic in $m$. Real wide tables ($n$ in the dozens-to-hundreds, $m$ in the millions) make naive enumeration infeasible.

## 2. Mathematical Foundations

FDs form a lattice ordered by determinant set inclusion; the holding FDs are **upward closed**, so the minimal FDs are the lower border, discoverable by border/lattice traversal (Mannila–Räihä). Validation uses **partitions / stripped partitions** (position list indices, PLIs): $\pi_X$ refines $\pi_{XA}$ iff $X\to A$ holds, checkable by counting equivalence-class sizes. **Agree-sets** and **difference-sets** give a dual, instance-driven characterization: an FD's RHS must be a hitting set of the complements of agree sets.

The fundamental hardness: the number of minimal FDs can be **exponential in $n$** ($\binom{n}{n/2}$ in the worst case), so any complete algorithm is necessarily worst-case exponential in the number of columns — **output complexity dominates**.

## 3. State of the Art (SOTA)

Two algorithmic families, benchmarked in Papenbrock et al.'s *Functional Dependency Discovery: An Experimental Evaluation of Seven Algorithms* (VLDB 2015):

- **Lattice/column-efficient (good for many rows, fewer columns):** TANE (Huhtala et al. 1999), FUN, FD_Mine — use PLIs and level-wise lattice traversal.
- **Row-efficient / dependency-induction (good for many columns):** FastFDs (Wyss et al.), Dep-Miner (agree-set based), FDEP.
- **Hybrid SOTA:** **HyFD** (Papenbrock & Naumann, SIGMOD 2016) alternates sampling-based induction with lattice validation and is the practical state of the art. **Pyro** (Kruse & Naumann, VLDB 2018) extends hybrid search to approximate FDs. Distributed: HyFD-style and **HFDD**/Spark-based methods for cluster scale.

## 4. Upper Bound

- Worst-case **$O(2^n \cdot m)$**-style bounds dominate any exact algorithm; concretely, lattice methods are output-sensitive but exponential in $n$ in the worst case.
- HyFD achieves practical near-linear scaling in $m$ via focused sampling and PLI-based validation, and column scaling far better than pure lattice traversal, but offers **no sub-exponential worst-case guarantee** in $n$ — it is an engineering, not a complexity, improvement (RAM/external-memory model).

## 5. Lower Bound

- The **output** can be exponential in $n$, so no algorithm can be polynomial in $n$ alone; the relevant target is **output-polynomial / polynomial-delay** enumeration.
- Deciding whether there exists an FD with a left-hand side of size $\le k$ (and related minimal-cover questions on instances) is **NP-hard**; enumerating minimal FDs is at least as hard as enumerating minimal hitting sets / transversals, for which polynomial-delay in general is a **long-standing open problem** (equivalent to the complexity of monotone dualization / hypergraph transversal enumeration).

## 6. The Gap

The gap is between **practical near-linear row scaling** (HyFD/Pyro) and the **absence of any polynomial-delay guarantee in the number of columns**. Whether minimal FDs can be enumerated with polynomial delay reduces to the open status of hypergraph transversal enumeration (best known: quasi-polynomial, Fredman–Khachiyan). So the gap is genuinely open and tied to a famous enumeration-complexity question, not merely an engineering matter.

## 7. Current Research (as of June 2026)

- **Incremental / streaming FD discovery** (maintaining $\Sigma$ under inserts/deletes) — e.g., DynFD-style approaches.
- **GPU- and distributed-memory** FD discovery for very wide tables *(frontier — verify)*.
- Tight links to **enumeration complexity**: polynomial-delay results for restricted lattices, and instance-parameterized analyses.
- Active groups: Naumann's group (HPI), and the data-profiling community broadly.

## 8. Future Work

- Polynomial-delay enumeration for natural restricted classes (bounded LHS, small solution sets).
- Memory-bounded discovery with provable external-memory I/O complexity.
- Unifying exact, approximate, and conditional discovery in one scalable engine.

## 9. Key References

- **[Foundational]** Y. Huhtala, J. Kärkkäinen, P. Porkka, H. Toivonen. *TANE: An Efficient Algorithm for Discovering Functional and Approximate Dependencies.* The Computer Journal, 1999.
- **[Survey]** T. Papenbrock et al. *Functional Dependency Discovery: An Experimental Evaluation of Seven Algorithms.* PVLDB, 2015.
- **[SOTA]** T. Papenbrock, F. Naumann. *A Hybrid Approach to Functional Dependency Discovery (HyFD).* ACM SIGMOD, 2016.
- **[SOTA]** S. Kruse, F. Naumann. *Efficient Discovery of Approximate Dependencies (Pyro).* PVLDB, 2018.
- **[Foundational]** H. Mannila, K.-J. Räihä. *Algorithms for Inferring Functional Dependencies from Relations.* Data & Knowledge Engineering, 1994.
- **[Foundational]** M. Fredman, L. Khachiyan. *On the Complexity of Dualization of Monotone Disjunctive Normal Forms.* Journal of Algorithms, 1996.

---
*Part of the [DBMS Research catalog](../../README.md).*
