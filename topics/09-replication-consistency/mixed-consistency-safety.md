# Mixing strong and weak consistency safely

> **Topic:** Replication & Consistency · **ID:** `09-replication-consistency/mixed-consistency-safety` · **Status:** partially-solved

## 1. Problem Statement

Applications want *most* operations to be fast and available (weak/eventual consistency) while a *few* critical operations are strongly consistent (linearizable / serializable) — e.g., an inventory app where "view stock" is eventual but "last-item purchase" must be coordinated. The problem: provide a **programming model and static analysis** under which strong and weak operations *coexist* on shared replicated state without violating application invariants, and without forcing the programmer to manually reason about every interleaving.

Concretely: given a set of operations, each annotated (or inferred) as strong or weak, and a set of invariants $\mathcal{I}$, **decide** whether the mixed execution preserves $\mathcal{I}$ under all admissible interleavings; if not, **synthesize** the minimal set of operations that must be promoted to strong (or the minimal coordination/tokens) to restore safety. Variants: decision (safety checking), synthesis (minimal strengthening — an optimization), and verification (machine-checked proof). Status **partially-solved**: sound analyses exist (RedBlue, Indigo, MixT, CISE) but completeness, expressive invariants, and full-program automation remain open.

## 2. Mathematical Foundations

Model replicated state as an object with operations; an execution is a partial order of effects with a **visibility** relation $\text{vis}$ and **arbitration** $\text{ar}$ (Burckhardt's *replicated data type* framework). Weak (blue) operations commute and may be applied in different orders at different replicas; strong (red) operations are globally ordered. **RedBlue consistency** (Li et al., OSDI 2012): an operation is *blue* (eventually-consistent, may be reordered) iff its *generator/shadow* form **commutes** with all other operations and is **globally invariant-preserving**; otherwise it is *red* (totally ordered).

The **CISE** logic (Gotsman et al., POPL 2016) gives a proof rule: invariants are preserved iff (i) each operation individually preserves $\mathcal{I}$ (sequential safety), (ii) operations that may **not commute** are ordered (a *token* / conflict relation), and (iii) any pair whose concurrent execution could break $\mathcal{I}$ is forbidden concurrently. This reduces to discharging Hoare-style verification conditions and a *stability* check against concurrent effects — often via SMT. Type systems like **MixT** (Milano–Myers, PLDI 2018) use **information-flow types** to prevent data from a weaker consistency level illegally influencing a stronger computation, with a noninterference soundness theorem.

## 3. State of the Art (SOTA)

- **RedBlue consistency** (Li et al., OSDI 2012) + Gemini system: shadow operations classified red/blue.
- **Indigo** (Balegas et al., EuroSys 2015): invariant-preserving eventual consistency with reservations/escrow to avoid coordination.
- **CISE** (Gotsman, Yang, Ferreira, Najafzadeh, Shapiro, POPL 2016): a sound proof rule + tool (CISE3) for "cause I'm strong enough" reasoning.
- **MixT** (Milano–Myers, PLDI 2018): a mixed-consistency language with information-flow types and *mixed-consistency transactions*.
- **Quelea** (Sivaramakrishnan et al., PLDI 2015): declarative contracts compiled to consistency levels via an SMT-backed classifier.
- **Hamsaz / Hampa** (Houshmand–Lesani, POPL 2019): automatic synthesis of coordination-avoidant replicated objects with correctness/optimality.

## 4. Upper Bound

Sound *checking* is decidable when invariants and operation effects fall in decidable SMT theories (linear arithmetic, arrays, EUF): CISE/Quelea/Hamsaz discharge VCs in NP-to-PSPACE-ish SMT regimes, terminating in practice. Hamsaz computes a *minimal* (often optimal) set of operation pairs to coordinate / conflict relation, i.e., minimal strengthening, via a reduction to a covering problem over non-commuting/non-stable pairs. MixT's type-checking is polynomial and *sound by construction*. These give automated, sound (if conservative) safety.

## 5. Lower Bound

Invariant preservation under arbitrary concurrent updates is **undecidable** in general (it subsumes verifying arbitrary program assertions / reachability for unbounded state — reduction from Turing-machine halting / Hoare-triple validity). Even restricted to first-order invariants over unbounded relations, checking is at least co-NP-hard and often undecidable depending on the theory. The **CALM theorem** (Hellerstein; Ameloot–Neven–Van den Bussche, PODS 2011) provides the boundary: a query/program has a coordination-free (monotone) implementation *iff* it is expressible in monotonic logic — non-monotone invariants provably require coordination, a fundamental lower bound on what can stay "blue."

## 6. The Gap

Sound, automated analyses exist; the gap is **completeness and expressiveness**. Current tools are conservative (may force unnecessary coordination), handle limited invariant logics (mostly numeric/relational first-order, struggling with quantifier alternation, aggregation, recursion), and verify *objects/transactions* rather than whole applications with derived/joined invariants. Synthesizing *provably minimal* coordination for rich invariants is open. Closing it needs: decidable-but-expressive invariant fragments, completeness results (when does the analysis reject only genuinely-unsafe programs?), and integration with the *partial-replication / causal+* setting where visibility is itself partial.

## 7. Current Research (as of June 2026)

Active: extending CISE-style reasoning to richer invariants and to transactions with mixed isolation *(frontier — verify)*; automatic, *optimal* coordination synthesis beyond Hamsaz (handling aggregates and referential integrity) *(frontier — verify)*; mechanized (Coq/Iris) proofs of mixed-consistency soundness; and LLM-assisted invariant/annotation inference to reduce programmer burden *(frontier — verify)*. Key groups: Shapiro/Gotsman/Najafzadeh lineage (IMDEA, Sorbonne), Lesani (UC Riverside), Myers/Milano (Cornell), Sivaramakrishnan (IIT Madras).

## 8. Future Work

- Completeness theorems and tighter decidable invariant fragments.
- Whole-program mixed-consistency verification with derived invariants and foreign keys.
- Optimal coordination synthesis for aggregates, uniqueness, and referential integrity.
- Mixed consistency under genuine partial replication / causal+.

## 9. Key References

- **[Foundational]** Li, C. et al. *Making Geo-Replicated Systems Fast as Possible, Consistent when Necessary (RedBlue).* OSDI, 2012. — [DBLP](https://dblp.org/rec/conf/osdi/LiPCGPR12.html)
- **[SOTA]** Gotsman, A., Yang, H., Ferreira, C., Najafzadeh, M., Shapiro, M. *'Cause I'm Strong Enough: Reasoning About Consistency Choices in Distributed Systems (CISE).* POPL, 2016. — [DOI](https://doi.org/10.1145/2837614.2837625)
- **[SOTA]** Balegas, V. et al. *Putting Consistency Back into Eventual Consistency (Indigo).* EuroSys, 2015. — [DOI](https://doi.org/10.1145/2741948.2741972)
- **[SOTA]** Milano, M., Myers, A. *MixT: A Language for Mixing Consistency in Geodistributed Transactions.* PLDI, 2018. — [DOI](https://doi.org/10.1145/3192366.3192375)
- **[SOTA]** Houshmand, F., Lesani, M. *Hamsaz: Replication Coordination Analysis and Synthesis.* POPL, 2019. — [DOI](https://doi.org/10.1145/3290387)
- **[Foundational]** Ameloot, T., Neven, F., Van den Bussche, J. *Relational Transducers for Declarative Networking (CALM).* PODS, 2011. — [DBLP](https://dblp.org/rec/conf/pods/AmelootNB11.html)

## 10. Worked Example

Inventory app, one item with $stock = 1$, invariant $I: stock \ge 0$. Operations:
- `view()` — read-only, marked **weak (blue)**: reading a slightly stale stock harms nothing, so it commutes with everything and stays coordination-free.
- `buy()` — decrements stock if $stock \ge 1$.

Classify `buy` under RedBlue. Its shadow effect "$stock \mathrel{-}= 1$" does *not* compose safely with a concurrent `buy`: replicas $R_1, R_2$ each see $stock=1$, each locally pass the check, each emit $-1$, merge gives $stock = 1 - 1 - 1 = -1$, violating $I$ — the classic last-item double-sell. So `buy` is **strong (red)**: it must be globally ordered, ruling out one of the two concurrent buys.

The minimal strengthening is exactly $\{$`buy`$\}$ promoted to strong; `view` remains weak. MixT's information-flow types add the dual guard: the boolean "is it in stock?" computed from a *weak* `view` may not flow into the *strong* `buy`'s commit decision, since stale data must not influence a linearizable action. Result: fast reads, coordinated last-item sale, invariant preserved.

---
*Part of the [DBMS Research catalog](../../README.md).*
