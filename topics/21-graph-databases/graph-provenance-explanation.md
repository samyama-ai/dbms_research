# Provenance and explanation for graph queries

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/graph-provenance-explanation` · **Status:** open

## 1. Problem Statement
Given an annotated property graph $G$ and a query $Q$ (a conjunctive pattern, a regular-path query, or a navigational graph pattern), and a tuple/path $t$ in the answer $Q(G)$, compute **why** $t$ is an answer. Concretely, we want: (i) the *why-provenance* — the set of minimal witnesses (subsets of edges/vertices whose presence suffices to derive $t$); (ii) *how-provenance* — the algebraic combination (alternative derivations and joins) that produced $t$; and (iii) a *minimal explanation* — a smallest (or otherwise optimal) sub-structure of $G$ that still yields $t$, possibly subject to user-supplied cost weights on annotations.

Variants:
- **Computation variant:** materialize the provenance polynomial / witness set for one or all answers.
- **Decision variant:** does a witness of size $\le k$ exist? (relevant for minimal explanations).
- **Counting variant:** how many distinct witnesses / derivations does $t$ have? (e.g., number of simple paths realizing a regular-path-query answer).
- **Why-not variant:** explain the *absence* of an expected answer via the smallest edit (edge insertion/relabeling) that would produce it.

The difficulty over plain relational provenance is **recursion and path semantics**: RPQ answers under simple-path semantics induce counting/enumeration problems that are intractable even when the answer set is small.

## 2. Mathematical Foundations
Provenance is formalized via **commutative semirings** (Green–Karvounarakis–Tannen, PODS 2007). Each base edge $e$ carries an annotation $x_e$ from a semiring $(K,+,\cdot,0,1)$; the provenance of an answer is a polynomial in $\mathbb{N}[X]$, with $\cdot$ for joint use (joins) and $+$ for alternative derivations (unions). Specializations: the boolean semiring (which-provenance), the *why*-semiring $(\mathbb{N}^{\mathbb{N}^X},\ldots)$, the trio semiring (bag), the tropical semiring $(\min,+)$ for shortest-witness cost.

For navigational queries, provenance must extend to **transitive closure / Kleene star**, requiring $\omega$-continuous or *closed* semirings so that $a^* = \sum_{i\ge 0} a^i$ is well-defined; path provenance is then the star of a transition matrix over $K$ (a generalized algebraic-path / Floyd–Warshall computation).

Key hardness levers: counting simple paths is $\\#P$-complete; finding a minimum-weight witness reduces to weighted set-cover (hence $\Theta(\log n)$-inapproximable unless $\mathrm{P}=\mathrm{NP}$). Minimal-explanation enumeration ties to the theory of *minimal hypergraph transversals* (output-polynomial via quasi-polynomial Fredman–Khachiyan).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** semiring provenance for Datalog/recursion (Green et al.; Deutch–Milo–Roy–Tannen *circuits for Datalog provenance*, ICDT 2014) gives provenance circuits of polynomial size for fixed programs, and absorptive/semimodule semirings for RPQs.
- **Systems-SOTA:** ProvSQL (Senellart et al., VLDB 2018) attaches semiring circuits to PostgreSQL; GProM (Arab et al.) does provenance for SQL incl. some recursion; Memgraph/Neo4j expose `shortestPath`/path enumeration but no principled provenance layer. Graph-specific: PReDS and the *PathFinder*-style provenance for RPQs (Ramusat–Maniu–Senellart, EDBT/ICDE 2018–2021) compute provenance of regular path queries over annotated graphs using semiring matrix closure and message-passing approximations.
- **Why-not / explanations:** edit-based and ML-attribution explanations for GNN-backed query answering are an active, separate line.

## 4. Upper Bound
For fixed conjunctive (non-recursive) graph patterns, why/how-provenance is computable in time polynomial in $|G|$ and in the (data-complexity) size of the provenance circuit. For RPQ provenance over an $\omega$-continuous semiring, Ramusat et al. give $O(n^3)$-style algebraic-closure algorithms (semiring Floyd–Warshall) and near-linear approximations for *absorptive* / tropical semirings via Dijkstra-like relaxation. Minimal single witness for an answer: polynomial. Minimum-weight witness: $O(\log n)$-approximation via greedy set cover.

## 5. Lower Bound
- Counting derivations/witnesses for RPQs under simple-path semantics is **$\\#P$-complete** (reduction from counting simple paths; Mendelzon–Wood, SIAM J. Comput. 1995 for the underlying simple-path RPQ hardness).
- Minimum-weight / minimum-size explanation is **NP-hard** and $(1-o(1))\ln n$-inapproximable (set-cover hardness, Dinur–Steurer 2014).
- Enumerating all minimal witnesses with polynomial delay is at least as hard as hypergraph dualization, for which no polynomial algorithm is known (only quasi-polynomial total time).

## 6. The Gap
For non-recursive patterns the gap is essentially closed (poly upper, matching circuit lower bounds). The genuine open gaps are: (a) **recursive/path provenance with simple-path semantics** — the $\\#P$ wall versus practically useful approximations with *guarantees*; (b) **minimal explanations** — closing the dualization gap (poly-delay vs quasi-poly) for graph-shaped witness hypergraphs; (c) a **unified semiring** that simultaneously captures bag-semantics, cost, and security/access annotations for navigational queries without exponential blow-up.

## 7. Current Research (as of June 2026)
Active threads: provenance for *property-graph* algebras and GQL/SQL-PGQ (Senellart's group at ENS/IPParis; the ProvSQL line); approximate semiring provenance with sampling-based error bounds for RPQs *(frontier — verify)*; provenance-aware differential dataflow and incremental maintenance (Milo, Deutch at Tel Aviv); connecting provenance to *responsibility/causality* and Shapley-value explanations over databases (Bertossi, Livshits, Kimelfeld) — extending Shapley-value computation to path answers is an open frontier *(frontier — verify)*. GQL standardization (ISO/IEC 39075, 2024) is renewing interest in a standard provenance semantics for the path-pattern algebra *(frontier — verify)*.

## 8. Future Work
- Tractable islands: characterize pattern/semiring pairs where minimal-explanation enumeration is output-polynomial.
- Approximation with formal error guarantees for $\\#P$-hard witness counting on huge graphs.
- Provenance for *negation* and aggregation in graph queries (semimodules, $m$-semirings).
- Interactive, cost-aware "smallest sufficient explanation" UIs, and why-not via minimum graph edits.
- Standardizing provenance into GQL/SQL-PGQ semantics.

## 9. Key References
- **[Foundational]** Green, Karvounarakis, Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Foundational]** Mendelzon, Wood. *Finding Regular Simple Paths in Graph Databases.* SIAM J. Comput., 1995. — [DOI](https://doi.org/10.1137/S009753979122370X)
- **[SOTA]** Ramusat, Maniu, Senellart. *Provenance-Based Algorithms for Rich Queries over Graph Databases* (and earlier *Semiring Provenance over Graph Databases*). EDBT / ICDE, 2018–2021. — [DOI](https://doi.org/10.5441/002/edbt.2021.08)
- **[SOTA]** Senellart, Jachiet, Maniu, Ramusat. *ProvSQL: Provenance and Probability Management in PostgreSQL.* VLDB, 2018. — [DOI](https://doi.org/10.14778/3229863.3236253)
- **[SOTA]** Deutch, Milo, Roy, Tannen. *Circuits for Datalog Provenance.* ICDT, 2014. — [DOI](https://doi.org/10.5441/002/icdt.2014.22)
- **[Survey]** Cheney, Chiticariu, Tan. *Provenance in Databases: Why, How, and Where.* Foundations and Trends in Databases, 2009. — [DOI](https://doi.org/10.1561/1900000006)

## 10. Worked Example

**How-provenance of an RPQ answer.** Take a tiny graph with edges annotated by semiring variables:
$$a \xrightarrow{\;x_1\;} b,\quad b \xrightarrow{\;x_2\;} d,\quad a \xrightarrow{\;x_3\;} c,\quad c \xrightarrow{\;x_4\;} d.$$
Query $Q$: is there a path from $a$ to $d$ of length 2? In the provenance semiring $\mathbb{N}[X]$, join (sequential edges) uses $\cdot$ and alternative derivations use $+$. Two distinct 2-hop witnesses exist — $a\!\to\!b\!\to\!d$ and $a\!\to\!c\!\to\!d$ — so the how-provenance polynomial of the answer is
$$x_1 x_2 \;+\; x_3 x_4.$$
Each monomial is a **why-witness** (a minimal edge set sufficing to derive the answer): $\{x_1,x_2\}$ and $\{x_3,x_4\}$.

**Tropical specialization for shortest witness.** Interpret the same expression over the tropical semiring $(\min,+)$ with edge costs $x_1{=}5,x_2{=}1,x_3{=}2,x_4{=}2$. Then $\cdot\mapsto+$ and $+\mapsto\min$, giving $\min(5{+}1,\;2{+}2)=\min(6,4)=4$ — the cheapest explanation is $\{x_3,x_4\}$. Counting witnesses (here 2) becomes $\\#P$-complete once paths must be *simple* and the graph is large.

---
*Part of the [DBMS Research catalog](../../README.md).*
