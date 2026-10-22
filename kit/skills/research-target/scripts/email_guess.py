#!/usr/bin/env python3
"""Candidate email addresses for a person at a domain, most likely first.

  email_guess.py "Firstname Lastname" company.com [--known a@company.com b@company.com]

Checks the domain's MX records with `dig` (no mail is sent). With --known, it
works out which format the known addresses share and puts that first; two or
more agreeing addresses make the result a `pattern`, otherwise every candidate
is a `guess`.
"""
import argparse
import re
import subprocess
import unicodedata

FORMATS = [  # rough order of how common each is at Indian startups
    ("first", "{f}"), ("first.last", "{f}.{l}"), ("firstlast", "{f}{l}"), ("flast", "{fi}{l}"),
    ("f.last", "{fi}.{l}"), ("first_last", "{f}_{l}"), ("firstl", "{f}{li}"), ("last", "{l}"), ("last.first", "{l}.{f}"),
]


def clean(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


def parts(name):
    bits = [clean(b) for b in name.split() if clean(b)]
    f, l = bits[0], bits[-1] if len(bits) > 1 else ""
    return {"f": f, "l": l, "fi": f[:1], "li": l[:1]}


def mx(domain):
    try:
        out = subprocess.run(["dig", "+short", "MX", domain], capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return None
    return out.splitlines()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("name")
    p.add_argument("domain")
    p.add_argument("--known", nargs="*", default=[], help="published addresses of other people at the domain, as name=addr, e.g. 'Rahul Sharma=rahul@x.com'")
    a = p.parse_args()

    records = mx(a.domain)
    if records is None:
        print("MX: could not run dig")
    elif not records:
        print(f"MX: none for {a.domain} — mail to this domain will bounce; find another address")
    else:
        print(f"MX: ok ({records[0]}{' ...' if len(records) > 1 else ''})")

    # Which formats do the known addresses use?
    votes = {}
    for k in a.known:
        if "=" not in k:
            continue
        kname, kaddr = k.split("=", 1)
        kp, local = parts(kname), kaddr.split("@")[0].lower()
        for label, f in FORMATS:
            if kp["l"] or "{l" not in f:
                if f.format(**kp) == local:
                    votes[label] = votes.get(label, 0) + 1
    me = parts(a.name)
    ranked = sorted(FORMATS, key=lambda x: -votes.get(x[0], 0))
    seen = set()
    for label, f in ranked:
        if not me["l"] and "{l" in f:
            continue
        addr = f"{f.format(**me)}@{a.domain}"
        if addr in seen:
            continue
        seen.add(addr)
        conf = "pattern" if votes.get(label, 0) >= 2 else "guess"
        extra = f"  ({votes[label]} known address{'es' if votes[label] > 1 else ''} match)" if votes.get(label) else ""
        print(f"{conf:8} {addr}{extra}")


if __name__ == "__main__":
    main()
