# Adaptive isolation level selection

> **Topic:** NewSQL & Distributed SQL · **ID:** `12-newsql-distributed-sql/adaptive-isolation-selection` · **Status:** empirically-open

## 1. Problem Statement

Stronger isolation (serializable) is safe but costly; weaker isolation (read committed,
snapshot isolation, causal) is cheaper but admits anomalies. For a given application,
**most** transactions can run at a weaker level without violating correctness, while a few
require stronger guarantees. The problem: **automatically assign to each transaction
(template, or even each dynamic instance) the weakest isolation level that still preserves
application correctness**, minimizing coordination/abort cost.

Variants: (i) **Static (per-template) assignment** — given templates and an invariant/
correctness spec, compute a per-template isolation map that is provably anomaly-safe.
(ii) **Optimization** — among all safe assignments, minimize expected cost (latency, abort
rate, coordination). (iii) **Online/adaptive** — adjust levels at runtime as contention and
mix shift, while never violating correctness; possibly per-instance.

## 2. Mathematical Foundations

Use Adya's **dependency-graph (DSG)** model with edges $ww, wr, rw$ over committed
transactions; each isolation level $\ell$ forbids a specific set of cycle structures. The
"robustness against a weaker level" question: a workload is **robust** against level $\ell$
if *every* $\ell$-admissible history is serializable — equivalently, the **static
dependency graph (SDG)** over templates contains no "dangerous" cycle for $\ell$ (Fekete et
al.: for SI, no cycle with two consecutive $rw$ anti-dependency edges on a pivot;
Cerone–Gotsman robustness criteria generalize this).

Selection is then a **mixed-level robustness** problem: given a partial isolation map
$\sigma: \text{Templates} \to \text{Levels}$, decide whether all histories admissible under
$\sigma$ are serializable (or invariant-preserving). The cost objective layers a workload
distribution and a per-level cost model on top, making it a constrained optimization:
$\min_\sigma \mathbb{E}[\text{cost}(\sigma)]$ s.t. $\text{robust}(\sigma)$. The
invariant-preservation variant connects to **I-confluence** (Bailis et al.) — the weakest
level need only be strong enough to block the *invariant-threatening* anomalies, not all
anomalies.

## 3. State of the Art (SOTA)

**Theory SOTA.** Fekete (PODS 2005; with O'Neil et al. TODS 2005) gives the
**mixed SI/serializable** assignment: identify pivot templates whose conflicts must be
promoted (e.g., to serializable or via materialized conflicts) and run the rest at SI.
Cerone–Gotsman (PODC 2016) and Beillahi–Bouajjani–Enea (CAV/POPL 2019–2020) give automated
robustness checks usable to certify a chosen level.

**Systems SOTA.** Most NewSQL engines expose per-transaction isolation hints
(`SET TRANSACTION ISOLATION LEVEL`), but selection is left to developers. Research systems —
MorphR / adaptive concurrency control, Tebaldi (Su et al., SIGMOD 2017) which composes
multiple concurrency-control protocols per partition, and contract-based systems
(Quelea, PLDI 2015) that synthesize the weakest sufficient consistency from declared
contracts — represent the automated frontier. PiLeus/Pileus-style consistency-SLA
selection adapts read consistency to latency targets.

## 4. Upper Bound

For **static per-template** assignment with a fixed invariant or serializability target and
finitely many templates and levels, a safe assignment is computable by SDG analysis in time
polynomial in the number of templates for SI-vs-serializable robustness (Fekete et al.;
Cerone–Gotsman). Searching for the **cost-minimal** safe assignment is at worst
exponential in the number of templates by enumeration, but the monotone structure (a safe
assignment stays safe if any template is *strengthened*) enables pruning; greedy
"promote only pivots" yields a provably safe (not necessarily cost-optimal) solution as the
practical upper bound. Contract synthesis (Quelea) bounds the assignment to the weakest
level satisfying each declared contract.

## 5. Lower Bound

Robustness/serializability certification of arbitrary workloads is hard: serializability of
general histories is **NP-complete** (Papadimitriou 1979 for view-serializability), and
robustness against weak isolation for parameterized template programs is **PSPACE-hard**
(Beillahi–Bouajjani–Enea), with **undecidability** for Turing-powerful interactive
transaction programs (reduction from reachability/halting). For the cost-optimization
variant, minimizing cost subject to a robustness constraint inherits this hardness and adds
a combinatorial assignment dimension (a covering/promotion problem plausibly NP-hard). Thus
exact optimal selection is intractable in the general case; tractable only for restricted
template/invariant classes.

## 6. The Gap

Marked **empirically-open**: sound *static* selection methods exist for specific level pairs
(SI vs. serializable) and specific correctness criteria, so the foundations are partly
solved, but there is **no general, practical algorithm** that (a) handles the full SQL
isolation lattice, (b) targets *application invariants* rather than blanket
serializability, (c) optimizes cost with guarantees, and (d) adapts online without ever
crossing into unsafety. Production practice relies on developer judgment and empirical
testing/Jepsen-style validation. Closing the gap needs a decidable-fragment characterization
plus an approximation theory for the cost-minimizing safe assignment, validated to actually
preserve correctness under real workloads.

## 7. Current Research (as of June 2026)

Active directions: invariant-aware isolation synthesis combining I-confluence with
robustness checking; ML/learned advisors that observe conflict patterns and recommend (or
auto-set) per-template levels *(frontier — verify)*; runtime **adaptive** controllers that
escalate isolation under detected contention while holding a static safety proof
*(frontier — verify)*; and verification tooling (Elle, Jepsen) used to empirically validate
chosen levels. Groups around Gotsman, Enea, Bouajjani, Bailis-lineage, and Jagannathan are
active; integration into CockroachDB/Postgres-class advisors is an emerging industrial
thread.

## 8. Future Work

- Decidable invariant-aware selection over the full isolation lattice for useful fragments.
- Approximation algorithms (with ratios) for cost-minimal safe assignment.
- Per-instance (not just per-template) online level selection with a maintained safety
  certificate.
- Tight integration of selection with verification so the chosen level is machine-checked
  end-to-end before deployment.

## 9. Key References

- **[Foundational]** Fekete. *Allocating Isolation Levels to Transactions.* PODS, 2005.
- **[Foundational]** Fekete, Liarokapis, O'Neil, O'Neil, Shasha. *Making Snapshot Isolation Serializable.* ACM TODS, 2005.
- **[SOTA]** Beillahi, Bouajjani, Enea. *Robustness Against Transactional Causal Consistency / Snapshot Isolation.* CONCUR/CAV, 2019–2020.
- **[SOTA]** Su, Crooks, Ding, Alvisi, Xie. *Bringing Modular Concurrency Control to the Next Level (Tebaldi).* SIGMOD, 2017.
- **[SOTA]** Sivaramakrishnan, Kaki, Jagannathan. *Declarative Programming over Eventually Consistent Data Stores (Quelea).* PLDI, 2015.
- **[Foundational]** Bailis, Fekete, Franklin, Ghodsi, Hellerstein, Stoica. *Coordination Avoidance in Database Systems.* VLDB, 2015.

---
*Part of the [DBMS Research catalog](../../README.md).*
