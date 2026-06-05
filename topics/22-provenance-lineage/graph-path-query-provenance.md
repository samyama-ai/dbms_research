# How-Provenance for Graph/Path Queries

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/graph-path-query-provenance` · **Status:** open

## 1. Problem Statement

Graph query languages (Cypher, SPARQL property paths, GQL, regular path queries) answer questions of the form "is there a path from $x$ to $y$ matching regular expression $r$?" The natural how-provenance of such an answer should record *which* edges, in *what* combinations, witness the connection. But in a cyclic graph the set of matching paths is **infinite** (a loop can be traversed arbitrarily many times), so the provenance polynomial has infinitely many monomials. Writing it out is impossible.

The problem: define and compute a **finitely representable, semiring-correct** how-provenance for regular-path queries (RPQs), conjunctive RPQs, and recursive (Datalog/transitive-closure) graph queries — capturing all (infinitely many) derivations exactly, in a closed and computable algebraic form.

Variants:
- **Representation:** What finite object faithfully encodes the (possibly infinite) provenance?
- **Computation (decision/optimization):** Compute it within the complexity of the underlying RPQ evaluation.
- **Counting:** Path/witness counting under provenance semantics (often #P-hard).

## 2. Mathematical Foundations

How-provenance lives in a commutative semiring $K$ (Green–Tannen). For recursion the right setting is **$\omega$-continuous / closed semirings** supporting a star operation
$$a^{*} = \sum_{n\ge 0} a^{n} = 1 + a\cdot a^{*},$$
so infinite sums of derivations converge to a finite element. The provenance of an RPQ is then computed by **algebraic path / Kleene-algebra** methods: the answer is the $(x,y)$ entry of $A^{*}$ where $A$ is the edge-annotation matrix over $K$ (Conway/Lehmann's algorithm; Tarjan's fast path algebra). This is exactly the **algebraic path problem** over a closed semiring.

For provenance to be *finitely representable*, $K$ must be **absorptive** or otherwise tame: the why-provenance / **PosBool**, the **tropical (min-plus)** semirings, and **$\mathbb{N}^\infty$** admit finite $a^*$, whereas the free polynomial semiring $\mathbb{N}[X]$ does **not** ($x^* = 1+x+x^2+\dots$ has no finite normal form). The correct object is therefore a **provenance regular expression / circuit with a star operator** (a system of fixpoint equations), or provenance computed in the semiring of **rational power series** recognized by weighted automata (Schützenberger). Correctness = the representation denotes the same semiring element as the (infinite) sum over all paths.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Provenance for recursive Datalog over **$\omega$-continuous semirings** (Green; Deutch, Milo, Roy, Tannen — "Circuits for Datalog Provenance", ICDT 2014) gives finite **provenance circuits** with fixpoints. Ramusat, Maniu, Senellart formalize **provenance for regular path queries** via the algebraic path problem over absorptive/star semirings (ICDT/EDBT 2018–2021), with efficient $K$-relation matrix algorithms.
- **Systems-SOTA:** **ProvSQL** (Senellart et al.) handles semiring provenance and is being extended toward recursion; graph engines (Neo4j, RDF stores) expose path bindings but **no** general semiring-correct provenance; weighted-automata / semiring matrix libraries (e.g. generalized Floyd–Warshall) implement the path-algebra core.

## 4. Upper Bound

Over a **closed/absorptive** semiring, RPQ provenance is the algebraic path problem: computable in $O(n^3)$ semiring operations via Conway/Lehmann (Floyd–Warshall-style) on the $n$-node product graph, or faster with Tarjan's path-expression algorithm in near-$O(m\,\alpha(m,n))$ for sparse/reducible structure, yielding a finite provenance regular expression. RPQ evaluation itself is **NL-complete** (PTIME data complexity); provenance computation stays in **PTIME data complexity** over semirings with PTIME star. For Datalog, provenance circuits are PTIME-constructible over $\omega$-continuous semirings (Deutch et al.).

## 5. Lower Bound

RPQ evaluation is **NL-complete** in combined complexity (and reachability is NL-hard), so any provenance method inherits NL-hardness. **Counting** paths/witnesses is **#P-hard** (counting simple paths is #P-complete), so provenance in counting semirings has no efficient exact representation unless $\mathsf{FP}=\\#\mathsf{P}$. Over the **free polynomial semiring $\mathbb{N}[X]$**, finite representation is *impossible* — $x^*$ has no finite normal form — an algebraic impossibility independent of complexity assumptions; recursion fundamentally requires moving to a closed/absorptive semiring. For **conjunctive RPQs**, evaluation is NP-complete (combined), bounding provenance computation. Simple-path semantics (Cypher's historical default) makes even decision **NP-hard**, so faithful simple-path provenance is intractable.

## 6. The Gap

The picture splits cleanly. For **absorptive/closed** semirings, the algebraic-path approach gives finite, semiring-correct provenance in PTIME data complexity — close to closed. The genuine **open** gaps: (1) for **non-absorptive** semirings (full $\mathbb{N}[X]$ counting derivations), finite representation is impossible, so the open question is *what finite surrogate* (rational series, circuit, bounded-multiplicity approximation) is both useful and provably faithful; (2) **conjunctive/recursive** RPQ provenance under different path semantics (arbitrary vs. trail vs. simple path — newly relevant for GQL/SQL-PGQ standards) lacks a complete complexity map; (3) practical, indexed computation at scale is largely unbuilt. No tight upper/lower characterization exists across the semantics zoo.

## 7. Current Research (as of June 2026)

- Provenance for the **GQL / SQL/PGQ** standard path semantics (walk/trail/simple/acyclic), aligning semiring theory with the new ISO graph-query standards *(frontier — verify)*.
- Ramusat–Maniu–Senellart line on algebraic-path provenance and its semiring complexity; extensions to top-$k$ / shortest-path provenance via tropical semirings.
- Provenance-aware graph engines and ProvSQL recursion support *(frontier — verify)*.
- Weighted-automata / rational-series representations of infinite provenance.

## 8. Future Work

- A complete complexity/representability map across path semantics × semirings.
- Faithful finite surrogates for non-absorptive recursive provenance.
- Indexed, incremental provenance for evolving graphs.
- Provenance for richer recursion (Datalog with aggregation, GQL quantified paths).
- Bridging semiring provenance with the emerging GQL standard.

## 9. Key References

- **[Foundational]** Green, Karvounarakis, Tannen. *Provenance Semirings.* PODS 2007. — [DBLP](https://dblp.org/rec/conf/pods/GreenKT07.html)
- **[Foundational]** Lehmann. *Algebraic Structures for Transitive Closure.* Theoretical Computer Science, 1977 (algebraic path problem / closed semirings). — [DOI](https://doi.org/10.1016/0304-3975(77)90056-1)
- **[Foundational]** Deutch, Milo, Roy, Tannen. *Circuits for Datalog Provenance.* ICDT 2014. — [DBLP](https://dblp.org/rec/conf/icdt/DeutchMRT14.html)
- **[SOTA]** Ramusat, Maniu, Senellart. *Semiring Provenance over Graph Databases.* TaPP 2018 / *Provenance-Based Algorithms for Rich Queries over Graph Databases.* EDBT 2021. — [TaPP](https://www.usenix.org/conference/tapp2018/presentation/ramusat) · [EDBT](https://inria.hal.science/hal-03140067)
- **[Foundational]** Schützenberger. *On the Definition of a Family of Automata.* Information and Control, 1961 (rational power series / weighted automata). — [DOI](https://doi.org/10.1016/S0019-9958(61)80020-X)
- **[Survey]** Barceló. *Querying Graph Databases.* PODS 2013 (regular path queries, complexity). — [DOI](https://doi.org/10.1145/2463664.2465216)

## 10. Worked Example

Consider a 2-node graph with edges annotated by provenance variables: a self-loop on $x$ labeled $a$, and an edge $x \to y$ labeled $b$. Ask the RPQ "reach $y$ from $x$ via $a^*b$" (any number of loops, then the $b$-edge).

The set of witnessing paths is infinite: $b,\ ab,\ aab,\ aaab,\dots$, so the how-provenance in the free polynomial semiring $\mathbb{N}[X]$ is
$$ \sum_{n\ge 0} a^{n} b = (1 + a + a^2 + \cdots)\,b = a^{*}b, $$
which has **no finite normal form** in $\mathbb{N}[X]$ — confirming the impossibility noted in section 5.

Move to a *closed/absorptive* semiring and it becomes finite. Over the tropical (min-plus) semiring with edge weights $a=2,\ b=5$, the star is $a^{*}=\min(0, 2, 4,\dots)=0$, so the answer is $a^{*}\otimes b = 0 + 5 = 5$ — the shortest path. The algebraic-path computation is the $(x,y)$ entry of $A^{*}$ for the $2\times 2$ matrix
$$ A=\begin{pmatrix} a & b \\ \infty & \infty \end{pmatrix}, $$
solvable by Conway/Lehmann in $O(n^3)=O(8)$ semiring ops — a finite, semiring-correct provenance for an infinite path set.

---
*Part of the [DBMS Research catalog](../../README.md).*
