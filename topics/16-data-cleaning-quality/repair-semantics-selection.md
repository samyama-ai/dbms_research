---
id: 16-data-cleaning-quality/repair-semantics-selection
title: "Optimal Repair Semantics Selection"
topic: 16-data-cleaning-quality
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimal Repair Semantics Selection

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/repair-semantics-selection` · **Status:** open

## 1. Problem Statement

Given a dirty instance $I$, constraints $\Sigma$, an application $A$ (with its queries, downstream cost/utility, and tolerance for over-/under-deletion), **decide which repair semantics** the cleaning pipeline should adopt, and characterize how the candidate semantics relate. Candidate semantics:

- **Subset (S-)repair:** delete tuples only ($I' \subseteq I$).
- **Superset (insertion) repair:** add tuples only ($I' \supseteq I$) — for inclusion/foreign-key dependencies.
- **Update (U-)repair:** modify cell values, preserving tuple identity.
- **Cardinality repair:** maximize $|I \cap I'|$ (minimal symmetric difference / fewest changes), orthogonal to the operation type.
- **Cost/preference repairs:** minimize a weighted cost or respect a preference order.

Variants:
- **Decision:** For a given $A$, does semantics $X$ dominate $Y$ (yield no-worse consistent answers / utility) on all/most instances?
- **Optimization:** Choose $X^\star = \arg\max_X \mathrm{Utility}_A(X)$.
- **Relational:** Establish inclusion/incomparability lattice among repair sets $\mathrm{Rep}_X(I,\Sigma)$.

## 2. Mathematical Foundations

Each semantics induces a family $\mathrm{Rep}_X(I,\Sigma) \subseteq \{I' : I' \models \Sigma\}$ ordered by a *distance* $\delta_X(I, I')$:
- S-repair: $\subseteq$-maximality, $\delta = |I \setminus I'|$ (tuple deletions).
- U-repair: cell Hamming distance, $\delta = |\{(t,a) : I[t,a] \neq I'[t,a]\}|$.
- Cardinality: $\delta = |I \triangle I'|$ minimized.

Consistent answers are the **certain answers** $\bigcap_{I'\in\mathrm{Rep}_X} Q(I')$; different $X$ yield different certain-answer sets, so **semantics selection changes query semantics**, not just efficiency. Key structural facts:

- Inclusion relationships: $\subseteq$-repairs vs. cardinality repairs differ (a cardinality repair need not be a maximal subset repair under multiple FDs).
- **AGM-style belief-revision** grounding: repairs realize the AGM postulates of minimal change; choice of $\delta$ = choice of revision operator.
- The complexity of CQA *jumps* across semantics: e.g., CQA can be FO-rewritable under S-repairs yet $\mathsf{coNP}$-hard under U-repairs for the same $(Q,\Sigma)$, so semantics selection is also a **tractability decision**.

## 3. State of the Art (SOTA)

- **Wijsen (2005)** "Database Repairing Using Updates" formalized U-repairs and showed they are *incomparable* to S-repairs in expressive power.
- **Afrati & Kolaitis (ICDT 2009)** mapped CQA complexity across **subset, superset, and ⊕(symmetric-difference)** repair semantics and dependency classes (a near-complete map for these axes).
- **Lopatenko & Bertossi (ICDT 2007)** analyzed **cardinality-based** repairs and their distinct complexity.
- **Systems:** Most tools fix a semantics: HoloClean/LLUNATIC use value-update (U) repairs; ConQuer/CAvSAT use subset semantics; ERACER and probabilistic cleaners blend. No system *recommends* a semantics; selection is manual and ad hoc.

## 4. Upper Bound

There is no single algorithmic upper bound — the problem is meta-level. Known constructive results:
- Given $(Q,\Sigma)$, the **CQA complexity per semantics** is decidable in the classified fragments (sjf-CQ + keys), so one can *compute* which semantics keeps CQA in $\mathsf{FO}$/$\mathsf{P}$ — an effective selection rule in those fragments.
- Utility-driven selection over a fixed candidate set is poly-time *given* an oracle estimating downstream utility per semantics (the hardness migrates into utility estimation).

## 5. Lower Bound

- Comparing semantics by their certain-answer sets is at least as hard as CQA itself, i.e., **$\mathsf{coNP}$-hard** in data complexity for the hard query/constraint classes.
- Deciding equivalence of repair families ($\mathrm{Rep}_X = \mathrm{Rep}_Y$) is undecidable for sufficiently rich constraint languages (reduction from implication problems for inclusion + functional dependencies, which is undecidable).

## 6. The Gap

This is **genuinely open** as a principled problem: there is no formal framework, complexity classification, or learning method that, given an application profile, *recommends* a repair semantics with guarantees. We have point results (per-semantics CQA complexity, pairwise incomparability) but no unifying decision theory linking semantics choice to downstream utility, nor a complete map across all four semantics × all constraint classes. Closing it requires (a) a utility/loss model for cleaning, and (b) a complete cross-semantics complexity atlas.

## 7. Current Research (as of June 2026)

- **Task-aware / downstream-aware cleaning**: choosing repairs (and implicitly semantics) to maximize ML model accuracy rather than constraint satisfaction (groups around Ilyas, Stoyanovich, Roth). *(frontier — verify)*
- **Unified repair frameworks** parameterized by semantics, letting a cost/utility model drive the choice. *(frontier — verify)*
- Probabilistic / possible-worlds semantics blending update and subset views. *(frontier — verify)*

## 8. Future Work

- A complete complexity atlas across the four semantics and major constraint classes.
- Learnable semantics-selection from labeled outcomes and application telemetry.
- Hybrid semantics (delete some, update others) with optimality guarantees.
- Benchmarks measuring downstream utility per semantics, not just constraint satisfaction.

## 9. Key References

- **[Foundational]** Wijsen. *Database Repairing Using Updates.* ACM TODS, 2005. — [DOI](https://doi.org/10.1145/1093382.1093385)
- **[Foundational]** Afrati, Kolaitis. *Repair Checking in Inconsistent Databases: Algorithms and Complexity.* ICDT, 2009. — [DOI](https://doi.org/10.1145/1514894.1514899)
- **[SOTA]** Lopatenko, Bertossi. *Complexity of Consistent Query Answering... under Cardinality-Based and Incremental Repair Semantics.* ICDT, 2007. — [DOI](https://doi.org/10.1007/11965893_13)
- **[SOTA]** Rekatsinas, Chu, Ilyas, Ré. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* VLDB, 2017. — [arXiv](https://arxiv.org/abs/1702.00820)
- **[Survey]** Bertossi. *Database Repairing and Consistent Query Answering.* Morgan & Claypool, 2011. — [DOI](https://doi.org/10.2200/S00379ED1V01Y201108DTM020)
- **[Survey]** Ilyas, Chu. *Data Cleaning.* ACM Books, 2019. — [DOI](https://doi.org/10.1145/3310205)

## 10. Worked Example

Relation $R(\text{Zip}, \text{City})$ with FD $\text{Zip}\to\text{City}$, three tuples:

| t | Zip | City |
|---|-----|------|
| $t_1$ | 10001 | NYC |
| $t_2$ | 10001 | NYC |
| $t_3$ | 10001 | Boston |

$t_3$ conflicts with the majority on the same Zip.

- **S-repair (delete only):** the minimal subset repair deletes $t_3$, giving $I' = \{t_1, t_2\}$, $\delta = 1$ tuple. We lose the Zip↔Boston row entirely.
- **U-repair (update cells):** change $t_3.\text{City} = \text{Boston} \to \text{NYC}$, a single cell edit, $\delta = 1$ cell. Tuple identity (and any keys referencing $t_3$) is preserved.
- **Cardinality repair:** maximizes $|I \cap I'|$; here it coincides with the U-repair (3 tuples kept vs. 2).

Now ask $Q = \pi_{\text{City}}(R)$. Under S-repairs the *certain answer* is $\{\text{NYC}\}$; under U-repairs (where the fresh value could also have been any consistent city) the certain answer can be empty. **Same instance, same FD — the semantics changes $Q$'s answer**, exactly the section-2 point: selection is a query-semantics decision, not just an efficiency one.

---
*Part of the [DBMS Research catalog](../../README.md).*
