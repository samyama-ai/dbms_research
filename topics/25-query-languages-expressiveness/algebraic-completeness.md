# Expressive Completeness of Algebraic Query Languages

> **Topic:** Query Languages & Expressiveness · **ID:** `25-query-languages-expressiveness/algebraic-completeness` · **Status:** partially-solved

## 1. Problem Statement

What, exactly, can an *algebraic* query language express, and what is a minimal/natural **operator basis** that achieves a given expressive class? Concretely:

- **Relational algebra (RA):** is it expressively complete for some logic, and complete relative to what notion of "query"?
- **Nested-relational algebra (NRA):** which operators are needed once attributes can be relations, and does nesting add power at flat-relation level?
- **Tensor / linear algebra (LA):** which linear-algebra operator sets are needed to express RA-style queries (and conversely), e.g. for ML-on-databases and graph workloads?

Variants: (i) **expressive-completeness** (which query class is captured exactly), (ii) **operator-basis minimality** (is each operator non-redundant; can one operator be dropped), and (iii) **conservativity** (does adding a feature — nesting, recursion, arithmetic — change what is expressible on inputs/outputs that don't use it). Status is **partially-solved**: RA's characterization is classical and tight; NRA's is largely settled (Paredaens–Van Gucht, Wong); LA's is an active, only-partially-resolved frontier.

## 2. Mathematical Foundations

**Codd's theorem.** Relational algebra is *expressively equivalent* to the domain/tuple relational calculus (safe, domain-independent first-order logic): $\mathrm{RA} \equiv \mathrm{FO}$. The RA basis is $\{\sigma, \pi, \times, \cup, \setminus\}$ (selection, projection, product, union, difference), with $\bowtie$, $\cap$, $\div$ derivable. Each of the five is independent (dropping any strictly reduces power). Crucially RA/FO **cannot express transitive closure or parity/counting** — proven via Ehrenfeucht–Fraïssé games and locality (Gaifman/Hanf locality, the bounded-degree property).

**Nested relations.** The nested-relational algebra adds **nest** $\nu$ and **unnest** $\mu$ over set-valued attributes; equivalently the **complex-object algebra** / monad-comprehension calculus with $\mathrm{powerset}$ or with bounded nesting. **Conservativity (Paredaens–Van Gucht 1992; Wong 1996):** NRA *without powerset* is **conservative** over RA — any NRA query whose input and output are flat is already expressible in flat RA; nesting is convenience, not extra flat power. Adding **powerset** jumps to a strictly larger class (elementary, captures e.g. transitive closure).

**Linear/tensor algebra.** Treat relations as (sparse) tensors/matrices; operators: matrix product, transpose, element-wise ops, reductions/sums, diag, and order-3+ contractions. The question is which fragment of LA equals RA-restricted-to-certain-arities, and what LA needs beyond bilinear maps. Formal yardsticks: the **MATLANG** / **sum-MATLANG** calculi (Brijder, Geerts, Van den Bussche, Weerwag) with results like $\mathrm{MATLANG} \subsetneq \mathrm{FO}$ on adjacency matrices, and extensions with summation/eigen-ops climbing toward FO+counting.

## 3. State of the Art (SOTA)

- **RA $\equiv$ FO:** Codd 1972; locality/inexpressibility via Libkin's *Elements of Finite Model Theory* (2004), the canonical synthesis.
- **NRA:** conservativity and operator basis settled by **Paredaens–Van Gucht (TODS 1992)** and **Wong (1996)**; comprehension-calculus presentation by **Buneman–Naqvi–Tannen–Wong (TCS 1995)**.
- **Linear algebra:** **MATLANG** (Brijder, Geerts, Van den Bussche, Weerwag, *ICDT/TODS 2019*) precisely locates matrix-algebra expressiveness; **sum-MATLANG** and **LARA** (Hutchison, Howe, Suciu) propose unifying relational+linear bases. This is the unsettled, partially-solved part.

## 4. Upper Bound

- RA evaluation is in **$\mathrm{AC}^0$** data complexity (FO = uniform $\mathrm{AC}^0$); every RA query is computable in **LOGSPACE** (indeed within the circuit class $\mathrm{AC}^0$), with combined complexity **PSPACE-complete**.
- NRA without powerset: same flat-data complexity as RA ($\mathrm{AC}^0$/LOGSPACE) by conservativity; with powerset, evaluation can be **elementary** but non-elementary in nesting depth in the worst case.
- MATLANG-style LA fragments: bounded by **FO with counting (FO+C)** / uniform $\mathrm{TC}^0$ for the summation-equipped variants — an upper bound on expressiveness, not just cost.

## 5. Lower Bound

- **RA/FO cannot express transitive closure, connectivity, parity, or "EVEN cardinality"** — Ehrenfeucht–Fraïssé / locality lower bounds (Gaifman locality; Hanf-locality). These are *unconditional, model-theoretic* lower bounds, not complexity-conditional.
- NRA **with powerset** strictly exceeds RA (separates by expressing TC), an unconditional separation.
- For LA: adjacency-matrix MATLANG **cannot** express all of FO (e.g. certain non-local Boolean queries) without summation — separations proved via algebraic/EF-style arguments (Geerts et al.).

## 6. The Gap

For RA and NRA the picture is **closed**: tight equivalences and independence/conservativity proofs exist. The genuinely **open** part is the **tensor/linear-algebra side**: a clean, agreed minimal operator basis equating a natural LA fragment with RA, RA+counting, or fixpoint logics — and conservativity results when LA and RA operators are mixed (LARA-style). Pinning the exact place of order-$\geq 3$ tensor contraction, eigen/inverse operators, and aggregation in the FO/FO+C/fixpoint hierarchy is the remaining work.

## 7. Current Research (as of June 2026)

- **MATLANG/LARA expressiveness** and conservativity (Geerts, Van den Bussche, Brijder; Suciu's group) — locating eigenvalue, inverse, and order-3 contraction operators relative to FO+C and fixpoint logic. *(frontier — verify)*
- **Tensor relational algebra** for ML-in-DB and the algebra of **datalog $\times$ linear algebra** (e.g. relational matrix-multiply, FAQ/AJAR aggregation frameworks of Abo Khamis–Ngo–Rudra). *(frontier — verify)* unifying-basis proposals.
- Renewed interest via **GQL/SQL:2023 property-graph** algebra fragments and their completeness relative to graph logics.

## 8. Future Work

- A canonical minimal operator basis equating LA with a named logic, with independence proofs.
- Conservativity theorems for mixed relational+linear+aggregation algebras.
- Operator bases for streaming/incremental and for differentiable (gradient-carrying) query algebras.

## 9. Key References

- **[Foundational]** Codd. *Relational Completeness of Data Base Sublanguages.* Database Systems (Courant), 1972. — [DBLP](https://dblp.org/rec/conf/codd/Codd72.html)
- **[Foundational]** Paredaens, Van Gucht. *Converting Nested Algebra Expressions into Flat Algebra Expressions.* ACM TODS, 1992 (conservativity). — [DOI](https://doi.org/10.1145/128765.128768)
- **[Foundational]** Buneman, Naqvi, Tannen, Wong. *Principles of Programming with Complex Objects and Collection Types.* TCS, 1995. — [DOI](https://doi.org/10.1016/0304-3975(95)00024-Q)
- **[Survey]** Libkin. *Elements of Finite Model Theory.* Springer, 2004 (locality, RA = FO, inexpressibility). — [DOI](https://doi.org/10.1007/978-3-662-07003-1)
- **[SOTA]** Brijder, Geerts, Van den Bussche, Weerwag. *On the Expressive Power of Query Languages for Matrices (MATLANG).* ACM TODS, 2019. — [arXiv](https://arxiv.org/abs/1709.08359) · [DOI](https://doi.org/10.1145/3331445)
- **[SOTA]** Abo Khamis, Ngo, Rudra. *FAQ: Questions Asked Frequently.* PODS, 2016 (algebraic aggregation framework spanning relational and tensor computation). — [arXiv](https://arxiv.org/abs/1504.04044) · [DOI](https://doi.org/10.1145/2902251.2902280)

## 10. Worked Example

**NRA nesting is convenient but not extra flat power.** Take $\mathrm{Enroll}(\text{student},\text{course})$:

| student | course |
|---------|--------|
| Ann | DB |
| Ann | OS |
| Bo  | DB |

A natural NRA query nests courses per student: $\nu_{\text{course}}(\mathrm{Enroll})$ yields the nested relation $\{(\text{Ann},\{\text{DB},\text{OS}\}),\ (\text{Bo},\{\text{DB}\})\}$. Now suppose we want a *flat* output: pairs of students sharing a course. Going through the nested value, we could intersect course-sets. But the conservativity theorem (Paredaens–Van Gucht) says any flat-to-flat NRA query is already flat-RA expressible: the shared-pair query is just
$$\pi_{s_1,s_2}\big(\rho_{s_1/\text{student}}(\mathrm{Enroll}) \bowtie_{\text{course}} \rho_{s_2/\text{student}}(\mathrm{Enroll})\big),$$
giving $\{(\text{Ann},\text{Ann}),(\text{Ann},\text{Bo}),(\text{Bo},\text{Ann}),(\text{Bo},\text{Bo})\}$ — no nesting needed.

**Where powerset crosses the line.** "Is the course-graph connected?" requires transitive closure, which flat RA/FO *cannot* express (locality). Adding $\mathrm{powerset}$ lets NRA build the set of all student-subsets and test closure properties, jumping strictly above RA — the unconditional separation of §5.

---
*Part of the [DBMS Research catalog](../../README.md).*
