---
id: 03-query-processing/semiring-aware-execution
title: "Provenance-aware / semiring execution cost"
topic: 03-query-processing
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Provenance-aware / semiring execution cost

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/semiring-aware-execution` · **Status:** open

## 1. Problem Statement

Generalize relational execution from the Boolean (set) semantics to evaluation over an
**arbitrary commutative semiring** $K = (K, \oplus, \otimes, 0, 1)$ — the algebraic framework
that uniformly captures set semantics ($\mathbb{B}$), bag/multiplicity counting
($\mathbb{N}$), provenance polynomials ($\mathbb{N}[X]$), probabilistic confidence, tropical
shortest-path costs $(\min,+)$, access-control levels, and more — and do so with **minimal
overhead relative to plain query evaluation**.

The problem: **execute joins and aggregation so that each output tuple carries its $K$-value,
computed by replacing relational join with $\otimes$ and union/projection with $\oplus$,
without the value-tracking blowing up time or space**. The central difficulty is that
provenance polynomials and probabilistic annotations can be **exponentially larger** than
the data and that aggregation over semirings does not always factor the way Boolean
projection does.

- **Computation variant:** annotate every output tuple of a positive relational query with
  its semiring value (the K-relation semantics of Green–Karvounarakis–Tannen).
- **Counting/probabilistic variant:** evaluate the query under the probability semiring —
  this generalizes **#P-hard** probabilistic-database query evaluation.
- **Optimization (cost) variant:** minimize the overhead factor $\rho = T_K / T_{\mathbb{B}}$
  of semiring execution versus plain execution, ideally $\rho = O(1)$ or polylog.

This is **open**: for many semirings we lack execution with provably small overhead, and the
boundary between tractable and intractable semirings/queries is only partially mapped.

## 2. Mathematical Foundations

A **K-relation** maps each tuple to an annotation in $K$; positive relational algebra is
interpreted by: selection multiplies by $0/1$, projection/union uses $\oplus$, join/product
uses $\otimes$. Green, Karvounarakis, Tannen (PODS 2007) proved this is the *unique*
semantics making provenance a homomorphism: queries commute with semiring homomorphisms, so
one symbolic evaluation over the **free semiring** $\mathbb{N}[X]$ specializes to all others.

Aggregation needs more structure — a **semimodule** / commutative monoid for the aggregate
values compatible with the annotation semiring (Amsterdamer, Deutch, Tannen, PODS 2011).
For provenance polynomials the value of an output tuple is a sum-of-products over all
derivation trees; its size can be $\Omega(2^{|q|})$, but a **factorized / circuit**
representation (provenance circuit) keeps it polynomial when the query is "hierarchical" or
low-treewidth. Connections: the **AGM bound** still governs the number of nonzero output
annotations; **functional aggregate queries (FAQ)** (Abo Khamis, Ngo, Rudra, PODS 2016)
cast semiring aggregation as variable elimination whose cost is governed by the
**fractional hypertree width** $\mathsf{fhtw}$, giving $O(N^{\mathsf{fhtw}} + |\text{out}|)$.
The dichotomy of Dalvi–Suciu (JACM 2012) separates PTIME from #P-hard queries over the
probability semiring.

## 3. State of the Art (SOTA)

- **Theory SOTA:** **FAQ / InsideOut** (Abo Khamis–Ngo–Rudra, PODS 2016) and **AJAR**
  (Joglekar, Puttagunta, Ré, PODS 2016) give a unified semiring variable-elimination
  algorithm with $\mathsf{fhtw}$-parameterized complexity, subsuming join+aggregation over
  any semiring. **Factorized databases** (Olteanu, Schleich; SIGMOD Record 2016) provide
  succinct representations that make many semiring aggregates output-linear.
- **Systems SOTA:** **ProvSQL** (Senellart et al., VLDB 2018) attaches semiring/provenance
  circuits to PostgreSQL; **GProM** (Glavic et al.) computes provenance via query rewriting;
  **MayBMS / Orion / SPROUT** target the probability semiring. ML-over-DB systems
  (**LMFAO**, **Functional Aggregate** engines) exploit semiring structure for in-database
  learning.
- Probabilistic DB engine work continues to ride the **Dalvi–Suciu dichotomy** and lifted
  inference.

## 4. Upper Bound

For a query $q$ over data of size $N$ and any commutative semiring, FAQ/InsideOut evaluates
join+aggregation in

$$O\!\big(N^{\mathsf{fhtw}(q)} \cdot \log N \;+\; |\text{output}|\big)$$

in the RAM model, where $\mathsf{fhtw}$ is the fractional hypertree width of the (possibly
aggregated) query — this is the best general upper bound and reduces to worst-case-optimal
join bounds when there is no aggregation. Factorized representations let the *result* be
stored in space $O(N^{\mathsf{fhtw}})$ and many aggregates be read off in output-linear
time. For provenance polynomials, **circuit** size $O(N^{\mathsf{fhtw}})$ is achievable, but
*expanding* to monomials can be exponential — so the upper bound is on the circuit, not its
expansion. Overhead factor $\rho$ is $O(\text{semiring-op cost})$ per intermediate when the
$\otimes/\oplus$ are $O(1)$ (e.g. $\mathbb{N}$, tropical), but unbounded for symbolic $K$.

## 5. Lower Bound

- **#P-hardness:** evaluating a single Boolean conjunctive query over the **probability
  semiring** is #P-hard for any non-hierarchical/unsafe query (Dalvi–Suciu dichotomy, JACM
  2012) — an unconditional intractability for that semiring, independent of execution cleverness.
- **Provenance size:** for general queries the provenance polynomial has $\Omega(2^{n})$
  monomials, so any execution that materializes expanded provenance needs exponential time —
  an information-theoretic output-size lower bound.
- **Fine-grained:** join-aggregation over a semiring inherits join lower bounds; under SETH,
  the $N^{\mathsf{fhtw}}$ exponent cannot be improved in general (it matches worst-case
  output for the join skeleton), tying semiring overhead to conjectured join hardness.

## 6. The Gap

The gap is twofold. (1) For *tractable* semirings/queries (set, bag, tropical, hierarchical
probabilistic) we have near-matching $N^{\mathsf{fhtw}}$ bounds, but the **constant/overhead
factor** $\rho$ over Boolean execution is not characterized — when can semiring tracking be
*free*? (2) For *general* provenance/probability the upper bound is a circuit while the lower
bound is on expansion, leaving open *which* semirings admit polynomial-overhead execution and
which provably do not. Closing it requires a semiring-parameterized complexity theory of
execution overhead, plus engines that compute provenance circuits at near-zero marginal cost.

## 7. Current Research (as of June 2026)

- **Tannen, Senellart, Olteanu, Ngo, Ré, Abo Khamis** lines: ProvSQL provenance circuits,
  factorized/FAQ engines, and semiring-aware in-database ML (e.g. Relational AI's worst-case
  optimal + semiring stack) *(frontier — verify)*.
- **Semiring provenance for recursive/Datalog and for the why/how-provenance of aggregation**
  with absorptive/$\omega$-continuous semirings (Grädel–Tannen) *(frontier — verify)*.
- **Differentiable / gradient semirings** for ML and probabilistic programming inside DB
  engines, and approximate (sampling) execution for #P-hard probability semirings.
- Hardware-conscious semiring kernels (SIMD/GPU $\oplus,\otimes$) for low-overhead tracking.

## 8. Future Work

- A dichotomy for *execution overhead* $\rho$ as a function of semiring algebraic properties
  (idempotence, absorption, $0$-divisors).
- Circuit-based provenance with output-linear, streaming maintenance under updates.
- Approximation schemes for #P-hard probabilistic semirings with execution-time guarantees.
- Unifying recursive (fixpoint) semiring evaluation with semi-naive execution.

## 9. Key References

- **[Foundational]** T. J. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007. — [ACM](https://dl.acm.org/doi/10.1145/1265530.1265535)
- **[Foundational]** N. Dalvi, D. Suciu. *The Dichotomy of Probabilistic Inference for Unions of Conjunctive Queries.* JACM 59(6), 2012. — [DOI](https://doi.org/10.1145/2395116.2395119)
- **[SOTA]** M. Abo Khamis, H. Q. Ngo, A. Rudra. *FAQ: Questions Asked Frequently.* PODS, 2016. — [arXiv](https://arxiv.org/abs/1504.04044)
- **[SOTA]** Y. Amsterdamer, D. Deutch, V. Tannen. *Provenance for Aggregate Queries.* PODS, 2011. — [arXiv](https://arxiv.org/abs/1101.1110)
- **[SOTA]** P. Senellart, L. Jachiet, S. Maniu, Y. Ramusat. *ProvSQL: Provenance and Probability Management in PostgreSQL.* PVLDB 11(12), 2018. — [DOI](https://doi.org/10.14778/3229863.3236253)
- **[Survey]** D. Olteanu, M. Schleich. *Factorized Databases.* SIGMOD Record, 2016. — [DOI](https://doi.org/10.1145/3003665.3003667)

## 10. Worked Example

Take $R(A,B)$ with tuples $r_1=(1,2)$ annotated $x$ and $r_2=(1,3)$ annotated $y$, and
$S(B,C)$ with $s_1=(2,9)$ annotated $u$ and $s_2=(3,9)$ annotated $v$. Evaluate
$Q = \pi_C(R \bowtie_B S)$ as a K-relation: join uses $\otimes$, projection uses $\oplus$.

Two join tuples survive: $(1,2,9)$ with annotation $x\otimes u$, and $(1,3,9)$ with
$y\otimes v$. Both project to $C=9$, so the output tuple $(9)$ carries
$$(x\otimes u)\;\oplus\;(y\otimes v).$$

Now *specialize the semiring*:
- **Bag** $\mathbb{N}$ ($\oplus=+,\otimes=\times$) with $x{=}u{=}y{=}v{=}1$: multiplicity $1{\cdot}1+1{\cdot}1=2$.
- **Probability** with $x{=}0.5,u{=}0.4,y{=}0.2,v{=}1$: $0.5{\cdot}0.4+0.2{\cdot}1=0.4$.
- **Tropical** $(\min,+)$ with costs $x{=}3,u{=}5,y{=}1,v{=}2$: $\min(3{+}5,\,1{+}2)=3$.

One symbolic evaluation $xu \oplus yv$, then a homomorphism per semiring — exactly the
Green–Karvounarakis–Tannen guarantee.

---
*Part of the [DBMS Research catalog](../../README.md).*
