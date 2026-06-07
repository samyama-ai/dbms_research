---
id: 21-graph-databases/rpq-complexity-bounds
title: "Tight bounds for regular path query evaluation"
topic: 21-graph-databases
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Tight bounds for regular path query evaluation

> **Topic:** Graph Databases & Graph Query Processing · **ID:** `21-graph-databases/rpq-complexity-bounds` · **Status:** partially-solved

## 1. Problem Statement

A **regular path query (RPQ)** $r$ over an edge-labeled graph $G=(V,E)$ with labels $\Sigma$ is a regular expression over $\Sigma$ (and, for **2RPQs**, inverse labels $\Sigma^{-}$). Its semantics: the set of node pairs $(s,t)$ connected by a path whose edge-label word is in $L(r)$. RPQs are the navigational core of SPARQL property paths, Cypher variable-length patterns, and GQL.

Variants:
- **Boolean / decision:** is there *some* pair (or a fixed pair) connected by an $L(r)$-path?
- **Evaluation (full):** compute the whole answer relation $\{(s,t)\}$.
- **Single-source / single-pair:** fix $s$ (and $t$).
- **Enumeration:** output answers one-by-one, minimizing *preprocessing* and *delay*.
- **Simple-path semantics:** restrict to paths without repeated nodes (changes complexity drastically).

The problem: pin down **fine-grained** upper and lower bounds beyond the textbook BFS-over-product-automaton baseline, for each variant and semantics.

## 2. Mathematical Foundations

The classical algorithm builds the **product graph** $G \times A_r$ where $A_r$ is an NFA for $r$, then does reachability. With $|G|=m$ edges and $|A_r|=a$ transitions, the product has $O(m a)$ edges; full evaluation is $O(|V| \cdot m a)$ (a BFS per source) — essentially **Boolean matrix multiplication (BMM)**-shaped. Under *arbitrary-path* (homomorphism) semantics, RPQ evaluation is in PTIME (data complexity) and **NL**-complete; combined complexity is **PSPACE**-style for full regular expressions but tractable per fixed query. Under **simple-path** semantics, even fixed simple expressions (e.g. $a^* b a^*$ style, or $(aa)^*$) make the problem **NP-complete** (Mendelzon–Wood 1995). Enumeration is studied in the *(preprocessing, delay)* model; output-sensitive bounds use the answer size $|\mathrm{out}|$.

## 3. State of the Art (SOTA)

- **Theory-SOTA:** Reductions to/from BMM and APSP/OMv give conditional lower bounds (Casel–Schmid, PODS 2021/2023; Bringmann, Grønlund, Larsen / Backurs–Indyk for related regex matching). Enumeration with linear preprocessing and **polynomial delay** for arbitrary-path 2RPQs is known; for *trail/simple-path* semantics, recent FPT and polynomial-delay results depend on the structure of $r$ (Martens–Niewerth–Popp, and Bagan–Bonifati–Groz).
- **Systems-SOTA:** SPARQL property-path engines (Virtuoso, Jena, Blazegraph), MillenniumDB *path-finding* (Vrgoč et al., 2023) with worst-case-optimal path enumeration; Neo4j variable-length expansion; *Waveguide*, *RPQ via automata + product BFS* with frontier optimizations.

## 4. Upper Bound

Full evaluation (arbitrary-path semantics): $O(|V| \cdot |E| \cdot |A_r|)$ via per-source product BFS, or $\tilde{O}(|V|^\omega)$-style via Boolean matrix multiplication when $r$ reduces to transitive closure (e.g. $a^*$), with $\omega < 2.372$. Single-source: $O(|E|\cdot|A_r|)$ linear in product size. **Enumeration** of distinct $(s,t)$ pairs is achievable with $O(|E|\cdot|A_r|)$ preprocessing and *polynomial delay* under arbitrary-path semantics; for many practical fragments **constant or linear delay** after near-linear preprocessing (Martens–Niewerth–Popp, PODS 2023 lineage). These hold in word-RAM.

## 5. Lower Bound

- **Simple/trail-path semantics:** evaluation is **NP-complete** even for fixed expressions like $(\sigma\sigma)^*$ (Mendelzon–Wood 1995; Bagan–Bonifati–Groz refine the dichotomy — tractable iff the language is "downward closed" in a precise sense).
- **Fine-grained (arbitrary path):** computing the full answer for transitive-closure-like RPQs is **BMM-hard**; an $O(n^{3-\epsilon})$ combinatorial algorithm would break the BMM conjecture. For single-pair RPQ enumeration, **OMv**-conditional and **APSP**-conditional lower bounds rule out certain preprocessing/delay trade-offs (Casel–Schmid, PODS 2021). Combined complexity of RPQ evaluation is **PSPACE**-complete via regex universality; 2RPQ containment lifts to higher levels (see RPQ-containment page).

## 6. The Gap

**Partially solved.** The arbitrary-path case has tight conditional bounds for the *full-evaluation* and *Boolean* variants (BMM/OMv-tight), and the simple-path *dichotomy* (which $r$ are tractable) is essentially settled by Bagan–Bonifati–Groz. The open gaps: (1) precise *(preprocessing, delay)* trade-offs for **2RPQ enumeration** with inverses and under *trail* semantics are not fully classified; (2) for sparse graphs the polylog gaps between $\tilde O(ma)$ algorithms and OMv lower bounds remain; (3) tight bounds for *counting* RPQ answers. Closing these requires either matching enumeration algorithms or new fine-grained reductions.

## 7. Current Research (as of June 2026)

- Enumeration complexity with bounded delay for (C)2RPQs (Martens, Niewerth, Popp, Bourhis; Bagan, Bonifati) — an active PODS/ICDT thread.
- *(frontier — verify)* worst-case-optimal *path* enumeration and *shortest/all-paths* semantics in MillenniumDB, aligning with the new **GQL/SQL-PGQ** standard's path-mode semantics (TRAIL, ACYCLIC, SHORTEST).
- *(frontier — verify)* fine-grained lower bounds tying RPQ enumeration delay to OMv/Hyperclique for specific automaton structures.

## 8. Future Work

- Complete the *(preprocessing, delay)* map for all 2RPQ fragments and path semantics (walk/trail/simple/shortest).
- Output-sensitive and counting bounds with matching lower bounds.
- Parallel/distributed (MPC-round) and dynamic RPQ maintenance bounds.
- Bridging the GQL standard's path modes to provably optimal algorithms.

## 9. Key References

- **[Foundational]** Mendelzon, Wood. *Finding Regular Simple Paths in Graph Databases.* SIAM J. Computing 1995. — [DOI](https://doi.org/10.1137/S009753979122370X)
- **[Foundational]** Bagan, Bonifati, Groz. *A Trichotomy for Regular Simple Path Queries on Graphs.* PODS 2013 / JCSS. — [arXiv](https://arxiv.org/abs/1212.6857) — [DBLP](https://dblp.org/rec/conf/pods/BaganBG13.html)
- **[SOTA]** Casel, Schmid. *Fine-Grained Complexity of Regular Path Queries.* ICDT/PODS 2021 (LMCS 2023). — [arXiv](https://arxiv.org/abs/2101.01945) — [DOI](https://doi.org/10.4230/LIPIcs.ICDT.2021.19)
- **[SOTA]** Martens, Niewerth, Popp, et al. *Enumeration of Regular Path Query Answers / Constant-Delay Enumeration for RPQs.* PODS 2023. — [DBLP search](https://dblp.org/search?q=Martens%20Niewerth%20Popp%20enumeration%20regular%20path%20queries)
- **[SOTA]** Vrgoč, Rojas, Angles, Arenas, et al. *MillenniumDB: A Persistent, Open-Source Graph Database / Path Querying.* 2023. — [arXiv](https://arxiv.org/abs/2111.01540)
- **[Survey]** Angles, Arenas, Barceló, Hogan, Reutter, Vrgoč. *Foundations of Modern Query Languages for Graph Databases.* ACM Computing Surveys, 2017. — [DOI](https://doi.org/10.1145/3104031) — [arXiv](https://arxiv.org/abs/1610.06264)

## 10. Worked Example

Take the RPQ $r = a\,b^{*}$ over the graph $G$ with edges $s\xrightarrow{a}u$, $u\xrightarrow{b}v$, $v\xrightarrow{b}w$, and $w\xrightarrow{b}u$ (a $b$-cycle $u\to v\to w\to u$). An NFA $A_r$ has states $q_0\xrightarrow{a}q_1$ and $q_1\xrightarrow{b}q_1$ (accepting $q_1$).

**Product-graph evaluation** explores $(\text{node},\text{state})$ pairs from source $(s,q_0)$:
$(s,q_0)\xrightarrow{a}(u,q_1)\xrightarrow{b}(v,q_1)\xrightarrow{b}(w,q_1)\xrightarrow{b}(u,q_1)$ — and the last revisits an already-seen pair, so BFS halts. Accepting pairs (state $q_1$) reached: $u,v,w$. Under **arbitrary-path (walk) semantics** the answer is $\{(s,u),(s,v),(s,w)\}$, computed in $O(|E|\cdot|A_r|)$ — here $4\times 2=8$ product edges.

Now switch to **simple-path semantics**: each answer needs a *node-disjoint* witness path. $(s,w)$ still holds via $s,u,v,w$, but the search can no longer collapse the cycle by revisiting $(u,q_1)$ — it must track visited *nodes*, and deciding membership becomes NP-complete for languages like $(b\,b)^{*}$ (Mendelzon–Wood). This is the exact complexity cliff between the two semantics on the same tiny instance.

---
*Part of the [DBMS Research catalog](../../README.md).*
