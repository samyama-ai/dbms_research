---
id: 25-query-languages-expressiveness/probabilistic-query-languages
title: "Query Language Power Over Probabilistic Databases"
topic: 25-query-languages-expressiveness
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Query Language Power Over Probabilistic Databases

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/probabilistic-query-languages` · **Status:** partially-solved

## 1. Problem Statement
A **probabilistic database (PDB)** is a probability distribution over ordinary database instances, most commonly the *tuple-independent* (TID) model where each tuple $t$ is present independently with probability $p(t)$. For a Boolean query $q$, **query evaluation** asks for $\Pr[q] = \sum_{D : D \models q} \Pr[D]$. The central question is the **complexity dichotomy**: classify queries (and query-language fragments) into those whose probability is computable in polynomial time (*safe*, *liftable*) versus those that are **#P-hard** (*unsafe*).

Variants:
- **Exact counting:** compute $\Pr[q]$ exactly (the dichotomy variant).
- **Approximate:** $(\varepsilon,\delta)$-approximation (FPRAS via Monte Carlo / Karp–Luby).
- **Top-$k$ / ranking** over uncertain answers; **most-probable-database / MAP** inference.
- **Expressiveness:** what is the right language to *write* probabilistic queries and reason about lineage/provenance (semiring provenance, PrDB-SQL, probabilistic programming over relations).

## 2. Mathematical Foundations
The probability of a Boolean query equals the probability of its **lineage** (provenance) Boolean formula $\Phi_q$ over the random tuple variables; thus $\Pr[q]$ is the **weighted model count** (WMC) of $\Phi_q$. For unions of conjunctive queries (UCQ), lineage is a monotone DNF, and exact computation is **#P-hard in general** (it generalizes counting DNF satisfying assignments).

The landmark result is the **Dichotomy Theorem** (Dalvi–Suciu): every Boolean UCQ without self-joins (and, in the full theorem, every UCQ) is either computable in PTIME by a *safe plan* using six rules (independent-join, independent-project, inclusion–exclusion, etc.) — equivalently the lineage admits an efficient **OBDD/d-DNNF / read-once-ish** compilation — **or** it is #P-hard, with *no intermediate* complexity (assuming $\mathsf{P}\neq\mathsf{\\#P}$). Algebraically, hardness is tied to whether the query's lineage is **liftable** (computable by lifted inference / extensional evaluation) vs. requiring grounded WMC.

$$\Pr[q] = \mathrm{WMC}(\Phi_q), \qquad \underbrace{q \text{ safe} \iff \Phi_q \text{ liftable (PTIME)}}_{\text{dichotomy: otherwise } q \text{ is } \\#P\text{-hard}}.$$

Foundations also draw on **knowledge compilation** (OBDD, FBDD, d-DNNF, SDD), **semiring provenance** (Green–Karvounarakis–Tannen), and **dichotomy methods** from constraint counting (#CSP dichotomies, Bulatov; Cai–Chen).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** The **UCQ dichotomy** (Dalvi–Suciu, JACM 2012) is the definitive result for the relational fragment; extended to queries with negation/inequalities partially, and to **symmetric/lifted inference** dichotomies (Van den Broeck et al.) connecting to statistical relational learning. Bound on knowledge-compilation size separating safe vs. unsafe (Beame–Li–Roy–Suciu).
- **Systems-SOTA:** **MystiQ**, **Trio**, **MayBMS/SPROUT** (Olteanu et al.), and **ProbLog / PSDD / lifted inference** engines; modern probabilistic-programming and PGM systems (e.g., differentiable WMC) implement approximate/exact PDB evaluation. **DeepDB / scaling WMC** with d-DNNF compilers (c2d, miniC2D, ADDMC).

## 4. Upper Bound
For **safe queries**, evaluation is in **PTIME data complexity** via a safe plan (extensional evaluation), with combined complexity polynomial in the query size for the read-once cases. For *any* monotone query, a **fully polynomial randomized approximation scheme (FPRAS)** exists for $\Pr[q]$ when lineage is a (monotone) DNF, via the Karp–Luby unbiased estimator: $(\varepsilon,\delta)$-approximation in time polynomial in $1/\varepsilon$, $\log(1/\delta)$, and lineage size. Knowledge compilation gives exact evaluation in time linear in the compiled d-DNNF/OBDD size.

## 5. Lower Bound
Exact evaluation of **unsafe** UCQs is **#P-hard** (Dalvi–Suciu); the canonical hard query $H_0 = R(x),S(x,y),T(y)$ (and the hierarchy $H_k$) is #P-hard, with the hardness shown by reduction from counting independent sets / #PP2DNF. For unsafe queries the **compiled representation is provably exponential**: there exist UCQs whose OBDD/FBDD (and even d-DNNF, under the relevant separations) size is $2^{\Omega(n)}$ (Beame–Li–Roy–Suciu, "Lower bounds for exact model counting and applications in probabilistic databases," UAI 2013). These are unconditional compilation lower bounds, not merely $\mathsf{P}\neq\mathsf{\\#P}$-conditional.

## 6. The Gap
For **UCQs the gap is essentially closed** (full dichotomy), which is why the status is *partially-solved*. It remains **open** to push a clean dichotomy beyond UCQs: with **inequalities/negation**, **aggregation**, **recursion (Datalog)**, **disjointness/correlations** (block-independent-disjoint and pc-tables), and **continuous/numerical attributes**. Whether a dichotomy holds for full relational calculus or for queries over more expressive correlation models is genuinely open, as is tightening approximation lower bounds for structured (low-treewidth) lineage.

## 7. Current Research (as of June 2026)
- Unifying PDB dichotomies with **lifted inference** and **#CSP** dichotomy machinery; dichotomies for queries with **self-joins** beyond the known partial results *(frontier — full self-join dichotomy still partial; verify scope)*.
- **Provenance semirings** and **differentiable / gradient** weighted model counting for ML-in-the-database; neuro-symbolic PDBs.
- PDBs over **open-world / infinite domains** and **continuous** attributes (Grohe–Lindner measure-theoretic PDBs), and complexity of expectation/aggregate queries.

## 8. Future Work
- A complete dichotomy for UCQ + aggregation and for safe recursion.
- Practical safe-plan / lifted-inference compilers that fall back to FPRAS with guarantees on unsafe sub-queries.
- Tight knowledge-compilation lower bounds for d-DNNF/SDD over realistic correlation models.

## 9. Key References
- **[Foundational]** N. Dalvi, D. Suciu. *The Dichotomy of Probabilistic Inference for Unions of Conjunctive Queries.* JACM, 2012. — [DOI](https://doi.org/10.1145/2395116.2395119)
- **[Survey]** D. Suciu, D. Olteanu, C. Ré, C. Koch. *Probabilistic Databases.* Synthesis Lectures, Morgan & Claypool, 2011. — [DOI](https://doi.org/10.2200/S00362ED1V01Y201105DTM016)
- **[SOTA]** P. Beame, J. Li, S. Roy, D. Suciu. *Lower Bounds for Exact Model Counting and Applications in Probabilistic Databases.* UAI, 2013. — [arXiv](https://arxiv.org/abs/1309.6815)
- **[Foundational]** T. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[SOTA]** G. Van den Broeck, D. Suciu. *Query Processing on Probabilistic Data: A Survey.* Foundations and Trends in Databases, 2017. — [DOI](https://doi.org/10.1561/1900000052)
- **[Foundational]** R. Karp, M. Luby, N. Madras. *Monte-Carlo Approximation Algorithms for Enumeration Problems.* J. Algorithms, 1989. — [DOI](https://doi.org/10.1016/0196-6774(89)90038-2)

## 10. Worked Example

Two TID tables. $R(A)$: tuple $r_1=(a)$ with $p=0.5$. $S(A)$: $s_1=(a)$ with $p=0.5$. Boolean query $q = \exists x\, R(x) \land S(x)$.

**Safe (independent-join) case.** Here $q$'s lineage is $\Phi_q = X_{r_1} \land X_{s_1}$, a read-once formula over *independent* variables, so $\Pr[q] = 0.5 \times 0.5 = 0.25$ — computed by a safe plan in PTIME.

**The hard query $H_0 = R(x), S(x,y), T(y)$.** Let $R=\{a_1,a_2\}$, $T=\{b_1,b_2\}$ (each $p=1$), and let $S$ contain $(a_i,b_j)$ with probability $0.5$ each. Lineage is the bipartite PP2DNF $\Phi = \bigvee_{i,j} X_{ij}$ over independent $S$-variables. Inclusion–exclusion does **not** factor (the terms share variables across both sides), and computing $\Pr[\Phi]$ is exactly #PP2DNF counting — the canonical **#P-hard** core. With all four $S$-tuples present-or-absent equiprobably, $\Pr[H_0]=1-\Pr[\text{no }(a_i,b_j)\text{ edge forms a path}]$; the dichotomy says no safe plan exists for $H_0$, so exact evaluation must fall back to grounded WMC or FPRAS.

---
*Part of the [DBMS Research catalog](../../README.md).*
