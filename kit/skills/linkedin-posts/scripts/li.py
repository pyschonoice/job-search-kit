#!/usr/bin/env python3
"""Helpers for the linkedin-posts skill (run from the repo root).

    li.py build [--feed] [--scrolls N] [--hours 24] [--queries q1 q2 ...]   build the li-posts snippet with the seen list baked in
    li.py resolve <url> [<url> ...]                    follow lnkd.in short links to their real target
    li.py seen <key> [<key> ...]                       remember handled posts so they never come back

build prints the snippet path; pass it as `filename` to mcp__playwright__browser_run_code_unsafe.
"""
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[4]
SEEN = ROOT / "tracker" / "li_seen.txt"
SNIP = ROOT / ".claude" / "skills" / "portal-apply" / "scripts" / "snip.py"
QUERIES = [
    'hiring "AI engineer" bangalore',
    'hiring SDE 1 bangalore',
    'hiring GenAI engineer "2+ years"',
    'hiring python backend developer bangalore email',
    'hiring founding engineer AI bangalore',
    'hiring full stack engineer bangalore "send your resume"',
]
SKIP = re.compile(r"linkedin|licdn|w3\.org|schema\.org|googletagmanager|gstatic")


def seen_keys():
    return [l for l in SEEN.read_text().splitlines() if l.strip()] if SEEN.exists() else []


def build(argv):
    hours, queries, i, feed, scrolls = 24, [], 0, False, 5
    while i < len(argv):
        if argv[i] == "--hours":
            hours = int(argv[i + 1]); i += 2
        elif argv[i] == "--feed":
            feed = True; i += 1
        elif argv[i] == "--scrolls":
            scrolls = int(argv[i + 1]); i += 2
        elif argv[i] == "--queries":
            queries = argv[i + 1:]; break
        else:
            i += 1
    args = {"queries": queries or QUERIES, "hours": hours, "scrolls": scrolls, "feed": feed, "maxMinYears": 4, "seen": seen_keys()[-400:]}
    subprocess.run([sys.executable, str(SNIP), "li-posts", json.dumps(args)], check=True)


def resolve(urls):
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                final, body = r.geturl(), r.read(200000).decode("utf-8", "ignore")
            if "lnkd.in" in final:  # LinkedIn's interstitial page holds the target as a link
                hits = [h for h in re.findall(r'https?://[^"<> ]+', body) if not SKIP.search(h)]
                final = hits[0] if hits else final
            print(f"{u} -> {final}")
        except Exception as e:  # noqa: BLE001
            print(f"{u} -> ERROR {e}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print(__doc__); return
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "build":
        build(rest)
    elif cmd == "resolve":
        resolve(rest)
    elif cmd == "seen":
        SEEN.parent.mkdir(exist_ok=True)
        with SEEN.open("a") as f:
            f.writelines(k.strip() + "\n" for k in rest if k.strip())
        print(f"{len(rest)} keys saved ({len(seen_keys())} total)")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
