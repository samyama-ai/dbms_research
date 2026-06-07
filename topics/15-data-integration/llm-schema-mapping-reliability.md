---
id: 15-data-integration/llm-schema-mapping-reliability
title: "LLM-Based Mapping Reliability"
topic: 15-data-integration
status: empirically-open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# LLM-Based Mapping Reliability

> **Topic:** Data Integration & Schema Mapping · **ID:** `15-data-integration/llm-schema-mapping-reliability` · **Status:** empirically-open

## 1. Problem Statement

Large language models are increasingly used to *generate* schema mappings: given a source schema $\mathbf{S}$, a target schema $\mathbf{T}$, sample instances, and natural-language hints, an LLM proposes attribute correspondences, GLAV/st-tgd mapping rules, or executable transformation code (SQL/SparkSQL/Python). The reliability problem: such outputs are **unverified and hallucination-prone** — the model may invent attributes absent from either schema, emit semantically plausible but logically incorrect joins, silently drop constraints, or produce different mappings across runs (non-reproducibility under temperature/prompt variation).

The problem is to make LLM-generated mappings **verifiable, hallucination-bounded, and reproducible against formal mapping semantics**. Concretely: (i) **verification** — decide whether a proposed mapping $\mathcal{M}$ is *sound* (every produced fact is justified by source + correspondences) and *complete* relative to a specification (examples, constraints, or a gold mapping); (ii) **hallucination bounding** — guarantee or certify that no rule references symbols outside $\mathbf{S} \cup \mathbf{T}$ and that every existential is Skolemized rather than fabricated; (iii) **reproducibility** — characterize and reduce output variance so the same inputs yield semantically equivalent mappings.

Variants: **decision** (is $\mathcal{M}$ semantically equivalent to a reference $\mathcal{M}^*$?), **certification** (produce a checkable witness of soundness/coverage), **repair** (minimally edit an LLM output to satisfy the spec), and **empirical** (precision/recall of correspondences vs. a benchmark).

## 2. Mathematical Foundations

The verification target rests on classical schema-mapping semantics: a mapping is a set of **st-tgds** $\forall \bar x\, (\varphi_{\mathbf S}(\bar x) \rightarrow \exists \bar y\, \psi_{\mathbf T}(\bar x,\bar y))$ (Fagin–Kolaitis–Miller–Popa). **Mapping equivalence** has three flavors — logical, data-exchange, and CQ-equivalence (Fagin–Kolaitis–Nash–Popa, *Towards a Theory of Schema-Mapping Optimization*, PODS 2008) — and equivalence/containment of GLAV mappings is decidable but **$\Pi_2^p$/undecidable** for rich classes. Verification against **examples** uses the *fitting/learnability* framework (ten Cate–Dalmau–Kolaitis): a finite set of universal/data examples can *uniquely characterize* a GLAV mapping, giving a sound checkable contract.

Hallucination is formalized as a **vocabulary/conservativity** condition: $\mathrm{sig}(\mathcal{M}) \subseteq \mathrm{sig}(\mathbf{S}) \cup \mathrm{sig}(\mathbf{T})$, checkable in linear time, plus a *no-invention* property — the chase of $\mathcal{M}$ introduces only labeled nulls, never fresh constants. Reproducibility connects to LLM **decoding stochasticity**: outputs are samples from $p_\theta(\cdot \mid \text{prompt})$; semantic-equivalence-rate over samples is the natural metric, and **self-consistency / majority voting** plus **conformal prediction** give distribution-free coverage guarantees ($\Pr[\text{correct} \in \text{prediction set}] \ge 1-\alpha$).

## 3. State of the Art (SOTA)

- **Systems-SOTA.** LLM matchers/mappers: **Jellyfish** (Zhang et al., 2023) and the matching prompts of **Narayan et al.** (*Can Foundation Models Wrangle Your Data?*, VLDB 2022) show GPT-class models are competitive zero/few-shot entity- and schema-matchers. **Ditto**'s pre-LLM transformer matching (Li et al., VLDB 2021) remains a strong learned baseline. RAG-style schema-mapping assistants and "text-to-mapping" tools are emerging in industrial catalogs.
- **Theory-SOTA.** The **fitting/unique-characterization** results for GLAV mappings (ten Cate, Kolaitis et al., PODS/LICS 2018–2023) provide the formal verification backbone; no LLM-specific tight reliability theory exists yet — hence *empirically-open*.

## 4. Upper Bound

Given a candidate mapping and a set of $n$ data examples, **checking** whether $\mathcal{M}$ fits all examples is in **PTime data complexity** (chase + homomorphism check) for GLAV mappings with terminating chase. Vocabulary/conservativity checking is **linear**. Deciding equivalence of two GLAV mappings is **decidable** (in $\Pi_2^p$ for CQ-equivalence of bounded mappings; ten Cate–Kolaitis). Conformal-prediction wrappers give a **distribution-free** $1-\alpha$ coverage guarantee on the validated set with $O(k)$ samples per instance. Model: standard RAM/Turing (verification) and exchangeability assumption (conformal coverage).

## 5. Lower Bound

The hard core is verification *against intent*, not against a fixed spec. **Logical equivalence** of unrestricted GLAV/second-order mappings is **undecidable** (reduces from CQ/Datalog equivalence and SO-tgd issues; Fagin–Kolaitis–Nash–Popa). Even CQ-equivalence is **$\Pi_2^p$-hard**. There is an **information-theoretic** floor: with only $n$ finite examples, infinitely many inequivalent mappings fit, so no algorithm can certify the *intended* mapping without a uniqueness/fitting precondition (a learning lower bound). For the LLM itself, **hallucination is not bounded by any in-model guarantee** — non-conservative outputs occur with positive probability under sampling, so external verification is provably necessary. Model: undecidability/$\Pi_2^p$ (verification), sample-complexity (learnability), no impossibility *closing* the empirical gap is known.

## 6. The Gap

This is **empirically open**: the *verification* side is theoretically grounded (decidable fitting, equivalence, conservativity), but the *generation* side has no formal reliability guarantee. The gap is between (a) what we can *check* in PTime given a spec and (b) the absence of any spec that pins down user intent precisely enough for LLM output to be certified end-to-end. No experiment yet establishes the achievable Pareto frontier of *correspondence precision/recall vs. human-effort-to-specify*, and no LLM mapper carries a soundness certificate. Closing it needs (i) standard benchmarks with gold mappings *and* example sets, (ii) a verifier-in-the-loop architecture with proven conservativity, and (iii) calibrated abstention so the model declines rather than hallucinates.

## 7. Current Research (as of June 2026)

Active directions: **verifier-in-the-loop / generate-then-check** pipelines that run the chase and reject non-fitting mappings; **conformal abstention** for matching decisions; **neuro-symbolic mapping synthesis** combining LLM proposals with the ten Cate–Kolaitis fitting algorithm as an oracle. *(frontier — verify)* Benchmarks extending Valentine and the Magellan/DeepMatcher suites with *mapping-level* (not just match-level) gold standards. *(frontier — verify)* Self-consistency and LLM-as-judge reliability studies for data engineering at SIGMOD/VLDB 2025–2026. Groups: Kolaitis & ten Cate (UCSC), Doan/Govind (Wisconsin, Magellan), Papotti (EURECOM), Tang/Naumann (HPI), Halevy (industrial data integration), with theory anchors from the fitting-mappings line.

## 8. Future Work

- A **soundness certificate** emitted alongside every LLM mapping, machine-checkable by a chase verifier.
- **Calibrated abstention**: principled "I don't know" instead of hallucinated correspondences.
- **Reproducibility metrics** and decoding strategies that bound semantic-equivalence variance.
- Mapping-level benchmarks with gold st-tgds and uniquely-characterizing example sets.
- Tight characterization of which schema-pair classes LLMs map reliably vs. systematically fail.

## 9. Key References

- **[Foundational]** R. Fagin, P. Kolaitis, R. Miller, L. Popa. *Data exchange: semantics and query answering.* Theoretical Computer Science, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[Foundational]** R. Fagin, P. Kolaitis, A. Nash, L. Popa. *Towards a theory of schema-mapping optimization.* PODS, 2008. — [DOI](https://doi.org/10.1145/1376916.1376922)
- **[Foundational]** B. ten Cate, V. Dalmau, P. Kolaitis. *Learning schema mappings.* ICDT / ACM TODS, 2013. — [DOI](https://doi.org/10.1145/2539032.2539035)
- **[SOTA]** A. Narayan, I. Chami, L. Orr, C. Ré. *Can foundation models wrangle your data?* PVLDB, 2022. — [arXiv](https://arxiv.org/abs/2205.09911)
- **[SOTA]** Y. Li, J. Li, Y. Suhara, A. Doan, W.-C. Tan. *Deep entity matching with pre-trained language models (Ditto).* PVLDB, 2021. — [arXiv](https://arxiv.org/abs/2004.00584)
- **[SOTA]** H. Zhang et al. *Jellyfish: A large language model for data preprocessing.* 2023. — [arXiv](https://arxiv.org/abs/2312.01678)
- **[Survey]** V. Vovk, A. Gammerman, G. Shafer. *Algorithmic Learning in a Random World* (conformal prediction). Springer, 2005. — [DOI](https://doi.org/10.1007/b106715)

## 10. Worked Example

Source $\mathbf{S}$: $\mathit{Emp}(\mathit{eid},\mathit{name},\mathit{dept})$. Target $\mathbf{T}$: $\mathit{Person}(\mathit{pid},\mathit{fullname})$, $\mathit{Works}(\mathit{pid},\mathit{deptname})$.

An LLM proposes the st-tgd:

$$\forall e,n,d\;\big(\mathit{Emp}(e,n,d) \rightarrow \exists p\;(\mathit{Person}(p,n) \wedge \mathit{Works}(p,d))\big)$$

**Conservativity check** (linear): every symbol used — $\mathit{Person},\mathit{Works},\mathit{Emp}$, and variables — lies in $\mathrm{sig}(\mathbf{S})\cup\mathrm{sig}(\mathbf{T})$. Pass. The existential $p$ becomes a labeled null, not a fabricated constant. Pass.

**Fitting check** against one data example: source $\{\mathit{Emp}(1,\text{Ada},\text{Sales})\}$, expected target containing $\mathit{Person}(p_0,\text{Ada})$, $\mathit{Works}(p_0,\text{Sales})$. Chase the source with $\mathcal{M}$: introduce null $N$, produce $\mathit{Person}(N,\text{Ada})$, $\mathit{Works}(N,\text{Sales})$. Homomorphism $N\mapsto p_0$ exists → **fits** (PTime).

Now a *hallucinated* variant adds $\mathit{Works}(p,\text{"HR"})$ with constant "HR" absent from the source row. Conservativity still passes (HR is a constant, not a relation), but the fitting check **fails** — the chase yields an extra HR fact with no witness in the example. The verifier rejects it. This is exactly the generate-then-check loop: cheap conservativity catches symbol invention; the chase catches semantic over-production.

---
*Part of the [DBMS Research catalog](../../README.md).*
