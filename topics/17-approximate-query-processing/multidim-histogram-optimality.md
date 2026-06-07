---
id: 17-approximate-query-processing/multidim-histogram-optimality
title: "Optimal Multidimensional Histograms"
topic: 17-approximate-query-processing
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Optimal Multidimensional Histograms

> **Topic:** Approximate Query Processing · **ID:** `17-approximate-query-processing/multidim-histogram-optimality` · **Status:** partially-solved

## 1. Problem Statement
A histogram partitions a data distribution into buckets, each storing a summary (e.g., the count and an average), and answers range/point queries from these summaries. In one dimension, the **v-optimal** histogram minimizes the sum of squared errors (SSE) within buckets and is computable optimally by dynamic programming. The problem: extend this to **$d\ge 2$ attributes**, constructing a $B$-bucket multidimensional histogram whose query-answering error is **provably near the optimal** for a workload of range queries (and point queries) over the $d$-dimensional domain.

Variants:
- **Optimization:** given $B$ buckets, minimize worst-case or expected error over a query class (range/point).
- **Decision:** does a $B$-bucket partition with error $\le \tau$ exist?
- **Structural:** which partition family — grid, arbitrary rectangular (hierarchical/GridTree), $k$-d-tree-like, or general space-partition — admits both small error and tractable construction?

The core difficulty: optimal *arbitrary* rectangular partitioning into $B$ buckets is NP-hard for $d\ge 2$, so the field studies restricted families with approximation guarantees.

## 2. Mathematical Foundations
For a data array $f$ over a $d$-dimensional grid, a histogram $H$ with buckets $\{b_i\}$ approximates $f$ by a per-bucket constant $c_i$. Error is typically SSE $\sum_i\sum_{x\in b_i}(f(x)-c_i)^2$, minimized within each bucket by $c_i=\mathrm{mean}_{b_i}(f)$. In 1-D, the optimal $B$-bucket partition minimizing SSE is found by DP in $O(n^2 B)$ (Jagadish et al., VLDB 1998), improvable with SMAWA/approximation.

In $d\ge 2$, **partition families** matter:
- **Grid (MHIST/EquiDepth):** axis-aligned grid; cheap but error-suboptimal under correlation.
- **Arbitrary rectangular (hierarchical) partitions:** strictly more powerful; optimal selection is NP-hard.
- **GenHist, STHoles, GridTree, ISOMER (max-entropy):** workload-aware refinements.

The query-error connection rests on **range-query sensitivity**: a range query touches partial buckets, so error depends on within-bucket variance *and* on how bucket boundaries align with query boundaries. Approximation results bound the achievable SSE/range error of restricted families against the unrestricted optimum, often using techniques from **geometric partitioning** and the **wavelet/Haar** decomposition (which gives a provably good $B$-term sparse representation in $\ell_2$).

## 3. State of the Art (SOTA)
- **Theory-SOTA:** Muthukrishnan–Poosala–Suel (ICDT 1999) prove hardness of optimal 2-D histograms and give approximation algorithms for restricted (hierarchical/$p\times p$ grid) partitions. Wavelet synopses (Garofalakis–Gibbons; Matias–Vitter–Wang) give provable $\ell_2$/maximum-error guarantees with thresholding.
- **Systems-SOTA:** **STHoles** (Bruno–Chaudhuri–Gravano, SIGMOD 2001) and **ISOMER** (Srivastava et al., ICDE 2006, max-entropy consistency) are workload-driven multidim histograms used for selectivity estimation; learned density models (deep autoregressive / sum-product networks) now often outperform classical multidim histograms on real correlated data for cardinality estimation.

## 4. Upper Bound
- 1-D v-optimal: exact optimum in $O(n^2 B)$ DP; $(1+\varepsilon)$-approximation in near-linear time.
- 2-D restricted partitions: polynomial-time **$O(1)$- and $(1+\varepsilon)$-approximations** for hierarchical/grid families (Muthukrishnan–Poosala–Suel and follow-ups), with running time polynomial in $n$ and $B$.
- Wavelet synopsis: best $B$-term Haar approximation is optimal in $\ell_2$ and computable in $O(n)$; thresholding gives provable maximum-error variants (Garofalakis–Kumar, PODS 2004).

## 5. Lower Bound
Constructing the **optimal arbitrary-rectangle $B$-bucket** histogram in $d\ge 2$ minimizing SSE is **NP-hard** (Muthukrishnan–Poosala–Suel, ICDT 1999), via reduction from geometric partition problems. Thus no polynomial exact algorithm exists for the general family unless P=NP; only restricted families admit optimal/PTAS construction. Information-theoretically, $B$ buckets cannot represent a distribution with more than $B$ "modes" without error proportional to residual variance — a per-instance lower bound on achievable accuracy.

## 6. The Gap
For **restricted** partition families the problem is essentially closed: PTAS/$O(1)$-approximations match the achievable optimum within those families. The gap is between **restricted families and the unrestricted optimum**: how much error must one pay for tractability (grid/hierarchical vs. arbitrary partitions), and whether a polynomial algorithm achieves a *constant-factor* approximation to the *unrestricted* 2-D v-optimal histogram for general query workloads. That worst-case-optimal, workload-aware multidimensional construction remains genuinely open.

## 7. Current Research (as of June 2026)
Classical multidim histograms are increasingly superseded by **learned density/selectivity models** (Naru/DeepDB/MSCN lineage from TUM, Berkeley, MIT) for correlated data, but these lack the provable error bounds histograms offer. *(frontier — verify)* Active work seeks **hybrid learned-histograms** with worst-case guarantees, and **differentially private** multidim histograms (HDMM, matrix-mechanism optimal under linear query workloads, McKenna et al.) where optimality is characterized via the matrix mechanism. Workload-adaptive partitioning under drift is also active.

## 8. Future Work
- Constant-factor polynomial approximation to the unrestricted multidim v-optimal histogram.
- Provable-error learned histograms combining ML accuracy with worst-case guarantees.
- Optimal workload-aware partitions under the matrix mechanism for private range queries.
- Tight bounds relating bucket budget $B$, dimensionality $d$, and achievable range-query error.

## 9. Key References
- **[Foundational]** Jagadish, H.V., Koudas, N., Muthukrishnan, S., Poosala, V., Sevcik, K., Suel, T. *Optimal Histograms with Quality Guarantees.* VLDB 1998. — [DOI](https://doi.org/10.5555/645924.671191)
- **[Foundational]** Muthukrishnan, S., Poosala, V., Suel, T. *On Rectangular Partitionings in Two Dimensions: Algorithms, Complexity, and Applications.* ICDT 1999. — [DOI](https://doi.org/10.1007/3-540-49257-7_16)
- **[SOTA]** Bruno, N., Chaudhuri, S., Gravano, L. *STHoles: A Multidimensional Workload-Aware Histogram.* SIGMOD 2001. — [DOI](https://doi.org/10.1145/375663.375686)
- **[SOTA]** Garofalakis, M., Kumar, A. *Deterministic Wavelet Thresholding for Maximum-Error Metrics.* PODS 2004. — [DOI](https://doi.org/10.1145/1055558.1055582)
- **[SOTA]** McKenna, R., Miklau, G., Hay, M., Machanavajjhala, A. *Optimizing Error of High-Dimensional Statistical Queries Under Differential Privacy (HDMM).* VLDB 2018. — [DOI](https://doi.org/10.14778/3231751.3231769) · [arXiv](https://arxiv.org/abs/1808.03537)

## 10. Worked Example

**1-D v-optimal DP, then why 2-D is hard.** Data values $f=(1,1,8,9)$ over 4 cells; budget $B=2$ buckets, minimize SSE. A bucket's optimal constant is its mean, and its SSE is its within-bucket variance times its size.

Candidate splits (contiguous):
- $[1{,}1\,|\,8{,}9]$: bucket means $1$ and $8.5$; SSE $=0 + (0.5^2+0.5^2)=0.5$.
- $[1\,|\,1{,}8{,}9]$: mean $6$; SSE $=0 + (25+4+9)=38$.
- $[1{,}1{,}8\,|\,9]$: mean $10/3$; SSE $=(5.44+5.44+21.78)+0\approx 32.7$.

DP picks the first, SSE $=0.5$, in $O(n^2 B)$ time (Jagadish et al.). The optimum cleanly separates the two modes $\{1\}$ and $\{8,9\}$.

**In 2-D** the same data laid on a $2\times 2$ grid cannot always be cut by axis-aligned rectangles into $B$ low-variance buckets without conflict: a checkerboard pattern $\begin{smallmatrix}1&9\\9&1\end{smallmatrix}$ has every $1\times 2$ or $2\times 1$ rectangle straddling a $1$ and a $9$ (bucket mean $5$, SSE $=(1-5)^2+(9-5)^2=32$ each). Choosing the best $B$-rectangle partition over arbitrary rectangles is exactly the NP-hard problem of Section 5 (Muthukrishnan–Poosala–Suel), so 2-D restricts to grid/hierarchical families with approximation guarantees.

---
*Part of the [DBMS Research catalog](../../README.md).*
