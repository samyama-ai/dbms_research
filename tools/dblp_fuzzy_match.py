#!/usr/bin/env python3
"""Second pass over the DBLP dump for references exact-title matching missed.

The catalogue routinely cites a paper by a shortened title -- "ARIES" for
"ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and
Partial Rollbacks Using Write-Ahead Logging", "Morsel-Driven Parallelism" for
the full SIGMOD'14 title. Exact matching reports all of those as papers that do
not exist, which is false in every case checked by hand. This pass scores the
cited title against DBLP titles that share a distinctive token and keeps the
best containment match, so only titles with no plausible DBLP record at all are
reported as unverified.

  python3 tools/dblp_fuzzy_match.py --titles dblp_titles.json \
      --dump <path>/dblp-<date>.xml.gz --out dblp_fuzzy.json
"""
import argparse, gzip, html, json, re, sys, time
from collections import defaultdict

REC_TYPES = ('article', 'inproceedings', 'incollection', 'book',
             'phdthesis', 'mastersthesis', 'proceedings')
REC_RE = re.compile(r'<(%s)\b[^>]*>(.*?)</\1>' % '|'.join(REC_TYPES), re.S)
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.S)
YEAR_RE = re.compile(r'<year[^>]*>(\d{4})</year>')
KEY_RE = re.compile(r'key="([^"]+)"')
TAG_RE = re.compile(r'<[^>]+>')

STOP = {'a', 'an', 'the', 'of', 'for', 'and', 'on', 'in', 'to', 'with', 'via',
        'is', 'are', 'from', 'by', 'at', 'as', 'using', 'towards', 'toward'}


def toks(t):
    t = html.unescape(t)
    t = TAG_RE.sub('', t).lower()
    t = re.sub(r'[^a-z0-9]+', ' ', t)
    return [w for w in t.split() if w not in STOP and len(w) > 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--titles', required=True, help='dblp_titles.json')
    ap.add_argument('--dump', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--min-score', type=float, default=0.70)
    args = ap.parse_args()

    unmatched = json.load(open(args.titles, encoding='utf-8'))['unmatched']
    # one entry per distinct cited title; several files may cite the same paper
    by_title = {}
    for u in unmatched:
        by_title.setdefault(u['title'], []).append(u['file'])
    titles = sorted(by_title)
    tsets = [set(toks(t)) for t in titles]
    print(f'{len(unmatched)} unmatched references, {len(titles)} distinct titles',
          file=sys.stderr)

    # index only distinctive tokens: a token shared by many of our titles ("data",
    # "query") would match most of DBLP and make the pass quadratic for no signal
    df = defaultdict(int)
    for s in tsets:
        for w in s:
            df[w] += 1
    index = defaultdict(list)
    for i, s in enumerate(tsets):
        for w in s:
            if df[w] <= 8:
                index[w].append(i)
    print(f'{len(index)} distinctive tokens indexed', file=sys.stderr)

    best = {}          # title idx -> (score, record)
    n_rec = 0
    t0 = time.time()
    buf = ''
    CHUNK = 1 << 22
    with gzip.open(args.dump, 'rt', encoding='utf-8', errors='replace') as fh:
        while True:
            chunk = fh.read(CHUNK)
            if not chunk:
                break
            buf += chunk
            last = 0
            for m in REC_RE.finditer(buf):
                last = m.end()
                n_rec += 1
                body = m.group(2)
                tm = TITLE_RE.search(body)
                if not tm:
                    continue
                dt = toks(tm.group(1))
                if not dt:
                    continue
                dset = set(dt)
                cands = set()
                for w in dset:
                    hit = index.get(w)
                    if hit:
                        cands.update(hit)
                if not cands:
                    continue
                for i in cands:
                    cs = tsets[i]
                    inter = len(cs & dset)
                    score = inter / min(len(cs), len(dset))
                    if score >= args.min_score and score > best.get(i, (0,))[0]:
                        ym = YEAR_RE.search(body)
                        km = KEY_RE.search(m.group(0))
                        best[i] = (score, {
                            'dblp_title': ' '.join(
                                TAG_RE.sub('', html.unescape(tm.group(1))).split()),
                            'key': km.group(1) if km else '',
                            'year': int(ym.group(1)) if ym else None,
                        })
            buf = buf[last:]

    print(f'done: {n_rec} records, {len(best)}/{len(titles)} titles matched '
          f'fuzzily, {time.time()-t0:.0f}s', file=sys.stderr)

    out = {'matched': {}, 'unmatched': []}
    for i, t in enumerate(titles):
        if i in best:
            score, rec = best[i]
            out['matched'][t] = {'score': round(score, 3), **rec,
                                 'files': by_title[t]}
        else:
            out['unmatched'].append({'title': t, 'files': by_title[t]})
    json.dump(out, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'still unverified: {len(out["unmatched"])} titles', file=sys.stderr)


if __name__ == '__main__':
    main()
