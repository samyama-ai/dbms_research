---
id: 22-provenance-lineage/deletion-propagation-approximability
title: "Deletion Propagation Approximability"
topic: 22-provenance-lineage
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Deletion Propagation Approximability

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/deletion-propagation-approximability` · **Status:** partially-solved
> **Verification note:** The Buneman–Khanna–Tan paper appeared at **PODS 2002** (DOI 10.1145/543613.543633), not ICDT 2002 as stated in sections 2–3.

## 1. Problem Statement

Given a database $D$, a monotone query/view $Q$, and a target answer $t \in Q(D)$, **deletion propagation** asks for a set $\Delta \subseteq D$ of source tuples whose deletion removes $t$ from the view, minimizing a side-effect objective:

- **View-Side-Effect (VSE):** minimize the number of *other* view tuples $Q(D)\setminus\{t\}$ collaterally lost.
- **Source-Side-Effect (SSE):** minimize $|\Delta|$ itself (number of source tuples deleted).

We seek **tight approximation thresholds** for both, classified by query structure.

Variants: single-target vs. multi-target deletion; weighted source/view tuples; the *group* version (delete a set of targets).

## 2. Mathematical Foundations

The view tuple's **lineage** is a monotone DNF $\lambda_t = \bigvee_w \bigwedge_{r\in w} x_r$ over source tuples. To delete $t$ we must falsify $\lambda_t$, i.e. choose $\Delta$ hitting **every** witness $w$ — a **minimum hitting set** over the witnesses (this is SSE). VSE instead minimizes how many *other* lineage formulas $\lambda_{t'}$ are simultaneously falsified, an objective with **set-cover / vertex-cover** combinatorial cores.

Buneman, Khanna, Tan (ICDT 2002) launched the complexity study; Kimelfeld, Vondrák, Williams (PODS 2011/2012) gave the **trichotomy/dichotomy** for VSE: for CQs without self-joins, the *head-domination* condition determines whether single-tuple VSE deletion propagation is **PTIME** or **APX-hard**, and they map the **constant-factor approximation thresholds**. SSE relates to vertex cover (2-approximable, but $(2-\varepsilon)$-hard under UGC). Submodularity of side-effect coverage underlies the greedy guarantees.

$$ \text{SSE: } \min |\Delta| \text{ s.t. } \lambda_t(D\setminus\Delta)=0; \qquad \text{VSE: } \min |\{t'\neq t : t'\notin Q(D\setminus\Delta)\}|. $$

## 3. State of the Art (SOTA)

- **Buneman, Khanna, Tan (ICDT 2002)** — *On Propagation of Deletions and Annotations Through Views*; first NP-hardness and tractable cases.
- **Kimelfeld, Vondrák, Williams (PODS 2011; JACM/TODS follow-ups)** — *Maximizing Conjunctive Views in Deletion Propagation*; the definitive **dichotomy** for VSE on self-join-free CQs, with approximation classification (PTIME, constant-factor, or APX-hard via head domination).
- **Kimelfeld (2012)** — a dichotomy for the *multi-tuple* / functional-dependency setting.
- **Freire, Gatterbauer, Immerman, Meliou (VLDB 2015)** — *resilience* of queries (a clean variant of source-side deletion / minimum-witness removal) with a dichotomy for self-join-free CQs and progress on self-joins.

## 4. Upper Bound

For self-join-free CQs satisfying head domination, VSE is in **PTIME**; otherwise a **constant-factor approximation** is achievable for many cases via LP-rounding/greedy submodular maximization (the complementary "maximize retained views" objective is monotone submodular, giving a **$1-1/e$** guarantee). SSE / resilience for safe self-join-free CQs is **PTIME** (max-flow / vertex-cover-structured); general SSE is **2-approximable** when it reduces to vertex cover.

## 5. Lower Bound

VSE deletion propagation is **NP-hard and APX-hard** for self-join-free CQs violating head domination (reductions from vertex cover / max-coverage), so no PTAS exists unless P = NP. SSE generalizes **minimum vertex cover**, hence **NP-hard** and **$(2-\varepsilon)$-inapproximable under the Unique Games Conjecture**. With self-joins, resilience/SSE can become harder; some self-join cases are conjectured (and partially shown) to remain at the dichotomy boundary, with the **complete self-join classification still open**.

## 6. The Gap

For **self-join-free CQs**, VSE and resilience/SSE are **essentially closed** (dichotomy + matching approximation thresholds). The **open** part: (1) a complete classification **with self-joins**; (2) sharp VSE approximation ratios in the APX-hard regime (gap between the best $1-1/e$/constant upper bounds and the APX-hardness constant); (3) **multi-target / weighted** variants. Hence *partially solved*.

## 7. Current Research (as of June 2026)

Active: **resilience with self-joins** (Gatterbauer, Meliou, Makhija) — recent papers push the dichotomy into self-join territory and connect resilience to **causal responsibility** and **unique-witness** structure. *(frontier — verify)* 2024–2025 work uses **integer-programming / FAQ-style** formulations and **information-theoretic (Shannon-flow) lower bounds** to characterize resilience, and ties deletion propagation to the broader **reverse data management** dichotomy program. Approximation via **submodular and LP-hierarchy** methods is being sharpened.

## 8. Future Work

- Complete the self-join dichotomy for VSE, SSE, and resilience.
- Pin down exact approximation constants in APX-hard regimes.
- Weighted, multi-target, and constraint-aware (FD/inclusion) variants.
- Practical engines integrating deletion propagation with provenance circuits.

## 9. Key References

- **[Foundational]** Buneman, Khanna, Tan. *On Propagation of Deletions and Annotations Through Views.* PODS, 2002. — [DOI](https://doi.org/10.1145/543613.543633)
- **[SOTA]** Kimelfeld, Vondrák, Williams. *Maximizing Conjunctive Views in Deletion Propagation.* PODS, 2011 (ACM TODS, 2012). — [DOI (PODS)](https://doi.org/10.1145/1989284.1989308) · [DOI (TODS)](https://doi.org/10.1145/2389241.2389243)
- **[SOTA]** Freire, Gatterbauer, Immerman, Meliou. *The Complexity of Resilience and Responsibility for Self-Join-Free Conjunctive Queries.* VLDB, 2015. — [arXiv](https://arxiv.org/abs/1507.00674) · [DOI](https://doi.org/10.14778/2850583.2850594)
- **[Foundational]** Cong, Fan, Geerts. *Annotation Propagation Revisited for Key Preserving Views.* CIKM, 2006. — [DOI](https://doi.org/10.1145/1183614.1183705)
- **[Survey]** Cheney, Chiticariu, Tan. *Provenance in Databases: Why, How, and Where.* Foundations and Trends in Databases, 2009. — [DOI](https://doi.org/10.1561/1900000006)

## 10. Worked Example

View `Q :- Author(a), Wrote(a,p), Paper(p,'DB')` over a tiny instance. Target view tuple $t$ is produced by three witnesses (each an author–paper pair on a DB paper):

$$ \lambda_t = (a_1\wedge w_1\wedge p_1)\;\vee\;(a_1\wedge w_2\wedge p_2)\;\vee\;(a_2\wedge w_3\wedge p_2). $$

**SSE (source side effect): minimum deletion to kill $t$.** We must falsify *every* clause — a minimum hitting set over the three witnesses. Deleting the single source tuple $a_1$ kills clauses 1 and 2; we still need clause 3, killed by deleting e.g. $p_2$. So $\Delta=\{a_1,p_2\}$, $|\Delta|=2$. But note $p_2$ alone hits clauses 2 and 3, leaving clause 1 (needs $a_1$ or $w_1$ or $p_1$) — also size 2. The optimum here is $|\Delta_{\min}|=2$.

**VSE (view side effect).** If another view tuple $t'$ has lineage that also uses $p_2$, then deleting $p_2$ collaterally removes $t'$ — a side effect VSE tries to minimize. Choosing $\Delta=\{a_1,w_3\}$ instead might avoid touching $t'$.

The hitting-set core makes SSE generalize **minimum vertex cover**: $2$-approximable, but $(2-\varepsilon)$-inapproximable under UGC. Whether *this* query is PTIME hinges on its structure (head domination / triad-freeness) — the dichotomy's dividing line.

---
*Part of the [DBMS Research catalog](../../README.md).*
