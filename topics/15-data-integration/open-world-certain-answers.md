# Open-World Certain Answers Semantics

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/open-world-certain-answers` · **Status:** partially-solved

## 1. Problem Statement

A schema mapping $\mathcal{M} = (\mathbf{S}, \mathbf{T}, \Sigma_{st}, \Sigma_t)$ relates a source schema $\mathbf{S}$ to a target schema $\mathbf{T}$ via source-to-target TGDs $\Sigma_{st}$ and target dependencies $\Sigma_t$. Given source instance $I$, the set of **solutions** $\mathrm{Sol}(\mathcal{M}, I)$ is the set of target instances $J$ satisfying $\Sigma_{st} \cup \Sigma_t$. The **certain answers** to a query $Q$ are $\mathsf{cert}(Q, I) = \bigcap_{J \in \mathrm{Sol}} Q(J)$.

The problem: solutions may be interpreted **open-world** (a solution may contain extra facts beyond those forced by the mapping) or **closed-world** (only forced facts, à la Libkin's CWA-solutions). Open-world certain answers are robust under homomorphism but lose information present in the source; closed-world semantics retain more answers but can make even simple queries intractable or non-monotone. The challenge is a **single, well-behaved, tractable semantics** that lets the mapping designer choose, per relation or per query class, an open- vs closed-world reading, while preserving (i) tractable data complexity, (ii) genericity/monotonicity guarantees, and (iii) compositionality of mappings.

Variants: **decision** (is $\bar a \in \mathsf{cert}$?), **certain-answer enumeration**, and the **representation** problem (compute a finite database — universal solution or condensed representation — that materializes the chosen semantics).

## 2. Mathematical Foundations

The canonical universal solution is the **chase** $\mathrm{chase}(I, \Sigma_{st} \cup \Sigma_t)$: a target instance $U$ with labeled nulls such that $U \to J$ for every $J \in \mathrm{Sol}$. For UCQs (homomorphism-closed queries), $\mathsf{cert}(Q,I) = Q(U)_{\downarrow}$, the null-free tuples of $Q(U)$ (Fagin–Kolaitis–Miller–Popa 2005).

Closed-world variants use **CWA-solutions** (Libkin 2006): instances generated *only* by justified chase steps, formalized with conditional tables / **naïve tables** and a partial order on possible worlds. Under CWA, queries with negation and universal quantification regain meaningful certain answers, computed via the representation system of $\mathbf{c}$-tables (Imielinski–Lipski). The **GLAV** vs **GAV** vs **LAV** distinction governs whether $U$ is computable in PTime (data complexity) and whether $\Sigma_t$ (EGDs/TGDs) keeps the chase terminating (weak acyclicity).

Key theorems: for GLAV mappings with weakly-acyclic $\Sigma_t$, a universal solution exists and is computable in polynomial data complexity; certain answers for UCQs are PTime; adding inequalities or negation pushes certainty to **coNP-complete** (Abiteboul–Duschka).

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Libkin's *open-and-closed-world* (OCWA) and its refinements (Libkin–Sirangelo, ICDT 2008/2011) give a parameterized family interpolating the two extremes via "colored" nulls and equality-/membership-justifications. Hernich's work on **CWA-solutions and certain answers for non-monotone queries** is the reference framework.
- **Systems-SOTA.** **Clio**/**HePToX** lineage and **++Spicy**/**Llunatic** chase engines materialize core universal solutions; **PDQ** and **ChaseBench** (Benedikt et al., SIGMOD 2017) benchmark chase-based answering on open-world semantics.

## 4. Upper Bound

UCQ certain answers under GLAV + weakly-acyclic target TGDs/EGDs: **PTime in data complexity** (polynomial chase + UCQ evaluation on the core). The **core** universal solution is computable in polynomial time for fixed mappings (Gottlob–Nash, JACM 2008) and is the minimal materialization. Combined complexity is generally **coNP** (UCQ) up to **$\Pi_2^p$** for richer queries. CWA certain answers for relational-calculus queries with bounded negation: **coNP** data complexity (Hernich). These hold in the standard RAM/Turing model.

## 5. Lower Bound

Certain answering for CQs with inequalities ($\neq$) under open-world data exchange is **coNP-complete in data complexity** (Abiteboul–Duschka 1998; Fagin et al. 2005) — the canonical hardness. CWA semantics: deciding certain answers for full first-order queries is **undecidable** in general and coNP-hard already for simple non-monotone fragments. Core computation is NP-hard to approximate beyond the exact polynomial cases. Model: NP/coNP many-one reductions (data complexity).

## 6. The Gap

For monotone (UCQ) queries the picture is essentially **closed**: PTime upper/lower bounds match, with the core as canonical representation. The **genuinely open** region is the **non-monotone / mixed open-closed** zone: there is no single tractable semantics that (a) handles negation and universal queries, (b) stays in PTime data complexity, and (c) composes under mapping composition and inversion. Closing it needs either a new tractable representation system richer than naïve tables but cheaper than full $\mathbf{c}$-tables, or sharp dichotomy theorems pinpointing which query/mapping classes admit PTime mixed-world certainty.

## 7. Current Research (as of June 2026)

Active threads: **OCWA$^*$** and label-driven semantics (Libkin school) generalizing both worlds with provenance annotations; **certain answers as approximations** and three-valued (Kleene) evaluation pushed by Libkin's "certainty by approximation" program, which trades exactness for guaranteed-PTime sound answers. *(frontier — verify)* Integration with **semiring provenance** to make open/closed choices a function of annotation, and **probabilistic open-world** semantics for noisy mappings, appear at PODS/ICDT 2025–2026. *(frontier — verify)* Groups: Libkin (Edinburgh/RelationalAI), Kolaitis (UCSC/IBM), Benedikt (Oxford), Pieris (Edinburgh).

## 8. Future Work

- A **compositional** open/closed semantics closed under mapping composition and inverse.
- PTime **mixed-world** certainty for bounded-negation queries with tight dichotomies.
- Practical condensed representations between naïve and full conditional tables.
- User-facing per-relation world-assumption annotations with cost-based answering.

## 9. Key References

- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data exchange: semantics and query answering.* Theoretical Computer Science, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[Foundational]** S. Abiteboul, O. Duschka. *Complexity of answering queries using materialized views.* PODS, 1998. — [DOI](https://doi.org/10.1145/275487.275516)
- **[SOTA]** L. Libkin. *Data exchange and incomplete information.* PODS, 2006. — [DOI](https://doi.org/10.1145/1142351.1142360)
- **[SOTA]** A. Hernich. *Answering non-monotonic queries in relational data exchange.* ICDT, 2010 / Logical Methods in CS, 2011. — [arXiv](https://arxiv.org/abs/1107.1456)
- **[SOTA]** G. Gottlob, A. Nash. *Efficient core computation in data exchange.* Journal of the ACM, 2008. — [DOI](https://doi.org/10.1145/1391289.1391293)
- **[Survey]** L. Libkin. *Certain answers as objects and knowledge.* Artificial Intelligence, 2016. — [DOI](https://doi.org/10.1016/j.artint.2015.11.004)

## 10. Worked Example

GAV mapping: source `Emp(name, dept)` with the single st-tgd $\text{Emp}(n,d) \to \text{Works}(n,d)$. Source $I = \{\text{Emp}(\text{Ann},\text{Sales})\}$. The chase gives universal solution $U = \{\text{Works}(\text{Ann},\text{Sales})\}$.

**Open-world (OWA).** A solution may add facts, e.g. $J = U \cup \{\text{Works}(\text{Bob},\text{HR})\}$ is valid. Query $Q_1(x) = \exists d\,\text{Works}(x,d)$ (monotone) has certain answer $\{\text{Ann}\}$ — Bob is not certain (some solution omits him). Computed directly as $Q_1(U)_{\downarrow} = \{\text{Ann}\}$.

**Where OWA fails.** Non-monotone query $Q_2 = \neg\exists x\,(\text{Works}(x,\text{HR}))$ ("no one in HR"). Under OWA $Q_2$ is *false certainly* (some solution adds an HR tuple), so certain answer is **no** — counterintuitive, since nothing forces HR. Under Libkin's **CWA-solutions** only justified facts survive: the unique CWA-minimal model is $U$ itself, so $Q_2$ is **true**. This is exactly the monotone-PTIME vs non-monotone-coNP/undecidable gap of Section 6: $Q_1$ is easy under either reading; $Q_2$ separates the two semantics.

---
*Part of the [DBMS Research catalog](../../README.md).*
