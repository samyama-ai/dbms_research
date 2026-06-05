# Provenance Semirings for Recursive Queries

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/provenance-semiring-recursion` · **Status:** partially-solved

## 1. Problem Statement

Semiring provenance (Green–Karvounarakis–Tannen, PODS 2007) annotates each base tuple with an element of a commutative semiring $K$ and propagates annotations through positive relational algebra so that the annotation of an output tuple records *how* it was derived (which tuples, in which alternative/joint combinations). The problem: **extend this provenance calculus soundly and *finitely* to recursive queries (Datalog) and to queries with aggregation**, where derivations may be infinite (cyclic) and aggregation is not a semiring operation.

Concretely:

- For **recursive Datalog**, a tuple can have infinitely many derivation trees (cycles), so its provenance is an *infinite formal power series*. We need semirings and representations in which the least fixpoint exists, is *finite/effectively computable*, and is the intended provenance.
- For **aggregation** ($\mathrm{SUM}$, $\mathrm{COUNT}$, $\mathrm{MIN}$, etc.) and **grouping**, values and annotations interact, requiring a richer algebraic structure than a single semiring.

The goal is a provenance framework that (a) specializes correctly to known instances (lineage, why-provenance, trust, security clearance, Boolean/counting, tropical shortest-path), (b) supports recursion with a well-defined finite result, and (c) handles aggregates compositionally.

## 2. Mathematical Foundations

A **commutative semiring** $(K,+,\cdot,0,1)$ models alternative use of data by $+$ and joint use by $\cdot$. Positive RA over $K$-relations is the canonical homomorphic image of the **provenance polynomial semiring** $\mathbb{N}[X]$ (the free commutative semiring), which is *universal*: any provenance is obtained by evaluating a homomorphism $\mathbb{N}[X]\to K$.

Recursion needs least fixpoints, hence **$\omega$-continuous / naturally ordered semirings** and **formal power series**:

$$\llbracket P \rrbracket = \mathrm{lfp}\big(T_P\big) \in K\langle\langle X \rangle\rangle,$$

where $T_P$ is the immediate-consequence operator. Finiteness is recovered in **$\omega$-continuous semirings** and, crucially, in **absorptive / $0$-closed** semirings where $a + a\cdot b = a$ (e.g., the tropical/access-control semirings $\mathrm{Trio}$, $\mathrm{Sorp}_k$), so the infinite series collapses to a finite value. Aggregation is handled by **semimodules** $(K,M)$ where a commutative monoid $M$ of values carries a $K$-action (Amsterdamer–Deutsch–Tannen, PODS 2011), giving the algebra of *aggregate provenance*. Connections: Kleene algebras, weighted automata, shortest paths via the tropical semiring.

## 3. State of the Art (SOTA)

- **Green–Karvounarakis–Tannen (PODS 2007)**: the foundational $K$-relations / provenance-polynomial framework. Tight for positive RA.
- **Green–Ives–Tannen, ORCHESTRA / ProQL**: systems realizing semiring provenance.
- **Foster–Green–Tannen and Karvounarakis–Green**: provenance for Datalog via **infinite power series** and convergence in $\omega$-continuous semirings.
- **Amsterdamer–Deutsch–Tannen (PODS 2011)**: provenance for **aggregate** queries via semimodules; the recognized SOTA for aggregation.
- **Deutch–Milo–Tannen, Senellart et al. (ProvSQL, VLDB 2017)**: practical provenance capture (incl. probabilistic) inside PostgreSQL; **ProvSQL** is the systems-SOTA.
- **Ramusat–Maniu–Senellart**: provenance circuits and *semiring shortest-path* abstractions for recursive/graph queries.

## 4. Upper Bound

- **Positive RA / non-recursive Datalog over polynomial semiring**: provenance computable in **PTIME data complexity** as a polynomial (or as a **provenance circuit** of polynomial size — Deutch–Milo–Roy–Tannen).
- **Recursive Datalog over absorptive / finitely-generated $\omega$-continuous semirings**: least fixpoint converges in finitely many steps; computable in **PTIME** data complexity (e.g., tropical/why/trust). For the security and Boolean semirings, provenance = standard Datalog cost, **PTIME**-complete.
- **Aggregation**: semimodule provenance computable compositionally; size can grow with grouping but stays polynomial per output for the standard semirings. Model: $K$-annotated finite instances with effective semiring operations.

## 5. Lower Bound

- Over the general **provenance-polynomial / power-series** semiring $\mathbb{N}[[X]]$, recursive provenance is **not finitely representable**: a single output tuple's full provenance is an infinite series, so any exact finite output is **impossible** without an absorptive/idempotent collapse (information-theoretic obstruction).
- For **counting** ($\mathbb{N}$) semiring with recursion, exact provenance encodes **#derivations**, which is **#P-hard** in general (counting paths/derivation trees).
- Datalog evaluation itself is **PTIME-complete** (data), a lower bound inherited by any faithful provenance computation.

## 6. The Gap

The positive-RA and *absorptive-recursion* corners are **closed**: provenance is well-defined and PTIME. The open frontier is **non-absorptive recursive provenance** (full counting/polynomial semirings), where exact provenance is infinite or #P-hard — there is no finite, faithful, polynomial representation, only truncations, $k$-bounded ($\mathrm{Sorp}_k$) approximations, or circuit encodings whose *size–faithfulness* trade-off is not fully characterized. Aggregation $\times$ recursion (recursive aggregates, e.g. shortest-path Datalog with SUM) lacks a complete compositional theory. Hence *partially-solved*.

## 7. Current Research (as of June 2026)

- **Senellart, Ramusat, Maniu**: a unifying view of provenance for recursive queries via **semiring shortest-path / fixpoint algorithms**, with practical convergence bounds. *(frontier — verify)*
- **Tannen, Deutch, Khamis–Ngo–Pichler–Suciu**: connections between provenance, **FAQ/semiring aggregation**, and worst-case-optimal evaluation.
- **Khamis, Ngo, Rudra et al.**: semiring-based query evaluation (FAQ, AJAR) blurring the line between provenance and aggregation.
- ProvSQL extensions to recursion and probabilistic/where-provenance.

## 8. Future Work

- A complete, **finite** provenance theory for **recursive aggregate** queries (recursive SUM/MIN with stratification).
- Characterizing semirings where recursive provenance is **finitely representable** vs. provably not.
- **Approximate provenance** with formal error/size guarantees ($k$-absorptive, sketched).
- Scalable provenance circuits for graph/Datalog workloads in real engines.

## 9. Key References

- **[Foundational]** Green, T.J., Karvounarakis, G., Tannen, V. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Foundational]** Amsterdamer, Y., Deutch, D., Tannen, V. *Provenance for Aggregate Queries.* PODS, 2011. — [arXiv](https://arxiv.org/abs/1101.1110)
- **[SOTA]** Karvounarakis, G., Green, T.J. *Semiring-Annotated Data: Queries and Provenance.* SIGMOD Record, 2012. — [DOI](https://doi.org/10.1145/2380776.2380778)
- **[SOTA]** Senellart, P., Jachiet, L., Maniu, S., Ramusat, Y. *ProvSQL: Provenance and Probability Management in PostgreSQL.* PVLDB, 2018. — [DOI](https://doi.org/10.14778/3229863.3236253)
- **[SOTA]** Ramusat, Y., Maniu, S., Senellart, P. *Provenance-Based Algorithms for Rich Queries over Graph Databases.* EDBT, 2021. — [HAL](https://inria.hal.science/hal-03140067)
- **[Survey]** Green, T.J., Tannen, V. *The Semiring Framework for Database Provenance.* PODS (tutorial), 2017. — [DOI](https://doi.org/10.1145/3034786.3056125)

## 10. Worked Example

Take a graph $\text{Edge}(x,y)$ with two base tuples, annotated by provenance tokens $a,b$:
$$\text{Edge}: \quad (1,2)\mapsto a,\qquad (2,1)\mapsto b.$$
Compute transitive closure $\text{Path}$ via $\text{Path}(x,y) \leftarrow \text{Edge}(x,y)$; $\text{Path}(x,z)\leftarrow \text{Path}(x,y),\text{Edge}(y,z)$.

In the **counting semiring** $\mathbb{N}$, the 2-cycle gives infinitely many derivations of $\text{Path}(1,2)$: $a,\ aba,\ ababa,\dots$, so its provenance is the divergent series $a + a^2b + a^3b^2 + \cdots$ — **not finitely representable** (section 5).

In the **absorptive tropical semiring** (min-plus, where $a + ab = a$), each token has a cost; the least-fixpoint *collapses*. With costs $a=1, b=1$, the shortest derivation of $\text{Path}(1,2)$ is the direct edge, cost $1$; longer cyclic derivations are absorbed since $1 \le 1+1+1$. The fixpoint stabilizes after one round: $\{\text{Path}(1,2)=1,\ \text{Path}(2,1)=1,\ \text{Path}(1,1)=2,\ \text{Path}(2,2)=2\}$, computed in PTIME. This contrast — divergence in $\mathbb{N}$ vs. finite convergence under absorption — is exactly the boundary in section 6.

---
*Part of the [DBMS Research catalog](../../README.md).*
