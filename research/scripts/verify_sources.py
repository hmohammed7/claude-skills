"""Check that paper citations exist, using the free Crossref API.

Usage:
    python verify_sources.py citations.txt        # one citation per line
    python verify_sources.py --cite "Author (2015). Title. Journal."
    type citations.txt | python verify_sources.py -
    add --json for machine-readable output

Each citation gets one status:
    VERIFIED   Crossref has a record whose title, first author and year all match
    MISMATCH   a close record exists but the title, author or year differ
    NOT FOUND  no record comes close
    ERROR      Crossref couldn't be reached, so nothing was checked

Exit code: 0 all verified, 1 any MISMATCH / NOT FOUND / ERROR, 2 bad or empty input.
Optional: set CROSSREF_MAILTO to your email to use Crossref's faster "polite" pool.
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from difflib import SequenceMatcher

API = "https://api.crossref.org/works"
FIELDS = "DOI,title,subtitle,author,issued,published-print,published-online,container-title,short-container-title,volume,issue,page,publisher"
TIMEOUT = 30
PAUSE = 0.3  # seconds between requests, to stay polite

# Thresholds (0-1). Title must appear almost word for word in the citation.
TITLE_MATCH = 0.85      # at or above: the title matches
TITLE_CLOSE = 0.60      # between this and TITLE_MATCH: a near miss, reported as MISMATCH
EXPLAINED_MIN = 0.55    # share of citation words the record explains; below this a short
                        # title probably matched by coincidence

STOPWORDS = set("""a an and are as at by de der des du et al for from in into is la le of on or
the to vol volume no pp pages page doi org https http www journal proceedings proc""".split())

DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>]+)", re.I)
YEAR_RE = re.compile(r"\b(1[89]\d\d|20\d\d)\b")


def words(text):
    text = text.lower().replace("‐", "-").replace("–", "-")
    return re.findall(r"[a-z0-9À-ɏ]+", text)


def content_words(text):
    return [w for w in words(text) if len(w) > 1 and w not in STOPWORDS]


def fetch(url):
    """GET url and return parsed JSON, None for 404, raise RuntimeError otherwise."""
    agent = "research-skill-verify-sources/1.0"
    mailto = os.environ.get("CROSSREF_MAILTO")
    if mailto:
        agent += f" (mailto:{mailto})"
    req = urllib.request.Request(url, headers={"User-Agent": agent})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(int(e.headers.get("Retry-After") or 2 * (attempt + 1)))
                continue
            raise RuntimeError(f"Crossref returned HTTP {e.code}")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f"couldn't reach Crossref ({e})")
    raise RuntimeError("couldn't reach Crossref")


def record_year(rec):
    for key in ("issued", "published-print", "published-online"):
        parts = (rec.get(key) or {}).get("date-parts") or [[None]]
        if parts and parts[0] and parts[0][0]:
            return int(parts[0][0])
    return None


def record_title(rec):
    title = " ".join(rec.get("title") or [])
    sub = " ".join(rec.get("subtitle") or [])
    return f"{title}: {sub}" if sub and sub.lower() not in title.lower() else title


def first_author(rec):
    authors = rec.get("author") or []
    if not authors:
        return None
    a = authors[0]
    return a.get("family") or a.get("name")


def record_bag(rec):
    """All words the record can account for in a citation."""
    parts = [record_title(rec), rec.get("DOI", ""), rec.get("publisher", ""),
             str(rec.get("volume", "")), str(rec.get("issue", "")),
             (rec.get("page") or "").replace("-", " ")]
    parts += rec.get("container-title") or []
    parts += rec.get("short-container-title") or []
    for a in rec.get("author") or []:
        parts += [a.get("family", ""), a.get("given", ""), a.get("name", "")]
    for key in ("issued", "published-print", "published-online"):
        for dp in (rec.get(key) or {}).get("date-parts") or []:
            parts += [str(x) for x in dp if x]
    return set(content_words(" ".join(parts)))


def title_coverage(title, citation):
    """Share of the title's words found in the citation, in order (longest matching runs)."""
    t = words(title)
    c = words(citation)
    if not t:
        return 0.0
    blocks = SequenceMatcher(None, t, c, autojunk=False).get_matching_blocks()
    return sum(b.size for b in blocks) / len(t)


def assess(citation, rec):
    """Compare one Crossref record against a citation. Returns (status, score, notes)."""
    title = record_title(rec)
    cov = title_coverage(title, citation)
    cite_words = content_words(citation)
    bag = record_bag(rec)
    explained = sum(w in bag for w in cite_words) / len(cite_words) if cite_words else 0.0

    notes = []
    problems = []
    cite_years = {int(y) for y in YEAR_RE.findall(citation)}
    year = record_year(rec)
    if cite_years and year and not any(abs(y - year) <= 1 for y in cite_years):
        problems.append(f"year: citation says {sorted(cite_years)}, Crossref says {year}")
    author = first_author(rec)
    cite_low = " " + " ".join(words(citation)) + " "
    if author and f" {' '.join(words(author))} " not in cite_low:
        problems.append(f"first author: Crossref says {author}, not in citation")

    score = cov * 0.6 + explained * 0.4 - 0.1 * len(problems)

    if cov >= TITLE_MATCH and explained >= EXPLAINED_MIN:
        status = "MISMATCH" if problems else "VERIFIED"
    elif cov >= TITLE_MATCH:
        # title words are there but most of the citation isn't explained by this record:
        # likely a short, generic title that matched by chance
        status = "NOT FOUND"
        notes.append(f"title matches \"{title}\" (https://doi.org/{rec.get('DOI')}) but only "
                     f"{explained:.0%} of the citation fits that record")
    elif cov >= TITLE_CLOSE and len(problems) < 2:
        # near-miss title, backed up by a matching first author or year
        status = "MISMATCH"
        problems.insert(0, f"title only {cov:.0%} matches")
    else:
        status = "NOT FOUND"
    return status, score, problems + notes


def check(citation):
    result = {"citation": citation, "status": None, "doi": None, "title": None,
              "author": None, "year": None, "notes": []}
    try:
        candidates = []
        doi_match = DOI_RE.search(citation)
        if doi_match:
            doi = doi_match.group(1).rstrip(".,;)")
            data = fetch(f"{API}/{urllib.parse.quote(doi, safe='/')}")
            if data is None:
                result["notes"].append(f"DOI {doi} is not registered with Crossref")
            else:
                rec = data["message"]
                status, score, notes = assess(citation, rec)
                # a citation that is only a DOI has nothing else to compare against
                if not content_words(DOI_RE.sub("", citation)):
                    status, notes = "VERIFIED", ["DOI only: existence checked, details not compared"]
                candidates.append((score + 1, status, notes, rec))  # DOI hit beats a search hit
            time.sleep(PAUSE)
        if not candidates or candidates[0][1] != "VERIFIED":
            query = DOI_RE.sub("", citation)
            url = f"{API}?" + urllib.parse.urlencode(
                {"query.bibliographic": query, "rows": 10, "select": FIELDS})
            data = fetch(url)
            for rec in (data or {}).get("message", {}).get("items", []):
                status, score, notes = assess(citation, rec)
                candidates.append((score, status, notes, rec))
            time.sleep(PAUSE)
    except RuntimeError as e:
        result["status"] = "ERROR"
        result["notes"].append(str(e))
        return result

    if not candidates:
        result["status"] = "NOT FOUND"
        return result
    rank = {"VERIFIED": 2, "MISMATCH": 1, "NOT FOUND": 0}
    candidates.sort(key=lambda c: (rank[c[1]], c[0]), reverse=True)
    _, status, notes, rec = candidates[0]
    result["status"] = status
    result["notes"] += notes
    if status != "NOT FOUND":
        label = "matched" if status == "VERIFIED" else "closest"
        result["notes"].insert(0, label)
        result.update(doi=rec.get("DOI"), title=record_title(rec),
                      author=first_author(rec), year=record_year(rec))
    return result


def read_citations(args):
    lines = []
    for cite in args.cite or []:
        lines.append(cite)
    for path in args.files:
        if path == "-":
            lines += sys.stdin.read().splitlines()
        else:
            try:
                with open(path, encoding="utf-8-sig") as f:
                    lines += f.read().splitlines()
            except OSError as e:
                sys.exit(f"error: can't read {path}: {e}")
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Check paper citations exist, via Crossref.")
    p.add_argument("files", nargs="*", help="text files with one citation per line ('-' for stdin)")
    p.add_argument("--cite", action="append", help="a citation to check (repeatable)")
    p.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = p.parse_args()

    citations = read_citations(args)
    if not citations:
        print("error: no citations given (empty file or no --cite). Nothing was checked.",
              file=sys.stderr)
        sys.exit(2)

    results = [check(c) for c in citations]

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        for i, r in enumerate(results, 1):
            print(f"[{i}] {r['status']}: {r['citation']}")
            if r["title"]:
                print(f"    {r['notes'][0]}: {r['title']} - {r['author']} ({r['year']}) "
                      f"https://doi.org/{r['doi']}")
            for note in r["notes"][1 if r["title"] else 0:]:
                print(f"    note: {note}")
        counts = {s: sum(r["status"] == s for r in results)
                  for s in ("VERIFIED", "MISMATCH", "NOT FOUND", "ERROR")}
        print("\n" + ", ".join(f"{n} {s}" for s, n in counts.items() if n)
              + f" (of {len(results)})")

    sys.exit(0 if all(r["status"] == "VERIFIED" for r in results) else 1)


if __name__ == "__main__":
    main()
