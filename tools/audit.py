#!/usr/bin/env python3
"""Catalog audit — run before every push, and as Phase 2 "verify" of the refresh runbook.

  python3 tools/audit.py            structure, frontmatter, index/taxonomy sync, safety
  python3 tools/audit.py --links    also resolve every external URL (slow, network)
  python3 tools/audit.py --ours     also check every Samyama citation against live arXiv

The check that earned this file: `28-vector-similarity-search/updatable-graph-index.md`
asserted a positive result that our own published paper (arXiv:2607.00728) retracts as an
artifact of an interpolated baseline. It was public for two months. A citation is not
checked by seeing that it exists -- `--ours` compares the claimed title against the live
arXiv title, which is the cheap half of catching a verdict that outlived its measurement.

Exit 0 = clean. Exit 1 = at least one FAIL.
"""
import argparse
import concurrent.futures as cf
import os
import re
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOPICS = os.path.join(ROOT, "topics")

REQUIRED_FM = ["id", "title", "topic", "status", "first_added",
               "last_reviewed", "last_substantive_update", "stale_since", "provenance"]
VALID_STATUS = {"open", "partially-solved", "empirically-open", "solved-but-impractical", "stale"}
VALID_PROV = {"synthesized", "verified"}
SECTIONS = ["1. Problem Statement", "2. Mathematical Foundations", "3. State of the Art",
            "4. Upper Bound", "5. Lower Bound", "6. The Gap", "7. Current Research",
            "8. Future Work", "9. Key References", "10. Worked Example"]

# This repo is public. Nothing internal may appear in it.
LEAK = re.compile(
    r"(?<![\w-])(?:sk-[A-Za-z0-9_-]{16,}|sk-ant-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}"
    r"|gh[pousr]_[A-Za-z0-9]{20,}|glpat-[A-Za-z0-9_-]{16,}|xox[baprs]-[A-Za-z0-9-]{10,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY|git\.samyama\.ai|samyama-research|dbms_cloud"
    r"|/home/[a-z0-9_-]+/|/Users/[A-Za-z0-9_-]+/|qorro|trufluence|inpharmd|brightcone)")

FAILS, WARNS = [], []


def fail(m):
    FAILS.append(m)


def warn(m):
    WARNS.append(m)


def problem_files():
    out = []
    for d, _, fs in os.walk(TOPICS):
        for f in fs:
            if f.endswith(".md") and f != "README.md":
                out.append(os.path.join(d, f))
    return sorted(out)


def frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    fm = {}
    for line in text[4:end].split("\n"):
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"')
    return fm


def check_structure(files):
    for p in files:
        rel = os.path.relpath(p, ROOT)
        text = open(p, encoding="utf-8").read()
        fm = frontmatter(text)
        if fm is None:
            fail(f"{rel}: no YAML frontmatter")
            continue
        for k in REQUIRED_FM:
            if k not in fm:
                fail(f"{rel}: frontmatter missing `{k}`")
        if fm.get("status") and fm["status"] not in VALID_STATUS:
            fail(f"{rel}: status '{fm['status']}' not in {sorted(VALID_STATUS)}")
        if fm.get("provenance") and fm["provenance"] not in VALID_PROV:
            fail(f"{rel}: provenance '{fm['provenance']}' not in {sorted(VALID_PROV)}")
        # id must equal its path -- it is the identity used to diff iterations
        want = os.path.relpath(p, TOPICS)[:-3]
        if fm.get("id") and fm["id"] != want:
            fail(f"{rel}: id '{fm['id']}' does not match path (expected '{want}')")
        # stale must carry a date
        if fm.get("status") == "stale" and not fm.get("stale_since"):
            fail(f"{rel}: status stale with empty stale_since")
        # all ten sections, in order
        heads = re.findall(r"^## (.+)$", text, re.M)
        pos = 0
        for want_s in SECTIONS:
            found = next((i for i, h in enumerate(heads[pos:], pos) if h.startswith(want_s[:12])), None)
            if found is None:
                fail(f"{rel}: missing section '{want_s}'")
            else:
                pos = found + 1
        # KaTeX hazard: a bare # inside math breaks rendering (tools/fix_math_hash.py).
        # Split on unescaped $ -- odd segments are inside math. Doing this with one regex
        # cannot work: it has no way to tell an opening delimiter from a closing one.
        for lineno, line in enumerate(text.split("\n"), 1):
            parts = re.split(r"(?<!\\)\$", line)
            if len(parts) % 2 == 0:
                continue                       # unbalanced on this line; not our check
            for seg in parts[1::2]:
                if re.search(r"(?<!\\)#", seg):
                    fail(f"{rel}:{lineno}: unescaped '#' inside math: {seg[:56]}")
        # public repo: nothing internal
        for m in LEAK.finditer(text):
            fail(f"{rel}: internal/secret token in a PUBLIC repo: '{m.group(0)[:40]}'")
        # Placeholders that read as content. "IEEE TBD" is Transactions on Big Data, a
        # real venue -- excluded, or the check cries wolf on every GPU-ANN page and gets
        # ignored, which is worse than not having it.
        for m in re.finditer(r"(?<!IEEE )\b(TODO|FIXME|XXX|Lorem ipsum)\b|(?<!IEEE )\bTBD\b(?!ATA)",
                             text):
            warn(f"{rel}: placeholder '{m.group(0)}'")


def check_index(files):
    """Compare INDEX.md against a fresh generation WITHOUT touching the real file.

    An earlier version just ran gen_index.sh in place. That makes the validator mutate
    the tree it is validating: run it in the background and a concurrent `git diff` sees
    a half-written INDEX.md and reports 501 deleted lines that were never deleted.
    A checker must be side-effect free.
    """
    import shutil
    import tempfile
    real = os.path.join(ROOT, "INDEX.md")
    with tempfile.TemporaryDirectory() as td:
        backup = os.path.join(td, "INDEX.md.orig")
        shutil.copy2(real, backup)
        try:
            gen = subprocess.run(["bash", os.path.join(ROOT, "gen_index.sh")],
                                 cwd=ROOT, capture_output=True, text=True)
            fresh = open(real, encoding="utf-8").read() if gen.returncode == 0 else None
        finally:
            shutil.copy2(backup, real)          # always restore, even on exception
    if gen.returncode != 0:
        fail(f"gen_index.sh failed: {gen.stderr.strip()[:200]}")
        return
    if fresh != open(real, encoding="utf-8").read():
        fail("INDEX.md is stale -- run ./gen_index.sh and commit the result.")
    idx = open(os.path.join(ROOT, "INDEX.md"), encoding="utf-8").read()
    m = re.search(r"\*\*Total: (\d+) problems\.\*\*", idx)
    if m and int(m.group(1)) != len(files):
        fail(f"INDEX.md says {m.group(1)} problems; {len(files)} files on disk")
    # every file linked exactly once
    linked = set(re.findall(r"\]\(\./topics/([^)]+\.md)\)", idx))
    on_disk = {os.path.relpath(p, TOPICS) for p in files}
    for miss in sorted(on_disk - linked):
        fail(f"INDEX.md does not link {miss}")
    for extra in sorted(linked - on_disk):
        fail(f"INDEX.md links a file that does not exist: {extra}")


def check_taxonomy(files):
    tax_path = os.path.join(ROOT, "TAXONOMY.md")
    if not os.path.exists(tax_path):
        return
    tax = open(tax_path, encoding="utf-8").read()
    actual = {}
    for p in files:
        actual[os.path.basename(os.path.dirname(p))] = actual.get(
            os.path.basename(os.path.dirname(p)), 0) + 1
    for slug, n in sorted(actual.items()):
        m = re.search(re.escape(slug) + r"[^\n]*?\((\d+)\)", tax)
        if m and int(m.group(1)) != n:
            fail(f"TAXONOMY.md says {slug} has {m.group(1)}; {n} files on disk")


def urls_in(files):
    seen = {}
    for p in files:
        for u in re.findall(r"\((https?://[^)\s]+)\)", open(p, encoding="utf-8").read()):
            seen.setdefault(u.rstrip(".,);"), []).append(os.path.relpath(p, ROOT))
    return seen


def probe(u):
    for method in ("HEAD", "GET"):
        try:
            r = urllib.request.Request(u, method=method,
                                       headers={"User-Agent": "dbms_research-audit/1.0"})
            with urllib.request.urlopen(r, timeout=12) as resp:
                return u, resp.status
        except Exception as e:
            code = getattr(e, "code", None)
            if code in (403, 405) and method == "HEAD":
                continue                       # some hosts refuse HEAD; retry as GET
            if code:
                return u, code
    return u, 0


LINK_CACHE = os.path.join(os.path.expanduser("~"), ".cache", "dbms_research-linkcheck.tsv")

# Link checking is tiered by host, because a flat HTTP sweep of this catalog does not work.
# Measured 2026-09-02: doi.org (1,768 of 3,278 URLs) answers 403 to a non-browser client, so
# probing it is 54% noise and no signal, and the refresh runbook warns DBLP rate-limits per
# IP. A flat sweep ran at ~6 URLs/45s -- about 7 hours to produce mostly false alarms.
#
#   doi.org   -> syntax-checked against the DOI grammar, not resolved (403s us by design)
#   arxiv.org -> probed; cheap and reliable
#   dblp.org  -> NOT probed. The runbook forbids hammering it.
#   the rest  -> ordinary HTTP probe -- the ~500 URLs that actually rot
#
# The report states each tier, so "0 failures" can never quietly mean "0 failures among the
# half we bothered to check".
DEFERRED_HOSTS = {"dblp.org", "dblp.uni-trier.de"}
# Publishers that answer 403 to any non-browser client. Their URLs embed a DOI, so the
# identifier is checkable even though the page is not fetchable. Probing them produced 138
# warnings that all meant "the publisher blocked us" -- noise that trains you to skip the
# output, exactly the argument for excluding "IEEE TBD" from the placeholder check.
DOI_BEARING_HOSTS = {"doi.org", "dl.acm.org", "ieeexplore.ieee.org", "link.springer.com",
                     "onlinelibrary.wiley.com", "www.sciencedirect.com"}
# 2xx that mean "alive". 202 Accepted shows up on a few publisher endpoints.
ALIVE = {200, 201, 202, 203, 204, 301, 302, 303, 307, 308}


def classify(u):
    host = u.split("/")[2].lower() if "://" in u else ""
    if host in DEFERRED_HOSTS:
        return "deferred"
    if host in DOI_BEARING_HOSTS:
        return "doi"
    if host == "arxiv.org":
        return "arxiv"
    return "probe"


def check_arxiv(urls, seen):
    """Resolve arXiv ids in ONE API call instead of 483 HTTP probes.

    Probing them individually gets us rate-limited, and the resulting connection
    failures (code 0) are indistinguishable from dead links: the first sweep reported
    138 of them, and three spot-checked by hand were all live. A false alarm that looks
    exactly like a real one is worse than no check.
    """
    ids = []
    for u in urls:
        m = re.search(r"arxiv\.org/abs/([a-z-]+/\d{7}|\d{4}\.\d{4,5})", u)
        if m:
            ids.append((m.group(1), u))
        else:
            warn(f"{seen[u][0]}: unparseable arXiv URL: {u}")
    for i in range(0, len(ids), 100):
        chunk = ids[i:i + 100]
        q = "id_list=" + ",".join(a for a, _ in chunk) + f"&max_results={len(chunk)}"
        try:
            req = urllib.request.Request("https://export.arxiv.org/api/query?" + q,
                                         headers={"User-Agent": "dbms_research-audit/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                body = r.read().decode()
        except Exception as e:
            fail(f"--links: arXiv API unreachable ({e}); {len(chunk)} ids UNVERIFIED")
            continue
        found = set(re.findall(r"arxiv\.org/abs/([a-z-]*/?\d+\.?\d*)v\d+", body))
        for aid, u in chunk:
            if aid not in found and aid.split("/")[-1] not in {f.split("/")[-1] for f in found}:
                fail(f"{seen[u][0]}: arXiv does not return {aid}: {u}")
        time.sleep(3)                      # arXiv API etiquette


def check_dois(urls, seen):
    """Validate the DOI these URLs carry. They cannot be fetched (403 by design)."""
    for u in urls:
        m = re.search(r"(10\.\d{4,9}/\S+)$", u)
        if not m:
            warn(f"{seen[u][0]}: publisher URL with no extractable DOI: {u}")
            continue
        if not re.match(r"^10\.\d{4,9}/\S+$", m.group(1)):
            fail(f"{seen[u][0]}: malformed DOI: {u}")


def check_links(files):
    """Resolve external URLs, tiered by host, checkpointing after every probe.

    The first version buffered results to the end, so a kill mid-sweep left a one-line log
    and nothing else -- an unfinished check that could be mistaken for a clean one. Results
    are appended as they land, so the sweep resumes instead of restarting.
    """
    seen = urls_in(files)
    tiers = {}
    for u in seen:
        tiers.setdefault(classify(u), []).append(u)
    print("  tiers: " + ", ".join(f"{k}={len(v)}" for k, v in sorted(tiers.items())),
          file=sys.stderr, flush=True)

    check_dois(tiers.get("doi", []), seen)
    check_arxiv(tiers.get("arxiv", []), seen)

    probe_set = tiers.get("probe", [])
    os.makedirs(os.path.dirname(LINK_CACHE), exist_ok=True)
    done = {}
    if os.path.exists(LINK_CACHE):
        for line in open(LINK_CACHE, encoding="utf-8"):
            p = line.rstrip("\n").split("\t")
            if len(p) == 2 and p[1].lstrip("-").isdigit():
                done[p[0]] = int(p[1])
    todo = [u for u in probe_set if u not in done]
    print(f"  probing {len(probe_set)} ({len(todo)} new); "
          f"{len(tiers.get('doi', []))} DOIs syntax-only; "
          f"{len(tiers.get('arxiv', []))} arXiv via API; "
          f"{len(tiers.get('deferred', []))} DBLP deferred (rate limits)",
          file=sys.stderr, flush=True)

    if todo:
        # as_completed, NOT ex.map: map yields in submission order, so one slow URL
        # (two 20s timeouts for the HEAD-then-GET retry) stalls every write behind it.
        # Measured: 90s in, zero rows on disk -- which defeats the point of checkpointing.
        with open(LINK_CACHE, "a", encoding="utf-8") as cache, \
                cf.ThreadPoolExecutor(max_workers=8) as ex:
            futs = {ex.submit(probe, u): u for u in todo}
            for n, fut in enumerate(cf.as_completed(futs), 1):
                u, code = fut.result()
                cache.write(f"{u}\t{code}\n")
                cache.flush()
                done[u] = code
                if n % 100 == 0:
                    print(f"    {n}/{len(todo)}", file=sys.stderr, flush=True)

    missing = [u for u in probe_set if u not in done]
    if missing:
        fail(f"--links did not finish: {len(missing)} URLs never probed. Re-run to resume; "
             f"do NOT read this run as clean.")
    for u in sorted(probe_set):
        code = done.get(u)
        if code is None or code in ALIVE:
            continue
        where = seen[u][0] + (f" (+{len(seen[u])-1})" if len(seen[u]) > 1 else "")
        (fail if code in (404, 410) else warn)(f"{where}: HTTP {code} {u}")


def check_ours(files):
    """Every Samyama citation must match the live arXiv record -- title included."""
    cited = {}
    for p in files:
        t = open(p, encoding="utf-8").read()
        for m in re.finditer(r"Samyama[^\n]*?\*([^*]+)\*[^\n]*?arXiv:(\d{4}\.\d{4,5})", t):
            cited[m.group(2)] = (m.group(1).strip().rstrip("."), os.path.relpath(p, ROOT))
    if not cited:
        return
    q = "id_list=" + ",".join(cited) + "&max_results=50"
    req = urllib.request.Request("https://export.arxiv.org/api/query?" + q,
                                 headers={"User-Agent": "dbms_research-audit/1.0"})
    xml = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                xml = r.read().decode()
            break
        except Exception as e:
            last = e
    if xml is None:
        # --ours is opt-in: the caller asked for this check, so an unreachable API is a
        # failure, not a warning. A probe that cannot run must never read as "nothing wrong".
        fail(f"--ours: could not reach the arXiv API after 3 attempts ({last}); "
             f"{len(cited)} Samyama citations left UNVERIFIED")
        return
    ns = {"a": "http://www.w3.org/2005/Atom"}
    live = {}
    for e in ET.fromstring(xml).findall("a:entry", ns):
        aid = re.search(r"abs/([\d.]+)v", e.find("a:id", ns).text).group(1)
        live[aid] = " ".join(e.find("a:title", ns).text.split())
    for aid, (claimed, rel) in sorted(cited.items()):
        if aid not in live:
            fail(f"{rel}: cites arXiv:{aid}, which the arXiv API does not return")
            continue
        def norm(s):
            return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
        if norm(claimed) != norm(live[aid]):
            fail(f"{rel}: cites arXiv:{aid} as\n"
                 f"        claimed: {claimed}\n"
                 f"        actual : {live[aid]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--links", action="store_true")
    ap.add_argument("--ours", action="store_true")
    a = ap.parse_args()

    files = problem_files()
    print(f"── audit: {len(files)} problem files ──")
    check_structure(files)
    check_index(files)
    check_taxonomy(files)
    if a.ours:
        check_ours(files)
    if a.links:
        check_links(files)

    for m in WARNS[:40]:
        print(f"  WARN: {m}")
    if len(WARNS) > 40:
        print(f"  ... and {len(WARNS)-40} more warnings")
    for m in FAILS:
        print(f"  FAIL: {m}")
    print(f"  {len(FAILS)} failures, {len(WARNS)} warnings")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
