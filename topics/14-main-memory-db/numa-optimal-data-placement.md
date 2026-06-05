# NUMA-Optimal Data Placement

> **Topic:** Main-Memory Databases · **ID:** `14-main-memory-db/numa-optimal-data-placement` · **Status:** open

## 1. Problem Statement
On a NUMA (non-uniform memory access) machine, a memory reference from a core to a remote socket's DRAM costs substantially more (latency and constrained interconnect bandwidth) than a local reference. Given a database workload, the problem is to **compute an assignment of data partitions to NUMA nodes, and threads/operators to cores, that minimizes total remote-memory traffic (or interconnect-bandwidth-weighted cost) subject to per-node memory-capacity and per-core load constraints.**

Variants: (decision) *Is there a placement with remote cost $\le C$?*; (optimization) *minimize weighted remote traffic*; (online/adaptive) *re-place as the workload drifts, amortizing migration cost*; (counting/robust) *placement robust to a distribution over query mixes*. Inputs: an access-affinity graph/hypergraph (which thread touches which partition, how often), node capacities, and the inter-node distance matrix. This is the database instantiation of graph/hypergraph partitioning under capacity constraints, and it is hard.

## 2. Mathematical Foundations
Model the workload as a weighted **hypergraph** $H=(V,E)$: vertices $V$ = data partitions (and thread/operator nodes), hyperedges $E$ capture co-access affinity with weights $w_e$ = access frequency. A placement is a map $\pi: V \to \{1,\dots,k\}$ to $k$ NUMA nodes with capacity $\mathrm{cap}_i$. The cost is

$$\mathrm{cost}(\pi)=\sum_{(u,v)} f(u,v)\cdot d(\pi(u),\pi(v))$$

where $f(u,v)$ is access frequency and $d$ is the NUMA distance matrix; with capacities $\sum_{v:\pi(v)=i} s(v)\le \mathrm{cap}_i$. This generalizes:
- **Balanced minimum $k$-cut / min-bisection** (NP-hard; no PTAS under standard assumptions),
- **Graph partitioning** (Kernighan–Lin heuristic; spectral methods),
- **Quadratic Assignment Problem (QAP)** when threads-to-cores with a distance matrix — QAP is NP-hard and notoriously inapproximable (no constant-factor unless P=NP),
- **Generalized assignment / hypergraph min-cut** for the capacity-constrained variant.

The affinity graph itself must be estimated from a query plan or measured counters, adding a statistical-estimation layer.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **HyPer / Umbra** "morsel-driven parallelism" with NUMA-local morsel scheduling (Leis et al., SIGMOD 2014) is the reference design; **ERIS** (Kissinger et al.) NUMA-aware storage; **SAP HANA**, **Oracle TimesTen**, and **Hekaton** add NUMA-aware allocation and work-stealing constrained to local nodes; **ATraPos** (Porobic et al., ICDE 2014) does hardware-aware OLTP partitioning; **DORA / PLP** (Pandis et al.) data-oriented thread-to-data binding. Production systems use **first-touch allocation**, **interleaving**, and **work-stealing with locality bias** rather than solving the optimization exactly.
- **Theory-SOTA:** general-graph balanced partitioning admits $O(\sqrt{\log n \log k})$-approximation (Krauthgamer–Naor–Schwartz) for related cut objectives; QAP variants remain inapproximable.

## 4. Upper Bound
For the cut-style relaxation (no QAP distance asymmetry), balanced $k$-partitioning has an $O(\sqrt{\log n \log k})$-approximation via semidefinite/spreading-metric techniques (Krauthgamer–Naor–Schwartz, 2009). Capacitated hypergraph partitioning is handled in practice by multilevel heuristics (**METIS/hMETIS**, Karypis–Kumar; **KaHyPar**) with no constant-factor guarantee but excellent empirical quality. For the online/adaptive setting, no competitive-ratio guarantee against migration cost is broadly established; systems use threshold-triggered repartitioning.

## 5. Lower Bound
The exact decision problem is **NP-hard** (reduction from balanced min-bisection / min $k$-cut). The thread-to-core variant with a distance matrix is **QAP-hard**, which is NP-hard *and* has no polynomial constant-factor approximation unless P=NP (Sahni–Gonzalez). Min-bisection has no known PTAS and is conjectured hard to approximate within constant factors. Thus NUMA-optimal placement is intractable in the worst case; the open questions concern approximability of the *capacitated, distance-weighted, workload-uncertain* database variant specifically.

## 6. The Gap
There is a wide gap between the inapproximability of the general QAP/bisection formulation and the strong *empirical* performance of multilevel heuristics on real workloads, which exhibit structure (sparse, near-planar affinity, few hot partitions). It is open whether realistic database affinity hypergraphs admit provable constant-factor or PTAS-style guarantees, and whether the online drift problem has a bounded-competitive algorithm against migration cost. Closing it requires either a parameterized/structural tractability result or a matching hardness for the structured instances.

## 7. Current Research (as of June 2026)
Directions: (i) learned/RL-based adaptive repartitioning that estimates affinity from live counters *(frontier — verify)*; (ii) NUMA-aware placement for **disaggregated/CXL memory** where the "distance matrix" becomes a tiered fabric *(frontier — verify)*; (iii) joint data+index+thread placement co-optimization. Groups: TUM (Neumann/Leis), EPFL DIAS (Ailamaki), CMU-DB (Pavlo), Dresden (Lehner).

## 8. Future Work
- Provable approximation for capacitated, distance-weighted database placement under realistic instance structure.
- Competitive online repartitioning accounting for migration/copy cost.
- Extending the model and algorithms to CXL/tiered and rack-scale memory.

## 9. Key References
- **[Foundational]** Sahni, S., Gonzalez, T. *P-Complete Approximation Problems (QAP inapproximability).* JACM, 1976. — [DOI](https://doi.org/10.1145/321958.321975)
- **[Foundational]** Karypis, G., Kumar, V. *Multilevel k-way Partitioning (METIS/hMETIS).* JPDC / SIAM, 1998. — [DBLP](https://dblp.org/rec/journals/jpdc/KarypisK98.html)
- **[SOTA]** Leis, V., Boncz, P., Kemper, A., Neumann, T. *Morsel-Driven Parallelism: A NUMA-Aware Query Evaluation Framework.* SIGMOD, 2014. — [DOI](https://doi.org/10.1145/2588555.2610507)
- **[SOTA]** Porobic, D., Liarou, E., Tözün, P., Ailamaki, A. *ATraPos: Adaptive Transaction Processing on Hardware Islands.* ICDE, 2014. — [DOI](https://doi.org/10.1109/ICDE.2014.6816692)
- **[SOTA]** Krauthgamer, R., Naor, J., Schwartz, R. *Partitioning Graphs into Balanced Components.* SODA, 2009. — [DOI](https://doi.org/10.1137/1.9781611973068.102)
- **[Survey]** Pandis, I., Johnson, R., Hardavellas, N., Ailamaki, A. *Data-Oriented Transaction Execution (DORA).* VLDB, 2010. — [DOI](https://doi.org/10.14778/1920841.1920959)

## 10. Worked Example

Four data partitions $\{P_1,P_2,P_3,P_4\}$, each size 1, to be placed on $k=2$ NUMA nodes with capacity 2 each. Access affinity (co-access frequency) is the weighted graph:

$$f(P_1,P_2)=10,\quad f(P_3,P_4)=8,\quad f(P_2,P_3)=1,\quad \text{others}=0.$$

NUMA distance: $d(\text{local})=1$, $d(\text{remote})=3$. Cost $=\sum f(u,v)\,d(\pi(u),\pi(v))$.

**Placement A:** node 0 $=\{P_1,P_2\}$, node 1 $=\{P_3,P_4\}$. Local edges $P_1P_2$ and $P_3P_4$; only $P_2P_3$ is remote.
$$\text{cost}_A = 10(1)+8(1)+1(3)=21.$$

**Placement B:** node 0 $=\{P_1,P_3\}$, node 1 $=\{P_2,P_4\}$. Now $P_1P_2$ and $P_3P_4$ both cross sockets:
$$\text{cost}_B = 10(3)+8(3)+1(1)=55.$$

Placement A wins by keeping the two heavy edges local — exactly the capacitated min-cut the heuristics target. With only 4 vertices we could enumerate all $\binom{4}{2}/2=3$ balanced cuts, but at $n$ partitions the search is $\binom{n}{n/2}$, and the decision form is NP-hard (§5), forcing the multilevel heuristics of §4.

---
*Part of the [DBMS Research catalog](../../README.md).*
