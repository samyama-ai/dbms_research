# Provenance Semirings for Recursive and Aggregate Queries

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/semiring-provenance-recursion` · **Status:** partially-solved

## 1. Problem Statement
**Provenance** annotates query answers with how they were derived, supporting trust, deletion propagation, probabilistic databases, access control, and incremental view maintenance. The Green–Karvounarakis–Tannen framework computes provenance as elements of a commutative **semiring** $K$, and is clean and complete for the positive relational algebra (selection, projection, join, union). The open problem is to extend semiring provenance **soundly and finitely** to (a) **recursion** (Datalog / transitive closure / fixpoints), where the natural provenance is an infinite formal power series, and (b) **aggregation** (`SUM`, `MIN`, group-by), where values and annotations interact and the semiring axioms no longer suffice.

Variants: *finiteness* — when is recursive provenance representable by a finite circuit/expression? *soundness* — does the annotated semantics commute with the standard one? *absorptive/semiring choice* — which algebraic structure (semiring, $\omega$-continuous semiring, semimodule, dioid) gives the intended answer for shortest-path-style and confidence-style aggregates?

## 2. Mathematical Foundations
A commutative semiring $(K,\oplus,\otimes,0,1)$ annotates tuples; relational-algebra operators map to $\oplus$ (alternative derivations / union / projection) and $\otimes$ (joint use / join). The provenance polynomial semiring $\mathbb{N}[X]$ is **universal**: any other semiring's provenance is a homomorphic image. Examples: $\mathbb{B}$ (set semantics), $\mathbb{N}$ (bag), $\mathrm{Trio}$/why-provenance, the tropical semiring $(\mathbb{R}_{\ge0}\cup\{\infty\},\min,+)$ for shortest paths, $([0,1],\max,\cdot)$ for fuzzy/confidence.

**Recursion.** Datalog provenance is the **least fixpoint** of the immediate-consequence operator over $K$. Convergence requires $K$ to be **$\omega$-continuous** (naturally ordered, with limits of $\omega$-chains): then the provenance is a well-defined possibly-infinite power series in the algebra of formal power series $K\langle\!\langle X\rangle\!\rangle$. Finiteness needs additional structure — e.g., $K$ **absorptive** ($a\oplus(a\otimes b)=a$, i.e., $a\otimes b\le a$) so that the lfp stabilizes after finitely many "useful" derivations (Deutch–Milo–Roy–Tannen, "circuits"; Ramusat–Maniu–Senellart on **absorptive** / **bounded** semirings for recursion).

**Aggregation.** Annotated values live in a **semimodule** $M$ over $K$ (scalars annotate; module elements are aggregated values), with compatibility $k\cdot(m_1+m_2)=k\cdot m_1+k\cdot m_2$. Amsterdamer–Deutch–Tannen (PODS 2011) showed the semiring framework alone **cannot** capture aggregation; the $K$-relation must carry tensor-product symbolic aggregate terms.

## 3. State of the Art (SOTA)
Theory-SOTA: Green–Karvounarakis–Tannen (PODS 2007) for positive RA; Amsterdamer–Deutch–Tannen (PODS 2011) for aggregation via semimodules; Deutch–Gilad–Milo–Moskovitch and Senellart's group for **provenance circuits** that finitely represent recursive provenance. Ramusat, Maniu, Senellart (ICDT 2018/2021) characterize which semirings admit **finite, efficiently computable** recursive provenance (absorptive / star-semiring conditions) and connect to algebraic path problems. Systems-SOTA: **ProvSQL** (Senellart et al., VLDB 2018) — a PostgreSQL extension computing semiring provenance and probabilistic answers; **GProM** (Glavic et al.) for provenance via query rewriting; Soufflé/Datalog provenance for debugging.

## 4. Upper Bound
For positive RA, provenance is computed with **no asymptotic overhead** over evaluation: one extra semiring op per relational op, giving an $O(|\text{output}|)$-sized circuit. For recursion over an **absorptive** $\omega$-continuous semiring, the least fixpoint converges in $\le n$ iterations on $n$-element domains and the provenance circuit has polynomial size; over the **tropical** semiring it reduces to the algebraic-path / Kleene-star problem solvable in $O(n^3)$ (Floyd–Warshall-style) or via Tarjan's path-expression algorithm. Aggregate provenance is computed in time linear in output plus the cost of symbolic-term construction.

## 5. Lower Bound
Over a **non-absorptive** $\omega$-continuous semiring (e.g., $\mathbb{N}$, counting derivations), recursive provenance is a genuine **infinite** power series (e.g., the number of paths in a cyclic graph is unbounded) — no finite expression exists, an information-theoretic impossibility. Computing the full provenance polynomial $\mathbb{N}[X]$ can be of **exponential** size in the query (number of derivation trees). For aggregation, Amsterdamer–Deutch–Tannen prove an algebraic impossibility: no commutative semiring structure on annotated values is sound for `SUM`/`AVG` — the semimodule extension is *necessary*, not a convenience.

## 6. The Gap
Largely **characterized**: we know recursion is finite exactly for absorptive/star-continuous semirings and infinite otherwise, and that aggregation needs semimodules. The *remaining* gaps: (1) a unified theory for **recursion + aggregation together** (e.g., Datalog with `MIN`/`SUM` aggregates and confidences), where fixpoint, lattice convergence, and semimodule aggregation must coexist — only partial results; (2) tight **size/complexity** bounds for provenance circuits under aggregation; (3) provenance for **non-monotone** recursion (negation/stratified Datalog), where least-fixpoint semantics is unavailable.

## 7. Current Research (as of June 2026)
Senellart's group (ProvSQL, m-semirings, probabilistic provenance) and Tannen/Deutch continue the algebraic program. Active: **provenance for Datalog with aggregation** unifying the semimodule and lattice-Datalog views *(frontier — verify the latest recursion+aggregation soundness results)*; provenance over the **tropical/absorptive** semirings for graph and routing queries; **differential/incremental provenance** linking to recursive view maintenance; provenance for **probabilistic and approximate** answers and its #P-hardness boundaries. Ramusat–Maniu–Senellart's algebraic-path characterization is being extended to richer aggregate algebras *(frontier — verify)*.

## 8. Future Work
A single algebraic structure (semiring + semimodule + lattice) with proven convergence and finiteness for stratified Datalog with aggregation; tight circuit-size lower bounds; soundness for negation via provenance for well-founded/stable semantics; and systems support that keeps provenance overhead sublinear for recursive workloads.

## 9. Key References
- **[Foundational]** T. J. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS 2007.
- **[Foundational]** Y. Amsterdamer, D. Deutch, V. Tannen. *Provenance for Aggregate Queries.* PODS 2011.
- **[SOTA]** Y. Ramusat, S. Maniu, P. Senellart. *Provenance-Based Algorithms for Rich Queries over Graph Databases.* / *Semiring Provenance over Graph Databases.* ICDT 2018 / EDBT 2021.
- **[SOTA]** P. Senellart, L. Jachiet, S. Maniu, Y. Ramusat. *ProvSQL: Provenance and Probability Management in PostgreSQL.* PVLDB 11(12), 2018.
- **[Survey]** P. Senellart. *Provenance and Probabilities in Relational Databases.* SIGMOD Record 46(4), 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
