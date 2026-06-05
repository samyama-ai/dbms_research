# Tight Bounds for Conjunctive Query Cardinality

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/agm-bound-tightness` · **Status:** partially-solved
> **Verification note:** The Cai–Balazinska–Suciu pessimistic estimator cited in §3 appeared as "Pessimistic Cardinality Estimation" at SIGMOD 2019 (DOI 10.1145/3299869.3319894), not as "Cardinality Estimation Done Right" at CIDR 2019.

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
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008. — [DBLP](https://dblp.org/rec/conf/focs/AtseriasGM08.html), [arXiv](https://arxiv.org/abs/1711.03860)
- **[Foundational]** Gottlob, Lee, Valiant, Valiant. *Size and Treewidth Bounds for Conjunctive Queries.* JACM, 2012. — [DOI](https://doi.org/10.1145/2220357.2220363)
- **[SOTA]** Abo Khamis, Ngo, Suciu. *What Do Shannon-type Inequalities, Submodular Width, and Disjunctive Datalog Have to Do with One Another?* PODS, 2017. — [DOI](https://doi.org/10.1145/3034786.3056105), [arXiv](https://arxiv.org/abs/1612.02503)
- **[SOTA]** Cai, Balazinska, Suciu. *Pessimistic Cardinality Estimation: Tighter Upper Bounds for Intermediate Join Cardinalities.* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3319894)
- **[SOTA]** Deeds, Suciu, Balazinska, et al. *SafeBound: A Practical System for Generating Cardinality Bounds.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3588907), [arXiv](https://arxiv.org/abs/2211.09864)
- **[Survey]** Ngo. *Worst-Case Optimal Join Algorithms: Techniques, Results, and Open Problems.* PODS, 2018. — [DOI](https://doi.org/10.1145/3196959.3196990), [arXiv](https://arxiv.org/abs/1803.09930)

## 10. Worked Example

Consider the **triangle query** $Q = R(a,b) \bowtie S(b,c) \bowtie T(c,a)$ with $|R|=|S|=|T|=N$. The hypergraph has vertices $\{a,b,c\}$ and three edges, each covering two vertices. A fractional edge cover must satisfy, per vertex, $x_R+x_T\ge 1$ (covers $a$), $x_R+x_S\ge 1$ (covers $b$), $x_S+x_T\ge 1$ (covers $c$). Minimizing $\sum x_e$ gives the symmetric optimum $x_R=x_S=x_T=\tfrac12$, so $\rho^* = \tfrac32$.

The **AGM bound** is therefore
$$|Q(D)| \le |R|^{1/2}|S|^{1/2}|T|^{1/2} = N^{3/2}.$$

This is *worst-case tight*: take $R=S=T = [\sqrt N] \times [\sqrt N]$ (a full $\sqrt N \times \sqrt N$ grid of pairs). Each relation has $N$ tuples, and every triple $(a,b,c)\in[\sqrt N]^3$ satisfies all three relations, giving exactly $(\sqrt N)^3 = N^{3/2}$ output triangles — matching the bound.

Yet on a **sparse real graph** with $N$ edges and bounded degree $d$, the true triangle count is $O(Nd) = O(N)$, far below $N^{3/2}$. For $N=10^6,\ d=10$ the bound says $\le 10^9$ but the truth is $\approx 10^7$ — the §6 worst-case-vs-actual gap of two orders of magnitude.

---
*Part of the [DBMS Research catalog](../../README.md).*
