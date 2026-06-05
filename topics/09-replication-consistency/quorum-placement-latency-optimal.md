# Latency-optimal quorum placement on real topologies

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/quorum-placement-latency-optimal` · **Status:** empirically-open

## 1. Problem Statement

Given a set of candidate datacenter/region locations with a (time-varying, asymmetric) inter-region latency matrix and a client-population distribution, choose (a) where to place $n$ replicas of a partition and (b) how to configure read/write quorums (sizes, or general quorum *systems* / flexible quorums) so as to minimize an objective on operation latency — typically a high percentile (p99) of write-commit and read latency subject to a fault-tolerance constraint (survive $f$ region failures) and capacity constraints.

Variants:
- **Decision:** "Does a placement achieving p99 write latency $\le L$ with $f$-fault-tolerance exist?"
- **Optimization:** minimize expected or tail latency (single objective) or trace the read/write Pareto frontier.
- **Online/adaptive:** latency matrices drift hourly; reconfigure placement to track the optimum while bounding reconfiguration cost (a metrical-task-system / online facility relocation flavor).
- **Counting/robustness:** number of placements within $\epsilon$ of optimum, or robustness to adversarial latency perturbation.

The "empirically-open" status reflects that no deployed system reliably attains tail-latency-optimal configurations on real, drifting WAN topologies; offline optimal computation is tractable at small $n$, but the *online, percentile, mis-estimated-matrix* version is unsolved in practice.

## 2. Mathematical Foundations

Model regions as a complete weighted digraph $G=(V,E)$ with latency $d_{uv}(t)$ (one-way, asymmetric, time-varying). A leader-based write to a replica set $R\subseteq V$ with quorum system $\mathcal{Q}$ commits when a write quorum $W\in\mathcal{Q}_W$ acks; for a leader $\ell$ and quorum $Q$, latency is the **$k$-th smallest round-trip**:
$$\text{lat}(\ell,Q) = \operatorname*{select}_{|W|}\big\{\, d_{\ell u}+d_{u\ell} : u\in Q \,\big\}.$$
With clients weighted $w_c$ and routed to nearest leader, the objective is $\sum_c w_c \cdot \text{lat}(c,\cdot)$ or a percentile of the induced latency distribution.

This generalizes **$k$-median / facility location** (NP-hard, but $O(1)$-approximable via LP rounding / local search, Charikar–Guha and Arya et al.) — but the *quorum* objective selects the $k$-th nearest, not the nearest, breaking the metric/submodular structure that classic facility-location approximations exploit. Fault-tolerance ($f$ failures) imposes an **intersection/availability** constraint on $\mathcal{Q}$ (Garcia-Molina–Barbara quorum systems; Naor–Wool load/availability tradeoffs). Flexible Paxos (Howard et al.) relaxes the constraint to "every write quorum intersects every read quorum," enlarging the design space.

## 3. State of the Art (SOTA)

- **Systems:** Spanner (Corbett et al., OSDI 2012) places replicas per-policy with Paxos; Volley (Agarwal et al., NSDI 2010) does data placement from access logs; SpaNStore (Wu et al., SOSP 2013) and Tuba (Ardekani–Terry, 2014) adapt replica placement/primary to minimize cost+latency under SLAs. EPaxos (Moraru et al., SOSP 2013) and its successors (e.g., Tempo, Atlas) reduce wide-area commit to one round-trip to the nearest fast quorum, making *which* quorum is "near" the placement question.
- **Configuration search:** PaxosStore and "WAN-optimized" Raft variants; recent autotuners frame placement as black-box/Bayesian optimization over the latency matrix.
- **Theory:** facility-location and $k$-center approximations; quorum-system constructions (grid, tree, Paths) with provable load/availability.

## 4. Upper Bound

Offline, for fixed small $n$ the optimum is computable by exhaustive enumeration in $O\!\big(\binom{|V|}{n}\cdot \text{poly}\big)$ — practical for $|V|\le 30$, $n\le 7$. For the mean-latency placement-only relaxation, metric facility-location LP rounding gives constant-factor approximations; local search yields a $(3+\epsilon)$-approximation for $k$-median, transferring to mean-latency leader placement. No constant-factor approximation is known for the **p99/tail** quorum objective; best practical results are heuristic (greedy + simulated annealing / Bayesian optimization) with no ratio guarantee.

## 5. Lower Bound

Placement subsumes metric $k$-median, hence is **NP-hard**, and $k$-median is APX-hard (hard to approximate below $1+2/e\approx 1.736$, Jain–Mahdian–Saberi / Guha–Khuller). The tail-percentile and asymmetric-latency variants are at least as hard. The *online* version inherits competitive lower bounds from metrical task systems / online facility location ($\Omega(\log n)$ competitive). Under matrix mis-estimation, no algorithm can guarantee optimality (information-theoretic: the true future matrix is unobserved) — a fundamental barrier, not just complexity.

## 6. The Gap

For **mean** latency the gap is essentially closed (constant-factor approx, matching APX-hardness up to the constant). For **tail latency on drifting, asymmetric matrices** the gap is wide and genuinely open: there is no approximation algorithm with a proven ratio for p99, and no online algorithm that provably tracks the moving optimum under measurement noise. Closing it requires either (i) a tail-aware objective amenable to LP/SDP rounding, or (ii) a learning-augmented online algorithm with consistency/robustness bounds for the quorum-select objective.

## 7. Current Research (as of June 2026)

Active threads: learning-augmented online placement (predictions + worst-case robustness, Mitzenmacher–Vassilvitskii lineage) applied to replica relocation *(frontier — verify)*; tail-latency-aware quorum selection inside leaderless protocols (Atlas/Tempo descendants) *(frontier — verify)*; and continuous reconfiguration informed by live latency telemetry rather than static policy. Groups around Microsoft Research (Flexible Paxos line), MPI-SWS, and cloud-provider research teams publish in OSDI/SOSP/NSDI. Robustness to adversarial/Byzantine latency reporting is an emerging sub-question.

## 8. Future Work

- A provable approximation for the p99 quorum-placement objective (open even offline).
- Online reconfiguration with bounded churn and consistency/robustness guarantees under noisy predictions.
- Joint optimization of placement, quorum system, *and* leader rotation (Mencius-style) for multi-leader tail latency.
- Benchmarks: a standard public corpus of real time-varying WAN latency matrices to make "empirically-open" claims falsifiable.

## 9. Key References

- **[Foundational]** Garcia-Molina, H., Barbara, D. *How to Assign Votes in a Distributed System.* JACM, 1985. — [DOI](https://doi.org/10.1145/4221.4223)
- **[Foundational]** Naor, M., Wool, A. *The Load, Capacity, and Availability of Quorum Systems.* SIAM J. Computing, 1998. — [DOI](https://doi.org/10.1137/S0097539795281232)
- **[SOTA]** Corbett, J. et al. *Spanner: Google's Globally-Distributed Database.* OSDI, 2012. — [DBLP](https://dblp.org/rec/conf/osdi/CorbettDEFFFGGHHHKKLLMMNQRRSSTWW12.html)
- **[SOTA]** Moraru, I., Andersen, D., Kaminsky, M. *There Is More Consensus in Egalitarian Parliaments (EPaxos).* SOSP, 2013. — [DOI](https://doi.org/10.1145/2517349.2517350)
- **[SOTA]** Howard, H., Malkhi, D., Spiegelman, A. *Flexible Paxos: Quorum Intersection Revisited.* OPODIS, 2016. — [DOI](https://doi.org/10.4230/LIPIcs.OPODIS.2016.25)
- **[Survey]** Agarwal, S. et al. *Volley: Automated Data Placement for Geo-Distributed Cloud Services.* NSDI, 2010. — [USENIX](https://www.usenix.org/conference/nsdi10-0/volley-automated-data-placement-geo-distributed-cloud-services)

## 10. Worked Example

Five regions $V=\{$us-e, us-w, eu, ap, sa$\}$; place $n=5$ replicas (one each) with a leader in **us-e** and a majority write quorum ($|W|=3$). Symmetric one-way latencies (ms) from us-e: us-e $0$, us-w $30$, eu $40$, ap $90$, sa $60$. Round-trip $=2\times$ one-way.

A write commits when the leader plus the 2 nearest followers ack — i.e. the **3rd-smallest** round-trip among all 5 (leader counts as RTT $0$). Sorted RTTs: $0, 60$ (us-w), $80$ (eu), $120$ (sa), $180$ (ap). The 3rd-smallest is $\text{lat}=80$ ms (waiting for eu).

Now move the leader to **eu** (central). New one-way from eu: eu $0$, us-e $40$, us-w $70$, sa $80$, ap $70$. RTTs sorted: $0, 80$ (us-e), $140$ (ap), $140$ (us-w), $160$ (sa); 3rd-smallest $=140$ ms — worse, because eu's two nearest neighbors are far.

So us-e leadership wins here ($80$ vs $140$ ms). Note the objective is a **select-3rd**, not a nearest-neighbor sum, which is exactly why classic $k$-median rounding does not directly apply.

---
*Part of the [DBMS Research catalog](../../README.md).*
