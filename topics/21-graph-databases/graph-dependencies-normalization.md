# Keys, normalization and dependencies for graphs

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/graph-dependencies-normalization` · **Status:** open
> **Verification note:** Per Fan–Wu–Xu (SIGMOD 2016), GFD *validation* (combined) is coNP-complete; the NP-hardness cited in §4/§5 refers to the dual violation-detection direction (subgraph matching).

## 1. Problem Statement
Define **functional/entity dependencies and normal forms for property graphs** that guide good design — minimizing redundancy and anomalies — *without presupposing a fixed schema*, then characterize their implication and a normalization procedure.

Concretely:
- **Define** graph functional dependencies (GFDs), graph entity dependencies (GEDs), and key constraints over heterogeneous, schema-flexible data.
- **Implication (decision):** does a set $\Sigma$ of GFDs/GEDs imply $\varphi$?
- **Validation/consistency (decision):** is $G\models\Sigma$? Is $\Sigma$ satisfiable?
- **Normalization (optimization):** transform a graph design into a normal form eliminating redundancy while preserving information and dependencies — the graph analogue of BCNF/4NF and lossless-join/dependency-preserving decomposition.

The problem is open because no consensus normal-form theory exists, and the absence of a fixed schema makes "redundancy" itself nontrivial to define.

## 2. Mathematical Foundations
**Relational baseline.** An FD $X\to Y$; Armstrong's axioms are **sound and complete**; implication is decidable in linear time; **BCNF** removes FD-redundancy, **lossless-join + dependency-preservation** characterize good decompositions (Beeri–Bernstein, Fagin). MVDs give **4NF**; join dependencies give **5NF/PJNF**.

**Graph lifting.** A **GFD** (Fan–Wu–Xu, SIGMOD 2016) is a pair $(Q[\bar{x}], X\to Y)$: a graph pattern $Q$ plus an FD on the matched attributes/labels — semantics quantify over all homomorphic/isomorphic matches of $Q$ in $G$. A **GED** (Fan–Lu) further allows equality of *vertex identities*, subsuming keys and FDs. Because satisfaction ranges over pattern matches, validation reduces to **subgraph matching** ⇒ NP-hard combined complexity.

Implication is governed by a **chase** over pattern-FD pairs; redundancy is information-theoretic — formalizable via the **Arenas–Libkin information-theoretic measure** of normal forms (entropy of a cell given the rest). A graph normal form should guarantee that no value is "predictable" from others given $\Sigma$, lifting Arenas–Libkin's characterization (which proved BCNF $\equiv$ "no redundancy" in an information-theoretic sense) to graphs.

## 3. State of the Art (SOTA)
- **GFDs** (Fan, Wu, Xu, SIGMOD 2016) and **GEDs** (Fan, Lu, PODS/TODS 2019) — the leading dependency formalisms; include sound-and-complete axiom systems and implication/validation complexity results.
- **Graph keys / GKeys** (Fan et al., VLDB 2015) — keys via patterns for entity resolution.
- **Differential dependencies / conditional FDs** lifted to graphs for data cleaning.
- **Normalization:** essentially *no* established graph normal-form theory; only scattered proposals and analogies. Relational normalization theory (Codd, Fagin, Arenas–Libkin) remains the reference point.
- **PG-Schema / PG-Keys** provide constraints but not a *normalization* (redundancy-elimination) theory.

## 4. Upper Bound
- **GFD/GED implication:** decidable; **NP-complete** for GFD implication (and **coNP-complete** for GFD satisfiability), with sound-and-complete finite axiomatizations (Fan et al.). Satisfiability for GEDs decidable, **coNP**/higher depending on fragment.
- **Validation:** in **PTIME data complexity** for fixed patterns; **NP-complete combined** (subgraph matching).
- **Normalization:** no general algorithm with proven guarantees; relational analogues give EXPTIME-worst-case BCNF decomposition, but the graph lifting is undefined/open.

## 5. Lower Bound
- **GFD implication:** **NP-complete** (Fan, Wu, Xu; satisfiability is coNP-complete) — strictly harder than relational FD implication (which is PTIME), due to pattern quantification.
- **Validation:** **NP-hard** combined (subgraph isomorphism).
- **General GED/embedded-dependency implication:** can become **undecidable** for unrestricted tgd-style graph dependencies (inheriting Beeri–Vardi undecidability).
- **Normalization lower bounds:** undefined — there is no agreed normal form against which to prove hardness, which is itself the open gap.

## 6. The Gap
Dependency *theory* (GFDs/GEDs with coNP implication, complete axioms) is comparatively mature; **normalization theory is essentially absent**. The open questions: (1) What is the right *information-theoretic* definition of graph redundancy under schema flexibility? (2) Is there a graph BCNF/4NF with a **lossless, dependency-preserving** decomposition theorem? (3) Can normalization operate *without* a fixed schema, treating structure itself as decomposable? No matching upper/lower bounds exist because the target object (the normal form) is undefined. Closing the gap requires first *defining* the normal form, then proving correctness/optimality.

## 7. Current Research (as of June 2026)
- Extending GEDs toward design guidance and data cleaning at scale; incremental GFD validation *(frontier — verify)*.
- Information-theoretic redundancy measures for semi-structured/graph data, extending Arenas–Libkin *(frontier — verify)*.
- Interaction of dependencies with PG-Schema open/closed types.
- Groups: Fan (Edinburgh/Shenzhen) and collaborators (dominant on graph dependencies), Arenas/Barceló (IMFD Chile, info-theoretic foundations), Bonifati (Lyon).

## 8. Future Work
- A principled, schema-agnostic notion of graph redundancy and an associated normal form.
- Lossless-join / dependency-preserving decomposition theorems for graphs.
- Tractable fragments of GED implication and practical normalization algorithms.
- Empirical study linking normal forms to query performance and update anomalies.

## 9. Key References
- **[Foundational]** Codd, E. F. *Further Normalization of the Data Base Relational Model.* IBM Research, 1972. — [DBLP search](https://dblp.org/search?q=Further+Normalization+of+the+Data+Base+Relational+Model)
- **[Foundational]** Fagin, R. *Multivalued Dependencies and a New Normal Form for Relational Databases.* ACM TODS, 1977. — [DOI](https://doi.org/10.1145/320557.320571)
- **[Foundational]** Arenas, M., Libkin, L. *An Information-Theoretic Approach to Normal Forms for Relational and XML Data.* JACM, 2005. — [DOI](https://doi.org/10.1145/1059513.1059519)
- **[SOTA]** Fan, W., Wu, Y., Xu, J. *Functional Dependencies for Graphs.* SIGMOD 2016. — [DOI](https://doi.org/10.1145/2882903.2915232)
- **[SOTA]** Fan, W., Lu, P. *Dependencies for Graphs.* ACM TODS, 2019 (PODS 2017). — [DOI](https://doi.org/10.1145/3287285)
- **[SOTA]** Fan, W., Fan, Z., Tian, C., Dong, X. L. *Keys for Graphs.* VLDB 2015. — [DOI](https://doi.org/10.14778/2824032.2824056)
- **[Survey]** Abiteboul, S., Hull, R., Vianu, V. *Foundations of Databases.* Addison-Wesley, 1995. — [book site](http://webdam.inria.fr/Alice/)

## 10. Worked Example

**A GFD detecting redundancy.** Consider a property graph of an airline. Pattern $Q$ matches any two `Flight` vertices $x,y$ that each point (via an `operatedBy` edge) to the same `Airline` vertex $z$. Attach the dependency
$$X \to Y:\quad z.\texttt{name} \;\to\; x.\texttt{carrierCode}.$$
Semantics: in **every** match of $Q$, if two flights share airline $z$, then $z.\texttt{name}$ functionally determines the flight's `carrierCode`.

Now take $G$ with $z.\texttt{name}=$ "Delta", and flights $f_1,\dots,f_{100}$ all `operatedBy` $z$, each storing `carrierCode = DL`. The GFD holds, but the value `DL` is **redundant**: it is predictable from $z.\texttt{name}$ in all 100 vertices. Information-theoretically (Arenas–Libkin), the conditional entropy of any one `carrierCode` cell given the rest is $0$ — the hallmark of a non-normal-form design. A graph "BCNF" would refactor `carrierCode` onto the `Airline` vertex $z$, storing it once.

**Validation cost.** Checking $G\models\Sigma$ requires enumerating matches of $Q$ — here a subgraph-isomorphism search, NP-hard in combined complexity but PTIME for the fixed pattern $Q$.

---
*Part of the [DBMS Research catalog](../../README.md).*
