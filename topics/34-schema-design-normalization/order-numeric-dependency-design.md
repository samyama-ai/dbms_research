# Numeric and Order/Differential Dependency Design

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/order-numeric-dependency-design` · **Status:** open

## 1. Problem Statement
Beyond equality-based FDs, real data carries **order dependencies (ODs)** ("if rows are sorted by tax bracket they are sorted by tax amount"), **numeric/aggregation constraints**, and **differential dependencies (DDs)** ("if two products' release dates differ by ≤ 7 days, their prices differ by ≤ \$5"). These capture monotonicity, tolerance, and metric structure that equality FDs cannot, and they are directly exploitable for both *logical* design (integrity, redundancy) and *physical* design (sort orders, range partitioning, index selection, query optimization via order propagation).

The problem: **discover order/numeric/differential dependencies from data, and exploit them for schema and physical design.** Subproblems:
- **Discovery (enumeration):** Find all minimal valid ODs / DDs / numeric dependencies in an instance.
- **Inference (decision):** Decide implication among ODs/DDs (needed for minimal covers and design reasoning).
- **Design (optimization):** Use them to choose sort keys, interesting orders, partition boundaries, and to detect redundancy a metric/order view exposes.

## 2. Mathematical Foundations
**Order dependency** $X \mapsto Y$ ("X orders Y") holds in relation $r$ if for all tuples $s,t$: $s \preceq_X t \Rightarrow s \preceq_Y t$, where $\preceq_X$ is lexicographic order on list $X$. ODs strictly generalize FDs ($X \to Y \equiv XY \mapsto X$ flavor relationships) and form a richer **axiom system**; their canonical form uses *order-compatibility* and *set-based* ODs (Szlichta et al.) to tame the lexicographic blowup. **Differential dependency** $X \to_\phi Y$ (Song & Chen) with distance constraints $\phi$ requires: for all $s,t$, if distances on $X$ satisfy $\phi_X$ then distances on $Y$ satisfy $\phi_Y$:
$$\forall s,t:\ d_X(s,t)\models \phi_X \ \Rightarrow\ d_Y(s,t)\models \phi_Y.$$
**Metric FDs** (Koudas et al.) are the special case $\phi_X$ = equality, $\phi_Y$ = bounded distance. Discovery is again an **evidence-set / lattice-search** problem, but over ordered/metric predicate spaces; OD implication has a sound-and-complete axiomatization and its decision problem is **coNP-complete** in general (Szlichta, Godfrey, Gryz).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Ginsburg & Hull introduced order dependencies (1983–86). **Szlichta, Godfrey, Gryz** (*Fundamentals of Order Dependencies*, PVLDB 2012; TODS) gave the modern axiomatization, set-based canonical forms, and the coNP-completeness of OD implication. **Song & Chen** (*Differential Dependencies*, TODS 2011) defined DDs and their inference. **Koudas et al.** defined metric FDs (ICDE 2009).
- **Systems-SOTA (discovery):** **FASTOD / OCDDISCOVER** and the set-based **DISTOD** (Schmidl & Papenbrock, 2022) discover ODs at scale; differential-dependency discovery tools exist but are less mature. ODs are used in **query optimization** (DB2's order-property propagation; "interesting orders" à la Selinger) — the strongest current *design* payoff.

## 4. Upper Bound
Set-based OD discovery (FASTOD, DISTOD) runs in time **exponential in the number of attributes** but polynomial in rows, with strong lattice-pruning making it practical for dozens of columns; building per-pair evidence costs up to $O(n^2)$ but sorting-based techniques reduce this for many OD shapes (model: RAM). OD implication checking is in **coNP** (a polynomial-size counterexample over $\le$ a few tuples can be guessed and verified). DD discovery is similarly $O(2^{|attrs|}\cdot\text{poly}(n))$ with metric-index pruning. No subexponential-in-attributes exact discovery is known.

## 5. Lower Bound
- **OD implication is coNP-complete** (Szlichta–Godfrey–Gryz; model: classical complexity) — strictly harder than the linear-time FD implication of Beeri–Bernstein. This makes minimal-cover computation for ODs intractable in the worst case.
- **DD implication** is likewise intractable; consistency of distance constraints embeds metric/interval reasoning.
- Discovery output can be **exponential in attribute count**, so polynomiality in input alone is impossible (enumeration lower bound). Pairwise evidence construction has an $\Omega(n^2)$ barrier in the worst case (model: RAM).

## 6. The Gap
Discovery is *partially solved* (FASTOD/DISTOD scale to realistic widths), but design exploitation is *open*. Three gaps: (1) the **coNP-completeness of OD inference** blocks efficient minimal-cover/design reasoning — no good approximation or fixed-parameter result is established for the design use-case; (2) there is **no normalization theory** that uses ODs/DDs to certify and remove redundancy analogous to BCNF — ODs reveal redundancy (e.g., derivable sorted columns) that FD-based design misses; (3) **physical-design integration** (auto-choosing sort keys, range partitions, interesting orders from discovered ODs) is largely manual/heuristic with no optimality guarantees. Closing requires both tractable design-oriented inference (or proof of hardness with approximations) and an OD/DD-aware decomposition theory.

## 7. Current Research (as of June 2026)
Active: **HPI (Papenbrock, Schmidl)** on scalable OD discovery (DISTOD) and unified profiling; **York University (Szlichta, Godfrey, Gryz)** on OD theory and optimizer integration; **Tsinghua (Song)** on differential/metric dependencies for cleaning. Emerging directions unify ODs/DDs with **denial-constraint** predicate spaces, push discovery onto **streaming and approximate** settings, and explore **learned/optimizer-in-the-loop** use of ODs to pick interesting orders and range partitions *(frontier — verify)*. Differential-dependency-driven *physical* design is an open, thinly populated frontier.

## 8. Future Work
- A normalization/decomposition theory certifying redundancy removal under ODs/DDs.
- Tractable or fixed-parameter algorithms for design-relevant OD/DD inference, or sharper hardness with approximation guarantees.
- Automated physical design (sort keys, range partitioning, interesting orders) driven by discovered ODs, with cost-model guarantees.
- Robust approximate OD/DD discovery on dirty data with statistical confidence.

## 9. Key References
- **[Foundational]** J. Szlichta, P. Godfrey, J. Gryz. *Fundamentals of Order Dependencies.* PVLDB, 2012 (and ACM TODS). — [DOI](https://doi.org/10.14778/2350229.2350241) — [arXiv](https://arxiv.org/abs/1208.0084)
- **[Foundational]** S. Song, L. Chen. *Differential Dependencies: Reasoning and Discovery.* ACM TODS, 2011. — [DOI](https://doi.org/10.1145/2000824.2000826)
- **[Foundational]** N. Koudas, A. Saha, D. Srivastava, S. Venkatasubramanian. *Metric Functional Dependencies.* ICDE, 2009. — [DOI](https://doi.org/10.1109/ICDE.2009.219)
- **[SOTA]** S. Schmidl, T. Papenbrock. *Efficient Distributed Discovery of Bidirectional Order Dependencies (DISTOD).* VLDB Journal, 2022. — [DOI](https://doi.org/10.1007/s00778-021-00683-4)
- **[Foundational]** S. Ginsburg, R. Hull. *Order Dependency in the Relational Model.* Theoretical Computer Science, 1983. — [DOI](https://doi.org/10.1016/0304-3975(83)90084-1)
- **[Survey]** Z. Abedjan, L. Golab, F. Naumann, T. Papenbrock. *Data Profiling.* Morgan & Claypool, 2018. — [DOI](https://doi.org/10.2200/S00878ED1V01Y201810DTM052)

## 10. Worked Example

Take a tiny `Tax` relation, attributes $\text{Income}$ and $\text{Tax}$:

| Income | Tax  |
|--------|------|
| 30000  | 3000 |
| 50000  | 6000 |
| 50000  | 6000 |
| 80000  | 12000 |

**Order dependency** $\text{Income}\mapsto\text{Tax}$: sort by Income $(30k,50k,50k,80k)$; the corresponding Tax list $(3000,6000,6000,12000)$ is non-decreasing, and ties on Income tie on Tax — so $s\preceq_{\text{Income}} t \Rightarrow s\preceq_{\text{Tax}} t$ holds. Note an FD $\text{Income}\to\text{Tax}$ *also* holds here, but the OD additionally certifies *monotonicity*, justifying a clustered index on Income that yields Tax already sorted (a free "interesting order").

**Differential dependency** with $\phi_X:\,|\Delta\text{Income}|\le 20000 \Rightarrow \phi_Y:\,|\Delta\text{Tax}|\le 6000$: check the pair $(30k,3000)$ vs $(50k,6000)$ — $\Delta\text{Income}=20000\le 20000$ and $\Delta\text{Tax}=3000\le 6000$, satisfied. But $(30k,3000)$ vs $(80k,12000)$ has $\Delta\text{Income}=50000>20000$, so the rule's antecedent is vacuously skipped. The DD holds on all $\binom{4}{2}=6$ pairs — but verifying it is inherently $\Omega(n^2)$ pairwise work, illustrating the lower bound.

---
*Part of the [DBMS Research catalog](../../README.md).*
