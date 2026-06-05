# Provenance and explanations for streaming results

> **Topic:** Streaming & Continuous Queries · **ID:** `18-streaming-queries/streaming-provenance` · **Status:** open

## 1. Problem Statement
For a continuous query that produces a stream of (possibly windowed, approximate, or partial) results, track and answer provenance/explanation questions — *why* a result appeared, *how* it was derived, *where* its values came from, and *why-not* an expected result is missing — with overhead bounded enough to coexist with the live computation (ideally $o(\text{state})$ extra memory and $O(1)$-amortized extra time per tuple).

Variants:
- **Why/How:** the set (provenance polynomial) of input tuples and operator steps producing an output, scoped to the window/punctuation that was live.
- **Where:** the source attribute that supplied each output value.
- **Why-not:** explain absence — especially results dropped by **load shedding/approximation** or never produced due to ordering.
- **Approximate provenance:** when the result itself is approximate (sketches/samples), provenance must describe the *sketch* and its error, not exact lineage.
- **Bounded-overhead constraint:** provenance must respect window expiry — lineage of expired inputs must be reclaimable.

## 2. Mathematical Foundations
**Provenance semirings** (Green, Karvounarakis, Tannen, PODS 2007): annotate each tuple with an element of a commutative semiring $(K,+,\times,0,1)$; relational-algebra-with-annotation computes the *provenance polynomial*; choosing $K$ (booleans, $\mathbb{N}[X]$ polynomials, why-provenance sets, tropical for "min-cost") yields the various provenance models in one framework. For streams this extends to **annotated bags over time/windows**: each annotation is also tagged with a validity interval, and window expiry corresponds to *resetting* annotations.

**Aggregation provenance** needs semiring + monoid structure (provenance for SUM/AVG via the semiring-module semantics of Amsterdamer–Deutch–Tannen, PODS 2011). **Retraction** (negative tuples) breaks pure semirings — explaining deletions requires $m$-semirings / semirings with monus or difference, which are not freely generated, complicating bounded representation.

**Why-not / missing-answer** explanations are formalized via query/instance modifications (Chapman–Jagadish; Huang et al.) and are tied to abduction; over streams the missing answer may be due to *timing* (watermark) rather than data, requiring a temporal causal model. Approximate provenance interacts with sketch error: a result derived from an AMS/CM sketch has lineage = the multiset that updated the sketch, whose exact recovery is itself $\Omega(\text{space})$-hard (the same lower bounds as the underlying aggregate).

## 3. State of the Art (SOTA)
- **Semiring provenance** (Green–Karvounarakis–Tannen 2007) and **aggregate provenance** (Amsterdamer–Deutch–Tannen 2011): the foundational algebra adapted by streaming work.
- **Ariadne** (Glavic, Sheykh Esmaili, Fischer, Tatbul, EDBT 2014): operator-instrumented provenance for the **Borealis/streaming** model, the canonical streaming-provenance system; handles windows and ordering.
- **GeneaLog** (Palyvos-Giannas, Gulisano, Papatriantafilou, 2018/2019): fine-grained, low-overhead provenance for streaming with backward tracing and bounded memory via pointer/bitset encoding.
- **Erebus / Ananke** (Palyvos-Giannas et al., 2020-2021): live, duplicate-free provenance and explanation streams.
- **GProM** (Arenas, Glavic et al.): general provenance middleware; **Smoke** (Psallidas–Wu, SIGMOD 2018) for fast lineage capture (batch).
- Why-not and explanation: **Scorpion** (Wu–Madden, VLDB 2013) explains aggregate outliers via predicates — influential for streaming explanation but not native streaming.

## 4. Upper Bound
GeneaLog demonstrates **constant per-tuple overhead** provenance for selection/aggregation/join pipelines by attaching compact pointers and reclaiming them on window expiry, giving $O(1)$ amortized time and provenance state proportional to live window contents ($O(W)$) rather than to history. Ariadne shows provenance can be computed by *query rewriting* into the same streaming engine, so the upper bound on overhead is a constant-factor blow-up of the original plan for positive (monotone) relational+windowed-aggregate queries. For full why-provenance polynomials the representation can be kept linear in the live derivation DAG.

## 5. Lower Bound
There is no clean complexity-class hardness; the barriers are *information-theoretic and impossibility-flavored*. (i) **Approximate results:** recovering exact lineage of a sketch-based result requires $\Omega$(sketch-lower-bound) space — e.g., reconstructing the distinct elements behind a COUNT DISTINCT needs $\Omega(n)$ bits — so bounded-overhead *exact* provenance for approximate queries is impossible. (ii) **Why-not** for general queries is at least **coNP-hard** (it quantifies over possible inputs/derivations; related to certain-answer and abduction hardness). (iii) **Retraction provenance** cannot be captured in a free positive semiring (the monus structure is not freely generated), so a finite, composable, bounded representation of deletion-provenance is provably unavailable in the pure model. (iv) Full-history provenance is incompatible with bounded memory by a trivial INDEX argument: distinguishing which past tuple caused an output needs $\Omega(\log(\text{history}))$ growing bits.

## 6. The Gap
The positive, exact, windowed case is largely solved ($O(1)$ overhead). The **open** frontier: (a) provenance for *approximate/shed* results that is itself principled and bounded (what does "why" mean for a dropped or sketched tuple?); (b) bounded why-not explanations distinguishing *data* absence from *timing/watermark* absence; (c) retraction/negative-tuple provenance with a composable algebra and bounded state; (d) tight overhead lower bounds matching the systems' empirical constants. No framework yet handles approximation, shedding, retraction, and why-not together under a single bounded-overhead guarantee.

## 7. Current Research (as of June 2026)
- Low-overhead, duplicate-free live provenance and explanation streams (Gulisano, Papatriantafilou, Chalmers; Palyvos-Giannas) — extending Ananke/GeneaLog to richer operators *(frontier — verify)*.
- Provenance for ML-augmented / approximate streaming pipelines and feature stores.
- Explanation of streaming anomalies/drift via causal and counterfactual methods (Scorpion-style, made continuous) *(frontier — verify)*.
- Provenance under exactly-once semantics, retraction, and watermarks in differential dataflow / Materialize.

## 8. Future Work
- A unified bounded-overhead algebra covering windows + approximation + retraction + why-not.
- Principled "approximate provenance" with error bounds tied to the sketch's error.
- Timing-aware why-not explanations (data vs. watermark causality).
- Provenance-driven debugging and SLA root-cause for production stream pipelines.

## 9. Key References
- **[Foundational]** Green, T.J., Karvounarakis, G., Tannen, V. *Provenance Semirings.* PODS, 2007. — [DOI](https://doi.org/10.1145/1265530.1265535)
- **[Foundational]** Amsterdamer, Y., Deutch, D., Tannen, V. *Provenance for Aggregate Queries.* PODS, 2011. — [arXiv](https://arxiv.org/abs/1101.1110) — [DOI](https://doi.org/10.1145/1989284.1989302)
- **[SOTA]** Glavic, B., Sheykh Esmaili, K., Fischer, P.M., Tatbul, N. *Ariadne: Managing Fine-Grained Provenance on Data Streams.* DEBS/EDBT, 2013/2014. — [DOI](https://doi.org/10.1145/2488222.2488256)
- **[SOTA]** Palyvos-Giannas, D., Gulisano, V., Papatriantafilou, M. *GeneaLog: Fine-Grained Data Streaming Provenance.* Distributed and Parallel Databases / DEBS, 2018-2019. — [DOI](https://doi.org/10.1145/3274808.3274826)
- **[SOTA]** Psallidas, F., Wu, E. *Smoke: Fine-Grained Lineage at Interactive Speed.* PVLDB, 2018. — [arXiv](https://arxiv.org/abs/1801.07237) — [DOI](https://doi.org/10.14778/3199517.3199522)
- **[Foundational]** Wu, E., Madden, S. *Scorpion: Explaining Away Outliers in Aggregate Queries.* PVLDB, 2013. — [DOI](https://doi.org/10.14778/2536354.2536356)
- **[Survey]** Cheney, J., Chiticariu, L., Tan, W.-C. *Provenance in Databases: Why, How, and Where.* Foundations and Trends in Databases, 2009. — [DOI](https://doi.org/10.1561/1900000006)

## 10. Worked Example

Consider a continuous query over a click stream that, per 1-minute tumbling window, emits `SELECT page, COUNT(*) FROM clicks GROUP BY page`. Annotate each input tuple with a distinct provenance variable from the semiring $\mathbb{N}[X]$. In window $[12{:}00,12{:}01)$ three tuples arrive:

| tuple | page | var |
|---|---|---|
| $c_1$ | A | $x_1$ |
| $c_2$ | A | $x_2$ |
| $c_3$ | B | $x_3$ |

Under bag/semiring semantics the COUNT for page A carries provenance $x_1 + x_2$ (the polynomial degree = the count = 2), and page B carries $x_3$ (count 1). **Why** A=2: the monomials $\{x_1,x_2\}$. **Where** the value came from: the `page=A` attribute of $c_1,c_2$.

Now $c_1$ is **retracted** (a late correction with multiplicity $-1$). In a pure positive semiring there is no inverse of $x_1$; we must move to a semiring-with-monus, and A's count becomes $\,(x_1+x_2)\ominus x_1$. The bounded-overhead win: once the window closes at $12{:}01$, all of $x_1,x_2,x_3$ expire and their annotation slots are reclaimed, so provenance state stays $O(W)$ rather than $O(\text{history})$.

---
*Part of the [DBMS Research catalog](../../README.md).*
