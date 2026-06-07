---
id: 34-schema-design-normalization/schema-inference-semistructured
title: "Schema Inference for Semi-Structured Data"
topic: 34-schema-design-normalization
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Schema Inference for Semi-Structured Data

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/schema-inference-semistructured` · **Status:** partially-solved

## 1. Problem Statement
Given a large, heterogeneous collection of semi-structured records $D = \{d_1,\dots,d_n\}$ (JSON documents, event logs, nested objects with optional/variant fields), **infer a compact and useful schema** $\mathcal{S}$ that describes the collection — a relational schema (with FDs/keys, possibly normalized), a document/JSON Schema, or a nested type.

- **Inference (optimization) variant:** Find the schema minimizing a tradeoff between **fidelity** (covers/validates the data) and **conciseness** (description length) — typically an **MDL** objective.
- **Decision variant:** Is there a schema of size $\le k$ in a target class consistent with $D$ (and, for some classes, rejecting some negatives)?
- **Class/identification variant:** From which subclass of schema languages is $\mathcal{S}$ *learnable* from positive examples alone?
- **Relational mapping variant:** Produce a normalized relational decomposition (tables + FKs) that shreds the nested data with minimal redundancy.

The tension: a schema that merely unions every observed shape is faithful but useless; an over-general schema is concise but uninformative. The goal is the **compact, generalizing** schema.

## 2. Mathematical Foundations
Schema inference is **grammatical inference / learning from positive data**. By **Gold's theorem**, no superfinite language class (including all regular languages) is *identifiable in the limit from positive examples only* — so unrestricted schema learning is impossible; tractable results require restricted target classes (e.g., **k-occurrence / single-occurrence regular expressions, SOREs/CHAREs**) for which Bex–Gelade–Neven–Vansummeren give learnable algorithms underlying XSD/DTD inference.

The fidelity–conciseness tradeoff is formalized via the **Minimum Description Length** principle: choose $\mathcal{S}$ minimizing $L(\mathcal{S}) + L(D\mid\mathcal{S})$ (model bits + data-given-model bits), an information-theoretic Occam objective. For relational shredding, redundancy is bounded by **functional-dependency** discovery (TANE/FDEP) and normalization theory; key/FD discovery has a search lattice with anti-monotone pruning. Document-schema generalization uses **type lattices** with subtyping joins; merging variant shapes is a least-upper-bound in a type lattice, and "compactness" can be a **VC-dimension / sample-complexity** statement: how many documents are needed before the inferred schema PAC-generalizes to the true one.

## 3. State of the Art (SOTA)
**Systems-SOTA.** **Spark/Hadoop `inferSchema`** and document-store tools do union-of-observed-types inference at scale (cheap, verbose). **Baazizi et al.** (EDBT 2017; *Counting Types for Massive JSON Datasets*) infer **succinct, parametric JSON schemas** with type fusion/equivalence and optional-field reduction — a leading principled approach. **MongoDB Compass schema analyzer**, **json-schema-inference** libraries, and **Frozza et al.** (JSON-Schema extraction) are practical. For relational shredding of XML/JSON, **Shanmugasundaram et al.** (inlining) and modern **JSON-to-relational** flatteners apply. FD/key discovery via **TANE** (Huhtala et al.), **HyFD** (Papenbrock–Naumann, SIGMOD 2016) supplies the normalization layer.

**Theory-SOTA.** Learnability of **SOREs/CHAREs** (Bex, Gelade, Neven, Vansummeren, VLDB 2006/TODS 2010) is the canonical decidable, polynomial-time inference result. MDL-based schema selection frames the objective formally.

## 4. Upper Bound
For the learnable regex subclasses (**single-occurrence / chain regular expressions**), schema inference from a sample runs in **polynomial time** and is **provably correct in the limit** for that class. JSON type fusion (Baazizi et al.) is **near-linear** in collection size with a lattice-join per record. FD/UCC discovery (HyFD) is worst-case exponential in attributes but, with hybrid sampling + lattice pruning, runs in **practically polynomial** time on real data. MDL schema selection is typically optimized **greedily/heuristically** (no global optimum guarantee but bounded local objective).

## 5. Lower Bound
By **Gold (1967)**, identification in the limit from positive examples is **impossible** for any superfinite class — so general, exact schema inference is information-theoretically unachievable; this is the foundational lower bound forcing restricted classes. Finding the **minimum-size** consistent regular expression/automaton is **NP-hard** (Gold's minimum-DFA-consistency hardness; Angluin), so exact MDL-optimal schema selection is **NP-hard**. FD/key discovery output can be **exponential** in attribute count (no input-polynomial enumeration in general). Thus optimality is intractable and exactness is impossible beyond restricted classes.

## 6. The Gap
The gap is between **practically-effective heuristics** (union/fusion + greedy MDL, used in systems) and **provably optimal/complete** inference (impossible in general, NP-hard for minimum size). It is *partially solved*: for the restricted SORE/CHARE classes the gap is closed (polynomial, correct-in-limit); for **rich, real JSON** with arrays, recursion, and semantic types there is no optimal tractable inference, and the open question is which expressive-yet-learnable class best balances fidelity, conciseness, and usefulness. Defining and learning that class would close the gap.

## 7. Current Research (as of June 2026)
- **LLM-assisted schema inference** that labels semantic types, names entities, and proposes normalized splits beyond purely structural induction *(frontier — verify)*.
- Inference over **lakehouse / streaming** data with schema drift detection and incremental re-inference (Iceberg/Delta schema evolution).
- Joint **schema + entity-relationship** induction (inferring FKs/INDs across document collections, linking to inclusion-dependency discovery).
- Tighter **MDL / Bayesian** formulations with sample-complexity (PAC/VC) guarantees for JSON type lattices *(frontier — verify)*.
- Groups: Baazizi/Colazzo/Ghelli/Sartiani (JSON type theory), HPI (Naumann/Papenbrock, profiling), and data-lake schema-discovery efforts (Toronto/Miller).

## 8. Future Work
- An expressive yet **PAC-learnable** JSON/document schema class with sample-complexity bounds.
- Globally-optimal or approximation-guaranteed MDL schema selection for nested data.
- Inference that emits a **normalized relational** target with FD/FK guarantees and minimal redundancy.
- Robust handling of semantic types, units, and cross-field constraints, not just structural shapes.

## 9. Key References
- **[Foundational]** Gold, E.M. *Language Identification in the Limit.* Information and Control, 1967. — [DOI](https://doi.org/10.1016/S0019-9958(67)91165-5)
- **[Foundational]** Bex, G.J., Gelade, W., Neven, F., Vansummeren, S. *Learning Deterministic Regular Expressions for the Inference of Schemas from XML Data.* ACM TWEB / WWW, 2010. — [DOI](https://doi.org/10.1145/1841909.1841911), [arXiv](https://arxiv.org/abs/1004.2372)
- **[SOTA]** Baazizi, M.-A., Colazzo, D., Ghelli, G., Sartiani, C. *Counting Types for Massive JSON Datasets / Schema Inference for Massive JSON Datasets.* EDBT, 2017. — [PDF](https://openproceedings.org/2017/conf/edbt/paper-62.pdf), [DBLP](https://dblp.org/rec/conf/edbt/BaaziziLCGS17.html)
- **[SOTA]** Papenbrock, T., Naumann, F. *A Hybrid Approach to Functional Dependency Discovery (HyFD).* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2915203)
- **[Foundational]** Rissanen, J. *Modeling by Shortest Data Description (MDL).* Automatica, 1978. — [DOI](https://doi.org/10.1016/0005-1098(78)90005-5)
- **[Survey]** Abiteboul, S., Buneman, P., Suciu, D. *Data on the Web: From Relations to Semistructured Data and XML.* Morgan Kaufmann, 2000. — [DBLP](https://dblp.org/rec/books/mk/BunemanSA99.html)

## 10. Worked Example

Infer a JSON schema from three documents:

```
d1 = {id:1, name:"Ann", tags:["x"]}
d2 = {id:2, name:"Bob"}
d3 = {id:3, name:"Cy", tags:[]}
```

**Type fusion (Baazizi et al.).** Per record, the inferred shapes are
$\{id:\text{Num}, name:\text{Str}, tags:[\text{Str}]\}$, $\{id:\text{Num}, name:\text{Str}\}$, $\{id:\text{Num}, name:\text{Str}, tags:[\,]\}$. The lattice join (least upper bound) merges them: `id` and `name` appear in all 3 records → **required**; `tags` appears in 2 of 3 → **optional**, written $tags?$. Empty and singleton arrays unify to $[\text{Str}]$. Result:
$$\mathcal{S} = \{\,id:\text{Num},\ name:\text{Str},\ tags?:[\text{Str}]\,\}.$$

**MDL check.** The verbose union-of-shapes schema would list all three variants ($\approx$ 3 shape descriptions). The fused $\mathcal{S}$ costs fewer model bits $L(\mathcal{S})$ while still validating all 3 docs ($L(D\mid\mathcal{S})$ unchanged), so it wins the $L(\mathcal{S})+L(D\mid\mathcal{S})$ objective. Note `tags?` generalizes correctly: a future doc with or without `tags` validates — exactly the compact, generalizing schema the problem seeks.

---
*Part of the [DBMS Research catalog](../../README.md).*
