# Definability and Loss in LAV Rewriting

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/lav-rewriting-definability` · **Status:** partially-solved

## 1. Problem Statement

In **Local-As-View (LAV)** integration, each source is described as a view $V_i$ defined by a query over a global/mediated schema $\mathbf{G}$. A user poses a query $Q$ over $\mathbf{G}$; the system can only read source extents, i.e. the materialized views. Two intertwined problems:

- **Definability / losslessness (decision):** Is $Q$ **exactly answerable** from the views — does there exist a rewriting $R$ over $\{V_1,\dots,V_m\}$ such that for *every* database $D$, $R(V_1(D),\dots,V_m(D)) = Q(D)$? Equivalently, is $Q$ determined by the views (the views are *lossless* for $Q$)?
- **Synthesis (function/optimization):** Compute the **maximally-contained rewriting** (MCR) — the best query over the views whose certain answers are exactly the certain answers of $Q$ under the open-world LAV semantics — and decide when it coincides with an **exact** rewriting.

"Solving" means deciding losslessness and outputting an MCR (and, when lossless, an exact rewriting) for the relevant query/view language, characterizing exactly when the rewriting loses no answers.

## 2. Mathematical Foundations

Views are CQs (or UCQs/datalog) $V_i(\bar{x}) \leftarrow \phi_i$. Under the **open-world assumption**, a source extent is a *subset* of $V_i(D)$, so query answering is **certain answers**: $\mathsf{certain}(Q, \mathcal{V}) = \bigcap \{ Q(D) \mid D \text{ consistent with the extents} \}$. **Determinacy**: $\mathcal{V}$ *determines* $Q$ iff for all $D_1, D_2$ with $\mathcal{V}(D_1)=\mathcal{V}(D_2)$ we have $Q(D_1)=Q(D_2)$; an exact rewriting exists iff $\mathcal{V}$ determines $Q$ *and* the rewriting is expressible in the target language (the **interpolation/Beth-definability** angle). The classic tools are **CQ containment** (NP, via homomorphisms), the **bucket / inverse-rules / MiniCon** algorithms, and for the certain-answer side the **chase** with inverse rules producing a datalog rewriting. The subtle phenomenon is **"losslessness $\neq$ first-order rewritability"**: $\mathcal{V}$ may determine $Q$ while no *FO* (or even CQ) exact rewriting exists — a failure of **Beth definability** for the fragment.

## 3. State of the Art (SOTA)

**Theory SOTA.** Nash, Segoufin, Vianu (PODS 2007 / TODS 2010) settled the core: for CQ views and CQ queries, **determinacy does not imply CQ-rewritability**, and FO-rewritability under determinacy fails in general (interpolation breaks). Afrati and collaborators charted exact-rewriting existence for restricted classes. **Systems SOTA.** MiniCon (Pottinger–Halevy, VLDB 2000) and the inverse-rules / Information Manifold lineage (Levy–Rajaraman–Ordille, VLDB 1996; Duschka–Genesereth) remain the practical MCR engines; modern descendants live in federated-query optimizers and ontology-based data access (OBDA) systems.

## 4. Upper Bound

Computing the **MCR** for CQ query + CQ views is decidable; the maximally-contained UCQ rewriting has size **exponential** in the query/view size and is found by MiniCon/bucket in time exponential in the number of subgoals, polynomial in the number of views per subgoal. The **inverse-rules** method yields a datalog MCR of polynomial size and **PTIME data complexity** for certain answers. Deciding *existence of an exact CQ rewriting* given the views is decidable (reduces to a containment battery). Model: classical complexity, combined vs. data complexity.

## 5. Lower Bound

CQ **rewriting existence** and **determinacy** are at least **NP-hard** (CQ-containment is NP-complete; determinacy for CQ/CQ is **decidable** but the precise complexity of FO-rewritability-under-determinacy is delicate). Nash–Segoufin–Vianu prove **undecidability** of determinacy once the language is enriched (e.g., for general FO views/queries) and exhibit separating examples showing no relational-algebra rewriting exists despite determinacy — an **expressiveness lower bound** independent of complexity. Model: classical undecidability (FO determinacy) and NP-hardness (CQ rewriting).

## 6. The Gap

The **CQ/CQ determinacy decidability** boundary and its exact complexity, and the precise frontier where *determinacy implies rewritability in some usable language*, remain partly open. We know rewritability can fail under determinacy but lack a clean syntactic characterization of *which* (query, view) pairs are lossless-and-rewritable. For richer languages (UCQ with comparisons, datalog, GLAV mappings) determinacy is undecidable, so the open question is identifying maximal decidable sub-fragments with effective exact-rewriting synthesis. Closing it needs new interpolation results for these fragments.

## 7. Current Research (as of June 2026)

Directions: (1) determinacy and rewriting for **datalog/recursive** and **path** queries (graph data), with ten Cate, Segoufin, Figueira and others; (2) **OBDA** perspective — losslessness of mappings + ontology for CQ answering, tying to the DL-Lite FO-rewritability frontier (Calvanese, De Giacomo, Lenzerini lineage); (3) cost-based MCR selection and *bounded-loss* rewritings that quantify how much $Q$ is lost when no exact rewriting exists; (4) learned/LLM rewriters checked against certain-answer semantics *(frontier — verify)*. Quantitative "definability defect" measures are an emerging frontier.

## 8. Future Work

Decidability and tight complexity of CQ/CQ determinacy; syntactic characterizations of lossless view sets; approximate/bounded-loss rewritings with provable answer-recall; determinacy for aggregate and graph-path queries; and integration with closed/partially-closed world assumptions (the source-completeness annotations that flip OWA to mixed semantics) where exactness can be recovered.

## 9. Key References

- **[Foundational]** Levy, Rajaraman, Ordille. *Querying Heterogeneous Information Sources Using Source Descriptions.* VLDB 1996.
- **[Foundational]** Pottinger, Halevy. *MiniCon: A Scalable Algorithm for Answering Queries Using Views.* VLDB 2000 / VLDBJ 2001.
- **[SOTA]** Nash, Segoufin, Vianu. *Views and Queries: Determinacy and Rewriting.* PODS 2007 / TODS 2010.
- **[Survey]** Halevy. *Answering Queries Using Views: A Survey.* VLDB Journal, 2001.
- **[Foundational]** Abiteboul, Duschka. *Complexity of Answering Queries Using Materialized Views.* PODS 1998.
- **[Survey]** Calvanese, De Giacomo, Lembo, Lenzerini, Rosati. *Ontology-Based Data Access.* (DL-Lite / OBDA), 2007–2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
