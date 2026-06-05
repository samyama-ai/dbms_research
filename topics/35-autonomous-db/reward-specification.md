# Reward / Objective Specification

> **Topic:** Self-Driving / Autonomous Databases · **ID:** `35-autonomous-db/reward-specification` · **Status:** open

## 1. Problem Statement
A self-driving DBMS controller acts (index creation, knob settings, partitioning, replica placement) to optimize an operator-supplied objective. The **reward-specification problem** asks: how do we encode true operator intent—a multi-objective, often non-stationary mix of latency percentiles, throughput, cost ($), durability/SLA penalties, and stability—into a scalar (or vectorial) reward $R$ such that the optimal policy under $R$ coincides with the intended behavior, *without reward hacking* (the agent exploiting an unintended high-reward region) or *perverse optima* (degenerate configurations that score well but are operationally useless, e.g., dropping all indexes to minimize maintenance cost).

Variants:
- **Decision:** given a candidate reward $R$ and a target policy $\pi^\*$, is $\pi^\*$ optimal under $R$? (Inverse-RL feasibility.)
- **Optimization:** find $R$ minimizing the gap between $\arg\max_\pi J_R(\pi)$ and the operator's true preference $\succeq$.
- **Counting / identifiability:** how many reward functions are consistent with observed operator demonstrations / preference labels (the IRL reward-ambiguity question)?

## 2. Mathematical Foundations
Model the DBMS as a Markov Decision Process $\mathcal{M}=(S,A,P,R,\gamma)$ where $S$ is workload+configuration state, $A$ tuning actions, $P$ transition dynamics. The agent maximizes $J_R(\pi)=\mathbb{E}_\pi[\sum_t \gamma^t R(s_t,a_t)]$.

True operator intent is a (partial) preference order $\succeq$ over trajectories; reward design seeks $R$ with $J_R(\tau)\ge J_R(\tau') \iff \tau\succeq\tau'$. The core obstruction is **reward ambiguity**: by Ng & Russell (2000), reward shaping via potential functions $R'=R+\gamma\Phi(s')-\Phi(s)$ leaves the optimal policy invariant, so demonstrations identify $R$ only up to a potential-shaping equivalence class. Conversely, *misspecified* $R$ admits **reward hacking**, formalized as a policy $\pi$ with $J_R(\pi)\gg J_R(\pi^\*)$ but $U(\pi)\ll U(\pi^\*)$ under the true utility $U$.

Multi-objective scalarization $R=\sum_i w_i r_i$ only recovers the Pareto front under convexity; for non-convex fronts, linear weights provably miss optima (Das & Dennis). Constrained-MDP formulations ($\max J_{R}$ s.t. $J_{c_i}\le b_i$) avoid weight-tuning but require feasibility and Slater-type conditions for strong duality.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** OtterTune (Van Aken et al., SIGMOD 2017) uses latency/throughput targets directly; CDBTune (Zhang et al., SIGMOD 2019) and QTune (Li et al., VLDB 2019) use hand-crafted RL rewards combining throughput and latency deltas. Peloton/NoisePage (Pavlo et al., CIDR 2017) frames "self-driving" forecast-then-act control. UDO (Wang et al., VLDB 2021) unifies online/offline tuning with a single objective.
- **Reward design:** Constrained-RL and preference-based RL (RLHF-style pairwise labels) are emerging in tuning to sidestep manual scalarization.
- **Theory-SOTA:** Inverse RL (Ng & Russell 2000; Ziebart et al. MaxEnt IRL 2008) characterizes the consistent-reward set; recent work on reward identifiability under entropy regularization (Cao et al., 2021) sharpens uniqueness conditions.

## 4. Upper Bound
For finite MDPs, the consistent-reward polytope is computable by LP (Ng & Russell), giving polynomial time to *test* optimality of a target policy. MaxEnt IRL recovers a reward maximizing demonstration likelihood; under entropy regularization the reward is identifiable up to a constant shift and potential shaping, a provable narrowing of the ambiguity class. Preference-based learning attains sample complexity $\tilde{O}(d/\epsilon^2)$ for a $d$-dimensional linear reward to within $\epsilon$ regret (Pacchiano et al.), in the bandit/dueling model.

## 5. Lower Bound
Reward ambiguity is fundamental: infinitely many rewards (the full potential-shaping class) induce the same optimal policy, so **no finite demonstration set point-identifies $R$** (information-theoretic). Choosing weights to realize an arbitrary point on a non-convex Pareto front is NP-hard in general (reduces to scalarized multi-objective optimization). Robust reward design against worst-case misspecification inherits hardness of robust MDPs, which are NP-hard for general uncertainty sets (Wiesemann et al., 2013).

## 6. The Gap
The gap is conceptual, not just quantitative. We can *test* and *bound* reward consistency, but we lack a principled, system-grounded specification language that (a) provably excludes perverse optima (e.g., index-thrash, knob-flapping) and (b) certifies absence of reward hacking under bounded model error. No tight characterization links operator SLAs to potential-shaping-invariant rewards. The problem is genuinely open: closing it requires either a canonical-form reward (a chosen representative of the equivalence class with operational guarantees) or verified constrained-MDP encodings.

## 7. Current Research (as of June 2026)
- Constrained and preference-based RL for tuning, replacing hand-weighted scalar rewards *(frontier — verify)*.
- "Specification-by-SLA" compilers translating latency/cost SLOs into constrained-MDP objectives with feasibility checks.
- Reward-hacking detection via shielding and conservative/pessimistic value estimates carried over from offline RL.
- Groups: CMU (Pavlo, self-driving DB line), the OtterTune lineage, Tsinghua/MSRA (Li, Zhou) on RL tuning, and AI-safety reward-design work (Hadfield-Menell, Krueger) increasingly cited in DB venues.

## 8. Future Work
- A formal taxonomy of perverse optima specific to storage/indexing/knob actions and reward terms that provably exclude them.
- Identifiability theory tying operator preference elicitation budget to reward uniqueness.
- Online detection certificates for reward hacking with bounded false-alarm rate.
- Composable multi-tenant objectives with fairness/priority constraints.

## 9. Key References
- **[Foundational]** A. Ng, S. Russell. *Algorithms for Inverse Reinforcement Learning.* ICML, 2000. — [DBLP](https://dblp.org/rec/conf/icml/NgR00.html)
- **[Foundational]** B. Ziebart, A. Maas, J. A. Bagnell, A. Dey. *Maximum Entropy Inverse Reinforcement Learning.* AAAI, 2008. — [DBLP](https://dblp.org/rec/conf/aaai/ZiebartMBD08.html)
- **[SOTA]** D. Van Aken, A. Pavlo, G. Gordon, B. Zhang. *Automatic Database Management System Tuning Through Large-scale Machine Learning.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064029)
- **[SOTA]** J. Zhang et al. *An End-to-End Automatic Cloud Database Tuning System Using Deep Reinforcement Learning (CDBTune).* SIGMOD, 2019. — [DOI](https://doi.org/10.1145/3299869.3300085)
- **[SOTA]** A. Pavlo et al. *Self-Driving Database Management Systems.* CIDR, 2017. — [DBLP](https://dblp.org/rec/conf/cidr/PavloAALLMMMPQS17.html)
- **[Survey]** W. Wiesemann, D. Kuhn, B. Rustem. *Robust Markov Decision Processes.* Mathematics of Operations Research, 2013. — [DOI](https://doi.org/10.1287/moor.1120.0566)

## 10. Worked Example

Take a single-step reward $R = w_1\,(\text{throughput}) - w_2\,(\text{index-maintenance cost})$ and watch a **perverse optimum** emerge. Suppose configurations:

| config | throughput | maint. cost | $R$ at $w_1{=}1, w_2{=}1$ |
|---|---|---|---|
| $A$: full index set | 1000 | 300 | $700$ |
| $B$: minimal indexes | 600 | 40 | $560$ |
| $C$: **no indexes** | 200 | 0 | $200$ |

Here $A$ wins, fine. But the operator *truly* cares about throughput, with maintenance only a soft tiebreaker. If a careless operator sets $w_2 = 4$ to "discourage bloat," the scores become $A: 1000-1200=-200$, $B: 600-160=440$, $C: 200-0=200$ — now $B$ wins and, worse, raising $w_2$ to $7$ makes $C$ (drop *all* indexes) optimal at $R=200$ vs $A$'s $-1100$. The agent "reward-hacks" by minimizing the penalty term, exactly the index-thrash degenerate optimum of Section 1.

The constrained-MDP fix avoids weight guessing: $\max(\text{throughput})$ s.t. $\text{maint. cost}\le 250$. That selects $A$ (feasible, highest throughput) and provably never returns $C$. Note also that Ng–Russell potential shaping ($R' = R + \gamma\Phi(s') - \Phi(s)$) would leave this ranking unchanged — illustrating the reward-ambiguity class of Section 2.

---
*Part of the [DBMS Research catalog](../../README.md).*
