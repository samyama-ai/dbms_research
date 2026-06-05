# Why-Not Provenance Minimality

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/why-not-provenance-minimality` · **Status:** open

## 1. Problem Statement

*Why-not provenance* explains why an expected tuple is **missing** from a query answer. The **minimality** problem asks for a **minimal-cost modification** — to the source data or to the query — that makes the missing tuple $t$ appear, with **provable optimality**:

- **Instance-based (what-if data fix):** find a minimum-cost set of source insertions/updates $\Delta^+$ such that $t \in Q(D \cup \Delta^+)$.
- **Query-based (refinement):** find a minimal relaxation of $Q$ (e.g., drop/loosen predicates) so that $t$ appears, minimizing semantic distance.
- **Operator/manipulation-based:** identify the *picky* operators in the plan that pruned $t$ (Chapman–Jagadish model).

Decision form: "is there a fix of cost $\le k$?"; optimization: minimize cost; we also care about **tractable subclasses** with exact optimality.

## 2. Mathematical Foundations

There are three established frameworks: (1) **manipulation-based** (Chapman, Jagadish 2009) — locate operators that discard the candidate; (2) **query refinement** (Tran, Chan 2010; Islam et al.) — search the space of query relaxations; (3) **instance-based** (Herschel, Hernández 2010; Huang, Chen, Doan, Naughton 2008 — *Artemis*) — compute minimal source updates.

The instance-based version is a **view-update / abduction** problem: find a minimal $\Delta$ making a *missing* tuple derivable, dual to deletion propagation. Formally, for a CQ $Q$ with body atoms $R_1,\dots,R_m$ and a target $t$, a witness for $t$ is a homomorphism from $Q$'s body to $D\cup\Delta$ mapping the head to $t$; we minimize the *new* tuples that homomorphism requires:
$$ \min_{\Delta} c(\Delta)\ \text{ s.t. } \exists\, h:\text{body}(Q)\to D\cup\Delta,\ h(\text{head})=t. $$
This is an **abductive minimal-explanation** problem; with integrity constraints it requires the **chase** and may have *no* finite minimal repair or many incomparable ones. Trust/preference orderings (which tables are editable) turn it into a constrained optimization closely related to **minimal database repair** (NP-hard in general).

## 3. State of the Art (SOTA)

- **Chapman, Jagadish (SIGMOD 2009)** — *Why Not?*; operator-level (manipulation) explanations, systems-SOTA origin.
- **Huang, Chen, Doan, Naughton (SIGMOD 2008)** — *Artemis*; instance-based, computes provenance of non-answers as minimal source modifications.
- **Tran, Chan (SIGMOD 2010)** — *Conquer*; query-refinement why-not with minimal query modification.
- **Herschel, Hernández (VLDB 2010)** and **Herschel (survey)** — unified why-not provenance; *Nautilus / Ted* lines.
- **He, Lo (ICDE 2012/2014)** — why-not for top-k and reverse skyline.
- **ten Cate, Civili, Sherkhonov, Tan (ICDT 2015)** — *High-Level Why-Not Explanations using Ontologies*, adding a logical, optimality-aware foundation.

## 4. Upper Bound

For self-join-free CQs without constraints, a minimal single-witness instance fix has size bounded by the number of body atoms, computable in **PTIME** (find the best partial homomorphism, fill missing atoms). Query-refinement over a bounded predicate lattice of depth $d$ is searchable in time **exponential in $d$** but **PTIME for fixed query size**. Under constraints, the **bounded chase** yields fixes when terminating; minimal-cost abduction is in **$\Sigma_2^p$** generally and **FPT** in fix size $k$.

## 5. Lower Bound

Minimal-cost instance fixes generalize **minimal database repair / abduction**, which is **NP-hard** (and **$\Sigma_2^p$-complete** for certain logical abduction problems). Query refinement that must simultaneously make $t$ appear while not admitting forbidden tuples reduces to **set-cover-style** problems and is **NP-hard**, with **$\ln n$-inapproximability** in the multi-constraint case. With recursion (Datalog), deciding whether a bounded-cost fix exists can become **undecidable** when arbitrary constraints interact (chase non-termination). No matching tight bounds are known for the general optimization.

## 6. The Gap

This problem is **open**: unlike deletion propagation (which has dichotomies), why-not minimality lacks a complexity **dichotomy** even for self-join-free CQs, because the search spans *both* data and query modifications and the "right" cost/optimality model is unsettled. Tractable subclasses (single-witness, constraint-free CQs) are known to be PTIME, but the boundary between PTIME and NP-hard/undecidable across constraints, recursion, and refinement spaces is **uncharted**. Closing it needs a principled cost model and a structural classification.

## 7. Current Research (as of June 2026)

Active: **explainability for missing answers in data pipelines and ML**, and **provenance-based debugging** of declarative programs (Deutch, Glavic, Meliou). *(frontier — verify)* 2024–2025 work connects why-not to **query-by-example / query reverse-engineering** (ten Cate, Kimelfeld, Martens) and uses **SMT / constraint-solver** backends to certify minimal-cost fixes with optimality guarantees. There is interest in **why-not for graph and recursive queries** and in unifying why-not minimality under the **reverse data management** umbrella.

## 8. Future Work

- A complexity dichotomy (PTIME vs. NP-hard) for instance-based why-not on CQ subclasses.
- Principled, learnable cost models for "minimal" data/query fixes.
- Decidability frontier under integrity constraints and recursion.
- Certified-optimal solvers (ILP/SMT) scaling to real warehouses.

## 9. Key References

- **[Foundational]** Chapman, Jagadish. *Why Not?* SIGMOD, 2009.
- **[Foundational]** Huang, Chen, Doan, Naughton. *On the Provenance of Non-Answers to Queries over Extracted Data (Artemis).* VLDB, 2008.
- **[SOTA]** Tran, Chan. *How to ConQueR Why-Not Questions.* SIGMOD, 2010.
- **[SOTA]** ten Cate, Civili, Sherkhonov, Tan. *High-Level Why-Not Explanations using Ontologies.* PODS/ICDT, 2015.
- **[Survey]** Herschel, Diestelkämper, Ben Lahmar. *A Survey on Provenance: What for? What form? What from?* VLDB Journal, 2017.

---
*Part of the [DBMS Research catalog](../../README.md).*
