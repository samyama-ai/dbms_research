# Active Learning for Constraint Acquisition

> **Topic:** Data Cleaning & Quality · **ID:** `16-data-cleaning-quality/active-constraint-acquisition` · **Status:** partially-solved

## 1. Problem Statement

Cleaning needs constraints (FDs, conditional FDs, denial constraints, matching/ER rules), but writing them by hand is hard and discovering them automatically yields noisy, overfit rule sets. The problem: **interactively acquire a high-quality constraint set $\Sigma$** by asking a human (oracle) a minimal number of well-chosen questions — "is this tuple pair a violation?", "is this rule valid?", "should these records match?" — with guarantees on (a) sample/query complexity and (b) convergence to the target constraints.

Variants:
- **Decision/realizability:** Is the target constraint set $\Sigma^\*$ exactly learnable from a given query type at all?
- **Query-complexity optimization:** Minimize the number of oracle queries (label budget) to reach error $\le \epsilon$.
- **Robust acquisition:** Converge despite a *noisy* or *erroneous* oracle (humans make mistakes).

This sits at the intersection of constraint discovery (the hypothesis space) and active learning (the querying strategy).

## 2. Mathematical Foundations

- **Constraint discovery base:** FD/DC discovery (TANE, FastFDs, FastDCs/Hydra) defines the hypothesis lattice; a discovered DC is a conjunction of predicates over tuple pairs that no pair satisfies.
- **PAC / active learning theory:** a concept class of constraints has **VC dimension** $d$; passive PAC needs $\Theta\!\big(\tfrac{1}{\epsilon}(d + \log\tfrac1\delta)\big)$ labels, while active learning can reach $O\!\big(\theta\, d\, \mathrm{polylog}\tfrac{1}{\epsilon}\big)$ where $\theta$ is the **disagreement coefficient** (Hanneke) — an exponential label saving when $\theta$ is small.
- **Exact learning with queries (Angluin):** membership + equivalence queries can exactly identify some constraint classes; lower bounds via the *approximate fingerprint* method.
- **Submodularity:** the "information gained" by asking about violations is often (approximately) submodular, so greedy question selection gives a $(1-1/e)$ guarantee on coverage of the violation space.
- **Version spaces:** maintain the set of constraints consistent with answers so far; an optimal query *splits* the version space — connecting to generalized binary search and its $O(\log|\mathcal{H}|)$ bounds.

## 3. State of the Art (SOTA)

- **Constraint discovery** — Hydra (Bleifuß et al., VLDB 2017) discovers all minimal denial constraints efficiently; TANE/FastFDs remain FD baselines.
- **Interactive cleaning with oracles** — Raha/Baran (Mahdavi, Abedjan et al., SIGMOD 2019/2020): configuration-free error detection and value correction that actively solicit a small label budget and propagate via learned models.
- **Rule/example-driven systems** — GDR / interactive repair (Yakout, Elmagarmid et al.) rank candidate repairs and learn from user feedback.
- **ER active learning** — active learning for entity matching (Sarawagi–Bhamidipaty 2002; Mozafari et al. 2014 crowd; recent deep-ER active sampling) minimizes labeled pairs.
- **LLM-as-oracle** — recent work uses LLMs to answer validity/matching questions in place of (or to pre-filter for) humans *(frontier — verify)*.

## 4. Upper Bound

- For constraint classes with VC dimension $d$ and disagreement coefficient $\theta$: active acquisition reaches error $\epsilon$ with **$O(\theta d \,\mathrm{polylog}(1/\epsilon))$** oracle queries (agnostic active learning, Dasgupta; Hanneke).
- Greedy violation-coverage question selection achieves a **$(1-1/e)$**-approximation to the optimal information-per-question schedule (submodular maximization, Nemhauser–Wolsey–Fisher).
- Exact identification of FD/DC sets needs at most $O(|\Sigma^\*| \cdot \text{poly})$ equivalence/membership queries for learnable subclasses (Angluin-style).

## 5. Lower Bound

- **Information-theoretic:** any algorithm needs $\Omega(\tfrac{1}{\epsilon}(d+\log\tfrac1\delta))$ labels in the *worst-case passive* setting; active learning cannot beat $\Omega(\theta)$ factors when the disagreement coefficient is large (there exist classes where active = passive).
- **Discovery hardness:** finding a *minimum-size* covering DC/FD set is **NP-hard** (set-cover reduction); enumerating all minimal FDs can be **exponential** in the number of attributes (output-size lower bound).
- **Noisy oracle:** with oracle error rate $\eta$, exact identification is impossible; query complexity gains an extra $\Omega(1/(1-2\eta)^2)$ factor (Castro–Nowak noisy-active-learning bound).

## 6. The Gap

**Partially solved.** Where the hypothesis class is simple (FDs over few attributes, ER pair-matching) and the oracle is clean, active acquisition has *matching* upper/lower query-complexity bounds via classical active-learning theory. The gap is genuinely open for: (i) **rich classes** (general DCs, cross-table matching rules) where VC dimension and disagreement coefficient are not characterized; (ii) **noisy/inconsistent human oracles** with provable convergence; (iii) **non-i.i.d. data** (selection-biased samples), where standard PAC guarantees break. Closing it needs VC/teaching-dimension analyses for denial-constraint lattices and robust query strategies for imperfect oracles.

## 7. Current Research (as of June 2026)

- LLMs as cheap, noisy oracles with human verification only on disagreements; calibration of LLM confidence into active-learning budgets *(frontier — verify)*.
- Weak-supervision / data-programming (Snorkel lineage) fused with active constraint elicitation.
- Acquisition under fairness constraints — ensuring elicited rules don't encode protected-attribute proxies (links to Fairness-Aware Cleaning).
- Theory of active learning of *structured* objects (rule sets, not single classifiers) with combinatorial query complexity (Abedjan, Stoyanovich, Ilyas groups) *(frontier — verify)*.

## 8. Future Work

- VC/disagreement-coefficient characterization of denial-constraint and matching-rule classes.
- Provably convergent acquisition with bounded-error (Byzantine) oracles.
- Joint active discovery of constraints *and* repairs in one budget-optimal loop.
- Transfer: reuse constraints learned on one dataset to warm-start acquisition on related schemas.

## 9. Key References

- **[Foundational]** Angluin. *Queries and Concept Learning.* Machine Learning, 1988.
- **[Foundational]** Hanneke. *Theory of Disagreement-Based Active Learning.* Foundations and Trends in ML, 2014.
- **[Foundational]** Sarawagi, Bhamidipaty. *Interactive Deduplication using Active Learning.* KDD, 2002.
- **[SOTA]** Bleifuß, Kruse, Naumann. *Efficient Denial Constraint Discovery with Hydra.* VLDB, 2017.
- **[SOTA]** Mahdavi et al. *Raha: A Configuration-Free Error Detection System.* SIGMOD, 2019.
- **[SOTA]** Mahdavi, Abedjan. *Baran: Effective Error Correction via a Unified Context Representation.* VLDB, 2020.

---
*Part of the [DBMS Research catalog](../../README.md).*
