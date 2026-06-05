# Optimal Bag-Semantics CQ Equivalence

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/bag-cq-equivalence` · **Status:** open

## 1. Problem Statement

Real SQL queries operate under **multiset (bag) semantics**: a tuple may appear multiple times, with multiplicity equal to the number of distinct valuations producing it. Given two conjunctive queries $Q_1, Q_2$, **bag equivalence** asks whether they return the *same multiset* on every database:
$$Q_1 \equiv_{\mathrm{bag}} Q_2 \quad\Longleftrightarrow\quad \forall D:\; \#Q_1(D)(\bar{t}) = \#Q_2(D)(\bar{t}) \;\text{ for all } \bar{t}.$$

Variants:
- **Bag equivalence** (the focus): is the count function identical everywhere?
- **Bag containment:** $\#Q_1(D)(\bar t) \le \#Q_2(D)(\bar t)$ for all $D, \bar t$.
- **Bag-set semantics** (duplicates only from the outer projection / `SELECT DISTINCT`-free bodies but set base tables).

**Bag equivalence is decidable** (it reduces to query isomorphism). The **open** problem — one of the oldest in database theory (Chaudhuri–Vardi 1993) — is the **decidability of bag containment**, on which optimal bag-equivalence reasoning and many SQL rewrites depend.

## 2. Mathematical Foundations

Under bag semantics, a CQ $Q$ on database $D$ assigns to each output tuple $\bar t$ the number of homomorphisms from $Q$'s body to $D$ that project to $\bar t$. This count is a **polynomial with nonnegative integer coefficients** in the relation multiplicities — it is the *Hilbert/counting* image of $Q$.

**Bag equivalence theorem (Chaudhuri–Vardi 1993):** $Q_1 \equiv_{\mathrm{bag}} Q_2$ iff their bodies are **isomorphic** (identical up to renaming of existential variables) after removing redundant duplicates — there is *no* minimization across non-isomorphic forms. Thus bag equivalence is **GI-complete-ish / decidable** and strictly finer than set equivalence (where homomorphic equivalence / minimization applies).

Bag *containment* corresponds to comparing two such counting polynomials for domination over all nonnegative integer assignments — a problem with the flavor of **Hilbert's Tenth Problem** and Positivstellensatz-style reasoning, which is exactly why decidability is elusive.

## 3. State of the Art (SOTA)

- **Chaudhuri–Vardi (PODS 1993)** introduced the problem, proved bag equivalence = isomorphism, and showed bag containment is at least as hard as a notoriously open number-theoretic question; they conjectured undecidability.
- **Ioannidis–Ramakrishnan** and **Jayram–Kolaitis–Vee (PODS 2006)** proved **bag containment of CQs with inequalities ($\neq$) is undecidable**, isolating where undecidability provably begins.
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

- **[Foundational]** S. Chaudhuri, M. Y. Vardi. *Optimization of Real Conjunctive Queries.* PODS, 1993.
- **[SOTA]** T. S. Jayram, P. G. Kolaitis, E. Vee. *The Containment Problem for Real Conjunctive Queries with Inequalities.* PODS, 2006.
- **[Foundational]** T. J. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007.
- **[SOTA]** M. A. Khamis, P. G. Kolaitis, H. Q. Ngo, D. Suciu. *Bag Query Containment and Information Theory.* PODS / TODS, 2020–2021.
- **[Foundational]** Y. E. Ioannidis, R. Ramakrishnan. *Containment of Conjunctive Queries: Beyond Relations as Sets.* TODS, 1995.
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995.

---
*Part of the [DBMS Research catalog](../../README.md).*
