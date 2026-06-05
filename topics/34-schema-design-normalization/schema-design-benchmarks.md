# Benchmarks and Ground Truth for Schema Design

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/schema-design-benchmarks` · **Status:** empirically-open

## 1. Problem Statement
Build **realistic, reusable benchmarks** for schema-design and dependency-discovery research: datasets paired with *ground-truth* dependencies (FDs, INDs, denial constraints), keys/foreign keys, intended normal forms, and known-good (or known-bad) designs, so that discovery and design tools can be evaluated on precision/recall and design quality rather than on instance-validity alone.

- **Construction problem:** produce schema+data instances where the *true* semantic constraints are known (because they were planted, or curated by domain experts), at varied scale and dirtiness.
- **Metric problem:** define evaluation measures that score *genuine* (not merely instance-valid) dependency recovery and design quality (normal-form attainment, anomaly reduction, workload cost).
- **Realism problem:** ensure synthetic data carries realistic correlations/coincidental dependencies so that precision is meaningfully tested (a benchmark with no spurious dependencies is too easy).

This is **empirically-open**: there is no theorem to prove; the open question is whether a benchmark suite can be built that the community accepts as ground truth and that discriminates among tools.

## 2. Mathematical Foundations
The core obstacle is that **instance-validity ≠ ground truth**: a dependency holding on $I$ may be coincidental, so a benchmark must encode *intended* constraints separately from what the data happens to satisfy. Formally, ground truth is a pair $(I, \Sigma^\star)$ where $\Sigma^\star$ is the semantic constraint set; a tool's output $\hat\Sigma$ is scored by precision $\frac{|\hat\Sigma \cap \Sigma^\star_{\text{closure}}|}{|\hat\Sigma|}$ and recall against $\Sigma^\star$, *modulo logical implication* — equivalence is up to closure under Armstrong/chase, so naive set overlap is wrong and the right metric quotients by implication.

Synthetic generation must control the **coincidence rate**: for columns of entropy $H$ and $r$ rows, the expected number of accidentally-holding FDs grows as rows shrink and arity grows, so realistic benchmarks tune $(r, n, \text{domain sizes}, \text{correlation})$ to plant a known $\Sigma^\star$ while inducing a controlled population of spurious near-dependencies (measured by the $g_3$ error distribution). Design-quality metrics tie back to information-theoretic normal forms (Arenas–Libkin) and workload-cost models.

## 3. State of the Art (SOTA)
**Systems/data-SOTA.** **Metanome** (Papenbrock et al.) and its dataset repository are the de facto profiling benchmark, bundling real tables (e.g., from UCI, ncvoter, census) with discovered constraint sets. The **TPC** family (TPC-H, TPC-DS, TPC-C) provides schemas with *declared* keys/FKs usable as partial ground truth, and the **JOB / IMDB** workload is a standard relational corpus. Data-cleaning benchmarks — **BART** (Arocena et al., 2015) which injects controlled errors with known repairs — and cleaning corpora (Tax, Hospital, Flights) supply ground-truth constraints. **GitTables** and **WikiTables/ TURL** corpora support large-scale column/relationship discovery. The **VLDB experiments-and-analysis** track institutionalized rigorous head-to-head evaluation of discovery algorithms.

**Theory-SOTA.** No formal benchmark theory; the SOTA is methodological — implication-aware scoring and controlled error injection.

## 4. Upper Bound
There is no algorithmic upper bound to state; the relevant "bound" is *evaluation tractability*. Scoring a tool against $(I,\Sigma^\star)$ modulo implication is **polynomial** for FDs (closure comparison, $O(|\Sigma|^2 n)$) but as hard as **IND implication (PSPACE)** when ground truth includes INDs, and **undecidable** for arbitrary FD+IND closure (Chandra–Vardi) — so benchmarks must restrict $\Sigma^\star$ to a fragment where equivalence-up-to-implication is decidable. Controlled synthetic generation (BART-style) runs in time linear in injected-error count.

## 5. Lower Bound
The fundamental barrier is **information-theoretic / epistemic**, not complexity: ground-truth semantic constraints are *unknowable from data alone* (the genuine-vs-spurious gap), so any benchmark must either *plant* $\Sigma^\star$ (risking unrealistic data) or rely on *expert curation* (costly, subjective, limited scale). Scoring with IND ground truth inherits **PSPACE-hardness** of implication; with FD+IND, equivalence checking is **undecidable**. There is therefore no benchmark that is simultaneously fully realistic, large-scale, and provably ground-truth-correct — an inherent tension rather than a removable engineering gap.

## 6. The Gap
The gap is between (a) *real* datasets, which are realistic but lack trustworthy ground truth, and (b) *synthetic* datasets, which have ground truth but risk unrealistic dependency structure. It is empirically open: no accepted suite resolves the trade-off, and metrics are not standardized (implication-aware vs. raw overlap; design quality vs. discovery accuracy). Closing it means a community-curated, implication-aware, scale-varied suite with documented coincidence rates and expert-validated semantic labels.

## 7. Current Research (as of June 2026)
Active directions: (1) **LLM-assisted ground-truth curation** — using models to propose semantic constraints for expert confirmation, scaling annotation *(frontier — verify)*; (2) realistic synthetic data generators that plant constraints while matching real correlation structure (GAN/diffusion-based tabular generators with constraint conditioning) *(frontier — verify)*; (3) extending Metanome-style repositories with denial constraints, INDs, and design-quality labels; (4) reproducibility/artifact-evaluation norms (SIGMOD/VLDB availability badges). Groups: Naumann/Papenbrock (HPI), Abedjan (Hannover), Mecca–Papotti (BART), the TPC consortium, and data-discovery efforts at Northeastern (Miller) and MIT.

## 8. Future Work
- A standardized, implication-aware scoring protocol adopted across discovery papers.
- Realistic generators that provably control coincidental-dependency rates.
- Expert-curated ground truth for INDs/FKs and full designs, not just FDs.
- Benchmarks for end-to-end *design* tasks (decomposition, placement), not only discovery.

## 9. Key References
- **[SOTA]** Papenbrock, F., et al. *Functional Dependency Discovery: An Experimental Evaluation of Seven Algorithms.* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2794367.2794377)
- **[SOTA]** Arocena, P., Glavic, B., Mecca, G., Miller, R.J., Papotti, P., Santoro, D. *Messing Up with BART: Error Generation for Evaluating Data-Cleaning Algorithms.* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2850578.2850579)
- **[Foundational]** Transaction Processing Performance Council. *TPC-H / TPC-DS Benchmark Specifications.* TPC, 1999–. — [TPC](https://www.tpc.org/tpch/)
- **[Foundational]** Arenas, M., Libkin, L. *An Information-Theoretic Approach to Normal Forms for Relational and XML Data.* JACM, 2005. — [DOI](https://doi.org/10.1145/1059513.1059519)
- **[SOTA]** Hulsebos, M., et al. *GitTables: A Large-Scale Corpus of Relational Tables.* SIGMOD, 2023. — [DOI](https://doi.org/10.1145/3588710)
- **[Survey]** Abedjan, Z., Golab, L., Naumann, F. *Profiling Relational Data: A Survey.* VLDB Journal, 2015. — [DOI](https://doi.org/10.1007/s00778-015-0389-y)

## 10. Worked Example

Consider a planted ground truth $\Sigma^\star = \{A \to B\}$ over a 5-row table. A discovery tool outputs $\hat\Sigma = \{A \to B,\ \ AB \to B,\ \ C \to D\}$.

**Why raw overlap misleads.** Naively, $|\hat\Sigma \cap \Sigma^\star| = 1$, giving precision $1/3 \approx 0.33$. But $AB \to B$ is *trivial* (RHS $\subseteq$ LHS) and $A \to B \models AB \to B$, so it is in the closure of $\Sigma^\star$. Scoring **modulo implication** quotients it out: only $C \to D$ is a genuine false positive, so
$$\text{precision} = \frac{|\{A\to B\}|}{|\{A\to B,\ C\to D\}|} = \frac{1}{2} = 0.5, \qquad \text{recall} = \frac{|\{A\to B\}|}{|\Sigma^\star|} = 1.0.$$

**Coincidence rate.** Is $C \to D$ spurious or real? With only $m=5$ rows and $C$ having 5 distinct values, $C$ is a key, so *every* $C \to X$ holds accidentally — $g_3$-error $= 0$ despite no semantic dependency. This is exactly the genuine-vs-coincidental gap: shrinking $m$ inflates accidental FDs, so a good benchmark must report the expected coincidence count and tune $(m, n, \text{domain sizes})$ so that planted $\Sigma^\star$ is distinguishable from noise. This is why ground truth cannot be read off the instance alone.

---
*Part of the [DBMS Research catalog](../../README.md).*
