---
id: 22-provenance-lineage/provenance-guided-repair
title: "Provenance-Guided Data Repair"
topic: 22-provenance-lineage
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Provenance-Guided Data Repair

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/provenance-guided-repair` · **Status:** open

## 1. Problem Statement

When a query answer is wrong or a database violates integrity constraints, the *symptom* (a bad output tuple, a violated dependency) is far from the *cause* (the source errors that produced it). **Provenance-guided data repair** uses lineage and causality to (a) **localize** the minimal set of source tuples/cells responsible for an incorrect or inconsistent answer, and (b) compute a **minimal repair** of those sources that fixes the symptom while perturbing the data as little as possible.

This unifies *why-not* / *why-so* explanation, **causality and responsibility** in databases, and **constraint-based repair**. Inputs: a query/result with a user-asserted error (a tuple that should/shouldn't appear, or a constraint violation) and its provenance. Output: a minimal source intervention.

Variants:
- **Decision:** Does a repair of size $\le k$ exist that fixes the symptom?
- **Optimization (cardinality/cost-minimal repair):** Minimize number/cost of changed cells.
- **Counting/ranking:** Rank candidate causes by **responsibility** $\rho = 1/(1+|\Gamma|)$.

## 2. Mathematical Foundations

**Causality (Halpern–Pearl) in databases** (Meliou et al.): tuple $t$ is a **counterfactual cause** of answer $a$ if removing $t$ flips $a$; it is an **actual cause** with **contingency set** $\Gamma$ if removing $\Gamma$ makes $t$ counterfactual. **Responsibility** is $\rho(t)=\frac{1}{1+\min|\Gamma|}$, formalizing "how much" a source is to blame.

How-provenance polynomials over the **Boolean / Why-semiring** encode exactly which source sets are witnesses; a repair must change variables so the polynomial evaluates correctly.

**Constraint repair** (Arenas–Bertossi–Chomicki): given constraints $\Sigma$ (FDs, denial constraints), a **repair** is a database $D'$ satisfying $\Sigma$ at minimal distance $|D \triangle D'|$. **Certain answers** are those true in all repairs. Minimal-cardinality repair maps to a **minimum vertex cover / hitting set** on the conflict hypergraph, linking repair to set-cover and giving the submodular/LP-rounding toolbox.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Causality/responsibility complexity dichotomies (Meliou et al., Salimi et al.); responsibility is computable in PTIME for some CQ classes and NP-hard in general. Consistent query answering (CQA) complexity is fully classified for FDs/primary keys (Koutris–Wijsen dichotomy: CQA is in PTIME or coNP-complete depending on the query).
- **Systems-SOTA:** **HoloClean** (Rekatsinas et al., VLDB 2017) — probabilistic repair combining constraints, statistics, and signals; **Holistic / LLUNATIC** for cost-based repair over denial constraints; **NADEEF**, **BigDansing** for scalable constraint repair; **Scorpion** (Wu–Madden, VLDB 2013) for provenance-based outlier explanation; **GProM** for why/why-not provenance feeding repair.

## 4. Upper Bound

For **primary-key / FD** repairs, minimum-cardinality repair localized via the conflict graph admits a factor-2 LP-rounding / vertex-cover approximation, and certain-answer computation is PTIME for the tractable side of the Koutris–Wijsen dichotomy. Cost-minimal repair over denial constraints reduces to weighted **set cover**, giving an $O(\log n)$-approximation. Responsibility for conjunctive queries with bounded structure (e.g. linear/read-once provenance) is computable in **PTIME**, and causes are read directly off the read-once provenance circuit. HoloClean's MAP-inference repair runs in polynomial time per round via factor-graph relaxation (heuristic optimality).

## 5. Lower Bound

Minimum-cardinality repair is **NP-hard** (via minimum vertex cover / hitting set), and not approximable better than the set-cover threshold $(1-o(1))\ln n$ unless $\mathsf{P}=\mathsf{NP}$. Computing **responsibility** is **NP-hard** in general (Meliou et al.) — it embeds minimal-contingency-set, which is a hitting-set problem; for non-read-once provenance, even deciding actual causation is intractable. Consistent query answering is **coNP-complete** for the hard side of the FD dichotomy (Koutris–Wijsen) and for general denial constraints. Why-not explanation with minimal source modification inherits these hardness results.

## 6. The Gap

Tractable and intractable fragments are sharply separated for *constraint* repair (Koutris–Wijsen dichotomy is essentially complete) and for *responsibility* on read-once provenance. The **open gap**: (1) no tight approximation for cost-minimal repair beyond the set-cover threshold when constraints and query provenance interact; (2) **joint** optimization of localization + minimal repair (most systems localize heuristically, then repair) lacks end-to-end guarantees; (3) repairs that must satisfy the *user's intent* (why-not) rather than just constraints have no clean complexity characterization. Closing it needs an approximation theory for provenance-coupled repair and a dichotomy for intent-driven repair.

## 7. Current Research (as of June 2026)

- LLM-assisted repair: using language models to propose value-level fixes grounded in provenance/constraints, with HoloClean-style verification *(frontier — verify)*.
- Causal-inference-grounded explanation and repair (Salimi, Roy, Meliou groups) extending HP-causality to aggregates and group-bys.
- Repair with fairness/equity constraints and provenance-aware bias localization *(frontier — verify)*.
- Interactive, human-in-the-loop repair ranking by responsibility.

## 8. Future Work

- End-to-end approximation guarantees for localize-and-repair.
- A complexity dichotomy for why-not / intent-driven repair.
- Repair under probabilistic and uncertain provenance.
- Scalable responsibility computation via factorized provenance.
- Repair that provably preserves downstream query answers (repair-stability).

## 9. Key References

- **[Foundational]** Arenas, Bertossi, Chomicki. *Consistent Query Answers in Inconsistent Databases.* PODS 1999. — [DOI](https://doi.org/10.1145/303976.303983)
- **[Foundational]** Meliou, Gatterbauer, Moore, Suciu. *The Complexity of Causality and Responsibility for Query Answers and Non-Answers.* VLDB 2011. — [DOI](https://doi.org/10.14778/1880172.1880176), [arXiv](https://arxiv.org/abs/1009.2021)
- **[Foundational]** Halpern, Pearl. *Causes and Explanations: A Structural-Model Approach.* British J. Philosophy of Science, 2005. — [DOI](https://doi.org/10.1093/bjps/axi147)
- **[SOTA]** Rekatsinas, Chu, Ilyas, Ré. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* VLDB 2017. — [DOI](https://doi.org/10.14778/3137628.3137631), [arXiv](https://arxiv.org/abs/1702.00820)
- **[SOTA]** Koutris, Wijsen. *Consistent Query Answering for Self-Join-Free Conjunctive Queries under Primary Key Constraints.* PODS 2015 / ACM TODS. — [DOI](https://doi.org/10.1145/2745754.2745769), [TODS](https://doi.org/10.1145/3068334)
- **[SOTA]** Wu, Madden. *Scorpion: Explaining Away Outliers in Aggregate Queries.* VLDB 2013. — [DOI](https://doi.org/10.14778/2536354.2536356)
- **[Survey]** Bertossi. *Database Repairs and Consistent Query Answering.* Morgan & Claypool, 2011. — [DOI](https://doi.org/10.2200/S00379ED1V01Y201108DTM020)

## 10. Worked Example

A table `Emp(name, dept, mgr)` with FD $\text{dept}\to\text{mgr}$ holds:

| name | dept | mgr |
|------|------|-----|
| Ann  | Sales | Bob |
| Cy   | Sales | Dee |
| Eve  | Sales | Bob |

The FD is violated: Sales maps to both Bob (rows Ann, Eve) and Dee (row Cy). The **conflict graph** has an edge between every pair of rows that disagree on `mgr` for the same `dept`: edges $\{$Ann–Cy$\}$ and $\{$Cy–Eve$\}$ (Ann–Eve agree, no edge). A *subset repair* deletes a minimum **vertex cover** of this conflict graph. The cover $\{\text{Cy}\}$ has size 1 and removes both edges, so the minimum-cardinality repair deletes the single row Cy, leaving all-Bob Sales — minimal $|D\triangle D'|=1$.

**Responsibility.** Suppose the analyst flags answer "Sales mgr = Dee" (from Cy) as the error. Cy is a *counterfactual cause*: deleting it (empty contingency set $\Gamma=\varnothing$) removes the answer, so $\rho(\text{Cy})=\frac{1}{1+0}=1$. Ann is only an *actual* cause with $\Gamma=\{\text{Eve}\}$ needed before deleting Ann flips the majority, giving $\rho(\text{Ann})=\frac{1}{1+1}=\tfrac12$. Ranking by $\rho$ correctly puts Cy first — the row a minimal repair should drop.

---
*Part of the [DBMS Research catalog](../../README.md).*
