# Chase Step Complexity and Size Bounds

> **Topic:** Relational Model & Dependency Theory · **ID:** `01-relational-theory/chase-size-bounds` · **Status:** partially-solved

## 1. Problem Statement

The **chase** is the canonical procedure for reasoning with tuple- and equality-generating dependencies (tgds/egds): repeatedly fix dependency violations by adding tuples (with fresh labeled nulls) or equating values. Given a database $D$ and a set $\Sigma$ of dependencies, the chase — when it terminates — yields a universal model $\mathrm{chase}_\Sigma(D)$. The problem:

- **(Termination)** Decide whether the (standard/oblivious/restricted) chase terminates on all instances for a given $\Sigma$.
- **(Size bound)** Bound $|\mathrm{chase}_\Sigma(D)|$ as a function of $|D|$ and the structure of $\Sigma$.
- **(Step bound)** Bound the *number of chase steps* (rule firings) until termination.
- **(Optimization)** Find the chase order / strategy minimizing produced facts.

These govern the cost of data-exchange materialization, query answering under constraints, and certain-answer computation.

## 2. Mathematical Foundations

A **tgd** has the form $\forall \bar x\, \big(\varphi(\bar x) \to \exists \bar y\, \psi(\bar x,\bar y)\big)$ with $\varphi,\psi$ conjunctions of atoms; an **egd** is $\forall \bar x\,(\varphi(\bar x) \to x_i = x_j)$. The chase produces a universal solution: a model that homomorphically maps into every solution, so certain answers are computed by evaluating the query on it and dropping nulls.

Termination is **undecidable** in general for the standard chase (Deutsch–Nash–Remmel). Sufficient *syntactic* conditions form a hierarchy:
$$
\text{weak acyclicity} \subsetneq \text{safety} \subsetneq \text{(super-)weak acyclicity} \subsetneq \text{stratification} \subsetneq \dots
$$
For **weakly acyclic** $\Sigma$, the chase terminates in **polynomial time in $|D|$** (degree depending on $\Sigma$), with $|\mathrm{chase}_\Sigma(D)| = O(|D|^{c})$ where $c$ is bounded by the longest path in the dependency graph. The exponent is tied to a **rank** of the position dependency graph.

## 3. State of the Art (SOTA)

- **Theory-SOTA.** Fagin, Kolaitis, Miller & Popa (*TCS* 2005) introduced weak acyclicity and the polynomial chase bound for data exchange. Marnette (2009) introduced **super-weak acyclicity**; Meier, Schmidt & Lausen and Grahne–Onet refined stratification-based criteria. Gogacz, Marcinkowski and colleagues sharpened (un)decidability boundaries of all-instance termination.
- **Restricted vs oblivious chase** termination classes were separated and partly characterized (Onet 2013; Grahne & Onet).
- **Systems-SOTA.** Chase engines: **LLUNATIC** (Geerts, Mecca, Papotti, Santoro), **PDQ**, **ChaseBench** (Benedikt et al., *SIGMOD* 2017) for benchmarking; **RDFox** and Datalog$^\pm$ reasoners exploit acyclicity in practice.

## 4. Upper Bound

For weakly acyclic $\Sigma$ the standard chase terminates after a number of steps polynomial in $|D|$, producing a universal solution of size $O(|D|^{r})$ where $r$ is bounded by the maximal rank in the dependency graph — combined complexity is exponential in $|\Sigma|$ but **PTIME in data complexity**. Restricted-chase termination, when it holds, can be exponentially smaller than the oblivious chase. For full tgds (no existentials) the chase terminates in PTIME with output polynomial in $|D|$. Model: finite labeled-null instances, homomorphism-based universal-solution semantics.

## 5. Lower Bound

- **Termination is undecidable**: whether the standard chase terminates on all instances for a given $\Sigma$ is **r.e.-complete / undecidable** (Deutsch, Nash, Remmel 2008; Gogacz & Marcinkowski 2014 closed remaining cases for the all-instances variant).
- **Size lower bounds**: there exist weakly-acyclic $\Sigma$ forcing $|\mathrm{chase}_\Sigma(D)| = \Omega(|D|^{r})$ matching the upper exponent, so the polynomial degree is essentially tight per dependency rank.
- Deciding certain answers under arbitrary tgds is **undecidable**; even guarded/bounded fragments reach **2EXPTIME**-completeness (Calì, Gottlob, Kifer for Datalog$^\pm$).

## 6. The Gap

For weakly-acyclic and the named syntactic classes, upper and lower size/step bounds **match up to the polynomial degree** — this part is essentially closed. The genuinely **open** frontier is *all-instance chase termination* outside the known syntactic islands: the precise boundary between decidable and undecidable termination criteria, and tight bounds for the **restricted (standard) chase** where order matters, are not fully characterized. Closing it requires either new decidable termination criteria strictly beyond super-weak acyclicity or sharper undecidability reductions.

## 7. Current Research (as of June 2026)

Active threads: (i) **restricted-chase termination** characterizations and the role of fact-ordering (Gogacz, Marcinkowski, Pieris); (ii) **chase termination for existential rules / Datalog$^\pm$** with guardedness and frontier-guardedness (Gottlob, Pieris, Calautti); (iii) practical **chase optimization** — provenance-aware and parallel chasing in LLUNATIC and VLog/RDFox. *(frontier — verify)* Recent work connects chase size to **information-theoretic / entropic bounds** on universal-model size and to worst-case-optimal-join-style output bounds (Suciu, Ngo circles). *(frontier — verify)* Incremental/streaming chase under updates is an emerging systems direction.

## 8. Future Work

- A decidable, semantically complete characterization of all-instance restricted-chase termination.
- Tight step-vs-size tradeoffs and order-optimal chase strategies.
- Entropy/AGM-style worst-case-optimal bounds on universal-solution size.
- Robust parallel and incremental chase engines with provenance.

## 9. Key References

- **[Foundational]** R. Fagin, P. G. Kolaitis, R. J. Miller, L. Popa. *Data exchange: semantics and query answering.* Theoretical Computer Science, 2005. — [DOI](https://doi.org/10.1016/j.tcs.2004.10.033)
- **[Foundational]** A. Deutsch, A. Nash, J. Remmel. *The chase revisited.* PODS, 2008. — [ACM](https://dl.acm.org/doi/10.1145/1376916.1376938)
- **[SOTA]** B. Marnette. *Generalized schema-mappings: from termination to tractability.* PODS, 2009. — [ACM](https://dl.acm.org/doi/10.1145/1559795.1559799)
- **[SOTA]** T. Gogacz, J. Marcinkowski. *All-instances termination of chase is undecidable.* ICALP, 2014. — [DOI](https://doi.org/10.1007/978-3-662-43951-7_25)
- **[SOTA]** M. Benedikt et al. *Benchmarking the chase.* SIGMOD (PODS), 2017. — [ACM](https://dl.acm.org/doi/10.1145/3034786.3034796)
- **[Foundational]** A. Calì, G. Gottlob, M. Kifer. *Taming the infinite chase: Query answering under expressive relational constraints (Datalog±).* Journal of Artificial Intelligence Research, 2013. — [arXiv](https://arxiv.org/abs/1212.3357)
- **[Survey]** S. Abiteboul, R. Hull, V. Vianu. *Foundations of Databases.* Addison-Wesley, 1995. — [DBLP](https://dblp.org/db/books/dbtext/abiteboul95.html)

## 10. Worked Example

A weakly-acyclic TGD set whose position graph has a path of length 2, giving a quadratic blow-up. Schema $N(\text{x})$, edges $E(\text{x},\text{y})$. Dependencies:
$$\tau_1:\ N(x)\to\exists y\,E(x,y),\qquad \tau_2:\ E(x,y)\to N(y).$$

The position dependency graph has a *special* edge $N[1]\to E[2]$ (existential) and an ordinary edge $E[2]\to N[1]$; no cycle passes through two special edges, so $\Sigma$ is weakly acyclic and the chase terminates.

Start with $D=\{N(a)\}$, $|D|=1$. Trace:
1. $\tau_1$ fires on $N(a)$: add $E(a,n_1)$ (fresh null $n_1$).
2. $\tau_2$ fires on $E(a,n_1)$: add $N(n_1)$.
3. $\tau_1$ on $N(n_1)$: add $E(n_1,n_2)$.
4. $\tau_2$: add $N(n_2)$ — and so on.

With $k$ starting constants the chase produces $O(k)$ facts here (rank $1$). The polynomial degree $r$ equals the longest special-edge path: $|\mathrm{chase}_\Sigma(D)|=O(|D|^{r})$. A two-stage propagation (rank $2$) instead yields the matching $\Omega(|D|^2)$ lower bound, confirming tightness per dependency rank.

---
*Part of the [DBMS Research catalog](../../README.md).*
