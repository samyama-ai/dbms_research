# Cross-System Transfer of Policies

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/cross-system-transfer` · **Status:** empirically-open

## 1. Problem Statement
A self-driving policy (a tuning agent, a learned cost model, an index advisor, a forecaster) is trained on one DBMS engine, version, or hardware platform. The **cross-system transfer problem**: deploy that policy on a *different* engine (Postgres→MySQL), version (PG14→PG16), or hardware (NVMe→cloud EBS, x86→ARM) and retain most of its quality **without full retraining**, despite shifted action semantics, knob spaces, cost-model internals, and dynamics.

Variants:
- **Optimization:** given a source policy $\pi_S$ and a small target budget, find target policy $\pi_T$ maximizing target return.
- **Decision:** does a known correspondence (knob/action alignment) preserve $\epsilon$-optimality across the shift?
- **Identifiability:** is the target dynamics identifiable from $k$ target samples plus the source model?

## 2. Mathematical Foundations
Source and target are MDPs $\mathcal{M}_S,\mathcal{M}_T$ differing in $(S,A,P,R)$. Transfer quality is bounded by a **simulation/bisimulation metric** $d(\mathcal{M}_S,\mathcal{M}_T)$: if states/actions can be aligned with bounded transition + reward discrepancy $\le\eta$, the value gap of a transferred policy is $O(\eta/(1-\gamma))$ (Ferns et al. bisimulation bounds). This is **domain adaptation** with covariate + label shift: the workload feature distribution and the action→performance map both move.

For learned cost models, transfer is regression under distribution shift; the target error decomposes (Ben-David et al. 2010) as source error + $\mathcal{H}$-divergence between source/target feature distributions + an irreducible joint-optimal term. Action-space mismatch (different knob sets, units, ranges) requires an **alignment map** $\phi:A_S\to A_T$; only the aligned subspace transfers, the rest must be relearned. Hardware shift mostly rescales the cost function (different constants in I/O vs. CPU), often modeled as an affine reparameterization of the cost model that few target samples can refit.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Learned cost models / cardinality estimators (MSCN—Kipf et al. 2019; Neo—Marcus et al. VLDB 2019; Bao—Marcus et al. SIGMOD 2021) show transfer struggles across schemas/engines and motivate retraining or fine-tuning. ResTune/OnlineTune transfer tuning across cloud instances. Stage/zero-shot cost models (Hilprecht & Binnig, *Zero-Shot Cost Models*, VLDB 2022) explicitly target unseen databases by using transferable features.
- **Theory-SOTA:** Bisimulation-metric value bounds (Ferns, Panangaden, Precup) and domain-adaptation generalization bounds (Ben-David et al. 2010) are the transferable theory.

## 4. Upper Bound
With an alignment of bounded discrepancy $\eta$, the transferred-policy value loss is bounded by $\frac{2\eta}{(1-\gamma)^2}$ (lax-bisimulation / simulation-lemma style). Domain-adaptation theory bounds target risk by source risk plus $\tfrac12 d_{\mathcal{H}\Delta\mathcal{H}}(D_S,D_T)+\lambda^\*$, and fine-tuning on $m$ target samples reduces the adaptive term at rate $\tilde O(\sqrt{\mathrm{VC}/m})$. Zero-shot cost models empirically transfer to unseen databases by restricting to engine-agnostic features, trading peak accuracy for portability—an upper-bound *in practice* on retraining cost (near zero).

## 5. Lower Bound
Transfer is impossible without overlap: if source and target supports are disjoint in the relevant feature region (no common-support / positivity), target risk is unidentifiable—an information-theoretic obstruction; the $\lambda^\*$ joint-optimal term in Ben-David's bound can be $\Omega(1)$ and is irreducible. **Negative transfer** is provable: an adversarial target dynamics makes the source policy arbitrarily suboptimal, so no algorithm guarantees improvement over training-from-scratch without an assumed bound on $d(\mathcal{M}_S,\mathcal{M}_T)$. Aligning two arbitrary knob/action spaces optimally (graph/assignment matching under performance preservation) is NP-hard in general.

## 6. The Gap
Theory gives value-loss bounds *as a function of an assumed cross-system discrepancy* $\eta$, but in practice $\eta$ is unknown and hard to estimate before deployment, and the cost-model/dynamics shift across engines is large and structured (different optimizers), not a small perturbation. The empirical gap: portable feature designs (zero-shot models) generalize but lose accuracy, while accurate models don't transfer—no method yet achieves both with a certified bound on retraining samples. Status is empirically-open.

## 7. Current Research (as of June 2026)
- Zero-shot and "tabular/relational foundation" models for cost/cardinality estimation transferring across unseen DBs *(frontier — verify)*.
- LLM-assisted knob/action alignment and documentation-grounded transfer across engines *(frontier — verify)*.
- Sim-to-real style robust RL for tuning, training under domain randomization over hardware/versions.
- Groups: TU Darmstadt (Binnig, Hilprecht — zero-shot models), MIT (Marcus, Kraska — Neo/Bao learned components), Alibaba/MSRA tuning groups, and the domain-adaptation theory community.

## 8. Future Work
- Pre-deployment estimators of cross-system discrepancy $\eta$ with safety margins.
- Provable negative-transfer guards (never worse than scratch) for DB policies.
- Canonical engine-agnostic action/feature representations with transfer guarantees.
- Continual/version-aware policies that cheaply adapt across DBMS upgrades.

## 9. Key References
- **[Foundational]** S. Ben-David, J. Blitzer, K. Crammer, A. Kulesza, F. Pereira, J. Wortman Vaughan. *A Theory of Learning from Different Domains.* Machine Learning, 2010.
- **[Foundational]** N. Ferns, P. Panangaden, D. Precup. *Metrics for Finite Markov Decision Processes.* UAI, 2004.
- **[SOTA]** B. Hilprecht, C. Binnig. *Zero-Shot Cost Models for Out-of-the-box Learned Cost Prediction.* VLDB, 2022.
- **[SOTA]** R. Marcus et al. *Neo: A Learned Query Optimizer.* VLDB, 2019.
- **[SOTA]** R. Marcus et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021.
- **[SOTA]** A. Kipf et al. *Learned Cardinalities: Estimating Correlated Joins with Deep Learning (MSCN).* CIDR, 2019.

---
*Part of the [DBMS Research catalog](../../README.md).*
