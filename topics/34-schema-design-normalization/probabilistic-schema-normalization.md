# Normalization Under Probabilistic and Uncertain Data

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/probabilistic-schema-normalization` · **Status:** open

## 1. Problem Statement
Probabilistic databases represent uncertainty as a distribution over possible worlds. In such data, a functional dependency rarely holds in *all* worlds; instead it holds with some probability, or holds approximately. Classical normalization theory (lossless join, dependency preservation, BCNF/4NF redundancy elimination) is defined over a single deterministic instance and breaks down: a decomposition that is lossless in every world may differ in correlation structure, and "redundancy" must be redefined in terms of information leakage between attributes.

The problem: **define normal-form theory and decomposition for relations whose dependencies hold only probabilistically**, such that decomposition (a) preserves the possible-worlds distribution (a *lossless* probabilistic join), (b) eliminates probabilistically-quantified redundancy, and (c) is computable.

Variants:
- **Decision:** Given a probabilistic relation and a set of probabilistic FDs (pFDs) with thresholds, is the schema in *probabilistic BCNF*?
- **Optimization:** Find a decomposition minimizing expected redundancy / mutual information subject to a lossless-join guarantee.
- **Counting/inference:** Compute the probability that a given FD holds, or the marginal correctness of a decomposed query.

## 2. Mathematical Foundations
A **probabilistic database** is a distribution $P$ over deterministic instances (possible worlds) $W_1,\dots,W_n$. A **probabilistic FD** $X \to_p Y$ holds at confidence $\theta$ if $\Pr_{W \sim P}[W \models X \to Y] \ge \theta$, or alternatively measures per-instance violation rate aggregated over worlds. The natural redundancy notion is **information-theoretic**: attribute $A$ is redundant if its conditional entropy given the rest is zero, $H(A \mid R \setminus A) = 0$; under uncertainty one instead bounds the **mutual information** $I(X;Y)$ that survives in a fragment, generalizing the Arenas–Libkin measure.

Lossless join becomes distributional: a decomposition $\{R_1,R_2\}$ is *probabilistically lossless* if $R = R_1 \bowtie R_2$ holds **as a distribution**, i.e. the joined result reproduces $P$ — which requires conditional independence $X \perp\!\!\!\perp (R\setminus XY) \mid Y$ exactly as in a graphical-model (Markov) factorization. Thus probabilistic normalization is closely tied to **Markov / Bayesian network factorization** and the chase over c-tables / pc-tables. $$R = R_1 \bowtie R_2 \text{ (as distributions)} \iff (R\setminus Y) \perp\!\!\!\perp \text{(across the split)} \mid Y.$$ Query evaluation over the result is governed by the **dichotomy theorem** (Dalvi–Suciu): a query is either PTIME or #P-hard over tuple-independent databases.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Foundations of probabilistic databases (Suciu, Olteanu, Ré, Koch — *Probabilistic Databases*, Morgan & Claypool 2011) give possible-worlds semantics, c-/pc-tables, and the #P/PTIME dichotomy, but **do not develop a normalization theory**. Wang, Dong, Fu et al. and Sismanis-style work on *approximate FDs* (CORDS, AFDs) supply probabilistic dependency discovery, not normal forms.
- **Systems-SOTA:** No production probabilistic DBMS performs probabilistic normalization; MystiQ, Trio, MayBMS, and Orion are research prototypes focused on query evaluation, not schema design. Probabilistic graphical-model factorization (e.g., factorized databases, FDB / Olteanu) is the closest systems analog and gives lossless distributional decomposition.

## 4. Upper Bound
Discovering pFDs / approximate FDs above a confidence threshold is solvable by adapting deterministic FD-discovery (TANE-style lattice search) with entropy/g3-error pruning, in time exponential in attribute count but polynomial in rows — i.e. $O(2^{|attrs|}\cdot \text{poly}(n))$ (model: RAM). Testing whether a candidate decomposition is *distributionally lossless* reduces to a conditional-independence test, computable in PTIME under tuple-independence but **#P-hard** under correlations expressed by general pc-tables. There is no known polynomial algorithm for optimal redundancy-minimizing probabilistic decomposition.

## 5. Lower Bound
Two hardness sources: (1) exact evaluation/inference of the joined or decomposed query is **#P-hard** for non-hierarchical conjunctive queries over probabilistic data (Dalvi–Suciu dichotomy — model: counting/#P). (2) Finding a minimum-redundancy decomposition inherits **NP-hardness** from deterministic dependency-preserving BCNF (Beeri–Bernstein 1979). Verifying exact conditional independence over arbitrary correlated representations is intractable, mirroring the hardness of learning Bayesian-network structure (NP-hard, Chickering 1996; model: NP).

## 6. The Gap
This is a *largely undeveloped* area, so the gap is definitional as much as quantitative. There is no agreed definition of probabilistic-BCNF, no redundancy theorem analogous to Arenas–Libkin's, and no synthesis algorithm with guarantees. The connection to graphical-model factorization suggests the "right" lossless criterion (conditional independence), but reconciling that with *syntactic* dependency preservation and *thresholded* pFDs is open. Closing it needs (i) an information-theoretic redundancy measure validated on possible-worlds semantics and (ii) a tractable-vs-#P-hard dichotomy for the resulting decomposition decision.

## 7. Current Research (as of June 2026)
Active directions: bridging **factorized databases / FDB** (Olteanu, Schleich) with normalization, since factorization *is* lossless distributional decomposition; entropy-based **approximate and conditional FD discovery** robust to noise (Naumann's HPI group, Kruse); and probabilistic-constraint repair for data cleaning (Ilyas, Chu). A plausible 2025–2026 frontier links **learned probabilistic dependency discovery to schema design under data uncertainty**, e.g. using neural density estimators to test conditional independence at scale *(frontier — verify)*. No consensus normal-form definition has yet emerged.

## 8. Future Work
- A possible-worlds-correct definition of probabilistic BCNF/4NF and an accompanying redundancy theorem.
- A PTIME-vs-#P dichotomy for deciding probabilistic-lossless decomposition.
- Synthesis algorithms minimizing expected mutual-information redundancy with provable bounds.
- Unifying pFD-thresholded design with graphical-model factorization and with denial-constraint repair.

## 9. Key References
- **[Foundational]** D. Suciu, D. Olteanu, C. Ré, C. Koch. *Probabilistic Databases.* Morgan & Claypool, 2011.
- **[Foundational]** N. Dalvi, D. Suciu. *Efficient Query Evaluation on Probabilistic Databases.* VLDB Journal, 2007.
- **[Foundational]** M. Arenas, L. Libkin. *An Information-Theoretic Approach to Normal Forms for Relational and XML Data.* JACM, 2005.
- **[SOTA]** D. Olteanu, M. Schleich. *Factorized Databases.* ACM SIGMOD Record, 2016.
- **[Foundational]** I. F. Ilyas, V. Markl, P. Haas, P. Brown, A. Aboulnaga. *CORDS: Automatic Discovery of Correlations and Soft Functional Dependencies.* SIGMOD, 2004.
- **[Survey]** T. Papenbrock et al. *Functional Dependency Discovery: An Experimental Evaluation of Seven Algorithms.* PVLDB, 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
