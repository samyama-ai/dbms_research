# PCIe/interconnect transfer lower bounds for GPU joins

> **Topic:** Hardware-Conscious Databases · **ID:** `29-hardware-conscious-db/gpu-join-transfer-bounds` · **Status:** open

## 1. Problem Statement
A discrete GPU has fast on-board memory (HBM/GDDR) of size $M$ but is connected to the host over a comparatively narrow interconnect (PCIe 4.0/5.0, NVLink, CXL). When the working set of a relational join exceeds $M$, tuples must be streamed across this link, and the link — not compute — becomes the bottleneck. The problem is to establish **tight lower and upper bounds on the number of bytes that must cross the host–device interconnect** to compute a join $R \bowtie S$ (and multi-way joins) as a function of $|R|, |S|$, output size $\mathrm{OUT}$, GPU memory $M$, and the transfer block size $B$.

Variants: (a) **decision** — does a transfer schedule using $\le T$ bytes exist? (b) **optimization** — minimize total bytes (or makespan under a fixed link bandwidth $\beta$); (c) **online/oblivious** — bounds when the optimizer cannot see data statistics before scheduling.

## 2. Mathematical Foundations
The natural model is the **external-memory / red-blue pebble model** with the interconnect as the "slow memory" boundary: GPU HBM is internal memory of size $M$, host RAM is external, transfers move blocks of size $B$. I/O complexity for join in this model is classically
$$ \Theta\!\left(\frac{N}{B}\log_{M/B}\frac{N}{B} + \frac{\mathrm{OUT}}{B}\right),\quad N=|R|+|S|. $$
For multi-way joins the relevant combinatorial ceiling on output is the **AGM bound** $\mathrm{OUT}\le \prod_e |R_e|^{x_e}$ for a fractional edge cover $x$, which lower-bounds any algorithm that must materialize results. Communication-complexity arguments (two-party, host vs. device) give transfer lower bounds independent of compute: deciding non-emptiness of $R\bowtie S$ on disjointly-held inputs reduces to set-disjointness, with $\Omega(\min(|R|,|S|))$ communication.

## 3. State of the Art (SOTA)
**Systems-SOTA:** Crystal/Tile-based GPU operators (Shanbhag et al., SIGMOD 2020), HeavyDB/OmniSci, and TQP/Velox-GPU show that PCIe transfer dominates once data spills; the dominant heuristic is to *push selections/projections to the host* and transfer only join keys + late-materialized row IDs. Sioulas et al. (ICDE 2019) gave hardware-conscious partitioned GPU hash joins; Lutz et al. (SIGMOD 2020, "Pump Up the Volume") quantified NVLink 2.0 vs PCIe and showed interconnect bandwidth, not GPU memory, sets the practical limit. **Theory-SOTA:** the external-memory join bounds of Aggarwal–Vitter (1988) and the I/O-optimal join framework of Hu–Tao–Yi (sort-based, worst-case optimal I/O) bound transfers when the boundary is treated as the I/O frontier.

## 4. Upper Bound
For binary joins, a **sort-merge or grace-hash schedule** achieves transfer cost $O\!\big(\frac{N}{B}\log_{M/B}\frac{N}{B} + \frac{\mathrm{OUT}}{B}\big)$ bytes across the link, matching the external-memory optimum (Hu–Tao–Yi-style worst-case-optimal I/O). When $S$ fits ($|S|\le M$), a single-pass broadcast/probe gives $O((|R|+|S|+\mathrm{OUT})/B)$ — linear, optimal. Late materialization improves constants by transferring only the projected join attributes.

## 5. Lower Bound
A matching $\Omega\!\big(\frac{N}{B}\log_{M/B}\frac{N}{B}\big)$ I/O lower bound follows from the permutation/sorting lower bound in the external-memory model (any join general enough to sort inherits it). Independently, **communication-complexity** reductions from set-disjointness give $\Omega(\min(|R|,|S|))$ bytes when inputs are split host/device — robust to compute power. Output-sensitive $\Omega(\mathrm{OUT}/B)$ is trivially required. These hold in the I/O / two-party communication models respectively.

## 6. The Gap
For **binary** joins under the pure external-memory model the bounds match — effectively closed. The genuinely **open** part: (i) bounds that jointly account for *block size $B$ + finite bandwidth $\beta$ + bidirectional/duplex links + concurrent kernel overlap* (makespan, not byte count); (ii) **multi-way** worst-case-optimal joins where transfer (not compute) is the cost measure — no tight characterization in terms of AGM/submodular width is known; (iii) **oblivious/online** schedules without prior statistics. These are open.

## 7. Current Research (as of June 2026)
Active threads: CXL-attached memory and disaggregated GPU pools change $M$ from fixed to elastic, reopening the "spill" regime *(frontier — verify)*. Groups at TU München (Neumann/Leis), EPFL (Ailamaki/DIAS), and the Heidelberg GPU-DB group continue empirical interconnect studies; NVIDIA's RAPIDS/cuDF team publishes NVLink-C2C (Grace-Hopper) numbers where the host–device boundary nearly disappears, motivating bounds parameterized by $\beta$ rather than $M$ *(frontier — verify)*.

## 8. Future Work
Tight makespan lower bounds under duplex bandwidth and compute–transfer overlap; transfer-optimal multi-way GPU join theory tied to fractional hypertree/submodular width; unified bounds spanning the PCIe → NVLink → C2C → CXL continuum; data-skew-aware lower bounds.

## 9. Key References
- **[Foundational]** A. Aggarwal, J. S. Vitter. *The Input/Output Complexity of Sorting and Related Problems.* CACM, 1988. — [DOI](https://doi.org/10.1145/48529.48535)
- **[Foundational]** A. Atserias, M. Grohe, D. Marx. *Size Bounds and Query Plans for Relational Joins.* SICOMP, 2013 (AGM bound). — [DOI](https://doi.org/10.1137/110859440) · [arXiv](https://arxiv.org/abs/1711.03860)
- **[SOTA]** C. Lutz, S. Breß, S. Zeuch, T. Rabl, V. Markl. *Pump Up the Volume: Processing Large Data on GPUs with Fast Interconnects.* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3389705)
- **[SOTA]** A. Shanbhag, S. Madden, X. Yu. *A Study of the Fundamental Performance Characteristics of GPUs and CPUs for Database Analytics (Crystal).* SIGMOD, 2020. — [DOI](https://doi.org/10.1145/3318464.3380595)
- **[SOTA]** X. Hu, Y. Tao, K. Yi. *Output-Optimal Parallel Algorithms for Similarity Joins / Worst-Case Optimal I/O Joins.* PODS, 2017. — [DBLP](https://dblp.org/rec/conf/pods/HuTY17.html)

## 10. Worked Example

Join $R \bowtie S$ on a GPU with HBM $M = 4$ MB, build side $S$, and transfer block $B$. Let $|R| = 100$ MB, $|S| = 10$ MB, output $\mathrm{OUT} = 20$ MB, all in units where $B$ normalizes counts to bytes/$B$.

**Case 1 — $S$ fits ($|S| = 10$ MB $> M$):** here $S$ does *not* fit, so a single-pass broadcast is impossible. We use **grace-hash**: partition both sides into $\lceil |S|/M \rceil = \lceil 10/4 \rceil = 3$ partitions so each build partition $\le M$. One partitioning pass streams $|R|+|S| = 110$ MB host→device→host, then the probe pass streams 110 MB again plus emits $\mathrm{OUT}=20$ MB. Total link traffic $\approx (110 + 110 + 20)/B = 240/B$ MB.

**Contrast — naive re-probe** (re-stream $R$ once per $S$-chunk that overflowed): $3 \times 100 = 300$ MB of $R$ alone, far worse.

The external-memory optimum is $O\!\big(\frac{N}{B}\log_{M/B}\frac{N}{B} + \frac{\mathrm{OUT}}{B}\big)$ with $N=110$ MB; here $\log_{M/B}(N/B)$ is small (one partitioning round suffices), so the grace-hash schedule is within a constant factor of optimal, illustrating why interconnect bytes — not compute — set the cost.

---
*Part of the [DBMS Research catalog](../../README.md).*
