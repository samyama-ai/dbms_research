# Provenance Polynomial Compression Bounds

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/provenance-polynomial-compression` · **Status:** open

## 1. Problem Statement
The how-provenance of an answer is a polynomial in $\mathbb{N}[X]$ whose monomials enumerate derivations. Written out explicitly, this polynomial can be astronomically large — a join of $k$ relations or a recursive reachability query produces exponentially many monomials. In practice provenance is stored as a **circuit** (a DAG of $+$ and $\cdot$ gates over the indeterminates) or a **factorized** representation (a nested-product form induced by a variable order / join tree). The problem is to determine **tight bounds on the smallest such representation** of a given query's provenance polynomial, and to characterize **exactly when polynomial-size representations exist**. Variants: (a) *decision* — does query $Q$ on database $D$ admit a circuit of size $\le s$? (b) *optimization* — find the minimum-size circuit/factorization. (c) *dichotomy* — classify queries by whether provenance is always polynomially-compressible (data complexity) regardless of $D$.

## 2. Mathematical Foundations
Provenance circuits are arithmetic circuits over the semiring; their size is the natural complexity measure. The factorized-database theory of **Olteanu–Závodný** ties the smallest factorization of a CQ's result/provenance to the query's structure via the **fractional hypertree width** $\mathrm{fhtw}$ and the *factorization width* $s^\uparrow(Q)$: the result (and its provenance) factorizes into size $O(|D|^{s^\uparrow(Q)})$, and this is *tight* — matching lower bounds hold. The deeper hierarchy is **knowledge compilation**: provenance can be compiled to OBDDs, FBDDs, d-DNNFs, or general circuits, with a strict succinctness hierarchy (OBDD $\subsetneq$ FBDD $\subsetneq$ d-DNNF $\subsetneq$ circuits). The seminal Jha–Suciu result connects a query's provenance OBDD-width to its being *(hierarchical)* — hierarchical CQs have poly-size (indeed OBDD) lineage, non-hierarchical ones provably do not (for read-once / bounded-width classes). Read-once lineage (a formula where each variable appears once) exists iff the query/instance avoids certain forbidden minors (Sen–Deshpande–Getoor). The AGM bound $|Q(D)| \le \prod \cdot$ governs output (and hence monomial-count) size.

## 3. State of the Art (SOTA)
Theory-SOTA: Olteanu–Závodný, *Factorised Representations of Query Results* (ACM TODS 2015) gives tight factorization-width bounds; Jha–Suciu, *Knowledge Compilation Meets Database Theory* (ICDT 2011 / TODS) classifies CQ lineage by compilation target and proves OBDD lower bounds for non-hierarchical queries. Amarilli–Bourhis–Senellart connect provenance circuit size to **treewidth** of the instance (bounded-treewidth databases yield linear-size provenance circuits for MSO/CQ queries) — *Provenance Circuits for Trees and Treelike Instances* (ICALP 2015). Systems-SOTA: factorized engines (FDB, F-IVM), ProvSQL (circuit-based provenance + probability), and the SafeQuery / lineage-compilation tools in probabilistic databases (MystiQ, SPROUT) realize these bounds.

## 4. Upper Bound
For a CQ $Q$, the provenance factorizes to size $O(|D|^{s^\uparrow(Q)})$ with $s^\uparrow(Q) \le \mathrm{fhtw}(Q)$, and to size $O(|D|)$ (linear) iff $Q$ is *hierarchical* (Olteanu–Závodný). Over instances of treewidth $w$, any MSO/CQ query has a provenance circuit of size $O(f(w)\cdot |D|)$ — linear in data (Amarilli–Bourhis–Senellart). d-DNNF/circuit compilation gives the smallest known *general* target, supporting linear-time model counting on the compiled form.

## 5. Lower Bound
**Non-hierarchical** CQs have **no polynomial-size OBDD** lineage and, more strongly, require super-polynomial FBDD / read-once-formula size (Jha–Suciu). These are *unconditional* lower bounds in the respective circuit models. Factorization-width bounds are matched by **information-theoretic lower bounds**: any factorization of the result of a query with width $s^\uparrow$ needs size $\Omega(|D|^{s^\uparrow})$ on worst-case instances (Olteanu–Závodný). Deciding the *minimum* circuit size is tied to general arithmetic-circuit minimization, believed intractable; finding minimum read-once / minimum factorization is **NP-hard** in general (subsumes formula-minimization). Exact probability over the lineage of non-hierarchical queries is **#P-hard** (Dalvi–Suciu dichotomy), which is *why* small circuits cannot always exist.

## 6. The Gap
For **CQs and bounded-treewidth instances** the picture is essentially **tight** (factorization width, treewidth-linear circuits, OBDD dichotomy). The genuinely **open** parts: (i) tight minimum-circuit-size bounds in the *most succinct general* models (d-DNNF and unrestricted arithmetic circuits) — no matching lower bounds, as these would imply breakthroughs in circuit complexity; (ii) compression bounds for *recursive* and *aggregate* provenance, where width measures are not fully developed; (iii) the gap between the OBDD/FBDD lower-bound hierarchy and what general circuits achieve. Closing (i) is entangled with notoriously hard arithmetic-circuit lower bounds.

## 7. Current Research (as of June 2026)
Amarilli, Bourhis, Capelli, Monet, and Senellart actively push **provenance circuit lower bounds** via communication complexity and knowledge-compilation succinctness; Monet's work on *combined* tractability and circuit size is central. Olteanu's group (Zurich) connects factorization width to learning and tensor decompositions. *(frontier — verify)* recent threads study circuit-size lower bounds for **probabilistic-database provenance beyond OBDD** using d-DNNF lower-bound techniques (e.g., via the rectangle/cover method) and compression of provenance for **conjunctive queries with negation**. Suciu's group continues the dichotomy program tying compressibility to query safety.

## 8. Future Work
Articulated directions: unconditional lower bounds for d-DNNF/SDD provenance of unsafe queries; compression theory for recursive and aggregate provenance; instance-optimal (not just worst-case) factorization; adaptive/lossy provenance compression with accuracy guarantees; and connections between provenance circuit size and the broader arithmetic-circuit-complexity frontier.

## 9. Key References
- **[Foundational]** D. Olteanu, J. Závodný. *Factorised Representations of Query Results.* ACM TODS, 2015.
- **[Foundational]** A. Jha, D. Suciu. *Knowledge Compilation Meets Database Theory.* ICDT, 2011 / ACM TODS.
- **[SOTA]** A. Amarilli, P. Bourhis, P. Senellart. *Provenance Circuits for Trees and Treelike Instances.* ICALP, 2015.
- **[SOTA]** A. Amarilli, F. Capelli, M. Monet, P. Senellart. *Connecting Knowledge Compilation Classes and Width Parameters.* Theory of Computing Systems, 2020.
- **[Foundational]** N. Dalvi, D. Suciu. *The Dichotomy of Probabilistic Inference for Unions of Conjunctive Queries.* J. ACM, 2012.

---
*Part of the [DBMS Research catalog](../../README.md).*
