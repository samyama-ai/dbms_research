---
id: 05-concurrency-control/multiversion-conflict-minimization
title: "Multi-Version Conflict Minimization"
topic: 05-concurrency-control
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Multi-Version Conflict Minimization

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/multiversion-conflict-minimization` · **Status:** open

## 1. Problem Statement

In a multi-version database, each write installs a new *version* of a data item, and each read may be served by **any** committed version that respects the transaction's logical read point. The scheduler therefore has a *degree of freedom* absent in single-version systems: by choosing *which* version each read observes, it can render a history serializable that would otherwise contain unavoidable cycles in the conflict graph.

The **Multi-Version Conflict Minimization** problem asks: given a multi-version history (a set of transactions with their read/write operations and a partial commit order), choose a *version function* — a mapping from each read to a version it reads — so that the resulting history is **view-serializable** under the multi-version model (MVSR), and, in the optimization variant, minimizes a conflict cost (e.g., number of induced edges, expected aborts, or rollback work).

Variants:
- **Decision (MVSR membership):** Does *some* version function make a given multi-version history serializable? Equivalently, is the history in the class **MVSR**?
- **Optimization:** Among serializable version functions, minimize a weighted conflict/abort objective.
- **Online/scheduling:** Choose version read points incrementally as transactions arrive, without rollback.

## 2. Mathematical Foundations

A **multi-version (MV) history** over transactions $T = \{T_1,\dots,T_n\}$ is a triple $(H, \ll, \mathsf{ver})$ where $H$ orders the operations $w_i(x_j)$ (write producing version $x_j$) and $r_i(x_j)$ (read of version $x_j$), $\ll$ is the version order, and $\mathsf{ver}$ assigns each read a version. A **multiversion serialization graph** $MVSG(H, \ll)$ has nodes $T_i$ and edges induced by reads-from relations plus version-order constraints: for $r_k(x_j)$ and any $w_i(x_i)$, either $T_i \to T_j$ or $T_k \to T_i$ depending on whether $x_i \ll x_j$.

A history is **MVSR** iff there exists a version order $\ll$ making $MVSG(H, \ll)$ acyclic (Bernstein, Hadzilacos, Goodman 1987). The combinatorial core is the *existential quantifier over $\ll$*: we must pick a topological-friendly version order. Equivalently MVSR membership reduces to acyclic-orientation existence over a constraint graph with "either/or" disjunctive edges, a structure isomorphic to instances used in NP-hardness of view-serializability.

Formally, MVSR membership is **NP-complete** (Papadimitriou 1979; the multiversion extension follows from the disjunctive constraint structure). The optimization variant inherits hardness and additionally lacks known constant-factor approximation guarantees because feasible orientations form a non-convex, non-submodular family.

## 3. State of the Art (SOTA)

**Theory-SOTA.** The characterization of MVSR via acyclic $MVSG$ orientation (BHG 1987) remains canonical; no polynomial algorithm exists for general MVSR. Tractable *subclasses* are used in practice instead: **MVSS** (multiversion serializability under a *fixed* version function) is polynomial, and **snapshot isolation (SI)** fixes read points to transaction-start snapshots, sidestepping the search entirely.

**Systems-SOTA.** Production engines do not solve MVSR; they restrict to SI or serializable SI (SSI). **Serializable Snapshot Isolation** (Cahill, Röhm, Fekete, SIGMOD 2008; in PostgreSQL since 9.1) certifies serializability by detecting *dangerous structures* (two rw-antidependencies forming a pivot) at runtime — a cheap sufficient condition, not optimal version selection. **Hekaton** (Larson et al., VLDB 2011), **Silo** (Tu et al., SOSP 2013), and **Cicada** (Lim, Kaminsky, Andersen, SIGMOD 2017) use optimistic MVCC validation rather than search over version functions.

## 4. Upper Bound

For **fixed** version function, serializability testing is $O(|H| + n^2)$ (cycle detection in $MVSG$). For the **existential** MVSR decision problem the only general upper bound is the trivial exponential search over version orders — there is no known sub-exponential algorithm. For the practically dominant restriction (SI snapshots), version selection is $O(1)$ per read and SSI certification adds $O(\text{rw-edges})$ overhead, holding in the **shared-memory multicore** systems model.

## 5. Lower Bound

MVSR membership is **NP-complete** (Papadimitriou, *J. ACM* 1979 for VSR; multiversion lift via BHG 1987). Thus, unless P = NP, no polynomial algorithm decides general MVSR. The optimization (minimum-conflict version function) is NP-hard by the same reduction and is not known to admit any constant-factor approximation; it is at least as hard as acyclic subgraph / feedback-arc-style problems embedded by the disjunctive constraints. No matching APX-hardness with a tight constant is published, leaving the approximability question itself open.

## 6. The Gap

The decision problem is *closed* in complexity (NP-complete) but **open in exploitable structure**: real workloads are not adversarial, and the gap is between the worst-case NP-hardness and the absence of a characterization of *which* practical multi-version histories admit fast optimal version selection. Concretely: (1) no parameterization (treewidth of $MVSG$, number of antidependency cycles, write-skew density) is proven to yield FPT algorithms; (2) no approximation lower/upper bounds match for the optimization variant. Closing the gap means either an FPT/structural-tractability result for realistic transaction graphs, or APX-hardness ruling it out.

## 7. Current Research (as of June 2026)

Active directions: (i) *learned and contention-aware version-pointer selection* in HTAP engines, choosing read snapshots to reduce abort rates *(frontier — verify)*; (ii) fine-grained complexity of serializability variants extending the SETH-conditional lower bounds for transaction scheduling; (iii) deterministic databases (Calvin lineage, Abadi/Thomson) that eliminate the search by pre-ordering. Groups at MIT (Madden), CMU (Pavlo), TU Munich (Neumann/Leis on Umbra/HyPer MVCC), and Sydney/Fekete-lineage isolation theory remain central. Recent MVCC GC and version-pruning work (Böttcher et al., *Scalable Garbage Collection for In-Memory MVCC*, VLDB 2019) intersects this problem by bounding the version space the selector searches.

## 8. Future Work

- Identify graph parameters of $MVSG$ for which optimal version selection is FPT or polynomial.
- Establish tight approximability (constant-factor algorithm vs. APX-hardness) for minimum-conflict version functions.
- Online competitive analysis: lower bounds on the competitive ratio of any incremental version-point chooser vs. clairvoyant optimum.
- Workload-driven structural studies: empirically characterize how far real OLTP/HTAP histories sit from the NP-hard core.

## 9. Key References

- **[Foundational]** P. A. Bernstein, V. Hadzilacos, N. Goodman. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987. — [DBLP](https://dblp.org/db/books/dbtext/bernstein87.html)
- **[Foundational]** C. H. Papadimitriou. *The Serializability of Concurrent Database Updates.* Journal of the ACM, 1979. — [DOI](https://doi.org/10.1145/322154.322158)
- **[SOTA]** M. J. Cahill, U. Röhm, A. D. Fekete. *Serializable Isolation for Snapshot Databases.* SIGMOD, 2008. — [DOI](https://doi.org/10.1145/1376616.1376690)
- **[SOTA]** H. Lim, M. Kaminsky, D. G. Andersen. *Cicada: Dependably Fast Multi-Core In-Memory Transactions.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064015)
- **[SOTA]** P.-Å. Larson et al. *High-Performance Concurrency Control Mechanisms for Main-Memory Databases.* VLDB, 2011. — [DOI](https://doi.org/10.14778/2095686.2095689)
- **[Survey]** Y. Wu, J. Arulraj, J. Lin, R. Xian, A. Pavlo. *An Empirical Evaluation of In-Memory Multi-Version Concurrency Control.* VLDB, 2017. — [DOI](https://doi.org/10.14778/3067421.3067427)

## 10. Worked Example

Three transactions over items $x,y$, with two existing versions $x_0,y_0$:

$$H:\quad w_1(x_1)\; w_2(y_2)\; r_3(x_?)\; r_3(y_?)\; \text{(commits } T_1,T_2,T_3)$$

In a *single-version* schedule, $T_3$ would be forced to read the last-written values, and if $T_1\to T_3$ and $T_3\to T_2$ both held while $T_2$'s write preceded $T_1$'s in some order, the conflict graph could cycle. Multiversion gives $T_3$ a choice via the version function.

Pick $\mathsf{ver}(r_3(x)) = x_1$ and $\mathsf{ver}(r_3(y)) = y_0$ (the *old* $y$). Then reads-from edges are $T_1\to T_3$ (reads $x_1$) and $T_0\to T_3$. Because $T_3$ reads $y_0$ not $y_2$, we need version order $y_0 \ll y_2$ with $T_3 \to T_2$ (read precedes the overwrite). The MVSG is $T_0\to T_1\to T_3\to T_2$ — **acyclic**, so $H$ is MVSR with serial order $T_0,T_1,T_3,T_2$.

Had we instead set $\mathsf{ver}(r_3(y))=y_2$, we would force $T_2\to T_3$ and $T_3\to T_2$ jointly only if other edges conflicted — illustrating that the *existential search over $\ll$* is exactly the NP-hard core: here a lucky choice works, but in general finding such a function is intractable.

---
*Part of the [DBMS Research catalog](../../README.md).*
