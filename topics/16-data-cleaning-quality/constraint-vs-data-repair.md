---
id: 16-data-cleaning-quality/constraint-vs-data-repair
title: "Constraint Repair Itself"
topic: 16-data-cleaning-quality
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Constraint Repair Itself

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/constraint-vs-data-repair` · **Status:** partially-solved

## 1. Problem Statement

Classical data cleaning treats the constraint set $\Sigma$ as ground truth and repairs the data $D$ to satisfy it. But constraints are themselves authored by humans, mined from samples, or copied from legacy schemas — and they are frequently *wrong, stale, or over-specified*. When $D \not\models \Sigma$, the violation may indicate dirty data **or** an incorrect constraint.

The problem is to decide, for each violation, whether to **repair the data**, **repair the constraint** (the *constraint/schema repair* a.k.a. *constraint relaxation/discovery-refinement* problem), or do a mixture — and to do so optimally under a joint cost.

Variants:
- **Decision:** Given budgets $(b_D, b_\Sigma)$, is there a pair $(D', \Sigma')$ with $D' \models \Sigma'$, $\Delta(D,D') \le b_D$, $\Delta(\Sigma, \Sigma') \le b_\Sigma$?
- **Optimization (joint min-cost):** Minimize $\alpha\,\Delta(D,D') + \beta\,\Delta(\Sigma,\Sigma')$ subject to $D' \models \Sigma'$.
- **Constraint-only repair:** Fix $D$, find the minimal modification of $\Sigma$ (drop, weaken, add antecedent literals) that restores consistency / desired generality.

## 2. Mathematical Foundations

Let $\Sigma$ be FDs/CFDs/DCs over schema $R$. A DC has form $\forall t_i,t_j: \neg(p_1 \wedge \cdots \wedge p_m)$ over predicates $p$. **Constraint repair** operates in the lattice of constraints: weakening a CFD by generalizing its pattern tuple, adding a predicate to a DC's antecedent (making it harder to violate), or removing a rule. This is dual to data repair, which moves $D$ in the lattice of instances.

Formally this is a **bi-level / joint optimization** over two interacting cost spaces. Connections:
- **Constraint implication & the chase:** deciding redundancy/minimality of $\Sigma'$ uses FD closure ($\Sigma^+$) and chase termination.
- **Confidence/support semantics:** mined constraints carry support $s(\phi)$ and confidence $c(\phi)$; "repair the constraint" is favored when its empirical confidence is low.
- **MDL framing:** choose $(D',\Sigma')$ minimizing $L(\Sigma') + L(D' \mid \Sigma') + L(\text{edits})$ — penalizing both convoluted constraints and heavy data edits.
- **G3/error-of-a-dependency** measures (Kivinen–Mannila) quantify how far $D$ is from satisfying $\phi$, guiding the data-vs-constraint choice.

## 3. State of the Art (SOTA)

- **Approximate / soft constraint discovery:** mining FDs/CFDs/DCs that hold *approximately* (Pena, Almeida, Naumann — VLDB 2019/2020; FastDC by Chu, Ilyas, Papotti — VLDB 2013) already implies the constraint may be wrong on a few tuples, blurring data vs. constraint error.
- **Unified data+constraint repair:** Chiang & Miller, *Unified Repair of Data and Constraints* (SIGMOD 2011 / VLDB) is the canonical formulation jointly modifying CFDs and data.
- **Continuous/incremental discovery** under data evolution (Schirmer, Papenbrock, Naumann — "DynFD", 2019) detects when a constraint should be retired.
- Interactive systems (e.g., **UGuide**, Thirumuruganathan et al.) solicit user feedback to disambiguate which side to fix.

## 4. Upper Bound

For CFDs, Chiang & Miller give heuristic algorithms that explore data and constraint modifications jointly; cost is dominated by candidate enumeration and is polynomial per candidate but exponential in the worst case over constraint-modification space. For the restricted *constraint-relaxation-only* problem (drop or generalize rules to admit a fixed dirty instance), greedy set-cover-style algorithms achieve $O(\log n)$ approximation when "cover the violations by removing rules" is cast as weighted set cover. Approximate-FD discovery (TANE-style) is exponential in schema arity but polynomial in tuples for fixed arity.

## 5. Lower Bound

The joint min-cost problem is **NP-hard**: it contains classical min-cost data repair (NP-hard for two FDs; Kolahi–Lakshmanan ICDT 2009) as the special case $\beta = \infty$. The constraint-side reduces to **minimum-cover / hitting-set** style problems, which are NP-hard and **$(1-o(1))\ln n$-inapproximable** under $\mathsf{P}\ne\mathsf{NP}$ (Dinur–Steurer). Discovery of all minimal FDs is **exponential** in the number of attributes in the worst case (the number of minimal FDs can be exponential), an unconditional output-size lower bound. No fine-grained conditional tightness is established for the joint problem.

## 6. The Gap

This is why the status is **partially-solved**: practical joint frameworks (Chiang–Miller and successors) exist and work on CFDs, and the hardness landscape is mapped (NP-hard, log-inapproximable). But the gap between the $O(\log n)$ cover-style upper bound and the $\ln n$ lower bound is essentially *closed up to constants* only for the relaxation-only variant; the **full joint** optimization has no matching approximation guarantee and no agreed model for the relative weights $\alpha,\beta$. Choosing $\alpha,\beta$ — i.e., a *prior* on whether humans or data are more trustworthy — is unresolved and largely empirical.

## 7. Current Research (as of June 2026)

Directions: (i) confidence-weighted joint repair where mined-constraint confidence directly sets the cost of editing that constraint; (ii) LLM-assisted constraint critique — using language models to judge whether a violated DC is *semantically* sensible *(frontier — verify)*; (iii) drift-aware constraint maintenance for streaming/evolving schemas. Active groups: Naumann/Papenbrock (HPI Potsdam) on discovery and maintenance, Miller (Northeastern) and Chiang (TU Dortmund) on unified repair, Ilyas/Chu lineage on DC discovery. Interactive/active-learning to allocate the human budget across the two sides is an open thread *(frontier — verify)*.

## 8. Future Work

- Approximation algorithm with provable guarantee for the *full* joint $(\alpha,\beta)$ objective.
- Principled, calibrated priors for trusting constraints vs. data (e.g., Bayesian over $\Sigma$).
- Constraint repair for richer languages (DCs with aggregation, temporal constraints).
- Online constraint repair with regret bounds under data drift.

## 9. Key References

- **[Foundational]** Kivinen, Mannila. *Approximate Inference of Functional Dependencies from Relations.* Theoretical Computer Science, 1995. — [DOI](https://doi.org/10.1016/0304-3975(95)00028-U)
- **[Foundational]** Kolahi, Lakshmanan. *On Approximating Optimum Repairs for Functional Dependency Violations.* ICDT, 2009. — [DOI](https://doi.org/10.1145/1514894.1514901)
- **[SOTA]** Chiang, Miller. *A Unified Model for Data and Constraint Repair.* ICDE, 2011. — [DOI](https://doi.org/10.1109/ICDE.2011.5767833)
- **[SOTA]** Chu, Ilyas, Papotti. *Discovering Denial Constraints.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2536258.2536262)
- **[SOTA]** Pena, de Almeida, Naumann. *Discovery of Approximate (and Exact) Denial Constraints.* VLDB, 2019. — [DOI](https://doi.org/10.14778/3368289.3368293)
- **[Survey]** Abedjan, Golab, Naumann, Papenbrock. *Data Profiling.* Morgan & Claypool, 2018. — [DOI](https://doi.org/10.1007/978-3-031-01865-7)

## 10. Worked Example

Mined FD $\phi:\ \text{zip}\to\text{city}$ over $D$ (4 tuples):

| id | zip   | city    |
|----|-------|---------|
| 1  | 10001 | NYC     |
| 2  | 10001 | NYC     |
| 3  | 10001 | NYC     |
| 4  | 10001 | Newark  |

Tuple 4 violates $\phi$. Two repairs compete. **Data repair:** change $\text{city}_4$ to NYC — cost $\alpha\cdot 1$ (one cell edit). **Constraint repair:** drop or weaken $\phi$ — cost $\beta\cdot 1$.

Which is right depends on the confidence of $\phi$. The G3 error (fraction of tuples to delete to satisfy $\phi$) is $1/4=0.25$, and empirical confidence $\approx 3/4$. With 3 of 4 tuples agreeing, $\phi$ looks *mostly* real, so if $\alpha < 3\beta$ the joint objective $\alpha\Delta(D,D')+\beta\Delta(\Sigma,\Sigma')$ favors editing the single outlier. But had the split been 2-2, confidence drops to $0.5$ and constraint repair (raise $\beta$ effectively cheaper) wins. The unresolved question (Section 6) is precisely how to calibrate $\alpha,\beta$ from such evidence.

---
*Part of the [DBMS Research catalog](../../README.md).*
