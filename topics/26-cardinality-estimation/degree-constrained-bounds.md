# Worst-Case-Optimal Bounds with Degree Constraints

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/degree-constrained-bounds` · **Status:** partially-solved

## 1. Problem Statement
The AGM bound uses only relation cardinalities. Real schemas carry much richer structure: **functional dependencies (FDs)**, **degree constraints** ("each customer has at most 5 addresses"), **frequency/skew profiles**, and **primary-key/foreign-key** relationships. The problem: derive the tightest valid upper bound on conjunctive-query output cardinality given such **degree and dependency constraints**, and turn it into worst-case-optimal join *algorithms* whose runtime matches the bound. Variants: the **bound** variant (compute the tightest certified size), the **algorithmic** variant (a join algorithm running in time $\tilde{O}(\text{bound} + \text{output})$), and the **counting** variant. Because the bound can be far below AGM, this directly attacks intermediate-result blowup.

## 2. Mathematical Foundations
A **degree constraint** is $(X, Y, N_{Y|X})$ asserting $\deg(Y \mid x) = |\pi_Y(\sigma_{X=x} R)| \le N_{Y|X}$ for all $x$; cardinality constraints ($X=\emptyset$) and FDs ($N_{Y|X}=1$) are special cases. The tightest bound expressible from such constraints is the **polymatroid bound**:
$$ \log |Q(D)| \;\le\; \max_{h \in \Gamma_n}\; h(V) \quad \text{s.t.}\quad h(XY) - h(X) \le \log N_{Y|X}\ \forall\,\text{constraints}, $$
where $\Gamma_n$ is the cone of polymatroids (monotone, submodular, $h(\emptyset)=0$). Restricting to **modular/Shannon** functions recovers cardinality (AGM) bounds; using the **entropic** cone $\overline{\Gamma^*_n}$ gives the true information-theoretic optimum. The dual/primal of this LP yields a **proof sequence** (a Shannon-inequality derivation) that the **PANDA** algorithm turns into a query plan. The **submodular width** $\mathsf{subw}(Q)$ characterizes the optimal exponent for bounded-arity queries.

## 3. State of the Art (SOTA)
**Theory-SOTA:** The **degree-constrained / polymatroid bound** and its tight algorithmic realization — **PANDA** (Abo Khamis, Ngo, Suciu, PODS 2017, and refinements) — give worst-case-optimal algorithms whose runtime matches the polymatroid bound up to polylog factors, generalizing **Generic Join / Leapfrog Triejoin** (Ngo–Porat–Ré–Rudra; Veldhuizen) from the AGM regime. The **degree-aware** framework (Joglekar–Ré; Abo Khamis et al.) handles skew explicitly. Recent work tightens bounds with **simple degree constraints** and gives closed-form / efficiently-computable bounds for many practical cases. **Systems-SOTA:** worst-case-optimal joins ship in systems like **Umbra/TUM**, **RelationalAI**, and graph engines; degree-bound-based pessimistic estimators (SafeBound) use degree sequences for certified cardinality bounds in cost-based optimizers.

## 4. Upper Bound
For a query with degree constraints, PANDA computes $Q(D)$ in time $\tilde{O}(\,2^{\text{poly}(|Q|)} \cdot \text{PolyBound} + |\text{output}|\,)$ in the RAM model, where PolyBound is the polymatroid-LP value — i.e., **worst-case optimal** up to factors depending only on query size. For acyclic and bounded-(submodular-)width queries the exponent is $\mathsf{subw}(Q)$. The bound itself is an LP over $O(2^n)$ variables with the constraint set; solvable in time polynomial in its (exponential-in-$n$) size, hence efficient for fixed query width.

## 5. Lower Bound
The polymatroid bound is **worst-case tight** for the constraint class: instances realize it up to constants, so no algorithm reading the input can beat $\mathsf{subw}(Q)$ in the worst case for that width class. The truly tightest bound (entropic) is **not LP-computable in general** — $\overline{\Gamma^*_n}$ is non-polyhedral for $n \ge 4$ (Zhang–Yeung), and there exist constraint sets where the polymatroid bound strictly exceeds the entropic bound, so polymatroid bounds are *not* always tight against the information-theoretic optimum. Exact counting under these constraints is #P-hard.

## 6. The Gap
Partially closed. For **cardinality + simple degree constraints**, bound and algorithm match (closed). The residual gap: (i) the **polymatroid–entropic gap**, where a non-polyhedral set of inequalities is needed and no efficient exact procedure is known; (ii) **practical tightness**, since worst-case-optimal bounds still overshoot real cardinalities (links to AGM-tightness problem); (iii) extending tight algorithms to richer constraints (general FDs, conditional independencies, inequality/arithmetic constraints). Whether the entropic bound is computable or approximable in polynomial time is a central open question.

## 7. Current Research (as of June 2026)
Active: (i) **practical PANDA-style optimization** and its integration into real engines, balancing the large query-size constants against intermediate-result savings *(frontier — verify)*; (ii) bounds and WCOJ algorithms under **conditional independence / FD-rich** schemas (Suciu, Ngo, Abo Khamis); (iii) connecting degree-constrained bounds to **certified cardinality estimation** (SafeBound) for optimizers; (iv) the algebra of information inequalities and partial progress toward computing/approximating entropic bounds. Centers: UW (Suciu), RelationalAI (Abo Khamis, Ngo), TUM, EPFL.

## 8. Future Work
Efficient approximation of the entropic bound; tight algorithms under general FDs and conditional independencies; reducing the query-size constants of PANDA to make it default-on in optimizers; data-adaptive degree statistics that shrink worst-case bounds toward observed sizes; and unifying degree-constrained bounds with learned point estimates.

## 9. Key References
- **[Foundational]** Atserias, Grohe, Marx. *Size Bounds and Query Plans for Relational Joins.* FOCS, 2008. — [arXiv](https://arxiv.org/abs/1711.03860)
- **[Foundational]** Ngo, Porat, Ré, Rudra. *Worst-Case Optimal Join Algorithms.* PODS, 2012 / JACM, 2018. — [arXiv](https://arxiv.org/abs/1203.1952)
- **[SOTA]** Abo Khamis, Ngo, Suciu. *Computing Join Queries with Functional Dependencies (PANDA).* PODS, 2016/2017. — [arXiv](https://arxiv.org/abs/1604.00111)
- **[SOTA]** Gottlob, Lee, Valiant, Valiant. *Size and Treewidth Bounds for Conjunctive Queries.* JACM, 2012. — [DOI](https://doi.org/10.1145/2220357.2220363)
- **[SOTA]** Joglekar, Ré. *It's All a Matter of Degree: Using Degree Information to Optimize Multiway Joins.* ICDT, 2016. — [arXiv](https://arxiv.org/abs/1508.01239)
- **[Survey]** Ngo, Ré, Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013. — [arXiv](https://arxiv.org/abs/1310.3314)

## 10. Worked Example

Take the triangle $Q = R(A,B) \bowtie S(B,C) \bowtie T(A,C)$ with $|R|=|S|=|T|=N$. Plain AGM gives $|Q| \le N^{3/2}$.

Now add one **degree constraint**: in $R$, each $A$-value has at most one $B$-value — i.e. $A \to B$ (an FD, $N_{B|A}=1$). Intuitively $R$ is now a *function* from $A$ to $B$, so $|R| \le |\pi_A R| \le N$ but each $a$ pins down $b$.

The polymatroid LP solves $\max h(ABC)$ subject to $h(AB) \le \log N$, $h(BC) \le \log N$, $h(AC) \le \log N$, and the FD $h(AB) = h(A)$ (knowing $A$ determines $B$, so no extra entropy). With the FD, $h(ABC) = h(AC)$ because $B$ is a function of $A$. Hence
$$\log|Q| \le h(AC) \le \log N \;\Rightarrow\; |Q| \le N.$$

So the FD collapses the bound from $N^{3/2}$ to $N$ — for $N = 10^6$ that is $10^9 \to 10^6$, a $1000\times$ reduction in the certified intermediate-size guarantee. PANDA turns the LP's dual (the Shannon-inequality proof sequence) into a plan that computes $Q$ in $\tilde O(N)$ time, matching the bound. This is precisely how degree/FD information beats vanilla AGM.

---
*Part of the [DBMS Research catalog](../../README.md).*
