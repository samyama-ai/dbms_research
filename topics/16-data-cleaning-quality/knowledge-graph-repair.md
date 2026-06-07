---
id: 16-data-cleaning-quality/knowledge-graph-repair
title: "Repairing Knowledge Graphs and Linked Data"
topic: 16-data-cleaning-quality
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Repairing Knowledge Graphs and Linked Data

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/knowledge-graph-repair` · **Status:** empirically-open

## 1. Problem Statement

A knowledge graph (KG) is a set of triples $(s, p, o)$ over entities and relations, often governed by a flexible/partial schema (RDFS/OWL ontology, SHACL/ShEx shapes, or none). KGs like Wikidata, DBpedia, and enterprise graphs contain wrong values, wrong/missing types, broken links, duplicate entities, and constraint violations. The problem: **detect and repair errors in large, heterogeneous, schema-flexible KGs** while respecting ontological semantics and the **open-world assumption** (OWA) — absence of a triple is *not* falsity.

Variants:
- **Decision:** Is the KG consistent w.r.t. ontology $\mathcal{O}$ and shape constraints $\mathcal{C}$?
- **Repair/optimization:** Find a minimal-change (subset- or cardinality-minimal, or weighted) set of triple additions/deletions/edits restoring consistency.
- **Counting/uncertainty:** Rank candidate repairs by likelihood, or compute certain answers over the repair space (KG analogue of CQA).

OWA + value diversity + multilingual labels + scale ($10^9$ triples) make this materially harder than relational cleaning.

## 2. Mathematical Foundations

- **Description Logics (DL):** ontology $\mathcal{O}$ in $\mathcal{EL}$, DL-Lite, or $\mathcal{SHIQ}$; consistency checking ranges from PTIME (DL-Lite, $\mathcal{EL}$) to ExpTime-complete ($\mathcal{SHIQ}$).
- **Ontology repair / belief revision:** an *ABox repair* is a maximal subset of assertions consistent with the TBox; this is the AGM/Hansson **kernel contraction** / **remainder set** framework — repairs = maximal consistent subsets, justifications = minimal inconsistent subsets (MinAs / MUSes).
- **Validation constraints:** SHACL shapes are essentially a constraint language; SHACL validation under recursion is intractable / undecidable in fragments (Corman–Reutter–Savković).
- **Embedding-based plausibility:** KG embeddings (TransE, ComplEx, RotatE) score triple plausibility $f(s,p,o)$; repairs leverage low-scoring triples as error candidates and high-scoring absent triples as completions, blending OWA with statistical signal.
- **Rule mining:** AMIE-style Horn rules with confidence under the **partial completeness assumption (PCA)** give logical error signals.

## 3. State of the Art (SOTA)

Empirically driven; no dominant principled solver.
- **Embedding + outlier detection** — KGTtm, CAGED, and contrastive methods flag implausible triples; numeric-error detectors for literals.
- **Wikidata in practice** — constraint reports, ORES/edit-quality models, and bot-driven fixes; SHACL/ShEx EntitySchemas catch violations.
- **Rule-based** — AMIE+/AnyBURL mine rules to predict and contradict triples; used for completion and error detection.
- **Holistic/probabilistic** — extensions of HoloClean-style inference and *KATARA* (Chu et al., SIGMOD 2015) use crowdsourcing + KGs to validate relational data; the reverse (cleaning the KG itself) is less mature.
- **LLM-based fact verification** — using LLMs to check/repair triples against text and the graph *(frontier — verify)*.

## 4. Upper Bound

- Consistency checking and **DL-Lite ABox repair existence** are in **PTIME** (data complexity); $\mathcal{EL}$ classification is PTIME.
- For DL-Lite, computing all *justifications* of an inconsistency and the **IAR/ICAR consistent-answer** semantics is tractable (in $\mathsf{AC}^0$/PTIME data complexity, Lembo–Lenzerini–Rosati et al.).
- Embedding-based detection is **linear** in #triples per scoring pass; rule application is polynomial per rule but exponential in rule body length in the worst case.

## 5. Lower Bound

- Consistency for expressive DLs ($\mathcal{SHIQ}$/OWL-DL) is **ExpTime/NExpTime-complete** — repair is at least as hard.
- Computing a **cardinality-minimal repair** is **NP-hard** even for DL-Lite (hitting-set over minimal inconsistent subsets / set-cover).
- **Certain answers over inconsistent DL-Lite KGs under brave/AR semantics** are **coNP-hard** (AR-semantics, Lembo et al.) — the KG analogue of CQA hardness.
- **Information-theoretic / OWA impossibility:** under the open-world assumption, absence of evidence cannot certify error; no algorithm can distinguish "missing" from "false" without external ground truth — a fundamental identifiability barrier.

## 6. The Gap

**Empirically open.** The complexity *landscape* of repair is well charted for clean DL fragments, but real KGs are messy, schema-partial, and OWA-bound, so theory rarely binds practice. There is no benchmark-validated method that jointly (i) uses ontology semantics, (ii) exploits statistical/embedding plausibility, and (iii) scales to billion-triple graphs with calibrated precision. The gap is less "tight bound vs. algorithm" and more "no agreed problem formalization + no realistic benchmark + no method dominant across error types." Closing it needs a unified logical-statistical repair semantics and a deployment-predictive benchmark (see Benchmarking page).

## 7. Current Research (as of June 2026)

- Neuro-symbolic repair: combine embedding plausibility with DL/SHACL constraints and rule confidence in one objective *(frontier — verify)*.
- LLM-assisted triple verification grounded in retrieved evidence, with abstention/calibration to respect OWA *(frontier — verify)*.
- Scalable SHACL validation and incremental repair over evolving Wikidata.
- Entity-resolution-aware repair: deduplication and value repair jointly, since duplicate entities create spurious inconsistencies (Stuckenschmidt, Paulheim, Bizer, Suchanek, Razniewski groups) *(frontier — verify)*.

## 8. Future Work

- A principled probabilistic repair semantics under OWA with identifiability guarantees.
- Joint inference over schema (TBox), data (ABox), and entity identity.
- Human-in-the-loop repair budgets with active querying (links to Active Constraint Acquisition).
- Standard, error-injected KG benchmarks with provenance and difficulty calibration.

## 9. Key References

- **[Foundational]** Lembo, Lenzerini, Rosati, Ruzzi, Savo. *Inconsistency-Tolerant Semantics for Description Logics (IAR/ICAR/AR).* RR, 2010. — [DOI](https://doi.org/10.1007/978-3-642-15918-3_9)
- **[Foundational]** Calvanese et al. *Tractable Reasoning and Efficient Query Answering in Description Logics: The DL-Lite Family.* JAR, 2007. — [DOI](https://doi.org/10.1007/s10817-007-9078-x)
- **[SOTA]** Galárraga, Teflioudi, Hose, Suchanek. *AMIE: Association Rule Mining under Incomplete Evidence in Ontological KBs.* WWW, 2013 (AMIE+ extension 2015). — [DOI](https://doi.org/10.1145/2488388.2488425)
- **[SOTA]** Chu et al. *KATARA: A Data Cleaning System Powered by Knowledge Bases and Crowdsourcing.* SIGMOD, 2015. — [DOI](https://doi.org/10.1145/2723372.2749431)
- **[SOTA]** Paulheim. *Knowledge Graph Refinement: A Survey of Approaches and Evaluation Methods.* Semantic Web Journal, 2017. — [DOI](https://doi.org/10.3233/SW-160218)
- **[Survey]** Corman, Reutter, Savković. *Semantics and Validation of Recursive SHACL.* ISWC, 2018. — [DOI](https://doi.org/10.1007/978-3-030-00671-6_19)

## 10. Worked Example

Take a tiny KG with a DL-Lite TBox stating $\mathsf{Person}\sqsubseteq \neg\mathsf{City}$ (a person is not a city) and the functional role $\mathsf{bornIn}$ has range $\mathsf{City}$. The ABox has three assertions:

$$a_1:\ \mathsf{bornIn}(\text{Marie}, \text{Paris}),\quad a_2:\ \mathsf{Person}(\text{Paris}),\quad a_3:\ \mathsf{City}(\text{Paris}).$$

Here $\{a_2, a_3\}$ is a **minimal inconsistent subset** (Paris is asserted both Person and City, violating disjointness). The **remainder sets** (maximal consistent ABoxes) are $\{a_1,a_2\}$ and $\{a_1,a_3\}$; each drops exactly one assertion.

**Cardinality-minimal repair** removes one assertion — but which? Logic alone cannot decide. An embedding score $f(\text{Paris},\mathsf{type},\mathsf{City})\gg f(\text{Paris},\mathsf{type},\mathsf{Person})$ favors deleting $a_2$, yielding repair $\{a_1,a_3\}$.

**OWA caveat:** under the open-world assumption, the *absence* of $\mathsf{Person}(\text{Marie})$ is not evidence that Marie is not a person — so no algorithm may "repair" by adding $\neg\mathsf{Person}(\text{Marie})$. Repair acts only on the inconsistency $\{a_2,a_3\}$, illustrating the identifiability barrier: missing $\ne$ false.

---
*Part of the [DBMS Research catalog](../../README.md).*
