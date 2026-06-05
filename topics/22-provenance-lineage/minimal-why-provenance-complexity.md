# Minimal Why-Provenance Complexity

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/minimal-why-provenance-complexity` · **Status:** partially-solved

## 1. Problem Statement
*Why-provenance* explains an answer $t$ to query $Q$ on database $D$ by its set of **witnesses**: subsets $W \subseteq D$ that already suffice to derive $t$. Buneman–Khanna–Tan defined the **witness basis** as the set of witnesses produced by the query's syntactic derivations; the *minimal* witness basis keeps only set-minimal ones. Two natural optimization questions arise: (a) compute the **minimal witness basis** (all minimal witnesses) — how many are there and how fast can we list them? (b) compute a **minimum-cardinality witness** — the *smallest* set of source tuples that still yields $t$ (the most concise explanation, a.k.a. minimal *why* in the sense of fewest sources). The problem is to pin down the **computational complexity** of these for conjunctive queries (CQs), unions of CQs, queries with self-joins, and richer (aggregate/recursive) queries. Variants: *decision* (is there a witness of size $\le k$?), *counting* (how many minimal witnesses?), *enumeration* (list them with bounded delay).

## 2. Mathematical Foundations
For a CQ $Q$ and answer $t$, a witness corresponds to a **homomorphism** from $Q$'s body (with $t$'s values substituted for head variables) into $D$; its image is the set of tuples used. The witness basis is the set of all such images over all satisfying homomorphisms; the *minimal* basis is its set-minimal members under $\subseteq$. Why-provenance is exactly the image of the how-provenance polynomial under the homomorphism $\mathbb{N}[X] \to \mathrm{PosBool}(X)$ (drop coefficients and exponents): the resulting positive Boolean formula's **prime implicants** are the minimal witnesses. Thus minimal-witness enumeration = prime-implicant enumeration of a monotone DNF, and minimum-cardinality witness = **shortest prime implicant**, which is the classic **MIN-DNF / minimum cover** style problem. The AGM / fractional-edge-cover bound caps the number of homomorphisms (hence raw witnesses) at $|D|^{\rho^*(Q)}$. Self-joins make distinct homomorphisms map to overlapping tuple sets, which is what pushes minimality from easy to hard.

## 3. State of the Art (SOTA)
Foundational definitions: Buneman, Khanna, Tan, *Why and Where: A Characterization of Data Provenance* (ICDT 2001) and Cui–Widom–Wiener lineage (TODS 2000). The modern complexity map is largely due to recent work on *the why-provenance problem*: for CQs **without self-joins**, deciding/enumerating minimal witnesses is tractable, while **self-joins** induce hardness. Recent results (Bourgaux, Amarilli, Bienvenu and collaborators; and the explicit "complexity of why-provenance" line, e.g. work presented at PODS/ICDT 2023–2024) sharpen this. For minimum-cardinality explanations, the connection to causality and responsibility (Meliou–Gatterbauer–Suciu, *Causality in Databases*, 2010) gives the relevant hardness frame. Systems-SOTA: Perm/GProM, ProvSQL, and the smoke/PROV-tools compute (non-minimal) witness bases; minimal-explanation features remain mostly research prototypes.

## 4. Upper Bound
For **self-join-free CQs**, a witness is determined uniquely per homomorphism and all witnesses in the basis are minimal; the basis is enumerable with **polynomial delay**, and a (the) minimum witness is found in PTIME. The full witness basis has size $\le |D|^{\rho^*(Q)}$ (AGM), computable in that time. For general CQs, the *witness basis* (non-minimal) is still PTIME-listable; checking whether a given set is a witness is PTIME (a homomorphism test). Minimal-witness enumeration for bounded-treewidth queries is fixed-parameter tractable. Minimum-cardinality witness reduces to weighted set-cover, giving an $O(\ln n)$-approximation upper bound.

## 5. Lower Bound
With **self-joins**, deciding whether a *minimal* witness of a given form exists — and computing the minimum-cardinality witness — becomes **NP-hard** (reduction from minimum set cover / minimum vertex cover via the overlapping-homomorphism structure). Counting minimal witnesses is **#P-hard** for general CQs (it subsumes counting prime implicants / #SAT-style counting over the provenance DNF). Minimum-cardinality explanation is **NP-hard to approximate** better than $\ln n$ unless P=NP (set-cover inapproximability, Dinur–Steurer). The *causality/responsibility* variant (Meliou et al.) is NP-hard / and responsibility computation is hard for the relevant counting classes. For UCQs and queries with negation, the why-provenance decision problem climbs the polynomial hierarchy.

## 6. The Gap
The dividing line is **largely characterized**: self-join-free CQs are tractable (polynomial-delay enumeration, PTIME minimum witness); self-joins and richer queries are NP-/#P-hard. The remaining open parts: (i) a *complete dichotomy* for all CQs/UCQs classifying exactly which queries admit polynomial-delay minimal-witness enumeration vs. which are hard (analogous to the Dalvi–Suciu dichotomy but for minimality); (ii) tight approximation factors for minimum-cardinality witnesses on structured query classes; (iii) the complexity for aggregate and recursive queries, which is only partially mapped. Closing (i) is the main open frontier.

## 7. Current Research (as of June 2026)
Amarilli, Bourgaux, Bienvenu, and Capelli are actively pushing the **fine-grained complexity and enumeration** of why-provenance; the explicit "complexity of why-provenance for (unions of) conjunctive queries" results (ICDT/PODS 2023–2024) are the current reference points. *(frontier — verify)* recent work extends minimal why-provenance to **ontology-mediated queries and Datalog** and studies *bounded-delay* enumeration under updates. Glavic (IIT) and Deutch (Tel Aviv) connect minimal explanations to user-facing tools (summarized/most-responsible explanations). The causality–provenance bridge (Suciu, Gatterbauer, Meliou) remains an active theoretical thread.

## 8. Future Work
Articulated directions: a full enumeration-complexity dichotomy for minimal witnesses across CQs/UCQs; tight approximation and parameterized bounds for minimum-cardinality explanations; minimal why-provenance for aggregate, recursive, and ontology-mediated queries; incremental/under-updates minimal-witness maintenance; and human-centered ranking of minimal explanations by responsibility or cost.

## 9. Key References
- **[Foundational]** P. Buneman, S. Khanna, W.-C. Tan. *Why and Where: A Characterization of Data Provenance.* ICDT, 2001. — [DOI](https://doi.org/10.1007/3-540-44503-X_20) · [DBLP](https://dblp.org/rec/conf/icdt/BunemanKT01.html)
- **[Foundational]** Y. Cui, J. Widom, J. L. Wiener. *Tracing the Lineage of View Data in a Warehousing Environment.* ACM TODS, 2000. — [DOI](https://doi.org/10.1145/357775.357777) · [DBLP](https://dblp.org/rec/journals/tods/CuiWW00.html)
- **[SOTA]** A. Meliou, W. Gatterbauer, K. F. Moore, D. Suciu. *The Complexity of Causality and Responsibility for Query Answers and Non-Answers.* VLDB, 2010. — [arXiv](https://arxiv.org/abs/1009.2021) · [DOI](https://doi.org/10.14778/1880172.1880176)
- **[SOTA]** M. Bienvenu, C. Bourgaux, et al. *On the Complexity of Why-Provenance for Conjunctive Queries.* ICDT/PODS, 2023–2024. — [DBLP search](https://dblp.org/search?q=complexity%20why-provenance%20datalog%20queries) *(unverified; closest confirmed work is Calautti–Livshits–Pieris–Schneider, "The Complexity of Why-Provenance for Datalog Queries," PODS 2024, [DOI](https://doi.org/10.1145/3651146))*
- **[Foundational]** N. Dalvi, D. Suciu. *The Dichotomy of Probabilistic Inference for Unions of Conjunctive Queries.* J. ACM, 2012. — [DOI](https://doi.org/10.1145/2395116.2395119)

## 10. Worked Example

Consider $R(A,B)$ with tuples $r_1=(1,2),\,r_2=(1,3),\,r_3=(4,2)$ and the self-join CQ
$Q(x) \leftarrow R(x,y),\,R(z,y)$, asking for $A$-values $x$ that share a $B$-value with *some* row.

For answer $t = (x{=}1)$, the satisfying homomorphisms (matching the two body atoms) give the how-provenance polynomial
$$\phi_1 = r_1^2 + r_1 r_3 + r_2^2,$$
since $y{=}2$ pairs $r_1$ with $r_1$ or $r_3$, and $y{=}3$ pairs $r_2$ with itself. Dropping exponents/coefficients into $\mathrm{PosBool}$ gives $r_1 \vee (r_1\wedge r_3) \vee r_2$. Absorbing the subsumed term $r_1\wedge r_3$, the **prime implicants** are $\{r_1\}$ and $\{r_2\}$ — these are the minimal witnesses. The **minimum-cardinality witness** has size $1$ (either single tuple).

Notice the self-join created the monomial $r_1 r_3$, which is *not* minimal — illustrating why self-joins push the problem beyond the trivial self-join-free case where every homomorphism image is already minimal. Here enumeration is still easy ($2$ witnesses), but in general the number of prime implicants of such a monotone DNF can be exponential, and finding the shortest is the NP-hard shortest-prime-implicant problem.

---
*Part of the [DBMS Research catalog](../../README.md).*
