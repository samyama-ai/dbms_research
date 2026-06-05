# Inference Detection Complexity

> **Topic:** Database Security & Access Control · **ID:** `23-database-security/inference-detection-complexity` · **Status:** open

## 1. Problem Statement

The **inference problem**: a user is granted access to a set of views/queries $\mathcal{V}$ over a database $D$, but a *secret* (a tuple, a cell value, or a predicate $\phi$) is supposed to remain hidden. Even when no single authorized view discloses the secret directly, the *combination* of authorized views, together with knowledge of the schema, integrity constraints, and possibly the query language, may *logically entail* the secret. **Inference detection** is the task of deciding whether such an entailment exists.

Decision variant (**certain disclosure**): *Given views $\mathcal{V}$ with answers, constraints $\Sigma$, and a Boolean secret query $Q_s$, is $Q_s$ true in **every** database consistent with the observed view answers and $\Sigma$?* If yes, the secret is disclosed.

Counting / quantitative variant: *over how many consistent worlds is the secret true?* — relevant to probabilistic disclosure.

Optimization variant: *find a minimal set of additional restrictions (denied views, masked cells) that closes all inference channels.*

The open problem is to **pin the exact complexity** of these variants as a function of (i) the view/query language (CQ, UCQ, SQL with aggregation, recursive), (ii) the constraint class ($\Sigma$ being FDs, inclusion deps, general TGDs/EGDs), and (iii) data vs. combined complexity.

## 2. Mathematical Foundations

Frame inference as **certain answers** under open-world / closed-world assumptions. Given views $\mathcal{V}=\{V_i = \text{def}_i\}$ with observed extensions $v_i$, the set of *possible worlds* is

$$\mathcal{W} = \{\,D' \models \Sigma \;:\; V_i(D') = v_i \ \forall i\,\}.$$

A secret $Q_s$ is **certainly disclosed** iff $Q_s$ holds in all $D' \in \mathcal{W}$ (i.e., $\mathcal{W} \models Q_s$). This is dual to **certain answers** in data integration and to **view-based query determinacy**: $\mathcal{V}$ *determines* $Q_s$ iff $Q_s$ is constant across $\mathcal{W}$.

Key machinery:
- **The chase** computes a universal solution for TGD/EGD constraints; certain-answer evaluation reduces to query evaluation on the (possibly infinite) chase.
- **Query determinacy** ($\mathcal{V} \twoheadrightarrow Q$) and **rewritability** are the formal backbone; determinacy is known **undecidable** for UCQs and even for path queries in general.
- Complexity scales by language: CQ certain answers are **coNP-complete** in data complexity under TGDs; combined complexity can reach **PSPACE/EXPTIME**.
- Information-theoretic disclosure uses entropy: a channel leaks if $H(\text{secret} \mid \mathcal{V}) < H(\text{secret})$.

## 3. State of the Art (SOTA)

- **Certain answers under constraints** (Imieliński–Lipski; Abiteboul–Duschka): coNP-complete data complexity for CQs over incomplete databases.
- **View determinacy** (Nash–Segoufin–Vianu, 2010): determinacy and rewritability *diverge*; CQ-to-CQ determinacy is **undecidable** in general, decidable for restricted fragments (e.g., monadic, path-constrained).
- **Inference control systems**: Disclosure monitors of Brodsky–Farkas–Jajodia and the **controlled query evaluation (CQE)** line (Biskup–Bonatti) provide policy-enforcement with provable confidentiality, at the cost of refusal/lying.
- Systems-SOTA: practitioner inference auditing largely uses heuristics (functional-dependency closure, association-rule mining) rather than complete logical entailment.

## 4. Upper Bound

- CQ secret over CQ views with FDs/IDs: certain disclosure decidable, **coNP** (data complexity); combined complexity **$\Pi_2^p$** to **PSPACE** depending on constraint class.
- Under **weakly-acyclic** TGDs the chase terminates, giving **decidable** disclosure with EXPTIME combined complexity.
- CQE with refusal achieves provable non-disclosure online without solving full entailment, but only for restricted policy/query classes.

## 5. Lower Bound

- **coNP-hardness** in data complexity for CQ certain answers (hence disclosure).
- **Undecidability** of view determinacy for UCQs (Nash–Segoufin–Vianu) and for CQs with inequalities — so exact "does $\mathcal{V}$ leak $Q_s$?" is *undecidable* in expressive fragments.
- Combined complexity **PSPACE/EXPTIME-hardness** under general TGDs via chase-based reductions.
- Probabilistic/counting variant inherits **#P-hardness** from probabilistic-database query evaluation.

## 6. The Gap

The complexity is *known* at the extremes (coNP data complexity for monotone fragments; undecidable for general view determinacy) but **not tightly mapped across the lattice** of (language × constraints × disclosure-notion). In particular: the exact decidability boundary between determinacy-based exact inference and approximation-based detection is open; the gap between coNP membership and the actual hardness for specific practical fragments (e.g., SQL with bounded aggregation over key/foreign-key schemas) is not closed. Whether useful, expressive fragments admit *complete and tractable* inference detection — versus only sound heuristics — remains genuinely open.

## 7. Current Research (as of June 2026)

- Sharpening **determinacy/rewritability dichotomies** for navigational and graph query languages (regular path queries) *(frontier — verify)*.
- Linking inference control to **differential privacy** budgets: treating cumulative query disclosure as privacy-loss accounting rather than Boolean entailment.
- **SMT- and Datalog-based disclosure auditors** that handle SQL fragments with constraints, trading completeness for decidable, certifiable runs.
- Groups: data-integration/incomplete-information theory community (Vianu, Segoufin, Libkin lineage); the CQE/confidentiality-policy community (Biskup lineage) *(frontier — verify)*.

## 8. Future Work

- A full **complexity map** of inference detection parameterized by query language and constraint class, with dichotomy theorems.
- Bridging **logical certain-disclosure** and **statistical/DP disclosure** into one quantitative framework.
- Incremental inference monitors that re-decide disclosure as the authorized view set evolves.
- Tractable complete algorithms for industrially common schema/constraint idioms.

## 9. Key References

- **[Foundational]** Tomasz Imieliński, Witold Lipski. *Incomplete Information in Relational Databases.* Journal of the ACM, 1984. — [DOI](https://doi.org/10.1145/1634.1886)
- **[Foundational]** Serge Abiteboul, Oliver M. Duschka. *Complexity of Answering Queries Using Materialized Views.* PODS, 1998. — [DBLP search](https://dblp.org/search?q=Complexity+of+Answering+Queries+Using+Materialized+Views+Abiteboul)
- **[SOTA]** Alan Nash, Luc Segoufin, Victor Vianu. *Views and Queries: Determinacy and Rewriting.* ACM Transactions on Database Systems (TODS), 2010. — [DOI](https://doi.org/10.1145/1806907.1806913)
- **[Foundational]** Joachim Biskup, Piero A. Bonatti. *Controlled Query Evaluation for Enforcing Confidentiality in Complete Information Systems.* International Journal of Information Security, 2004. — [DOI](https://doi.org/10.1007/s10207-004-0032-1)
- **[Survey]** Csilla Farkas, Sushil Jajodia. *The Inference Problem: A Survey.* ACM SIGKDD Explorations, 2002. — [DOI](https://doi.org/10.1145/772862.772864)
- **[Foundational]** Serge Abiteboul, Richard Hull, Victor Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP search](https://dblp.org/search?q=Foundations+of+Databases+Abiteboul+Hull+Vianu)

## 10. Worked Example

Let the base relation be $\mathsf{Emp}(\text{name},\text{dept},\text{salary})$ with the **functional dependency** $\Sigma=\{\text{dept}\to\text{salary}\}$ (everyone in a department earns the same). The secret is the Boolean $Q_s$: *"Alice's salary $= 100$k."*

Authorized views:
- $V_1 = \pi_{\text{name},\text{dept}}(\mathsf{Emp})$, returning $v_1=\{(\text{Alice},\text{Sales}),(\text{Bob},\text{Sales})\}$.
- $V_2 = \pi_{\text{dept},\text{salary}}(\mathsf{Emp})$, returning $v_2=\{(\text{Sales},100\text{k})\}$.

Neither view names *both* Alice and a salary, so no single view discloses $Q_s$. But every possible world $D'\in\mathcal{W}$ must satisfy $v_1,v_2$ **and** $\text{dept}\to\text{salary}$. From $v_1$, Alice is in Sales; from $v_2$, Sales pays $100$k; the FD forces Alice's salary to equal the Sales salary $=100$k. Thus $Q_s$ holds in *all* $D'\in\mathcal{W}$ — a **certain disclosure** via the join $V_1\bowtie_{\text{dept}} V_2$ that the FD makes lossless. Drop the FD and $\mathcal{W}$ contains worlds where Alice earns $\neq100$k, so $Q_s$ is no longer certain — illustrating how the constraint class $\Sigma$, not just the view language, determines leakage.

---
*Part of the [DBMS Research catalog](../../README.md).*
