# Human-in-the-Loop Dependency Validation

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/human-in-the-loop-dependency-validation` · **Status:** empirically-open

## 1. Problem Statement
Automated discovery (of FDs, INDs, denial constraints, approximate dependencies) returns a large candidate set $\mathcal{D}$, many of which *hold on the instance by coincidence* rather than reflecting a genuine design intent. The problem: **minimize the human expert effort** (number/cost of yes-no validations, examples reviewed, or questions answered) needed to confidently separate **genuine** dependencies from **spurious** ones for use in schema (re)design.

- **Decision/labeling variant:** Given budget $B$ of expert questions, which subset of $\mathcal{D}$ to ask about to maximize correctly classified dependencies?
- **Optimization variant:** Minimize total expected expert cost to reach a target precision/recall on the genuine set, exploiting logical *implication* (confirming $X\to Z$ may settle $X\to Y, Y\to Z$).
- **Active-learning variant:** Sequentially choose the next dependency (or counterexample tuple) to label so as to maximize information gain.

The genuine-vs-spurious distinction is *semantic* and not determined by the instance, so this is intrinsically an interactive, human-supervised task — hence **empirically-open**: progress is measured by user studies, not closed-form bounds.

## 2. Mathematical Foundations
Dependencies are partially ordered by **logical implication** (Armstrong axioms for FDs; the chase for tgds/egds). This induces structure exploited for cheap validation: confirming/rejecting one dependency propagates through its implication cone, so the *effective* question set is the set of **non-redundant (minimal cover)** dependencies, dramatically smaller than $\mathcal{D}$.

The selection problem is an **active learning / optimal experimental design** instance. If a human label has cost $c_d$ and prior genuineness $p_d$, choosing questions to maximize expected correctly-resolved dependencies under budget is a **submodular maximization** (information gain is submodular), giving a $(1-1/e)$ greedy template, but the *implication coupling* breaks independence. Query complexity connects to **exact learning with membership/equivalence queries** (Angluin); learning Armstrong-style relations relates to **VC dimension** of the dependency hypothesis class and to teaching dimension.

Spuriousness has an information-theoretic null model: an approximate FD with error $g_3=\epsilon$ on $r$ rows can arise by chance with probability depending on column entropies; **Bayesian** scoring combines this likelihood with priors from naming, types, and value distributions to set $p_d$.

## 3. State of the Art (SOTA)
**Systems-SOTA.** **Armstrong relations** (Mannila–Räihä; Beeri–Dowd–Fagin–Statman) let a system present a small "perfect example" instance so an expert can confirm a whole FD set by inspecting representative tuples — the classic effort-reducing device. Interactive cleaning/discovery systems — **GDR (Guided Data Repair)** (Yakout et al., 2011), **UGuide** (Thirumuruganathan et al.) for FD validation, and **Falcon**/**HoloClean**-style active learning — choose high-value questions. **Raha/Baran** (Mahdavi–Abedjan) actively learn error detectors with few labels. Visualization tools (e.g., **Metanome** front-ends) help triage discovered constraints.

**Theory-SOTA.** Optimal-teaching and active-learning query-complexity results for FDs (sample/Armstrong-relation size bounds) frame the achievable lower question counts; submodular active selection gives the planning guarantee.

## 4. Upper Bound
Using a **minimal cover**, the number of FDs a human must inspect drops from potentially exponential $|\mathcal{D}|$ to the cover size; an **Armstrong relation** lets an expert validate an entire FD set by examining one instance whose size is **at most exponential but often small** (Beeri et al.). Greedy submodular question selection achieves the **$(1-1/e)$** guarantee on expected resolved-dependency value under a budget. Active-learning label complexity for separable dependency classes is **$O(\frac{1}{\epsilon}\log\frac{1}{\delta})$**-style under benign noise — but these hold only under model assumptions, not for real semantic intent.

## 5. Lower Bound
Genuine-vs-spurious is **not information-theoretically determined by the instance**: two dependencies with identical data footprints can differ in intent, so *no* algorithm achieves exact recovery without human input — a hard impossibility for the fully automatic version. Exact learning with only equivalence/membership queries has classical **query-complexity lower bounds** (Angluin): adversarial classes force $\Omega(|\text{cover}|)$ questions. Armstrong relations can require **exponential size** in the number of attributes in the worst case (Beeri–Dowd–Fagin–Statman), bounding how compactly a single example can certify a constraint set. Empirically, human accuracy/fatigue impose a non-formal but real ceiling.

## 6. The Gap
There is no formal upper/lower-bound matching here because the objective (semantic correctness) is human-defined; the gap is **empirical**. We have effort-reducing devices (covers, Armstrong relations, active learning) and planning guarantees, but no agreed benchmark establishing how few questions suffice on real schemas, nor calibrated spuriousness priors that hold across domains. Empirically-open: closing it means user studies + shared ground-truth (see *schema-design-benchmarks*) showing question-count vs. accuracy frontiers.

## 7. Current Research (as of June 2026)
Active directions: (1) **LLM-as-oracle / LLM-assisted triage** that pre-labels dependencies with explanations and reserves humans for low-confidence cases, reducing expert load *(frontier — verify)*; (2) active-learning policies that jointly pick the dependency *and* the most convincing counterexample tuple; (3) crowd + expert hybrid validation with quality control; (4) calibrated Bayesian spuriousness scoring fusing structural and semantic signals. Groups: Abedjan (Leibniz Hannover/TU Berlin), Ilyas–Chu (Waterloo), Naumann (HPI), Das/Thirumuruganathan (interactive discovery).

## 8. Future Work
- Standard benchmarks reporting *questions-to-target-accuracy* across domains.
- Provable label-complexity bounds under realistic noise + implication coupling.
- Trustworthy LLM oracles with abstention and uncertainty calibration for dependency intent.
- Mixed-initiative interfaces minimizing cognitive load, validated by user studies.

## 9. Key References
- **[Foundational]** Mannila, H., Räihä, K.-J. *Design by Example: An Application of Armstrong Relations.* JCSS, 1986.
- **[Foundational]** Beeri, C., Dowd, M., Fagin, R., Statman, R. *On the Structure of Armstrong Relations for Functional Dependencies.* JACM, 1984.
- **[Foundational]** Angluin, D. *Queries and Concept Learning.* Machine Learning, 1988.
- **[SOTA]** Yakout, M., Elmagarmid, A., Neville, J., Ouzzani, M., Ilyas, I. *Guided Data Repair.* PVLDB, 2011.
- **[SOTA]** Mahdavi, M., Abedjan, Z., et al. *Raha: A Configuration-Free Error Detection System.* SIGMOD, 2019.
- **[Foundational]** Nemhauser, G., Wolsey, L., Fisher, M. *An Analysis of Approximations for Maximizing Submodular Set Functions.* Math. Programming, 1978.

---
*Part of the [DBMS Research catalog](../../README.md).*
