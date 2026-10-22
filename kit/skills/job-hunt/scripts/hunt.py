#!/usr/bin/env python3
"""Pull fresh job postings for the user from the sources that need no login,
filter them for fit, drop anything already in the tracker or already seen,
and write a ranked shortlist for the job-hunt skill.

  hunt.py run [--days 2] [--sources linkedin,hn,boards,careerops,freehire] [--max-details 80]
  hunt.py seen <url> [<url> ...]     mark URLs as handled so they never come back

Writes hunts/<today>.json and hunts/<today>.md at the repo root. Reddit,
LinkedIn posts, YC Work at a Startup, Wellfound and the rest need a browser
or a login; the skill covers those (references/sources.md).
"""
import argparse
import csv
import datetime as dt
import html
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CFG = json.loads((Path(__file__).resolve().parents[1] / "references" / "search.json").read_text())
TRACKER = ROOT / "tracker" / "applications.csv"
HUNTS = ROOT / "hunts"
SEEN = HUNTS / "seen.txt"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/128 Safari/537.36"}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
YEARS_RE = re.compile(r"(\d{1,2})\s*(?:\+|plus)?\s*(?:-|–|to)?\s*(\d{1,2})?\s*\+?\s*(?:years|yrs)", re.I)


def get(url, as_json=False, tries=2):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
                body = r.read().decode("utf-8", "replace")
                return json.loads(body) if as_json else body
        except Exception as e:  # network or rate limit: back off once, then give up on this URL
            if i == tries - 1:
                print(f"  skip {url[:90]}: {e}", file=sys.stderr)
                return None
            time.sleep(3)


def text(s):
    s = re.sub(r"<br\s*/?>|</p>|<p>|</li>", "\n", s or "")
    return html.unescape(re.sub(r"<[^>]+>", " ", s))


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def min_years(desc):
    """Smallest 'N years' requirement in the text that looks like an experience ask."""
    found = []
    for m in YEARS_RE.finditer(desc or ""):
        ctx = desc[max(0, m.start() - 60): m.end() + 40].lower()
        if "experience" in ctx or "exp" in ctx:
            found.append(int(m.group(1)))
    return min(found) if found else None


def title_ok(title):
    t = f" {title.lower()} "
    if any(x in t for x in CFG["title_exclude"]):
        return False
    return any(x in t for x in CFG["title_include"])


FOREIGN = re.compile(r"\b(us|usa|u\.s\.|canada|uk|united kingdom|united states|europe|eu|emea|latam|north america|americas|germany|est hours|pst)\b", re.I)
JUNK_EMAIL = re.compile(r"^(privacy|legal|noreply|no-reply|donotreply|support|security|abuse|gdpr|dpo)@", re.I)


def location_ok(loc):
    l = (loc or "").lower()
    if not any(x in l for x in CFG["location_ok"]):
        return False
    # "Remote - Canada, UK" is not open to India unless India or worldwide is named too
    if FOREIGN.search(l) and not re.search(r"india|bengaluru|bangalore|worldwide|global|anywhere|apac", l):
        return False
    return True


# ---------- sources ----------

def from_linkedin(days, max_details):
    tpr = f"r{days * 86400}"
    cards = {}
    for q in CFG["linkedin_queries"]:
        for loc in CFG["linkedin_locations"]:
            for start in (0, 25):
                url = ("https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?"
                       + urllib.parse.urlencode({"keywords": q, "geoId": loc["geoId"], "f_TPR": tpr,
                                                 "f_E": CFG["linkedin_experience"], "start": start}))
                page = get(url)
                time.sleep(1.2)
                if not page:
                    break
                found = 0
                for c in page.split("<li>")[1:]:
                    jid = re.search(r"jobPosting:(\d+)", c)
                    title = re.search(r'base-search-card__title">\s*(.*?)\s*</h3>', c, re.S)
                    comp = re.search(r'base-search-card__subtitle">(.*?)</h4>', c, re.S)
                    where = re.search(r'job-search-card__location">\s*(.*?)\s*</span>', c, re.S)
                    when = re.search(r'datetime="([\d-]+)"', c)
                    if not (jid and title):
                        continue
                    found += 1
                    t = html.unescape(title.group(1))
                    w = html.unescape(where.group(1)) if where else ""
                    if not title_ok(t):
                        continue
                    if loc["label"] == "India" and not re.search(r"bengaluru|bangalore|remote", w, re.I):
                        continue
                    cards[jid.group(1)] = {
                        "source": "linkedin", "company": re.sub(r"\s+", " ", text(comp.group(1))).strip() if comp else "",
                        "role": t, "location": w, "posted": when.group(1) if when else "",
                        "url": f"https://www.linkedin.com/jobs/view/{jid.group(1)}/",
                    }
                if found < 25:
                    break
    print(f"linkedin: {len(cards)} title matches; fetching details for up to {max_details}", file=sys.stderr)
    out = []
    for jid, job in list(cards.items())[:max_details]:
        page = get(f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{jid}")
        time.sleep(1.2)
        if not page:
            continue
        d = re.search(r"description__text[^>]*>(.*?)</section", page, re.S)
        job["description"] = text(d.group(1)).strip() if d else ""
        crit = [re.sub(r"\s+", " ", x).strip() for x in re.findall(r"description__job-criteria-text[^>]*>(.*?)<", page, re.S)]
        job["seniority"] = crit[0] if crit else ""
        n = re.search(r"num-applicants__caption[^>]*>\s*(.*?)\s*<", page, re.S)
        job["applicants"] = re.sub(r"\s+", " ", n.group(1)).strip() if n else ""
        if not n:
            n = re.search(r"(Over \d+|\d+) applicants", page)
            job["applicants"] = n.group(0) if n else ""
        out.append(job)
    return out


def from_hn():
    hits = get("https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&hitsPerPage=5", as_json=True)
    if not hits:
        return []
    story = next((h for h in hits["hits"] if "who is hiring" in h["title"].lower()), None)
    if not story:
        return []
    tree = get(f"https://hn.algolia.com/api/v1/items/{story['objectID']}", as_json=True) or {}
    out = []
    for c in tree.get("children", []):
        body = text(c.get("text"))
        if not body.strip():
            continue
        first = body.strip().split("\n")[0]
        wide = re.search(r"remote\s*\(?\s*(worldwide|global|anywhere|india|apac)|bengaluru|bangalore|india", body, re.I)
        if not wide:
            continue
        if FOREIGN.search(first) and not re.search(r"india|bengaluru|bangalore|worldwide|global|anywhere|apac", first, re.I):
            continue
        if not re.search(r"\b(ai|llm|ml|backend|back-end|python|full[- ]?stack|node|typescript|agents?)\b", body, re.I):
            continue
        parts = [p.strip() for p in first.split("|")]
        out.append({
            "source": "hn", "company": parts[0][:60], "role": " | ".join(parts[1:3])[:120] or "(see post)",
            "location": wide.group(0), "posted": c["created_at"][:10],
            "url": f"https://news.ycombinator.com/item?id={c['id']}",
            "description": body[:4000], "seniority": "", "applicants": "",
        })
    return out


def from_boards(days):
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=max(days, 21))  # boards change slowly
    out = []
    for b in CFG["boards"]:
        if b["ats"] == "ashby":
            d = get(f"https://api.ashbyhq.com/posting-api/job-board/{b['slug']}", as_json=True) or {}
            for j in d.get("jobs", []):
                loc = " ".join([j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
                               + (["remote"] if j.get("isRemote") else []))
                out.append({"company": b["company"], "role": j["title"], "location": loc,
                            "posted": (j.get("publishedAt") or "")[:10], "url": j.get("applyUrl") or j["jobUrl"],
                            "description": j.get("descriptionPlain") or ""})
        elif b["ats"] == "greenhouse":
            d = get(f"https://boards-api.greenhouse.io/v1/boards/{b['slug']}/jobs?content=true", as_json=True) or {}
            for j in d.get("jobs", []):
                out.append({"company": b["company"], "role": j["title"], "location": (j.get("location") or {}).get("name", ""),
                            "posted": (j.get("first_published") or j.get("updated_at") or "")[:10],
                            "url": j["absolute_url"], "description": text(html.unescape(j.get("content") or ""))})
        elif b["ats"] == "lever":
            d = get(f"https://api.lever.co/v0/postings/{b['slug']}?mode=json", as_json=True) or []
            for j in d:
                cat = j.get("categories") or {}
                loc = " ".join(cat.get("allLocations") or [cat.get("location") or ""]) + " " + (j.get("workplaceType") or "")
                posted = dt.datetime.fromtimestamp(j["createdAt"] / 1000, dt.timezone.utc).date().isoformat() if j.get("createdAt") else ""
                out.append({"company": b["company"], "role": j["text"], "location": loc, "posted": posted,
                            "url": j["hostedUrl"], "description": (j.get("descriptionPlain") or "") + "\n"
                            + "\n".join(text(l.get("content")) for l in j.get("lists") or [])})
        time.sleep(0.5)
    keep = []
    for j in out:
        j.update(source=f"board:{j['company']}", seniority="", applicants="", ats_hint=True)
        if not (title_ok(j["role"]) and location_ok(j["location"])):
            continue
        if j["posted"] and j["posted"] < cutoff.date().isoformat():
            continue
        keep.append(j)
    return keep


def from_freehire(days):
    """freehire.me: ~3M postings crawled from company ATS boards, tagged by city, category and seniority."""
    fh = CFG["freehire"]
    out = []
    for q in fh["queries"]:
        params = dict(q, category=fh["category"], seniority_exclude=fh["seniority_exclude"],
                      open_within_days=days, sort="created_at", order="desc", limit=100,
                      description_format="markdown")
        for page in range(fh["max_pages"]):
            params["offset"] = page * 100
            d = get("https://freehire.me/api/v1/agent/jobs/search?" + urllib.parse.urlencode(params), as_json=True) or {}
            for j in d.get("data", []):
                if j.get("source") in fh["skip_sources"] or (j.get("reality") or {}).get("class") == "stale":
                    continue
                c = j.get("company")
                out.append({
                    "source": f"freehire:{j.get('source')}", "company": (c.get("name") if isinstance(c, dict) else c) or "",
                    "role": j["title"], "location": j.get("location") or "",
                    "posted": (j.get("posted_at") or j.get("created_at") or "")[:10],
                    "url": re.sub(r"[?&]utm_source=freehire\.me$", "", j["url"]),
                    "description": j.get("description") or "", "seniority": "", "applicants": "",
                    "fh_years": (j.get("enrichment") or {}).get("experience_years_min"),
                })
            if (page + 1) * 100 >= (d.get("meta") or {}).get("total", 0):
                break
            time.sleep(0.5)
    return [j for j in out if title_ok(j["role"])]


def from_careerops(days):
    """career-ops scan.mjs (vendored in tools/career-ops): ~65 company boards across Greenhouse, Ashby, Lever,
    Workday, Rippling, Workable, Zoho Recruit and more, from .claude/skills/career-ops/root/portals.yml.
    Titles, locations and posting age are filtered there; no descriptions, so workers read the JD."""
    co = ROOT / ".claude" / "skills" / "career-ops"
    pipe = co / "root" / "data" / "pipeline.md"
    pipe.unlink(missing_ok=True)  # each run starts a fresh pipeline; scan-history.tsv keeps the dedupe
    try:
        r = subprocess.run(["bash", str(co / "scripts" / "co.sh"), "scan", "--json", "--quiet", "--since", str(max(days, 21))],
                           capture_output=True, text=True, timeout=900)
        receipt = json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e:
        print(f"  skip career-ops scan: {e}", file=sys.stderr)
        return []
    for err in receipt.get("errors", []):
        print(f"  career-ops: {err['company']}: {err['error'][:80]}", file=sys.stderr)
    out = []
    for line in pipe.read_text().splitlines() if pipe.exists() else []:
        if not line.startswith("- [ ] "):
            continue
        parts = [p.strip() for p in line[6:].split(" | ")]
        if len(parts) < 4:
            continue
        posted = parts[4].removeprefix("posted: ") if len(parts) > 4 else ""
        out.append({"source": "careerops", "company": parts[1], "role": parts[2], "location": parts[3],
                    "posted": posted, "url": parts[0], "description": "", "seniority": "", "applicants": "",
                    "ats_hint": True})
    return [j for j in out if title_ok(j["role"]) and location_ok(j["location"])]


# ---------- filter, dedupe, rank ----------

def tracker_keys():
    if not TRACKER.exists():
        return set(), set()
    rows = list(csv.DictReader(TRACKER.open(newline="", encoding="utf-8")))
    urls = {r["job_url"] for r in rows if r["job_url"]}
    pairs = {(norm(r["company"]), norm(r["role"])) for r in rows}
    return urls, pairs


def score(j):
    s, why = 0, []
    t, d = j["role"].lower(), (j.get("description") or "").lower()
    for kw, pts in (("genai", 4), ("llm", 4), ("agent", 4), ("ai engineer", 4), ("voice", 3), ("whatsapp", 3),
                    ("fastapi", 3), ("python", 2), ("mcp", 3), ("rag", 2), ("node", 1), ("typescript", 1),
                    ("postgres", 1), ("redis", 1), ("fintech", 1), ("bfsi", 2), ("backend", 2)):
        if kw in t:
            s += pts * 2
            why.append(kw)
        elif kw in d:
            s += pts
            why.append(kw)
    y = min_years(j.get("description"))
    if y is None and isinstance(j.get("fh_years"), int):
        y = j["fh_years"]
    j["min_years"] = y
    if y is not None:
        s += 4 if y <= 2 else 1
    if j.get("ats_hint") or re.search(r"ashbyhq|greenhouse|lever\.co", j["url"]):
        s += 2  # forms that fill cleanly without an account
    m = re.search(r"(\d+)", j.get("applicants") or "")
    if m and int(m.group(1)) < 50:
        s += 2
    if (j.get("seniority") or "").lower() in ("entry level", "associate"):
        s += 2
    j["emails"] = sorted({e for e in EMAIL_RE.findall(j.get("description") or "")
                          if not e.endswith((".png", ".jpg")) and not JUNK_EMAIL.match(e)})
    if j["emails"]:
        s += 3
    j["score"], j["why"] = s, why[:6]
    return j


def cmd_run(a):
    HUNTS.mkdir(exist_ok=True)
    seen = set(SEEN.read_text().split()) if SEEN.exists() else set()
    t_urls, t_pairs = tracker_keys()
    want = set(a.sources.split(","))
    raw = []
    if "boards" in want:
        raw += from_boards(a.days)
    if "careerops" in want:
        raw += from_careerops(a.days)
    if "hn" in want:
        raw += from_hn()
    if "freehire" in want:
        raw += from_freehire(a.days)
    if "linkedin" in want:
        raw += from_linkedin(a.days, a.max_details)

    kept, dropped = [], {"seen or tracked": 0, "too many years": 0, "duplicate": 0}
    keys = set()
    for j in raw:
        k = (norm(j["company"]), norm(j["role"]))
        if j["url"] in seen or j["url"] in t_urls or k in t_pairs:
            dropped["seen or tracked"] += 1
            continue
        if k in keys:
            dropped["duplicate"] += 1
            continue
        keys.add(k)
        score(j)
        if j["min_years"] is not None and j["min_years"] > CFG["max_min_years"]:
            dropped["too many years"] += 1
            continue
        kept.append(j)
    kept.sort(key=lambda j: j["score"], reverse=True)

    day = dt.date.today().isoformat()
    for j in kept:
        j["description"] = (j.get("description") or "")[:3000]
    (HUNTS / f"{day}.json").write_text(json.dumps(kept, indent=1, ensure_ascii=False))
    lines = [f"# Hunt {day}", "", f"Raw {len(raw)}, kept {len(kept)}, dropped {dropped}", "",
             "| # | score | company | role | location | posted | yrs | applicants | emails | url |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    cell = lambda v: str(v).replace("|", "/").replace("\n", " ")
    for i, j in enumerate(kept, 1):
        lines.append(f"| {i} | {j['score']} | {cell(j['company'])} | {cell(j['role'])} | {cell(j['location'][:30])} | {j['posted']} | "
                     f"{j['min_years'] if j['min_years'] is not None else '?'} | {j['applicants']} | {', '.join(j['emails'])} | {j['url']} |")
    (HUNTS / f"{day}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:4 + min(len(kept), 40) + 2]))
    print(f"\nwrote hunts/{day}.json and hunts/{day}.md")


def cmd_seen(a):
    HUNTS.mkdir(exist_ok=True)
    with SEEN.open("a") as f:
        for u in a.urls:
            f.write(u + "\n")
    print(f"marked {len(a.urls)} seen")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--days", type=int, default=2, help="posting window in days (LinkedIn, freehire)")
    r.add_argument("--sources", default="boards,careerops,hn,freehire,linkedin")
    r.add_argument("--max-details", type=int, default=80, help="LinkedIn job pages to open for descriptions")
    r.set_defaults(fn=cmd_run)
    s = sub.add_parser("seen")
    s.add_argument("urls", nargs="+")
    s.set_defaults(fn=cmd_seen)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
