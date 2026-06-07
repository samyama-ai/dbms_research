---
id: 27-learned-db-components/learned-cost-model-calibration
title: "Learned Plan Cost Model Calibration"
topic: 27-learned-db-components
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Learned Plan Cost Model Calibration

> **Topic:** Learned Database Components · **ID:** `27-learned-db-components/learned-cost-model-calibration` · **Status:** partially-solved

## 1. Problem Statement

A learned cost model maps a physical plan (and its inputs) to a predicted latency, trained on observed executions. The calibration problem: **keep the model's predictions accurate and well-calibrated as the deployment environment drifts** — different hardware, growing/changing data, and varying concurrency — without full retraining on every shift.

Variants:

- **Point accuracy (estimation):** keep relative error / q-error of $\hat L(p)$ vs. true latency $L(p)$ bounded across environments.
- **Probabilistic calibration (decision):** emit predictive intervals $[\ell,u]$ whose empirical coverage matches the nominal $1-\delta$ *after* shift (a calibration, not accuracy, criterion).
- **Ranking fidelity (the optimizer-relevant variant):** preserve the *order* of candidate plans even if absolute latencies are mis-scaled — the optimizer only needs $\hat L(p_1)<\hat L(p_2)\iff L(p_1)<L(p_2)$.

It is *partially-solved*: transfer/calibration techniques (re-scaling, conformal recalibration, hardware features) handle moderate shift well; large or compositional shift (new hardware class + 10× data + high concurrency simultaneously) remains open.

## 2. Mathematical Foundations

Let environment $e=(\text{hw},\text{data }D,\text{conc }c)$ induce a conditional latency distribution $L\mid p,e$. Training samples come from $e_0$; deployment is $e_1$ with **covariate and label shift**. The model $\hat L_\theta(p)$ is calibrated on $e_1$ if, for predicted quantile $\tau$, $\Pr_{e_1}[L\le \hat F^{-1}(\tau\mid p)]=\tau$.

Foundations:

- **Domain adaptation under shift:** generalization across environments is governed by an $\mathcal H$-divergence / discrepancy term $d(e_0,e_1)$ (Ben-David et al. 2010): error on $e_1\le$ error on $e_0$ + discrepancy + best-joint-error. Calibration cannot be guaranteed when $d$ is large and unmeasured.
- **Conformal recalibration:** with a small labeled sample from $e_1$, split/weighted conformal prediction restores finite-sample coverage distribution-free (Vovk; Tibshirani et al. 2019), even if point accuracy is off.
- **Compositional structure:** latency is roughly additive/serial over operators plus contention terms; a learned model that respects $L(\text{plan})\approx\sum_{\text{op}}\hat\ell(\text{op})+\text{contention}(c)$ transfers better because per-operator kernels recalibrate independently (cost = work / throughput, with throughput a hardware constant). Queueing theory (e.g., $M/M/k$, USL — Universal Scalability Law) models the concurrency term, letting concurrency be a *fitted scalar* rather than a learned black box.

## 3. State of the Art (SOTA)

- **Systems-SOTA:** *QPP-Net* (Marcus & Papaemmanouil, ICDE 2019) — a plan-structured neural net predicting latency by composing per-operator sub-networks, which aids transfer. *Stage*/*Zero-shot cost models* — Hilprecht & Binnig (*"Zero-Shot Cost Models for Out-of-the-Box Learned Cost Prediction,"* VLDB 2022) generalize across **unseen databases** by featurizing data and operators transferably. *DACE* and end-to-end learned cost models for concurrent workloads; Microsoft/Amazon use feedback-driven cardinality+cost correction in production *(frontier — verify)*.
- **Theory-SOTA:** domain-adaptation bounds and conformal recalibration give the formal backbone; no tight, DBMS-specific transfer theorem.

## 4. Upper Bound

- **With $n$ labeled samples from target env:** weighted conformal recalibration gives finite-sample, distribution-free coverage within $O(1/\sqrt n)$ of nominal under bounded likelihood-ratio shift — **statistical learning model**. Point error after re-scaling is bounded by the residual discrepancy $d(e_0,e_1)$ that re-scaling cannot remove.
- **Zero-shot transfer:** with transferable operator/data features, target error $\le$ source error $+\,d_{\mathcal H\Delta\mathcal H}(e_0,e_1)+\lambda^\*$ (Ben-David bound); empirically small for hardware/data shift, not provably small in general.

## 5. Lower Bound

- **No-free-lunch under unmeasured shift:** if the target environment differs in an unobserved factor (e.g., a memory-bandwidth regime absent from features), no method achieves bounded error without target samples — information-theoretic impossibility (discrepancy term is unbounded).
- **Concurrency hardness:** predicting latency under arbitrary concurrent workloads is at least as hard as predicting interference of co-running plans; in the worst case contention is non-additive and adversarial schedules force $\Omega(1)$ relative error for any model trained on isolated executions.
- **Calibration lower bound:** distribution-free *conditional* coverage (per-query, not marginal) is impossible without extra assumptions (Foygel Barber et al. 2021) — only marginal calibration is achievable distribution-free.

## 6. The Gap

Partially closed. Marginal calibration and single-axis shift (hardware *or* data *or* concurrency) are handled with target samples + conformal/transfer methods. The open gap is **compositional, unlabeled, conditional**: simultaneous multi-axis shift, with little/no target data, and per-query (conditional) coverage. Closing it likely needs mechanistic priors (queueing/USL contention terms, per-operator hardware kernels) that shrink the effective discrepancy so statistical recalibration has little left to fix.

## 7. Current Research (as of June 2026)

- Zero-shot / transferable cost models with data-and-operator features that generalize to unseen DBs and hardware (Binnig/Hilprecht, TU Darmstadt) *(frontier — verify)*.
- Hybrid mechanistic+learned models: analytical queueing/USL concurrency term wrapped around a learned per-operator kernel, so concurrency recalibrates by fitting a scalar (CMU, MSR) *(frontier — verify)*.
- Online feedback-driven recalibration: use observed runtimes to continuously correct estimates (closing the loop with cardinality feedback, à la DB2 LEO lineage).
- Conformalized cost intervals feeding **safe-exploration-optimizers** as pre-execution upper bounds.

## 8. Future Work

- Per-query (conditional) calibration guarantees under realistic assumptions.
- Provable transfer bounds tied to measurable hardware/data features (turn discrepancy into something computable).
- Robust concurrency modeling validated against adversarial co-runner schedules (links to **learned-component-robustness**).
- Sample-efficient target adaptation (few-shot recalibration after a hardware migration).

## 9. Key References

- **[SOTA]** Marcus, Papaemmanouil. *Plan-Structured Deep Neural Network Models for Query Performance Prediction (QPP-Net).* ICDE / VLDB, 2019. — [arXiv](https://arxiv.org/abs/1902.00132)
- **[SOTA]** Hilprecht, Binnig. *Zero-Shot Cost Models for Out-of-the-Box Learned Cost Prediction.* VLDB, 2022. — [arXiv](https://arxiv.org/abs/2201.00561)
- **[Foundational]** Ben-David, Blitzer, Crammer, Kulesza, Pereira, Vaughan. *A Theory of Learning from Different Domains.* Machine Learning, 2010. — [DOI](https://doi.org/10.1007/s10994-009-5152-4)
- **[Foundational]** Tibshirani, Foygel Barber, Candès, Ramdas. *Conformal Prediction Under Covariate Shift.* NeurIPS, 2019. — [arXiv](https://arxiv.org/abs/1904.06019)
- **[Foundational]** Foygel Barber, Candès, Ramdas, Tibshirani. *The Limits of Distribution-Free Conditional Predictive Inference.* Information and Inference, 2021. — [arXiv](https://arxiv.org/abs/1903.04684)
- **[Foundational]** Stillger, Lohman, Markl, Kandil. *LEO — DB2's LEarning Optimizer.* VLDB, 2001. — [DBLP](https://dblp.org/rec/conf/vldb/StillgerLMK01.html)

## 10. Worked Example

A model trained on source hardware $e_0$ predicts a hash-join plan's latency as $\hat L=100$ ms. After migration to faster hardware $e_1$ the true latency is $L=62$ ms, so raw predictions are biased high by a roughly constant **scale factor**.

**Ranking fidelity survives a monotone shift.** Two candidate plans predicted at $\hat L(p_1)=100$ and $\hat L(p_2)=140$ keep their order after any monotone rescale, so the optimizer still picks $p_1$ — even though both absolute numbers are wrong (Section 1, ranking variant).

**Conformal recalibration of the interval.** Collect $n=200$ labeled runs on $e_1$ and form residuals $r_i=L_i-\hat L_i$. For nominal $90\%$ coverage take the empirical quantile at rank $\lceil(n+1)(1-\delta)\rceil=\lceil201\cdot0.9\rceil=181$, i.e. the $181$st smallest residual, say $-35$ ms with a symmetric spread of $\pm12$. The calibrated interval becomes $\hat L + [-47,\,-23]$, so for $\hat L=100$ we emit $[53,\,77]$ ms — which covers the true $62$ ms. Coverage error shrinks as $O(1/\sqrt n)\approx 0.07$ (Section 4).

But this only fixes *marginal* coverage. If $e_1$ also changed an unmeasured memory-bandwidth regime, no amount of rescaling removes the residual discrepancy $d(e_0,e_1)$ (Section 5) — the open compositional case.

---
*Part of the [DBMS Research catalog](../../README.md).*
