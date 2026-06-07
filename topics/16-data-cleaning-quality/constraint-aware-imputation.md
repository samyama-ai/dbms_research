---
id: 16-data-cleaning-quality/constraint-aware-imputation
title: "Imputation Under Constraints"
topic: 16-data-cleaning-quality
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Imputation Under Constraints

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/constraint-aware-imputation` · **Status:** open

## 1. Problem Statement
Given a relation $R$ with missing cells (NULLs) and a set of **integrity constraints** $\Sigma$ (functional dependencies, conditional FDs, denial constraints, foreign keys, check constraints), **fill in the missing values so the completed instance satisfies $\Sigma$** and behaves correctly under downstream queries—rather than imputing each cell in isolation.

Variants:
- **Decision (consistency):** Does there exist a completion of $R$ satisfying $\Sigma$? (constraint satisfiability over NULLs)
- **Optimization:** Among valid completions, find one minimizing a cost (distance to a statistical model, number of cells changed, expected query error).
- **Counting / certain answers:** How many completions satisfy $\Sigma$; which query answers are **certain** across all valid completions?

This is harder than ordinary imputation because constraints couple cells: a value chosen for one NULL forces or forbids values elsewhere.

## 2. Mathematical Foundations
Missing data are modeled with **conditional tables / c-tables** (Imielinski–Lipski 1984): NULLs become variables $x_i$ over domains $\mathrm{dom}(A)$, and $\Sigma$ becomes constraints over a valuation $\nu$. A completion is a $\nu$ with $\nu(R)\models\Sigma$. **Certain answers** $\bigcap_\nu Q(\nu(R))$ and **possible answers** $\bigcup_\nu Q(\nu(R))$ formalize what queries can safely return. The **chase** procedure repairs $R$ against tuple/equality-generating dependencies; for FDs/denial constraints, finding a minimal-cost valid completion is a **constraint optimization / weighted CSP**. Denial constraints $\forall \bar t\, \neg(\varphi)$ make each NULL a variable in a (possibly infinite-domain) CSP. Statistical priors enter as a soft objective $\min \sum_i \mathrm{cost}(x_i)$ s.t. hard constraints $\Sigma$—a **constrained MAP** problem, equivalently MAP inference in a Markov network with hard factors.

## 3. State of the Art (SOTA)
- **HoloClean** (Rekatsinas, Chu, Ilyas, Ré, VLDB 2017): unifies integrity constraints, statistical signals, and external data in a single probabilistic (factor-graph) model to repair/impute—the leading constraint-aware system.
- **NADEEF / LLUNATIC** (Dallachiesa et al., SIGMOD 2013; Geerts et al., VLDB 2013): generic constraint-based cleaning and a chase-based mapping-and-cleaning engine producing constraint-satisfying solutions.
- **ImputeDB** (Cambronero et al., VLDB 2017): pushes imputation into query plans (query-aware, though not constraint-focused).
- **ERACER, relational dependency networks** for joint relational imputation.
- Theory-SOTA: certain-answer semantics and the chase from data-exchange/incomplete-databases (Fagin–Kolaitis–Miller–Popa 2005; Abiteboul–Hull–Vianu).

## 4. Upper Bound
For acyclic/weakly-acyclic dependency sets the **chase terminates in polynomial time**, giving a canonical (universal) solution and PTIME certain-answer evaluation for unions of conjunctive queries (Fagin et al. 2005). HoloClean computes an approximate MAP completion in time polynomial in the grounded factor graph via relaxed inference. For bounded-domain FD-only consistency, a valid completion (if one exists) is found in PTIME by 2-SAT-like propagation in special cases; general weighted optimal completion is solved via ILP/MaxSAT with no sub-exponential worst-case guarantee.

## 5. Lower Bound
Deciding existence of a constraint-satisfying completion is **NP-hard** in general: minimum-cost repair under FDs is NP-hard (Bohannon–Fan–Geerts–Jia–Kementsietsidis, SIGMOD 2005), and denial-constraint satisfaction over open domains encodes general **CSP/SAT**. Computing **certain answers** is **coNP-hard** for many query/constraint classes, and **undefined/undecidable** for non-terminating chase with arbitrary tgds+egds (chase termination itself is undecidable). MAP inference in the induced Markov network is NP-hard (it generalizes MAX-SAT). These are **model-theoretic NP/coNP-hardness** lower bounds, not merely fine-grained.

## 6. The Gap
**Open and wide.** Exact optimal constraint-respecting imputation is NP/coNP-hard; deployed systems (HoloClean) use *approximate* MAP with **no quality certificate**—we cannot generally bound how far an imputed instance is from an optimal or correct one (ties to repair-quality-certification). The gap between PTIME tractable islands (weakly-acyclic, bounded-domain, FD-only) and the NP-hard general case is fundamental. Closing it means either (a) carving larger tractable constraint classes with statistical objectives, or (b) approximation algorithms with provable cost ratios.

## 7. Current Research (as of June 2026)
- **LLM-based imputation respecting constraints:** prompting/finetuning LLMs to fill values, then *verifying/repairing* against $\Sigma$ in a generate-and-check loop *(frontier — verify)*.
- **Differentiable/neural-symbolic constrained imputation** that bakes denial constraints into the loss *(frontier — verify)*.
- Groups: Ihab Ilyas & Theo Rekatsinas (HoloClean/Inductiv), Christopher Ré (Stanford), Wang-Chiew Tan, Paolo Papotti (constraint cleaning), Floris Geerts.

## 8. Future Work
- Approximation algorithms with cost guarantees for FD/DC-constrained MAP imputation.
- Query-aware imputation that minimizes downstream answer error directly (bridge to imputation-statistical-validity).
- Tractable certain-answer semantics under statistical priors; certified-repair guarantees.

## 9. Key References
- **[Foundational]** T. Imielinski, W. Lipski. *Incomplete Information in Relational Databases.* JACM, 1984. — [DOI](https://doi.org/10.1145/1634.1886)
- **[Foundational]** P. Bohannon, W. Fan, F. Geerts, X. Jia, A. Kementsietsidis. *Conditional Functional Dependencies for Data Cleaning.* (and minimal-repair complexity) ICDE/SIGMOD, 2005–2007. — [DBLP](https://dblp.org/rec/conf/icde/BohannonFGJK07.html)
- **[Foundational]** R. Fagin, P. G. Kolaitis, R. J. Miller, L. Popa. *Data Exchange: Semantics and Query Answering.* TCS, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[SOTA]** T. Rekatsinas, X. Chu, I. F. Ilyas, C. Ré. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* VLDB, 2017. — [arXiv](https://arxiv.org/abs/1702.00820)
- **[SOTA]** F. Geerts, G. Mecca, P. Papotti, D. Santoro. *The LLUNATIC Data-Cleaning Framework.* VLDB, 2013. — [DOI](https://doi.org/10.14778/2536360.2536363)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995 (incomplete information, chase). — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)

## 10. Worked Example

Relation $\text{Emp}(\underline{\text{name}}, \text{dept}, \text{city})$ with FD $\text{dept}\to\text{city}$ (a department sits in one city). Domain of city is $\{\text{NYC},\text{LA}\}$.

| name | dept | city |
|------|------|------|
| Ann  | D1   | NYC  |
| Bob  | D1   | $x_1$ (NULL) |
| Cara | D2   | $x_2$ (NULL) |
| Dan  | D2   | LA   |

The FD couples cells: Bob shares dept D1 with Ann, so $x_1$ is *forced* to NYC. Cara shares D2 with Dan, so $x_2$ is forced to LA. Independent per-cell imputation (e.g., "most frequent city = NYC") would wrongly set $x_2=\text{NYC}$, violating $\text{dept}\to\text{city}$.

Here propagation yields a unique valid completion in linear time. But add a third NULL-dept row for "Eve, $x_3$, LA": now $x_3$ may be D1 (forcing nothing new) or D2 — branching. With $k$ such free cells over a domain of size $d$, the naive search is $d^k$; the optimization version (minimize edits subject to $\Sigma$) is the NP-hard MAP problem of Section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
