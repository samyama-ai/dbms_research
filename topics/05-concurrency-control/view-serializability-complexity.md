# Optimal Schedule Recognition Complexity

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/view-serializability-complexity` · **Status:** open

## 1. Problem Statement

Given a complete history (schedule) $H$ over a set of transactions, we want to recognize whether $H$ belongs to a desirable serializability class. Three classical classes are relevant:

- **Conflict-serializability (CSR):** $H$ is equivalent to a serial history under reordering of non-conflicting operations.
- **View-serializability (VSR):** $H$ is equivalent to a serial history with the same reads-from relation and final writes.
- **Final-state serializability (FSR):** $H$ produces the same final database state as some serial history.

The **decision problem** is: given $H$, decide membership in VSR (resp. FSR). The **optimization/counting variants** ask for the minimum number of operation reorderings to reach serializability, or the number of equivalent serial orders. A related recognition problem is detecting whether a *prefix-committed* schedule produced online by a scheduler is serializable, which underlies optimistic concurrency control validation. The open question is to pin the *exact* complexity landscape — including parameterized, fine-grained, and structural-restriction results — beyond the half-century-old NP-completeness baseline.

## 2. Mathematical Foundations

Model a history as a partial order on read/write steps $r_i(x), w_i(x)$ for transaction $i$ on object $x$. The **conflict graph** (serialization graph) $SG(H)$ has a node per transaction and an edge $T_i \to T_j$ when conflicting operations are ordered $i$ before $j$. The foundational theorem (Eswaran–Gray–Lorie–Traiger) states:

$$H \in \text{CSR} \iff SG(H) \text{ is acyclic},$$

testable in $O(n + e)$ time. View-serializability rests on the **reads-from relation** $RF(H) = \{(T_i, x, T_j) : T_j \text{ reads } x \text{ written by } T_i\}$ and the polygraph construction of Papadimitriou: $H \in \text{VSR}$ iff the associated polygraph admits an acyclic orientation. Deciding the existence of such an acyclic orientation is the source of hardness.

$$\text{CSR} \subsetneq \text{VSR} \subseteq \text{FSR}.$$

## 3. State of the Art (SOTA)

The defining result is **Papadimitriou (JACM 1979)**: testing VSR and FSR is **NP-complete**. CSR is decidable in linear time and is the basis of virtually all deployed schedulers, precisely because VSR is intractable. SOTA *theory*: the NP-completeness is robust, and Papadimitriou's monograph *The Theory of Database Concurrency Control* (1986) remains canonical. SOTA *systems*: no production system tests VSR; engines enforce CSR (two-phase locking, SSI) or weaker isolation, sidestepping recognition entirely. Recent structural work studies VSR under bounded conflict-graph treewidth and acyclic data-access patterns where polynomial recognition is recoverable.

## 4. Upper Bound

CSR membership: $O(n+e)$ deterministic. VSR/FSR membership: in **NP** (guess the equivalent serial order, verify reads-from and final-writes in polynomial time). Parameterized upper bound: VSR is fixed-parameter tractable in the number of objects written by multiple transactions, and polynomial when every object has a bounded number of writers — the polygraph has bounded "choice width," yielding an $O(2^k \cdot \text{poly})$ orientation search.

## 5. Lower Bound

**NP-hardness** of VSR and FSR (Papadimitriou 1979), via reduction from non-circular SAT / a specialized acyclic-orientation problem. The hardness persists even when each object is written at most a constant number of times above the FPT threshold. No fine-grained (SETH/3SUM-conditional) separation is known that would, e.g., rule out an $O(2^{n/2})$ exact algorithm; this is open. CSR's linear-time bound is essentially optimal (it subsumes cycle detection).

## 6. The Gap

For VSR, decision-complexity is **closed at the coarse level** (NP-complete). The genuine gaps are: (i) the *fine-grained* exact-exponential complexity of VSR — is there a $2^{o(n)}$ algorithm, or a SETH lower bound? (ii) a complete *dichotomy* over structural restrictions (graph classes, version bounds) separating polynomial from NP-hard instances; (iii) the complexity of the **counting** variant (#VSR) and the **online recognition** variant. These remain open.

## 7. Current Research (as of June 2026)

Active threads connect serializability recognition to constraint-satisfaction dichotomies and to fine-grained complexity of acyclic-orientation problems. Work on *robustness* under weak isolation (Cerone, Vandevoort, Neven) indirectly revives interest in tractable serializability fragments *(frontier — verify)*. Practical interest comes from deterministic databases and serializable cloud OLTP (Calvin/Aria lineage) where cheap online certification of serializability is valuable.

## 8. Future Work

- A SETH- or 3SUM-conditional lower bound (or a faster exact algorithm) for VSR.
- A full complexity dichotomy parameterized by conflict-graph structure and per-object writer count.
- Complexity of #VSR and of the minimum-reordering optimization variant.
- Streaming/online certification with provable competitive guarantees.

## 9. Key References

- **[Foundational]** Papadimitriou, C. H. *The Serializability of Concurrent Database Updates.* JACM, 1979.
- **[Foundational]** Eswaran, K. P.; Gray, J. N.; Lorie, R. A.; Traiger, I. L. *The Notions of Consistency and Predicate Locks in a Database System.* CACM, 1976.
- **[Foundational]** Papadimitriou, C. H. *The Theory of Database Concurrency Control.* Computer Science Press, 1986.
- **[Survey]** Bernstein, P. A.; Hadzilacos, V.; Goodman, N. *Concurrency Control and Recovery in Database Systems.* Addison-Wesley, 1987.
- **[SOTA]** Fekete, A. *Allocating Isolation Levels to Transactions.* PODS, 2005.

---
*Part of the [DBMS Research catalog](../../README.md).*
