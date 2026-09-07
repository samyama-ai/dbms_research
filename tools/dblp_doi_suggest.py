#!/usr/bin/env python3
"""For references whose identifier resolves to a different paper, recover the
identifier the cited paper actually has.

Flagging a wrong DOI is only half the job -- the fix needs the right one. DBLP
records each paper's own DOI in its <ee> element, so matching the cited title
against DBLP and reading back the <ee> turns "this DOI is wrong" into "this DOI
should be X".

  python3 tools/dblp_doi_suggest.py --bad bad_ids.json \
      --dump <path>/dblp-<date>.xml.gz --out doi_suggest.json
"""
import argparse, gzip, html, json, re, sys, time
from collections import defaultdict

REC_TYPES = ('article', 'inproceedings', 'incollection', 'book', 'phdthesis')
REC_RE = re.compile(r'<(%s)\b[^>]*>(.*?)</\1>' % '|'.join(REC_TYPES), re.S)
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.S)
YEAR_RE = re.compile(r'<year[^>]*>(\d{4})</year>')
EE_RE = re.compile(r'<ee[^>]*>(.*?)</ee>', re.S)
KEY_RE = re.compile(r'key="([^"]+)"')
TAG_RE = re.compile(r'<[^>]+>')
DOI_RE = re.compile(r'doi\.org/(10\.[^\s<]+)')

STOP = {'a', 'an', 'the', 'of', 'for', 'and', 'on', 'in', 'to', 'with', 'via',
        'is', 'are', 'from', 'by', 'at', 'as', 'using'}


def toks(t):
    t = TAG_RE.sub('', html.unescape(t)).lower()
    return [w for w in re.sub(r'[^a-z0-9]+', ' ', t).split()
            if w not in STOP and len(w) > 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bad', required=True)
    ap.add_argument('--dump', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--min-score', type=float, default=0.6)
    args = ap.parse_args()

    bad = json.load(open(args.bad, encoding='utf-8'))
    titles, meta = [], []
    for b in bad:
        titles.append(b['title'])
        meta.append(b)
    tsets = [set(toks(t)) for t in titles]

    df = defaultdict(int)
    for s in tsets:
        for w in s:
            df[w] += 1
    index = defaultdict(list)
    for i, s in enumerate(tsets):
        for w in s:
            if df[w] <= 8:
                index[w].append(i)
    print(f'{len(titles)} flagged references, {len(index)} distinctive tokens',
          file=sys.stderr)

    best = {}
    t0 = time.time()
    buf = ''
    with gzip.open(args.dump, 'rt', encoding='utf-8', errors='replace') as fh:
        while True:
            chunk = fh.read(1 << 22)
            if not chunk:
                break
            buf += chunk
            last = 0
            for m in REC_RE.finditer(buf):
                last = m.end()
                body = m.group(2)
                tm = TITLE_RE.search(body)
                if not tm:
                    continue
                dset = set(toks(tm.group(1)))
                if not dset:
                    continue
                cands = set()
                for w in dset:
                    h = index.get(w)
                    if h:
                        cands.update(h)
                if len(dset) < 3:
                    # Encyclopedia of Database Systems has thousands of one-word
                    # entries ("Adaptive.", "Index.", "Core."). Scored by
                    # containment against the shorter title they match everything.
                    continue
                for i in cands:
                    cs = tsets[i]
                    # symmetric: a short DBLP title must not win by being short
                    score = len(cs & dset) / max(len(cs), len(dset))
                    if score >= args.min_score and score > best.get(i, (0,))[0]:
                        ees = [html.unescape(TAG_RE.sub('', e)).strip()
                               for e in EE_RE.findall(body)]
                        dois = [d.group(1) for e in ees
                                if (d := DOI_RE.search(e))]
                        ym = YEAR_RE.search(body)
                        km = KEY_RE.search(m.group(0))
                        best[i] = (score, {
                            'dblp_title': ' '.join(
                                TAG_RE.sub('', html.unescape(tm.group(1))).split()),
                            'dblp_key': km.group(1) if km else '',
                            'dblp_year': int(ym.group(1)) if ym else None,
                            'dblp_doi': dois[0] if dois else None,
                            'dblp_ee': ees[:3],
                        })
            buf = buf[last:]

    out = []
    for i, b in enumerate(meta):
        rec = {'file': b['file'], 'title': b['title'],
               'cited_id': b.get('id'), 'cited_kind': b.get('kind'),
               'resolved_to': b.get('resolved'), 'verdict': b.get('verdict')}
        if i in best:
            rec['suggest_score'] = round(best[i][0], 3)
            rec.update(best[i][1])
        out.append(rec)
    json.dump(out, open(args.out, 'w', encoding='utf-8'), ensure_ascii=False,
              indent=1)
    n = sum(1 for r in out if r.get('dblp_doi'))
    print(f'done: {n}/{len(out)} flagged references got a suggested DOI, '
          f'{time.time()-t0:.0f}s', file=sys.stderr)


if __name__ == '__main__':
    main()
