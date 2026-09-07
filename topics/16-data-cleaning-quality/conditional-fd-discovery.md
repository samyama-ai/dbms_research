---
id: 16-data-cleaning-quality/conditional-fd-discovery
title: "Scalable Conditional FD Discovery"
topic: 16-data-cleaning-quality
status: partially-solved
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Scalable Conditional FD Discovery

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/conditional-fd-discovery` · **Status:** partially-solved

## 1. Problem Statement

A **conditional functional dependency (CFD)** is an FD that holds only on the sub-relation selected by a *pattern tuple*: $(X \rightarrow Y,\ t_p)$ where $t_p$ binds some attributes to constants (and others to the wildcard `_`). CFDs capture data-quality rules far more expressive than plain FDs (e.g., "in country = US, ZIP $\rightarrow$ state"). **CFD discovery** is: given an instance $I$ (and thresholds), find a **minimal, non-redundant** set of CFDs that (approximately) hold, with **statistical reliability** (support, confidence) so that spurious, overfit, or coincidental rules are excluded — and do so **at scale** in rows and columns.

Variants:
- **Exact:** all CFDs holding with zero violations.
- **Approximate:** CFDs holding with confidence $\ge \delta$ and support $\ge s$ (tolerating noise).
- **Top-$k$ / interesting:** rank by an interestingness/reliability measure.
- **Decision:** Does a CFD with given support/confidence exist?

## 2. Mathematical Foundations

The CFD search space is the product of the **FD lattice** over attribute subsets ($2^{|R|}$ left-hand sides) and the **pattern space** of constant bindings drawn from active domains — exponential in attributes and polynomial-to-large in domain sizes. Core machinery:

- **Partition refinement / stripped partitions** (TANE-style): each attribute set $X$ induces an equivalence partition $\pi_X$; $X \rightarrow A$ holds iff $\pi_X$ refines $\pi_{X\cup A}$, checkable by error measure $e(X\rightarrow A)=1-|\pi_{X\cup A}|/|\pi_X|$. CFDs extend this to *per-partition-class* (per-pattern) checks.
- **Support / confidence**: $\mathrm{supp}(t_p)=$ fraction of tuples matching the pattern; $\mathrm{conf}=$ fraction among them satisfying the FD. Statistical reliability adds **significance testing / MDL** to avoid rules that fit noise — connecting to **information theory** (MDL: a rule is kept only if it compresses the data) and to **multiple-hypothesis correction**.
- Minimality is defined via a partial order (a CFD is redundant if implied by more general ones); the implication problem for CFDs is in PTIME for the standard semantics but the *discovery* enumeration is output-exponential.

## 3. State of the Art (SOTA)

- **CFD foundations:** Fan, Geerts, Jia, Kementsietsidis (TODS 2008) — semantics, axiomatization, and the implication/consistency problems.
- **Discovery algorithms:** **CTANE** and **FastCFD** (Fan, Geerts, Li, Xiong, TKDE 2011) — lattice-based (CTANE) and depth-first (FastCFD) CFD miners; **CFDMiner** for constant CFDs.
- **Approximate / reliable discovery:** algorithms adding support/confidence thresholds and pruning; **Pyro**, **HyFD**/**HyUCC**-style hybrid pruning (Papenbrock & Naumann, SIGMOD/VLDB 2016) for FDs adapted toward CFDs.
- **Systems / scale:** **Metanome** (Papenbrock et al., VLDB 2015) profiling platform; distributed CFD/DC discovery (e.g., **DCFinder** for denial constraints, Pena et al., 2019) and sampling-based miners. Recent statistical/learned CFD discovery. *(frontier — verify)*

## 4. Upper Bound

- Exact lattice discovery (CTANE): time roughly $O(|R|^2 \cdot 2^{|R|} \cdot n)$ in the worst case (exponential in attributes, linear-ish per level via partition refinement); FastCFD is **output-sensitive** with depth-first pruning, better on wide schemas.
- Sampling / focused-sampling reduces the row factor: confidence estimable from a sample of size $O(\varepsilon^{-2}\log(1/\delta))$ by Hoeffding/Chernoff bounds — giving probabilistic reliability with sublinear data passes.
- Hybrid pruning (HyFD-style) gives large constant-factor practical speedups, near-linear in many real instances.

## 5. Lower Bound

- The number of minimal CFDs can be **exponential in the number of attributes**, so any complete discovery algorithm is **output-exponential** — an unavoidable enumeration lower bound.
- Deciding existence of a non-trivial FD/CFD with given error is tied to problems whose worst case is exponential; the FD-discovery search space has provably exponential minimal-cover size in the worst case.
- **Statistical lower bound:** distinguishing a true CFD from a coincidental one requires support $\Omega(\varepsilon^{-2})$ samples per pattern (concentration/VC-type bound); rare patterns are information-theoretically unverifiable.

## 6. The Gap

**Partially solved**: exact discovery is well-understood (CTANE/FastCFD) but does not scale to wide schemas or large domains; sampling and hybrid pruning scale rows but the **column/pattern blow-up** remains. The open gap is a discovery method that is simultaneously (i) **scalable in attributes and domain size**, (ii) **statistically reliable** (controls false-discovery rate under multiple testing), and (iii) yields a **minimal, semantically useful** rule set for repair — no single algorithm achieves all three with guarantees. Bridging requires output-sensitive enumeration with built-in significance control and principled approximate-confidence semantics.

## 7. Current Research (as of June 2026)

- **Reliable / FDR-controlled** CFD and DC discovery that filters spurious rules via statistical testing and MDL (Naumann/Papenbrock, Abedjan groups). *(frontier — verify)*
- **Sampling- and sketch-based** scalable miners; GPU/distributed discovery. *(frontier — verify)*
- **LLM-assisted / learned** discovery proposing semantically meaningful CFDs validated against data. *(frontier — verify)*
- **Discovery-to-repair pipelines** that mine CFDs and feed holistic repair end-to-end. *(frontier — verify)*

## 8. Future Work

- Output-sensitive discovery with provable false-discovery-rate control.
- Joint discovery across CFDs, DCs, and inclusion dependencies.
- Active / interactive discovery using user feedback to prune semantically.
- Streaming and incremental CFD maintenance under updates.

## 9. Key References

- **[Foundational]** Fan, Geerts, Jia, Kementsietsidis. *Conditional Functional Dependencies for Capturing Data Inconsistencies.* ACM TODS, 2008. — [DOI](https://doi.org/10.1145/1366102.1366103)
- **[Foundational]** Huhtala, Kärkkäinen, Porkka, Toivonen. *TANE: An Efficient Algorithm for Discovering Functional and Approximate Dependencies.* Computer Journal, 1999. — [DOI](https://doi.org/10.1093/comjnl/42.2.100)
- **[SOTA]** Fan, Geerts, Li, Xiong. *Discovering Conditional Functional Dependencies.* IEEE TKDE, 2011. — [DOI](https://doi.org/10.1109/TKDE.2010.154)
- **[SOTA]** Papenbrock, Naumann. *A Hybrid Approach to Functional Dependency Discovery (HyFD).* SIGMOD, 2016. — [DOI](https://doi.org/10.1145/2882903.2915203)
- **[SOTA]** Papenbrock et al. *Functional Dependency Discovery: An Experimental Evaluation of Seven Algorithms.* VLDB, 2015 (and Metanome platform). — [DOI](https://doi.org/10.14778/2794367.2794377)
- **[Survey]** Abedjan, Golab, Naumann. *Profiling Relational Data: A Survey.* VLDB Journal, 2015. — [DOI](https://doi.org/10.1007/s00778-015-0389-y)

## 10. Worked Example

Relation $\text{Addr}(\text{country}, \text{ZIP}, \text{state})$:

| country | ZIP   | state |
|---------|-------|-------|
| US      | 10001 | NY    |
| US      | 10001 | NY    |
| US      | 90001 | CA    |
| UK      | EC1   | —     |
| UK      | EC1   | —     |

The plain FD $\text{ZIP} \rightarrow \text{state}$ holds here, but we want the *conditional* rule restricted to US. Consider the CFD $(\text{ZIP} \rightarrow \text{state},\ t_p = (\text{country}{=}\text{US}))$.

Support: 3 of 5 tuples match $\text{country}{=}\text{US}$, so $\mathrm{supp} = 3/5 = 0.6$. Among those, ZIP determines state with zero violations (10001 $\to$ NY twice, 90001 $\to$ CA once), so $\mathrm{conf} = 3/3 = 1.0$.

Partition check (TANE-style): on the US sub-relation, $\pi_{\text{ZIP}} = \{\{t_1,t_2\},\{t_3\}\}$ and $\pi_{\text{ZIP,state}}$ is identical, so $\pi_{\text{ZIP}}$ refines $\pi_{\text{ZIP,state}}$; error $e = 1 - |\pi_{\text{ZIP,state}}|/|\pi_{\text{ZIP}}| = 1 - 2/2 = 0$. The CFD is exact.

Statistical caution: with only 3 supporting tuples, distinguishing this from a coincidence needs $\Omega(\varepsilon^{-2})$ samples per pattern — so at small support the rule should be flagged as not yet reliable.

---
*Part of the [DBMS Research catalog](../../README.md).*
