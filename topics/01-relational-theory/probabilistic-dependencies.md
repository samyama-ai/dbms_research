# Probabilistic Database Dependency Theory

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/probabilistic-dependencies` · **Status:** partially-solved

## 1. Problem Statement

Probabilistic databases (PDBs) represent uncertainty as a distribution over possible worlds. Classical dependency theory (FDs, MVDs, JDs, INDs) assumes a single deterministic instance. The problem is to **develop a dependency and implication theory for probabilistic and uncertain relational data**:

- What does it mean for an FD/MVD to *hold* in a PDB — in every world, in expectation, or approximately/probabilistically?
- **Implication:** Given probabilistic dependencies $\Sigma$, does $\sigma$ follow, and under which semantics?
- **Discovery / optimization:** Find dependencies that hold with high probability (soft/approximate FDs), and quantify "how functional" an FD is.
- **Counting:** Probability that a constraint holds = a weighted model-counting (#P) problem.

This is **partially solved**: solid foundations exist for soft/approximate FDs, conditional independence, and tuple-independent models, but a unified implication theory across the full dependency zoo remains incomplete.

## 2. Mathematical Foundations

A **PDB** is a distribution $P$ over a set $\mathcal{W}$ of possible worlds (deterministic instances). For tuple-independent databases (TIDBs), each tuple $t$ exists independently with probability $p_t$.

Semantics for an FD $X \to Y$:
- **Certain:** holds in *every* world with nonzero probability.
- **Possible:** holds in *some* world.
- **In-expectation / probabilistic:** $P[X\to Y \text{ holds}] \ge \tau$.
- **Approximate (soft FD):** measured by an error like $g_3$ (minimum fraction of tuples to delete to satisfy the FD) or by **conditional entropy** $H(Y\mid X)$; $X\to Y$ is "soft" when $H(Y\mid X)$ is small.

This ties probabilistic FDs to **information theory**: a deterministic FD means $H(Y\mid X)=0$. Multivalued dependencies correspond to **conditional independence**: $X \twoheadrightarrow Y$ iff $Y \perp Z \mid X$ (the graphical-models/Markov-network connection, Geiger–Pearl). Thus probabilistic dependency theory inherits the **axiomatization of conditional independence** (semi-graphoids) and its known **non-finite-axiomatizability** (Studený).

$$X \to Y \ (\text{exact}) \iff H(Y \mid X) = 0,\qquad X \twoheadrightarrow Y \iff I(Y;Z\mid X)=0.$$

## 3. State of the Art (SOTA)

**Theory-SOTA:**
- **Probabilistic / approximate FDs** with the $g_3$ measure and entropy-based scores are well established (Kivinen–Mannila 1995; Giannella–Robertson).
- **Conditional-independence ↔ EMVD** correspondence and the **non-finite-axiomatizability** of probabilistic CI (Studený 1992) is the deepest structural result.
- **PDB query semantics** (Suciu, Olteanu, Ré, Koch) — possible worlds, lineage, dichotomy theorems for query evaluation (Dalvi–Suciu) — provide the model in which dependency probabilities live.

**Systems-SOTA:**
- **Soft/approximate FD discovery** in data cleaning: **HoloClean** (Rekatsinas et al., VLDB 2017) uses probabilistic dependencies (denial constraints) for repair; **Metanome**/**pyro** discover approximate FDs at scale.
- **MystiQ**, **MayBMS**, **ProbLog/DeepProbLog**, and modern **probabilistic programming** systems operationalize possible-world reasoning.

## 4. Upper Bound

- Checking whether an FD holds in **expectation** / with probability $\ge\tau$ in a TIDB reduces to **weighted model counting**; tractable for hierarchical/safe queries (PTIME) via the Dalvi–Suciu dichotomy.
- Computing the $g_3$ approximate-FD error is **polynomial** for a fixed FD on a deterministic instance.
- Discovering all approximate FDs above a threshold is exponential in attributes but has effective pruning (TANE-style, lattice search).

## 5. Lower Bound

- **Probability that an FD holds** in a general PDB is **#P-hard** (it is a model-counting problem; reduces from #SAT / unsafe conjunctive-query evaluation, Dalvi–Suciu dichotomy giving #P-hardness for non-hierarchical cases).
- **Implication for probabilistic conditional independence (≈ probabilistic MVDs)** has **no finite complete axiomatization** (Studený 1992) — a definitive structural lower bound.
- General CI implication is **undecidable** in some formulations / not known to be elementary; the "stable" semi-graphoid theory is incomplete for the probabilistic case.

## 6. The Gap

Foundations are partly solved (soft FDs, the CI–MVD bridge, query-side dichotomies), but **no unified implication theory** spans FDs, MVDs, INDs, and JDs under probabilistic semantics with matching algorithms. Key gaps: (a) the divergence between "holds in expectation," "holds with probability $\ge \tau$," and "approximately holds" has no clean unifying calculus; (b) implication is variously #P-hard, non-axiomatizable, or open depending on the dependency and semantics; (c) the relationship between information-theoretic measures and a *decidable* implication system is not closed. What would close it: a semantics with a sound/complete (possibly infinite but recursive) inference system plus tight complexity per fragment.

## 7. Current Research (as of June 2026)

- **Information-theoretic / entropic dependency reasoning**: using Shannon-inequality LPs to bound and reason about soft dependencies and cardinalities (Khamis–Ngo–Suciu lineage) *(frontier — verify)*.
- **Probabilistic constraints for data cleaning & ML data quality**: extending HoloClean-style denial-constraint repair with learned probabilistic FDs *(frontier — verify)*.
- **Causal/CI dependency theory** feeding back into databases via the graphical-models connection.
- Dependencies over **probabilistic and semantic embeddings** / vector data, an emerging direction *(frontier — verify)*.

## 8. Future Work

- A unified, decidable implication system for probabilistic FD/MVD/IND with tight complexity.
- Robust **approximate-dependency** measures with statistical guarantees on finite samples (VC-dimension / PAC-style bounds).
- Normalization theory for PDBs (what does BCNF/4NF mean when dependencies are soft).
- Scalable discovery of probabilistic dependencies integrated with query optimization and repair.

## 9. Key References

- **[Foundational]** Studený, M. *Conditional Independence Relations Have No Finite Complete Characterization.* Trans. 11th Prague Conf., 1992. — [PDF](https://staff.utia.cas.cz/studeny/FTP/ci-no-axiom-92.pdf)
- **[Foundational]** Kivinen, J., Mannila, H. *Approximate Inference of Functional Dependencies from Relations.* Theoretical Computer Science, 1995. — [DOI](https://doi.org/10.1016/0304-3975(95)00028-U)
- **[Foundational]** Dalvi, N., Suciu, D. *The Dichotomy of Probabilistic Inference for Unions of Conjunctive Queries.* J. ACM, 2012. — [DOI](https://doi.org/10.1145/2395116.2395119)
- **[Survey]** Suciu, D., Olteanu, D., Ré, C., Koch, C. *Probabilistic Databases.* Morgan & Claypool, 2011. — [DOI](https://doi.org/10.1007/978-3-031-01879-4)
- **[SOTA]** Rekatsinas, T., Chu, X., Ilyas, I., Ré, C. *HoloClean: Holistic Data Repairs with Probabilistic Inference.* PVLDB, 2017. — [DOI](https://doi.org/10.14778/3137628.3137631)
- **[SOTA]** Geiger, D., Pearl, J. *Logical and Algorithmic Properties of Conditional Independence and Graphical Models.* Annals of Statistics, 1993. — [DOI](https://doi.org/10.1214/aos/1176349407)

## 10. Worked Example

Consider a TIDB over $R(\text{Zip}, \text{City})$ testing the FD $\text{Zip}\to\text{City}$. Three independent tuples:

| tuple | Zip | City | $p_t$ |
|---|---|---|---|
| $t_1$ | 02139 | Cambridge | 0.9 |
| $t_2$ | 02139 | Somerville | 0.4 |
| $t_3$ | 90001 | LA | 1.0 |

The FD is *violated* in a world iff both $t_1$ and $t_2$ are present (same Zip, different City); $t_3$ never conflicts. So
$$P[\text{FD holds}] = 1 - P[t_1\wedge t_2] = 1 - (0.9)(0.4) = 0.64.$$
Thus the FD holds with probability $0.64$ — it passes a threshold $\tau=0.6$ but fails $\tau=0.7$.

Approximate ($g_3$) view on the most-likely world $\{t_1,t_3\}$ (drop $t_2$, $p<0.5$): the FD holds exactly, $g_3=0$. But in the world $\{t_1,t_2,t_3\}$ we must delete 1 of 3 tuples to satisfy it, so $g_3 = 1/3 \approx 0.33$. The single PDB yields *different* verdicts under "in-expectation" ($0.64$), "certain" (fails), and "approximate" ($g_3$) semantics — illustrating the section-6 gap that these notions lack a unifying calculus.

---
*Part of the [DBMS Research catalog](../../README.md).*
