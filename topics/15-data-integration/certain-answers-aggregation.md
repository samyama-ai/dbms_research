# Certain Answers for Aggregate Queries

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/certain-answers-aggregation` · **Status:** open

## 1. Problem Statement

Standard **certain answers** are defined for queries returning *tuples*: an answer is certain if it holds in every possible world (every solution/completion of incomplete data). This intersection semantics breaks down for **aggregate queries** (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `GROUP BY`): each possible world may yield a *different numeric value*, so the naïve intersection of answer sets is almost always **empty**, giving no useful certainty.

The problem: **define a coherent semantics for certain answers to aggregate queries over incomplete / exchanged data**, and provide **tractable evaluation**. Over a set of possible worlds $\{W\}$ with aggregate values $\{v_W\}$, candidate semantics include: the **range** $[\min_W v_W, \max_W v_W]$ (certain bounds), the **certain value** (when all $v_W$ coincide), and refined notions over **labeled-null / conditional-table** representations.

Variants: (i) **decision** — is $v$ a certain/possible aggregate value? (ii) **range computation** — compute tight $[\,\underline{v}, \overline{v}\,]$; (iii) **counting** — how many worlds achieve a value. The problem is *open*: no single agreed-upon semantics is both intuitive and uniformly tractable across the aggregate functions and incompleteness models.

## 2. Mathematical Foundations

Incomplete data is modeled by **naïve tables / conditional tables (c-tables)** (Imieliński–Lipski) or by the space of solutions in **data exchange** (the universal solution with **labeled nulls**). The set of *possible worlds* is the set of ground completions / valuations of nulls.

For a non-aggregate query $Q$, $\mathsf{cert}(Q) = \bigcap_W Q(W)$. For an aggregate $\alpha$, the meaningful objects are the **certain bounds**:
$$\mathsf{cert}^{\min}(\alpha) = \min_W \alpha(W), \qquad \mathsf{cert}^{\max}(\alpha) = \max_W \alpha(W).$$
Computing these is an **optimization over valuations of nulls** subject to integrity constraints — naturally an **integer/linear program** for `SUM`/`COUNT`, and a **fractional/ratio optimization** for `AVG`. Arenas–Barceló–Libkin and later work (Libkin, "SQL's null semantics") supply the formal grounding, distinguishing **marked vs. unmarked nulls** and the role of `GROUP BY` over uncertain grouping keys.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Foundational treatment by **Arenas, Libkin** and collaborators on certain answers in exchange; **Afrati–Kolaitis** ("Answering aggregate queries in data exchange," PODS 2008) gave the first systematic semantics and complexity for `COUNT/SUM/AVG/MIN/MAX` under s-t TGDs, using the universal solution and a notion of certain *interval* answers. **Console, Guagliardo, Libkin** advanced approximate certain answers with correctness guarantees (the "certain answers with nulls" program). 
- **Systems-SOTA.** Probabilistic/incomplete-DB engines — **MayBMS**, **ProbDB/Orchestra**, and approximate-answer prototypes — compute bounds; mainstream SQL engines ignore certainty and apply ad-hoc null arithmetic, which is *unsound* for certainty.

## 4. Upper Bound

Afrati–Kolaitis show that for mappings given by s-t TGDs, **certain range answers** for `MIN`/`MAX` are **PTime** (data complexity) and reduce to evaluating extremal completions of the universal solution; for `COUNT` and certain forms of `SUM` over the core/universal solution, **PTime** algorithms exist by counting non-null contributions and bounding null contributions. The bounds are computed in the **standard model** over the canonical universal (or core) solution; `AVG` is handled via paired SUM/COUNT optimization. Approximate-certain-answer frameworks (Libkin et al.) give **PTime** evaluation with one-sided soundness for richer queries.

## 5. Lower Bound

For more expressive settings, the optimization becomes hard: computing exact certain `SUM`/`AVG` bounds under **target constraints (EGDs/TGDs)** or with **selection over uncertain values** is **NP-hard / coNP-hard** (it embeds integer programming / subset-sum-style choices over null valuations). Deciding the **exact** certain value of an aggregate over c-tables is **coNP-hard** in general; counting worlds achieving a value is **#P-hard**. These are *worst-case* hardness results in the standard complexity model; `AVG` is particularly hard due to its **non-monotone, ratio** nature (extremes need not occur at extremal completions).

## 6. The Gap

**Genuinely open** on two axes. (1) **Semantic axis:** there is no community-wide agreed definition — range vs. point vs. distributional ("expected") certain answers each have drawbacks; reconciling them, especially under `GROUP BY` with **uncertain grouping keys** and under constraints, is unsettled. (2) **Complexity axis:** a clean dividing line between PTime and (co)NP-/#P-hard cases is mapped only for restricted fragments (no target EGDs, simple aggregates). Tractable, *sound* approximations that work uniformly for `SUM`/`AVG` with selections and constraints are missing.

## 7. Current Research (as of June 2026)

Active work continues the **"certain answers with nulls / approximate certain answers"** program (Libkin, Console, Guagliardo, Toussaint) extending one-sided-sound PTime evaluation toward aggregation and `GROUP BY`. *(frontier — verify)* Recent ICDT/PODS 2025 papers explore **interval / abstract-domain semantics** for aggregates over incomplete data and connections to **probabilistic databases** (expected aggregates as a complementary semantics). *(frontier — verify)* Interest is rising in **certain answers for analytics/OLAP** over lakehouse data with missing values, and in LLM/ML-imputed data where uncertainty must be tracked.

## 8. Future Work

- A unifying semantics covering range, exact, and expected aggregate answers, including `GROUP BY`.
- Sharp PTime-vs-hard dichotomies under target constraints for each aggregate function.
- Sound, tight **approximation** algorithms for `SUM`/`AVG` with selections.
- Integration with probabilistic DBs and with OLAP engines for practical "uncertain analytics."

## 9. Key References

- **[Foundational]** T. Imieliński, W. Lipski. *Incomplete Information in Relational Databases.* JACM, 1984. (c-tables.)
- **[Foundational]** F. Afrati, P. Kolaitis. *Answering Aggregate Queries in Data Exchange.* PODS, 2008.
- **[Foundational]** M. Arenas, L. Bertossi, J. Chomicki. *Consistent Query Answers in Inconsistent Databases.* PODS, 1999. (Related certainty semantics.)
- **[SOTA]** P. Guagliardo, L. Libkin. *Making SQL Queries Correct on Incomplete Databases.* PODS, 2017.
- **[SOTA]** M. Console, P. Guagliardo, L. Libkin. *Approximations and Refinements of Certain Answers via Many-Valued Logics.* KR, 2016.
- **[Survey]** L. Libkin. *SQL's Three-Valued Logic and Certain Answers.* ACM TODS, 2016.
- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data exchange: semantics and query answering.* TCS, 2005.

---
*Part of the [DBMS Research catalog](../../README.md).*
