# Cleaning-Aware Query Answering

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/cleaning-aware-query-answering` · **Status:** partially-solved

## 1. Problem Statement

Given a dirty database instance $D$ that violates a set of integrity constraints $\Sigma$, and a query $Q$, return answers that are *consistent* with — or robust to — the space of possible cleanings of $D$, **without** materializing any single clean instance. Materialization is undesirable because (i) the number of minimal repairs can be exponential, (ii) committing to one repair discards uncertainty, and (iii) cleaning the whole instance to answer one query is wasteful.

Three canonical variants:

- **Decision (CQA membership):** Is tuple $t$ a *certain answer* of $Q$ over $D, \Sigma$, i.e. $t \in Q(D')$ for **every** repair $D'$?
- **Counting:** How many repairs (or what fraction) yield $t$ — i.e. compute the *relative frequency* / probability of $t$?
- **Optimization:** Among repairs, return answers under a cost-minimal or most-probable repair, or compute a query result with formal error bounds.

A *repair* $D'$ is a database satisfying $\Sigma$ that is minimal w.r.t. some notion (symmetric-difference $\subseteq$-minimality, cardinality-minimality, or cost-minimality under attribute updates).

## 2. Mathematical Foundations

Let $\Sigma$ be functional dependencies (FDs), conditional FDs, denial constraints, or tuple-generating dependencies. **Consistent Query Answering (CQA)**, due to Arenas–Bertossi–Chomicki (PODS 1999), defines certain answers as
$$\mathsf{certain}(Q, D, \Sigma) = \bigcap_{D' \in \mathsf{Rep}(D,\Sigma)} Q(D').$$

Key tools:
- **Conflict hypergraph / repair lattice:** repairs under subset-minimal deletion correspond to maximal independent sets of the conflict (hyper)graph; counting repairs reduces to counting such structures (#P-hard in general).
- **The chase** generates repairs for tgds/egds; termination and confluence govern decidability.
- **Dichotomy theory:** For self-join-free conjunctive queries (CQs) under primary-key constraints, Koutris–Wijsen established a **trichotomy** — $\mathsf{certain}(Q)$ is in $\mathsf{FO}$ (first-order rewritable), or $\mathsf{L}$-complete / $\mathsf{P}$-complete, or $\mathsf{coNP}$-complete — fully classified by syntactic attack-graph criteria.
- **Counting dichotomy:** $\#$CQA under primary keys is either in $\mathsf{FP}$ or $\#\mathsf{P}$-complete (Maslowski–Wijsen).

## 3. State of the Art (SOTA)

**Theory-SOTA.** The Koutris–Wijsen attack-graph machinery (PODS 2015; JACM 2017) gives an *effective* FO-rewriting whenever one exists for self-join-free CQs under one key per relation; extensions cover certain foreign keys and some self-joins (Koutris–Wijsen 2020; Figueira et al. 2023). Counting trichotomy completed by Calautti–Console–Pieris (ICDT/PODS 2019–2022) with approximate-counting (FPRAS) results for tractable-to-approximate cases.

**Systems-SOTA.** CAvSAT (Dixit–Kolaitis, SIGMOD 2019) reduces CQA to SAT/MaxSAT and scales general CQA via modern solvers. LinCQA (Fan et al., 2023) compiles linear FO-rewritings. Probabilistic/ML approaches — HoloClean (Rekatsinas et al., VLDB 2017) and follow-ons — answer queries over a probabilistic clean instance via inference rather than enumeration.

## 4. Upper Bound

- For self-join-free CQs under primary keys in the FO-rewritable class: **$\mathsf{AC}^0$ / linear-time data complexity** via a SQL rewriting (Koutris–Wijsen).
- General CQA for CQs under denial constraints / FDs: in **$\mathsf{coNP}$** (data complexity); CAvSAT realizes this with MaxSAT, polynomial-size encoding.
- Counting tractable cases admit an **FPRAS** (randomized $(1\pm\epsilon)$-approximation, Calautti et al.).
- Set-minimal-repair CQA always sits in $\mathsf{\Pi}_2^p$ (combined) / $\mathsf{coNP}$ (data) upper envelope.

## 5. Lower Bound

- $\mathsf{certain}(Q)$ is **$\mathsf{coNP}$-complete** (data complexity) already for some self-join-free CQs under two FDs / primary keys — the hard side of the Koutris–Wijsen trichotomy (reduction from monotone 3-SAT / MIS).
- Exact $\#$CQA is **$\#\mathsf{P}$-complete** for the hard side of the counting dichotomy.
- For cardinality-minimal and cost-minimal repairs, even *deciding* whether a repair of cost $\le k$ exists is $\mathsf{NP}$-hard (vertex-cover reduction on the conflict graph).
- No fine-grained ($\mathsf{SETH}$) separation is known for the FO-rewritable cases; rewritings are already near-linear.

## 6. The Gap

For self-join-free CQs under single keys the decision problem is **closed** (exact trichotomy with matching algorithms). The genuinely **open** frontier: (i) full classification for CQs *with self-joins* and *multiple keys/FDs* — only fragments are settled; (ii) tight combined-complexity and practical-cost bounds for **cost-minimal** numerical repairs, where the gap between $\mathsf{NP}$-hardness and heuristic solvers is wide; (iii) approximation-counting dichotomy completeness for non-key constraints. Closing them needs new attack-graph analogues for self-joins and a fine-grained lens on rewriting size.

## 7. Current Research (as of June 2026)

- Extending dichotomies to richer constraint classes and bag semantics (Wijsen; Kolaitis; Pieris) *(frontier — verify)*.
- Differentiable / learned CQA: neural certain-answer estimators and LLM-assisted repair selection feeding query operators *(frontier — verify)*.
- Tight integration of CQA into query optimizers so that "cleaning happens at scan time" only for touched tuples (lazy/just-in-time cleaning), building on CAvSAT and HoloClean lineages.
- Quantitative CQA — returning answers with calibrated probabilities rather than certain/possible — connecting to probabilistic databases.

## 8. Future Work

- A unifying complexity map covering self-joins, multiple keys, and tgds in one framework.
- Anytime CQA with monotone error bounds for interactive analytics.
- CQA under update/insertion semantics, not just deletion repairs, with cost-aware minimality.
- Benchmarks linking CQA answer quality to downstream decision quality (see Benchmarking page).

## 9. Key References

- **[Foundational]** Arenas, Bertossi, Chomicki. *Consistent Query Answers in Inconsistent Databases.* PODS, 1999. — [DOI](https://doi.org/10.1145/303976.303983)
- **[Foundational]** Koutris, Wijsen. *Consistent Query Answering for Self-Join-Free Conjunctive Queries Under Primary Key Constraints.* ACM TODS / JACM, 2017. — [DOI](https://doi.org/10.1145/3068334)
- **[SOTA]** Dixit, Kolaitis. *A SAT-Based System for Consistent Query Answering (CAvSAT).* SIGMOD, 2019. — [arXiv](https://arxiv.org/abs/1905.02828)
- **[SOTA]** Calautti, Console, Pieris. *Counting Database Repairs under Primary Keys Revisited.* PODS, 2019. — [DOI](https://doi.org/10.1145/3294052.3319703)
- **[SOTA]** Rekatsinas, Chu, Ilyas, Ré. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* VLDB, 2017. — [DOI](https://doi.org/10.14778/3137628.3137631)
- **[Survey]** Bertossi. *Database Repairs and Consistent Query Answering.* Morgan & Claypool, 2011. — [DOI](https://doi.org/10.2200/S00379ED1V01Y201108DTM020)

## 10. Worked Example

Relation $\text{Emp}(\underline{\text{eid}}, \text{dept})$ with primary key $\text{eid}$. The dirty instance has a key violation:

| eid | dept |
|-----|------|
| 1   | Sales |
| 1   | HR    |
| 2   | Sales |

Tuples $(1,\text{Sales})$ and $(1,\text{HR})$ conflict on key $\text{eid}{=}1$. Subset-minimal repairs delete one of the two, giving exactly **two repairs**:
$R_1 = \{(1,\text{Sales}),(2,\text{Sales})\}$ and $R_2 = \{(1,\text{HR}),(2,\text{Sales})\}$.

Query $Q_1$: "Does someone work in Sales?" $\;\exists e\,(e,\text{Sales})$. In $R_1$: yes (eid 1 and 2); in $R_2$: yes (eid 2). True in **every** repair $\Rightarrow$ **certain answer = yes**.

Query $Q_2$: "Is eid 1 in Sales?" True in $R_1$, false in $R_2$ $\Rightarrow$ **not certain**.

Counting: $Q_2$ holds in $1$ of $2$ repairs, relative frequency $1/2$. For self-join-free CQs under one key, $Q_1$ ("Sales exists") is FO-rewritable — it has an empty attack graph, so Koutris–Wijsen yields a plain SQL rewriting computable in $\mathsf{AC}^0$, no repair enumeration needed.

---
*Part of the [DBMS Research catalog](../../README.md).*
