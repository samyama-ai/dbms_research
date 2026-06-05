# Counterfactual Explanation Complexity

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/counterfactual-explanation-complexity` · **Status:** partially-solved

## 1. Problem Statement

Given a database $D$, a Boolean (or specific-answer) query $Q$, and a tuple $t \in D$, **causality** asks whether $t$ is a *cause* of the answer, and **responsibility** quantifies *how much* by the size of the smallest *contingency set* — a set $\Gamma$ whose removal makes $t$ **counterfactual** (removing $t$ flips the answer once $\Gamma$ is gone). We study the **complexity and approximability** of:

- **Decision (cause):** is $t$ a (actual) cause of $Q(D)$?
- **Optimization (responsibility):** compute $\rho(t) = \frac{1}{1+|\Gamma_{\min}|}$ for the minimum contingency set $\Gamma_{\min}$.
- **Counting:** number of minimal contingency sets.

This is the Halpern–Pearl actual-causality framework specialized to queries (Meliou et al.). It is *partially solved*: a complete **dichotomy for conjunctive queries** is known, but the picture for unions, aggregation, and approximation is open.

## 2. Mathematical Foundations

Tuples are partitioned into **endogenous** (manipulable) and **exogenous**. $t$ is a *counterfactual cause* if $Q(D)\neq Q(D\setminus\{t\})$. $t$ is an *actual cause* (contingent cause) if $\exists \Gamma \subseteq D_{\text{endo}}$ with $t\notin\Gamma$ such that $Q(D\setminus\Gamma)=Q(D)$ but $Q(D\setminus(\Gamma\cup\{t\}))\neq Q(D)$. **Responsibility** is
$$ \rho(t) = \frac{1}{1+\min\{|\Gamma| : \Gamma \text{ is a contingency set for } t\}}. $$

The query *lineage* $\lambda$ is a monotone Boolean formula; responsibility is the minimum number of other variables to fix so that $t$ becomes pivotal — equivalently a **minimum-weight implicant / vertex-cover-like** structure. The Meliou–Gatterbauer–Suciu dichotomy: for every CQ without self-joins, responsibility is either in **PTIME** or **NP-hard**, classified by query structure (a "linear" / hierarchical condition closely tied to the **safe-query** dichotomy of probabilistic databases by Dalvi–Suciu).

## 3. State of the Art (SOTA)

- **Meliou, Gatterbauer, Moore, Suciu (VLDB 2010; "The Complexity of Causality and Responsibility for Query Answers and Non-Answers")** — the defining paper; gives the CQ dichotomy.
- **Salimi, Bertossi, et al.** connected causality/responsibility to **database repairs** and consistency, and to the **Shapley value** for tuple contribution (Livshits, Bertossi, Kimelfeld, Sebag, "The Shapley Value of Tuples in Query Answering," ICDT 2020 / LMCS 2021).
- **Bertossi, Salimi (2017)** — causality, view-conditioned causes, and responsibility surveys.
- Systems: causality/intervention engines built atop provenance (e.g., extensions in GProM, and explanation tools in Roy–Suciu line).

## 4. Upper Bound

For **hierarchical / safe** self-join-free CQs, responsibility is computable in **PTIME** (the dichotomy's tractable side). General actual-cause checking is in **NP** (guess the contingency set, verify in PTIME). Responsibility as an optimization sits in **FP$^{NP}$**; for bounded contingency-set size $k$ it is **FPT**, $O^*(c^k)$. Shapley-value tuple contribution is computable in **PTIME for the same safe class** and admits an **FPRAS** in general via sampling.

## 5. Lower Bound

For non-hierarchical self-join-free CQs, responsibility is **NP-hard**, and as it captures **min vertex cover / min set cover** structures it is **APX-hard / inapproximable** below the corresponding constant or $\ln n$ thresholds for the relevant constructions. Actual-causality decision is **NP-complete** for unsafe CQs. The **Shapley value** of a tuple is **#P-hard** to compute exactly for non-hierarchical queries (Livshits et al.), mirroring the Dalvi–Suciu #P-hardness of unsafe query evaluation. Counting minimal contingency sets is **#P-hard**.

## 6. The Gap

The **decision/exact dichotomy for self-join-free CQs is closed**. Open gaps: (1) queries **with self-joins** — no full dichotomy; (2) **approximability of responsibility** on the hard side — the exact inapproximability constant is not pinned down; (3) **UCQs, aggregation, and negation**; (4) tight FPRAS-vs-inapproximability boundary for Shapley contribution beyond the hierarchical class. So the problem is genuinely *partially solved*.

## 7. Current Research (as of June 2026)

Hot directions: **Shapley- and Banzhaf-value** measures of tuple importance and their fine-grained complexity (Kimelfeld, Livshits, Bertossi groups), and **causality for ML and fairness over databases**. *(frontier — verify)* 2024–2025 work tightens **FPRAS / approximation** results for Banzhaf values and explores **knowledge-compilation (d-DNNF)** to make responsibility/Shapley tractable on circuit-bounded instances. Connections to **SHAP explanations** for tabular ML and to **database repairs under denial constraints** are active.

## 8. Future Work

- A causality/responsibility dichotomy for CQs *with* self-joins and for UCQs.
- Tight approximation thresholds and practical approximation algorithms for responsibility.
- Unified treatment of Shapley/Banzhaf/responsibility under one knowledge-compilation framework.
- Causality for aggregates, recursion, and probabilistic data.

## 9. Key References

- **[Foundational]** Halpern, Pearl. *Causes and Explanations: A Structural-Model Approach. Part I: Causes.* British J. Phil. Sci., 2005. — [DOI](https://doi.org/10.1093/bjps/axi147)
- **[SOTA]** Meliou, Gatterbauer, Moore, Suciu. *The Complexity of Causality and Responsibility for Query Answers and Non-Answers.* VLDB, 2010. — [arXiv](https://arxiv.org/abs/1009.2021) · [DOI](https://doi.org/10.14778/1880172.1880176)
- **[SOTA]** Livshits, Bertossi, Kimelfeld, Sebag. *The Shapley Value of Tuples in Query Answering.* ICDT, 2020 (LMCS, 2021). — [arXiv](https://arxiv.org/abs/1904.08679) · [DOI](https://doi.org/10.4230/LIPIcs.ICDT.2020.20)
- **[Foundational]** Dalvi, Suciu. *Efficient Query Evaluation on Probabilistic Databases.* VLDB Journal, 2007. — [DOI](https://doi.org/10.1007/s00778-006-0004-3)
- **[Survey]** Bertossi, Salimi. *From Causes for Database Queries to Repairs and Model-Based Diagnosis and Back.* Theory of Computing Systems, 2017. — [arXiv](https://arxiv.org/abs/1507.00257) · [DOI](https://doi.org/10.1007/s00224-016-9718-9)

## 10. Worked Example

Tables `R(A)` and `S(A)`, all tuples endogenous. Boolean query $Q :\!-\, R(x), S(x)$ (is there a shared value?).

| $R$ | | $S$ |
|----|---|----|
| $r_1: 1$ | | $s_1: 1$ |
| $r_2: 2$ | | $s_2: 2$ |
| $r_3: 3$ | | $s_3: 4$ |

$Q(D)=\text{true}$ via two witnesses, $\{r_1,s_1\}$ and $\{r_2,s_2\}$. Lineage: $\lambda = (r_1\wedge s_1)\vee(r_2\wedge s_2)$.

**Is $r_1$ a cause?** Removing $r_1$ alone leaves witness $\{r_2,s_2\}$, so $Q$ stays true — $r_1$ is *not counterfactual*. But take contingency set $\Gamma=\{r_2\}$ (or $\{s_2\}$): with $\Gamma$ gone, $Q(D\setminus\Gamma)$ is still true (via $r_1,s_1$), yet $Q(D\setminus(\Gamma\cup\{r_1\}))$ is false. So $r_1$ **is an actual cause** with minimal contingency set of size $1$.

**Responsibility:** $\rho(r_1)=\dfrac{1}{1+|\Gamma_{\min}|}=\dfrac{1}{1+1}=\tfrac12.$

By symmetry $\rho(r_2)=\rho(s_1)=\rho(s_2)=\tfrac12$, while $r_3,s_3$ contribute to no witness so they are non-causes ($\rho=0$). This self-join-free CQ is hierarchical, so all responsibilities are computed in PTIME — the tractable side of the Meliou–Gatterbauer–Suciu dichotomy. Adding a self-join (e.g. $R(x),R(y),S(x,y)$) is exactly where the dichotomy is still open.

---
*Part of the [DBMS Research catalog](../../README.md).*
