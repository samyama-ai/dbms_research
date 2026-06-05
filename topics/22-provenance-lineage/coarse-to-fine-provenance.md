# Coarse-to-Fine Provenance Refinement

> **Topic:** Provenance & Lineage · **ID:** `22-provenance-lineage/coarse-to-fine-provenance` · **Status:** open

## 1. Problem Statement

Full fine-grained (cell- or tuple-level, semiring-polynomial) provenance is expensive to capture and store, yet most provenance queries touch only a tiny fraction of the data. The **coarse-to-fine** problem asks for a *multi-resolution* lineage scheme: capture cheap **coarse** provenance eagerly (e.g., relation/partition/block-level or "this answer depends on files A, B"), and **refine** to record- or cell-granularity **lazily, only where a later query demands it**, with provable cost guarantees on both the eager phase and each refinement.

Variants:
- **Decision:** given a coarse summary and a provenance query $q_p$, decide whether $q_p$ is answerable at the current resolution without refinement.
- **Optimization (online):** minimize total cost = eager capture + sum of refinement costs over an adversarial / stochastic query sequence; competitive against the offline optimum that knows which cells will be queried.
- **Static-budget:** given a space/time budget $B$, choose the resolution lattice maximizing expected answerability.

The crux is a guarantee that *refinement is always possible and bounded*: coarse capture must retain enough (recomputation-complete or replay-complete) information that descending one level never requires re-running the whole pipeline.

## 2. Mathematical Foundations

Model provenance at a **resolution lattice** $\mathcal{L}$ of granularities $g_0 \sqsubseteq g_1 \sqsubseteq \cdots \sqsubseteq g_n$ (relation $\sqsubseteq$ partition $\sqsubseteq$ tuple $\sqsubseteq$ cell), each a coarsening homomorphism $h_{g}:\mathbb{N}[X]\to\mathbb{N}[X_g]$ on the provenance-polynomial semiring (Green–Karvounarakis–Tannen). A coarse annotation is the image $h_g(\text{poly})$; refinement inverts $h_g$ on demand using retained **replay metadata** (operator boundaries, partition keys, deterministic-recompute handles).

Refinement cost is governed by **selective recomputation**: descending from $g_i$ to $g_{i+1}$ on a queried region $S$ costs $C(S)=O(|\text{re-eval}(S)|)$ rather than $O(|\text{whole pipeline}|)$, achievable only if operators are **replayable** on sub-inputs. The online tradeoff is a **rent-or-buy / ski-rental** structure: pay capture cost up front (buy) vs. refine-on-demand (rent); the classic deterministic ski-rental $2$-competitive and randomized $\frac{e}{e-1}$ bounds apply when refinement cost equals capture cost. With heterogeneous costs and dependencies it becomes **online weighted set cover / metrical task systems**, where competitive ratios degrade to $O(\log)$ factors.

## 3. State of the Art (SOTA)

No system implements a clean, guaranteed coarse-to-fine lattice; the components exist piecemeal. **Lazy / on-demand provenance** (Ikeda–Widom Panda; Glavic–Alonso Perm/GProM via query rewriting) recomputes lineage from retained queries rather than storing it. **Approximate / sampled lineage** in Spark/dataflow systems (Titian, Interlandi et al., SIGMOD 2016) captures coarse RDD-level lineage and recomputes finer detail by re-execution. **Smoke** (Psallidas–Wu, VLDB 2018) shows tight eager fine-grained capture is feasible but pays a fixed overhead regardless of query demand. **Multi-resolution / hierarchical lineage** appears in workflow systems (provenance at task vs. data-item level). Systems-SOTA is thus *two fixed resolutions chosen statically*, not a refined-on-demand lattice with cost guarantees.

## 4. Upper Bound

- **Eager coarse capture:** $O(1)$ amortized per operator if coarse annotation is relation/partition-level (constant set of identifiers per output block) — RAM model.
- **Single refinement of region $S$:** $O(|\text{IN}_S| + |\text{OUT}_S|)$ via Yannakakis-style replay of the sub-pipeline restricted to $S$, when all operators are deterministic and replayable on sub-inputs.
- **Online total cost:** $2$-competitive (deterministic ski-rental) when per-level refinement cost equals incremental eager-capture cost; $\frac{e}{e-1}$-competitive randomized — competitive-analysis model.
- **Static budget:** $(1-1/e)$ greedy approximation when expected-answerability is **monotone submodular** in the set of refined regions.

## 5. Lower Bound

- **No online algorithm beats $2$** for the symmetric rent-or-buy refinement decision (ski-rental lower bound), and $\frac{e}{e-1}$ for randomized — competitive-analysis model.
- **Replay-completeness is necessary:** if coarse capture discards information below the recomputation-complete threshold, exact refinement is **impossible** (information-theoretic) — you cannot recover cell lineage that was never retained nor recomputable from a non-deterministic operator.
- Choosing the optimal static resolution set under a hard budget generalizes **weighted set cover / facility location**, hence **NP-hard** and inapproximable below $(1-o(1))\ln n$ unless P=NP — for the budgeted variant.
- For non-deterministic / non-replayable UDFs, even *deciding* answerability at a finer level is undecidable in general (reduces to UDF equivalence).

## 6. The Gap

The decision/answerability core is clean (lattice + homomorphism), but the **online optimization gap is genuinely open**: real refinement costs are *correlated and dependency-laden* (refining one region forces recomputing shared upstream operators), breaking the independent ski-rental model — no tight competitive ratio is known for the dependency-DAG version. Separately, there is no characterized class of pipelines for which a *bounded* refinement guarantee provably holds (which operators admit $O(|S|)$ sub-replay). Closing the gap needs both an online-algorithm result for DAG-correlated rent-or-buy and an operator-algebra characterization of replayability.

## 7. Current Research (as of June 2026)

(1) **Refinement-on-demand in lakehouse/dataflow engines** — extending GProM-style rewriting to descend resolution levels lazily over Delta/Iceberg partitions *(frontier — verify)*. (2) **Cost-based provenance plan selection** that treats resolution as a physical-design knob, co-optimized with the query (Glavic group; Wu group). (3) **Sampling + refine** hybrids that capture probabilistic coarse lineage and refine exactly only on audited answers. (4) Online-algorithms theory for **DAG-correlated rent-or-buy** and primal-dual provenance caching *(frontier — verify)*.

## 8. Future Work

- A tight competitive ratio for refinement under shared-upstream dependencies.
- An operator algebra characterizing $O(|S|)$-replayable transformations (relational vs. UDF vs. ML).
- Workload-adaptive resolution lattices learned online with regret bounds.
- Integration with verifiable provenance so coarse summaries remain tamper-evident across refinement.

## 9. Key References

- **[Foundational]** T. J. Green, G. Karvounarakis, V. Tannen. *Provenance Semirings.* PODS, 2007.
- **[Foundational]** R. Ikeda, J. Widom. *Panda: A System for Provenance and Data.* IEEE Data Eng. Bulletin, 2010.
- **[SOTA]** F. Psallidas, E. Wu. *Smoke: Fine-grained Lineage at Interactive Speed.* PVLDB, 2018.
- **[SOTA]** M. Interlandi et al. *Titian: Data Provenance Support in Spark.* PVLDB, 2016.
- **[SOTA]** B. Glavic et al. *GProM: A Swiss Army Knife for Your Provenance Needs.* IEEE Data Eng. Bulletin, 2018.
- **[Foundational]** A. Karlin, M. Manasse, L. Rudolph, D. Sleator. *Competitive Snoopy Caching / Ski-Rental.* Algorithmica, 1988.

---
*Part of the [DBMS Research catalog](../../README.md).*
