# Tight Bounds for Conjunctive Query Cardinality

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/agm-bound-tightness` · **Status:** partially-solved

## 1. Problem Statement
Given a conjunctive query (CQ) $Q$ over relations with known statistics (cardinalities, attribute domains, degree/frequency profiles, functional dependencies), produce an *upper bound* on the output cardinality $|Q(D)|$ that is as tight as possible while remaining valid for *every* database $D$ consistent with those statistics. The motivating questions are: (i) how far is the worst-case AGM bound from the *actual* cardinality on realistic instances, (ii) which additional statistics provably shrink the worst-case envelope, and (iii) can a tractable bound match the true cardinality up to a small factor. Variants: the **counting** variant (estimate $|Q(D)|$ numerically), the **bounding** variant (a certified upper bound), and the **optimization** variant (choose the statistics budget that minimizes worst-case looseness).

## 2. Mathematical Foundations
Model a CQ as a hypergraph $H = (V, E)$ where $V$ are variables (attributes) and each relation $R_e$ is a hyperedge $e \subseteq V$. A **fractional edge cover** is $x \in \mathbb{R}_{\ge 0}^E$ with $\sum_{e \ni v} x_e \ge 1$ for all $v \in V$. The **AGM bound** (Atserias–Grohe–Marx) states
$$ |Q(D)| \le \prod_{e \in E} |R_e|^{x_e}, $$
and the optimal $x$ (the fractional edge cover number $\rho^*$) makes this bound *tight in the worst case*: there exists a $D$ achieving it up to constants. The bound follows from Shearer's entropy inequality / Loomis–Whitney generalizations; the LP dual is a fractional vertex packing. Refinements replace cardinalities with **degree constraints** $\deg(Y \mid X) \le N$, yielding the **polymatroid bound**: minimize $h(V)$ over polymatroids $h$ (submodular, monotone, $h(\emptyset)=0$) subject to the statistical constraints, giving entropic/polymatroid LPs whose value upper-bounds $\log|Q(D)|$.

## 3. State of the Art (SOTA)
**Theory-SOTA:** The polymatroid bound and its degree-aware refinement (Gottlob–Lee–Valiant–Valiant; Abo Khamis–Ngo–Suciu) generalize AGM and are provably the tightest bounds expressible from the given constraint class (relaxing entropic to polymatroid functions). Suciu et al.'s work on the **entropic bound** characterizes the exact limit. **Systems-SOTA:** **Pessimistic cardinality estimators** — *Cardinality Estimation Done Right* (Cai–Balazinska–Suciu, CIDR 2019) and follow-ups — compute degree-sequence-based bounds and feed them to optimizers; *SafeBound* (Deeds et al., SIGMOD 2023) makes certified bounds practical via compressed degree sequences. Learned estimators (e.g., MSCN, NeuroCard) give point estimates but no certificates.

## 4. Upper Bound
The AGM bound is computable by solving a linear program over $|E|$ variables; it is a valid upper bound on $|Q(D)|$ in the **cardinality-statistics model**. The polymatroid/degree bound is an LP/relaxation over $O(2^{|V|})$ constraints, polynomial when the number of degree constraints is fixed; SafeBound achieves near-linear preprocessing in data size and per-query cost polynomial in query size, with the certified guarantee $|Q(D)| \le \widehat{B}$.

## 5. Lower Bound
Worst-case *tightness* is a lower bound on looseness: for AGM, instances exist where $|Q(D)| = \Theta(\prod |R_e|^{x_e})$, so no cardinality-only bound can beat $\rho^*$. Computing the *entropic* bound exactly is tied to the (non-)characterization of entropic functions — the cone $\overline{\Gamma^*_n}$ is not polyhedral for $n \ge 4$ (Zhang–Yeung), making the truly tightest information-theoretic bound non-LP-expressible. Evaluating $|Q(D)|$ exactly is #P-hard for general CQs; deciding emptiness is NP-hard for unbounded queries.

## 6. The Gap
For worst-case bounds over a *fixed* statistics class, AGM and polymatroid bounds are essentially closed (tight). The genuine gap is the **worst-case-vs-actual** gap: on real, skewed-but-not-adversarial data the certified bound can overshoot the true cardinality by orders of magnitude. Closing it requires statistics that constrain the instance toward realism (correlations, multi-column degrees) without exploding the constraint budget, and a bound that is the *tightest entropic* one — currently uncomputable exactly. Whether a polynomially-representable bound can approximate the entropic bound within a fixed factor is open.

## 7. Current Research (as of June 2026)
Active directions: (i) **certified yet tight** estimators that combine degree sequences with sampling residuals (SafeBound line, UW Database group — Suciu, Deeds); (ii) **entropic-bound approximation** and the algebra of information-theoretic inequalities (Abo Khamis, Ngo, Suciu) *(frontier — verify)*; (iii) bridging learned point estimates with bound certificates so optimizers get both a guess and a guarantee. There is renewed interest in connecting AGM tightness to **worst-case-optimal join** runtime, since the bound governs intermediate-result blowup.

## 8. Future Work
Tractable approximations of the entropic bound; data-dependent statistics that provably shrink the worst-case envelope toward observed cardinalities; bounds that compose across query plans (linking to error-propagation work); incremental maintenance of certified statistics under updates; and integrating certified bounds into cost-based optimization with regret guarantees.

## 9. Key References
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008.
- **[Foundational]** Gottlob, Lee, Valiant, Valiant. *Size and Treewidth Bounds for Conjunctive Queries.* JACM, 2012.
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* PODS, 2017.
- **[SOTA]** Cai, Balazinska, Suciu. *Pessimistic Cardinality Estimation: Tighter Upper Bounds for Intermediate Join Cardinalities.* SIGMOD, 2019.
- **[SOTA]** Deeds, Suciu, Balazinska, et al. *SafeBound: A Practical System for Generating Cardinality Bounds.* SIGMOD, 2023.
- **[Survey]** Ngo. *Worst-Case Optimal Join Algorithms: Techniques, Results, and Open Problems.* PODS, 2018.

---
*Part of the [DBMS Research catalog](../../README.md).*
