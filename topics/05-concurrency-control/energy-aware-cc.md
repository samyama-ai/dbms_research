# Energy-Optimal Concurrency Control

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/energy-aware-cc` · **Status:** open

## 1. Problem Statement

Concurrency control (CC) is traditionally tuned for throughput and latency; **energy** is a derived afterthought. But wasted work — aborted/restarted transactions under OCC, spinning on contended locks, cache-coherence traffic, idle cores held for blocked 2PL transactions — burns joules without committing transactions. This problem treats **energy per committed transaction (J/txn)** as a *first-class* CC objective: design and choose CC mechanisms (2PL, OCC, MVCC, deterministic) and their parameters (backoff, batch size, core allocation, voltage/frequency) to **minimize energy per commit** subject to throughput/latency/correctness constraints.

Variants: the **optimization** problem (minimize $\mathbb{E}[\text{J/committed txn}]$ given a workload and hardware power model); the **decision** problem (can energy budget $E$ sustain commit rate $\lambda$ at isolation level $L$?); the **online/competitive** problem (adapt CC policy and DVFS to a changing workload, competing against an offline energy optimum); the **scheduling** problem (place/consolidate transactions on cores to maximize energy proportionality without violating SLOs).

## 2. Mathematical Foundations

Model total energy over a window as

$$E = \int \big( P_{\text{static}} + P_{\text{dyn}}(f, v, u(t)) \big)\, dt, \qquad P_{\text{dyn}} \propto C\, v^2 f,$$

so dynamic power scales with the square of voltage $v$ times frequency $f$ (the classic CMOS relation), and utilization $u(t)$ couples to CC: aborts and lock-waits inflate the time-integral without increasing the committed count $N_c$. Define the metric $\eta = E / N_c$ (joules per commit). A CC policy induces a **commit efficiency** $\gamma = N_c / N_{\text{attempted}}$ (one minus the abort/restart fraction); to first order $\eta \approx E_{\text{work}}/(\gamma\, N_{\text{attempted}})$, so abort rate directly taxes energy. The DVFS trade-off is a convex **race-to-idle vs. crawl-to-deadline** problem: lowering $f$ cuts $P_{\text{dyn}}$ but extends active time and may worsen lock-hold durations and static-energy leakage; the energy-optimal frequency is interior and workload-dependent. Energy proportionality (Barroso & Hölzle) sets the ideal: power consumed $\propto$ useful work done.

## 3. State of the Art (SOTA)

**Systems-SOTA:** There is no widely adopted, energy-first CC engine; the field is nascent. Foundational empirical work includes Tsirogiannis, Harizopoulos, Shah (SIGMOD 2010), *"Analyzing the Energy Efficiency of a Database Server,"* which argued the most energy-efficient configuration is often the highest-performing one (race-to-idle), reframing energy as largely a performance-and-consolidation problem. Lang & Patel (and the broader "green databases" line) studied DVFS and query-level energy. Modern in-memory CC studies (e.g., the Yu/Bezerra/Pavlo/Devadas/Stonebraker 1000-core CC evaluation, VLDB 2014) implicitly expose where energy is wasted (abort storms, latch contention) even though they measure scalability rather than joules. Hardware-assisted CC (HTM, RDMA) and energy-aware scheduling in cloud OLTP are the practical levers.

## 4. Upper Bound

The strongest principled upper bound is **race-to-idle** plus consolidation: run at max efficient frequency, finish, and enter low-power idle, which empirically and analytically minimizes energy when static power and idle states dominate (Tsirogiannis et al.). Reducing wasted work gives a direct multiplicative gain: improving commit efficiency from $\gamma_1$ to $\gamma_2$ scales $\eta$ by $\gamma_1/\gamma_2$, so deterministic or contention-aware CC that cuts aborts under skew is provably more energy-efficient per commit on contended workloads. These bounds hold in measured RAM/server power models, not as asymptotic guarantees; the energy-optimal DVFS point is computable per workload by convex optimization.

## 5. Lower Bound

No clean complexity-theoretic lower bound exists; the obstructions are physical and combinatorial. **Static/leakage power** imposes a floor: while any transaction holds resources, $P_{\text{static}}$ is paid regardless of CC cleverness, so $\eta \ge P_{\text{static}} \cdot (\text{minimum critical-path time per commit})$. Under contention, the hot-key critical path (see deterministic-DB skew) lower-bounds active time and hence energy. Energy-optimal *online* policy selection (choosing CC + DVFS without knowing the future workload) is subject to standard competitive-ratio limits for online convex/metrical-task-system problems, and offline optimal placement/consolidation is **NP-hard** (bin-packing of transactions to power-managed cores).

## 6. The Gap

**Open.** Energy is rarely a *first-class* CC design objective, so there is neither an accepted J/txn benchmark nor matching upper/lower bounds in a shared model. We lack: a validated analytical model linking CC mechanism + contention + DVFS to J/txn; proof of when race-to-idle is genuinely optimal versus when contention-driven waste dominates; and online algorithms with competitive energy guarantees. The gap between Tsirogiannis-style "performance ≈ efficiency" guidance and contended, abort-heavy modern workloads (where wasted CC work, not idle power, dominates) is essentially unexplored.

## 7. Current Research (as of June 2026)

Drivers: datacenter carbon/energy pressure and the rise of energy- and carbon-aware scheduling are pulling CC into the conversation; **carbon-aware** transaction scheduling and frequency capping under power budgets are emerging *(frontier — verify)*. Relevant communities: sustainable-computing / "green data systems" researchers, the cloud-OLTP autotuning line (e.g., self-driving DB work at CMU on knob/resource tuning), and hardware-software co-design groups exploring HTM/RDMA/near-data CC for efficiency. Energy proportionality and accelerator (GPU/SmartNIC) offload of CC bookkeeping are active angles.

## 8. Future Work

- A standardized **J/txn** benchmark and validated energy model spanning 2PL/OCC/MVCC/deterministic CC.
- Online, workload-adaptive CC+DVFS policies with provable competitive energy ratios.
- Energy/carbon-aware transaction scheduling and consolidation with SLO constraints.
- Quantifying when reducing CC wasted work beats race-to-idle, with matching bounds.

## 9. Key References

- **[Foundational]** Tsirogiannis, D.; Harizopoulos, S.; Shah, M. *Analyzing the Energy Efficiency of a Database Server.* SIGMOD, 2010. — [DOI](https://doi.org/10.1145/1807167.1807194)
- **[Foundational]** Barroso, L. A.; Hölzle, U. *The Case for Energy-Proportional Computing.* IEEE Computer, 2007. — [DOI](https://doi.org/10.1109/MC.2007.443)
- **[SOTA]** Yu, X.; Bezerra, G.; Pavlo, A.; Devadas, S.; Stonebraker, M. *Staring into the Abyss: An Evaluation of Concurrency Control with One Thousand Cores.* PVLDB, 2014. — [DOI](https://doi.org/10.14778/2735508.2735511)
- **[SOTA]** Lang, W.; Patel, J. *Towards Eco-friendly Database Management Systems.* CIDR, 2009. — [arXiv](https://arxiv.org/abs/0909.1767)
- **[Survey]** Harizopoulos, S.; Shah, M.; Meza, J.; Ranganathan, P. *Energy Efficiency: The New Holy Grail of Data Management Systems Research.* CIDR, 2009. — [arXiv](https://arxiv.org/abs/0909.1784)
- **[Foundational]** Weiser, M.; Welch, B.; Demers, A.; Shenker, S. *Scheduling for Reduced CPU Energy (DVFS).* OSDI, 1994. — [USENIX](https://www.usenix.org/conference/osdi-94/scheduling-reduced-cpu-energy)

## 10. Worked Example

Compare two CC policies on a contended workload, attempting $N_{\text{att}} = 10{,}000$ transactions. Each attempt does $E_{\text{work}} = 5$ J of compute; static/leakage adds $P_{\text{static}} = 50$ W over the run.

- **OCC under skew:** commit efficiency $\gamma_1 = 0.5$ (half abort and retry). To get $N_c = 10{,}000$ commits we burn $20{,}000$ attempts $\times 5 = 100$ kJ of work. At $1000$ commits/s the run takes $20$ s, so static energy is $50 \times 20 = 1$ kJ. Total $\approx 101$ kJ, giving $\eta_1 = 101{,}000 / 10{,}000 = 10.1$ J/commit.
- **Deterministic CC:** $\gamma_2 = 0.95$. Attempts $\approx 10{,}526$, work $= 52.6$ kJ; faster run ($\approx 10.5$ s) gives $0.53$ kJ static. Total $\approx 53.2$ kJ, so $\eta_2 \approx 5.3$ J/commit.

The work-energy ratio matches the bound $\gamma_1/\gamma_2 = 0.5/0.95 \approx 0.53$: cutting aborts nearly halves J/commit, and here wasted CC work — not idle power — dominates the bill.

---
*Part of the [DBMS Research catalog](../../README.md).*
