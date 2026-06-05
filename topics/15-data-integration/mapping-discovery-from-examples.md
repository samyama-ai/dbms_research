# Mapping Discovery From Data Examples

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/mapping-discovery-from-examples` · **Status:** partially-solved

## 1. Problem Statement

Given a source schema $\mathbf{S}$, a target schema $\mathbf{T}$, and a finite set of **data examples** $E = \{(I_1, J_1), \dots, (I_n, J_n)\}$ — each a pair of a source instance fragment $I_k$ and a target instance fragment $J_k$ that a designer asserts the desired mapping should produce — find a **GLAV schema mapping** $\mathcal{M}$ (a finite set of source-to-target tuple-generating dependencies, st-tgds) that is consistent with all examples, and ideally that is *the* intended mapping.

- **Decision variant:** Given $E$ and a candidate $\mathcal{M}$, does $\mathcal{M}$ **fit** $E$ (each $J_k$ is a valid solution for $I_k$ under $\mathcal{M}$, under a chosen fitting notion: universal, certain-answer, or exact)?
- **Existence variant:** Is there *any* GLAV mapping fitting $E$?
- **Synthesis/optimization variant:** Among fitting mappings, return one that is most general / minimal-size / *characterized* by $E$.
- **Characterizability variant:** Does there exist a *finite* set of examples that **uniquely identifies** (up to logical equivalence) a given target mapping $\mathcal{M}$ within a class?

"Solving" means an algorithm that, from polynomially many well-chosen examples, returns a GLAV mapping provably equivalent to the designer's intended one.

## 2. Mathematical Foundations

A schema mapping is a triple $(\mathbf{S}, \mathbf{T}, \Sigma)$ where $\Sigma$ is a set of st-tgds $\forall \mathbf{x}\,(\varphi(\mathbf{x}) \rightarrow \exists \mathbf{y}\,\psi(\mathbf{x}, \mathbf{y}))$, with $\varphi$ a CQ over $\mathbf{S}$ and $\psi$ a CQ over $\mathbf{T}$. A target instance $J$ is a **solution** for $I$ if $(I, J) \models \Sigma$; a **universal solution** maps homomorphically into every solution and is produced by the **chase** of $I$ with $\Sigma$.

Fitting comes in flavors (Alexe–ten Cate–Kolaitis–Tan): a data example $(I, J)$ is *universal* if $J$ is (the core of) a universal solution, *certain* if $J = \mathsf{certain}(\mathcal{M}, I)$, or *positive/negative* w.r.t. a labeling. The central learnability result casts this as **exact learning** in Angluin's framework: GLAV mappings are *characterizable* by **unique characterizations** — a finite example set $E_\mathcal{M}$ such that any mapping fitting $E_\mathcal{M}$ is logically equivalent to $\mathcal{M}$. Characterization size is governed by the **fitting Galois connection** between sets of examples and sets of mappings, and by the *frontier* of the homomorphism order on the canonical instances of $\varphi$. PAC bounds depend on the VC dimension of the st-tgd hypothesis class, which is finite only under bounds on body/head size.

## 3. State of the Art (SOTA)

**Theory SOTA.** ten Cate, Dalmau, Kolaitis (TODS 2013) gave the foundational fitting/characterizability theory for GAV and GLAV; ten Cate, Kolaitis, Qian, Tan (PODS/LMCS 2017–2018) established that GAV mappings are *exactly learnable* with membership+equivalence queries and that unique characterizations exist but can be exponential. ten Cate, Dalmau (ICDT 2021–2022) sharpened the "most-general fitting" and frontier-based synthesis. **Systems SOTA.** EIRENE / MapMerge-style example-driven design (Alexe et al., VLDB 2011) and the interactive refinement loop in Clio descendants; ML/LLM-assisted example-to-mapping induction is an active empirical thread *(frontier — verify)*.

## 4. Upper Bound

For **GAV** mappings, fitting-existence is decidable and a most-specific fitting GAV mapping is computable; exact learnability with membership and equivalence queries runs in polynomial time *in the size of the target mapping and the largest counterexample* (ten Cate–Kolaitis–Qian–Tan, 2017). For **GLAV**, a fitting mapping exists iff a certain *homomorphism-closure* condition on $E$ holds, decidable in $\Sigma^p_2$ / coNP-style bounds depending on the fitting notion; unique characterizations exist but may require example sets of size exponential in the schema arity. Model: classical complexity / exact learning (membership + equivalence query) model.

## 5. Lower Bound

Deciding whether a GLAV mapping fits a set of data examples under the *exact* semantics is **coNP-hard** in combined complexity, reducing from CQ-containment / homomorphism existence. Unique characterizations for GAV can require **exponentially many** examples in the schema size (ten Cate et al.), an information-theoretic lower bound on any characterization scheme. Learnability with only membership queries (no equivalence oracle) is impossible for GLAV in general — an Angluin-style **approximate fingerprint** argument rules out polynomial-query exact learning. Model: exact-learning query complexity and NP/coNP.

## 6. The Gap

For GAV the picture is essentially **closed** (poly-time learnable with both oracles; exponential characterization tight). For **GLAV** a genuine gap remains: we lack a tight bound on the minimum characterizing-example-set size, and there is no known polynomial-query exact-learning algorithm — it is open whether one exists or is provably ruled out. Closing it requires either a GLAV learning algorithm matching the GAV oracle bounds or an unconditional query-complexity lower bound. The interaction of *minimality* (core, most-general) with *fitting* adds a second open axis.

## 7. Current Research (as of June 2026)

Active directions: (1) ten Cate, Dalmau, Kolaitis and collaborators on frontiers, most-general fittings, and the homomorphism-order structure underlying characterizations; (2) example-driven and LLM-in-the-loop synthesis that proposes st-tgds and uses formal fitting checks as a verifier *(frontier — verify)*; (3) extending characterizability to mappings with target constraints (egds/target-tgds) and to nested/JSON schemas; (4) PAC/agnostic learnability of mappings under noisy examples. The verification-against-formal-semantics angle ties this to the broader "make learned mappings checkable" thread.

## 8. Future Work

Tight characterization-size bounds for GLAV; polynomial-query learnability or its refutation; robust (noise-tolerant, agnostic) learning; active-learning strategies that minimize designer-labeled examples; integration with target constraints and second-order tgds; and principled handling of *under-determination*, where many inequivalent mappings fit, requiring an inductive bias (Occam / minimality) with provable recovery guarantees.

## 9. Key References

- **[Foundational]** Fagin, Kolaitis, Miller, Popa. *Data Exchange: Semantics and Query Answering.* ICDT 2003 / TCS 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[Foundational]** ten Cate, Dalmau, Kolaitis. *Learning Schema Mappings.* ICDT 2012 / TODS 2013. — [DOI](https://doi.org/10.1145/2539032.2539035)
- **[SOTA]** ten Cate, Kolaitis, Qian, Tan. *Active Learning of GAV Schema Mappings.* PODS 2018 / LMCS. — [DOI](https://doi.org/10.1145/3196959.3196974)
- **[SOTA]** Alexe, ten Cate, Kolaitis, Tan. *Designing and Refining Schema Mappings via Data Examples.* SIGMOD 2011. — [DOI](https://doi.org/10.1145/1989323.1989338)
- **[Foundational]** Angluin. *Queries and Concept Learning.* Machine Learning, 1988. — [DOI](https://doi.org/10.1007/BF00116828)
- **[Survey]** Kolaitis. *Schema Mappings, Data Exchange, and Metadata Management.* PODS 2005. — [DOI](https://doi.org/10.1145/1065167.1065176)

## 10. Worked Example

Source schema $\mathbf{S} = \{\mathsf{Teaches}(\text{prof}, \text{course})\}$; target $\mathbf{T} = \{\mathsf{Instructs}(\text{prof}, \text{course}, \text{dept})\}$. The designer gives one data example
$$I_1 = \{\mathsf{Teaches}(\text{Lee}, \text{DB})\}, \quad J_1 = \{\mathsf{Instructs}(\text{Lee}, \text{DB}, N)\}$$
where $N$ is a labeled null (dept unknown). A GAV-style candidate $\mathcal{M}_1: \mathsf{Teaches}(p,c) \rightarrow \exists d\,\, \mathsf{Instructs}(p,c,d)$ **fits**: chasing $I_1$ yields exactly $\mathsf{Instructs}(\text{Lee}, \text{DB}, N')$, which maps homomorphically onto $J_1$ (and vice versa), so $J_1$ is a universal solution.

But $\mathcal{M}_2: \mathsf{Teaches}(p,c) \rightarrow \mathsf{Instructs}(p,c,p)$ (copy prof into dept) **also fits this example** under certain-answer semantics if we only check the projection $(\text{prof},\text{course})$ — illustrating **under-determination**: one example cannot separate $\mathcal{M}_1$ from $\mathcal{M}_2$. Adding a second example with a distinct prof/dept (e.g. forcing dept $\neq$ prof) is what a *unique characterization* $E_\mathcal{M}$ supplies. The information-theoretic lower bound says for GAV such separating sets can grow exponentially in schema arity.

---
*Part of the [DBMS Research catalog](../../README.md).*
