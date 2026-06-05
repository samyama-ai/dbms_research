# Consensus Throughput vs Tail Latency

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/throughput-tail-latency-tradeoff` · **Status:** empirically-open

## 1. Problem Statement
Replicated-log systems (Multi-Paxos, Raft, EPaxos, DAG-BFT) raise throughput by **batching** many client commands into one consensus instance, amortizing the fixed per-instance cost (rounds, fsyncs, signatures) over many commands. But batching makes an early-arriving command **wait** for the batch to fill or for a timer to fire, inflating its latency — and the *tail* (p99/p99.9) suffers most because a command can sit behind a full batch, a slow follower, or a leader-pipeline stall. The problem: characterize the **fundamental tension** between batching-for-throughput and **per-command tail latency**, and find scheduling/batching policies that are Pareto-optimal — or prove the achievable frontier. This is *empirically-open*: there is no agreed closed-form lower bound on tail latency at a given throughput on real hardware/networks.

Variants: optimization (minimize p99 latency subject to throughput $\ge \lambda$), online (choose batch size/timeout without future knowledge), and the queueing-theoretic decision ("is latency profile $\mathcal{L}$ achievable at load $\rho$?").

## 2. Mathematical Foundations
Model the leader's commit pipeline as a queue. Let per-instance overhead be $c$ (rounds + fsync + network), batch size $b$, command service add $s$ per command. Throughput $\approx b/(c + bs)$, saturating at $1/s$ as $b\to\infty$. A command's latency decomposes as $$\underbrace{T_{\text{batch}}}_{\text{wait to fill}} + \underbrace{T_{\text{queue}}}_{\text{pipeline backlog}} + \underbrace{T_{\text{commit}}}_{c}.$$ Under Poisson arrivals rate $\lambda$ and batching window $w$, expected batch-wait is $\sim w/2$ but the **tail** is governed by the *distribution* of $T_{\text{queue}}$, which by **Kingman's formula** blows up as utilization $\rho = \lambda s \to 1$: $$\mathbb{E}[T_{\text{queue}}] \approx \frac{\rho}{1-\rho}\cdot\frac{c_a^2 + c_s^2}{2}\, s,$$ with $c_a, c_s$ the coefficients of variation of arrivals and service. Tail latency is dominated by **straggler replicas** (one slow follower in a $f+1$-quorum delays commit) and by **head-of-line blocking** in the ordered log. EPaxos-style leaderless protocols trade a single-leader bottleneck for **dependency-graph** overhead, shifting the tail to conflict-resolution cost.

## 3. State of the Art (SOTA)
Systems-SOTA: adaptive batching in **etcd/Raft**, **NOPaxos/Speculative Paxos** (network-ordered, cuts a round), **Mencius** and **EPaxos** (load-balance the leader to raise throughput), **Compartmentalized Paxos** (Whittaker et al., VLDB 2021) which decouples the leader's roles to scale throughput without inflating latency, and DAG-BFT (**Narwhal/Bullshark**) which separates data dissemination from ordering to hit bandwidth-bound throughput while bounding latency to a few DAG rounds. Tail-mitigation SOTA borrows from request hedging and **quorum-of-fastest** reads to dodge stragglers. Theory-SOTA is thinner: queueing models exist but real systems deviate (bursty arrivals, GC pauses, fsync tails), so the problem is classed empirically-open.

## 4. Upper Bound
Achievable today: Compartmentalized/scaled Paxos and DAG-BFT reach **near-network-bandwidth throughput** while keeping median latency at a small constant number of round-trips; adaptive batching with a short timeout keeps p99 within a few times the median at moderate load ($\rho \lesssim 0.7$). With speculative/network-ordered protocols, the common-case commit is **one round trip**. These are the best measured operating points; no protocol provably dominates across the full $(\lambda, \text{p99})$ plane. Model: partially-synchronous crash (CFT) or partial-synchrony BFT, real datacenter networks.

## 5. Lower Bound
Per-command latency $\ge$ one round trip to a quorum (consensus round-trip lower bound, Lamport), plus at least one durable write if persistence is required. Queueing-theoretic tail divergence: as $\rho \to 1$, p99 latency grows **unboundedly** for any work-conserving scheduler (Kingman / heavy-traffic), so high throughput and bounded tail are *intrinsically* opposed near saturation. Straggler lower bound: with a $\lceil (n+1)/2\rceil$ quorum, commit waits for the **median** replica, so tail tracks the order statistics of replica delay. These are information/queueing-theoretic, not problem-specific artifacts. Model: asynchronous arrivals, partially-synchronous network.

## 6. The Gap
There is **no tight, agreed lower bound** on tail latency as a function of throughput on real systems — only the loose queueing asymptotics and the per-command round-trip floor. The gap is genuinely empirical: workloads are bursty and service times heavy-tailed (fsync, GC), so the clean $M/M/1$ intuition under-predicts the measured tail, while adversarial worst cases over-predict it. Closing it needs (a) a *realistic* stochastic model of replica/fsync/network tails validated against traces, and (b) batching/scheduling policies proven optimal *under that model*. Whether a single policy can be Pareto-optimal across load levels, or whether load-adaptive switching is necessary, is open.

## 7. Current Research (as of June 2026)
Active: **self-tuning** batch size and timeout via online learning/control theory (links to *Self-Tuning Consensus Parameters*); **straggler-resilient** quorums (flexible/witness replicas, hedged commits); DAG-BFT latency reduction (**Mysticeti**, Sailfish) cutting commit to ~1–2 rounds while keeping bandwidth-bound throughput; latency-SLO-aware admission control. Groups: Ports/Zhang lineage (UW), Whittaker/Hellerstein (Berkeley), Mysten Labs / Danezis (DAG-BFT), Aguilera (MSR). A 2025–2026 frontier applies *learned* schedulers that predict batch-fill and straggler probability to shave p99 *(frontier — verify)*.

## 8. Future Work
- A validated stochastic tail model yielding a tight throughput–p99 frontier.
- Provably Pareto-optimal adaptive batching across load regimes.
- Straggler-aware quorum selection with formal tail guarantees.
- Co-design with storage (fsync batching) and NIC offload to flatten the tail.

## 9. Key References
- **[Foundational]** Lamport, L. *The Part-Time Parliament (Paxos).* ACM TOCS, 1998. — [ACM](https://dl.acm.org/doi/10.1145/279227.279229)
- **[Foundational]** Kingman, J.F.C. *The Single Server Queue in Heavy Traffic.* Proc. Cambridge Phil. Soc., 1961. — [DOI](https://doi.org/10.1017/S0305004100036094)
- **[SOTA]** Moraru, I., Andersen, D., Kaminsky, M. *There Is More Consensus in Egalitarian Parliaments (EPaxos).* SOSP, 2013. — [ACM](https://dl.acm.org/doi/10.1145/2517349.2517350)
- **[SOTA]** Whittaker, M., et al. *Scaling Replicated State Machines with Compartmentalization.* VLDB, 2021. — [arXiv](https://arxiv.org/abs/2012.15762)
- **[SOTA]** Danezis, G., Kokoris-Kogias, L., Sonnino, A., Spiegelman, A. *Narwhal and Tusk: A DAG-based Mempool and Efficient BFT Consensus.* EuroSys, 2022. — [arXiv](https://arxiv.org/abs/2105.11827)
- **[Foundational]** Dean, J., Barroso, L.A. *The Tail at Scale.* CACM, 2013. — [ACM](https://dl.acm.org/doi/10.1145/2408776.2408794)

## 10. Worked Example

Leader pipeline with per-instance overhead $c=2\,\text{ms}$ (round-trip + fsync) and per-command service $s=0.1\,\text{ms}$. With batch size $b$, throughput is $b/(c+bs)$.

- $b=10$: $10/(2+1)=3.33$ Kcmd/s, batch-fill wait $\approx w/2$.
- $b=100$: $100/(2+10)=8.33$ Kcmd/s.
- $b\to\infty$: saturates at $1/s = 10$ Kcmd/s.

Bigger batches buy throughput but each command waits longer to fill the batch. Now load the queue: at utilization $\rho = \lambda s = 0.9$ with $c_a^2=c_s^2=1$ (Poisson-ish), Kingman gives

$$\mathbb{E}[T_{\text{queue}}] \approx \frac{\rho}{1-\rho}\cdot\frac{c_a^2+c_s^2}{2}\,s = \frac{0.9}{0.1}\cdot 1 \cdot 0.1 = 0.9\,\text{ms}.$$

Push to $\rho=0.99$ and the same formula yields $9.9\,\text{ms}$ — a $10\times$ blow-up from a 10% load increase. This is the heavy-traffic divergence ($\rho\to1$) that makes high throughput and bounded tail intrinsically opposed near saturation.

---
*Part of the [DBMS Research catalog](../../README.md).*
