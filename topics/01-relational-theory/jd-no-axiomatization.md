---
id: 01-relational-theory/jd-no-axiomatization
title: "MVD/JD Inference Without a Complete Axiomatization"
topic: 01-relational-theory
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# MVD/JD Inference Without a Complete Axiomatization

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/jd-no-axiomatization` · **Status:** open

## 1. Problem Statement

Functional dependencies (FDs) enjoy Armstrong's complete and sound finite axiomatization, and multivalued dependencies (MVDs) plus FDs are captured by a finite set of inference rules. **Join dependencies (JDs)**, the natural generalization that asserts a relation is the lossless join of several projections, lack any such complete axiomatization. The core problem:

- **(Decision)** Given a finite set $\Sigma$ of JDs (possibly mixed with FDs and MVDs) and a candidate JD $\sigma$, decide whether $\Sigma \models \sigma$ (logical implication).
- **(Axiomatization existence)** Determine whether there exists a *finite, $k$-ary, sound and complete* set of inference rules for the implication of JDs. A $k$-ary rule has at most $k$ dependencies in its premise.
- **(Counting/structural)** Characterize the structure of implication proofs and the minimal arity $k$ required if any finite axiomatization exists.

The decision variant *is* decidable (via the chase), but the question of a "nice" rule-based proof system — the analogue of Armstrong's axioms — remains open in a precise sense.

## 2. Mathematical Foundations

A JD $\bowtie[R_1,\dots,R_m]$ over attribute set $U$ holds in relation $r$ iff $r = \pi_{R_1}(r) \bowtie \cdots \bowtie \pi_{R_m}(r)$ with $\bigcup_i R_i = U$. An MVD $X \twoheadrightarrow Y$ is the binary JD $\bowtie[XY, X(U\setminus Y)]$.

Implication is tested by the **chase**: $\Sigma \models \sigma$ iff chasing the tableau of $\sigma$ with $\Sigma$ yields a tableau in which $\sigma$'s join target row appears. The chase for full dependencies (which JDs are) always terminates, giving decidability.

The negative result is **Petrov's theorem** and the line begun by Sagiv–Walecka: there is *no $k$-ary complete axiomatization* of JDs for any fixed $k$ — formally, for every $k$ there is an implication $\Sigma \models \sigma$ that no sound $k$-ary rule system can derive without first deriving "wider" intermediate JDs, so no finite bound on premise arity suffices.

$$
\Sigma \models \sigma \iff \text{chase}_\Sigma(T_\sigma) \models \sigma .
$$

## 3. State of the Art (SOTA)

- **Theory-SOTA.** The non-axiomatizability of JDs by bounded-arity rules is established (Petrov 1989; Sagiv & Walecka, *JACM* 1982). Beeri, Fagin & Howard (1977) gave the complete axiomatization for FDs+MVDs *together*, but it does not extend to general JDs.
- The implication problem for JDs alone is decidable and **EXPTIME**-related; for FD+JD it is decidable via the chase. Maier, Mendelzon & Sagiv (*TODS* 1979) established the chase as the canonical tool.
- No production "JD reasoner" exists in systems; JD reasoning surfaces in schema-design and normalization tools (5NF/PJNF checks).

## 4. Upper Bound

Implication of full dependencies (JDs, FDs, MVDs, full tgds) is decidable by the chase. The chase of a JD tableau under $\Sigma$ terminates; deciding $\Sigma \models \sigma$ is in **EXPTIME**, and for fixed dependency sets the chase produces a tableau of size exponential in $|U|$. For the restricted MVD+FD case the implication problem is in **PTIME** via the dependency-basis algorithm (Beeri 1980). Model: standard relational logical implication over finite and unrestricted relations (they coincide for full dependencies).

## 5. Lower Bound

JD implication is **coNP-hard** (and the general full-tgd implication problem is EXPTIME-complete; Chandra, Lewis & Makowsky-style tableau constructions). The sharper "lower bound" here is structural rather than complexity-theoretic: Petrov / Sagiv–Walecka prove an **impossibility** — for every finite $k$ there exist instances of $\Sigma \models \sigma$ requiring proof steps whose intermediate JDs have arity exceeding $k$, so *no* $k$-bounded sound rule set is complete. This is an information-theoretic-style impossibility on proof systems, not a hardness reduction.

## 6. The Gap

Two distinct gaps. (a) The **complexity gap**: precise complexity of JD-only implication (versus the EXPTIME-complete full-tgd case) is not tightly pinned for all natural subclasses. (b) The **axiomatization gap** is *closed in the negative for bounded-arity rules* but *open* for more liberal notions — e.g., whether some finite schema of *unbounded-arity* rule templates, or a finite set with auxiliary dependency types, yields completeness. What would close it: either a positive finite axiomatization under a relaxed rule format, or an unconditional impossibility covering all finitary proof formats.

## 7. Current Research (as of June 2026)

Renewed interest comes from the **information-theoretic reformulation** of dependency implication (Lee 1987; revived by Abo Khamis, Ngo, Suciu and collaborators), recasting MVD/JD entailment as entropy inequalities — connecting JD non-axiomatizability to the **non-finite-axiomatizability of the entropy region** (Matúš). Groups around Suciu (UW), Ngo (RelationalAI), and Kenig & Suciu have pushed entropic characterizations of dependency implication. *(frontier — verify)* Work on whether the entropic view yields a *semi-decision* procedure of practical size for JD implication is ongoing. Connections to acyclic-hypergraph and structural decomposition theory (Gottlob, Pichler) remain active.

## 8. Future Work

- Settle whether an unbounded-arity but finitely-described rule schema can be complete for JDs.
- Map the entropy-region non-axiomatizability results precisely onto JD proof theory.
- Tight complexity classification of JD-only versus FD+JD implication for acyclic and bounded-treewidth schemas.
- Practical reasoners exploiting acyclicity (where JD reasoning collapses to MVD reasoning).

## 9. Key References

- **[Foundational]** C. Beeri, R. Fagin, J. H. Howard. *A complete axiomatization for functional and multivalued dependencies in database relations.* SIGMOD, 1977. — [DBLP search](https://dblp.org/search?q=A%20complete%20axiomatization%20for%20functional%20and%20multivalued%20dependencies)
- **[Foundational]** Y. Sagiv, S. F. Walecka. *Subset dependencies and a completeness result for a subclass of embedded multivalued dependencies.* JACM, 1982. — [DBLP search](https://dblp.org/search?q=Subset%20dependencies%20completeness%20embedded%20multivalued%20Sagiv%20Walecka)
- **[Foundational]** D. Maier, A. O. Mendelzon, Y. Sagiv. *Testing implications of data dependencies.* ACM TODS, 1979. — [DOI](https://doi.org/10.1145/320107.320115)
- **[Foundational]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. (Chapters on dependencies and the chase.) — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)
- **[Survey]** F. Matúš. *Infinitely many information inequalities.* IEEE ISIT, 2007. (Entropy region non-finite-axiomatizability.) — [DOI](https://doi.org/10.1109/ISIT.2007.4557201)
- **[SOTA]** B. Kenig, D. Suciu. *Integrity constraints revisited: from exact to approximate implication.* ICDT / Logical Methods in CS, 2020–2022. — [arXiv](https://arxiv.org/abs/1812.09987)

## 10. Worked Example

A JD is *not* always equivalent to a pair of MVDs. Consider $U=\{A,B,C\}$ and the ternary JD $\sigma = \bowtie[AB, BC, AC]$ (the "triangle"). Test whether it holds on:

| A | B | C |
|---|---|---|
| 1 | 1 | 2 |
| 2 | 1 | 1 |
| 1 | 2 | 1 |

Projections: $\pi_{AB}=\{(1,1),(2,1),(1,2)\}$, $\pi_{BC}=\{(1,2),(1,1),(2,1)\}$, $\pi_{AC}=\{(1,2),(2,1),(1,1)\}$. Joining all three reconstructs the three originals **plus** the spurious tuple $(1,1,1)$: row 1 gives $A{=}1,B{=}1$; row 2 gives $B{=}1,C{=}1$; row 3 gives $A{=}1,C{=}1$ — all three pairwise projections contain the matching pairs, so $(1,1,1)\in \pi_{AB}\bowtie\pi_{BC}\bowtie\pi_{AC}$. Since the join strictly exceeds $r$, the JD $\sigma$ **fails** here.

The chase test mirrors this: chasing $\sigma$'s tableau with no constraints leaves the spurious row, so $\emptyset \not\models \sigma$. Crucially, this triangle JD is provably not derivable from any fixed-arity (e.g., binary MVD-style) rule set — the phenomenon behind Petrov's non-axiomatizability result.

---
*Part of the [DBMS Research catalog](../../README.md).*
