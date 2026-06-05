# Probabilistic-DB Provenance Hardness

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/probabilistic-db-provenance` · **Status:** partially-solved

## 1. Problem Statement

In a tuple-independent probabilistic database (TID), each input tuple $t$ is present independently with probability $p_t$. The **reliability** (marginal probability) of a Boolean query answer equals the probability that its **provenance formula** $\phi$ (a propositional formula / semiring polynomial over tuple variables) evaluates to true — i.e., a **weighted model-counting (WMC)** problem on $\phi$. The problem is to map out the **exact-vs-approximate computation boundary**: for which queries is reliability computable in PTIME (the query is *safe*), for which is it #P-hard, and where exact hardness coexists with efficient *approximation*; and how this **lifts** from the propositional (grounded) level to the query/first-order level.

Variants:
- **Counting (exact):** compute $\Pr[\phi]$ exactly.
- **Approximation:** compute $\Pr[\phi]$ within $(1\pm\varepsilon)$ (FPRAS) or additively.
- **Dichotomy (meta):** classify each query as safe (PTIME) or unsafe (#P-hard) — and within unsafe, FPRAS-approximable vs. not.

Status **partially solved**: the *exact* dichotomy for unions of conjunctive queries (UCQs) is fully resolved; the *approximation* frontier for unsafe queries is only partially mapped.

## 2. Mathematical Foundations

Provenance is the lineage formula $\phi$; $\Pr[\phi] = \sum_{\text{worlds } W \models \phi}\prod_{t\in W}p_t\prod_{t\notin W}(1-p_t)$ — **weighted model counting**, a $\#P$ problem (Valiant). Tractability is governed by **knowledge compilation**: $\Pr[\phi]$ is computable in time linear in the size of an **OBDD/FBDD/d-DNNF** for $\phi$; safe queries are exactly those whose lineage compiles to polynomial-size such circuits.

The central result is the **dichotomy theorem** (Dalvi–Suciu): for every UCQ $Q$, computing $\Pr[Q]$ is **either in PTIME or #P-hard**, with a *syntactic* criterion (the query is "safe" iff a safe plan / `inclusion–exclusion`-based factorization exists). The PTIME algorithm uses **inclusion–exclusion + independence/disjointness** to factor $\Pr[Q]$; hardness is by reduction from **counting (e.g., #PP2DNF / permanent)**.

Lifting: the *lifted inference* view connects safe-query evaluation to **lifted (first-order) probabilistic inference** in AI (domain-lifted classes). Approximation rests on **Karp–Luby / FPRAS for DNF counting** (the lineage of a UCQ is a monotone DNF), giving an FPRAS for the *DNF-evaluation* even when exact is #P-hard — but this is per-answer, and uniform approximation across structured queries is subtler.

## 3. State of the Art (SOTA)

Theory-SOTA: the **Dalvi–Suciu dichotomy** (PODS 2007; JACM 2012) completely classifies UCQ reliability as PTIME-or-#P-hard with a decidable syntactic test; extensions cover **probabilistic XML**, **queries with self-joins** (the hard frontier resolved by the dichotomy), and **bag semantics / aggregates** partially. **Knowledge-compilation characterizations** (Jha–Suciu; Amarilli–Bourhis–Monet–Senellart) tie safety to OBDD/d-DNNF size and to **bounded-treewidth** instances (Monet; Amarilli et al. — bounded treewidth gives tractable compilation). Systems-SOTA: **ProvSQL** (Senellart et al., VLDB 2018) computes provenance circuits and exact/approximate probabilities in PostgreSQL; **MayBMS / SPROUT** (Koch, Olteanu) use OBDD-based confidence computation; **Mystiq**, **Orion**. Approximation: **Karp–Luby FPRAS** for the DNF lineage, and **anytime bounds** via partial compilation.

## 4. Upper Bound

- **Safe UCQs:** exact $\Pr[Q]$ in **PTIME data complexity** via a safe plan (inclusion–exclusion + independent/disjoint project) — RAM model (Dalvi–Suciu).
- **Bounded-treewidth instances:** exact $\Pr[Q]$ in **linear time** via bounded-width d-DNNF compilation — instance/structural model (Amarilli–Bourhis–Senellart).
- **Any monotone DNF lineage (per answer):** $(1\pm\varepsilon)$ **FPRAS** in $O(\varepsilon^{-2}\,m\,n)$ via Karp–Luby–Madras importance sampling — randomized model.
- **General $\phi$:** exact via d-DNNF compilation, time/space linear in (worst-case exponential) circuit size — knowledge-compilation model.

## 5. Lower Bound

- **Unsafe UCQs:** computing $\Pr[Q]$ exactly is **#P-hard** (Dalvi–Suciu) — counting model; the canonical hard query $H_0 = R(x),S(x,y),T(y)$ reduces from #PP2DNF / permanent.
- **Compilation lower bounds:** unsafe queries have lineage requiring **$2^{\Omega(n)}$-size FBDD/d-DNNF/OBDD** (Jha–Suciu; Amarilli–Monet–Senellart) — unconditional in the compilation model.
- **Approximation hardness:** for *non-monotone* lineage (queries with negation/difference), even **multiplicative approximation is NP-hard** (no FPRAS unless RP=NP), since deciding satisfiability is embedded.
- **Beyond bounded treewidth:** unbounded-treewidth instance families force super-polynomial compilation (lower-bound transfer from FBDD size).

## 6. The Gap

The **exact** boundary is **closed** for UCQs (full dichotomy, matching compilation lower bounds) — a landmark. The **open part is approximation**: although each *monotone* DNF answer admits a Karp–Luby FPRAS, there is **no full dichotomy for approximability** of structured/recursive queries, queries with **negation/aggregation**, or **uniform** approximation across all answers; and the interaction of safety with **correlated (not tuple-independent)** models (block-independent, pc-tables, Markov-logic) is only partly mapped. Closing the gap means an *approximation dichotomy* (FPRAS-vs-not) parallel to the exact one, plus extension beyond TID and beyond monotone lineage.

## 7. Current Research (as of June 2026)

(1) **Approximation dichotomies** and FPRAS frontiers for unsafe queries, including self-joins and recursion (Suciu, Van den Broeck, Amarilli, Monet) *(frontier — verify)*. (2) **Lifted inference ↔ safe queries** cross-pollination with probabilistic-programming and neuro-symbolic systems (Van den Broeck, Suciu). (3) **ProvSQL / circuit-based** engines extending compilation to aggregates and where-provenance with anytime bounds (Senellart). (4) **Provenance for probabilistic + differential-privacy** combinations, and reliability over learned/correlated models *(frontier — verify)*. (5) Fine-grained / treewidth-parameterized exact algorithms with matching conditional lower bounds.

## 8. Future Work

- A full FPRAS-vs-inapproximable dichotomy mirroring the exact dichotomy.
- Reliability for non-monotone (difference/negation) and aggregate queries.
- Tractability boundaries under correlated probabilistic models (BID, pc-tables, PGMs).
- Anytime exact/approximate engines with provable error–time tradeoffs at scale.

## 9. Key References

- **[Foundational]** N. Dalvi, D. Suciu. *The Dichotomy of Probabilistic Inference for Unions of Conjunctive Queries.* PODS 2007 / JACM, 2012.
- **[Foundational]** L. G. Valiant. *The Complexity of Enumeration and Reliability Problems.* SIAM J. Computing, 1979.
- **[Foundational]** R. M. Karp, M. Luby, N. Madras. *Monte-Carlo Approximation Algorithms for Enumeration Problems (FPRAS for DNF).* J. Algorithms, 1989.
- **[SOTA]** A. Amarilli, P. Bourhis, P. Senellart. *Provenance Circuits for Trees and Treelike Instances / Bounded Treewidth.* ICALP, 2015.
- **[SOTA]** P. Senellart, L. Jachiet, S. Maniu, Y. Ramusat. *ProvSQL: Provenance and Probability Management in PostgreSQL.* PVLDB, 2018.
- **[Survey]** D. Suciu, D. Olteanu, C. Ré, C. Koch. *Probabilistic Databases.* Morgan & Claypool, 2011.

---
*Part of the [DBMS Research catalog](../../README.md).*
