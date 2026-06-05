# A semantics-complete algebra for windowing

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/windowing-semantics-algebra` · **Status:** open

## 1. Problem Statement

Streaming systems offer many window kinds — **tumbling**, **sliding**, **session**, **landmark**, **count-based**, **data-driven**, **punctuation-delimited**, and arbitrary user-defined windows — yet there is no single algebra in which all of these are *first-class operators* with **sound, complete, and compositional** rewrite rules. The problem: define a windowing algebra $\mathcal{W}$ such that

1. **(Expressiveness/completeness)** every "reasonable" window assignment is expressible as a composition of a small set of primitives;
2. **(Soundness)** algebraic rewrite rules (e.g., window/filter commutation, window fusion, slice-and-dice) preserve denotational equivalence under a fixed time/event model;
3. **(Compositionality)** windows can be *nested* and *composed* (window-over-window, co-windowing of joins) with well-defined semantics.

This has a **decision** flavor (given two window expressions, are they equivalent? — likely undecidable in full generality), an **optimization** flavor (find an equivalent expression minimizing state/latency), and a **definitional** flavor (what is the right denotational model at all?).

## 2. Mathematical Foundations

Model a stream as a (possibly infinite) multiset of **time-tagged tuples** $(e, t_e, t_p)$ with event-time $t_e$ and processing-time $t_p$. A **windowing function** assigns each element to a set of window identifiers; following the Dataflow/Beam model a window is a function `AssignWindows : Element → Set⟨Window⟩` plus a `MergeWindows` operation (for sessions) and a `Trigger` controlling materialization. Denotationally a continuous query is a function from streams to **time-varying relations** (TVRs); Streaming SQL (the SQL:2023 / "one SQL" line) formalizes this via the **stream↔relation** duality of CQL: `S2R` (stream-to-relation, i.e. windowing), `R2R` (relational algebra), `R2S` (relation-to-stream: `Istream`/`Dstream`/`Rstream`).

Key formal objects: the **TVR** $R : \text{Time} \to \text{Relation}$; **window assignment** as a relation $W \subseteq \text{Element} \times \text{WindowId}$; and equivalence $Q_1 \equiv Q_2$ iff they induce equal TVRs for all input streams. Soundness of rewrites is proved in this denotational semantics; a *complete* axiomatization would mirror Codd's completeness for relational algebra but is **not known** for windows. Session-window merging gives the algebra a **lattice/union-find** flavor absent from tumbling/sliding.

## 3. State of the Art (SOTA)

- **CQL** (Arasu, Babu, Widom; VLDB Journal 2006): the foundational stream-relation algebra; sound but its window operators are limited (time/tuple-based sliding) and it lacks sessions and merging windows.
- **The Dataflow Model** (Akidau et al., VLDB 2015) and **Beam**: a *practical* decomposition into `AssignWindows`/`MergeWindows`/`Trigger`/`Accumulation` that covers tumbling/sliding/session/custom — but it is an operational specification, not an algebra with a proved-complete rewrite system.
- **Streaming SQL standardization** (Begoli, Hueske, Hyde, et al.; SIGMOD 2019 "One SQL to Rule Them All") and SQL:2023 windowing — aligns vendors (Flink, Calcite, ksqlDB) on TVR semantics.
- **Apache Calcite / "Stream Window Functions"**: rewrite rules exist but are an engineering rule set, not proven complete.

## 4. Upper Bound

There is no complexity "upper bound" in the usual sense; the constructive state of the art is: the Dataflow primitives plus CQL's S2R/R2S can *express* all production window kinds, and Calcite-style rule application *terminates* with cost-based search. For the **slicing** optimization (decomposing overlapping sliding windows into disjoint slices shared across queries — Krishnamurthy et al.; Pane/Stream Slicing, Traub et al. ICDE 2018), state cost can be reduced from $O(\text{overlap})$ to $O(1)$ amortized per slice, giving an effective upper bound on shared-window maintenance.

## 5. Lower Bound

Full **equivalence is expected to be undecidable**: even non-streaming conjunctive-query equivalence over time with arithmetic comparisons reaches into undecidable fragments, and adding session-merge (a transitive-closure-like operation) pushes expressiveness beyond first-order. No clean hardness theorem pins the windowing algebra specifically; informally, equivalence of window expressions with user-defined merge predicates is at least as hard as equivalence of programs computing the merge, hence undecidable. For restricted fragments (fixed tumbling/sliding, no UDF), equivalence is decidable but its precise complexity (likely PSPACE/coNP-hard via containment) is **open**.

## 6. The Gap

The gap is **definitional and foundational**, not numeric: we have (a) a sound operational model (Dataflow) and (b) a sound but incomplete algebra (CQL), but **no proved-complete, compositional algebra** with a decidable equational theory over a useful fragment. Closing it requires (i) identifying a primitive set provably generating all window assignments, (ii) a confluent terminating rewrite system, and (iii) a decidability boundary separating tractable fragments from undecidable (UDF-merge) ones.

## 7. Current Research (as of June 2026)

Lines of work: **stream slicing & general window aggregation sharing** (Traub, Grulich, Markl at TU Berlin); **TVR-based Streaming SQL semantics** (Hyde/Calcite community, Flink SQL team); and **differential/incremental foundations** via **DBSP** (Budiu et al., VLDB 2023) which gives a circuit algebra where windows are stream operators with formally verified incrementalization — arguably the closest current candidate for a semantics-complete substrate *(frontier — verify)*. Type-theoretic / category-theoretic treatments of temporal streams (FRP, "temporal type theory") are being connected to windowing *(frontier — verify)*.

## 8. Future Work

- A completeness theorem (à la Codd) for a window primitive set.
- Decidability map of equivalence/containment across window fragments.
- Compositional semantics for **windows over joins** and nested windows with retractions.
- Bridging Dataflow's `Trigger`/`Accumulation` (materialization policy) into the *denotational* algebra rather than treating it as orthogonal.

## 9. Key References

- **[Foundational]** Arvind Arasu, Shivnath Babu, Jennifer Widom. *The CQL Continuous Query Language: Semantic Foundations and Query Execution.* VLDB Journal, 2006.
- **[Foundational/SOTA]** Tyler Akidau et al. *The Dataflow Model.* PVLDB, 2015.
- **[SOTA]** Edmon Begoli, Tyler Akidau, Fabian Hueske, Julian Hyde, et al. *One SQL to Rule Them All.* SIGMOD, 2019.
- **[SOTA]** Jonas Traub et al. *Efficient Window Aggregation with General Stream Slicing.* ICDE/EDBT, 2018.
- **[SOTA]** Mihai Budiu et al. *DBSP: Automatic Incremental View Maintenance for Rich Query Languages.* PVLDB, 2023.

---
*Part of the [DBMS Research catalog](../../README.md).*
