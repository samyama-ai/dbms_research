# Instance-optimal join evaluation

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/instance-optimal-joins` · **Status:** open

## 1. Problem Statement

Worst-case-optimal join algorithms guarantee runtime $\tilde O(\mathrm{AGM}(Q,D))$ — optimal against the *worst* database of given cardinalities. But two databases with identical relation sizes can have wildly different join difficulty: one may be solvable by reading a tiny "certificate" of tuples, the other may genuinely require near-AGM work. **Instance optimality** asks for an algorithm whose cost on *every specific instance* $D$ is within a (small, ideally constant) factor of the *best possible* cost any correct algorithm must incur on that same $D$.

The problem: **design a join (and enumeration) algorithm $A$ such that for every instance $D$, $\mathrm{cost}(A, D) \le c \cdot \mathrm{cost}^{*}(D) + \tilde O(\text{input})$, where $\mathrm{cost}^{*}(D)$ is the optimum over all correct algorithms (or over a natural class), and $c$ is small.** Variants: (a) the **certificate-complexity** variant — cost measured against the smallest *proof* that the output is correct/complete; (b) the **order-oblivious** variant — optimal regardless of input order (à la instance-optimal aggregation, Fagin's TA); (c) the **comparison/decision-tree** model variant — count only comparisons/probes, as in instance-optimal geometric algorithms. It is **open** for general conjunctive queries: instance optimality is known only for special cases (e.g., triangle/path queries, intersection joins on sorted inputs).

## 2. Mathematical Foundations

The benchmark is **certificate complexity**. For a join $Q$ on sorted relations, a *certificate* is a set of comparison outcomes (gap witnesses between adjacent probed values) sufficient to verify the output is exactly $Q(D)$. Let $\mathcal C(D)$ be the minimum certificate size; an algorithm is instance-optimal in the comparison model if its comparison count is $O(\mathcal C(D))$ for every $D$, uniformly over input orderings. This generalizes the **Fagin–Lotem–Naor** instance-optimal threshold algorithm for top-$k$/aggregation, where the optimality ratio is taken over algorithms that access the same sorted lists.

For joins, the **Minesweeper** framework (Ngo–Nguyen–Olteanu–Ré) models evaluation as adaptively probing a multidimensional space and inserting "gap boxes" (regions proved empty); the number of probes is bounded by the certificate $\mathcal C$ plus a structural term depending on the query's **treewidth**. Formally, for $\beta$-acyclic queries, Minesweeper runs in $\tilde O(\mathcal C + Z)$ where $Z=|Q(D)|$; for general queries an extra factor in treewidth appears. The cone of achievable bounds sits between input size $N$, certificate size $\mathcal C(D)$, output size $Z$, and the worst-case $\mathrm{AGM}(Q,D)$.

## 3. State of the Art (SOTA)

**Theory-SOTA:** **Minesweeper** (PODS 2014) is instance-optimal w.r.t. comparison-based certificates for $\beta$-acyclic queries and degrades gracefully (treewidth factor) otherwise. **Tetris** (Abo Khamis–Ngo–Ré–Rudra, PODS 2016 / JACM) reformulates this as *geometric resolution* over dyadic boxes, giving worst-case-optimal *and* certificate-sensitive bounds and connecting join evaluation to the Beyond Worst-Case Analysis program. For two sorted sets, the classic **instance-optimal set intersection** (Demaine–López-Ortiz–Munro, "adaptive intersection") and gap-encoding intersection algorithms achieve $O(\mathcal C)$. **Systems-SOTA:** Largely absent — no production engine is provably instance-optimal; adaptive/learned join operators and "small-materialization" tricks approximate the spirit but without guarantees.

## 4. Upper Bound

In the **comparison model** with sorted-input access: Minesweeper achieves $\tilde O(\mathcal C(D) + Z)$ for $\beta$-acyclic CQs and $\tilde O(\mathcal C(D) \cdot N^{(w-1)} + Z)$ flavored bounds for treewidth-$w$ queries; Tetris achieves $\tilde O(\mathcal C^{w} + Z)$-type bounds tying certificate size to fractional cover width and recovering AGM in the worst case. For the special case of a single multiway intersection / star join on sorted lists, instance optimality with constant ratio is achieved (gap/galloping intersection). Space is near-linear plus output.

## 5. Lower Bound

In the comparison/certificate model, any correct algorithm must read enough comparisons to *certify* the output, so $\Omega(\mathcal C(D))$ probes are necessary by an adversary argument — this is the model-internal lower bound that makes "instance-optimal" well-defined. For general queries, the treewidth factor in Minesweeper is shown necessary in the comparison model (Ngo et al.): there are instances where any comparison-based algorithm pays the extra width factor, so *true constant-ratio* instance optimality is provably **impossible** for general CQs in this model. Outside comparisons (RAM with hashing), no clean certificate notion is agreed upon, and lower bounds connect to fine-grained barriers (3SUM/SETH for join-related detection).

## 6. The Gap

The gap is genuinely **open and partly an impossibility**. For $\beta$-acyclic queries the gap is essentially closed (Minesweeper/Tetris are instance-optimal up to polylog). For general CQs, comparison-model instance optimality with constant ratio is *ruled out* (width factor is unavoidable), so the open question shifts: (1) what is the right *parameterized* notion of instance optimality (certificate $\times$ width) and is it tight? (2) Is there a meaningful instance-optimality theory in the **RAM-with-hashing** model that better matches real engines, and what is the right certificate definition there? (3) Can any of it be made practical?

## 7. Current Research (as of June 2026)

Directions: (1) **certificate-aware enumeration** combining instance optimality with constant-delay enumeration (links to `wco-enumeration-delay`); (2) **beyond-worst-case join theory** under the BWCA program — smoothed/parameterized analyses of join cost; (3) bridging to **adaptive query processing** so engines exploit "easy" instances without a priori knowledge; (4) **learned probing orders** approximating certificate-optimal access. Groups: Ngo/Abo Khamis/Rudra (RelationalAI/Buffalo), Olteanu (Zurich), Ré (Stanford), Suciu (UW), and the broader Beyond-Worst-Case-Analysis community (Roughgarden). *(frontier — verify)* 2025–2026 work reportedly explores instance-optimal *enumeration* delay and RAM-model certificate notions, but no production-grade instance-optimal join engine exists.

## 8. Future Work

- A clean, agreed certificate-complexity notion in the RAM/hashing model that engines actually use.
- Parameterized instance optimality: tight (certificate $\times$ structural-width) bounds for all CQs.
- Practical adaptive operators that provably approach certificate cost on easy instances.
- Instance-optimal *enumeration* with delay guarantees, not just full-materialization cost.
- Connecting instance optimality to learned/adaptive optimizers and to degree-aware (PANDA-style) bounds.

## 9. Key References

- **[Foundational]** Fagin, Lotem, Naor. *Optimal Aggregation Algorithms for Middleware.* PODS 2001 / JCSS 2003 (instance optimality, the TA algorithm). — [arXiv](https://arxiv.org/abs/cs/0204046)
- **[Foundational]** Demaine, López-Ortiz, Munro. *Adaptive Set Intersections, Unions, and Differences.* SODA 2000. — [DBLP](https://dblp.org/rec/conf/soda/DemaineLM00.html)
- **[SOTA]** Ngo, Nguyen, Ré, Olteanu. *Beyond Worst-Case Analysis for Joins with Minesweeper.* PODS 2014. — [arXiv](https://arxiv.org/abs/1302.0914)
- **[SOTA]** Abo Khamis, Ngo, Ré, Rudra. *Joins via Geometric Resolutions: Worst-Case and Beyond (Tetris).* PODS 2016 / ACM TODS 2017. — [arXiv](https://arxiv.org/abs/1404.0703)
- **[Survey]** Roughgarden (ed.). *Beyond the Worst-Case Analysis of Algorithms.* Cambridge University Press, 2021. — [DOI](https://doi.org/10.1017/9781108637435)
- **[Survey]** Ngo, Ré, Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013. — [arXiv](https://arxiv.org/abs/1310.3314)

## 10. Worked Example

Intersect two sorted sets $A=\{1,2,3,\dots,1000\}$ and $B=\{1000,1001,\dots,1999\}$; the answer is $\{1000\}$. Both have $|A|=|B|=1000$, so the worst-case (AGM-style) bound suggests up to $\sim 1000$ comparisons. But this *instance* is easy: one galloping (exponential) search for $\min(B)=1000$ in $A$ probes positions $1,2,4,8,\dots,512,1000$ — about $\log_2 1000 \approx 10$ comparisons — lands on the single overlap, and a symmetric step confirms nothing follows.

The **certificate** here is tiny: the comparisons $A[512]=512 < 1000$ and $A[1000]=1000=B[1]$, plus $A[1000]<B[2]=1001$, witness that exactly one element matches. So $\mathcal C(D)=O(\log n)$, and an instance-optimal algorithm (adaptive/galloping intersection) runs in $O(\mathcal C)=O(\log n)$, not $O(n)$.

Contrast a *hard* instance: $A,B$ perfectly interleaved ($A$ odd, $B$ even). Then every adjacent gap must be witnessed, forcing $\Omega(n)$ comparisons — here $\mathcal C(D)=\Theta(n)$ and no algorithm can do better. Instance optimality means matching $\mathcal C(D)$ on *both* instances with the same algorithm.

---
*Part of the [DBMS Research catalog](../../README.md).*
