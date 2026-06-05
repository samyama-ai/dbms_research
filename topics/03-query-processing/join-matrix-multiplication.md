# Faster-than-AGM joins via fast matrix multiplication

> **Topic:** Query Processing & Execution · **ID:** `03-query-processing/join-matrix-multiplication` · **Status:** solved-but-impractical

## 1. Problem Statement

The AGM bound caps the *output size* and is a barrier for **combinatorial** join algorithms: any algorithm that materializes the join (or even just detects/counts certain patterns by combinatorial means) seems stuck near $\mathrm{AGM}(Q,D)$. But **fast matrix multiplication (FMM)** — Strassen and its descendants, running in $O(n^{\omega})$ with $\omega < 2.372$ — provides *algebraic* shortcuts that beat combinatorial bounds for problems like Boolean matrix multiplication, transitive closure, and **triangle counting/detection**. Since many join (sub)problems reduce to matrix products, FMM can evaluate or count certain queries *faster than AGM* — for the counting/Boolean/detection variants.

The problem: **characterize exactly which join queries (and which variants — detect, count, list, full materialization) admit faster-than-AGM evaluation via fast matrix multiplication, give the best exponent as a function of query structure and $\omega$, and determine whether any of it can be made practical** given that FMM's galactic constants and numerical/Boolean encoding overheads usually erase the asymptotic win. Key distinction: FMM helps **Boolean/counting/detection** and **aggregation over semirings** variants; it generally does **not** help **full enumeration** (output can be $\Omega(\mathrm{AGM})$, which dominates).

## 2. Mathematical Foundations

Let $\omega$ be the matrix-multiplication exponent: two $n\times n$ matrices multiply in $O(n^{\omega+o(1)})$ ring operations, currently $\omega \le 2.3714$ *(frontier — verify; Alman–Duan–Vassilevska Williams–Xu–Xu–Zhou 2024 line of refinements)*. **Triangle detection/counting** in an $n$-vertex graph reduces to computing $\mathrm{tr}(A^3)$ via $A\cdot A$, giving $O(n^{\omega})$ — versus the combinatorial $\tilde O(n^{3})$ or the AGM/listing bound $\Theta(m^{3/2})$ for $m$ edges. More generally, **counting homomorphisms / answering Boolean and aggregate CQs** can be sped up by FMM when the query's structure exposes a matrix product: a "rectangular" sub-pattern $\sum_b R(a,b)S(b,c)$ is exactly a matrix product. The relevant width measure becomes a **matrix-multiplication-aware width** rather than fhw/subw. For sparse inputs, *sparse/rectangular* FMM exponents ($\omega(1,\mu,1)$, the cost of multiplying $n\times n^\mu$ by $n^\mu\times n$) and output-sensitive matrix multiplication govern the achievable bounds.

## 3. State of the Art (SOTA)

**Theory-SOTA:** Triangle and small-pattern *counting* via FMM is classical (Itai–Rodeh; Alon–Yuster–Zwick for subgraph counting). **Counting and Boolean CQ evaluation with FMM** is characterized for several query classes; recent work gives FMM-based algorithms for **counting answers to (quantified) conjunctive queries** parameterized by structural width, beating combinatorial bounds for dense instances. **Sparse triangle/listing** results (e.g., $\tilde O(m^{2\omega/(\omega+1)})$ for triangle detection in sparse graphs, Alon–Yuster–Zwick) interpolate FMM with sparsity. **Systems-SOTA:** Essentially none in production. The constants of sub-Strassen FMM are *galactic*; only Strassen ($O(n^{2.807})$) is ever used in practice (numerical BLAS), and Boolean/relational encodings rarely recoup the cost. Linear-algebra-backed graph engines (GraphBLAS) use FMM-shaped primitives but not the fast (subcubic) exponents.

## 4. Upper Bound

For **triangle detection/counting**: $O(n^{\omega}) \le O(n^{2.372})$ in the RAM/arithmetic model (dense), and $\tilde O(m^{2\omega/(\omega+1)}) \le O(m^{1.41})$ for sparse graphs with $m$ edges — both *below* the combinatorial listing bound $\Theta(m^{3/2})$ for detection/counting. For broader **Boolean/counting CQs**, the best exponent is given by FMM-aware width parameters and is $< \mathrm{subw}$ in dense regimes. These hold in the arithmetic/word-RAM model and assume fast rectangular matrix multiplication subroutines. The bounds are **non-uniform / impractical**: they depend on FMM constructions with enormous hidden constants and apply only to detection/counting/aggregation, not full output listing.

## 5. Lower Bound

The natural barrier is the value of $\omega$ itself: it is **conjectured (but unproven)** that $\omega = 2$. Under the **fine-grained hardness** program, faster combinatorial triangle detection ($O(n^{3-\epsilon})$ combinatorial) would refute the **combinatorial Boolean Matrix Multiplication conjecture**; many DB problems (set cover-style, certain CQ-evaluation problems) are **BMM-hard** or **SETH/3SUM-hard**, meaning sub-$\mathrm{AGM}$ *combinatorial* algorithms are unlikely. For *listing* $t$ triangles, the output term $\Omega(t)$ and $\Omega(m^{4/3})$-style listing lower bounds (under 3SUM) limit gains. There is no unconditional lower bound matching $n^{\omega}$; the entire FMM speedup rests on the unproven value of $\omega$.

## 6. The Gap

There are **two gaps**, and the problem is "solved-but-impractical" because of the second. (1) *Theory gap:* the FMM-based upper bounds depend on $\omega$, whose true value (conjectured $2$) is unknown, so exact exponents for FMM-aided CQ counting are not pinned down. (2) *Practicality gap (the dominant one):* the asymptotically fast FMM algorithms have galactic constants and only help counting/Boolean/aggregate variants — full enumeration is bounded below by output size. Thus the speedups are real and proven asymptotically (hence "solved") but essentially never realizable in a deployed engine (hence "impractical"). Closing the practical gap would require a *practical* subcubic matrix multiply or relational encodings that exploit Strassen-level (not galactic) FMM.

## 7. Current Research (as of June 2026)

Directions: (1) **FMM-aware CQ counting** — tight exponents for counting/Boolean conjunctive (and aggregate/semiring) queries as a function of width and $\omega$; (2) **rectangular and sparse FMM** refinements feeding output-sensitive subgraph counting; (3) ongoing improvements to $\omega$ via the laser method and its refinements *(frontier — verify: the 2023–2024 Williams–Xu–Xu–Zhou and follow-ups pushing $\omega$ below $2.372$)*; (4) **practical** angles: when Strassen-level recursion plus relational/Boolean tricks (e.g., for path counting, reachability, GNN message passing) actually pays off on real hardware/GPUs. Groups: Vassilevska Williams (MIT) and the FMM-exponent community; Abo Khamis/Ngo/Rudra and Olteanu on FMM-aided FAQ/counting; the fine-grained-complexity community (Bringmann, Künnemann) on matching lower bounds.

## 8. Future Work

- Pin down FMM-aware exponents for counting/Boolean CQ classes and prove matching conditional lower bounds.
- Determine the practical crossover: for which densities and queries does Strassen-level FMM beat combinatorial joins on real hardware/GPUs?
- Output-sensitive FMM-based *listing* that interpolates between detection ($n^\omega$) and full enumeration ($\mathrm{AGM}$).
- Resolve or further narrow $\omega$ (toward the conjectured $2$).
- FMM primitives for semiring/aggregate FAQ queries inside real engines (GraphBLAS-style but with fast exponents).

## 9. Key References

- **[Foundational]** Itai, Rodeh. *Finding a Minimum Circuit in a Graph.* SIAM J. Computing, 1978 (triangles via matrix multiplication). — [DOI](https://doi.org/10.1137/0207033)
- **[Foundational]** Alon, Yuster, Zwick. *Finding and Counting Given Length Cycles.* Algorithmica, 1997 (sparse subgraph counting via FMM). — [DOI](https://doi.org/10.1007/BF02523189)
- **[SOTA]** Alman, Duan, Vassilevska Williams, Xu, Xu, Zhou. *More Asymmetry Yields Faster Matrix Multiplication.* SODA 2025 *(frontier — verify exact venue/exponent)*. — [arXiv](https://arxiv.org/abs/2404.16349)
- **[SOTA]** Abo Khamis, Curtin, Moseley, Ngo, Nguyen, Olteanu, Schleich. *Functional Aggregate Queries with Additive Inequalities / FMM-aided evaluation.* (FAQ / counting line) PODS/SIGMOD, 2019–2021. — [arXiv](https://arxiv.org/abs/1812.09526)
- **[Survey]** Vassilevska Williams. *On Some Fine-Grained Questions in Algorithms and Complexity.* ICM 2018 (BMM/triangle hardness and FMM). — [DOI](https://doi.org/10.1142/9789813272880_0188)
- **[Survey]** Ngo, Ré, Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013. — [arXiv](https://arxiv.org/abs/1310.3314)

## 10. Worked Example

**Counting triangles** in a 4-vertex graph with edges $\{12, 23, 13, 34\}$ (a triangle $1$–$2$–$3$ plus a pendant edge $3$–$4$). The query is $\sum_{a,b,c} E(a,b)E(b,c)E(a,c)$ — a 3-cycle CQ.

*Combinatorial / AGM view:* with $m=4$ edges, the listing bound is $\Theta(m^{3/2})=\Theta(8)$ probe-style operations to enumerate candidate paths and test closure.

*FMM view:* form the symmetric adjacency matrix $A$ and compute $A^2$, then $\mathrm{tr}(A^3)=\sum_i (A^3)_{ii}$. Here $\mathrm{tr}(A^3)=6$, which counts each of the single triangle's $3!=6$ ordered traversals, so the number of triangles is $6/6 = 1$. Computing $A\cdot A$ costs $O(n^{\omega})=O(4^{2.3714})$ ring operations.

The point: $\mathrm{tr}(A^3)$ *never enumerates* the triangle — it counts via an algebraic product, the FMM shortcut that beats combinatorial listing for the *counting* variant. But to actually *output* the triangle $\{1,2,3\}$ you still pay $\Omega(\mathrm{OUT})$; and at $n=4$ the galactic FMM constants make $O(n^\omega)$ slower in wall-clock than the naive $O(n^3)$ — exactly the "solved-but-impractical" tension.

---
*Part of the [DBMS Research catalog](../../README.md).*
