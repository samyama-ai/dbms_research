# Metamorphic Relations for Query Engines

> **Topic:** Benchmarking, Testing & Verification · **ID:** `33-benchmarking-testing/metamorphic-relations-queries` · **Status:** partially-solved

## 1. Problem Statement

A **metamorphic relation (MR)** is an invariant linking the outputs of related queries that any correct engine must satisfy, used as a partial test oracle (no trusted reference needed). The problem: **systematically discover, prove sound, and maximize the coverage** of MRs over the *full* SQL surface, rather than relying on a handful of hand-crafted relations (NoREC, TLP, PQS).

Variants:
- **Discovery (search) variant:** enumerate candidate MRs over a query algebra.
- **Verification variant:** prove a candidate MR is a theorem of SQL semantics (sound for all engines).
- **Optimization variant:** select a minimal MR set maximizing bug-detection coverage subject to a query-budget.

## 2. Mathematical Foundations

Model SQL as bag-relational algebra $\mathcal{BA}$ with operators $\sigma,\pi,\bowtie,\cup,\setminus,\gamma$ (aggregation) and 3-valued predicates. A metamorphic relation is a pair $(\tau, \rho)$: a *source-to-follow-up transformation* $\tau:\mathcal{Q}\to\mathcal{Q}$ (possibly with an input transform on $I$) and an *output relation* $\rho \subseteq \mathcal{R}\times\mathcal{R}$ such that for the true semantics,
$$ \forall q, I:\quad \rho\big(\llbracket q\rrbracket_I,\ \llbracket \tau(q)\rrbracket_{\tau(I)}\big). $$

Examples (all theorems of $\mathcal{BA}$):
- **TLP:** $\llbracket q\rrbracket = \llbracket q_p\rrbracket \uplus \llbracket q_{\neg p}\rrbracket \uplus \llbracket q_{p\,\mathrm{IS\,NULL}}\rrbracket$ ($\uplus$ = bag union).
- **NoREC:** $|\sigma_p(R)| = \sum_{r\in R}[\,p(r)\,]$ via predicate moved to projection.
- **Monotonicity:** $I \subseteq I' \Rightarrow \llbracket q\rrbracket_I \subseteq \llbracket q\rrbracket_{I'}$ for positive (union-difference-free) $q$.

**Soundness** of $(\tau,\rho)$ = a proof in the equational theory of $\mathcal{BA}$. Discovery can be framed as searching the equational theory; selecting an MR subset of size $k$ maximizing expected coverage is a **submodular maximization** problem ($1-1/e$ greedy guarantee) when coverage of bug classes is modeled as a coverage function.

## 3. State of the Art (SOTA)

- **Hand-crafted, proven MRs:** NoREC, TLP/QPG, PQS, CERT (cardinality estimation), and EET — **Equivalent Expression Transformation** (Jiang et al., 2024) which *automatically composes* many semantics-preserving rewrites into deep equivalent queries — the closest to systematic discovery.
- **DQE / DQP** extend MRs to distributed plans and result-set equivalence.
- General **metamorphic testing** theory (Chen et al., since 1998) provides the framework; query-specific automated *discovery* remains mostly manual or template-driven.
- SQLancer integrates these as pluggable oracles; **SQLRight / industrial fuzzers** combine MRs with coverage feedback.

## 4. Upper Bound

Applying one MR costs a constant number of extra query executions, $O(\text{cost}(q))$ each. EET-style composition grows the follow-up query but stays polynomial in the rewrite count. For MR *selection*, greedy submodular maximization gives a $(1-1/e)$-approximate optimal coverage set in $O(k\cdot m)$ evaluations ($m$ candidate MRs). No tighter universal bound on *discovery* exists because it inherits the undecidability of equivalence.

## 5. Lower Bound

- Deciding whether an arbitrary candidate $(\tau,\rho)$ is sound = a query-equivalence/implication check, **undecidable** for full relational algebra with difference; NP-complete already for conjunctive-query containment (Chandra-Merlin 1977).
- Optimal MR-subset selection for max coverage is **NP-hard** (Set Cover / Max-Coverage reduction); $(1-1/e)$ is the best poly-time approximation unless $\mathrm{P}=\mathrm{NP}$ (Feige 1998).
- Information-theoretically, no finite MR set achieves coverage 1 (see oracle problem): some wrong-but-consistent behaviors violate no relation in the set.

## 6. The Gap

For the *decidable* conjunctive/positive fragment, sound MR discovery is "solved" in principle but intractable (NP-hard) and not exhaustively engineered. For the *full* SQL surface (windows, recursion, NULL-sensitive aggregates, JSON), there is **no complete catalogue** and no proof that current MRs cover even a characterized fraction of bug classes — hence *partially-solved*. Closing it needs (a) a mechanized SQL semantics to certify MRs and (b) a coverage theory quantifying what each MR can witness.

## 7. Current Research (as of June 2026)

- **Automated MR synthesis** via equational rewriting plus SMT/proof-assistant certification *(frontier — verify)*.
- Extending EET-style equivalent-expression generation to window functions and recursive CTEs *(frontier — verify)*.
- Coverage-guided MR selection combining fuzzer feedback with submodular budgeting.
- Groups: Manuel Rigger (NUS), the EET authors, Alvin Cheung/Shumo Chu/Dan Suciu (formal semantics), T.Y. Chen lineage (metamorphic-testing theory).

## 8. Future Work

- A certified, machine-checked library of MRs spanning SQL:2023.
- Formal coverage metrics: map each MR to the bug classes it can/cannot detect.
- Learning MRs from observed bug corpora; transfer across dialects.
- Compositional soundness: guarantees preserved when MRs are chained (as EET does).

## 9. Key References

- **[Foundational]** T. Y. Chen, S. C. Cheung, S. M. Yiu. *Metamorphic Testing: A New Approach for Generating Next Test Cases.* Tech. Report HKUST, 1998. — [arXiv](https://arxiv.org/abs/2002.12543)
- **[Foundational]** A. K. Chandra, P. M. Merlin. *Optimal Implementation of Conjunctive Queries.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[SOTA]** M. Rigger, Z. Su. *Finding Bugs in Database Systems via Query Partitioning (TLP).* OOPSLA, 2020. — [DOI](https://doi.org/10.1145/3428279)
- **[SOTA]** X. Jiang et al. *Detecting Logic Bugs in Database Engines via Equivalent Expression Transformation (EET).* OSDI, 2024. — [USENIX](https://www.usenix.org/conference/osdi24/presentation/jiang)
- **[Survey]** S. Segura, G. Fraser, A. B. Sánchez, A. Ruiz-Cortés. *A Survey on Metamorphic Testing.* IEEE TSE, 2016. — [DOI](https://doi.org/10.1109/TSE.2016.2532875)
- **[Foundational]** U. Feige. *A Threshold of ln n for Approximating Set Cover.* JACM, 1998. — [DOI](https://doi.org/10.1145/285055.285059)

## 10. Worked Example

Apply the **TLP** metamorphic relation to one table $R(a)$ with rows $\{1, 2, \texttt{NULL}\}$ and predicate $p \equiv (a > 1)$.

Source query: $q = \texttt{SELECT a FROM R}$, returning the full bag $\{1,2,\texttt{NULL}\}$.

Follow-up partition (3-valued logic splits every row into exactly one of TRUE / FALSE / UNKNOWN):
- $q_p = \texttt{SELECT a FROM R WHERE a > 1}$ $\to \{2\}$
- $q_{\neg p} = \texttt{SELECT a FROM R WHERE NOT (a > 1)}$ $\to \{1\}$
- $q_{p\,\text{IS NULL}} = \texttt{SELECT a FROM R WHERE (a > 1) IS NULL}$ $\to \{\texttt{NULL}\}$

The MR asserts $\llbracket q\rrbracket = \llbracket q_p\rrbracket \uplus \llbracket q_{\neg p}\rrbracket \uplus \llbracket q_{p\,\text{IS NULL}}\rrbracket$. Here $\{1,2,\texttt{NULL}\} = \{2\}\uplus\{1\}\uplus\{\texttt{NULL}\}$ — holds.

Bug witness: an engine that mistakenly treats `NOT (NULL > 1)` as TRUE would put `NULL` into $q_{\neg p}$, yielding $\{1,\texttt{NULL}\}\uplus\{2\}\uplus\{\} = \{1,2,\texttt{NULL}\}$ — still correct *here*, but on a query where the partitions overlap the bag union breaks, and TLP flags the mismatch with **no trusted reference oracle** needed.

---
*Part of the [DBMS Research catalog](../../README.md).*
