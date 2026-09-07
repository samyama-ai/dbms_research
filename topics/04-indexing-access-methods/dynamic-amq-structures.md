---
id: 04-indexing-access-methods/dynamic-amq-structures
title: "Approximate-membership for dynamic sets"
topic: 04-indexing-access-methods
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Approximate-membership for dynamic sets

> **Topic:** Indexing & Access Methods · **ID:** `04-indexing-access-methods/dynamic-amq-structures` · **Status:** open

## 1. Problem Statement
An **approximate membership query (AMQ)** structure (a "filter") represents a set $S\subseteq U$ and answers membership: "yes" always for $x\in S$ (no false negatives) and "yes" with probability at most $\varepsilon$ for $x\notin S$ (false positives). The **dynamic** problem additionally requires efficient **insertions**, **deletions**, and **resizing/growth** as $|S|=n$ changes — ideally while (i) staying within the static information-theoretic space lower bound, (ii) preserving the target false-positive rate $\varepsilon$ even after long delete/insert sequences, and (iii) keeping operations $O(1)$ expected time with good cache locality. Variants: **deletion-correctness** (deletes must not introduce false negatives), the **adaptive/adversarial** variant (maintain $\varepsilon$ against a query-adaptive adversary), and the **resizable** variant (grow without rebuild while keeping space optimal). The open question is whether one structure achieves all three simultaneously.

## 2. Mathematical Foundations
The static space lower bound is information-theoretic: any AMQ for $n$ elements from universe $|U|=u$ with FPR $\varepsilon$ needs at least $n\log_2(1/\varepsilon)$ bits, i.e. $\ge \log_2(1/\varepsilon)$ bits/element (Carter–Floyd–Gill–Markowsky–Wegman 1978; Bloom 1970 gives $\approx 1.44\log_2(1/\varepsilon)$). Standard **Bloom filters** are static-friendly but do not support deletion; **counting Bloom filters** add deletes at ~4× space. **Quotient filters** and **cuckoo filters** store fingerprints of length $\approx \log_2(1/\varepsilon)+O(1)$ in an open-addressed table, supporting delete and reaching $\log_2(1/\varepsilon)+2.125$ bits (cuckoo) or near $\log_2(1/\varepsilon)+2.125$–$3$ (quotient). The relevant measures: **redundancy** $R = \text{space} - n\log_2(1/\varepsilon)$ bits, operation time, and the **resize cost**. Adaptivity is formalized via an adversary that, after each "yes," can pick the next query (Bender et al.); maintaining $\varepsilon$ then requires re-randomizing fingerprints, which interacts with deletes.

## 3. State of the Art (SOTA)
- **Foundational:** Bloom filter (Bloom, CACM 1970); counting Bloom (Fan et al., 2000).
- **Deletable, near-optimal:** **Quotient filter** (Bender et al., *Don't Thrash: How to Cache Your Hash on Flash*, VLDB 2012) and the **RSQF/CQF — Counting Quotient Filter** (Pandey, Bender, Johnson, Patro, SIGMOD 2017): supports inserts, deletes, counts, resizing, near space-optimal, cache-friendly.
- **Cuckoo filter** (Fan, Andersen, Kaminsky, Mitzenmacher, CoNEXT 2014): deletes, $\le \log_2(1/\varepsilon)+3$ bits, but deletion correctness assumes elements were actually inserted, and load-factor limits complicate resize.
- **Adaptive:** **Telescoping/adaptive cuckoo filters** and the **Broom filter / adaptive AMQ** (Bender, Conway, Farach-Colton, Kuszmaul, et al., FOCS 2018) maintain $\varepsilon$ against adaptive adversaries with near-optimal space.
- **Succinct:** Bloomier filters and **succinct retrieval/XOR filters** (Ribbon, BinaryFuse) reach $\sim 1.0$–$1.13\times$ the bound but are **static/immutable**.

## 4. Upper Bound
For the **dynamic** setting, the CQF achieves $O(1)$ expected insert/delete/lookup with redundancy roughly $2.125$–$3$ bits/element above the bound and supports resizing by re-hashing. The **adaptive** Broom filter attains $(1+o(1))\,n\log_2(1/\varepsilon)$ bits with $O(1)$ operations while sustaining FPR $\varepsilon$ under adversarial queries (RAM model, word size $w=\Omega(\log u)$). Static XOR/Ribbon filters get within $\sim 1.1\times$ of optimal but forbid updates. Thus the *static-optimal-and-dynamic-and-adaptive* combination is not simultaneously achieved by any single known structure.

## 5. Lower Bound
The $n\log_2(1/\varepsilon)$-bit floor is unconditional and information-theoretic. For **dynamic** filters, Lovett–Porat (FOCS 2010) showed a *space–time* lower bound: any dynamic filter using close-to-optimal space must pay a super-constant penalty — specifically there is no dynamic AMQ that is simultaneously space-optimal and constant-time in the cell-probe model under their assumptions, establishing a genuine separation between static and dynamic. For **adaptive** filters, maintaining a fixed $\varepsilon$ against an adaptive adversary requires additional randomness/space (Naor–Yogev; Bender et al.). These give cell-probe and information-theoretic obstructions to "best of all worlds."

## 6. The Gap
The Lovett–Porat lower bound says a *dynamic* filter cannot match the static bound at constant time, so some redundancy or time penalty is provably necessary — but the **exact optimal trade-off curve** (redundancy vs. operation time vs. resizability vs. adaptivity) is unknown. Practical structures (CQF, cuckoo) sit a few bits above the floor with $O(1)$ ops; whether $o(1)$ redundancy-per-element is achievable dynamically, and whether adaptivity can be free, are open. Resizing without amortized rebuild while staying optimal is also unresolved. This is genuinely open.

## 7. Current Research (as of June 2026)
Active directions: practical **adaptive AMQs** that combine CQF-style space with telescoping adaptivity; **Ribbon/BinaryFuse** filters and making such retrieval-based designs incrementally updatable *(frontier — verify)*; learned and **partitioned/blocked** filters tuned to skewed workloads (LSM-tree filter design, Monkey/ElasticBF lineage from Idreos/Athanassoulis groups); GPU/vectorized filter throughput; and filters resilient to adversarial inputs (cryptographic robustness, Naor–Yogev). Groups: Bender–Farach-Colton–Kuszmaul–Pandey (BetrFS/CQF lineage), Mitzenmacher (cuckoo/learned filters), Dillinger/Walzer (Ribbon).

## 8. Future Work
- Tight characterization of the dynamic redundancy–time trade-off (close the Lovett–Porat gap).
- A single structure: space-optimal, deletable, resizable, and adaptive.
- Incrementally updatable XOR/Ribbon filters approaching $1.0\times$ the bound dynamically.
- Workload-/distribution-aware (learned) dynamic filters with provable FPR guarantees.
- Robust filters against adaptive and adversarial query streams at near-optimal space.

## 9. Key References
- **[Foundational]** B. H. Bloom. *Space/Time Trade-offs in Hash Coding with Allowable Errors.* CACM, 1970. — [DOI](https://doi.org/10.1145/362686.362692)
- **[Foundational]** L. Carter, R. Floyd, J. Gill, G. Markowsky, M. Wegman. *Exact and Approximate Membership Testers.* STOC, 1978. — [DOI](https://doi.org/10.1145/800133.804332)
- **[SOTA]** P. Pandey, M. A. Bender, R. Johnson, R. Patro. *A General-Purpose Counting Filter: Making Every Bit Count.* SIGMOD, 2017. — [DOI](https://doi.org/10.1145/3035918.3035963)
- **[SOTA]** B. Fan, D. G. Andersen, M. Kaminsky, M. Mitzenmacher. *Cuckoo Filter: Practically Better Than Bloom.* CoNEXT, 2014. — [DOI](https://doi.org/10.1145/2674005.2674994)
- **[Foundational]** S. Lovett, E. Porat. *A Lower Bound for Dynamic Approximate Membership Data Structures.* FOCS, 2010. — [DBLP](https://dblp.org/rec/conf/focs/LovettP10.html)
- **[SOTA]** M. A. Bender, M. Farach-Colton, M. Goswami, R. Johnson, S. McCauley, S. Singh. *Bloom Filters, Adaptivity, and the Dictionary Problem (Broom Filter).* FOCS, 2018. — [arXiv](https://arxiv.org/abs/1711.01616)

## 10. Worked Example

Target FPR $\varepsilon=2^{-8}=1/256$, so the information-theoretic floor is $\log_2(1/\varepsilon)=8$ bits/element. Store $n=10^6$ keys.

- **Floor:** $n\log_2(1/\varepsilon)=8\text{ Mbit}=1.0$ MB.
- **Bloom filter:** $\approx 1.44\cdot 8=11.5$ bits/elt $\Rightarrow 1.44$ MB, but **no deletes**.
- **Cuckoo filter:** fingerprint $8$ bits $+$ overhead $\approx 8+3=11$ bits/elt $\Rightarrow 1.31$ MB, **supports delete**.
- **Counting Quotient Filter:** $\approx 8+2.125=10.1$ bits/elt $\Rightarrow 1.26$ MB, deletes + counts + resize.

Now the **dynamic** twist. Delete key $x$ from the cuckoo filter: it removes *a* fingerprint matching $x$'s 8-bit tag from one of $x$'s two buckets. If a different key $y$ collided to the same tag+bucket, the delete may evict $y$'s slot — correctness holds only if $x$ was genuinely inserted. And under an **adaptive adversary** who, after each false positive, re-queries the offending element, a static fingerprint keeps failing; sustaining $\varepsilon$ forces re-randomizing that fingerprint, costing extra bits. The Lovett–Porat bound says no dynamic filter hits the $8$-bit floor at $O(1)$ time — the $\sim 2$–$3$ surplus bits above are provably not fully removable.

---
*Part of the [DBMS Research catalog](../../README.md).*
