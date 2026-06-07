---
id: 06-recovery-logging/compressed-encrypted-log-recovery
title: "Recovery for compressed/encrypted logs"
topic: 06-recovery-logging
status: open
first_added: 2026-06
last_reviewed: 2026-06
last_substantive_update: 2026-06
stale_since: ""
provenance: synthesized
---

# Recovery for compressed/encrypted logs

> **Topic:** Recovery, Logging & Durability · **ID:** `06-recovery-logging/compressed-encrypted-log-recovery` · **Status:** open

## 1. Problem Statement
Write-ahead logs are increasingly **compressed** (to cut log volume, I/O, and replication bandwidth) and **encrypted** (at rest and in flight, for confidentiality and regulatory compliance). Both transformations sit on the critical durability path and interact badly with recovery's core requirements: recovery must be able to (a) read the log *forward and backward* (redo forward, undo backward), (b) recover from a crash *in the middle of writing a record/block*, and (c) detect corruption and authenticate records. Compression couples records into blocks (you cannot decode record $i$ without the surrounding block) and encryption with chaining/AEAD couples ciphertext and requires nonce/IV management and authentication tags. The problem is to **guarantee recoverability and integrity when log records are compressed and/or encrypted**, without sacrificing crash-atomicity, partial-rollback, or recovery performance.

Variants:
- **Decision/verification:** given a compressed-and-encrypted log format, is every crash-truncated log *uniquely and correctly recoverable* (no ambiguity, no undetected truncation/tearing)?
- **Optimization:** minimize the recovery-time and space cost of supporting random access / reverse scan over compressed-encrypted logs (block size vs. compression ratio vs. seek cost trade-off).
- **Security:** provide **integrity/authenticity** (tamper-evidence, forward security, ordering/append-only proofs) and confidentiality with bounded overhead, ideally without trusting the storage layer.

## 2. Mathematical Foundations
A WAL is an append-only sequence with per-record LSNs and back-links; recovery relies on **self-identifying, independently decodable** records and on detecting the *valid prefix* after a crash (the longest well-formed, checksum-valid prefix). Compression breaks per-record independence: with block compression, the decode unit is a **block**, so the recoverable granularity becomes the block, and a torn block can lose a whole batch — formalized by requiring the log to be a sequence of **self-delimiting, individually verifiable frames** $F_1\,F_2\,\dots$ where each $F_j$ carries (length, checksum, and for AEAD an authentication tag over (header ∥ associated-data ∥ ciphertext)).

Encryption brings cryptographic structure: **authenticated encryption (AEAD)** $(\mathit{Enc}_k(N, A, M)\to C\|T)$ provides confidentiality + integrity, but correctness requires **unique nonces** $N$ per key (catastrophic on reuse for GCM/CTR), which on a *replayed/recovered* log means nonce derivation must be deterministic in LSN yet never repeat across crashes — a subtle invariant. **Forward security** (a compromise at time $t$ does not expose records before $t$) maps to evolving-key / hash-chain schemes; **tamper-evident append-only** logs map to **Merkle/hash chains** and history trees (Crosby & Wallach, USENIX Security 2009). Information-theoretically, compression ratio is bounded by the log's empirical entropy $H$; reverse/random access over compressed data costs an index (a space-time trade-off, cf. succinct/compressed indexes).

## 3. State of the Art (SOTA)
- **Systems-SOTA:** Production engines compress WAL/redo (Oracle redo compression, SQL Server backup/log compression, MySQL binlog `binlog_transaction_compression` with zstd, PostgreSQL WAL compression of full-page images). **Transparent Data Encryption (TDE)** encrypts data and log files (Oracle, SQL Server, MySQL keyring, PostgreSQL via patches/forks). Block-based framing (fixed compression units with per-block checksums/CRC32C) is the standard reconciliation of compression with recoverability.
- **Theory/security-SOTA:** **AEAD** (GCM, ChaCha20-Poly1305), **forward-secure logging** (Bellare-Yee; Schneier-Kelsey secure audit logs, 1999), and **tamper-evident history trees** (Crosby-Wallach 2009) are the canonical primitives. A *unified* treatment giving recovery-correctness + crash-atomicity + AEAD integrity + forward security with proven bounds is **open**.

## 4. Upper Bound
Block-framed compression with per-block CRC/AEAD tags makes recovery cost $O(\text{block size})$ granularity overhead and recovers the longest valid block-prefix after a crash; compression saves I/O proportional to ratio $\rho$, lowering log-bandwidth-bound recovery time by $\approx \rho$. AEAD adds a constant per-block tag (e.g. 16 bytes) and one MAC verification per block — $O(1)$ overhead per frame, parallelizable. Reverse scan / random access is supported with a sparse LSN→block-offset index at $O(\text{index})$ extra space. Tamper-evidence via a hash chain costs one hash per record and gives $O(\log n)$ membership/consistency proofs with a history tree (Crosby-Wallach).

## 5. Lower Bound
- **Information-theoretic:** no log can be compressed below its entropy $H$; random/reverse access over a stream compressed to near $H$ requires $\Omega(1)$ extra index bits per access point (space-time trade-off from compressed-indexing lower bounds). 
- **Crash-atomicity:** with block coupling, the recoverable unit is the block, so a torn block loses up to one block of records — an unavoidable granularity floor unless records are framed independently (sacrificing compression ratio).
- **Security:** authenticity requires a MAC/tag of $\Omega(\kappa)$ bits per authenticated unit for $\kappa$-bit security (a cryptographic lower bound); forward security requires key evolution costing $\Omega(1)$ per epoch and *cannot* be retrofitted to already-leaked keys. Detecting truncation/rollback (an adversary chopping the log tail) is **impossible** without an external/anchored commitment — a fundamental impossibility absent a trusted ordering anchor.

## 6. The Gap
Each ingredient is individually understood, but their **composition under crash recovery** is not. Open questions: deterministic, never-repeating nonce derivation that survives arbitrary crash/replay sequences without weakening AEAD; reconciling high compression ratio (large blocks) with fine crash-atomicity and cheap reverse scan; combining forward-secure tamper-evidence with the performance budget of the commit path; and defending log **truncation/rollback** attacks without a trusted external anchor. No system offers a *proven* end-to-end guarantee (recoverable ∧ crash-atomic ∧ confidential ∧ tamper-evident ∧ forward-secure) with stated bounds — hence **open**.

## 7. Current Research (as of June 2026)
- **Confidential computing / TEE-backed logs** (SGX/SEV/TDX, AWS Nitro) to anchor ordering and defend rollback/truncation, and to keep keys out of the storage layer *(frontier — verify)*.
- Learned/columnar and dictionary compression of structured log records for higher ratios while keeping per-record decodability *(frontier — verify)*.
- Verifiable/auditable logs (transparency-log and history-tree techniques) applied to DB redo for regulatory tamper-evidence *(frontier — verify)*.
- Formal crash-consistency proofs that *include* the crypto layer (nonce uniqueness across crashes, AEAD integrity under truncation).

## 8. Future Work
- A unified formal model and proof: recoverable ∧ crash-atomic ∧ AEAD-authenticated ∧ forward-secure, with explicit space/time/security bounds.
- Crash-safe deterministic nonce/IV management proven across arbitrary crash-replay schedules.
- Optimal block-size policy trading compression ratio vs. crash-atomicity granularity vs. reverse-scan cost.
- Anchored, low-overhead defenses against log truncation/rollback (TEE or external transparency anchor).

## 9. Key References
- **[Foundational]** Mohan, C. et al. *ARIES: A Transaction Recovery Method ... Using Write-Ahead Logging.* ACM TODS, 1992. — [DOI](https://doi.org/10.1145/128765.128770)
- **[Foundational]** Schneier, B. & Kelsey, J. *Secure Audit Logs to Support Computer Forensics.* ACM TISSEC, 1999. — [DOI](https://doi.org/10.1145/317087.317089)
- **[Foundational]** Bellare, M. & Yee, B. *Forward-Security in Private-Key Cryptography.* CT-RSA, 2003. — [DOI](https://doi.org/10.1007/3-540-36563-X_1)
- **[SOTA]** Crosby, S. A. & Wallach, D. S. *Efficient Data Structures for Tamper-Evident Logging.* USENIX Security, 2009. — [USENIX](https://www.usenix.org/conference/usenixsecurity09/technical-sessions/presentation/efficient-data-structures-tamper-evident)
- **[Foundational]** Rogaway, P. *Authenticated-Encryption with Associated-Data (AEAD).* ACM CCS, 2002. — [DOI](https://doi.org/10.1145/586110.586125)
- **[Survey]** Dworkin, M. / NIST SP 800-38D. *Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC.* NIST, 2007. — [DOI](https://doi.org/10.6028/NIST.SP.800-38D)

## 10. Worked Example

Consider a compressed-and-encrypted WAL written as self-delimiting AEAD frames. Each frame holds a block of records and is stored as
$$F_j = \langle \text{len},\ N_j,\ C_j,\ T_j \rangle,\quad (C_j \| T_j) = \mathit{Enc}_k(N_j,\ A_j,\ \text{zstd}(records_j)),$$
where $A_j = \text{LSN-of-block}\,\|\,j$ is associated data and $T_j$ is a 16-byte tag.

Say block $F_5$ compresses 40 records ($8\,\text{KB} \to 2\,\text{KB}$, ratio $\rho = 0.25$). The crash happens mid-write of $F_6$, leaving a torn frame.

- **Recovery prefix:** scan $F_1\dots F_5$, verifying each tag $T_j$. $F_6$'s tag fails (or `len` overruns the file), so recovery stops; the valid prefix is $F_1\dots F_5$. The whole block $F_6$ is lost — the **block-granularity atomicity floor**: you cannot recover record 41 without 42–60 in the same compression unit.
- **Nonce safety:** $N_j = \text{LSN}_j$ is derived deterministically, so re-writing $F_6$ after restart reuses no nonce from $F_1\dots F_5$ — preserving GCM security.
- **Truncation attack:** an adversary deleting $F_5$ is **undetectable** without an external anchor (e.g. a TEE-sealed high-water LSN), since $F_1\dots F_4$ is itself a valid prefix — the fundamental rollback impossibility.

---
*Part of the [DBMS Research catalog](../../README.md).*
