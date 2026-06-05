# Transformation-rule completeness and confluence

> **Topic:** Query Optimization · **ID:** `02-query-optimization/transformation-rule-completeness` · **Status:** open

## 1. Problem Statement

Rule-based optimizers (Volcano/Cascades, Calcite, Orca) generate the search space by repeatedly applying **transformation rules** — logical rewrites such as join commutativity/associativity, predicate pushdown, aggregate pushdown, subquery unnesting — to expressions in a memo until fixpoint. Two foundational questions about a rule set $\mathcal{R}$:

- **Completeness (the "soundness-and-completeness" question):** Does $\mathcal{R}$, applied exhaustively, generate the **entire logical equivalence class** of a query (every plan equivalent under the relational-algebra semantics), or only a subset? If a subset, *which* plans are unreachable?
- **Confluence / termination:** Does rule application **terminate** (reach a fixpoint memo), and is the resulting memo **independent of application order** (confluent / Church–Rosser)? Non-confluence means the reachable space depends on scheduling — undermining any optimality claim.

Variants: the **decision** problem "is plan $p$ derivable from query $q$ under $\mathcal{R}$?"; the **counting** problem "how many distinct equivalent expressions does $\mathcal{R}$ generate?"; and the **synthesis** problem "construct a minimal complete, confluent, terminating $\mathcal{R}$ for a query class." "Solving" means a soundness+completeness theorem plus a termination/confluence proof for a stated algebra fragment.

## 2. Mathematical Foundations

Model rules as a **term-rewriting system (TRS)** over relational-algebra expression trees, or as an **AND/OR graph** (memo) closure. Each rule $\ell\to r$ rewrites a matching subexpression; soundness means $\llbracket\ell\rrbracket=\llbracket r\rrbracket$ under bag/set semantics. The **logical equivalence class** $[q]=\{e:\llbracket e\rrbracket=\llbracket q\rrbracket\}$ is what completeness targets. Completeness asks whether the rewrite relation $\to_{\mathcal{R}}^{*}$ restricted to $[q]$ is **strongly connected** (every equivalent expression reachable from every other). Termination is **strong normalization** of the TRS; because join commutativity is symmetric ($A\bowtie B\to B\bowtie A$), naive TRS termination fails, so optimizers terminate via **memoization** (dedup of logically-equal groups) rather than normal forms. Confluence is the **Church–Rosser** property: $a\to^* b$ and $a\to^* c \Rightarrow \exists d: b\to^* d, c\to^* d$. Local confluence + termination $\Rightarrow$ confluence (Newman's Lemma); critical-pair analysis (Knuth–Bendix) is the standard tool, but equational theories with associativity/commutativity (AC-rewriting) require AC-unification, which is decidable but NP-hard. The semantics underpinning equivalence is the relational algebra and the **chase** for constraint-aware rewrites (Abiteboul–Hull–Vianu).

## 3. State of the Art (SOTA)

- **Theory SOTA:** Completeness is known for restricted fragments. For **conjunctive queries**, the equivalence class is characterized by query homomorphism / the chase, and a complete rewriting calculus exists. For **join reordering only**, commutativity+associativity provably generate all bushy trees (classical). General full-algebra rule sets (with aggregation, null-aware outer joins, set ops) have **no published completeness proof**; practical sets are known *incomplete* (e.g., missing transformations leave better plans unreachable).
- **Systems SOTA:** Apache **Calcite** ships a large, curated rule library with no formal completeness guarantee; Orca and SQL Server similarly. Recent formal-methods work verifies *soundness* of individual rewrites (e.g., **Cosette**/UDP equivalence provers, Chu–Wang–Suciu) but not set-level completeness or confluence.

## 4. Upper Bound

For **conjunctive queries**, deciding expression equivalence is decidable (CQ containment, NP-complete, Chandra–Merlin 1977), so derivability under a complete CQ rewrite system is decidable and the equivalence class is finite up to renaming; exhaustive memo closure terminates. For the **join-only** fragment, commutativity+associativity reach all $\sim n!\cdot C_{n-1}$ bushy trees, and memoization makes closure run in $O(\\#\text{ccp})$-style time (RAM model). Where a complete, terminating, confluent $\mathcal{R}$ is known, the upper bound is "exhaustive memo fixpoint," polynomial in the size of the generated memo.

## 5. Lower Bound

General relational expression **equivalence is undecidable** once arbitrary operators (notably with arithmetic, recursion, or full first-order conditions) are admitted — by reduction from FO/relational-calculus equivalence, which is undecidable (Trakhtenbrot). Hence no algorithm can decide completeness of an arbitrary $\mathcal{R}$ for the full algebra. Even for **conjunctive queries**, equivalence/containment is **NP-complete** (Chandra–Merlin), so confluence checking that hinges on equivalence inherits NP-hardness. AC-unification needed for critical-pair analysis under commutative/associative joins is NP-hard. These place the general problem firmly outside tractability and, for the full algebra, outside decidability.

## 6. The Gap

This problem is **genuinely open** in a strong sense: for restricted fragments (CQ, join-only) completeness and termination are understood, but for the **full algebra used by real optimizers** there is (a) no general completeness theorem — indeed undecidability blocks one — and (b) essentially no confluence analysis, so deployed optimizers cannot certify that their reachable plan set is order-independent or maximal. The gap is therefore not "upper vs. lower bound on one algorithm" but a missing **theory delineating the largest algebra fragment for which a finite complete confluent terminating rule set exists**, and a **characterization of the unreachable plans** for the incomplete fragments beyond it. Closing it requires fragment-by-fragment completeness results plus a principled account of how memoization substitutes for TRS termination.

## 7. Current Research (as of June 2026)

- **Mechanized equivalence proving** for individual rewrites (Cosette/UDP, HoTTSQL lineage; Suciu, Wang, Chu) extending toward libraries of *verified* rules. *(frontier — verify)*
- **Formal semantics for Calcite/Cascades** enabling completeness and confluence reasoning over the actual rule library (Calcite community; academic formalizations). *(frontier — verify)*
- **Constraint-aware completeness** using the chase and homomorphism theory for CQ-with-constraints rewriting (links to *semantic-query-optimization*).
- Automated **rule synthesis / learning** that discovers missing rewrites to close incompleteness empirically (e.g., learned or SMT-guided rule discovery). *(frontier — verify)*

## 8. Future Work

- Identify the maximal algebra fragment admitting a finite, complete, confluent, terminating rule set; prove it.
- Characterize and bound the *unreachable* plan set for standard incomplete libraries.
- Confluence/critical-pair analysis adapted to memoized (rather than normalizing) rewriting.
- Machine-checked completeness proofs for production rule libraries on a defined fragment.

## 9. Key References

- **[Foundational]** Chandra, Merlin. *Optimal Implementation of Conjunctive Queries in Relational Data Bases.* STOC, 1977. — [ACM](https://dl.acm.org/doi/10.1145/800105.803397)
- **[Foundational]** Abiteboul, Hull, Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)
- **[Foundational]** Graefe. *The Cascades Framework for Query Optimization.* IEEE Data Eng. Bulletin, 1995. — [DBLP](https://dblp.org/rec/journals/debu/Graefe95a.html)
- **[SOTA]** Chu, Weiss, Suciu, et al. *Cosette / HoTTSQL: Proving Query Rewrites with Univalent SQL Semantics.* PLDI / CIDR, 2017. — [ACM](https://dl.acm.org/doi/10.1145/3062341.3062348)
- **[SOTA]** Begoli, Camacho-Rodríguez, Hyde, et al. *Apache Calcite: A Foundational Framework for Optimized Query Processing.* SIGMOD, 2018. — [arXiv](https://arxiv.org/abs/1802.10233)
- **[Survey]** Baader, Nipkow. *Term Rewriting and All That.* Cambridge University Press, 1998. — [Cambridge](https://www.cambridge.org/core/books/term-rewriting-and-all-that/71768055278D0DEF4FFC74722DE0D707)

## 10. Worked Example

Take the **join-only** fragment with a single rule, associativity $A\bowtie(B\bowtie C)\to(A\bowtie B)\bowtie C$ plus commutativity. Start from the left-deep tree $(A\bowtie B)\bowtie C$ over 3 relations. How many distinct trees does exhaustive application generate, and does the memo terminate?

The number of binary trees on $n$ leaves is $C_{n-1}$ (Catalan), and leaf orderings give $n!$ labelings; for $n=3$: $C_2\cdot 3! = 2\cdot 6 = 12$ distinct expressions. Commutativity alone is **non-terminating** as a TRS — $A\bowtie B\to B\bowtie A\to A\bowtie B$ loops — so a normalizing rewriter never halts. Optimizers instead **memoize**: each logical group (e.g. $\{A,B\}$) is stored once, deduplicated by its relation set, so the 12 expressions collapse into $2^3-1=7$ memo groups (one per non-empty subset), and closure reaches fixpoint.

**Completeness check:** every one of the 12 bushy trees is reachable from any other via commutativity+associativity, so $\to^*_{\mathcal R}$ is strongly connected on $[q]$ — complete for this fragment. Add a `GROUP BY` above the join and no published rule set guarantees this property (§3) — that is the open frontier.

---
*Part of the [DBMS Research catalog](../../README.md).*
