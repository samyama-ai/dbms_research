# Denial-Constraint Discovery at Scale

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/denial-constraint-discovery` · **Status:** partially-solved

## 1. Problem Statement

A *denial constraint* (DC) over relation $R$ is a first-order sentence
$\varphi : \forall t_\alpha, t_\beta \in R,\ \neg(p_1 \wedge \dots \wedge p_m)$
where each predicate $p_i$ has the form $t_\alpha.A_i\ \theta\ t_\beta.A_j$ (or a constant comparison) with $\theta \in \{=,\neq,<,\le,>,\ge\}$. DCs subsume functional dependencies (FDs), order dependencies, and conditional FDs.

**Discovery problem.** Given an instance $r$ of $R$, output the set of *minimal* DCs that hold (exact discovery) or *approximately hold* (approximate discovery, allowing a fraction $\epsilon$ of violating tuple pairs). Variants:
- **Decision:** does DC $\varphi$ hold on $r$ (up to $\epsilon$)?
- **Enumeration:** list all minimal valid DCs.
- **Optimization/counting:** find top-$k$ DCs by an interestingness/coverage score; count satisfying pairs.

The challenge: the predicate space and the search lattice are huge, the data is dirty (so exact DCs are rare and useless — approximate DCs are needed), and instances reach $10^7$–$10^9$ rows.

## 2. Mathematical Foundations

Let $P$ be the set of admissible predicates; $|P|$ is $O(\text{cols}^2 \cdot |\Theta|)$. A DC is an antimonotone element of the lattice $2^P$: if a predicate set is non-violated (a valid DC), no superset is *minimal*. Discovery reduces to computing the **evidence set** — for each tuple pair $(t_\alpha,t_\beta)$, the maximal satisfied predicate set $\mathit{ev}(t_\alpha,t_\beta) \subseteq P$ — and then finding minimal *hitting sets* of the complements. A DC $\neg(X)$ is valid iff $X$ is **not** a subset of any evidence; equivalently the valid minimal DCs are the minimal transversals of the evidence set, an instance of the **minimal hypergraph transversal / dualization** problem (Fredman–Khachiyan: solvable in quasi-polynomial output time).

Approximate validity uses the $g_1$ error metric: $g_1(\varphi,r) = \frac{|\{(t_\alpha,t_\beta): \text{violate } \varphi\}|}{|r|^2}$; $\varphi$ is $\epsilon$-approximate if $g_1 \le \epsilon$. Building the evidence set is the dominant cost: naively $\Theta(|r|^2 |P|)$ pair comparisons. Sampling-based estimators give PAC-style bounds: a sample of $O(\epsilon^{-2}\log(|P|/\delta))$ pairs estimates each predicate's violation rate within $\epsilon$ w.p. $1-\delta$ (Hoeffding + union bound), connecting to VC dimension of the predicate class.

## 3. State of the Art (SOTA)

- **FASTDC** (Chu, Ilyas, Papotti, *VLDB 2013*) — first general DC discovery via evidence sets + minimal-cover search; quadratic in tuples.
- **Hydra** (Bleifuß, Kruse, Naumann, *VLDB 2017*) — avoids materializing all pairs by sampling to build a *partial* evidence set, then refining with focused comparisons; orders-of-magnitude faster, the systems-SOTA for exact DCs.
- **DCFinder / dynamic position lists** and **ADCMiner** (Pena, de Almeida, Naumann, *VLDB 2019/2021*) — approximate DC discovery with $g_1$ guarantees and shipping/clue-based evidence aggregation.
- **DESBORDANTE** (2023–2024) — open-source platform consolidating DC/FD/AFD discovery at scale.
- Theory-SOTA for the transversal step remains Fredman–Khachiyan quasi-poly dualization; no truly output-polynomial algorithm is known.

## 4. Upper Bound

Evidence-set construction: $O(|r|^2 |P|)$ time, $O(|r| |P| + |\text{ev}|)$ space (Hydra reduces the constant and expected pairs sampled dramatically but worst case stays quadratic). The cover/transversal enumeration runs in **quasi-polynomial output-sensitive time** $N^{o(\log N)}$ where $N$ is input+output size (Fredman–Khachiyan). Approximate discovery with sampling achieves $g_1$ estimation in $O(\epsilon^{-2}\log(|P|/\delta))$ sampled pairs per predicate, i.e. sublinear in $|r|^2$, with PAC guarantees.

## 5. Lower Bound

- **Transversal hardness:** minimal-DC enumeration is at least as hard as monotone dualization; deciding whether a given collection is the *complete* set of minimal transversals is the canonical problem not known to be in P nor coNP-complete — a structural lower-bound barrier.
- **Counting:** counting violating pairs / satisfying assignments for general DC predicate conjunctions is **#P-hard** by reduction from counting in conjunctive queries with inequalities.
- **Fine-grained:** building the exact evidence set with arbitrary $\neq/<$ predicates inherits hardness from **(min,+)-style and 3SUM-hard** geometric comparison problems; no strongly subquadratic ($O(|r|^{2-\delta})$) exact algorithm is known, consistent with conditional 3SUM/OV lower bounds for pairwise-inequality detection.

## 6. The Gap

For *exact* discovery the gap is the quadratic evidence-set construction vs. the conjectured 3SUM/OV barrier — likely **closed up to subpolynomial factors** for worst-case adversarial data, but practically wide because real data is far from worst case (Hydra exploits this). For *approximate* discovery, sampling closes the time gap to sublinear, but the gap between $g_1$-validity on a sample and on the full instance leaves a tunable error–cost tradeoff that is *not* tight; no algorithm matches the information-theoretic sample-complexity lower bound for the full DC class. The enumeration/dualization gap (quasi-poly vs. poly) is **genuinely open**.

## 7. Current Research (as of June 2026)

- Learned/embedding-guided predicate-space pruning to cut $|P|$ before evidence construction *(frontier — verify)*.
- DC discovery over **streams and incremental updates** without recomputing evidence sets.
- Integrating discovery with repair (HoloClean-style) so discovered approximate DCs are weighted by repair utility, not just coverage (Ilyas, Chu; Waterloo).
- GPU/vectorized evidence-set builders in DESBORDANTE *(frontier — verify)*.
- Active groups: Naumann (HPI), Ilyas/Chu (Waterloo), Papotti (EURECOM), Abedjan (Leibniz Hannover).

## 8. Future Work

- Truly output-polynomial DC enumeration (the dualization barrier).
- Subquadratic exact evidence sets under realistic data models, or matching fine-grained lower bounds.
- Robust interestingness measures so discovered DCs are *semantically* meaningful, not spurious.
- Discovery jointly over multiple relations (denial constraints with joins) and with privacy/DP guarantees.

## 9. Key References

- **[Foundational]** Chu, Ilyas, Papotti. *Discovering Denial Constraints.* PVLDB, 2013. — [DOI](https://dl.acm.org/doi/10.14778/2536258.2536262)
- **[SOTA]** Bleifuß, Kruse, Naumann. *Efficient Denial Constraint Discovery with Hydra.* PVLDB, 2017. — [DOI](https://dl.acm.org/doi/10.14778/3157794.3157800)
- **[SOTA]** Pena, de Almeida, Naumann. *Discovery of Approximate (and Exact) Denial Constraints.* PVLDB, 2019/2021. — [DOI](https://dl.acm.org/doi/10.14778/3368289.3368293)
- **[Foundational]** Fredman, Khachiyan. *On the Complexity of Dualization of Monotone Disjunctive Normal Forms.* J. Algorithms, 1996. — [DOI](https://doi.org/10.1006/jagm.1996.0062)
- **[Survey]** Abedjan, Golab, Naumann, Papenbrock. *Data Profiling.* Synthesis Lectures / VLDB tutorials, 2018. — [DOI](https://doi.org/10.1007/978-3-031-01865-7)
- **[SOTA]** Chernishev et al. *Desbordante: Data Profiling Toolkit.* 2023–2024. — [arXiv](https://arxiv.org/abs/2301.05965)

## 10. Worked Example

Take a 3-row salary table $R(\text{Emp}, \text{Role}, \text{Sal})$:

| t | Role | Sal |
|---|------|-----|
| $t_1$ | Mgr | 90 |
| $t_2$ | Eng | 70 |
| $t_3$ | Eng | 70 |

Candidate DC: $\varphi : \neg(t_\alpha.\text{Role}=t_\beta.\text{Role} \wedge t_\alpha.\text{Sal}\neq t_\beta.\text{Sal})$ — "same role $\Rightarrow$ same salary."

Build evidence sets over ordered pairs. Predicates: $p_= : \text{Role}{=}$, $p_{\neq}:\text{Sal}{\neq}$. Pair $(t_2,t_3)$: roles equal, salaries equal $\Rightarrow$ satisfies $p_=$ but **not** $p_{\neq}$, so $\{p_=, p_{\neq}\}$ is not a subset of its evidence. Pair $(t_1,t_2)$: roles differ, so $p_=$ fails. No pair satisfies *both* $p_=$ and $p_{\neq}$, so $\varphi$ holds exactly: $g_1=0/9=0$.

Now add $t_4(\text{Eng}, 80)$. Pair $(t_2,t_4)$ has equal role, unequal salary $\Rightarrow$ violates $\varphi$. With $|r|=4$, $g_1 = 2/16 = 0.125$ (pairs $(t_2,t_4),(t_3,t_4)$). If $\epsilon=0.1$, $\varphi$ is rejected; raising $\epsilon$ to $0.15$ admits it as approximate.

---
*Part of the [DBMS Research catalog](../../README.md).*
