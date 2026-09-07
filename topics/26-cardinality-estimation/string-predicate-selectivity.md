---
id: 26-cardinality-estimation/string-predicate-selectivity
title: "Statistics for String & Pattern Predicates"
topic: 26-cardinality-estimation
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
refs_checked: 2026-09
---

# Statistics for String & Pattern Predicates

> **Topic:** Cardinality Estimation & Statistics · **ID:** `26-cardinality-estimation/string-predicate-selectivity` · **Status:** open

## 1. Problem Statement

Estimate the **selectivity** (fraction of matching rows) of predicates over text columns: equality, prefix (`LIKE 'abc%'`), suffix, substring (`LIKE '%abc%'`), arbitrary `LIKE` patterns with multiple wildcards, and regular expressions. The optimizer needs $\hat s(p)$ for such predicates to size scans, index choices, and downstream joins.

Variants:

- **Counting/estimation:** estimate the number of strings in column $C$ matching pattern $p$.
- **Per-pattern-class:** prefix and exact-match are comparatively easy (tries, histograms); substring/regex are hard because matches are not contiguous in sort order.
- **Compositional:** propagate string-predicate selectivity into join and group-by estimates.

The defining challenge: unlike numeric ranges, string match-sets are *not intervals* in any single order, so 1-D histograms fail for substring/regex, and the combinatorial space of patterns precludes precomputing per-pattern counts.

## 2. Mathematical Foundations

Let $C$ be a multiset of $n$ strings over alphabet $\Sigma$. For a pattern $p$, selectivity $s(p)=\frac1n\,\big|\{w\in C: w\models p\}\big|$.

- **Prefix:** matches form a contiguous range in lexicographic order, so an **equi-depth string histogram** or a count-augmented **trie/B-tree** answers prefix selectivity exactly or with bounded error.
- **Substring:** decompose the pattern into **q-grams** (length-$q$ substrings). Under a (naive) independence assumption, $\Pr[\text{string contains } g_1g_2\cdots g_m]\approx \prod_i \Pr[g_i]$, but overlapping q-grams are highly correlated, so this overestimates or underestimates badly. **Markov / n-gram language models** of order $k$ refine this: $\Pr[w]\approx \prod_t \Pr[c_t\mid c_{t-1}\dots c_{t-k}]$.
- **Pruned suffix trees / Krishnan–Vitter–Iyer (SIGMOD 1996):** count substring occurrences via a pruned suffix tree (PST) over the concatenated column, the foundational structure for substring selectivity.
- **Set-similarity view:** treat each string as its q-gram set; selectivity of `LIKE '%p%'` relates to q-gram set containment, connecting to MinHash/Jaccard sketches.

For regex, the match set is the language $L(r)\cap C$; selectivity estimation reduces to estimating $|C\cap L(\mathcal A)|$ for the automaton $\mathcal A$, which can be folded over a trie of $C$ but with state-space blow-up.

## 3. State of the Art (SOTA)

- **Foundational structures:** Pruned Suffix Trees (Krishnan, Vitter, Iyer, SIGMOD 1996); **Maximal Overlap (MO) and Markov estimators** for substrings (Jagadish, Ng, Srivastava, ICDE 1999; Chaudhuri, Ganti, Gravano, ICDE 2004 — "selectivity estimation for string predicates with regular expressions / short identifying substrings").
- **q-gram + Markov tables** are the practical workhorse in systems; PostgreSQL estimates `LIKE`/regex via a heuristic over the most-common-values list and a fixed per-wildcard fudge factor.
- **Systems-SOTA:** commercial optimizers use trigram statistics and MCV lists; specialized text indexes (GIN/GiST trigram in PostgreSQL) help execution but not always estimation.
- **Learned-SOTA:** character-level RNN/Transformer density models and embedding-based estimators (e.g. **Astrid**, learned substring/LIKE estimators) outperform q-gram baselines on benchmarks *(frontier — verify)*; cardinality-estimation models extended to string predicates.

## 4. Upper Bound

- **Prefix/equality:** exact or $(1\pm\varepsilon)$ from a count-augmented trie/string histogram in $O(|p|)$ lookup, near-optimal.
- **Substring (PST/Markov):** $O(|p|)$ estimation from a pruned suffix tree of bounded size; error is bounded only under the Markov-independence model — no distribution-free guarantee.
- **Set-similarity:** MinHash sketches over q-gram sets give $(\varepsilon,\delta)$ Jaccard/containment estimates in $O(\varepsilon^{-2})$ space, yielding bounds for some `%...%` patterns.

## 5. Lower Bound

- **Substring counting is hard:** exact substring-occurrence counting over a stream needs $\Omega(n)$ space in the worst case; estimating it tightly inherits text-indexing space lower bounds.
- **Regex selectivity:** for general regular expressions the match-set can be adversarial; *exactly* counting matches relates to #P-style counting over automaton-weighted languages, and any compact synopsis must lose patterns (information-theoretic — there are $\exp(\Theta(\cdot))$ patterns but only polynomial space).
- **Independence assumptions are provably violable:** adversarial string distributions make q-gram-independence estimates off by $\Theta(n)$-factors, so no fixed-order Markov synopsis has a worst-case multiplicative guarantee.

## 6. The Gap

**Open.** Prefix/equality is effectively closed; **substring and regex selectivity remain genuinely open**: every practical estimator relies on independence or Markov assumptions that lack worst-case guarantees, and the few information-theoretic results say compact synopses *must* fail on adversarial inputs. Learned models improve average accuracy but inherit the drift/no-guarantee problems of LCEs. Closing the gap needs either (a) synopses with provable error under stated string-distribution classes, or (b) hardness theorems pinning the achievable accuracy–space tradeoff for substring/regex.

## 7. Current Research (as of June 2026)

- Learned substring/LIKE estimators (character-level autoregressive and embedding models such as Astrid and successors) and their integration into optimizers *(frontier — verify)*.
- Robust q-gram/Markov hybrids with calibrated error and OOD detection for unseen patterns.
- Regex selectivity via automaton-folded sketches and learned counting (groups at Microsoft Research, TUM, and the broader learned-CE community: Chaudhuri/Narasayya, Kemper/Neumann).
- Extending string selectivity to multilingual / Unicode and to join predicates on text keys.

## 8. Future Work

- Distribution-free or assumption-bounded substring/regex selectivity with guarantees.
- Unified synopsis serving prefix, substring, and regex from one compact structure.
- Calibrated uncertainty intervals for string predicates (link to the CI problem in this topic).
- Update-friendly text synopses under high-churn columns.

## 9. Key References

- **[Foundational]** Krishnan, Vitter, Iyer. *Estimating Alphanumeric Selectivity in the Presence of Wildcards.* SIGMOD, 1996. — [DOI](https://doi.org/10.1145/233269.233341)
- **[Foundational]** Jagadish, Ng, Srivastava. *Substring Selectivity Estimation.* PODS, 1999. — [DBLP](https://dblp.org/rec/conf/pods/JagadishNS99)
- **[SOTA]** Chaudhuri, Ganti, Gravano. *Selectivity Estimation for String Predicates: Overcoming the Underestimation Problem.* ICDE, 2004. — [DOI](https://doi.org/10.1109/ICDE.2004.1319999)
- **[SOTA]** Shetiya, Thirumuruganathan, Koudas, Das. *Astrid: Accurate Selectivity Estimation for String Predicates using Deep Learning.* PVLDB, 2021. — [DOI](https://doi.org/10.14778/3436905.3436907)
- **[Survey]** Cormode, Garofalakis, Haas, Jermaine. *Synopses for Massive Data: Samples, Histograms, Wavelets, Sketches.* Foundations and Trends in Databases, 2011. — [DOI](https://doi.org/10.1561/1900000004)
- **[Foundational]** Broder. *On the Resemblance and Containment of Documents (MinHash).* SEQUENCES, 1997. — [DOI](https://doi.org/10.1109/SEQUEN.1997.666900)

## 10. Worked Example

Column $C$ = four strings: `data`, `database`, `metadata`, `rate`; $n=4$. Estimate selectivity of `LIKE '%at%'` using **2-grams** under the naive independence model.

Tokenize each string into overlapping bigrams and count how many strings contain each:
- `at`: in `data`, `database`, `metadata`, `rate` → 4/4, so $\Pr[\texttt{at}]=1.0$.

For the single-bigram pattern `%at%`, the estimate is just $\Pr[\texttt{at}]=1.0$, i.e. $\hat s=1.0$ — and indeed all 4 strings match, so this is exact.

Now `LIKE '%ata%'` (pattern bigrams `at`,`ta`). $\Pr[\texttt{at}]=1.0$; `ta` appears in `data`,`database`,`metadata` → $\Pr[\texttt{ta}]=3/4$. Independence gives $\hat s \approx 1.0 \times 0.75 = 0.75 \Rightarrow 3$ rows. True matches of substring `ata`: `data`, `database`, `metadata` = 3 — here independence happens to be right. But for `%tat%` (bigrams `ta`,`at`), independence predicts $0.75\times1.0=0.75 \Rightarrow 3$ rows, yet **no** string actually contains the substring `tat` (0/4): independence **overestimates** badly (3 predicted rows vs. 0 true) because the bigrams overlap and the order constraint `t-a-t` is lost — the core failure mode that q-gram independence cannot bound in the worst case.

---
*Part of the [DBMS Research catalog](../../README.md).*
