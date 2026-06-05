# Adaptive Isolation Level Selection

> **Topic:** Concurrency Control · **ID:** `05-concurrency-control/adaptive-isolation-selection` · **Status:** open

## 1. Problem Statement
Given an application with a set of transaction programs $\mathcal{T} = \{T_1, \dots, T_k\}$ and a set of **application invariants** $\Phi$ (integrity constraints the application assumes always hold), assign to each transaction (or each execution instance) the **weakest** isolation level from a lattice $\mathcal{L}$ (e.g., Read Uncommitted $\prec$ Read Committed $\prec$ Snapshot Isolation $\prec$ Serializable) such that **every interleaving permitted by the chosen levels preserves $\Phi$**, while maximizing concurrency/throughput.

Variants:
- *Decision:* "Is assignment $\alpha: \mathcal{T} \to \mathcal{L}$ invariant-safe?" — is every anomaly newly admitted by weakening from serializable harmless w.r.t. $\Phi$?
- *Optimization (static):* find the throughput-maximizing safe assignment over all transactions.
- *Online/adaptive:* choose levels per-instance at runtime from observed contention, with a regret objective against the best fixed-in-hindsight policy.

This generalizes the classic **acyclicity / robustness** question: a workload is *robust* against isolation level $L$ if every $L$-permitted schedule is serializable — but robustness is sufficient, not necessary, since some non-serializable schedules still preserve $\Phi$.

## 2. Mathematical Foundations
The formal substrate is **Adya's generalized isolation theory**: isolation levels are defined by *phenomena* (dirty read G1, lost update, write skew G2-item, etc.) forbidden over the **Direct Serialization Graph (DSG)**, whose nodes are committed transactions and whose edges $\xrightarrow{ww}, \xrightarrow{wr}, \xrightarrow{rw}$ encode dependencies. A level $L$ corresponds to forbidding a set of cycle types in the DSG.

- **Serializability ⇔ acyclic DSG** (Adya, Bernstein–Hadzilacos–Goodman).
- **Robustness against SI**: characterized via the existence of a *dangerous structure* — two consecutive $\xrightarrow{rw}$ anti-dependency edges on a cycle (Fekete et al. 2005); detectable statically from the static dependency graph (SDG).
- **Invariant confluence / $\mathcal{I}$-confluence** (Bailis et al. 2014): a set of transactions with merge operator preserves invariant $\Phi$ under coordination-free execution iff $\Phi$ is *$\mathcal{I}$-confluent* — closed under merge of $\Phi$-reachable states. This reframes "weakest safe level" as: how much coordination is *necessary*, formalized as $\Phi$ being preserved under the reachable-state join semilattice.

Determining whether weakening from serializable preserves a first-order invariant reduces to checking emptiness of a set of *bad interleavings*, which is undecidable in general (Turing-complete transaction programs) and PSPACE/NP-hard for bounded fragments.

## 3. State of the Art (SOTA)
**Theory-SOTA.** Fekete et al. (TODS 2005) give a sound static analysis to make an SI workload serializable by promoting a minimal set of transactions; this underlies *PostgreSQL SSI* groundwork. Bailis et al. *Coordination Avoidance* (VLDB 2015) provides the $\mathcal{I}$-confluence test partitioning invariants into coordination-free vs. coordination-requiring. Cerone–Gotsman (2016+) give axiomatic specifications of SI/PSI enabling robustness proofs.

**Systems-SOTA.** Production systems leave the choice to developers (per-statement/per-transaction `SET TRANSACTION ISOLATION LEVEL`), with no automatic invariant-aware selection. **PostgreSQL SSI** (Ports–Grittner, VLDB 2012) implements serializable via SI + rw-conflict tracking. Research prototypes: **MorphoSys / IsoDiff** detect anomalies; learned/contention-adaptive CC (Polyjuice, OSDI 2021) tunes *mechanism* per access but not invariant-driven isolation level.

## 4. Upper Bound
For the **static robustness-against-SI** test, the dangerous-structure detection runs in polynomial time over the static dependency graph: $O(|\mathcal{T}|^2)$ to $O(|\mathcal{T}|^3)$ depending on graph density (Fekete et al.). For $\mathcal{I}$-confluence with finite-state merge and a fixed invariant, checking is decidable in time polynomial in the (finite) state space but is generally **co-NP** in the number of transaction effects (search over pairs of $\Phi$-reachable states). These hold in the **abstract transaction-effect model**, abstracting away unbounded data.

## 5. Lower Bound
- **Undecidability:** deciding whether an arbitrary application preserves a first-order invariant under a weak level reduces from the halting/Trakhtenbrot problem when transaction programs are Turing-complete — no algorithm exists in full generality.
- **NP-hardness:** even in bounded models, choosing the *minimum-coordination* (max-weakening) safe assignment encodes a covering/independent-set problem over the conflict graph → NP-hard.
- **Coordination impossibility (CALM / CAP):** Bailis et al. and the CALM theorem (Hellerstein–Alvaro) show invariants that are *not* monotone/$\mathcal{I}$-confluent **provably require** coordination — a synchronization lower bound independent of implementation.

## 6. The Gap
The gap is between (a) *sufficient* static safety tests (robustness, $\mathcal{I}$-confluence) that are conservative — they may force serializable when a weaker level would actually preserve $\Phi$ — and (b) the *exact* weakest-safe-level frontier, which is undecidable for general programs and only sharply characterized for restricted invariant classes (equality, per-key, monotone). Closing it requires either richer decidable invariant logics with tight complexity, or sound-and-near-complete heuristics with quantified false-promotion rates. Genuinely **open**.

## 7. Current Research (as of June 2026)
- **Verification-driven selection:** tools that take SQL + declared invariants and synthesize per-transaction isolation (extending CLOTHO / IsoDiff / Cobra-style checking). *(frontier — verify)*
- **Learned/RL adaptive isolation** that switches levels online under contention with safety guards derived from static robustness, blending Polyjuice-style learning with $\mathcal{I}$-confluence guardrails. *(frontier — verify)*
- Groups: Bailis/Hellerstein lineage (Berkeley), Gotsman–Cerone (weak-consistency semantics), Kemper/Neumann (HyPer/Umbra) on practical isolation tuning.

## 8. Future Work
- Decidable invariant fragments (e.g., GSO / first-order with restricted quantifier alternation) with tight complexity for weakest-safe-level.
- Counterexample-guided synthesis of minimal coordination points.
- Online algorithms with provable regret against the best static safe assignment under shifting workloads.

## 9. Key References
- **[Foundational]** A. Adya, B. Liskov, P. O'Neil. *Generalized Isolation Level Definitions.* ICDE, 2000. — [DBLP](https://dblp.org/rec/conf/icde/AdyaLO00.html)
- **[Foundational]** A. Fekete, D. Liarokapis, E. O'Neil, P. O'Neil, D. Shasha. *Making Snapshot Isolation Serializable.* ACM TODS, 2005. — [DOI](https://doi.org/10.1145/1071610.1071615)
- **[SOTA]** P. Bailis, A. Fekete, M. J. Franklin, A. Ghodsi, J. M. Hellerstein, I. Stoica. *Coordination Avoidance in Database Systems.* VLDB, 2015. — [DOI](https://doi.org/10.14778/2735508.2735509)
- **[SOTA]** D. R. K. Ports, K. Grittner. *Serializable Snapshot Isolation in PostgreSQL.* VLDB, 2012. — [DOI](https://doi.org/10.14778/2367502.2367523)
- **[Survey]** A. Cerone, A. Gotsman. *Analysing Snapshot Isolation.* JACM, 2018. — [DOI](https://doi.org/10.1145/3152396)

## 10. Worked Example

The classic **write-skew** anomaly shows why "weakest safe level" is invariant-dependent. Two doctors are on call; invariant $\Phi$: at least one stays on call, i.e. `oncall(A) OR oncall(B)`. Initial state: both on call.

$T_1$: `if (oncall(B)) set oncall(A)=false;`
$T_2$: `if (oncall(A)) set oncall(B)=false;`

Under **Snapshot Isolation**, both read the same snapshot (both colleagues on call), each independently decides it is safe to go off call, and both commit — final state violates $\Phi$ (nobody on call). The DSG has two $\xrightarrow{rw}$ anti-dependency edges $T_1\xrightarrow{rw}T_2\xrightarrow{rw}T_1$ forming the *dangerous structure* of Fekete et al.

So for $\Phi$ = `oncall(A) OR oncall(B)`, SI is **not** safe — the selector must promote at least one of $T_1,T_2$ to Serializable. But if $\Phi$ were merely `oncall(A) OR true` (always satisfied), SI would be safe and the weakest level would suffice. Same transactions, different invariant, different answer — exactly the frontier section 6 describes.

---
*Part of the [DBMS Research catalog](../../README.md).*
