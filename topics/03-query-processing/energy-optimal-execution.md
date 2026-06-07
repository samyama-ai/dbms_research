---
id: 03-query-processing/energy-optimal-execution
title: "Energy-optimal query execution"
topic: 03-query-processing
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Energy-optimal query execution

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/energy-optimal-execution` · **Status:** empirically-open

## 1. Problem Statement

Choose and run query execution plans to minimize **energy** (joules), or a chosen
energy-delay objective, rather than time alone, across a heterogeneous machine with
big/little CPU cores, GPUs, FPGAs, SmartNICs, and DVFS-controllable frequency/voltage. Time
and energy are *not* the same objective: the fastest plan is often not the most efficient
(racing to idle vs. running slow-and-cool), and operator placement on a low-power core or
accelerator can cut energy at modest latency cost.

Formally: given a query, a plan space, and a hardware model with per-resource power
functions, choose a plan + operator placement + frequency settings minimizing energy
$\;E = \int P(t)\,dt\;$ subject to a latency bound, or minimizing a combined metric
$E\cdot T^{\alpha}$ (energy-delay product, $\alpha\ge 0$).

- **Decision variant:** is there a plan/placement/DVFS schedule with energy $\le E_0$ and
  latency $\le L_0$?
- **Optimization variant:** minimize $E$ (or $E\cdot T^\alpha$) over plans, placements, and
  frequencies.
- **Pareto variant:** characterize the energy–latency Pareto frontier and let policy pick a
  point.

It is **empirically-open**: there is no accurate, portable energy cost model for query
execution, and engines optimize for time with energy as an afterthought; the asymptotics
coincide with time-optimization, so the difficulty is constant-factor/modeling and
multi-objective scheduling.

## 2. Mathematical Foundations

Model a heterogeneous machine with resources $\{r\}$; running operator $o$ on resource $r$
at frequency $f$ takes time $t_{o,r}(f)$ and draws power $P_r(f) = P_r^{\text{static}} +
c_r f^{\gamma}$ (dynamic power grows roughly with $f^{\gamma}$, $\gamma\approx 2$–$3$ from
$P\propto C V^2 f$ with $V\propto f$). Energy of a plan is

$$E \;=\; \sum_{o} P_{r(o)}\!\big(f(o)\big)\cdot t_{o,r(o)}\big(f(o)\big) \;+\; P^{\text{static}}\cdot T_{\text{total}},$$

exposing the **race-to-idle vs. run-slow** tension: higher $f$ cuts $t$ but raises dynamic
power superlinearly, while static/leakage power favors finishing fast. With a latency
constraint this is a **constrained scheduling / assignment** problem. Energy-minimal speed
scaling has classical structure: **Yao–Demers–Shenker** (FOCS 1995) gives the optimal
continuous-speed schedule for jobs with deadlines under a convex power function, and
discrete heterogeneous placement is an **NP-hard assignment** (generalized
assignment/scheduling on unrelated machines). The relevant guarantees are therefore
**approximation/competitive** (e.g. constant-factor speed-scaling, $O(1)$-competitive online
algorithms), not exact.

## 3. State of the Art (SOTA)

- **Foundational measurement:** **Tsirogiannis, Harizopoulos, Shah**, *Analyzing the Energy
  Efficiency of a Database Server* (SIGMOD 2010) established the influential finding that,
  for a single server, **the most energy-efficient configuration is typically the
  highest-performing one** — energy and performance are largely aligned within one machine,
  so "race to idle" usually wins. **Lang & Patel** (*Towards Eco-friendly Database
  Management Systems*, CIDR 2009) and follow-ups studied DVFS/PVC trade-offs.
- **Systems SOTA:** energy-aware operator placement and DVFS in heterogeneous-DBMS prototypes
  (big.LITTLE, GPU/FPGA offload); cloud schedulers (carbon/energy-aware placement). FPGA
  and SmartNIC near-data processing reduces data-movement energy substantially.
- **Theory SOTA:** speed-scaling and energy-aware scheduling (Albers; Bansal–Kimbrel–
  Pruhs) provide the algorithmic backbone, though rarely instantiated in real query engines.

## 4. Upper Bound

- **Speed scaling:** for jobs with deadlines under a convex power function $P(f)=f^\gamma$,
  the **YDS** algorithm computes the energy-optimal continuous schedule in polynomial time;
  online variants are **$O(1)$-competitive** (constant depending on $\gamma$). This bounds
  the DVFS sub-problem optimally.
- **Heterogeneous placement:** approximation algorithms for scheduling on **unrelated
  machines** give constant-factor energy guarantees for fixed assignments; combined
  energy+latency objectives admit **bicriteria** $(1+\epsilon)$-type approximations in
  restricted settings.
- **In practice:** because intra-server energy tracks time (Tsirogiannis et al.),
  time-optimal plans are a *good* (often near-optimal) upper bound on energy for
  single-node, homogeneous workloads — the upper bound is empirical and workload-dependent.

## 5. Lower Bound

- **NP-hardness:** energy-minimal operator placement across heterogeneous resources subject
  to a latency bound is **NP-hard** (it generalizes unrelated-machine scheduling /
  generalized assignment), so no exact poly-time optimizer exists unless P = NP.
- **Physical floor:** dynamic energy per useful operation is bounded below by switching
  energy $\propto C V^2$; there is an irreducible energy to move $n$ bytes across an
  interconnect, $\Omega(n)\cdot$(per-byte transfer energy) — an information-/physics-level
  lower bound that placement can shift between resources but not eliminate.
- **Static-power floor:** leakage imposes $P^{\text{static}}\cdot T$ regardless of plan,
  bounding any "run slow" strategy from below and favoring race-to-idle — a structural lower
  bound on slow-execution savings.

## 6. The Gap

Asymptotically, energy- and time-optimization largely coincide on a single homogeneous
server, so the gap there is small (Tsirogiannis et al.). The real, open gap is in
**heterogeneous and multi-node** settings: we lack (a) a portable, accurate per-operator
energy cost model spanning CPU/GPU/FPGA/SmartNIC and DVFS states, and (b) a multi-objective
optimizer that places operators and sets frequencies on the energy–latency Pareto frontier
with provable guarantees. Without measured power models the optimizer cannot even rank plans
by energy. Closing it requires calibrated energy models, bicriteria approximation
algorithms instantiated in real engines, and validation that predicted energy matches the
wall plug.

## 7. Current Research (as of June 2026)

- **Carbon-/energy-aware cloud scheduling** (shifting work in time/space to greener energy)
  is a hot 2025–2026 direction, extending query scheduling to a carbon objective
  *(frontier — verify)*.
- **Near-data / in-network processing** (SmartNIC, computational storage, FPGA) to cut
  data-movement energy, and **heterogeneous big.LITTLE operator placement**
  *(frontier — verify)*.
- **Energy models for accelerated analytics** (GPU offload energy break-even vs. CPU),
  jointly with the GPU-execution problem in this topic *(frontier — verify)*.
- Groups: Patel (UW-Madison/now industry), Harizopoulos/Ailamaki lineage, and
  systems-for-sustainability efforts at several labs.

## 8. Future Work

- A standardized, portable energy cost model integrated into the optimizer's cost API.
- Bicriteria (energy, latency) plan search with approximation guarantees on real hardware.
- DVFS + placement co-optimization with online/competitive guarantees under varying load.
- Carbon-aware and renewable-aware query scheduling across geo-distributed datacenters.

## 9. Key References

- **[Foundational]** D. Tsirogiannis, S. Harizopoulos, M. A. Shah. *Analyzing the Energy Efficiency of a Database Server.* SIGMOD, 2010. — [DOI](https://doi.org/10.1145/1807167.1807194)
- **[Foundational]** W. Lang, J. M. Patel. *Towards Eco-friendly Database Management Systems.* CIDR, 2009. — [DBLP](https://dblp.org/rec/conf/cidr/LangP09.html) · [arXiv](https://arxiv.org/abs/0909.1767)
- **[Foundational]** F. Yao, A. Demers, S. Shenker. *A Scheduling Model for Reduced CPU Energy.* FOCS, 1995. — [DOI](https://doi.org/10.1109/SFCS.1995.492493)
- **[SOTA]** S. Albers. *Energy-Efficient Algorithms.* Communications of the ACM 53(5), 2010. — [DOI](https://doi.org/10.1145/1735223.1735245)
- **[SOTA]** W. Lang, R. Kandhan, J. M. Patel. *Rethinking Query Processing for Energy Efficiency: Slowing Down to Win the Race.* IEEE Data Eng. Bulletin, 2011. — [DBLP](https://dblp.org/rec/journals/debu/LangKP11.html)
- **[Survey]** S. Harizopoulos, M. A. Shah, J. Meza, P. Ranganathan. *Energy Efficiency: The New Holy Grail of Data Management Systems Research.* CIDR, 2009. — [DBLP](https://dblp.org/rec/conf/cidr/HarizopoulosSR09.html) · [arXiv](https://arxiv.org/abs/0909.1784)

## 10. Worked Example

A scan-and-aggregate operator does a fixed amount of work $W$ that takes time $t = W/f$ at
frequency $f$. Use dynamic power $P_{\text{dyn}}(f) = c\,f^{3}$ (the $\gamma=3$ cubic model)
with $c = 1$, plus static/leakage power $P_{\text{stat}} = 4$. Let $W = 1$, so $t = 1/f$ and

$$E(f) = (c f^{3} + P_{\text{stat}})\cdot \frac{W}{f} = f^{2} + \frac{4}{f}.$$

Minimize: $E'(f) = 2f - 4/f^{2} = 0 \Rightarrow f^{3} = 2 \Rightarrow f^\* = 2^{1/3} \approx 1.26$.

- At $f = 1$: $E = 1 + 4 = 5$ joules, time $= 1.0$.
- At $f^\* \approx 1.26$: $E \approx 1.59 + 3.17 = 4.76$ joules, time $\approx 0.79$.
- At $f = 2$ (race-to-idle): $E = 4 + 2 = 6$ joules, time $= 0.5$.

The energy minimum sits at moderate $f^\*$, but high static power ($P_{\text{stat}}=4$) pulls
the optimum toward faster execution — illustrating Tsirogiannis et al.'s "race to idle":
when leakage dominates, finishing quickly beats running slow. Lower $P_{\text{stat}}$ would
shift $f^\*$ down, favoring the slow-and-cool regime.

---
*Part of the [DBMS Research catalog](../../README.md).*
