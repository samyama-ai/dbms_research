# Optimal Core Computation for Data Exchange

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/core-universal-solution-cost` · **Status:** solved-but-impractical

## 1. Problem Statement

In **data exchange**, a source instance $I$ and a mapping $M$ (s-t TGDs plus target TGDs/EGDs) admit many **universal solutions** — target instances that homomorphically map into every solution. The **core** is the unique (up to isomorphism) **smallest** universal solution: it is the minimal target instance that is still a faithful representative for certain-answer query answering. Materializing the core saves storage and speeds query evaluation.

The problem: **compute the core universal solution efficiently** for large instances and expressive mappings. Variants: (i) **decision** — is a given solution a core? (ii) **construction** — produce the core; (iii) **optimization/cost** — minimize the time/space of core computation relative to producing a (non-minimal) canonical universal solution via the chase.

Status is *solved-but-impractical*: polynomial-time algorithms exist, but their constants/exponents and reliance on costly homomorphism checks make them hard to scale, so practice usually settles for the (larger) canonical universal solution.

## 2. Mathematical Foundations

A homomorphism $h: J \to J'$ maps nulls to constants/nulls preserving facts. $J$ is a **core** if every endomorphism $h: J \to J$ is an automorphism (no proper "folding"). The core is unique up to isomorphism and is the smallest universal solution.

Computing a universal solution: run the **chase** of $I$ with $M$, materializing fresh nulls for existentials — size **polynomial in data**. The chase result is *not* minimal; the core removes redundant null-only patterns. Core computation reduces to **core-of-a-structure**, related to constraint-satisfaction: deciding "is $J$ a core?" is **coNP-complete** for arbitrary structures, but data exchange has special structure (constants from $I$ plus nulls) that the FNT/GN algorithms exploit.

Key theorem (Fagin–Kolaitis–Popa, 2005; Gottlob–Nash, 2008): for mappings given by s-t TGDs and target **EGDs + weakly-acyclic TGDs**, the core is computable in **polynomial time in the size of the data**.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Fagin, Kolaitis, Popa (TODS 2005) introduced cores for data exchange and gave PTime algorithms for s-t-TGD mappings (*blocks* and *greedy/findcore*). **Gottlob–Nash** (PODS 2006 / JACM 2008) extended PTime core computation to **target EGDs and weakly-acyclic target TGDs**, the most expressive class with a poly-time core.
- **Systems-SOTA.** **++Spicy** (Mecca–Papotti–Bonifati and the Marnette–Mecca–Papotti "core schema mappings" line, SIGMOD 2009) rewrites s-t TGDs into SQL that directly produces **core (or near-core) solutions**, avoiding post-hoc minimization — the most practical approach. **LLunatic** computes core solutions during chase-based cleaning/exchange.

## 4. Upper Bound

For mappings = s-t TGDs + target EGDs + **weakly-acyclic** target TGDs, the core is computable in **polynomial time in data complexity** (Gottlob–Nash); combined complexity is exponential. The naïve route — chase then minimize — has minimization dominated by homomorphism search whose worst case is super-linear; ++Spicy's **rewriting** approach computes cores in essentially the cost of evaluating the rewritten SQL (low-degree polynomial) by precomputing how nulls would fold, sidestepping global minimization.

## 5. Lower Bound

The general "**is $J$ a core?**" problem is **coNP-complete** (recognizing cores of arbitrary relational structures). Outside the weakly-acyclic regime (e.g., non-terminating target TGDs), a finite core may not exist. Even within PTime classes, core computation is **at least as hard as evaluating the mapping's target constraints**, and the polynomial exponents grow with arity and the number of existentials, making worst-case cost an effective barrier. Producing the core is provably no easier than detecting all redundant null-homomorphisms — an inherently **global** condition (cell-probe/locality intuition: local fixes do not suffice).

## 6. The Gap

The complexity question is **closed in theory** (PTime for the main class). The gap is **theory-vs-practice**: poly-time core algorithms have high constants and assume in-memory homomorphism checking; they do not exploit indexes, parallelism, or incremental/streaming updates well. ++Spicy narrows this for many mappings but does not handle the **full** expressive class (rich target TGDs/EGDs) at scale, and **incremental core maintenance** under source updates is largely open. So the open problem is *engineering optimality and incrementality*, not decidability.

## 7. Current Research (as of June 2026)

Directions: **scalable, parallel, and incremental** core materialization. *(frontier — verify)* Recent work pushes **GPU/columnar chase** and **worst-case-optimal-join-style** evaluation of the rewritten core SQL, plus **provenance-annotated cores** so updates can be propagated. *(frontier — verify)* The Mecca–Papotti–Santoro line and the LLunatic team explore cores for **data cleaning/repairing** at scale; interest in cores for **lakehouse/ELT** materialized views is growing. Approximate / "good-enough" cores with bounded redundancy are an emerging compromise.

## 8. Future Work

- Truly scalable core engines exploiting indexes, parallelism, and out-of-core execution.
- **Incremental core maintenance** under source/mapping changes.
- Cores under the **full** weakly-acyclic-plus-EGD class without falling back to canonical solutions.
- Cost-based optimizers that choose between canonical and core materialization per workload.

## 9. Key References

- **[Foundational]** R. Fagin, P. Kolaitis, L. Popa. *Data Exchange: Getting to the Core.* PODS 2003 / TODS, 2005. — [DOI](https://doi.org/10.1145/1061318.1061323)
- **[Foundational]** G. Gottlob, A. Nash. *Efficient Core Computation in Data Exchange.* PODS 2006 / JACM, 2008. — [DOI](https://doi.org/10.1145/1346330.1346334)
- **[SOTA]** B. Marnette, G. Mecca, P. Papotti. *Scalable Data Exchange with Functional Dependencies.* VLDB, 2010. — [PVLDB](https://vldb.org/pvldb/vol3/R09.pdf)
- **[SOTA]** G. Mecca, P. Papotti, S. Raunich. *Core Schema Mappings.* SIGMOD, 2009. (++Spicy.) — [DOI](https://doi.org/10.1145/1559845.1559914)
- **[SOTA]** F. Geerts, G. Mecca, P. Papotti, D. Santoro. *Mapping and Cleaning.* ICDE / VLDB (LLUNATIC), 2014. — [DOI](https://doi.org/10.1109/ICDE.2014.6816655)
- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data exchange: semantics and query answering.* TCS, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)

## 10. Worked Example

Source has $\text{Emp}(\text{Alice})$. Mapping s-t TGD: $\text{Emp}(x) \to \exists m\, \text{Reports}(x,m)$ and $\text{Emp}(x)\to\exists b\,\text{Reports}(b,b)$.

**Chase (canonical universal solution).** Firing both rules on $\text{Alice}$ produces nulls $N_1,N_2$:
$$J = \{\,\text{Reports}(\text{Alice},N_1),\ \text{Reports}(N_2,N_2)\,\}.$$

**Is $J$ the core?** Consider the endomorphism $h$ with $h(\text{Alice})=\text{Alice}$, $h(N_1)=N_2$, $h(N_2)=N_2$. Then $h(\text{Reports}(\text{Alice},N_1)) = \text{Reports}(\text{Alice},N_2)$ — but that fact is *not* in $J$, so this $h$ fails. Try instead mapping the second fact into the first: there is no way to send $\text{Reports}(N_2,N_2)$ (a self-loop) onto $\text{Reports}(\text{Alice},N_1)$ unless $\text{Alice}=N_1$, impossible since $\text{Alice}$ is a constant. So both facts survive: here $J$ already equals its core.

Contrast: had the second TGD been $\text{Emp}(x)\to\exists m'\,\text{Reports}(x,m')$, the chase would yield two facts $\text{Reports}(\text{Alice},N_1),\text{Reports}(\text{Alice},N_2)$, and the folding $N_2\mapsto N_1$ is an endomorphism — the core collapses to the single fact $\text{Reports}(\text{Alice},N_1)$, halving storage.

---
*Part of the [DBMS Research catalog](../../README.md).*
