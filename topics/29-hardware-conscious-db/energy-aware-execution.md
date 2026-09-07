---
id: 29-hardware-conscious-db/energy-aware-execution
title: "Energy-efficient query execution models"
topic: 29-hardware-conscious-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Energy-efficient query execution models

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/energy-aware-execution` · **Status:** open

## 1. Problem Statement
Conventional query optimizers minimize latency or estimated I/O cost. The problem here: build **cost models and plans that minimize energy (joules per query)**, or jointly optimize an energy-delay objective, across heterogeneous accelerators (CPU, GPU, FPGA, SmartNIC, low-power cores). Energy is not a monotone function of time — a slower, lower-power core or a vectorized in-cache plan can finish later yet consume fewer joules, so latency-optimal $\ne$ energy-optimal.

- **Optimization variant (primary):** given query $Q$ and a set of devices $D$ with power/performance profiles, choose a plan $P$ and device assignment minimizing total energy $E(P) = \int \text{power}(t)\,dt$, possibly subject to a latency SLO $\le T$.
- **Decision variant:** does a plan exist meeting both an energy budget $E_0$ and deadline $T_0$? (Two-constraint feasibility — a multi-objective/Pareto question.)
- **Optimization (energy-delay):** minimize $E \cdot T^{w}$ (the energy-delay product, weighted by $w$) to avoid race-to-idle vs run-slow degeneracies.

## 2. Mathematical Foundations
Device dynamic power follows $P_\text{dyn} \approx \alpha C V^2 \kern1pt f$ with static leakage $P_\text{leak}$; under **DVFS**, energy per fixed work scales roughly with $V^2 \propto f^2$, so $E \propto f^2 \cdot t$ while $t \propto 1/f$, giving $E \propto f$ for the dynamic part — favoring low frequency — but $P_\text{leak}\cdot t \propto 1/f$ pushes toward **race-to-idle**. The optimum is a convex trade-off; the **energy-delay product** $\text{EDP} = E\cdot T$ is the standard scalarization, generalized to $E^{a}T^{b}$.

Per-operator energy is modeled additively, $E(P) = \sum_{op\in P} e_d(op)$ where $e_d(op)$ depends on the assigned device $d$ — turning planning into a **min-cost assignment / shortest-path over the plan-DAG with device labels**, solvable by DP like Selinger join enumeration but with an energy cost annotation. With a latency constraint it becomes a **constrained shortest path / resource-constrained DAG scheduling** problem (NP-hard in general). The roofline + power model gives a per-device lower bound: a memory-bound operator pays $\Omega(\text{bytes}/B_d)$ time and $\ge P_d^{\min}\cdot(\text{bytes}/B_d)$ joules.

## 3. State of the Art (SOTA)
- **Foundational measurement:** Tsirogiannis, Harizopoulos, Shah (*Analyzing the Energy Efficiency of a Database Server*, SIGMOD 2010) established that, within a single server, **the most energy-efficient configuration is typically the highest-performing one** ("the most performant is the most energy-efficient") — race-to-idle dominates for homogeneous CPUs. Lang & Patel and the "energy management for DBMS" line (VLDB 2009–2010) explored QED/PVC (Processor Voltage/frequency Control).
- **Heterogeneity changes this:** with GPUs/FPGAs the equivalence breaks — Mueller, Teubner, Alonso (FPGA query processing, VLDB 2009+) and the DAPHNE/accelerator-DB efforts show large energy wins for offloaded operators.
- **Systems-SOTA:** energy-aware scheduling in heterogeneous edge/cloud DBs; carbon/energy-aware query scheduling (e.g., carbon-aware batch placement) is emerging.

## 4. Upper Bound
For the static energy-only assignment over a fixed plan DAG, optimal device assignment is computable in polynomial time by dynamic programming over the operator tree (Selinger-style), giving the **energy-optimal plan among enumerated shapes** in $O(\text{plans}\cdot|D|)$. With DVFS on a single device and convex power, the energy-optimal frequency is found in closed form / by convex optimization (the EDP-minimizing $f^\*$). For the constrained problem (energy subject to deadline), there are FPTAS results for resource-constrained shortest path, giving a $(1+\varepsilon)$-energy plan respecting the deadline. These hold in the additive-cost model assuming accurate per-operator energy estimates.

## 5. Lower Bound
Joint **energy-and-deadline feasibility is NP-hard** (it embeds resource-constrained scheduling / multi-constraint knapsack), so no efficient exact optimizer exists in general unless P=NP. Physically, there is a hard floor: any operator reading $n$ bytes on device $d$ consumes at least $P_d^{\min}\cdot n / B_d$ joules (a roofline/static-power lower bound), and **Landauer's principle** sets an absolute thermodynamic floor of $k_B T \ln 2$ joules per irreversible bit erasure — far below current hardware but a real asymptotic limit. The deeper lower bound is epistemic: energy estimates inherit cardinality-estimation error, and worst-case cardinality error is unbounded, so any energy plan can be arbitrarily far from optimal on adversarial inputs.

## 6. The Gap
The problem is **open** because the model and the measurement both wobble. On homogeneous CPUs the 2010 result ("fastest = greenest") nearly closes it — race-to-idle wins — but on **heterogeneous accelerators** that equivalence provably fails, and no accepted cost model predicts per-operator joules across CPU/GPU/FPGA/SmartNIC with the fidelity that latency models have. The gaps: (1) no standardized, portable per-operator energy model (power varies with data, temperature, co-tenancy, DVFS state); (2) optimizers don't expose energy as a first-class objective; (3) multi-objective (energy, latency, carbon) Pareto plan selection lacks a principled, low-regret online policy. Closing it needs calibrated energy cost models tied to hardware counters plus a multi-objective optimizer with guarantees.

## 7. Current Research (as of June 2026)
- Carbon- and energy-aware query/workload scheduling that shifts work in time and across regions by grid carbon intensity (groups at MIT, UW, TU Berlin, and cloud-provider research) *(frontier — verify)*.
- Per-operator energy models calibrated via RAPL / NVML / FPGA power telemetry, feeding learned cost models *(frontier — verify)*.
- Accelerator-offload decision frameworks (CPU vs GPU vs FPGA vs SmartNIC) optimizing energy-delay (Teubner/TU Dortmund, Alonso/ETH, and near-data/CSD efforts) *(frontier — verify)*.
- Energy-aware DVFS scheduling for vectorized engines and the rise of ARM/Graviton low-power query processing in cloud DBs *(frontier — verify)*.

## 8. Future Work
- A portable, composable per-operator energy cost model validated against hardware power counters.
- First-class multi-objective optimizers returning the energy-latency-carbon Pareto frontier with regret bounds.
- Reversible/approximate computing and near-data processing to approach the Landauer-adjacent regime for selected operators.
- Standard energy benchmarks (beyond TPC-Energy) for heterogeneous accelerator query processing.

## 9. Key References
- **[Foundational]** D. Tsirogiannis, S. Harizopoulos, M. Shah. *Analyzing the Energy Efficiency of a Database Server.* SIGMOD, 2010. — [DOI](https://doi.org/10.1145/1807167.1807194)
- **[Foundational]** W. Lang, J. Patel. *Towards Eco-friendly Database Management Systems.* CIDR, 2009; and *Energy Management for MapReduce Clusters*, VLDB 2010. — [arXiv](https://arxiv.org/abs/0909.1767)
- **[SOTA]** R. Mueller, J. Teubner, G. Alonso. *Data Processing on FPGAs.* VLDB, 2009. (Accelerator energy/throughput trade-offs.) — [DOI](https://doi.org/10.14778/1687627.1687730)
- **[Foundational]** R. Landauer. *Irreversibility and Heat Generation in the Computing Process.* IBM J. R&D, 1961. (Thermodynamic energy floor.) — [DOI](https://doi.org/10.1147/rd.53.0183)
- **[Foundational]** P. Selinger, et al. *Access Path Selection in a Relational DBMS.* SIGMOD, 1979. (Cost-based plan enumeration substrate.) — [DOI](https://doi.org/10.1145/582095.582099)
- **[Survey]** S. Harizopoulos, M. Shah, J. Meza, P. Ranganathan. *Energy Efficiency: The New Holy Grail of Data Management Systems Research.* CIDR, 2009. — [arXiv](https://arxiv.org/abs/0909.1784)

## 10. Worked Example

Run one scan-heavy query on two device choices. A CPU core finishes in $T_{\mathrm{cpu}} = 10$ s drawing dynamic power $P_{\mathrm{cpu}} = 60$ W plus static leakage $P_{\mathrm{leak}} = 20$ W. A GPU finishes the same work in $T_{\mathrm{gpu}} = 2$ s at $P_{\mathrm{gpu}} = 150$ W dynamic, same $20$ W leakage on the host.

Energy $E = (P_{\mathrm{dyn}} + P_{\mathrm{leak}})\cdot T$:
- CPU: $(60+20)\times 10 = 800$ J.
- GPU: $(150+20)\times 2 = 340$ J.

The GPU is both faster *and* lower-energy here — **race-to-idle** wins, consistent with the 2010 result.

Now add **DVFS** on the CPU: halving frequency makes $T_{\mathrm{cpu}} = 20$ s. Compute the dynamic energy as $P_{\mathrm{dyn}}\cdot T$, with $P_{\mathrm{dyn}}\propto f^2$ so at $f/2$ the dynamic power drops to $60/4 = 15$ W; over $20$ s that is $300$ J (equivalently, since dynamic energy $\propto f$, $600\times\tfrac{1}{2} = 300$ J). Add leakage $20\times20 = 400$ J $\Rightarrow 700$ J total. Leakage now dominates, but $700 < 800$, so slowing helps slightly — it is still worse than the GPU's $340$ J. The lesson: on heterogeneous hardware, offload beats DVFS tuning, and the leakage term $P_{\mathrm{leak}}\cdot T$ caps how far slowing down can pay.

---
*Part of the [DBMS Research catalog](../../README.md).*
