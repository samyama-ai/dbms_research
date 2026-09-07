---
id: 30-cloud-serverless-db/verifiable-billing
title: "Verifiable billing for cloud query services"
topic: 30-cloud-serverless-db
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Verifiable billing for cloud query services

> **Topic:** Cloud & Serverless Databases · **ID:** `30-cloud-serverless-db/verifiable-billing` · **Status:** open

## 1. Problem Statement
Serverless query services bill by *consumed resources* (compute-seconds, bytes scanned, I/O, rows processed). The provider both **executes** the query and **measures** what to charge — a conflict of interest. A tenant currently cannot independently verify that the reported consumption is **accurate** (matches what an honest, reasonably efficient execution would use) and **non-inflated** (the provider didn't pad work, pick a deliberately wasteful plan, or fabricate counters).

**Verifiable billing** asks for a protocol producing, alongside the result, a **proof** $\pi$ that the reported bill $B$ correctly reflects resource consumption of a *correct and not-gratuitously-wasteful* execution of query $Q$ over committed data $D$ — checkable by the tenant (or a third party) far more cheaply than re-running $Q$.

Variants:
- **Result correctness:** prove the *answer* to $Q$ over $D$ is correct (classic verifiable/authenticated query processing).
- **Consumption accuracy:** prove the *reported cost* $B$ equals the resources a defined execution used.
- **Non-inflation / efficiency:** prove $B \le (1+\gamma)\cdot \text{OPT-ish}$ — the provider didn't choose a needlessly expensive plan to inflate the bill.
- **Decision vs. optimization:** verify a claimed bill vs. compute the minimal certifiable bill.

The third variant is the hard, genuinely **open** one: "cost" is plan-dependent, so honest executions legitimately vary, and there is no canonical "true" cost to prove against.

## 2. Mathematical Foundations
- **Authenticated query processing / result correctness** rests on **authenticated data structures (ADS)**: Merkle trees and Merkle B-trees, signature-aggregation, and verifiable computation. The server returns a **verification object (VO)**; the client checks an answer of size $k$ in $O(k + \log |D|)$ using collision-resistant hashing (security from $H$ being a random oracle / CRHF).
- **General verifiable computation:** **SNARKs/STARKs** prove that a computation transcript of size $T$ was executed correctly with a proof of size $\text{polylog}(T)$ and verification $O(\text{polylog}(T))$ — security from knowledge-of-exponent / collision-resistance / PCP machinery. **Interactive proofs (GKR/$\text{IP}=\text{PSPACE}$)** give doubly-efficient verification for low-depth circuits, fitting data-parallel relational operators.
- **Measuring resources** turns the resource counters (rows touched, bytes scanned, ops) into *public outputs of the proven circuit*: if the verified transcript itself counts $\\#\text{ops}$, then $B=f(\\#\text{ops})$ is provably tied to a correct execution. The **AGM bound** gives an *information-theoretic floor* on join work ($|Q|\le \prod_e |R_e|^{x_e}$), and **worst-case-optimal join** runtime gives an upper certificate — together bounding the *legitimate* cost range a proof of non-inflation could certify.
- **Commitment:** $D$ is fixed by a polynomial/vector commitment $c=\text{Com}(D)$ so the provider can't switch data; freshness via **append-only / transparency logs**.

## 3. State of the Art (SOTA)
- **Theory/Systems-SOTA (result correctness):** authenticated query processing — Merkle B-trees (Li–Hadjieleftheriou–Kollios–Reyzin), **IntegriDB**, **vSQL**, **Spice/Pantry**-style verifiable storage, and ZK proofs for SQL (**ZKSQL**, **vSQL** for general queries) prove *answers*. These are mature for selection/join/aggregation answers.
- **Verifiable computation infra:** SNARKs (Groth16, Plonk, Marlin), STARKs, GKR (Libra, Virgo) make per-query proofs increasingly practical, though prover overhead remains $10^2$–$10^6\times$.
- **Consumption/billing verification:** **largely absent** in production; cloud billing relies on **trust + audits + TEEs** (SGX/SEV attestation of metering) rather than cryptographic non-inflation proofs. Trusted-hardware metering and tamper-evident logs are the practical SOTA.

## 4. Upper Bound
- **Answer verification:** $O(k+\log|D|)$ client work with $O(\log|D|)$-size VO per result via authenticated B-trees (random-oracle/CRHF model) — essentially optimal.
- **General execution proof:** SNARK proof size $O(1)$ / $\text{polylog}(T)$, verify $O(\text{polylog}(T))$, prover $\tilde{O}(T)$ — so a *consumption-accuracy* proof (bill = function of proven transcript counters) is achievable with succinct verification, at heavy prover cost.
- **Non-inflation upper certificate:** one can certify $B \le$ worst-case-optimal-join runtime bound, and $B \ge$ AGM/output-size floor, giving a *checkable interval* $[\text{floor}, \text{wcoj}]$ the bill must lie in.

## 5. Lower Bound
- **Verification can't beat reading the answer:** any sound protocol needs $\Omega(k)$ to convey a $k$-tuple answer; VO size $\Omega(\log|D|)$ for membership/non-membership (cell-probe / Merkle lower bounds).
- **Proof-of-work-amount is impossible to make tight:** there is **no canonical "true" resource cost** — choosing the optimal plan is itself **NP-hard** (join order is hard), so proving $B\le(1+\gamma)\text{OPT}$ requires certifying near-optimal planning, which is intractable; the best one can hope is membership in the $[\text{AGM}, \text{WCOJ}]$ interval, a loose bound.
- **Soundness limits:** without commitment + freshness, a malicious provider can answer over stale/forged $D$ (needs CRHF assumption); TEEs shift trust to hardware (side-channel-vulnerable, not unconditional).
- General succinct non-interactive arguments require **non-falsifiable assumptions** (Gentry–Wichs: no black-box SNARK from falsifiable assumptions), an inherent cryptographic barrier.

## 6. The Gap
*Answer*-correctness is essentially solved; *consumption-accuracy* is achievable in principle but with prohibitive prover overhead and no production deployment. The truly **open** problem is **non-inflation**: there is no agreed definition of, or efficient proof for, "the provider didn't waste resources to pad the bill," because optimal cost is NP-hard and honest costs vary by plan/hardware. Closing it needs (a) a *certifiable cost model* (a canonical, hardware-normalized resource accounting both parties accept), (b) succinct proofs cheap enough to attach to every billed query, and (c) handling non-determinism/elasticity (preemption, retries) inside the proof. All three are open.

## 7. Current Research (as of June 2026)
- **ZK/SNARK proofs over SQL execution transcripts** that export resource counters as public outputs, tying bills to proven work *(frontier — verify)*.
- **TEE-attested metering + transparency logs** as a pragmatic bridge while SNARK provers remain costly.
- **Certifiable cost models** and hardware-normalized accounting so "compute-seconds" is well-defined across heterogeneous fleets.
- Folding/accumulation schemes (Nova-style) to amortize prover cost across many queries; groups in ZK (Stanford, Berkeley), DB verifiability (UC Riverside, HKUST, Microsoft Research).
- **AGM/WCOJ-bounded billing audits** as a lightweight statistical alternative to full proofs.

## 8. Future Work
- A formal, adopted definition of a *non-inflated bill* and a protocol proving it succinctly.
- Practical prover overhead ($<2\times$) for per-query billing proofs.
- Verifiable metering under elasticity (autoscale, spot preemption, retries).
- Composability with verifiable carbon/energy reporting (greenwashing-resistant carbon bills).

## 9. Key References
- **[Foundational]** Feifei Li, Marios Hadjieleftheriou, George Kollios, Leonid Reyzin. *Dynamic Authenticated Index Structures for Outsourced Databases.* SIGMOD, 2006. — [DOI](https://doi.org/10.1145/1142473.1142488)
- **[Foundational]** Ralph C. Merkle. *A Digital Signature Based on a Conventional Encryption Function.* CRYPTO, 1987. — [DBLP](https://dblp.org/rec/conf/crypto/Merkle87.html)
- **[SOTA]** Yupeng Zhang, Daniel Genkin, Jonathan Katz, Dimitrios Papadopoulos, Charalampos Papamanthou. *vSQL: Verifying Arbitrary SQL Queries over Dynamic Outsourced Databases.* IEEE S&P, 2017. — [DBLP](https://dblp.org/rec/conf/sp/ZhangGKPP17.html)
- **[SOTA]** Jens Groth. *On the Size of Pairing-Based Non-interactive Arguments (Groth16).* EUROCRYPT, 2016. — [DBLP](https://dblp.org/rec/conf/eurocrypt/Groth16.html)
- **[Foundational]** Shafi Goldwasser, Yael Tauman Kalai, Guy N. Rothblum. *Delegating Computation: Interactive Proofs for Muggles (GKR).* STOC, 2008 / JACM, 2015. — [DOI](https://doi.org/10.1145/1374376.1374396)
- **[SOTA]** Hung Q. Ngo, Christopher Ré, Atri Rudra. *Skew Strikes Back: New Developments in the Theory of Join Algorithms.* SIGMOD Record, 2013 (AGM / worst-case-optimal joins as cost floor/ceiling). — [arXiv](https://arxiv.org/abs/1310.3314)
- **[Foundational]** Craig Gentry, Daniel Wichs. *Separating Succinct Non-Interactive Arguments from All Falsifiable Assumptions.* STOC, 2011. — [DOI](https://doi.org/10.1145/1993636.1993651)

## 10. Worked Example

A tenant runs $Q$: a join $R(x,y)\bowtie S(y,z)\bowtie T(z,x)$ (the triangle query) over $|R|=|S|=|T|=N=10{,}000$ tuples. The provider bills by *intermediate tuples touched*.

**Naive plan (provider-favorable):** compute $R\bowtie S$ first. With skew this can be as large as $N^2 = 10^8$ intermediate tuples before joining $T$ — the provider could legitimately pick this and bill for $\sim10^8$ units.

**AGM floor / WCOJ ceiling.** The AGM bound caps the *output* size at the fractional-cover optimum: for the triangle, $x_e=\tfrac12$ per edge gives $|Q|\le N^{1/2}\cdot N^{1/2}\cdot N^{1/2} = N^{3/2} = 10^6$. A worst-case-optimal join (e.g. Leapfrog Triejoin) runs in $\tilde O(N^{3/2}) = \tilde O(10^6)$ — never materializing the $10^8$ blowup.

So a non-inflation audit certifies the bill must lie in the interval
$$ [\text{AGM floor},\ \text{WCOJ ceiling}] = [\,\Omega(|Q|),\ \tilde O(10^6)\,]. $$
A bill of $10^8$ falls **outside** this interval and is provably inflated ($100\times$ the WCOJ ceiling). But within $[10^6 \text{-ish}, \tilde O(10^6)]$ no proof can pin down a unique "true" cost — illustrating exactly why non-inflation is only loosely certifiable and remains open.

---
*Part of the [DBMS Research catalog](../../README.md).*
