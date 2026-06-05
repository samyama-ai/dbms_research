# Mechanized Proof of a Cost-Based Optimizer

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/verified-cost-based-optimizer` · **Status:** open

## 1. Problem Statement
Build an **end-to-end, machine-checked** proof (in a proof assistant such as Coq/Rocq, Isabelle/HOL, or Lean) that a *cost-based* query optimizer is **semantics-preserving**: for every input logical plan $P$ and every database $D$, the physical plan $P^\star = \mathrm{Opt}(P)$ produced by the optimizer satisfies $\llbracket P^\star\rrbracket_D = \llbracket P\rrbracket_D$ under SQL bag + 3VL semantics. The optimizer comprises (i) a rule/transformation engine, (ii) a **cost model**, (iii) a **cardinality estimator**, and (iv) a **search strategy** (dynamic programming à la System R, or a Cascades/Volcano top-down search).

Variants:
- **Equivalence (the core):** prove output ≡ input for the *actual implemented* search, not just the rule library in isolation.
- **Optimality (much stronger, usually out of scope):** prove $P^\star$ minimizes the cost model over the explored space — i.e. the search is correct *and* the chosen plan is cost-minimal among enumerated alternatives.
- **Cost-model soundness:** prove the cost/cardinality functions are total, well-defined, and (optionally) bounded-error — typically *not* provable since estimators are heuristic.

Critically, only *equivalence* admits a clean theorem; cost models and estimators are heuristics, so optimality and accuracy are explicitly outside the equivalence guarantee.

## 2. Mathematical Foundations
The optimizer is a function $\mathrm{Opt}$ over an expression algebra with denotational semantics $\llbracket\cdot\rrbracket$ into K-relations / multiplicity vectors $\mathbb{N}^{\mathrm{Tup}}$ (Green–Karvounarakis–Tannen). The proof obligation factors as:
1. **Per-rule soundness:** each transformation $r$ preserves $\llbracket\cdot\rrbracket$ (see the rule-verification problem).
2. **Search soundness:** the search engine only ever combines/applies sound rules, so by structural induction over the search trace every memo-group member is equivalent to the original — a **simulation/refinement** argument over the Cascades memo or the System-R DP table.
3. **Lowering soundness:** logical-to-physical operator selection refines each logical operator with a physical one of equal denotation.

This mirrors **verified-compiler** methodology (CompCert): a *simulation relation* between phases, with each pass proved to preserve a behavioral semantics. The optimizer's DP recurrence over subset lattices is the database analogue of compiler pass composition; soundness is closure of equivalence under the chosen enumeration, *independent* of the cost numbers.

## 3. State of the Art (SOTA)
- **Verified DBMS components:** the closest realized artifact is a *full verified relational engine* rather than an industrial optimizer.
  - **DBCert** (Benzaken, Contejean, et al.) and the broader **Datacert** effort give Coq-formalized SQL semantics (bags, NULLs, aggregation) and proved-correct query compilation/evaluation.
  - **HoTTSQL/UDP, SPES, WeTune** mechanically verify *rewrite rules* (the per-rule layer) but not the search/cost engine.
  - **Q*cert** (Auerbach, Hirzel, et al.) gives a verified query-compiler pipeline (NRA/NRC to targets) with mechanized correctness.
- **Verified optimization elsewhere:** **CompCert** (Leroy, CACM 2009) is the template for end-to-end mechanized optimization correctness in compilers; no equivalent exists for a *cost-based* DB optimizer's search.
- No published artifact provides an end-to-end machine-checked equivalence proof for a *cost-based search* (Cascades/System-R) over realistic SQL — hence **open**.

## 4. Upper Bound
"Upper bound" here is the *scope achieved* by mechanization, not asymptotics. State of the art mechanizes: full SQL denotational semantics with NULLs/bags (DBCert/Datacert), verified evaluators, and automated per-rule equivalence at Calcite scale (SPES verifies hundreds of rules). Composing these gives, in principle, a sound (if labor-intensive) path to a verified *transformation pipeline*; the runtime of the verified optimizer itself remains the standard DP/Cascades cost (exponential in relations in the worst case, polynomial per the System-R left-deep restriction).

## 5. Lower Bound
The *equivalence* obligation rests on query equivalence, which is **undecidable** under bag + 3VL semantics (Jayram–Kolaitis–Vee, PODS 2006), so full automation is impossible — proofs require human-guided or fragment-restricted mechanization. The *optimality* variant additionally inherits the NP-hardness of join-order optimization (Ibaraki–Kameda 1984; cyclic join ordering is NP-hard), so a machine-checked optimality proof can at best certify cost-minimality *within the enumerated space*, not global optimality. These are hard barriers, not engineering gaps.

## 6. The Gap
The components exist in isolation — verified SQL semantics, verified rewrite rules, the CompCert blueprint — but **no one has stitched them into an end-to-end mechanized proof for a cost-based search engine** on realistic SQL. The gap is (1) integration effort (a CompCert-scale, multi-year mechanization), (2) handling the full operator set (correlated subqueries, window functions, recursion) inside the proof, and (3) proving the *search trace* (memo manipulation, pruning, group merging) preserves equivalence, not just the rule set. It is genuinely open: closing it requires a sustained mechanization project, not a single algorithmic insight.

## 7. Current Research (as of June 2026)
Directions: (1) extending Datacert/DBCert toward a verified *optimizing* path, layering verified rewrite rules onto the verified evaluator *(frontier — verify)*; (2) Lean/Rocq formalizations of Cascades memo structures with simulation proofs *(frontier — verify)*; (3) translation-validation as a pragmatic middle ground — instead of verifying the optimizer once, emit a per-query machine-checkable certificate that $P^\star\equiv P$ (SPES-style equivalence checking deployed as a runtime gate). Groups: Benzaken/Contejean and the Datacert/DBCert team (France), Cheung/Suciu (UW) on the verification primitives, and verified-compiler communities (Inria CompCert lineage) supplying methodology.

## 8. Future Work
- A CompCert-style, end-to-end verified cost-based optimizer over a substantial SQL fragment.
- Per-query translation-validation certificates integrated into production optimizers as a cheaper alternative to full verification.
- Mechanized proofs covering Cascades pruning/branch-and-bound so search optimizations remain sound.
- Certified *bounds* on cost-model error (where estimators admit any guarantee), separating equivalence from accuracy.

## 9. Key References
- **[Foundational]** Leroy. *Formal Verification of a Realistic Compiler (CompCert).* CACM, 2009. — [DOI](https://doi.org/10.1145/1538788.1538814) · [PDF](https://xavierleroy.org/publi/compcert-CACM.pdf)
- **[Foundational]** Selinger, Astrahan, Chamberlin, Lorie, Price. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099) · [DBLP](https://dblp.org/rec/conf/sigmod/SelingerACLP79.html)
- **[SOTA]** Benzaken, Contejean, et al. *A Coq Formalization of the Relational Data Model / DBCert verified SQL compilation.* ESOP / journal, 2014–2019. — [DOI](https://doi.org/10.1007/978-3-642-54833-8_11) · [DBLP](https://dblp.org/rec/conf/esop/BenzakenCD14.html)
- **[SOTA]** Auerbach, Hirzel, et al. *Q*cert: A Verified Query Compiler.* (project / SIGMOD demo), 2017. — [project](https://querycert.github.io/)
- **[SOTA]** Zhou, Arulraj, et al. *SPES: A Symbolic Approach to Proving Query Equivalence Under Bag Semantics.* ICDE, 2022. — [arXiv](https://arxiv.org/abs/2004.00481)
- **[Foundational]** Ibaraki, Kameda. *On the Optimal Nesting Order for Computing N-Relational Joins.* ACM TODS, 1984. — [DOI](https://doi.org/10.1145/1270.1498) · [DBLP](https://dblp.org/rec/journals/tods/IbarakiK84.html)

## 10. Worked Example

A miniature semantics-preservation obligation under K-relation semantics. Consider join associativity, the rule the search engine applies when it reorders a 3-way join. Input plan $P = (R \bowtie S) \bowtie T$; the optimizer's DP picks $P^\star = R \bowtie (S \bowtie T)$.

Denote each relation as a multiplicity function into $\mathbb{N}$. For a tuple $t$ over the combined schema, the join denotation multiplies matching multiplicities:
$$\llbracket A \bowtie B\rrbracket_D(t) = \llbracket A\rrbracket_D(t|_A)\cdot \llbracket B\rrbracket_D(t|_B).$$

Then
$$\llbracket P\rrbracket_D(t) = \big(\llbracket R\rrbracket(t|_R)\cdot\llbracket S\rrbracket(t|_S)\big)\cdot\llbracket T\rrbracket(t|_T),$$
$$\llbracket P^\star\rrbracket_D(t) = \llbracket R\rrbracket(t|_R)\cdot\big(\llbracket S\rrbracket(t|_S)\cdot\llbracket T\rrbracket(t|_T)\big).$$
By associativity of $\cdot$ in $\mathbb{N}$, these are equal for *all* $t$ and *all* $D$ — the per-rule obligation discharges.

Concretely: $R=\{a\!\mapsto\!2\}$, $S=\{a\!\mapsto\!3\}$, $T=\{a\!\mapsto\!1\}$ on a shared key. $\llbracket P\rrbracket=(2\cdot3)\cdot1=6$; $\llbracket P^\star\rrbracket=2\cdot(3\cdot1)=6$. The *search* proof then inducts over the memo: every group member is built only by such sound rules, so $P^\star\equiv P$ — and this holds *independent of the cost numbers* that chose $P^\star$, which is exactly why equivalence is provable while optimality (NP-hard join ordering) is not.

---
*Part of the [DBMS Research catalog](../../README.md).*
