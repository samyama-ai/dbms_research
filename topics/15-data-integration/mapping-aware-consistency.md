---
id: 15-data-integration/mapping-aware-consistency
title: "Mapping-Aware Consistency Repair"
topic: 15-data-integration
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Mapping-Aware Consistency Repair

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/mapping-aware-consistency` · **Status:** open

## 1. Problem Statement

In **data exchange**, a source instance $S$ is translated into a target instance via schema mappings $\Sigma_{st}$ (source-to-target TGDs), and the target must additionally satisfy **target constraints** $\Sigma_t$ (target TGDs and **equality-generating dependencies / EGDs**, i.e. keys and functional dependencies). The chase that materializes the target can **introduce constraint violations** (EGD failures, key clashes) that are not repairable by adding tuples — they require **value identification or deletion**, i.e., a *repair*.

The open problem: **jointly repair target-constraint violations introduced by exchange while preserving certain answers** of queries over the original mapping semantics. A naive repair (à la standard *consistent query answering*, CQA) treats the target as a flat dirty instance and ignores that its tuples carry **labeled nulls and provenance from the mapping** — so it can destroy information that the mapping certifies. We want repairs $J'$ that (a) satisfy $\Sigma_t$, (b) stay a **solution** for $(S,\Sigma_{st})$ as much as possible, and (c) **preserve $\mathsf{cert}(Q,S,\Sigma)$** for a query class $Q$.

Variants: **decision** (does a repair preserving certain answers exist?); **optimization** (minimum-cost / cardinality-minimal repair); **certain-answers-over-repairs** (what holds in *all* such repairs — a CQA semantics layered on data exchange).

## 2. Mathematical Foundations

The setting is **Fagin–Kolaitis–Miller–Popa data exchange**: solutions are target instances $J$ with $(S,J)\models\Sigma_{st}$ and $J\models\Sigma_t$; the **canonical universal solution** is produced by the chase, and $\mathsf{cert}(Q,S)=\bigcap\{Q(J)\}$ equals $Q$ evaluated on the core universal solution (for UCQs). With **EGDs in $\Sigma_t$**, the chase may **fail** (try to equate two distinct constants) — there is then *no* solution, and one must **repair**.

This fuses two theories: **data exchange / the chase** (Fagin et al., TCS 2005; cores, Gottlob–Nash) and **consistent query answering** (Arenas–Bertossi–Chomicki, PODS 1999) — $\mathsf{cert}(Q)$ over the set of minimal repairs. Key objects: **labeled nulls** (the repair may *instantiate* a null rather than delete a tuple — a degree of freedom absent in classical CQA), **provenance semirings** (Green–Karvounarakis–Tannen) to track which mapping firings justify each tuple, and **repair lattices** ordered by subset/symmetric-difference. Certain answers under repairs become $\bigcap_{J' \in \mathsf{Rep}} Q(J')$, a **doubly-universal** quantification (over solutions and over repairs).

## 3. State of the Art (SOTA)

- **Foundational.** Fagin, Kolaitis, Miller, Popa — *Data Exchange: Semantics and Query Answering* (TCS 2005); Fagin, Kolaitis, Popa — *Data Exchange: Getting to the Core* (TODS 2005). Arenas, Bertossi, Chomicki — *Consistent Query Answers in Inconsistent Databases* (PODS 1999).
- **Repair + exchange.** ten Cate, Fontaine, Kolaitis — *On the Data Complexity of Consistent Query Answering* (ICDT 2012). Afrati, Kolaitis — *Repair Checking in Inconsistent Databases* (ICDT 2009). Bertossi — *Database Repairing and Consistent Query Answering* (Morgan & Claypool, 2011).
- **Systems.** **Llunatic** (Geerts, Mecca, Papotti, Santoro, VLDB 2013–2014) — a chase-based engine that *unifies* mapping enforcement and cleaning (EGD repair with "cell groups"), the closest practical realization. **HoloClean** (Rekatsinas et al., VLDB 2017) — probabilistic repair, but mapping-agnostic.

## 4. Upper Bound

For restricted classes the problem is decidable with known data complexity. With **weakly-acyclic $\Sigma_{st}\cup\Sigma_t$** the chase terminates in PTIME data complexity; **CQA over the resulting repairs for UCQs and key/FD constraints** is in **$\mathrm{coNP}$ (data complexity)** and PTIME for the well-behaved subclasses (e.g., primary-key constraints with the "consistent answers via conflict hypergraph" approach of Koutris–Wijsen, where dichotomies give PTIME vs. coNP-complete). **Llunatic** computes a representative repair (the *upgrade* of the chase with cell-group resolution) in PTIME under acyclicity assumptions, the systems upper bound. Minimum-cardinality repair is approximable via vertex-cover-style $2$-approximations on the conflict hypergraph for binary EGD conflicts.

## 5. Lower Bound

Even ignoring mappings, **CQA is $\mathrm{coNP}$-complete in data complexity** for general FDs (Chomicki–Marcinkowski; Koutris–Wijsen establish a **PTIME/coNP-complete dichotomy** for self-join-free conjunctive queries under primary keys — many queries are coNP-complete). **Minimum-cardinality repair** under FDs is **NP-hard** and **APX-hard**. Adding target TGDs to $\Sigma_t$ can make solution existence undecidable (general TGDs), and combining EGDs + TGDs in the chase yields **undecidable** consistency in the general case. Thus mapping-aware CQA inherits coNP-hardness from CQA *and* undecidability from unrestricted data exchange — the combination is strictly at least as hard as each.

## 6. The Gap

This is **genuinely open**. CQA and data exchange are each well-understood *in isolation*, but their **interaction is largely uncharted**: (1) no agreed semantics for "repair that preserves certain answers" when tuples carry labeled nulls (repair-by-null-instantiation vs. deletion changes the answer); (2) no complexity classification of **certain-answers-over-repairs in data exchange** beyond fragments; (3) systems (Llunatic) provide *a* repair but **no certain-answer guarantee** across all repairs; (4) the dichotomy theorems (Koutris–Wijsen) do not yet extend to the **null-bearing, provenance-annotated** instances exchange produces. Closing it needs a unified semantics + a complexity map (dichotomies) for mapping-aware repair and certain answering.

## 7. Current Research (as of June 2026)

- Extending the **Koutris–Wijsen CQA dichotomy** to instances with labeled nulls / under mappings. *(frontier — verify)*
- **Provenance-guided repair**: using semiring provenance to choose repairs that maximally preserve certified query answers (Tannen, Geerts, Senellart lines). *(frontier — verify)*
- **Probabilistic / learned repair under mappings** (HoloClean successors) made *mapping- and certain-answer-aware*. *(frontier — verify)*
- Chase-based unified cleaning at scale (Llunatic successors; *(frontier — verify)*) and connections to **certain answers under existential rules**.

## 8. Future Work

- A canonical semantics for repairs preserving certain answers in data exchange.
- Complexity dichotomies (PTIME vs. coNP-complete) for mapping-aware CQA with keys/FDs and nulls.
- Approximation algorithms with provenance-aware cost models; minimum-information-loss repairs.
- Practical engines that emit *certified* consistent answers, not just one repaired instance.

## 9. Key References

- **[Foundational]** R. Fagin, P. G. Kolaitis, R. J. Miller, L. Popa. *Data Exchange: Semantics and Query Answering.* TCS, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[Foundational]** R. Fagin, P. G. Kolaitis, L. Popa. *Data Exchange: Getting to the Core.* ACM TODS, 2005. — [DOI](https://doi.org/10.1145/1061318.1061323)
- **[Foundational]** M. Arenas, L. Bertossi, J. Chomicki. *Consistent Query Answers in Inconsistent Databases.* PODS, 1999. — [DOI](https://doi.org/10.1145/303976.303983)
- **[SOTA]** P. Koutris, J. Wijsen. *The Data Complexity of Consistent Query Answering for Self-Join-Free Conjunctive Queries under Primary Key Constraints.* PODS / ACM TODS, 2015–2017. (Dichotomy.) — [DOI](https://doi.org/10.1145/3068334)
- **[SOTA]** F. Geerts, G. Mecca, P. Papotti, D. Santoro. *The LLUNATIC Data-Cleaning Framework.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2536360.2536363)
- **[Foundational]** T. J. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Survey]** L. Bertossi. *Database Repairing and Consistent Query Answering.* Morgan & Claypool, 2011. — [DOI](https://doi.org/10.2200/S00379ED1V01Y201108DTM020)

## 10. Worked Example

Source $S$ has $\mathsf{Emp}(\text{name}, \text{dept})$ with two rows: $\mathsf{Emp}(\text{Ann}, \text{Sales})$, $\mathsf{Emp}(\text{Ann}, \text{Eng})$. The st-tgd is
$$\mathsf{Emp}(n,d) \rightarrow \exists o\,\, \mathsf{Target}(n, d, o)$$
The chase produces $\mathsf{Target}(\text{Ann}, \text{Sales}, N_1)$ and $\mathsf{Target}(\text{Ann}, \text{Eng}, N_2)$ with labeled nulls $N_1, N_2$ (office). Now add a target EGD: $\text{name}$ is a key, i.e. $\mathsf{Target}(n,d_1,o_1) \wedge \mathsf{Target}(n,d_2,o_2) \rightarrow d_1 = d_2$. The EGD tries to equate the constants $\text{Sales} = \text{Eng}$ — a **hard failure**: no solution exists, so we must repair.

Two minimal repairs delete one tuple each: $J_1 = \{\mathsf{Target}(\text{Ann},\text{Sales},N_1)\}$ or $J_2 = \{\mathsf{Target}(\text{Ann},\text{Eng},N_2)\}$. For query $Q(n) \leftarrow \mathsf{Target}(n,\_,\_)$, both repairs return $\text{Ann}$, so $\mathsf{cert}(Q) = \{\text{Ann}\}$ survives. But for $Q'(d) \leftarrow \mathsf{Target}(\text{Ann},d,\_)$, $J_1 \cap J_2$ gives $\emptyset$ — the dept is **not** certain. This shows repair choice destroys mapping-certified info that flat CQA cannot see.

---
*Part of the [DBMS Research catalog](../../README.md).*
