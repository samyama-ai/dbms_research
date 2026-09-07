---
id: 01-relational-theory/open-world-certain-answers
title: "Open-World Certain Answers Complexity"
topic: 01-relational-theory
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Open-World Certain Answers Complexity

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/open-world-certain-answers` · **Status:** partially-solved

## 1. Problem Statement

Under the **open-world assumption (OWA)**, a database instance is treated as a *partial* description of the world: missing facts are unknown, not false. An *incomplete database* is represented by a set of possible worlds — most commonly via a **naïve table** (relations with marked nulls/variables) plus a set $\Sigma$ of constraints. The semantics of a query $Q$ is its set of **certain answers**:

$$\mathrm{cert}(Q, T, \Sigma) = \bigcap \{\, Q(I) \mid I \models \Sigma,\ I \in \mathrm{rep}(T)\,\},$$

where $\mathrm{rep}(T)$ is the set of completions of table $T$. The task is to determine the **complexity of computing/deciding membership in $\mathrm{cert}$** as a function of:

- the **query class** (CQ, UCQ, CQ with inequalities/negation, FO, Datalog),
- the **table representation** (Codd, naïve, conditional/c-tables), and
- the **constraint class** $\Sigma$ (none, FDs, TGDs/EGDs, ontologies).

We distinguish **data complexity** (query and constraints fixed, table varies), **combined complexity**, and **query complexity**. The goal is a full map of $(\text{query class}) \times (\text{constraint class}) \times (\text{representation})$ onto complexity classes, plus tractability dichotomies.

## 2. Mathematical Foundations

Certain answering is the model-theoretic intersection over an (infinite) family of completions, computable via **universal models**. For CQs/UCQs without constraints, certain answers over a naïve table equal the **naïve evaluation** (Imieliński–Lipski 1984): treat nulls as constants, then keep null-free tuples — a polynomial-time procedure proving CQ data complexity is in **PTIME**. With existential constraints, the canonical universal model is the **chase**; certain answering over OWA reduces to query answering on the chase:

$$\mathrm{cert}(Q,T,\Sigma) = Q(\mathrm{chase}(T,\Sigma))\big|_{\text{null-free}}.$$

This connects OWA certain answers to **homomorphism existence** and to **ontology-mediated query answering (OMQA)**. Negation and inequalities break monotonicity, pushing the problem up the polynomial hierarchy (coNP). The framework rests on c-tables being a *strong representation system* for relational algebra (Imieliński–Lipski).

## 3. State of the Art (SOTA)

- **Imieliński–Lipski (JACM 1984)**: c-tables are a strong representation system; naïve tables suffice for positive relational algebra. Foundational and essentially tight for the no-constraint case.
- **Abiteboul–Kanellakis–Grahne (1991)** and the **AHV** textbook fix the polynomial-hierarchy landscape for FO queries.
- **OMQA / Datalog$^\pm$** line (Calì–Gottlob–Pieris; Bienvenu–Ortiz): combined and data complexity of certain CQ answering under guarded, sticky, frontier-guarded, and DL-Lite/$\mathcal{EL}$ constraints — yielding **first-order rewritability** (AC$^0$) for DL-Lite and **PTIME-completeness** for $\mathcal{EL}$/guarded fragments.
- **Console, Libkin, Guagliardo**: modern OWA semantics and SQL nulls; partial but rigorous accounts of three-valued certain answers.

## 4. Upper Bound

- **CQ/UCQ, no constraints, naïve tables**: data complexity **PTIME** (naïve evaluation); combined complexity **NP-complete** (homomorphism).
- **CQ under DL-Lite / linear TGDs**: data complexity in **AC$^0$** via FO-rewriting; combined in **NP/PSpace**.
- **CQ under guarded TGDs**: data complexity **PTIME**, combined **2ExpTime**.
- **FO queries, c-tables**: certain answering in **coNP** (data). These hold in the standard finite-instance model with the named/marked-null semantics.

## 5. Lower Bound

- For **FO queries with negation/inequalities** over naïve or Codd tables, certain answering is **coNP-hard** in data complexity (Abiteboul–Kanellakis–Grahne) — already for simple queries with $\neq$.
- Combined complexity of CQ certain answering matches CQ evaluation: **NP-hard** (homomorphism, Chandra–Merlin 1977).
- Under expressive existential rules, combined complexity is **2ExpTime-hard** (guarded) and **undecidable** for unrestricted TGDs (TGD entailment). These are classical many-one hardness results, not conditional.

## 6. The Gap

The no-constraint and DL-Lite corners are **closed and tight**. The genuinely open territory: (i) **dichotomy theorems** separating PTIME from coNP-hard certain answering for queries with *limited* negation/inequality over OWA tables, analogous to the CQA primary-key dichotomy; (ii) **combined-complexity tightness** for several intermediate existential-rule fragments; and (iii) faithful complexity of certain answers under **realistic SQL three-valued nulls + bag semantics**, where current theory and engine behavior diverge. Hence *partially-solved*: large regions are mapped, several boundaries remain open.

## 7. Current Research (as of June 2026)

- **Libkin, Console, Guagliardo, Toussaint**: certain-answer semantics that match SQL nulls and *approximation* algorithms returning sound-but-incomplete answers in PTIME.
- **Bienvenu, Ortiz, Šimkus, Lutz**: tightening combined/data complexity and FO-rewritability frontiers for OMQA and *bounded* existential rules.
- *(frontier — verify)* Work coupling OWA certain answers with **probabilistic** and **bag** semantics, and fine-grained (within-PTIME) classification of naïve evaluation.

## 8. Future Work

- A definitive **tractability dichotomy** for OWA certain answers across query+constraint classes.
- Practical, **sound approximation** operators integrated into SQL engines (replacing today's unsound null handling).
- Certain answers under **aggregation** and under **bag** semantics.
- Closing remaining combined-complexity gaps for sticky/frontier-guarded rules.

## 9. Key References

- **[Foundational]** Imieliński, T., Lipski, W. *Incomplete Information in Relational Databases.* JACM, 1984. — [DOI](https://doi.org/10.1145/1634.1886)
- **[Foundational]** Abiteboul, S., Hull, R., Vianu, V. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)
- **[Foundational]** Abiteboul, S., Kanellakis, P., Grahne, G. *On the Representation and Querying of Sets of Possible Worlds.* Theoretical Computer Science, 1991. — [DBLP search](https://dblp.org/search?q=On%20the%20Representation%20and%20Querying%20of%20Sets%20of%20Possible%20Worlds)
- **[SOTA]** Calì, A., Gottlob, G., Pieris, A. *Towards More Expressive Ontology Languages (Datalog±).* Artificial Intelligence, 2012. — [DOI](https://doi.org/10.1016/j.artint.2012.08.002)
- **[SOTA]** Libkin, L. *SQL's Three-Valued Logic and Certain Answers.* ACM TODS, 2016. — [DOI](https://doi.org/10.1145/2877206)
- **[Survey]** Bienvenu, M., Ortiz, M. *Ontology-Mediated Query Answering with Data-Tractable Description Logics.* Reasoning Web, 2015. — [DOI](https://doi.org/10.1007/978-3-319-21768-0_9)

## 10. Worked Example

Naïve table $T$ over $\text{Emp}(\text{name},\text{dept})$ with a marked null $\bot$ (unknown department):

| name  | dept  |
|-------|-------|
| Ann   | Sales |
| Bob   | $\bot$ |

**Query** $Q_1$: "names of employees" $=\pi_{\text{name}}(\text{Emp})$. Naïve evaluation treats $\bot$ as a value, projects, and keeps tuples — both $\bot$-free after projecting to name — giving $\mathrm{cert}(Q_1)=\{\text{Ann},\text{Bob}\}$. Correct: in *every* completion both rows exist.

**Query** $Q_2$: "names in Sales" $=\pi_{\text{name}}(\sigma_{\text{dept}=\text{Sales}}\text{Emp})$. Naïve evaluation: Ann matches; Bob's row has $\bot\neq$ the constant Sales under the keep-only-$\bot$-free rule, so it is dropped. $\mathrm{cert}(Q_2)=\{\text{Ann}\}$ — and indeed Bob is *not* certain, since a completion may set Bob's dept to HR.

**Why negation breaks this:** for $Q_3$="names not in Sales", Bob is certain only if $\bot\neq\text{Sales}$ in all completions — false. Deciding such certain answers with $\neq$/negation is $\text{coNP}$-hard in data complexity, versus PTIME naïve evaluation for the positive $Q_1,Q_2$.

---
*Part of the [DBMS Research catalog](../../README.md).*
