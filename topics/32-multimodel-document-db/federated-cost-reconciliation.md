---
id: 32-multimodel-document-db/federated-cost-reconciliation
title: "Federated cost-model reconciliation"
topic: 32-multimodel-document-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Federated cost-model reconciliation

> **Topic:** Multi-Model & Document Databases · **ID:** `32-multimodel-document-db/federated-cost-reconciliation` · **Status:** open

## 1. Problem Statement

A polystore/federation routes sub-plans to autonomous stores $S_1, \dots, S_k$ (a relational engine, a document store, a graph DB, a column store). Each $S_i$ exposes an **opaque** local cost estimate $c_i(\text{sub-plan})$ in its *own units* (page reads, CPU ticks, abstract "cost", or nothing at all). The federated optimizer must choose a global plan, which requires comparing $c_i$ across stores. The problem: **reconcile incompatible, opaque, possibly adversarial local cost estimates into a single comparable currency** (e.g., wall-clock seconds or dollars) so global plan selection is sound.

Variants:
- **Calibration (estimation):** learn $g_i : c_i \mapsto \hat t_i$ mapping each store's cost units to a common unit, minimizing global plan-quality regret.
- **Decision:** given two candidate global plans, decide which has lower true cost using only opaque/partial local estimates.
- **Robust optimization:** choose a plan minimizing worst-case cost over the *uncertainty set* induced by unreliable local estimates.

The crux is **autonomy + opacity**: stores will not expose their internals, their estimators are independently biased and non-monotone, and units are incommensurable.

## 2. Mathematical Foundations

- **Cost model algebra:** a plan is a tree of operators; total cost is a (possibly non-additive) composition $C(\text{plan}) = \Phi(\{c_i\})$. Classical optimizers assume additivity and a single currency (Selinger). Federation breaks both.
- **Calibration as regression under covariate shift:** learn $g_i$ from observed $(c_i, t_i)$ pairs; the workload distribution at calibration differs from production, so generalization needs distribution-shift bounds.
- **Decision-theory / regret:** model optimizer choice as a bandit/online-learning problem; plan-selection **regret** $\sum_t (t(\text{plan}_t) - t(\text{plan}^\*))$ is the right objective. Calibrating cost is a means to bound regret.
- **Robust/minimax:** with uncertainty sets $\mathcal U_i$ around each estimate, choose $\arg\min_{\text{plan}} \max_{c \in \mathcal U} C$. This connects to robust query optimization (Plan Bouquets, parametric/PQO).
- **Mechanism-design view:** autonomous stores may *strategically* report costs (to attract or shed work); reconciliation then needs incentive-compatible elicitation — eliciting truthful cost is a scoring-rule problem.
- **Order theory:** reconciliation needs only a consistent *total preorder* over plans, not absolute costs — weaker and sometimes achievable when absolute calibration is not.

## 3. State of the Art (SOTA)

- **Foundational systems:** Garlic and the wrapper cost-model approach (Roth–Schwarz; Haas et al., VLDB 1997) — wrappers export calibrated cost formulas. Mariposa (Stonebraker et al., 1996) used an *economic*/bidding model: stores bid in a common currency (dollars), sidestepping unit reconciliation by construction.
- **Polystores:** BigDAWG (Duggan et al., 2015) "islands of information" with cast-based cross-engine costing; Myria, Estocada, MISO, QUEPA. Apache Calcite/Presto/Trino use a single normalized cost model and *re-implement* connector costs rather than reconcile opaque ones.
- **Learned-SOTA:** learned cost models (e.g., per-engine learned latency predictors; Bao/Neo-style learned optimizers, Marcus et al. 2019–2021) used as a *common* calibrated currency across engines *(frontier — verify)*.

## 4. Upper Bound

When each store exports a *monotone* calibratable cost formula and a small profiling workload is available, learning $g_i$ via isotonic/linear regression yields a common currency with bounded calibration error, and Selinger-style dynamic programming then selects a globally near-optimal plan — i.e., the problem reduces to standard cost-based optimization with a known additive error. With the **economic model** (Mariposa), reconciliation is *trivially* achieved a priori: all stores bid in dollars, giving a sound comparison with no calibration. No general algorithm is known to give a provable global-plan approximation guarantee when local estimates are opaque, non-monotone, and only ordinally meaningful.

## 5. Lower Bound

- **Impossibility of common cardinality from opaque parts:** propagated cardinality/cost error compounds **multiplicatively** through a plan (Ioannidis–Christodoulakis, SIGMOD 1991): errors grow exponentially in plan depth, so any reconciliation built on biased local estimates inherits an unbounded worst-case ratio.
- **Elicitation hardness:** if stores report strategically, no non-incentive-compatible scheme can guarantee truthful costs (mechanism-design impossibility); truthful elicitation requires payment/scoring rules.
- **Information-theoretic:** without *any* shared observable (no common unit, no probe queries), the cross-store comparison is unidentifiable — distinct true-cost orderings produce identical observable reports. This is a genuine impossibility, not just hardness.

## 6. The Gap

The gap is **wide open**. Upper bounds exist only under strong assumptions (monotone, calibratable, profilable, or a priori common currency à la Mariposa). The lower bounds show that with genuinely opaque, strategic, or unprobeable stores the comparison can be *unidentifiable* or have unbounded error. What would close it: (a) a calibration protocol with provable regret under bounded shift and bounded probing budget; (b) characterizing exactly which autonomy/observability conditions make reconciliation identifiable; (c) incentive-compatible cost elicitation integrated with optimization.

## 7. Current Research (as of June 2026)

- Learned per-engine latency models as the lingua-franca currency in Trino/Presto-style federations *(frontier — verify)*.
- Robust/parametric federated optimization extending Plan Bouquets to cross-engine uncertainty (Haritsa group) *(frontier — verify)*.
- Reinforcement-learning federated optimizers that learn cross-engine cost ordering from execution feedback (MIT, Marcus/Kraska lineage).
- Groups: MIT DSAIL (Kraska, Madden — BigDAWG/Bao), IISc (Haritsa), CWI/Inria (Manolescu — Estocada).

## 8. Future Work

- Identifiability theory: necessary/sufficient observability for sound reconciliation.
- Incentive-compatible cost reporting for autonomous/commercial stores.
- Online calibration with regret bounds under workload drift.
- Standard probe-query protocol for unit calibration across engines.

## 9. Key References

- **[Foundational]** Selinger et al. *Access Path Selection in a Relational Database Management System.* SIGMOD, 1979. — [DOI](https://doi.org/10.1145/582095.582099)
- **[Foundational]** Stonebraker et al. *Mariposa: A Wide-Area Distributed Database System.* VLDB Journal, 1996. — [DOI](https://doi.org/10.1007/s007780050015)
- **[Foundational]** Haas, Kossmann, Wimmers, Yang. *Optimizing Queries Across Diverse Data Sources (Garlic).* VLDB, 1997. — [DBLP](https://dblp.org/rec/conf/vldb/HaasKWY97.html)
- **[Foundational]** Ioannidis, Christodoulakis. *On the Propagation of Errors in the Size of Join Results.* SIGMOD, 1991. — [DOI](https://doi.org/10.1145/115790.115835)
- **[SOTA]** Duggan et al. *The BigDAWG Polystore System.* SIGMOD Record, 2015. — [DOI](https://doi.org/10.1145/2814710.2814713)
- **[SOTA]** Marcus et al. *Bao: Making Learned Query Optimization Practical.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3452838)
- **[Survey]** Tan, Kaoudi, et al. *Polystore Systems: A Survey.* (overview of federated/polystore optimization), 2017–2020. *(unverified)*

## 10. Worked Example

Two stores price the same join sub-plan. Relational $S_1$ reports $c_1 = 4000$ "page reads"; document $S_2$ reports $c_2 = 250$ abstract "cost units". Incommensurable units — $250 < 4000$ tells us nothing. We probe with 3 calibration sub-plans and fit per-store linear maps $g_i(c)=a_i c$ to observed wall-clock seconds:

- $S_1$: $(1000, 0.6),\,(2000,1.1),\,(3000,1.6)$ → $a_1 \approx 0.00053$ s/unit.
- $S_2$: $(100,0.9),\,(200,1.7),\,(300,2.6)$ → $a_2 \approx 0.0087$ s/unit.

Reconciled estimates: $\hat t_1 = 0.00053 \times 4000 \approx 2.1$ s versus $\hat t_2 = 0.0087 \times 250 \approx 2.2$ s. So $S_1$ wins narrowly — the *opposite* conclusion to comparing raw $c_i$. Note error compounds: a 20% bias in $a_2$ flips the decision, illustrating why depth-$d$ plans inherit a $(1+\epsilon)^d$ worst-case ratio (Ioannidis–Christodoulakis).

---
*Part of the [DBMS Research catalog](../../README.md).*
