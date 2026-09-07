---
id: 01-relational-theory/bag-cq-equivalence
title: "Optimal Bag-Semantics CQ Equivalence"
topic: 01-relational-theory
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Optimal Bag-Semantics CQ Equivalence

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/bag-cq-equivalence` · **Status:** open

## 1. Problem Statement

Real SQL queries operate under **multiset (bag) semantics**: a tuple may appear multiple times, with multiplicity equal to the number of distinct valuations producing it. Given two conjunctive queries $Q_1, Q_2$, **bag equivalence** asks whether they return the *same multiset* on every database:
$$Q_1 \equiv_{\mathrm{bag}} Q_2 \quad\Longleftrightarrow\quad \forall D:\; \\#Q_1(D)(\bar{t}) = \\#Q_2(D)(\bar{t}) \;\text{ for all } \bar{t}.$$

Variants:
- **Bag equivalence** (the focus): is the count function identical everywhere?
- **Bag containment:** $\\#Q_1(D)(\bar t) \le \\#Q_2(D)(\bar t)$ for all $D, \bar t$.
- **Bag-set semantics** (duplicates only from the outer projection / `SELECT DISTINCT`-free bodies but set base tables).

**Bag equivalence is decidable** (it reduces to query isomorphism). The **open** problem — one of the oldest in database theory (Chaudhuri–Vardi 1993) — is the **decidability of bag containment**, on which optimal bag-equivalence reasoning and many SQL rewrites depend.

## 2. Mathematical Foundations

Under bag semantics, a CQ $Q$ on database $D$ assigns to each output tuple $\bar t$ the number of homomorphisms from $Q$'s body to $D$ that project to $\bar t$. This count is a **polynomial with nonnegative integer coefficients** in the relation multiplicities — it is the *Hilbert/counting* image of $Q$.

**Bag equivalence theorem (Chaudhuri–Vardi 1993):** $Q_1 \equiv_{\mathrm{bag}} Q_2$ iff their bodies are **isomorphic** (identical up to renaming of existential variables) after removing redundant duplicates — there is *no* minimization across non-isomorphic forms. Thus bag equivalence is **decidable**, with complexity comparable to **graph isomorphism**, and strictly finer than set equivalence (where homomorphic equivalence / minimization applies).

Bag *containment* corresponds to comparing two such counting polynomials for domination over all nonnegative integer assignments — a problem with the flavor of **Hilbert's Tenth Problem** and Positivstellensatz-style reasoning, which is exactly why decidability is elusive.

## 3. State of the Art (SOTA)

- **Chaudhuri–Vardi (PODS 1993)** introduced the problem, proved bag equivalence = isomorphism, and showed bag containment is at least as hard as a notoriously open number-theoretic question; they conjectured undecidability.
- **Jayram–Kolaitis–Vee (PODS 2006)** proved **bag containment of CQs with inequalities ($\neq$) is undecidable**, isolating where undecidability provably begins; **Ioannidis–Ramakrishnan (1995)** is the earlier study of containment beyond pure set semantics.
- **Kopparty–Rossman**, **Khamis–Kolaitis–Ngo–Suciu** and others connected bag containment to **information theory and tensor/Hölder inequalities**, giving sufficient conditions and approximations.
- For restricted classes (single self-join-free CQs, "projection-free" CQs), bag containment is decidable and polynomial. Systems (query optimizers in PostgreSQL, Spark SQL, Calcite) rely on *sound but incomplete* bag-equivalence rules for rewrites.

## 4. Upper Bound

- **Bag equivalence (general CQs):** decidable; reduces to checking body isomorphism — solvable in time comparable to **graph isomorphism** (quasi-polynomial, Babai 2016), polynomial for bounded arity / treewidth.
- **Bag-set equivalence:** decidable, with a Chaudhuri–Vardi-style characterization.
- **Bag containment, projection-free CQs:** decidable; expressible via comparison of monomials.
- **Bag containment, general CQs:** *no* general decision procedure known — only **semidecision** (e.g., enumerate witnesses) and **sufficient** information-theoretic/Hölder certificates that prove containment when a valid "shape" inequality exists.

## 5. Lower Bound

- **Bag containment with inequalities:** **undecidable** (Jayram–Kolaitis–Vee 2006), by reduction from Hilbert's Tenth Problem.
- **Bag containment without inequalities:** **no nontrivial lower bound is known to settle decidability** — it is genuinely open. Chaudhuri–Vardi showed it is at least as hard as deciding whether two counting polynomials dominate, linking it to hard problems in number theory.
- Bag equivalence inherits at least **graph-isomorphism hardness** in the lower-bound direction (no known NP-hardness; not believed NP-hard).

## 6. The Gap

This is a rare **decidability gap that has stayed open for 30+ years**. Bag *equivalence* is fully closed (= isomorphism). For bag *containment* of self-join-bearing projection CQs, we have neither a decision algorithm nor an undecidability proof. The boundary is sharp: adding $\neq$ makes it undecidable; the pure-CQ case sits exactly on the frontier. Closing it would require either (a) a reduction from a known-undecidable problem that survives the absence of inequalities, or (b) a complete decision procedure, likely via real/integer Positivstellensatz or polynomial-domination machinery.

## 7. Current Research (as of June 2026)

(1) **Information-theoretic characterizations** of bag containment via entropy/Hölder inequalities and the **polymatroid/Shannon-flow** framework (Khamis, Kolaitis, Ngo, Suciu) — pushing the class of provable containments *(frontier — verify)*. (2) Connections to **#CQ / counting-query** equivalence and to **provenance semirings** (Green–Karvounarakis–Tannen), where bag semantics is the $\mathbb{N}$-semiring. (3) **Approximate / relaxed** bag containment for optimizer soundness. (4) Renewed attacks via real algebraic geometry on the polynomial-domination formulation *(frontier — verify)*.

## 8. Future Work

- Settle decidability of bag containment for general CQs — the central prize.
- Tight complexity of bag equivalence under bounded width / under constraints.
- Bag containment under TGDs/EGDs (bag semantics + integrity constraints).
- Optimizer-grade complete bag-rewrite rules for the decidable fragments.

## 9. Key References

- **[Foundational]** S. Chaudhuri, M. Y. Vardi. *Optimization of Real Conjunctive Queries.* PODS, 1993. — [DOI](https://doi.org/10.1145/153850.153856)
- **[SOTA]** T. S. Jayram, P. G. Kolaitis, E. Vee. *The Containment Problem for Real Conjunctive Queries with Inequalities.* PODS, 2006. — [DOI](https://doi.org/10.1145/1142351.1142363)
- **[Foundational]** T. J. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[SOTA]** M. A. Khamis, P. G. Kolaitis, H. Q. Ngo, D. Suciu. *Bag Query Containment and Information Theory.* PODS / TODS, 2020–2021. — [arXiv](https://arxiv.org/abs/1906.09727)
- **[Foundational]** Y. E. Ioannidis, R. Ramakrishnan. *Containment of Conjunctive Queries: Beyond Relations as Sets.* TODS, 1995. — [DOI](https://doi.org/10.1145/211414.211419)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)

## 10. Worked Example

Let database $D$ have one binary relation $E$ (a graph). Compare two CQs:

- $Q_1(x)\;{:}\!-\;E(x,y)$ — project the source $x$ of each edge, body of one atom.
- $Q_2(x)\;{:}\!-\;E(x,y),E(x,z)$ — source $x$ with two (possibly equal) outgoing edges.

For each value $a$, the bag multiplicity of $a$ as an answer is: $Q_1$ gives $\deg^{+}(a)$ (out-degree), while $Q_2$ gives $\deg^{+}(a)^2$ (pairs $(y,z)$). On the tiny graph $E=\{(a,b),(a,c)\}$: $Q_1$ outputs $a$ with multiplicity $2$; $Q_2$ outputs $a$ with multiplicity $4$.

**Equivalence** asks if $\deg^{+}(a)=\deg^{+}(a)^2$ for all $D$ — false (take any node of degree 2), and indeed the bodies are non-isomorphic, so $Q_1\not\equiv_{\mathrm{bag}}Q_2$ (Chaudhuri–Vardi). **Containment** $Q_1\sqsubseteq_{\mathrm{bag}}Q_2$ asks $\deg^{+}\le(\deg^{+})^2$ everywhere — true here ($n\le n^2$ for $n\in\mathbb{N}$). Deciding such polynomial-domination relations for arbitrary CQs is precisely the 30-year-open problem.

---
*Part of the [DBMS Research catalog](../../README.md).*
