# FPGA query operator synthesis from SQL

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/fpga-operator-synthesis` · **Status:** empirically-open

## 1. Problem Statement

Field-Programmable Gate Arrays (FPGAs) offer massive pipelined parallelism and high streaming throughput, attractive for relational operators (selection, projection, hashing, joins, aggregation, sorting, regex/decompression). The problem: **compile relational operators (ultimately SQL) to pipelined FPGA dataflow** that runs at line rate, **without paying per-query bitstream reconfiguration cost** — full FPGA reconfiguration takes milliseconds to seconds, dwarfing query latency, so synthesizing a fresh circuit per query is a non-starter.

Variants:
- **Compilation/decision:** can a given operator (or sub-plan) be realized as a fixed, parameterizable circuit that covers a query class without re-synthesis?
- **Optimization:** maximize throughput / minimize FPGA resource usage (LUTs, BRAM, DSPs) and reconfiguration frequency for a workload.
- **Coverage:** what fragment of relational algebra admits reconfiguration-free execution via runtime-parameterized circuits?

## 2. Mathematical Foundations

Relational operators are expressed in **relational algebra** ($\sigma, \pi, \bowtie, \gamma, \delta$). The FPGA target is a **synchronous dataflow** model: a circuit is a pipeline graph where each stage consumes/produces tuples per clock; throughput is bounded by the slowest stage and the achievable clock frequency $f$, giving $\text{tuples/s} \approx f \times \text{lanes}$. Resource use is a packing constraint over LUT/BRAM/DSP budgets.

The reconfiguration-cost problem is structurally a **specialization vs. generality** trade-off: a fully specialized circuit (constants baked in) is small/fast but query-specific; a **runtime-parameterized** or **interpreted** circuit (a "query processor on chip" reading micro-instructions, à la *skeleton automata* / template) covers a class without re-synthesis but costs area and may lower $f$. Formally, one seeks a family of circuits $\{C_\theta\}$ parameterized by $\theta$ such that a workload's operators all map to some $\theta$ loadable as data (not bitstream). This connects to **partial reconfiguration** (swap only a region) and to the theory of finite-automata templates for predicate/regex evaluation.

## 3. State of the Art (SOTA)

- **Systems-SOTA.** *Glacier* (Mueller, Teubner, Alonso, VLDB 2009) compiled streaming queries to hardware circuits — a foundational SQL-to-FPGA compiler. *Ibex* (Woods, István, Alonso, VLDB 2014) is an FPGA-based smart storage engine pushing selection/projection into the data path. *Centaur* (Owaida et al.) integrates FPGA operators with a DBMS. *DoppioDB* (Sidler et al., SIGMOD 2017) embeds FPGA-accelerated operators (e.g. regex, ML) in MonetDB. Teubner & Woods' synthesis lecture *Data Processing on FPGAs* (2013) is the canonical reference. Microsoft *Catapult* and AWS F1 productionized FPGA acceleration. Sort/merge networks and hash-join engines (Halstead et al.; István et al. histogram/hash) are well studied. **Skeleton automata** (Teubner et al.) realize reconfiguration-free pattern/XML/predicate matching by loading transition tables as data.
- **Theory-SOTA.** No general account of which relational fragment admits reconfiguration-free, resource-bounded synthesis; results are operator-by-operator.

## 4. Upper Bound

Achievable at line rate: streaming **selection/projection** and **regex/pattern** matching via parameterized automata loaded as data (skeleton automata) — *zero* re-synthesis across the supported class. **Hash joins** and **partitioning** reach near-memory-bandwidth throughput on chip; **bitonic/merge sorting networks** sort $N$ elements with $O(\log^2 N)$ pipeline depth at fixed $f$. Aggregations and group-by run at line rate with bounded BRAM for the hash table. Partial reconfiguration limits re-program cost to a region (microseconds-to-low-milliseconds) rather than the whole device. So for fixed operator templates, throughput is $O(f \cdot \text{lanes})$ with O(1) reconfiguration amortized over a workload.

## 5. Lower Bound

There is no clean complexity-theoretic lower bound; the binding constraints are **physical/resource**: on-chip BRAM caps hash-table and sort-buffer sizes, so operators exceeding capacity must spill, reintroducing memory-bandwidth bounds (an external-memory lower bound re-emerges). Bitonic sorting networks have an $\Omega(\log^2 N)$ depth (and the AKS network's $O(\log N)$ depth is impractical), bounding latency. The **reconfiguration cost itself** is a hard physical lower bound: full-device bitstream load time is fixed by the device, so any design that needs per-query re-synthesis cannot beat that latency — this is the constraint the whole problem is organized to avoid. No fine-grained or information-theoretic lower bound characterizes the minimal area for a reconfiguration-free circuit covering a given query class.

## 6. The Gap

Individual operators are solved empirically and run at line rate; the **open gap** is (1) a general SQL-to-dataflow compiler that covers broad query classes **without per-query re-synthesis** while staying resource-bounded, and (2) any theory predicting which relational fragments admit such reconfiguration-free, area-bounded realization. Practice has impressive point solutions and template/automata tricks, but no unifying compiler or characterization, and resource/reconfiguration trade-offs are explored by engineering, not bounds. Hence **empirically-open**.

## 7. Current Research (as of June 2026)

- **Composable / overlay architectures**: a fixed coarse-grained reconfigurable "operator fabric" reprogrammed by loading microcode, avoiding bitstream swaps *(frontier — verify)*.
- HLS- and MLIR-based **SQL-to-RTL** compilation pipelines, and integration with columnar/Arrow formats and CXL-attached FPGAs/SmartNICs *(frontier — verify)*.
- Near-data FPGA processing in **computational storage** and SmartNICs. Active groups: ETH Zürich (Alonso/Owaida), TU Dortmund (Teubner), Microsoft Research (Catapult lineage), Xilinx/AMD and Intel research.

## 8. Future Work

- A general SQL compiler producing parameterized, reconfiguration-free operator pipelines with a characterized coverage class.
- Theory of minimal area for reconfiguration-free realization of a relational fragment.
- Spill-aware operators that degrade gracefully past BRAM limits with provable throughput.
- Tight integration with CXL/host memory and columnar formats; cost models for the optimizer to place operators on FPGA vs CPU/GPU.

## 9. Key References

- **[Foundational]** Mueller, Teubner, Alonso. *Streams on Wires — A Query Compiler for FPGAs (Glacier).* VLDB, 2009.
- **[Foundational]** Teubner, Woods. *Data Processing on FPGAs.* Synthesis Lectures on Data Management, Morgan & Claypool, 2013.
- **[SOTA]** Woods, István, Alonso. *Ibex — An Intelligent Storage Engine with Support for Advanced SQL Off-loading.* VLDB, 2014.
- **[SOTA]** Sidler, Owaida, István, Kara, Alonso. *doppioDB: A Hardware Accelerated Database.* SIGMOD (demo), 2017.
- **[SOTA]** Teubner, Woods, Nie. *Skeleton Automata for FPGAs: Reconfiguring without Reconstructing.* SIGMOD, 2012.
- **[Foundational]** Putnam et al. *A Reconfigurable Fabric for Accelerating Large-Scale Datacenter Services (Catapult).* ISCA, 2014.

---
*Part of the [DBMS Research catalog](../../README.md).*
