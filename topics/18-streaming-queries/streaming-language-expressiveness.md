# Expressiveness of streaming query languages

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/streaming-language-expressiveness` · **Status:** open

## 1. Problem Statement
Characterize exactly which queries over an unbounded, ordered stream are computable by a *bounded-memory* (or sublinear-memory) streaming language, and how that class relates to relational algebra/calculus, temporal logics (LTL, MSO over $\omega$-words), and register/quantitative automata.

Concretely:
- **Decision (membership):** given a relational/temporal query $Q$, is it expressible as a streaming computation using $O(1)$ (or $o(n)$, or polylog) memory per input prefix while producing the correct output stream?
- **Separation:** exhibit queries provably *not* expressible under a given memory bound (e.g., does a language capture exactly the "monotone" or "weakly-output-bounded" fragment?).
- **Calculus design:** define a language whose expressible queries coincide with a natural semantic class (e.g., all queries with bounded-memory exact evaluation), giving a syntactic characterization à la Codd's theorem for the relational case.

The open challenge is a clean *syntactic = semantic = resource* trichotomy for streams, analogous to (FO = relational algebra) and (Datalog = least fixpoint) in the classical setting.

## 2. Mathematical Foundations
A stream is an (infinite) word over an infinite alphabet (tuples) with an order/time attribute. Two complementary lenses:

1. **Logic/automata over $\omega$-words.** Büchi's theorem: MSO over $\omega$-words = $\omega$-regular = nondeterministic Büchi automata. LTL = star-free / FO over $(\mathbb{N},<)$ (Kamp's theorem). Streaming pattern languages (CEP, match-recognize) correspond to *register automata* / *symbolic automata* over data words, whose emptiness and membership are well-studied (Kaminski–Francez; Bojańczyk; Segoufin).

2. **Data-stream complexity.** A query is *bounded-memory computable* iff some constant-space online algorithm outputs the correct (possibly infinite) answer stream. Arasu, Babcock, Babu et al. and Babcock–Babu–Datar–Motwani–Widom characterized which **CQL/SQL** continuous queries can be evaluated with bounded memory, tied to attribute *boundedness* (whether the set of distinct values an attribute takes is finite/known). The space hierarchy is governed by communication complexity: e.g., exact **DISTINCT** needs $\Omega(n)$ bits (INDEX/DISJOINTNESS reductions), so it is not bounded-memory.

Key quantity: for a query $Q$, $S_Q(n)=$ minimum memory to maintain $Q$ over a prefix of length $n$. The expressiveness question asks for a *language whose syntax bounds $S_Q$*, e.g. captures exactly $S_Q=O(1)$. Quantitative/weighted automata and the algebra of *monoids* (for aggregates) provide the compositional semantics.

## 3. State of the Art (SOTA)
- **Bounded-memory characterization of CQL/SQL queries:** Arasu, Babcock, Babu, et al. (STREAM project) and Babu–Widom give sufficient/necessary conditions (constraint-based; attribute-boundedness) — the closest thing to a decidable membership test, but incomplete in general.
- **Register/symbolic automata** for streaming patterns: Grez, Riveros, Ugarte's **CEL (Complex Event Logic)** and a formal foundation for CEP with well-defined enumeration/expressiveness results (PODS 2019 onward).
- **Differential dataflow / relational streaming semantics**: McSherry et al. give an operational model whose expressiveness equals incrementally maintainable relational+fixpoint queries.
- **Temporal/streaming Datalog and Dedalus/Bloom** (Hellerstein, Alvaro): logic for distributed/streaming computation, with the **CALM theorem** characterizing coordination-free (monotone) queries.
- Systems-SOTA languages: SQL:2016 `MATCH_RECOGNIZE`, Flink SQL, ksqlDB, Materialize SQL, Spark Structured Streaming — pragmatic but lacking a complete expressiveness theory.

## 4. Upper Bound
**CALM theorem** (Hellerstein 2010; Ameloot, Neven, Van den Bussche, PODS 2011/JACM 2013): a query has an eventually-consistent, coordination-free distributed/streaming implementation **iff** it is *monotone*. This is a complete, semantic characterization for the coordination-free fragment. For bounded-memory exact evaluation, *constraint-based* sufficient conditions (Arasu–Babu–Widom) give an upper bound on what is expressible in $O(1)$ space; for $\omega$-regular properties, Büchi automata give the tight automaton-size upper bound.

## 5. Lower Bound
Information-theoretic / communication lower bounds delimit expressiveness: exact DISTINCT, MEDIAN, and unbounded joins require $\Omega(n)$ space (INDEX, DISJOINTNESS) and so are *provably not* bounded-memory streaming queries — separating SQL from any $O(1)$-space language. Non-monotone queries are provably **not** coordination-free (CALM, lower-bound direction). Register-automaton languages over data words have **undecidable** universality/inclusion in general (Kaminski–Francez; Neven–Schwentick–Vianu), bounding how rich a decidable streaming pattern language can be.

## 6. The Gap
There is **no complete, decidable syntactic characterization** of exactly the bounded-memory (or polylog-memory) computable continuous queries: known conditions are sufficient or necessary but not both, and depend on undecidable side-conditions (attribute boundedness, constraint entailment). A Codd-style theorem — "language $\mathcal{L}$ expresses precisely the queries with $S_Q=O(\text{polylog})$" — is open. Closing it requires either a new decidable language design or a proof that no decidable characterization exists.

## 7. Current Research (as of June 2026)
- Foundations of CEP/streaming logics with enumeration and constant-delay output (Riveros, Ugarte, Vansummeren, Bucchi) *(frontier — verify)*.
- Expressiveness/complexity of streaming MATCH_RECOGNIZE and its automata semantics.
- Quantitative/weighted streaming languages and their relation to cost-register automata (Alur et al.).
- Streaming Datalog, recursive streaming, and CALM-style coordination characterizations for stronger consistency models *(frontier — verify)*.

## 8. Future Work
- A decidable language capturing exactly $O(1)$- or polylog-space exact queries (or a proof of impossibility).
- Tight expressiveness/space trade-off hierarchies for approximate streaming queries.
- Unifying temporal-logic, register-automata, and data-stream-complexity views into one semantics.
- Expressiveness of out-of-order/late-event semantics (watermarks) as a logical primitive.

## 9. Key References
- **[Foundational]** Babcock, B., Babu, S., Datar, M., Motwani, R., Widom, J. *Models and Issues in Data Stream Systems.* PODS, 2002. — [DOI](https://doi.org/10.1145/543613.543615)
- **[Foundational]** Arasu, A., Babu, S., Widom, J. *The CQL Continuous Query Language: Semantic Foundations and Query Execution.* VLDB Journal, 2006. — [DOI](https://doi.org/10.1007/s00778-004-0147-z)
- **[Foundational]** Ameloot, T.J., Neven, F., Van den Bussche, J. *Relational Transducers for Declarative Networking (CALM).* JACM, 2013. — [DOI](https://doi.org/10.1145/2450142.2450151)
- **[SOTA]** Grez, A., Riveros, C., Ugarte, M. *A Formal Framework for Complex Event Processing (CEL).* ICDT/PODS, 2019. — [DOI](https://doi.org/10.4230/LIPIcs.ICDT.2019.5)
- **[Foundational]** Kaminski, M., Francez, N. *Finite-Memory Automata.* Theoretical Computer Science, 1994. — [DOI](https://doi.org/10.1016/0304-3975(94)90242-9)
- **[Survey]** Hellerstein, J.M., Alvaro, P. *Keeping CALM: When Distributed Consistency Is Easy.* CACM, 2020. — [DOI](https://doi.org/10.1145/3369736)

## 10. Worked Example

**A query that is *not* bounded-memory, proven by an INDEX reduction.** Consider the continuous query "is the newest element a *duplicate* of some earlier element?" — a 1-bit-per-prefix slice of exact `DISTINCT`. Claim: no $O(1)$-memory (indeed no $o(n)$-memory) streaming algorithm computes it over a universe $[n]$.

Reduction from the INDEX communication problem. Alice holds a set $A\subseteq[n]$ (a bit-vector); Bob holds an index $j\in[n]$ and must learn whether $j\in A$. Alice feeds the elements of $A$ into the stream, then passes the algorithm's memory state to Bob. Bob appends $j$ and queries: the answer "duplicate" is yes iff $j\in A$.

Tiny instance, $n=4$, $A=\{1,3\}$, stream prefix $1,3$. Bob's index $j=3$: appending $3$ makes it a duplicate $\Rightarrow$ "yes, $3\in A$." With $j=2$: appending $2$ is fresh $\Rightarrow$ "no, $2\notin A$."

Since INDEX has one-way communication complexity $\Omega(n)$ bits, the memory state Bob received must carry $\Omega(n)$ bits — so the streaming algorithm uses $\Omega(n)$ space. Hence exact `DISTINCT` lies *outside* any $O(1)$-space streaming language, formally separating full SQL from the bounded-memory fragment (Section 5). Contrast a monotone query like "has value $7$ ever appeared?", which needs a single bit — and, by CALM, is also coordination-free.

---
*Part of the [DBMS Research catalog](../../README.md).*
