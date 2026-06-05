# Multivalued and Join Dependency Discovery

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/mvd-jd-discovery` · **Status:** open

## 1. Problem Statement

Beyond FDs, higher normal forms rest on richer dependencies:

- A **multivalued dependency (MVD)** $X \twoheadrightarrow Y$ holds on $r$ if, for the values of $X$, the set of $Y$-values is independent of the remaining attributes $Z = R \setminus (X \cup Y)$. MVDs justify **4NF**.
- A **join dependency (JD)** $\bowtie[R_1,\dots,R_k]$ holds if $r$ equals the join of its projections onto $R_1,\dots,R_k$ (lossless multi-way decomposition). JDs justify **5NF / project–join normal form**.

The problem: **discover from a data instance the MVDs and JDs that hold**, so a designer can justify a 4NF/5NF decomposition — **without** the naive strategy of enumerating all possible decompositions and testing each for losslessness.

- **MVD discovery (enumeration):** output all minimal nontrivial MVDs holding on $r$.
- **JD discovery / recognition:** find lossless multi-way decompositions; given a candidate JD, decide whether it holds.

## 2. Mathematical Foundations

An MVD $X\twoheadrightarrow Y$ holds iff $r = \pi_{XY}(r) \bowtie \pi_{XZ}(r)$ — i.e., it is exactly a **binary JD**. MVDs satisfy a richer axiomatization (Beeri–Fagin–Howard) and exhibit the **complementation** rule: $X\twoheadrightarrow Y \Leftrightarrow X\twoheadrightarrow Z$. Validation uses partitions: $X\twoheadrightarrow Y$ holds iff within each $X$-class the tuples form a Cartesian product over $Y$ and $Z$ projections.

**JDs are strictly more expressive** than MVDs and are **not finitely axiomatizable by MVD rules alone**; checking whether a JD holds on an instance requires a **chase**-style or projection–join test. The implication problem for JDs (do $\Sigma$ logically imply a JD) is markedly harder than for FDs/MVDs.

The combinatorial obstacle: the space of candidate MVDs is, like FDs, exponential in $n$, but each *check* is costlier (a join/Cartesian-product test), and JDs add the choice of **arbitrary $k$-ary partitions** of attributes — a doubly exponential candidate space.

## 3. State of the Art (SOTA)

- **MVD discovery:** far less developed than FD discovery. Notable: methods deriving MVDs from FD/agree-set structure and partition refinement; Savnik & Flach-style dependency inference; recent partition-based MVD miners. There is **no** universally adopted "TANE for MVDs."
- **JD discovery:** essentially **open / nascent** — most work addresses JD *implication* and *recognition* (acyclic JDs, $\gamma$-acyclicity) rather than data-driven discovery. Acyclic JDs are well-understood (Beeri–Fagin–Maier–Yannakakis 1983) and tractable to test; general JD discovery is not practically solved.
- **Implication:** MVD/FD implication is decidable in polynomial time (Beeri 1980); JD implication is more complex.

## 4. Upper Bound

- **MVD validation** of a single candidate: polynomial in $m$ via partitions (Cartesian-product test per $X$-class); **enumeration** is exponential in $n$ (output can be exponential), so output-sensitive at best.
- **Acyclic JD recognition:** the GYO reduction tests acyclicity in polynomial time, and acyclic-JD losslessness is checkable efficiently; **general $k$-ary JD discovery** has no known sub-doubly-exponential algorithm because of the partition search space.

## 5. Lower Bound

- The number of minimal MVDs can be **exponential in $n$**, ruling out poly-$n$ complete discovery (output lower bound), analogous to FDs.
- **JD implication** is, in general, harder than FD/MVD implication; deciding implication for unrestricted JDs together with FDs is **NP-hard / not finitely axiomatizable** in the MVD calculus (Beeri–Vardi). Discovery over arbitrary attribute partitions inherits a **doubly exponential** candidate space.
- Lossless-decomposition existence under general JDs ties to chase termination, which is undecidable for unrestricted tuple-generating dependencies (though decidable for the JD/MVD fragment).

## 6. The Gap

This is **genuinely open**. For FDs we have mature, scalable discovery; for MVDs the algorithmics are immature and lack a benchmarked SOTA; for JDs, data-driven discovery is largely **unsolved** — recognition of acyclic JDs is tractable but *finding* the right multi-way decomposition without enumerating partitions has no established polynomial-delay or output-sensitive algorithm. Closing the gap requires (i) a HyFD-class efficient MVD miner with pruning that exploits complementation, and (ii) a principled JD-discovery method that searches decompositions guided by acyclicity rather than brute force.

## 7. Current Research (as of June 2026)

- Partition/PLI-based **MVD miners** extending FD-discovery infrastructure (Metanome ecosystem) *(frontier — verify)*.
- Restricting to **acyclic / hierarchical JDs** to make discovery tractable and tie directly to GYO and 5NF *(frontier — verify)*.
- Connections to **factorized databases** and **worst-case-optimal joins** (Ngo–Porat–Ré–Rudra), where JD/acyclicity structure governs representation size — a fresh lens on which decompositions are worth discovering.
- Active: data-profiling community (HPI/Naumann), database-theory groups on dependency implication.

## 8. Future Work

- A scalable, benchmarked MVD-discovery algorithm with complementation-aware pruning.
- Output-sensitive JD discovery restricted to acyclic decompositions, justifying 4NF/5NF without enumerating all partitions.
- Robust/approximate MVDs and JDs for dirty data, mirroring the AFD/CFD line.
- Tight complexity characterization of minimal-JD enumeration.

## 9. Key References

- **[Foundational]** R. Fagin. *Multivalued Dependencies and a New Normal Form for Relational Databases.* ACM TODS, 1977. — [DOI](https://doi.org/10.1145/320557.320571)
- **[Foundational]** C. Beeri, R. Fagin, J. H. Howard. *A Complete Axiomatization for Functional and Multivalued Dependencies.* ACM SIGMOD, 1977. — [DOI](https://doi.org/10.1145/509404.509414)
- **[Foundational]** R. Fagin. *Normal Forms and Relational Database Operators (PJ/NF, 5NF).* ACM SIGMOD, 1979. — [DBLP search](https://dblp.org/search?q=Fagin+Normal+Forms+and+Relational+Database+Operators)
- **[Foundational]** C. Beeri, R. Fagin, D. Maier, M. Yannakakis. *On the Desirability of Acyclic Database Schemes.* JACM, 1983. — [DOI](https://doi.org/10.1145/2402.322389)
- **[SOTA]** H. Q. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-Case Optimal Join Algorithms.* JACM, 2018 (PODS 2012). — [DOI](https://doi.org/10.1145/3180143)
- **[Survey]** Z. Abedjan, L. Golab, F. Naumann. *Profiling Relational Data: A Survey.* The VLDB Journal, 2015. — [DOI](https://doi.org/10.1007/s00778-015-0389-y)

## 10. Worked Example

Consider the classic 4NF-violating relation $\text{CTB}(\text{Course},\text{Teacher},\text{Book})$ — each course has a set of teachers and an *independent* set of books:

| Course | Teacher | Book   |
|--------|---------|--------|
| DB     | Alice   | Ullman |
| DB     | Alice   | Date   |
| DB     | Bob     | Ullman |
| DB     | Bob     | Date   |

For $X=\text{Course}$, the single $X$-class $\{\text{DB}\}$ contains every $(\text{Teacher},\text{Book})$ pair — a $2\times 2$ Cartesian product $\{$Alice,Bob$\}\times\{$Ullman,Date$\}$. By the partition test, $\text{Course}\twoheadrightarrow\text{Teacher}$ holds (and by complementation $\text{Course}\twoheadrightarrow\text{Book}$). Equivalently the binary JD $\bowtie[\text{CT},\text{CB}]$ holds: $\pi_{CT}=\{($DB,Alice$),($DB,Bob$)\}$ joined with $\pi_{CB}=\{($DB,Ullman$),($DB,Date$)\}$ on Course reproduces all 4 rows losslessly. Drop one row, say (DB, Bob, Date): the class is no longer a full product (it has 3 of 4 cells), the MVD fails, and the join would *re-introduce* the missing tuple — a spurious tuple exposing the lost dependency. The 4NF fix decomposes CTB into CT and CB, each storing $2$ rows instead of $4$.

---
*Part of the [DBMS Research catalog](../../README.md).*
