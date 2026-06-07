---
id: 25-query-languages-expressiveness/counting-logic-queries
title: "Querying with Counting and Majority Quantifiers"
topic: 25-query-languages-expressiveness
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Querying with Counting and Majority Quantifiers

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/counting-logic-queries` · **Status:** partially-solved

## 1. Problem Statement

Pure first-order logic (= relational algebra) cannot count: it cannot express "the relation has an even number of tuples," "two relations have equal cardinality," or "more than half satisfy $\varphi$." Practical queries constantly count, aggregate, and compare majorities. The problem is to **determine the expressive power of FO and fixpoint logics extended with counting and majority quantifiers** on concrete query problems:

- **FO+C** (first-order with counting quantifiers $\exists^{\geq i}$), **FO+MAJ** (majority quantifier), and their fixpoint extensions **IFP+C / LFP+C** (inductive/least fixpoint + counting).
- **Decision variant:** which Boolean queries (graph properties, cardinality comparisons) are/aren't expressible?
- **Counting variant:** which *counting functions* (e.g. number of satisfying assignments, #paths) are computable?
- **Capture variant:** does a counting logic *capture* a complexity class (e.g. does IFP+C = PTIME on a class of structures)?

Status **partially-solved**: deep results exist (Cai–Fürer–Immerman; Grohe's capture theorems), but the central question — a logic capturing PTIME in general — remains the major open problem of descriptive complexity.

## 2. Mathematical Foundations

Structures may be two-sorted: a **domain sort** and a **number sort** $\{0,\dots,n\}$ with order and arithmetic. **Counting quantifiers** $\exists^{\geq i} x\,\varphi$ ("at least $i$ elements satisfy $\varphi$") and the **majority quantifier** $\mathrm{Maj}\,x\,\varphi$ ("more than half") extend FO to **FO+C** and **FO+MAJ**.

**Descriptive complexity anchors:**
- **Fagin:** $\exists\mathrm{SO} = \mathrm{NP}$; **Immerman–Vardi:** on *ordered* structures, $\mathrm{LFP} = \mathrm{PTIME}$ and $\mathrm{PFP}=\mathrm{PSPACE}$.
- Counting added: **FO+MAJ captures (uniform) $\mathrm{TC}^0$**; **FO+C** corresponds to FO with counting within $\mathrm{TC}^0$-style classes. **IFP+C** is the canonical candidate logic for PTIME.

**The Cai–Fürer–Immerman (CFI) theorem (1992):** IFP+C does **not** capture PTIME — there are polynomial-time-decidable graph properties (CFI graphs, built to defeat the **Weisfeiler–Leman (WL) algorithm**) not expressible in IFP+C. This ties counting logic to the **WL graph-isomorphism heuristic**: $k$-variable counting logic $\mathrm{C}^k$ has *exactly* the distinguishing power of the $(k{-}1)$-dimensional WL algorithm (Cai–Fürer–Immerman; Immerman–Lander). This equivalence is now central to GNN expressiveness.

**Capture successes (Grohe):** IFP+C **does** capture PTIME on every class of graphs with **excluded minors** (and bounded rank-width), a landmark partial positive answer.

## 3. State of the Art (SOTA)

- **Lower bound on counting logic:** Cai, Fürer, Immerman (*Combinatorica 1992*) — IFP+C $\neq$ PTIME via CFI construction.
- **Capture results:** **Grohe** (*Descriptive Complexity, Canonisation, and Definable Graph Structure Theory*, 2017) — IFP+C captures PTIME on minor-closed classes; the deepest SOTA.
- **$\mathrm{C}^k$ = WL:** Immerman–Lander; recently bridged to **GNN expressiveness** (Morris et al. *AAAI 2019*; Grohe *PODS 2021 keynote*).
- **Rank logic / linear-algebraic operators:** rank logic (Dawar, Grohe, Holm, Laubner) was proposed to beat CFI but was shown **not** to capture PTIME (Lichter, LICS 2021) — a major SOTA negative result.

## 4. Upper Bound

- **FO+C / FO+MAJ:** evaluation in uniform **$\mathrm{TC}^0$** data complexity (counting/majority is exactly threshold circuits); combined complexity PSPACE-ish.
- **IFP+C / LFP+C:** **PTIME** data complexity — every IFP+C query is polynomial-time computable (so it is a *sound* candidate for capturing P; it just isn't complete).
- **On structured classes:** IFP+C **equals** PTIME (an exact characterization) on bounded-treewidth, planar, and any excluded-minor class — best-possible upper-and-lower matching there.

## 5. Lower Bound

- **CFI lower bound:** IFP+C cannot express certain PTIME properties (solvability of linear equation systems over $\mathbb{F}_2$ / CFI graphs) — *unconditional*, via pebble-game / WL arguments.
- **Rank logic lower bound:** even FO/IFP extended with *rank operators over all prime fields* does **not** capture PTIME (Lichter 2021) — unconditional.
- **FO without counting:** cannot express parity/cardinality-equality at all (locality lower bounds).
- These are model-theoretic (game-based) lower bounds, not complexity-conditional.

## 6. The Gap

The flagship gap is **wide open**: *is there any logic that captures PTIME?* IFP+C is provably insufficient (CFI), and the natural linear-algebraic strengthenings (rank logic) also fail (Lichter). On *restricted structure classes* the gap is closed (Grohe: IFP+C = P on excluded-minor classes). For practical query problems the gap is narrower but real: characterizing exactly which cardinality/aggregation queries need counting vs. fixpoint vs. both. Closing the general gap would resolve a 40-year open problem and would likely require a fundamentally new logical operator beyond counting and rank.

## 7. Current Research (as of June 2026)

- **Beyond rank logic:** searching for operators stronger than WL/rank that might capture PTIME, post-Lichter; **higher-arity WL** and **invertible-map / linear-algebraic** logics (Dawar, Grohe, Pakusa, Lichter). *(frontier — verify)*
- **Counting logic ↔ GNN expressiveness:** $\mathrm{C}^k$/WL hierarchy used to certify and extend graph-neural-network query power; subgraph/higher-order GNNs vs. logical counting (Morris, Grohe, Maron). *(frontier — verify)*
- **Counting in query languages:** expressiveness of SQL aggregation, GROUP BY, and recursive-counting in SQL/PGQ relative to FO+C / IFP+C (Libkin's group; Hella, Niemistö). *(frontier — verify)*

## 8. Future Work

- Find (or prove non-existence of) a logic capturing PTIME.
- Tight expressiveness maps for SQL/PGQ counting & majority against $\mathrm{TC}^0$ / FO+C.
- Operators bridging counting logic and linear algebra that strictly extend WL while staying in P.

## 9. Key References

- **[Foundational]** Cai, Fürer, Immerman. *An Optimal Lower Bound on the Number of Variables for Graph Identification.* Combinatorica, 1992 (CFI; IFP+C ≠ P). — [DOI](https://doi.org/10.1007/BF01305232)
- **[Foundational]** Immerman. *Descriptive Complexity.* Springer, 1999. — [DOI](https://doi.org/10.1007/978-1-4612-0539-5)
- **[Foundational]** Libkin. *Elements of Finite Model Theory.* Springer, 2004 (FO+C, locality, capture results). — [DOI](https://doi.org/10.1007/978-3-662-07003-1)
- **[SOTA]** Grohe. *Descriptive Complexity, Canonisation, and Definable Graph Structure Theory.* Cambridge Univ. Press, 2017. — [DOI](https://doi.org/10.1017/9781139028868)
- **[SOTA]** Lichter. *Separating Rank Logic from Polynomial Time.* LICS, 2021. — [arXiv](https://arxiv.org/abs/2104.12999) · [DOI](https://doi.org/10.1145/3572918)
- **[SOTA]** Morris, Ritzert, Fey, Hamilton, et al. *Weisfeiler and Leman Go Neural: Higher-Order GNNs.* AAAI, 2019. — [arXiv](https://arxiv.org/abs/1810.02244) · [DOI](https://doi.org/10.1609/aaai.v33i01.33014602)

## 10. Worked Example

**Counting beats plain FO; one CFI gadget beats counting.**

*FO cannot say "even".* On a unary relation $P$ with elements $\{p_1,\dots,p_m\}$, no fixed FO sentence expresses "$|P|$ is even": an EF / locality argument lets the duplicator win on $P$ of size $2k$ vs $2k{+}1$ once $k$ exceeds the quantifier rank. But **FO+C** says it trivially: $\exists i\,(2i = \\#x.\,P(x))$ on the number sort. So counting strictly adds power here.

*Why even FO+C (indeed IFP+C) is not enough for P.* The CFI construction replaces each edge of an ordered base graph $G$ by a small gadget with a hidden $\mathbb{F}_2$ "twist". Flipping an *odd* number of twists yields a non-isomorphic graph $\tilde G$, yet $G$ and $\tilde G$ agree on **every** property the $k$-dimensional Weisfeiler–Leman test sees, for $k$ up to $\Omega(n)$. Since $\mathrm{C}^{k+1}\equiv$ $k$-WL (Cai–Fürer–Immerman), no fixed-variable counting formula — hence no IFP+C query — distinguishes $G$ from $\tilde G$. But telling them apart is just solving a linear system over $\mathbb{F}_2$, which is in PTIME. Concretely: a counting query computing "number of length-2 walks" assigns identical multisets of vertex colors to $G$ and $\tilde G$, so it returns the same answer on both — yet a Gaussian-elimination algorithm separates them in $O(n^3)$. This single family witnesses $\mathrm{IFP{+}C}\subsetneq\mathrm{PTIME}$.

---
*Part of the [DBMS Research catalog](../../README.md).*
