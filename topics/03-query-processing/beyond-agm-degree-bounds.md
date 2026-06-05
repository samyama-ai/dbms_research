# Beyond-AGM bounds with functional dependencies

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/beyond-agm-degree-bounds` · **Status:** partially-solved

## 1. Problem Statement

The AGM bound bounds the output size of a conjunctive query using only relation *cardinalities*. Real schemas carry much more structure: **functional dependencies (FDs)**, **degree constraints** (e.g., each user has at most $k$ orders), keys, and cardinality constraints on projections. These can make the true maximum output far smaller than $\mathrm{AGM}(Q)$. The problem: **given a query $Q$ and a set of statistical/structural constraints $\Sigma$ (cardinalities, degree bounds, FDs), determine the tight worst-case output size $\max_{D\models\Sigma}|Q(D)|$, and design a join algorithm that runs in time matching that refined bound.**

Variants: (a) the **bound** (combinatorial) variant — compute/characterize the tight size bound; (b) the **algorithmic** variant — an evaluation algorithm whose runtime matches the bound up to polylog; (c) the **closed-form vs. LP** variant — when does the bound have a clean closed form versus requiring solving an exponential-size information-theoretic program?

## 2. Mathematical Foundations

The refined bounds are **information-theoretic**. Associate to each attribute set a random variable; for a joint distribution on output tuples, the entropy $h(W)$ of attribute set $W$ obeys: monotonicity, submodularity ($h(X\cup Y)+h(X\cap Y)\le h(X)+h(Y)$), and constraints from $\Sigma$ (a degree bound or cardinality bound caps a conditional entropy $h(Y\mid X)\le \log b$; an FD $X\to Y$ forces $h(Y\mid X)=0$). The tight log-output bound is the **entropic bound**
$$\log_2 \max_{D\models\Sigma}|Q(D)| \;\le\; \max_{h\in \Gamma^*_n} h(V) \ \text{s.t.}\ h \text{ satisfies } \Sigma,$$
where $\Gamma^*_n$ is the (non-polyhedral) cone of entropic vectors. Relaxing $\Gamma^*_n$ to the **polymatroid cone** $\Gamma_n$ (Shannon inequalities) gives the computable **polymatroid bound**, which equals AGM when only cardinalities are present and is tight in many constrained cases but can be strictly looser than the entropic bound in general (because $\overline{\Gamma^*_n}\subsetneq\Gamma_n$ for $n\ge 4$, by non-Shannon inequalities — Zhang–Yeung).

## 3. State of the Art (SOTA)

**Theory-SOTA:** the **PANDA** algorithm (Abo Khamis, Ngo, Suciu — "Proof-Assisted eNtropic Degree-Aware") evaluates a query in time matching the polymatroid bound under degree/cardinality/FD constraints, by turning a *proof sequence* of the bound (a Shannon-inequality derivation) into a sequence of joins and projections. Earlier, the **CEDC / degree-aware** framework (Abo Khamis–Ngo–Rudra, "FAQ" and "Computing Join Queries with Functional Dependencies") gave size bounds with FDs and degree constraints. The **submodular width** $\mathrm{subw}(Q)$ (Marx) characterizes the best width achievable; PANDA achieves $\tilde O(N^{\mathrm{subw}})$ for Boolean CQs.

## 4. Upper Bound

For a conjunctive query with constraint set $\Sigma$ (cardinalities, degrees, simple FDs), PANDA evaluates $Q$ in time $\tilde O\big(2^{\mathrm{poly}(n)}\cdot N^{w}\big)$ where $N^{w}$ is the polymatroid bound value (and for Boolean queries $w=\mathrm{subw}(Q)$), in the RAM model. When constraints are only cardinalities, this reduces to the AGM/Generic-Join bound $\tilde O(\mathrm{AGM}(Q,D))$. The bound is "tight" in the sense of matching the polymatroid program optimum; the dependence on the number of variables (size of the proof sequence) is the practical weak point.

## 5. Lower Bound

The polymatroid bound is **not always achievable as a true max output**: for $n\ge 4$ attributes, non-Shannon information inequalities (Zhang–Yeung 1998 and successors) prove the entropic cone is strictly inside the polymatroid cone, so the *true* tight bound can be strictly below the polymatroid bound — meaning current matching algorithms can be a polynomial factor away from the genuine optimum. Computing the exact entropic bound is tied to the **undecidability/complexity of the entropy region**: the closure $\overline{\Gamma^*_n}$ has no known finite description, and determining membership for related conditional-independence implication problems is hard. Output materialization is trivially $\Omega(|Q(D)|)$.

## 6. The Gap

Two gaps. (1) **Polymatroid vs. entropic:** algorithms match the polymatroid bound, but the true worst-case output can be smaller (governed by the entropic cone), and no algorithm is known to match the entropic bound in general — closing this requires either new non-Shannon-aware algorithms or a proof that the gap is irrelevant for "natural" constraint classes. (2) **Practicality:** PANDA's proof-sequence overhead ($2^{\mathrm{poly}(n)}$ and large constants) makes it a theoretical algorithm; no system implements general degree/FD-aware WCOJ at production speed.

## 7. Current Research (as of June 2026)

Directions: (1) characterizing constraint classes (e.g., **acyclic** degree constraints, simple FDs) where polymatroid = entropic and closed forms exist; (2) simplifying PANDA toward an implementable operator (degree-aware Generic Join variants); (3) connections to **conjunctive query containment under constraints** and to **cardinality estimation** (using degree statistics to bound intermediate sizes). Groups: Suciu, Abo Khamis, Ngo (RelationalAI/UW), Rudra (Buffalo), Marx (Bonn), Olteanu (Zurich). *(frontier — verify)* 2025–2026 work reportedly gives improved degree-aware size bounds and partial PANDA implementations integrated with optimizer cardinality estimation.

## 8. Future Work

- Determine for which constraint families the polymatroid bound is tight (entropic = polymatroid) and admits a closed form.
- A practical, low-overhead degree/FD-aware WCOJ operator usable inside a real engine.
- Tight bounds and algorithms under *projection* cardinality constraints and approximate (statistical) degree bounds.
- Bridge to learned cardinality estimation: degree constraints as principled upper bounds for the optimizer.

## 9. Key References

- **[Foundational]** Gottlob, Lee, Valiant, Valiant. *Size and Treewidth Bounds for Conjunctive Queries.* JACM, 2012.
- **[Foundational]** Abo Khamis, Ngo, Rudra. *FAQ: Questions Asked Frequently.* PODS 2016.
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* PODS 2017 (the PANDA paper).
- **[Foundational]** Marx. *Tractable Hypergraph Properties for Constraint Satisfaction and Conjunctive Queries.* JACM, 2013 (submodular width).
- **[Foundational]** Zhang, Yeung. *On Characterization of Entropy Function via Information Inequalities.* IEEE Trans. Information Theory, 1998 (non-Shannon inequalities).
- **[Survey]** Ngo. *Worst-Case Optimal Join Algorithms: Techniques, Results, and Open Problems.* PODS 2018 (tutorial/survey).

---
*Part of the [DBMS Research catalog](../../README.md).*
