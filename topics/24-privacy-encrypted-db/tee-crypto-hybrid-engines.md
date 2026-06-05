# Hybrid TEE + Crypto Query Engines

> **Topic:** Privacy & Encrypted Databases · **ID:** `24-privacy-encrypted-db/tee-crypto-hybrid-engines` · **Status:** empirically-open

## 1. Problem Statement
Given a SQL query plan and a security/leakage budget, decide **which operators run inside a Trusted Execution Environment (TEE/enclave)** versus **under cryptography** (FHE, MPC, searchable/property-preserving encryption, ORAM), so that total cost is minimized while the *composed* leakage stays within the budget under a stated adversary. Neither extreme is satisfactory: pure-crypto engines are slow (FHE) or leaky (deterministic/order-preserving encryption); pure-TEE engines are fast but expose timing/paging/microarchitectural side channels and require trusting the hardware vendor.

Variants:
- **Optimization (primary):** minimize expected runtime/cost of a plan subject to $\mathrm{Leak}(\text{plan}) \preceq \mathcal{B}$.
- **Decision:** is there an operator placement achieving leakage $\le \mathcal{B}$ at cost $\le C$?
- **Composition:** does combining a low-leakage crypto operator with a side-channel-prone enclave operator stay within budget, or does leakage *compose superadditively*?

## 2. Mathematical Foundations
Model an execution as a DAG of operators; each operator $O$ has implementations $I_1,\dots,I_k$ with cost $c(I_j)$ and a **leakage profile** $\ell(I_j) \in \mathcal{L}$ drawn from a lattice of leakage functions (access-pattern leakage, volume/cardinality leakage, equality/order leakage). Following **Cash et al.** and the **Curtmola et al. SSE framework**, security is parameterized by a leakage function $\mathcal{L}_{\Pi}$ and proved via simulation: $\mathrm{REAL} \approx_c \mathrm{Sim}(\mathcal{L}_{\Pi})$.

Placement is a constrained optimization over the plan DAG. If leakage composed additively under a monotone order, optimal placement would be a min-cost selection subject to a packing constraint (knapsack-like, NP-hard but well-approximable). The hard reality: leakage **composes non-monotonically** — an enclave operator's access pattern, combined with a crypto operator's volume leakage, can enable *cross-operator inference* (cf. **reconstruction from access-pattern + volume**, Kellaris–Kollios–Nissim–O'Neill, CCS'16). Side channels are modeled as an extra leakage term $\ell_{\mathrm{sc}}$ (page-fault sequence, cache footprint) bounded only under data-oblivious execution.

## 3. State of the Art (SOTA)
- **Systems-SOTA:** **EnclaveDB** (Priebe–Vaswani–Costa, IEEE S&P'18) — full in-enclave engine; **StealthDB**, **Cipherbase** (Microsoft, hardware-trusted module + SQL Server) — partition operators between trusted module and untrusted DBMS; **Opaque** (NSDI'17) and **ObliDB** (PVLDB'19) — oblivious operators in SGX; **CryptDB** (SOSP'11) — onion encryption, pure-crypto baseline; **Operon / Azure Always Encrypted with secure enclaves** — production hybrid.
- **Hybrid-SOTA:** **HEDB** and **Secure-NDP** lines splitting work; MPC+TEE designs (e.g., **Senate**, **Conclave** for the MPC side) and FHE-offload prototypes. **Coeus / Snoopy** for oblivious-storage scaling under a TEE controller.

## 4. Upper Bound
No single tight bound — the field reports **empirical Pareto frontiers** rather than proven optima. For a fixed leakage profile, the best placement is computable by exhaustive/ILP search over the plan ($O(k^{|V|})$ naïvely; ILP in practice). In-enclave operators run at near-plaintext cost *if* made oblivious, paying the oblivious-operator factor ($O(\log n)$–$O(\log^2 n)$, see oblivious-relational-operators). Crypto operators (FHE aggregation) sit at the high-cost end. The achievable region is workload- and hardware-specific; the "upper bound" is the measured cost of the best known hybrid system on a benchmark, **not** a closed-form guarantee.

## 5. Lower Bound
- **Leakage composition:** there is no general theorem bounding composed leakage by the sum of component leakages; **reconstruction attacks** (KKNO'16, Grubbs et al. "Pump up the Volume," CCS'18) show access-pattern + volume leakage suffices for full column reconstruction — a *lower bound on harm* from naïve composition.
- **Side channels:** controlled-channel/page-fault attacks (Xu–Cui–Peinado, S&P'15) and microarchitectural attacks (Foreshadow, USENIX Security'18) show non-oblivious enclave execution leaks data-dependent control flow — so any placement using a non-oblivious in-enclave operator has *unbounded* worst-case leakage.
- **Hardness:** optimal leakage-bounded placement generalizes constrained knapsack/QAP → NP-hard; with non-additive leakage it is not even known to be in NP without an oracle for composed-leakage evaluation.

## 6. The Gap
The gap is **definitional and empirical, not asymptotic**. We lack (i) a *compositional leakage algebra* that lets you certify a hybrid plan's leakage from its parts, and (ii) a cost model that the optimizer can trust across heterogeneous TEE/crypto operators. Until composed leakage is formalized, "optimal placement" is ill-posed — hence *empirically-open*: systems demonstrate good points on a Pareto curve but cannot prove the curve, nor that a chosen plan meets a stated adversary's budget.

## 7. Current Research (as of June 2026)
Directions: **compositional leakage frameworks** extending SSE leakage profiles to multi-operator plans; **leakage-aware query optimizers** that treat $\ell$ as a first-class cost dimension; confidential-computing stacks on **Intel TDX / AMD SEV-SNP / ARM CCA / NVIDIA confidential GPUs** broadening the TEE substrate *(frontier — verify)*; **FHE-offload accelerators** changing the crossover point where crypto beats oblivious-enclave execution *(frontier — verify)*. Groups: Costa/Vaswani (Microsoft Research), Zaharia/Eskandarian (Stanford/GWU), Popa (Berkeley, RISELab/encrypted systems), Kerschbaum (Waterloo), Fuller/Kamara (Brown/MongoDB) on leakage definitions.

## 8. Future Work
- A leakage algebra with a soundness theorem for plan composition.
- Cost models calibrated across TEE + FHE + MPC so an optimizer can place operators provably.
- Attestation and remote-trust reduction (multi-vendor / open TEEs) so the trust base is auditable.
- Automatic synthesis of oblivious in-enclave operators from relational specs.
- Benchmarks that score systems on a (cost, leakage, trust) triple, not cost alone.

## 9. Key References
- **[Foundational]** Curtmola, Garay, Kamara, Ostrovsky. *Searchable Symmetric Encryption: Improved Definitions and Efficient Constructions.* CCS, 2006. — [DOI](https://doi.org/10.1145/1180405.1180417) · [DBLP](https://dblp.org/rec/conf/ccs/CurtmolaGKO06.html)
- **[Foundational]** Popa, Redfield, Zeldovich, Balakrishnan. *CryptDB: Protecting Confidentiality with Encrypted Query Processing.* SOSP, 2011. — [DOI](https://doi.org/10.1145/2043556.2043566) · [DBLP](https://dblp.org/rec/conf/sosp/PopaRZB11.html)
- **[SOTA]** Priebe, Vaswani, Costa. *EnclaveDB: A Secure Database Using SGX.* IEEE S&P, 2018. — [DOI](https://doi.org/10.1109/SP.2018.00025)
- **[SOTA]** Eskandarian, Zaharia. *ObliDB: Oblivious Query Processing for Secure Databases.* PVLDB, 2019. — [DOI](https://doi.org/10.14778/3364324.3364331) · [DBLP](https://dblp.org/rec/journals/pvldb/EskandarianZ19.html)
- **[SOTA]** Arasu, Eguro, Kaushik, et al. *Transaction Processing on Confidential Data using Cipherbase.* ICDE, 2015. — [DOI](https://doi.org/10.1109/ICDE.2015.7113304)
- **[Survey]** Fuller, Varia, Hamlin, et al. *SoK: Cryptographically Protected Database Search.* IEEE S&P, 2017. — [arXiv](https://arxiv.org/abs/1703.02014) · [DBLP](https://dblp.org/rec/conf/sp/FullerVYSHGSMC17.html)

## 10. Worked Example

**Operator placement for a two-operator plan.** Query: `SELECT AVG(salary) FROM emp WHERE dept = 'ENG'`. Plan = $\sigma_{dept}$ (filter) $\to$ AVG (aggregate). Each operator has two implementations:

| Operator | Impl. | cost (units) | leakage $\ell$ |
|---|---|---|---|
| filter | DET-encrypted index | 1 | equality pattern (which rows share a dept) |
| filter | oblivious enclave | 8 | none (data-oblivious) |
| AVG | enclave (non-oblivious) | 2 | branch/page trace $\propto$ #matching rows (volume) |
| AVG | FHE | 50 | none |

With budget $\mathcal{B}=$ "no volume leakage," the cheapest *per-operator* choice is DET-filter (cost 1) + enclave-AVG (cost 2) $=3$. But composition bites: the DET filter leaks the *equality partition* and the non-oblivious AVG leaks the *count of matching rows* — together this is exactly access-pattern + volume, which (KKNO'16, Grubbs et al. CCS'18) reconstructs the `dept` column. So the naively optimal plan **violates** $\mathcal{B}$ superadditively.

A budget-feasible plan must break the chain: e.g. oblivious-enclave filter (8) + enclave-AVG (2) $=10$, or DET-filter (1) + FHE-AVG (50) $=51$. The optimizer picks cost-$10$. The example shows why $\mathrm{Leak}(\text{plan})\not\preceq\sum_i\ell(I_i)$ makes "optimal placement" ill-posed without a composition theorem.

---
*Part of the [DBMS Research catalog](../../README.md).*
