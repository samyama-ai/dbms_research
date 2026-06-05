# Expressiveness of Window and Streaming Query Languages

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/streaming-language-expressiveness` · **Status:** open

## 1. Problem Statement
Stream query languages (CQL, Flink SQL, KSQL, Esper EPL, Materialize SQL) extend relational and temporal logics with *windows* (tumbling, sliding, session, count-based), *punctuations*, and *continuous* (standing) queries over potentially infinite, ordered, possibly out-of-order data streams. The central problem is to **formalize the semantics of these constructs and characterize their relative expressive power**, both against each other and against classical yardsticks (first-order logic FO, fixpoint logics, temporal logics LTL/MSO, relational algebra).

Variants:
- **Expressiveness (separation):** Given two stream languages $L_1, L_2$, is $L_1 \subsetneq L_2$, $L_1 = L_2$, or are they incomparable, over the class of stream transductions they define?
- **Window primitivity:** Are sliding windows definable from tumbling windows + aggregation, or do they add power? Is a count-window expressible without an order predicate?
- **Continuous vs. snapshot:** Does the continuous (monotone, incremental) restriction reduce expressive power relative to one-shot evaluation on each prefix?
- **Decision problems:** equivalence and containment of two continuous queries; monotonicity/safety; bounded-memory realizability.

## 2. Mathematical Foundations
Model a stream as an infinite word $s = a_0 a_1 \cdots$ over a (typically infinite) data alphabet with timestamps $t_i \in \mathbb{T}$, $t_i \le t_{i+1}$ (in-order) or arbitrary with a watermark/skew bound (out-of-order). A continuous query is a **stream transduction** $f: \Sigma^\omega \to \Gamma^\omega$ or, in the relational-stream view (Arasu–Babu–Widom CQL), a pair of mappings: *stream-to-relation* (windows producing time-varying relations $R(\tau)$), *relation-to-relation* (relational algebra on snapshots), and *relation-to-stream* (Istream/Dstream/Rstream).

Key foundations:
- **Register/data automata** and **streaming string transducers (SST)** (Alur–Černý) give the regular yardstick for bounded-memory transductions; MSO-definable string transductions equal copyless SSTs.
- **Bounded-memory computability:** a continuous query is bounded-memory iff its needed synopsis is finite for all streams — characterized for conjunctive queries by Arasu et al. and tied to constant-state register automata.
- **Temporal/metric logics:** Metric Temporal Logic (MTL) and Metric First-Order Temporal Logic (MFOTL) underpin runtime-monitoring expressiveness; window aggregation relates to MSO with counting.
- **Monotonicity & CALM:** the CALM theorem (Hellerstein–Ameloot) ties coordination-free (eventually consistent) computability to *monotone* queries; monotonicity bounds what continuous, coordination-free stream programs can express.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** CQL's three-mapping semantics (Arasu–Babu–Widom, VLDBJ 2006) remains the reference relational-stream semantics. SECRET (Botan et al., VLDB 2010) gives an operational model unifying window semantics across systems. Streaming SST/data-word transducer theory (Alur et al.) is the cleanest bounded-memory expressiveness result. *Differential dataflow* / *Materialize* provides a denotational incremental semantics (timely dataflow, partially-ordered timestamps) due to McSherry et al.
- **Systems-SOTA:** Apache Flink and the SQL standard's **MATCH_RECOGNIZE** row-pattern matching (SQL:2016) extend stream SQL toward $\omega$-regular pattern detection; Beam's unified batch/stream model formalizes windowing+triggers+watermarks (Akidau et al., "The Dataflow Model," VLDB 2015).

## 4. Upper Bound
For the **bounded-memory fragment** (conjunctive continuous queries over windows with finite synopsis), evaluation is in constant state per element and $O(1)$ amortized time, realizable by register automata. MSO-definable stream transductions are exactly the copyless-SST-computable ones, giving linear-time single-pass evaluation with state polynomial in the formula. Window+aggregation over sliding windows admits $O(1)$ amortized updates via the **two-stacks / DABA** algorithms (Tangwongsan, Hirzel, Schneider) for invertible and non-invertible associative aggregates.

## 5. Lower Bound
Many natural continuous queries are **not bounded-memory**: any query requiring unbounded distinct-count or join state over an unbounded window needs $\Omega(n)$ space (communication-complexity / streaming lower bounds, e.g. DISTINCT elements requires $\Omega(\log n)$ even approximately, set-disjointness gives $\Omega(n)$ for exact joins). Equivalence/containment of continuous conjunctive queries with windows is at least as hard as relational query containment (**NP-hard**; undecidable once recursion or arithmetic on timestamps enters). Out-of-order processing with bounded skew that must produce in-order output forces buffering proportional to skew — an information-theoretic lower bound.

## 6. The Gap
There is **no agreed canonical expressiveness hierarchy** placing sliding/session windows, punctuation, and Istream/Dstream relative to FO, FO+counting, and MSO over data words. Whether session windows add power over tumbling+sliding, and a tight separation between continuous (monotone) and snapshot semantics, are open. The gap is genuinely open: we lack both a unifying logic capturing industrial stream SQL (windows + triggers + retractions) and matching separation theorems.

## 7. Current Research (as of June 2026)
- Logical foundations of *retractions/diffs* in incremental view maintenance and differential dataflow (Z-sets), connecting to the **DBSP** calculus (Budiu et al.) and its completeness for incremental relational computation *(frontier — verify the exact expressiveness completeness claims for DBSP)*.
- Expressiveness of **MATCH_RECOGNIZE** vs. $\omega$-regular and data-word automata; complex-event-processing logic (Grez–Riveros, "CORE" / a formal CEP language, PODS/ICDT 2020s).
- Coordination-freeness and CALM extended to streaming dataflows; consistency-aware windowing.

## 8. Future Work
- A robust *Codd-style theorem* for streams: a logic provably equivalent to bounded-memory continuous queries.
- Decidability frontier for equivalence/containment of windowed queries with arithmetic timestamps and watermarks.
- Compositional semantics unifying batch and stream (Beam/Flink) with provable expressiveness, and a separation theory for triggers and lateness.

## 9. Key References
- **[Foundational]** A. Arasu, S. Babu, J. Widom. *The CQL Continuous Query Language: Semantic Foundations and Query Execution.* VLDB Journal, 2006. — [DOI](https://doi.org/10.1007/s00778-004-0147-z)
- **[Foundational]** R. Alur, P. Černý. *Streaming Transducers for Algorithmic Verification of Single-Pass List-Processing Programs.* POPL, 2011. — [DOI](https://doi.org/10.1145/1926385.1926454)
- **[SOTA]** T. Akidau et al. *The Dataflow Model: A Practical Approach to Balancing Correctness, Latency, and Cost in Massive-Scale, Unbounded, Out-of-Order Data Processing.* VLDB, 2015. — [DOI](https://doi.org/10.14778/2824032.2824076)
- **[SOTA]** I. Botan et al. *SECRET: A Model for Analysis of the Execution Semantics of Stream Processing Systems.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920874)
- **[SOTA]** A. Grez, C. Riveros, M. Ugarte. *A Formal Framework for Complex Event Processing.* ICDT, 2019. — [DOI](https://doi.org/10.4230/LIPIcs.ICDT.2019.5)
- **[SOTA]** M. Budiu, F. McSherry, L. Ryzhyk, V. Tannen. *DBSP: Automatic Incremental View Maintenance for Rich Query Languages.* VLDB, 2023. — [arXiv](https://arxiv.org/abs/2203.16684) · [DOI](https://doi.org/10.14778/3587136.3587137)

## 10. Worked Example

Consider a stream of (timestamp, value) tuples arriving in-order:

$$ (1,5),\;(2,3),\;(3,8),\;(4,1),\;(5,6) $$

Run a **count-based sliding window** of size $w=3$ computing `SUM` (a CQL stream-to-relation window, then relation-to-relation aggregation, then Rstream output):

| at $t$ | window contents | SUM |
|--------|-----------------|-----|
| 3 | $5,3,8$ | 16 |
| 4 | $3,8,1$ | 12 |
| 5 | $8,1,6$ | 15 |

**Bounded memory?** `SUM` is an *invertible* associative aggregate ($g^{-1}$ exists: subtract the expiring element). So each step costs $O(1)$ amortized: on advancing from $t{=}3$ to $t{=}4$, $16 - 5 + 1 = 12$ — subtract the departed $5$, add the new $1$. State is just the window buffer of size $w{=}3$ plus a running sum: $O(w)$, **constant in stream length** $n$. This is the bounded-memory fragment the topic's upper bound names.

Contrast `COUNT(DISTINCT value)` over an *unbounded* (landmark) window: distinctness needs the full set seen so far, $\Omega(n)$ space, and even approximate distinct-count needs $\Omega(\log n)$ (a streaming/communication lower bound). The expressiveness question this illustrates: **which window+aggregate combinations stay in constant state** — the boundary between $O(1)$ register-automaton-realizable queries and those provably requiring unbounded synopsis.

---
*Part of the [DBMS Research catalog](../../README.md).*
