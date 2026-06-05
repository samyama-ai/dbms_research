# Tractable CQs via Treewidth/Submodular Width

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/cq-treewidth-submodular-width` · **Status:** partially-solved

## 1. Problem Statement

For **conjunctive queries (CQs)**, evaluation is NP-complete in combined complexity (it is essentially the homomorphism problem). The question is which **structural parameter** of the query's hypergraph exactly governs polynomial-time evaluation:

- **(Boolean CQ decision)** For a class $\mathcal{C}$ of CQs, when is evaluation (does $Q(D)$ hold?) solvable in time $\mathrm{poly}(|D|)$ uniformly over $\mathcal{C}$?
- **(Exact characterization)** Identify the single width measure $w(Q)$ such that bounded-$w$ classes are tractable and unbounded-$w$ classes are not (under standard complexity assumptions).
- **(Enumeration/counting)** Extend the characterization to answer enumeration with delay and to counting (#CQ).

The headline parameters are **treewidth**, **(fractional/generalized) hypertree width**, and **submodular width** — and the deep question is which is *the* exact tractability frontier.

## 2. Mathematical Foundations

A CQ corresponds to a hypergraph $H=(V,E)$ (variables = vertices, atoms = hyperedges). Width measures, in increasing generality:
$$
\mathrm{tw} \;\geq\; \mathrm{ghw} \;\geq\; \mathrm{fhw} \;\geq\; \mathrm{subw}.
$$

- **Treewidth (tw)** governs Boolean queries with bounded arity. Grohe's theorem: for classes of *bounded-arity* CQs, evaluation is in PTIME (and FPT) **iff** the cores have bounded treewidth (under FPT $\neq$ W[1]).
- **Fractional hypertree width (fhw)** and the **AGM bound** (Atserias, Grohe, Marx 2008) bound output size $|Q(D)| \le \prod \text{(fractional edge cover)}$, enabling $O(|D|^{\mathrm{fhw}})$ evaluation via worst-case-optimal joins.
- **Submodular width (subw)** (Marx 2010) is the finest: classes of CQs are **fixed-parameter tractable iff bounded submodular width** (assuming the Exponential Time Hypothesis). The **PANDA** algorithm (Abo Khamis, Ngo, Suciu 2017) realizes evaluation in time $\tilde O(|D|^{\mathrm{subw}})$ via information-theoretic (Shannon/entropy) inequalities and edge-cover LPs.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Grohe (2007) for bounded-arity tw dichotomy; **Marx (2010, JACM 2013)** for the submodular-width FPT characterization; AGM (2008) for tight size bounds; Ngo, Porat, Ré, Rudra (2012) **worst-case-optimal joins (NPRR/Leapfrog Triejoin)**; **PANDA** (Abo Khamis, Ngo, Suciu, PODS 2017) for subw-optimal evaluation. Enumeration with constant delay characterized by **free-connex acyclicity** (Bagan, Durand, Grandjean 2007).
- **Systems-SOTA.** Worst-case-optimal join engines: **LogicBlob/EmptyHeaded** (Aberger, Ré et al., *SIGMOD* 2017), **Umbra/Tributary**, factorized databases **FDB / FAQ** (Olteanu, Schleich), and Leapfrog Triejoin in commercial/graph engines (RelationalAI). DuckDB and others adopt WCOJ for cyclic joins.

## 4. Upper Bound

- Bounded-treewidth (bounded-arity) CQ evaluation: **$O(|D|^{\mathrm{tw}+1})$**, FPT in query size.
- General CQ: **$\tilde O(|D|^{\mathrm{fhw}})$** via worst-case-optimal joins respecting the AGM/fractional-cover bound.
- Best known overall: **PANDA** evaluates a CQ in $\tilde O(|D|^{\mathrm{subw}} + |Q(D)|)$, and $\mathrm{subw} \le \mathrm{fhw}$, so submodular width is the tightest general upper bound. Model: RAM model, combined complexity, data of size $|D|$.

## 5. Lower Bound

- **CQ evaluation is W[1]-hard** parameterized by query size (Papadimitriou & Yannakakis; Grohe), so no uniform PTIME for unbounded-tw bounded-arity classes unless FPT = W[1].
- **Grohe's dichotomy**: bounded-arity classes are PTIME-solvable iff bounded treewidth (cores), assuming FPT $\neq$ W[1].
- **Marx's lower bound**: under the **Exponential Time Hypothesis (ETH)**, classes of unbounded submodular width are *not* FPT — establishing subw as the exact frontier in the parameterized sense.
- **Fine-grained**: AGM is tight (instances achieve $\Omega(|D|^{\mathrm{fhw}})$ output); triangle/clique detection lower bounds connect to matrix-multiplication and 3SUM-style barriers for specific shapes.

## 6. The Gap

For **bounded-arity** CQs the frontier is *closed*: treewidth, via Grohe's dichotomy. For **general (unbounded-arity) CQs**, submodular width is the proven frontier for **fixed-parameter tractability** (Marx, under ETH) — but several gaps remain: (i) the precise relationship between **subw upper bounds (PANDA) and matching unconditional lower bounds** beyond ETH; (ii) tractability of **counting (#CQ)** and **enumeration** is governed by *different* (stricter) measures, not yet unified; (iii) the constants/exponents hidden in $\tilde O$ and whether subw is computable efficiently. So: closed for Boolean bounded-arity decision; **partially open** for general/counting/enumeration variants.

## 7. Current Research (as of June 2026)

- **Information-theoretic query evaluation**: extending **FAQ/PANDA** with Shannon-inequality machinery, **degree-aware** and **output-sensitive** bounds (Abo Khamis, Ngo, Suciu; Joglekar, Ré). *(frontier — verify)* Tighter "polymatroid bound" vs. "Shannon bound" separations for join output size remain actively studied.
- **WCOJ in real systems**: integration into DuckDB, Umbra, and graph engines; cost-based mixing of binary and WCOJ plans. *(frontier — verify)* Learned/adaptive width-aware optimizers.
- **Enumeration & counting dichotomies** beyond free-connex (Carmeli, Kröll, Schweikardt, Segoufin), and **CQs with negation/aggregation**.
- **Disjunctive/UCQ and CQ-with-comparisons** width theory.

## 8. Future Work

- Unconditional (non-ETH) lower bounds matching submodular width.
- A single parameter unifying decision, counting, and enumeration tractability.
- Efficient computation/approximation of submodular width for the optimizer.
- Width-aware adaptive join engines and provenance/factorized representations at scale.

## 9. Key References

- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size bounds and query plans for relational joins (the AGM bound).* FOCS, 2008 / SIAM J. Computing, 2013.
- **[Foundational]** M. Grohe. *The complexity of homomorphism and constraint satisfaction problems seen from the other side.* JACM, 2007.
- **[SOTA]** D. Marx. *Tractable hypergraph properties for constraint satisfaction and conjunctive queries (submodular width).* JACM, 2013 (STOC 2010).
- **[SOTA]** H. Q. Ngo, E. Porat, C. Ré, A. Rudra. *Worst-case optimal join algorithms.* PODS, 2012 / JACM, 2018.
- **[SOTA]** M. Abo Khamis, H. Q. Ngo, D. Suciu. *What do Shannon-type inequalities, submodular width, and disjunctive Datalog have to do with one another? (PANDA).* PODS, 2017.
- **[SOTA]** C. R. Aberger, S. Tu, K. Olukotun, C. Ré. *EmptyHeaded: a relational engine for graph processing.* SIGMOD, 2017.
- **[Survey]** D. Olteanu, M. Schleich. *Factorized databases.* SIGMOD Record, 2016.

---
*Part of the [DBMS Research catalog](../../README.md).*
