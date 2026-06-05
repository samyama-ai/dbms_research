# Reverse Data Management Tractability

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/reverse-data-management-tractability` · **Status:** open

## 1. Problem Statement

*Reverse data management* (RDM) inverts the classic forward pipeline: instead of "given data and a query, compute the answer," it asks "given a desired property of the **output**, find a minimal **modification of the input** that achieves it." This subsumes **how-to** queries (Tiresias), **what-if** analysis, deletion propagation, why-not, and constraint-based repair. The open problem is a **dichotomy**: a complete map classifying RDM update problems as **PTIME** versus **intractable** (NP-hard / inapproximable / undecidable), as a function of the query class, the update operations allowed, and the **objective**, thereby *generalizing the deletion-propagation dichotomy to arbitrary objectives*.

Variants: minimize update size / cost (optimization); decide feasibility (decision); count solutions (counting); produce a Pareto frontier under multiple objectives.

## 2. Mathematical Foundations

Meliou, Gatterbauer, Suciu (2011) framed RDM as: given source $D$, query $Q$, and an *objective* $\Phi$ on $Q(D')$, find $D'$ reachable from $D$ by allowed updates $U$ minimizing $\text{dist}(D,D')$ subject to $\Phi(Q(D'))$. The forward map $Q$ is generally many-to-one and non-invertible, so RDM is an **inverse / abductive optimization**.

Special cases anchor the theory:
- **Deletion propagation** = RDM with deletions and objective "$t \notin Q(D')$" (dichotomy known for self-join-free CQs).
- **How-to queries** (Tiresias, Meliou–Suciu SIGMOD 2012) compile RDM into **mixed-integer programming** over a *provenance/lineage* encoding; tractability hinges on the lineage formula's structure.
- **Resilience, causal responsibility, why-not** are objective-instantiations of RDM.

Formally, with provenance polynomial $p_t \in \mathbb{N}[X]$ per output tuple, an RDM instance becomes a constrained optimization over $\{0,1\}^{|D|}$:
$$ \min_{x\in\{0,1\}^{|D|}} \text{cost}(x)\ \text{ s.t. } \Phi\big(\{t : p_t(x)\neq 0\}\big)\ \text{holds}. $$
Tractability is governed by whether this program is **totally unimodular / submodular / hierarchical** (PTIME) or encodes vertex-cover/set-cover/3SAT (intractable). The hoped-for dichotomy generalizes Dalvi–Suciu safety and the Kimelfeld–Vondrák–Williams head-domination condition.

## 3. State of the Art (SOTA)

- **Meliou, Gatterbauer, Suciu (CIDR 2011)** — *Reverse Data Management*; the vision and framework.
- **Meliou, Suciu (SIGMOD 2012)** — *Tiresias: The Database Oracle for How-To Queries*; systems-SOTA, MILP-based engine.
- **Kimelfeld, Vondrák, Williams (PODS 2011)** and **Freire et al. (VLDB 2015)** — dichotomies for the deletion/resilience sub-cases (theory-SOTA for special objectives).
- **Deutch, Ives, Milo, Tan (and others)** — provenance-for-updates and *interactive what-if* lineage tooling.
- No general RDM dichotomy exists; results are objective-specific.

## 4. Upper Bound

When the per-objective program is **submodular minimization** or reduces to **min-cut / matching**, RDM is in **PTIME** (e.g., safe/hierarchical CQ deletion). General how-to queries are solved by **MILP** (worst-case exponential, but practical via solvers). For monotone objectives with bounded fix size $k$, RDM is **FPT** ($O^*(c^k)$). Where the lineage is a **read-once / hierarchical** formula, exact polynomial algorithms via knowledge compilation (d-DNNF / OBDD) apply.

## 5. Lower Bound

RDM is **NP-hard** as soon as the objective encodes deletion propagation on a non-head-dominated CQ or a set-cover/vertex-cover structure; correspondingly **APX-hard** or **$\ln n$-inapproximable** in those regimes. With multiple objectives or aggregate constraints it reaches **$\Sigma_2^p$**, and under recursion + integrity constraints (chase non-termination) feasibility can be **undecidable**. Counting solutions is **#P-hard** (subsumes Dalvi–Suciu unsafe-query #P-hardness). These are *conditional* per-objective lower bounds, not a unified frontier.

## 6. The Gap

The gap is the **absence of a general dichotomy**. For individual objectives (deletion, resilience, responsibility) the PTIME/intractable boundary is sharp; but no theorem classifies *arbitrary* objectives + update operations. The open question: is there a single structural criterion (a generalization of safety/head-domination/submodularity) that decides RDM tractability uniformly? It is genuinely **open** — even the right meta-parameters are debated. Closing it likely requires unifying probabilistic-database safety, provenance-circuit structure, and submodular/TU optimization into one classification.

## 7. Current Research (as of June 2026)

Active: extending **resilience/responsibility dichotomies to richer objectives and self-joins** (Gatterbauer, Meliou, Makhija), and **knowledge-compilation** approaches that make RDM tractable when the provenance circuit is bounded-width. *(frontier — verify)* 2024–2025 work explores **Shannon-flow / information-theoretic lower bounds** for resilience-style RDM and **ILP/SMT-certified** how-to solvers, plus RDM objectives for **fairness, ML-data-debugging, and what-if over feature pipelines**. A unified "RDM dichotomy" remains a stated grand challenge.

## 8. Future Work

- A meta-dichotomy: one structural criterion for PTIME vs. intractable RDM over query class × update ops × objective.
- Tight approximation thresholds for intractable objectives.
- Decidability frontier under constraints and recursion.
- Scalable certified-optimal engines beyond MILP heuristics.

## 9. Key References

- **[Foundational]** Meliou, Gatterbauer, Suciu. *Reverse Data Management.* CIDR / VLDB Vision, 2011.
- **[SOTA]** Meliou, Suciu. *Tiresias: The Database Oracle for How-To Queries.* SIGMOD, 2012.
- **[SOTA]** Kimelfeld, Vondrák, Williams. *Maximizing Conjunctive Views in Deletion Propagation.* PODS, 2011 (TODS, 2012).
- **[SOTA]** Freire, Gatterbauer, Immerman, Meliou. *The Complexity of Resilience and Responsibility for Self-Join-Free Conjunctive Queries.* VLDB, 2015.
- **[Foundational]** Dalvi, Suciu. *The Dichotomy of Probabilistic Inference for Unions of Conjunctive Queries.* Journal of the ACM, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
