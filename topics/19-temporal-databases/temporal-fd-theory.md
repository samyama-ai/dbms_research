# Temporal Functional Dependency Theory

> **Topic:** Temporal Databases · **ID:** `19-temporal-databases/temporal-fd-theory` · **Status:** open

## 1. Problem Statement

A *temporal functional dependency* (TFD) constrains how attribute values may co-vary across time. Informally, $X \to Y$ holds "temporally" if, within every temporally coherent grouping of tuples, equal $X$-values force equal $Y$-values. But "temporally coherent" admits many readings — snapshot-wise ($X \to Y$ in every database state), interval-wise (over maximal periods of agreement), and granularity-relative ($X \xrightarrow{\mu} Y$ where the constraint is evaluated at granularity $\mu$, e.g. *salary is fixed per-month but may change per-year*). The open problem is to produce a **single dependency language with a sound and complete finite axiomatization** that subsumes these readings, together with a **normalization theory** (analogues of 3NF/BCNF and a dependency-preserving, lossless decomposition algorithm) that respects time.

Concretely:
- **Decision (implication):** given a set $\Sigma$ of TFDs and a candidate $\sigma$, does $\Sigma \models \sigma$? Is implication finitely axiomatizable and decidable, and at what complexity?
- **Optimization (normalization):** compute a minimum-cost lossless, dependency-preserving decomposition into temporal-BCNF/3NF.
- **Counting/enumeration:** enumerate a canonical cover or all minimal keys over time.

The difficulty is that granularities form a lattice and interact with the dependency, so the inference rules cannot simply be Armstrong's axioms.

## 2. Mathematical Foundations

Let a temporal relation be $r \subseteq \mathrm{dom}(U) \times \mathbb{T}$ where $\mathbb{T}$ is a (discrete, totally ordered) time domain and $U$ the attribute set. A **granularity** $\mu$ is a partition of $\mathbb{T}$ into contiguous granules; granularities form a lattice under *finer-than* $\preceq$. Wijsen's TFD $X \xrightarrow{\mu} Y$ holds iff for all tuples $t_1,t_2$ whose timestamps fall in the same $\mu$-granule, $t_1[X]=t_2[X] \Rightarrow t_1[Y]=t_2[Y]$.

Classical results: ordinary FDs are axiomatized by **Armstrong's axioms** (reflexivity, augmentation, transitivity), with implication decidable in linear time via attribute closure $X^+$. For TFDs the analogue must add a **granularity rule** (if $X\xrightarrow{\mu}Y$ and $\mu' \preceq \mu$ then $X\xrightarrow{\mu'}Y$) and rules governing temporal grouping. Wijsen proved sound and complete axiomatizations for restricted classes and showed implication is decidable; the unrestricted case mixing multiple granularities and "dynamic" dependencies (constraints relating consecutive states, e.g. $X \to_{\text{next}} Y$) is where completeness/decidability remain open or only partially mapped.

Key theorems it rests on: Armstrong relations and their existence; the **chase** for embedded dependencies; undecidability of implication for general embedded tuple/equality-generating dependencies (Beeri–Vardi), which bounds how expressive a temporally-complete language can become before implication becomes undecidable.

## 3. State of the Art (SOTA)

- **Wijsen (TKDE 1999; ICDT/IS 1990s–2000s):** granularity-based TFDs, sound and complete axiomatization for the single-relation case, polynomial implication, and a temporal-BCNF.
- **Jensen, Snodgrass, Su — "Unifying Temporal Data Models via a Conceptual Model" (IS 1994)** and the **Jensen–Snodgrass temporal-keys / temporal normal form (TNF)** line: normalization driven by separating time-varying from time-invariant attributes.
- **Vianu's dynamic functional dependencies (1987)** for update-driven constraints relating old/new states — the theoretical root of "dynamic" TFDs.
- Systems side: SQL:2011 application-time/system-time periods give primary-key uniqueness *over time* but no general TFD enforcement; enforcement is left to triggers/constraints.

## 4. Upper Bound

For Wijsen's granularity TFDs over a fixed granularity lattice, **implication is decidable in polynomial time** via a temporal closure computation generalizing $X^+$. Lossless-join temporal decomposition is computable; producing a *dependency-preserving* temporal-3NF synthesis is achievable in polynomial time in the size of a canonical cover (mirroring Bernstein synthesis) for the single-granularity fragment. BCNF decomposition can be exponential in the worst case (as classically), and minimum-cost decomposition is NP-hard (inherited from the non-temporal case).

## 5. Lower Bound

Implication for FDs alone is trivially in P, so hardness arises only with richer features. Determining whether a decomposition is BCNF / finding a minimal key is **NP-complete** (Lucchesi–Osborn for prime-attribute / key problems), and these lower bounds transfer to the temporal setting. For combined classes mixing TFDs with inclusion or "next-state" (dynamic) dependencies, implication can become **undecidable**, inherited from undecidability of implication for general embedded dependencies (Beeri–Vardi) and from the word/tiling encodings used for temporal-logic satisfiability over $\mathbb{T}$. Pinning the exact decidability frontier as features are added is the open lower-bound question.

## 6. The Gap

The single-granularity, single-relation fragment is essentially closed (P-time, axiomatized). The gap is the **multi-granularity + dynamic + multi-relation** combination: no one has a finite complete axiomatization that simultaneously covers granularity reasoning *and* inter-state (temporal) dependencies, and the decidability boundary between "still axiomatizable/decidable" and "undecidable" is not sharply drawn. Closing it requires either a new normal-form theorem with a matching completeness proof, or an undecidability reduction showing the full language is too expressive.

## 7. Current Research (as of June 2026)

Active threads: integrating TFDs with SQL:2011 bitemporal semantics so that declared period keys imply enforceable normal forms; data-profiling work on **discovering** approximate TFDs from logs (extending FD-discovery algorithms like TANE/HyFD to interval data) *(frontier — verify)*; and constraint repair for temporal data. Groups historically central are Wijsen (Mons), Snodgrass/Currim (Arizona), and the TimeCenter alumni network; recent activity appears in the data-profiling community (Naumann group, HPI) on temporal/streaming dependency discovery *(frontier — verify)*.

## 8. Future Work

- A complete axiomatization unifying granularity reasoning with dynamic (state-transition) TFDs.
- A temporal-BCNF that is simultaneously lossless, dependency-preserving, and history-preserving, with a characterization of when all three are achievable.
- Practical discovery of approximate TFDs at scale, with statistical guarantees.
- Reconciliation with bitemporal models (see *Bitemporal Normal Forms*).

## 9. Key References

- **[Foundational]** Codd, E.F. *A Relational Model of Data for Large Shared Data Banks.* CACM, 1970. — [DOI](https://doi.org/10.1145/362384.362685)
- **[Foundational]** Wijsen, J. *Temporal FDs on Complex Objects / Design of Temporal Relational Databases Based on Dynamic and Temporal Functional Dependencies.* IEEE TKDE, 1999. — [Temporal FDs on Complex Objects, ACM TODS 24(1) 1999, DOI](https://doi.org/10.1145/310701.310715)
- **[Foundational]** Vianu, V. *Dynamic Functional Dependencies and Database Aging.* JACM, 1987. — [DOI](https://doi.org/10.1145/7531.7918)
- **[Foundational]** Jensen, C.S., Snodgrass, R.T., Soo, M.D. *Unifying Temporal Data Models via a Conceptual Model.* Information Systems, 1994. — [DOI](https://doi.org/10.1016/0306-4379(94)90013-2)
- **[Foundational]** Abiteboul, S., Hull, R., Vianu, V. *Foundations of Databases.* Addison-Wesley, 1995 (chase, dependency theory). — [DBLP](https://dblp.org/rec/books/aw/AbiteboulHV95.html)
- **[Survey]** Lucchesi, C.L., Osborn, S.L. *Candidate Keys for Relations.* JCSS, 1978. — [DOI](https://doi.org/10.1016/0022-0000(78)90009-0)

## 10. Worked Example

Let the TFD be $\text{Emp} \xrightarrow{\text{month}} \text{Salary}$: *within any month, an employee's salary is fixed, but it may change across months.* Tuples carry a day-granularity timestamp:

| Emp | Salary | day |
|-----|--------|-----|
| Alice | 5000 | Jan-10 |
| Alice | 5000 | Jan-25 |
| Alice | 5200 | Feb-03 |

Group by month-granule. The Jan-granule holds the two Jan tuples: both have $\text{Emp}=\text{Alice} \Rightarrow \text{Salary}=5000$ — **consistent**. The Feb-granule holds one tuple — trivially consistent. So $\text{Emp}\xrightarrow{\text{month}}\text{Salary}$ **holds**.

Now add Alice, $4800$, Jan-30. The Jan-granule now has $\{5000,5000,4800\}$ for the same Emp — the dependency is **violated** at granularity month, though it would still hold at granularity *day* (each day has one value). This shows the granularity rule: $\mu' \preceq \mu$ (day finer than month) means $X\xrightarrow{\text{month}}Y \Rightarrow X\xrightarrow{\text{day}}Y$, but not conversely — exactly why ordinary attribute-closure $X^+$ must be lifted with the granularity lattice to decide implication.

---
*Part of the [DBMS Research catalog](../../README.md).*
