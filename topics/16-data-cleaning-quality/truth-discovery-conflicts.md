# Truth Discovery From Conflicting Sources

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/truth-discovery-conflicts` · **Status:** partially-solved

## 1. Problem Statement
Given $K$ sources each asserting (possibly conflicting) values for a set of *data items* (entity–attribute pairs), **jointly infer (a) the true value of each item and (b) the reliability of each source**, with no ground truth. This is the core of *data fusion*.

Variants:
- **Decision:** Is value $v$ the consensus truth for item $o$ under a given reliability model?
- **Optimization (MLE/MAP):** Find truths $\{v_o^\*\}$ and reliabilities $\{r_k\}$ maximizing the joint likelihood of observed claims.
- **Categorical vs. numeric vs. structured** items (sets, rankings) change the conflict model.

Plain majority voting fails because sources differ wildly in accuracy and copy from one another (see copy-detection-fusion). The challenge is the **chicken-and-egg coupling**: truth depends on reliability, reliability depends on truth.

## 2. Mathematical Foundations
Let $X_{ko}$ be the claim of source $k$ on object $o$, $v_o$ the latent truth, and $r_k$ source accuracy. A common generative model:
$$\Pr(X_{ko}=v \mid v_o, r_k) = \begin{cases} r_k & v=v_o \\ \tfrac{1-r_k}{n_o-1} & v\neq v_o \end{cases}$$
with $n_o$ candidate values. The joint log-likelihood $\sum_{k,o}\log\Pr(X_{ko}\mid v_o,r_k)$ is optimized by **EM**-style alternation (estimate $v_o$ given $r_k$, then $r_k$ given $v_o$), generalizing **Dawid–Skene**. Bayesian variants (TruthFinder, LCA, BCC) place priors on $r_k$. Numeric items use Gaussian source-variance models; correlations between sources are captured by covariance or copying parameters. Convergence and identifiability rest on conditions analogous to **spectral/tensor decomposition** recovery of latent confusion matrices (Zhang–Chen–Zhou–Jordan, NeurIPS 2014), which give global optima with sample guarantees—unlike EM's local optima.

## 3. State of the Art (SOTA)
- **TruthFinder** (Yin, Han, Yu, KDD 2007): iterative trust/confidence propagation—the seminal formulation.
- **Bayesian / Latent fusion: ACCU, PopAccu** (Dong, Berti-Équille, Srivastava, VLDB 2009): probabilistic accuracy models with copy detection.
- **LCA / CRH** (Pasternack–Roth; Li et al., SIGMOD 2014): the **Conflict Resolution on Heterogeneous data (CRH)** optimization framework unifies categorical+numeric loss minimization.
- **Spectral methods** (Zhang et al., NeurIPS 2014): provable Dawid–Skene recovery with statistical rates.
- Surveys: Li et al., *A Survey on Truth Discovery* (SIGKDD Explorations 2016); Berti-Équille & Borge-Holthoefer (2015).

## 4. Upper Bound
Each EM/CRH iteration is $O(|\text{claims}|)$; convergence is fast empirically but only to a **local** optimum. Spectral/tensor methods (Zhang et al. 2014) achieve **global** minimax-optimal estimation of worker reliabilities and labels with error decaying as $O(1/\sqrt{n})$ in the number of items per source, under separation conditions, in polynomial time. Under the one-coin/symmetric model, message-passing (Karger–Oh–Shah-style) attains order-optimal label error $e^{-\Theta(\bar{q}\,I)}$ where $I$ measures redundancy×reliability.

## 5. Lower Bound
Joint MLE over discrete truths with general source-correlation structure subsumes **MAX-SAT/MaxLikelihood inference in factor graphs**, which is **NP-hard**; exact MAP is hard in general. Information-theoretically, recovery is **impossible** below a redundancy/reliability threshold: if average source accuracy $\le 1/n_o$ (no better than random) truth is unidentifiable—a phase-transition lower bound. Without separation, EM-style methods cannot beat random initialization (non-identifiability), matching the spectral-method assumptions.

## 6. The Gap
For the symmetric Dawid–Skene model the gap is essentially **closed** (spectral methods meet the minimax bound). It remains **open** for **realistic models**: correlated/copying sources, structured values (rankings, sets), long-tailed source coverage, and adversarial sources. No polynomial algorithm provably attains optimal accuracy when copying and correlation are present; closing it needs identifiable correlated-source models with recovery guarantees.

## 7. Current Research (as of June 2026)
- **LLM-assisted truth discovery:** using LLM priors as an additional (calibrated) "source," and fusing model+web claims *(frontier — verify)*.
- **Knowledge-graph / temporal truth discovery:** truths that change over time, with change-point models *(frontier — verify)*.
- Groups: Xin Luna Dong (now in industry), Jiawei Han (UIUC), Bo Zhao / Qi Li / Jing Gao (truth-discovery optimization lineage), Laure Berti-Équille.

## 8. Future Work
- Provable algorithms for copy-aware, correlated-source models (bridge to copy-detection-fusion).
- Truth discovery with formal coverage/abstention guarantees (link to repair-quality-certification).
- Streaming/online truth discovery with regret bounds; differential-privacy-preserving fusion.

## 9. Key References
- **[Foundational]** X. Yin, J. Han, P. S. Yu. *Truth Discovery with Multiple Conflicting Information Providers on the Web.* KDD, 2007. — [DOI](https://doi.org/10.1145/1281192.1281309)
- **[Foundational]** X. L. Dong, L. Berti-Équille, D. Srivastava. *Integrating Conflicting Data: The Role of Source Dependence.* VLDB, 2009. — [DOI](https://doi.org/10.14778/1687627.1687690)
- **[SOTA]** Q. Li, Y. Li, J. Gao, B. Zhao, W. Fan, J. Han. *Resolving Conflicts in Heterogeneous Data by Truth Discovery and Source Reliability Estimation (CRH).* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2610509)
- **[SOTA]** Y. Zhang, X. Chen, D. Zhou, M. I. Jordan. *Spectral Methods Meet EM: A Provably Optimal Algorithm for Crowdsourcing.* NeurIPS, 2014. — [arXiv](https://arxiv.org/abs/1406.3824)
- **[Survey]** Y. Li, J. Gao, C. Meng, Q. Li, L. Su, B. Zhao, W. Fan, J. Han. *A Survey on Truth Discovery.* SIGKDD Explorations, 2016. — [DOI](https://doi.org/10.1145/2897350.2897352)

## 10. Worked Example

Three sources report the CEO of a company; the truth is unknown. Items $o_1, o_2, o_3$ have a known ground truth (omitted from the algorithm) of A, B, C respectively.

| source | $o_1$ | $o_2$ | $o_3$ |
|--------|-------|-------|-------|
| $s_1$ | A | B | C |
| $s_2$ | A | B | X |
| $s_3$ | A | Y | Z |

Plain majority: $o_1\to$A (3 votes), $o_2\to$B (2 votes), $o_3$ is a 3-way tie — unresolved.

EM/Dawid–Skene alternation breaks the tie. **E-step** (start $r_k=0.5$ all): with current truths A,B,? estimate accuracies from agreement counts. $s_1$ agrees on $o_1,o_2$ and the consensus, $s_3$ disagrees on $o_2,o_3$, giving roughly $\hat r_1 \approx 1.0$, $\hat r_2 \approx 0.67$, $\hat r_3 \approx 0.33$. **M-step:** reweigh votes by $\log\frac{r_k(n_o-1)}{1-r_k}$. For $o_3$, $s_1$'s vote (C) now carries far more weight than $s_2$ (X) or $s_3$ (Z), so $o_3\to$C. The chicken-and-egg coupling (section 1) resolves the tie majority could not — converging to the correct A, B, C.

---
*Part of the [DBMS Research catalog](../../README.md).*
