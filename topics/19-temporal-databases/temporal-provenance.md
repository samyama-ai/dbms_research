---
id: 19-temporal-databases/temporal-provenance
title: "Temporal Provenance & Lineage"
topic: 19-temporal-databases
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Temporal Provenance & Lineage

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-provenance` · **Status:** open

## 1. Problem Statement
Provenance explains *how* an output tuple was derived from inputs. **Temporal provenance** asks for that explanation when both the inputs and the query are time-varying: source tuples have valid/transaction-time periods, the query may itself be temporal (sequenced, as-of, sliding-window), and the derivation must explain not just *which* inputs but *over which time intervals* and *at which version* each contributed. The output is a provenance annotation that is correct under the temporal semantics — e.g. a sequenced join's result tuple's lineage must attribute the precise sub-interval and the exact source versions that produced it.

Variants:
- **Why/how-provenance:** the provenance polynomial of an output, lifted to carry time.
- **Where-provenance / temporal lineage:** which source cells (and their as-of versions) a value came from.
- **Decision:** does output $o$ depend on source tuple $s$ during interval $I$? (delta/why-not over time)
- **Counting:** number of distinct derivations weighted by temporal overlap.

The crux: time is both *data* (interval-valued attributes) and *metadata* (the version/instant a fact held), and provenance must commute correctly with coalescing, alignment, and as-of operators.

## 2. Mathematical Foundations
The unifying framework is **provenance semirings** (Green–Karvounarakis–Tannen, PODS 2007): annotate each base tuple with an element of a commutative semiring $(K,\oplus,\otimes,0,1)$; positive relational algebra propagates annotations with $\otimes$ for joins and $\oplus$ for unions/projection. The free semiring $\mathbb{N}[X]$ (provenance polynomials) is most informative; specializations give lineage, trust, multiplicity, security levels.

Temporal provenance enriches $K$ with the **time dimension**. One line treats time via *semimodules* / the **semiring of timed annotations**, where an annotation is a function from time to a base semiring, and operators integrate over interval intersection: a sequenced join over periods $p,q$ contributes $\otimes$ on $p\cap q$. Formally, annotations live in $K^T$ with pointwise $\oplus$ and a *convolution-like* $\otimes$ respecting interval algebra (Allen relations). Difference and aggregation require **semirings with monus** ($m$-semirings) and the **semimodule** structure of Amsterdamer–Deutch–Tannen (PODS 2011) for aggregate provenance. Correctness criterion: the annotated operator must form a *homomorphism* from the temporal-algebra to $K^T$, so that coalescing/alignment factor cleanly.

## 3. State of the Art (SOTA)
**Theory-SOTA:** Semiring provenance for positive RA (Green et al. 2007), extended to aggregation (Amsterdamer–Deutch–Tannen 2011), to difference via m-semirings (Geerts–Poggi), and to *temporal/streaming* settings via **timed provenance** and provenance for window queries. Provenance for **Datalog / recursive** queries uses the semiring of formal power series (absorptive / $\omega$-continuous semirings), relevant to recursive temporal reasoning.

**Systems-SOTA:** GProM (Glavic et al.) computes provenance by query rewriting (the *Perm/GProM* approach) and supports transaction-time / "reenactment" provenance over **temporal/versioned** tables — replaying past transactions to reconstruct historical provenance without a dedicated log format. ProvSQL (Senellart et al.) maintains provenance circuits inside PostgreSQL. Time-travel and lineage in Delta Lake/Iceberg and in stream processors (Flink, Apache Beam) provide coarse, operational lineage but not formal semiring-correct temporal why-provenance.

## 4. Upper Bound
For positive temporal RA (select-project-join-union with sequenced semantics over interval-annotated tuples), provenance polynomials can be computed by a single annotated pass that intersects intervals at joins; the **provenance circuit** has size $O(|Q(I)| + \text{intermediate})$ and is built in PTIME (data complexity) in the RAM model, with the circuit being polynomial for non-recursive queries. GProM's reenactment computes transaction-time provenance with overhead polynomial in log/version count by rewriting into standard SQL evaluated on the temporal tables — no special engine needed.

## 5. Lower Bound
Computing the *most informative* (full $\mathbb{N}[X]$) provenance for queries with **difference/aggregation** is intractable in general: deciding equivalence of provenance polynomials and certain *why-not* (missing-answer) provenance questions are **coNP-hard / $\Sigma_2^p$**-flavored, and exact why-not provenance is NP-hard. For recursive temporal queries the provenance series can be **infinite**, requiring $\omega$-continuous semirings (no finite polynomial). Lower bounds on annotation size: distinguishing derivations forces provenance circuits whose size matches query-output blow-up; succinct (poly-size) provenance for all CQs would collapse known circuit lower bounds in the worst case. These are information-theoretic/complexity-theoretic, not yet temporally-tight.

## 6. The Gap
Positive sequenced temporal provenance is essentially solved (semiring homomorphism + interval intersection). The open gap is a **single semiring framework that simultaneously and correctly handles (a) difference/negation, (b) aggregation, (c) recursion, and (d) the dual role of time as data and as version** — and that commutes with coalescing and as-of. No accepted complexity classification exists for temporal why-not provenance, nor a canonical minimal temporal-provenance representation analogous to coalescing's normal form. Closing it requires the right algebraic object (likely a timed m-semimodule) plus matching size lower bounds.

## 7. Current Research (as of June 2026)
Active: (i) **reenactment-based** transaction-time provenance and "what-if"/"how-to" over versioned data (Glavic, Niu, Arab — GProM); (ii) provenance for **streaming/window** queries and CEP with bounded-memory annotation; (iii) provenance-aware **time-travel** in lakehouses, linking Iceberg/Delta snapshots to derivation. *(frontier — verify)* Emerging work fuses temporal provenance with **differential privacy accounting over time** and with verifiable/cryptographic lineage for auditability of historical query answers. Groups: Tannen/Deutch/Amsterdamer (Penn/Tel Aviv), Glavic (IIT), Senellart (ENS/ProvSQL), Glavic–Arab on reenactment.

## 8. Future Work
- A unified **timed m-semimodule** covering aggregation, difference, recursion, and as-of versioning.
- Canonical minimal temporal-provenance form and its size lower bounds.
- Tractable fragments and approximations for **temporal why-not** provenance.
- Provenance-driven explanation/debugging of sequenced-semantics rewrites and window analytics, with privacy-budget accounting.

## 9. Key References
- **[Foundational]** Green, T. J., Karvounarakis, G., Tannen, V. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Foundational]** Amsterdamer, Y., Deutch, D., Tannen, V. *Provenance for Aggregate Queries.* PODS, 2011. — [DOI](https://doi.org/10.1145/1989284.1989302)
- **[SOTA]** Arab, B., Gawlick, D., Krishnaswamy, V., Radhakrishnan, V., Glavic, B. *Reenactment for Read-Committed Snapshot Isolation (Transaction Provenance).* VLDB / TaPP, 2018. — [arXiv](https://arxiv.org/abs/1608.08258)
- **[SOTA]** Senellart, P. et al. *ProvSQL: Provenance and Probability Management in PostgreSQL.* VLDB (demo), 2018. — [DOI](https://doi.org/10.14778/3229863.3236253)
- **[Survey]** Cheney, J., Chiticariu, L., Tan, W.-C. *Provenance in Databases: Why, How, and Where.* Foundations and Trends in Databases, 2009. — [DOI](https://doi.org/10.1561/1900000006)
- **[Foundational]** Glavic, B., Alonso, G. *Perm: Processing Provenance and Data on the Same Data Model through Query Rewriting.* ICDE, 2009. — [DOI](https://doi.org/10.1109/ICDE.2009.15)

## 10. Worked Example

Take two interval-annotated relations. $R$ ("on shift") has tuple $r$ over $[0,8)$; $S$ ("in building") has tuple $s$ over $[3,10)$. Annotate base tuples with semiring variables: $r\mapsto x$, $s\mapsto y$.

**Sequenced join** $R\bowtie S$ over the period intersection produces one result tuple valid on $[0,8)\cap[3,10)=[3,8)$. Lifting provenance into the timed semiring $K^T$, the join contributes $x\otimes y$ but *only* on the overlap, so the annotation is the timed product
$$\text{prov} = (x\otimes y)\big|_{[3,8)},\qquad \text{i.e. } t\mapsto\begin{cases} x\cdot y & t\in[3,8)\\ 0 & \text{otherwise.}\end{cases}$$

Now ask the **decision variant** of §1: *does the output depend on $s$ during $[6,7)$?* Since $[6,7)\subseteq[3,8)$ and the coefficient of $y$ there is $x\neq 0$, the answer is yes. But during $[0,3)$ the annotation is $0$ — $s$ contributes nothing, correctly reflecting that the two facts did not co-occur before $t=3$.

This shows the homomorphism property: $\otimes$ acts on annotations while interval intersection acts on time, and the two commute — exactly the correctness criterion of §2. A plain (non-timed) semiring would wrongly report provenance $x\cdot y$ over all of $[0,8)$.

---
*Part of the [DBMS Research catalog](../../README.md).*
