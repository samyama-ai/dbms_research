# Inclusion Dependency and Foreign-Key Discovery

> **Topic:** Schema Design & Normalization · **ID:** `34-schema-design-normalization/inclusion-dependency-discovery` · **Status:** partially-solved

## 1. Problem Statement
Given a database instance $I$ over a schema with relations $R_1,\dots,R_m$, discover all **inclusion dependencies (INDs)** that hold on $I$ and then distinguish *genuine* foreign keys (FKs) from *coincidental* containments.

- **Decision variant:** Given a candidate IND $R[A_1,\dots,A_k] \subseteq S[B_1,\dots,B_k]$, does it hold on $I$? (Trivially checkable; the difficulty is the search space.)
- **Discovery (enumeration) variant:** Output the set of all *valid* INDs, typically only the **maximal** ones to control output size.
- **n-ary variant:** Find INDs where $k>1$ (column combinations), whose candidate space is exponential in attribute count.
- **FK ranking variant (optimization):** Among valid INDs, score/select the subset most likely to be *real* referential constraints rather than chance overlaps (e.g., two unrelated low-cardinality columns).

The core tension: IND *validity* is cheap per candidate, but the **candidate lattice** is enormous, and validity does not imply semantic foreign-keyness.

## 2. Mathematical Foundations
An IND $\sigma: R[X] \subseteq S[Y]$ with $|X|=|Y|=k$ holds on $I$ iff $\pi_X(R^I) \subseteq \pi_Y(S^I)$ (projection-containment under relational algebra). INDs are governed by a sound and complete axiomatization (reflexivity, projection-permutation, transitivity); however, the **finite implication problem for INDs combined with functional dependencies is undecidable** (Chandra–Vardi), and IND implication alone is **PSPACE-complete** (Casanova–Fagin–Papadimitriou).

The discovery search forms a lattice ordered by attribute-set containment with an **anti-monotone** property: if $R[X]\subseteq S[Y]$ fails, no superset extension holds — enabling Apriori-style pruning. n-ary candidate generation mirrors frequent-itemset mining; the number of unary INDs bounds binary candidates, etc.

Coincidence likelihood can be modeled information-theoretically: for columns of domain size $d$ and cardinalities $n_R,n_S$, the probability that $n_R$ random draws fall inside an $n_S$-subset gives a null-model $p$-value; FK scores combine such randomness bounds with $\frac{|\pi_X(R)|}{|\pi_Y(S)|}$ coverage, value-distribution similarity, and naming/typing priors. Some formalize "spurious vs. genuine" via $\chi^2$ or KL divergence between donor and recipient value histograms.

## 3. State of the Art (SOTA)
**Systems-SOTA.** **SPIDER** (Bauckmann et al., 2007) sorts and merge-scans columns to find all unary INDs in near-linear I/O. **BINDER** (Papenbrock et al., VLDB 2015) uses divide-and-conquer bucketing for unary+n-ary INDs at scale. **FAIDA** (Kruse et al., 2017) trades exactness for speed via inverted-index + HyperLogLog approximation. For FK selection, **Rostin et al. (2009)** apply ML over features (value coverage, distribution, name similarity); **HoPF** and **Zhang et al.** rank FKs by coverage + randomness. **Metanome** packages these as a benchmarked profiling platform.

**Theory-SOTA.** n-ary IND discovery is **W[?]/exponential** in arity; tractable fragments and the lattice-pruning meta-algorithm (Marchi–Lopes–Petit, "Unary and N-ary Inclusion Dependency Discovery," 2009) frame the canonical approach.

## 4. Upper Bound
Unary IND discovery is **$O(N \log N)$** I/O via global sort-merge (SPIDER), where $N$ is total cell count — essentially optimal for the sort-based model. n-ary discovery is **output-sensitive**: levelwise generation costs $O(\sum_\ell c_\ell \cdot \text{validate})$ where $c_\ell$ is candidates at arity $\ell$; with anti-monotone pruning this is polynomial in the number of *valid maximal* INDs but worst-case exponential in attribute count. Approximate variants (FAIDA) achieve **near-linear** time with bounded false-positive rate $\delta$ via sketching.

## 5. Lower Bound
Deciding whether a given set of INDs *implies* another is **PSPACE-complete** (Casanova–Fagin–Papadimitriou, 1984), so any complete reasoning layer inherits this. The **enumeration** problem has output that can be exponential in the schema arity, so no algorithm runs polynomially in input size alone. FK *correctness* has **no information-theoretic lower bound from data alone**: distinguishing a true FK from a coincidental IND is not determined by the instance — it is a fundamentally underdetermined (semantic) inference, making exact recovery impossible without external schema/intent signals.

## 6. The Gap
For **unary** INDs the gap is essentially closed (sort-optimal). For **n-ary** discovery the gap is between worst-case exponential candidate space and the often-small valid output — open whether instance-adaptive enumeration can be made output-polynomial for all schemas. For **FK identification**, the gap is qualitative, not complexity-theoretic: there is no ground-truth-free guarantee, so research targets calibrated precision/recall rather than provable correctness.

## 7. Current Research (as of June 2026)
Active threads: (1) GPU/columnar-vectorized IND discovery and incremental/streaming maintenance under updates; (2) **LLM-assisted FK inference** that combines structural IND validity with column-name/value semantics to rank referential intent *(frontier — verify)*; (3) data-lake-scale cross-table profiling integrated with table-discovery/union-search systems (Nargesian, Miller; the "table union search" line). Groups at HPI (Naumann, Papenbrock), Toronto (Miller), and the Metanome/Metacrate ecosystem remain central. Benchmark work increasingly measures FK *semantic* precision, not just IND validity.

## 8. Future Work
- Output-polynomial enumeration guarantees for n-ary INDs on realistic schemas.
- Principled null-models / hypothesis tests that give calibrated *p*-values for "coincidental IND."
- Incremental discovery under inserts/deletes with provable maintenance cost.
- Joint discovery of INDs + FDs + conditional INDs for richer constraint recovery.

## 9. Key References
- **[Foundational]** Casanova, M.A., Fagin, R., Papadimitriou, C.H. *Inclusion Dependencies and Their Interaction with Functional Dependencies.* PODS / JCSS, 1984. — [DOI](https://doi.org/10.1016/0022-0000(84)90075-8)
- **[Foundational]** Chandra, A., Vardi, M. *The Implication Problem for Functional and Inclusion Dependencies is Undecidable.* SIAM J. Computing, 1985. — [DOI](https://doi.org/10.1137/0214049)
- **[SOTA]** Papenbrock, F., Kruse, S., Quiané-Ruiz, J.-A., Naumann, F. *Divide & Conquer-based Inclusion Dependency Discovery (BINDER).* PVLDB, 2015. — [DOI](https://doi.org/10.14778/2752939.2752946)
- **[SOTA]** Bauckmann, J., Leser, U., Naumann, F. *Efficiently Detecting Inclusion Dependencies (SPIDER).* ICDE, 2007. — [DOI](https://doi.org/10.1109/ICDE.2007.369009) · [DBLP](https://dblp.org/rec/conf/icde/BauckmannLNT07.html)
- **[SOTA]** Rostin, A., Albrecht, O., Bauckmann, J., Naumann, F., Leser, U. *A Machine Learning Approach to Foreign Key Discovery.* WebDB, 2009. — [DBLP](https://dblp.org/rec/conf/webdb/RostinABNL09.html)
- **[Survey]** Abiteboul, S., Hull, R., Vianu, V. *Foundations of Databases.* Addison-Wesley, 1995 (IND theory, Ch. 9). — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)

## 10. Worked Example
Two relations:
$$\text{Order}(oid, custid):\ \{(1,10),(2,10),(3,20)\}\qquad \text{Customer}(cid, status):\ \{(10,\text{gold}),(20,\text{silver}),(30,\text{new})\}.$$

**Validity check.** Candidate IND $\sigma:\ \text{Order}[custid]\subseteq\text{Customer}[cid]$. Compute $\pi_{custid}(\text{Order})=\{10,20\}$ and $\pi_{cid}(\text{Customer})=\{10,20,30\}$. Since $\{10,20\}\subseteq\{10,20,30\}$, $\sigma$ **holds** — a genuine FK candidate. The reverse $\text{Customer}[cid]\subseteq\text{Order}[custid]$ fails ($30\notin\{10,20\}$), illustrating the anti-monotone direction.

**Coincidental IND.** Add $\text{Order}[oid]\subseteq\text{Customer}[cid]$: $\pi_{oid}=\{1,2,3\}$, which is *not* $\subseteq\{10,20,30\}$, so it fails — good. But had $oid$ values happened to be $\{10,20,30\}$, this IND would hold by chance despite no referential meaning. The null model quantifies this: for domain size $d=100$, $n_R=3$ draws falling in an $n_S=3$ subset by chance has probability $\approx (3/100)^3 \approx 2.7\times10^{-5}$ — low, so a holding IND here is unlikely coincidental, raising its FK score.

**Cost.** Unary discovery via SPIDER sorts all $N$ cells once and merge-scans: $O(N\log N)$ I/O, here $N=2\cdot3 + 2\cdot3 = 12$ cells. The hard part is not this check but the n-ary lattice: with $a$ attributes the binary-candidate count grows combinatorially, pruned only when a unary sub-IND already fails.

---
*Part of the [DBMS Research catalog](../../README.md).*
