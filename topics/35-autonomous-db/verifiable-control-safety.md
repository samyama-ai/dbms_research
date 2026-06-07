---
id: 35-autonomous-db/verifiable-control-safety
title: "Verifiable Safety of Control Loops"
topic: 35-autonomous-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Verifiable Safety of Control Loops

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/verifiable-control-safety` · **Status:** open

## 1. Problem Statement
A self-driving database is a **closed control loop**: a (often learned, possibly black-box) controller observes telemetry and issues actions that change the system, which feeds back new telemetry. The problem: provide **formal guarantees** that this loop **never drives the database into an unsafe state** — e.g., never exhausts disk via runaway index builds, never deadlocks via a configuration change, never oscillates (thrash), never violates an invariant (replica divergence, lock-budget overflow), regardless of workload.

Formally, model the closed loop as a (hybrid/stochastic) dynamical system with state $s_t$, controller $\pi$, transition $s_{t+1}=F(s_t,\pi(s_t),w_t)$ under disturbance (workload) $w_t\in W$. Let $\mathcal{U}$ be the unsafe set. We seek a certificate that the **reachable set** stays clear of $\mathcal U$:
$$\mathrm{Reach}(s_0,\pi,W)\cap \mathcal{U} = \varnothing,$$
or, probabilistically, $\Pr[\exists t: s_t\in\mathcal U]\le\delta$. Variants. **(i) Verification (decision):** given $\pi$ and $\mathcal U$, decide safety. **(ii) Synthesis:** construct a controller (or a runtime shield) that is provably safe by design. **(iii) Runtime certification:** a monitor that vetoes any unsafe action online (least-restrictive safe filter). Distinguishing feature vs. generic tuning: the goal is a **proof / certificate of an invariant**, not average performance.

## 2. Mathematical Foundations
- **Reachability analysis:** over-approximate $\mathrm{Reach}$ via zonotopes/Taylor models (continuous), or via model checking of a transition system (discrete) — safety = emptiness of intersection with $\mathcal U$.
- **Lyapunov / barrier certificates:** a **control barrier function (CBF)** $h$ with $h(s)\ge0\Leftrightarrow$ safe, and $\dot h \ge -\alpha(h)$, certifies forward-invariance of the safe set — the standard tool for "never leave safe region."
- **Safe RL via shielding:** a **shield** synthesized from a correct-by-construction automaton (temporal-logic safety game) overrides unsafe actions while letting the learner explore — guarantees an LTL safety property by construction (Alshiekh et al.).
- **Model checking / temporal logic:** invariants and liveness (no-thrash) expressed in LTL/CTL; verified over a system model.
- **Stochastic safety:** martingale/supermartingale certificates and concentration give $\Pr[\text{reach }\mathcal U]\le\delta$ bounds.
- **Abstract interpretation** for verifying neural controllers (sound over-approximation of network outputs).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Production autonomous tuners enforce safety **operationally**, not formally: **resource governors / guardrails**, regression-gated **monitored rollout with automatic rollback** (Azure SQL auto-indexing/auto-tuning), action whitelists, and reversibility constraints. These are engineering safeguards, *not* certified invariants. Self-driving-DBMS proposals (Pavlo CIDR 2017) call out safety/verification as an explicit open requirement.
- **Theory-SOTA:** From control/ML, **control barrier functions** (Ames et al.), **shielded RL** (Alshiekh et al., AAAI 2018), and **neural-network verification** (Reluplex/Marabou; Katz et al.) are the SOTA tools; none is yet specialized to DBMS control loops with end-to-end proofs.

## 4. Upper Bound
For a **finite-state** abstraction of the control loop, safety (an invariant / LTL safety property) is **decidable** and a least-restrictive safe **shield** is synthesizable in time polynomial in the product automaton size (safety games solvable in linear time in the arena; LTL synthesis 2-EXPTIME in formula size). For systems with a valid **control barrier function**, online safety filtering reduces to a per-step convex (QP) projection — $O(\text{poly})$ per action — guaranteeing forward-invariance of the certified safe set *under the assumed model*. Neural-controller safety on bounded inputs is verifiable by SMT/MILP (Reluplex/Marabou), giving sound yes/no certificates.

## 5. Lower Bound
- **Undecidability:** safety/reachability for general **hybrid** and unbounded-counter systems is **undecidable** (reachability for Minsky machines / general hybrid automata) — an exact, complete safety verifier for an arbitrary DBMS control loop cannot exist.
- **Complexity:** even for finite but succinct (factored) models, invariant verification is **PSPACE-hard**; reactive-synthesis of a safe controller from LTL is **2-EXPTIME-complete**.
- **NN verification hardness:** verifying ReLU-network properties is **NP-complete** (Katz et al.).
- **Distributional impossibility:** with unbounded/adversarial disturbance $W$ and an imperfect model, *no* certificate can guarantee zero-probability of unsafety — only $\delta$-bounds, and only as good as the model.

## 6. The Gap
**Wide open.** Formal machinery (barrier functions, shields, model checking, NN verification) exists and is tight *for the models it assumes*, but applying it to self-driving databases founders on (a) **no faithful dynamical model** of how a configuration change propagates to latency/resource state; (b) **high-dimensional, partially-observed, non-stationary** state; (c) **learned black-box controllers** whose reachable behavior is hard to bound; (d) the undecidability/PSPACE walls for realistic state spaces. The gap between "we can verify a toy finite abstraction" and "we certify a production learned tuner never crashes the DB" is essentially uncrossed. Closing it needs sound, scalable abstractions of DBMS dynamics plus shields/barriers proven against them.

## 7. Current Research (as of June 2026)
Threads: (a) **runtime shielding / safe filters** wrapping learned tuners — vetoing actions that a (conservative) model predicts could violate an invariant *(frontier — verify)*; (b) **control-barrier-function** style guards for resource-exhaustion and thrash invariants; (c) **conformal / statistical safety certificates** giving distribution-free $\delta$-bounds when no white-box model exists; (d) digital-twin / simulator-based reachability before committing actions. Groups: Pavlo/CMU (self-driving DBMS), formal-methods + safe-RL communities (Topcu/UT Austin shielded RL, Ames/Caltech CBFs, Katz/Barrett on NN verification), Krause/ETH (safe learning). Largely a *theory-meets-systems frontier* with few end-to-end DBMS results.

## 8. Future Work
- Sound, tractable abstractions of DBMS control dynamics suitable for reachability/barrier certificates.
- Provably least-restrictive shields for learned tuners with bounded performance loss.
- Distribution-free runtime safety certificates (conformal) under workload drift.
- Compositional verification across the tuning, scheduling, and recovery loops (no harmful interaction).

## 9. Key References
- **[Foundational]** A. D. Ames, S. Coogan, M. Egerstedt, G. Notomista, K. Sreenath, P. Tabuada. *Control Barrier Functions: Theory and Applications.* European Control Conference, 2019. — [PDF](https://coogan.ece.gatech.edu/papers/amesecc19.html)
- **[SOTA]** M. Alshiekh, R. Bloem, R. Ehlers, B. Könighofer, S. Niekum, U. Topcu. *Safe Reinforcement Learning via Shielding.* AAAI, 2018. — [arXiv](https://arxiv.org/abs/1708.08611)
- **[SOTA]** G. Katz, C. Barrett, D. Dill, K. Julian, M. Kochenderfer. *Reluplex: An Efficient SMT Solver for Verifying Deep Neural Networks.* CAV, 2017. — [arXiv](https://arxiv.org/abs/1702.01135)
- **[Foundational]** R. Alur et al. *The Algorithmic Analysis of Hybrid Systems.* Theoretical Computer Science, 1995. — [PDF](https://www.cis.upenn.edu/~alur/TCS95.pdf)
- **[Survey]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [PDF](https://www.cidrdb.org/cidr2017/papers/p42-pavlo-cidr17.pdf)

## 10. Worked Example

Consider a disk-usage invariant. Let state $s_t$ = free disk in GB. The tuner's actions: build an index ($-20$ GB) or drop one ($+20$ GB); background ingest consumes $5$ GB/round (the disturbance $w_t\in[3,7]$, worst case $7$). Unsafe set $\mathcal U=\{s<0\}$ (disk full).

Define a barrier $h(s)=s$ (safe $\Leftrightarrow h\ge0$). The shield admits action $a$ only if the worst-case next state stays safe: $s_t - 20\cdot\mathbb 1[\text{build}] - 7 \ge 0$.

Trace from $s_0=30$: the learned tuner proposes "build index." Worst-case successor $=30-20-7=3\ge0$ — admitted. Now $s_1=30-20-5=5$. Next round it again proposes "build": worst-case $5-20-7=-22<0$ — the shield **vetoes** it and substitutes the least-restrictive safe action (skip build), so $s_2=5-5=0$, still safe.

This shows forward-invariance: the reachable set never enters $\mathcal U$ *under the assumed model*. The catch (section 6): if real ingest spikes to $12$ GB (outside $W=[3,7]$), the certificate breaks — the guarantee is only as sound as the disturbance bound, the heart of the modeling gap.

---
*Part of the [DBMS Research catalog](../../README.md).*
