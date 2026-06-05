# Formal Verification of Live Reconfiguration

> **Topic:** Consensus & Coordination · **ID:** `10-consensus-coordination/verified-reconfiguration` · **Status:** partially-solved

## 1. Problem Statement
Reconfiguration — changing the replica set of a consensus group while it keeps processing commands — is where most real consensus bugs live: overlapping configurations, lost quorum intersection, leaders elected in stale configs, and snapshots taken across a config boundary. Abstract protocols (Raft joint consensus, Vertical Paxos, Stoppable Paxos) have paper proofs, but **production code** diverges from the paper. The problem: **produce machine-checked proofs of both safety (linearizability across configuration changes) and liveness (eventual progress despite reconfiguration) for the *actual executable code* that runs in production, not merely an idealized model.**

Variants:
- **Safety verification:** Prove no two committed values disagree at the same log index across any sequence of (possibly overlapping) configurations.
- **Liveness verification:** Prove that under eventual synchrony and a stable enough config, the system eventually commits — typically the harder, less-automated half.
- **Refinement/extraction:** Prove the gap is closed by either verifying the deployed implementation directly or extracting verified code, so the "model–code gap" carries no unverified trust.

## 2. Mathematical Foundations
The correctness target is **linearizability** of the replicated object across configuration epochs, usually proved by **refinement**: the implementation's state machine refines an atomic specification via a forward/backward simulation relation, with an inductive invariant $I$ closed under every step. Reconfiguration breaks the standard single-config quorum-intersection invariant ($\forall Q_1,Q_2:\;Q_1\cap Q_2\neq\emptyset$) because two *different* configurations need overlapping decision power; the key lemma is a **cross-configuration quorum-intersection** invariant guaranteeing that any decision in config $c_{k+1}$ is informed by every decision committed in $c_k$.

Liveness is stated in temporal logic (TLA⁺ / LTL): $\Box(\text{stable config} \wedge \Diamond\Box\text{synchrony}) \Rightarrow \Diamond\,\text{commit}$, and proved via well-founded ranking / fairness arguments, which automation handles far worse than safety. Tooling spans: **TLA⁺ + TLAPS** (deductive) or **TLC** (model checking, bounded), **Ivy** (EPR-decidable inductive invariants — safety only, push-button), **Coq/Verdi** and **Dafny/IronFleet** (full refinement to executable code), and **Coq+separation logic (Iris/Perennial)** for crash-safe storage.

## 3. State of the Art (SOTA)
- **Verdi / Raft** (Wilcox et al., PLDI 2015; Woos et al., CPP 2016): a Coq-verified Raft including log/leader-election safety, with verified system transformers — but reconfiguration was the hardest, least-complete part.
- **IronFleet** (Hawblitzel et al., SOSP 2015): Dafny refinement proof of a Paxos-based replicated state machine (IronRSL) down to executable code, including some reconfiguration, with both safety *and* liveness.
- **Ivy** (Padon et al., PLDI 2016) and the **Ivy Paxos/Multi-Paxos/Vertical-Paxos** proofs (Padon et al., OOPSLA 2017): decidable inductive-invariant verification of consensus, including reconfiguration variants, by careful EPR modeling.
- **Verified Raft reconfiguration / MongoDB**: TLA⁺ specs of MongoDB's reconfiguration protocol (Schultz, Dardik, Tripakis, 2021–22) model-checked and partly TLAPS-proved. **Perennial/Grove** for crash-safe verified distributed code. *(frontier — verify newest extraction-to-Rust/Go efforts 2024–2026.)*

## 4. Upper Bound
What is achievable today: **mechanized safety proofs of reconfiguration for realistic protocols** (Ivy's Vertical/Stoppable Paxos; IronFleet; Verdi-Raft) and, in the IronFleet line, **both safety and liveness down to executable Dafny code**. Ivy demonstrates that with the right EPR encoding the inductive-invariant check becomes *decidable and push-button* for Multi-Paxos with reconfiguration — the strongest automation result. These hold in the asynchronous-with-eventual-synchrony crash model.

## 5. Lower Bound
Liveness verification is fundamentally limited: temporal/liveness properties of parameterized distributed systems are **undecidable** in general (reductions to non-termination / the halting problem), so full automation for liveness is impossible — human-guided ranking proofs are required. Even safety invariant inference for unbounded-state, parameterized protocols is undecidable; Ivy's tractability relies on staying inside the decidable EPR fragment, which not all real protocols admit. There is also an inherent **model–code gap**: any proof over a model leaves the model-faithfulness obligation, formally discharged only by verifying or extracting the executable.

## 6. The Gap
Safety of reconfiguration is largely *solved* for verified models and, in places, verified code — hence "partially-solved." Open: (1) liveness proofs are scarce, labor-intensive, and rarely cover reconfiguration; (2) the verified artifact is usually a *reimplementation*, not the battle-tested production code (etcd-Raft, ZooKeeper, MongoDB), so the deployed system stays unverified; (3) crash-recovery + reconfiguration + storage corruption interactions are only beginning to be verified end-to-end. Closing the gap means liveness-complete proofs over the actual shipping implementation.

## 7. Current Research (as of June 2026)
- Verifying real-world reconfiguration (MongoDB's "reconfig" via TLA⁺/TLAPS; etcd-Raft conformance). *(frontier — verify.)*
- Push-button liveness via temporal-prophecy / liveness-to-safety reductions in Ivy. *(frontier — verify.)*
- Extracting verified consensus to Rust/Go and proving the storage/crash layer with Perennial/Grove.
- Groups: Tel Aviv/MSR (Padon, Shoham, Sagiv — Ivy), MSR (Hawblitzel, Lorch — IronFleet), Washington (Tatlock, Anderson — Verdi), MIT (Chajed, Kaashoek — Perennial), Northeastern/Boston (Tripakis, Schultz — MongoDB TLA⁺).

## 8. Future Work
- Liveness-complete, mechanized reconfiguration proofs as a reusable library.
- Verifying the deployed implementation (not a model) via conformance or refinement to existing code.
- Compositional proofs combining reconfiguration, snapshotting, and crash recovery.

## 9. Key References
- **[Foundational]** Leslie Lamport. *The Part-Time Parliament (Paxos)* / *Vertical Paxos.* ACM TOCS 1998 / PODC 2009.
- **[SOTA]** James Wilcox et al. *Verdi: A Framework for Implementing and Formally Verifying Distributed Systems.* PLDI, 2015.
- **[SOTA]** Chris Hawblitzel et al. *IronFleet: Proving Practical Distributed Systems Correct.* SOSP, 2015.
- **[SOTA]** Oded Padon et al. *Paxos Made EPR: Decidable Reasoning about Distributed Protocols.* OOPSLA, 2017.
- **[SOTA]** William Schultz, Ian Dardik, Stavros Tripakis. *Formal Verification of a Distributed Dynamic Reconfiguration Protocol (MongoDB).* CPP, 2022.

---
*Part of the [DBMS Research catalog](../../README.md).*
