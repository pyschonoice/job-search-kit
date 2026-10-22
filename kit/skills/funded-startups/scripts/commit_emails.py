#!/usr/bin/env python3
"""Prove a company's email pattern from public GitHub commits (company-domain addresses only).

  commit_emails.py <github-org> <domain> [--repos 6]

Lists the most recently pushed repos of the org, reads up to 100 commits each and prints
author addresses on <domain>. Two or more people in the same format = a proven `pattern`.
Needs the `gh` CLI (logged in). Never prints personal (gmail etc.) addresses.
"""
import argparse, collections, json, subprocess

def gh(path):
    r = subprocess.run(["gh", "api", path], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)
    except Exception:
        return []

a = argparse.ArgumentParser(); a.add_argument("org"); a.add_argument("domain"); a.add_argument("--repos", type=int, default=6)
a = a.parse_args()
repos = gh(f"orgs/{a.org}/repos?per_page={a.repos}&sort=pushed")
if not isinstance(repos, list) or not repos:
    raise SystemExit(f"{a.org}: no public org repos")
c = collections.Counter()
for r in repos:
    for cm in gh(f"repos/{a.org}/{r['name']}/commits?per_page=100") or []:
        e = ((cm.get("commit") or {}).get("author") or {}).get("email", "").lower()
        if e.endswith("@" + a.domain.lower()) and not e.startswith("noreply"):
            c[e] += 1
for e, n in c.most_common():
    print(f"{n:4} {e}")
locals_ = [e.split("@")[0] for e in c]
fmt = "first.l" if any("." in l for l in locals_) else "first"
print(f"-> {len(c)} addresses; looks like `{fmt}@{a.domain}`" + ("  (proven: 2+)" if len(c) >= 2 else "  (1 sample: still a guess)") if c else "-> none found")
