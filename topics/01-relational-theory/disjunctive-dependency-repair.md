---
id: 01-relational-theory/disjunctive-dependency-repair
title: "Disjunctive and Existential Dependency Repair"
topic: 01-relational-theory
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Disjunctive and Existential Dependency Repair

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/disjunctive-dependency-repair` · **Status:** open

## 1. Problem Statement

Given a database instance $D$ that violates a set $\Sigma$ of integrity constraints, a *repair* is a database $D'$ that satisfies $\Sigma$ and differs from $D$ "minimally" (under subset, symmetric-difference, or cardinality minimality, or attribute-update minimality). Classical repair work targets *denial constraints* (DCs) and functional dependencies, where repairs are obtained by tuple deletion. This problem concerns repair when $\Sigma$ simultaneously contains:

- **Disjunctive existential rules** (disjunctive tuple-generating dependencies, *disjunctive TGDs*): $\forall \bar{x}\,\big(\varphi(\bar{x}) \to \bigvee_{i=1}^{k} \exists \bar{y}_i\, \psi_i(\bar{x},\bar{y}_i)\big)$, which *force* facts (and fresh nulls) into the instance and offer disjunctive choices; and
- **Denial constraints / negative constraints**, which *forbid* combinations of facts.

Because existential rules add tuples while DCs demand deletions, a repair must interleave insertions, deletions, and the choice of disjuncts. The decision problems are:

- **Repair existence**: does any $\Sigma$-satisfying $D'$ within the chosen minimality bound exist?
- **Repair checking**: given $D'$, is it a minimal repair of $(D,\Sigma)$?
- **Consistent query answering (CQA)** / **certain repair answers**: is a tuple in the answer of $Q$ on *every* minimal repair?

Optimization variants ask for a *minimum-cost* repair under weighted edit operations.

## 2. Mathematical Foundations

The semantic backbone is the **disjunctive chase**. Firing a disjunctive TGD on a trigger produces a *set* of possible successor instances (one per disjunct), so a chase tree, not a chase sequence, results; models correspond to leaves. The relevant notions:

$$\mathrm{chase}^{\vee}(D,\Sigma) = \text{a tree whose branches are candidate (universal) models.}$$

Repairs live in the lattice of instances ordered by $\subseteq$ or by symmetric difference $\triangle$ to $D$. Existential rules with disjunction subsume the **disjunctive embedded dependencies**; combined with DCs they capture **Disjunctive Existential Rules + Negative Constraints**, the logical core of ontology-mediated querying (Datalog$^{\pm}$, DL-Lite$_{\text{bool}}$).

Key results this rests on: undecidability of TGD entailment in general; decidability for guarded / frontier-guarded / sticky / weakly-acyclic fragments; the *coNP-completeness* of repair checking and *$\Pi_2^p$* phenomena for CQA under DCs; and the closed/open-world distinction governing whether existential witnesses may be invented.

## 3. State of the Art (SOTA)

- **CQA under denial constraints / FDs** is mature: Arenas–Bertossi–Chomicki (PODS 1999) launched it; the **LinCQA / FastFO** rewriting line (Koutris–Wijsen, and Figueira et al.) gives first-order/linear-time CQA for self-join-free CQs under primary keys via the celebrated **$P$/$coNP$ dichotomy** (Koutris–Wijsen, *TODS* 2017–2021).
- **Existential-rule repair** is far less settled. ChaseFUN/Graal and **VLog/Rulewerk** engines support disjunctive chase but treat consistency, not minimal repair. Theoretical treatments of repairs under TGDs+NCs appear in work on *inconsistency-tolerant* ontology query answering (Lembo–Lenzerini–Rosati–Ruzzi–Savo; Bienvenu).
- No production system computes minimal repairs under disjunctive TGDs *together with* DCs.

## 4. Upper Bound

For **guarded** or **weakly-acyclic** disjunctive TGDs plus DCs, the disjunctive chase terminates, models are finite, and CQA is decidable in **$\Pi_2^p$** (combined: up to **2ExpTime** for expressive guarded fragments). Repair checking under subset-minimality with terminating chase is in **coNP** (data complexity). Brave/possible answers are in **$\Sigma_2^p$**. These hold in the standard *finite-model / terminating-chase* model.

## 5. Lower Bound

CQA under DCs alone is already **$\Pi_2^p$-hard** (combined) and **coNP-hard** in data complexity for many constraint classes. Adding disjunction inherits the **$\Pi_2^p$** hardness of disjunctive Datalog reasoning (Eiter–Gottlob–Mannila). For non-terminating fragments, repair existence with arbitrary TGDs is **undecidable** (reduction from TGD entailment / the implication problem). Thus the *general* problem has no algorithm; hardness is information-theoretic/recursion-theoretic, not merely complexity-theoretic.

## 6. The Gap

For *unrestricted* disjunctive existential rules + DCs the problem is **open and partly undecidable**: there is no agreed decidable fragment that captures both insertion-forcing existential disjunction and deletion-forcing denials with a *minimal-repair* semantics, and no dichotomy theorem analogous to Koutris–Wijsen. The gap is qualitative (decidability frontier) before it is quantitative (complexity tightness). Closing it requires either a syntactic fragment with a terminating disjunctive chase admitting a repair lattice with finite minimal elements, or an impossibility proof.

## 7. Current Research (as of June 2026)

- **Bienvenu, Bourgaux** and collaborators: inconsistency-tolerant semantics (AR, IAR, brave) lifted toward existential rules and explanation of repairs.
- **Koutris, Wijsen, Figueira, Kimelfeld**: extending the CQA dichotomy beyond keys toward FDs and toward counting repairs (`#CQA`).
- **Calautti, Console, Pieris**: probabilistic and counting variants of repair under existential rules. *(frontier — verify)* Recent work on *operational* (cost-based) repair semantics unifying insertions/deletions for Datalog$^\pm$.
- ASP-based solvers (clingo encodings of repairs) are the practical workhorse for disjunctive cases.

## 8. Future Work

- A **dichotomy** (P vs. coNP-hard) for CQA under disjunctive existential rules + DCs over restricted query/constraint classes.
- Terminating **disjunctive-chase fragments** with provably finite minimal-repair sets.
- **Cost/preference-aware** repairs unifying insert, delete, and disjunct choice.
- Scalable solvers beyond grounding-heavy ASP; incremental repair under updates.

## 9. Key References

- **[Foundational]** Arenas, M., Bertossi, L., Chomicki, J. *Consistent Query Answers in Inconsistent Databases.* PODS, 1999. — [DOI](https://doi.org/10.1145/303976.303983)
- **[Foundational]** Eiter, T., Gottlob, G., Mannila, H. *Disjunctive Datalog.* ACM TODS, 1997. — [DOI](https://doi.org/10.1145/261124.261126)
- **[SOTA]** Koutris, P., Wijsen, J. *Consistent Query Answering for Primary Keys.* ACM TODS, 2017–2021. — [DOI](https://doi.org/10.1145/3068334)
- **[Survey]** Bertossi, L. *Database Repairing and Consistent Query Answering.* Morgan & Claypool Synthesis Lectures, 2011. — [DOI](https://doi.org/10.2200/S00379ED1V01Y201108DTM020)
- **[Survey]** Bienvenu, M., Bourgaux, C. *Inconsistency-Tolerant Querying of Description Logic Knowledge Bases.* Reasoning Web, 2016. — [DOI](https://doi.org/10.1007/978-3-319-49493-7_5)
- **[Foundational]** Calì, A., Gottlob, G., Pieris, A. *Towards More Expressive Ontology Languages: The Query Answering Problem (Datalog±).* Artificial Intelligence, 2012. — [DOI](https://doi.org/10.1016/j.artint.2012.08.002)

## 10. Worked Example

Instance $D=\{\text{Phone}(\text{alice})\}$. Constraints:
- disjunctive TGD $\sigma$: $\text{Phone}(p)\to \text{Mobile}(p)\vee \text{Landline}(p)$ (every phone is mobile or landline);
- denial constraint $\delta$: $\bot\leftarrow \text{Landline}(\text{alice})$ (alice cannot have a landline — say a known fact).

The disjunctive chase on $\sigma$ branches:
- **Branch A:** add $\text{Mobile}(\text{alice})$ — satisfies $\delta$.
- **Branch B:** add $\text{Landline}(\text{alice})$ — violates $\delta$; to restore consistency the repair must *delete* $\text{Phone}(\text{alice})$ (or the landline fact), giving $D'_B=\emptyset$.

Under subset/symmetric-difference minimality, the repairs are $D'_A=\{\text{Phone}(\text{alice}),\text{Mobile}(\text{alice})\}$ and $D'_B=\{\}$ (delete to dodge the denial). For CQA of $Q()\leftarrow\text{Phone}(x)$: it holds in $D'_A$ but not $D'_B$, so the **certain** answer is *false* — even though $D$ asserted Phone(alice). This interleaving of forced insertion (the disjunct) with forced deletion (the denial) is exactly what makes minimal-repair semantics under disjunctive rules + DCs open.

---
*Part of the [DBMS Research catalog](../../README.md).*
