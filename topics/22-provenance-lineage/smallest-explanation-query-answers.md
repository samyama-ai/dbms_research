# Smallest-Explanation Query Answers

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/smallest-explanation-query-answers` · **Status:** open

## 1. Problem Statement

Given a database $D$, a query $Q$, and an answer $t \in Q(D)$, an *explanation* under a fixed explanation model is a subset of source tuples (or instantiated rules) that *justifies* $t$. The **smallest-explanation** problem asks for a justification of **minimum size** (cardinality or cost). Intuitively: what is the most concise human-readable reason this answer appears?

Variants:
- **Decision:** is there an explanation of size $\le k$?
- **Optimization:** minimize $|E|$ (or weighted cost) such that $E \subseteq D$ and $t \in Q(E)$ (a *sufficient* / why-provenance witness).
- **Counting:** how many minimal explanations exist?
- **Enumeration:** output minimal explanations in ranked order with polynomial delay.

The explanation model must be fixed in advance: a *minimal witness* (support of a why-provenance monomial), a *minimal model* under a Datalog/rule semantics, or a *minimal sufficient subset* for non-monotone queries.

## 2. Mathematical Foundations

For monotone queries, the **why-provenance** of $t$ is a set of *witnesses* $W \subseteq 2^D$, each $w$ a set of tuples with $t \in Q(w)$. The minimal witnesses form the prime implicants of the monotone Boolean *lineage* formula $\lambda_t = \bigvee_{w} \bigwedge_{r \in w} x_r$. A smallest explanation is a **minimum-weight prime implicant** of $\lambda_t$.

This connects directly to **minimum-cost satisfaction / minimum hitting**. For a CQ, a single witness has size bounded by the number of atoms (constant for fixed $Q$), so for a *single* monomial the minimum is trivial; the hardness arises with (i) *unions/recursion* where exponentially many witnesses compete, and (ii) explanations that must cover *multiple* answers simultaneously, yielding a **minimum set cover** / **red-blue set cover** structure with the classic $\ln n$ inapproximability of Dinur–Steurer. Under semiring semantics, smallest explanation = lowest-degree monomial in the **tropical (min-plus) semiring** evaluation of the provenance polynomial.

$$ \text{cost}(t) = \min_{w \in W(t)} \sum_{r \in w} c(r), \qquad \lambda_t \in \mathbb{N}[X],\ \text{evaluated over } (\mathbb{R}_{\ge 0}\cup\{\infty\}, \min, +). $$

## 3. State of the Art (SOTA)

- **Roy, Suciu (SIGMOD 2014)** — a formal framework for explanations of query results via *intervention* and aggregate outliers, with optimization over predicate space.
- **Wu, Madden (VLDB 2013)** — *Scorpion*: explanations as predicates maximizing influence on aggregate outliers (systems-SOTA for OLAP explanations).
- **Meliou, Gatterbauer, Moore, Suciu (2009–2011)** — causality/responsibility, providing the optimization backbone.
- **Datalog provenance / why-provenance enumeration** (Deutch, Gilad, Moskovitch; *selective provenance*, VLDB 2015) gives ranked, summarized explanations.
- Tropical-semiring shortest-derivation for Datalog (Green et al.; absorptive semirings) gives smallest-derivation directly.

## 4. Upper Bound

For a single CQ answer, a minimal witness is found in **PTIME** (size bounded by atom count). For Datalog, the *minimum-weight derivation tree* is computable by semi-naïve evaluation in the **tropical semiring** in PTIME (polynomial in $|D|$) for the lowest-cost single derivation. For covering many answers, the greedy set-cover algorithm gives an **$H_n = O(\ln n)$ approximation**. Minimum prime implicant for general monotone DNF is solvable in time exponential only in explanation size $k$ — **FPT-style $O^*(c^k)$** bounds apply.

## 5. Lower Bound

Computing a **minimum-size prime implicant** of a monotone Boolean formula is **NP-hard** and, as it generalizes **minimum set cover**, is **$(1-\varepsilon)\ln n$-inapproximable** unless P = NP (Dinur–Steurer 2014). Hence multi-answer / UCQ smallest explanation is NP-hard with a tight logarithmic approximation threshold. Counting minimal explanations is **#P-hard** (it subsumes counting minimal models / DNF prime implicants). For self-join-free CQs single-tuple lineage is tractable, but explanation *minimization across the lineage DNF* hits the set-cover wall.

## 6. The Gap

For single-answer monotone CQ/Datalog the problem is essentially **closed** (PTIME via tropical evaluation). For *aggregate*, *non-monotone*, and *multi-answer* explanations the gap is between the $\ln n$ greedy upper bound and the matching $\ln n$ hardness — **closed up to constants** for the set-cover core, but **open** for richer cost models (e.g., diversity-aware or rule-level explanations) where no tight approximability is known.

## 7. Current Research (as of June 2026)

Active directions: **explanations for ML-over-DB pipelines** and natural-language verbalization of provenance (Deutch's Tel Aviv group), and **explanation summarization** that trades minimality for readability. *(frontier — verify)* Recent work couples smallest-explanation with **LLM-generated rationales** grounded in provenance, and explores **submodular surrogate objectives** to get better-than-greedy bounds for diverse explanations. There is growing interest in *responsibility-ranked* smallest explanations unifying this page with counterfactual responsibility.

## 8. Future Work

- Tight approximability for weighted, diversity-, and coverage-constrained explanations.
- Polynomial-delay enumeration of minimal explanations in ranked order for recursive queries.
- Explanation models for aggregation and negation with provable minimality guarantees.
- Human-in-the-loop evaluation linking "smallest" to "most understandable."

## 9. Key References

- **[Foundational]** Buneman, Khanna, Tan. *Why and Where: A Characterization of Data Provenance.* ICDT, 2001.
- **[SOTA]** Roy, Suciu. *A Formal Approach to Finding Explanations for Database Queries.* SIGMOD, 2014.
- **[SOTA]** Wu, Madden. *Scorpion: Explaining Away Outliers in Aggregate Queries.* VLDB, 2013.
- **[SOTA]** Deutch, Gilad, Moskovitch. *Selective Provenance for Datalog Programs Using Top-K Queries.* VLDB, 2015.
- **[Foundational]** Dinur, Steurer. *Analytical Approach to Parallel Repetition (Set Cover Inapproximability).* STOC, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
