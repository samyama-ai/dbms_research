---
id: 15-data-integration/probabilistic-schema-mappings
title: "Probabilistic Schema Mappings Semantics"
topic: 15-data-integration
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Probabilistic Schema Mappings Semantics

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/probabilistic-schema-mappings` · **Status:** open

## 1. Problem Statement

When a mapping between source $\mathbf{S}$ and target $\mathbf{T}$ is **discovered automatically** (by schema matching, learning, or LLMs), the mapping itself is *uncertain*: instead of one set of st-tgds we have a distribution over candidate mappings. A **probabilistic schema mapping (p-mapping)** is a finite set $\{(\mathcal{M}_1, p_1), \dots, (\mathcal{M}_k, p_k)\}$ with $\sum_i p_i = 1$ (or a more compact factorized representation). Problems:

- **Semantics (definitional):** What is the meaning of "the answer to query $Q$ over the target" when the mapping is probabilistic? Two leading semantics — **by-table** (one $\mathcal{M}_i$ governs the whole instance) and **by-tuple** (each source tuple may be governed by a different $\mathcal{M}_i$) — and their interaction with **certain answers**.
- **Evaluation (computation/counting):** Given $Q$ and a source $I$, compute, for each candidate answer $\bar{a}$, its **probability** $\Pr[\bar{a} \in Q]$ (probable answers) and/or the set of **certain answers** that hold with probability 1. This is a *probabilistic query-answering* problem combining incompleteness (open-world target) with mapping uncertainty.
- **Tractability:** Identify mapping/query classes where probable-answer computation is in PTIME data complexity rather than #P-hard.

"Solving" means a sound semantics plus an algorithm with characterized (ideally PTIME data) complexity for probable and certain answers, with a dichotomy separating easy from hard cases.

## 2. Mathematical Foundations

The target under one st-tgd mapping is an **incomplete database** (set of solutions); query answering is **certain answers**, computed via the **chase** + naive evaluation. Layering a distribution over mappings yields a two-level uncertainty: a **probabilistic incomplete database**. The by-tuple semantics induces a sum over exponentially many *mapping-assignment worlds*: $\Pr[\bar a \in Q] = \sum_{w} \Pr[w]\,\mathbf{1}[\bar a \in \mathsf{certain}(Q, w)]$. This connects to **probabilistic databases (PDBs)**: the **dichotomy theorem** of Dalvi–Suciu states that for tuple-independent PDBs, evaluating a UCQ is either PTIME (via the *safe plan* / read-once lineage) or **#P-hard**, governed by whether the query is **hierarchical**. The mapping-uncertainty layer adds correlation structure (a *block-independent-disjoint*-like model over candidate mappings), so the relevant tool is **lineage/provenance over semirings** $(\mathbb{N}[X], \text{or } \mathbb{B})$ together with the chase, and approximate counting via **FPRAS** / Monte-Carlo when exact is #P-hard.

## 3. State of the Art (SOTA)

**Theory SOTA.** Dong, Halevy, Yu (VLDB 2007 / VLDBJ 2009) introduced p-mappings with by-table and by-tuple semantics and showed by-table query answering is PTIME data complexity while **by-tuple is #P-hard** in general but PTIME for important subclasses. Subsequent work links p-mappings to PDB provenance and to **probabilistic data exchange** (Fagin, Kimelfeld, Kolaitis, PODS 2010 / JACM 2011), which gives a clean possible-worlds semantics for "the chase under a distribution." **Systems SOTA.** No production system computes by-tuple probable answers at scale; approximate, sampling-based pipelines and confidence propagation in matchers (and modern LLM-mapping confidence scores) are the practical state, without formal guarantees *(frontier — verify)*.

## 4. Upper Bound

**By-table** semantics: probable-answer computation is **PTIME in data complexity** (run the query once per candidate mapping, weight by $p_i$) — $O(k \cdot |Q\text{-eval}|)$. **By-tuple**: a UCQ whose lineage over the mapping-choice variables is **safe/hierarchical** admits a PTIME safe plan (Dalvi–Suciu dichotomy transported to the mapping layer); otherwise an **FPRAS** gives a $(1\pm\epsilon)$ estimate via Karp–Luby-style sampling in randomized polynomial time. Probabilistic data exchange (Fagin et al.) gives a possible-worlds semantics where certain answers remain computable via the chase. Model: data complexity, RAM + randomization.

## 5. Lower Bound

By-tuple probable-answer evaluation is **#P-hard** even for simple conjunctive queries (Dong–Halevy–Yu), inheriting hardness from #P-hardness of PDB query evaluation for **non-hierarchical** CQs (Dalvi–Suciu) — the canonical hard instance being the "non-hierarchical" query $R(x), S(x,y), T(y)$. For probabilistic data exchange, computing the probability of an answer is likewise **#P-hard** for unrestricted st-tgds. These are #P-hardness lower bounds in the *counting* model; no SETH-style fine-grained refinement is established. Model: #P-completeness (counting complexity).

## 6. The Gap

A complete **dichotomy** (PTIME vs #P-hard) for by-tuple probable answers across (mapping language × query language) is **not known** — Dalvi–Suciu solves the PDB layer, but the *composition with the chase* over existential rules (target nulls, correlations from shared candidate mappings) is open. There is also no agreed-upon, fully compositional semantics that simultaneously handles by-tuple uncertainty, open-world target incompleteness, and target constraints. The gap is genuinely open on both the semantic-foundations axis and the fine-grained-complexity axis; closing it needs a chase-aware lifting of the safe-plan dichotomy.

## 7. Current Research (as of June 2026)

Directions: (1) provenance-semiring treatments unifying p-mappings, PDBs, and data exchange (Green–Tannen lineage; Kimelfeld, Kolaitis); (2) **probabilistic data exchange** complexity census and approximate certain-answer computation; (3) calibrating and *propagating* the confidence scores emitted by learned/LLM matchers into formal p-mapping distributions, then querying them — largely empirical and unverified *(frontier — verify)*; (4) connections to **probabilistic OBDA** and to consistency under uncertain constraints. Approximate query processing with anytime probability bounds is an active practical thread.

## 8. Future Work

A full PTIME/#P-hard dichotomy for by-tuple answering under existential-rule mappings; compact, tractable representations of correlated mapping distributions; principled estimation of $p_i$ from matcher/LLM evidence with calibration guarantees; combined treatment of mapping uncertainty *and* data uncertainty; and scalable FPRAS/lifted-inference engines that surface calibrated probabilities to users.

## 9. Key References

- **[Foundational]** Dong, Halevy, Yu. *Data Integration with Uncertainty.* VLDB 2007 / VLDB Journal 2009. — [DOI](https://doi.org/10.1007/s00778-008-0119-9)
- **[Foundational]** Fagin, Kimelfeld, Kolaitis. *Probabilistic Data Exchange.* ICDT 2010 / JACM 2011. — [DOI](https://doi.org/10.1145/1989727.1989729)
- **[Foundational]** Dalvi, Suciu. *Efficient Query Evaluation on Probabilistic Databases.* VLDB 2004 / VLDBJ 2007; *The Dichotomy of Conjunctive Queries on Probabilistic Structures.* PODS 2007. — [DOI](https://doi.org/10.1007/s00778-006-0004-3)
- **[Survey]** Suciu, Olteanu, Ré, Koch. *Probabilistic Databases.* Morgan & Claypool, 2011. — [DOI](https://doi.org/10.2200/S00362ED1V01Y201105DTM016)
- **[Foundational]** Green, Karvounarakis, Tannen. *Provenance Semirings.* PODS 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)

## 10. Worked Example

A discovered attribute mapping is uncertain: the source column `addr` maps to target `home` with prob $0.6$, else to `work` with prob $0.4$. So $\mathcal{M}_1$ (prob $0.6$) and $\mathcal{M}_2$ (prob $0.4$). Source has two tuples, $t_1, t_2$, each carrying an address.

**By-table.** One mapping governs everything: $\Pr[\text{both addresses are }home] = \Pr[\mathcal{M}_1] = 0.6$. Linear in $k=2$ candidates.

**By-tuple.** Each tuple independently picks $\mathcal{M}_1$ or $\mathcal{M}_2$. Query $Q$: "is there a `home` address?" The four assignment-worlds are $(\mathcal{M}_i \text{ for } t_1, \mathcal{M}_j \text{ for } t_2)$:
$$\Pr[Q] = 1 - \Pr[\text{neither is }home] = 1 - (0.4)(0.4) = 0.84.$$
With $n$ tuples there are $2^n$ worlds — the sum is exponential in general. For this hierarchical (single-table) query a safe plan computes $0.84$ in PTIME; but a non-hierarchical pattern like $R(x),S(x,y),T(y)$ over mapping-choice variables makes by-tuple evaluation **#P-hard** (Dalvi–Suciu), exactly the dichotomy boundary of Section 6.

---
*Part of the [DBMS Research catalog](../../README.md).*
