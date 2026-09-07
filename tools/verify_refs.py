#!/usr/bin/env python3
"""Verify catalogue references against the identifiers they cite.

Tier A (online): every DOI and arXiv id in a reference link is resolved and the
*resolved* title compared to the *cited* title. A live identifier pointing at a
different paper is the failure this catches; link-liveness alone would pass it.

Resumable: results append to a JSONL cache keyed by identifier, so a killed run
resumes without refetching. Never caches a non-200 as a result.
"""
import json, os, re, sys, time, html, argparse
import urllib.request, urllib.error, urllib.parse
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

UA = 'dbms_research-audit/1.0 (+https://github.com/samyama-ai/dbms_research)'


TAG_RE = re.compile(r'<[^>]+>')


def norm_title(t):
    # strip markup with '' not ' ': Crossref writes O<scp>rpheus</scp>DB,
    # and a space there splits one word into three that match nothing
    t = html.unescape(TAG_RE.sub('', t)).lower().replace('’', "'").replace('–', '-').replace('—', '-')
    t = re.sub(r'[^a-z0-9]+', ' ', t)
    return ' '.join(t.split())


STOP = {'a', 'an', 'the', 'of', 'for', 'and', 'on', 'in', 'to', 'with', 'via'}


def title_sim(a, b):
    """Containment, not Jaccard.

    Crossref returns ACM proceedings titles truncated at the subtitle ("Calvin"
    for "Calvin: Fast Distributed Transactions..."), so Jaccard scores a correct
    citation 0.125. Containment against the shorter title scores it 1.0 and still
    scores an unrelated paper 0.
    """
    # Crossref stores markup with newlines around it -- "O\n <scp>rpheus</scp>\n DB"
    # -- so stripping tags still leaves "o rpheus db" and no token matches. Compare
    # the punctuation-free squash first; a containment there is the same paper.
    sa = norm_title(a).replace(' ', '')
    sb = norm_title(b).replace(' ', '')
    if sa and sb and (sa in sb or sb in sa):
        return 1.0
    A = set(norm_title(a).split()) - STOP
    B = set(norm_title(b).split()) - STOP
    if not A or not B:
        return 0.0
    return len(A & B) / min(len(A), len(B))


def fetch(url, tries=4, backoff=5.0):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=40) as r:
                if r.status != 200:
                    raise urllib.error.HTTPError(url, r.status, 'non-200', None, None)
                return r.read()
        except Exception as e:  # throttles and timeouts must never be cached
            last = e
            time.sleep(backoff * (i + 1))
    raise last


def resolve_datacite(doi):
    body = fetch('https://api.datacite.org/dois/' + urllib.parse.quote(doi, safe=''))
    a = json.loads(body)['data']['attributes']
    titles = a.get('titles') or []
    return {'title': (titles[0].get('title') if titles else ''),
            'year': a.get('publicationYear'),
            'venue': (a.get('container') or {}).get('title', '') or '',
            'type': ((a.get('types') or {}).get('resourceTypeGeneral') or ''),
            'registry': 'datacite'}


def resolve_doi(doi):
    body = fetch('https://api.crossref.org/works/' + urllib.parse.quote(doi))
    msg = json.loads(body)['message']
    titles = msg.get('title') or []
    year = None
    for k in ('published-print', 'published-online', 'issued', 'created'):
        parts = (msg.get(k) or {}).get('date-parts') or []
        if parts and parts[0] and parts[0][0]:
            year = parts[0][0]
            break
    return {'title': titles[0] if titles else '', 'year': year,
            'venue': (msg.get('container-title') or [''])[0],
            'type': msg.get('type', '')}


ARXIV_NS = {'a': 'http://www.w3.org/2005/Atom'}


def resolve_arxiv_batch(ids):
    """arXiv's API takes up to 100 ids per query; one request per 100 beats 100."""
    q = ('https://export.arxiv.org/api/query?id_list=' + ','.join(ids)
         + '&max_results=' + str(len(ids)))
    root = ET.fromstring(fetch(q, tries=5, backoff=30.0))
    out = {}
    for e in root.findall('a:entry', ARXIV_NS):
        idu = e.find('a:id', ARXIV_NS).text
        m = re.search(r'abs/([^v]+)', idu)
        if not m:
            continue
        t = e.find('a:title', ARXIV_NS)
        pub = e.find('a:published', ARXIV_NS)
        out[m.group(1)] = {
            'title': ' '.join((t.text or '').split()),
            'year': int(pub.text[:4]) if pub is not None and pub.text else None,
            'venue': 'arXiv', 'type': 'preprint',
        }
    return out


def load_cache(path):
    cache = {}
    if os.path.exists(path):
        for line in open(path, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            cache[r['id']] = r
    return cache


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--refs', required=True, help='refs.jsonl from parse_refs.py')
    ap.add_argument('--cache', required=True, help='resolution cache (JSONL)')
    ap.add_argument('--kind', choices=['doi', 'arxiv'], required=True)
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--batch', type=int, default=25)
    ap.add_argument('--sleep', type=float, default=20.0)
    args = ap.parse_args()

    refs = [r for r in map(json.loads, open(args.refs, encoding='utf-8'))
            if not r['parse_error']]
    want = {}   # identifier -> set of cited titles
    for r in refs:
        for l in r['links']:
            u = l['url']
            if args.kind == 'doi':
                m = re.search(r'doi\.org/(10\.\S+)', u)
            else:
                m = re.search(r'arxiv\.org/abs/([0-9]{4}\.[0-9]{4,5}|[a-z-]+/[0-9]{7})', u)
            if m:
                want.setdefault(m.group(1).rstrip('.'), set()).add(r['title'])

    cache = load_cache(args.cache)
    todo = [i for i in sorted(want) if i not in cache]
    if args.limit:
        todo = todo[:args.limit]
    print(f'{len(want)} unique {args.kind} ids; {len(cache)} cached; {len(todo)} to fetch',
          file=sys.stderr)

    out = open(args.cache, 'a', encoding='utf-8')

    def emit(rec):
        out.write(json.dumps(rec, ensure_ascii=False) + '\n')
        out.flush()   # a killed sweep must keep what it already paid for

    if args.kind == 'doi':
        def work(i):
            try:
                return {'id': i, 'ok': True, **resolve_doi(i)}
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    try:            # not in Crossref -> try the other registry
                        return {'id': i, 'ok': True, **resolve_datacite(i)}
                    except urllib.error.HTTPError as e2:
                        if e2.code == 404:
                            return {'id': i, 'ok': False, 'error': 'not-found'}
                        return None
                    except Exception:
                        return None
                return None          # throttle/5xx: leave uncached, retry next run
            except Exception:
                return None
        # as_completed, never ex.map: map yields in submission order, so one slow
        # identifier stalls every write behind it and a killed sweep loses them
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futs = [ex.submit(work, i) for i in todo]
            for n, fut in enumerate(as_completed(futs), 1):
                rec = fut.result()
                if rec:
                    emit(rec)
                if n % 100 == 0:
                    print(f'  {n}/{len(todo)}', file=sys.stderr)
    else:
        for s in range(0, len(todo), args.batch):
            batch = todo[s:s + args.batch]
            try:
                got = resolve_arxiv_batch(batch)
            except Exception as e:
                print(f'  batch {s} failed: {e}', file=sys.stderr)
                continue
            for i in batch:
                if i in got:
                    emit({'id': i, 'ok': True, **got[i]})
                else:
                    emit({'id': i, 'ok': False, 'error': 'not-found'})
            print(f'  {min(s + args.batch, len(todo))}/{len(todo)}', file=sys.stderr)
            time.sleep(args.sleep)   # arXiv 429s well before its documented 3s floor
    out.close()


if __name__ == '__main__':
    main()
