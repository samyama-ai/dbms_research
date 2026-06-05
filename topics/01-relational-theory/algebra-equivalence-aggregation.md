# Relational Algebra Equivalence with Aggregation

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/algebra-equivalence-aggregation` · **Status:** open

## 1. Problem Statement

**Query equivalence** asks: given two query expressions $E_1, E_2$, do they return the same result on *every* database instance, $E_1 \equiv E_2$? Equivalence underpins semantic query optimization, view-based rewriting, regression testing, and verified query compilers. This problem targets equivalence (and the related **containment** $E_1 \sqsubseteq E_2$) for **relational algebra extended with grouping ($\gamma$) and aggregation functions** ($\mathrm{COUNT}$, $\mathrm{SUM}$, $\mathrm{AVG}$, $\mathrm{MIN}$, $\mathrm{MAX}$), under realistic **bag (multiset) semantics** and SQL's **NULL** handling.

Variants:

- **Decision (equivalence/containment)** over set vs. bag semantics, with/without arithmetic on aggregated values.
- **Restricted fragments**: conjunctive queries with a single aggregate, $\mathrm{COUNT}(*)$-only, $\mathrm{SUM}$/$\mathrm{MAX}$ over CQs, queries with `HAVING`/grouping.
- **Equivalence modulo integrity constraints** $\Sigma$ (FDs/keys), which can make otherwise-inequivalent grouped queries equivalent.

The central difficulty: aggregation is *not monotone*, the classical homomorphism technique fails, and bag semantics turns containment into a question about multiplicities (counting homomorphisms).

## 2. Mathematical Foundations

For **set-semantics CQs**, equivalence/containment is decidable by the **Chandra–Merlin theorem (STOC 1977)**: $Q_1 \sqsubseteq Q_2$ iff there is a homomorphism $Q_2 \to Q_1$ (canonical-database / homomorphism test), making containment **NP-complete**. Under constraints, the **chase** extends this test.

**Bag semantics** changes everything: $Q_1 \equiv_{\text{bag}} Q_2$ iff the queries are **isomorphic as expressions** (Chaudhuri–Vardi, PODS 1993), but **bag-containment** of CQs is a deep open problem — its decidability is *unknown*, with known connections to **Hilbert's Tenth Problem**-style Diophantine reasoning and to **homomorphism-counting**.

Aggregation is formalized by mapping grouped results into a **semiring/semimodule** of values (cf. provenance for aggregates, Amsterdamer–Deutsch–Tannen). $\mathrm{COUNT}$ corresponds to the counting semiring $\mathbb{N}$; $\mathrm{MAX}/\mathrm{MIN}$ to the tropical semiring; $\mathrm{SUM}$ to $\mathbb{Z}$-linear combinations. Equivalence of $\mathrm{COUNT}$-queries reduces to **bag-equivalence**; $\mathrm{SUM}$-queries to **$\mathbb{Z}$-linear** (counting) equivalence; $\mathrm{MAX}$ to set-equivalence of underlying tuples. This places the problem at the interface of finite model theory, the theory of **homomorphism counts** (Lovász; Chen–Mengel; Dell–Grohe–Rattan), and Diophantine decidability.

## 3. State of the Art (SOTA)

- **Theory-SOTA**: Cohen–Nutt–Sagiv (*JCSS* / PODS 1999, 2006) gave decidability and complexity for equivalence of **aggregate conjunctive queries** with $\mathrm{COUNT}$, $\mathrm{SUM}$, $\mathrm{MAX}$, $\mathrm{MIN}$ (decidable via reduction to bag/set equivalence) — the standard reference. Bag-equivalence of CQs is decidable (isomorphism); **bag-containment remains open**.
- **Systems-SOTA**: **Cosette** (Chu–Wang–Cheung–Suciu, CIDR/VLDB 2017) and its successors **UDP/SQLSolver** prove/refute SQL equivalences using a semiring (U-semiring) model + symbolic reasoning and SMT; **WeTune** (Wang et al., SIGMOD 2022) auto-discovers rewrite rules via verified equivalence. These handle aggregation/bag SQL pragmatically but **incompletely** (sound, not complete).

## 4. Upper Bound

- **Set-semantics CQ containment**: **NP-complete** (Chandra–Merlin), in the standard combined-complexity model; **$\Pi_2^p$**/decidable under common constraint classes via the chase.
- **Aggregate CQ equivalence** ($\mathrm{COUNT}$, $\mathrm{SUM}$, $\mathrm{MAX}$, $\mathrm{MIN}$): **decidable**, with complexity from **NP** up to higher levels of PH depending on the aggregate and arithmetic (Cohen–Nutt–Sagiv).
- **Bag equivalence of CQs**: decidable, **graph-isomorphism-flavored** (no polynomial bound known to be tight). Tools like SQLSolver give *decidable-in-practice* but theoretically incomplete coverage.

## 5. Lower Bound

- Set CQ containment/equivalence is **NP-hard** (Chandra–Merlin, 1977).
- **Bag-containment** of conjunctive queries is **not known to be decidable**; it is at least as hard as long-standing number-theoretic problems and is widely conjectured **undecidable** (links to Diophantine equations / Hilbert's Tenth). This is the dominant lower-bound barrier.
- Adding **inequalities** ($\leq$) to CQs already makes containment **$\Pi_2^p$-complete** (van der Meyden); with aggregation and arithmetic, undecidability looms for sufficiently rich fragments.

## 6. The Gap

This is **genuinely open**. While *equivalence* of the standard aggregate CQ classes is decided (Cohen–Nutt–Sagiv), the surrounding territory is not: **bag-containment** of plain CQs — a prerequisite for full $\mathrm{COUNT}/\mathrm{SUM}$ containment — has unknown decidability after 30+ years; equivalence with **arithmetic on aggregates**, **`HAVING`**, **outer joins**, and **three-valued NULL** semantics has no decision procedure and is suspected undecidable in full generality. The gap is therefore at the **decidability frontier**, not merely complexity tightness. Closing it requires either a decision procedure for bag-containment or an undecidability proof, plus a faithful treatment of SQL NULLs/bags.

## 7. Current Research (as of June 2026)

- **Suciu, Chu, Wang, Cheung**: the **U-semiring / SQLSolver / SQLSolver+** line — algebraic, SMT-backed equivalence checkers extending to more aggregation and recursion. *(frontier — verify)*
- **WeTune / verified-rewrite** efforts (Tsinghua, MIT): mining and certifying equivalence-preserving rewrites for optimizers.
- **Hannula, Kontinen, Geerts** and others: information-theoretic / counting characterizations of bag equivalence; renewed attacks on bag-containment decidability.
- Coq/Lean-formalized relational algebra equivalence kernels.

## 8. Future Work

- Resolve **decidability of bag-containment** for CQs (the keystone open problem).
- Complete decision procedures for **SUM/AVG with arithmetic** and **`HAVING`** predicates.
- Equivalence under **bag + NULL (3-valued)** semantics matching real SQL.
- Marrying complete theory with the scalable, incomplete SMT tools used in optimizers.

## 9. Key References

- **[Foundational]** Chandra, A.K., Merlin, P.M. *Optimal Implementation of Conjunctive Queries in Relational Databases.* STOC, 1977. — [DOI](https://doi.org/10.1145/800105.803397)
- **[Foundational]** Chaudhuri, S., Vardi, M.Y. *Optimization of Real Conjunctive Queries (Bag Semantics).* PODS, 1993. — [DOI](https://doi.org/10.1145/153850.153856)
- **[Foundational]** Cohen, S., Nutt, W., Sagiv, Y. *Deciding Equivalences Among Conjunctive Aggregate Queries.* JACM / PODS, 1999–2007. — [DOI](https://doi.org/10.1145/1219092.1219093)
- **[SOTA]** Chu, S., Weitz, K., Cheung, A., Suciu, D. *HoTTSQL / Cosette: Proving Query Rewrites with Univalent SQL Semantics.* PLDI / CIDR, 2017. — [arXiv](https://arxiv.org/abs/1607.04822)
- **[SOTA]** Wang, Z., Zhou, Z., Yang, Y., et al. *WeTune: Automatic Discovery and Verification of Query Rewrite Rules.* SIGMOD, 2022. — [DOI](https://doi.org/10.1145/3514221.3526125)
- **[Survey]** Sagiv, Y., Yannakakis, M. *Equivalences Among Relational Expressions with the Union and Difference Operators.* JACM, 1980. — [DOI](https://doi.org/10.1145/322217.322221)

## 10. Worked Example

Consider relation $R(A)$ with bag $\{1,1,2\}$ and two queries returning $\mathrm{COUNT}(*)$ grouped by $A$:

- $Q_1$: `SELECT A, COUNT(*) FROM R GROUP BY A` → $\{(1,2),(2,1)\}$.
- $Q_2$: `SELECT A, COUNT(*) FROM R, S WHERE R.A=S.A GROUP BY A`, with $S(A)=\{1\}$ → $\{(1,2)\}$.

**Set semantics would lose this distinction.** The *set* of $A$-values projected from each differs ($\{1,2\}$ vs $\{1\}$), so a homomorphism test could separate them — but the subtlety is the *count*. Now take

- $Q_3$: `SELECT x FROM R(x),R(y)` and $Q_4$: `SELECT x FROM R(x)`.

Set-equivalent (both have homomorphic-equivalent bodies), yet on $R=\{a,a\}$, $Q_3$ yields $x{=}a$ with multiplicity $|R|^2=4$ while $Q_4$ yields $2$. So $Q_3\not\equiv_{\mathrm{bag}}Q_4$: the count polynomials $|R|^2$ vs $|R|$ differ. This is exactly the Chaudhuri–Vardi insight — bag equivalence = body isomorphism, and *containment* ($|R|\le|R|^2$ here) is the open, Diophantine-flavored frontier.

---
*Part of the [DBMS Research catalog](../../README.md).*
