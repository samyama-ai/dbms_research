# Optimistic vs Pessimistic Crossover Prediction

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/occ-2pl-crossover` · **Status:** empirically-open

## 1. Problem Statement
Optimistic concurrency control (OCC) wins under low contention (no locking overhead, no deadlocks) but wastes work on aborts/restarts under high contention; two-phase locking (2PL) is the reverse. There exists, for each workload, a **crossover point** in contention space where the throughput curves cross. The problem:

> Given a live workload, **predict online** the contention level at which OCC overtakes 2PL (and vice versa), accurately enough to switch protocols (or tune a hybrid) before throughput collapses.

Variants:
- **Decision variant:** At time $t$, decide whether OCC or 2PL yields higher throughput for the *current* arrival/conflict process.
- **Optimization variant:** Choose, per transaction or per partition, the protocol/mix maximizing expected goodput minus switching cost.
- **Prediction (regret) variant:** Minimize cumulative regret of an online policy versus the best fixed-in-hindsight protocol on a possibly adversarial workload sequence.

This is "empirically-open": no closed-form, workload-portable predictor with guarantees exists; current answers are measured per-system.

## 2. Mathematical Foundations
Model contention by a conflict probability $p$ (probability two concurrent transactions conflict), multiprogramming level $n$, and transaction length $k$ operations. Classic analytic models (Tay–Goodman–Suri; Agrawal–Carey–Livny) give throughput as a function of $(n,p,k)$. Under OCC, expected restarts grow roughly as a function of the *data-contention* $\approx \binom{n}{2}p$; throughput exhibits **thrashing** — a non-monotone curve peaking then collapsing as $n$ rises. 2PL throughput degrades more gracefully but pays blocking/deadlock: deadlock probability $\approx \frac{n^2 k^4}{4 D}$ (Gray et al.) for $D$ lockable items.

The crossover is the $p^\*$ (or $n^\*$) solving $\Theta_{OCC}(n,p,k) = \Theta_{2PL}(n,p,k)$. The online prediction problem is to estimate the relevant latent parameters $(p, k, \text{skew})$ from a stream and map to $p^\*$ — an instance of **online model selection / experts** with switching costs, where regret bounds (e.g. from the *follow-the-perturbed-leader* or contextual-bandit literature) are the natural yardstick.

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Analytic queueing/Markov models (Tay 1987; Yu–Dias–Lavenberg, JACM 1993; Thomasian's hybrid analyses) characterize crossover *offline* given parameters, but assume stationarity and uniform access.
- **Systems-SOTA:** *Adaptive/hybrid* engines: the "Staring into the Abyss" study (Yu et al., VLDB 2014) maps protocol performance across core counts and contention; *MOCC* (Wang–Kimura, VLDB 2016) blends OCC with selective pessimistic locking on hot records; *IC3* and *Bamboo* (SIGMOD 2021) reorder/retire to cut 2PL blocking; *Polyjuice* (Wang et al., OSDI 2021) **learns** per-access concurrency-control actions via RL, effectively learning the crossover policy empirically. Tebaldi/CormCC compose protocols per partition.

## 4. Upper Bound
No provable competitive ratio is established for online protocol selection in the general adversarial model. The best *practical* upper bound is set by hybrids that approach the per-record optimum: MOCC and Polyjuice empirically track the better of OCC/2PL across the contention range, but their guarantees are experimental, not worst-case. Learning-based selectors (Polyjuice) reach near-best fixed-policy goodput on trained distributions — an empirical, distribution-dependent bound.

## 5. Lower Bound
Online protocol switching with switching cost is at least as hard as **metrical task systems / ski-rental**, giving a classical competitive lower bound of $2$ (deterministic) for the simplest two-state switch; against an *adaptive adversary* that flips contention to defeat the predictor, no constant-competitive guarantee can hold without restricting the workload. No fine-grained or information-theoretic lower bound specific to CC-crossover is published; the hardness is *prediction under distribution shift*, not computation.

## 6. The Gap
The gap is between rich *offline* analytic crossover models (need stationary, known parameters) and *online reality* (bursty, skewed, shifting hotspots). It is genuinely open: we lack (a) a workload-portable predictor with regret/competitive guarantees, and (b) agreement on the right feature set (conflict rate, abort rate, lock-wait time, hotspot entropy) that suffices to predict $p^\*$. Closing it needs an online-learning formulation with proven regret under bounded distribution drift plus a validated lightweight estimator.

## 7. Current Research (as of June 2026)
Active: RL/contextual-bandit concurrency control (Polyjuice lineage), per-record/per-partition adaptive escalation, and ML cost models feeding the optimizer. *(frontier — verify)* 2025–2026 work on transformer/feature-based contention forecasters and on "self-driving" DBMS (CMU NoisePage successors, Peloton lineage) selecting CC online, and theoretical regret analyses of CC selection as a switching-cost online problem, appear to be emerging frontiers.

## 8. Future Work
- A regret-bounded online selector robust to hotspot drift.
- Cheap, universal contention features predictive across engines.
- Fine-grained (sub-transaction, per-access) hybrid policies with analyzable behavior.

## 9. Key References
- **[Foundational]** Agrawal, Carey, Livny. *Concurrency Control Performance Modeling: Alternatives and Implications.* TODS, 1987. — [DOI](https://doi.org/10.1145/32204.32220)
- **[Foundational]** Gray, Homan, Korth, Obermarck. *A Straw Man Analysis of the Probability of Waiting and Deadlock.* IBM RJ, 1981. — [DBLP search](https://dblp.org/search?q=Straw+Man+Analysis+Probability+Waiting+Deadlock)
- **[SOTA]** Yu, Bezerra, Pavlo, Devadas, Stonebraker. *Staring into the Abyss: An Evaluation of Concurrency Control with One Thousand Cores.* VLDB, 2014. — [DOI](https://doi.org/10.14778/2735508.2735511)
- **[SOTA]** Wang, Kimura. *Mostly-Optimistic Concurrency Control for Highly Contended Dynamic Workloads (MOCC).* VLDB, 2016. — [DOI](https://doi.org/10.14778/3015274.3015276)
- **[SOTA]** Wang, Ding, Wang, Christensen, Wang, Chen, Li. *Polyjuice: High-Performance Transactions via Learned Concurrency Control.* OSDI, 2021. — [arXiv](https://arxiv.org/abs/2105.10329)
- **[Survey]** Thomasian. *Concurrency Control: Methods, Performance, and Analysis.* ACM Computing Surveys, 1998. — [DOI](https://doi.org/10.1145/274440.274443)

## 10. Worked Example

Take $n=10$ concurrent transactions, each touching $k=4$ items out of $D=1000$. The per-pair conflict probability is $p \approx k^2/D = 16/1000 = 0.016$. Expected conflicting pairs $\approx \binom{10}{2}p = 45 \cdot 0.016 = 0.72$.

- **2PL side:** deadlock probability $\approx \dfrac{n^2 k^4}{4D} = \dfrac{100 \cdot 256}{4000} = 6.4$ — already $>1$, so the straw-man estimate signals heavy waiting/deadlock; throughput is blocking-limited.
- **OCC side:** with $\approx 0.72$ expected conflicts, most transactions validate cleanly; abort/restart waste is small, so OCC's no-lock fast path wins here.

Now scale to $n=50$: OCC conflicts $\approx \binom{50}{2}\cdot0.016 = 1225\cdot0.016 \approx 19.6$ expected conflicting pairs — restart cascades dominate and OCC thrashes, while 2PL (despite blocking) degrades more gracefully. Somewhere between $n=10$ and $n=50$ lies the crossover $n^\*$; predicting it online from the live conflict-rate stream is exactly the open problem.

---
*Part of the [DBMS Research catalog](../../README.md).*
