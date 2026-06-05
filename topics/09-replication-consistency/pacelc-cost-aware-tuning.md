# Energy/cost-aware PACELC operating points

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/pacelc-cost-aware-tuning` · **Status:** empirically-open

## 1. Problem Statement

Abadi's **PACELC** refines CAP: if there is a **P**artition, a system trades **A**vailability vs **C**onsistency; **E**lse (normal operation) it trades **L**atency vs **C**onsistency. Most production stores expose this as discrete or continuous **knobs**: replication factor, read/write quorum sizes ($R$, $W$, $N$), consistency level (ONE / QUORUM / ALL / bounded-staleness), placement and routing, and (in the cloud) instance type and provisioned IOPS. Each setting fixes a point on a *latency × consistency × dollar/energy* surface.

The problem: **choose, per workload (and adaptively over time), the PACELC operating point that optimizes a stated objective — e.g. minimize \$/energy cost subject to a latency-SLO and a consistency-SLO (bounded staleness $\Delta$, or session/causal guarantees)** — given that the surface is non-stationary, the mapping from knobs to outcomes is system- and workload-specific, and measuring it is expensive.

Variants: (a) **decision** — does any feasible point meet all SLOs? (b) **single-objective optimization** — min cost s.t. latency $\le \tau$, staleness $\le \Delta$, availability $\ge a$; (c) **multi-objective** — recover the Pareto frontier of (cost, p99-latency, staleness); (d) **online/bandit** — track the optimum under drift without violating SLOs while exploring.

## 2. Mathematical Foundations

Let knob vector $x \in \mathcal{X}$ (mixed discrete/continuous). Unknown response functions give expected cost $c(x)$, tail latency $\ell_p(x)$, staleness $s(x)$, availability $a(x)$ under a workload $w$. The optimization is
$$\min_{x\in\mathcal{X}} \; c(x) \quad \text{s.t.}\quad \ell_p(x)\le \tau,\; s(x)\le \Delta,\; a(x)\ge a_0 .$$
The objective/constraints are **black-box, noisy, and expensive** to evaluate (each trial = a load test or a risky production change), motivating **Bayesian optimization / Gaussian-process** surrogates and **contextual multi-armed bandits** (context = workload features) with **constrained** / safe exploration (e.g. SafeOpt-style feasibility guarantees).

Quorum mechanics give partial structure: for an $N$-replica system, **bounded staleness** under $(R,W)$ relates to the **probabilistically bounded staleness (PBS)** model (Bailis et al., 2012), which predicts the probability a read sees a write $\Delta$ ago as a function of message-delay distributions — a closed form that can seed the surrogate instead of pure black-box search. Strong consistency requires $R+W>N$; relaxing it trades a quantifiable staleness for lower latency/cost. Energy adds a term: cost $\approx$ \$\,(\text{instances}) + \kappa\cdot(\text{energy})$, where energy scales with replication factor and write amplification.

## 3. State of the Art (SOTA)

- **PBS** (Bailis, Venkataraman, Hellerstein, Franklin, Stoica, VLDB 2012) quantifies the L-vs-C side of PACELC, giving staleness-vs-latency curves for Dynamo-style quorums — the analytical backbone.
- **Auto-tuning systems-SOTA:** OtterTune (Van Aken et al., SIGMOD 2017) and CDBTune/QTune (RL-based, VLDB 2019) tune DBMS knobs via ML/RL but target throughput/latency, *not* the consistency/cost axes jointly.
- **Tunable-consistency systems:** Cassandra/DynamoDB per-request consistency levels, Pileus/Tuba (Terry et al., SOSP 2013) which pick replicas to meet a **consistency-based SLA** and maximize utility — closest deployed work to cost-aware PACELC.
- No system jointly optimizes the *full* PACELC surface against an explicit dollar/energy budget; this is the empirically-open core.

## 4. Upper Bound

There is no clean asymptotic upper bound — the object is empirical. Practically: GP-based Bayesian optimization converges to a near-optimal feasible point in $O(\text{poly})$ trials with sublinear cumulative **regret** ($\tilde O(\sqrt{T})$ for GP-UCB under smoothness assumptions, Srinivas et al., 2010), and PBS closed forms let one *predict* much of the L–C surface without trials, collapsing the search. Constrained/safe BO bounds the SLO-violation probability during exploration. These hold in the **stochastic black-box optimization model** with smoothness (bounded RKHS norm) assumptions that real workloads only approximately satisfy.

## 5. Lower Bound

- **CAP/PACELC impossibility** is the hard structural lower bound: no operating point gives strong consistency *and* full availability under partition, so the feasible region can be empty for adversarial SLO combinations.
- **Information-theoretic:** any tuner must spend exploration to learn a non-stationary surface; bandit lower bounds give $\Omega(\sqrt{KT})$ regret for $K$ arms, $\Omega(\sqrt{T})$ for smooth GP settings — you cannot find the optimum "for free."
- Tail-latency vs consistency has queueing-theoretic floors (a synchronous QUORUM read's p99 is lower-bounded by the $\lceil (R{+}1)/2\rceil$-th order statistic of replica latencies), so cost reductions below that are infeasible without weakening consistency.

## 6. The Gap

The gap is not an upper-vs-lower asymptotic gap but a **modeling and generalization** gap: (1) no validated, transferable model mapping knobs → (cost, p99, staleness) across heterogeneous cloud hardware and shifting workloads; (2) energy/$ is poorly instrumented, so the objective is itself uncertain; (3) safe online retuning that never breaches SLOs during exploration is unsolved at production scale. PBS covers part of the L–C analytics but ignores cost/energy and tail interactions. Genuinely empirically-open.

## 7. Current Research (as of June 2026)

- **Carbon/energy-aware data systems**: scheduling and replica placement that fold grid carbon-intensity and \$ into the consistency tradeoff *(frontier — verify)* (work from the sustainable-computing and cloud-DB communities).
- Learned/contextual-bandit consistency-level selection per request, extending Pileus/Tuba with cost terms *(frontier — verify)*.
- LLM/RL-assisted autotuners extending OtterTune-style search to consistency knobs (Carnegie Mellon DB group lineage).
- Serverless/edge cost models where replication factor directly drives billing, making PACELC a first-class cost lever.

## 8. Future Work

- A standard, reproducible **benchmark** exposing the joint (consistency, latency, cost, energy) surface (a "PACELC-bench").
- Transferable surrogate models that generalize across hardware/workloads with few trials.
- Provably SLO-safe online retuning under drift (safe RL / constrained BO with guarantees).
- First-class **energy** accounting in replication protocols, not just dollars.

## 9. Key References

- **[Foundational]** Abadi, D. *Consistency tradeoffs in modern distributed database system design: CAP is only part of the story.* IEEE Computer, 2012. — [DOI](https://doi.org/10.1109/MC.2012.33)
- **[SOTA]** Bailis, P., Venkataraman, S., Hellerstein, J. M., Franklin, M. J., Stoica, I. *Probabilistically Bounded Staleness for practical partial quorums.* VLDB, 2012. — [DOI](https://doi.org/10.14778/2212351.2212359)
- **[SOTA]** Terry, D. B., Prabhakaran, V., Kotla, R., Balakrishnan, M., Aguilera, M. K., Abu-Libdeh, H. *Consistency-based service level agreements for cloud storage (Pileus/Tuba).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2522731)
- **[SOTA]** Van Aken, D., Pavlo, A., Gordon, G. J., Zhang, B. *Automatic database management system tuning through large-scale machine learning (OtterTune).* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3064029)
- **[Foundational]** Srinivas, N., Krause, A., Kakade, S., Seeger, M. *Gaussian process optimization in the bandit setting: no regret and experimental design.* ICML, 2010. — [arXiv](https://arxiv.org/abs/0912.3995)
- **[Foundational]** Gilbert, S., Lynch, N. *Brewer's conjecture and the feasibility of consistent, available, partition-tolerant web services.* ACM SIGACT News, 2002. — [DOI](https://doi.org/10.1145/564585.564601)

## 10. Worked Example

A Cassandra-style store with $N = 3$ replicas. Read/write knobs $(R, W)$ choose a PACELC point.

- **Strong (QUORUM/QUORUM):** $R = W = 2$. Then $R + W = 4 > N = 3$, so reads always intersect the latest write — staleness $0$. A QUORUM read's tail latency is the $2$nd-fastest of $3$ replica responses, i.e. the median order statistic. With per-replica latencies drawn as $\{8, 12, 40\}$ ms, p-latency $= 12$ ms.
- **Weak (ONE/ONE):** $R = W = 1$, $R + W = 2 \not> 3$ — a partial quorum. Read latency drops to the fastest replica, $8$ ms, but PBS now predicts a nonzero chance the read misses the freshest write. If write-to-read gap is short and inter-replica delay $\sim$ tens of ms, PBS might give "consistent within $\Delta = 10$ ms with prob. $0.94$."

The tuner's job: pick the point minimizing \$ subject to SLOs. If the consistency-SLO is "staleness $\le 10$ ms w.p. $\ge 0.99$," ONE/ONE's $0.94$ fails it, forcing QUORUM. If the SLO is looser ($\ge 0.90$), ONE/ONE is feasible and cheaper/faster. PBS lets the optimizer evaluate this *without* running a load test, collapsing the search.

---
*Part of the [DBMS Research catalog](../../README.md).*
