---
id: 01-relational-theory/inclusion-dependencies-acyclicity
title: "Inclusion Dependencies and FD Interaction"
topic: 01-relational-theory
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Inclusion Dependencies and FD Interaction

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/inclusion-dependencies-acyclicity` · **Status:** partially-solved

## 1. Problem Statement

An **inclusion dependency (IND)** $R[A_1,\dots,A_k] \subseteq S[B_1,\dots,B_k]$ asserts that the projection of relation $R$ onto attributes $A_1,\dots,A_k$ is contained in the projection of $S$ onto $B_1,\dots,B_k$. A **functional dependency (FD)** $X \to Y$ asserts that $X$-equal tuples agree on $Y$.

The central problem is the **implication problem**: given a set $\Sigma$ of FDs and INDs and a single dependency $\sigma$, decide whether every database satisfying $\Sigma$ also satisfies $\sigma$ (written $\Sigma \models \sigma$). Variants:
- **Decision (finite vs. unrestricted implication):** Do these coincide? (They do *not* for FD+IND.)
- **Restricted classes:** acyclic INDs, unary INDs (UINDs), key-based INDs.
- **Optimization angle:** minimal cover / non-redundant axiomatization size.

The interaction is the difficulty: FDs and INDs are each individually well-behaved, but their combination breaks finite controllability and axiomatizability.

## 2. Mathematical Foundations

INDs alone are axiomatizable (reflexivity, projection-permutation, transitivity) and their implication is **PSPACE-complete** (Casanova–Fagin–Papadimitriou, 1984). FDs alone are decidable in linear time via closure.

The combination is governed by a fundamental negative result: **FD+IND implication is undecidable** (Chandra–Vardi 1985; Mitchell 1983), and **finite implication differs from unrestricted implication**. The proof encodes word problems / tiling via the cyclic chase, which need not terminate.

The **chase** is the core tool: repeatedly apply FDs (equating values) and INDs (introducing fresh "null" witnesses) to a tableau. IND firing can introduce new tuples indefinitely, producing an infinite chase. Acyclicity of the IND graph $G_\Sigma$ (nodes = relations, edges = INDs) bounds chase depth.

$$\Sigma \models \sigma \iff \text{the chase of } \mathrm{tableau}(\sigma) \text{ by } \Sigma \text{ satisfies } \sigma.$$

For **noncircular / acyclic INDs + FDs**, the chase terminates and implication becomes decidable. **Key-based** INDs (foreign-key style, where the referenced side is a key) combined with FDs restore decidability and finite controllability.

## 3. State of the Art (SOTA)

**Theory-SOTA:**
- General FD+IND: undecidable (Chandra–Vardi, *J. Comput. Syst. Sci.* 1985).
- Acyclic IND + FD: decidable, axiomatizable (Cosmadakis–Kanellakis–Vardi, PODS 1990).
- **Unary INDs + FDs:** finitely axiomatizable and decidable in polynomial time — the cleanest positive island (Cosmadakis–Kanellakis–Vardi).
- Key/foreign-key + FD reasoning underlies all modern schema validation.

**Systems-SOTA:** IND discovery (not implication) drives data-profiling tools — **BINDER** (Papenbrock et al., VLDB 2015) and **SINDY** for n-ary IND discovery; FAIDA for approximate INDs. These mine candidate INDs from data rather than reason about implication.

## 4. Upper Bound

- **INDs alone:** implication PSPACE-complete; membership in PSPACE by a polynomial-space chase-path search.
- **Unary IND + FD:** implication in **PTIME** (cubic), via a closure-style algorithm over a graph of unary inclusions and FD closures.
- **Acyclic IND + FD:** decidable; the chase terminates in length bounded by the acyclic structure, giving an exponential-tableau procedure (EXPTIME-style upper bounds).
- **Key-based IND + FD:** decidable; finite and unrestricted implication coincide.

Model: relational instances under set semantics, classical (finite) and unrestricted implication.

## 5. Lower Bound

- **INDs alone:** PSPACE-hard (Casanova–Fagin–Papadimitriou 1984) via reduction from linear-space Turing machine acceptance / regular-expression problems.
- **General FD+IND:** **undecidable** — both finite and unrestricted implication (Chandra–Vardi 1985; Mitchell 1983). This is the definitive lower bound: no algorithm exists, and the two notions provably diverge.
- Undecidability is by reduction from the word problem for monoids / the halting problem encoded in a non-terminating chase.

## 6. The Gap

For the *general* class the problem is closed in the strongest negative sense: **undecidable**, so no upper-bound algorithm can exist. The genuinely open frontier is the **boundary**: which syntactic restrictions on the FD/IND interaction restore decidability with *tight* complexity. Acyclic, unary, and key-based fragments are settled; intermediate fragments (e.g., bounded-cyclicity, typed INDs with limited FDs) have gaps between known decidability and matching lower bounds. Whether broader "guarded" or "frontier-guarded" fragments capturing realistic foreign-key + FD schemas admit elementary implication is partly open.

## 7. Current Research (as of June 2026)

- Connections to **existential rules / tuple-generating dependencies (TGDs)** and Datalog$^\pm$: INDs are a special TGD, and decidable fragments (guarded, sticky, weakly-acyclic) generalize acyclic-IND results. Work by Calì, Gottlob, Pieris on guarded TGDs continues to refine these boundaries.
- IND + FD reasoning re-enters via **knowledge-graph and ontology-mediated query answering**, where referential constraints meet keys *(frontier — verify)*.
- Approximate / soft IND discovery at scale (data lakes) by the Naumann group (HPI) and the discovery community remains active on the systems side.

## 8. Future Work

- Tight complexity for bounded-cycle IND+FD fragments.
- Implication under **bag (multiset)** and **incomplete (null)** semantics, where SQL referential integrity actually lives.
- Combining INDs/FDs with **denial and cardinality constraints** in a unified decidable core.
- Practical reasoners that exploit decidable islands for schema-evolution and integration tooling.

## 9. Key References

- **[Foundational]** Casanova, M., Fagin, R., Papadimitriou, C. *Inclusion Dependencies and Their Interaction with Functional Dependencies.* J. Comput. Syst. Sci., 1984. — [DOI](https://doi.org/10.1016/0022-0000(84)90075-8)
- **[Foundational]** Chandra, A., Vardi, M. *The Implication Problem for Functional and Inclusion Dependencies is Undecidable.* SIAM J. Comput. / JCSS, 1985. — [DOI](https://doi.org/10.1137/0214049)
- **[Foundational]** Cosmadakis, S., Kanellakis, P., Vardi, M. *Polynomial-time Implication Problems for Unary Inclusion Dependencies.* J. ACM, 1990. — [DOI](https://doi.org/10.1145/78935.78937)
- **[Survey]** Abiteboul, S., Hull, R., Vianu, V. *Foundations of Databases.* Addison-Wesley, 1995 (Ch. on dependency theory and the chase). — [book site](http://webdam.inria.fr/Alice/)
- **[SOTA]** Papenbrock, T., Kruse, S., Naumann, F. et al. *Divide & Conquer-based Inclusion Dependency Discovery (BINDER).* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2752939.2752946)

## 10. Worked Example

Why FD+IND interaction is dangerous, on a tiny schema. Relation $R(A,B)$ with FD $A \to B$ and the *cyclic* IND $R[B] \subseteq R[A]$. The IND graph has a self-loop on $R$ ($B$-column to $A$-column), so it is **not acyclic** — chase termination is not guaranteed.

Chase $\sigma$'s tableau starting from $R(a_0, b_0)$:
- IND $R[B]\subseteq R[A]$ fires on $b_0$: invent fresh tuple $R(b_0, b_1)$ (the $A$-value must be $b_0$, $B$-value is a new null $b_1$).
- It fires again on $b_1$: invent $R(b_1, b_2)$.
- ... producing an unbounded chain $a_0 \to b_0 \to b_1 \to b_2 \to \cdots$.

The FD $A\to B$ never merges these (all $A$-values distinct), so the chase runs forever. This non-termination is the engine behind Chandra–Vardi's undecidability proof — a Turing machine's tape is encoded in such a chain. Contrast the **acyclic** case: drop the IND or make it $R[B]\subseteq S[A]$ across distinct relations forming a DAG; then the chain length is bounded by the longest path in $G_\Sigma$, the chase halts, and implication becomes decidable.

---
*Part of the [DBMS Research catalog](../../README.md).*
