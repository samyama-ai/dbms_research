# Copy Detection in Data Fusion

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/copy-detection-fusion` · **Status:** partially-solved

## 1. Problem Statement
When fusing data from many sources, some sources **copy** (wholly or partially) from others. Treating copied values as independent evidence **double-counts** and lets popular-but-wrong values win. The problem: **detect copying relationships among sources and discount dependent evidence during fusion**.

Variants:
- **Decision:** Given two sources $S_1, S_2$, is one a (partial) copier of the other?
- **Direction:** If a copying relation exists, who is the originator?
- **Structure recovery:** Infer the full copying graph / dependency DAG over $K$ sources.
- **Joint:** Co-estimate truths, accuracies, and the copying graph (couples with truth-discovery-conflicts).

The signal is statistical: **shared errors** are far more telling than shared truths, since two accurate independent sources naturally agree on truths but rarely on the *same* mistake.

## 2. Mathematical Foundations
Let $\Phi$ be the set of objects, $\bar\Phi_t$ those where both sources give the same *true* value, $\bar\Phi_f$ same *false* value, $\Phi_d$ different values. The Bayesian copy-detection model (Dong et al., VLDB 2009) compares
$$\Pr(\text{observation}\mid S_1 \perp S_2) \quad\text{vs.}\quad \Pr(\text{observation}\mid S_2 \text{ copies } S_1),$$
where independence predicts shared false values with probability $\sim$ (per-value error)$^2$, but copying makes $|\bar\Phi_f|$ anomalously large. A copying parameter $c\in[0,1]$ and direction are inferred by Bayes' rule; the posterior feeds back to *down-weight* a source's vote by $(1-c)$. Detecting the global structure is a **latent-DAG/structure-learning** problem; correlated (not directional) copying maps to learning a Gaussian/Ising dependency graph. Identifiability requires enough independent objects—an information-theoretic constraint analogous to causal-direction identifiability (shared-noise asymmetry).

## 3. State of the Art (SOTA)
- **Solomon / Depen / Accu-Copy** (Dong, Berti-Équille, Srivastava, VLDB 2009): the foundational copy-detection + accuracy fusion model; later extended to **global** dependence detection and **PopAccu** (VLDB 2010, *"Global Detection of Complex Copying Relationships Between Sources"*).
- **Dynamic / evolving copying** (Dong et al., VLDB 2009 *"Truth Discovery and Copying Detection in a Dynamic World"*): handles sources that update over time and copy histories.
- **Knowledge-based trust / source quality** (Dong et al., VLDB 2015): web-scale source-reliability estimation that must contend with copying.
- Systems-SOTA folds copy discounting into the CRH/Bayesian fusion loop; theory-SOTA is largely the original Bayesian asymmetry argument—few hard guarantees.

## 4. Upper Bound
Pairwise copy detection costs $O(|\Phi|)$ per pair; naive global detection is $O(K^2|\Phi|)$, with Dong et al. giving pruning to scale to thousands of sources. The Bayesian estimator is **consistent**: as $|\bar\Phi_f|$ grows, posterior copying probability $\to 1$ for true copiers, $\to 0$ for independents, under the model's assumptions. No general polynomial algorithm is known to recover the *full* copying DAG with provable accuracy under partial/transitive copying; best results are heuristic with empirical validation.

## 5. Lower Bound
Recovering a dependency/copying DAG generalizes **Bayesian-network structure learning**, which is **NP-hard** (Chickering 1996). **Direction identifiability** has an information-theoretic floor: with too few shared false values, copier vs. originator is statistically **indistinguishable** (symmetry). Transitive copying ($A\to B\to C$) creates confounding equivalent to indistinguishable Markov-equivalence classes—a fundamental limit, not an algorithmic gap. Adversarial copiers that inject independent noise to mask copying can defeat any detector below a detection threshold (info-theoretic).

## 6. The Gap
**Genuinely open.** Pairwise detection is well-understood and consistent; **global, transitive, partial, and adversarial** copying recovery lacks tight guarantees. The gap between the NP-hard/identifiability lower bounds and practical heuristic detectors is wide. Closing it needs (a) identifiable structural assumptions under which the copying DAG is provably recoverable in poly-time, and (b) matching hardness for the residual cases.

## 7. Current Research (as of June 2026)
- **LLM-content provenance & near-duplicate web detection:** distinguishing genuinely independent corroboration from model-generated/copied web text—an acute new copying source *(frontier — verify)*.
- **Embedding-based correlation detection** replacing exact shared-error counts for noisy/numeric data *(frontier — verify)*.
- Groups: Xin Luna Dong, Divesh Srivastava (AT&T/Amazon lineage), Laure Berti-Équille; web-data-quality community.

## 8. Future Work
- Provable global copying-DAG recovery under structural assumptions.
- Joint truth+copying estimation with end-to-end guarantees (link to truth-discovery-conflicts).
- Robustness to adversarial/strategic copiers; provenance-aware fusion using cryptographic or watermark signals.

## 9. Key References
- **[Foundational]** X. L. Dong, L. Berti-Équille, D. Srivastava. *Integrating Conflicting Data: The Role of Source Dependence.* VLDB, 2009. — [DOI](https://doi.org/10.14778/1687627.1687690)
- **[Foundational]** X. L. Dong, L. Berti-Équille, D. Srivastava. *Truth Discovery and Copying Detection in a Dynamic World.* VLDB, 2009. — [DOI](https://doi.org/10.14778/1687627.1687691)
- **[SOTA]** X. L. Dong, L. Berti-Équille, Y. Hu, D. Srivastava. *Global Detection of Complex Copying Relationships Between Sources.* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1921008)
- **[SOTA]** X. L. Dong et al. *Knowledge-Based Trust: Estimating the Trustworthiness of Web Sources.* VLDB, 2015. — [arXiv](https://arxiv.org/abs/1502.03519)
- **[Foundational]** D. M. Chickering. *Learning Bayesian Networks is NP-Complete.* Learning from Data (AI & Statistics V), 1996. — [DOI](https://doi.org/10.1007/978-1-4612-2404-4_12)

## 10. Worked Example

Three sources report a country's capital over $|\Phi|=100$ objects. Per-source error rate $\epsilon=0.1$, so two *independent* sources should share a wrong answer on about $\epsilon^2\cdot 100 = 1$ object.

Observed shared-*false* counts: $|\bar\Phi_f(S_1,S_2)| = 12$, while $|\bar\Phi_f(S_1,S_3)| = 1$ and $|\bar\Phi_f(S_2,S_3)| = 1$.

For the pair $(S_1,S_2)$, seeing 12 identical mistakes when independence predicts $\approx 1$ is a $\sim$Poisson tail of $e^{-1}1^{12}/12! \approx 10^{-9}$ — overwhelming evidence of copying. Bayes' rule drives the posterior copying probability $c\to 1$. The fusion loop then discounts the second source's vote by $(1-c)\approx 0$, so $S_1,S_2$ count as essentially *one* witness rather than two.

Direction ($S_1\!\to\!S_2$ vs. $S_2\!\to\!S_1$) needs the accuracy asymmetry: the less-accurate source is inferred to be the copier. With only 12 shared errors, if both are equally accurate the direction is statistically indistinguishable — the identifiability floor of Section 5.

---
*Part of the [DBMS Research catalog](../../README.md).*
