# Multi-Source Data Fusion Truth Discovery

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/multi-source-truth-discovery` · **Status:** empirically-open

## 1. Problem Statement

After schema mapping and entity resolution, many sources assert **conflicting values** for the same (entity, attribute) cell — e.g., different birthdates, prices, or affiliations. **Truth discovery (data fusion)** infers, for each *data item* $i$, the most likely true value $v_i^\star$ while **jointly estimating the trustworthiness** of each source $s$, under the principle: *a source is trustworthy if it provides true values, and a value is likely true if asserted by trustworthy sources.*

Formally: given a set of items $\mathcal{I}$, sources $\mathcal{S}$, and observations $o_{s,i}$ (the value source $s$ gives for item $i$, possibly missing), estimate truth labels $\{v_i^\star\}$ and source-trust parameters $\{\theta_s\}$. Complications make this **empirically open**: (i) **copying/correlation** between sources (non-independence breaks naive voting), (ii) **source coverage** and missing data, (iii) heterogeneous value types (categorical, numeric, set-valued), (iv) **adversarial/colluding** sources. The decision/estimation goal is principled, **source-trust-aware accuracy guarantees** — provable recovery conditions — which current methods largely lack (they are heuristic EM-style iterations with empirical, not certified, accuracy).

## 2. Mathematical Foundations

Truth discovery is a **latent-variable estimation** problem closely tied to **crowdsourcing / Dawid–Skene** aggregation. The Dawid–Skene model treats each source as a confusion matrix and recovers truth by EM; identifiability and error rates are analyzable via **spectral / tensor decomposition** (Zhang, Chen, Zhou, Jordan, 2014) and **information-theoretic minimax** bounds (function of source reliabilities' KL divergence from chance and redundancy).

- **Optimization view (CRH/conflict resolution):** minimize $\sum_s \theta_s \sum_i d(o_{s,i}, v_i^\star)$ subject to a normalization on weights $\{\theta_s\}$, alternating between truth and weight updates (Li et al., SIGMOD 2014). Convexity and convergence depend on the distance $d$.
- **Probabilistic / copy detection:** Dong, Berti-Équille, Srivastava model **copying** via Bayesian dependence detection so dependent sources don't double-count.
- **Guarantees:** recovery is provable in **planted** models (each source reliability $> 1/2$, sufficient redundancy, independence) via spectral methods; the gap is that real sources are **correlated and adversarial**, where minimax-optimal, copy-robust estimators are not established.

## 3. State of the Art (SOTA)

- **Foundational.** Yin, Han, Yu — *TruthFinder* (TKDE 2008); Dong, Berti-Équille, Srivastava — *Integrating Conflicting Data: the Role of Source Dependence* (VLDB 2009) — copy detection + accuracy (the "ACCU/Depen/Fusion" family).
- **Optimization-SOTA.** Li, Gao, Meng, Su, Zhao, Fan, Han — *Resolving Conflicts in Heterogeneous Data by Truth Discovery and Source Reliability Estimation (CRH)* (SIGMOD 2014); *A Survey on Truth Discovery* (Li et al., SIGKDD Explorations 2016).
- **Theory.** Zhang, Chen, Zhou, Jordan — *Spectral Methods Meet EM* (NeurIPS 2014) — provable Dawid–Skene recovery. Ghosh–Kale–McAfee, Karger–Oh–Shah — crowdsourcing label aggregation guarantees.
- **Knowledge-base scale.** Dong et al. — *Knowledge-Based Trust* (VLDB 2015) — web-scale source quality.

## 4. Upper Bound

Under the **Dawid–Skene / planted** model (independent sources, reliability bounded away from $1/2$, adequate redundancy $r$), spectral + one EM step achieves error decaying as $\exp(-\Omega(r \cdot \mathrm{gap}))$ and is **minimax-rate-optimal** (Zhang et al. 2014; Gao–Zhou 2016), in the statistical estimation model. **CRH/optimization** methods converge to a stationary point of the joint objective in $O(\text{iters} \cdot |\mathcal{S}||\mathcal{I}|)$ per pass; **copy-aware** Bayesian fusion (Dong et al.) empirically restores accuracy under dependence. KDD-style guarantees are **conditional on model correctness**.

## 5. Lower Bound

There is an **information-theoretic minimax lower bound**: below a redundancy/reliability threshold (sources too few or too close to chance), **no estimator** recovers truth better than majority/chance (Karger–Oh–Shah; Gao–Zhou minimax). Under **correlated/copying** sources, the effective independent redundancy collapses and recovery can be **impossible** even with many sources (an adversary controlling a copying majority is unbeatable). Detecting copying is itself hard — distinguishing coincidence from copying is a **statistical hypothesis-testing** problem with non-trivial sample complexity; with **colluding adversaries**, identifiability **fails** (multiple truth/trust assignments fit the data), an impossibility distinct from any computational hardness.

## 6. The Gap

The **theory is tight in the idealized model** (independent, non-adversarial sources: minimax rates known and achieved). The problem is **empirically open** because real data integration violates every assumption: sources **copy**, coverage is skewed, errors are **structured** (not i.i.d.), and adversaries collude. No method offers **certified accuracy under correlation + adversarial sources** simultaneously; heuristics dominate practice and are evaluated only empirically (benchmark wins, not bounds). Closing the gap means recovery guarantees under realistic dependence and adversary models, plus identifiability conditions stating *when truth is recoverable at all*.

## 7. Current Research (as of June 2026)

- **Robust / Byzantine-resilient truth discovery** with provable recovery under a bounded fraction of colluding sources, importing Byzantine-aggregation tools from federated learning. *(frontier — verify)*
- **LLMs as sources / fusers:** treating model outputs as additional fallible sources, calibrating their trust, and detecting LLM "copying" from shared training data. *(frontier — verify)*
- Truth discovery integrated with **uncertain/probabilistic data exchange** and provenance, propagating source-trust into query answers. *(frontier — verify)*
- Causal / temporal truth discovery where values legitimately change over time (Dong, Berti-Équille lines). *(frontier — verify)*

## 8. Future Work

- Identifiability theory under copying and collusion: *when is the truth recoverable?*
- Minimax-optimal, copy-robust estimators (beyond heuristic EM).
- Calibrated, source-trust-aware confidence on each fused value (not just point estimates).
- Online/streaming truth discovery with drifting source reliability.

## 9. Key References

- **[Foundational]** X. Yin, J. Han, P. S. Yu. *Truth Discovery with Multiple Conflicting Information Providers on the Web (TruthFinder).* IEEE TKDE, 2008.
- **[Foundational]** X. L. Dong, L. Berti-Équille, D. Srivastava. *Integrating Conflicting Data: The Role of Source Dependence.* VLDB, 2009.
- **[SOTA]** Q. Li, Y. Li, J. Gao, B. Zhao, W. Fan, J. Han. *Resolving Conflicts in Heterogeneous Data by Truth Discovery and Source Reliability Estimation (CRH).* SIGMOD, 2014.
- **[SOTA]** Y. Zhang, X. Chen, D. Zhou, M. I. Jordan. *Spectral Methods Meet EM: A Provably Optimal Algorithm for Crowdsourcing.* NeurIPS, 2014.
- **[Foundational]** A. P. Dawid, A. M. Skene. *Maximum Likelihood Estimation of Observer Error-Rates Using the EM Algorithm.* Applied Statistics, 1979.
- **[Survey]** Y. Li, J. Gao, C. Meng, Q. Li, L. Su, B. Zhao, W. Fan, J. Han. *A Survey on Truth Discovery.* SIGKDD Explorations, 2016.
- **[Foundational]** D. R. Karger, S. Oh, D. Shah. *Iterative Learning for Reliable Crowdsourcing Systems.* NeurIPS, 2011.

---
*Part of the [DBMS Research catalog](../../README.md).*
