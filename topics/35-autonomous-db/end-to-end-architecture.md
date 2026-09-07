---
id: 35-autonomous-db/end-to-end-architecture
title: "End-to-End Self-Driving Architecture"
topic: 35-autonomous-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# End-to-End Self-Driving Architecture

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/end-to-end-architecture` · **Status:** open

## 1. Problem Statement
A self-driving DBMS is not a single tuner but a **control system**: it must **forecast** future workload, **plan** a sequence of actions, **act** (apply reconfigurations), and **monitor** outcomes to close the loop — all while individual components (index advisor, knob tuner, partitioner, view selector) interact. The problem is to define a **unified control architecture** whose parts are *composable* (clean interfaces, no hidden coupling) and *verifiable* (each part and the whole carry guarantees: stability, safety, bounded regret).

Sub-problems:
- **Decomposition:** how to split forecast / plan / act / monitor into modules with contracts (inputs, outputs, guarantees) that compose without emergent instability (oscillation, conflicting actions).
- **Coordination (optimization):** schedule heterogeneous actions (indexes, knobs, partitions) that share resources and interact, maximizing long-horizon utility minus action cost.
- **Verification:** prove end-to-end properties — *safety* (never violate SLO/invariants), *stability* (no thrashing), *liveness* (converges to good configs) — from component contracts.

## 2. Mathematical Foundations
- **Closed-loop control:** the system is a feedback controller; classical/robust control gives *stability* notions (Lyapunov, $H_\infty$) and warns of oscillation when fast inner loops fight slow outer loops — exactly the index-vs-knob interaction. Model-predictive control (MPC) formalizes "forecast → plan over horizon → act → re-plan."
- **Sequential decision-making:** the whole loop is a (PO)MDP; planning is policy optimization with **action costs** and **switching costs**. Hierarchical RL / options give the forecast-plan-act decomposition; the monitor supplies state estimation.
- **Compositional verification:** **assume–guarantee reasoning** lets each module's guarantee hold under assumptions discharged by others, so global correctness follows from local proofs (interface automata, contract theory). For learned modules, this is *compositional* robustness — propagating uncertainty/conformal bounds across the pipeline.
- **Interaction / co-tuning:** components are not independent; index choice changes the optimal knobs and partition layout. This is a **joint** optimization over a product action space; submodular/matroid structure (when present) enables greedy guarantees, but cross-component interactions can break submodularity.
- **Self-driving reference loop:** Pavlo et al.'s articulation — *workload forecasting → action planning (what-if + cost) → deployment → reward observation* — is the canonical pipeline this problem seeks to make composable and verifiable.

## 3. State of the Art (SOTA)
**Systems-SOTA:** **Peloton / NoisePage** (CMU) is the reference self-driving prototype with a forecast-plan-act loop and behavior modeling; **OtterTune** (knobs), **DBA bandits / DRL index agents**, and **MB2 / modeling** for action cost estimation are components. Cloud platforms (Oracle Autonomous DB, Azure SQL automatic tuning, Aurora) ship *vertically integrated but mostly siloed* autonomy (each feature its own loop). **QueryBot 5000** (CMU) is a notable workload forecaster. The pieces exist; a *principled, verifiable* composition does not. *(frontier — verify)*

**Theory-SOTA:** control theory, MPC, hierarchical RL, and assume–guarantee verification are mature *individually*; their application to a DB self-driving stack with guarantees is nascent. No published architecture proves end-to-end stability/safety from component contracts.

## 4. Upper Bound
- **MPC / receding-horizon** gives provable performance and stability under model accuracy assumptions; with bounded forecast error $\epsilon$, MPC cost is within a known factor of clairvoyant optimal (regret scales with $\epsilon$ and horizon).
- **Learning-augmented composition:** if forecasts feed a consistency/robustness online policy, the loop inherits $(1+\epsilon)$-consistency / $\beta$-robustness end-to-end.
- **Assume–guarantee** verification gives sound (if conservative) end-to-end safety proofs in $O(\sum_i |M_i|)$ rather than the product state space, when contracts are well-formed. These hold in the control-theoretic and formal-methods models, modulo faithful component models.

## 5. Lower Bound
- **Composition can be unstable:** independently-stable feedback loops can oscillate when composed (gain/phase interaction) — a control-theoretic impossibility absent coordination, matching observed index/knob thrashing.
- **Verification hardness:** compositional verification is undecidable for sufficiently expressive (Turing-complete) component behaviors; even bounded model checking is PSPACE-hard, so global proofs require restricting component expressiveness.
- **Forecasting limit:** no controller beats an adversarial/unpredictable workload — if future load is not predictable from the past (high entropy rate), planning regret is $\Omega(T)$ (information-theoretic).
- **Joint-action hardness:** co-optimizing indexes + knobs + partitions is NP-hard (inherits index-selection hardness) and interactions can destroy submodularity, removing greedy guarantees.

## 6. The Gap
**Open.** Strong tools exist on both sides — control/MPC and assume–guarantee verification above, mature components below — but there is **no unifying architecture** that (a) specifies forecast/plan/act/monitor contracts, (b) coordinates interacting heterogeneous actions without instability, and (c) yields *end-to-end* safety + stability + bounded-regret proofs from component guarantees. Closing it requires a contract language for self-driving modules, a coordinator with provable anti-oscillation, and a compositional verification methodology tolerant of *learned* components (propagating distribution-free uncertainty).

## 7. Current Research (as of June 2026)
- Holistic self-driving prototypes coordinating multiple actions with shared cost models (NoisePage lineage, modeling work). *(frontier — verify)*
- LLM-agent "autonomous DBA" architectures orchestrating tools (forecast, advise, apply, verify) with planning loops. *(frontier — verify)*
- Compositional / conformal uncertainty propagation across learned DB pipelines; MPC-style tuning. Groups: CMU (Pavlo), MIT/Berkeley (learned systems), Microsoft, TU Munich/HPI/Darmstadt. *(frontier — verify)*

## 8. Future Work
- A contract/interface specification for forecast-plan-act-monitor modules with composable guarantees.
- Coordinator algorithms with provable stability (no thrashing) over heterogeneous, resource-sharing actions.
- End-to-end verification methodology tolerant of learned components and distribution shift.
- Integration with the other problems here: online-reconfiguration safety, multi-tenant constraints, adversarial robustness, and trust-calibrated human oversight as first-class architectural concerns.

## 9. Key References
- **[Foundational/Survey]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/PavloAALLMMMPQS17.html)
- **[SOTA]** L. Ma, D. Van Aken, A. Hefny, G. Mezerhane, A. Pavlo, G. Gordon. *Query-based Workload Forecasting for Self-Driving Database Management Systems (QueryBot 5000).* SIGMOD, 2018. — [DOI](https://doi.org/10.1145/3183713.3196908)
- **[SOTA]** L. Ma et al. *MB2: Decomposed Behavior Modeling for Self-Driving Database Management Systems.* SIGMOD, 2021. — [DOI](https://doi.org/10.1145/3448016.3457276)
- **[Foundational]** D. Q. Mayne, J. B. Rawlings, C. V. Rao, P. O. M. Scokaert. *Constrained Model Predictive Control: Stability and Optimality.* Automatica, 2000. — [DOI](https://doi.org/10.1016/S0005-1098(99)00214-9)
- **[Foundational]** R. Alur, T. Henzinger. *Reactive Modules / Assume-Guarantee Reasoning.* Formal Methods in System Design, 1999. — [DOI](https://doi.org/10.1023/A:1008739929481)
- **[SOTA]** T. Lykouris, S. Vassilvitskii. *Competitive Caching with Machine Learned Advice.* JACM, 2021. — [DOI](https://doi.org/10.1145/3447579)

## 10. Worked Example

**Two composed loops that oscillate.** A *knob loop* sets buffer-pool size; an *index loop* adds/drops indexes. Suppose the workload alternates between scan-heavy and point-lookup phases, and the monitor reports cache hit-rate every 5 s. The index loop, seeing low hit-rate, builds a covering index $I$ (build cost = 30 s). Once $I$ exists, fewer pages are read, hit-rate rises, so the knob loop *shrinks* the buffer pool to "reclaim" memory. With less buffer, the next scan phase shows low hit-rate again, so the index loop builds *another* index — and the knob loop shrinks again. The two locally-stable controllers form an unstable composite: action cost paid every cycle with no net SLO gain (thrashing).

An MPC coordinator over horizon $H=3$ avoids this by planning jointly. With forecast error $\epsilon$, receding-horizon cost obeys $\mathrm{cost}_{\text{MPC}} \le \mathrm{OPT} + O(\epsilon H)$. Concretely, if per-cycle thrash cost is $30$ s and the clairvoyant optimum is $40$ s total over the window, the coordinated plan ("build $I$ once, hold buffer pool fixed") stays near $40$ s, whereas the uncoordinated loops accrue $40 + 3\times 30 = 130$ s — illustrating why composition needs an anti-oscillation coordinator, not just two correct parts.

---
*Part of the [DBMS Research catalog](../../README.md).*
